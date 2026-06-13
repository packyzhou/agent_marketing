"""Run a resolved flow's Agent and yield OpenAI-compatible chunk dicts.

The chunk shapes match what the chat proxy + frontend already consume, so
agent mode is a drop-in replacement for llm_client.chat_completion():
  - streaming  -> chat.completion.chunk dicts (delta / finish / usage)
  - blocking   -> a single chat.completion dict
"""

import time
import uuid
from contextlib import AsyncExitStack
from typing import Any, AsyncIterator, Dict, List, Optional

from .cache import ResolvedFlow
from .factory import build_agent


def _now() -> int:
    return int(time.time())


def _messages_to_input(messages: List[dict]) -> List[dict]:
    """Convert chat messages into Agents SDK input items (user/assistant turns)."""
    items: List[dict] = []
    for msg in messages or []:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role not in {"user", "assistant"}:
            continue
        content = msg.get("content")
        if isinstance(content, list):
            content = "\n".join(str(c) for c in content)
        elif content is not None and not isinstance(content, str):
            content = str(content)
        if content:
            items.append({"role": role, "content": content})
    return items


def _extract_usage(result: Any) -> Optional[Dict[str, int]]:
    try:
        usage = result.context_wrapper.usage
    except AttributeError:
        return None
    if usage is None:
        return None
    prompt = int(getattr(usage, "input_tokens", 0) or 0)
    completion = int(getattr(usage, "output_tokens", 0) or 0)
    total = int(getattr(usage, "total_tokens", 0) or 0) or (prompt + completion)
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
    }


async def run_flow(
    flow: ResolvedFlow,
    messages: List[dict],
    model_label: str,
    extra_instructions: Optional[str] = None,
    stream: bool = False,
) -> AsyncIterator[Dict[str, Any]]:
    try:
        from agents import Runner
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "openai-agents package is not installed. Run: pip install openai-agents mcp"
        ) from exc

    from openai.types.responses import ResponseTextDeltaEvent

    chunk_id = f"agent-{uuid.uuid4().hex[:24]}"
    created = _now()
    input_items = _messages_to_input(messages)
    max_turns = max(1, int(flow.max_turns or 10))

    async with AsyncExitStack() as exit_stack:
        agent = await build_agent(flow, exit_stack, extra_instructions=extra_instructions)

        if stream:
            run = Runner.run_streamed(agent, input=input_items, max_turns=max_turns)
            # opening role delta
            yield {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_label,
                "choices": [
                    {"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}
                ],
            }
            async for event in run.stream_events():
                if event.type != "raw_response_event":
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent) and data.delta:
                    yield {
                        "id": chunk_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model_label,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": data.delta},
                                "finish_reason": None,
                            }
                        ],
                    }
            # final stop chunk
            yield {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_label,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            usage = _extract_usage(run)
            if usage:
                yield {
                    "id": chunk_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_label,
                    "choices": [],
                    "usage": usage,
                }
            return

        result = await Runner.run(agent, input=input_items, max_turns=max_turns)
        content = result.final_output
        if not isinstance(content, str):
            content = str(content) if content is not None else ""
        payload: Dict[str, Any] = {
            "id": chunk_id,
            "object": "chat.completion",
            "created": created,
            "model": model_label,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
        }
        usage = _extract_usage(result)
        if usage:
            payload["usage"] = usage
        yield payload
