import json
from typing import Optional
from application.services.llm_service import LLMService
from application.services.embedding_service import EmbeddingService
from infrastructure.adapters.output.postgres.connection import PostgresConnection

class RAGService:
    def __init__(self, embedding_service: EmbeddingService, llm_service: Optional[LLMService] = None):
        self.embedder = embedding_service
        self.llm = llm_service

    async def index_content(self, text: str, source_type: str, source_id: int, metadata: dict = None):
        chunks = self.embedder.chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = await self.embedder.embed_text(chunk)
            meta = json.dumps(metadata or {})
            with PostgresConnection.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO knowledge_chunks (chunk_text, metadata, embedding, source_type, source_id, chunk_index)
                    VALUES (%s, %s, %s::vector, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (chunk, meta, embedding, source_type, source_id, i))

    async def search(self, query: str, top_k: int = 5, source_type: str = None) -> list[dict]:
        query_embedding = await self.embedder.embed_text(query)
        filters = ""
        params = [query_embedding, query_embedding, top_k]
        if source_type:
            filters = "AND source_type = %s"
            params.insert(2, source_type)
        sql = f"""
            SELECT chunk_text, metadata, source_type, source_id,
                   1 - (embedding <=> %s::vector) as similarity
            FROM knowledge_chunks
            WHERE 1=1 {filters}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        with PostgresConnection.get_cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            results = []
            for r in rows:
                try:
                    meta = json.loads(r[1]) if isinstance(r[1], str) else r[1]
                except (json.JSONDecodeError, TypeError):
                    meta = {}
                results.append({
                    "text": r[0],
                    "metadata": meta,
                    "source_type": r[2],
                    "source_id": r[3],
                    "similarity": float(r[4]) if r[4] else 0.0,
                })
            return results

    async def build_context(self, query: str, top_k: int = 3) -> str:
        results = await self.search(query, top_k=top_k)
        if not results:
            return ""
        context_parts = []
        for r in results:
            context_parts.append(f"[{r['source_type']}] {r['text']}")
        return "\n\n".join(context_parts)
