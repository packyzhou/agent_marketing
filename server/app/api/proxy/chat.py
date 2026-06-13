from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import asyncio
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from ...core.database import get_db
from ...core.database import SessionLocal
from ...core.snowflake import generate_snowflake_id
from ...core.threadpool import run_blocking
from ...models.tenant import Tenant
from ...models.provider import ProviderKey, Provider
from ...models.conversation import Conversation
from ...services.llm_factory import get_llm_client
from ...services.token_service import update_token_stats, save_conversation_token_usage
from ...services.memory_service import load_memory, schedule_memory_processing
from ...agent import service as agent_service
import json
import httpx
import openai

router = APIRouter()
MESSAGE_DIR = Path("./message")
MESSAGE_RETENTION_DAYS = 7


def _resolve_app_key(request: Request, body: dict) -> str:
    header_app_key = request.headers.get("X-App-Key")
    body_app_key = body.get("app_key")
    app_key = (header_app_key or body_app_key or "").strip()
    if not app_key:
        raise HTTPException(status_code=401, detail="Missing app_key")
    return app_key


def _resolve_provider_context(db: Session, app_key: str):
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid app_key")
    tenant_status = (
        tenant.status.value if hasattr(tenant.status, "value") else str(tenant.status)
    )
    if str(tenant_status).upper() != "ACTIVE":
        raise HTTPException(status_code=401, detail="Tenant is inactive")

    provider_key = (
        db.query(ProviderKey)
        .filter(ProviderKey.app_key == app_key)
        .order_by(desc(ProviderKey.updated_at), desc(ProviderKey.created_at))
        .first()
    )

    if not provider_key:
        raise HTTPException(status_code=400, detail="No provider configured")

    provider = (
        db.query(Provider).filter(Provider.id == provider_key.provider_id).first()
    )
    if not provider:
        raise HTTPException(status_code=400, detail="Provider not found")
    return provider_key, provider


def _resolve_provider_context_blocking(app_key: str) -> dict:
    db = SessionLocal()
    try:
        provider_key, provider = _resolve_provider_context(db, app_key)
        return {
            "provider_key_api_key": provider_key.api_key,
            "provider_key_model_name": provider_key.model_name,
            "provider_code": provider.code,
            "provider_name": provider.name,
            "provider_base_url": provider.base_url,
        }
    finally:
        db.close()


def _load_memory_blocking(app_key: str) -> str:
    db = SessionLocal()
    try:
        return asyncio.run(load_memory(app_key, db=db))
    finally:
        db.close()


def _build_openai_payload(body: dict) -> dict:
    if not isinstance(body, dict):
        return {}
    payload = dict(body)
    payload.pop("app_key", None)
    payload.pop("debug", None)
    payload.pop("use_memory", None)
    payload.pop("use_agent", None)
    return payload


def _resolve_use_memory(body: dict) -> bool:
    if not isinstance(body, dict):
        return True
    value = body.get("use_memory", True)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() != "false"
    return bool(value)


def _resolve_use_agent(body: dict) -> bool:
    if not isinstance(body, dict):
        return False
    value = body.get("use_agent", False)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _is_debug_mode(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _resolve_request_model(body: dict, provider_model_name: str | None) -> str:
    body_model = (body.get("model") or "").strip()
    configured_model = (provider_model_name or "").strip()
    debug = _is_debug_mode(body.get("debug"))
    if debug:
        return body_model or configured_model or "qwen-plus"
    if not configured_model:
        raise HTTPException(status_code=400, detail="No model configured")
    return configured_model


def _safe_filename_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)


def _cleanup_old_message_files(now: datetime) -> None:
    cutoff = now.date() - timedelta(days=MESSAGE_RETENTION_DAYS - 1)
    for path in MESSAGE_DIR.glob("message_*_*.txt"):
        try:
            date_text = path.stem.rsplit("_", 1)[-1]
            file_date = datetime.strptime(date_text, "%Y%m%d").date()
        except ValueError:
            continue
        if file_date < cutoff:
            path.unlink(missing_ok=True)


