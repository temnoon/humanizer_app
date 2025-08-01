-- Unified Humanizer Platform Database Schema
-- Consolidates all data structures with proper indexing and constraints

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector" CASCADE;

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS transformations;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================================================
-- USER MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE users.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    api_quota_used INTEGER DEFAULT 0,
    api_quota_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_username CHECK (username ~* '^[a-zA-Z0-9_]+$'),
    CONSTRAINT positive_quota CHECK (api_quota_limit >= 0 AND api_quota_used >= 0)
);

CREATE INDEX idx_users_username ON users.users(username);
CREATE INDEX idx_users_email ON users.users(email);
CREATE INDEX idx_users_active ON users.users(is_active) WHERE is_active = TRUE;

-- API Keys for programmatic access
CREATE TABLE users.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_expiry CHECK (expires_at IS NULL OR expires_at > created_at)
);

CREATE INDEX idx_api_keys_user ON users.api_keys(user_id);
CREATE INDEX idx_api_keys_active ON users.api_keys(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- CONTENT MANAGEMENT TABLES
-- ============================================================================

-- Content types enumeration
CREATE TYPE content.content_type_enum AS ENUM (
    'text', 'html', 'markdown', 'json', 'pdf', 'image', 'video', 'audio'
);

-- Processing status enumeration
CREATE TYPE content.processing_status_enum AS ENUM (
    'pending', 'processing', 'completed', 'failed', 'cancelled'
);

-- Main content table
CREATE TABLE content.contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type content.content_type_enum NOT NULL,
    data TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    embedding VECTOR(1536), -- OpenAI ada-002 dimension
    processing_status content.processing_status_enum DEFAULT 'pending',
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),
    file_size INTEGER,
    checksum VARCHAR(64), -- SHA-256 hash for deduplication
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users.users(id) ON DELETE SET NULL,
    
    -- Metadata validation
    CONSTRAINT valid_metadata CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT valid_file_size CHECK (file_size IS NULL OR file_size >= 0),
    CONSTRAINT valid_checksum CHECK (checksum IS NULL OR length(checksum) = 64)
);

-- Indexes for content
CREATE INDEX idx_contents_type ON content.contents(content_type);
CREATE INDEX idx_contents_status ON content.contents(processing_status);
CREATE INDEX idx_contents_created_at ON content.contents(created_at DESC);
CREATE INDEX idx_contents_quality ON content.contents(quality_score DESC) WHERE quality_score IS NOT NULL;
CREATE INDEX idx_contents_creator ON content.contents(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX idx_contents_checksum ON content.contents(checksum) WHERE checksum IS NOT NULL;

-- GIN indexes for JSONB metadata
CREATE INDEX idx_contents_metadata_gin ON content.contents USING GIN(metadata);
CREATE INDEX idx_contents_source ON content.contents USING GIN((metadata->'source'));
CREATE INDEX idx_contents_tags ON content.contents USING GIN((metadata->'tags'));

-- Vector similarity index
CREATE INDEX idx_contents_embedding_cosine ON content.contents 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search index
CREATE INDEX idx_contents_fts ON content.contents USING GIN(to_tsvector('english', data));

-- Content versions for tracking changes
CREATE TABLE content.content_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES content.contents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users.users(id) ON DELETE SET NULL,
    
    UNIQUE(content_id, version_number),
    CONSTRAINT positive_version CHECK (version_number > 0)
);

CREATE INDEX idx_content_versions_content ON content.content_versions(content_id, version_number DESC);

-- ============================================================================
-- TRANSFORMATION TABLES
-- ============================================================================

-- Transformation engines
CREATE TYPE transformations.engine_enum AS ENUM (
    'lpe', 'quantum', 'maieutic', 'translation', 'vision'
);

-- Transformation requests and results
CREATE TABLE transformations.transformation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content.contents(id) ON DELETE CASCADE,
    engine transformations.engine_enum NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}',
    options JSONB NOT NULL DEFAULT '{}',
    status content.processing_status_enum DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users.users(id) ON DELETE SET NULL,
    
    CONSTRAINT valid_attributes CHECK (jsonb_typeof(attributes) = 'object'),
    CONSTRAINT valid_options CHECK (jsonb_typeof(options) = 'object')
);

