#!/usr/bin/env python3
"""
Joplin Export Generator for Humanizer Books
Converts Humanizer-generated books into Joplin-importable format (.jex files)
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

class JoplinExportGenerator:
    def __init__(self):
        self.export_data = {
            'format_version': 4,  # Joplin export format version
            'export_date': datetime.now().isoformat(),
            'folders': [],
            'notes': [],
            'resources': []
        }
        
    def generate_from_book_file(self, book_file_path: str, output_dir: str = None) -> str:
        """Generate Joplin export from existing book markdown file"""
        book_path = Path(book_file_path)
        
        if not book_path.exists():
            raise FileNotFoundError(f"Book file not found: {book_file_path}")
            
        print(f"📚 Processing book: {book_path.name}")
        
        # Parse existing book file
        book_content = book_path.read_text(encoding='utf-8')
        book_data = self.parse_book_markdown(book_content, book_path.stem)
        
        # Generate Joplin structure
        self.create_joplin_structure(book_data)
        
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
        
    def generate_from_book_data(self, book_data: Dict[str, Any], output_dir: str) -> str:
        """Generate Joplin export from structured book data"""
        print(f"📚 Processing book data: {book_data.get('title', 'Untitled')}")
        
        # Generate Joplin structure
        self.create_joplin_structure(book_data)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate .jex file
        title = book_data.get('title', 'Untitled_Book').replace(' ', '_')
        export_file = output_path / f"{title}.jex"
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
                    print("⚠️  YAML not available, skipping frontmatter parsing")
                except Exception as e:
                    print(f"⚠️  Error parsing frontmatter: {e}")
        
        # Parse content structure
        current_content = []
        
        for line in lines:
            line = line.strip()
            
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
            
    def create_joplin_structure(self, book_data: Dict[str, Any]):
        """Create Joplin folder and note structure"""
        # Create main book folder
        book_folder = self.create_folder(
            title=book_data['title'],
            parent_id='',
            is_book=True
        )
        
        # Create book metadata note
        metadata_note = self.create_metadata_note(
            book_data=book_data,
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
                    section_note = self.create_section_note(
                        section=section,
                        chapter_title=chapter['title'],
                        book_title=book_data['title'],
                        parent_id=chapter_folder['id']
                    )
            else:
                # Create single chapter note
                chapter_note = self.create_chapter_note(
                    chapter=chapter,
                    book_title=book_data['title'],
                    parent_id=chapter_folder['id']
                )
                
    def create_folder(self, title: str, parent_id: str, is_book: bool = False) -> Dict[str, Any]:
        """Create Joplin folder"""
        folder = {
            'id': self.generate_id(),
            'title': title,
            'created_time': self.get_timestamp(),
            'updated_time': self.get_timestamp(),
            'user_created_time': self.get_timestamp(),
            'user_updated_time': self.get_timestamp(),
            'encryption_cipher_text': '',
            'encryption_applied': 0,
            'parent_id': parent_id,
            'is_shared': 0,
            'type_': 2  # Folder type
        }
        
        # Add book-specific metadata
        if is_book:
            folder['icon'] = '📚'
            
        self.export_data['folders'].append(folder)
        return folder
        
    def create_metadata_note(self, book_data: Dict[str, Any], parent_id: str) -> Dict[str, Any]:
        """Create book metadata note"""
        metadata = book_data.get('metadata', {})
        
        content = f"""---
title: "{book_data['title']}"
type: "book"
format_version: "1.0"
created: "{datetime.now().isoformat()}"
humanizer_book: true
lighthouse_generated: true
editable_with_humanizer: true
---

# {book_data['title']}

## Book Information

- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Generated by**: Humanizer Lighthouse V2 Book Generation System
- **Chapters**: {len(book_data.get('chapters', []))}

## Description

{metadata.get('description', 'Generated with advanced semantic analysis and narrative clustering.')}

## Quality Metrics

{self._format_quality_metrics(metadata)}

## Editing with Humanizer

This book was created with the Humanizer Lighthouse platform and is ready for editing with the Humanizer Bridge Plugin for Joplin.

