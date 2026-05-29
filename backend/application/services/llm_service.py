import hashlib
import json
from typing import Optional
import httpx

class LLMService:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:1.5b", timeout: int = 120):
        self.base_url = ollama_url
        self.model = model
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.3, max_tokens: int = 500) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        resp = await self._client.post(f"{self.base_url}/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"]

    async def chat(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 500) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        resp = await self._client.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    async def embed(self, text: str) -> list[float]:
        resp = await self._client.post(f"{self.base_url}/api/embeddings", json={
            "model": self.model,
            "prompt": text,
        })
        resp.raise_for_status()
        return resp.json()["embedding"]

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get(f"{self.base_url}/api/tags")
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self._client.aclose()