CREATE INDEX idx_transform_requests_content ON transformations.transformation_requests(content_id);
CREATE INDEX idx_transform_requests_engine ON transformations.transformation_requests(engine);
CREATE INDEX idx_transform_requests_status ON transformations.transformation_requests(status);
CREATE INDEX idx_transform_requests_created ON transformations.transformation_requests(created_at DESC);

-- Transformation results
CREATE TABLE transformations.transformation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES transformations.transformation_requests(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    transformed_text TEXT NOT NULL,
    quality_metrics JSONB DEFAULT '{}',
    processing_time_ms INTEGER NOT NULL,
    token_usage JSONB DEFAULT '{}',
    cost_usd DECIMAL(10,6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT positive_processing_time CHECK (processing_time_ms >= 0),
    CONSTRAINT valid_cost CHECK (cost_usd IS NULL OR cost_usd >= 0),
    CONSTRAINT valid_metrics CHECK (jsonb_typeof(quality_metrics) = 'object'),
    CONSTRAINT valid_token_usage CHECK (jsonb_typeof(token_usage) = 'object')
);

CREATE INDEX idx_transform_results_request ON transformations.transformation_results(request_id);
CREATE INDEX idx_transform_results_created ON transformations.transformation_results(created_at DESC);
CREATE INDEX idx_transform_results_cost ON transformations.transformation_results(cost_usd DESC) WHERE cost_usd IS NOT NULL;

-- Batch processing jobs
CREATE TABLE transformations.batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_items INTEGER NOT NULL,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    status content.processing_status_enum DEFAULT 'pending',
    estimated_completion TIMESTAMP WITH TIME ZONE,
    error_messages JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users.users(id) ON DELETE SET NULL,
    
    CONSTRAINT positive_items CHECK (total_items > 0 AND processed_items >= 0 AND failed_items >= 0),
    CONSTRAINT valid_completion CHECK (processed_items + failed_items <= total_items),
    CONSTRAINT valid_errors CHECK (jsonb_typeof(error_messages) = 'array')
);

CREATE INDEX idx_batch_jobs_status ON transformations.batch_jobs(status);
CREATE INDEX idx_batch_jobs_created ON transformations.batch_jobs(created_at DESC);
CREATE INDEX idx_batch_jobs_creator ON transformations.batch_jobs(created_by) WHERE created_by IS NOT NULL;

-- Individual batch items
CREATE TABLE transformations.batch_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES transformations.batch_jobs(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES content.contents(id) ON DELETE CASCADE,
    result_id UUID REFERENCES transformations.transformation_results(id) ON DELETE SET NULL,
    status content.processing_status_enum DEFAULT 'pending',
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT positive_processing_time CHECK (processing_time_ms IS NULL OR processing_time_ms >= 0)
);

CREATE INDEX idx_batch_items_job ON transformations.batch_items(job_id, status);
CREATE INDEX idx_batch_items_content ON transformations.batch_items(content_id);

-- ============================================================================
-- ANALYTICS AND MONITORING TABLES
-- ============================================================================

-- API usage tracking
CREATE TABLE analytics.api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users.users(id) ON DELETE SET NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_status_code CHECK (status_code >= 100 AND status_code < 600),
    CONSTRAINT positive_times CHECK (response_time_ms >= 0),
    CONSTRAINT positive_sizes CHECK (
        (request_size_bytes IS NULL OR request_size_bytes >= 0) AND
        (response_size_bytes IS NULL OR response_size_bytes >= 0)
    )
);

-- Partition by month for performance
CREATE INDEX idx_api_usage_created_at ON analytics.api_usage(created_at DESC);
CREATE INDEX idx_api_usage_user ON analytics.api_usage(user_id, created_at DESC) WHERE user_id IS NOT NULL;
CREATE INDEX idx_api_usage_endpoint ON analytics.api_usage(endpoint, created_at DESC);
CREATE INDEX idx_api_usage_status ON analytics.api_usage(status_code, created_at DESC);

-- Error tracking
CREATE TABLE analytics.error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context JSONB DEFAULT '{}',
    user_id UUID REFERENCES users.users(id) ON DELETE SET NULL,
    request_id UUID,
    endpoint VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_context CHECK (jsonb_typeof(context) = 'object')
);

CREATE INDEX idx_error_logs_type ON analytics.error_logs(error_type, created_at DESC);
CREATE INDEX idx_error_logs_created ON analytics.error_logs(created_at DESC);
CREATE INDEX idx_error_logs_user ON analytics.error_logs(user_id) WHERE user_id IS NOT NULL;

