"""
Pipeline Router for Enhanced Lighthouse API
==========================================

Integrates the comprehensive pipeline system with the main API,
enabling sophisticated batch operations and HAW CLI command composition.
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Pipeline Router
pipeline_router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

# Pydantic Models for Pipeline Operations
class HAWCommand(BaseModel):
    """Individual HAW CLI command with parameters."""
    command: str = Field(..., description="HAW command (e.g., 'status', 'advanced-books')")
    args: List[str] = Field(default=[], description="Command arguments")
    timeout: int = Field(default=300, description="Timeout in seconds")
    description: str = Field(default="", description="Human-readable description")

class PipelineDefinition(BaseModel):
    """Definition of a pipeline with multiple HAW commands."""
    name: str = Field(..., description="Pipeline name")
    description: str = Field(..., description="Pipeline description")
    commands: List[HAWCommand] = Field(..., description="Sequence of HAW commands")
    parallel_execution: bool = Field(default=False, description="Run commands in parallel")
    continue_on_error: bool = Field(default=True, description="Continue if a command fails")
    quality_threshold: Optional[float] = Field(None, description="Quality threshold for content selection")
    max_content_items: Optional[int] = Field(None, description="Maximum content items to process")

class PipelineExecution(BaseModel):
    """Pipeline execution status and results."""
    pipeline_id: str
    name: str
    status: str  # pending, running, completed, failed, cancelled
    commands: List[Dict[str, Any]]
    progress: Dict[str, Any]
    results: List[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_duration_ms: Optional[int]

class BatchJobRequest(BaseModel):
    """Request for batch processing with HAW commands."""
    job_name: str = Field(..., description="Name for the batch job")
    pipeline_name: Optional[str] = Field(None, description="Predefined pipeline to use")
    custom_commands: Optional[List[HAWCommand]] = Field(None, description="Custom HAW commands")
    filters: Optional[Dict[str, Any]] = Field(None, description="Content filters")
    scheduling: Optional[Dict[str, Any]] = Field(None, description="Scheduling options")

class PipelineTemplate(BaseModel):
    """Reusable pipeline template."""
    template_id: str
    name: str
    description: str
    category: str
    commands: List[HAWCommand]
    default_params: Dict[str, Any]
    estimated_duration: Optional[int]
    resource_requirements: Dict[str, Any]

# In-memory storage for pipeline executions (in production, use database)
active_pipelines: Dict[str, PipelineExecution] = {}
pipeline_templates: Dict[str, PipelineTemplate] = {}

# Initialize predefined pipeline templates
def initialize_pipeline_templates():
    """Initialize predefined pipeline templates for common workflows."""
    
    templates = {
        "content_discovery": PipelineTemplate(
            template_id="content_discovery",
            name="Content Discovery Pipeline",
            description="Discover and analyze interesting content for insights",
            category="analysis",
            commands=[
                HAWCommand(
                    command="assess",
                    args=["stats"],
                    description="Get archive statistics"
                ),
                HAWCommand(
                    command="agentic",
                    args=["assess", "gem_detection", "--batch-size", "50"],
                    description="Find exceptional insights"
                ),
                HAWCommand(
                    command="sample",
                    args=["--min-quality", "0.6", "--limit", "100"],
                    description="Sample high-quality content"
                )
            ],
            default_params={"min_quality": 0.6, "batch_size": 50},
            estimated_duration=300,
            resource_requirements={"memory": "moderate", "cpu": "low"}
        ),
        
        "title_generation": PipelineTemplate(
            template_id="title_generation",
            name="Title Generation Pipeline",
            description="Generate titles for interesting content and create embeddings",
            category="content_generation",
            commands=[
                HAWCommand(
                    command="agentic",
                    args=["assess", "gem_detection", "--batch-size", "100"],
                    description="Identify interesting content"
                ),
                HAWCommand(
                    command="advanced-books",
                    args=["--analyze-only", "--min-quality", "0.6", "--max-books", "20"],
                    description="Generate titles from content analysis"
                ),
                HAWCommand(
                    command="embed",
                    args=["embed", "--limit", "200", "--timeout", "120"],
                    description="Create embeddings for titles"
                )
            ],
            default_params={"min_quality": 0.6, "max_books": 20, "embedding_limit": 200},
            estimated_duration=600,
            resource_requirements={"memory": "high", "cpu": "moderate"}
        ),
        
        "book_production": PipelineTemplate(
            template_id="book_production",
            name="Complete Book Production Pipeline",
            description="Full automated book creation from insights to publication",
            category="publishing",
            commands=[
                HAWCommand(
                    command="curate-book",
                    args=["analyze"],
                    description="Thematic analysis for book curation"
                ),
                HAWCommand(
                    command="advanced-books",
                    args=["--min-quality", "0.5", "--max-books", "5"],
                    description="Generate high-quality books"
                ),
                HAWCommand(
                    command="book-editor",
                    args=[],
                    description="AI-assisted editorial refinement"
                ),
                HAWCommand(
                    command="book-pipeline",
                    args=["--quality-threshold", "0.6"],
                    description="Final book production pipeline"
                )
            ],
            default_params={"quality_threshold": 0.5, "max_books": 5},
            estimated_duration=1200,
            resource_requirements={"memory": "high", "cpu": "high"}
        ),
        
        "embedding_batch": PipelineTemplate(
            template_id="embedding_batch",
            name="Batch Embedding Pipeline",
            description="Process content embeddings in optimized batches",
            category="processing",
            commands=[
                HAWCommand(
                    command="embed-full",
                    args=["--batch-size", "25", "--timeout", "180", "--min-score", "0.5"],
                    description="Full archive embedding with quality filter"
                ),
                HAWCommand(
                    command="monitor",
                    args=["status"],
                    description="Check embedding progress"
                )
            ],
            default_params={"batch_size": 25, "min_score": 0.5},
            estimated_duration=900,
            resource_requirements={"memory": "very_high", "cpu": "moderate"}
        ),
        
        "quality_assessment": PipelineTemplate(
            template_id="quality_assessment",
            name="Quality Assessment Pipeline",
            description="Comprehensive content quality evaluation",
            category="analysis",
            commands=[
                HAWCommand(
                    command="assess",
                    args=["--new-content", "--min-score", "0.7"],
                    description="Assess new content quality"
                ),
                HAWCommand(
                    command="agentic",
                    args=["assess", "editorial_assessment", "--batch-size", "50"],
                    description="Editorial quality assessment"
                ),
                HAWCommand(
                    command="pipeline-mgr",
                    args=["stats"],
                    description="Pipeline statistics"
                )
            ],
            default_params={"min_score": 0.7, "batch_size": 50},
            estimated_duration=400,
            resource_requirements={"memory": "moderate", "cpu": "moderate"}
        )
    }
    
    global pipeline_templates
    pipeline_templates = templates
    logger.info(f"Initialized {len(templates)} pipeline templates")

# Initialize templates on module load
initialize_pipeline_templates()

async def execute_haw_command(command: HAWCommand, working_dir: str = "/Users/tem/humanizer-lighthouse") -> Dict[str, Any]:
    """Execute a single HAW command with proper error handling."""
    
    start_time = datetime.now()
    
    try:
        # Build full command
        cmd_parts = ["./haw", command.command] + command.args
        full_command = " ".join(cmd_parts)
        
        logger.info(f"Executing HAW command: {full_command}")
        
        # Execute command
        process = subprocess.run(
            cmd_parts,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=command.timeout,
            env=dict(os.environ, **{
                "PYTHONPATH": f"{working_dir}:{os.environ.get('PYTHONPATH', '')}",
                "PATH": f"{working_dir}:{os.environ.get('PATH', '')}"
            })
        )
        
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "command": full_command,
            "description": command.description,
            "output": process.stdout or "",
            "error": process.stderr or "",
            "return_code": process.returncode,
            "duration_ms": duration_ms,
            "success": process.returncode == 0,
            "timestamp": start_time.isoformat()
        }
        
    except subprocess.TimeoutExpired:
        duration_ms = command.timeout * 1000
        return {
            "command": full_command,
            "description": command.description,
            "output": "",
            "error": f"Command timed out after {command.timeout} seconds",
            "return_code": 124,
            "duration_ms": duration_ms,
            "success": False,
            "timestamp": start_time.isoformat()
        }
        
    except Exception as e:
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        return {
            "command": full_command,
            "description": command.description,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "return_code": 1,
            "duration_ms": duration_ms,
            "success": False,
            "timestamp": start_time.isoformat()
        }

async def execute_pipeline(pipeline_def: PipelineDefinition) -> str:
    """Execute a pipeline and return the execution ID."""
    
    pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(active_pipelines)}"
    
    # Create pipeline execution record
    execution = PipelineExecution(
        pipeline_id=pipeline_id,
        name=pipeline_def.name,
        status="pending",
        commands=[],
        progress={"completed": 0, "total": len(pipeline_def.commands), "current_step": None},
        results=[],
        error_message=None,
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        total_duration_ms=None
    )
    
    active_pipelines[pipeline_id] = execution
    
    # Execute pipeline in background
    asyncio.create_task(run_pipeline_execution(pipeline_id, pipeline_def))
    
    return pipeline_id

async def run_pipeline_execution(pipeline_id: str, pipeline_def: PipelineDefinition):
    """Run the actual pipeline execution in the background."""
    
    execution = active_pipelines[pipeline_id]
    execution.status = "running"
    execution.started_at = datetime.now()
    
    try:
        if pipeline_def.parallel_execution:
            # Execute commands in parallel
            tasks = [execute_haw_command(cmd) for cmd in pipeline_def.commands]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    result = {
                        "command": pipeline_def.commands[i].command,
                        "error": str(result),
                        "success": False
                    }
                execution.results.append(result)
                
        else:
            # Execute commands sequentially
            for i, command in enumerate(pipeline_def.commands):
                execution.progress["current_step"] = command.command
                execution.progress["completed"] = i
                
                result = await execute_haw_command(command)
                execution.results.append(result)
                
                # Check if we should continue on error
                if not result["success"] and not pipeline_def.continue_on_error:
                    execution.error_message = f"Pipeline stopped at command '{command.command}': {result['error']}"
                    execution.status = "failed"
                    return
        
        # Pipeline completed successfully
        execution.status = "completed"
        execution.progress["completed"] = len(pipeline_def.commands)
        execution.progress["current_step"] = None
        
    except Exception as e:
        execution.status = "failed"
        execution.error_message = f"Pipeline execution error: {str(e)}"
        logger.error(f"Pipeline {pipeline_id} failed: {e}")
        
    finally:
        execution.completed_at = datetime.now()
        if execution.started_at:
            execution.total_duration_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )

# API Endpoints

@pipeline_router.get("/templates", response_model=List[PipelineTemplate])
async def get_pipeline_templates():
    """Get all available pipeline templates."""
    return list(pipeline_templates.values())

@pipeline_router.get("/templates/{template_id}", response_model=PipelineTemplate)
async def get_pipeline_template(template_id: str):
    """Get a specific pipeline template."""
    if template_id not in pipeline_templates:
        raise HTTPException(status_code=404, detail="Pipeline template not found")
    return pipeline_templates[template_id]

@pipeline_router.post("/execute")
async def execute_pipeline_from_template(
    template_id: str,
    custom_params: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Execute a pipeline from a template with optional parameter overrides."""
    
    if template_id not in pipeline_templates:
        raise HTTPException(status_code=404, detail="Pipeline template not found")
    
    template = pipeline_templates[template_id]
    
    # Apply custom parameters to commands
    commands = []
    for cmd in template.commands:
        new_args = cmd.args.copy()
        
        # Apply parameter overrides
        if custom_params:
            for i, arg in enumerate(new_args):
                if arg.startswith("--min-quality") and "min_quality" in custom_params:
                    if i + 1 < len(new_args):
                        new_args[i + 1] = str(custom_params["min_quality"])
                elif arg.startswith("--max-books") and "max_books" in custom_params:
                    if i + 1 < len(new_args):
                        new_args[i + 1] = str(custom_params["max_books"])
                elif arg.startswith("--batch-size") and "batch_size" in custom_params:
                    if i + 1 < len(new_args):
                        new_args[i + 1] = str(custom_params["batch_size"])
        
        commands.append(HAWCommand(
            command=cmd.command,
            args=new_args,
            timeout=cmd.timeout,
            description=cmd.description
        ))
    
    pipeline_def = PipelineDefinition(
        name=f"{template.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=template.description,
        commands=commands,
        parallel_execution=False,
        continue_on_error=True
    )
    
    pipeline_id = await execute_pipeline(pipeline_def)
    
    return {
        "pipeline_id": pipeline_id,
        "template_used": template_id,
        "status": "started",
        "estimated_duration": template.estimated_duration
    }

