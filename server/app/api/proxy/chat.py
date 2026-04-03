from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.tenant import Tenant
from ...models.provider import ProviderKey, Provider
from ...models.conversation import Conversation
from ...services.llm_factory import get_llm_client
from ...services.token_service import update_token_stats
from ...services.memory_service import load_memory, should_process_memory
import json

router = APIRouter()

@router.post("/chat/completions")
async def proxy_chat(request: Request, db: Session = Depends(get_db)):
    app_key = request.headers.get("X-App-Key")
    if not app_key:
        raise HTTPException(status_code=401, detail="Missing X-App-Key header")

    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid app_key")

    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "qwen-plus")
    stream = body.get("stream", False)

    # 加载记忆
    memory_context = await load_memory(app_key)
    if memory_context:
        messages.insert(0, {"role": "system", "content": memory_context})

    # 获取供应商配置
    provider_key = db.query(ProviderKey).filter(
        ProviderKey.app_key == app_key
    ).first()

    if not provider_key:
        raise HTTPException(status_code=400, detail="No provider configured")

    provider = db.query(Provider).filter(Provider.id == provider_key.provider_id).first()
    llm_client = get_llm_client(provider.name, provider_key.api_key, provider.base_url)

    # 调用LLM
    total_tokens = 0
    ai_response = ""

    async def generate():
        nonlocal total_tokens, ai_response
        async for chunk in llm_client.chat_completion(messages, model, stream):
            if isinstance(chunk, dict):
                total_tokens += chunk.get("usage", {}).get("total_tokens", 0)
                # 收集AI响应内容
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    ai_response += content
            yield f"data: {json.dumps(chunk)}\n\n"

        # 更新Token统计
        await update_token_stats(db, app_key, total_tokens)

        # 保存对话记录
        user_message = messages[-1].get("content", "") if messages else ""
        round_number = db.query(Conversation).filter(Conversation.app_key == app_key).count() + 1
        conversation = Conversation(
            app_key=app_key,
            round_number=round_number,
            user_message=user_message,
            ai_response=ai_response
        )
        db.add(conversation)
        db.commit()

        # 检查是否需要处理记忆
        await should_process_memory(db, app_key, messages)

    if stream:
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        result = None
        async for chunk in llm_client.chat_completion(messages, model, False):
            result = chunk
        total_tokens = result.get("usage", {}).get("total_tokens", 0)
        await update_token_stats(db, app_key, total_tokens)

        # 保存对话记录
        user_message = messages[-1].get("content", "") if messages else ""
        ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        round_number = db.query(Conversation).filter(Conversation.app_key == app_key).count() + 1
        conversation = Conversation(
            app_key=app_key,
            round_number=round_number,
            user_message=user_message,
            ai_response=ai_response
        )
        db.add(conversation)
        db.commit()

        await should_process_memory(db, app_key, messages)
        return result
