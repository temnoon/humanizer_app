"""
Gutenberg Analysis API Routes
Endpoints for book discovery, analysis, and batch job management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from gutenberg_service import gutenberg_service, GutenbergBook, BookAnalysisJob
from models import APIResponse

router = APIRouter(prefix="/gutenberg", tags=["gutenberg"])


# Request/Response Models
class BookSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query for titles")
    author: Optional[str] = Field(None, description="Author name")
    subject: Optional[str] = Field(None, description="Subject category")
    language: str = Field("en", description="Language code")
    limit: int = Field(50, ge=1, le=200, description="Maximum results")


class AnalysisJobRequest(BaseModel):
    gutenberg_ids: List[int] = Field(..., min_items=1, max_items=20, description="List of Gutenberg book IDs")
    analysis_type: str = Field("sample", description="Analysis type: sample, targeted, or full")
    
    class Config:
        schema_extra = {
            "example": {
                "gutenberg_ids": [1342, 11, 84],
                "analysis_type": "sample"
            }
        }


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    gutenberg_ids: List[int]
    analysis_type: str
    results_summary: Optional[Dict[str, Any]]
    error_message: Optional[str]


class BookSearchResponse(BaseModel):
    books: List[Dict[str, Any]]
    total_found: int
    query_info: Dict[str, Any]


@router.get("/search", response_model=BookSearchResponse)
async def search_books(
    query: Optional[str] = Query(None, description="Search query"),
    author: Optional[str] = Query(None, description="Author name"),
    subject: Optional[str] = Query(None, description="Subject category"),
    language: str = Query("en", description="Language code"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results")
):
    """
    Search Project Gutenberg catalog for books
    
    Returns books matching the search criteria with metadata for analysis
    """
    try:
        books = await gutenberg_service.search_books(
            query=query,
            author=author,
            subject=subject,
            language=language,
            limit=limit
        )
        
        books_data = []
        for book in books:
            books_data.append({
                "gutenberg_id": book.gutenberg_id,
                "title": book.title,
                "author": book.author,
                "language": book.language,
                "subjects": book.subjects,
                "download_url": book.download_url,
                "file_size": book.file_size
            })
        
        return BookSearchResponse(
            books=books_data,
            total_found=len(books_data),
            query_info={
                "query": query,
                "author": author,
                "subject": subject,
                "language": language,
                "limit": limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/analyze", response_model=APIResponse)
async def create_analysis_job(request: AnalysisJobRequest):
    """
    Create a batch analysis job for Gutenberg books
    
    Analyzes books for attribute enrichment potential and returns job ID for tracking
    """
    try:
        # Validate analysis type
        valid_types = ["sample", "targeted", "full"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid analysis_type. Must be one of: {valid_types}"
            )
        
        job_id = await gutenberg_service.create_analysis_job(
            gutenberg_ids=request.gutenberg_ids,
            analysis_type=request.analysis_type
        )
        
        return APIResponse(
            success=True,
            message=f"Analysis job created successfully",
            data={
                "job_id": job_id,
                "gutenberg_ids": request.gutenberg_ids,
                "analysis_type": request.analysis_type,
                "status": "pending"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")


@router.get("/jobs", response_model=APIResponse)
async def list_analysis_jobs():
    """
    List all analysis jobs with their current status
    """
    try:
        jobs = await gutenberg_service.list_jobs()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "gutenberg_ids": job.gutenberg_ids,
                "analysis_type": job.analysis_type,
                "results_summary": job.results_summary,
                "error_message": job.error_message
            })
        
        return APIResponse(
            success=True,
            message=f"Found {len(jobs_data)} analysis jobs",
            data={"jobs": jobs_data}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get detailed status of a specific analysis job
    """
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            gutenberg_ids=job.gutenberg_ids,
            analysis_type=job.analysis_type,
            results_summary=job.results_summary,
            error_message=job.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/jobs/{job_id}/results", response_model=APIResponse)
async def get_job_results(job_id: str, limit: int = Query(50, ge=1, le=500)):
    """
    Get results of a completed analysis job
    
    Returns the best candidates for attribute enrichment
    """
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Job {job_id} is not completed (status: {job.status})"
            )
        
        results = await gutenberg_service.get_job_results(job_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
        
        # Limit the results returned
        if "high_quality_paragraphs" in results:
            results["high_quality_paragraphs"] = results["high_quality_paragraphs"][:limit]
        
        return APIResponse(
            success=True,
            message=f"Retrieved results for job {job_id}",
            data={
                "job_info": results["job"],
                "results": results.get("high_quality_paragraphs", []),
                "summary": results["job"]["results_summary"],
                "total_candidates": len(results.get("high_quality_paragraphs", [])),
                "returned_count": min(limit, len(results.get("high_quality_paragraphs", [])))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job results: {str(e)}")


@router.post("/jobs/{job_id}/enrich", response_model=APIResponse)
async def enrich_database_with_results(job_id: str, min_score: float = Query(0.5, ge=0.0, le=1.0)):
    """
    Add selected high-quality paragraphs to the content database for attribute enrichment
    """
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Job {job_id} is not completed (status: {job.status})"
            )
        
        results = await gutenberg_service.get_job_results(job_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
        
        # Filter paragraphs by minimum score
        high_quality_paragraphs = [
            p for p in results.get("high_quality_paragraphs", [])
            if p["attribute_enrichment_score"] >= min_score
        ]
        
        # TODO: Integrate with content_service to actually add to database
        # For now, just return the count that would be added
        
        enriched_count = len(high_quality_paragraphs)
        
        return APIResponse(
            success=True,
            message=f"Would enrich database with {enriched_count} high-quality paragraphs",
            data={
                "job_id": job_id,
                "min_score_threshold": min_score,
                "candidates_found": len(results.get("high_quality_paragraphs", [])),
                "enriched_count": enriched_count,
                "avg_enrichment_score": sum(p["attribute_enrichment_score"] for p in high_quality_paragraphs) / max(enriched_count, 1),
                "top_concepts": results["job"]["results_summary"].get("top_concepts", [])[:10]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enrich database: {str(e)}")


@router.delete("/jobs/{job_id}", response_model=APIResponse)
async def cancel_job(job_id: str):
    """
    Cancel a running analysis job
    """
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status in ["completed", "failed"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel job in {job.status} status"
            )
        
        # TODO: Implement actual job cancellation logic
        job.status = "cancelled"
        job.completed_at = datetime.now()
        
        return APIResponse(
            success=True,
            message=f"Job {job_id} cancelled successfully",
            data={"job_id": job_id, "status": "cancelled"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_analysis_stats():
    """
    Get overall statistics about Gutenberg analysis activities
    """
    try:
        jobs = await gutenberg_service.list_jobs()
        
        stats = {
            "total_jobs": len(jobs),
            "completed_jobs": len([j for j in jobs if j.status == "completed"]),
            "running_jobs": len([j for j in jobs if j.status == "running"]),
            "failed_jobs": len([j for j in jobs if j.status == "failed"]),
            "total_books_analyzed": sum(len(j.gutenberg_ids) for j in jobs if j.status == "completed"),
            "cache_size": len(list(gutenberg_service.cache_dir.glob("*.txt"))),
            "results_available": len(list(gutenberg_service.cache_dir.glob("analysis_results_*.json")))
        }
        
        return APIResponse(
            success=True,
            message="Analysis statistics retrieved",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")