from .llm_base import BaseLLM, QwenLLM

class DoubaoLLM(QwenLLM):
    pass

class DeepseekLLM(QwenLLM):
    pass

def get_llm_client(provider_name: str, api_key: str, base_url: str) -> BaseLLM:
    name = (provider_name or "").lower()
    if "千问" in provider_name or "qwen" in name:
        return QwenLLM(api_key, base_url)
    elif "豆包" in provider_name or "doubao" in name or "ark" in name:
        return DoubaoLLM(api_key, base_url)
    elif "deepseek" in name:
        return DeepseekLLM(api_key, base_url)
    return QwenLLM(api_key, base_url)
