#!/usr/bin/env python3
"""
Universal Book Generator
General-purpose book generation system that works with any content source
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Callable
import re
from collections import Counter, defaultdict
import argparse
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib

# Import the advanced components from our previous implementation
from advanced_book_factory import (
    ContentInsight, ThematicCluster, BookStructure, ChapterStructure, SectionStructure,
    AdvancedSemanticAnalyzer
)

class ContentExtractor(ABC):
    """Abstract base class for content extractors"""
    
    @abstractmethod
    def extract_content(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract raw content from source"""
        pass
    
    @abstractmethod
    def get_source_description(self) -> str:
        """Get description of the content source"""
        pass

class NotebookTranscriptExtractor(ContentExtractor):
    """Extract content from notebook transcripts (Journal Recognizer OCR)"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def extract_content(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract notebook transcripts from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    child.id,
                    child.parent_id as conversation_id,
                    COALESCE(parent.title, 'Untitled') as conversation_title,
                    child.body_text,
                    child.timestamp,
                    child.author
                FROM archived_content child
                JOIN archived_content parent ON child.parent_id = parent.id
                WHERE child.source_metadata->>'gizmo_id' = %s
                    AND child.content_type = 'message'
                    AND child.body_text IS NOT NULL
                    AND LENGTH(child.body_text) > 300
                ORDER BY child.timestamp
            """, (self.JOURNAL_OCR_GIZMO_ID,))
            
            return cursor.fetchall()
    
    def get_source_description(self) -> str:
        return "Handwritten notebook transcripts from Journal Recognizer OCR"

class ConversationExtractor(ContentExtractor):
    """Extract content from general conversations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def extract_content(self, gizmo_id: str = None, author: str = None, 
                       min_length: int = 200, **kwargs) -> List[Dict[str, Any]]:
        """Extract conversation messages with flexible filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic query
            conditions = ["child.content_type = 'message'", "child.body_text IS NOT NULL"]
            params = []
            
            if gizmo_id:
                conditions.append("child.source_metadata->>'gizmo_id' = %s")
                params.append(gizmo_id)
            
            if author:
                conditions.append("child.author = %s")
                params.append(author)
            
            if min_length:
                conditions.append("LENGTH(child.body_text) > %s")
                params.append(min_length)
            
            query = f"""
                SELECT 
                    child.id,
                    child.parent_id as conversation_id,
                    COALESCE(parent.title, 'Untitled') as conversation_title,
                    child.body_text,
                    child.timestamp,
                    child.author,
                    child.source_metadata
                FROM archived_content child
                JOIN archived_content parent ON child.parent_id = parent.id
                WHERE {' AND '.join(conditions)}
                ORDER BY child.timestamp
            """
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_source_description(self) -> str:
        return "General conversation messages"

