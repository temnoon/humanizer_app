#!/usr/bin/env python3
"""
Attribute Processing Agent
=========================

Intelligent agent that manages content processing pipelines between 
archive retrieval, attribute extraction, validation, and allegory engine transformation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

from pydantic import BaseModel, Field, validator
from attribute_taxonomy import AttributeCollection, HumanReadableAttribute, transform_technical_attributes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Processing job status tracking"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    TRANSFORMING = "transforming"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job processing priority levels"""
    URGENT = "urgent"      # Process immediately
    HIGH = "high"          # Process within 1 hour
    NORMAL = "normal"      # Process within 24 hours
    LOW = "low"           # Process when resources available
    BATCH = "batch"       # Batch processing mode


class ValidationResult(BaseModel):
    """Result of attribute validation"""
    is_valid: bool = Field(..., description="Whether the attributes pass validation")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence in results")
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class ProcessingJob(BaseModel):
    """Individual content processing job with full lifecycle tracking"""
    
    # Job identification
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str = Field(..., description="Type of content source (conversation, document, etc.)")
    source_id: str = Field(..., description="Unique identifier for source content")
    
    # Job configuration
    priority: JobPriority = Field(JobPriority.NORMAL)
    processing_goals: List[str] = Field(default_factory=list, description="What should be accomplished")
    attribute_categories: List[str] = Field(default_factory=list, description="Which attribute categories to extract")
    transformation_targets: Dict[str, str] = Field(default_factory=dict, description="Allegory engine targets")
    
    # Job state
    status: JobStatus = Field(JobStatus.PENDING)
    current_step: str = Field("", description="Current processing step")
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    
    # Results and outputs
    extracted_attributes: Optional[AttributeCollection] = Field(None)
    validation_result: Optional[ValidationResult] = Field(None)
    transformation_outputs: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata and tracking
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    estimated_completion: Optional[datetime] = Field(None)
    
    # Error handling
    retry_count: int = Field(0)
    max_retries: int = Field(3)
    error_messages: List[str] = Field(default_factory=list)
    
    # Quality metrics
    processing_time_seconds: float = Field(0.0)
    resource_usage: Dict[str, float] = Field(default_factory=dict)
    
    def add_error(self, error_message: str):
        """Add an error message and increment retry count"""
        self.error_messages.append(f"{datetime.now().isoformat()}: {error_message}")
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries and self.status == JobStatus.FAILED
    
    def estimate_completion_time(self) -> datetime:
        """Estimate when job will complete based on priority and complexity"""
        base_minutes = {
            JobPriority.URGENT: 5,
            JobPriority.HIGH: 30,
            JobPriority.NORMAL: 120,
            JobPriority.LOW: 480,
            JobPriority.BATCH: 1440
        }
        
        complexity_multiplier = len(self.attribute_categories) * 0.5 + 1.0
        estimated_minutes = base_minutes[self.priority] * complexity_multiplier
        
        return datetime.now() + timedelta(minutes=estimated_minutes)


