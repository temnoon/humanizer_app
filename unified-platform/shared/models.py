"""
Unified Pydantic Models
All data structures with comprehensive validation and security
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid
import re


class ContentType(str, Enum):
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


class TransformationEngine(str, Enum):
    LPE = "lpe"
    QUANTUM = "quantum"
    MAIEUTIC = "maieutic"
    TRANSLATION = "translation"
    VISION = "vision"


# Base Models
class TimestampedModel(BaseModel):
    """Base model with automatic timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IdentifiedModel(TimestampedModel):
    """Base model with UUID identification"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


# Content Models
class ContentMetadata(BaseModel):
    """Content metadata with validation"""
    source: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=255)
    language: str = Field("en", regex=r"^[a-z]{2}$")
    tags: List[str] = Field(default_factory=list, max_items=50)
    
    @validator("tags")
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]


class ContentInput(BaseModel):
    """Input for content ingestion"""
    content_type: ContentType
    data: Union[str, bytes] = Field(..., description="Content data")
    metadata: ContentMetadata
    
    @validator("data")
    def validate_data_size(cls, v):
        if isinstance(v, str) and len(v) > 1_000_000:  # 1MB limit for text
            raise ValueError("Text content too large (max 1MB)")
        if isinstance(v, bytes) and len(v) > 50_000_000:  # 50MB limit for binary
            raise ValueError("Binary content too large (max 50MB)")
        return v


class Content(IdentifiedModel):
    """Stored content with processing status"""
    content_type: ContentType
    data: str = Field(..., description="Processed content data")
    metadata: ContentMetadata
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    @validator("embedding")
    def validate_embedding_dimension(cls, v):
        if v is not None and len(v) != 1536:  # Configurable via config
            raise ValueError("Embedding must be 1536 dimensions")
        return v


# Search Models
class SearchQuery(BaseModel):
    """Search query with comprehensive options"""
    query: str = Field(..., min_length=1, max_length=1000)
    content_types: Optional[List[ContentType]] = None
    tags: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    
    @validator("query")
    def sanitize_query(cls, v):
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>\"\'&]', '', v.strip())
        if not sanitized:
            raise ValueError("Query cannot be empty after sanitization")
        return sanitized


class SearchResult(BaseModel):
    """Search result with relevance scoring"""
    content: Content
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    rank: int = Field(..., ge=1)
    highlight_snippets: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Complete search response"""
    results: List[SearchResult]
    total_results: int
    query_time_ms: float
    query: SearchQuery


# Transformation Models
class TransformationAttributes(BaseModel):
    """LPE transformation attributes"""
    persona: Optional[str] = Field(None, max_length=255)
    namespace: Optional[str] = Field(None, max_length=255)
    style: Optional[str] = Field(None, max_length=255)
    
    @validator("persona", "namespace", "style")
    def sanitize_attributes(cls, v):
        if v:
            return re.sub(r'[<>\"\'&]', '', v.strip())
        return v


class TransformationRequest(BaseModel):
    """Request for content transformation"""
    content_id: Optional[uuid.UUID] = None
    text: Optional[str] = Field(None, max_length=50000)
    engine: TransformationEngine = TransformationEngine.LPE
    attributes: TransformationAttributes = Field(default_factory=TransformationAttributes)
    options: Dict[str, Any] = Field(default_factory=dict)
    
    @root_validator
    def validate_content_source(cls, values):
        content_id = values.get("content_id")
        text = values.get("text")
        if not content_id and not text:
            raise ValueError("Either content_id or text must be provided")
        if content_id and text:
            raise ValueError("Cannot provide both content_id and text")
        return values


class TransformationResult(IdentifiedModel):
    """Result of content transformation"""
    request_id: uuid.UUID
    original_text: str
    transformed_text: str
    engine: TransformationEngine
    attributes: TransformationAttributes
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    processing_time_ms: float
    token_usage: Dict[str, int] = Field(default_factory=dict)


# LLM Provider Models
class LLMRequest(BaseModel):
    """Request to LLM provider"""
    prompt: str = Field(..., max_length=100000)
    model: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4096, ge=1, le=32000)
    stop_sequences: Optional[List[str]] = None
    
    @validator("prompt")
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class LLMResponse(BaseModel):
    """Response from LLM provider"""
    text: str
    model: str
    provider: str
    token_usage: Dict[str, int]
    response_time_ms: float
    cost_usd: Optional[float] = None


# Analysis Models
class QualityAnalysis(BaseModel):
    """Content quality analysis"""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    coherence_score: float = Field(..., ge=0.0, le=1.0)
    clarity_score: float = Field(..., ge=0.0, le=1.0)
    grammar_score: float = Field(..., ge=0.0, le=1.0)
    toxicity_score: float = Field(..., ge=0.0, le=1.0)
    readability_score: float = Field(..., ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list)


class QuantumAnalysis(BaseModel):
    """Quantum narrative analysis"""
    quantum_state: Dict[str, float]
    coherence_measures: Dict[str, float]
    entanglement_score: float = Field(..., ge=0.0, le=1.0)
    superposition_states: List[str]


# Batch Processing Models
class BatchJob(IdentifiedModel):
    """Batch processing job"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    total_items: int = Field(..., ge=1)
    processed_items: int = Field(0, ge=0)
    failed_items: int = Field(0, ge=0)
    status: ProcessingStatus = ProcessingStatus.PENDING
    estimated_completion: Optional[datetime] = None
    error_messages: List[str] = Field(default_factory=list)


class BatchItem(IdentifiedModel):
    """Individual item in batch job"""
    job_id: uuid.UUID
    content_id: uuid.UUID
    status: ProcessingStatus = ProcessingStatus.PENDING
    result_id: Optional[uuid.UUID] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str = Field(..., regex=r"^[a-z_]+$")
    session_id: uuid.UUID
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProgressUpdate(BaseModel):
    """Progress update message"""
    job_id: uuid.UUID
    progress_percent: float = Field(..., ge=0.0, le=100.0)
    current_step: str
    estimated_remaining_ms: Optional[int] = None
    message: Optional[str] = None


# User Management Models
class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator("password")
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        return v


class User(IdentifiedModel):
    """User model (without password)"""
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False
    api_quota_used: int = 0
    api_quota_limit: int = 1000


class TokenData(BaseModel):
    """JWT token data"""
    user_id: uuid.UUID
    username: str
    expires_at: datetime


# API Response Models
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: float
    dependencies: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standardized success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Export commonly used models
__all__ = [
    "Content", "ContentInput", "ContentMetadata",
    "SearchQuery", "SearchResult", "SearchResponse",
    "TransformationRequest", "TransformationResult", "TransformationAttributes",
    "LLMRequest", "LLMResponse",
    "QualityAnalysis", "QuantumAnalysis",
    "BatchJob", "BatchItem",
    "WebSocketMessage", "ProgressUpdate",
    "User", "UserCreate", "TokenData",
    "HealthCheck", "ErrorResponse", "SuccessResponse"
]