def _save_llm_messages(app_key: str, messages: list) -> None:
    now = datetime.now()
    MESSAGE_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup_old_message_files(now)
    safe_app_key = _safe_filename_part(app_key)
    file_path = MESSAGE_DIR / f"message_{safe_app_key}_{now.strftime('%Y%m%d')}.txt"
    payload = {
        "app_key": app_key,
        "created_at": now.isoformat(timespec="seconds"),
        "messages": messages,
    }
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _persist_usage_blocking(
    app_key: str,
    user_message: str,
    ai_response: str,
    total_tokens: int,
    provider_name: str,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    save_conversation: bool = True,
) -> None:
    db = SessionLocal()
    try:
        asyncio.run(update_token_stats(db, app_key, total_tokens))
        if save_conversation:
            round_number = asyncio.run(_save_conversation(db, app_key, user_message, ai_response))
            asyncio.run(
                save_conversation_token_usage(
                    db=db,
                    app_key=app_key,
                    round_number=round_number,
                    provider_name=provider_name,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                )
            )
    finally:
        db.close()


async def _save_conversation(
    db: Session, app_key: str, user_message: str, ai_response: str
):
    round_number = (
        db.query(Conversation).filter(Conversation.app_key == app_key).count() + 1
    )
    conversation = Conversation(
        # id=generate_snowflake_id(),
        app_key=app_key,
        round_number=round_number,
        user_message=user_message,
        ai_response=ai_response,
    )
    db.add(conversation)
    db.commit()
    return round_number


def _parse_usage_dict(usage: dict) -> tuple[int, int, int]:
    if not isinstance(usage, dict):
        return 0, 0, 0

    prompt_tokens_raw = usage.get("prompt_tokens", usage.get("input_tokens", 0))
    completion_tokens_raw = usage.get(
        "completion_tokens", usage.get("output_tokens", 0)
    )
    total_tokens_raw = usage.get("total_tokens", 0)
    try:
        prompt_tokens = int(prompt_tokens_raw or 0)
    except (TypeError, ValueError):
        prompt_tokens = 0
    try:
        completion_tokens = int(completion_tokens_raw or 0)
    except (TypeError, ValueError):
        completion_tokens = 0
    try:
        total_tokens = int(total_tokens_raw or 0)
    except (TypeError, ValueError):
        total_tokens = 0
    if total_tokens <= 0:
        total_tokens = prompt_tokens + completion_tokens
    return int(prompt_tokens), int(completion_tokens), int(total_tokens)


def _extract_openai_usage(payload: dict) -> tuple[int, int, int]:
    if not isinstance(payload, dict):
        return 0, 0, 0

    usage = payload.get("usage")
    if isinstance(usage, dict):
        return _parse_usage_dict(usage)

    if isinstance(payload.get("message"), dict):
        message_usage = payload["message"].get("usage")
        if isinstance(message_usage, dict):
            return _parse_usage_dict(message_usage)

    return 0, 0, 0


def _estimate_prompt_tokens(llm_client, messages: list) -> int:
    content_list = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if isinstance(content, str):
            content_list.append(content)
        elif isinstance(content, list):
            content_list.extend([str(item) for item in content])
        elif content is not None:
            content_list.append(str(content))
    joined = "\n".join(content_list)
    return max(int(llm_client.count_tokens(joined)), 0) if joined else 0


def _message_content_to_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n".join(str(item).strip() for item in content if item).strip()
    if content is not None:
        return str(content).strip()
    return ""


def _normalize_text(value) -> str:
    return value if isinstance(value, str) else ""


def _log_llm_elapsed(app_key: str, provider_code: str, model: str, stream: bool, started_at: float, status: str) -> None:
    elapsed_seconds = time.perf_counter() - started_at
    print(
        "LLM request elapsed | "
        f"app_key:{app_key} | provider:{provider_code} | model:{model} | "
        f"stream:{stream} | status:{status} | elapsed_seconds:{elapsed_seconds:.3f}"
    )


def _is_llm_timeout_error(error: Exception) -> bool:
    return isinstance(
        error,
        (
            asyncio.TimeoutError,
            TimeoutError,
            httpx.TimeoutException,
            openai.APITimeoutError,
        ),
    )


def _llm_timeout_message() -> str:
    return "LLM request timed out after 300 seconds"


