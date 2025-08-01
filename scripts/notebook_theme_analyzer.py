#!/usr/bin/env python3
"""
Notebook Theme Analyzer
Quick thematic analysis of notebook transcripts with agent assistance
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import re
from collections import Counter
from typing import List, Dict, Any

class NotebookThemeAnalyzer:
    """Quick thematic analysis of notebook content"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://tem@localhost/humanizer_archive"
        self.database_url = database_url
    
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def extract_sample_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Extract sample insights for analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    child.parent_id as conversation_id,
                    COALESCE(parent.title, 'Untitled') as conversation_title,
                    child.body_text,
                    child.timestamp,
                    LENGTH(child.body_text) as content_length
                FROM archived_content child
                JOIN archived_content parent ON child.parent_id = parent.id
                WHERE child.source_metadata->>'gizmo_id' = %s
                    AND child.content_type = 'message'
                    AND child.body_text IS NOT NULL
                    AND LENGTH(child.body_text) > 300
                ORDER BY LENGTH(child.body_text) DESC, child.timestamp DESC
                LIMIT %s
            """, (self.JOURNAL_OCR_GIZMO_ID, limit))
            
            results = cursor.fetchall()
        
        insights = []
        for row in results:
            # Extract handwritten content
            content = self._extract_handwritten_content(row['body_text'])
            if content and len(content) > 100:
                insights.append({
                    'conversation_id': row['conversation_id'],
                    'conversation_title': row['conversation_title'],
                    'content': content,
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None,
                    'word_count': len(content.split())
                })
        
        return insights
    
    def _extract_handwritten_content(self, body_text: str) -> str:
        """Extract handwritten content from OCR transcript"""
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
    
    def analyze_themes_overview(self) -> Dict[str, Any]:
        """Generate thematic overview"""
        insights = self.extract_sample_insights(30)
        
        if not insights:
            return {"error": "No insights found"}
        
        # Basic analysis
        total_words = sum(insight['word_count'] for insight in insights)
        conversations = set(insight['conversation_title'] for insight in insights)
        
        # Extract all content for pattern analysis
        all_content = " ".join(insight['content'].lower() for insight in insights)
        
        # Philosophical term frequency
        philosophical_terms = [
            'consciousness', 'being', 'existence', 'reality', 'awareness', 'experience',
            'mind', 'thought', 'meditation', 'contemplation', 'zen', 'ego', 'self',
            'truth', 'wisdom', 'understanding', 'nature', 'universe', 'time', 'space'
        ]
        
        term_frequencies = {}
        for term in philosophical_terms:
            count = len(re.findall(r'\b' + re.escape(term) + r'\b', all_content))
            if count > 0:
                term_frequencies[term] = count
        
        # Sample high-quality excerpts
        sample_excerpts = []
        for insight in insights[:5]:
            excerpt = insight['content'][:300] + "..." if len(insight['content']) > 300 else insight['content']
            sample_excerpts.append({
                'source': insight['conversation_title'],
                'excerpt': excerpt,
                'word_count': insight['word_count']
            })
        
        return {
            'total_insights': len(insights),
            'total_words': total_words,
            'unique_conversations': len(conversations),
            'avg_words_per_insight': total_words // len(insights),
            'top_conversations': list(conversations)[:10],
            'philosophical_terms': dict(Counter(term_frequencies).most_common(10)),
            'sample_excerpts': sample_excerpts,
            'summary': {
                'content_richness': 'high' if total_words > 10000 else 'moderate' if total_words > 5000 else 'limited',
                'thematic_diversity': len(term_frequencies),
                'conversation_span': len(conversations)
            }
        }
    
    def generate_analysis_report(self, output_file: str = None) -> str:
        """Generate comprehensive analysis report"""
        analysis = self.analyze_themes_overview()
        
        if 'error' in analysis:
            return f"❌ {analysis['error']}"
        
        report = []
        report.append("# Notebook Content Thematic Analysis")
        report.append(f"**Generated:** {datetime.now().isoformat()}")
        report.append("")
        
        # Overview
        report.append("## Overview")
        report.append(f"- **Total Insights:** {analysis['total_insights']}")
        report.append(f"- **Total Words:** {analysis['total_words']:,}")
        report.append(f"- **Unique Conversations:** {analysis['unique_conversations']}")
        report.append(f"- **Average Words per Insight:** {analysis['avg_words_per_insight']}")
        report.append(f"- **Content Richness:** {analysis['summary']['content_richness']}")
        report.append("")
        
        # Top conversations
        report.append("## Source Conversations")
        for i, conv in enumerate(analysis['top_conversations'], 1):
            report.append(f"{i}. {conv}")
        report.append("")
        
        # Philosophical themes
        report.append("## Dominant Philosophical Themes")
        for term, count in analysis['philosophical_terms'].items():
            report.append(f"- **{term.title()}:** {count} occurrences")
        report.append("")
        
        # Sample content
        report.append("## Sample Content")
        for i, excerpt in enumerate(analysis['sample_excerpts'], 1):
            report.append(f"### Sample {i}: {excerpt['source']}")
            report.append(f"*{excerpt['word_count']} words*")
            report.append("")
            report.append(f"```")
            report.append(excerpt['excerpt'])
            report.append(f"```")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Report saved to: {output_file}")
        
        return report_text

def main():
    analyzer = NotebookThemeAnalyzer()
    
    print("📊 Quick Notebook Theme Analysis")
    print("=" * 40)
    
    try:
        analysis = analyzer.analyze_themes_overview()
        
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        print(f"📖 Found {analysis['total_insights']} insights")
        print(f"📝 Total words: {analysis['total_words']:,}")
        print(f"💬 From {analysis['unique_conversations']} conversations")
        print(f"📊 Content richness: {analysis['summary']['content_richness']}")
        
        print(f"\n🧠 Top Philosophical Themes:")
        for term, count in list(analysis['philosophical_terms'].items())[:8]:
            print(f"  • {term.title()}: {count}x")
        
        print(f"\n📚 Top Source Conversations:")
        for i, conv in enumerate(analysis['top_conversations'][:5], 1):
            print(f"  {i}. {conv}")
        
        print(f"\n💡 Sample Insight:")
        if analysis['sample_excerpts']:
            excerpt = analysis['sample_excerpts'][0]
            print(f"From: {excerpt['source']}")
            preview = excerpt['excerpt'][:200] + "..." if len(excerpt['excerpt']) > 200 else excerpt['excerpt']
            print(f"Content: {preview}")
        
        # Offer to generate full report
        response = input(f"\nGenerate full analysis report? (y/N): ").strip().lower()
        if response == 'y':
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"notebook_analysis_{timestamp}.md"
            analyzer.generate_analysis_report(report_file)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()