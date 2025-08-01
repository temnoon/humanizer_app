"""
LLM Service with Multi-Provider Support
Intelligent provider selection, fallback handling, and cost optimization
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import hashlib

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import ollama

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config, LLMProvider
from models import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class ProviderStatus:
    """Track provider health and performance"""
    is_available: bool = True
    last_error: Optional[str] = None
    error_count: int = 0
    last_success: Optional[float] = None
    avg_response_time: float = 0.0
    total_requests: int = 0
    total_cost: float = 0.0


@dataclass 
class ProviderConfig:
    """Provider-specific configuration"""
    name: str
    api_key: Optional[str]
    base_url: Optional[str] = None
    model: str = ""
    max_tokens: int = 4096
    timeout: int = 30
    cost_per_1k_tokens: float = 0.0


class LLMService:
    """Advanced LLM service with intelligent provider management"""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, ProviderConfig] = {}
        self.provider_status: Dict[LLMProvider, ProviderStatus] = {}
        self.clients: Dict[LLMProvider, Any] = {}
        self.request_cache: Dict[str, tuple] = {}  # (response, timestamp)
        
        self._initialize_providers()
        self._cost_tracker = CostTracker()
        
    def _initialize_providers(self):
        """Initialize all configured LLM providers with keychain integration"""
        
        # Import keychain service
        try:
            from .keychain_service import keychain_service
            # Load all keys from keychain to environment
            keychain_service.load_all_keys_to_env()
        except ImportError:
            logger.warning("Keychain service not available, using environment variables only")
        
        # DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.providers[LLMProvider.DEEPSEEK] = ProviderConfig(
                name="deepseek",
                api_key=deepseek_key,
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                cost_per_1k_tokens=0.0014  # $0.14 per 1M tokens
            )
            self.clients[LLMProvider.DEEPSEEK] = AsyncOpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com/v1"
            )
            
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers[LLMProvider.OPENAI] = ProviderConfig(
                name="openai",
                api_key=openai_key,
                model="gpt-4-turbo-preview",
                cost_per_1k_tokens=0.01  # $10 per 1M tokens
            )
            self.clients[LLMProvider.OPENAI] = AsyncOpenAI(
                api_key=openai_key
            )
            
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.providers[LLMProvider.ANTHROPIC] = ProviderConfig(
                name="anthropic",
                api_key=anthropic_key,
                model="claude-3-sonnet-20240229",
                cost_per_1k_tokens=0.003  # $3 per 1M tokens
            )
            self.clients[LLMProvider.ANTHROPIC] = AsyncAnthropic(
                api_key=anthropic_key
            )
        
        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers[LLMProvider.GROQ] = ProviderConfig(
                name="groq",
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
                model="mixtral-8x7b-32768",
                cost_per_1k_tokens=0.0002  # Very cheap
            )
            self.clients[LLMProvider.GROQ] = AsyncOpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
        
        # Together
        together_key = os.getenv("TOGETHER_API_KEY")
        if together_key:
            self.providers[LLMProvider.TOGETHER] = ProviderConfig(
                name="together",
                api_key=together_key,
                base_url="https://api.together.xyz/v1",
                model="meta-llama/Llama-2-70b-chat-hf",
                cost_per_1k_tokens=0.0008  # Cheap
            )
            self.clients[LLMProvider.TOGETHER] = AsyncOpenAI(
                api_key=together_key,
                base_url="https://api.together.xyz/v1"
            )
            
        # Ollama (local - no API key needed)
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.providers[LLMProvider.OLLAMA] = ProviderConfig(
            name="ollama",
            api_key=None,
            base_url=ollama_host,
            model="llama2:7b",
            cost_per_1k_tokens=0.0  # Free local
        )
        
        # Initialize status tracking
        for provider in self.providers:
            self.provider_status[provider] = ProviderStatus()
            
        logger.info(f"Initialized {len(self.providers)} LLM providers")
    
    async def complete(self, request: LLMRequest, preferred_provider: Optional[LLMProvider] = None) -> LLMResponse:
        """Complete text using optimal provider with fallback"""
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        if cache_key in self.request_cache:
            cached_response, timestamp = self.request_cache[cache_key]
            if time.time() - timestamp < config.cache.llm_response_ttl_seconds:
                logger.info(f"Returning cached response for request")
                return cached_response
        
        # Select optimal provider
        provider = self._select_provider(request, preferred_provider)
        
        # Attempt completion with fallback
        last_error = None
        for attempt_provider in self._get_fallback_order(provider):
            try:
                response = await self._complete_with_provider(request, attempt_provider)
                
                # Cache successful response
                self.request_cache[cache_key] = (response, time.time())
                
                # Update provider status
                self._update_provider_success(attempt_provider, response.response_time_ms)
                
                return response
                
            except Exception as e:
                last_error = e
                self._update_provider_error(attempt_provider, str(e))
                logger.warning(f"Provider {attempt_provider.value} failed: {e}")
                continue
        
        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    async def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate embeddings using optimal provider"""
        
        # Use OpenAI for embeddings (most reliable)
        if LLMProvider.OPENAI in self.clients:
            try:
                client = self.clients[LLMProvider.OPENAI]
                response = await client.embeddings.create(
                    model=model or "text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
                
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")
        
        # Fallback to sentence transformers (local)
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            
        # Return zero vector as last resort
        logger.warning("Returning zero vector for embedding")
        return [0.0] * config.vectordb.embedding_dimension
    
    async def _complete_with_provider(self, request: LLMRequest, provider: LLMProvider) -> LLMResponse:
        """Complete request with specific provider"""
        
        start_time = time.time()
        provider_config = self.providers[provider]
        
        if provider == LLMProvider.DEEPSEEK:
            return await self._complete_openai_compatible(request, provider, provider_config)
            
        elif provider == LLMProvider.OPENAI:
            return await self._complete_openai(request, provider, provider_config)
            
        elif provider == LLMProvider.ANTHROPIC:
            return await self._complete_anthropic(request, provider, provider_config)
            
        elif provider == LLMProvider.OLLAMA:
            return await self._complete_ollama(request, provider, provider_config)
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _complete_openai_compatible(self, request: LLMRequest, provider: LLMProvider, config: ProviderConfig) -> LLMResponse:
        """Complete using OpenAI-compatible API (DeepSeek, etc.)"""
        
        start_time = time.time()
        client = self.clients[provider]
        
        response = await client.chat.completions.create(
            model=request.model or config.model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=request.stop_sequences,
            timeout=config.timeout
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Calculate cost
        usage = response.usage
        cost = self._calculate_cost(provider, usage.prompt_tokens, usage.completion_tokens)
        
        return LLMResponse(
            text=response.choices[0].message.content,
            model=response.model,
            provider=provider.value,
            token_usage={
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            response_time_ms=response_time,
            cost_usd=cost
        )
    
    async def _complete_openai(self, request: LLMRequest, provider: LLMProvider, config: ProviderConfig) -> LLMResponse:
        """Complete using OpenAI API"""
        return await self._complete_openai_compatible(request, provider, config)
    
    async def _complete_anthropic(self, request: LLMRequest, provider: LLMProvider, config: ProviderConfig) -> LLMResponse:
        """Complete using Anthropic API"""
        
        start_time = time.time()
        client = self.clients[provider]
        
        response = await client.messages.create(
            model=request.model or config.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            messages=[{"role": "user", "content": request.prompt}]
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Calculate cost (Anthropic pricing)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = self._calculate_cost(provider, input_tokens, output_tokens)
        
        return LLMResponse(
            text=response.content[0].text,
            model=response.model,
            provider=provider.value,
            token_usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            response_time_ms=response_time,
            cost_usd=cost
        )
    
    async def _complete_ollama(self, request: LLMRequest, provider: LLMProvider, config: ProviderConfig) -> LLMResponse:
        """Complete using Ollama local API"""
        
        start_time = time.time()
        
        try:
            response = await ollama.AsyncClient(host=config.base_url).chat(
                model=request.model or config.model,
                messages=[{"role": "user", "content": request.prompt}],
                options={
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=response['message']['content'],
                model=request.model or config.model,
                provider=provider.value,
                token_usage={
                    "prompt_tokens": len(request.prompt.split()),  # Rough estimate
                    "completion_tokens": len(response['message']['content'].split()),
                    "total_tokens": len(request.prompt.split()) + len(response['message']['content'].split())
                },
                response_time_ms=response_time,
                cost_usd=0.0  # Local is free
            )
            
        except Exception as e:
            # Try HTTP request as fallback
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.base_url}/api/generate",
                    json={
                        "model": request.model or config.model,
                        "prompt": request.prompt,
                        "stream": False,
                        "options": {
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        }
                    },
                    timeout=config.timeout
                )
                response.raise_for_status()
                
                response_time = (time.time() - start_time) * 1000
                result = response.json()
                
                return LLMResponse(
                    text=result.get('response', ''),
                    model=request.model or config.model,
                    provider=provider.value,
                    token_usage={
                        "prompt_tokens": len(request.prompt.split()),
                        "completion_tokens": len(result.get('response', '').split()),
                        "total_tokens": len(request.prompt.split()) + len(result.get('response', '').split())
                    },
                    response_time_ms=response_time,
                    cost_usd=0.0
                )
    
    def _select_provider(self, request: LLMRequest, preferred: Optional[LLMProvider] = None) -> LLMProvider:
        """Select optimal provider based on requirements and status"""
        
        # Use preferred if specified and available
        if preferred and preferred in self.providers and self.provider_status[preferred].is_available:
            return preferred
        
        # Use configured default if available
        default_provider = config.llm.default_provider
        if default_provider in self.providers and self.provider_status[default_provider].is_available:
            return default_provider
        
        # Find best available provider
        available_providers = [
            p for p in self.providers 
            if self.provider_status[p].is_available and self.provider_status[p].error_count < 5
        ]
        
        if not available_providers:
            # All providers have errors, try the least problematic
            available_providers = list(self.providers.keys())
        
        # Sort by performance (response time and error rate)
        available_providers.sort(key=lambda p: (
            self.provider_status[p].error_count,
            self.provider_status[p].avg_response_time
        ))
        
        return available_providers[0]
    
    def _get_fallback_order(self, primary: LLMProvider) -> List[LLMProvider]:
        """Get fallback order starting with primary provider"""
        
        fallback_order = [primary]
        
        # Add configured fallbacks
        for provider in config.llm.fallback_providers:
            if provider != primary and provider in self.providers:
                fallback_order.append(provider)
        
        # Add any remaining providers
        for provider in self.providers:
            if provider not in fallback_order:
                fallback_order.append(provider)
        
        return fallback_order
    
    def _calculate_cost(self, provider: LLMProvider, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for provider and token usage"""
        
        provider_config = self.providers[provider]
        cost_per_1k = provider_config.cost_per_1k_tokens
        
        # Most providers charge differently for input/output
        if provider == LLMProvider.ANTHROPIC:
            # Anthropic: $3/$15 per 1M for input/output
            input_cost = (input_tokens / 1000) * 0.003
            output_cost = (output_tokens / 1000) * 0.015
            return input_cost + output_cost
        elif provider == LLMProvider.OPENAI:
            # OpenAI GPT-4: $10/$30 per 1M for input/output  
            input_cost = (input_tokens / 1000) * 0.01
            output_cost = (output_tokens / 1000) * 0.03
            return input_cost + output_cost
        else:
            # Simple pricing for others
            total_tokens = input_tokens + output_tokens
            return (total_tokens / 1000) * cost_per_1k
    
    def _update_provider_success(self, provider: LLMProvider, response_time_ms: float):
        """Update provider status on successful request"""
        
        status = self.provider_status[provider]
        status.is_available = True
        status.last_success = time.time()
        status.total_requests += 1
        
        # Update rolling average response time
        if status.avg_response_time == 0:
            status.avg_response_time = response_time_ms
        else:
            status.avg_response_time = (status.avg_response_time * 0.9) + (response_time_ms * 0.1)
        
        # Reset error count on success
        if status.error_count > 0:
            status.error_count = max(0, status.error_count - 1)
    
    def _update_provider_error(self, provider: LLMProvider, error: str):
        """Update provider status on error"""
        
        status = self.provider_status[provider]
        status.error_count += 1
        status.last_error = error
        
        # Mark as unavailable if too many errors
        if status.error_count >= 3:
            status.is_available = False
            logger.warning(f"Provider {provider.value} marked as unavailable after {status.error_count} errors")
    
    def _get_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key for request"""
        
        cache_data = {
            "prompt": request.prompt,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stop_sequences": request.stop_sequences
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        
        health_status = {}
        
        for provider in self.providers:
            status = self.provider_status[provider]
            health_status[provider.value] = {
                "available": status.is_available,
                "error_count": status.error_count,
                "last_error": status.last_error,
                "avg_response_time_ms": status.avg_response_time,
                "total_requests": status.total_requests,
                "total_cost_usd": status.total_cost
            }
        
        return health_status
    
    def get_cost_summary(self) -> Dict[str, float]:
        """Get cost summary by provider"""
        
        return {
            provider.value: self.provider_status[provider].total_cost
            for provider in self.providers
        }


class CostTracker:
    """Track LLM API costs and budgets"""
    
    def __init__(self):
        self.daily_costs: Dict[str, float] = {}
        self.monthly_costs: Dict[str, float] = {}
        self.budget_alerts_sent = set()
    
    def record_cost(self, provider: str, cost: float):
        """Record cost for provider"""
        
        today = time.strftime("%Y-%m-%d")
        month = time.strftime("%Y-%m")
        
        # Update daily costs
        daily_key = f"{provider}:{today}"
        self.daily_costs[daily_key] = self.daily_costs.get(daily_key, 0) + cost
        
        # Update monthly costs
        monthly_key = f"{provider}:{month}"
        self.monthly_costs[monthly_key] = self.monthly_costs.get(monthly_key, 0) + cost
        
        # Check budget alerts
        self._check_budget_alerts(provider, month)
    
    def _check_budget_alerts(self, provider: str, month: str):
        """Check if budget alerts should be sent"""
        
        monthly_key = f"{provider}:{month}"
        monthly_cost = self.monthly_costs.get(monthly_key, 0)
        
        budget_limit = config.llm.monthly_budget_usd
        
        # Alert at 80% and 100% of budget
        alert_thresholds = [0.8, 1.0]
        
        for threshold in alert_thresholds:
            alert_key = f"{monthly_key}:{threshold}"
            
            if monthly_cost >= budget_limit * threshold and alert_key not in self.budget_alerts_sent:
                self.budget_alerts_sent.add(alert_key)
                logger.warning(
                    f"Budget alert: {provider} has used ${monthly_cost:.2f} "
                    f"({threshold*100:.0f}% of ${budget_limit:.2f} monthly budget)"
                )