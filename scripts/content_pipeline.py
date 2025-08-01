#!/usr/bin/env python3
"""
Flexible Content Pipeline System
Routes narratives through transformations to multiple destinations: humanizer threads, books, Discourse posts, etc.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import argparse
from abc import ABC, abstractmethod
import yaml

class DestinationType(Enum):
    HUMANIZER_THREAD = "humanizer_thread"
    BOOK_CHAPTER = "book_chapter"
    DISCOURSE_POST = "discourse_post"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    ACADEMIC_PAPER = "academic_paper"
    NEWSLETTER = "newsletter"
    PODCAST_SCRIPT = "podcast_script"

class TransformationType(Enum):
    QUALITY_ENHANCEMENT = "quality_enhancement"
    STRUCTURAL_IMPROVEMENT = "structural_improvement"
    TONE_ADJUSTMENT = "tone_adjustment"
    LENGTH_OPTIMIZATION = "length_optimization"
    AUDIENCE_ADAPTATION = "audience_adaptation"
    FORMAT_CONVERSION = "format_conversion"
    FACT_VERIFICATION = "fact_verification"
    STYLE_HARMONIZATION = "style_harmonization"

@dataclass
class ContentItem:
    """Represents a piece of content moving through the pipeline"""
    content_id: str
    source_conversation_id: int
    title: str
    content: str
    metadata: Dict[str, Any]
    quality_scores: Dict[str, float]
    transformations_applied: List[str]
    destination_preferences: List[DestinationType]
    processing_status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class PipelineRule:
    """Defines routing and transformation rules"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]  # Metadata conditions for triggering
    transformations: List[TransformationType]
    destinations: List[DestinationType]
    priority: int
    active: bool

class ContentTransformer(ABC):
    """Abstract base class for content transformers"""
    
    @abstractmethod
    def transform(self, content_item: ContentItem) -> ContentItem:
        pass
    
    @abstractmethod
    def can_transform(self, content_item: ContentItem) -> bool:
        pass

class DestinationHandler(ABC):
    """Abstract base class for destination handlers"""
    
    @abstractmethod
    def publish(self, content_item: ContentItem) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def can_handle(self, destination_type: DestinationType) -> bool:
        pass