@pipeline_router.post("/execute/custom")
async def execute_custom_pipeline(pipeline_def: PipelineDefinition):
    """Execute a custom pipeline definition."""
    
    pipeline_id = await execute_pipeline(pipeline_def)
    
    return {
        "pipeline_id": pipeline_id,
        "status": "started",
        "commands_count": len(pipeline_def.commands)
    }

@pipeline_router.get("/executions", response_model=List[PipelineExecution])
async def get_pipeline_executions():
    """Get all pipeline executions."""
    return list(active_pipelines.values())

@pipeline_router.get("/executions/{pipeline_id}", response_model=PipelineExecution)
async def get_pipeline_execution(pipeline_id: str):
    """Get a specific pipeline execution."""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline execution not found")
    return active_pipelines[pipeline_id]

@pipeline_router.post("/executions/{pipeline_id}/cancel")
async def cancel_pipeline_execution(pipeline_id: str):
    """Cancel a running pipeline execution."""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline execution not found")
    
    execution = active_pipelines[pipeline_id]
    if execution.status == "running":
        execution.status = "cancelled"
        execution.completed_at = datetime.now()
        return {"message": "Pipeline cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail=f"Cannot cancel pipeline in status: {execution.status}")

@pipeline_router.delete("/executions/{pipeline_id}")
async def delete_pipeline_execution(pipeline_id: str):
    """Delete a pipeline execution from memory."""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline execution not found")
    
    execution = active_pipelines[pipeline_id]
    if execution.status == "running":
        raise HTTPException(status_code=400, detail="Cannot delete running pipeline")
    
    del active_pipelines[pipeline_id]
    return {"message": "Pipeline execution deleted"}

@pipeline_router.post("/batch/title-generation")
async def batch_title_generation(
    min_quality: float = 0.6,
    max_content_items: int = 100,
    generate_embeddings: bool = True
):
    """Start batch title generation for interesting content."""
    
    commands = [
        HAWCommand(
            command="agentic",
            args=["assess", "gem_detection", "--batch-size", "50"],
            description="Find interesting content for title generation"
        ),
        HAWCommand(
            command="advanced-books",
            args=["--analyze-only", "--min-quality", str(min_quality), "--max-books", "10"],
            description="Generate titles from interesting content"
        )
    ]
    
    if generate_embeddings:
        commands.append(HAWCommand(
            command="embed",
            args=["embed", "--limit", str(max_content_items), "--timeout", "180"],
            description="Create embeddings for generated titles"
        ))
    
    pipeline_def = PipelineDefinition(
        name="Batch Title Generation",
        description="Generate titles for interesting content with optional embeddings",
        commands=commands,
        parallel_execution=False,
        continue_on_error=True,
        quality_threshold=min_quality,
        max_content_items=max_content_items
    )
    
    pipeline_id = await execute_pipeline(pipeline_def)
    
    return {
        "pipeline_id": pipeline_id,
        "operation": "title_generation",
        "parameters": {
            "min_quality": min_quality,
            "max_content_items": max_content_items,
            "generate_embeddings": generate_embeddings
        }
    }

@pipeline_router.get("/system/status")
async def get_pipeline_system_status():
    """Get pipeline system status and statistics."""
    
    total_executions = len(active_pipelines)
    running_count = sum(1 for p in active_pipelines.values() if p.status == "running")
    completed_count = sum(1 for p in active_pipelines.values() if p.status == "completed")
    failed_count = sum(1 for p in active_pipelines.values() if p.status == "failed")
    
    return {
        "total_templates": len(pipeline_templates),
        "total_executions": total_executions,
        "running_pipelines": running_count,
        "completed_pipelines": completed_count,
        "failed_pipelines": failed_count,
        "available_templates": list(pipeline_templates.keys()),
        "system_health": "healthy" if running_count < 5 else "busy"
    }

@pipeline_router.post("/cleanup")
async def cleanup_completed_pipelines(older_than_hours: int = 24):
    """Clean up completed pipeline executions older than specified hours."""
    
    cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
    removed_count = 0
    
    for pipeline_id in list(active_pipelines.keys()):
        execution = active_pipelines[pipeline_id]
        if (execution.status in ["completed", "failed", "cancelled"] and 
            execution.completed_at and execution.completed_at < cutoff_time):
            del active_pipelines[pipeline_id]
            removed_count += 1
    
    return {
        "removed_executions": removed_count,
        "remaining_executions": len(active_pipelines)
    }

# Function to add pipeline routes to main app
def add_pipeline_routes(app):
    """Add pipeline routes to the FastAPI application."""
    app.include_router(pipeline_router)