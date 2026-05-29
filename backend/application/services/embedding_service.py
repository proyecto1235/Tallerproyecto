from typing import Optional
from application.services.llm_service import LLMService
from infrastructure.adapters.output.redis.cache import AICache

class EmbeddingService:
    def __init__(self, llm_service: LLMService, cache: Optional[AICache] = None):
        self.llm = llm_service
        self.cache = cache

    async def embed_text(self, text: str) -> list[float]:
        if self.cache:
            try:
                cached = await self.cache.get_cached_embedding(text)
                if cached:
                    return cached
            except Exception:
                pass
        embedding = await self.llm.embed(text[:2000])
        if self.cache:
            try:
                await self.cache.cache_embedding(text, embedding)
            except Exception:
                pass
        return embedding

    def chunk_text(self, text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
        if len(text) <= max_chars:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            if end >= len(text):
                chunks.append(text[start:])
                break
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
