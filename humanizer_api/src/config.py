"""
Humanizer API Configuration Management

Centralized configuration with environment variable support and validation.
Integrates with ChromaDB Memory for configuration learning and best practices.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    
    # ChromaDB Memory
    chromadb_path: str = Field(default="./chromadb_data", env="CHROMADB_PATH")
    chromadb_host: str = Field(default="localhost", env="CHROMADB_HOST")
    chromadb_port: int = Field(default=8000, env="CHROMADB_PORT")
    
    # PostgreSQL (optional)
    postgres_url: Optional[str] = Field(default=None, env="POSTGRES_URL")
    
    # SQLite (fallback)
    sqlite_path: str = Field(default="./data/humanizer.db", env="SQLITE_PATH")

class LLMConfig(BaseSettings):
    """LLM provider configuration"""
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # DeepSeek (cost-effective)
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    # Ollama (local)
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")
    
    # Provider selection and fallback
    preferred_provider: str = Field(default="deepseek", env="LLM_PREFERRED_PROVIDER")
    fallback_providers: List[str] = Field(default=["ollama", "openai", "anthropic"])
    
    # Generation parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    timeout: int = Field(default=60, ge=1, le=300)

class APIConfig(BaseSettings):
    """API service configuration"""
    
    # Service ports
    archive_api_port: int = Field(default=7200, env="ARCHIVE_API_PORT")
    lpe_api_port: int = Field(default=7201, env="LPE_API_PORT") 
    lawyer_api_port: int = Field(default=7202, env="LAWYER_API_PORT")
    pulse_api_port: int = Field(default=7203, env="PULSE_API_PORT")
    
    # API settings
    host: str = Field(default="0.0.0.0", env="API_HOST")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Request timeout
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")

class DiscourseConfig(BaseSettings):
    """Discourse platform integration"""
    
    url: str = Field(default="https://humanizer.com", env="DISCOURSE_URL")
    api_key: Optional[str] = Field(default=None, env="DISCOURSE_API_KEY")
    username: str = Field(default="api_user", env="DISCOURSE_USERNAME")
    
    # Publishing settings
    default_category: str = Field(default="general", env="DISCOURSE_DEFAULT_CATEGORY")
    auto_publish: bool = Field(default=False, env="DISCOURSE_AUTO_PUBLISH")
    require_approval: bool = Field(default=True, env="DISCOURSE_REQUIRE_APPROVAL")
    
    # Quality thresholds
    min_quality_score: float = Field(default=0.7, ge=0.0, le=1.0)
    max_retry_attempts: int = Field(default=3, ge=1, le=10)

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    file_path: str = Field(default="./logs/humanizer_api.log", env="LOG_FILE")
    max_file_size: str = Field(default="10MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Format
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    
    @validator('level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

class SecurityConfig(BaseSettings):
    """Security and authentication settings"""
    
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE")
    
    # Content safety
    enable_content_filter: bool = Field(default=True, env="ENABLE_CONTENT_FILTER")
    max_content_length: int = Field(default=50000, env="MAX_CONTENT_LENGTH")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")

class HumanizerConfig(BaseSettings):
    """Main configuration class combining all settings"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    version: str = "1.0.0"
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    discourse: DiscourseConfig = Field(default_factory=DiscourseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Project paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("./data"))
    logs_dir: Path = Field(default_factory=lambda: Path("./logs"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
        self._setup_logging()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.data_dir,
            self.logs_dir,
            Path(self.database.chromadb_path),
            Path(self.database.sqlite_path).parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.logging.level),
            format=self.logging.format,
            datefmt=self.logging.date_format,
            handlers=[
                logging.FileHandler(self.logging.file_path),
                logging.StreamHandler()
            ]
        )
        
        # Set third-party library log levels
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("chromadb").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.INFO)

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for the preferred provider"""
        provider = self.llm.preferred_provider.lower()
        
        config_map = {
            "openai": {
                "api_key": self.llm.openai_api_key,
                "model": self.llm.openai_model,
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": {
                "api_key": self.llm.anthropic_api_key,
                "model": self.llm.anthropic_model,
                "base_url": "https://api.anthropic.com"
            },
            "deepseek": {
                "api_key": self.llm.deepseek_api_key,
                "model": self.llm.deepseek_model,
                "base_url": "https://api.deepseek.com/v1"
            },
            "ollama": {
                "model": self.llm.ollama_model,
                "base_url": self.llm.ollama_host
            }
        }
        
        return config_map.get(provider, config_map["ollama"])

    def get_database_url(self) -> str:
        """Get appropriate database URL"""
        if self.database.postgres_url:
            return self.database.postgres_url
        return f"sqlite:///{self.database.sqlite_path}"

    def validate_required_keys(self) -> List[str]:
        """Validate that required API keys are present"""
        missing_keys = []
        
        provider = self.llm.preferred_provider.lower()
        if provider == "openai" and not self.llm.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        elif provider == "anthropic" and not self.llm.anthropic_api_key:
            missing_keys.append("ANTHROPIC_API_KEY")
        elif provider == "deepseek" and not self.llm.deepseek_api_key:
            missing_keys.append("DEEPSEEK_API_KEY")
        
        if self.discourse.api_key is None:
            missing_keys.append("DISCOURSE_API_KEY")
        
        return missing_keys

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        config_dict = self.dict()
        
        # Remove sensitive information
        sensitive_keys = [
            "database.postgres_url",
            "llm.openai_api_key", 
            "llm.anthropic_api_key",
            "llm.deepseek_api_key",
            "discourse.api_key",
            "security.secret_key"
        ]
        
        for key_path in sensitive_keys:
            keys = key_path.split(".")
            current = config_dict
            for key in keys[:-1]:
                if key in current:
                    current = current[key]
                else:
                    break
            else:
                if keys[-1] in current:
                    current[keys[-1]] = "***REDACTED***"
        
        return config_dict

# Global configuration instance
config = HumanizerConfig()

# Convenience functions
def get_config() -> HumanizerConfig:
    """Get the global configuration instance"""
    return config

def reload_config() -> HumanizerConfig:
    """Reload configuration from environment"""
    global config
    config = HumanizerConfig()
    return config

# Export main components
__all__ = [
    "HumanizerConfig",
    "DatabaseConfig", 
    "LLMConfig",
    "APIConfig",
    "DiscourseConfig",
    "LoggingConfig",
    "SecurityConfig",
    "config",
    "get_config",
    "reload_config"
]
