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

When prompt_type is passed to system_chat_completion, the matching system prompt
is loaded from tb_system_prompt and prepended to the conversation automatically.
Each caller is responsible for supplying the appropriate prompt_type.
"""

import json
from pathlib import Path
from typing import Dict, Any, AsyncIterator, Optional

from sqlalchemy.orm import Session

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
    return get_llm_client(cfg.get("provider", "openai"), cfg.get("api_key", ""), cfg.get("base_url", ""))


def get_system_model() -> str:
    """Return the model name configured for system-level calls."""
    return _load_system_llm_config().get("model", "gpt-3.5-turbo")


def get_system_prompt_content(db: Session, prompt_type: str) -> Optional[str]:
    """Look up system prompt content by an explicit prompt_type.

    Returns None when prompt_type is empty or no matching record exists.
    """
    if not prompt_type or not prompt_type.strip():
        return None

    from ..models.system_prompt import SystemPrompt  # avoid circular import at module level

    sp = db.query(SystemPrompt).filter(SystemPrompt.prompt_type == prompt_type.strip()).first()
    return sp.content if sp else None


async def system_chat_completion(
    messages: list,
    stream: bool = False,
    extra_body: Dict[str, Any] | None = None,
    db: Optional[Session] = None,
    prompt_type: Optional[str] = None,
) -> AsyncIterator[Dict[str, Any]]:
    """Call the system LLM.

    When both db and prompt_type are supplied, the matching system prompt from
    tb_system_prompt is prepended to the messages as a system role message.

    Args:
        messages:    Conversation messages (list of dicts).
        stream:      Whether to stream the response.
        extra_body:  Extra parameters forwarded to the model API.
        db:          SQLAlchemy session used to look up the system prompt.
        prompt_type: Identifier of the system prompt to prepend.
                     The caller is responsible for passing the right value;
                     the memory module reads memory_processing.prompt_type
                     from agent_config.json and passes it here explicitly.

    Usage (non-streaming):
        async for chunk in system_chat_completion(messages, db=db, prompt_type="foo"):
            result = chunk

    Usage (streaming):
        async for chunk in system_chat_completion(messages, stream=True, db=db, prompt_type="foo"):
            ...
    """
    final_messages = list(messages)

    if db is not None and prompt_type:
        prompt_content = get_system_prompt_content(db, prompt_type)
        if prompt_content:
            final_messages = [{"role": "system", "content": prompt_content}] + final_messages

    client = get_system_llm_client()
    model = get_system_model()
    async for chunk in client.chat_completion(final_messages, model, stream, extra_body):
        yield chunk
