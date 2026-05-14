from abc import ABC, abstractmethod
import threading
from typing import Dict, Any, AsyncIterator

from openai import AsyncOpenAI
import openai


# OpenAI SDK chat.completions.create() accepted keyword params
_OPENAI_KNOWN_PARAMS = frozenset(
    {
        "temperature",
        "max_tokens",
        "max_completion_tokens",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "stop",
        "n",
        "logit_bias",
        "user",
        "response_format",
        "seed",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
        "logprobs",
        "top_logprobs",
        "timeout",
        "metadata",
    }
)

# Keys managed explicitly by chat_completion(); strip from extra_body
_RESERVED_KEYS = frozenset({"model", "messages", "stream", "stream_options", "app_key", "debug"})
_OPENAI_CLIENTS: dict[tuple[str, str], AsyncOpenAI] = {}
_OPENAI_CLIENTS_LOCK = threading.Lock()


async def close_openai_clients() -> None:
    with _OPENAI_CLIENTS_LOCK:
        clients = list(_OPENAI_CLIENTS.values())
        _OPENAI_CLIENTS.clear()
    for client in clients:
        try:
            await client.close()
        except RuntimeError as e:
            if "handler is closed" not in str(e):
                raise


def _split_extra_body(extra_body: dict | None) -> tuple[dict, dict]:
    """Split extra_body into (known_sdk_kwargs, vendor_extra_body)."""
    extras = {k: v for k, v in (extra_body or {}).items() if k not in _RESERVED_KEYS}
    known: dict = {}
    vendor: dict = {}
    for k, v in extras.items():
        (known if k in _OPENAI_KNOWN_PARAMS else vendor)[k] = v
    return known, vendor


class BaseLLM(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def chat_completion(
        self,
        messages: list,
        model: str,
        stream: bool = False,
        extra_body: Dict[str, Any] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass


class OpenAICompatibleLLM(BaseLLM):
    """OpenAI-SDK-based implementation for any OpenAI-compatible endpoint."""

    def _get_client(self) -> AsyncOpenAI:
        cache_key = (self.api_key or "", self.base_url or "")
        client = _OPENAI_CLIENTS.get(cache_key)
        if client is not None:
            return client
        with _OPENAI_CLIENTS_LOCK:
            client = _OPENAI_CLIENTS.get(cache_key)
            if client is None:
                print(f"Creating client with api_key: {self.api_key}, base_url: {self.base_url}")
                client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
                _OPENAI_CLIENTS[cache_key] = client
            return client

    async def chat_completion(
        self,
        messages: list,
        model: str,
        stream: bool = False,
        extra_body: Dict[str, Any] | None = None,
    ):
        client = self._get_client()
        known_kwargs, vendor_extra = _split_extra_body(extra_body)

        if stream:
            stream_options = {"include_usage": True}
            # Try with stream_options first; fall back if the endpoint rejects it
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    stream_options=stream_options,
                    extra_body=vendor_extra or None,
                    **known_kwargs,
                )
                async for chunk in response:
                    yield chunk.model_dump()
            except openai.BadRequestError:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    extra_body=vendor_extra or None,
                    **known_kwargs,
                )
                async for chunk in response:
                    yield chunk.model_dump()
        else:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                extra_body=vendor_extra or None,
                **known_kwargs,
            )
            yield response.model_dump()

    def count_tokens(self, text: str) -> int:
        return len(text) // 2


# Backward-compatible aliases
class QwenLLM(OpenAICompatibleLLM):
    pass
