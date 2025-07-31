#!/usr/bin/env python3
"""
Batch Content Curator
=====================

Intelligent batch processing system for creating curated essays from conversations.
Manages the pipeline: Archive → Native Format → AI Projections → Essay Creation → Book Compilation
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

from archive_cli import ArchiveCLI
from native_conversation_format import (
    NativeConversation, ConversationCollection, TransformationType,
    create_native_conversation_from_archive
)
from integrated_processing_cli import IntegratedProcessingCLI
from attribute_processing_agent import JobPriority


class EssayCandidate:
    """Represents a conversation that could become an essay"""
    
    def __init__(self, native_conversation: NativeConversation, assessment: Dict[str, Any]):
        self.conversation = native_conversation
        self.assessment = assessment
        self.essay_content = None
        self.writebook_entry = None
    
    @property
    def score(self) -> float:
        return self.assessment.get('overall_essay_score', 0.0)
    
    @property
    def estimated_reading_time(self) -> float:
        return self.assessment.get('estimated_reading_time', 0.0)
    
    @property
    def target_audience(self) -> str:
        return self.assessment.get('target_audience', 'general_public')


class BatchCurator:
    """Intelligent batch curator for creating essays from conversations"""
    
    def __init__(self):
        self.archive_cli = ArchiveCLI()
        self.processing_cli = IntegratedProcessingCLI()
        self.output_dir = Path("./curated_content")
        self.essays_dir = self.output_dir / "essays"
        self.collections_dir = self.output_dir / "collections"
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.essays_dir.mkdir(exist_ok=True)
        self.collections_dir.mkdir(exist_ok=True)
        
        # Curation statistics
        self.stats = {
            'conversations_processed': 0,
            'essays_created': 0,
            'collections_built': 0,
            'total_word_count': 0,
            'average_quality_score': 0.0
        }
    
    async def discover_and_curate(self, 
                                topic: str,
                                max_conversations: int = 50,
                                min_quality: float = 0.6,
                                max_essays: int = 20) -> ConversationCollection:
        """Discover conversations and curate them into essays"""
        
        print(f"🎯 Starting curation for topic: '{topic}'")
        print(f"   Max conversations: {max_conversations}")
        print(f"   Min quality: {min_quality}")
        print(f"   Max essays: {max_essays}")
        
        # Step 1: Discover relevant conversations
        print("\n🔍 Discovering conversations...")
        discovered = await self.processing_cli.discover_content(
            search_query=topic,
            limit=max_conversations * 2,  # Get extra to filter
            quality_filter=True
        )
        
        print(f"   Found {len(discovered)} quality conversations")
        
        # Step 2: Process conversations to get full analysis
        print("\n🔄 Processing conversations for analysis...")
        processed_conversations = []
        
        # Process in smaller batches to avoid overwhelming
        batch_size = 10
        for i in range(0, min(len(discovered), max_conversations), batch_size):
            batch = discovered[i:i + batch_size]
            conversation_ids = [str(conv['id']) for conv in batch]
            
            print(f"   Processing batch {i//batch_size + 1}: {len(conversation_ids)} conversations")
            
            # Use batch processing from integrated CLI
            batch_results = await self.processing_cli.batch_process_conversations(
                conversation_ids, 
                priority=JobPriority.BATCH
            )
            
            # Convert to native format
            for conv_id, job_result in batch_results.get('job_results', {}).items():
                if job_result.get('status') == 'completed':
                    # Load the individual result file
                    result_file = self.processing_cli.output_dir / f"conv_{conv_id}_batch_result.json"
                    if result_file.exists():
                        with open(result_file, 'r') as f:
                            processing_data = json.load(f)
                        
                        # Find original conversation data
                        original_conv = next(
                            (conv for conv in discovered if str(conv['id']) == conv_id), 
                            None
                        )
                        
                        if original_conv:
                            # Get full conversation messages
                            archive_data = self.archive_cli.get_conversation_messages(int(conv_id))
                            if archive_data:
                                native_conv = create_native_conversation_from_archive(
                                    archive_data, 
                                    processing_data
                                )
                                processed_conversations.append(native_conv)
        
        print(f"   Successfully processed {len(processed_conversations)} conversations")
        
        # Step 3: Create collection and assess essay potential
        collection = ConversationCollection(
            name=f"Curated Essays: {topic}",
            subject_focus=topic,
            quality_threshold=min_quality,
            target_transformations=[
                TransformationType.PHILOSOPHICAL_PROJECTION,
                TransformationType.LAMISH_VEIL,
                TransformationType.ACADEMIC_SUMMARY
            ]
        )
        
        for conv in processed_conversations:
            collection.add_conversation(conv)
        
        # Step 4: Get essay candidates
        print(f"\n📝 Assessing essay potential...")
        essay_candidates = collection.get_essay_candidates(min_score=min_quality)
        
        # Sort by score and take top candidates
        essay_candidates.sort(key=lambda x: x['assessment']['overall_essay_score'], reverse=True)
        essay_candidates = essay_candidates[:max_essays]
        
        print(f"   Found {len(essay_candidates)} essay candidates")
        
        # Step 5: Create essays
        created_essays = []
        for i, candidate_data in enumerate(essay_candidates, 1):
            conv = candidate_data['conversation']
            assessment = candidate_data['assessment']
            
            print(f"   Creating essay {i}/{len(essay_candidates)}: {conv.title[:50]}...")
            
            essay = await self._create_essay_from_conversation(conv, assessment, topic)
            if essay:
                created_essays.append(essay)
        
        # Step 6: Save collection and statistics
        collection_file = self.collections_dir / f"collection_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(collection_file, 'w') as f:
            json.dump(collection.dict(), f, indent=2, default=str)
        
        # Update statistics
        self.stats['conversations_processed'] += len(processed_conversations)
        self.stats['essays_created'] += len(created_essays)
        self.stats['collections_built'] += 1
        self.stats['total_word_count'] += collection.total_word_count
        
        if processed_conversations:
            avg_quality = sum(conv.conversation_quality_score for conv in processed_conversations) / len(processed_conversations)
            self.stats['average_quality_score'] = avg_quality
        
        print(f"\n✅ Curation completed!")
        print(f"   📚 Collection saved: {collection_file}")
        print(f"   📝 Essays created: {len(created_essays)}")
        print(f"   📊 Average quality: {self.stats['average_quality_score']:.2f}")
        
        return collection
    
    async def _create_essay_from_conversation(self, 
                                            conversation: NativeConversation,
                                            assessment: Dict[str, Any],
                                            topic: str) -> Optional[Dict[str, Any]]:
        """Create an essay from a conversation"""
        
        # Choose best projection for essay
        best_projection = None
        if TransformationType.LAMISH_VEIL in conversation.conversation_projections:
            best_projection = conversation.conversation_projections[TransformationType.LAMISH_VEIL]
            projection_type = "lamish_veil"
        elif TransformationType.PHILOSOPHICAL_PROJECTION in conversation.conversation_projections:
            best_projection = conversation.conversation_projections[TransformationType.PHILOSOPHICAL_PROJECTION]
            projection_type = "philosophical"
        elif TransformationType.ACADEMIC_SUMMARY in conversation.conversation_projections:
            best_projection = conversation.conversation_projections[TransformationType.ACADEMIC_SUMMARY]
            projection_type = "academic"
        
        if not best_projection:
            print(f"     ❌ No suitable projection found for {conversation.title}")
            return None
        
        # Create essay structure
        essay = {
            "essay_id": str(uuid.uuid4()),
            "title": self._generate_essay_title(conversation.title, topic),
            "subtitle": f"A {projection_type.title()} Exploration",
            "source_conversation_id": conversation.conversation_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            
            # Content
            "content": {
                "narrative": best_projection.get('narrative', ''),
                "reflection": best_projection.get('reflection', ''),
                "word_count": len(best_projection.get('narrative', '').split())
            },
            
            # Metadata
            "metadata": {
                "projection_type": projection_type,
                "quality_score": assessment.get('overall_essay_score', 0.0),
                "target_audience": assessment.get('target_audience', 'general_public'),
                "estimated_reading_time": assessment.get('estimated_reading_time', 0.0),
                "original_conversation_stats": {
                    "total_messages": conversation.total_messages,
                    "total_word_count": conversation.total_word_count,
                    "participants": len(conversation.participants)
                }
            },
            
            # Publication metadata
            "publication": {
                "ready_for_writebook": True,
                "ready_for_discourse": assessment.get('overall_essay_score', 0.0) > 0.7,
                "suggested_categories": conversation.subject_classifications,
                "content_warnings": []
            }
        }
        
        # Save essay
        essay_filename = f"essay_{essay['essay_id']}_{topic.replace(' ', '_')}.json"
        essay_file = self.essays_dir / essay_filename
        
        with open(essay_file, 'w') as f:
            json.dump(essay, f, indent=2, default=str)
        
        print(f"     ✅ Essay saved: {essay_file}")
        
        return essay
    
    def _generate_essay_title(self, original_title: str, topic: str) -> str:
        """Generate an appropriate essay title"""
        if len(original_title) > 60:
            # Use topic-based title for long original titles
            return f"Exploring {topic}: Insights from Modern Discourse"
        else:
            # Enhance original title
            return f"{original_title}: A Study in {topic}"
    
    async def curate_by_quality_tiers(self,
                                    search_query: str,
                                    tier_thresholds: Dict[str, float] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Curate content into quality tiers for different purposes"""
        
        if tier_thresholds is None:
            tier_thresholds = {
                'premium': 0.85,      # Best content for books/academic use
                'standard': 0.70,     # Good content for public essays
                'draft': 0.55,        # Potential content for further development
                'archive': 0.40       # Archive quality for reference
            }
        
        print(f"🎯 Curating by quality tiers for: '{search_query}'")
        
        # Discover and process content
        collection = await self.discover_and_curate(
            topic=search_query,
            max_conversations=100,
            min_quality=tier_thresholds['archive'],
            max_essays=50
        )
        
        # Organize into tiers
        tiers = {tier: [] for tier in tier_thresholds.keys()}
        
        for conv in collection.conversations:
            quality_score = conv.conversation_quality_score
            
            # Assign to highest applicable tier
            for tier, threshold in sorted(tier_thresholds.items(), 
                                        key=lambda x: x[1], reverse=True):
                if quality_score >= threshold:
                    essay_assessment = conv.assess_essay_potential()
                    tiers[tier].append({
                        'conversation': conv,
                        'quality_score': quality_score,
                        'essay_potential': essay_assessment,
                        'recommended_use': self._recommend_use_by_tier(tier)
                    })
                    break
        
        # Save tier analysis
        tier_file = self.collections_dir / f"quality_tiers_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(tier_file, 'w') as f:
            json.dump({
                'search_query': search_query,
                'tier_thresholds': tier_thresholds,
                'tier_counts': {tier: len(items) for tier, items in tiers.items()},
                'tiers': {tier: [item for item in items] for tier, items in tiers.items()}
            }, f, indent=2, default=str)
        
        print(f"\n📊 Quality Tier Analysis:")
        for tier, items in tiers.items():
            print(f"   {tier.upper()}: {len(items)} items (≥{tier_thresholds[tier]:.2f})")
        
        print(f"💾 Tier analysis saved: {tier_file}")
        
        return tiers
    
    def _recommend_use_by_tier(self, tier: str) -> List[str]:
        """Recommend uses based on quality tier"""
        recommendations = {
            'premium': [
                "Academic book chapters",
                "High-quality blog posts",
                "Conference presentation material",
                "Premium content for subscribers"
            ],
            'standard': [
                "Public blog posts with Lamish veil",
                "Discourse community discussions",
                "Educational resources",
                "Social media long-form content"
            ],
            'draft': [
                "Internal development content",
                "Basis for further refinement",
                "Reference material for other essays",
                "Training data for AI models"
            ],
            'archive': [
                "Long-term storage",
                "Historical reference",
                "Context for other content",
                "Data mining and analysis"
            ]
        }
        return recommendations.get(tier, ["General reference"])
    
    def get_curation_statistics(self) -> Dict[str, Any]:
        """Get detailed curation statistics"""
        return {
            **self.stats,
            'output_directories': {
                'essays': str(self.essays_dir),
                'collections': str(self.collections_dir),
                'main_output': str(self.output_dir)
            },
            'files_created': {
                'essay_files': len(list(self.essays_dir.glob('*.json'))),
                'collection_files': len(list(self.collections_dir.glob('*.json')))
            }
        }


