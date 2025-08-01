"""
Core Dependencies for Unified Platform
Database connections, authentication, and shared services
"""
import logging
from typing import AsyncGenerator, Optional
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import redis.asyncio as redis
import chromadb
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import User, TokenData

# Database setup
Base = declarative_base()

# Global connection pools
_async_engine = None
_redis_pool = None
_vector_db = None

# Security
security = HTTPBearer(auto_error=False)


# Database Dependencies
@lru_cache()
def get_async_engine():
    """Get or create async database engine"""
    global _async_engine
    
    if _async_engine is None:
        _async_engine = create_async_engine(
            config.database.url,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
            pool_recycle=config.database.pool_recycle,
            echo=config.database.echo,
        )
        logging.info("Created async database engine")
    
    return _async_engine


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Redis Dependencies
@lru_cache()
async def get_redis_pool():
    """Get or create Redis connection pool"""
    global _redis_pool
    
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            config.redis.url,
            max_connections=config.redis.max_connections,
            socket_timeout=config.redis.socket_timeout,
            socket_connect_timeout=config.redis.socket_connect_timeout,
            retry_on_timeout=config.redis.retry_on_timeout,
            decode_responses=True
        )
        logging.info("Created Redis connection pool")
    
    return _redis_pool


async def get_redis() -> redis.Redis:
    """Dependency to get Redis connection"""
    return await get_redis_pool()


# Vector Database Dependencies
@lru_cache()
def get_vector_db_client():
    """Get or create ChromaDB client"""
    global _vector_db
    
    if _vector_db is None:
        _vector_db = chromadb.PersistentClient(path=config.vectordb.path)
        logging.info(f"Created ChromaDB client at {config.vectordb.path}")
    
    return _vector_db


async def get_vector_db():
    """Dependency to get vector database"""
    return get_vector_db_client()


# Authentication Dependencies
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> Optional[User]:
    """Get current authenticated user from JWT token"""
    
    if not credentials:
        return None
    
    # Extract token
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            config.security.jwt_secret_key,
            algorithms=[config.security.jwt_algorithm]
        )
        
        # Extract user info
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            return None
        
        # Validate token data
        token_data = TokenData(
            user_id=user_id,
            username=username,
            expires_at=payload.get("exp")
        )
        
    except JWTError:
        return None
    
    # Get user from database
    # Note: This would typically query the user table
    # For now, return a mock user based on token data
    return User(
        id=token_data.user_id,
        username=token_data.username,
        email=f"{token_data.username}@example.com",  # Would come from DB
        is_active=True
    )


async def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authenticated user (raise exception if not authenticated)"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return current_user


async def require_admin_user(
    current_user: User = Depends(require_authenticated_user)
) -> User:
    """Require admin user (raise exception if not admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


# Service Dependencies
class LLMService:
    """LLM service with provider management"""
    
    def __init__(self):
        self.current_provider = config.llm.default_provider
        self.fallback_providers = config.llm.fallback_providers
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Complete text using configured LLM provider"""
        
        # This would implement the actual LLM calling logic
        # For now, return a placeholder
        return f"LLM response to: {prompt[:50]}..."
    
    async def embed(self, text: str) -> list[float]:
        """Generate embeddings for text"""
        
        # This would implement actual embedding generation
        # For now, return a placeholder vector
        return [0.0] * config.vectordb.embedding_dimension


class CacheService:
    """Multi-tier caching service"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.local_cache = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache (local first, then Redis)"""
        
        # Check local cache first
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Check Redis
        try:
            value = await self.redis.get(f"{config.cache.redis_key_prefix}{key}")
            if value:
                # Store in local cache
                if len(self.local_cache) < config.cache.local_max_size:
                    self.local_cache[key] = value
                return value
        except Exception as e:
            logging.warning(f"Redis cache error: {e}")
        
        return None
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache (both local and Redis)"""
        
        if ttl is None:
            ttl = config.cache.redis_ttl_seconds
        
        # Store in local cache
        if len(self.local_cache) < config.cache.local_max_size:
            self.local_cache[key] = value
        
        # Store in Redis
        try:
            await self.redis.setex(f"{config.cache.redis_key_prefix}{key}", ttl, value)
            return True
        except Exception as e:
            logging.warning(f"Redis cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        
        # Remove from local cache
        self.local_cache.pop(key, None)
        
        # Remove from Redis
        try:
            await self.redis.delete(f"{config.cache.redis_key_prefix}{key}")
            return True
        except Exception as e:
            logging.warning(f"Redis cache delete error: {e}")
            return False


# Service Dependency Providers
async def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    return LLMService()


async def get_cache_service(redis_client: redis.Redis = Depends(get_redis)) -> CacheService:
    """Get cache service instance"""
    return CacheService(redis_client)


# Health Check Dependencies
async def check_database_health(db: AsyncSession = Depends(get_database)) -> bool:
    """Check database connectivity"""
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_redis_health(redis_client: redis.Redis = Depends(get_redis)) -> bool:
    """Check Redis connectivity"""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False


async def check_vectordb_health(vectordb = Depends(get_vector_db)) -> bool:
    """Check vector database connectivity"""
    try:
        vectordb.heartbeat()
        return True
    except Exception:
        return False


# Resource Cleanup
async def cleanup_connections():
    """Cleanup all connections on shutdown"""
    global _async_engine, _redis_pool, _vector_db
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        logging.info("Closed database connections")
    
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
        logging.info("Closed Redis connections")
    
    # ChromaDB doesn't need explicit cleanup
    _vector_db = None
    logging.info("Cleaned up all connections")