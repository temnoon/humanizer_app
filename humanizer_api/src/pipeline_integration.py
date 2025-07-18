"""
Pipeline Integration Client for Humanizer API Services

Connects Archive API → LPE API → Lawyer API for seamless content processing pipeline.
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from config import get_config

logger = logging.getLogger(__name__)
config = get_config()

@dataclass
class PipelineResult:
    """Result from pipeline processing"""
    success: bool
    stage: str
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None

class HumanizerPipelineClient:
    """Client for integrating Archive, LPE, and Lawyer APIs"""
    
    def __init__(self):
        self.archive_base_url = f"http://localhost:{config.api.archive_api_port}"
        self.lpe_base_url = f"http://localhost:{config.api.lpe_api_port}"
        self.lawyer_base_url = f"http://localhost:{config.api.lawyer_api_port}"
        self.timeout = 300  # 5 minute timeout for pipeline
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all services"""
        results = {}
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Check Archive API
            try:
                response = await client.get(f"{self.archive_base_url}/health")
                results["archive"] = response.status_code == 200
            except:
                results["archive"] = False
            
            # Check LPE API
            try:
                response = await client.get(f"{self.lpe_base_url}/health")
                results["lpe"] = response.status_code == 200
            except:
                results["lpe"] = False
            
            # Check Lawyer API
            try:
                response = await client.get(f"{self.lawyer_base_url}/health")
                results["lawyer"] = response.status_code == 200
            except:
                results["lawyer"] = False
        
        return results
    
    async def ingest_content(self, content: str, source: str, content_type: str = "text", 
                           title: str = None, metadata: Dict[str, Any] = None) -> PipelineResult:
        """Ingest content into Archive API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                form_data = {
                    "content_type": content_type,
                    "source": source,
                    "data": content
                }
                
                if title:
                    form_data["title"] = title
                
                if metadata:
                    form_data["metadata"] = str(metadata)
                
                response = await client.post(
                    f"{self.archive_base_url}/ingest",
                    data=form_data
                )
                response.raise_for_status()
                
                return PipelineResult(
                    success=True,
                    stage="archive",
                    data=response.json()
                )
                
        except Exception as e:
            logger.error(f"Archive ingestion failed: {e}")
            return PipelineResult(
                success=False,
                stage="archive",
                data={},
                error=str(e)
            )
    
    async def transform_content(self, content: str, processing_type: str = "projection",
                              parameters: Dict[str, Any] = None) -> PipelineResult:
        """Transform content using LPE API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_data = {
                    "content": [{
                        "content_type": "text",
                        "data": content
                    }],
                    "processing_type": processing_type,
                    "parameters": parameters or {}
                }
                
                response = await client.post(
                    f"{self.lpe_base_url}/transform",
                    json=request_data
                )
                response.raise_for_status()
                
                return PipelineResult(
                    success=True,
                    stage="lpe",
                    data=response.json()
                )
                
        except Exception as e:
            logger.error(f"LPE transformation failed: {e}")
            return PipelineResult(
                success=False,
                stage="lpe",
                data={},
                error=str(e)
            )
    
    async def assess_content(self, content: str, content_id: str = None,
                           quality_threshold: float = 0.7, context: str = None) -> PipelineResult:
        """Assess content quality using Lawyer API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_data = {
                    "content": {
                        "id": content_id or f"assess_{int(datetime.now().timestamp())}",
                        "content": content,
                        "content_type": "text"
                    },
                    "review_type": "detailed",
                    "quality_threshold": quality_threshold
                }
                
                if context:
                    request_data["context"] = context
                
                response = await client.post(
                    f"{self.lawyer_base_url}/assess",
                    json=request_data
                )
                response.raise_for_status()
                
                return PipelineResult(
                    success=True,
                    stage="lawyer",
                    data=response.json()
                )
                
        except Exception as e:
            logger.error(f"Lawyer assessment failed: {e}")
            return PipelineResult(
                success=False,
                stage="lawyer",
                data={},
                error=str(e)
            )
    
    async def full_pipeline(self, content: str, source: str = "pipeline_test",
                          transform_type: str = "projection",
                          quality_threshold: float = 0.7) -> Dict[str, PipelineResult]:
        """Run full content pipeline: Archive → LPE → Lawyer"""
        results = {}
        
        # Step 1: Ingest into Archive
        logger.info("Pipeline Step 1: Ingesting content")
        archive_result = await self.ingest_content(content, source)
        results["archive"] = archive_result
        
        if not archive_result.success:
            return results
        
        content_id = archive_result.data.get("content_id")
        
        # Step 2: Transform with LPE
        logger.info("Pipeline Step 2: Transforming content")
        lpe_result = await self.transform_content(content, transform_type)
        results["lpe"] = lpe_result
        
        # Use transformed content if available, otherwise original
        final_content = content
        if lpe_result.success and lpe_result.data.get("results"):
            transformed = lpe_result.data["results"][0].get("output_content")
            if transformed:
                final_content = transformed
        
        # Step 3: Assess with Lawyer
        logger.info("Pipeline Step 3: Assessing content quality")
        lawyer_result = await self.assess_content(
            final_content, 
            content_id=content_id,
            quality_threshold=quality_threshold,
            context=f"Content processed through {transform_type} transformation"
        )
        results["lawyer"] = lawyer_result
        
        return results
    
    async def search_and_assess(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search archived content and assess quality of results"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search in Archive
                search_response = await client.post(
                    f"{self.archive_base_url}/search",
                    data={"query": query, "limit": str(limit)}
                )
                search_response.raise_for_status()
                search_results = search_response.json()
                
                # Assess each result
                assessments = []
                for item in search_results.get("results", []):
                    content = item.get("content_data", "")
                    if content:
                        assessment = await self.assess_content(
                            content,
                            content_id=item.get("id"),
                            context=f"Search result for query: {query}"
                        )
                        assessments.append({
                            "content_id": item.get("id"),
                            "title": item.get("title"),
                            "assessment": assessment.data if assessment.success else None,
                            "error": assessment.error
                        })
                
                return {
                    "search_results": search_results,
                    "quality_assessments": assessments,
                    "total_assessed": len(assessments)
                }
                
        except Exception as e:
            logger.error(f"Search and assess failed: {e}")
            return {"error": str(e)}
    
    async def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics from all services"""
        stats = {}
        
        async with httpx.AsyncClient(timeout=30) as client:
            # Archive stats
            try:
                response = await client.get(f"{self.archive_base_url}/stats")
                if response.status_code == 200:
                    stats["archive"] = response.json()
            except:
                stats["archive"] = {"error": "Service unavailable"}
            
            # LPE stats
            try:
                response = await client.get(f"{self.lpe_base_url}/stats")
                if response.status_code == 200:
                    stats["lpe"] = response.json()
            except:
                stats["lpe"] = {"error": "Service unavailable"}
            
            # Lawyer stats
            try:
                response = await client.get(f"{self.lawyer_base_url}/stats")
                if response.status_code == 200:
                    stats["lawyer"] = response.json()
            except:
                stats["lawyer"] = {"error": "Service unavailable"}
        
        return stats

