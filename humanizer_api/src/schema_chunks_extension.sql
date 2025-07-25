-- Schema extension for storing content chunks with embeddings
-- This extends the existing archive schema to support full embeddings

-- Content chunks table for storing processed text chunks with embeddings
CREATE TABLE IF NOT EXISTS content_chunks (
    id SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES archived_content(id) ON DELETE CASCADE,
    chunk_type VARCHAR(20) NOT NULL DEFAULT 'content', -- 'content', 'summary_l1', 'summary_l2', 'summary_l3'
    text TEXT NOT NULL,
    embedding vector(768), -- nomic-text-embed produces 768-dimensional vectors
    position INTEGER NOT NULL DEFAULT 0, -- Position within the original content
    word_count INTEGER NOT NULL DEFAULT 0,
    summary_level INTEGER NOT NULL DEFAULT 0, -- 0=original, 1-3=summary levels
    chunk_hash VARCHAR(64), -- SHA-256 hash of text for deduplication
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embedding processing jobs table for tracking batch operations
CREATE TABLE IF NOT EXISTS embedding_jobs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL, -- UUID for grouping related processing
    content_id INTEGER REFERENCES archived_content(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'skipped'
    chunks_generated INTEGER DEFAULT 0,
    chunks_embedded INTEGER DEFAULT 0,
    error_message TEXT,
    processing_time_seconds FLOAT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embedding processing sessions for tracking overnight batch runs
CREATE TABLE IF NOT EXISTS embedding_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    session_name VARCHAR(200),
    total_content_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    total_chunks_generated INTEGER DEFAULT 0,
    total_chunks_embedded INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'paused'
    config JSONB, -- Configuration used for this session
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_content_chunks_content_id ON content_chunks(content_id);
CREATE INDEX IF NOT EXISTS idx_content_chunks_type_level ON content_chunks(chunk_type, summary_level);
CREATE INDEX IF NOT EXISTS idx_content_chunks_hash ON content_chunks(chunk_hash);
CREATE INDEX IF NOT EXISTS idx_content_chunks_created ON content_chunks(created_at);

-- Vector similarity index for semantic search
CREATE INDEX IF NOT EXISTS idx_content_chunks_embedding ON content_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Embedding jobs indexes
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_session_id ON embedding_jobs(session_id);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_status ON embedding_jobs(status);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_content_id ON embedding_jobs(content_id);

-- Embedding sessions indexes
CREATE INDEX IF NOT EXISTS idx_embedding_sessions_status ON embedding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_embedding_sessions_created ON embedding_sessions(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_content_chunks_updated_at 
    BEFORE UPDATE ON content_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for embedding statistics
CREATE OR REPLACE VIEW embedding_stats AS
SELECT 
    ac.id as content_id,
    ac.title,
    ac.author,
    ac.timestamp as content_created,
    COUNT(cc.id) as total_chunks,
    COUNT(cc.embedding) as embedded_chunks,
    COUNT(cc.embedding) * 100.0 / NULLIF(COUNT(cc.id), 0) as embedding_completion_pct,
    MAX(cc.created_at) as last_embedding_created,
    SUM(cc.word_count) as total_chunk_words,
    COUNT(CASE WHEN cc.summary_level = 0 THEN 1 END) as content_chunks,
    COUNT(CASE WHEN cc.summary_level = 1 THEN 1 END) as summary_l1_chunks,
    COUNT(CASE WHEN cc.summary_level = 2 THEN 1 END) as summary_l2_chunks,
    COUNT(CASE WHEN cc.summary_level = 3 THEN 1 END) as summary_l3_chunks
FROM archived_content ac
LEFT JOIN content_chunks cc ON ac.id = cc.content_id
GROUP BY ac.id, ac.title, ac.author, ac.timestamp;

-- View for session progress
CREATE OR REPLACE VIEW session_progress AS
SELECT 
    es.session_id,
    es.session_name,
    es.status as session_status,
    es.total_content_items,
    es.processed_items,
    es.failed_items,
    es.total_chunks_generated,
    es.total_chunks_embedded,
    ROUND(es.processed_items * 100.0 / NULLIF(es.total_content_items, 0), 2) as completion_pct,
    es.started_at,
    es.completed_at,
    EXTRACT(EPOCH FROM (COALESCE(es.completed_at, NOW()) - es.started_at)) as duration_seconds,
    COUNT(ej.id) as total_jobs,
    COUNT(CASE WHEN ej.status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN ej.status = 'failed' THEN 1 END) as failed_jobs,
    COUNT(CASE WHEN ej.status = 'processing' THEN 1 END) as processing_jobs
FROM embedding_sessions es
LEFT JOIN embedding_jobs ej ON es.session_id = ej.session_id
GROUP BY es.session_id, es.session_name, es.status, es.total_content_items, 
         es.processed_items, es.failed_items, es.total_chunks_generated, 
         es.total_chunks_embedded, es.started_at, es.completed_at;

-- Function to get content items needing embeddings
CREATE OR REPLACE FUNCTION get_content_needing_embeddings(limit_count INTEGER DEFAULT 100)
RETURNS TABLE(
    content_id INTEGER,
    title TEXT,
    author TEXT,
    content_type TEXT,
    content_length INTEGER,
    existing_chunks INTEGER,
    needs_processing BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ac.id::INTEGER,
        ac.title::TEXT,
        ac.author::TEXT,
        ac.content_type::TEXT,
        LENGTH(ac.content)::INTEGER as content_length,
        COALESCE(chunk_counts.chunk_count, 0)::INTEGER as existing_chunks,
        (COALESCE(chunk_counts.chunk_count, 0) = 0 OR 
         COALESCE(chunk_counts.embedded_count, 0) < COALESCE(chunk_counts.chunk_count, 0))::BOOLEAN as needs_processing
    FROM archived_content ac
    LEFT JOIN (
        SELECT 
            content_id,
            COUNT(*) as chunk_count,
            COUNT(embedding) as embedded_count
        FROM content_chunks 
        GROUP BY content_id
    ) chunk_counts ON ac.id = chunk_counts.content_id
    WHERE ac.content IS NOT NULL 
      AND LENGTH(ac.content) > 10 -- Skip very short content
    ORDER BY 
        -- Prioritize by activity and completeness
        CASE WHEN chunk_counts.chunk_count IS NULL THEN 0 ELSE 1 END, -- No chunks processed
        CASE WHEN chunk_counts.embedded_count < chunk_counts.chunk_count THEN 0 ELSE 1 END, -- Partial embeddings
        ac.timestamp DESC -- Most recent first
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to search content by semantic similarity
CREATE OR REPLACE FUNCTION search_content_semantic(
    query_embedding vector(768),
    similarity_threshold FLOAT DEFAULT 0.7,
    result_limit INTEGER DEFAULT 20
)
RETURNS TABLE(
    content_id INTEGER,
    chunk_id INTEGER,
    chunk_text TEXT,
    chunk_type TEXT,
    similarity_score FLOAT,
    content_title TEXT,
    content_author TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cc.content_id::INTEGER,
        cc.id::INTEGER as chunk_id,
        cc.text::TEXT as chunk_text,
        cc.chunk_type::TEXT,
        (1 - (cc.embedding <=> query_embedding))::FLOAT as similarity_score,
        ac.title::TEXT as content_title,
        ac.author::TEXT as content_author
    FROM content_chunks cc
    JOIN archived_content ac ON cc.content_id = ac.id
    WHERE cc.embedding IS NOT NULL
      AND (1 - (cc.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY cc.embedding <=> query_embedding
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON content_chunks TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON embedding_jobs TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON embedding_sessions TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE content_chunks_id_seq TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE embedding_jobs_id_seq TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE embedding_sessions_id_seq TO your_app_user;