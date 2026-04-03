from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator
import httpx
import json

class BaseLLM(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def chat_completion(
        self,
        messages: list,
        model: str,
        stream: bool = False
    ) -> AsyncIterator[Dict[str, Any]]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

class QwenLLM(BaseLLM):
    async def chat_completion(self, messages: list, model: str, stream: bool = False):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            if stream:
                async with client.stream("POST", f"{self.base_url}/chat/completions",
                                        headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:].strip()
                            if data == "[DONE]" or not data:
                                continue
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(f"{self.base_url}/chat/completions",
                                            headers=headers, json=payload)
                response.raise_for_status()
                yield response.json()

    def count_tokens(self, text: str) -> int:
        return len(text) // 2
