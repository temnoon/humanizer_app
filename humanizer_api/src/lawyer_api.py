"""
Lamish Lawyer API - Content Quality Assessment and Style Review

Content quality assessment service that analyzes writing quality, coherence, 
factual accuracy, tone, and provides improvement suggestions. Acts as a 
gatekeeper before content goes to the Pulse Controller.

Architecture: Archive API → LPE API → Lawyer API → Pulse Controller → Discourse
"""

import logging
import asyncio
import json
import uuid
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import httpx
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Import our configuration
from config import get_config, HumanizerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
config = get_config()

# Database Models
Base = declarative_base()

class QualityAssessment(Base):
    __tablename__ = "quality_assessments"
    
    id = Column(String, primary_key=True)
    content_id = Column(String, nullable=False)  # From Archive API
    session_id = Column(String)  # From LPE API if applicable
    
    # Quality Scores (0.0 to 1.0)
    overall_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)
    coherence_score = Column(Float, nullable=False)
    factual_score = Column(Float, nullable=False)
    tone_score = Column(Float, nullable=False)
    style_score = Column(Float, nullable=False)
    
    # Assessment Results
    assessment_result = Column(String, nullable=False)  # approved, needs_improvement, rejected
    improvement_suggestions = Column(JSON, default=[])
    detected_issues = Column(JSON, default=[])
    
    # Content Analysis
    word_count = Column(Integer)
    readability_grade = Column(Float)
    sentiment_score = Column(Float)
    
    # Metadata
    llm_provider = Column(String)
    llm_model = Column(String)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON, default={})

class ContentReview(Base):
    __tablename__ = "content_reviews"
    
    id = Column(String, primary_key=True)
    assessment_id = Column(String, nullable=False)
    reviewer_type = Column(String, nullable=False)  # ai, human, hybrid
    review_status = Column(String, nullable=False)  # pending, completed, escalated
    
    # Review Details
    review_notes = Column(Text)
    recommendations = Column(JSON, default=[])
    follow_up_required = Column(String, default="no")  # no, minor, major
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Enums
class AssessmentResult(str, Enum):
    APPROVED = "approved"
    NEEDS_IMPROVEMENT = "needs_improvement"
    REJECTED = "rejected"

class IssueType(str, Enum):
    CLARITY = "clarity"
    COHERENCE = "coherence"
    FACTUAL = "factual"
    TONE = "tone"
    STYLE = "style"
    GRAMMAR = "grammar"
    STRUCTURE = "structure"

class ReviewType(str, Enum):
    QUICK = "quick"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

