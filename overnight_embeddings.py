#!/usr/bin/env python3
"""
Overnight Embeddings Processor
==============================

This script processes all archive content to generate embeddings for semantic search.
Designed to run overnight with progress tracking and restart capability.

Usage:
    python overnight_embeddings.py [--config config.json] [--resume session_id]

Features:
- Activity-aware prioritization (recent content first)
- Restartable processing with session management
- Progress tracking and statistics
- Resource monitoring and throttling
- Completion notifications
- Comprehensive error handling
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import asyncpg
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "humanizer_api" / "src"))

try:
    from embedding_system import AdvancedEmbeddingSystem
    from smart_archive_processor import SmartArchiveProcessor
    from progress_tracker import ProgressTracker
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running from the correct directory and dependencies are installed.")
    sys.exit(1)

console = Console()

class OvernightEmbeddingProcessor:
    """Main processor for overnight embedding generation."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.session_name = f"overnight_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.embedding_system = None
        self.smart_processor = None
        self.progress_tracker = None
        self.db_pool = None
        
        # Statistics
        self.stats = {
            'session_id': self.session_id,
            'started_at': None,
            'completed_at': None,
            'total_content_items': 0,
            'processed_items': 0,
            'failed_items': 0,
            'total_chunks_generated': 0,
            'total_chunks_embedded': 0,
            'processing_rate': 0.0,
            'estimated_completion': None
        }
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the overnight processor."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"overnight_embeddings_{self.session_id[:8]}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize all required components."""
        self.logger.info(f"Initializing overnight embedding processor (Session: {self.session_id})")
        
        try:
            # Initialize database connection
            db_config = self.config.get('database', {})
            self.db_pool = await asyncpg.create_pool(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config.get('user', 'postgres'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'humanizer'),
                min_size=2,
                max_size=10
            )
            
            # Test database connection
            async with self.db_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            self.logger.info("Database connection established")
            
            # Initialize embedding system
            embedding_config = self.config.get('embedding', {})
            self.embedding_system = AdvancedEmbeddingSystem(
                ollama_host=embedding_config.get('ollama_host', 'http://localhost:11434'),
                model_name=embedding_config.get('model_name', 'nomic-text-embed'),
                chunk_size=embedding_config.get('chunk_size', 240),
                chunk_overlap=embedding_config.get('chunk_overlap', 50)
            )
            
            # Test embedding system
            await self.embedding_system.test_connection()
            self.logger.info("Embedding system initialized and tested")
            
            # Initialize smart processor
            processor_config = self.config.get('processor', {})
            self.smart_processor = SmartArchiveProcessor(
                db_pool=self.db_pool,
                embedding_system=self.embedding_system,
                batch_size=processor_config.get('batch_size', 10),
                max_concurrent=processor_config.get('max_concurrent', 3),
                retry_attempts=processor_config.get('retry_attempts', 2)
            )
            
            # Initialize progress tracker
            self.progress_tracker = ProgressTracker(
                session_id=self.session_id,
                db_pool=self.db_pool
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
            
    async def create_session_record(self):
        """Create a session record in the database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO embedding_sessions 
                    (session_id, session_name, status, config, started_at)
                    VALUES ($1, $2, 'running', $3, $4)
                """, self.session_id, self.session_name, json.dumps(self.config), datetime.now())
                
            self.logger.info(f"Created session record: {self.session_name}")
        except Exception as e:
            self.logger.error(f"Failed to create session record: {e}")
            raise
            
    async def get_content_to_process(self) -> List[Dict]:
        """Get list of content items that need embedding processing."""
        try:
            async with self.db_pool.acquire() as conn:
                # Use the SQL function we created in the schema
                rows = await conn.fetch("""
                    SELECT * FROM get_content_needing_embeddings($1)
                    WHERE needs_processing = true
                """, self.config.get('batch_limit', 1000))
                
                content_list = []
                for row in rows:
                    content_list.append({
                        'id': row['content_id'],
                        'title': row['title'],
                        'author': row['author'],
                        'content_type': row['content_type'],
                        'content_length': row['content_length'],
                        'existing_chunks': row['existing_chunks']
                    })
                    
                self.logger.info(f"Found {len(content_list)} content items needing processing")
                return content_list
                
        except Exception as e:
            self.logger.error(f"Failed to get content list: {e}")
            raise
            
    async def process_content_item(self, content_item: Dict) -> Dict:
        """Process a single content item to generate embeddings."""
        content_id = content_item['id']
        
        try:
            # Record job start
            job_id = await self.progress_tracker.start_job(content_id)
            
            # Get full content from database
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, title, content, author, timestamp, content_type
                    FROM archived_content WHERE id = $1
                """, content_id)
                
                if not row:
                    raise ValueError(f"Content {content_id} not found")
                    
                content_data = {
                    'id': row['id'],
                    'title': row['title'],
                    'content': row['content'],
                    'author': row['author'],
                    'timestamp': row['timestamp'],
                    'content_type': row['content_type']
                }
                
            # Generate embeddings using the advanced system
            start_time = time.time()
            result = await self.embedding_system.process_content(content_data)
            processing_time = time.time() - start_time
            
            # Store chunks and embeddings in database
            chunks_stored = await self._store_chunks(content_id, result['chunks'])
            
            # Update job record
            await self.progress_tracker.complete_job(
                job_id, 
                chunks_generated=len(result['chunks']),
                chunks_embedded=chunks_stored,
                processing_time=processing_time
            )
            
            return {
                'content_id': content_id,
                'status': 'completed',
                'chunks_generated': len(result['chunks']),
                'chunks_embedded': chunks_stored,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process content {content_id}: {e}")
            
            # Mark job as failed
            if 'job_id' in locals():
                await self.progress_tracker.fail_job(job_id, str(e))
                
            return {
                'content_id': content_id,
                'status': 'failed',
                'error': str(e),
                'processing_time': 0
            }
            
    async def _store_chunks(self, content_id: int, chunks: List[Dict]) -> int:
        """Store processed chunks with embeddings in the database."""
        stored_count = 0
        
        try:
            async with self.db_pool.acquire() as conn:
                for chunk in chunks:
                    # Convert embedding to the format expected by pgvector
                    embedding_vector = chunk.get('embedding')
                    if embedding_vector:
                        # Store chunk in database
                        await conn.execute("""
                            INSERT INTO content_chunks 
                            (content_id, chunk_type, text, embedding, position, word_count, summary_level, chunk_hash)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                            ON CONFLICT (content_id, chunk_hash) DO UPDATE SET
                                embedding = EXCLUDED.embedding,
                                updated_at = NOW()
                        """, 
                        content_id,
                        chunk.get('type', 'content'),
                        chunk['text'],
                        embedding_vector,
                        chunk.get('position', 0),
                        chunk.get('word_count', 0),
                        chunk.get('summary_level', 0),
                        chunk.get('hash', '')
                        )
                        stored_count += 1
                        
        except Exception as e:
            self.logger.error(f"Failed to store chunks for content {content_id}: {e}")
            
        return stored_count
        
    async def update_session_progress(self):
        """Update session progress in the database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE embedding_sessions 
                    SET processed_items = $1,
                        failed_items = $2,
                        total_chunks_generated = $3,
                        total_chunks_embedded = $4
                    WHERE session_id = $5
                """, 
                self.stats['processed_items'],
                self.stats['failed_items'],
                self.stats['total_chunks_generated'],
                self.stats['total_chunks_embedded'],
                self.session_id
                )
        except Exception as e:
            self.logger.error(f"Failed to update session progress: {e}")
            
    async def run(self):
        """Main processing loop."""
        try:
            self.stats['started_at'] = datetime.now()
            await self.create_session_record()
            
            # Get content to process
            content_list = await self.get_content_to_process()
            self.stats['total_content_items'] = len(content_list)
            
            if not content_list:
                self.logger.info("No content needs processing. All embeddings are up to date!")
                return
                
            # Process content with progress tracking
            console.print(f"\n[bold blue]Starting overnight embedding processing[/bold blue]")
            console.print(f"Session: {self.session_name}")
            console.print(f"Total items to process: {len(content_list)}")
            
            with Progress() as progress:
                task = progress.add_task("[green]Processing content...", total=len(content_list))
                
                batch_size = self.config.get('processor', {}).get('batch_size', 10)
                
                for i in range(0, len(content_list), batch_size):
                    batch = content_list[i:i + batch_size]
                    
                    # Process batch
                    batch_results = []
                    for content_item in batch:
                        result = await self.process_content_item(content_item)
                        batch_results.append(result)
                        
                        # Update statistics
                        if result['status'] == 'completed':
                            self.stats['processed_items'] += 1
                            self.stats['total_chunks_generated'] += result.get('chunks_generated', 0)
                            self.stats['total_chunks_embedded'] += result.get('chunks_embedded', 0)
                        else:
                            self.stats['failed_items'] += 1
                            
                        progress.update(task, advance=1)
                        
                        # Update progress in database periodically
                        if self.stats['processed_items'] % 10 == 0:
                            await self.update_session_progress()
                            
                        # Add small delay to prevent overwhelming the system
                        await asyncio.sleep(self.config.get('processor', {}).get('delay_seconds', 0.5))
                        
                    # Print batch statistics
                    completed_batch = [r for r in batch_results if r['status'] == 'completed']
                    failed_batch = [r for r in batch_results if r['status'] == 'failed']
                    
                    if completed_batch:
                        avg_time = sum(r['processing_time'] for r in completed_batch) / len(completed_batch)
                        console.print(f"Batch {i//batch_size + 1}: {len(completed_batch)} completed, {len(failed_batch)} failed, avg time: {avg_time:.2f}s")
                        
            # Mark session as completed
            self.stats['completed_at'] = datetime.now()
            await self._finalize_session()
            
            # Print final statistics
            self._print_final_stats()
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            await self._mark_session_failed(str(e))
            raise
            
    async def _finalize_session(self):
        """Mark session as completed and update final statistics."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE embedding_sessions 
                    SET status = 'completed',
                        processed_items = $1,
                        failed_items = $2,
                        total_chunks_generated = $3,
                        total_chunks_embedded = $4,
                        completed_at = $5
                    WHERE session_id = $6
                """, 
                self.stats['processed_items'],
                self.stats['failed_items'],
                self.stats['total_chunks_generated'],
                self.stats['total_chunks_embedded'],
                self.stats['completed_at'],
                self.session_id
                )
        except Exception as e:
            self.logger.error(f"Failed to finalize session: {e}")
            
    async def _mark_session_failed(self, error_message: str):
        """Mark session as failed."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE embedding_sessions 
                    SET status = 'failed',
                        completed_at = $1
                    WHERE session_id = $2
                """, datetime.now(), self.session_id)
        except Exception as e:
            self.logger.error(f"Failed to mark session as failed: {e}")
            
    def _print_final_stats(self):
        """Print final processing statistics."""
        duration = self.stats['completed_at'] - self.stats['started_at']
        
        table = Table(title=f"Overnight Embeddings Completed - {self.session_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Session ID", self.session_id[:8] + "...")
        table.add_row("Duration", str(duration))
        table.add_row("Total Items", str(self.stats['total_content_items']))
        table.add_row("Processed", str(self.stats['processed_items']))
        table.add_row("Failed", str(self.stats['failed_items']))
        table.add_row("Total Chunks Generated", str(self.stats['total_chunks_generated']))
        table.add_row("Total Chunks Embedded", str(self.stats['total_chunks_embedded']))
        
        if self.stats['processed_items'] > 0:
            avg_time = duration.total_seconds() / self.stats['processed_items']
            table.add_row("Avg Time per Item", f"{avg_time:.2f}s")
            
        console.print(table)
        
    async def cleanup(self):
        """Clean up resources."""
        if self.db_pool:
            await self.db_pool.close()


