"""
Security Middleware for Unified Platform
Comprehensive security controls with configurable policies
"""
import time
import logging
import uuid
import hashlib
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import ErrorResponse


@dataclass
class RateLimitInfo:
    """Rate limit tracking information"""
    requests: int
    window_start: float
    last_request: float


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = config.security.max_request_size_mb * 1024 * 1024
        
    async def dispatch(self, request: Request, call_next):
        """Process security checks for each request"""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Security headers check
        if not self._validate_security_headers(request):
            return self._security_error("Invalid security headers", request_id)
        
        # Request size validation
        if hasattr(request, 'headers'):
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_request_size:
                return self._security_error(
                    f"Request too large (max {config.security.max_request_size_mb}MB)", 
                    request_id
                )
        
        # Path traversal protection
        if self._has_path_traversal(str(request.url.path)):
            return self._security_error("Path traversal detected", request_id)
        
        # SQL injection basic protection
        if self._has_sql_injection_patterns(str(request.url.query)):
            return self._security_error("Suspicious query patterns detected", request_id)
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response)
            
            # Add request ID to response
            response.headers["X-Request-ID"] = request_id
            
            # Add timing header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logging.error(f"Request {request_id} failed: {e}")
            return self._security_error("Internal server error", request_id, status_code=500)
    
    def _validate_security_headers(self, request: Request) -> bool:
        """Validate required security headers"""
        
        # In production, require certain headers
        if config.environment.value == "production":
            user_agent = request.headers.get("user-agent", "")
            if not user_agent or len(user_agent) < 10:
                return False
                
            # Block known bad user agents
            bad_agents = ["curl", "wget", "python-requests"]
            if any(agent in user_agent.lower() for agent in bad_agents):
                if not request.headers.get("x-api-key"):  # Allow if has API key
                    return False
        
        return True
    
    def _has_path_traversal(self, path: str) -> bool:
        """Check for path traversal attempts"""
        dangerous_patterns = ["../", "..\\", "%2e%2e", "%252e%252e"]
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in dangerous_patterns)
    
    def _has_sql_injection_patterns(self, query: str) -> bool:
        """Basic SQL injection pattern detection"""
        if not query:
            return False
            
        query_lower = query.lower()
        sql_patterns = [
            "union select", "drop table", "delete from", "insert into",
            "update set", "exec(", "execute(", "--", "/*", "*/"
        ]
        return any(pattern in query_lower for pattern in sql_patterns)
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""
        
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        })
    
    def _security_error(self, message: str, request_id: str, status_code: int = 403) -> JSONResponse:
        """Return standardized security error"""
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error="SECURITY_VIOLATION",
                message=message,
                request_id=request_id
            ).dict()
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis: Optional[redis.Redis] = None
        self.local_cache: Dict[str, RateLimitInfo] = {}
        self.cache_cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # Rate limit configurations per endpoint type
        self.rate_limits = {
            "/api/v1/auth/login": (5, 300),     # 5 requests per 5 minutes
            "/api/v1/auth/register": (3, 3600), # 3 requests per hour
            "/api/v1/transform": (20, 3600),    # 20 requests per hour
            "/api/v1/search": (100, 3600),      # 100 requests per hour
            "default": (config.security.rate_limit_per_minute, 60)  # Default rate
        }
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting based on client and endpoint"""
        
        # Initialize Redis connection if needed
        if not self.redis:
            try:
                self.redis = redis.from_url(config.redis.url)
            except Exception:
                # Fall back to local rate limiting
                pass
        
        # Get client identifier
        client_id = self._get_client_id(request)
        endpoint = self._get_endpoint_pattern(request.url.path)
        
        # Check rate limit
        is_allowed, reset_time = await self._check_rate_limit(client_id, endpoint)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content=ErrorResponse(
                    error="RATE_LIMIT_EXCEEDED",
                    message=f"Rate limit exceeded. Reset in {int(reset_time)} seconds",
                    details={"reset_time": reset_time}
                ).dict(),
                headers={
                    "Retry-After": str(int(reset_time)),
                    "X-RateLimit-Limit": str(self.rate_limits.get(endpoint, self.rate_limits["default"])[0]),
                    "X-RateLimit-Reset": str(int(time.time() + reset_time))
                }
            )
        
        # Proceed with request
        response = await call_next(request)
        
        # Add rate limit headers
        limit, window = self.rate_limits.get(endpoint, self.rate_limits["default"])
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Window"] = str(window)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier for rate limiting"""
        
        # Check for API key first
        api_key = request.headers.get("x-api-key")
        if api_key:
            return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
        
        # Check for authenticated user
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Extract user info from JWT (simplified)
            return f"user:{hashlib.sha256(auth_header.encode()).hexdigest()[:16]}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _get_endpoint_pattern(self, path: str) -> str:
        """Map request path to rate limit pattern"""
        
        for pattern in self.rate_limits:
            if pattern != "default" and path.startswith(pattern):
                return pattern
        return "default"
    
    async def _check_rate_limit(self, client_id: str, endpoint: str) -> Tuple[bool, float]:
        """Check if request is within rate limit"""
        
        limit, window = self.rate_limits.get(endpoint, self.rate_limits["default"])
        current_time = time.time()
        
        # Try Redis first
        if self.redis:
            try:
                return await self._check_redis_rate_limit(client_id, endpoint, limit, window, current_time)
            except Exception as e:
                logging.warning(f"Redis rate limiting failed, falling back to local: {e}")
        
        # Fall back to local rate limiting
        return self._check_local_rate_limit(client_id, endpoint, limit, window, current_time)
    
    async def _check_redis_rate_limit(self, client_id: str, endpoint: str, limit: int, window: int, current_time: float) -> Tuple[bool, float]:
        """Redis-based distributed rate limiting"""
        
        key = f"rate_limit:{client_id}:{endpoint}"
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        
        request_count = results[0]
        
        if request_count > limit:
            # Get TTL for reset time
            ttl = await self.redis.ttl(key)
            return False, max(ttl, 0)
        
        return True, 0
    
    def _check_local_rate_limit(self, client_id: str, endpoint: str, limit: int, window: int, current_time: float) -> Tuple[bool, float]:
        """Local in-memory rate limiting (fallback)"""
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cache_cleanup_interval:
            self._cleanup_local_cache(current_time, window)
            self.last_cleanup = current_time
        
        key = f"{client_id}:{endpoint}"
        
        if key not in self.local_cache:
            self.local_cache[key] = RateLimitInfo(1, current_time, current_time)
            return True, 0
        
        rate_info = self.local_cache[key]
        
        # Check if window has expired
        if current_time - rate_info.window_start >= window:
            rate_info.requests = 1
            rate_info.window_start = current_time
            rate_info.last_request = current_time
            return True, 0
        
        # Increment request count
        rate_info.requests += 1
        rate_info.last_request = current_time
        
        if rate_info.requests > limit:
            reset_time = window - (current_time - rate_info.window_start)
            return False, reset_time
        
        return True, 0
    
    def _cleanup_local_cache(self, current_time: float, max_window: int):
        """Clean up expired entries from local cache"""
        
        expired_keys = []
        for key, rate_info in self.local_cache.items():
            if current_time - rate_info.last_request > max_window * 2:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_cache[key]
        
        logging.info(f"Cleaned up {len(expired_keys)} expired rate limit entries")