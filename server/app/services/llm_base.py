from abc import ABC, abstractmethod
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
_RESERVED_KEYS = frozenset({"model", "messages", "stream", "stream_options", "app_key"})


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

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.api_key or "none",
            base_url=self.base_url,
        )

    async def chat_completion(
        self,
        messages: list,
        model: str,
        stream: bool = False,
        extra_body: Dict[str, Any] | None = None,
    ):
        client = self._create_client()
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