class QualityEnhancementTransformer(ContentTransformer):
    """Enhances content quality using LLM analysis"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
    
    def transform(self, content_item: ContentItem) -> ContentItem:
        print(f"🔧 Applying quality enhancement to: {content_item.title}")
        
        # Analyze current quality issues
        quality_analysis = self._analyze_quality_issues(content_item)
        
        # Apply improvements
        improved_content = self._apply_improvements(content_item, quality_analysis)
        
        # Update content item
        content_item.content = improved_content
        content_item.transformations_applied.append("quality_enhancement")
        content_item.updated_at = datetime.now()
        
        return content_item
    
    def can_transform(self, content_item: ContentItem) -> bool:
        return content_item.quality_scores.get('composite', 0) < 0.8
    
    def _analyze_quality_issues(self, content_item: ContentItem) -> Dict[str, Any]:
        """Analyze specific quality issues using LLM"""
        
        prompt = f"""
        Analyze this content for specific quality issues and improvement opportunities:
        
        TITLE: {content_item.title}
        QUALITY SCORES: {content_item.quality_scores}
        
        CONTENT:
        {content_item.content[:3000]}
        
        Identify specific issues and provide improvement suggestions:
        
        Respond in JSON format:
        {{
            "clarity_issues": ["issue1", "issue2", ...],
            "structure_issues": ["issue1", "issue2", ...],
            "coherence_issues": ["issue1", "issue2", ...],
            "completeness_gaps": ["gap1", "gap2", ...],
            "improvement_priority": "high|medium|low",
            "specific_improvements": [
                {{"type": "clarity|structure|coherence|completeness", "description": "...", "suggestion": "..."}},
                ...
            ]
        }}
        """
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                response_text = response.json().get('response', '{}')
                return json.loads(response_text)
        
        except Exception as e:
            print(f"⚠️ Quality analysis failed: {e}")
        
        return {}
    
    def _apply_improvements(self, content_item: ContentItem, analysis: Dict[str, Any]) -> str:
        """Apply specific improvements to content"""
        
        improvements = analysis.get('specific_improvements', [])
        if not improvements:
            return content_item.content
        
        # Create improvement prompt
        improvement_descriptions = []
        for improvement in improvements[:5]:  # Limit to top 5
            improvement_descriptions.append(f"- {improvement.get('type', 'general')}: {improvement.get('suggestion', '')}")
        
        prompt = f"""
        Improve this content by addressing the following specific issues:
        
        {chr(10).join(improvement_descriptions)}
        
        ORIGINAL CONTENT:
        {content_item.content}
        
        Provide the improved version while maintaining the original meaning and intent:
        """
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                improved_content = response.json().get('response', '')
                if len(improved_content) > 100:  # Sanity check
                    return improved_content
        
        except Exception as e:
            print(f"⚠️ Content improvement failed: {e}")
        
        return content_item.content

class StructuralImprovementTransformer(ContentTransformer):
    """Improves content structure and organization"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
    
    def transform(self, content_item: ContentItem) -> ContentItem:
        print(f"📐 Applying structural improvements to: {content_item.title}")
        
        structured_content = self._restructure_content(content_item)
        
        content_item.content = structured_content
        content_item.transformations_applied.append("structural_improvement")
        content_item.updated_at = datetime.now()
        
        return content_item
    
    def can_transform(self, content_item: ContentItem) -> bool:
        return (content_item.quality_scores.get('coherence_score', 0) < 0.7 or 
                len(content_item.content) > 1000)  # Longer content benefits from structure
    
    def _restructure_content(self, content_item: ContentItem) -> str:
        """Restructure content for better organization"""
        
        prompt = f"""
        Restructure this content for better organization and flow:
        
        TITLE: {content_item.title}
        CATEGORY: {content_item.metadata.get('category', 'general')}
        
        CONTENT:
        {content_item.content}
        
        Restructure with:
        1. Clear introduction
        2. Logical section breaks
        3. Smooth transitions
        4. Compelling conclusion
        
        Maintain the original ideas and meaning while improving structure:
        """
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                restructured = response.json().get('response', '')
                if len(restructured) > 100:
                    return restructured
        
        except Exception as e:
            print(f"⚠️ Structural improvement failed: {e}")
        
        return content_item.content

