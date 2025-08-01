"""
Simple Configuration for CLI Testing
Minimal dependencies version
"""
import os
from typing import Optional

class SimpleConfig:
    """Simple configuration without complex dependencies"""
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # LLM Configuration  
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    
    # Available LLM providers
    PROVIDERS = [
        "openai", "anthropic", "deepseek", "groq", 
        "google", "ollama", "together"
    ]
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for provider from environment"""
        key_name = f"{provider.upper()}_API_KEY"
        return os.getenv(key_name)

# Global config instance
config = SimpleConfig()