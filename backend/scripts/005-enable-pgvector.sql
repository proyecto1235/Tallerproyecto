-- Enable pgvector extension (requires pgvector/pgvector:pg16 image)
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge chunks table for RAG (requires pgvector)
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    source_type VARCHAR(50) NOT NULL,
    source_id INTEGER NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source ON knowledge_chunks(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