async def _proxy_chat_impl(request: Request, db: Session, force_stream: bool = False):
    body = await request.json()
    app_key = _resolve_app_key(request, body)
    provider_context = await run_blocking(_resolve_provider_context_blocking, app_key)
    openai_payload = _build_openai_payload(body)
    messages = body.get("messages", [])
    if not isinstance(messages, list) or len(messages) == 0:
        raise HTTPException(status_code=400, detail="messages is required")
    system_contexts = []
    user_messages = []
    for message in messages:
        if isinstance(message, dict) and message.get("role") == "system":
            system_content = _message_content_to_text(message.get("content"))
            if system_content:
                system_contexts.append(system_content)
        else:
            user_messages.append(message)
    messages = user_messages

    provider_code = provider_context["provider_code"]
    provider_name = provider_context["provider_name"]
    provider_base_url = provider_context["provider_base_url"]
    provider_api_key = provider_context["provider_key_api_key"]
    provider_model_name = provider_context["provider_key_model_name"]
    model = _resolve_request_model(body, provider_model_name)
    stream = force_stream or body.get("stream", False)
    openai_payload["model"] = model
    use_memory = _resolve_use_memory(body)
    use_agent = _resolve_use_agent(body)
    if use_agent:
        flow_ready = await run_blocking(agent_service.has_enabled_flow_blocking, app_key)
        if not flow_ready:
            raise HTTPException(
                status_code=400,
                detail="No enabled agent flow configured for this app_key",
            )
    if use_memory:
        print(f"用户[{app_key}] - 输入use_memory：{use_memory} ")
        memory_context = await run_blocking(_load_memory_blocking, app_key)
        # print(f"用户[{app_key}] - 加载到的memory_context：{len(memory_context) if memory_context else 0} ")
        memory_context = (
            memory_context
            + " \n ---------------- \n 以上是与用户相关的历史记忆内容（含永久记忆与近期对话临时记忆）,请根据用户输入的内容进行回答，无关的内容忽略。"
            if memory_context
            else None
        )
    else:
        memory_context = None
    system_content_parts = []
    if memory_context:
        system_content_parts.append(memory_context)
    system_content_parts.extend(system_contexts)
    system_text = "\n\n".join(system_content_parts) if system_content_parts else ""
    # In agent mode the system/memory context is passed as the Agent's
    # instructions (the SDK runner only consumes user/assistant input items),
    # so we must not inject it as a system message into `messages`.
    agent_extra_instructions = system_text or None if use_agent else None
    if system_text and not use_agent:
        messages.insert(0, {"role": "system", "content": system_text})
    openai_payload["messages"] = messages
    await run_blocking(_save_llm_messages, app_key, messages)
    print(f"最终输入openai_payload-messages：{messages} | use_agent:{use_agent}")
    llm_client = get_llm_client(provider_code, provider_api_key, provider_base_url)

    def completion_source(stream_flag: bool):
        if use_agent:
            return agent_service.run_agent(
                app_key,
                messages,
                model_label=model,
                extra_instructions=agent_extra_instructions,
                stream=stream_flag,
            )
        return llm_client.chat_completion(messages, model, stream_flag, openai_payload)
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    ai_response = ""
    persisted = False

    async def persist_usage():
        nonlocal total_tokens, prompt_tokens, completion_tokens, persisted
        if persisted:
            return
        if completion_tokens <= 0:
            completion_tokens = (
                max(int(llm_client.count_tokens(ai_response)), 0) if ai_response else 0
            )
        if prompt_tokens <= 0:
            prompt_tokens = _estimate_prompt_tokens(llm_client, messages)
        if total_tokens <= 0:
            total_tokens = prompt_tokens + completion_tokens
        if total_tokens <= 0:
            return
        user_message = messages[-1].get("content", "") if messages else ""
        await run_blocking(
            _persist_usage_blocking,
            app_key,
            user_message,
            ai_response,
            total_tokens,
            provider_name,
            model,
            prompt_tokens,
            completion_tokens,
            use_memory,
        )
        if use_memory:
            schedule_memory_processing(app_key)
        persisted = True

    async def generate():
        nonlocal total_tokens, prompt_tokens, completion_tokens, ai_response
        prompt_tokens = _estimate_prompt_tokens(llm_client, messages)
        llm_started_at = time.perf_counter()
        try:
            async for chunk in completion_source(True):
                usage_prompt, usage_completion, usage_total = _extract_openai_usage(
                    chunk
                )
                prompt_tokens = max(prompt_tokens, usage_prompt)
                completion_tokens = max(completion_tokens, usage_completion)
                total_tokens = max(total_tokens, usage_total)
                choices = chunk.get("choices", []) if isinstance(chunk, dict) else []
                if len(choices) > 0:
                    first_choice = choices[0] if isinstance(choices[0], dict) else {}
                    delta = first_choice.get("delta", {})
                    if not isinstance(delta, dict):
                        delta = {}
                    content = _normalize_text(delta.get("content"))
                    if not content and "message" in first_choice:
                        message_obj = first_choice.get("message", {})
                        if isinstance(message_obj, dict):
                            content = _normalize_text(message_obj.get("content"))
                    ai_response += content
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except httpx.HTTPStatusError as e:
            _log_llm_elapsed(app_key, provider_code, model, True, llm_started_at, "http_error")
            error_payload = {
                "error": {
                    "type": "upstream_http_error",
                    "status_code": (
                        e.response.status_code if e.response is not None else None
                    ),
                    "message": str(e),
                }
            }
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return
        except asyncio.CancelledError:
            _log_llm_elapsed(app_key, provider_code, model, True, llm_started_at, "cancelled")
            await persist_usage()
            raise
        except Exception as e:
            if _is_llm_timeout_error(e):
                _log_llm_elapsed(app_key, provider_code, model, True, llm_started_at, "timeout")
                error_payload = {
                    "error": {
                        "type": "upstream_timeout",
                        "status_code": 504,
                        "message": _llm_timeout_message(),
                    }
                }
                yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return
            _log_llm_elapsed(app_key, provider_code, model, True, llm_started_at, "error")
            await persist_usage()
            error_payload = {"error": {"type": "stream_error", "message": str(e)}}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        _log_llm_elapsed(app_key, provider_code, model, True, llm_started_at, "success")
        await persist_usage()
        yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(generate(), media_type="text/event-stream")

    result = None
    llm_started_at = time.perf_counter()
    try:
        async for chunk in completion_source(False):
            result = chunk
        _log_llm_elapsed(app_key, provider_code, model, False, llm_started_at, "success")
    except httpx.HTTPStatusError:
        _log_llm_elapsed(app_key, provider_code, model, False, llm_started_at, "http_error")
        raise
    except Exception as e:
        if _is_llm_timeout_error(e):
            _log_llm_elapsed(app_key, provider_code, model, False, llm_started_at, "timeout")
            raise HTTPException(status_code=504, detail=_llm_timeout_message()) from e
        _log_llm_elapsed(app_key, provider_code, model, False, llm_started_at, "error")
        raise

    if result is None:
        _log_llm_elapsed(app_key, provider_code, model, False, llm_started_at, "empty_response")
        raise HTTPException(
            status_code=502, detail="Upstream provider returned empty response"
        )

    prompt_tokens, completion_tokens, total_tokens = _extract_openai_usage(result)
    if prompt_tokens <= 0:
        prompt_tokens = _estimate_prompt_tokens(llm_client, messages)
    user_message = messages[-1].get("content", "") if messages else ""
    choices = result.get("choices", []) if isinstance(result, dict) else []
    first_choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message_obj = (
        first_choice.get("message", {}) if isinstance(first_choice, dict) else {}
    )
    if not isinstance(message_obj, dict):
        message_obj = {}
    ai_response = _normalize_text(message_obj.get("content"))
    if completion_tokens <= 0:
        completion_tokens = (
            max(int(llm_client.count_tokens(ai_response)), 0) if ai_response else 0
        )
    if total_tokens <= 0:
        total_tokens = prompt_tokens + completion_tokens
    await run_blocking(
        _persist_usage_blocking,
        app_key,
        user_message,
        ai_response,
        total_tokens,
        provider_name,
        model,
        prompt_tokens,
        completion_tokens,
        use_memory,
    )
    if use_memory:
        schedule_memory_processing(app_key)
    return result


@router.post("/chat/completions")
async def proxy_chat(request: Request, db: Session = Depends(get_db)):
    return await _proxy_chat_impl(request, db, False)


@router.post("/chat/completions/sse")
async def proxy_chat_sse(request: Request, db: Session = Depends(get_db)):
    return await _proxy_chat_impl(request, db, True)
