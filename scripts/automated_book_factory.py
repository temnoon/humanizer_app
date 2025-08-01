#!/usr/bin/env python3
"""
Automated Book Factory
Mass production system for generating 7 books from thematic clusters with AI editor integration
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re
from collections import Counter, defaultdict
import argparse

class AutomatedBookFactory:
    """Automated system for generating multiple books from thematic clusters"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    # Predefined book themes based on clustering analysis
    BOOK_THEMES = {
        1: {
            "title": "The Nature of Consciousness",
            "subtitle": "Explorations in Awareness and Being",
            "keywords": ["consciousness", "awareness", "being", "existence", "mind"],
            "min_insights": 50,
            "target_words": 40000
        },
        2: {
            "title": "Experience and Perception", 
            "subtitle": "Understanding How We Know What We Know",
            "keywords": ["experience", "perception", "sensing", "knowing", "reality"],
            "min_insights": 40,
            "target_words": 35000
        },
        3: {
            "title": "The Question of Self",
            "subtitle": "Identity, Ego, and Personal Truth", 
            "keywords": ["self", "identity", "ego", "personal", "individual"],
            "min_insights": 30,
            "target_words": 30000
        },
        4: {
            "title": "Philosophical Inquiry",
            "subtitle": "Methods and Approaches to Understanding",
            "keywords": ["philosophy", "inquiry", "question", "method", "understanding"],
            "min_insights": 25,
            "target_words": 25000
        },
        5: {
            "title": "Spiritual Practice and Contemplation",
            "subtitle": "Applied Wisdom in Daily Life",
            "keywords": ["spiritual", "practice", "meditation", "contemplation", "wisdom"],
            "min_insights": 20,
            "target_words": 20000
        },
        6: {
            "title": "Time, Space, and Reality",
            "subtitle": "The Fabric of Existence",
            "keywords": ["time", "space", "reality", "universe", "existence"],
            "min_insights": 15,
            "target_words": 18000
        },
        7: {
            "title": "Unity and Interconnection",
            "subtitle": "The Web of All Things",
            "keywords": ["unity", "connection", "relationship", "wholeness", "integration"],
            "min_insights": 10,
            "target_words": 15000
        }
    }
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://tem@localhost/humanizer_archive"
        self.database_url = database_url
        self.output_dir = Path("automated_books")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🏭 Automated Book Factory")
        print("=" * 50)
        print(f"📚 Target: {len(self.BOOK_THEMES)} books from notebook insights")
        
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        
    def extract_all_insights(self) -> List[Dict[str, Any]]:
        """Extract all meaningful insights from notebook transcripts"""
        print("📖 Extracting insights from all notebook transcripts...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
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
            
            raw_messages = cursor.fetchall()
        
        insights = []
        total_processed = 0
        
        for message in raw_messages:
            total_processed += 1
            if total_processed % 50 == 0:
                print(f"  Processing {total_processed}/{len(raw_messages)} messages...")
                
            # Extract handwritten content
            content = self._extract_handwritten_content(message['body_text'])
            if content and len(content) > 100:
                insight = {
                    'id': f"insight_{total_processed}",
                    'conversation_id': message['conversation_id'],
                    'conversation_title': message['conversation_title'],
                    'content': content,
                    'timestamp': message['timestamp'].isoformat() if message['timestamp'] else None,
                    'author': message['author'],
                    'word_count': len(content.split()),
                    'quality_score': self._calculate_quality_score(content),
                    'themes': self._identify_themes(content),
                    'depth_indicators': self._analyze_depth(content)
                }
                insights.append(insight)
        
        print(f"✅ Extracted {len(insights)} meaningful insights from {total_processed} messages")
        return insights
    
    def _extract_handwritten_content(self, body_text: str) -> str:
        """Extract handwritten content from message"""
        patterns = [
            r'```markdown\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                if len(content) > 50:
                    return content
        return ""
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score for content"""
        score = 0.0
        
        # Length bonus (optimal around 200-800 words)
        word_count = len(content.split())
        if 200 <= word_count <= 800:
            score += 0.3
        elif word_count > 100:
            score += 0.1
            
        # Philosophical depth indicators
        depth_terms = [
            'consciousness', 'experience', 'being', 'existence', 'reality',
            'awareness', 'perception', 'understanding', 'inquiry', 'contemplation'
        ]
        found_depth = sum(1 for term in depth_terms if term.lower() in content.lower())
        score += min(found_depth * 0.1, 0.4)
        
        # Question engagement (shows active inquiry)
        question_count = content.count('?')
        score += min(question_count * 0.05, 0.2)
        
        # Personal reflection indicators
        personal_indicators = ['I feel', 'I think', 'I notice', 'I wonder', 'my sense']
        personal_count = sum(1 for indicator in personal_indicators 
                           if indicator.lower() in content.lower())
        score += min(personal_count * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def _identify_themes(self, content: str) -> List[str]:
        """Identify which book themes this content relates to"""
        content_lower = content.lower()
        themes = []
        
        for book_id, book_info in self.BOOK_THEMES.items():
            keyword_matches = sum(1 for keyword in book_info['keywords'] 
                                if keyword.lower() in content_lower)
            if keyword_matches >= 1:  # At least one keyword match
                themes.append(book_id)
        
        return themes
    
    def _analyze_depth(self, content: str) -> Dict[str, Any]:
        """Analyze philosophical depth indicators"""
        return {
            'abstract_concepts': len(re.findall(r'\b(consciousness|being|existence|reality|awareness)\b', 
                                              content, re.IGNORECASE)),
            'inquiry_questions': content.count('?'),
            'personal_reflection': len(re.findall(r'\b(I feel|I think|I notice|I wonder)\b', 
                                                content, re.IGNORECASE)),
            'comparative_thinking': len(re.findall(r'\b(like|similar|different|contrast)\b',
                                                 content, re.IGNORECASE))
        }
    
    def organize_insights_by_books(self, insights: List[Dict]) -> Dict[int, List[Dict]]:
        """Organize insights into book categories"""
        print("📚 Organizing insights by book themes...")
        
        book_insights = defaultdict(list)
        
        for insight in insights:
            # Add to all relevant book themes
            for theme_id in insight['themes']:
                book_insights[theme_id].append(insight)
        
        # Sort each book's insights by quality score
        for book_id in book_insights:
            book_insights[book_id].sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Report organization results
        print("\n📊 Book Organization Results:")
        for book_id in sorted(book_insights.keys()):
            theme = self.BOOK_THEMES[book_id]
            count = len(book_insights[book_id])
            total_words = sum(insight['word_count'] for insight in book_insights[book_id])
            avg_quality = sum(insight['quality_score'] for insight in book_insights[book_id]) / count if count > 0 else 0
            
            status = "✅" if count >= theme['min_insights'] else "⚠️"
            print(f"  {status} Book {book_id}: {theme['title']}")
            print(f"      {count} insights, {total_words:,} words, avg quality: {avg_quality:.2f}")
        
        return dict(book_insights)
    
    def generate_book_structure(self, book_id: int, insights: List[Dict]) -> Dict[str, Any]:
        """Generate automated book structure"""
        theme = self.BOOK_THEMES[book_id]
        
        # Filter and select best insights
        quality_threshold = 0.3
        selected_insights = [insight for insight in insights 
                           if insight['quality_score'] >= quality_threshold]
        
        # Limit to reasonable size
        max_insights = min(len(selected_insights), 150)
        selected_insights = selected_insights[:max_insights]
        
        # Generate chapter structure (divide into 4-6 chapters)
        num_chapters = min(6, max(4, len(selected_insights) // 20))
        insights_per_chapter = len(selected_insights) // num_chapters
        
        chapters = []
        for i in range(num_chapters):
            start_idx = i * insights_per_chapter
            end_idx = start_idx + insights_per_chapter if i < num_chapters - 1 else len(selected_insights)
            chapter_insights = selected_insights[start_idx:end_idx]
            
            # Generate chapter title based on most common concepts
            chapter_concepts = []
            for insight in chapter_insights:
                chapter_concepts.extend(insight['themes'])
            
            chapter_title = self._generate_chapter_title(i + 1, chapter_insights)
            
            chapters.append({
                'number': i + 1,
                'title': chapter_title,
                'insights': chapter_insights,
                'word_count': sum(insight['word_count'] for insight in chapter_insights),
                'avg_quality': sum(insight['quality_score'] for insight in chapter_insights) / len(chapter_insights)
            })
        
        return {
            'book_id': book_id,
            'title': theme['title'],
            'subtitle': theme['subtitle'],
            'total_insights': len(selected_insights),
            'total_words': sum(insight['word_count'] for insight in selected_insights),
            'chapters': chapters,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'quality_threshold': quality_threshold,
                'avg_book_quality': sum(insight['quality_score'] for insight in selected_insights) / len(selected_insights)
            }
        }
    
    def _generate_chapter_title(self, chapter_num: int, insights: List[Dict]) -> str:
        """Generate chapter title based on content analysis"""
        # Analyze most common concepts in this chapter
        all_content = " ".join(insight['content'] for insight in insights)
        
        # Extract key philosophical concepts
        concept_patterns = {
            'consciousness': r'\b(consciousness|aware|awaken)\w*\b',
            'experience': r'\b(experience|feel|sense)\w*\b', 
            'being': r'\b(being|exist|is|am)\w*\b',
            'understanding': r'\b(understand|know|learn)\w*\b',
            'reality': r'\b(real|truth|actual)\w*\b',
            'practice': r'\b(practice|do|act)\w*\b'
        }
        
        concept_counts = {}
        for concept, pattern in concept_patterns.items():
            matches = len(re.findall(pattern, all_content, re.IGNORECASE))
            if matches > 0:
                concept_counts[concept] = matches
        
        # Generate title based on dominant concepts
        if concept_counts:
            top_concept = max(concept_counts.items(), key=lambda x: x[1])[0]
            chapter_titles = {
                'consciousness': f"Chapter {chapter_num}: The Emergence of Awareness",
                'experience': f"Chapter {chapter_num}: Dimensions of Experience", 
                'being': f"Chapter {chapter_num}: The Nature of Being",
                'understanding': f"Chapter {chapter_num}: Paths to Understanding",
                'reality': f"Chapter {chapter_num}: The Question of Reality",
                'practice': f"Chapter {chapter_num}: Applied Wisdom"
            }
            return chapter_titles.get(top_concept, f"Chapter {chapter_num}: Explorations")
        
        return f"Chapter {chapter_num}: Reflections"
    
    def export_book_draft(self, book_structure: Dict[str, Any]) -> str:
        """Export book as markdown draft"""
        book_id = book_structure['book_id']
        filename = f"book_{book_id}_{book_structure['title'].lower().replace(' ', '_')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Title page
            f.write(f"# {book_structure['title']}\n")
            f.write(f"## {book_structure['subtitle']}\n\n")
            f.write(f"*Generated from {book_structure['total_insights']} handwritten insights*\n")
            f.write(f"*{book_structure['total_words']:,} words*\n\n")
            f.write("---\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            for chapter in book_structure['chapters']:
                f.write(f"{chapter['number']}. {chapter['title']} "
                       f"({chapter['word_count']:,} words)\n")
            f.write("\n---\n\n")
            
            # Chapters
            for chapter in book_structure['chapters']:
                f.write(f"# {chapter['title']}\n\n")
                f.write(f"*{len(chapter['insights'])} insights, "
                       f"{chapter['word_count']:,} words, "
                       f"quality score: {chapter['avg_quality']:.2f}*\n\n")
                
                # Group insights into sections
                insights_per_section = max(3, len(chapter['insights']) // 5)
                section_num = 1
                
                for i in range(0, len(chapter['insights']), insights_per_section):
                    section_insights = chapter['insights'][i:i + insights_per_section]
                    
                    f.write(f"## Section {section_num}\n\n")
                    
                    for insight in section_insights:
                        f.write(f"### Insight from {insight['conversation_title']}\n")
                        f.write(f"*Quality: {insight['quality_score']:.2f} | "
                               f"Words: {insight['word_count']} | "
                               f"Date: {insight['timestamp'][:10] if insight['timestamp'] else 'Unknown'}*\n\n")
                        f.write(f"{insight['content']}\n\n")
                        f.write("---\n\n")
                    
                    section_num += 1
                
                f.write("\n\n")
        
        return str(filepath)
    
    def generate_all_books(self, quality_threshold: float = 0.2) -> List[str]:
        """Generate all 7 books automatically"""
        print("🏭 Starting automated book generation process...")
        
        # Extract all insights
        insights = self.extract_all_insights()
        
        # Organize by books  
        book_insights = self.organize_insights_by_books(insights)
        
        generated_books = []
        
        print(f"\n📚 Generating {len(self.BOOK_THEMES)} books...")
        
        for book_id in sorted(self.BOOK_THEMES.keys()):
            if book_id in book_insights:
                print(f"\n📖 Generating Book {book_id}: {self.BOOK_THEMES[book_id]['title']}")
                
                # Generate structure
                book_structure = self.generate_book_structure(book_id, book_insights[book_id])
                
                # Export draft
                filepath = self.export_book_draft(book_structure)
                generated_books.append(filepath)
                
                print(f"✅ Generated: {filepath}")
                print(f"   📊 {book_structure['total_insights']} insights, "
                      f"{book_structure['total_words']:,} words")
            else:
                print(f"⏭️  Skipping Book {book_id}: No matching insights found")
        
        return generated_books
    
    def generate_editor_prompts(self, book_files: List[str]) -> str:
        """Generate prompts for AI editor to refine the books"""
        prompts_file = self.output_dir / "editor_prompts.md"
        
        with open(prompts_file, 'w', encoding='utf-8') as f:
            f.write("# AI Editor Prompts for Book Refinement\n\n")
            f.write("Use these prompts to refine each generated book draft.\n\n")
            
            for i, book_file in enumerate(book_files, 1):
                book_path = Path(book_file)
                f.write(f"## Book {i}: {book_path.stem}\n\n")
                f.write("### Editor Prompt:\n")
                f.write(f"```\n")
                f.write(f"Please review and refine the book draft '{book_path.name}'. Focus on:\n\n")
                f.write("1. **Narrative Flow**: Ensure insights flow logically within chapters\n")
                f.write("2. **Thematic Coherence**: Group related insights more effectively\n") 
                f.write("3. **Chapter Transitions**: Add smooth transitions between chapters\n")
                f.write("4. **Content Organization**: Reorganize sections for better readability\n")
                f.write("5. **Duplicate Removal**: Identify and merge similar insights\n")
                f.write("6. **Quality Enhancement**: Elevate the most profound insights\n\n")
                f.write("Provide:\n")
                f.write("- Revised chapter structure\n")
                f.write("- Key insights to highlight\n") 
                f.write("- Suggested content reordering\n")
                f.write("- Editorial recommendations\n")
                f.write("```\n\n")
        
        return str(prompts_file)

def main():
    parser = argparse.ArgumentParser(description="Automated Book Factory - Generate 7 books from insights")
    parser.add_argument('--quality-threshold', type=float, default=0.2, 
                       help='Minimum quality threshold for insights (0.0-1.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be generated without creating files')
    
    args = parser.parse_args()
    
    try:
        factory = AutomatedBookFactory()
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - Analyzing without generating files")
            insights = factory.extract_all_insights()
            book_insights = factory.organize_insights_by_books(insights)
            
            print(f"\n📊 Would generate {len(book_insights)} books:")
            for book_id, insights_list in book_insights.items():
                theme = factory.BOOK_THEMES[book_id]
                print(f"  Book {book_id}: {theme['title']} ({len(insights_list)} insights)")
        else:
            print("🚀 PRODUCTION MODE - Generating all books")
            book_files = factory.generate_all_books(args.quality_threshold)
            
            print(f"\n✅ Generated {len(book_files)} books:")
            for book_file in book_files:
                print(f"   📚 {book_file}")
            
            # Generate editor prompts
            editor_prompts = factory.generate_editor_prompts(book_files)
            print(f"\n🤖 Editor prompts generated: {editor_prompts}")
            
            print(f"\n🎯 Next steps:")
            print(f"1. Review generated books in: {factory.output_dir}")
            print(f"2. Use editor prompts to refine content with AI")
            print(f"3. Run editorial review process")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()