**Available Features:**
- 🧠 **Extract narrative attributes** from any text selection
- 🎭 **Transform text** with persona and style options
- 📊 **Analyze content quality** and thematic coherence
- 🔗 **Link back to source** conversations and chunks
- 📈 **Track quality metrics** as you edit

## Humanizer Integration Commands

When the Humanizer Bridge Plugin is installed, you can:

- **Right-click any text** → "Analyze with Humanizer"
- **Select text** → Use Ctrl+H for quick analysis
- **Transform selections** → Apply persona/style transformations
- **Analyze entire notes** → Ctrl+Shift+H for full note analysis

---
*Generated by Humanizer Lighthouse V2 Book Generation System*
*Ready for editing in Joplin with Humanizer Bridge Plugin*
"""

        note = self.create_note(
            title=f"{book_data['title']} - Book Information",
            content=content,
            parent_id=parent_id
        )
        
        return note
        
    def create_chapter_note(self, chapter: Dict[str, Any], book_title: str, parent_id: str) -> Dict[str, Any]:
        """Create individual chapter note"""
        content = f"""# {chapter['title']}

## Chapter Content

{self._format_chapter_content(chapter)}

## Humanizer Analysis

*This chapter can be analyzed and enhanced using the Humanizer Bridge Plugin for Joplin.*

**Available Actions:**
- Select any text and right-click → "Analyze with Humanizer"
- Use Ctrl+H for quick analysis of selected text
- Apply persona/style transformations to enhance writing
- Analyze thematic coherence and quality metrics

---
*Part of "{book_title}" | Generated by Humanizer Lighthouse*
"""

        return self.create_note(
            title=chapter['title'],
            content=content,
            parent_id=parent_id
        )
        
    def create_section_note(self, section: Dict[str, Any], chapter_title: str, 
                          book_title: str, parent_id: str) -> Dict[str, Any]:
        """Create section note within chapter"""
        content = f"""# {section['title']}

## Section Content

{self._format_section_content(section)}

## Narrative Chunks

*Individual narrative chunks in this section can be analyzed with the Humanizer Bridge Plugin.*

### Analysis Features Available:
- **Quality Assessment**: Measure content quality and coherence
- **Attribute Extraction**: Identify persona, style, and thematic elements  
- **Content Transformation**: Apply different personas and styles
- **Source Tracking**: Link back to original conversations and chunks

### Quick Actions:
- **Select text** → Right-click → "Analyze with Humanizer"
- **Transform text** → Select → Right-click → "Transform with Humanizer"
- **Quality check** → Ctrl+H for instant quality analysis

---
*Section of {chapter_title} | Part of "{book_title}"*
*Generated by Humanizer Lighthouse V2*
"""

        return self.create_note(
            title=section['title'],
            content=content,
            parent_id=parent_id
        )
        
    def create_note(self, title: str, content: str, parent_id: str) -> Dict[str, Any]:
        """Create Joplin note"""
        note = {
            'id': self.generate_id(),
            'title': title,
            'body': content,
            'created_time': self.get_timestamp(),
            'updated_time': self.get_timestamp(),
            'is_conflict': 0,
            'latitude': 0.0,
            'longitude': 0.0,
            'altitude': 0.0,
            'author': '',
            'source_url': '',
            'is_todo': 0,
            'todo_due': 0,
            'todo_completed': 0,
            'source': 'humanizer-lighthouse',
            'source_application': 'humanizer-lighthouse',
            'application_data': json.dumps({
                'humanizer_book': True,
                'generated_by': 'lighthouse_v2',
                'editable_with_humanizer': True
            }),
            'order': 0,
            'user_created_time': self.get_timestamp(),
            'user_updated_time': self.get_timestamp(),
            'encryption_cipher_text': '',
            'encryption_applied': 0,
            'markup_language': 1,  # Markdown
            'is_shared': 0,
            'parent_id': parent_id,
            'type_': 1  # Note type
        }
        
        self.export_data['notes'].append(note)
        return note
        
    def _format_quality_metrics(self, metadata: Dict[str, Any]) -> str:
        """Format quality metrics for display"""
        if not metadata:
            return "- Quality metrics will be added during analysis"
            
        metrics = []
        
        if 'quality_score' in metadata:
            metrics.append(f"- **Overall Quality**: {metadata['quality_score']:.2f}")
        if 'coherence' in metadata:
            metrics.append(f"- **Coherence**: {metadata['coherence']:.2f}")
        if 'source_chunks' in metadata:
            metrics.append(f"- **Source Chunks**: {len(metadata['source_chunks'])}")
        if 'themes' in metadata:
            themes_str = ', '.join(metadata['themes'])
            metrics.append(f"- **Key Themes**: {themes_str}")
            
        return '\n'.join(metrics) if metrics else "- Quality metrics will be added during analysis"
        
    def _format_chapter_content(self, chapter: Dict[str, Any]) -> str:
        """Format chapter content with narrative chunk markers"""
        content_parts = []
        
        # Add chapter content
        for content_block in chapter.get('content', []):
            # Check if this looks like a narrative chunk
            if ':::{' in content_block and 'chunk_' in content_block:
                # This is already a formatted narrative chunk
                content_parts.append(content_block)
            else:
                # Regular content - wrap as potential narrative chunk
                if content_block.strip():
                    content_parts.append(f"""