# Convenience functions for common operations
async def quick_assess(content: str, threshold: float = 0.7) -> Dict[str, Any]:
    """Quick content assessment"""
    client = HumanizerPipelineClient()
    result = await client.assess_content(content, quality_threshold=threshold)
    return result.data if result.success else {"error": result.error}

async def full_process(content: str, source: str = "api_test") -> Dict[str, Any]:
    """Process content through full pipeline"""
    client = HumanizerPipelineClient()
    results = await client.full_pipeline(content, source)
    
    # Summarize results
    summary = {
        "pipeline_success": all(r.success for r in results.values()),
        "stages_completed": [stage for stage, result in results.items() if result.success],
        "final_assessment": None,
        "errors": [f"{stage}: {result.error}" for stage, result in results.items() if not result.success]
    }
    
    if "lawyer" in results and results["lawyer"].success:
        summary["final_assessment"] = results["lawyer"].data
    
    return {
        "summary": summary,
        "detailed_results": {stage: result.data for stage, result in results.items()}
    }

if __name__ == "__main__":
    # Example usage
    async def test_pipeline():
        client = HumanizerPipelineClient()
        
        # Health check
        health = await client.health_check_all()
        print("Service Health:", health)
        
        # Test content
        test_content = """
        The rapid advancement of artificial intelligence presents both unprecedented opportunities 
        and significant challenges for society. While AI systems can enhance productivity and 
        solve complex problems, we must carefully consider their impact on employment, privacy, 
        and human agency. A balanced approach that prioritizes human values while embracing 
        innovation will be essential for navigating this technological transformation successfully.
        """
        
        # Run full pipeline
        results = await full_process(test_content.strip())
        print("\nPipeline Results:", results)
    
    asyncio.run(test_pipeline())