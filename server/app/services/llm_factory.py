from .llm_base import BaseLLM, QwenLLM

class DoubaoLLM(BaseLLM):
    async def chat_completion(self, messages: list, model: str, stream: bool = False):
        # 字节豆包实现
        pass

    def count_tokens(self, text: str) -> int:
        return len(text) // 2

class DeepseekLLM(BaseLLM):
    async def chat_completion(self, messages: list, model: str, stream: bool = False):
        # Deepseek实现
        pass

    def count_tokens(self, text: str) -> int:
        return len(text) // 2

def get_llm_client(provider_name: str, api_key: str, base_url: str) -> BaseLLM:
    if "千问" in provider_name or "qwen" in provider_name.lower():
        return QwenLLM(api_key, base_url)
    elif "豆包" in provider_name or "doubao" in provider_name.lower():
        return DoubaoLLM(api_key, base_url)
    elif "deepseek" in provider_name.lower():
        return DeepseekLLM(api_key, base_url)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