<!-- Potential Narrative Chunk -->
:::{{{self.generate_chunk_id()}}}
**[Humanizer Analysis Available]**
*Right-click this text and select "Analyze with Humanizer" to extract attributes and quality metrics*

{content_block}

**[Transformation Options]**
*Select text above and use "Transform with Humanizer" to apply different personas and styles*
:::
""")
                    
        return '\n\n'.join(content_parts) if content_parts else "*Content will be added here*"
        
    def _format_section_content(self, section: Dict[str, Any]) -> str:
        """Format section content with narrative chunk markers"""
        content_parts = []
        
        for content_block in section.get('content', []):
            if content_block.strip():
                # Check if already formatted as chunk
                if ':::{' in content_block and 'chunk_' in content_block:
                    content_parts.append(content_block)
                else:
                    # Wrap as analyzable chunk
                    content_parts.append(f"""
<!-- Narrative Chunk: Ready for Humanizer Analysis -->
:::{{{self.generate_chunk_id()}}}
**[Ready for Analysis]**
*This content can be analyzed with the Humanizer Bridge Plugin*

{content_block}

**[Available Actions]**
- Extract narrative attributes (persona, style, themes)
- Assess content quality and coherence  
- Transform with different personas
- Link to source conversations
:::
""")
                    
        return '\n\n'.join(content_parts) if content_parts else "*Section content will be added here*"
        
    def write_jex_file(self, output_file: Path):
        """Write Joplin export (.jex) file in correct format"""
        # Joplin .jex format is a tar file containing individual JSON files for each item
        with tarfile.open(output_file, 'w') as tar:
            # Add folders as individual JSON files
            for folder in self.export_data['folders']:
                folder_json = json.dumps(folder)
                filename = f"{folder['id']}.md"
                info = tarfile.TarInfo(filename)
                info.size = len(folder_json.encode('utf-8'))
                tar.addfile(info, io.BytesIO(folder_json.encode('utf-8')))
                
            # Add notes as individual JSON files  
            for note in self.export_data['notes']:
                note_json = json.dumps(note)
                filename = f"{note['id']}.md"
                info = tarfile.TarInfo(filename)
                info.size = len(note_json.encode('utf-8'))
                tar.addfile(info, io.BytesIO(note_json.encode('utf-8')))
            
    def generate_id(self) -> str:
        """Generate Joplin-compatible ID"""
        return uuid.uuid4().hex
        
    def generate_chunk_id(self) -> str:
        """Generate unique chunk ID"""
        return f"chunk_{uuid.uuid4().hex[:8]}"
        
    def get_timestamp(self) -> int:
        """Get current timestamp in Joplin format"""
        return int(datetime.now().timestamp() * 1000)


def main():
    parser = argparse.ArgumentParser(description='Generate Joplin exports from Humanizer books')
    parser.add_argument('input_path', help='Path to book markdown file')
    parser.add_argument('--output-dir', '-o', help='Output directory for .jex file')
    parser.add_argument('--title', help='Override book title')
    
    args = parser.parse_args()
    
    try:
        generator = JoplinExportGenerator()
        
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
        print("4. Install Humanizer Bridge Plugin for full functionality")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())