class AttributeValidator:
    """Validates extracted attributes for quality and consistency"""
    
    def __init__(self):
        self.validation_rules = {
            'min_attributes': 5,
            'min_confidence': 0.3,
            'max_outlier_ratio': 0.2,
            'required_categories': ['textual_rhythm', 'linguistic_structure']
        }
    
    async def validate_attributes(self, attributes: AttributeCollection) -> ValidationResult:
        """Comprehensive attribute validation"""
        errors = []
        warnings = []
        recommendations = []
        quality_metrics = {}
        
        # Check minimum attribute count
        if attributes.total_attributes < self.validation_rules['min_attributes']:
            errors.append(f"Too few attributes extracted: {attributes.total_attributes} < {self.validation_rules['min_attributes']}")
        
        # Check attribute confidence levels
        all_attributes = []
        for category in ['textual_rhythm', 'linguistic_structure', 'narrative_voice', 
                        'content_domain', 'stylistic_signature', 'discourse_patterns',
                        'emotional_resonance', 'cognitive_complexity']:
            all_attributes.extend(getattr(attributes, category, []))
        
        if all_attributes:
            confidences = [attr.confidence for attr in all_attributes]
            avg_confidence = sum(confidences) / len(confidences)
            quality_metrics['average_confidence'] = avg_confidence
            
            if avg_confidence < self.validation_rules['min_confidence']:
                warnings.append(f"Low average confidence: {avg_confidence:.2f}")
                recommendations.append("Consider reprocessing with different parameters")
            
            # Check for outliers
            outliers = [c for c in confidences if c < 0.1 or c > 0.95]
            outlier_ratio = len(outliers) / len(confidences)
            quality_metrics['outlier_ratio'] = outlier_ratio
            
            if outlier_ratio > self.validation_rules['max_outlier_ratio']:
                warnings.append(f"High outlier ratio: {outlier_ratio:.2f}")
        
        # Check category coverage
        filled_categories = []
        for category in ['textual_rhythm', 'linguistic_structure', 'narrative_voice', 
                        'content_domain', 'stylistic_signature', 'discourse_patterns',
                        'emotional_resonance', 'cognitive_complexity']:
            if len(getattr(attributes, category, [])) > 0:
                filled_categories.append(category)
        
        quality_metrics['category_coverage'] = len(filled_categories) / 8.0
        
        missing_required = set(self.validation_rules['required_categories']) - set(filled_categories)
        if missing_required:
            errors.append(f"Missing required categories: {missing_required}")
        
        # Calculate overall confidence
        error_penalty = len(errors) * 0.2
        warning_penalty = len(warnings) * 0.1
        confidence_bonus = quality_metrics.get('average_confidence', 0.5)
        coverage_bonus = quality_metrics.get('category_coverage', 0.5) * 0.3
        
        overall_confidence = max(0.0, min(1.0, confidence_bonus + coverage_bonus - error_penalty - warning_penalty))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            confidence_score=overall_confidence,
            quality_metrics=quality_metrics,
            validation_errors=errors,
            validation_warnings=warnings,
            recommended_actions=recommendations
        )


