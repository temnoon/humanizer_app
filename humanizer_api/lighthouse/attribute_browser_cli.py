#!/usr/bin/env python3
"""
Attribute Browser CLI - Interactive tool for exploring narrative attributes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

class AttributeBrowser:
    """Interactive browser for exploring narrative attributes"""
    
    def __init__(self, attributes_dir: str = "./mass_attributes"):
        self.attributes_dir = Path(attributes_dir)
        if not self.attributes_dir.exists():
            raise FileNotFoundError(f"Attributes directory not found: {attributes_dir}")
        
        self.attribute_files = list(self.attributes_dir.glob("*.json"))
        print(f"📚 Found {len(self.attribute_files)} attribute files")
    
    def list_files(self, limit: int = 20) -> None:
        """List available attribute files"""
        print(f"\n📋 Attribute Files (showing {min(limit, len(self.attribute_files))}):")
        for i, file in enumerate(self.attribute_files[:limit]):
            size_kb = file.stat().st_size // 1024
            print(f"  {i+1:3d}. {file.name:<30} ({size_kb}KB)")
        
        if len(self.attribute_files) > limit:
            print(f"  ... and {len(self.attribute_files) - limit} more")
    
    def show_summary(self) -> None:
        """Show overall summary of attribute collection"""
        total_size = sum(f.stat().st_size for f in self.attribute_files)
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"\n📊 Collection Summary:")
        print(f"  Total files: {len(self.attribute_files)}")
        print(f"  Total size: {total_size_mb:.1f} MB")
        print(f"  Average file size: {total_size_mb/len(self.attribute_files):.1f} MB")
        
        # Sample a few files to get stats
        sample_files = random.sample(self.attribute_files, min(5, len(self.attribute_files)))
        total_attributes = 0
        total_paragraphs = 0
        
        for file in sample_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    total_attributes += len(data.get('attributes', []))
                    total_paragraphs += data.get('total_paragraphs', 0)
            except:
                continue
        
        if sample_files:
            avg_attributes = total_attributes / len(sample_files)
            avg_paragraphs = total_paragraphs / len(sample_files)
            print(f"  Avg attributes per file: {avg_attributes:.1f}")
            print(f"  Avg paragraphs per file: {avg_paragraphs:.1f}")
    
    def browse_file(self, filename: str) -> None:
        """Browse contents of a specific attribute file"""
        file_path = self.attributes_dir / filename
        if not file_path.exists():
            # Try finding by partial match
            matches = [f for f in self.attribute_files if filename in f.name]
            if matches:
                file_path = matches[0]
                print(f"📁 Found match: {file_path.name}")
            else:
                print(f"❌ File not found: {filename}")
                return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"\n📖 File: {file_path.name}")
            print(f"  Book ID: {data.get('book_id', 'Unknown')}")
            print(f"  Extraction time: {data.get('extraction_timestamp', 'Unknown')}")
            print(f"  Total paragraphs: {data.get('total_paragraphs', 0)}")
            print(f"  Attributes found: {len(data.get('attributes', []))}")
            
            # Show first few attributes
            attributes = data.get('attributes', [])
            print(f"\n📝 Sample Attributes:")
            for i, attr in enumerate(attributes[:3]):
                print(f"\n  Attribute {i+1}:")
                print(f"    ID: {attr.get('id', 'Unknown')}")
                print(f"    Paragraph: {attr.get('paragraph_index', 'Unknown')}")
                print(f"    Words: {attr.get('word_count', 'Unknown')}")
                
                # Show text sample (truncated)
                text = attr.get('text_sample', '')
                if len(text) > 100:
                    text = text[:100] + "..."
                print(f"    Text: {text}")
                
                # Show narrative DNA
                dna = attr.get('narrative_dna', {})
                if dna:
                    print(f"    DNA: {dna.get('persona', 'Unknown')} | {dna.get('namespace', 'Unknown')} | {dna.get('style', 'Unknown')}")
            
            if len(attributes) > 3:
                print(f"\n  ... and {len(attributes) - 3} more attributes")
        
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {filename}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def search_content(self, query: str, limit: int = 10) -> None:
        """Search for text content across attribute files"""
        print(f"🔍 Searching for: '{query}'")
        matches = []
        
        for file_path in self.attribute_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                for attr in data.get('attributes', []):
                    text = attr.get('text_sample', '').lower()
                    if query.lower() in text:
                        matches.append({
                            'file': file_path.name,
                            'book_id': data.get('book_id'),
                            'attr_id': attr.get('id'),
                            'paragraph': attr.get('paragraph_index'),
                            'text': attr.get('text_sample', '')[:200] + "..."
                        })
                        
                        if len(matches) >= limit:
                            break
                
                if len(matches) >= limit:
                    break
                    
            except:
                continue
        
        print(f"\n📋 Found {len(matches)} matches:")
        for i, match in enumerate(matches):
            print(f"\n  {i+1}. {match['file']} (Book {match['book_id']})")
            print(f"     Paragraph {match['paragraph']}")
            print(f"     {match['text']}")
    
    def random_sample(self, count: int = 5) -> None:
        """Show random attribute samples"""
        print(f"🎲 Random Sample ({count} attributes):")
        
        sampled_files = random.sample(self.attribute_files, min(count, len(self.attribute_files)))
        
        for i, file_path in enumerate(sampled_files):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                attributes = data.get('attributes', [])
                if attributes:
                    attr = random.choice(attributes)
                    print(f"\n  {i+1}. From {file_path.name} (Book {data.get('book_id')})")
                    print(f"     Paragraph {attr.get('paragraph_index')}: {attr.get('text_sample', '')[:150]}...")
                    
                    dna = attr.get('narrative_dna', {})
                    if dna:
                        print(f"     DNA: {dna.get('persona')} | {dna.get('namespace')} | {dna.get('style')}")
                        
            except:
                continue

def main():
    parser = argparse.ArgumentParser(description="Browse narrative attributes")
    parser.add_argument('--dir', default='./mass_attributes', help='Attributes directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List attribute files')
    list_parser.add_argument('--limit', type=int, default=20, help='Limit number of files shown')
    
    # Summary command
    subparsers.add_parser('summary', help='Show collection summary')
    
    # Browse command
    browse_parser = subparsers.add_parser('browse', help='Browse specific file')
    browse_parser.add_argument('filename', help='Filename to browse')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search content')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    # Random command
    random_parser = subparsers.add_parser('random', help='Show random samples')
    random_parser.add_argument('--count', type=int, default=5, help='Number of samples')
    
    args = parser.parse_args()
    
    try:
        browser = AttributeBrowser(args.dir)
        
        if args.command == 'list':
            browser.list_files(args.limit)
        elif args.command == 'summary':
            browser.show_summary()
        elif args.command == 'browse':
            browser.browse_file(args.filename)
        elif args.command == 'search':
            browser.search_content(args.query, args.limit)
        elif args.command == 'random':
            browser.random_sample(args.count)
        else:
            browser.show_summary()
            print("\n💡 Use --help for available commands")
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()