# Pydantic Models
class ContentForAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., description="Text content to assess")
    content_type: str = Field(default="text", description="Type of content")
    source: Optional[str] = Field(None, description="Content source")
    title: Optional[str] = Field(None, description="Content title")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content_length(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Content cannot be empty")
        if len(v) > 100000:  # 100k character limit
            raise ValueError("Content too long (max 100k characters)")
        return v

class AssessmentRequest(BaseModel):
    content: ContentForAssessment = Field(..., description="Content to assess")
    review_type: ReviewType = Field(default=ReviewType.DETAILED, description="Type of review")
    context: Optional[str] = Field(None, description="Additional context for assessment")
    target_audience: Optional[str] = Field(None, description="Target audience")
    content_purpose: Optional[str] = Field(None, description="Purpose of the content")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum quality threshold")

class QualityScores(BaseModel):
    overall: float = Field(..., ge=0.0, le=1.0)
    clarity: float = Field(..., ge=0.0, le=1.0)
    coherence: float = Field(..., ge=0.0, le=1.0)
    factual: float = Field(..., ge=0.0, le=1.0)
    tone: float = Field(..., ge=0.0, le=1.0)
    style: float = Field(..., ge=0.0, le=1.0)

class ImprovementSuggestion(BaseModel):
    issue_type: IssueType
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    description: str
    suggestion: str
    example: Optional[str] = None

class AssessmentResponse(BaseModel):
    assessment_id: str
    content_id: str
    result: AssessmentResult
    scores: QualityScores
    suggestions: List[ImprovementSuggestion]
    issues: List[str]
    word_count: int
    readability_grade: Optional[float]
    sentiment_score: Optional[float]
    processing_time_ms: int
    created_at: datetime

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    uptime_seconds: float
    assessments_processed: int
    average_processing_time_ms: float

# Database setup
def get_database():
    """Get database session"""
    database_url = config.get_database_url()
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    """Dependency for database session"""
    db = get_database()
    try:
        yield db
    finally:
        db.close()

# LLM Client for content analysis
class LLMClient:
    def __init__(self):
        self.config = config.get_llm_config()
        self.timeout = config.llm.timeout
    
    async def analyze_content(self, content: str, context: str = None) -> Dict[str, Any]:
        """Analyze content quality using LLM"""
        
        analysis_prompt = f"""
You are a content quality expert. Analyze the following content and provide detailed assessment scores and suggestions.

Content to analyze:
{content}

{f"Context: {context}" if context else ""}

Please provide:
1. Quality scores (0.0 to 1.0) for:
   - Clarity: How clear and understandable is the content?
   - Coherence: How well-structured and logical is the content?
   - Factual: How accurate and well-supported are the claims?
   - Tone: How appropriate is the tone for discourse?
   - Style: How well-written and engaging is the content?

2. Specific improvement suggestions with:
   - Issue type and severity
   - Clear description of the problem
   - Actionable suggestion for improvement
   - Example if helpful

3. Overall assessment: approved, needs_improvement, or rejected

Return the analysis as JSON with this structure:
{{
    "scores": {{
        "clarity": 0.0-1.0,
        "coherence": 0.0-1.0,
        "factual": 0.0-1.0,
        "tone": 0.0-1.0,
        "style": 0.0-1.0
    }},
    "suggestions": [
        {{
            "issue_type": "clarity|coherence|factual|tone|style|grammar|structure",
            "severity": "low|medium|high|critical",
            "description": "Description of issue",
            "suggestion": "How to improve",
            "example": "Optional example"
        }}
    ],
    "issues": ["List of detected issues"],
    "readability_grade": 0.0-20.0,
    "sentiment_score": -1.0 to 1.0,
    "overall_assessment": "approved|needs_improvement|rejected"
}}
"""
        
        try:
            if self.config.get("api_key"):
                # Use external LLM API
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.config['base_url']}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.config['api_key']}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.config["model"],
                            "messages": [{"role": "user", "content": analysis_prompt}],
                            "temperature": config.llm.temperature,
                            "max_tokens": config.llm.max_tokens
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    content_analysis = result["choices"][0]["message"]["content"]
            else:
                # Use Ollama local
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.config['base_url']}/api/generate",
                        json={
                            "model": self.config["model"],
                            "prompt": analysis_prompt,
                            "stream": False
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    content_analysis = result["response"]
            
            # Parse JSON response
            try:
                # Extract JSON from response if wrapped in markdown
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content_analysis, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group(1))
                else:
                    analysis_data = json.loads(content_analysis)
                
                return analysis_data
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM JSON response, using fallback analysis")
                return self._fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis(content)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when LLM is unavailable"""
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        
        # Basic heuristics
        clarity_score = min(1.0, max(0.3, 1.0 - (word_count / sentence_count - 15) / 50))
        coherence_score = 0.7 if word_count > 50 else 0.5
        factual_score = 0.6  # Neutral when can't verify
        tone_score = 0.8 if not any(word in content.lower() for word in ['hate', 'stupid', 'idiot']) else 0.3
        style_score = min(1.0, max(0.4, word_count / 1000))
        
        return {
            "scores": {
                "clarity": clarity_score,
                "coherence": coherence_score,
                "factual": factual_score,
                "tone": tone_score,
                "style": style_score
            },
            "suggestions": [
                {
                    "issue_type": "clarity",
                    "severity": "medium",
                    "description": "LLM unavailable - basic analysis only",
                    "suggestion": "Consider manual review for detailed assessment"
                }
            ],
            "issues": ["LLM analysis unavailable"],
            "readability_grade": max(6.0, min(16.0, word_count / sentence_count)),
            "sentiment_score": 0.0,
            "overall_assessment": "needs_improvement" if any(score < 0.6 for score in [clarity_score, coherence_score, tone_score]) else "approved"
        }

# Content Quality Service
class ContentQualityService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.start_time = time.time()
        self.assessments_count = 0
        self.total_processing_time = 0
    
    async def assess_content(self, request: AssessmentRequest, db: Session) -> AssessmentResponse:
        """Main content assessment function"""
        start_time = time.time()
        
        try:
            # Analyze content with LLM
            analysis = await self.llm_client.analyze_content(
                request.content.content,
                request.context
            )
            
            # Calculate overall score
            scores = analysis["scores"]
            overall_score = sum(scores.values()) / len(scores)
            
            # Determine assessment result
            if overall_score >= request.quality_threshold and analysis["overall_assessment"] == "approved":
                result = AssessmentResult.APPROVED
            elif overall_score >= 0.4:
                result = AssessmentResult.NEEDS_IMPROVEMENT
            else:
                result = AssessmentResult.REJECTED
            
            # Create suggestions objects
            suggestions = [
                ImprovementSuggestion(**suggestion) 
                for suggestion in analysis.get("suggestions", [])
            ]
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Create assessment record
            assessment = QualityAssessment(
                id=str(uuid.uuid4()),
                content_id=request.content.id,
                overall_score=overall_score,
                clarity_score=scores["clarity"],
                coherence_score=scores["coherence"],
                factual_score=scores["factual"],
                tone_score=scores["tone"],
                style_score=scores["style"],
                assessment_result=result.value,
                improvement_suggestions=[s.dict() for s in suggestions],
                detected_issues=analysis.get("issues", []),
                word_count=len(request.content.content.split()),
                readability_grade=analysis.get("readability_grade"),
                sentiment_score=analysis.get("sentiment_score"),
                llm_provider=config.llm.preferred_provider,
                llm_model=config.get_llm_config()["model"],
                processing_time_ms=processing_time,
                meta_data=request.content.metadata
            )
            
            db.add(assessment)
            db.commit()
            
            # Update stats
            self.assessments_count += 1
            self.total_processing_time += processing_time
            
            return AssessmentResponse(
                assessment_id=assessment.id,
                content_id=assessment.content_id,
                result=result,
                scores=QualityScores(
                    overall=overall_score,
                    clarity=scores["clarity"],
                    coherence=scores["coherence"],
                    factual=scores["factual"],
                    tone=scores["tone"],
                    style=scores["style"]
                ),
                suggestions=suggestions,
                issues=analysis.get("issues", []),
                word_count=assessment.word_count,
                readability_grade=assessment.readability_grade,
                sentiment_score=assessment.sentiment_score,
                processing_time_ms=processing_time,
                created_at=assessment.created_at
            )
            
        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

# Initialize service
quality_service = ContentQualityService()

# FastAPI app
app = FastAPI(
    title="Lamish Lawyer API",
    description="Content Quality Assessment and Style Review Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/assess", response_model=AssessmentResponse)
async def assess_content(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Assess content quality and provide improvement suggestions"""
    return await quality_service.assess_content(request, db)

