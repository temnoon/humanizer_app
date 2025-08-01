#!/usr/bin/env python3
"""
Content Pipeline API
Provides formal API endpoints for pipeline configuration, execution, and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import uuid
import logging
from contextlib import asynccontextmanager

# Database and external dependencies
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums for type safety
class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransformationType(str, Enum):
    QUALITY_ENHANCEMENT = "quality_enhancement"
    STRUCTURAL_IMPROVEMENT = "structural_improvement"
    TONE_ADJUSTMENT = "tone_adjustment"
    LENGTH_OPTIMIZATION = "length_optimization"
    AUDIENCE_ADAPTATION = "audience_adaptation"
    FORMAT_CONVERSION = "format_conversion"

class DestinationType(str, Enum):
    HUMANIZER_THREAD = "humanizer_thread"
    BOOK_CHAPTER = "book_chapter"
    DISCOURSE_POST = "discourse_post"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    ACADEMIC_PAPER = "academic_paper"
    NEWSLETTER = "newsletter"

# Pydantic models for API requests/responses
class PipelineRuleCondition(BaseModel):
    min_quality: Optional[float] = None
    max_quality: Optional[float] = None
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    category: Optional[str] = None
    has_embedding: Optional[bool] = None

class PipelineRuleCreate(BaseModel):
    name: str = Field(..., description="Human-readable name for the rule")
    description: str = Field(..., description="Description of what this rule does")
    conditions: PipelineRuleCondition
    transformations: List[TransformationType]
    destinations: List[DestinationType]
    priority: int = Field(default=50, ge=1, le=100, description="Priority (1-100, higher = more priority)")
    active: bool = Field(default=True)

class PipelineRule(PipelineRuleCreate):
    rule_id: str
    created_at: datetime
    updated_at: datetime

class PipelineExecutionRequest(BaseModel):
    name: Optional[str] = Field(None, description="Optional name for this execution")
    conversation_ids: Optional[List[int]] = Field(None, description="Specific conversation IDs to process")
    filters: Optional[PipelineRuleCondition] = Field(None, description="Filters for auto-selecting conversations")
    rule_ids: Optional[List[str]] = Field(None, description="Specific rules to apply (default: all active)")
    limit: int = Field(default=10, ge=1, le=1000, description="Maximum conversations to process")
    dry_run: bool = Field(default=False, description="Preview what would be processed without executing")

class PipelineExecution(BaseModel):
    execution_id: str
    name: Optional[str]
    status: PipelineStatus
    conversation_ids: List[int]
    rules_applied: List[str]
    progress: Dict[str, Any]
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

class ContentTransformationResult(BaseModel):
    content_id: str
    conversation_id: int
    transformations_applied: List[str]
    destinations: List[str]
    success: bool
    error_message: Optional[str]
    processing_time_seconds: float

# Global state for pipeline executions
pipeline_executions: Dict[str, PipelineExecution] = {}
active_rules: Dict[str, PipelineRule] = {}

# Database configuration
DATABASE_URL = "postgresql://tem@localhost/humanizer_archive"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Content Pipeline API")
    
    # Load existing rules from database on startup
    await load_pipeline_rules_from_db()
    
    yield
    
    logger.info("🛑 Shutting down Content Pipeline API")

app = FastAPI(
    title="Content Pipeline API",
    description="Formal API for content transformation and routing",
    version="1.0.0",
    lifespan=lifespan
)

# Database helper functions
async def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

async def load_pipeline_rules_from_db():
    """Load pipeline rules from database"""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_rules (
                rule_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                conditions JSONB,
                transformations JSONB,
                destinations JSONB,
                priority INTEGER DEFAULT 50,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Load existing rules
        cursor.execute("SELECT * FROM pipeline_rules WHERE active = TRUE")
        rules = cursor.fetchall()
        
        for rule_data in rules:
            rule = PipelineRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                description=rule_data['description'],
                conditions=PipelineRuleCondition(**rule_data['conditions']),
                transformations=[TransformationType(t) for t in rule_data['transformations']],
                destinations=[DestinationType(d) for d in rule_data['destinations']],
                priority=rule_data['priority'],
                active=rule_data['active'],
                created_at=rule_data['created_at'],
                updated_at=rule_data['updated_at']
            )
            active_rules[rule.rule_id] = rule
        
        conn.commit()
        conn.close()
        
        logger.info(f"📋 Loaded {len(active_rules)} active pipeline rules")
        
    except Exception as e:
        logger.error(f"❌ Error loading pipeline rules: {e}")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Content Pipeline API",
        "timestamp": datetime.now().isoformat(),
        "active_rules": len(active_rules),
        "active_executions": len([e for e in pipeline_executions.values() if e.status == PipelineStatus.RUNNING])
    }

@app.get("/rules", response_model=List[PipelineRule])
async def list_pipeline_rules():
    """List all pipeline rules"""
    return list(active_rules.values())

@app.post("/rules", response_model=PipelineRule)
async def create_pipeline_rule(rule_data: PipelineRuleCreate):
    """Create a new pipeline rule"""
    try:
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        
        rule = PipelineRule(
            rule_id=rule_id,
            name=rule_data.name,
            description=rule_data.description,
            conditions=rule_data.conditions,
            transformations=rule_data.transformations,
            destinations=rule_data.destinations,
            priority=rule_data.priority,
            active=rule_data.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pipeline_rules 
            (rule_id, name, description, conditions, transformations, destinations, priority, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            rule.rule_id,
            rule.name,
            rule.description,
            rule.conditions.dict(),
            [t.value for t in rule.transformations],
            [d.value for d in rule.destinations],
            rule.priority,
            rule.active
        ))
        
        conn.commit()
        conn.close()
        
        # Add to active rules
        active_rules[rule_id] = rule
        
        logger.info(f"📋 Created pipeline rule: {rule.name}")
        return rule
        
    except Exception as e:
        logger.error(f"❌ Error creating pipeline rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/{rule_id}", response_model=PipelineRule)  
async def get_pipeline_rule(rule_id: str):
    """Get a specific pipeline rule"""
    if rule_id not in active_rules:
        raise HTTPException(status_code=404, detail="Pipeline rule not found")
    
    return active_rules[rule_id]

@app.put("/rules/{rule_id}", response_model=PipelineRule)
async def update_pipeline_rule(rule_id: str, rule_data: PipelineRuleCreate):
    """Update an existing pipeline rule"""
    if rule_id not in active_rules:
        raise HTTPException(status_code=404, detail="Pipeline rule not found")
    
    try:
        # Update the rule
        updated_rule = PipelineRule(
            rule_id=rule_id,
            name=rule_data.name,
            description=rule_data.description,
            conditions=rule_data.conditions,
            transformations=rule_data.transformations,
            destinations=rule_data.destinations,
            priority=rule_data.priority,
            active=rule_data.active,
            created_at=active_rules[rule_id].created_at,
            updated_at=datetime.now()
        )
        
        # Update in database
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pipeline_rules 
            SET name = %s, description = %s, conditions = %s, transformations = %s, 
                destinations = %s, priority = %s, active = %s, updated_at = NOW()
            WHERE rule_id = %s
        """, (
            updated_rule.name,
            updated_rule.description,
            updated_rule.conditions.dict(),
            [t.value for t in updated_rule.transformations],
            [d.value for d in updated_rule.destinations],
            updated_rule.priority,
            updated_rule.active,
            rule_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update in memory
        active_rules[rule_id] = updated_rule
        
        logger.info(f"📋 Updated pipeline rule: {updated_rule.name}")
        return updated_rule
        
    except Exception as e:
        logger.error(f"❌ Error updating pipeline rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rules/{rule_id}")
async def delete_pipeline_rule(rule_id: str):
    """Delete a pipeline rule"""
    if rule_id not in active_rules:
        raise HTTPException(status_code=404, detail="Pipeline rule not found")
    
    try:
        # Mark as inactive in database (soft delete)
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pipeline_rules 
            SET active = FALSE, updated_at = NOW()
            WHERE rule_id = %s
        """, (rule_id,))
        
        conn.commit()
        conn.close()
        
        # Remove from active rules
        del active_rules[rule_id]
        
        logger.info(f"📋 Deleted pipeline rule: {rule_id}")
        return {"message": "Pipeline rule deleted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error deleting pipeline rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute", response_model=PipelineExecution)
async def execute_pipeline(request: PipelineExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a pipeline with specified parameters"""
    execution_id = f"exec_{uuid.uuid4().hex[:8]}"
    
    try:
        # Get conversations to process
        conversation_ids = await get_conversations_for_execution(request)
        
        if not conversation_ids:
            raise HTTPException(status_code=400, detail="No conversations found matching criteria")
        
        # Create execution record
        execution = PipelineExecution(
            execution_id=execution_id,
            name=request.name,
            status=PipelineStatus.PENDING,
            conversation_ids=conversation_ids,
            rules_applied=request.rule_ids or list(active_rules.keys()),
            progress={"total": len(conversation_ids), "completed": 0, "failed": 0},
            results=None,
            error_message=None,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None
        )
        
        pipeline_executions[execution_id] = execution
        
        if request.dry_run:
            # Return preview without executing
            execution.status = PipelineStatus.COMPLETED
            execution.results = {
                "dry_run": True,
                "would_process": len(conversation_ids),
                "preview": conversation_ids[:5]
            }
            return execution
        
        # Start background execution
        background_tasks.add_task(execute_pipeline_background, execution_id, request)
        
        logger.info(f"📋 Started pipeline execution: {execution_id}")
        return execution
        
    except Exception as e:
        logger.error(f"❌ Error starting pipeline execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions", response_model=List[PipelineExecution])
async def list_pipeline_executions(status: Optional[PipelineStatus] = None, limit: int = 50):
    """List pipeline executions"""
    executions = list(pipeline_executions.values())
    
    if status:
        executions = [e for e in executions if e.status == status]
    
    # Sort by creation date (newest first) and limit
    executions.sort(key=lambda x: x.created_at, reverse=True)
    return executions[:limit]

@app.get("/executions/{execution_id}", response_model=PipelineExecution)
async def get_pipeline_execution(execution_id: str):
    """Get a specific pipeline execution"""
    if execution_id not in pipeline_executions:
        raise HTTPException(status_code=404, detail="Pipeline execution not found")
    
    return pipeline_executions[execution_id]

@app.post("/executions/{execution_id}/cancel")
async def cancel_pipeline_execution(execution_id: str):
    """Cancel a running pipeline execution"""
    if execution_id not in pipeline_executions:
        raise HTTPException(status_code=404, detail="Pipeline execution not found")
    
    execution = pipeline_executions[execution_id]
    
    if execution.status not in [PipelineStatus.PENDING, PipelineStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Cannot cancel execution in current status")
    
    execution.status = PipelineStatus.CANCELLED
    execution.completed_at = datetime.now()
    
    logger.info(f"📋 Cancelled pipeline execution: {execution_id}")
    return {"message": "Pipeline execution cancelled"}

@app.get("/stats")
async def get_pipeline_stats():
    """Get pipeline system statistics"""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        # Get execution stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_executions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running
            FROM pipeline_executions
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        execution_stats = cursor.fetchone() or {}
        
        # Get transformation stats
        cursor.execute("""
            SELECT 
                destination,
                COUNT(*) as count
            FROM content_pipeline_records 
            WHERE processed_at >= NOW() - INTERVAL '7 days'
            GROUP BY destination
            ORDER BY count DESC
        """)
        
        destination_stats = {row['destination']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "active_rules": len(active_rules),
            "execution_stats": execution_stats,
            "destination_stats": destination_stats,
            "current_executions": len([e for e in pipeline_executions.values() if e.status == PipelineStatus.RUNNING])
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting pipeline stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background processing functions
async def get_conversations_for_execution(request: PipelineExecutionRequest) -> List[int]:
    """Get conversation IDs for pipeline execution"""
    if request.conversation_ids:
        return request.conversation_ids
    
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        conditions = ["ac.content_type = 'conversation'"]
        params = []
        
        if request.filters:
            if request.filters.min_quality is not None:
                conditions.append("cqa.composite_score >= %s")
                params.append(request.filters.min_quality)
            
            if request.filters.max_quality is not None:
                conditions.append("cqa.composite_score <= %s")
                params.append(request.filters.max_quality)
            
            if request.filters.category:
                conditions.append("ac.category = %s")
                params.append(request.filters.category)
            
            if request.filters.min_words is not None:
                conditions.append("COALESCE(cqa.word_count, ac.word_count, 0) >= %s")
                params.append(request.filters.min_words)
            
            if request.filters.max_words is not None:
                conditions.append("COALESCE(cqa.word_count, ac.word_count, 0) <= %s")
                params.append(request.filters.max_words)
            
            if request.filters.has_embedding is not None:
                if request.filters.has_embedding:
                    conditions.append("ac.semantic_vector IS NOT NULL")
                else:
                    conditions.append("ac.semantic_vector IS NULL")
        
        query = f"""
            SELECT ac.id
            FROM archived_content ac
            LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
            WHERE {' AND '.join(conditions)}
            ORDER BY cqa.composite_score DESC NULLS LAST
            LIMIT %s
        """
        params.append(request.limit)
        
        cursor.execute(query, params)
        conversation_ids = [row['id'] for row in cursor.fetchall()]
        
        conn.close()
        return conversation_ids
        
    except Exception as e:
        logger.error(f"❌ Error getting conversations for execution: {e}")
        return []

async def execute_pipeline_background(execution_id: str, request: PipelineExecutionRequest):
    """Background task for pipeline execution"""
    execution = pipeline_executions[execution_id]
    
    try:
        execution.status = PipelineStatus.RUNNING
        execution.started_at = datetime.now()
        
        logger.info(f"📋 Starting pipeline execution: {execution_id}")
        
        # Process each conversation
        results = []
        for i, conversation_id in enumerate(execution.conversation_ids):
            try:
                # Simulate content processing (replace with actual pipeline logic)
                result = await process_conversation_through_pipeline(
                    conversation_id, 
                    execution.rules_applied
                )
                results.append(result)
                
                # Update progress
                execution.progress["completed"] += 1
                
                logger.info(f"📋 Processed conversation {conversation_id} ({i+1}/{len(execution.conversation_ids)})")
                
            except Exception as e:
                logger.error(f"❌ Error processing conversation {conversation_id}: {e}")
                execution.progress["failed"] += 1
                
                results.append(ContentTransformationResult(
                    content_id=f"conv_{conversation_id}",
                    conversation_id=conversation_id,
                    transformations_applied=[],
                    destinations=[],
                    success=False,
                    error_message=str(e),
                    processing_time_seconds=0.0
                ))
        
        # Complete execution
        execution.status = PipelineStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.results = {
            "total_processed": len(results),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "transformations": results
        }
        
        logger.info(f"✅ Completed pipeline execution: {execution_id}")
        
    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {e}")
        execution.status = PipelineStatus.FAILED
        execution.completed_at = datetime.now()
        execution.error_message = str(e)

async def process_conversation_through_pipeline(conversation_id: int, rule_ids: List[str]) -> ContentTransformationResult:
    """Process a single conversation through the pipeline"""
    start_time = datetime.now()
    
    try:
        # Simulate processing (replace with actual pipeline logic)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ContentTransformationResult(
            content_id=f"conv_{conversation_id}",
            conversation_id=conversation_id,
            transformations_applied=["quality_enhancement"],
            destinations=["book_chapter"],
            success=True,
            error_message=None,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ContentTransformationResult(
            content_id=f"conv_{conversation_id}",
            conversation_id=conversation_id,
            transformations_applied=[],
            destinations=[],
            success=False,
            error_message=str(e),
            processing_time_seconds=processing_time
        )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "pipeline_api:app",
        host="127.0.0.1",
        port=7204,
        reload=False,
        log_level="info"
    )