async def main():
    """Main CLI interface for batch curation"""
    parser = argparse.ArgumentParser(description="Batch Content Curator - Create Essays from Conversations")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Curate command
    curate_parser = subparsers.add_parser('curate', help='Curate conversations into essays')
    curate_parser.add_argument('--topic', required=True, help='Topic to curate around')
    curate_parser.add_argument('--max-conversations', type=int, default=50, help='Max conversations to process')
    curate_parser.add_argument('--min-quality', type=float, default=0.6, help='Minimum quality threshold')
    curate_parser.add_argument('--max-essays', type=int, default=20, help='Maximum essays to create')
    
    # Quality tiers command
    tiers_parser = subparsers.add_parser('tiers', help='Curate content into quality tiers')
    tiers_parser.add_argument('search_query', help='Search query for content')
    tiers_parser.add_argument('--premium-threshold', type=float, default=0.85, help='Premium tier threshold')
    tiers_parser.add_argument('--standard-threshold', type=float, default=0.70, help='Standard tier threshold')
    tiers_parser.add_argument('--draft-threshold', type=float, default=0.55, help='Draft tier threshold')
    tiers_parser.add_argument('--archive-threshold', type=float, default=0.40, help='Archive tier threshold')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show curation statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    curator = BatchCurator()
    
    try:
        if args.command == 'curate':
            collection = await curator.discover_and_curate(
                topic=args.topic,
                max_conversations=args.max_conversations,
                min_quality=args.min_quality,
                max_essays=args.max_essays
            )
            
            print(f"\n🎉 Curation Summary:")
            print(f"   Topic: {args.topic}")
            print(f"   Conversations processed: {collection.total_conversations}")
            print(f"   Total word count: {collection.total_word_count:,}")
            print(f"   Essays created: Check {curator.essays_dir}")
        
        elif args.command == 'tiers':
            tier_thresholds = {
                'premium': args.premium_threshold,
                'standard': args.standard_threshold,
                'draft': args.draft_threshold,
                'archive': args.archive_threshold
            }
            
            tiers = await curator.curate_by_quality_tiers(
                args.search_query,
                tier_thresholds
            )
            
            print(f"\n🎉 Quality Tier Curation Complete:")
            total_items = sum(len(items) for items in tiers.values())
            print(f"   Total items categorized: {total_items}")
            
        elif args.command == 'stats':
            stats = curator.get_curation_statistics()
            print(f"\n📊 Curation Statistics:")
            for key, value in stats.items():
                if isinstance(value, dict):
                    print(f"   {key.replace('_', ' ').title()}:")
                    for subkey, subvalue in value.items():
                        print(f"     {subkey}: {subvalue}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Curation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())