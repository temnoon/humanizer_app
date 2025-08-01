#!/usr/bin/env python3
"""
Advanced Export Format Generation System
Converts content to multiple publication formats with proper styling and metadata
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import yaml
import markdown
from jinja2 import Template

class FormatGenerator:
    """Advanced format generation and export system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.exports_dir = self.project_root / "exports"
        self.templates_dir = self.project_root / "config" / "templates"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure template directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def load_format_config(self) -> Dict[str, Any]:
        """Load format generation configuration"""
        config_file = self.templates_dir / "format_config.yaml"
        
        if not config_file.exists():
            default_config = {
                'html': {
                    'template': 'article.html',
                    'css_files': ['styles.css', 'highlight.css'],
                    'include_toc': True,
                    'syntax_highlighting': True
                },
                'pdf': {
                    'engine': 'pandoc',  # or 'weasyprint' if available
                    'template': 'article.tex',
                    'paper_size': 'letter',
                    'margin': '1in',
                    'font_size': '12pt'
                },
                'epub': {
                    'cover_image': 'cover.jpg',
                    'metadata': {
                        'author': 'Humanizer User',
                        'language': 'en'
                    }
                },
                'confluence': {
                    'space_key': 'DOCS',
                    'parent_page': 'Documentation'
                },
                'docx': {
                    'template': 'template.docx',
                    'style_reference': True
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def create_html_template(self):
        """Create default HTML template if it doesn't exist"""
        template_file = self.templates_dir / "article.html"
        
        if not template_file.exists():
            html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title | default('Document') }}</title>
    <style>
        body {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2rem;
        }
        h1 { border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        h2 { border-bottom: 1px solid #ecf0f1; padding-bottom: 0.3rem; }
        code {
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-size: 0.9em;
        }
        pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 1rem 0;
            padding-left: 1rem;
            color: #666;
        }
        .metadata {
            background: #ecf0f1;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 2rem;
            font-size: 0.9em;
        }
        .toc {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 2rem;
        }
        .toc ul { margin: 0; }
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #ecf0f1;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    {% if metadata %}
    <div class="metadata">
        {% if metadata.title %}<strong>Title:</strong> {{ metadata.title }}<br>{% endif %}
        {% if metadata.author %}<strong>Author:</strong> {{ metadata.author }}<br>{% endif %}
        {% if metadata.date %}<strong>Date:</strong> {{ metadata.date }}<br>{% endif %}
        {% if metadata.persona %}<strong>Persona:</strong> {{ metadata.persona }}<br>{% endif %}
        {% if metadata.namespace %}<strong>Namespace:</strong> {{ metadata.namespace }}<br>{% endif %}
        {% if metadata.style %}<strong>Style:</strong> {{ metadata.style }}<br>{% endif %}
    </div>
    {% endif %}
    
    {% if include_toc and toc %}
    <div class="toc">
        <h3>Table of Contents</h3>
        {{ toc | safe }}
    </div>
    {% endif %}
    
    <main>
        {{ content | safe }}
    </main>
    
    <div class="footer">
        Generated by Humanizer Lighthouse Platform on {{ generation_date }}
    </div>
</body>
</html>"""
            
            with open(template_file, 'w') as f:
                f.write(html_template)
    
    def extract_metadata(self, content: str, source_file: Path = None) -> Dict[str, Any]:
        """Extract metadata from content or filename"""
        metadata = {
            'generation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source_file': source_file.name if source_file else 'Unknown'
        }
        
        # Extract from filename patterns
        if source_file:
            filename = source_file.stem
            parts = filename.split('_')
            
            # Look for timestamp patterns
            if len(parts) > 0 and parts[0].isdigit() and len(parts[0]) >= 8:
                metadata['timestamp'] = parts[0]
                parts = parts[1:]  # Remove timestamp
            
            # Look for persona indicators
            personas = ['philosopher', 'scientist', 'artist', 'critic', 'historian']
            for part in parts:
                if part.lower() in personas:
                    metadata['persona'] = part.lower()
                    break
        
        # Extract YAML frontmatter if present
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            yaml_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_end = i
                    break
            
            if yaml_end > 0:
                try:
                    yaml_content = '\n'.join(lines[1:yaml_end])
                    yaml_data = yaml.safe_load(yaml_content)
                    if yaml_data:
                        metadata.update(yaml_data)
                except yaml.YAMLError:
                    pass  # Ignore YAML parsing errors
        
        return metadata
    
    def generate_toc(self, content: str) -> str:
        """Generate table of contents from markdown headers"""
        toc_items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:  # Valid header levels
                    title = line.lstrip('#').strip()
                    anchor = title.lower().replace(' ', '-').replace('[^a-z0-9-]', '')
                    toc_items.append(f"{'  ' * (level-1)}- [{title}](#{anchor})")
        
        return '\n'.join(toc_items) if toc_items else ""
    
    def to_html(self, input_file: Path, output_file: Path = None, 
                metadata: Dict[str, Any] = None) -> Path:
        """Convert markdown to HTML with template"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        file_metadata = self.extract_metadata(content, input_file)
        if metadata:
            file_metadata.update(metadata)
        
        # Remove YAML frontmatter from content
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    content = '\n'.join(lines[i+1:])
                    break
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['toc', 'codehilite', 'tables', 'fenced_code'])
        html_content = md.convert(content)
        
        # Generate TOC
        toc_html = self.generate_toc(content)
        toc_html = markdown.markdown(toc_html) if toc_html else ""
        
        # Load template
        self.create_html_template()
        template_file = self.templates_dir / "article.html"
        
        with open(template_file, 'r') as f:
            template = Template(f.read())
        
        # Render template
        rendered = template.render(
            content=html_content,
            metadata=file_metadata,
            toc=toc_html,
            include_toc=True,
            title=file_metadata.get('title', input_file.stem),
            generation_date=file_metadata['generation_date']
        )
        
        # Determine output file
        if output_file is None:
            output_file = self.exports_dir / "html" / f"{self.timestamp}_{input_file.stem}.html"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        return output_file
    
    def to_pdf(self, input_file: Path, output_file: Path = None) -> Path:
        """Convert to PDF using pandoc"""
        
        if output_file is None:
            output_file = self.exports_dir / "pdf" / f"{self.timestamp}_{input_file.stem}.pdf"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Try pandoc first
            cmd = [
                'pandoc',
                str(input_file),
                '-o', str(output_file),
                '--pdf-engine=xelatex',
                '--variable', 'geometry:margin=1in',
                '--variable', 'fontsize=12pt'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_file
            else:
                print(f"⚠️  Pandoc failed: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️  Pandoc not found. Install with: brew install pandoc")
        
        # Fallback: create HTML and note PDF generation failure
        html_file = self.to_html(input_file)
        print(f"📝 HTML generated instead: {html_file}")
        print("💡 For PDF generation, install pandoc: brew install pandoc")
        
        return html_file
    
    def to_docx(self, input_file: Path, output_file: Path = None) -> Path:
        """Convert to DOCX using pandoc"""
        
        if output_file is None:
            output_file = self.exports_dir / "docx" / f"{self.timestamp}_{input_file.stem}.docx"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                'pandoc',
                str(input_file),
                '-o', str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_file
            else:
                print(f"⚠️  DOCX conversion failed: {result.stderr}")
                return self.to_html(input_file)  # Fallback to HTML
                
        except FileNotFoundError:
            print("⚠️  Pandoc not found for DOCX generation")
            return self.to_html(input_file)  # Fallback to HTML
    
    def batch_convert(self, input_dir: Path, formats: List[str] = None, 
                     output_base: Path = None) -> Dict[str, Any]:
        """Batch convert multiple files to multiple formats"""
        
        if formats is None:
            formats = ['html', 'pdf']
        
        if not input_dir.exists():
            return {'error': f'Input directory not found: {input_dir}'}
        
        # Find markdown files
        md_files = list(input_dir.glob('*.md')) + list(input_dir.glob('*.txt'))
        
        if not md_files:
            return {'error': 'No markdown files found'}
        
        results = {
            'converted': [],
            'failed': [],
            'summary': {
                'total_files': len(md_files),
                'formats': formats,
                'successful': 0,
                'failed': 0
            }
        }
        
        print(f"🔄 Batch converting {len(md_files)} files to {len(formats)} formats")
        
        for md_file in md_files:
            file_results = {'source': str(md_file), 'outputs': {}}
            
            for format_type in formats:
                try:
                    if format_type == 'html':
                        output_file = self.to_html(md_file)
                    elif format_type == 'pdf':
                        output_file = self.to_pdf(md_file)
                    elif format_type == 'docx':
                        output_file = self.to_docx(md_file)
                    else:
                        print(f"⚠️  Unknown format: {format_type}")
                        continue
                    
                    file_results['outputs'][format_type] = str(output_file)
                    print(f"  ✅ {md_file.name} → {format_type}: {output_file.name}")
                    
                except Exception as e:
                    file_results['outputs'][format_type] = f"Error: {str(e)}"
                    print(f"  ❌ {md_file.name} → {format_type}: {str(e)}")
            
            if any('Error:' not in output for output in file_results['outputs'].values()):
                results['converted'].append(file_results)
                results['summary']['successful'] += 1
            else:
                results['failed'].append(file_results)
                results['summary']['failed'] += 1
        
        # Save batch results
        results_file = self.exports_dir / "archive" / f"batch_format_{self.timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Batch conversion complete: {results['summary']['successful']}/{results['summary']['total_files']} successful")
        print(f"📋 Results saved: {results_file}")
        
        return results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Advanced Export Format Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file to HTML
  python format_generator.py convert --file essay.md --format html
  
  # Convert to multiple formats
  python format_generator.py convert --file essay.md --format html,pdf,docx
  
  # Batch convert directory
  python format_generator.py batch --dir exports/transformations/ --formats html,pdf
  
  # Convert with custom output
  python format_generator.py convert --file essay.md --format html --output my_essay.html
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert single file')
    convert_parser.add_argument('--file', type=Path, required=True, help='Input file')
    convert_parser.add_argument('--format', required=True, help='Output format(s): html,pdf,docx')
    convert_parser.add_argument('--output', type=Path, help='Output file path')
    convert_parser.add_argument('--title', help='Document title')
    convert_parser.add_argument('--author', help='Document author')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch convert directory')
    batch_parser.add_argument('--dir', type=Path, required=True, help='Input directory')
    batch_parser.add_argument('--formats', default='html,pdf', help='Output formats: html,pdf,docx')
    batch_parser.add_argument('--output', type=Path, help='Output base directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = FormatGenerator()
    
    if args.command == 'convert':
        formats = [f.strip() for f in args.format.split(',')]
        metadata = {}
        
        if args.title:
            metadata['title'] = args.title
        if args.author:
            metadata['author'] = args.author
        
        for fmt in formats:
            try:
                if fmt == 'html':
                    output = generator.to_html(args.file, args.output, metadata)
                elif fmt == 'pdf':
                    output = generator.to_pdf(args.file, args.output)
                elif fmt == 'docx':
                    output = generator.to_docx(args.file, args.output)
                else:
                    print(f"❌ Unknown format: {fmt}")
                    continue
                
                print(f"✅ Generated {fmt.upper()}: {output}")
                
            except Exception as e:
                print(f"❌ Error generating {fmt}: {str(e)}")
    
    elif args.command == 'batch':
        formats = [f.strip() for f in args.formats.split(',')]
        result = generator.batch_convert(args.dir, formats, args.output)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()