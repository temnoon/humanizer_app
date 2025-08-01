#!/usr/bin/env python3
"""
Comprehensive Metadata Browser for Humanizer Archive
Provides interactive exploration of all conversation metadata including wordclouds, categories, assessments, and more
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from collections import Counter, defaultdict
import re

class MetadataBrowser:
    """Interactive browser for all conversation metadata"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.current_filters = {}
        self.current_selection = []
        
        print("🔍 Humanizer Archive Metadata Browser")
        print("=" * 50)
    
    def get_metadata_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of all available metadata"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            overview = {
                'content_stats': {},
                'quality_distribution': {},
                'category_distribution': {},
                'temporal_distribution': {},
                'metadata_completeness': {}
            }
            
            # Content statistics
            cursor.execute("""
                SELECT 
                    content_type,
                    COUNT(*) as count,
                    AVG(ac.word_count) as avg_words,
                    COUNT(CASE WHEN category IS NOT NULL THEN 1 END) as categorized,
                    COUNT(CASE WHEN semantic_vector IS NOT NULL THEN 1 END) as embedded
                FROM archived_content ac
                GROUP BY content_type
            """)
            overview['content_stats'] = {row['content_type']: dict(row) for row in cursor.fetchall()}
            
            # Quality distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN composite_score >= 0.8 THEN 'excellent'
                        WHEN composite_score >= 0.6 THEN 'good'
                        WHEN composite_score >= 0.4 THEN 'fair'
                        WHEN composite_score >= 0.2 THEN 'poor'
                        ELSE 'very_poor'
                    END as quality_tier,
                    COUNT(*) as count,
                    AVG(composite_score) as avg_score,
                    AVG(ac.word_count) as avg_words
                FROM conversation_quality_assessments cqa
                JOIN archived_content ac ON cqa.conversation_id = ac.id
                WHERE cqa.is_duplicate = FALSE
                GROUP BY quality_tier
                ORDER BY avg_score DESC
            """)
            overview['quality_distribution'] = {row['quality_tier']: dict(row) for row in cursor.fetchall()}
            
            # Category distribution
            cursor.execute("""
                SELECT 
                    category,
                    COUNT(*) as count,
                    AVG(category_confidence) as avg_confidence,
                    AVG(word_count) as avg_words
                FROM archived_content 
                WHERE category IS NOT NULL AND content_type = 'conversation'
                GROUP BY category
                ORDER BY count DESC
                LIMIT 20
            """)
            overview['category_distribution'] = {row['category']: dict(row) for row in cursor.fetchall()}
            
            # Temporal distribution
            cursor.execute("""
                SELECT 
                    DATE_TRUNC('month', timestamp) as month,
                    COUNT(*) as conversations,
                    AVG(word_count) as avg_words
                FROM archived_content 
                WHERE content_type = 'conversation' AND timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month DESC
                LIMIT 12
            """)
            overview['temporal_distribution'] = [dict(row) for row in cursor.fetchall()]
            
            # Metadata completeness
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(category) as has_category,
                    COUNT(semantic_vector) as has_embedding,
                    COUNT(extracted_attributes) as has_attributes,
                    COUNT(content_quality_score) as has_quality_score,
                    COUNT(search_terms) as has_search_terms
                FROM archived_content 
                WHERE content_type = 'conversation'
            """)
            row = cursor.fetchone()
            total = row['total']
            overview['metadata_completeness'] = {
                field: {'count': row[field], 'percentage': (row[field]/total*100) if total > 0 else 0}
                for field in ['has_category', 'has_embedding', 'has_attributes', 'has_quality_score', 'has_search_terms']
            }
            
        return overview
    
    def search_conversations(self, 
                           category: Optional[str] = None,
                           min_quality: Optional[float] = None,
                           max_quality: Optional[float] = None,
                           min_words: Optional[int] = None,
                           max_words: Optional[int] = None,
                           keyword: Optional[str] = None,
                           has_embedding: Optional[bool] = None,
                           date_from: Optional[str] = None,
                           date_to: Optional[str] = None,
                           limit: int = 100) -> List[Dict]:
        """Search conversations with comprehensive metadata filtering"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            # Build dynamic query
            conditions = ["ac.content_type = 'conversation'"]
            params = []
            
            if category:
                conditions.append("ac.category ILIKE %s")
                params.append(f"%{category}%")
            
            if min_quality is not None:
                conditions.append("cqa.composite_score >= %s")
                params.append(min_quality)
                
            if max_quality is not None:
                conditions.append("cqa.composite_score <= %s")
                params.append(max_quality)
            
            if min_words:
                conditions.append("COALESCE(cqa.word_count, ac.word_count, 0) >= %s")
                params.append(min_words)
                
            if max_words:
                conditions.append("COALESCE(cqa.word_count, ac.word_count, 0) <= %s")
                params.append(max_words)
            
            if keyword:
                conditions.append("(ac.title ILIKE %s OR ac.body_text ILIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if has_embedding is not None:
                if has_embedding:
                    conditions.append("ac.semantic_vector IS NOT NULL")
                else:
                    conditions.append("ac.semantic_vector IS NULL")
            
            if date_from:
                conditions.append("ac.timestamp >= %s")
                params.append(date_from)
                
            if date_to:
                conditions.append("ac.timestamp <= %s")
                params.append(date_to)
            
            query = f"""
                SELECT 
                    ac.id,
                    ac.title,
                    COALESCE(cqa.word_count, ac.word_count, 0) as word_count,
                    ac.category,
                    ac.category_confidence,
                    ac.timestamp,
                    ac.author,
                    ac.search_terms,
                    ac.extracted_attributes,
                    cqa.composite_score,
                    cqa.readability_score,
                    cqa.coherence_score,
                    cqa.depth_score,
                    cqa.completeness_score,
                    cqa.primary_topic,
                    cqa.editorial_potential,
                    CASE WHEN ac.semantic_vector IS NOT NULL THEN TRUE ELSE FALSE END as has_embedding
                FROM archived_content ac
                LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                WHERE {' AND '.join(conditions)}
                ORDER BY cqa.composite_score DESC NULLS LAST, COALESCE(cqa.word_count, ac.word_count, 0) DESC
                LIMIT %s
            """
            
            params.append(limit)
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
    
    def get_conversation_details(self, conversation_id: int) -> Dict[str, Any]:
        """Get complete metadata for a specific conversation"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            # Main conversation data
            cursor.execute("""
                SELECT 
                    ac.*,
                    cqa.word_count as qa_word_count,
                    cqa.message_count,
                    cqa.code_density,
                    cqa.readability_score,
                    cqa.coherence_score,
                    cqa.depth_score,
                    cqa.completeness_score,
                    cqa.composite_score,
                    cqa.primary_topic,
                    cqa.editorial_potential,
                    cqa.assessment_metadata,
                    cqa.content_hash,
                    cqa.is_duplicate
                FROM archived_content ac
                LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                WHERE ac.id = %s
            """, (conversation_id,))
            
            conversation = cursor.fetchone()
            if not conversation:
                return {}
            
            result = dict(conversation)
            
            # Get messages for this conversation
            cursor.execute("""
                SELECT id, author, body_text, timestamp, word_count
                FROM archived_content 
                WHERE parent_id = %s AND content_type = 'message'
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            result['messages'] = [dict(row) for row in cursor.fetchall()]
            
            # Get semantic chunks if available
            cursor.execute("""
                SELECT level, summary, embedding IS NOT NULL as has_embedding
                FROM semantic_chunks 
                WHERE conversation_id = %s
                ORDER BY level ASC
            """, (conversation_id,))
            
            result['semantic_chunks'] = [dict(row) for row in cursor.fetchall()]
            
            return result
    
    def analyze_patterns(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in a set of conversations"""
        
        if not conversations:
            return {}
        
        df = pd.DataFrame(conversations)
        
        patterns = {
            'quality_patterns': {},
            'category_patterns': {},
            'temporal_patterns': {},
            'length_patterns': {},
            'correlation_analysis': {}
        }
        
        # Quality patterns
        if 'composite_score' in df.columns:
            patterns['quality_patterns'] = {
                'mean_quality': df['composite_score'].mean(),
                'std_quality': df['composite_score'].std(),
                'quality_quartiles': df['composite_score'].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        
        # Category patterns
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            patterns['category_patterns'] = {
                'top_categories': category_counts.head(10).to_dict(),
                'category_diversity': len(category_counts),
                'avg_confidence': df['category_confidence'].mean() if 'category_confidence' in df.columns else None
            }
        
        # Temporal patterns
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['weekday'] = df['timestamp'].dt.day_name()
            
            patterns['temporal_patterns'] = {
                'peak_hours': df['hour'].value_counts().head(5).to_dict(),
                'peak_days': df['weekday'].value_counts().to_dict(),
                'date_range': {
                    'earliest': df['timestamp'].min().isoformat(),
                    'latest': df['timestamp'].max().isoformat()
                }
            }
        
        # Length patterns
        if 'word_count' in df.columns:
            patterns['length_patterns'] = {
                'mean_length': df['word_count'].mean(),
                'median_length': df['word_count'].median(),
                'length_quartiles': df['word_count'].quantile([0.25, 0.5, 0.75]).to_dict(),
                'very_long': len(df[df['word_count'] > 2000]),
                'very_short': len(df[df['word_count'] < 100])
            }
        
        # Correlation analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            correlations = df[numeric_cols].corr()
            # Get strongest correlations
            mask = np.triu(np.ones_like(correlations), k=1).astype(bool)
            correlations = correlations.where(mask)
            
            strong_correlations = []
            for col in correlations.columns:
                for idx in correlations.index:
                    val = correlations.loc[idx, col]
                    if pd.notna(val) and abs(val) > 0.5:
                        strong_correlations.append({
                            'variables': f"{idx} <-> {col}",
                            'correlation': val,
                            'strength': 'strong' if abs(val) > 0.7 else 'moderate'
                        })
            
            patterns['correlation_analysis'] = {
                'strong_correlations': sorted(strong_correlations, key=lambda x: abs(x['correlation']), reverse=True)[:10]
            }
        
        return patterns
    
    def export_selection(self, conversations: List[Dict], 
                        export_format: str = 'json',
                        output_file: Optional[str] = None) -> str:
        """Export selected conversations with full metadata"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not output_file:
            output_file = f"metadata_export_{timestamp}.{export_format}"
        
        if export_format == 'json':
            # Get detailed metadata for each conversation
            detailed_conversations = []
            for conv in conversations:
                detailed = self.get_conversation_details(conv['id'])
                detailed_conversations.append(detailed)
            
            with open(output_file, 'w') as f:
                json.dump({
                    'export_info': {
                        'timestamp': timestamp,
                        'count': len(detailed_conversations),
                        'filters_applied': self.current_filters
                    },
                    'conversations': detailed_conversations
                }, f, indent=2, default=str)
        
        elif export_format == 'csv':
            # Flatten metadata for CSV
            df = pd.DataFrame(conversations)
            df.to_csv(output_file, index=False)
        
        elif export_format == 'markdown':
            # Create readable markdown report
            with open(output_file, 'w') as f:
                f.write(f"# Metadata Export Report\n\n")
                f.write(f"**Generated**: {timestamp}\n")
                f.write(f"**Conversations**: {len(conversations)}\n\n")
                
                if self.current_filters:
                    f.write("## Filters Applied\n\n")
                    for key, value in self.current_filters.items():
                        f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
                
                f.write("## Conversations\n\n")
                for conv in conversations:
                    f.write(f"### {conv.get('title', 'Untitled')} (ID: {conv['id']})\n\n")
                    f.write(f"- **Category**: {conv.get('category', 'N/A')}\n")
                    f.write(f"- **Quality Score**: {conv.get('composite_score', 'N/A'):.3f}\n")
                    f.write(f"- **Word Count**: {conv.get('word_count', 'N/A'):,}\n")
                    f.write(f"- **Date**: {conv.get('timestamp', 'N/A')}\n")
                    f.write(f"- **Primary Topic**: {conv.get('primary_topic', 'N/A')}\n")
                    f.write(f"- **Editorial Potential**: {conv.get('editorial_potential', 'N/A')}\n")
                    f.write("\n")
        
        print(f"📁 Exported {len(conversations)} conversations to: {output_file}")
        return output_file
    
    def interactive_browse(self):
        """Interactive browsing session"""
        
        print("\n🔍 Interactive Metadata Browser")
        print("Commands: overview, search, details <id>, analyze, export, help, quit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit' or command == 'q':
                    break
                    
                elif command == 'overview':
                    overview = self.get_metadata_overview()
                    self._print_overview(overview)
                
                elif command.startswith('search'):
                    self._interactive_search()
                
                elif command.startswith('details'):
                    parts = command.split()
                    if len(parts) > 1:
                        try:
                            conv_id = int(parts[1])
                            details = self.get_conversation_details(conv_id)
                            self._print_conversation_details(details)
                        except ValueError:
                            print("❌ Please provide a valid conversation ID")
                    else:
                        print("❌ Usage: details <conversation_id>")
                
                elif command == 'analyze':
                    if self.current_selection:
                        patterns = self.analyze_patterns(self.current_selection)
                        self._print_patterns(patterns)
                    else:
                        print("❌ No conversations selected. Run a search first.")
                
                elif command.startswith('export'):
                    if self.current_selection:
                        parts = command.split()
                        format_type = parts[1] if len(parts) > 1 else 'json'
                        self.export_selection(self.current_selection, format_type)
                    else:
                        print("❌ No conversations selected. Run a search first.")
                
                elif command == 'help':
                    self._print_help()
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _interactive_search(self):
        """Interactive search with filters"""
        
        print("\n🔍 Search Filters (press Enter to skip):")
        
        filters = {}
        
        category = input("Category (partial match): ").strip()
        if category:
            filters['category'] = category
        
        min_quality = input("Minimum quality score (0-1): ").strip()
        if min_quality:
            try:
                filters['min_quality'] = float(min_quality)
            except ValueError:
                print("⚠️ Invalid quality score, skipping")
        
        keyword = input("Keyword search: ").strip()
        if keyword:
            filters['keyword'] = keyword
        
        min_words = input("Minimum word count: ").strip()
        if min_words:
            try:
                filters['min_words'] = int(min_words)
            except ValueError:
                print("⚠️ Invalid word count, skipping")
        
        limit = input("Result limit (default 50): ").strip()
        if limit:
            try:
                filters['limit'] = int(limit)
            except ValueError:
                filters['limit'] = 50
        else:
            filters['limit'] = 50
        
        print(f"\n🔍 Searching with filters: {filters}")
        
        results = self.search_conversations(**filters)
        self.current_selection = results
        self.current_filters = filters
        
        print(f"\n📊 Found {len(results)} conversations")
        
        if results:
            print("\nTop results:")
            for i, conv in enumerate(results[:10]):
                score = conv.get('composite_score', 0) or 0
                category = conv.get('category') or 'N/A'
                words = conv.get('word_count', 0) or 0
                title = conv.get('title') or 'Untitled'
                title = title[:60] if title else 'Untitled'
                print(f"  {i+1:2d}. [{conv['id']:5d}] {score:.3f} | {category:12s} | {words:5,}w | {title}")
            
            if len(results) > 10:
                print(f"    ... and {len(results) - 10} more")
    
    def _print_overview(self, overview: Dict):
        """Print formatted overview"""
        
        print("\n📊 Metadata Overview")
        print("=" * 50)
        
        print("\n📈 Content Statistics:")
        for content_type, stats in overview['content_stats'].items():
            print(f"  {content_type:12s}: {stats['count']:5,} items, avg {stats.get('avg_words', 0):6.0f} words")
        
        print("\n🎯 Quality Distribution:")
        for tier, stats in overview['quality_distribution'].items():
            print(f"  {tier:12s}: {stats['count']:4,} convs, avg score {stats['avg_score']:.3f}")
        
        print("\n📂 Top Categories:")
        for category, stats in list(overview['category_distribution'].items())[:10]:
            conf = stats.get('avg_confidence', 0)
            print(f"  {category:15s}: {stats['count']:4,} convs, confidence {conf:.2f}")
        
        print("\n📅 Recent Activity:")
        for period in overview['temporal_distribution'][:6]:
            month = period['month'].strftime('%Y-%m') if period['month'] else 'N/A'
            print(f"  {month}: {period['conversations']:4,} conversations")
        
        print("\n✅ Metadata Completeness:")
        for field, stats in overview['metadata_completeness'].items():
            field_name = field.replace('has_', '').replace('_', ' ').title()
            print(f"  {field_name:15s}: {stats['count']:5,} ({stats['percentage']:5.1f}%)")
    
    def _print_conversation_details(self, details: Dict):
        """Print detailed conversation information"""
        
        if not details:
            print("❌ Conversation not found")
            return
        
        print(f"\n📄 Conversation Details (ID: {details['id']})")
        print("=" * 60)
        
        print(f"Title: {details.get('title', 'Untitled')}")
        print(f"Category: {details.get('category', 'N/A')} (confidence: {details.get('category_confidence', 0):.2f})")
        print(f"Word Count: {details.get('word_count', 0):,}")
        print(f"Date: {details.get('timestamp', 'N/A')}")
        print(f"Author: {details.get('author', 'N/A')}")
        
        if details.get('composite_score'):
            print(f"\n📊 Quality Scores:")
            print(f"  Composite: {details['composite_score']:.3f}")
            print(f"  Readability: {details.get('readability_score', 0):.3f}")
            print(f"  Coherence: {details.get('coherence_score', 0):.3f}")
            print(f"  Depth: {details.get('depth_score', 0):.3f}")
            print(f"  Completeness: {details.get('completeness_score', 0):.3f}")
        
        if details.get('primary_topic'):
            print(f"Primary Topic: {details['primary_topic']}")
        
        if details.get('editorial_potential'):
            print(f"Editorial Potential: {details['editorial_potential']}")
        
        if details.get('search_terms'):
            print(f"Search Terms: {', '.join(details['search_terms'])}")
        
        if details.get('messages'):
            print(f"\n💬 Messages: {len(details['messages'])}")
            for i, msg in enumerate(details['messages'][:3]):
                author = msg.get('author', 'Unknown')
                words = msg.get('word_count', 0)
                preview = msg.get('body_text', '')[:100] + "..." if len(msg.get('body_text', '')) > 100 else msg.get('body_text', '')
                print(f"  {i+1}. {author} ({words} words): {preview}")
            
            if len(details['messages']) > 3:
                print(f"    ... and {len(details['messages']) - 3} more messages")
        
        if details.get('semantic_chunks'):
            print(f"\n🧠 Semantic Chunks: {len(details['semantic_chunks'])}")
            for chunk in details['semantic_chunks']:
                level = chunk.get('level', 'N/A')
                has_embedding = "✅" if chunk.get('has_embedding') else "❌"
                summary = chunk.get('summary', 'No summary')
                if summary and len(summary) > 80:
                    summary = summary[:80] + "..."
                elif not summary:
                    summary = 'No summary'
                print(f"  Level {level} {has_embedding}: {summary}")
    
    def _print_patterns(self, patterns: Dict):
        """Print pattern analysis results"""
        
        print("\n📈 Pattern Analysis")
        print("=" * 50)
        
        if 'quality_patterns' in patterns:
            qp = patterns['quality_patterns']
            print(f"\n🎯 Quality Patterns:")
            print(f"  Mean Quality: {qp.get('mean_quality', 0):.3f}")
            print(f"  Std Dev: {qp.get('std_quality', 0):.3f}")
            if 'quality_quartiles' in qp:
                print(f"  Quartiles: Q1={qp['quality_quartiles'].get(0.25, 0):.3f}, Q2={qp['quality_quartiles'].get(0.5, 0):.3f}, Q3={qp['quality_quartiles'].get(0.75, 0):.3f}")
        
        if 'category_patterns' in patterns:
            cp = patterns['category_patterns']
            print(f"\n📂 Category Patterns:")
            print(f"  Diversity: {cp.get('category_diversity', 0)} unique categories")
            if cp.get('avg_confidence'):
                print(f"  Avg Confidence: {cp['avg_confidence']:.3f}")
            if 'top_categories' in cp:
                print("  Top Categories:")
                for cat, count in list(cp['top_categories'].items())[:5]:
                    print(f"    {cat}: {count}")
        
        if 'temporal_patterns' in patterns:
            tp = patterns['temporal_patterns']
            print(f"\n📅 Temporal Patterns:")
            if 'peak_hours' in tp:
                print("  Peak Hours:")
                for hour, count in list(tp['peak_hours'].items())[:3]:
                    print(f"    {hour:02d}:00 - {count} conversations")
            if 'peak_days' in tp:
                print("  Peak Days:")
                for day, count in list(tp['peak_days'].items())[:3]:
                    print(f"    {day} - {count} conversations")
        
        if 'correlation_analysis' in patterns:
            ca = patterns['correlation_analysis']
            if 'strong_correlations' in ca and ca['strong_correlations']:
                print(f"\n🔗 Strong Correlations:")
                for corr in ca['strong_correlations'][:5]:
                    print(f"  {corr['variables']}: {corr['correlation']:.3f} ({corr['strength']})")
    
    def _print_help(self):
        """Print help information"""
        
        print("\n🆘 Metadata Browser Help")
        print("=" * 30)
        print("overview        - Show metadata overview statistics")
        print("search          - Interactive search with filters")
        print("details <id>    - Show detailed metadata for conversation")
        print("analyze         - Analyze patterns in current selection")
        print("export [format] - Export selection (json/csv/markdown)")
        print("help            - Show this help")
        print("quit            - Exit browser")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Metadata Browser for Humanizer Archive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive browsing
  python metadata_browser.py browse

  # Quick overview
  python metadata_browser.py overview

  # Search with filters
  python metadata_browser.py search --category philosophical --min-quality 0.6

  # Export high-quality conversations
  python metadata_browser.py search --min-quality 0.8 --export json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Browse command
    browse_parser = subparsers.add_parser('browse', help='Interactive browsing session')
    
    # Overview command
    overview_parser = subparsers.add_parser('overview', help='Show metadata overview')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search with filters')
    search_parser.add_argument('--category', help='Category filter')
    search_parser.add_argument('--min-quality', type=float, help='Minimum quality score')
    search_parser.add_argument('--max-quality', type=float, help='Maximum quality score')
    search_parser.add_argument('--min-words', type=int, help='Minimum word count')
    search_parser.add_argument('--max-words', type=int, help='Maximum word count')
    search_parser.add_argument('--keyword', help='Keyword search')
    search_parser.add_argument('--has-embedding', action='store_true', help='Has semantic embedding')
    search_parser.add_argument('--limit', type=int, default=50, help='Result limit')
    search_parser.add_argument('--export', choices=['json', 'csv', 'markdown'], help='Export results')
    
    args = parser.parse_args()
    
    browser = MetadataBrowser()
    
    if args.command == 'browse':
        browser.interactive_browse()
    
    elif args.command == 'overview':
        overview = browser.get_metadata_overview()
        browser._print_overview(overview)
    
    elif args.command == 'search':
        results = browser.search_conversations(
            category=args.category,
            min_quality=args.min_quality,
            max_quality=args.max_quality,
            min_words=args.min_words,
            max_words=args.max_words,
            keyword=args.keyword,
            has_embedding=args.has_embedding,
            limit=args.limit
        )
        
        browser.current_selection = results
        
        print(f"\n📊 Found {len(results)} conversations")
        if results:
            for i, conv in enumerate(results[:20]):
                score = conv.get('composite_score', 0) or 0
                category = conv.get('category') or 'N/A'
                words = conv.get('word_count', 0) or 0
                title = conv.get('title') or 'Untitled'
                title = title[:50] if title else 'Untitled'
                print(f"  {i+1:2d}. [{conv['id']:5d}] {score:.3f} | {category:12s} | {words:5,}w | {title}")
        
        if args.export:
            browser.export_selection(results, args.export)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()