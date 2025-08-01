"""
Unified Humanizer Platform API Gateway
Centralized FastAPI application with security, routing, and middleware
"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import uvicorn

# Import our unified modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config import config
from models import HealthCheck, ErrorResponse

# Import routers
from routers import (
    content_router,
    transformation_router, 
    search_router,
    llm_router,
    websocket_router,
    auth_router
)

# Import middleware and dependencies
from middleware.security import SecurityMiddleware, RateLimitMiddleware
from middleware.logging import LoggingMiddleware
from core.dependencies import get_database, get_redis, get_vector_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logging.info("🚀 Starting Unified Humanizer Platform API")
    
    # Initialize database connections
    try:
        db = await get_database()
        redis = await get_redis() 
        vectordb = await get_vector_db()
        
        # Store in app state for access
        app.state.db = db
        app.state.redis = redis
        app.state.vectordb = vectordb
        app.state.startup_time = time.time()
        
        logging.info("✅ Database connections established")
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Unified Humanizer Platform API")
    
    # Cleanup connections
    if hasattr(app.state, 'db'):
        await app.state.db.close()
    if hasattr(app.state, 'redis'):
        await app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title="Unified Humanizer Platform API",
    description="Consolidated API gateway for content transformation, search, and curation",
    version="2.0.0",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    lifespan=lifespan
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Add security middleware
if config.environment.value == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["humanizer.com", "*.humanizer.com", "localhost"]
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=True,
    allow_methods=config.security.cors_methods,
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standardized response"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP_{exc.status_code}",
            message=exc.detail,
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with basic API information"""
    return {
        "name": "Unified Humanizer Platform API",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs" if config.debug else "Contact administrator",
        "timestamp": time.time()
    }


# Health check endpoint
@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check(request: Request):
    """Comprehensive health check with dependency status"""
    startup_time = getattr(app.state, 'startup_time', time.time())
    uptime_seconds = time.time() - startup_time
    
    dependencies = {}
    
    # Check database
    try:
        await app.state.db.execute("SELECT 1")
        dependencies["database"] = "healthy"
    except Exception as e:
        dependencies["database"] = f"unhealthy: {str(e)[:100]}"
    
    # Check Redis
    try:
        await app.state.redis.ping()
        dependencies["redis"] = "healthy"
    except Exception as e:
        dependencies["redis"] = f"unhealthy: {str(e)[:100]}"
    
    # Check Vector DB
    try:
        app.state.vectordb.heartbeat()
        dependencies["vectordb"] = "healthy"
    except Exception as e:
        dependencies["vectordb"] = f"unhealthy: {str(e)[:100]}"
    
    return HealthCheck(
        version="2.0.0",
        uptime_seconds=uptime_seconds,
        dependencies=dependencies
    )


# Include routers with versioned API prefix
API_V1_PREFIX = "/api/v1"

app.include_router(
    auth_router, 
    prefix=f"{API_V1_PREFIX}/auth", 
    tags=["Authentication"]
)

app.include_router(
    content_router, 
    prefix=f"{API_V1_PREFIX}/content", 
    tags=["Content Management"]
)

app.include_router(
    search_router, 
    prefix=f"{API_V1_PREFIX}/search", 
    tags=["Search & Discovery"]
)

app.include_router(
    transformation_router, 
    prefix=f"{API_V1_PREFIX}/transform", 
    tags=["Content Transformation"]
)

app.include_router(
    llm_router, 
    prefix=f"{API_V1_PREFIX}/llm", 
    tags=["LLM Services"]
)

app.include_router(
    websocket_router, 
    prefix="/ws", 
    tags=["WebSocket"]
)


# Development server
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.monitoring.log_level.value),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=config.api.host,
        port=config.api.port,
        workers=1 if config.debug else config.api.workers,
        reload=config.debug,
        log_level=config.monitoring.log_level.value.lower()
    )