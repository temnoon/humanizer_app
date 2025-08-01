"""
Logging Middleware for Unified Platform
Structured logging with request tracking and performance monitoring
"""
import time
import json
import logging
import uuid
from typing import Dict, Any, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config


class LoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive request/response logging middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("api.requests")
        
        # Configure structured logging based on config
        if config.monitoring.log_format.value == "json":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, config.monitoring.log_level.value))
        
        # Performance tracking
        self.slow_request_threshold = 5.0  # seconds
        self.request_metrics: Dict[str, list] = {"response_times": []}
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response with performance metrics"""
        
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        # Extract request information
        request_info = self._extract_request_info(request)
        
        # Log incoming request
        self.logger.info("Request started", extra={
            "event": "request_started",
            "request_id": request_id,
            **request_info
        })
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            self._track_performance(response_time)
            
            # Extract response information
            response_info = self._extract_response_info(response, response_time)
            
            # Determine log level based on status and performance
            log_level = self._get_log_level(response.status_code, response_time)
            
            # Log completed request
            self.logger.log(log_level, "Request completed", extra={
                "event": "request_completed",
                "request_id": request_id,
                **request_info,
                **response_info
            })
            
            return response
            
        except Exception as e:
            # Calculate error response time
            response_time = time.time() - start_time
            
            # Log error
            self.logger.error("Request failed", extra={
                "event": "request_failed",
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": round(response_time * 1000, 2),
                **request_info
            }, exc_info=True)
            
            raise
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract relevant request information for logging"""
        
        # Get client information
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host
        
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Extract useful headers (sanitized)
        relevant_headers = {}
        for header, value in request.headers.items():
            if header.lower() in ['user-agent', 'content-type', 'content-length', 'accept']:
                relevant_headers[header] = value[:200]  # Truncate long values
        
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "headers": relevant_headers,
            "path_params": getattr(request, 'path_params', {}),
        }
    
    def _extract_response_info(self, response: Response, response_time: float) -> Dict[str, Any]:
        """Extract relevant response information for logging"""
        
        return {
            "status_code": response.status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "response_size": response.headers.get("content-length", "unknown"),
            "content_type": response.headers.get("content-type", "unknown"),
        }
    
    def _get_log_level(self, status_code: int, response_time: float) -> int:
        """Determine appropriate log level based on response"""
        
        # Error responses
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        
        # Slow requests
        if response_time > self.slow_request_threshold:
            return logging.WARNING
        
        # Normal requests
        return logging.INFO
    
    def _track_performance(self, response_time: float):
        """Track performance metrics"""
        
        self.request_metrics["response_times"].append(response_time)
        
        # Keep only last 1000 requests for metrics
        if len(self.request_metrics["response_times"]) > 1000:
            self.request_metrics["response_times"] = self.request_metrics["response_times"][-1000:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        
        response_times = self.request_metrics["response_times"]
        if not response_times:
            return {}
        
        return {
            "total_requests": len(response_times),
            "avg_response_time_ms": round(sum(response_times) / len(response_times) * 1000, 2),
            "max_response_time_ms": round(max(response_times) * 1000, 2),
            "min_response_time_ms": round(min(response_times) * 1000, 2),
            "slow_requests": len([t for t in response_times if t > self.slow_request_threshold]),
        }


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        
        # Base log entry
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'event'):
            log_entry["event"] = record.event
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        # Add all extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                if not key.startswith('_'):
                    log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str, separators=(',', ':'))


# Performance monitoring utilities
class PerformanceMonitor:
    """Utility class for tracking API performance"""
    
    def __init__(self):
        self.metrics = {
            "endpoint_stats": {},
            "error_counts": {},
            "response_time_buckets": {
                "fast": 0,      # < 100ms
                "normal": 0,    # 100ms - 1s
                "slow": 0,      # 1s - 5s
                "very_slow": 0, # > 5s
            }
        }
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Record request metrics"""
        
        key = f"{method} {endpoint}"
        
        # Track endpoint statistics
        if key not in self.metrics["endpoint_stats"]:
            self.metrics["endpoint_stats"][key] = {
                "count": 0,
                "total_time": 0,
                "errors": 0
            }
        
        stats = self.metrics["endpoint_stats"][key]
        stats["count"] += 1
        stats["total_time"] += response_time
        
        if status_code >= 400:
            stats["errors"] += 1
        
        # Track response time buckets
        if response_time < 0.1:
            self.metrics["response_time_buckets"]["fast"] += 1
        elif response_time < 1.0:
            self.metrics["response_time_buckets"]["normal"] += 1
        elif response_time < 5.0:
            self.metrics["response_time_buckets"]["slow"] += 1
        else:
            self.metrics["response_time_buckets"]["very_slow"] += 1
        
        # Track error counts
        if status_code >= 400:
            error_key = f"{status_code}"
            self.metrics["error_counts"][error_key] = self.metrics["error_counts"].get(error_key, 0) + 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        # Calculate endpoint averages
        endpoint_summary = {}
        for endpoint, stats in self.metrics["endpoint_stats"].items():
            if stats["count"] > 0:
                endpoint_summary[endpoint] = {
                    "requests": stats["count"],
                    "avg_response_time_ms": round(stats["total_time"] / stats["count"] * 1000, 2),
                    "error_rate": round(stats["errors"] / stats["count"] * 100, 2)
                }
        
        return {
            "endpoints": endpoint_summary,
            "response_time_distribution": self.metrics["response_time_buckets"],
            "error_counts": self.metrics["error_counts"]
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()