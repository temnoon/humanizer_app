#!/usr/bin/env python3
"""
Book Builder - Writebook Integration
====================================

Creates structured books from curated essays, integrating with the Rails Writebook system.
Organizes essays into chapters, sections, and complete books by subject area.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import requests

from native_conversation_format import NativeConversation, ConversationCollection
from batch_curator import BatchCurator


class Chapter:
    """Represents a book chapter built from essays"""
    
    def __init__(self, title: str, subject_area: str):
        self.chapter_id = str(uuid.uuid4())
        self.title = title
        self.subject_area = subject_area
        self.essays = []
        self.total_word_count = 0
        self.estimated_reading_time = 0.0
        self.created_at = datetime.now()
    
    def add_essay(self, essay_data: Dict[str, Any]):
        """Add an essay to this chapter"""
        self.essays.append(essay_data)
        self.total_word_count += essay_data.get('content', {}).get('word_count', 0)
        self.estimated_reading_time = self.total_word_count / 250  # 250 WPM
    
    def to_writebook_section(self) -> Dict[str, Any]:
        """Convert chapter to Writebook section format"""
        
        # Combine all essay content into chapter content
        chapter_content = f"# {self.title}\n\n"
        
        for i, essay in enumerate(self.essays, 1):
            chapter_content += f"## {essay.get('title', f'Section {i}')}\n\n"
            
            # Add essay narrative
            narrative = essay.get('content', {}).get('narrative', '')
            if narrative:
                chapter_content += f"{narrative}\n\n"
            
            # Add reflection if it adds value
            reflection = essay.get('content', {}).get('reflection', '')
            if reflection and len(reflection) > 100:
                chapter_content += f"### Reflection\n\n{reflection}\n\n"
            
            chapter_content += "---\n\n"
        
        return {
            "title": self.title,
            "content": chapter_content,
            "position": None,  # Will be set when added to book
            "metadata": {
                "chapter_id": self.chapter_id,
                "subject_area": self.subject_area,
                "essay_count": len(self.essays),
                "word_count": self.total_word_count,
                "estimated_reading_time": self.estimated_reading_time,
                "created_at": self.created_at.isoformat()
            }
        }


class Book:
    """Represents a complete book built from chapters"""
    
    def __init__(self, title: str, subject_area: str, description: str = ""):
        self.book_id = str(uuid.uuid4())
        self.title = title
        self.subject_area = subject_area
        self.description = description
        self.chapters = []
        self.total_word_count = 0
        self.total_essays = 0
        self.estimated_reading_time = 0.0
        self.created_at = datetime.now()
        self.writebook_id = None  # Set when created in Rails
    
    def add_chapter(self, chapter: Chapter):
        """Add a chapter to this book"""
        self.chapters.append(chapter)
        self.total_word_count += chapter.total_word_count
        self.total_essays += len(chapter.essays)
        self.estimated_reading_time = self.total_word_count / 250  # 250 WPM
    
    def to_writebook_format(self) -> Dict[str, Any]:
        """Convert book to Writebook format for Rails integration"""
        
        # Create book introduction
        introduction = f"""# {self.title}

{self.description}

This book is a curated collection of AI-enhanced conversations and essays exploring {self.subject_area.lower()}. Each chapter presents unique perspectives and insights, transformed through the Lamish Projection Engine to create accessible yet profound explorations of complex topics.

**Book Statistics:**
- Chapters: {len(self.chapters)}
- Essays: {self.total_essays}
- Total Words: {self.total_word_count:,}
- Estimated Reading Time: {self.estimated_reading_time:.1f} minutes

---