class FormatConversionTransformer(ContentTransformer):
    """Converts content to different formats based on destination"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        
        self.format_templates = {
            DestinationType.DISCOURSE_POST: {
                'intro': 'Engaging community discussion starter',
                'structure': 'conversational with questions',
                'length': 'medium (300-800 words)',
                'tone': 'inclusive and thought-provoking'
            },
            DestinationType.BLOG_POST: {
                'intro': 'Hook readers with compelling opening',
                'structure': 'intro -> main points -> conclusion with CTA',
                'length': 'long-form (800-2000 words)',
                'tone': 'informative yet accessible'
            },
            DestinationType.SOCIAL_MEDIA: {
                'intro': 'Attention-grabbing first line',
                'structure': 'key insight -> brief explanation -> engagement hook',
                'length': 'short (under 280 chars for Twitter)',
                'tone': 'concise and engaging'
            },
            DestinationType.ACADEMIC_PAPER: {
                'intro': 'Abstract and literature context',
                'structure': 'formal academic structure with citations',
                'length': 'comprehensive (3000+ words)',
                'tone': 'formal and scholarly'
            }
        }
    
    def transform(self, content_item: ContentItem) -> ContentItem:
        destination = content_item.destination_preferences[0] if content_item.destination_preferences else DestinationType.BLOG_POST
        
        print(f"🔄 Converting format for destination: {destination.value}")
        
        converted_content = self._convert_to_format(content_item, destination)
        
        content_item.content = converted_content
        content_item.transformations_applied.append("format_conversion")
        content_item.metadata['target_format'] = destination.value
        content_item.updated_at = datetime.now()
        
        return content_item
    
    def can_transform(self, content_item: ContentItem) -> bool:
        return bool(content_item.destination_preferences)
    
    def _convert_to_format(self, content_item: ContentItem, destination: DestinationType) -> str:
        """Convert content to specific format"""
        
        if destination not in self.format_templates:
            return content_item.content
        
        template = self.format_templates[destination]
        
        prompt = f"""
        Convert this content to {destination.value} format:
        
        FORMAT REQUIREMENTS:
        - Introduction: {template['intro']}
        - Structure: {template['structure']}
        - Target length: {template['length']}
        - Tone: {template['tone']}
        
        ORIGINAL CONTENT:
        {content_item.content}
        
        Convert while preserving the core ideas and insights:
        """
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                converted = response.json().get('response', '')
                if len(converted) > 50:
                    return converted
        
        except Exception as e:
            print(f"⚠️ Format conversion failed: {e}")
        
        return content_item.content

class HumanizerThreadHandler(DestinationHandler):
    """Handler for publishing to humanizer threads"""
    
    def publish(self, content_item: ContentItem) -> Dict[str, Any]:
        print(f"📝 Publishing to humanizer thread: {content_item.title}")
        
        # Create thread-optimized content
        thread_content = self._format_for_thread(content_item)
        
        # In a real implementation, this would post to the humanizer platform
        result = {
            'destination': 'humanizer_thread',
            'status': 'published',
            'thread_id': f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'url': f"https://humanizer.com/threads/{content_item.content_id}",
            'formatted_content': thread_content
        }
        
        return result
    
    def can_handle(self, destination_type: DestinationType) -> bool:
        return destination_type == DestinationType.HUMANIZER_THREAD
    
    def _format_for_thread(self, content_item: ContentItem) -> str:
        """Format content for humanizer thread"""
        
        # Add thread-specific formatting
        formatted = f"# {content_item.title}\n\n"
        formatted += f"*Source: Conversation {content_item.source_conversation_id}*\n\n"
        formatted += content_item.content
        formatted += f"\n\n---\n*Processed by Humanizer Pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        return formatted

class DiscoursePostHandler(DestinationHandler):
    """Handler for publishing to Discourse forum"""
    
    def __init__(self, discourse_url: str = None, api_key: str = None):
        self.discourse_url = discourse_url
        self.api_key = api_key
    
    def publish(self, content_item: ContentItem) -> Dict[str, Any]:
        print(f"💬 Publishing to Discourse: {content_item.title}")
        
        # Format for Discourse
        discourse_content = self._format_for_discourse(content_item)
        
        if self.discourse_url and self.api_key:
            # Real Discourse API call would go here
            pass
        
        result = {
            'destination': 'discourse_post',
            'status': 'published',
            'post_id': f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'category': self._determine_discourse_category(content_item),
            'formatted_content': discourse_content
        }
        
        return result
    
    def can_handle(self, destination_type: DestinationType) -> bool:
        return destination_type == DestinationType.DISCOURSE_POST
    
    def _format_for_discourse(self, content_item: ContentItem) -> str:
        """Format content for Discourse post"""
        
        # Add Discourse-specific formatting
        formatted = content_item.content
        
        # Add metadata tags
        tags = []
        if content_item.metadata.get('category'):
            tags.append(content_item.metadata['category'])
        
        if content_item.quality_scores.get('composite', 0) > 0.8:
            tags.append('high-quality')
        
        if tags:
            formatted += f"\n\n*Tags: {', '.join(tags)}*"
        
        return formatted
    
    def _determine_discourse_category(self, content_item: ContentItem) -> str:
        """Determine appropriate Discourse category"""
        
        category_map = {
            'philosophical': 'Philosophy',
            'technical': 'Technology',
            'creative': 'Creative Writing',
            'academic': 'Research',
            'personal': 'General Discussion'
        }
        
        content_category = content_item.metadata.get('category', 'general')
        return category_map.get(content_category, 'General Discussion')

class BookChapterHandler(DestinationHandler):
    """Handler for organizing content into book chapters"""
    
    def __init__(self, output_dir: str = "book_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def publish(self, content_item: ContentItem) -> Dict[str, Any]:
        print(f"📖 Organizing as book chapter: {content_item.title}")
        
        chapter_content = self._format_as_chapter(content_item)
        
        # Save to file
        filename = f"chapter_{content_item.content_id}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(chapter_content)
        
        result = {
            'destination': 'book_chapter',
            'status': 'saved',
            'file_path': filepath,
            'word_count': len(chapter_content.split()),
            'chapter_number': self._assign_chapter_number(content_item)
        }
        
        return result
    
    def can_handle(self, destination_type: DestinationType) -> bool:
        return destination_type == DestinationType.BOOK_CHAPTER
    
    def _format_as_chapter(self, content_item: ContentItem) -> str:
        """Format content as book chapter"""
        
        formatted = f"# Chapter: {content_item.title}\n\n"
        formatted += f"*Quality Score: {content_item.quality_scores.get('composite', 0):.3f}*\n\n"
        formatted += content_item.content
        formatted += f"\n\n---\n\n*Source: Conversation {content_item.source_conversation_id}*\n"
        formatted += f"*Transformations Applied: {', '.join(content_item.transformations_applied)}*\n"
        
        return formatted
    
    def _assign_chapter_number(self, content_item: ContentItem) -> int:
        """Assign chapter number based on quality and topic"""
        
        # Simple assignment based on quality score
        quality = content_item.quality_scores.get('composite', 0)
        if quality >= 0.9:
            return 1  # Best content first
        elif quality >= 0.8:
            return 2
        elif quality >= 0.7:
            return 3
        else:
            return 4

class ContentPipeline:
    """Main content pipeline orchestrator"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.transformers = {}
        self.destination_handlers = {}
        self.pipeline_rules = []
        
        # Initialize default transformers
        self._initialize_transformers()
        
        # Initialize default destination handlers
        self._initialize_destination_handlers()
        
        print("🔄 Content Pipeline System")
        print("=" * 40)
    
    def _initialize_transformers(self):
        """Initialize available transformers"""
        
        self.transformers = {
            TransformationType.QUALITY_ENHANCEMENT: QualityEnhancementTransformer(),
            TransformationType.STRUCTURAL_IMPROVEMENT: StructuralImprovementTransformer(),
            TransformationType.FORMAT_CONVERSION: FormatConversionTransformer()
        }
    
    def _initialize_destination_handlers(self):
        """Initialize available destination handlers"""
        
        self.destination_handlers = {
            DestinationType.HUMANIZER_THREAD: HumanizerThreadHandler(),
            DestinationType.DISCOURSE_POST: DiscoursePostHandler(),
            DestinationType.BOOK_CHAPTER: BookChapterHandler()
        }
    
    def add_pipeline_rule(self, rule: PipelineRule):
        """Add a new pipeline rule"""
        self.pipeline_rules.append(rule)
        self.pipeline_rules.sort(key=lambda r: r.priority, reverse=True)
        print(f"📋 Added pipeline rule: {rule.name}")
    
    def create_content_item_from_conversation(self, conversation_id: int) -> Optional[ContentItem]:
        """Create content item from conversation"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ac.id, ac.title, ac.body_text, ac.word_count, ac.category,
                    ac.extracted_attributes, ac.search_terms,
                    cqa.composite_score, cqa.readability_score, cqa.coherence_score,
                    cqa.depth_score, cqa.completeness_score, cqa.primary_topic,
                    cqa.editorial_potential
                FROM archived_content ac
                LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                WHERE ac.id = %s AND ac.content_type = 'conversation'
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            content_item = ContentItem(
                content_id=f"conv_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_conversation_id=conversation_id,
                title=row['title'] or f"Conversation {conversation_id}",
                content=row['body_text'] or "",
                metadata={
                    'category': row['category'],
                    'word_count': row['word_count'],
                    'primary_topic': row['primary_topic'],
                    'editorial_potential': row['editorial_potential'],
                    'search_terms': row['search_terms'] or [],
                    'extracted_attributes': row['extracted_attributes'] or {}
                },
                quality_scores={
                    'composite': float(row['composite_score']) if row['composite_score'] else 0,
                    'readability_score': float(row['readability_score']) if row['readability_score'] else 0,
                    'coherence_score': float(row['coherence_score']) if row['coherence_score'] else 0,
                    'depth_score': float(row['depth_score']) if row['depth_score'] else 0,
                    'completeness_score': float(row['completeness_score']) if row['completeness_score'] else 0
                },
                transformations_applied=[],
                destination_preferences=[],
                processing_status='created',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return content_item
    
    def determine_destinations(self, content_item: ContentItem) -> List[DestinationType]:
        """Determine appropriate destinations based on content characteristics"""
        
        destinations = []
        
        # Quality-based routing
        quality = content_item.quality_scores.get('composite', 0)
        if quality >= 0.8:
            destinations.extend([DestinationType.BOOK_CHAPTER, DestinationType.BLOG_POST])
        elif quality >= 0.6:
            destinations.extend([DestinationType.DISCOURSE_POST, DestinationType.HUMANIZER_THREAD])
        
        # Category-based routing
        category = content_item.metadata.get('category', '')
        if category in ['philosophical', 'academic']:
            destinations.append(DestinationType.ACADEMIC_PAPER)
        elif category in ['technical', 'educational']:
            destinations.append(DestinationType.BLOG_POST)
        elif category in ['personal', 'creative']:
            destinations.append(DestinationType.HUMANIZER_THREAD)
        
        # Length-based routing
        word_count = content_item.metadata.get('word_count', 0)
        if word_count < 200:
            destinations.append(DestinationType.SOCIAL_MEDIA)
        elif word_count > 2000:
            destinations.append(DestinationType.BOOK_CHAPTER)
        
        # Remove duplicates and return
        return list(set(destinations))
    
    def apply_pipeline_rules(self, content_item: ContentItem) -> Tuple[List[TransformationType], List[DestinationType]]:
        """Apply pipeline rules to determine transformations and destinations"""
        
        applicable_transformations = []
        applicable_destinations = []
        
        for rule in self.pipeline_rules:
            if not rule.active:
                continue
            
            # Check if rule conditions are met
            if self._evaluate_rule_conditions(content_item, rule.conditions):
                applicable_transformations.extend(rule.transformations)
                applicable_destinations.extend(rule.destinations)
                print(f"📋 Applied rule: {rule.name}")
        
        # Remove duplicates
        applicable_transformations = list(set(applicable_transformations))
        applicable_destinations = list(set(applicable_destinations))
        
        # Fallback to automatic determination if no rules applied
        if not applicable_destinations:
            applicable_destinations = self.determine_destinations(content_item)
        
        return applicable_transformations, applicable_destinations
    
    def _evaluate_rule_conditions(self, content_item: ContentItem, conditions: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        
        for condition_key, condition_value in conditions.items():
            if condition_key == 'min_quality':
                if content_item.quality_scores.get('composite', 0) < condition_value:
                    return False
            elif condition_key == 'max_quality':
                if content_item.quality_scores.get('composite', 0) > condition_value:
                    return False
            elif condition_key == 'category':
                if content_item.metadata.get('category') != condition_value:
                    return False
            elif condition_key == 'min_words':
                if content_item.metadata.get('word_count', 0) < condition_value:
                    return False
            elif condition_key == 'max_words':
                if content_item.metadata.get('word_count', 0) > condition_value:
                    return False
        
        return True
    
    def process_content_item(self, content_item: ContentItem) -> Dict[str, Any]:
        """Process a content item through the complete pipeline"""
        
        print(f"🔄 Processing content item: {content_item.title}")
        
        # Apply pipeline rules
        transformations, destinations = self.apply_pipeline_rules(content_item)
        content_item.destination_preferences = destinations
        
        # Apply transformations
        for transformation_type in transformations:
            if transformation_type in self.transformers:
                transformer = self.transformers[transformation_type]
                if transformer.can_transform(content_item):
                    content_item = transformer.transform(content_item)
        
        # Publish to destinations
        publication_results = []
        for destination_type in destinations:
            if destination_type in self.destination_handlers:
                handler = self.destination_handlers[destination_type]
                if handler.can_handle(destination_type):
                    result = handler.publish(content_item)
                    publication_results.append(result)
        
        # Store processing record
        processing_record = {
            'content_id': content_item.content_id,
            'source_conversation_id': content_item.source_conversation_id,
            'transformations_applied': content_item.transformations_applied,
            'destinations_published': [r['destination'] for r in publication_results],
            'publication_results': publication_results,
            'processing_status': 'completed',
            'processed_at': datetime.now().isoformat()
        }
        
        self._store_processing_record(processing_record)
        
        print(f"✅ Completed processing: {len(transformations)} transformations, {len(publication_results)} publications")
        
        return processing_record
    
    def _store_processing_record(self, record: Dict[str, Any]):
        """Store processing record in database"""
        
        with psycopg2.connect(self.database_url) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_pipeline_records (
                    id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255),
                    source_conversation_id BIGINT,
                    transformations_applied JSONB,
                    destinations_published JSONB,
                    publication_results JSONB,
                    processing_status VARCHAR(50),
                    processed_at TIMESTAMP
                )
            """)
            
            # Insert record
            cursor.execute("""
                INSERT INTO content_pipeline_records 
                (content_id, source_conversation_id, transformations_applied, 
                 destinations_published, publication_results, processing_status, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                record['content_id'],
                record['source_conversation_id'],
                json.dumps(record['transformations_applied']),
                json.dumps(record['destinations_published']),
                json.dumps(record['publication_results'], default=str),
                record['processing_status'],
                record['processed_at']
            ))
            
            conn.commit()
    
    def process_batch(self, conversation_ids: List[int]) -> List[Dict[str, Any]]:
        """Process a batch of conversations through the pipeline"""
        
        print(f"🔄 Processing batch of {len(conversation_ids)} conversations")
        
        results = []
        for conversation_id in conversation_ids:
            try:
                content_item = self.create_content_item_from_conversation(conversation_id)
                if content_item:
                    result = self.process_content_item(content_item)
                    results.append(result)
                else:
                    print(f"⚠️ Could not create content item for conversation {conversation_id}")
            except Exception as e:
                print(f"❌ Error processing conversation {conversation_id}: {e}")
                continue
        
        print(f"✅ Batch processing complete: {len(results)} items processed")
        return results
    
    def load_pipeline_config(self, config_file: str):
        """Load pipeline configuration from YAML file"""
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load pipeline rules
            if 'pipeline_rules' in config:
                for rule_config in config['pipeline_rules']:
                    rule = PipelineRule(
                        rule_id=rule_config['rule_id'],
                        name=rule_config['name'],
                        description=rule_config['description'],
                        conditions=rule_config['conditions'],
                        transformations=[TransformationType(t) for t in rule_config['transformations']],
                        destinations=[DestinationType(d) for d in rule_config['destinations']],
                        priority=rule_config['priority'],
                        active=rule_config.get('active', True)
                    )
                    self.add_pipeline_rule(rule)
            
            print(f"📋 Loaded pipeline configuration from: {config_file}")
            
        except Exception as e:
            print(f"❌ Error loading pipeline config: {e}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Content Pipeline System")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process conversations through pipeline')
    process_parser.add_argument('--conversation-ids', nargs='+', type=int, help='Specific conversation IDs')
    process_parser.add_argument('--min-quality', type=float, help='Minimum quality threshold for auto-selection')
    process_parser.add_argument('--category', help='Category filter for auto-selection')
    process_parser.add_argument('--limit', type=int, default=10, help='Limit for auto-selection')
    process_parser.add_argument('--config', help='Pipeline configuration file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show pipeline processing status')
    
    args = parser.parse_args()
    
    pipeline = ContentPipeline()
    
    # Load configuration if provided
    if hasattr(args, 'config') and args.config:
        pipeline.load_pipeline_config(args.config)
    else:
        # Add default rules
        default_rule = PipelineRule(
            rule_id="high_quality_to_book",
            name="High Quality to Book Chapters",
            description="Route high-quality content to book chapter format",
            conditions={'min_quality': 0.8, 'min_words': 500},
            transformations=[TransformationType.QUALITY_ENHANCEMENT, TransformationType.STRUCTURAL_IMPROVEMENT],
            destinations=[DestinationType.BOOK_CHAPTER],
            priority=10,
            active=True
        )
        pipeline.add_pipeline_rule(default_rule)
        
        discourse_rule = PipelineRule(
            rule_id="medium_quality_to_discourse",
            name="Medium Quality to Discourse",
            description="Route medium quality content to Discourse posts",
            conditions={'min_quality': 0.5, 'max_quality': 0.8},
            transformations=[TransformationType.FORMAT_CONVERSION],
            destinations=[DestinationType.DISCOURSE_POST],
            priority=5,
            active=True
        )
        pipeline.add_pipeline_rule(discourse_rule)
    
    if args.command == 'process':
        conversation_ids = args.conversation_ids
        
        # Auto-select conversations if none specified
        if not conversation_ids:
            with psycopg2.connect(pipeline.database_url, cursor_factory=RealDictCursor) as conn:
                cursor = conn.cursor()
                
                conditions = ["ac.content_type = 'conversation'"]
                params = []
                
                if args.min_quality:
                    conditions.append("cqa.composite_score >= %s")
                    params.append(args.min_quality)
                
                if args.category:
                    conditions.append("ac.category = %s")
                    params.append(args.category)
                
                query = f"""
                    SELECT ac.id
                    FROM archived_content ac
                    LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                    WHERE {' AND '.join(conditions)}
                    ORDER BY cqa.composite_score DESC NULLS LAST
                    LIMIT %s
                """
                params.append(args.limit)
                
                cursor.execute(query, params)
                conversation_ids = [row['id'] for row in cursor.fetchall()]
        
        if conversation_ids:
            results = pipeline.process_batch(conversation_ids)
            
            print(f"\n📊 Pipeline Processing Summary:")
            print(f"   Conversations processed: {len(results)}")
            
            # Show destination breakdown
            destinations = {}
            for result in results:
                for dest in result['destinations_published']:
                    destinations[dest] = destinations.get(dest, 0) + 1
            
            print(f"   Destination breakdown:")
            for dest, count in destinations.items():
                print(f"     {dest}: {count}")
        
        else:
            print("❌ No conversations found matching criteria")
    
    elif args.command == 'status':
        with psycopg2.connect(pipeline.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    processing_status,
                    COUNT(*) as count,
                    MAX(processed_at) as latest_processing
                FROM content_pipeline_records
                GROUP BY processing_status
                ORDER BY count DESC
            """)
            
            print("📊 Pipeline Processing Status:")
            for row in cursor.fetchall():
                print(f"   {row['processing_status']}: {row['count']} items (latest: {row['latest_processing']})")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()