@app.get("/assessment/{assessment_id}")
async def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    """Get specific assessment results"""
    assessment = db.query(QualityAssessment).filter(QualityAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {
        "assessment_id": assessment.id,
        "content_id": assessment.content_id,
        "result": assessment.assessment_result,
        "scores": {
            "overall": assessment.overall_score,
            "clarity": assessment.clarity_score,
            "coherence": assessment.coherence_score,
            "factual": assessment.factual_score,
            "tone": assessment.tone_score,
            "style": assessment.style_score
        },
        "suggestions": assessment.improvement_suggestions,
        "issues": assessment.detected_issues,
        "word_count": assessment.word_count,
        "readability_grade": assessment.readability_grade,
        "sentiment_score": assessment.sentiment_score,
        "processing_time_ms": assessment.processing_time_ms,
        "created_at": assessment.created_at
    }

@app.get("/assessments")
async def list_assessments(
    limit: int = 50,
    offset: int = 0,
    result_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List recent assessments with optional filtering"""
    query = db.query(QualityAssessment)
    
    if result_filter:
        query = query.filter(QualityAssessment.assessment_result == result_filter)
    
    assessments = query.order_by(QualityAssessment.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "assessments": [
            {
                "assessment_id": a.id,
                "content_id": a.content_id,
                "result": a.assessment_result,
                "overall_score": a.overall_score,
                "created_at": a.created_at
            }
            for a in assessments
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get assessment statistics"""
    total_assessments = db.query(QualityAssessment).count()
    approved = db.query(QualityAssessment).filter(QualityAssessment.assessment_result == "approved").count()
    needs_improvement = db.query(QualityAssessment).filter(QualityAssessment.assessment_result == "needs_improvement").count()
    rejected = db.query(QualityAssessment).filter(QualityAssessment.assessment_result == "rejected").count()
    
    avg_scores = db.query(QualityAssessment).with_entities(
        func.avg(QualityAssessment.overall_score),
        func.avg(QualityAssessment.clarity_score),
        func.avg(QualityAssessment.coherence_score),
        func.avg(QualityAssessment.factual_score),
        func.avg(QualityAssessment.tone_score),
        func.avg(QualityAssessment.style_score)
    ).first()
    
    return {
        "total_assessments": total_assessments,
        "results_breakdown": {
            "approved": approved,
            "needs_improvement": needs_improvement,
            "rejected": rejected
        },
        "average_scores": {
            "overall": float(avg_scores[0] or 0),
            "clarity": float(avg_scores[1] or 0),
            "coherence": float(avg_scores[2] or 0),
            "factual": float(avg_scores[3] or 0),
            "tone": float(avg_scores[4] or 0),
            "style": float(avg_scores[5] or 0)
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    avg_processing_time = (
        quality_service.total_processing_time / quality_service.assessments_count
        if quality_service.assessments_count > 0 else 0
    )
    
    return HealthResponse(
        uptime_seconds=time.time() - quality_service.start_time,
        assessments_processed=quality_service.assessments_count,
        average_processing_time_ms=avg_processing_time
    )

@app.post("/batch-assess")
async def batch_assess(
    requests: List[AssessmentRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Batch assessment for multiple content pieces"""
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 items per batch")
    
    results = []
    for request in requests:
        try:
            result = await quality_service.assess_content(request, db)
            results.append(result)
        except Exception as e:
            logger.error(f"Batch assessment item failed: {e}")
            results.append({"error": str(e), "content_id": request.content.id})
    
    return {"results": results, "processed": len(results)}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Lamish Lawyer API on port {config.api.lawyer_api_port}")
    logger.info(f"Using LLM provider: {config.llm.preferred_provider}")
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.lawyer_api_port,
        log_level="info"
    )