class FileExtractor(ContentExtractor):
    """Extract content from files"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def extract_content(self, file_patterns: List[str] = None, 
                       recursive: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """Extract content from files matching patterns"""
        if file_patterns is None:
            file_patterns = ['*.md', '*.txt']
        
        content_items = []
        
        for pattern in file_patterns:
            if recursive:
                files = self.base_path.rglob(pattern)
            else:
                files = self.base_path.glob(pattern)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content) > 100:  # Minimum content length
                        content_items.append({
                            'id': str(file_path),
                            'conversation_id': str(file_path.parent),
                            'conversation_title': file_path.stem,
                            'body_text': content,
                            'timestamp': datetime.fromtimestamp(file_path.stat().st_mtime),
                            'author': 'file_system'
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        return content_items
    
    def get_source_description(self) -> str:
        return f"Files from {self.base_path}"

class ContentProcessor:
    """Process raw content into insights"""
    
    def __init__(self, analyzer: AdvancedSemanticAnalyzer):
        self.analyzer = analyzer
    
    def process_raw_content(self, raw_content: List[Dict[str, Any]], 
                          content_filter: Callable[[str], str] = None,
                          min_quality: float = 0.3) -> List[ContentInsight]:
        """Process raw content into analyzed insights"""
        insights = []
        processed = 0
        
        print(f"📊 Processing {len(raw_content)} content items...")
        
        for item in raw_content:
            processed += 1
            if processed % 50 == 0:
                print(f"  Processed {processed}/{len(raw_content)} items...")
            
            # Extract meaningful content
            if content_filter:
                content = content_filter(item['body_text'])
            else:
                content = self._default_content_filter(item['body_text'])
            
            if not content or len(content) < 100:
                continue
            
            # Perform semantic analysis
            analysis = self.analyzer.analyze_content(content)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(content, analysis)
            
            if quality_score < min_quality:
                continue
            
            # Create content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
            
            insight = ContentInsight(
                id=f"insight_{item['id']}",
                source_id=str(item['conversation_id']),
                source_title=item['conversation_title'],
                content=content,
                timestamp=item['timestamp'].isoformat() if item.get('timestamp') else None,
                author=item.get('author', 'unknown'),
                word_count=len(content.split()),
                quality_score=quality_score,
                semantic_embedding=None,
                themes=analysis['themes'],
                concepts=[c['concept'] for c in analysis['concepts']],
                emotional_tone=analysis['emotional_tone'],
                complexity_level=analysis['complexity_level'],
                uniqueness_hash=content_hash
            )
            
            insights.append(insight)
        
        # Remove duplicates
        insights = self._deduplicate_insights(insights)
        
        print(f"✅ Processed {len(insights)} high-quality unique insights")
        return insights
    
    def _default_content_filter(self, body_text: str) -> str:
        """Default content filtering - extracts main content"""
        # Remove markdown code blocks if present
        patterns = [
            r'```markdown\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body_text, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Otherwise return the full text
        return body_text.strip()
    
    def _calculate_quality_score(self, content: str, analysis: Dict[str, Any]) -> float:
        """Calculate quality score for content"""
        score = 0.0
        word_count = len(content.split())
        
        # Base content quality (40% of score)
        if 50 <= word_count <= 500:
            score += 0.4
        elif word_count > 25:
            score += 0.2
        
        # Philosophical depth (25% of score)
        depth_score = analysis['philosophical_depth']
        score += depth_score * 0.25
        
        # Concept richness (20% of score)
        concept_score = min(len(analysis['concepts']) / 3.0, 1.0)
        score += concept_score * 0.20
        
        # Complexity appropriateness (10% of score)
        complexity = analysis['complexity_level']
        if 2 <= complexity <= 4:  # Sweet spot
            score += 0.10
        elif complexity >= 1:
            score += 0.05
        
        # Narrative elements (5% of score)
        narrative = analysis['narrative_elements']
        narrative_score = sum([
            narrative.get('has_questions', False),
            narrative.get('has_examples', False),
            narrative.get('personal_reflection', False)
        ]) / 3.0
        score += narrative_score * 0.05
        
        return min(score, 1.0)
    
    def _deduplicate_insights(self, insights: List[ContentInsight]) -> List[ContentInsight]:
        """Remove duplicate insights"""
        unique_insights = []
        seen_hashes = set()
        
        # Sort by quality score (keep highest quality versions)
        insights_sorted = sorted(insights, key=lambda x: x.quality_score, reverse=True)
        
        for insight in insights_sorted:
            if insight.uniqueness_hash not in seen_hashes:
                unique_insights.append(insight)
                seen_hashes.add(insight.uniqueness_hash)
        
        return unique_insights

class BookThemeTemplate:
    """Template for book themes with customizable parameters"""
    
    def __init__(self, name: str, title_templates: List[Tuple[str, str]], 
                 keywords: List[str], narrative_arc: str,
                 chapter_templates: Dict[int, List[str]]):
        self.name = name
        self.title_templates = title_templates
        self.keywords = keywords
        self.narrative_arc = narrative_arc
        self.chapter_templates = chapter_templates

class UniversalBookGenerator:
    """Universal book generator that works with any content source"""
    
    def __init__(self, content_extractor: ContentExtractor, database_url: str = None):
        self.content_extractor = content_extractor
        self.analyzer = AdvancedSemanticAnalyzer()
        self.content_processor = ContentProcessor(self.analyzer)
        self.output_dir = Path("universal_books")
        self.output_dir.mkdir(exist_ok=True)
        
        # Customizable book theme templates
        self.theme_templates = self._load_default_theme_templates()
        
        print("🌍 Universal Book Generator")
        print("=" * 50)
        print(f"📖 Content Source: {self.content_extractor.get_source_description()}")
    
    def _load_default_theme_templates(self) -> Dict[str, BookThemeTemplate]:
        """Load default book theme templates"""
        return {
            'consciousness': BookThemeTemplate(
                name='consciousness',
                title_templates=[
                    ("The Nature of Consciousness", "Explorations in Awareness and Being"),
                    ("Conscious Being", "An Inquiry into Awareness"),
                    ("The Awakening Mind", "Studies in Consciousness")
                ],
                keywords=['consciousness', 'awareness', 'being', 'mind', 'cognition'],
                narrative_arc="A journey from basic awareness through layers of consciousness to deep understanding",
                chapter_templates={
                    1: ["Foundations of Awareness", "The Nature of Consciousness", "Awakening to Being"],
                    2: ["Layers of Experience", "The Structure of Awareness", "Consciousness in Action"],
                    3: ["Deep Understanding", "Advanced Awareness", "The Integrated Self"],
                    4: ["Transcendent Awareness", "Beyond Individual Consciousness", "Unity of Being"]
                }
            ),
            'experience': BookThemeTemplate(
                name='experience',
                title_templates=[
                    ("The Art of Experience", "Perception, Sensation, and Meaning"),
                    ("Living Experience", "The Dance of Perception and Reality"),
                    ("Experience and Understanding", "How We Know What We Know")
                ],
                keywords=['experience', 'perception', 'sensation', 'feeling', 'knowing'],
                narrative_arc="Exploring the full spectrum of human experience from sensation to meaning",
                chapter_templates={
                    1: ["Basic Experience", "The World of Sensation", "Primary Perception"],
                    2: ["Complex Experience", "Meaning in Experience", "The Interpreted World"],
                    3: ["Deep Experience", "Layers of Understanding", "The Significance of Experience"],
                    4: ["Transformative Experience", "Experience as Teacher", "Learning from Life"]
                }
            ),
            'self': BookThemeTemplate(
                name='self',
                title_templates=[
                    ("The Question of Self", "Identity, Authenticity, and Being"),
                    ("Knowing the Self", "A Journey Beyond Ego"),
                    ("The Authentic Self", "Personal Truth and Identity")
                ],
                keywords=['self', 'identity', 'ego', 'personality', 'authenticity'],
                narrative_arc="An inquiry into personal identity from ego through authentic self to transcendence",
                chapter_templates={
                    1: ["The Question of Self", "Who Am I?", "The Search for Identity"],
                    2: ["Beyond Ego", "The Authentic Self", "True Identity"],
                    3: ["Self and Others", "Relational Identity", "The Social Self"],
                    4: ["The Evolving Self", "Growth and Change", "Transformation of Identity"]
                }
            )
        }
    
    def add_custom_theme_template(self, template: BookThemeTemplate):
        """Add a custom book theme template"""
        self.theme_templates[template.name] = template
    
    def generate_books(self, content_filter: Callable[[str], str] = None,
                      min_quality: float = 0.4, max_books: int = 5,
                      **extractor_kwargs) -> List[str]:
        """Generate books from content source"""
        
        # Extract raw content
        print("📥 Extracting content from source...")
        raw_content = self.content_extractor.extract_content(**extractor_kwargs)
        
        if not raw_content:
            print("❌ No content found in source")
            return []
        
        # Process into insights
        insights = self.content_processor.process_raw_content(
            raw_content, content_filter, min_quality
        )
        
        if not insights:
            print("❌ No quality insights found")
            return []
        
        # Create thematic clusters
        clusters = self._create_thematic_clusters(insights)
        
        if not clusters:
            print("❌ No coherent thematic clusters found")
            return []
        
        # Generate books
        generated_books = []
        max_books = min(max_books, len(clusters))
        
        print(f"\n📚 Generating {max_books} books from top clusters...")
        
        for i, cluster in enumerate(clusters[:max_books], 1):
            book = self._generate_book_from_cluster(cluster, i)
            book_path = self._export_book(book)
            generated_books.append(book_path)
        
        print(f"\n🎉 Generated {len(generated_books)} books:")
        for book_path in generated_books:
            print(f"   📚 {Path(book_path).name}")
        
        return generated_books
    
    def _create_thematic_clusters(self, insights: List[ContentInsight]) -> List[ThematicCluster]:
        """Create thematic clusters using theme templates"""
        print("🎯 Creating thematic clusters...")
        
        # Group insights by themes using templates
        theme_groups = defaultdict(list)
        
        for insight in insights:
            # Find best matching theme template
            best_theme = self._find_best_theme_match(insight)
            theme_groups[best_theme].append(insight)
        
        clusters = []
        for theme_name, theme_insights in theme_groups.items():
            if len(theme_insights) < 5:  # Skip small themes
                continue
            
            template = self.theme_templates.get(theme_name)
            if not template:
                continue
            
            # Calculate cluster coherence
            coherence = self._calculate_cluster_coherence(theme_insights)
            
            # Extract primary concepts
            all_concepts = []
            for insight in theme_insights:
                all_concepts.extend(insight.concepts)
            
            concept_counts = Counter(all_concepts)
            primary_concepts = [concept for concept, count in concept_counts.most_common(5)]
            
            cluster = ThematicCluster(
                theme_name=theme_name,
                primary_concepts=primary_concepts,
                insights=sorted(theme_insights, key=lambda x: x.quality_score, reverse=True),
                coherence_score=coherence,
                avg_quality=sum(i.quality_score for i in theme_insights) / len(theme_insights),
                total_words=sum(i.word_count for i in theme_insights),
                narrative_arc=template.narrative_arc
            )
            
            clusters.append(cluster)
        
        # Sort by coherence and quality
        clusters.sort(key=lambda x: (x.coherence_score * x.avg_quality), reverse=True)
        
        print(f"✅ Created {len(clusters)} thematic clusters")
        for cluster in clusters:
            print(f"   📚 {cluster.theme_name}: {len(cluster.insights)} insights, "
                  f"coherence: {cluster.coherence_score:.2f}")
        
        return clusters
    
    def _find_best_theme_match(self, insight: ContentInsight) -> str:
        """Find the best matching theme template for an insight"""
        best_match = 'general'
        best_score = 0.0
        
        content_lower = insight.content.lower()
        
        for theme_name, template in self.theme_templates.items():
            score = 0.0
            
            # Count keyword matches
            for keyword in template.keywords:
                if keyword.lower() in content_lower:
                    score += 1.0
            
            # Boost if theme is already in insight themes
            if theme_name in insight.themes:
                score += 2.0
            
            # Normalize by number of keywords
            if template.keywords:
                score = score / len(template.keywords)
            
            if score > best_score:
                best_score = score
                best_match = theme_name
        
        return best_match
    
    def _calculate_cluster_coherence(self, insights: List[ContentInsight]) -> float:
        """Calculate cluster coherence"""
        if len(insights) < 2:
            return 1.0
        
        # Measure concept overlap
        all_concepts = [set(insight.concepts) for insight in insights]
        
        overlap_scores = []
        for i in range(len(all_concepts)):
            for j in range(i + 1, len(all_concepts)):
                intersection = len(all_concepts[i] & all_concepts[j])
                union = len(all_concepts[i] | all_concepts[j])
                if union > 0:
                    overlap_scores.append(intersection / union)
        
        return sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0.0
    
    def _generate_book_from_cluster(self, cluster: ThematicCluster, book_id: int) -> BookStructure:
        """Generate book structure from cluster"""
        print(f"📖 Generating book {book_id}: {cluster.theme_name}")
        
        template = self.theme_templates.get(cluster.theme_name)
        if not template:
            template = self.theme_templates['consciousness']  # Fallback
        
        # Generate title and subtitle
        title, subtitle = template.title_templates[0]  # Use first template
        
        # Select best insights
        max_insights = min(len(cluster.insights), 100)
        selected_insights = cluster.insights[:max_insights]
        
        # Create chapters using template
        chapters = self._create_chapters_from_template(selected_insights, template)
        
        # Calculate quality metrics
        quality_metrics = {
            'avg_insight_quality': sum(i.quality_score for i in selected_insights) / len(selected_insights),
            'concept_diversity': len(set(concept for insight in selected_insights 
                                       for concept in insight.concepts)),
            'thematic_coherence': sum(ch.coherence_score for ch in chapters) / len(chapters),
            'narrative_flow': cluster.coherence_score
        }
        
        book = BookStructure(
            title=title,
            subtitle=subtitle,
            theme=cluster.theme_name,
            insights=selected_insights,
            chapters=chapters,
            total_words=sum(insight.word_count for insight in selected_insights),
            quality_metrics=quality_metrics,
            narrative_summary=cluster.narrative_arc
        )
        
        return book
    
    def _create_chapters_from_template(self, insights: List[ContentInsight], 
                                     template: BookThemeTemplate) -> List[ChapterStructure]:
        """Create chapters using theme template"""
        # Determine number of chapters based on content and template
        num_chapters = min(len(template.chapter_templates), max(3, len(insights) // 15))
        
        chapters = []
        insights_per_chapter = len(insights) // num_chapters
        
        # Sort insights by complexity for progression
        sorted_insights = sorted(insights, key=lambda x: x.complexity_level)
        
        for i in range(num_chapters):
            chapter_num = i + 1
            start_idx = i * insights_per_chapter
            
            if i == num_chapters - 1:
                chapter_insights = sorted_insights[start_idx:]
            else:
                chapter_insights = sorted_insights[start_idx:start_idx + insights_per_chapter]
            
            # Get chapter title from template
            if chapter_num in template.chapter_templates:
                chapter_title = template.chapter_templates[chapter_num][0]
            else:
                chapter_title = f"Chapter {chapter_num}: Advanced Exploration"
            
            # Create sections
            sections = self._create_chapter_sections(chapter_insights)
            
            # Calculate coherence
            coherence = self._calculate_cluster_coherence(chapter_insights)
            
            chapter = ChapterStructure(
                number=chapter_num,
                title=chapter_title,
                theme=template.name,
                insights=chapter_insights,
                sections=sections,
                word_count=sum(insight.word_count for insight in chapter_insights),
                coherence_score=coherence
            )
            
            chapters.append(chapter)
        
        return chapters
    
    def _create_chapter_sections(self, insights: List[ContentInsight]) -> List[SectionStructure]:
        """Create sections within a chapter"""
        num_sections = min(4, max(2, len(insights) // 6))
        insights_per_section = len(insights) // num_sections
        
        sections = []
        for i in range(num_sections):
            start_idx = i * insights_per_section
            if i == num_sections - 1:
                section_insights = insights[start_idx:]
            else:
                section_insights = insights[start_idx:start_idx + insights_per_section]
            
            section = SectionStructure(
                title=f"Section {i + 1}",
                insights=section_insights,
                transition_text=f"This section explores {len(section_insights)} related insights."
            )
            
            sections.append(section)
        
        return sections
    
    def _export_book(self, book: BookStructure) -> str:
        """Export book to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"universal_{book.theme}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Title page
            f.write(f"# {book.title}\n")
            f.write(f"## {book.subtitle}\n\n")
            f.write(f"*Generated from {len(book.insights)} insights*\n")
            f.write(f"*{book.total_words:,} words*\n\n")
            
            # Quality metrics
            f.write("### Quality Metrics\n")
            for metric, value in book.quality_metrics.items():
                f.write(f"- **{metric.replace('_', ' ').title()}:** {value:.2f}\n")
            f.write(f"\n### Overview\n{book.narrative_summary}\n\n")
            
            f.write("---\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            for chapter in book.chapters:
                f.write(f"{chapter.number}. {chapter.title} ({chapter.word_count:,} words)\n")
            f.write("\n---\n\n")
            
            # Chapters
            for chapter in book.chapters:
                f.write(f"# {chapter.title}\n\n")
                
                for section in chapter.sections:
                    f.write(f"## {section.title}\n\n")
                    f.write(f"{section.transition_text}\n\n")
                    
                    for insight in section.insights:
                        f.write(f"### From: {insight.source_title}\n")
                        f.write(f"*Quality: {insight.quality_score:.2f} | "
                               f"Complexity: {insight.complexity_level}/5 | "
                               f"Words: {insight.word_count}*\n\n")
                        f.write(f"{insight.content}\n\n")
                        f.write("---\n\n")
                
                f.write("\n\n")
        
        print(f"✅ Book exported: {filepath.name}")
        return str(filepath)

def main():
    parser = argparse.ArgumentParser(description="Universal Book Generator")
    parser.add_argument('--source-type', choices=['notebooks', 'conversations', 'files'],
                       default='notebooks', help='Content source type')
    parser.add_argument('--database-url', help='Database URL for database sources')
    parser.add_argument('--file-path', help='Base path for file sources')
    parser.add_argument('--min-quality', type=float, default=0.4,
                       help='Minimum quality threshold')
    parser.add_argument('--max-books', type=int, default=3,
                       help='Maximum books to generate')
    parser.add_argument('--gizmo-id', help='Gizmo ID for conversation filtering')
    parser.add_argument('--author', help='Author for conversation filtering')
    
    args = parser.parse_args()
    
    try:
        # Create appropriate content extractor
        if args.source_type == 'notebooks':
            database_url = args.database_url or "postgresql://tem@localhost/humanizer_archive"
            extractor = NotebookTranscriptExtractor(database_url)
            extractor_kwargs = {}
        elif args.source_type == 'conversations':
            database_url = args.database_url or "postgresql://tem@localhost/humanizer_archive"
            extractor = ConversationExtractor(database_url)
            extractor_kwargs = {
                'gizmo_id': args.gizmo_id,
                'author': args.author,
                'min_length': 200
            }
        elif args.source_type == 'files':
            file_path = args.file_path or "."
            extractor = FileExtractor(file_path)
            extractor_kwargs = {
                'file_patterns': ['*.md', '*.txt'],
                'recursive': True
            }
        else:
            print(f"❌ Unknown source type: {args.source_type}")
            return
        
        # Create generator and generate books
        generator = UniversalBookGenerator(extractor)
        book_paths = generator.generate_books(
            min_quality=args.min_quality,
            max_books=args.max_books,
            **extractor_kwargs
        )
        
        if book_paths:
            print(f"\n🎉 Successfully generated {len(book_paths)} books!")
            print(f"📂 Books saved in: {generator.output_dir}")
        else:
            print("❌ No books were generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()