"""
        
        return {
            "writebook": {
                "title": self.title,
                "description": self.description,
                "subject_area": self.subject_area,
                "introduction": introduction,
                "published": False,  # Start as draft
                "metadata": {
                    "book_id": self.book_id,
                    "total_word_count": self.total_word_count,
                    "total_essays": self.total_essays,
                    "estimated_reading_time": self.estimated_reading_time,
                    "created_at": self.created_at.isoformat(),
                    "source": "humanizer_ai_curation"
                }
            },
            "sections": [chapter.to_writebook_section() for chapter in self.chapters]
        }


class WritebookIntegration:
    """Integration with Rails Writebook system"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        # Add CSRF protection headers if needed
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_writebook(self, book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new writebook in Rails system"""
        try:
            response = self.session.post(
                f"{self.base_url}/writebooks",
                json=book_data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to create writebook: {e}")
            return None
    
    def add_section_to_writebook(self, writebook_id: int, section_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add a section to an existing writebook"""
        try:
            response = self.session.post(
                f"{self.base_url}/writebooks/{writebook_id}/sections",
                json={"section": section_data}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to add section: {e}")
            return None
    
    def list_writebooks(self) -> List[Dict[str, Any]]:
        """List existing writebooks"""
        try:
            response = self.session.get(f"{self.base_url}/writebooks")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to list writebooks: {e}")
            return []


class BookBuilder:
    """Main book building system"""
    
    def __init__(self, writebook_url: str = "http://localhost:3000"):
        self.curator = BatchCurator()
        self.writebook_integration = WritebookIntegration(writebook_url)
        self.output_dir = Path("./compiled_books")
        self.output_dir.mkdir(exist_ok=True)
        
        # Book building statistics
        self.stats = {
            'books_created': 0,
            'chapters_created': 0,
            'essays_compiled': 0,
            'total_word_count': 0,
            'writebooks_created': 0
        }
    
    async def build_book_from_topic(self,
                                  topic: str,
                                  max_chapters: int = 10,
                                  essays_per_chapter: int = 3,
                                  min_quality: float = 0.7,
                                  create_writebook: bool = True) -> Book:
        """Build a complete book from a topic"""
        
        print(f"📚 Building book for topic: '{topic}'")
        print(f"   Max chapters: {max_chapters}")
        print(f"   Essays per chapter: {essays_per_chapter}")
        print(f"   Min quality: {min_quality}")
        
        # Step 1: Curate high-quality content
        print("\n🎯 Curating high-quality content...")
        collection = await self.curator.discover_and_curate(
            topic=topic,
            max_conversations=max_chapters * essays_per_chapter * 2,  # Get extra for selection
            min_quality=min_quality,
            max_essays=max_chapters * essays_per_chapter
        )
        
        # Step 2: Load created essays
        essays = self._load_essays_from_collection(collection)
        if not essays:
            print("❌ No essays found to build book")
            return None
        
        print(f"   Loaded {len(essays)} essays")
        
        # Step 3: Group essays into chapters
        chapters = self._group_essays_into_chapters(essays, max_chapters, essays_per_chapter)
        
        # Step 4: Create book
        book_title = f"Explorations in {topic.title()}: AI-Curated Insights"
        book_description = f"""A curated collection of conversations and insights exploring {topic}. This book presents AI-enhanced perspectives on complex topics, making sophisticated ideas accessible through the Lamish Projection Engine. Each chapter offers unique viewpoints and deep reflections on {topic.lower()}, drawn from real conversations and transformed into coherent, engaging essays."""
        
        book = Book(
            title=book_title,
            subject_area=topic,
            description=book_description
        )
        
        for chapter in chapters:
            book.add_chapter(chapter)
        
        print(f"\n📖 Book created:")
        print(f"   Title: {book.title}")
        print(f"   Chapters: {len(book.chapters)}")
        print(f"   Total essays: {book.total_essays}")
        print(f"   Word count: {book.total_word_count:,}")
        print(f"   Reading time: {book.estimated_reading_time:.1f} minutes")
        
        # Step 5: Save book locally
        book_file = self.output_dir / f"book_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(book_file, 'w') as f:
            json.dump(book.to_writebook_format(), f, indent=2, default=str)
        
        print(f"💾 Book saved locally: {book_file}")
        
        # Step 6: Create in Writebook system if requested
        if create_writebook:
            writebook_result = await self._create_in_writebook_system(book)
            if writebook_result:
                book.writebook_id = writebook_result.get('id')
                print(f"📚 Writebook created with ID: {book.writebook_id}")
        
        # Update statistics
        self.stats['books_created'] += 1
        self.stats['chapters_created'] += len(book.chapters)
        self.stats['essays_compiled'] += book.total_essays
        self.stats['total_word_count'] += book.total_word_count
        if book.writebook_id:
            self.stats['writebooks_created'] += 1
        
        return book
    
    def _load_essays_from_collection(self, collection: ConversationCollection) -> List[Dict[str, Any]]:
        """Load essays created by the curator"""
        essays = []
        
        # Look for essay files in the curator's output
        essay_files = list(self.curator.essays_dir.glob('*.json'))
        
        for essay_file in essay_files:
            try:
                with open(essay_file, 'r') as f:
                    essay_data = json.load(f)
                    # Only include essays that match our collection
                    if essay_data.get('topic') == collection.subject_focus:
                        essays.append(essay_data)
            except Exception as e:
                print(f"Warning: Could not load essay {essay_file}: {e}")
        
        # Sort by quality score
        essays.sort(key=lambda x: x.get('metadata', {}).get('quality_score', 0.0), reverse=True)
        
        return essays
    
    def _group_essays_into_chapters(self, 
                                  essays: List[Dict[str, Any]], 
                                  max_chapters: int,
                                  essays_per_chapter: int) -> List[Chapter]:
        """Group essays into logical chapters"""
        
        chapters = []
        essays_used = 0
        
        # Simple grouping strategy: group by target audience and quality
        audience_groups = {}
        for essay in essays:
            audience = essay.get('metadata', {}).get('target_audience', 'general_public')
            if audience not in audience_groups:
                audience_groups[audience] = []
            audience_groups[audience].append(essay)
        
        chapter_num = 1
        for audience, audience_essays in audience_groups.items():
            if len(chapters) >= max_chapters:
                break
            
            # Create chapters for this audience
            for i in range(0, len(audience_essays), essays_per_chapter):
                if len(chapters) >= max_chapters:
                    break
                
                chapter_essays = audience_essays[i:i + essays_per_chapter]
                
                # Create chapter title based on content
                chapter_title = self._generate_chapter_title(chapter_essays, chapter_num, audience)
                
                chapter = Chapter(
                    title=chapter_title,
                    subject_area=essays[0].get('topic', 'General')
                )
                
                for essay in chapter_essays:
                    chapter.add_essay(essay)
                    essays_used += 1
                
                chapters.append(chapter)
                chapter_num += 1
        
        print(f"   Created {len(chapters)} chapters from {essays_used} essays")
        
        return chapters
    
    def _generate_chapter_title(self, essays: List[Dict[str, Any]], chapter_num: int, audience: str) -> str:
        """Generate an appropriate chapter title"""
        
        # Extract common themes from essay titles
        titles = [essay.get('title', '') for essay in essays]
        
        # Simple approach: use most common significant words
        import re
        from collections import Counter
        
        all_words = []
        for title in titles:
            words = re.findall(r'\b[A-Z][a-z]+\b', title)  # Capitalized words
            all_words.extend(words)
        
        if all_words:
            common_words = Counter(all_words).most_common(3)
            theme_words = [word for word, count in common_words if count > 1]
            
            if theme_words:
                return f"Chapter {chapter_num}: {' and '.join(theme_words[:2])}"
        
        # Fallback to audience-based titles
        audience_titles = {
            'academic_researchers': f"Chapter {chapter_num}: Advanced Perspectives",
            'educated_general_public': f"Chapter {chapter_num}: Accessible Insights",
            'general_public': f"Chapter {chapter_num}: Fundamental Concepts"
        }
        
        return audience_titles.get(audience, f"Chapter {chapter_num}: Collected Essays")
    
    async def _create_in_writebook_system(self, book: Book) -> Optional[Dict[str, Any]]:
        """Create the book in the Rails Writebook system"""
        
        print(f"📚 Creating writebook in Rails system...")
        
        # Convert to writebook format
        writebook_data = book.to_writebook_format()
        
        # Create the writebook first
        writebook_result = self.writebook_integration.create_writebook(
            writebook_data['writebook']
        )
        
        if not writebook_result:
            print("❌ Failed to create writebook")
            return None
        
        writebook_id = writebook_result.get('id')
        print(f"   ✅ Writebook created with ID: {writebook_id}")
        
        # Add sections (chapters)
        for i, section_data in enumerate(writebook_data['sections'], 1):
            section_data['position'] = i
            
            section_result = self.writebook_integration.add_section_to_writebook(
                writebook_id, 
                section_data
            )
            
            if section_result:
                print(f"   ✅ Added chapter {i}: {section_data['title']}")
            else:
                print(f"   ❌ Failed to add chapter {i}")
        
        return writebook_result
    
    async def build_subject_library(self, 
                                  subjects: List[str],
                                  books_per_subject: int = 2) -> List[Book]:
        """Build a library of books across multiple subjects"""
        
        print(f"📚 Building subject library:")
        print(f"   Subjects: {subjects}")
        print(f"   Books per subject: {books_per_subject}")
        
        library = []
        
        for subject in subjects:
            print(f"\n🎯 Building books for subject: {subject}")
            
            for book_num in range(books_per_subject):
                print(f"   Building book {book_num + 1}/{books_per_subject}...")
                
                book = await self.build_book_from_topic(
                    topic=subject,
                    max_chapters=8,
                    essays_per_chapter=3,
                    min_quality=0.7,
                    create_writebook=True
                )
                
                if book:
                    library.append(book)
        
        # Save library index
        library_index = {
            'library_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'subjects': subjects,
            'total_books': len(library),
            'books': [
                {
                    'book_id': book.book_id,
                    'title': book.title,
                    'subject_area': book.subject_area,
                    'chapters': len(book.chapters),
                    'word_count': book.total_word_count,
                    'writebook_id': book.writebook_id
                }
                for book in library
            ]
        }
        
        library_file = self.output_dir / f"subject_library_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(library_file, 'w') as f:
            json.dump(library_index, f, indent=2, default=str)
        
        print(f"\n🎉 Subject library completed!")
        print(f"   Total books created: {len(library)}")
        print(f"   Library index saved: {library_file}")
        
        return library
    
    def get_book_statistics(self) -> Dict[str, Any]:
        """Get book building statistics"""
        return {
            **self.stats,
            'output_directory': str(self.output_dir),
            'books_on_disk': len(list(self.output_dir.glob('book_*.json'))),
            'libraries_created': len(list(self.output_dir.glob('subject_library_*.json')))
        }


async def main():
    """Main CLI interface for book building"""
    parser = argparse.ArgumentParser(description="Book Builder - Create Books from Curated Essays")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build single book
    build_parser = subparsers.add_parser('build', help='Build a book from a topic')
    build_parser.add_argument('topic', help='Topic to build book around')
    build_parser.add_argument('--max-chapters', type=int, default=10, help='Maximum chapters')
    build_parser.add_argument('--essays-per-chapter', type=int, default=3, help='Essays per chapter')
    build_parser.add_argument('--min-quality', type=float, default=0.7, help='Minimum quality threshold')
    build_parser.add_argument('--no-writebook', action='store_true', help='Skip Writebook creation')
    build_parser.add_argument('--writebook-url', default='http://localhost:3000', help='Writebook Rails URL')
    
    # Build library
    library_parser = subparsers.add_parser('library', help='Build a library of books')
    library_parser.add_argument('subjects', nargs='+', help='List of subjects for the library')
    library_parser.add_argument('--books-per-subject', type=int, default=2, help='Books per subject')
    library_parser.add_argument('--writebook-url', default='http://localhost:3000', help='Writebook Rails URL')
    
    # List writebooks
    list_parser = subparsers.add_parser('list', help='List existing writebooks')
    list_parser.add_argument('--writebook-url', default='http://localhost:3000', help='Writebook Rails URL')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Show book building statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'build':
            builder = BookBuilder(args.writebook_url)
            
            book = await builder.build_book_from_topic(
                topic=args.topic,
                max_chapters=args.max_chapters,
                essays_per_chapter=args.essays_per_chapter,
                min_quality=args.min_quality,
                create_writebook=not args.no_writebook
            )
            
            if book:
                print(f"\n🎉 Book Building Summary:")
                print(f"   Title: {book.title}")
                print(f"   Chapters: {len(book.chapters)}")
                print(f"   Essays: {book.total_essays}")
                print(f"   Word count: {book.total_word_count:,}")
                if book.writebook_id:
                    print(f"   Writebook ID: {book.writebook_id}")
        
        elif args.command == 'library':
            builder = BookBuilder(args.writebook_url)
            
            library = await builder.build_subject_library(
                subjects=args.subjects,
                books_per_subject=args.books_per_subject
            )
            
            print(f"\n🎉 Library Building Summary:")
            print(f"   Subjects: {len(args.subjects)}")
            print(f"   Books created: {len(library)}")
            total_word_count = sum(book.total_word_count for book in library)
            print(f"   Total word count: {total_word_count:,}")
        
        elif args.command == 'list':
            integration = WritebookIntegration(args.writebook_url)
            writebooks = integration.list_writebooks()
            
            print(f"\n📚 Existing Writebooks:")
            for wb in writebooks:
                print(f"   ID: {wb.get('id')} | {wb.get('title', 'Untitled')}")
                print(f"      Subject: {wb.get('subject_area', 'Unknown')}")
                print(f"      Created: {wb.get('created_at', 'Unknown')[:19]}")
                print()
        
        elif args.command == 'stats':
            builder = BookBuilder()
            stats = builder.get_book_statistics()
            
            print(f"\n📊 Book Building Statistics:")
            for key, value in stats.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Book building interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())