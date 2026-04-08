import json
from typing import Any, AsyncIterator, Dict

import aiohttp
from openai import AsyncOpenAI

from .llm_base import BaseLLM, OpenAICompatibleLLM, QwenLLM


class DoubaoLLM(OpenAICompatibleLLM):
    pass


class DeepseekLLM(OpenAICompatibleLLM):
    pass


class OllamaLLM(BaseLLM):
    """Ollama local inference via its native /api/generate streaming endpoint.

    Constructs the generate URL from base_url (strips trailing /v1 if present).
    Yields OpenAI-compatible chunk dicts so the rest of the pipeline is unchanged.
    """

    def _generate_url(self) -> str:
        base = (self.base_url or "http://localhost:11434").rstrip("/")
        # Remove /v1 suffix if configured as OpenAI-compat URL
        if base.endswith("/v1"):
            base = base[:-3]
        return f"{base}/api/generate"

    @staticmethod
    def _messages_to_prompt(messages: list) -> str:
        """Flatten chat messages into a single prompt string."""
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                parts.append(f"[System]: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(f"User: {content}")
        return "\n".join(parts)

    async def chat_completion(
        self,
        messages: list,
        model: str,
        stream: bool = False,
        extra_body: Dict[str, Any] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        url = self._generate_url()
        prompt = self._messages_to_prompt(messages)
        payload = {"model": model, "prompt": prompt, "stream": stream}
        print(f"----ollama url:{url} | model:{model}----")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if stream:
                    accumulated = ""
                    async for line in resp.content:
                        if not line:
                            continue
                        try:
                            data = json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue
                        token = data.get("response", "")
                        accumulated += token
                        done = data.get("done", False)

                        # Yield OpenAI-compatible streaming chunk
                        yield {
                            "id": "ollama-stream",
                            "object": "chat.completion.chunk",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"role": "assistant", "content": token},
                                    "finish_reason": "stop" if done else None,
                                }
                            ],
                            "usage": None,
                        }

                        if done:
                            break
                else:
                    # Non-streaming: collect all chunks then yield once
                    full_text = ""
                    async for line in resp.content:
                        if not line:
                            continue
                        try:
                            data = json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue
                        full_text += data.get("response", "")
                        if data.get("done"):
                            break

                    yield {
                        "id": "ollama-nonstream",
                        "object": "chat.completion",
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": full_text},
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": None,
                    }

    def count_tokens(self, text: str) -> int:
        return len(text) // 2


def get_llm_client(provider_name: str, api_key: str, base_url: str) -> BaseLLM:
    name = (provider_name or "").lower()
    print(
        f"----llm client created | name:{name} | api_key:{api_key} | base_url:{base_url}----"
    )
    if "ollama" in name:
        return OllamaLLM(api_key, base_url)
    if "千问" in provider_name or "qwen" in name:
        return QwenLLM(api_key, base_url)
    if "豆包" in provider_name or "doubao" in name or "ark" in name:
        return DoubaoLLM(api_key, base_url)
    if "deepseek" in name:
        return DeepseekLLM(api_key, base_url)
    return OpenAICompatibleLLM(api_key, base_url)
