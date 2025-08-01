#!/usr/bin/env python3
"""
Conversation Word Cloud Generator
Analyzes most common words in conversations and messages, excluding duplicates and stop words
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import statistics

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL support not available. Install with: pip install psycopg2-binary")
    sys.exit(1)

@dataclass
class WordCloudData:
    """Data structure for word cloud analysis"""
    conversation_id: int
    conversation_score: float
    total_words: int
    unique_words: int
    top_words: List[Tuple[str, int]]
    word_frequency: Dict[str, int]
    primary_topic: str
    editorial_potential: str
    title: str = "Untitled Conversation"

class ConversationWordCloud:
    """Generates word clouds for conversations excluding duplicates"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        
        # Extended stop words list
        self.stop_words = {
            # Common English stop words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'out', 'off', 'down', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'can', 'will', 'just', 'should', 'now',
            
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            
            # Common verbs
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'having', 'do', 'does', 'did', 'doing', 'would', 'could', 'should', 'may', 'might',
            'must', 'shall', 'will', 'can',
            
            # Conversational words
            'yes', 'no', 'ok', 'okay', 'sure', 'well', 'oh', 'ah', 'um', 'uh', 'like', 'get',
            'got', 'getting', 'go', 'going', 'went', 'come', 'coming', 'came', 'see', 'saw',
            'seen', 'look', 'looking', 'looked', 'know', 'knew', 'known', 'think', 'thought',
            'thinking', 'say', 'said', 'saying', 'tell', 'told', 'telling', 'ask', 'asked',
            'asking', 'give', 'gave', 'given', 'giving', 'take', 'took', 'taken', 'taking',
            'make', 'made', 'making', 'put', 'putting', 'let', 'lets', 'try', 'trying', 'tried',
            'want', 'wanted', 'wanting', 'need', 'needed', 'needing', 'use', 'used', 'using',
            'work', 'working', 'worked', 'help', 'helping', 'helped',
            
            # Technical/formatting words
            'also', 'however', 'therefore', 'thus', 'hence', 'furthermore', 'moreover',
            'additionally', 'specifically', 'particularly', 'especially', 'basically',
            'essentially', 'generally', 'typically', 'usually', 'often', 'sometimes',
            'always', 'never', 'really', 'actually', 'quite', 'rather', 'pretty',
            'much', 'many', 'little', 'less', 'least', 'more', 'most', 'enough',
            'several', 'various', 'different', 'similar', 'same', 'another', 'others',
            'else', 'still', 'yet', 'already', 'since', 'until', 'unless', 'although',
            'though', 'while', 'whereas', 'because', 'if', 'whether', 'either', 'neither'
        }
        
        # Technical artifacts to filter
        self.technical_patterns = [
            r'^[a-f0-9]{8,}$',  # Hex strings
            r'^\d+$',           # Pure numbers
            r'^[A-Z]{2,}$',     # All caps abbreviations (2 chars)
            r'^www\.',          # URLs
            r'^http',           # URLs
            r'\.com$',          # Domains
            r'\.org$',          # Domains
            r'\.net$',          # Domains
            r'^[^\w\s]',        # Starts with punctuation
        ]
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_non_duplicate_conversations(self, min_score: float = 0.0, limit: int = None) -> List[Dict]:
        """Get conversations that are not marked as duplicates"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT qa.conversation_id, qa.composite_score, qa.primary_topic, 
                       qa.editorial_potential, qa.word_count, qa.message_count,
                       ac.title, ac.source_id
                FROM conversation_quality_assessments qa
                JOIN archived_content ac ON qa.conversation_id = ac.id
                WHERE qa.is_duplicate = FALSE
                    AND qa.composite_score >= %s
                ORDER BY qa.composite_score DESC
            """
            
            params = [min_score]
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_conversation_text(self, conversation_id: int) -> str:
        """Get all text content from a conversation"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT body_text
                FROM archived_content 
                WHERE parent_id = %s 
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                    AND word_count > 10
                ORDER BY timestamp
            """, (conversation_id,))
            
            messages = cursor.fetchall()
            return ' '.join([msg['body_text'] for msg in messages if msg['body_text']])
    
    def get_message_texts(self, conversation_id: int) -> List[Dict]:
        """Get individual message texts from a conversation"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, body_text, author, word_count
                FROM archived_content 
                WHERE parent_id = %s 
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                    AND word_count > 10
                ORDER BY timestamp
            """, (conversation_id,))
            
            return cursor.fetchall()
    
    def clean_text(self, text: str) -> str:
        """Clean text for word analysis"""
        if not text:
            return ""
        
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', ' ', text)
        text = re.sub(r'`[^`\n]+`', ' ', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', ' ', text)
        text = re.sub(r'www\.\S+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', ' ', text)
        
        # Remove JSON-like structures
        text = re.sub(r'\{[^}]*\}', ' ', text)
        text = re.sub(r'\[[^\]]*\]', ' ', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove special characters but keep apostrophes in words
        text = re.sub(r"[^\w\s']", ' ', text)
        
        # Remove standalone apostrophes and quotes
        text = re.sub(r"\s+'|'\s+", ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text.lower()
    
    def extract_words(self, text: str, min_length: int = 3) -> List[str]:
        """Extract meaningful words from text"""
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        filtered_words = []
        for word in words:
            # Skip stop words
            if word in self.stop_words:
                continue
            
            # Skip short words
            if len(word) < min_length:
                continue
            
            # Skip technical artifacts
            skip_word = False
            for pattern in self.technical_patterns:
                if re.match(pattern, word):
                    skip_word = True
                    break
            
            if skip_word:
                continue
            
            # Clean up word endings
            word = word.strip("'\".,!?;:")
            
            if len(word) >= min_length and word.isalpha():
                filtered_words.append(word)
        
        return filtered_words
    
    def analyze_conversation_words(self, conversation_data: Dict, top_n: int = 50) -> WordCloudData:
        """Analyze word frequency for a single conversation"""
        
        conversation_id = conversation_data['conversation_id']
        conversation_text = self.get_conversation_text(conversation_id)
        
        if not conversation_text:
            return WordCloudData(
                conversation_id=conversation_id,
                conversation_score=float(conversation_data['composite_score']),
                total_words=0,
                unique_words=0,
                top_words=[],
                word_frequency={},
                primary_topic=conversation_data.get('primary_topic', 'unknown'),
                editorial_potential=conversation_data.get('editorial_potential', 'unknown'),
                title=conversation_data.get('title', f"Conversation {conversation_id}")
            )
        
        # Extract and count words
        words = self.extract_words(conversation_text)
        word_counts = Counter(words)
        
        # Get top words
        top_words = word_counts.most_common(top_n)
        
        return WordCloudData(
            conversation_id=conversation_id,
            conversation_score=float(conversation_data['composite_score']),
            total_words=len(words),
            unique_words=len(word_counts),
            top_words=top_words,
            word_frequency=dict(word_counts),
            primary_topic=conversation_data.get('primary_topic', 'unknown'),
            editorial_potential=conversation_data.get('editorial_potential', 'unknown'),
            title=conversation_data.get('title', f"Conversation {conversation_id}")
        )
    
    def analyze_message_words(self, conversation_id: int, min_words: int = 20) -> List[Dict]:
        """Analyze word frequency for individual messages in a conversation"""
        
        messages = self.get_message_texts(conversation_id)
        message_analyses = []
        
        for msg in messages:
            if msg['word_count'] < min_words:
                continue
            
            words = self.extract_words(msg['body_text'])
            if len(words) < 10:  # Skip messages with too few meaningful words
                continue
            
            word_counts = Counter(words)
            top_words = word_counts.most_common(10)  # Top 10 for messages
            
            message_analyses.append({
                'message_id': msg['id'],
                'author': msg['author'],
                'word_count': msg['word_count'],
                'meaningful_words': len(words),
                'unique_words': len(word_counts),
                'top_words': top_words,
                'word_frequency': dict(word_counts)
            })
        
        return message_analyses
    
    def generate_global_word_cloud(self, conversation_analyses: List[WordCloudData]) -> Dict[str, int]:
        """Generate a global word cloud from all conversations"""
        
        global_word_counts = Counter()
        
        for analysis in conversation_analyses:
            # Weight words by conversation quality score
            weight = max(0.1, analysis.conversation_score)  # Minimum weight of 0.1
            
            for word, count in analysis.word_frequency.items():
                global_word_counts[word] += int(count * weight)
        
        return dict(global_word_counts)
    
    def run_word_cloud_analysis(self, min_score: float = 0.5, limit: int = 50, 
                               include_messages: bool = False) -> Dict[str, Any]:
        """Run complete word cloud analysis"""
        
        print(f"🔍 Analyzing word patterns in non-duplicate conversations")
        print(f"   Minimum score: {min_score}")
        print(f"   Limit: {limit}")
        print(f"   Include message analysis: {include_messages}")
        
        # Get eligible conversations
        conversations = self.get_non_duplicate_conversations(min_score, limit)
        
        if not conversations:
            print("❌ No conversations found meeting criteria")
            return {}
        
        print(f"📊 Processing {len(conversations)} conversations...")
        
        conversation_analyses = []
        message_analyses = {}
        
        for i, conversation in enumerate(conversations, 1):
            conv_id = conversation['conversation_id']
            print(f"   {i:3d}/{len(conversations)}: Analyzing conversation {conv_id} (score: {conversation['composite_score']:.3f})")
            
            try:
                # Analyze conversation words
                conv_analysis = self.analyze_conversation_words(conversation)
                conversation_analyses.append(conv_analysis)
                
                print(f"      📝 {conv_analysis.total_words} words, {conv_analysis.unique_words} unique")
                print(f"      🏆 Top words: {', '.join([f'{word}({count})' for word, count in conv_analysis.top_words[:5]])}")
                
                # Analyze message words if requested
                if include_messages:
                    msg_analysis = self.analyze_message_words(conv_id)
                    if msg_analysis:
                        message_analyses[conv_id] = msg_analysis
                        print(f"      💬 {len(msg_analysis)} messages analyzed")
                
            except Exception as e:
                print(f"      ❌ Error analyzing conversation: {e}")
                continue
        
        # Generate global word cloud
        print(f"\n🌐 Generating global word cloud...")
        global_word_cloud = self.generate_global_word_cloud(conversation_analyses)
        global_top_words = Counter(global_word_cloud).most_common(100)
        
        print(f"   📊 Global top words: {', '.join([f'{word}({count})' for word, count in global_top_words[:10]])}")
        
        # Compile results
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'parameters': {
                'min_score': min_score,
                'limit': limit,
                'include_messages': include_messages
            },
            'summary': {
                'conversations_analyzed': len(conversation_analyses),
                'total_words_processed': sum(a.total_words for a in conversation_analyses),
                'unique_words_global': len(global_word_cloud),
                'messages_analyzed': sum(len(msgs) for msgs in message_analyses.values()) if include_messages else 0
            },
            'global_word_cloud': global_top_words,
            'conversations': [
                {
                    'conversation_id': a.conversation_id,
                    'title': a.title,
                    'conversation_score': a.conversation_score,
                    'primary_topic': a.primary_topic,
                    'editorial_potential': a.editorial_potential,
                    'total_words': a.total_words,
                    'unique_words': a.unique_words,
                    'top_words': a.top_words
                }
                for a in conversation_analyses
            ]
        }
        
        if include_messages:
            results['messages'] = message_analyses
        
        return results
    
    def export_results(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Export word cloud results to files"""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"word_cloud_analysis_{timestamp}"
        
        base_path = Path("test_runs") / output_file
        base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export JSON
        json_file = f"{base_path}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Export readable markdown report
        md_file = f"{base_path}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Word Cloud Analysis Report\n\n")
            f.write(f"**Generated:** {results['analysis_timestamp']}\n")
            f.write(f"**Conversations Analyzed:** {results['summary']['conversations_analyzed']:,}\n")
            f.write(f"**Total Words Processed:** {results['summary']['total_words_processed']:,}\n")
            f.write(f"**Global Unique Words:** {results['summary']['unique_words_global']:,}\n\n")
            
            # Global word cloud
            f.write(f"## 🌐 Global Word Cloud (Top 50)\n\n")
            global_words = results['global_word_cloud'][:50]
            for i, (word, count) in enumerate(global_words, 1):
                f.write(f"{i:2d}. **{word}** ({count:,} weighted occurrences)\n")
            
            f.write(f"\n## 📊 Top Conversations by Word Diversity\n\n")
            # Sort by unique words
            sorted_convs = sorted(results['conversations'], key=lambda x: x['unique_words'], reverse=True)
            
            for i, conv in enumerate(sorted_convs[:20], 1):
                title = conv.get('title', f"Conversation {conv['conversation_id']}")
                f.write(f"### {i}. {title} (Score: {conv['conversation_score']:.3f})\n")
                f.write(f"- **ID:** {conv['conversation_id']}\n")
                f.write(f"- **Topic:** {conv['primary_topic']}\n")
                f.write(f"- **Editorial Potential:** {conv['editorial_potential']}\n")
                f.write(f"- **Total Words:** {conv['total_words']:,}\n")
                f.write(f"- **Unique Words:** {conv['unique_words']:,}\n")
                f.write(f"- **Top Words:** {', '.join([f'{word}({count})' for word, count in conv['top_words'][:10]])}\n\n")
        
        print(f"\n📄 Results exported:")
        print(f"   JSON: {json_file}")
        print(f"   Report: {md_file}")
        
        return str(base_path)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Conversation Word Cloud Generator - Analyze word patterns in non-duplicate conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze top 50 conversations with word clouds
  python conversation_word_cloud.py --limit 50 --min-score 0.5

  # Include message-level analysis  
  python conversation_word_cloud.py --limit 30 --include-messages

  # Focus on high-quality conversations only
  python conversation_word_cloud.py --limit 20 --min-score 0.7

  # Analyze all eligible conversations
  python conversation_word_cloud.py --limit 1000 --min-score 0.0
        """
    )
    
    parser.add_argument('--limit', type=int, default=50, 
                       help='Maximum conversations to analyze (default: 50)')
    parser.add_argument('--min-score', type=float, default=0.5,
                       help='Minimum conversation quality score (default: 0.5)')
    parser.add_argument('--include-messages', action='store_true',
                       help='Include message-level word analysis')
    parser.add_argument('--output', help='Output file base name')
    
    args = parser.parse_args()
    
    analyzer = ConversationWordCloud()
    
    # Run analysis
    results = analyzer.run_word_cloud_analysis(
        min_score=args.min_score,
        limit=args.limit,
        include_messages=args.include_messages
    )
    
    if not results:
        print("❌ No results generated")
        return
    
    # Export results
    output_path = analyzer.export_results(results, args.output)
    
    print(f"\n{'='*80}")
    print(f"🎉 WORD CLOUD ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"📊 Conversations analyzed: {results['summary']['conversations_analyzed']:,}")
    print(f"📝 Words processed: {results['summary']['total_words_processed']:,}")
    print(f"🔤 Unique words found: {results['summary']['unique_words_global']:,}")
    print(f"📄 Results saved to: {output_path}")


if __name__ == "__main__":
    main()