#!/usr/bin/env python3
"""
AI Book Editor Agent
Automated editorial refinement system for generated books
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime
import subprocess

class AIBookEditor:
    """AI agent for editorial refinement of generated books"""
    
    def __init__(self, books_dir: str = "automated_books"):
        self.books_dir = Path(books_dir)
        self.refined_dir = self.books_dir / "refined"
        self.refined_dir.mkdir(exist_ok=True)
        
        print("🤖 AI Book Editor Agent")
        print("=" * 30)
        print(f"📂 Input directory: {self.books_dir}")
        print(f"📂 Output directory: {self.refined_dir}")
    
    def analyze_book_structure(self, book_path: Path) -> Dict[str, Any]:
        """Analyze the structure and content of a book"""
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic structure
        lines = content.split('\n')
        structure = {
            'title': '',
            'subtitle': '',
            'chapters': [],
            'total_insights': 0,
            'total_words': 0,
            'issues': []
        }
        
        current_chapter = None
        insight_count = 0
        word_count = len(content.split())
        
        for line in lines:
            line = line.strip()
            
            # Title extraction
            if line.startswith('# ') and not structure['title']:
                structure['title'] = line[2:]
            elif line.startswith('## ') and not structure['subtitle']:
                structure['subtitle'] = line[3:]
            
            # Chapter detection
            elif line.startswith('# Chapter') or (line.startswith('# ') and 'Chapter' in line):
                if current_chapter:
                    structure['chapters'].append(current_chapter)
                
                current_chapter = {
                    'title': line[2:] if line.startswith('# ') else line,
                    'sections': 0,
                    'insights': 0,
                    'word_estimate': 0
                }
            
            # Section detection
            elif line.startswith('## Section'):
                if current_chapter:
                    current_chapter['sections'] += 1
            
            # Insight detection  
            elif line.startswith('### Insight'):
                insight_count += 1
                if current_chapter:
                    current_chapter['insights'] += 1
        
        # Add final chapter
        if current_chapter:
            structure['chapters'].append(current_chapter)
        
        structure['total_insights'] = insight_count
        structure['total_words'] = word_count
        
        # Identify structural issues
        self._identify_issues(structure)
        
        return structure
    
    def _identify_issues(self, structure: Dict[str, Any]) -> None:
        """Identify structural and content issues"""
        issues = []
        
        # Chapter balance issues
        chapter_insights = [ch['insights'] for ch in structure['chapters']]
        if chapter_insights:
            avg_insights = sum(chapter_insights) / len(chapter_insights)
            for i, count in enumerate(chapter_insights):
                if count < avg_insights * 0.5:
                    issues.append(f"Chapter {i+1} has very few insights ({count} vs avg {avg_insights:.1f})")
                elif count > avg_insights * 2:
                    issues.append(f"Chapter {i+1} is overloaded ({count} vs avg {avg_insights:.1f})")
        
        # Too few chapters
        if len(structure['chapters']) < 3:
            issues.append("Too few chapters - readers expect 4-8 chapters")
        elif len(structure['chapters']) > 10:
            issues.append("Too many chapters - consider consolidation")
        
        # Length issues
        if structure['total_words'] < 15000:
            issues.append("Book may be too short for publication")
        elif structure['total_words'] > 80000:
            issues.append("Book may be too long - consider splitting")
        
        structure['issues'] = issues
    
    def generate_editorial_recommendations(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed editorial recommendations"""
        recommendations = {
            'priority': 'medium',
            'structural_changes': [],
            'content_improvements': [],
            'chapter_reorganization': {},
            'narrative_flow': [],
            'quality_enhancements': []
        }
        
        # Structural recommendations
        if len(structure['chapters']) < 4:
            recommendations['structural_changes'].append({
                'type': 'merge_chapters',
                'action': 'Consider splitting larger chapters into smaller, focused chapters',
                'rationale': 'Readers prefer 4-6 chapters for optimal flow'
            })
        
        # Chapter balance
        chapter_insights = [ch['insights'] for ch in structure['chapters']]
        if chapter_insights:
            max_insights = max(chapter_insights)
            min_insights = min(chapter_insights)
            
            if max_insights > min_insights * 3:
                recommendations['structural_changes'].append({
                    'type': 'rebalance_chapters',
                    'action': 'Redistribute insights for better chapter balance',
                    'rationale': f'Uneven distribution: {min_insights}-{max_insights} insights per chapter'
                })
        
        # Content improvements
        recommendations['content_improvements'] = [
            {
                'type': 'add_transitions',
                'priority': 'high',
                'description': 'Add smooth transitions between insights within chapters'
            },
            {
                'type': 'thematic_grouping', 
                'priority': 'high',
                'description': 'Group related insights together within sections'
            },
            {
                'type': 'remove_duplicates',
                'priority': 'medium', 
                'description': 'Identify and merge similar or duplicate insights'
            },
            {
                'type': 'enhance_flow',
                'priority': 'medium',
                'description': 'Improve logical progression from basic to advanced concepts'
            }
        ]
        
        # Quality enhancements
        recommendations['quality_enhancements'] = [
            'Highlight the most profound 3-5 insights per chapter',
            'Add brief contextual introductions to each chapter',
            'Include reflection questions at chapter ends',
            'Create thematic bridges between chapters',
            'Develop a stronger opening and closing for the book'
        ]
        
        # Set priority based on issues
        if len(structure['issues']) > 3:
            recommendations['priority'] = 'high'
        elif len(structure['issues']) > 1:
            recommendations['priority'] = 'medium'
        else:
            recommendations['priority'] = 'low'
        
        return recommendations
    
    def create_refined_outline(self, book_path: Path, structure: Dict[str, Any], 
                             recommendations: Dict[str, Any]) -> str:
        """Create a refined outline for editorial implementation"""
        
        outline_path = self.refined_dir / f"{book_path.stem}_editorial_outline.md"
        
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(f"# Editorial Outline: {structure['title']}\n\n")
            f.write(f"**Original Book:** {book_path.name}\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Priority:** {recommendations['priority'].upper()}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Content:** {structure['total_insights']} insights, {structure['total_words']:,} words\n")
            f.write(f"- **Current Structure:** {len(structure['chapters'])} chapters\n")
            f.write(f"- **Issues Identified:** {len(structure['issues'])}\n")
            f.write(f"- **Editorial Priority:** {recommendations['priority']}\n\n")
            
            # Issues and Recommendations
            if structure['issues']:
                f.write("## Identified Issues\n\n")
                for i, issue in enumerate(structure['issues'], 1):
                    f.write(f"{i}. {issue}\n")
                f.write("\n")
            
            # Structural Changes
            if recommendations['structural_changes']:
                f.write("## Structural Changes\n\n")
                for change in recommendations['structural_changes']:
                    f.write(f"**{change['type'].replace('_', ' ').title()}**\n")
                    f.write(f"- Action: {change['action']}\n")
                    f.write(f"- Rationale: {change['rationale']}\n\n")
            
            # Content Improvements
            f.write("## Content Improvements\n\n")
            for improvement in recommendations['content_improvements']:
                priority_icon = "🚨" if improvement['priority'] == 'high' else "⚠️" if improvement['priority'] == 'medium' else "💡"
                f.write(f"{priority_icon} **{improvement['type'].replace('_', ' ').title()}** ({improvement['priority']} priority)\n")
                f.write(f"   {improvement['description']}\n\n")
            
            # Chapter Analysis
            f.write("## Chapter-by-Chapter Analysis\n\n")
            for i, chapter in enumerate(structure['chapters'], 1):
                f.write(f"### Chapter {i}: {chapter['title']}\n")
                f.write(f"- **Insights:** {chapter['insights']}\n")
                f.write(f"- **Sections:** {chapter['sections']}\n")
                
                # Chapter-specific recommendations
                avg_insights = structure['total_insights'] / len(structure['chapters'])
                if chapter['insights'] < avg_insights * 0.7:
                    f.write("- **Issue:** Too few insights - consider merging with another chapter\n")
                elif chapter['insights'] > avg_insights * 1.5:
                    f.write("- **Issue:** Too many insights - consider splitting\n")
                else:
                    f.write("- **Status:** Well-balanced\n")
                f.write("\n")
            
            # Quality Enhancements
            f.write("## Quality Enhancement Checklist\n\n")
            for enhancement in recommendations['quality_enhancements']:
                f.write(f"- [ ] {enhancement}\n")
            f.write("\n")
            
            # Implementation Plan
            f.write("## Implementation Plan\n\n")
            f.write("### Phase 1: Structural Fixes\n")
            f.write("1. Address chapter balance issues\n")
            f.write("2. Reorganize content for better flow\n")
            f.write("3. Remove duplicate insights\n\n")
            
            f.write("### Phase 2: Content Enhancement\n")
            f.write("1. Add chapter introductions and transitions\n")
            f.write("2. Group related insights thematically\n")  
            f.write("3. Highlight key insights\n\n")
            
            f.write("### Phase 3: Final Polish\n")
            f.write("1. Review narrative arc\n")
            f.write("2. Add reflection questions\n")
            f.write("3. Final proofreading pass\n\n")
        
        return str(outline_path)
    
    def auto_implement_basic_fixes(self, book_path: Path, recommendations: Dict[str, Any]) -> str:
        """Automatically implement basic editorial fixes"""
        
        # Read original book
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"🔧 Implementing basic fixes for {book_path.name}...")
        
        # Fix 1: Improve chapter transitions
        content = self._add_chapter_transitions(content)
        
        # Fix 2: Remove excessive whitespace
        content = self._clean_formatting(content)
        
        # Fix 3: Improve insight headers
        content = self._improve_insight_headers(content)
        
        # Fix 4: Add section breaks
        content = self._add_section_breaks(content)
        
        # Save refined version
        refined_path = self.refined_dir / f"{book_path.stem}_auto_refined.md"
        with open(refined_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Auto-refined version saved: {refined_path.name}")
        return str(refined_path)
    
    def _add_chapter_transitions(self, content: str) -> str:
        """Add basic transitions between chapters"""
        lines = content.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            result.append(line)
            
            # Add transition after chapter headers
            if line.startswith('# Chapter') and i < len(lines) - 1:
                # Look ahead to see if there's already an intro
                next_few_lines = lines[i+1:i+4]
                has_intro = any(line.strip() and not line.startswith('*') and not line.startswith('#') 
                               for line in next_few_lines)
                
                if not has_intro:
                    result.append("")
                    result.append("This chapter explores the interconnected themes that emerge from deep contemplation and personal inquiry.")
                    result.append("")
        
        return '\n'.join(result)
    
    def _clean_formatting(self, content: str) -> str:
        """Clean up excessive whitespace and formatting"""
        # Remove excessive blank lines
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # Ensure consistent spacing around headers
        content = re.sub(r'\n(#+[^\n]+)\n', r'\n\n\1\n\n', content)
        
        # Clean up insight metadata formatting
        content = re.sub(r'\*Quality: ([0-9.]+) \| Words: ([0-9]+) \| Date: ([^*]+)\*', 
                        r'*Quality: \1 | Words: \2 | Date: \3*', content)
        
        return content
    
    def _improve_insight_headers(self, content: str) -> str:
        """Improve insight headers for better readability"""
        # Make insight headers more engaging
        content = re.sub(r'### Insight from ([^\\n]+)', 
                        r'### From \1', content)
        
        return content
    
    def _add_section_breaks(self, content: str) -> str:
        """Add visual breaks between insights"""
        # Ensure proper spacing around section dividers
        content = re.sub(r'^---$', r'\n---\n', content, flags=re.MULTILINE)
        
        return content
    
    def process_all_books(self) -> List[str]:
        """Process all books in the directory"""
        book_files = list(self.books_dir.glob("book_*.md"))
        
        if not book_files:
            print("❌ No book files found to process")
            return []
        
        print(f"📚 Found {len(book_files)} books to process")
        
        processed_files = []
        
        for book_path in book_files:
            print(f"\n📖 Processing: {book_path.name}")
            
            # Analyze structure
            structure = self.analyze_book_structure(book_path)
            print(f"   📊 {structure['total_insights']} insights, {structure['total_words']:,} words")
            
            # Generate recommendations
            recommendations = self.generate_editorial_recommendations(structure)
            print(f"   🎯 Priority: {recommendations['priority']}")
            
            # Create editorial outline
            outline_path = self.create_refined_outline(book_path, structure, recommendations)
            print(f"   📋 Outline: {Path(outline_path).name}")
            
            # Auto-implement basic fixes
            refined_path = self.auto_implement_basic_fixes(book_path, recommendations)
            processed_files.append(refined_path)
            
            print(f"   ✅ Processed: {Path(refined_path).name}")
        
        return processed_files
    
    def generate_master_editorial_report(self, processed_files: List[str]) -> str:
        """Generate master editorial report for all books"""
        report_path = self.refined_dir / "master_editorial_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Master Editorial Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Books Processed:** {len(processed_files)}\n\n")
            
            f.write("## Processing Summary\n\n")
            
            for i, file_path in enumerate(processed_files, 1):
                file_name = Path(file_path).name
                f.write(f"{i}. **{file_name}**\n")
                f.write(f"   - Auto-refined version created\n")
                f.write(f"   - Editorial outline available\n")
                f.write(f"   - Ready for detailed review\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. **Review Auto-Refined Versions**: Check the automatically improved books\n")
            f.write("2. **Apply Editorial Outlines**: Use the detailed recommendations for manual refinement\n")
            f.write("3. **Quality Review**: Conduct final editorial review\n")
            f.write("4. **Publication Preparation**: Format for final publication\n\n")
            
            f.write("## Files Generated\n\n")
            f.write("### Auto-Refined Books\n")
            for file_path in processed_files:
                f.write(f"- `{Path(file_path).name}`\n")
            
            f.write("\n### Editorial Outlines\n")
            outline_files = list(self.refined_dir.glob("*_editorial_outline.md"))
            for outline_file in outline_files:
                f.write(f"- `{outline_file.name}`\n")
        
        return str(report_path)

