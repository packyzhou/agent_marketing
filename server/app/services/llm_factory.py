from openai import AsyncOpenAI

from .llm_base import BaseLLM, OpenAICompatibleLLM, QwenLLM


class DoubaoLLM(OpenAICompatibleLLM):
    pass


class DeepseekLLM(OpenAICompatibleLLM):
    pass


class OllamaLLM(OpenAICompatibleLLM):
    """Ollama local inference via its OpenAI-compatible endpoint.

    Ollama does not require authentication and typically runs at
    http://localhost:11434/v1. stream_options is not supported, so the
    base-class fallback handles that transparently.
    """

    _DEFAULT_BASE_URL = "http://localhost:11434/v1"

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.api_key or "ollama",
            base_url=self.base_url or self._DEFAULT_BASE_URL,
        )


def get_llm_client(provider_name: str, api_key: str, base_url: str) -> BaseLLM:
    name = (provider_name or "").lower()
    if "ollama" in name:
        return OllamaLLM(api_key, base_url)
    if "千问" in provider_name or "qwen" in name:
        return QwenLLM(api_key, base_url)
    if "豆包" in provider_name or "doubao" in name or "ark" in name:
        return DoubaoLLM(api_key, base_url)
    if "deepseek" in name:
        return DeepseekLLM(api_key, base_url)
    return OpenAICompatibleLLM(api_key, base_url)
