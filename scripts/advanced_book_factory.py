#!/usr/bin/env python3
"""
Advanced Book Factory
Sophisticated, general-purpose book generation with semantic clustering and AI analysis
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter, defaultdict
import argparse
import numpy as np
from dataclasses import dataclass
import hashlib

@dataclass
class ContentInsight:
    """Structured representation of a content insight"""
    id: str
    source_id: str
    source_title: str
    content: str
    timestamp: Optional[str]
    author: str
    word_count: int
    quality_score: float
    semantic_embedding: Optional[List[float]]
    themes: List[str]
    concepts: List[str]
    emotional_tone: str
    complexity_level: int
    uniqueness_hash: str

@dataclass
class ThematicCluster:
    """A cluster of related insights around a theme"""
    theme_name: str
    primary_concepts: List[str]
    insights: List[ContentInsight]
    coherence_score: float
    avg_quality: float
    total_words: int
    narrative_arc: str

@dataclass
class BookStructure:
    """Complete book structure with chapters and metadata"""
    title: str
    subtitle: str
    theme: str
    insights: List[ContentInsight]
    chapters: List['ChapterStructure']
    total_words: int
    quality_metrics: Dict[str, float]
    narrative_summary: str

@dataclass 
class ChapterStructure:
    """Individual chapter structure"""
    number: int
    title: str
    theme: str
    insights: List[ContentInsight]
    sections: List['SectionStructure']
    word_count: int
    coherence_score: float

@dataclass
class SectionStructure:
    """Section within a chapter"""
    title: str
    insights: List[ContentInsight]
    transition_text: str
    
class AdvancedSemanticAnalyzer:
    """Advanced semantic analysis for content clustering"""
    
    def __init__(self):
        # Sophisticated concept hierarchies
        self.concept_hierarchies = {
            'consciousness': {
                'subconcepts': ['awareness', 'perception', 'cognition', 'sentience', 'mindfulness'],
                'weight': 1.0,
                'complexity': 4
            },
            'being': {
                'subconcepts': ['existence', 'ontology', 'presence', 'reality', 'essence'],
                'weight': 0.9,
                'complexity': 4
            },
            'experience': {
                'subconcepts': ['perception', 'sensation', 'feeling', 'qualia', 'phenomenology'],
                'weight': 0.8,
                'complexity': 3
            },
            'self': {
                'subconcepts': ['identity', 'ego', 'personality', 'individuality', 'selfhood'],
                'weight': 0.7,
                'complexity': 3
            },
            'inquiry': {
                'subconcepts': ['questioning', 'investigation', 'exploration', 'methodology', 'analysis'],
                'weight': 0.6,
                'complexity': 2
            },
            'practice': {
                'subconcepts': ['meditation', 'contemplation', 'discipline', 'method', 'technique'],
                'weight': 0.5,
                'complexity': 2
            },
            'time': {
                'subconcepts': ['temporality', 'duration', 'sequence', 'moment', 'eternity'],
                'weight': 0.8,
                'complexity': 4
            },
            'unity': {
                'subconcepts': ['connection', 'integration', 'wholeness', 'oneness', 'harmony'],
                'weight': 0.7,
                'complexity': 3
            }
        }
        
        # Emotional tone patterns
        self.emotional_patterns = {
            'contemplative': [r'\bi wonder\b', r'\bperhaps\b', r'\bmight be\b', r'\bseems?\b'],
            'analytical': [r'\btherefore\b', r'\bbecause\b', r'\bif.*then\b', r'\bconsequently\b'],
            'experiential': [r'\bi feel\b', r'\bi sense\b', r'\bi experience\b', r'\bmy.*feels?\b'],
            'philosophical': [r'\bwhat is\b', r'\bthe nature of\b', r'\bfundamental\b', r'\bessence\b'],
            'practical': [r'\bhow to\b', r'\bmethod\b', r'\btechnique\b', r'\bapproach\b'],
            'mystical': [r'\btranscend\b', r'\bdivine\b', r'\bsacred\b', r'\binfinite\b']
        }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Comprehensive semantic analysis of content"""
        analysis = {
            'concepts': self._extract_concepts(content),
            'emotional_tone': self._detect_emotional_tone(content),
            'complexity_level': self._assess_complexity(content),
            'themes': self._identify_themes(content),
            'narrative_elements': self._extract_narrative_elements(content),
            'philosophical_depth': self._assess_philosophical_depth(content)
        }
        return analysis
    
    def _extract_concepts(self, content: str) -> List[Dict[str, Any]]:
        """Extract philosophical concepts with confidence scores"""
        content_lower = content.lower()
        concepts = []
        
        for concept, info in self.concept_hierarchies.items():
            confidence = 0.0
            
            # Direct concept match
            if concept in content_lower:
                confidence += info['weight']
            
            # Subconcept matches
            subconcept_matches = sum(1 for sub in info['subconcepts'] 
                                   if sub in content_lower)
            confidence += (subconcept_matches / len(info['subconcepts'])) * info['weight'] * 0.7
            
            if confidence > 0.1:  # Threshold for inclusion
                concepts.append({
                    'concept': concept,
                    'confidence': min(confidence, 1.0),
                    'complexity': info['complexity'],
                    'subconcepts_found': [sub for sub in info['subconcepts'] 
                                        if sub in content_lower]
                })
        
        return sorted(concepts, key=lambda x: x['confidence'], reverse=True)
    
    def _detect_emotional_tone(self, content: str) -> str:
        """Detect the primary emotional tone of the content"""
        content_lower = content.lower()
        tone_scores = {}
        
        for tone, patterns in self.emotional_patterns.items():
            score = sum(len(re.findall(pattern, content_lower, re.IGNORECASE)) 
                       for pattern in patterns)
            if score > 0:
                tone_scores[tone] = score
        
        if not tone_scores:
            return 'neutral'
        
        return max(tone_scores.items(), key=lambda x: x[1])[0]
    
    def _assess_complexity(self, content: str) -> int:
        """Assess conceptual complexity (1-5 scale)"""
        complexity_indicators = {
            'abstract_terms': len(re.findall(r'\b(abstract|concept|idea|notion|principle)\b', 
                                           content, re.IGNORECASE)),
            'conditional_logic': len(re.findall(r'\b(if|when|because|therefore|thus|hence)\b',
                                              content, re.IGNORECASE)),
            'philosophical_terms': len(re.findall(r'\b(ontology|epistemology|phenomenology|metaphysics)\b',
                                                content, re.IGNORECASE)),
            'sentence_complexity': len([s for s in re.split(r'[.!?]', content) 
                                      if len(s.split()) > 15])
        }
        
        total_complexity = sum(complexity_indicators.values())
        word_count = len(content.split())
        
        if word_count == 0:
            return 1
        
        complexity_ratio = total_complexity / word_count
        
        if complexity_ratio > 0.15:
            return 5
        elif complexity_ratio > 0.10:
            return 4
        elif complexity_ratio > 0.06:
            return 3
        elif complexity_ratio > 0.03:
            return 2
        else:
            return 1
    
    def _identify_themes(self, content: str) -> List[str]:
        """Identify thematic categories for the content"""
        concepts = self._extract_concepts(content)
        
        # Map concepts to book themes
        theme_mapping = {
            'consciousness': ['consciousness', 'awareness', 'mind'],
            'experience': ['experience', 'perception', 'sensation'],
            'self': ['self', 'identity', 'ego'],
            'inquiry': ['inquiry', 'philosophy', 'method'],
            'practice': ['practice', 'meditation', 'spiritual'],
            'time_space': ['time', 'space', 'reality'],
            'unity': ['unity', 'connection', 'wholeness']
        }
        
        themes = []
        for theme, keywords in theme_mapping.items():
            if any(concept['concept'] in keywords for concept in concepts):
                themes.append(theme)
        
        return themes or ['general']
    
    def _extract_narrative_elements(self, content: str) -> Dict[str, Any]:
        """Extract narrative structure elements"""
        return {
            'has_questions': '?' in content,
            'has_examples': bool(re.search(r'\b(for example|such as|like|instance)\b', 
                                         content, re.IGNORECASE)),
            'has_conclusions': bool(re.search(r'\b(therefore|thus|in conclusion|finally)\b',
                                            content, re.IGNORECASE)),
            'personal_reflection': bool(re.search(r'\b(I feel|I think|I believe|my sense)\b',
                                                content, re.IGNORECASE))
        }
    
    def _assess_philosophical_depth(self, content: str) -> float:
        """Assess philosophical depth (0.0-1.0)"""
        depth_indicators = {
            'fundamental_questions': len(re.findall(r'\b(what is|why do|how can|what does.*mean)\b',
                                                  content, re.IGNORECASE)),
            'abstract_reasoning': len(re.findall(r'\b(essence|nature|fundamental|underlying)\b',
                                               content, re.IGNORECASE)),
            'philosophical_schools': len(re.findall(r'\b(phenomenology|existential|buddhist|stoic)\b',
                                                  content, re.IGNORECASE)),
            'critical_thinking': len(re.findall(r'\b(question|doubt|examine|analyze|consider)\b',
                                              content, re.IGNORECASE))
        }
        
        total_depth = sum(depth_indicators.values())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        return min(total_depth / word_count * 10, 1.0)  # Scale to 0-1

