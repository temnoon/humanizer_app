#!/usr/bin/env python3
"""
Integrated Processing CLI
========================

Complete command-line interface for content processing pipeline:
Archive → Attribute Extraction → Validation → Allegory Transformation

Combines archive access, intelligent attribute taxonomy, agent-controlled 
processing, and allegory engine integration.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import our components
from archive_cli import ArchiveCLI
from attribute_taxonomy import AttributeCollection, transform_technical_attributes
from attribute_processing_agent import (
    AttributeProcessingAgent, ProcessingJob, JobPriority, JobStatus,
    create_conversation_processing_job
)
from humanizer_cli import HumanizerCLI

class IntegratedProcessingCLI:
    """Unified CLI for complete content processing workflows"""
    
    def __init__(self):
        self.archive_cli = ArchiveCLI()
        self.humanizer_cli = HumanizerCLI()
        self.processing_agent = None
        self.output_dir = Path("./processed_content")
        self.output_dir.mkdir(exist_ok=True)
        
    async def initialize_agent(self):
        """Initialize the processing agent with our clients"""
        if not self.processing_agent:
            self.processing_agent = AttributeProcessingAgent(
                archive_client=self.archive_cli,
                attribute_extractor=None,  # Will use built-in fallback
                allegory_client=self.humanizer_cli,
                max_concurrent_jobs=3
            )
            
            # Start the agent in background
            asyncio.create_task(self.processing_agent.start_processing())
            print("🤖 Processing agent initialized and started")
    
    async def discover_content(self, 
                             search_query: Optional[str] = None,
                             limit: int = 20,
                             quality_filter: bool = True) -> List[Dict[str, Any]]:
        """Discover content from archive with quality filtering"""
        
        print(f"🔍 Discovering content in archive...")
        
        if search_query:
            print(f"   Search query: '{search_query}'")
            conversations = self.archive_cli.search_content(search_query, limit)
        else:
            conversations = self.archive_cli.list_conversations(page=1, limit=limit)
        
        if quality_filter:
            # Filter for conversations with reasonable message counts
            filtered = []
            for conv in conversations:
                msg_count = conv.get('message_count', 0)
                word_count = conv.get('word_count', 0)
                
                # Quality criteria: 3-50 messages, 100+ words
                if 3 <= msg_count <= 50 and word_count >= 100:
                    filtered.append(conv)
            
            print(f"   Found {len(conversations)} conversations, {len(filtered)} meet quality criteria")
            conversations = filtered
        
        # Sort by word count descending (richer content first)
        conversations.sort(key=lambda x: x.get('word_count', 0), reverse=True)
        
        return conversations[:limit]
    
    async def process_conversation_comprehensive(self,
                                              conversation_id: str,
                                              priority: JobPriority = JobPriority.NORMAL,
                                              include_transformations: bool = True,
                                              output_prefix: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive processing of a single conversation"""
        
        await self.initialize_agent()
        
        print(f"🔄 Starting comprehensive processing of conversation {conversation_id}")
        
        # Create processing job
        job = await create_conversation_processing_job(
            conversation_id, 
            priority=priority,
            include_transformation=include_transformations
        )
        
        # Submit to agent
        job_id = await self.processing_agent.submit_job(job)
        print(f"   📋 Job {job_id} submitted with priority {priority}")
        
        # Monitor progress
        await self._monitor_job_progress(job_id)
        
        # Get final results
        completed_job = self.processing_agent.get_job_status(job_id)
        if completed_job.status != JobStatus.COMPLETED:
            print(f"❌ Job failed with status: {completed_job.status}")
            if completed_job.error_messages:
                print("   Errors:")
                for error in completed_job.error_messages:
                    print(f"     - {error}")
            return {}
        
        print(f"✅ Processing completed in {completed_job.processing_time_seconds:.1f}s")
        
        # Save comprehensive results
        results = {
            "job_metadata": {
                "job_id": job_id,
                "conversation_id": conversation_id,
                "processing_time": completed_job.processing_time_seconds,
                "completed_at": completed_job.completed_at.isoformat() if completed_job.completed_at else None,
                "quality_score": completed_job.validation_result.confidence_score if completed_job.validation_result else 0.0
            },
            "extracted_attributes": completed_job.extracted_attributes.dict() if completed_job.extracted_attributes else {},
            "validation_results": completed_job.validation_result.dict() if completed_job.validation_result else {},
            "transformations": completed_job.transformation_outputs
        }
        
        # Save to file
        output_prefix = output_prefix or f"conv_{conversation_id}"
        output_file = self.output_dir / f"{output_prefix}_comprehensive.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        
        return results
    
    async def batch_process_conversations(self,
                                        conversation_ids: List[str],
                                        priority: JobPriority = JobPriority.BATCH,
                                        max_concurrent: int = 3) -> Dict[str, Any]:
        """Process multiple conversations in batch mode"""
        
        await self.initialize_agent()
        
        print(f"🔄 Starting batch processing of {len(conversation_ids)} conversations")
        
        # Submit all jobs
        job_ids = []
        for conv_id in conversation_ids:
            job = await create_conversation_processing_job(conv_id, priority=priority)
            job_id = await self.processing_agent.submit_job(job)
            job_ids.append(job_id)
        
        print(f"   📋 Submitted {len(job_ids)} jobs")
        
        # Monitor all jobs
        completed_jobs = []
        failed_jobs = []
        
        while len(completed_jobs) + len(failed_jobs) < len(job_ids):
            await asyncio.sleep(2)
            
            for job_id in job_ids:
                if job_id in [j.job_id for j in completed_jobs + failed_jobs]:
                    continue
                
                job = self.processing_agent.get_job_status(job_id)
                if job.status == JobStatus.COMPLETED:
                    completed_jobs.append(job)
                    print(f"   ✅ Job {job_id} completed ({len(completed_jobs)}/{len(job_ids)})")
                elif job.status == JobStatus.FAILED:
                    failed_jobs.append(job)
                    print(f"   ❌ Job {job_id} failed ({len(failed_jobs)} failures total)")
        
        # Compile batch results
        batch_results = {
            "batch_metadata": {
                "total_jobs": len(job_ids),
                "completed": len(completed_jobs),
                "failed": len(failed_jobs),
                "completion_rate": len(completed_jobs) / len(job_ids),
                "processed_at": datetime.now().isoformat()
            },
            "job_results": {}
        }
        
        # Save individual results and compile summaries
        total_attributes = 0
        avg_quality = 0.0
        
        for job in completed_jobs:
            conv_id = job.source_id
            
            job_result = {
                "status": "completed",
                "processing_time": job.processing_time_seconds,
                "attributes_extracted": job.extracted_attributes.total_attributes if job.extracted_attributes else 0,
                "quality_score": job.validation_result.confidence_score if job.validation_result else 0.0,
                "transformations": list(job.transformation_outputs.keys())
            }
            
            total_attributes += job_result["attributes_extracted"]
            avg_quality += job_result["quality_score"]
            
            batch_results["job_results"][conv_id] = job_result
            
            # Save individual comprehensive result
            individual_output = self.output_dir / f"conv_{conv_id}_batch_result.json"
            with open(individual_output, 'w') as f:
                json.dump({
                    "conversation_id": conv_id,
                    "extracted_attributes": job.extracted_attributes.dict() if job.extracted_attributes else {},
                    "validation_results": job.validation_result.dict() if job.validation_result else {},
                    "transformations": job.transformation_outputs
                }, f, indent=2, default=str)
        
        # Add failed job results
        for job in failed_jobs:
            batch_results["job_results"][job.source_id] = {
                "status": "failed",
                "error_messages": job.error_messages,
                "retry_count": job.retry_count
            }
        
        # Add summary statistics
        if completed_jobs:
            batch_results["batch_metadata"]["total_attributes_extracted"] = total_attributes
            batch_results["batch_metadata"]["average_quality_score"] = avg_quality / len(completed_jobs)
        
        # Save batch summary
        batch_output = self.output_dir / f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_output, 'w') as f:
            json.dump(batch_results, f, indent=2, default=str)
        
        print(f"📊 Batch processing completed: {len(completed_jobs)} successful, {len(failed_jobs)} failed")
        print(f"💾 Batch summary saved to: {batch_output}")
        
        return batch_results
    
    async def discover_and_process_workflow(self,
                                          search_query: str,
                                          max_conversations: int = 10,
                                          auto_process: bool = False) -> Dict[str, Any]:
        """Complete workflow: discover → review → process"""
        
        print(f"🚀 Starting discover-and-process workflow")
        print(f"   Query: '{search_query}'")
        print(f"   Max conversations: {max_conversations}")
        
        # Step 1: Discover content
        discovered = await self.discover_content(search_query, max_conversations * 2, quality_filter=True)
        discovered = discovered[:max_conversations]
        
        if not discovered:
            print("❌ No suitable content found")
            return {}
        
        print(f"\n📋 Discovered Conversations:")
        for i, conv in enumerate(discovered, 1):
            title = conv.get('title', 'Untitled')[:50]
            msg_count = conv.get('message_count', 0)
            word_count = conv.get('word_count', 0)
            print(f"   {i}. ID:{conv['id']} | {title}... | {msg_count} msgs, {word_count} words")
        
        # Step 2: User review (unless auto_process)
        if not auto_process:
            print("\n🤔 Review conversations above. Process all? (y/n/select): ", end="")
            choice = input().lower().strip()
            
            if choice == 'n':
                print("Processing cancelled")
                return {}
            elif choice == 'select':
                print("Enter conversation numbers to process (comma-separated): ", end="")
                selected = input().strip()
                try:
                    indices = [int(x.strip()) - 1 for x in selected.split(',')]
                    discovered = [discovered[i] for i in indices if 0 <= i < len(discovered)]
                except (ValueError, IndexError):
                    print("❌ Invalid selection, processing all")
        
        # Step 3: Process selected conversations
        conversation_ids = [str(conv['id']) for conv in discovered]
        
        if len(conversation_ids) == 1:
            print(f"\n🔄 Processing single conversation comprehensively...")
            results = await self.process_conversation_comprehensive(conversation_ids[0])
        else:
            print(f"\n🔄 Processing {len(conversation_ids)} conversations in batch...")
            results = await self.batch_process_conversations(conversation_ids)
        
        return results
    
    async def _monitor_job_progress(self, job_id: str):
        """Monitor and display job progress"""
        last_progress = 0.0
        
        while True:
            job = self.processing_agent.get_job_status(job_id)
            if not job:
                break
            
            if job.progress_percentage != last_progress:
                print(f"   📊 {job.current_step}: {job.progress_percentage:.1f}%")
                last_progress = job.progress_percentage
            
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                break
            
            await asyncio.sleep(1)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if self.processing_agent:
            return self.processing_agent.get_processing_stats()
        return {"message": "Agent not initialized"}


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Integrated Content Processing Pipeline")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover content from archive')
    discover_parser.add_argument('--search', help='Search query')
    discover_parser.add_argument('--limit', type=int, default=20, help='Max results')
    discover_parser.add_argument('--no-quality-filter', action='store_true', help='Disable quality filtering')
    
    # Process single conversation
    process_parser = subparsers.add_parser('process', help='Process single conversation')
    process_parser.add_argument('conversation_id', help='Conversation ID to process')
    process_parser.add_argument('--priority', choices=['urgent', 'high', 'normal', 'low', 'batch'], 
                               default='normal', help='Processing priority')
    process_parser.add_argument('--no-transform', action='store_true', help='Skip allegory transformations')
    process_parser.add_argument('--output-prefix', help='Custom output file prefix')
    
    # Batch processing
    batch_parser = subparsers.add_parser('batch', help='Batch process multiple conversations')
    batch_parser.add_argument('conversation_ids', nargs='+', help='Conversation IDs to process')
    batch_parser.add_argument('--priority', choices=['urgent', 'high', 'normal', 'low', 'batch'], 
                             default='batch', help='Processing priority')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Complete discover-and-process workflow')
    workflow_parser.add_argument('search_query', help='Topic or keywords to search for')
    workflow_parser.add_argument('--max-conversations', type=int, default=10, help='Max conversations to discover')
    workflow_parser.add_argument('--auto-process', action='store_true', help='Process all discovered without confirmation')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show processing statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = IntegratedProcessingCLI()
    
    try:
        if args.command == 'discover':
            quality_filter = not args.no_quality_filter
            conversations = await cli.discover_content(args.search, args.limit, quality_filter)
            
            print(f"\n📋 Discovered {len(conversations)} conversations:")
            for i, conv in enumerate(conversations, 1):
                title = conv.get('title', 'Untitled')[:60]
                msg_count = conv.get('message_count', 0)
                word_count = conv.get('word_count', 0)
                author = conv.get('author', 'Unknown')
                timestamp = conv.get('timestamp', '')[:19] if conv.get('timestamp') else 'Unknown'
                
                print(f"{i:2d}. ID: {conv['id']}")
                print(f"    Title: {title}...")
                print(f"    Stats: {msg_count} messages, {word_count} words")
                print(f"    Author: {author} | Date: {timestamp}")
                print()
        
        elif args.command == 'process':
            priority = JobPriority(args.priority)
            include_transform = not args.no_transform
            
            result = await cli.process_conversation_comprehensive(
                args.conversation_id,
                priority=priority,
                include_transformations=include_transform,
                output_prefix=args.output_prefix
            )
            
            if result:
                print(f"\n📊 Processing Summary:")
                print(f"   Quality Score: {result['job_metadata']['quality_score']:.2f}")
                print(f"   Attributes Extracted: {len(result.get('extracted_attributes', {}).get('textual_rhythm', []))}")
                if result.get('transformations'):
                    print(f"   Transformations: {list(result['transformations'].keys())}")
        
        elif args.command == 'batch':
            priority = JobPriority(args.priority)
            result = await cli.batch_process_conversations(args.conversation_ids, priority)
            
            print(f"\n📊 Batch Processing Summary:")
            print(f"   Completion Rate: {result['batch_metadata']['completion_rate']:.1%}")
            print(f"   Total Attributes: {result['batch_metadata'].get('total_attributes_extracted', 0)}")
            print(f"   Average Quality: {result['batch_metadata'].get('average_quality_score', 0):.2f}")
            
        elif args.command == 'workflow':
            result = await cli.discover_and_process_workflow(
                args.search_query,
                args.max_conversations,
                args.auto_process
            )
            
            if result:
                print(f"\n🎉 Workflow completed successfully!")
                
        elif args.command == 'stats':
            stats = cli.get_processing_statistics()
            print(f"\n📊 Processing Statistics:")
            for key, value in stats.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        if cli.processing_agent:
            await cli.processing_agent.stop_processing()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cli.processing_agent:
            await cli.processing_agent.stop_processing()


if __name__ == "__main__":
    asyncio.run(main())