def main():
    parser = argparse.ArgumentParser(description="AI Book Editor - Refine generated books")
    parser.add_argument('--books-dir', default='automated_books',
                       help='Directory containing books to edit')
    parser.add_argument('--book', help='Edit specific book file')
    
    args = parser.parse_args()
    
    try:
        editor = AIBookEditor(args.books_dir)
        
        if args.book:
            # Process single book
            book_path = Path(args.book)
            if not book_path.exists():
                book_path = Path(args.books_dir) / args.book
            
            if book_path.exists():
                print(f"📖 Processing single book: {book_path.name}")
                structure = editor.analyze_book_structure(book_path)
                recommendations = editor.generate_editorial_recommendations(structure)
                outline_path = editor.create_refined_outline(book_path, structure, recommendations)
                refined_path = editor.auto_implement_basic_fixes(book_path, recommendations)
                
                print(f"✅ Completed processing of {book_path.name}")
                print(f"   📋 Editorial outline: {outline_path}")
                print(f"   📚 Refined version: {refined_path}")
            else:
                print(f"❌ Book file not found: {args.book}")
        else:
            # Process all books
            processed_files = editor.process_all_books()
            
            if processed_files:
                # Generate master report
                report_path = editor.generate_master_editorial_report(processed_files)
                
                print(f"\n🎉 Editorial Processing Complete!")
                print(f"📚 Processed {len(processed_files)} books")
                print(f"📋 Master report: {report_path}")
                print(f"📂 All outputs in: {editor.refined_dir}")
            else:
                print("❌ No books were successfully processed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()