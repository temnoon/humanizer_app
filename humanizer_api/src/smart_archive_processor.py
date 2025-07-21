#!/usr/bin/env python3
"""
Smart Archive Processor: Restartable Batch Import with Activity-Aware Embedding
Combines archive import with intelligent embedding generation and activity-based prioritization
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

from archive_unified_schema import UnifiedArchiveDB, ArchiveContent, SourceType, ContentType
from node_archive_importer import NodeArchiveImporter
from embedding_system import AdvancedEmbeddingSystem
from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingJob:
    """Represents a processing job with checkpoints"""
    job_id: str
    job_type: str  # "import", "embed", "analyze"
    content_id: int
    source_path: str
    status: str  # "pending", "processing", "completed", "failed", "skipped"
    priority: int  # 1-10, higher = more important
    activity_score: float  # Based on recency and engagement
    attempts: int = 0
    error_message: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None
    estimated_chunks: int = 0
    actual_chunks: int = 0

@dataclass
class ActivityMetrics:
    """Activity-based metrics for prioritization"""
    last_access: Optional[datetime] = None
    message_count: int = 0
    conversation_length: int = 0  # in words
    participants: int = 0
    engagement_score: float = 0.0  # Complex engagement calculation
    recency_weight: float = 1.0
    semantic_richness: float = 0.0  # Based on vocabulary diversity

class SmartArchiveProcessor:
    """
    Intelligent archive processor with activity-aware prioritization
    
    Features:
    - Restartable batch processing with checkpoints
    - Activity-based prioritization (today > this week > this month > older)
    - Parallel import and embedding generation
    - Smart chunk estimation and progress tracking
    - Failure recovery and retry logic
    - Multi-dimensional accessibility (semantic + temporal + engagement)
    """
    
    def __init__(self, database_url: str, node_archive_path: str):
        self.database_url = database_url
        self.node_archive_path = Path(node_archive_path)
        
        # Components
        self.archive_db = None
        self.embedding_system = None
        self.node_importer = None
        
        # Processing state
        self.job_queue: List[ProcessingJob] = []
        self.completed_jobs: Set[str] = set()
        self.failed_jobs: Dict[str, str] = {}
        self.checkpoint_file = Path("archive_processing_checkpoint.json")
        
        # Activity analysis
        self.activity_metrics: Dict[str, ActivityMetrics] = {}
        
        # Configuration
        self.batch_size = 10  # Process N conversations at once
        self.embedding_batch_size = 5  # Embed N conversations simultaneously
        self.max_retries = 3
        self.checkpoint_interval = 50  # Save checkpoint every N jobs
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🚀 Initializing Smart Archive Processor...")
        
        # Initialize database
        self.archive_db = UnifiedArchiveDB(self.database_url)
        await self.archive_db.create_tables()
        
        # Initialize embedding system
        self.embedding_system = AdvancedEmbeddingSystem(self.database_url)
        await self.embedding_system.initialize()
        
        # Initialize node importer
        self.node_importer = NodeArchiveImporter(self.archive_db, str(self.node_archive_path))
        
        logger.info("✅ Smart Archive Processor initialized")
    
    async def analyze_archive_activity(self) -> Dict[str, Any]:
        """
        Analyze archive for activity patterns and prioritization
        
        Returns comprehensive activity analysis for intelligent processing
        """
        logger.info("🔍 Analyzing archive activity patterns...")
        
        conversations = list(self.node_archive_path.glob("*/conversation.json"))
        logger.info(f"Found {len(conversations)} conversations to analyze")
        
        activity_analysis = {
            "total_conversations": len(conversations),
            "activity_distribution": {"today": 0, "this_week": 0, "this_month": 0, "older": 0},
            "engagement_levels": {"high": [], "medium": [], "low": []},
            "processing_estimate": {"total_chunks": 0, "total_time_minutes": 0},
            "priority_queue": []
        }
        
        now = datetime.now(timezone.utc)
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        for conv_file in conversations:
            try:
                # Parse conversation
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv_data = json.load(f)
                
                # Extract activity metrics
                metrics = self._extract_activity_metrics(conv_data, conv_file)
                conv_id = conv_file.parent.name
                self.activity_metrics[conv_id] = metrics
                
                # Categorize by recency
                if metrics.last_access and metrics.last_access.date() == today:
                    activity_analysis["activity_distribution"]["today"] += 1
                    priority = 10
                elif metrics.last_access and metrics.last_access >= week_ago:
                    activity_analysis["activity_distribution"]["this_week"] += 1
                    priority = 8
                elif metrics.last_access and metrics.last_access >= month_ago:
                    activity_analysis["activity_distribution"]["this_month"] += 1
                    priority = 6
                else:
                    activity_analysis["activity_distribution"]["older"] += 1
                    priority = 4
                
                # Adjust priority by engagement
                engagement_boost = min(2, metrics.engagement_score * 2)
                final_priority = min(10, priority + engagement_boost)
                
                # Estimate processing requirements
                estimated_chunks = max(1, metrics.conversation_length // 240)  # 240-word chunks
                activity_analysis["processing_estimate"]["total_chunks"] += estimated_chunks
                
                # Create processing job
                job = ProcessingJob(
                    job_id=f"import_{conv_id}",
                    job_type="import_and_embed",
                    content_id=0,  # Will be set after import
                    source_path=str(conv_file),
                    status="pending",
                    priority=int(final_priority),
                    activity_score=metrics.engagement_score * metrics.recency_weight,
                    estimated_chunks=estimated_chunks,
                    created_at=now
                )
                
                activity_analysis["priority_queue"].append({
                    "conversation_id": conv_id,
                    "priority": final_priority,
                    "activity_score": metrics.engagement_score * metrics.recency_weight,
                    "estimated_chunks": estimated_chunks,
                    "last_access": metrics.last_access.isoformat() if metrics.last_access else None,
                    "engagement_level": "high" if metrics.engagement_score > 0.7 else "medium" if metrics.engagement_score > 0.3 else "low"
                })
                
                self.job_queue.append(job)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {conv_file}: {e}")
        
        # Sort by priority and activity score
        self.job_queue.sort(key=lambda j: (j.priority, j.activity_score), reverse=True)
        activity_analysis["priority_queue"].sort(key=lambda x: (x["priority"], x["activity_score"]), reverse=True)
        
        # Estimate total processing time
        total_embedding_time = activity_analysis["processing_estimate"]["total_chunks"] * 2  # 2 seconds per chunk
        activity_analysis["processing_estimate"]["total_time_minutes"] = total_embedding_time / 60
        
        logger.info(f"📊 Activity Analysis Complete:")
        logger.info(f"   • Today: {activity_analysis['activity_distribution']['today']} conversations")
        logger.info(f"   • This week: {activity_analysis['activity_distribution']['this_week']} conversations")
        logger.info(f"   • This month: {activity_analysis['activity_distribution']['this_month']} conversations")
        logger.info(f"   • Older: {activity_analysis['activity_distribution']['older']} conversations")
        logger.info(f"   • Estimated {activity_analysis['processing_estimate']['total_chunks']} chunks")
        logger.info(f"   • Estimated {activity_analysis['processing_estimate']['total_time_minutes']:.1f} minutes processing time")
        
        return activity_analysis
    
    def _extract_activity_metrics(self, conv_data: Dict[str, Any], conv_file: Path) -> ActivityMetrics:
        """Extract detailed activity metrics from conversation data"""
        
        # Extract basic metrics
        create_time = conv_data.get("create_time", 0)
        update_time = conv_data.get("update_time", 0)
        mapping = conv_data.get("mapping", {})
        
        # Calculate metrics
        message_count = len([msg for msg in mapping.values() if msg.get("message")])
        
        # Count unique participants
        participants = set()
        total_words = 0
        vocab_set = set()
        
        for msg_data in mapping.values():
            message = msg_data.get("message")
            if message:
                author = message.get("author", {}).get("role", "unknown")
                participants.add(author)
                
                # Extract text content
                content = message.get("content", {})
                if content.get("content_type") == "text":
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            words = part.split()
                            total_words += len(words)
                            vocab_set.update(word.lower() for word in words if word.isalpha())
        
        # Calculate engagement score (complex heuristic)
        engagement_score = 0.0
        if message_count > 0:
            # Base engagement from interaction volume
            engagement_score += min(1.0, message_count / 20)  # Normalize to 20 messages
            
            # Vocabulary richness
            if total_words > 0:
                vocab_richness = len(vocab_set) / total_words
                engagement_score += min(0.5, vocab_richness * 10)
            
            # Multi-participant bonus
            if len(participants) > 1:
                engagement_score += 0.3
        
        # Recency weight
        last_access = datetime.fromtimestamp(max(create_time, update_time), timezone.utc) if max(create_time, update_time) > 0 else None
        recency_weight = 1.0
        if last_access:
            days_ago = (datetime.now(timezone.utc) - last_access).days
            recency_weight = max(0.1, 1.0 / (1 + days_ago / 30))  # Decay over 30 days
        
        return ActivityMetrics(
            last_access=last_access,
            message_count=message_count,
            conversation_length=total_words,
            participants=len(participants),
            engagement_score=min(1.0, engagement_score),
            recency_weight=recency_weight,
            semantic_richness=len(vocab_set) / max(1, total_words)
        )
    
    async def process_archive_smart(self, max_conversations: Optional[int] = None) -> Dict[str, Any]:
        """
        Smart processing of archive with activity-aware prioritization
        
        Args:
            max_conversations: Limit processing for testing
            
        Returns:
            Comprehensive processing results
        """
        logger.info("🎯 Starting Smart Archive Processing...")
        
        # Load previous checkpoint if exists
        self.load_checkpoint()
        
        # Analyze activity if not already done
        if not self.job_queue:
            await self.analyze_archive_activity()
        
        # Limit for testing
        if max_conversations:
            self.job_queue = self.job_queue[:max_conversations]
            logger.info(f"Limited to {max_conversations} conversations for processing")
        
        start_time = time.time()
        results = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "total_jobs": len(self.job_queue),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "total_chunks_created": 0,
            "total_embeddings_generated": 0,
            "activity_breakdown": {"today": 0, "this_week": 0, "this_month": 0, "older": 0},
            "processing_phases": []
        }
        
        # Process in smart batches
        try:
            for i in range(0, len(self.job_queue), self.batch_size):
                batch = self.job_queue[i:i + self.batch_size]
                logger.info(f"📦 Processing batch {i//self.batch_size + 1}: {len(batch)} jobs")
                
                # Process batch
                batch_results = await self._process_batch(batch)
                
                # Update results
                results["completed"] += batch_results["completed"]
                results["failed"] += batch_results["failed"]
                results["skipped"] += batch_results["skipped"]
                results["total_chunks_created"] += batch_results["chunks_created"]
                results["total_embeddings_generated"] += batch_results["embeddings_generated"]
                
                # Update activity breakdown
                for job in batch:
                    if job.status == "completed":
                        conv_id = Path(job.source_path).parent.name
                        metrics = self.activity_metrics.get(conv_id)
                        if metrics and metrics.last_access:
                            days_ago = (datetime.now(timezone.utc) - metrics.last_access).days
                            if days_ago == 0:
                                results["activity_breakdown"]["today"] += 1
                            elif days_ago <= 7:
                                results["activity_breakdown"]["this_week"] += 1
                            elif days_ago <= 30:
                                results["activity_breakdown"]["this_month"] += 1
                            else:
                                results["activity_breakdown"]["older"] += 1
                
                # Save checkpoint
                if (i + self.batch_size) % self.checkpoint_interval == 0:
                    self.save_checkpoint()
                
                logger.info(f"✅ Batch complete: {batch_results['completed']} successful, {batch_results['failed']} failed")
        
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.save_checkpoint()
            raise
        
        # Final results
        end_time = time.time()
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        results["total_time_seconds"] = end_time - start_time
        results["average_time_per_conversation"] = results["total_time_seconds"] / max(1, results["completed"])
        
        # Clean up checkpoint
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        
        logger.info(f"🎉 Smart Archive Processing Complete!")
        logger.info(f"   • Processed: {results['completed']}/{results['total_jobs']} conversations")
        logger.info(f"   • Chunks created: {results['total_chunks_created']}")
        logger.info(f"   • Embeddings: {results['total_embeddings_generated']}")
        logger.info(f"   • Total time: {results['total_time_seconds']:.1f} seconds")
        logger.info(f"   • Activity breakdown: {results['activity_breakdown']}")
        
        return results
    
    async def _process_batch(self, batch: List[ProcessingJob]) -> Dict[str, int]:
        """Process a batch of jobs concurrently"""
        
        results = {"completed": 0, "failed": 0, "skipped": 0, "chunks_created": 0, "embeddings_generated": 0}
        
        # Process jobs concurrently (but limit concurrent embeddings)
        semaphore = asyncio.Semaphore(self.embedding_batch_size)
        
        async def process_single_job(job: ProcessingJob):
            async with semaphore:
                return await self._process_single_job(job)
        
        # Execute batch
        job_results = await asyncio.gather(
            *[process_single_job(job) for job in batch],
            return_exceptions=True
        )
        
        # Aggregate results
        for job, result in zip(batch, job_results):
            if isinstance(result, Exception):
                logger.error(f"Job {job.job_id} failed with exception: {result}")
                job.status = "failed"
                job.error_message = str(result)
                results["failed"] += 1
            elif result:
                results["completed"] += 1
                results["chunks_created"] += result.get("chunks_created", 0)
                results["embeddings_generated"] += result.get("embeddings_generated", 0)
            else:
                results["skipped"] += 1
        
        return results
    
    async def _process_single_job(self, job: ProcessingJob) -> Optional[Dict[str, Any]]:
        """Process a single import+embedding job"""
        
        try:
            logger.info(f"🔄 Processing {job.job_id} (priority: {job.priority}, activity: {job.activity_score:.2f})")
            job.status = "processing"
            job.attempts += 1
            job.updated_at = datetime.now(timezone.utc)
            
            # Step 1: Import conversation
            conv_file = Path(job.source_path)
            import_result = await self.node_importer.import_single_conversation(conv_file)
            
            if not import_result:
                logger.warning(f"Import failed for {job.job_id}")
                job.status = "failed"
                job.error_message = "Import returned no result"
                return None
            
            # Step 2: Generate embeddings for imported content
            content_id = import_result.get("content_id")
            if content_id:
                embedding_result = await self._generate_embeddings_for_content(content_id)
                
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)
                job.actual_chunks = embedding_result.get("total_chunks", 0)
                
                return {
                    "chunks_created": embedding_result.get("total_chunks", 0),
                    "embeddings_generated": embedding_result.get("embeddings_generated", 0),
                    "content_id": content_id
                }
            else:
                job.status = "failed"
                job.error_message = "No content_id from import"
                return None
                
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            
            # Retry logic
            if job.attempts < self.max_retries:
                job.status = "pending"  # Will retry
                logger.info(f"Will retry {job.job_id} (attempt {job.attempts}/{self.max_retries})")
            
            return None
    
    async def _generate_embeddings_for_content(self, content_id: int) -> Dict[str, Any]:
        """Generate embeddings for specific content"""
        
        # Get content text from database
        content = await self.archive_db.get_content_by_id(content_id)
        if not content or not content.body_text:
            return {"total_chunks": 0, "embeddings_generated": 0}
        
        # Process through embedding system
        result = await self.embedding_system.process_content(content_id, content.body_text)
        
        # Store chunks and embeddings in database (implementation needed)
        # This would store the chunk data with embeddings in a separate chunks table
        
        return {
            "total_chunks": result.get("total_chunks", 0),
            "embeddings_generated": len([c for c in result.get("chunks", []) if c.get("embedding")])
        }
    
    def save_checkpoint(self):
        """Save processing checkpoint for resumability"""
        checkpoint_data = {
            "completed_jobs": list(self.completed_jobs),
            "failed_jobs": self.failed_jobs,
            "job_queue": [asdict(job) for job in self.job_queue],
            "activity_metrics": {k: asdict(v) for k, v in self.activity_metrics.items()},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
        
        logger.info(f"💾 Checkpoint saved with {len(self.job_queue)} jobs")
    
    def load_checkpoint(self):
        """Load previous checkpoint to resume processing"""
        if not self.checkpoint_file.exists():
            return
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.completed_jobs = set(checkpoint_data.get("completed_jobs", []))
            self.failed_jobs = checkpoint_data.get("failed_jobs", {})
            
            # Reconstruct job queue
            job_data = checkpoint_data.get("job_queue", [])
            self.job_queue = []
            for job_dict in job_data:
                # Convert datetime strings back to datetime objects
                if job_dict.get("created_at"):
                    job_dict["created_at"] = datetime.fromisoformat(job_dict["created_at"])
                if job_dict.get("updated_at"):
                    job_dict["updated_at"] = datetime.fromisoformat(job_dict["updated_at"])
                if job_dict.get("completed_at"):
                    job_dict["completed_at"] = datetime.fromisoformat(job_dict["completed_at"])
                
                job = ProcessingJob(**job_dict)
                # Only add pending and failed jobs (not completed)
                if job.status in ["pending", "failed"]:
                    self.job_queue.append(job)
            
            # Reconstruct activity metrics
            activity_data = checkpoint_data.get("activity_metrics", {})
            self.activity_metrics = {}
            for conv_id, metrics_dict in activity_data.items():
                if metrics_dict.get("last_access"):
                    metrics_dict["last_access"] = datetime.fromisoformat(metrics_dict["last_access"])
                self.activity_metrics[conv_id] = ActivityMetrics(**metrics_dict)
            
            logger.info(f"📥 Checkpoint loaded: {len(self.job_queue)} jobs to process")
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            self.checkpoint_file.unlink()  # Remove corrupted checkpoint

# CLI Interface
async def main():
    """CLI interface for smart archive processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Archive Processor with Activity-Aware Prioritization")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL with pgvector")
    parser.add_argument("--node-archive-path", required=True, help="Path to Node Archive Browser data")
    parser.add_argument("--max-conversations", type=int, help="Limit conversations for testing")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze activity, don't process")
    parser.add_argument("--resume", action="store_true", help="Resume from previous checkpoint")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = SmartArchiveProcessor(args.database_url, args.node_archive_path)
    await processor.initialize()
    
    if args.analyze_only:
        # Just analyze activity patterns
        analysis = await processor.analyze_archive_activity()
        print("\n📊 Activity Analysis Results:")
        print(json.dumps(analysis, indent=2, default=str))
    else:
        # Full processing
        results = await processor.process_archive_smart(args.max_conversations)
        print("\n🎉 Processing Results:")
        print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())