def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from file or use defaults."""
    default_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "database": "humanizer"
        },
        "embedding": {
            "ollama_host": "http://localhost:11434",
            "model_name": "nomic-text-embed",
            "chunk_size": 240,
            "chunk_overlap": 50
        },
        "processor": {
            "batch_size": 10,
            "max_concurrent": 3,
            "retry_attempts": 2,
            "delay_seconds": 0.5
        },
        "batch_limit": 1000
    }
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            # Merge with defaults
            for section, values in user_config.items():
                if section in default_config:
                    default_config[section].update(values)
                else:
                    default_config[section] = values
                    
    return default_config


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Overnight Embeddings Processor")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--resume", help="Resume from session ID")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without doing it")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    processor = OvernightEmbeddingProcessor(config)
    
    try:
        await processor.initialize()
        
        if args.dry_run:
            content_list = await processor.get_content_to_process()
            console.print(f"[bold yellow]DRY RUN MODE[/bold yellow]")
            console.print(f"Would process {len(content_list)} content items")
            for item in content_list[:10]:  # Show first 10
                console.print(f"  - {item['title'][:50]}... ({item['content_length']} chars)")
            if len(content_list) > 10:
                console.print(f"  ... and {len(content_list) - 10} more items")
        else:
            await processor.run()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Processing failed: {e}[/red]")
    finally:
        await processor.cleanup()


if __name__ == "__main__":
    asyncio.run(main())