class AdvancedBookFactory:
    """Advanced book factory with sophisticated clustering and generation"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://tem@localhost/humanizer_archive"
        self.database_url = database_url
        self.analyzer = AdvancedSemanticAnalyzer()
        self.output_dir = Path("advanced_books")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🧠 Advanced Book Factory")
        print("=" * 50)
        print("🎯 Sophisticated semantic clustering and book generation")
    
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def extract_and_analyze_insights(self, min_quality: float = 0.3) -> List[ContentInsight]:
        """Extract and perform deep analysis on all insights"""
        print("📖 Extracting and analyzing notebook insights...")
        
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
            
            raw_messages = cursor.fetchall()
        
        insights = []
        processed = 0
        
        print(f"📊 Processing {len(raw_messages)} potential insights...")
        
        for message in raw_messages:
            processed += 1
            if processed % 50 == 0:
                print(f"  Analyzed {processed}/{len(raw_messages)} messages...")
            
            # Extract handwritten content
            content = self._extract_handwritten_content(message['body_text'])
            if not content or len(content) < 100:
                continue
            
            # Perform semantic analysis
            analysis = self.analyzer.analyze_content(content)
            
            # Calculate quality score
            quality_score = self._calculate_advanced_quality_score(content, analysis)
            
            if quality_score < min_quality:
                continue
            
            # Create content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
            
            insight = ContentInsight(
                id=f"insight_{message['id']}",
                source_id=str(message['conversation_id']),
                source_title=message['conversation_title'],
                content=content,
                timestamp=message['timestamp'].isoformat() if message['timestamp'] else None,
                author=message['author'],
                word_count=len(content.split()),
                quality_score=quality_score,
                semantic_embedding=None,  # Could add vector embeddings here
                themes=analysis['themes'],
                concepts=[c['concept'] for c in analysis['concepts']],
                emotional_tone=analysis['emotional_tone'],
                complexity_level=analysis['complexity_level'],
                uniqueness_hash=content_hash
            )
            
            insights.append(insight)
        
        # Remove duplicates based on content similarity
        insights = self._deduplicate_insights(insights)
        
        print(f"✅ Extracted {len(insights)} high-quality unique insights")
        return insights
    
    def _extract_handwritten_content(self, body_text: str) -> str:
        """Extract handwritten content with better filtering"""
        patterns = [
            r'```markdown\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                
                # Filter out obvious non-philosophical content
                if self._is_philosophical_content(content):
                    return content
        
        return ""
    
    def _is_philosophical_content(self, content: str) -> bool:
        """Determine if content is philosophical/reflective"""
        content_lower = content.lower()
        
        # Exclude patterns
        exclude_patterns = [
            r'"[^"]*".*"[^"]*"',  # Dialogue patterns
            r'tidoom|dreelge',     # Sci-fi terms
            r'crystal|instrument', # Specific objects
            r'three hours apart',  # Specific temporal references
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, content_lower):
                return False
        
        # Include patterns
        philosophical_indicators = [
            'consciousness', 'awareness', 'being', 'existence', 'reality',
            'experience', 'perception', 'feel', 'think', 'understand',
            'question', 'wonder', 'perhaps', 'sense', 'meaning'
        ]
        
        matches = sum(1 for indicator in philosophical_indicators 
                     if indicator in content_lower)
        
        return matches >= 2 and len(content.split()) >= 20
    
    def _calculate_advanced_quality_score(self, content: str, analysis: Dict[str, Any]) -> float:
        """Advanced quality scoring algorithm"""
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
        """Remove duplicate or very similar insights"""
        unique_insights = []
        seen_hashes = set()
        
        # Sort by quality score (keep highest quality versions)
        insights_sorted = sorted(insights, key=lambda x: x.quality_score, reverse=True)
        
        for insight in insights_sorted:
            # Simple deduplication by hash
            if insight.uniqueness_hash not in seen_hashes:
                unique_insights.append(insight)
                seen_hashes.add(insight.uniqueness_hash)
        
        return unique_insights
    
    def create_thematic_clusters(self, insights: List[ContentInsight]) -> List[ThematicCluster]:
        """Create sophisticated thematic clusters"""
        print("🎯 Creating thematic clusters...")
        
        # Group insights by primary themes
        theme_groups = defaultdict(list)
        for insight in insights:
            primary_theme = insight.themes[0] if insight.themes else 'general'
            theme_groups[primary_theme].append(insight)
        
        clusters = []
        for theme, theme_insights in theme_groups.items():
            if len(theme_insights) < 5:  # Skip small themes
                continue
            
            # Calculate cluster coherence
            coherence = self._calculate_cluster_coherence(theme_insights)
            
            # Extract primary concepts
            all_concepts = []
            for insight in theme_insights:
                all_concepts.extend(insight.concepts)
            
            concept_counts = Counter(all_concepts)
            primary_concepts = [concept for concept, count in concept_counts.most_common(5)]
            
            # Generate narrative arc
            narrative_arc = self._generate_narrative_arc(theme, theme_insights)
            
            cluster = ThematicCluster(
                theme_name=theme,
                primary_concepts=primary_concepts,
                insights=sorted(theme_insights, key=lambda x: x.quality_score, reverse=True),
                coherence_score=coherence,
                avg_quality=sum(i.quality_score for i in theme_insights) / len(theme_insights),
                total_words=sum(i.word_count for i in theme_insights),
                narrative_arc=narrative_arc
            )
            
            clusters.append(cluster)
        
        # Sort by coherence and quality
        clusters.sort(key=lambda x: (x.coherence_score * x.avg_quality), reverse=True)
        
        print(f"✅ Created {len(clusters)} thematic clusters")
        for cluster in clusters:
            print(f"   📚 {cluster.theme_name}: {len(cluster.insights)} insights, "
                  f"coherence: {cluster.coherence_score:.2f}")
        
        return clusters
    
    def _calculate_cluster_coherence(self, insights: List[ContentInsight]) -> float:
        """Calculate how coherent a cluster of insights is"""
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
    
    def _generate_narrative_arc(self, theme: str, insights: List[ContentInsight]) -> str:
        """Generate a narrative arc description for the theme"""
        theme_arcs = {
            'consciousness': "A journey from basic awareness through layers of consciousness to deep understanding",
            'experience': "Exploring the full spectrum of human experience from sensation to meaning",
            'self': "An inquiry into personal identity from ego through authentic self to transcendence",
            'inquiry': "The development of philosophical method from questioning to wisdom",
            'practice': "The path from initial spiritual practice to integrated living",
            'time_space': "Understanding reality from temporal experience to cosmic perspective",
            'unity': "Recognition of interconnection from individual to universal consciousness"
        }
        
        return theme_arcs.get(theme, f"An exploration of {theme} through personal insight and reflection")
    
    def generate_book_from_cluster(self, cluster: ThematicCluster, book_id: int) -> BookStructure:
        """Generate a sophisticated book structure from a thematic cluster"""
        print(f"📖 Generating book {book_id}: {cluster.theme_name}")
        
        # Generate book title and subtitle
        title, subtitle = self._generate_book_titles(cluster)
        
        # Select best insights (limit to reasonable book size)
        max_insights = min(len(cluster.insights), 120)
        selected_insights = cluster.insights[:max_insights]
        
        # Create chapter structure
        chapters = self._create_sophisticated_chapters(selected_insights, cluster)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_book_quality_metrics(selected_insights, chapters)
        
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
    
    def _generate_book_titles(self, cluster: ThematicCluster) -> Tuple[str, str]:
        """Generate sophisticated book titles"""
        title_templates = {
            'consciousness': [
                ("The Nature of Consciousness", "Explorations in Awareness and Being"),
                ("Conscious Being", "An Inquiry into Awareness"),
                ("The Awakening Mind", "Studies in Consciousness")
            ],
            'experience': [
                ("The Art of Experience", "Perception, Sensation, and Meaning"),
                ("Living Experience", "The Dance of Perception and Reality"),
                ("Experience and Understanding", "How We Know What We Know")
            ],
            'self': [
                ("The Question of Self", "Identity, Authenticity, and Being"),
                ("Knowing the Self", "A Journey Beyond Ego"),
                ("The Authentic Self", "Personal Truth and Identity")
            ],
            'inquiry': [
                ("The Art of Inquiry", "Methods for Understanding"),
                ("Philosophical Practice", "The Way of Questioning"),
                ("The Inquiring Mind", "Paths to Wisdom")
            ],
            'practice': [
                ("Contemplative Practice", "Wisdom in Daily Life"),
                ("The Way of Practice", "Spiritual Development and Growth"),
                ("Living Wisdom", "Practice and Understanding")
            ],
            'time_space': [
                ("Time, Space, and Reality", "The Fabric of Existence"),
                ("The Nature of Reality", "Time, Space, and Being"),
                ("Cosmic Perspective", "Understanding Time and Space")
            ],
            'unity': [
                ("Unity and Connection", "The Web of Being"),
                ("Interconnected Being", "Finding Unity in Diversity"),
                ("The Connected Self", "Relationships and Wholeness")
            ]
        }
        
        templates = title_templates.get(cluster.theme_name, [
            (f"Reflections on {cluster.theme_name.title()}", "Personal Insights and Understanding")
        ])
        
        # Choose based on cluster characteristics
        if cluster.coherence_score > 0.7:
            return templates[0]  # Most sophisticated
        elif len(templates) > 1:
            return templates[1]  # Alternative
        else:
            return templates[0]
    
    def _create_sophisticated_chapters(self, insights: List[ContentInsight], 
                                     cluster: ThematicCluster) -> List[ChapterStructure]:
        """Create sophisticated chapter structure with unique themes"""
        # Determine optimal number of chapters
        total_insights = len(insights)
        if total_insights <= 30:
            num_chapters = 3
        elif total_insights <= 60:
            num_chapters = 4
        elif total_insights <= 90:
            num_chapters = 5
        else:
            num_chapters = 6
        
        # Group insights by complexity and concepts for chapter themes
        chapters = []
        insights_per_chapter = total_insights // num_chapters
        
        # Sort insights by complexity for natural progression
        sorted_insights = sorted(insights, key=lambda x: x.complexity_level)
        
        for i in range(num_chapters):
            start_idx = i * insights_per_chapter
            if i == num_chapters - 1:
                chapter_insights = sorted_insights[start_idx:]
            else:
                chapter_insights = sorted_insights[start_idx:start_idx + insights_per_chapter]
            
            # Generate unique chapter title based on dominant concepts
            chapter_title = self._generate_chapter_title(i + 1, chapter_insights, cluster.theme_name)
            chapter_theme = self._identify_chapter_theme(chapter_insights)
            
            # Create sections within chapter
            sections = self._create_chapter_sections(chapter_insights)
            
            # Calculate coherence
            coherence = self._calculate_cluster_coherence(chapter_insights)
            
            chapter = ChapterStructure(
                number=i + 1,
                title=chapter_title,
                theme=chapter_theme,
                insights=chapter_insights,
                sections=sections,
                word_count=sum(insight.word_count for insight in chapter_insights),
                coherence_score=coherence
            )
            
            chapters.append(chapter)
        
        return chapters
    
    def _generate_chapter_title(self, chapter_num: int, insights: List[ContentInsight], 
                              book_theme: str) -> str:
        """Generate unique, meaningful chapter titles"""
        # Analyze dominant concepts in this chapter
        all_concepts = []
        for insight in insights:
            all_concepts.extend(insight.concepts)
        
        concept_counts = Counter(all_concepts)
        top_concepts = [concept for concept, count in concept_counts.most_common(3)]
        
        # Analyze complexity progression
        avg_complexity = sum(insight.complexity_level for insight in insights) / len(insights)
        
        # Generate contextual title based on theme and concepts
        title_generators = {
            'consciousness': {
                1: ("Foundations of Awareness", "The Nature of Consciousness", "Awakening to Being"),
                2: ("Layers of Experience", "The Structure of Awareness", "Consciousness in Action"),
                3: ("Deep Understanding", "Advanced Awareness", "The Integrated Self"),
                4: ("Transcendent Awareness", "Beyond Individual Consciousness", "Unity of Being"),
                5: ("Wisdom and Integration", "Living Consciousness", "Embodied Awareness"),
                6: ("The Complete Picture", "Consciousness as Reality", "Ultimate Understanding")
            },
            'experience': {
                1: ("Basic Experience", "The World of Sensation", "Primary Perception"),
                2: ("Complex Experience", "Meaning in Experience", "The Interpreted World"),
                3: ("Deep Experience", "Layers of Understanding", "The Significance of Experience"),
                4: ("Transformative Experience", "Experience as Teacher", "Learning from Life"),
                5: ("Integrated Experience", "Wisdom Through Experience", "The Experienced Self"),
                6: ("Transcendent Experience", "Beyond Personal Experience", "Universal Patterns")
            },
            'self': {
                1: ("The Question of Self", "Who Am I?", "The Search for Identity"),
                2: ("Beyond Ego", "The Authentic Self", "True Identity"),
                3: ("Self and Others", "Relational Identity", "The Social Self"),
                4: ("The Evolving Self", "Growth and Change", "Transformation of Identity"),
                5: ("The Integrated Self", "Wholeness and Authenticity", "The Complete Person"),
                6: ("The Transcendent Self", "Beyond Personal Identity", "Universal Being")
            }
        }
        
        # Get chapter titles for this theme
        theme_titles = title_generators.get(book_theme, {})
        
        if chapter_num in theme_titles:
            # Choose title based on complexity and concepts
            if avg_complexity >= 4 and 'consciousness' in top_concepts:
                return theme_titles[chapter_num][2]  # Most advanced
            elif avg_complexity >= 3:
                return theme_titles[chapter_num][1]  # Medium
            else:
                return theme_titles[chapter_num][0]  # Basic
        
        # Fallback: generate from concepts
        if top_concepts:
            primary_concept = top_concepts[0].title()
            return f"Chapter {chapter_num}: {primary_concept} and Understanding"
        
        return f"Chapter {chapter_num}: Explorations"
    
    def _identify_chapter_theme(self, insights: List[ContentInsight]) -> str:
        """Identify the dominant theme of a chapter"""
        all_themes = []
        for insight in insights:
            all_themes.extend(insight.themes)
        
        if not all_themes:
            return 'general'
        
        theme_counts = Counter(all_themes)
        return theme_counts.most_common(1)[0][0]
    
    def _create_chapter_sections(self, insights: List[ContentInsight]) -> List[SectionStructure]:
        """Create sections within a chapter"""
        # Group insights into 2-4 sections per chapter
        num_sections = min(4, max(2, len(insights) // 8))
        insights_per_section = len(insights) // num_sections
        
        sections = []
        for i in range(num_sections):
            start_idx = i * insights_per_section
            if i == num_sections - 1:
                section_insights = insights[start_idx:]
            else:
                section_insights = insights[start_idx:start_idx + insights_per_section]
            
            # Generate section title
            section_title = f"Section {i + 1}"
            
            # Generate transition text
            transition_text = self._generate_section_transition(i, section_insights)
            
            section = SectionStructure(
                title=section_title,
                insights=section_insights,
                transition_text=transition_text
            )
            
            sections.append(section)
        
        return sections
    
    def _generate_section_transition(self, section_num: int, insights: List[ContentInsight]) -> str:
        """Generate transition text for sections"""
        if section_num == 0:
            return "These initial insights establish the foundation for our exploration."
        
        # Analyze dominant emotional tone
        tones = [insight.emotional_tone for insight in insights]
        dominant_tone = Counter(tones).most_common(1)[0][0] if tones else 'contemplative'
        
        transitions = {
            'contemplative': "Building on these reflections, we turn to deeper questions.",
            'analytical': "These analytical insights lead us to examine the underlying structures.",
            'experiential': "From these lived experiences, we can draw broader insights.",
            'philosophical': "These philosophical foundations support our continued inquiry.",
            'practical': "These practical insights guide our understanding forward.",
            'mystical': "These transcendent insights open new dimensions of understanding."
        }
        
        return transitions.get(dominant_tone, "Continuing our exploration, we encounter new dimensions.")
    
    def _calculate_book_quality_metrics(self, insights: List[ContentInsight], 
                                      chapters: List[ChapterStructure]) -> Dict[str, float]:
        """Calculate comprehensive quality metrics for the book"""
        return {
            'avg_insight_quality': sum(i.quality_score for i in insights) / len(insights),
            'concept_diversity': len(set(concept for insight in insights 
                                       for concept in insight.concepts)),
            'complexity_progression': self._calculate_complexity_progression(chapters),
            'thematic_coherence': sum(ch.coherence_score for ch in chapters) / len(chapters),
            'narrative_flow': self._calculate_narrative_flow(chapters)
        }
    
    def _calculate_complexity_progression(self, chapters: List[ChapterStructure]) -> float:
        """Calculate how well complexity progresses through chapters"""
        if len(chapters) < 2:
            return 1.0
        
        chapter_complexities = []
        for chapter in chapters:
            avg_complexity = sum(insight.complexity_level for insight in chapter.insights) / len(chapter.insights)
            chapter_complexities.append(avg_complexity)
        
        # Measure if complexity generally increases
        progression_score = 0.0
        for i in range(1, len(chapter_complexities)):
            if chapter_complexities[i] >= chapter_complexities[i-1]:
                progression_score += 1.0
        
        return progression_score / (len(chapter_complexities) - 1)
    
    def _calculate_narrative_flow(self, chapters: List[ChapterStructure]) -> float:
        """Calculate narrative flow quality"""
        # Simplified: average coherence across chapters
        return sum(ch.coherence_score for ch in chapters) / len(chapters)
    
    def export_advanced_book(self, book: BookStructure) -> str:
        """Export book with sophisticated formatting"""
        filename = f"advanced_{book.theme}_{book.title.lower().replace(' ', '_')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Title page
            f.write(f"# {book.title}\n")
            f.write(f"## {book.subtitle}\n\n")
            f.write(f"*Generated from {len(book.insights)} carefully selected insights*\n")
            f.write(f"*{book.total_words:,} words of philosophical exploration*\n\n")
            
            # Quality metrics
            f.write("### Book Quality Metrics\n")
            f.write(f"- **Average Insight Quality:** {book.quality_metrics['avg_insight_quality']:.2f}\n")
            f.write(f"- **Concept Diversity:** {book.quality_metrics['concept_diversity']} unique concepts\n")
            f.write(f"- **Thematic Coherence:** {book.quality_metrics['thematic_coherence']:.2f}\n")
            f.write(f"- **Narrative Flow:** {book.quality_metrics['narrative_flow']:.2f}\n\n")
            
            # Narrative summary
            f.write("### Book Overview\n")
            f.write(f"{book.narrative_summary}\n\n")
            
            f.write("---\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            for chapter in book.chapters:
                f.write(f"{chapter.number}. {chapter.title} ({chapter.word_count:,} words)\n")
            f.write("\n---\n\n")
            
            # Chapters
            for chapter in book.chapters:
                f.write(f"# {chapter.title}\n\n")
                f.write(f"*Theme: {chapter.theme} | {len(chapter.insights)} insights | "
                       f"Coherence: {chapter.coherence_score:.2f}*\n\n")
                
                # Chapter introduction
                f.write("## Chapter Introduction\n\n")
                f.write(f"This chapter explores {chapter.theme} through {len(chapter.insights)} "
                       f"carefully selected insights. The material progresses from foundational "
                       f"concepts to deeper understanding.\n\n")
                
                # Sections
                for section in chapter.sections:
                    f.write(f"## {section.title}\n\n")
                    f.write(f"{section.transition_text}\n\n")
                    
                    for insight in section.insights:
                        f.write(f"### From: {insight.source_title}\n")
                        f.write(f"*Quality: {insight.quality_score:.2f} | "
                               f"Complexity: {insight.complexity_level}/5 | "
                               f"Tone: {insight.emotional_tone} | "
                               f"Words: {insight.word_count}*\n\n")
                        
                        # Add concept tags
                        if insight.concepts:
                            concepts_str = ", ".join(insight.concepts[:5])
                            f.write(f"**Key Concepts:** {concepts_str}\n\n")
                        
                        f.write(f"{insight.content}\n\n")
                        f.write("---\n\n")
                
                f.write("\n\n")
        
        print(f"✅ Advanced book exported: {filepath.name}")
        return str(filepath)

def main():
    parser = argparse.ArgumentParser(description="Advanced Book Factory - Sophisticated book generation")
    parser.add_argument('--min-quality', type=float, default=0.4,
                       help='Minimum quality threshold (0.0-1.0)')
    parser.add_argument('--max-books', type=int, default=5,
                       help='Maximum number of books to generate')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze content, don\'t generate books')
    
    args = parser.parse_args()
    
    try:
        factory = AdvancedBookFactory()
        
        # Extract and analyze insights
        insights = factory.extract_and_analyze_insights(args.min_quality)
        
        if not insights:
            print("❌ No insights found meeting quality threshold")
            return
        
        # Create thematic clusters
        clusters = factory.create_thematic_clusters(insights)
        
        if args.analyze_only:
            print(f"\n📊 Analysis Complete:")
            print(f"  📖 {len(insights)} quality insights extracted")
            print(f"  🎯 {len(clusters)} thematic clusters identified")
            for cluster in clusters:
                print(f"    • {cluster.theme_name}: {len(cluster.insights)} insights, "
                      f"coherence {cluster.coherence_score:.2f}")
            return
        
        # Generate books
        generated_books = []
        max_books = min(args.max_books, len(clusters))
        
        print(f"\n📚 Generating {max_books} books from top clusters...")
        
        for i, cluster in enumerate(clusters[:max_books], 1):
            book = factory.generate_book_from_cluster(cluster, i)
            book_path = factory.export_advanced_book(book)
            generated_books.append(book_path)
        
        print(f"\n🎉 Generated {len(generated_books)} advanced books:")
        for book_path in generated_books:
            print(f"   📚 {Path(book_path).name}")
        
        print(f"\n📂 Books saved in: {factory.output_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()