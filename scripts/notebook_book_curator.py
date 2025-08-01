#!/usr/bin/env python3
"""
Notebook Book Curator
Agent-assisted system for organizing handwritten notebook transcripts into a coherent book structure
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from dataclasses import dataclass

@dataclass
class NotebookInsight:
    """Structure for individual notebook insights"""
    id: str
    conversation_id: int
    conversation_title: str
    content: str
    timestamp: datetime
    word_count: int
    philosophical_concepts: List[str]
    key_phrases: List[str]
    emotional_tone: str
    depth_score: float
    themes: List[str]

@dataclass
class ThematicCluster:
    """Structure for thematic clusters"""
    theme_name: str
    insights: List[NotebookInsight]
    central_concepts: List[str]
    narrative_arc: str
    coherence_score: float
    word_count: int

class NotebookBookCurator:
    """Agent-assisted curator for organizing notebook insights into book structure"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://tem@localhost/humanizer_archive"
        self.database_url = database_url
        
        print("📚 Notebook Book Curator")
        print("========================")
        print("Agent-assisted book structure generation from handwritten insights")
        
        # Initialize analysis components
        self.philosophical_terms = [
            'consciousness', 'being', 'existence', 'reality', 'awareness', 'experience',
            'phenomenology', 'ontology', 'epistemology', 'metaphysics', 'subjective', 
            'objective', 'perception', 'contemplation', 'meditation', 'zen', 'tao',
            'ego', 'self', 'identity', 'agency', 'freedom', 'liberation', 'awakening',
            'truth', 'wisdom', 'understanding', 'insight', 'realization', 'enlightenment',
            'mind', 'thought', 'feeling', 'emotion', 'intuition', 'reason', 'logic',
            'universe', 'cosmos', 'nature', 'energy', 'vibration', 'interconnection',
            'interdependence', 'wholeness', 'unity', 'duality', 'nonduality'
        ]
        
        self.narrative_markers = [
            'first', 'initially', 'beginning', 'start', 'origin',
            'then', 'next', 'following', 'after', 'subsequently',
            'however', 'but', 'yet', 'nevertheless', 'although',
            'therefore', 'thus', 'consequently', 'as a result',
            'finally', 'ultimately', 'in conclusion', 'end', 'culmination'
        ]
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def extract_all_notebook_insights(self) -> List[NotebookInsight]:
        """Extract and analyze all notebook insights"""
        print("📖 Extracting all notebook insights...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all notebook transcripts with conversation context
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
                    AND LENGTH(child.body_text) > 200
                ORDER BY child.timestamp
            """, (self.JOURNAL_OCR_GIZMO_ID,))
            
            results = cursor.fetchall()
        
        insights = []
        print(f"Processing {len(results)} potential insights...")
        
        for i, row in enumerate(results, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(results)} insights...")
                
            insight = self._analyze_content(row)
            if insight:
                insights.append(insight)
        
        print(f"✅ Extracted {len(insights)} meaningful insights")
        return insights
    
    def _analyze_content(self, row: Dict) -> Optional[NotebookInsight]:
        """Analyze individual content for insight extraction"""
        body_text = row['body_text']
        
        # Extract markdown content if present
        markdown_content = self._extract_handwritten_content(body_text)
        if not markdown_content or len(markdown_content.strip()) < 50:
            return None
        
        # Analyze philosophical concepts
        concepts = self._identify_philosophical_concepts(markdown_content)
        if len(concepts) < 2:  # Must have at least 2 philosophical concepts
            return None
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(markdown_content)
        
        # Analyze emotional tone
        emotional_tone = self._analyze_emotional_tone(markdown_content)
        
        # Calculate depth score
        depth_score = self._calculate_depth_score(markdown_content, concepts, key_phrases)
        
        # Identify themes
        themes = self._identify_themes(markdown_content, concepts)
        
        return NotebookInsight(
            id=f"{row['conversation_id']}_{row['id']}",
            conversation_id=row['conversation_id'],
            conversation_title=row['conversation_title'],
            content=markdown_content,
            timestamp=row['timestamp'],
            word_count=len(markdown_content.split()),
            philosophical_concepts=concepts,
            key_phrases=key_phrases,
            emotional_tone=emotional_tone,
            depth_score=depth_score,
            themes=themes
        )
    
    def _extract_handwritten_content(self, body_text: str) -> str:
        """Extract handwritten content from OCR transcript"""
        # Try multiple markdown patterns
        patterns = [
            r'```markdown\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                if len(content) > 50:  # Minimum meaningful content
                    return content
        
        return ""
    
    def _identify_philosophical_concepts(self, content: str) -> List[str]:
        """Identify philosophical concepts in content"""
        content_lower = content.lower()
        found_concepts = []
        
        for term in self.philosophical_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', content_lower):
                found_concepts.append(term)
        
        return found_concepts
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract meaningful phrases from content"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter for meaningful sentences
        key_phrases = []
        for sentence in sentences:
            sentence = sentence.strip()
            if (20 <= len(sentence) <= 150 and 
                any(term in sentence.lower() for term in self.philosophical_terms[:15])):
                key_phrases.append(sentence)
        
        return key_phrases[:5]  # Top 5
    
    def _analyze_emotional_tone(self, content: str) -> str:
        """Analyze the emotional tone of the content"""
        content_lower = content.lower()
        
        contemplative_markers = ['contemplation', 'meditation', 'reflection', 'pondering', 'wondering']
        urgent_markers = ['must', 'should', 'need', 'crucial', 'important', 'vital']
        peaceful_markers = ['peace', 'calm', 'serenity', 'tranquil', 'stillness', 'harmony']
        questioning_markers = ['?', 'what if', 'how', 'why', 'perhaps', 'maybe']
        assertive_markers = ['is', 'are', 'will', 'shall', 'certainly', 'definitely']
        
        scores = {
            'contemplative': sum(1 for marker in contemplative_markers if marker in content_lower),
            'urgent': sum(1 for marker in urgent_markers if marker in content_lower),
            'peaceful': sum(1 for marker in peaceful_markers if marker in content_lower),
            'questioning': sum(1 for marker in questioning_markers if marker in content_lower) + content.count('?'),
            'assertive': sum(1 for marker in assertive_markers if marker in content_lower)
        }
        
        return max(scores, key=scores.get)
    
    def _calculate_depth_score(self, content: str, concepts: List[str], key_phrases: List[str]) -> float:
        """Calculate intellectual depth score"""
        word_count = len(content.split())
        
        # Base score from word count (normalized)
        length_score = min(word_count / 500, 1.0)
        
        # Concept diversity score
        concept_score = min(len(concepts) / 10, 1.0)
        
        # Abstract thinking indicators
        abstract_terms = ['essence', 'nature', 'fundamental', 'underlying', 'principle', 
                         'truth', 'reality', 'being', 'existence', 'consciousness']
        abstract_score = sum(1 for term in abstract_terms if term in content.lower()) / 10
        
        # Paradox and complexity indicators
        paradox_markers = ['paradox', 'contradiction', 'both', 'neither', 'yet', 'however', 'although']
        paradox_score = sum(1 for marker in paradox_markers if marker in content.lower()) / 5
        
        # Quality of key phrases
        phrase_score = min(len(key_phrases) / 5, 1.0)
        
        # Weighted combination
        depth_score = (
            length_score * 0.2 +
            concept_score * 0.3 +
            abstract_score * 0.2 +
            paradox_score * 0.2 +
            phrase_score * 0.1
        )
        
        return min(depth_score, 1.0)
    
    def _identify_themes(self, content: str, concepts: List[str]) -> List[str]:
        """Identify thematic categories"""
        content_lower = content.lower()
        themes = []
        
        theme_patterns = {
            'consciousness_nature': ['consciousness', 'awareness', 'mind', 'thought', 'perception'],
            'being_existence': ['being', 'existence', 'reality', 'nature', 'essence'],
            'self_identity': ['self', 'ego', 'identity', 'i am', 'who am', 'person'],
            'spiritual_practice': ['meditation', 'contemplation', 'zen', 'tao', 'practice', 'awakening'],
            'philosophical_inquiry': ['truth', 'wisdom', 'knowledge', 'understanding', 'meaning'],
            'interconnection': ['interconnected', 'interdependent', 'unity', 'wholeness', 'oneness'],
            'experience_perception': ['experience', 'feeling', 'sensation', 'perceive', 'observe'],
            'time_space': ['time', 'space', 'moment', 'now', 'present', 'eternal'],
            'transformation': ['change', 'transformation', 'growth', 'evolution', 'becoming'],
            'paradox_mystery': ['paradox', 'mystery', 'unknown', 'uncertain', 'enigma']
        }
        
        for theme_name, keywords in theme_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                # Check concept overlap
                concept_overlap = sum(1 for concept in concepts if concept in keywords)
                if concept_overlap > 0:
                    themes.append(theme_name)
        
        return themes
    
    def cluster_by_themes(self, insights: List[NotebookInsight]) -> List[ThematicCluster]:
        """Cluster insights by thematic similarity"""
        print("🎯 Clustering insights by themes...")
        
        # Group insights by themes
        theme_groups = defaultdict(list)
        for insight in insights:
            for theme in insight.themes:
                theme_groups[theme].append(insight)
        
        # Create thematic clusters
        clusters = []
        for theme_name, theme_insights in theme_groups.items():
            if len(theme_insights) >= 3:  # Minimum insights per cluster
                cluster = self._create_thematic_cluster(theme_name, theme_insights)
                clusters.append(cluster)
        
        # Sort by coherence score
        clusters.sort(key=lambda x: x.coherence_score, reverse=True)
        
        print(f"✅ Created {len(clusters)} thematic clusters")
        return clusters
    
    def _create_thematic_cluster(self, theme_name: str, insights: List[NotebookInsight]) -> ThematicCluster:
        """Create a thematic cluster from insights"""
        # Sort insights by depth score and timestamp
        sorted_insights = sorted(insights, key=lambda x: (x.depth_score, x.timestamp), reverse=True)
        
        # Extract central concepts
        all_concepts = []
        for insight in insights:
            all_concepts.extend(insight.philosophical_concepts)
        concept_counts = Counter(all_concepts)
        central_concepts = [concept for concept, count in concept_counts.most_common(10)]
        
        # Generate narrative arc description
        narrative_arc = self._generate_narrative_arc(sorted_insights)
        
        # Calculate coherence score
        coherence_score = self._calculate_cluster_coherence(sorted_insights, central_concepts)
        
        # Calculate total word count
        total_words = sum(insight.word_count for insight in insights)
        
        return ThematicCluster(
            theme_name=theme_name,
            insights=sorted_insights,
            central_concepts=central_concepts,
            narrative_arc=narrative_arc,
            coherence_score=coherence_score,
            word_count=total_words
        )
    
    def _generate_narrative_arc(self, insights: List[NotebookInsight]) -> str:
        """Generate a narrative arc description for clustered insights"""
        if not insights:
            return "No clear narrative arc"
        
        # Analyze temporal progression
        early_insights = insights[:len(insights)//3] if len(insights) > 3 else [insights[0]]
        late_insights = insights[-len(insights)//3:] if len(insights) > 3 else [insights[-1]]
        
        # Extract dominant themes from early vs late
        early_themes = []
        late_themes = []
        
        for insight in early_insights:
            early_themes.extend(insight.themes)
        for insight in late_insights:
            late_themes.extend(insight.themes)
        
        early_dominant = Counter(early_themes).most_common(2)
        late_dominant = Counter(late_themes).most_common(2)
        
        # Generate arc description
        if early_dominant and late_dominant:
            early_theme = early_dominant[0][0].replace('_', ' ')
            late_theme = late_dominant[0][0].replace('_', ' ')
            
            if early_theme == late_theme:
                return f"Sustained exploration of {early_theme}"
            else:
                return f"Journey from {early_theme} toward {late_theme}"
        else:
            dominant_theme = Counter([theme for insight in insights for theme in insight.themes]).most_common(1)
            if dominant_theme:
                return f"Deep dive into {dominant_theme[0][0].replace('_', ' ')}"
            else:
                return "Diverse philosophical exploration"
    
    def _calculate_cluster_coherence(self, insights: List[NotebookInsight], central_concepts: List[str]) -> float:
        """Calculate how coherent a thematic cluster is"""
        if not insights:
            return 0.0
        
        # Concept overlap score
        concept_overlap_scores = []
        for insight in insights:
            overlap = len(set(insight.philosophical_concepts) & set(central_concepts))
            max_possible = min(len(insight.philosophical_concepts), len(central_concepts))
            if max_possible > 0:
                concept_overlap_scores.append(overlap / max_possible)
        
        concept_coherence = np.mean(concept_overlap_scores) if concept_overlap_scores else 0
        
        # Depth consistency
        depth_scores = [insight.depth_score for insight in insights]
        depth_coherence = 1 - (np.std(depth_scores) if len(depth_scores) > 1 else 0)
        
        # Theme consistency
        all_insight_themes = [theme for insight in insights for theme in insight.themes]
        theme_distribution = Counter(all_insight_themes)
        theme_coherence = len(theme_distribution) / max(len(all_insight_themes), 1)  # Fewer themes = more coherent
        theme_coherence = max(0, 1 - theme_coherence)  # Invert so higher is better
        
        # Weighted combination
        return (concept_coherence * 0.4 + depth_coherence * 0.3 + theme_coherence * 0.3)
    
    def generate_book_structure(self, clusters: List[ThematicCluster]) -> Dict[str, Any]:
        """Generate suggested book structure from thematic clusters"""
        print("📖 Generating book structure...")
        
        # Group related clusters into potential chapters
        chapters = self._organize_clusters_into_chapters(clusters)
        
        # Generate overall narrative arc
        book_arc = self._generate_book_narrative_arc(chapters)
        
        # Calculate statistics
        total_insights = sum(len(cluster.insights) for cluster in clusters)
        total_words = sum(cluster.word_count for cluster in clusters)
        
        # Generate book metadata
        book_structure = {
            'title_suggestions': self._generate_title_suggestions(clusters),
            'subtitle_suggestions': self._generate_subtitle_suggestions(clusters),
            'overall_narrative_arc': book_arc,
            'chapters': chapters,
            'statistics': {
                'total_insights': total_insights,
                'total_words': total_words,
                'num_chapters': len(chapters),
                'avg_words_per_chapter': total_words // len(chapters) if chapters else 0,
                'dominant_themes': self._get_dominant_themes(clusters),
                'time_span': self._calculate_time_span(clusters)
            },
            'essence_description': self._extract_essence_description(clusters)
        }
        
        return book_structure
    
    def _organize_clusters_into_chapters(self, clusters: List[ThematicCluster]) -> List[Dict[str, Any]]:
        """Organize thematic clusters into logical chapters"""
        # Define logical chapter progressions
        chapter_flow = [
            (['consciousness_nature', 'being_existence'], 'Foundations of Being and Consciousness'),
            (['self_identity', 'experience_perception'], 'The Nature of Self and Experience'),
            (['spiritual_practice', 'philosophical_inquiry'], 'Paths of Inquiry and Practice'),
            (['interconnection', 'time_space'], 'Unity, Time, and the Cosmic Perspective'),
            (['transformation', 'paradox_mystery'], 'Transformation and the Embrace of Mystery')
        ]
        
        chapters = []
        used_clusters = set()
        
        # Create chapters based on logical flow
        for theme_group, suggested_title in chapter_flow:
            chapter_clusters = []
            for cluster in clusters:
                if cluster.theme_name in theme_group and cluster.theme_name not in used_clusters:
                    chapter_clusters.append(cluster)
                    used_clusters.add(cluster.theme_name)
            
            if chapter_clusters:
                # Sort clusters within chapter by coherence
                chapter_clusters.sort(key=lambda x: x.coherence_score, reverse=True)
                
                chapter = {
                    'title': suggested_title,
                    'theme_focus': theme_group,
                    'clusters': chapter_clusters,
                    'word_count': sum(c.word_count for c in chapter_clusters),
                    'insight_count': sum(len(c.insights) for c in chapter_clusters),
                    'narrative_flow': self._generate_chapter_narrative_flow(chapter_clusters)
                }
                chapters.append(chapter)
        
        # Add remaining clusters to a miscellaneous chapter
        remaining_clusters = [c for c in clusters if c.theme_name not in used_clusters]
        if remaining_clusters:
            chapters.append({
                'title': 'Further Explorations',
                'theme_focus': ['miscellaneous'],
                'clusters': remaining_clusters,
                'word_count': sum(c.word_count for c in remaining_clusters),
                'insight_count': sum(len(c.insights) for c in remaining_clusters),
                'narrative_flow': 'Additional insights and reflections'
            })
        
        return chapters
    
    def _generate_chapter_narrative_flow(self, clusters: List[ThematicCluster]) -> str:
        """Generate narrative flow description for a chapter"""
        if not clusters:
            return "No clear flow"
        
        cluster_arcs = [cluster.narrative_arc for cluster in clusters]
        
        # Simple heuristic for chapter flow
        if len(clusters) == 1:
            return cluster_arcs[0]
        elif len(clusters) == 2:
            return f"{cluster_arcs[0]}, leading to {cluster_arcs[1]}"
        else:
            return f"Beginning with {cluster_arcs[0]}, exploring {cluster_arcs[1]}, and culminating in {cluster_arcs[-1]}"
    
    def _generate_book_narrative_arc(self, chapters: List[Dict[str, Any]]) -> str:
        """Generate overall narrative arc for the book"""
        if not chapters:
            return "A collection of philosophical insights"
        
        chapter_themes = []
        for chapter in chapters:
            chapter_themes.append(chapter['title'].lower())
        
        # Create narrative arc based on chapter progression
        if len(chapters) >= 3:
            return f"A philosophical journey beginning with {chapter_themes[0]}, exploring {chapter_themes[1]}, and culminating in {chapter_themes[-1]}"
        else:
            return f"An exploration of {' and '.join(chapter_themes)}"
    
    def _generate_title_suggestions(self, clusters: List[ThematicCluster]) -> List[str]:
        """Generate book title suggestions"""
        # Extract dominant concepts
        all_concepts = []
        for cluster in clusters:
            all_concepts.extend(cluster.central_concepts)
        
        dominant_concepts = [concept for concept, count in Counter(all_concepts).most_common(5)]
        
        suggestions = [
            "Handwritten Wisdom: Reflections on Consciousness and Being",
            "The Notebook Insights: A Journey Through Contemplation",
            "Ink and Awareness: Philosophical Reflections from Personal Practice",
            f"Contemplations on {dominant_concepts[0].title()} and {dominant_concepts[1].title()}" if len(dominant_concepts) >= 2 else "Philosophical Contemplations",
            "The Art of Handwritten Philosophy",
            "Notebook Meditations: Essays on Experience and Understanding",
            "Written Wisdom: Insights from the Contemplative Path"
        ]
        
        return suggestions
    
    def _generate_subtitle_suggestions(self, clusters: List[ThematicCluster]) -> List[str]:
        """Generate subtitle suggestions"""
        total_insights = sum(len(cluster.insights) for cluster in clusters)
        
        return [
            f"Insights from {total_insights} Handwritten Reflections",
            "A Personal Journey Through Philosophy and Practice",
            "Contemplative Essays on the Nature of Experience",
            "Handwritten Explorations of Consciousness and Being",
            "From Notebook Pages to Philosophical Understanding"
        ]
    
    def _get_dominant_themes(self, clusters: List[ThematicCluster]) -> List[Tuple[str, int]]:
        """Get dominant themes across all clusters"""
        theme_counts = Counter([cluster.theme_name for cluster in clusters])
        return theme_counts.most_common(5)
    
    def _calculate_time_span(self, clusters: List[ThematicCluster]) -> Dict[str, str]:
        """Calculate time span of insights"""
        all_timestamps = []
        for cluster in clusters:
            for insight in cluster.insights:
                all_timestamps.append(insight.timestamp)
        
        if all_timestamps:
            earliest = min(all_timestamps)
            latest = max(all_timestamps)
            return {
                'earliest': earliest.strftime("%Y-%m-%d"),
                'latest': latest.strftime("%Y-%m-%d"),
                'span_days': (latest - earliest).days
            }
        
        return {'earliest': 'Unknown', 'latest': 'Unknown', 'span_days': 0}
    
    def _extract_essence_description(self, clusters: List[ThematicCluster]) -> str:
        """Extract the natural essence of the notebook insights"""
        # Analyze patterns across all clusters
        all_concepts = []
        all_themes = []
        all_tones = []
        
        for cluster in clusters:
            all_concepts.extend(cluster.central_concepts)
            all_themes.append(cluster.theme_name)
            for insight in cluster.insights:
                all_tones.append(insight.emotional_tone)
        
        dominant_concepts = [c for c, _ in Counter(all_concepts).most_common(3)]
        dominant_tone = Counter(all_tones).most_common(1)[0][0] if all_tones else 'contemplative'
        
        essence_patterns = {
            'contemplative': "deeply reflective and meditative exploration",
            'questioning': "curious inquiry into fundamental questions",
            'peaceful': "serene contemplation of life's deeper meanings",
            'urgent': "passionate investigation of crucial insights",
            'assertive': "confident articulation of philosophical understanding"
        }
        
        tone_description = essence_patterns.get(dominant_tone, "thoughtful exploration")
        
        return (f"This collection represents a {tone_description} of "
                f"{', '.join(dominant_concepts[:2])} and related themes. "
                f"The insights emerge from personal practice and contemplation, "
                f"offering a unique perspective on the fundamental questions of "
                f"existence, awareness, and the human experience.")
    
    def interactive_curation(self):
        """Interactive curation process"""
        print("\n🎨 Interactive Book Curation Process")
        print("=" * 50)
        
        # Step 1: Extract insights
        insights = self.extract_all_notebook_insights()
        if not insights:
            print("❌ No insights found!")
            return
        
        print(f"\n📊 Analysis Summary:")
        print(f"Total insights: {len(insights)}")
        print(f"Total words: {sum(i.word_count for i in insights):,}")
        print(f"Average depth score: {np.mean([i.depth_score for i in insights]):.2f}")
        
        # Step 2: Cluster by themes
        clusters = self.cluster_by_themes(insights)
        
        # Step 3: Generate book structure
        book_structure = self.generate_book_structure(clusters)
        
        # Step 4: Present results
        self._present_book_structure(book_structure)
        
        # Step 5: Export options
        self._offer_export_options(book_structure, insights, clusters)
    
    def _present_book_structure(self, structure: Dict[str, Any]):
        """Present the generated book structure"""
        print(f"\n📖 Proposed Book Structure")
        print("=" * 60)
        
        print(f"\n🏷️  Title Suggestions:")
        for i, title in enumerate(structure['title_suggestions'][:3], 1):
            print(f"  {i}. {title}")
        
        print(f"\n📝 Essence:")
        print(f"  {structure['essence_description']}")
        
        print(f"\n📊 Statistics:")
        stats = structure['statistics']
        print(f"  • Total insights: {stats['total_insights']}")
        print(f"  • Total words: {stats['total_words']:,}")
        print(f"  • Chapters: {stats['num_chapters']}")
        print(f"  • Time span: {stats['time_span']['span_days']} days")
        
        print(f"\n📚 Chapter Structure:")
        for i, chapter in enumerate(structure['chapters'], 1):
            print(f"\n  Chapter {i}: {chapter['title']}")
            print(f"    📊 {chapter['insight_count']} insights, {chapter['word_count']:,} words")
            print(f"    🎯 {chapter['narrative_flow']}")
            
            for j, cluster in enumerate(chapter['clusters'], 1):
                print(f"      {i}.{j} {cluster.theme_name.replace('_', ' ').title()}")
                print(f"          {len(cluster.insights)} insights, coherence: {cluster.coherence_score:.2f}")
    
    def _offer_export_options(self, structure: Dict[str, Any], insights: List[NotebookInsight], clusters: List[ThematicCluster]):
        """Offer export options"""
        print(f"\n💾 Export Options:")
        print("1. Full book structure (JSON)")
        print("2. Chapter outlines (Markdown)")
        print("3. Raw insights by theme (Markdown)")
        print("4. Book proposal document")
        
        try:
            choice = input("\nSelect export option (1-4, or 'skip'): ").strip()
            
            if choice == '1':
                self._export_full_structure(structure)
            elif choice == '2':
                self._export_chapter_outlines(structure)
            elif choice == '3':
                self._export_insights_by_theme(clusters)
            elif choice == '4':
                self._export_book_proposal(structure, insights)
            elif choice.lower() != 'skip':
                print("Invalid choice, skipping export")
                
        except KeyboardInterrupt:
            print("\n👋 Export cancelled")
    
    def _export_full_structure(self, structure: Dict[str, Any]):
        """Export full book structure as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"book_structure_{timestamp}.json"
        output_path = Path("exports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        # Convert structure to JSON-serializable format
        json_structure = self._convert_structure_to_json(structure)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exported full structure to: {output_path}")
    
    def _export_chapter_outlines(self, structure: Dict[str, Any]):
        """Export chapter outlines as Markdown"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"chapter_outlines_{timestamp}.md"
        output_path = Path("exports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Book Chapter Outlines\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Proposed Titles\n\n")
            for title in structure['title_suggestions'][:3]:
                f.write(f"- {title}\n")
            
            f.write(f"\n## Book Essence\n\n")
            f.write(f"{structure['essence_description']}\n\n")
            
            f.write("## Chapter Structure\n\n")
            for i, chapter in enumerate(structure['chapters'], 1):
                f.write(f"### Chapter {i}: {chapter['title']}\n\n")
                f.write(f"**Theme Focus:** {', '.join(chapter['theme_focus'])}\n")
                f.write(f"**Word Count:** {chapter['word_count']:,}\n")
                f.write(f"**Insights:** {chapter['insight_count']}\n")
                f.write(f"**Narrative Flow:** {chapter['narrative_flow']}\n\n")
                
                f.write("**Sections:**\n")
                for j, cluster in enumerate(chapter['clusters'], 1):
                    f.write(f"  {i}.{j} {cluster.theme_name.replace('_', ' ').title()}\n")
                    f.write(f"      - {len(cluster.insights)} insights\n")
                    f.write(f"      - Coherence score: {cluster.coherence_score:.2f}\n")
                    f.write(f"      - Central concepts: {', '.join(cluster.central_concepts[:5])}\n")
                
                f.write("\n")
        
        print(f"✅ Exported chapter outlines to: {output_path}")
    
    def _export_insights_by_theme(self, clusters: List[ThematicCluster]):
        """Export raw insights organized by theme"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"insights_by_theme_{timestamp}.md"
        output_path = Path("exports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Notebook Insights by Theme\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            for cluster in clusters:
                f.write(f"## {cluster.theme_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Central Concepts:** {', '.join(cluster.central_concepts[:8])}\n")
                f.write(f"**Narrative Arc:** {cluster.narrative_arc}\n")
                f.write(f"**Coherence Score:** {cluster.coherence_score:.2f}\n")
                f.write(f"**Total Words:** {cluster.word_count:,}\n\n")
                
                for i, insight in enumerate(cluster.insights, 1):
                    f.write(f"### Insight {i}\n\n")
                    f.write(f"**Source:** {insight.conversation_title}\n")
                    f.write(f"**Date:** {insight.timestamp.strftime('%Y-%m-%d')}\n")
                    f.write(f"**Depth Score:** {insight.depth_score:.2f}\n")
                    f.write(f"**Tone:** {insight.emotional_tone}\n\n")
                    
                    f.write("**Content:**\n")
                    f.write(f"```\n{insight.content}\n```\n\n")
                    
                    if insight.key_phrases:
                        f.write("**Key Phrases:**\n")
                        for phrase in insight.key_phrases:
                            f.write(f"- {phrase}\n")
                        f.write("\n")
                
                f.write("---\n\n")
        
        print(f"✅ Exported insights by theme to: {output_path}")
    
    def _export_book_proposal(self, structure: Dict[str, Any], insights: List[NotebookInsight]):
        """Export a book proposal document"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"book_proposal_{timestamp}.md"
        output_path = Path("exports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Book Proposal: Handwritten Philosophical Insights\n\n")
            f.write(f"**Prepared:** {datetime.now().strftime('%B %d, %Y')}\n\n")
            
            f.write("## Proposed Title Options\n\n")
            for i, title in enumerate(structure['title_suggestions'][:3], 1):
                f.write(f"{i}. **{title}**\n")
            f.write("\n")
            
            f.write("## Book Description\n\n")
            f.write(f"{structure['essence_description']}\n\n")
            
            stats = structure['statistics']
            f.write("## Manuscript Statistics\n\n")
            f.write(f"- **Total Insights:** {stats['total_insights']}\n")
            f.write(f"- **Estimated Word Count:** {stats['total_words']:,} words\n")
            f.write(f"- **Chapters:** {stats['num_chapters']}\n")
            f.write(f"- **Source Period:** {stats['time_span']['earliest']} to {stats['time_span']['latest']}\n")
            f.write(f"- **Composition Span:** {stats['time_span']['span_days']} days\n\n")
            
            f.write("## Chapter Outline\n\n")
            for i, chapter in enumerate(structure['chapters'], 1):
                f.write(f"### Chapter {i}: {chapter['title']}\n")
                f.write(f"*{chapter['word_count']:,} words, {chapter['insight_count']} insights*\n\n")
                f.write(f"{chapter['narrative_flow']}\n\n")
            
            f.write("## Sample Content\n\n")
            # Include highest-scoring insight as sample
            best_insight = max(insights, key=lambda x: x.depth_score)
            f.write(f"**From:** {best_insight.conversation_title}\n")
            f.write(f"**Depth Score:** {best_insight.depth_score:.2f}\n\n")
            f.write(f"```\n{best_insight.content[:500]}...\n```\n\n")
            
            f.write("## Thematic Analysis\n\n")
            f.write("**Dominant Themes:**\n")
            for theme, count in stats['dominant_themes']:
                f.write(f"- {theme.replace('_', ' ').title()}: {count} clusters\n")
            
        print(f"✅ Exported book proposal to: {output_path}")
    
    def _convert_structure_to_json(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Convert structure to JSON-serializable format"""
        # This is a simplified version - in practice, you'd need to handle
        # all the custom objects properly
        return {
            'title_suggestions': structure['title_suggestions'],
            'subtitle_suggestions': structure.get('subtitle_suggestions', []),
            'essence_description': structure['essence_description'],
            'overall_narrative_arc': structure['overall_narrative_arc'],
            'statistics': structure['statistics'],
            'chapters': [
                {
                    'title': ch['title'],
                    'theme_focus': ch['theme_focus'],
                    'word_count': ch['word_count'],
                    'insight_count': ch['insight_count'],
                    'narrative_flow': ch['narrative_flow'],
                    'clusters': [
                        {
                            'theme_name': cl.theme_name,
                            'central_concepts': cl.central_concepts,
                            'narrative_arc': cl.narrative_arc,
                            'coherence_score': cl.coherence_score,
                            'word_count': cl.word_count,
                            'insight_count': len(cl.insights)
                        }
                        for cl in ch['clusters']
                    ]
                }
                for ch in structure['chapters']
            ]
        }

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agent-assisted notebook book curation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python notebook_book_curator.py curate     # Interactive curation process
  python notebook_book_curator.py analyze    # Quick analysis only
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Curate command (interactive)
    curate_parser = subparsers.add_parser('curate', help='Interactive curation process')
    
    # Analyze command (analysis only)
    analyze_parser = subparsers.add_parser('analyze', help='Analysis only, no exports')
    
    args = parser.parse_args()
    
    try:
        curator = NotebookBookCurator()
        
        if args.command == 'curate' or args.command is None:
            curator.interactive_curation()
        elif args.command == 'analyze':
            insights = curator.extract_all_notebook_insights()
            clusters = curator.cluster_by_themes(insights)
            structure = curator.generate_book_structure(clusters)
            curator._present_book_structure(structure)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()