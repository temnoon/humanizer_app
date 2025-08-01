#!/usr/bin/env python3
"""
Fixed Joplin Export Generator for Humanizer Books
Creates correct .jex format compatible with Joplin import
Based on Joplin's actual export format specification
"""

import json
import tarfile
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import sys
import os

# Add the lighthouse directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'humanizer_api', 'lighthouse'))

class JoplinExportGeneratorFixed:
    def __init__(self):
        self.items = []
        
    def generate_from_book_file(self, book_file_path: str, output_dir: str = None) -> str:
        """Generate Joplin export from existing book markdown file"""
        book_path = Path(book_file_path)
        
        if not book_path.exists():
            raise FileNotFoundError(f"Book file not found: {book_file_path}")
            
        print(f"📚 Processing book: {book_path.name}")
        
        # Parse existing book file
        book_content = book_path.read_text(encoding='utf-8')
        book_data = self.parse_book_markdown(book_content, book_path.stem)
        
        # Generate Joplin items
        self.create_joplin_items(book_data)
        
        # Create output directory
        if output_dir is None:
            output_dir = book_path.parent / 'joplin_exports'
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate .jex file
        export_file = output_path / f"{book_data['title'].replace(' ', '_')}.jex"
        self.write_jex_file(export_file)
        
        print(f"✅ Joplin export created: {export_file}")
        return str(export_file)
        
    def parse_book_markdown(self, content: str, default_title: str) -> Dict[str, Any]:
        """Parse book markdown file to extract structure and metadata"""
        lines = content.split('\n')
        
        # Initialize book data
        book_data = {
            'title': default_title,
            'metadata': {},
            'chapters': [],
            'current_chapter': None,
            'current_section': None
        }
        
        # Parse YAML frontmatter if present
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end > 0:
                frontmatter = content[3:frontmatter_end].strip()
                try:
                    import yaml
                    metadata = yaml.safe_load(frontmatter)
                    book_data['metadata'] = metadata
                    if 'title' in metadata:
                        book_data['title'] = metadata['title']
                except ImportError:
                    print("⚠️  YAML not available, using simple frontmatter parsing")
                    # Simple parsing for title
                    for line in frontmatter.split('\n'):
                        if line.strip().startswith('title:'):
                            title = line.split('title:', 1)[1].strip().strip('"\'')
                            if title:
                                book_data['title'] = title
                except Exception as e:
                    print(f"⚠️  Error parsing frontmatter: {e}")
        
        # Parse content structure
        current_content = []
        
        for line in lines:
            line = line.rstrip()
            
            # Skip frontmatter
            if line == '---' and len(book_data['chapters']) == 0:
                continue
                
            # Chapter headers (# Chapter X:)
            if line.startswith('# ') and ('chapter' in line.lower() or line.startswith('# Chapter')):
                # Save previous section/chapter
                if current_content:
                    self._save_current_content(book_data, current_content)
                    current_content = []
                
                # Create new chapter
                chapter_title = line[2:].strip()
                chapter = {
                    'title': chapter_title,
                    'sections': [],
                    'content': []
                }
                book_data['chapters'].append(chapter)
                book_data['current_chapter'] = chapter
                book_data['current_section'] = None
                
            # Section headers (## Section X.X:)
            elif line.startswith('## ') and book_data['current_chapter']:
                # Save previous section content
                if current_content:
                    self._save_current_content(book_data, current_content)
                    current_content = []
                
                # Create new section
                section_title = line[3:].strip()
                section = {
                    'title': section_title,
                    'content': []
                }
                book_data['current_chapter']['sections'].append(section)
                book_data['current_section'] = section
                
            # Regular content
            else:
                current_content.append(line)
        
        # Save final content
        if current_content:
            self._save_current_content(book_data, current_content)
            
        return book_data
        
    def _save_current_content(self, book_data: Dict[str, Any], content: List[str]):
        """Save current content to appropriate section or chapter"""
        content_text = '\n'.join(content).strip()
        if not content_text:
            return
            
        if book_data['current_section']:
            book_data['current_section']['content'].append(content_text)
        elif book_data['current_chapter']:
            book_data['current_chapter']['content'].append(content_text)
            
    def create_joplin_items(self, book_data: Dict[str, Any]):
        """Create Joplin items in correct format"""
        # Create main book folder
        book_folder = self.create_folder(
            title=book_data['title'],
            parent_id=''
        )
        
        # Create book metadata note
        metadata_note = self.create_note(
            title=f"{book_data['title']} - Book Information",
            body=self.generate_metadata_content(book_data),
            parent_id=book_folder['id']
        )
        
        # Create chapters
        for i, chapter in enumerate(book_data.get('chapters', [])):
            chapter_folder = self.create_folder(
                title=chapter['title'],
                parent_id=book_folder['id']
            )
            
            # If chapter has sections, create section notes
            if chapter.get('sections'):
                for section in chapter['sections']:
                    section_note = self.create_note(
                        title=section['title'],
                        body=self.generate_section_content(section, chapter['title'], book_data['title']),
                        parent_id=chapter_folder['id']
                    )
            else:
                # Create single chapter note
                chapter_note = self.create_note(
                    title=chapter['title'],
                    body=self.generate_chapter_content(chapter, book_data['title']),
                    parent_id=chapter_folder['id']
                )
                
    def create_folder(self, title: str, parent_id: str) -> Dict[str, Any]:
        """Create Joplin folder item"""
        folder_id = self.generate_id()
        timestamp = self.get_timestamp()
        
        folder = {
            'id': folder_id,
            'title': title,
            'created_time': timestamp,
            'updated_time': timestamp,
            'user_created_time': timestamp,
            'user_updated_time': timestamp,
            'encryption_cipher_text': '',
            'encryption_applied': 0,
            'parent_id': parent_id,
            'is_shared': 0,
            'type_': 2  # Folder type
        }
        
        self.items.append(folder)
        return folder
        
    def create_note(self, title: str, body: str, parent_id: str) -> Dict[str, Any]:
        """Create Joplin note item"""
        note_id = self.generate_id()
        timestamp = self.get_timestamp()
        
        note = {
            'id': note_id,
            'title': title,
            'body': body,
            'created_time': timestamp,
            'updated_time': timestamp,
            'is_conflict': 0,
            'latitude': '0.00000000',
            'longitude': '0.00000000',
            'altitude': '0.0000',
            'author': '',
            'source_url': '',
            'is_todo': 0,
            'todo_due': 0,
            'todo_completed': 0,
            'source': 'humanizer-lighthouse',
            'source_application': 'net.cozic.joplin-desktop',
            'application_data': '',
            'order': 0,
            'user_created_time': timestamp,
            'user_updated_time': timestamp,
            'encryption_cipher_text': '',
            'encryption_applied': 0,
            'markup_language': 1,  # Markdown
            'is_shared': 0,
            'parent_id': parent_id,
            'type_': 1  # Note type
        }
        
        self.items.append(note)
        return note
        
    def generate_metadata_content(self, book_data: Dict[str, Any]) -> str:
        """Generate metadata note content"""
        metadata = book_data.get('metadata', {})
        
        return f"""# {book_data['title']}

*Generated by Humanizer Lighthouse V2 Book Generation System*

## Book Information

- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Chapters**: {len(book_data.get('chapters', []))}
- **Format**: Humanizer Enhanced Markdown

## Description

{metadata.get('description', 'Generated with advanced semantic analysis and narrative clustering.')}

## Quality Metrics

{self._format_quality_metrics(metadata)}

## Editing with Humanizer

This book was created with the Humanizer Lighthouse platform and is optimized for editing in Joplin.

**Current Features:**
- 📝 **Professional formatting** - Structured chapters and sections
- 🏷️ **Narrative chunk markers** - Content ready for analysis
- 📊 **Quality indicators** - Embedded quality scores and source attribution
- 🔗 **Source tracking** - Links back to original conversations

**Future Features (with Humanizer Bridge Plugin):**
- 🧠 **Extract narrative attributes** from any text selection
- 🎭 **Transform text** with persona and style options  
- 📈 **Analyze content quality** and thematic coherence
- 🔄 **Bidirectional sync** with Humanizer system

---
*Ready for professional editing in Joplin*
"""

    def generate_chapter_content(self, chapter: Dict[str, Any], book_title: str) -> str:
        """Generate chapter content"""
        content = f"""# {chapter['title']}

{self._format_chapter_content(chapter)}

---
*Chapter of "{book_title}" | Generated by Humanizer Lighthouse*
"""
        return content
        
    def generate_section_content(self, section: Dict[str, Any], chapter_title: str, book_title: str) -> str:
        """Generate section content"""
        content = f"""# {section['title']}

{self._format_section_content(section)}

---
*Section of {chapter_title} | Part of "{book_title}"*
*Generated by Humanizer Lighthouse V2*
"""
        return content
        
    def _format_quality_metrics(self, metadata: Dict[str, Any]) -> str:
        """Format quality metrics for display"""
        if not metadata:
            return "- Quality metrics available during analysis"
            
        metrics = []
        
        if 'quality_score' in metadata:
            metrics.append(f"- **Overall Quality**: {metadata['quality_score']:.2f}")
        if 'coherence' in metadata:
            metrics.append(f"- **Coherence**: {metadata['coherence']:.2f}")
        if 'source_chunks' in metadata:
            if isinstance(metadata['source_chunks'], list):
                metrics.append(f"- **Source Chunks**: {len(metadata['source_chunks'])}")
            else:
                metrics.append(f"- **Source Chunks**: {metadata['source_chunks']}")
        if 'themes' in metadata:
            if isinstance(metadata['themes'], list):
                themes_str = ', '.join(metadata['themes'])
                metrics.append(f"- **Key Themes**: {themes_str}")
            else:
                metrics.append(f"- **Key Themes**: {metadata['themes']}")
                
        return '\n'.join(metrics) if metrics else "- Quality metrics available during analysis"
        
    def _format_chapter_content(self, chapter: Dict[str, Any]) -> str:
        """Format chapter content"""
        content_parts = []
        
        # Add any chapter-level content
        for content_block in chapter.get('content', []):
            if content_block.strip():
                content_parts.append(content_block)
        
        # Add content from sections if they exist
        for section in chapter.get('sections', []):
            if section.get('content'):
                content_parts.extend(section['content'])
                    
        return '\n\n'.join(content_parts) if content_parts else "*Chapter content will be added here*"
        
    def _format_section_content(self, section: Dict[str, Any]) -> str:
        """Format section content"""
        content_parts = []
        
        for content_block in section.get('content', []):
            if content_block.strip():
                content_parts.append(content_block)
                    
        return '\n\n'.join(content_parts) if content_parts else "*Section content will be added here*"
        
    def write_jex_file(self, output_file: Path):
        """Write Joplin export (.jex) file in correct format"""
        # Create temporary directory for staging files
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write each item as a serialized text file (Joplin's actual format)
            for item in self.items:
                item_file = temp_path / f"{item['id']}.md"
                serialized_content = self.serialize_item(item)
                item_file.write_text(serialized_content, encoding='utf-8')
            
            # Create tar archive (uncompressed, as Joplin expects)
            with tarfile.open(output_file, 'w') as tar:
                for item_file in temp_path.glob('*.md'):
                    tar.add(item_file, arcname=item_file.name)
                    
    def serialize_item(self, item: Dict[str, Any]) -> str:
        """Serialize item in Joplin's text format"""
        # Joplin serializes items as: title + body + properties
        lines = []
        
        # Add title (if present and not empty)
        if item.get('title'):
            lines.append(item['title'])
            lines.append('')  # Empty line after title
            
        # Add body (if present and not empty)
        if item.get('body'):
            lines.append(item['body'])
            lines.append('')  # Empty line after body
            
        # Add properties
        for key, value in item.items():
            if key not in ['title', 'body']:
                # Format timestamps properly
                if key.endswith('_time') and isinstance(value, int):
                    # Convert milliseconds to ISO format
                    dt = datetime.fromtimestamp(value / 1000)
                    formatted_value = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    lines.append(f"{key}: {formatted_value}")
                else:
                    lines.append(f"{key}: {value}")
                    
        return '\n'.join(lines)
        
    def generate_id(self) -> str:
        """Generate Joplin-compatible ID"""
        return uuid.uuid4().hex
        
    def get_timestamp(self) -> int:
        """Get current timestamp in Joplin format (milliseconds)"""
        return int(datetime.now().timestamp() * 1000)


def main():
    parser = argparse.ArgumentParser(description='Generate correct Joplin exports from Humanizer books')
    parser.add_argument('input_path', help='Path to book markdown file')
    parser.add_argument('--output-dir', '-o', help='Output directory for .jex file')
    parser.add_argument('--title', help='Override book title')
    
    args = parser.parse_args()
    
    try:
        generator = JoplinExportGeneratorFixed()
        
        # Generate export
        export_file = generator.generate_from_book_file(
            book_file_path=args.input_path,
            output_dir=args.output_dir
        )
        
        print(f"\n🎉 Success! Joplin export ready:")
        print(f"📂 File: {export_file}")
        print("\n📋 Next steps:")
        print("1. Open Joplin")
        print("2. Go to File → Import")
        print("3. Select the .jex file")
        print("4. Your book will appear as a structured notebook!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())