class AttributeProcessingAgent:
    """Intelligent agent for managing attribute processing pipelines"""
    
    def __init__(self, 
                 archive_client=None,
                 attribute_extractor=None,
                 allegory_client=None,
                 max_concurrent_jobs: int = 5):
        
        self.archive_client = archive_client
        self.attribute_extractor = attribute_extractor
        self.allegory_client = allegory_client
        self.validator = AttributeValidator()
        
        # Job management
        self.job_queue: List[ProcessingJob] = []
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.completed_jobs: Dict[str, ProcessingJob] = {}
        self.max_concurrent_jobs = max_concurrent_jobs
        
        # Agent state
        self.is_running = False
        self.processing_stats = {
            'jobs_processed': 0,
            'jobs_failed': 0,
            'average_processing_time': 0.0,
            'total_attributes_extracted': 0
        }
        
        # Tool registry for extensibility
        self.tools = {
            'archive_retrieval': self._retrieve_from_archive,
            'attribute_extraction': self._extract_attributes,
            'attribute_validation': self._validate_attributes,
            'allegory_transformation': self._transform_with_allegory,
            'quality_assessment': self._assess_quality
        }
    
    async def submit_job(self, job: ProcessingJob) -> str:
        """Submit a new processing job"""
        job.estimated_completion = job.estimate_completion_time()
        self.job_queue.append(job)
        
        # Sort queue by priority
        priority_order = {
            JobPriority.URGENT: 0,
            JobPriority.HIGH: 1,
            JobPriority.NORMAL: 2,
            JobPriority.LOW: 3,
            JobPriority.BATCH: 4
        }
        self.job_queue.sort(key=lambda j: priority_order[j.priority])
        
        logger.info(f"Job {job.job_id} submitted with priority {job.priority}")
        return job.job_id
    
    async def start_processing(self):
        """Start the job processing loop"""
        self.is_running = True
        logger.info("Attribute Processing Agent started")
        
        while self.is_running:
            try:
                await self._process_job_queue()
                await asyncio.sleep(1)  # Prevent busy waiting
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def stop_processing(self):
        """Stop the job processing loop"""
        self.is_running = False
        
        # Wait for active jobs to complete
        if self.active_jobs:
            logger.info(f"Waiting for {len(self.active_jobs)} active jobs to complete...")
            while self.active_jobs:
                await asyncio.sleep(1)
        
        logger.info("Attribute Processing Agent stopped")
    
    async def _process_job_queue(self):
        """Process jobs from the queue"""
        # Start new jobs if we have capacity
        while (len(self.active_jobs) < self.max_concurrent_jobs and 
               self.job_queue and 
               self.is_running):
            
            job = self.job_queue.pop(0)
            job.status = JobStatus.ANALYZING
            job.started_at = datetime.now()
            
            self.active_jobs[job.job_id] = job
            
            # Process job asynchronously
            asyncio.create_task(self._process_single_job(job))
    
    async def _process_single_job(self, job: ProcessingJob):
        """Process a single job through the complete pipeline"""
        try:
            logger.info(f"Starting job {job.job_id}: {job.source_type}:{job.source_id}")
            
            # Step 1: Retrieve content from archive
            job.current_step = "archive_retrieval"
            job.progress_percentage = 10.0
            content = await self.tools['archive_retrieval'](job)
            
            if not content:
                raise Exception("Failed to retrieve content from archive")
            
            # Step 2: Extract attributes
            job.current_step = "attribute_extraction"
            job.progress_percentage = 30.0
            job.status = JobStatus.EXTRACTING
            
            raw_attributes = await self.tools['attribute_extraction'](content, job)
            job.extracted_attributes = transform_technical_attributes(raw_attributes)
            
            # Step 3: Validate attributes
            job.current_step = "attribute_validation"
            job.progress_percentage = 60.0
            job.status = JobStatus.VALIDATING
            
            validation_result = await self.tools['attribute_validation'](job.extracted_attributes)
            job.validation_result = validation_result
            
            if not validation_result.is_valid:
                if job.can_retry():
                    job.add_error("Attribute validation failed, retrying with different parameters")
                    job.status = JobStatus.RETRYING
                    # Re-queue for retry
                    self.job_queue.insert(0, job)
                    return
                else:
                    raise Exception(f"Attribute validation failed after {job.max_retries} retries")
            
            # Step 4: Transform with Allegory Engine (if requested)
            if job.transformation_targets:
                job.current_step = "allegory_transformation"
                job.progress_percentage = 80.0
                job.status = JobStatus.TRANSFORMING
                
                transformations = await self.tools['allegory_transformation'](content, job)
                job.transformation_outputs = transformations
            
            # Step 5: Final quality assessment
            job.current_step = "quality_assessment"
            job.progress_percentage = 95.0
            
            quality_score = await self.tools['quality_assessment'](job)
            job.validation_result.quality_metrics['final_quality_score'] = quality_score
            
            # Job completion
            job.status = JobStatus.COMPLETED
            job.progress_percentage = 100.0
            job.completed_at = datetime.now()
            job.processing_time_seconds = (job.completed_at - job.started_at).total_seconds()
            
            # Update statistics
            self.processing_stats['jobs_processed'] += 1
            self.processing_stats['total_attributes_extracted'] += job.extracted_attributes.total_attributes
            
            # Calculate rolling average processing time
            current_avg = self.processing_stats['average_processing_time']
            job_count = self.processing_stats['jobs_processed']
            new_avg = ((current_avg * (job_count - 1)) + job.processing_time_seconds) / job_count
            self.processing_stats['average_processing_time'] = new_avg
            
            logger.info(f"Job {job.job_id} completed successfully in {job.processing_time_seconds:.1f}s")
            
        except Exception as e:
            job.add_error(str(e))
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            self.processing_stats['jobs_failed'] += 1
            
            logger.error(f"Job {job.job_id} failed: {e}")
        
        finally:
            # Move job to completed jobs and remove from active
            self.completed_jobs[job.job_id] = job
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
    
    # Tool implementations
    async def _retrieve_from_archive(self, job: ProcessingJob) -> Optional[Dict[str, Any]]:
        """Retrieve content from archive based on job configuration"""
        if not self.archive_client:
            logger.warning("No archive client configured, using mock data")
            return {"text": "Sample text for processing", "metadata": {}}
        
        try:
            if job.source_type == "conversation":
                content = await self.archive_client.get_conversation_messages(int(job.source_id))
                return content
            else:
                # Handle other source types
                return await self.archive_client.get_content(job.source_id)
        except Exception as e:
            logger.error(f"Archive retrieval failed: {e}")
            return None
    
    async def _extract_attributes(self, content: Dict[str, Any], job: ProcessingJob) -> Dict[str, Any]:
        """Extract technical attributes from content"""
        if not self.attribute_extractor:
            logger.warning("No attribute extractor configured, using mock attributes")
            return {
                'avg_sentence_length': 18.5,
                'comma_density': 0.045,
                'flesch_ease': 67.2,
                'noun_ratio': 0.28,
                'subordination_ratio': 0.15
            }
        
        # Extract text from content
        if 'messages' in content:
            # Conversation format
            combined_text = "\n".join([msg.get('content', msg.get('body_text', '')) 
                                     for msg in content['messages']])
        else:
            combined_text = content.get('text', str(content))
        
        return await self.attribute_extractor.extract_features(combined_text)
    
    async def _validate_attributes(self, attributes: AttributeCollection) -> ValidationResult:
        """Validate extracted attributes"""
        return await self.validator.validate_attributes(attributes)
    
    async def _transform_with_allegory(self, content: Dict[str, Any], job: ProcessingJob) -> Dict[str, Any]:
        """Transform content using Allegory Engine"""
        if not self.allegory_client:
            logger.warning("No allegory client configured, skipping transformation")
            return {}
        
        transformations = {}
        for target_name, target_config in job.transformation_targets.items():
            try:
                result = await self.allegory_client.transform(content, target_config)
                transformations[target_name] = result
            except Exception as e:
                logger.error(f"Allegory transformation '{target_name}' failed: {e}")
                transformations[target_name] = {"error": str(e)}
        
        return transformations
    
    async def _assess_quality(self, job: ProcessingJob) -> float:
        """Assess overall quality of job results"""
        quality_factors = []
        
        # Validation confidence
        if job.validation_result:
            quality_factors.append(job.validation_result.confidence_score)
        
        # Attribute coverage
        if job.extracted_attributes:
            coverage = job.extracted_attributes.total_attributes / 20.0  # Expect ~20 attributes
            quality_factors.append(min(1.0, coverage))
        
        # Processing time factor (faster is better, up to a point)
        if job.processing_time_seconds > 0:
            time_factor = max(0.5, min(1.0, 60.0 / job.processing_time_seconds))
            quality_factors.append(time_factor)
        
        # Error count factor
        error_factor = max(0.0, 1.0 - (len(job.error_messages) * 0.2))
        quality_factors.append(error_factor)
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get status of a specific job"""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        else:
            # Check queue
            for job in self.job_queue:
                if job.job_id == job_id:
                    return job
        return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            'active_jobs': len(self.active_jobs),
            'queued_jobs': len(self.job_queue),
            'completed_jobs': len(self.completed_jobs),
            'total_jobs': self.processing_stats['jobs_processed'] + self.processing_stats['jobs_failed']
        }


# Convenience functions for common workflows
async def create_conversation_processing_job(conversation_id: str, 
                                           priority: JobPriority = JobPriority.NORMAL,
                                           include_transformation: bool = True) -> ProcessingJob:
    """Create a job for processing a conversation from the archive"""
    
    job = ProcessingJob(
        source_type="conversation",
        source_id=str(conversation_id),
        priority=priority,
        processing_goals=[
            "Extract comprehensive narrative attributes",
            "Validate attribute quality",
            "Generate human-readable descriptions"
        ],
        attribute_categories=[
            "textual_rhythm", "linguistic_structure", "narrative_voice",
            "content_domain", "stylistic_signature", "discourse_patterns"
        ]
    )
    
    if include_transformation:
        job.transformation_targets = {
            "philosophical_projection": {
                "persona": "philosophical_narrator",
                "namespace": "existential_philosophy", 
                "style": "contemplative_prose"
            },
            "academic_summary": {
                "persona": "academic_researcher",
                "namespace": "scholarly_discourse",
                "style": "analytical_prose"
            }
        }
    
    return job


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = AttributeProcessingAgent()
        
        # Create a sample job
        job = await create_conversation_processing_job("203110", JobPriority.HIGH)
        
        # Submit job
        job_id = await agent.submit_job(job)
        print(f"Submitted job: {job_id}")
        
        # Start processing (in real usage, this would run in background)
        # await agent.start_processing()
    
    # Run example
    # asyncio.run(main())