#!/usr/bin/env python3
"""
Simple Markdown Exporter for Joplin Import
Converts LaTeX delimiters to KaTeX-compatible format with proper spacing
"""

import json
import os
import re
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class JoplinMarkdownExporterSimple:
    def __init__(self):
        self.output_dir = None
        
    def export_book_to_markdown(self, book_file_path: str, output_dir: str = None) -> str:
        """Export book to markdown directory structure for Joplin import"""
        book_path = Path(book_file_path)
        
        if not book_path.exists():
            raise FileNotFoundError(f"Book file not found: {book_file_path}")
            
        print(f"📚 Processing book: {book_path.name}")
        
        # Parse existing book file - RAW content without processing
        book_content = book_path.read_text(encoding='utf-8')
        book_data = self.parse_book_markdown(book_content, book_path.stem)
        
        # Create output directory structure
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = book_path.parent / 'joplin_markdown_export_simple'
            
        # Create main book directory
        book_dir = self.output_dir / self.sanitize_filename(book_data['title'])
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Create overview file
        self.create_overview_file(book_data, book_dir)
        
        # Create individual chapter files with LaTeX conversion
        self.create_chapter_files_converted(book_data, book_dir)
        
        print(f"✅ Simple markdown export created: {book_dir}")
        print(f"\n🎉 Success! Joplin markdown export ready:")
        print(f"📂 Directory: {book_dir}")
        print(f"\n📋 Next steps:")
        print("1. Open Joplin")
        print("2. Go to File → Import")
        print("3. Select 'Markdown' format")
        print("4. Choose the export directory")
        print("5. LaTeX should render with KaTeX!")
        
        return str(book_dir)
        
    def parse_book_markdown(self, content: str, default_title: str) -> Dict[str, Any]:
        """Parse book markdown content into structured data - NO PROCESSING"""
        book_data = {
            'title': default_title.replace('_', ' ').title(),
            'chapters': []
        }
        
        lines = content.split('\n')
        
        # Extract title from first line if it's a header
        if lines and lines[0].startswith('# '):
            book_data['title'] = lines[0][2:].strip()
        
        # Parse content into chapters - PRESERVE ALL ORIGINAL CONTENT
        current_chapter = None
        current_content = []
        
        i = 0
        while i < len(lines):
            line = lines[i]  # Keep original line with all whitespace
            
            # Main chapter headers (single # )
            if line.startswith('# ') and not self._is_metadata_line(line):
                # Save previous chapter
                if current_chapter and current_content:
                    # Join with original line endings - NO PROCESSING
                    current_chapter['content'] = '\n'.join(current_content)
                    current_content = []
                
                # Create new chapter
                chapter_title = line[2:].strip()
                current_chapter = {
                    'title': chapter_title,
                    'content': ''
                }
                book_data['chapters'].append(current_chapter)
                
            # Collect content for current chapter - RAW
            elif current_chapter:
                current_content.append(lines[i])  # Keep EVERYTHING as-is
                
            i += 1
        
        # Save final chapter content - RAW
        if current_chapter and current_content:
            current_chapter['content'] = '\n'.join(current_content)
            
        print(f"📖 Extracted RAW content from {len(book_data['chapters'])} chapters")
        for i, chapter in enumerate(book_data['chapters']):
            content_length = len(chapter.get('content', ''))
            print(f"   Chapter {i+1}: {chapter['title']} ({content_length} chars)")
            
        return book_data
        
    def _is_metadata_line(self, line: str) -> bool:
        """Check if line is metadata rather than chapter content"""
        metadata_patterns = [
            r'.*\*Generated.*\*',
            r'.*words of.*exploration',
            r'.*Book Quality Metrics.*',
            r'.*Table of Contents.*',
            r'.*Book Overview.*'
        ]
        for pattern in metadata_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
        
    def convert_latex_delimiters(self, content: str) -> str:
        """Convert LaTeX delimiters to KaTeX-compatible format"""
        
        # Strategy: Use negative lookahead/lookbehind to avoid converting LaTeX
        # that's already inside dollar signs or existing $$ blocks
        
        # Convert \[ \] to $$ (display math) - but not if already inside $ or $$
        # Negative lookbehind: not preceded by $ or $$
        # Negative lookahead: not followed by content that ends in $ or $$
        content = re.sub(r'(?<!\$)\\\[', '$$', content)
        content = re.sub(r'\\\](?!\$)', '$$', content)
        
        # Convert \( and \) to $ (inline math) - REMOVE SPACES!
        # But avoid if we're already inside dollar signs
        content = re.sub(r'(?<!\$)\\\(\s*', '$', content)  # \( with optional space
        content = re.sub(r'\s*\\\)(?!\$)', '$', content)  # optional space \)
        
        return content
        
    def create_overview_file(self, book_data: Dict[str, Any], book_dir: Path):
        """Create book overview markdown file"""
        overview_content = f"""# {book_data['title']}

*Generated by Humanizer Lighthouse - Simple LaTeX Conversion*

## Book Information

- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Chapters**: {len(book_data.get('chapters', []))}
- **Format**: Markdown with KaTeX-compatible LaTeX
- **LaTeX Rendering**: Standard Joplin KaTeX

## LaTeX Conversion

This export converts LaTeX delimiters for KaTeX compatibility:
- `\\( ` → `$` (space removed)
- ` \\)` → `$` (space removed)
- `\\[` → `$$`
- `\\]` → `$$`

**Standard Joplin KaTeX rendering handles all math expressions!**

## Content Source

This book was generated from conversation transcripts and contains:
- 📝 **KaTeX-compatible LaTeX** from physics/math discussions
- 🧠 **OCR transcripts** from handwritten notebooks
- 🎯 **Semantic clustering** for thematic organization
- 📊 **Quality filtering** for best insights

## Chapters

{self._generate_chapter_links(book_data)}

---
*KaTeX-compatible LaTeX formatting*"""

        overview_file = book_dir / "00_Overview.md"
        overview_file.write_text(overview_content, encoding='utf-8')
        
    def _generate_chapter_links(self, book_data: Dict[str, Any]) -> str:
        """Generate markdown links to chapters"""
        links = []
        for i, chapter in enumerate(book_data.get('chapters', []), 1):
            chapter_filename = f"{i:02d}_{self.sanitize_filename(chapter['title'])}.md"
            links.append(f"- [{chapter['title']}](./{chapter_filename})")
        return '\n'.join(links)
        
    def create_chapter_files_converted(self, book_data: Dict[str, Any], book_dir: Path):
        """Create individual chapter markdown files with LaTeX conversion"""
        for i, chapter in enumerate(book_data.get('chapters', []), 1):
            # Get raw content and convert LaTeX delimiters
            chapter_raw_content = chapter.get('content', '*Chapter content will be added here*')
            converted_content = self.convert_latex_delimiters(chapter_raw_content)
            
            chapter_content = f"""# {chapter['title']}

{converted_content}

---
*Chapter {i} of "{book_data['title']}" | Generated by Humanizer Lighthouse*
*KaTeX-compatible LaTeX formatting*
"""
            
            chapter_filename = f"{i:02d}_{self.sanitize_filename(chapter['title'])}.md"
            chapter_file = book_dir / chapter_filename
            chapter_file.write_text(chapter_content, encoding='utf-8')
            
            # Report conversion stats
            original_inline = len(re.findall(r'\\?\(.*?\\?\)', chapter_raw_content))
            original_display = len(re.findall(r'\\?\[.*?\\?\]', chapter_raw_content))
            if original_inline > 0 or original_display > 0:
                print(f"   Chapter {i}: Converted {original_inline} inline + {original_display} display LaTeX expressions")
            
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('._')
        return filename[:100]  # Limit length

def main():
    parser = argparse.ArgumentParser(description='Export Humanizer book to Joplin-compatible markdown with simple LaTeX conversion')
    parser.add_argument('input_path', help='Path to the book markdown file')
    parser.add_argument('--output-dir', help='Output directory for markdown export')
    parser.add_argument('--title', help='Override book title')
    
    args = parser.parse_args()
    
    try:
        exporter = JoplinMarkdownExporterSimple()
        export_path = exporter.export_book_to_markdown(
            args.input_path,
            args.output_dir
        )
        
        print(f"\n✅ Export completed successfully!")
        print(f"📁 Directory: {export_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()