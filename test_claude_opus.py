import aiohttp
import asyncio
import json

OLLAMA_URL = "http://192.168.1.53:11434/api/generate"


async def stream_generate(model: str, prompt: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": True}
        ) as resp:

            async for line in resp.content:
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))

                    # 流式输出
                    if "response" in data:
                        print(data["response"], end="", flush=True)

                    # 结束标志
                    if data.get("done"):
                        print("\n\n[Done]")
                        break

                except json.JSONDecodeError:
                    continue


async def main():
    await stream_generate(model="qwen3.5-27b_q4", prompt="用一句话解释什么是AI Agent")


if __name__ == "__main__":
    asyncio.run(main())
