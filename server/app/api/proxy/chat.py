from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.tenant import Tenant
from ...models.provider import ProviderKey, Provider
from ...models.conversation import Conversation
from ...services.llm_factory import get_llm_client
from ...services.token_service import update_token_stats
from ...services.memory_service import load_memory, should_process_memory
import json
import httpx

router = APIRouter()


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
    if str(tenant.status) != "TenantStatus.ACTIVE" and str(tenant.status) != "ACTIVE":
        raise HTTPException(status_code=403, detail="Tenant is inactive")

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


async def _save_conversation(
    db: Session, app_key: str, user_message: str, ai_response: str
):
    round_number = (
        db.query(Conversation).filter(Conversation.app_key == app_key).count() + 1
    )
    conversation = Conversation(
        app_key=app_key,
        round_number=round_number,
        user_message=user_message,
        ai_response=ai_response,
    )
    db.add(conversation)
    db.commit()
    return round_number


async def _proxy_chat_impl(request: Request, db: Session, force_stream: bool = False):
    body = await request.json()
    app_key = _resolve_app_key(request, body)
    provider_key, provider = _resolve_provider_context(db, app_key)

    messages = body.get("messages", [])
    if not isinstance(messages, list) or len(messages) == 0:
        raise HTTPException(status_code=400, detail="messages is required")

    model = body.get("model") or provider_key.model_name or "qwen-plus"
    stream = force_stream or body.get("stream", False)

    memory_context = await load_memory(app_key)
    if memory_context:
        messages.insert(0, {"role": "system", "content": memory_context})

    llm_client = get_llm_client(provider.name, provider_key.api_key, provider.base_url)
    total_tokens = 0
    ai_response = ""

    async def generate():
        nonlocal total_tokens, ai_response
        try:
            async for chunk in llm_client.chat_completion(messages, model, True):
                usage = chunk.get("usage") if isinstance(chunk, dict) else {}
                if not isinstance(usage, dict):
                    usage = {}
                total_tokens += usage.get("total_tokens", 0)
                choices = chunk.get("choices", []) if isinstance(chunk, dict) else []
                if len(choices) > 0:
                    first_choice = choices[0] if isinstance(choices[0], dict) else {}
                    delta = first_choice.get("delta", {})
                    if not isinstance(delta, dict):
                        delta = {}
                    content = delta.get("content", "")
                    if not content and "message" in first_choice:
                        message_obj = first_choice.get("message", {})
                        if isinstance(message_obj, dict):
                            content = message_obj.get("content", "")
                    ai_response += content
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except httpx.HTTPStatusError as e:
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
        except Exception as e:
            error_payload = {"error": {"type": "stream_error", "message": str(e)}}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        await update_token_stats(db, app_key, total_tokens)
        user_message = messages[-1].get("content", "") if messages else ""
        round_number = await _save_conversation(db, app_key, user_message, ai_response)
        await should_process_memory(db, app_key, round_number)
        yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(generate(), media_type="text/event-stream")

    result = None
    async for chunk in llm_client.chat_completion(messages, model, False):
        result = chunk

    if result is None:
        raise HTTPException(
            status_code=502, detail="Upstream provider returned empty response"
        )

    usage = result.get("usage", {}) if isinstance(result, dict) else {}
    if not isinstance(usage, dict):
        usage = {}
    total_tokens = usage.get("total_tokens", 0)
    await update_token_stats(db, app_key, total_tokens)
    user_message = messages[-1].get("content", "") if messages else ""
    choices = result.get("choices", []) if isinstance(result, dict) else []
    first_choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message_obj = (
        first_choice.get("message", {}) if isinstance(first_choice, dict) else {}
    )
    if not isinstance(message_obj, dict):
        message_obj = {}
    ai_response = message_obj.get("content", "")
    round_number = await _save_conversation(db, app_key, user_message, ai_response)
    await should_process_memory(db, app_key, round_number)
    return result


@router.post("/chat/completions")
async def proxy_chat(request: Request, db: Session = Depends(get_db)):
    return await _proxy_chat_impl(request, db, False)


@router.post("/chat/completions/sse")
async def proxy_chat_sse(request: Request, db: Session = Depends(get_db)):
    return await _proxy_chat_impl(request, db, True)
