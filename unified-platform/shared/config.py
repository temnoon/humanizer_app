"""
Unified Configuration Management
Centralizes ALL configurable values - no magic numbers anywhere!
"""
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
import os


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class LLMProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GROQ = "groq"
    TOGETHER = "together"


class DatabaseConfig(BaseSettings):
    """Database configuration with all connection parameters"""
    url: str = Field(..., description="Full database URL")
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(20, description="Max overflow connections")
    pool_timeout: int = Field(30, description="Pool timeout seconds")
    pool_recycle: int = Field(3600, description="Pool recycle seconds")
    echo: bool = Field(False, description="Echo SQL queries")


class RedisConfig(BaseSettings):
    """Redis configuration"""
    url: str = Field(..., description="Redis connection URL")
    max_connections: int = Field(50, description="Max Redis connections")
    socket_timeout: int = Field(30, description="Socket timeout seconds")
    socket_connect_timeout: int = Field(30, description="Connect timeout seconds")
    retry_on_timeout: bool = Field(True, description="Retry on timeout")


class VectorDBConfig(BaseSettings):
    """Vector database configuration"""
    path: str = Field("./vectordb", description="ChromaDB storage path")
    collection_name: str = Field("humanizer_vectors", description="Default collection")
    embedding_dimension: int = Field(1536, description="Embedding vector dimension")
    similarity_threshold: float = Field(0.7, description="Similarity search threshold")
    max_results: int = Field(50, description="Max search results")
    batch_size: int = Field(100, description="Batch processing size")


class LLMConfig(BaseSettings):
    """LLM provider configuration with all parameters"""
    default_provider: LLMProvider = Field(LLMProvider.DEEPSEEK, description="Primary LLM provider")
    fallback_providers: List[LLMProvider] = Field(
        [LLMProvider.DEEPSEEK, LLMProvider.OLLAMA, LLMProvider.OPENAI],
        description="Fallback provider order"
    )
    
    # Model specifications
    default_model: str = Field("deepseek-chat", description="Default model name")
    embedding_model: str = Field("text-embedding-ada-002", description="Embedding model")
    vision_model: str = Field("gpt-4-vision-preview", description="Vision analysis model")
    
    # Request parameters
    max_tokens: int = Field(4096, description="Max tokens per request")
    temperature: float = Field(0.7, description="Default temperature")
    timeout_seconds: int = Field(30, description="Request timeout")
    max_retries: int = Field(3, description="Max retry attempts")
    retry_delay: float = Field(1.0, description="Retry delay seconds")
    
    # Rate limiting
    requests_per_minute: int = Field(60, description="Requests per minute limit")
    tokens_per_minute: int = Field(40000, description="Tokens per minute limit")
    
    # Cost tracking
    enable_cost_tracking: bool = Field(True, description="Track API costs")
    monthly_budget_usd: float = Field(100.0, description="Monthly budget limit")


class CacheConfig(BaseSettings):
    """Caching configuration for all cache layers"""
    # Local cache (in-memory)
    local_ttl_seconds: int = Field(300, description="Local cache TTL")
    local_max_size: int = Field(1000, description="Local cache max items")
    
    # Redis cache (distributed)
    redis_ttl_seconds: int = Field(3600, description="Redis cache TTL")
    redis_key_prefix: str = Field("humanizer:", description="Redis key prefix")
    
    # Embedding cache
    embedding_ttl_seconds: int = Field(86400, description="Embedding cache TTL (24h)")
    
    # LLM response cache
    llm_response_ttl_seconds: int = Field(7200, description="LLM response cache TTL")
    
    # File processing cache
    file_processing_ttl_seconds: int = Field(1800, description="File processing cache TTL")


