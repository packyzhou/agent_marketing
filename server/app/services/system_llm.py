"""System-level LLM interface.

Reads configuration from agent_config.json → "system_llm" section and exposes
a singleton client + a convenience coroutine for the rest of the codebase.

agent_config.json example:
    {
      "system_llm": {
        "provider": "qwen",
        "api_key": "sk-xxx",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo"
      }
    }
"""

import json
from pathlib import Path
from typing import Dict, Any, AsyncIterator

from .llm_base import BaseLLM
from .llm_factory import get_llm_client

_AGENT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "agent_config.json"


def _load_system_llm_config() -> dict:
    try:
        text = _AGENT_CONFIG_PATH.read_text(encoding="utf-8")
        return json.loads(text).get("system_llm", {})
    except Exception:
        return {}


def get_system_llm_client() -> BaseLLM:
    """Return a configured LLM client for system-level calls.

    Raises RuntimeError if system_llm is not configured in agent_config.json.
    """
    cfg = _load_system_llm_config()
    if not cfg:
        raise RuntimeError(
            "system_llm is not configured in agent_config.json. "
            "Add a 'system_llm' section with provider, api_key, base_url, and model."
        )
    provider = cfg.get("provider", "openai")
    api_key = cfg.get("api_key", "")
    base_url = cfg.get("base_url", "")
    return get_llm_client(provider, api_key, base_url)


def get_system_model() -> str:
    """Return the model name configured for system-level calls."""
    return _load_system_llm_config().get("model", "gpt-3.5-turbo")


async def system_chat_completion(
    messages: list,
    stream: bool = False,
    extra_body: Dict[str, Any] | None = None,
) -> AsyncIterator[Dict[str, Any]]:
    """Convenience wrapper: call the system LLM with the given messages.

    Usage (non-streaming):
        async for chunk in system_chat_completion(messages):
            result = chunk

    Usage (streaming):
        async for chunk in system_chat_completion(messages, stream=True):
            ...
    """
    client = get_system_llm_client()
    model = get_system_model()
    async for chunk in client.chat_completion(messages, model, stream, extra_body):
        yield chunk