-- Performance metrics
CREATE TABLE analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_tags CHECK (jsonb_typeof(tags) = 'object')
);

-- Time-series index for metrics
CREATE INDEX idx_performance_metrics_name_time ON analytics.performance_metrics(metric_name, created_at DESC);
CREATE INDEX idx_performance_metrics_tags ON analytics.performance_metrics USING GIN(tags);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_contents_updated_at 
    BEFORE UPDATE ON content.contents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Content deduplication function
CREATE OR REPLACE FUNCTION check_content_duplicate()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if content with same checksum already exists
    IF NEW.checksum IS NOT NULL AND EXISTS (
        SELECT 1 FROM content.contents 
        WHERE checksum = NEW.checksum AND id != COALESCE(NEW.id, uuid_nil())
    ) THEN
        RAISE NOTICE 'Duplicate content detected with checksum: %', NEW.checksum;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER check_content_duplicate_trigger
    BEFORE INSERT OR UPDATE ON content.contents
    FOR EACH ROW EXECUTE FUNCTION check_content_duplicate();

-- Batch job progress update function
CREATE OR REPLACE FUNCTION update_batch_progress()
RETURNS TRIGGER AS $$
BEGIN
    -- Update parent job progress when batch item status changes
    IF NEW.status != OLD.status THEN
        UPDATE transformations.batch_jobs 
        SET 
            processed_items = (
                SELECT COUNT(*) FROM transformations.batch_items 
                WHERE job_id = NEW.job_id AND status = 'completed'
            ),
            failed_items = (
                SELECT COUNT(*) FROM transformations.batch_items 
                WHERE job_id = NEW.job_id AND status = 'failed'
            )
        WHERE id = NEW.job_id;
        
        -- Update job status if all items are complete
        UPDATE transformations.batch_jobs 
        SET 
            status = CASE 
                WHEN processed_items + failed_items = total_items THEN 'completed'
                WHEN failed_items > 0 AND processed_items + failed_items = total_items THEN 'failed'
                ELSE status
            END,
            completed_at = CASE 
                WHEN processed_items + failed_items = total_items THEN NOW()
                ELSE completed_at
            END
        WHERE id = NEW.job_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_batch_progress_trigger
    AFTER UPDATE ON transformations.batch_items
    FOR EACH ROW EXECUTE FUNCTION update_batch_progress();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Content with latest transformations
CREATE VIEW content.content_with_transformations AS
SELECT 
    c.*,
    tr.id as latest_transformation_id,
    tr.engine as latest_engine,
    tr.transformed_text as latest_transformed_text,
    tr.quality_metrics as latest_quality_metrics
FROM content.contents c
LEFT JOIN LATERAL (
    SELECT tr.id, tr.engine, res.transformed_text, res.quality_metrics
    FROM transformations.transformation_requests tr
    JOIN transformations.transformation_results res ON tr.id = res.request_id
    WHERE tr.content_id = c.id AND tr.status = 'completed'
    ORDER BY tr.created_at DESC
    LIMIT 1
) tr ON true;

-- User activity summary
CREATE VIEW analytics.user_activity_summary AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT c.id) as contents_created,
    COUNT(DISTINCT tr.id) as transformations_requested,
    COUNT(DISTINCT au.id) as api_calls_made,
    MAX(au.created_at) as last_activity
FROM users.users u
LEFT JOIN content.contents c ON u.id = c.created_by
LEFT JOIN transformations.transformation_requests tr ON u.id = tr.created_by
LEFT JOIN analytics.api_usage au ON u.id = au.user_id
GROUP BY u.id, u.username;

-- Performance dashboard
CREATE VIEW analytics.performance_dashboard AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time,
    COUNT(*) FILTER (WHERE status_code >= 400) as error_count,
    COUNT(*) FILTER (WHERE status_code >= 500) as server_error_count
FROM analytics.api_usage
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default admin user (password: 'admin123' - change in production!)
INSERT INTO users.users (username, email, password_hash, is_admin) VALUES 
('admin', 'admin@humanizer.com', crypt('admin123', gen_salt('bf')), true)
ON CONFLICT (username) DO NOTHING;

-- Create indexes for optimal query performance
ANALYZE;