class SecurityConfig(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(..., description="App secret key")
    jwt_secret_key: str = Field(..., description="JWT signing key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(30, description="JWT expiration minutes")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(100, description="API rate limit per minute")
    rate_limit_burst: int = Field(10, description="Rate limit burst allowance")
    
    # CORS
    cors_origins: List[str] = Field(["*"], description="Allowed CORS origins")
    cors_methods: List[str] = Field(["GET", "POST", "PUT", "DELETE"], description="Allowed HTTP methods")
    
    # Request limits
    max_request_size_mb: int = Field(100, description="Max request size in MB")
    max_file_size_mb: int = Field(50, description="Max file upload size in MB")


class ProcessingConfig(BaseSettings):
    """Content processing configuration"""
    # Text processing
    max_text_length: int = Field(50000, description="Max text length for processing")
    chunk_size: int = Field(1000, description="Text chunking size")
    chunk_overlap: int = Field(200, description="Chunk overlap size")
    
    # Batch processing
    batch_size: int = Field(10, description="Batch processing size")
    max_concurrent_jobs: int = Field(5, description="Max concurrent processing jobs")
    job_timeout_seconds: int = Field(300, description="Job timeout seconds")
    
    # Quality thresholds
    quality_threshold: float = Field(0.6, description="Content quality threshold")
    coherence_threshold: float = Field(0.7, description="Coherence threshold")
    toxicity_threshold: float = Field(0.3, description="Toxicity detection threshold")
    
    # Transformation parameters
    max_transformation_iterations: int = Field(3, description="Max transformation iterations")
    transformation_timeout_seconds: int = Field(60, description="Transformation timeout")


class APIConfig(BaseSettings):
    """API server configuration"""
    host: str = Field("0.0.0.0", description="API host")
    port: int = Field(8100, description="API port")
    workers: int = Field(4, description="Number of worker processes")
    reload: bool = Field(False, description="Auto-reload on changes")
    
    # Request handling
    request_timeout_seconds: int = Field(30, description="Request timeout")
    keepalive_timeout_seconds: int = Field(5, description="Keep-alive timeout")
    max_concurrent_requests: int = Field(1000, description="Max concurrent requests")
    
    # WebSocket configuration
    websocket_ping_interval: int = Field(20, description="WebSocket ping interval")
    websocket_ping_timeout: int = Field(10, description="WebSocket ping timeout")
    websocket_max_size: int = Field(16777216, description="Max WebSocket message size")


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration"""
    # Logging
    log_level: LogLevel = Field(LogLevel.INFO, description="Logging level")
    log_format: LogFormat = Field(LogFormat.JSON, description="Log format")
    log_file_path: Optional[str] = Field(None, description="Log file path")
    log_rotation_size_mb: int = Field(100, description="Log rotation size in MB")
    log_retention_days: int = Field(30, description="Log retention days")
    
    # Metrics
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    metrics_port: int = Field(9090, description="Metrics server port")
    
    # Health checks
    health_check_interval_seconds: int = Field(30, description="Health check interval")
    dependency_timeout_seconds: int = Field(5, description="Dependency check timeout")


class ExternalServiceConfig(BaseSettings):
    """External service URLs and timeouts"""
    # Legacy services (during migration)
    archive_service_url: str = Field("http://localhost:7200", description="Archive API URL")
    lpe_service_url: str = Field("http://localhost:7201", description="LPE API URL")
    lighthouse_service_url: str = Field("http://localhost:8100", description="Lighthouse API URL")
    
    # Service timeouts
    service_timeout_seconds: int = Field(30, description="External service timeout")
    service_retry_attempts: int = Field(3, description="Service retry attempts")
    service_retry_delay: float = Field(1.0, description="Service retry delay")


class UnifiedConfig(BaseSettings):
    """Main configuration class combining all sub-configurations"""
    
    # Environment
    environment: Environment = Field(Environment.DEVELOPMENT, description="Runtime environment")
    debug: bool = Field(False, description="Debug mode")
    
    # Sub-configurations
    database: DatabaseConfig
    redis: RedisConfig
    vectordb: VectorDBConfig
    llm: LLMConfig
    cache: CacheConfig
    security: SecurityConfig
    processing: ProcessingConfig
    api: APIConfig
    monitoring: MonitoringConfig
    external_services: ExternalServiceConfig
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("database", pre=True)
    def parse_database_config(cls, v):
        if isinstance(v, str):
            return DatabaseConfig(url=v)
        return DatabaseConfig(**v) if isinstance(v, dict) else v
    
    @validator("redis", pre=True)
    def parse_redis_config(cls, v):
        if isinstance(v, str):
            return RedisConfig(url=v)
        return RedisConfig(**v) if isinstance(v, dict) else v
    
    def get_llm_provider_config(self, provider: LLMProvider) -> Dict[str, Any]:
        """Get provider-specific configuration"""
        base_config = {
            "timeout": self.llm.timeout_seconds,
            "max_retries": self.llm.max_retries,
            "max_tokens": self.llm.max_tokens,
            "temperature": self.llm.temperature,
        }
        
        provider_configs = {
            LLMProvider.DEEPSEEK: {
                **base_config,
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
            },
            LLMProvider.OPENAI: {
                **base_config,
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4-turbo-preview",
            },
            LLMProvider.ANTHROPIC: {
                **base_config,
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": "claude-3-sonnet-20240229",
            },
            LLMProvider.OLLAMA: {
                **base_config,
                "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                "model": "llama2:7b",
                "api_key": None,  # Ollama doesn't need API key
            }
        }
        
        return provider_configs.get(provider, base_config)


# Global configuration instance
def get_config() -> UnifiedConfig:
    """Get the global configuration instance"""
    return UnifiedConfig(
        database=DatabaseConfig(url=os.getenv("DATABASE_URL", "sqlite:///./test.db")),
        redis=RedisConfig(url=os.getenv("REDIS_URL", "redis://localhost:6379/0")),
        vectordb=VectorDBConfig(),
        llm=LLMConfig(),
        cache=CacheConfig(),
        security=SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
        ),
        processing=ProcessingConfig(),
        api=APIConfig(),
        monitoring=MonitoringConfig(),
        external_services=ExternalServiceConfig()
    )


# Export for easy importing
config = get_config()