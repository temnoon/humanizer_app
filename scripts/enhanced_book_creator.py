#!/usr/bin/env python3
"""
Enhanced Book Creator - Interactive Interface for Creating Books with Joplin Export
Integrates with existing Humanizer book generation tools
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the lighthouse directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'humanizer_api', 'lighthouse'))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  PostgreSQL not available, some features will be limited")

from joplin_export_generator_fixed import JoplinExportGeneratorFixed


class EnhancedBookCreator:
    def __init__(self):
        self.selected_content = []
        self.book_structure = {}
        self.connection = None
        
        # Try to connect to database
        if POSTGRES_AVAILABLE:
            self.connect_to_database()
            
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="humanizer_archive",
                user="postgres",
                password="password"
            )
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            self.connection = None
            
    def launch_interactive_creator(self):
        """Launch interactive book creation interface"""
        print("🚀 Humanizer Enhanced Book Creator")
        print("=" * 60)
        print("Create publication-ready books with Joplin integration")
        print()
        
        while True:
            print("📋 Book Creation Options:")
            print("1. 🤖 Use Advanced Book Generation (auto-curated)")
            print("2. 📝 Manual chunk selection")
            print("3. 💬 Conversation-based selection")
            print("4. 📂 Import existing book")
            print("5. 🔍 Browse available content")
            print("6. ❌ Exit")
            print()
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                return self.use_advanced_generation()
            elif choice == "2":
                return self.manual_chunk_selection()
            elif choice == "3":
                return self.conversation_selection()
            elif choice == "4":
                return self.import_existing_book()
            elif choice == "5":
                self.browse_available_content()  
            elif choice == "6":
                print("👋 Goodbye!")
                return None
            else:
                print("❌ Invalid option. Please try again.\n")
                
    def use_advanced_generation(self):
        """Use existing advanced book generation system"""
        print("\n🤖 Advanced Book Generation")
        print("-" * 30)
        
        # Get parameters for advanced generation
        print("Configure advanced book generation:")
        min_quality = float(input("Minimum quality threshold (0.4): ") or "0.4")
        max_books = int(input("Maximum number of books (3): ") or "3")
        analyze_only = input("Analysis only? (y/N): ").lower().startswith('y')
        
        # Call existing advanced book factory
        try:
            from advanced_book_factory import AdvancedBookFactory
            
            factory = AdvancedBookFactory()
            
            if analyze_only:
                print("\n📊 Running analysis...")
                results = factory.analyze_content_potential()
                self.display_analysis_results(results)
                
                if input("\nProceed with book generation? (y/N): ").lower().startswith('y'):
                    books = factory.generate_books(min_quality=min_quality, max_books=max_books)
                else:
                    return None
            else:
                books = factory.generate_books(min_quality=min_quality, max_books=max_books)
                
            # Offer Joplin export
            if books:
                print(f"\n✅ Generated {len(books)} books")
                self.offer_joplin_export(books)
                
            return books
            
        except ImportError:
            print("❌ Advanced book factory not available")
            return None
        except Exception as e:
            print(f"❌ Error in advanced generation: {e}")
            return None
            
    def manual_chunk_selection(self):
        """Interactive chunk selection interface"""
        print("\n📝 Manual Chunk Selection")
        print("-" * 30)
        
        if not self.connection:
            print("❌ Database connection required for chunk selection")
            return None
            
        # Get available chunks with quality scores
        chunks = self.get_quality_chunks()
        
        if not chunks:
            print("❌ No chunks available")
            return None
            
        print(f"\n📚 Available High-Quality Chunks ({len(chunks)} total)")
        print("=" * 70)
        
        selected_chunks = []
        page_size = 10
        current_page = 0
        
        while True:
            # Display current page
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(chunks))
            
            print(f"\nPage {current_page + 1} of {(len(chunks) - 1) // page_size + 1}")
            print("-" * 70)
            
            for i in range(start_idx, end_idx):
                chunk = chunks[i]
                quality = chunk.get('quality_score', 0)
                source = chunk.get('source_info', 'Unknown')
                preview = chunk.get('content', '')[:80] + "..."
                
                selected_marker = "✓" if chunk in selected_chunks else " "
                
                print(f"{selected_marker} {i+1:3d}. [Q:{quality:.2f}] {source}")
                print(f"      {preview}")
                print()
                
            # Navigation options
            print("Options:")
            print("s <numbers> - Select chunks (e.g., 's 1,3,5')")
            print("d <numbers> - Deselect chunks")
            print("n - Next page")
            print("p - Previous page") 
            print("v <number> - View full chunk")
            print("c - Create book from selected chunks")
            print("q - Quit selection")
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice.startswith('s '):
                # Select chunks
                try:
                    numbers = [int(x.strip()) - 1 for x in choice[2:].split(',')]
                    for num in numbers:
                        if 0 <= num < len(chunks) and chunks[num] not in selected_chunks:
                            selected_chunks.append(chunks[num])
                    print(f"✅ Selected {len(selected_chunks)} chunks total")
                except ValueError:
                    print("❌ Invalid format. Use: s 1,2,3")
                    
            elif choice.startswith('d '):
                # Deselect chunks
                try:
                    numbers = [int(x.strip()) - 1 for x in choice[2:].split(',')]
                    for num in numbers:
                        if 0 <= num < len(chunks) and chunks[num] in selected_chunks:
                            selected_chunks.remove(chunks[num])
                    print(f"✅ {len(selected_chunks)} chunks selected")
                except ValueError:
                    print("❌ Invalid format. Use: d 1,2,3")
                    
            elif choice.startswith('v '):
                # View full chunk
                try:
                    num = int(choice[2:]) - 1
                    if 0 <= num < len(chunks):
                        self.display_full_chunk(chunks[num])
                except ValueError:
                    print("❌ Invalid chunk number")
                    
            elif choice == 'n':
                if end_idx < len(chunks):
                    current_page += 1
                else:
                    print("❌ Already on last page")
                    
            elif choice == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    print("❌ Already on first page")
                    
            elif choice == 'c':
                if selected_chunks:
                    return self.create_book_from_chunks(selected_chunks)
                else:
                    print("❌ No chunks selected")
                    
            elif choice == 'q':
                return None
                
    def conversation_selection(self):
        """Select entire conversations for book creation"""
        print("\n💬 Conversation-Based Selection")
        print("-" * 30)
        
        if not self.connection:
            print("❌ Database connection required")
            return None
            
        # Get notebook conversations (like your existing notebook_transcript_browser)
        conversations = self.get_notebook_conversations()
        
        if not conversations:
            print("❌ No notebook conversations found")
            return None
            
        print(f"\n📱 Available Notebook Conversations ({len(conversations)} total)")
        print("=" * 70)
        
        for i, conv in enumerate(conversations):
            title = conv.get('title', 'Untitled')[:50]
            message_count = conv.get('message_count', 0)
            quality_avg = conv.get('avg_quality', 0)
            
            print(f"{i+1:3d}. {title}")
            print(f"     Messages: {message_count}, Avg Quality: {quality_avg:.2f}")
            print()
            
        print("Enter conversation numbers to include (comma-separated):")
        selection_input = input("Conversations: ").strip()
        
        if not selection_input:
            return None
            
        try:
            indices = [int(x.strip()) - 1 for x in selection_input.split(',')]
            selected_conversations = [conversations[i] for i in indices if 0 <= i < len(conversations)]
            
            if selected_conversations:
                return self.create_book_from_conversations(selected_conversations)
            else:
                print("❌ No valid conversations selected")
                return None
                
        except ValueError:
            print("❌ Invalid format. Use numbers separated by commas")
            return None
            
    def import_existing_book(self):
        """Import and potentially enhance existing book"""
        print("\n📂 Import Existing Book")
        print("-" * 30)
        
        # Look for existing books
        book_dirs = [
            Path("humanizer_api/lighthouse/advanced_books"),
            Path("humanizer_api/lighthouse/automated_books"),
            Path("humanizer_api/lighthouse/complete_book_production")
        ]
        
        existing_books = []
        for book_dir in book_dirs:
            if book_dir.exists():
                for book_file in book_dir.glob("*.md"):
                    existing_books.append(book_file)
                    
        if not existing_books:
            print("❌ No existing books found")
            return None
            
        print("📚 Found existing books:")
        for i, book_path in enumerate(existing_books):
            print(f"{i+1:3d}. {book_path.name}")
            
        try:
            choice = int(input("\nSelect book to import: ")) - 1
            if 0 <= choice < len(existing_books):
                selected_book = existing_books[choice]
                
                # Offer direct Joplin export
                print(f"\n📖 Selected: {selected_book.name}")
                if input("Export directly to Joplin? (Y/n): ").lower() != 'n':
                    return self.export_to_joplin(str(selected_book))
                    
                return selected_book
            else:
                print("❌ Invalid selection")
                return None
                
        except ValueError:
            print("❌ Invalid input")
            return None
            
    def browse_available_content(self):
        """Browse available content without selection"""
        print("\n🔍 Content Browser")
        print("-" * 30)
        
        if not self.connection:
            print("❌ Database connection required")
            return
            
        # Show content statistics
        stats = self.get_content_statistics()
        
        print("📊 Content Statistics:")
        print(f"  • Total conversations: {stats.get('total_conversations', 0)}")
        print(f"  • Notebook conversations: {stats.get('notebook_conversations', 0)}")
        print(f"  • High-quality chunks (>0.6): {stats.get('high_quality_chunks', 0)}")
        print(f"  • Medium-quality chunks (0.4-0.6): {stats.get('medium_quality_chunks', 0)}")
        print(f"  • Total analyzed content: {stats.get('total_content', 0)} pieces")
        
        print("\n🎯 Quality Distribution:")
        quality_ranges = stats.get('quality_distribution', {})
        for range_name, count in quality_ranges.items():
            print(f"  • {range_name}: {count}")
            
        input("\nPress Enter to continue...")
        
    def get_quality_chunks(self) -> List[Dict[str, Any]]:
        """Get chunks with quality scores from database"""
        if not self.connection:
            return []
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Simplified query to get quality content
                cursor.execute("""
                    SELECT 
                        ac.id,
                        ac.title,
                        ac.body_text as content,
                        ac.source_metadata,
                        COALESCE(ac.source_metadata->>'quality_score', '0')::float as quality_score,
                        ac.timestamp,
                        CASE 
                            WHEN ac.source_metadata->>'gizmo_id' = 'g-T7bW2qVzx' THEN 'Notebook Transcript'
                            ELSE 'Conversation'
                        END as source_type
                    FROM archived_content ac
                    WHERE ac.body_text IS NOT NULL
                        AND LENGTH(ac.body_text) > 100
                        AND COALESCE(ac.source_metadata->>'quality_score', '0')::float > 0.3
                    ORDER BY COALESCE(ac.source_metadata->>'quality_score', '0')::float DESC
                    LIMIT 500
                """)
                
                results = cursor.fetchall()
                
                chunks = []
                for row in results:
                    chunk = {
                        'id': row['id'],
                        'content': row['content'],
                        'quality_score': row['quality_score'],
                        'source_info': f"{row['source_type']} - {row['timestamp'].strftime('%Y-%m-%d') if row['timestamp'] else 'Unknown'}",
                        'metadata': row['source_metadata'] or {}
                    }
                    chunks.append(chunk)
                    
                return chunks
                
        except Exception as e:
            print(f"❌ Error fetching chunks: {e}")
            return []
            
    def get_notebook_conversations(self) -> List[Dict[str, Any]]:
        """Get notebook conversations from database"""
        if not self.connection:
            return []
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get notebook conversations (Journal Recognizer OCR)
                cursor.execute("""
                    SELECT 
                        parent.id,
                        COALESCE(parent.title, 'Untitled') as title,
                        parent.timestamp,
                        COUNT(child.id) as message_count,
                        AVG(COALESCE(child.source_metadata->>'quality_score', '0')::float) as avg_quality
                    FROM archived_content parent
                    JOIN archived_content child ON parent.id = child.parent_id
                    WHERE child.source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
                        AND child.content_type = 'message'
                        AND child.body_text IS NOT NULL
                    GROUP BY parent.id, parent.title, parent.timestamp
                    HAVING COUNT(child.id) > 2
                    ORDER BY avg_quality DESC, message_count DESC
                    LIMIT 100
                """)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Error fetching conversations: {e}")
            return []
            
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics from database"""
        if not self.connection:
            return {}
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                stats = {}
                
                # Total conversations
                cursor.execute("SELECT COUNT(*) FROM archived_content WHERE content_type = 'conversation'")
                stats['total_conversations'] = cursor.fetchone()[0]
                
                # Notebook conversations
                cursor.execute("""
                    SELECT COUNT(DISTINCT parent_id) FROM archived_content 
                    WHERE source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
                """)
                stats['notebook_conversations'] = cursor.fetchone()[0]
                
                # Quality distribution
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN COALESCE(source_metadata->>'quality_score', '0')::float >= 0.6 THEN 'High (0.6+)'
                            WHEN COALESCE(source_metadata->>'quality_score', '0')::float >= 0.4 THEN 'Medium (0.4-0.6)'
                            WHEN COALESCE(source_metadata->>'quality_score', '0')::float > 0 THEN 'Low (0.1-0.4)'
                            ELSE 'Unanalyzed'
                        END as quality_range,
                        COUNT(*) as count
                    FROM archived_content
                    WHERE body_text IS NOT NULL
                    GROUP BY quality_range
                """)
                
                quality_dist = {}
                for row in cursor.fetchall():
                    quality_dist[row[0]] = row[1]
                stats['quality_distribution'] = quality_dist
                
                # High/medium quality counts
                stats['high_quality_chunks'] = quality_dist.get('High (0.6+)', 0)
                stats['medium_quality_chunks'] = quality_dist.get('Medium (0.4-0.6)', 0)
                stats['total_content'] = sum(quality_dist.values())
                
                return stats
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
            
    def display_full_chunk(self, chunk: Dict[str, Any]):
        """Display full chunk content"""
        print("\n" + "=" * 80)
        print(f"📄 Chunk Details")
        print("=" * 80)
        print(f"Quality Score: {chunk.get('quality_score', 0):.2f}")
        print(f"Source: {chunk.get('source_info', 'Unknown')}")
        print("-" * 80)
        print(chunk.get('content', 'No content'))
        print("=" * 80)
        input("Press Enter to continue...")
        
    def display_analysis_results(self, results: Dict[str, Any]):
        """Display analysis results from advanced generation"""
        print("\n📊 Content Analysis Results")
        print("=" * 50)
        
        if 'total_chunks' in results:
            print(f"Total content pieces: {results['total_chunks']}")
        if 'quality_threshold' in results:
            print(f"Quality threshold: {results['quality_threshold']}")
        if 'themes' in results:
            print(f"Identified themes: {', '.join(results['themes'])}")
        if 'estimated_books' in results:
            print(f"Estimated books: {results['estimated_books']}")
            
    def create_book_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Create book from selected chunks"""
        print(f"\n📖 Creating book from {len(chunks)} selected chunks...")
        
        # Get book metadata
        title = input("Book title: ").strip()
        if not title:
            title = f"Curated Insights - {datetime.now().strftime('%Y-%m-%d')}"
            
        author = input("Author (Humanizer Generated): ").strip() or "Humanizer Generated"
        description = input("Brief description: ").strip()
        
        # Simple thematic organization
        book_data = {
            'title': title,
            'metadata': {
                'title': title,
                'author': author,
                'description': description,
                'created': datetime.now().isoformat(),
                'source_chunks': len(chunks),
                'generation_method': 'manual_curation'
            },
            'chapters': self.organize_chunks_into_chapters(chunks)
        }
        
        # Save as markdown file
        output_dir = Path("humanizer_api/lighthouse/curated_books")
        output_dir.mkdir(exist_ok=True)
        
        book_file = output_dir / f"{title.replace(' ', '_').lower()}.md"
        self.write_book_markdown(book_data, book_file)
        
        print(f"✅ Book created: {book_file}")
        
        # Offer Joplin export
        if input("Export to Joplin format? (Y/n): ").lower() != 'n':
            self.export_to_joplin(str(book_file))
            
        return str(book_file)
        
    def create_book_from_conversations(self, conversations: List[Dict[str, Any]]) -> str:
        """Create book from selected conversations"""
        print(f"\n📖 Creating book from {len(conversations)} conversations...")
        
        # This would integrate with your existing conversation processing
        # For now, create a simple structure
        
        title = input("Book title: ").strip()
        if not title:
            title = f"Notebook Insights - {datetime.now().strftime('%Y-%m-%d')}"
            
        # Create basic book structure
        book_data = {
            'title': title,
            'metadata': {
                'title': title,
                'author': 'Humanizer Generated',
                'created': datetime.now().isoformat(),
                'source_conversations': len(conversations),
                'generation_method': 'conversation_curation'
            },
            'chapters': self.organize_conversations_into_chapters(conversations)
        }
        
        # Save and offer export
        output_dir = Path("humanizer_api/lighthouse/curated_books")
        output_dir.mkdir(exist_ok=True)
        
        book_file = output_dir / f"{title.replace(' ', '_').lower()}.md"
        self.write_book_markdown(book_data, book_file)
        
        print(f"✅ Book created: {book_file}")
        
        if input("Export to Joplin format? (Y/n): ").lower() != 'n':
            self.export_to_joplin(str(book_file))
            
        return str(book_file)
        
    def organize_chunks_into_chapters(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Organize chunks into chapters by theme/quality"""
        # Simple organization by quality tiers
        high_quality = [c for c in chunks if c.get('quality_score', 0) >= 0.7]
        medium_quality = [c for c in chunks if 0.4 <= c.get('quality_score', 0) < 0.7]
        
        chapters = []
        
        if high_quality:
            chapters.append({
                'title': 'Chapter 1: Premium Insights',
                'content': [self.format_chunk_content(chunk) for chunk in high_quality]
            })
            
        if medium_quality:
            chapters.append({
                'title': 'Chapter 2: Core Insights',
                'content': [self.format_chunk_content(chunk) for chunk in medium_quality]
            })
            
        return chapters
        
    def organize_conversations_into_chapters(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Organize conversations into chapters"""
        chapters = []
        
        for i, conv in enumerate(conversations):
            chapters.append({
                'title': f'Chapter {i+1}: {conv.get("title", "Untitled")}',
                'content': [f"Content from conversation {conv['id']} will be extracted here"]
            })
            
        return chapters
        
    def format_chunk_content(self, chunk: Dict[str, Any]) -> str:
        """Format chunk for book inclusion"""
        content = chunk.get('content', '')
        quality = chunk.get('quality_score', 0)
        source = chunk.get('source_info', 'Unknown')
        
        return f"""
<!-- Narrative Chunk: {chunk.get('id', 'unknown')} -->
:::{{{chunk.get('id', 'chunk_unknown')}}}
**[Quality: {quality:.2f} | Source: {source}]**

{content}

**[Humanizer Bridge Ready]**
*This content can be analyzed and enhanced with the Humanizer Bridge Plugin*
:::
"""
        
    def write_book_markdown(self, book_data: Dict[str, Any], output_file: Path):
        """Write book data to markdown file"""
        content = f"""---
title: "{book_data['title']}"
author: "{book_data['metadata']['author']}"
created: "{book_data['metadata']['created']}"
type: "book"
format_version: "1.0"
generation_method: "{book_data['metadata']['generation_method']}"
source_count: {book_data['metadata'].get('source_chunks', 0)}
humanizer_book: true
---

# {book_data['title']}

{book_data['metadata'].get('description', 'Generated by Humanizer Lighthouse')}

"""
        
        for chapter in book_data['chapters']:
            content += f"\n## {chapter['title']}\n\n"
            for section_content in chapter['content']:
                content += f"{section_content}\n\n"
                
        content += """
---
*Generated by Humanizer Lighthouse Enhanced Book Creator*
*Ready for editing in Joplin with Humanizer Bridge Plugin*
"""
        
        output_file.write_text(content, encoding='utf-8')
        
    def offer_joplin_export(self, books: List[str]):
        """Offer to export generated books to Joplin"""
        if not books:
            return
            
        print(f"\n📤 Export {len(books)} books to Joplin?")
        for i, book_path in enumerate(books):
            print(f"  {i+1}. {Path(book_path).name}")
            
        if input("Export all to Joplin? (Y/n): ").lower() != 'n':
            for book_path in books:
                self.export_to_joplin(book_path)
                
    def export_to_joplin(self, book_path: str) -> str:
        """Export book to Joplin format"""
        try:
            generator = JoplinExportGeneratorFixed()
            export_file = generator.generate_from_book_file(book_path)
            
            print(f"✅ Joplin export created: {export_file}")
            print("\n📋 Next steps:")
            print("1. Open Joplin")
            print("2. Go to File → Import")
            print(f"3. Select: {export_file}")
            print("4. Your book will appear as a structured notebook!")
            
            return export_file
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return ""


def main():
    parser = argparse.ArgumentParser(description='Enhanced Book Creator with Joplin Integration')
    parser.add_argument('--mode', choices=['interactive', 'advanced', 'export'], 
                       default='interactive', help='Creation mode')
    parser.add_argument('--book-file', help='Book file to export (for export mode)')
    parser.add_argument('--output-dir', help='Output directory')
    
    args = parser.parse_args()
    
    creator = EnhancedBookCreator()
    
    if args.mode == 'interactive':
        result = creator.launch_interactive_creator()
        if result:
            print(f"\n🎉 Book creation completed!")
    elif args.mode == 'advanced':
        result = creator.use_advanced_generation()
    elif args.mode == 'export':
        if args.book_file:
            creator.export_to_joplin(args.book_file)
        else:
            print("❌ --book-file required for export mode")
            
    return 0


if __name__ == '__main__':
    sys.exit(main())