#!/usr/bin/env python3
"""
Word Cloud Browser
Interactive tool to explore word clouds and frequency patterns from conversations
"""

import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re
from pathlib import Path

class WordCloudBrowser:
    """Interactive browser for word cloud analysis results"""
    
    def __init__(self, results_dir: str = "test_runs"):
        self.results_dir = results_dir
        self.available_analyses = self._find_available_analyses()
        
        if not self.available_analyses:
            print("❌ No word cloud analyses found!")
            print(f"   Looking in: {os.path.abspath(results_dir)}")
            print("   Generate word clouds with: haw wordcloud --limit 50")
            return
        
        print("🌐 Word Cloud Browser")
        print("=" * 30)
        print(f"Found {len(self.available_analyses)} word cloud analyses")
    
    def _find_available_analyses(self) -> List[Dict[str, str]]:
        """Find all available word cloud analyses"""
        analyses = []
        
        if not os.path.exists(self.results_dir):
            return analyses
        
        # Look for word cloud JSON files
        for filename in os.listdir(self.results_dir):
            if filename.startswith('word_cloud_analysis_') and filename.endswith('.json'):
                timestamp = filename.replace('word_cloud_analysis_', '').replace('.json', '')
                
                # Check for corresponding markdown file
                md_file = filename.replace('.json', '.md')
                
                analyses.append({
                    'timestamp': timestamp,
                    'json_file': os.path.join(self.results_dir, filename),
                    'md_file': os.path.join(self.results_dir, md_file) if os.path.exists(os.path.join(self.results_dir, md_file)) else None
                })
        
        # Sort by timestamp (most recent first)
        analyses.sort(key=lambda x: x['timestamp'], reverse=True)
        return analyses
    
    def list_analyses(self):
        """List all available word cloud analyses"""
        print("\n📋 Available Word Cloud Analyses:")
        print("-" * 50)
        
        for i, analysis in enumerate(self.available_analyses, 1):
            timestamp = analysis['timestamp']
            # Parse timestamp for display
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = timestamp
            
            print(f"  {i}. {date_str}")
            
            # Try to load basic info
            try:
                with open(analysis['json_file'], 'r') as f:
                    data = json.load(f)
                    
                conversations = data.get('conversations', [])
                summary = data.get('summary', {})
                global_word_cloud = data.get('global_word_cloud', [])
                
                print(f"     Conversations: {summary.get('conversations_analyzed', len(conversations)):,}")
                print(f"     Total words: {summary.get('total_words_processed', 'Unknown'):,}")
                print(f"     Unique words: {summary.get('unique_words_global', 'Unknown'):,}")
                
                if global_word_cloud:
                    top_5 = global_word_cloud[:5] if isinstance(global_word_cloud, list) else []
                    top_words_str = ', '.join([f"{word}({count})" for word, count in top_5])
                    print(f"     Top words: {top_words_str}")
                    
            except Exception as e:
                print(f"     (Unable to load details: {e})")
            print()
    
    def show_global_overview(self, analysis_index: int = 0):
        """Show global word cloud overview"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            conversations = data.get('conversations', [])
            global_word_cloud = data.get('global_word_cloud', [])
            
            print(f"\n🌐 Global Word Cloud Overview")
            print("=" * 50)
            print(f"Analysis Date: {analysis['timestamp']}")
            print(f"Conversations Analyzed: {summary.get('conversations_analyzed', len(conversations)):,}")
            print(f"Total Words Processed: {summary.get('total_words_processed', 0):,}")
            print(f"Unique Words Found: {summary.get('unique_words_global', 0):,}")
            
            # Top global words
            if global_word_cloud:
                print(f"\n🏆 Top Global Words:")
                print("-" * 25)
                for i, (word, count) in enumerate(global_word_cloud[:20], 1):
                    print(f"  {i:2d}. {word:<20} {count:>6,} occurrences")
            
            # Word length distribution
            word_lengths = data.get('word_lengths', {})
            if word_lengths:
                print(f"\n📏 Word Length Distribution:")
                print("-" * 30)
                print(f"  Average length: {word_lengths.get('average', 0):.1f} characters")
                print(f"  Shortest words: {word_lengths.get('shortest', [])}")
                print(f"  Longest words: {word_lengths.get('longest', [])}")
            
            # Category breakdown if available
            if conversations:
                category_counts = defaultdict(int)
                category_words = defaultdict(set)
                
                for conv in conversations:
                    category = conv.get('category', 'uncategorized')
                    category_counts[category] += 1
                    
                    for word, count in conv.get('top_words', [])[:5]:
                        category_words[category].add(word)
                
                print(f"\n📂 Content Categories:")
                print("-" * 22)
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    sample_words = ', '.join(list(category_words[category])[:5])
                    print(f"  {category:<15} {count:>3} convs | {sample_words}")
        
        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
    
    def search_by_word(self, search_word: str, analysis_index: int = 0, min_count: int = 1):
        """Search conversations containing a specific word"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            print(f"\n🔍 Conversations containing '{search_word}' (min {min_count}x)")
            print("-" * 60)
            
            matching_convs = []
            
            for conv in conversations:
                # Convert top_words list to frequency dict for searching
                word_freq = {}
                for word, count in conv.get('top_words', []):
                    word_freq[word.lower()] = count
                
                if search_word.lower() in word_freq and word_freq[search_word.lower()] >= min_count:
                    matching_convs.append((conv, word_freq[search_word.lower()]))
            
            # Sort by frequency of the search word
            matching_convs.sort(key=lambda x: x[1], reverse=True)
            
            if not matching_convs:
                print(f"❌ No conversations found containing '{search_word}' with count >= {min_count}")
                return
            
            print(f"Found {len(matching_convs)} matching conversations:")
            print()
            
            for i, (conv, word_count) in enumerate(matching_convs[:20], 1):
                title = conv.get('title', f"Conversation {conv.get('conversation_id', 'Unknown')}")
                title = title[:50] + "..." if len(title) > 50 else title
                
                score = conv.get('conversation_score', 0)
                total_words = conv.get('total_words', 0)
                
                print(f"{i:2d}. [{conv.get('conversation_id', 'Unknown'):6}] {title}")
                print(f"    '{search_word}': {word_count:3}x | Score: {score:.3f} | Total words: {total_words:,}")
                
                # Show other top words for context
                top_words = [f"{w}({c})" for w, c in conv.get('top_words', [])[:5]]
                print(f"    Context: {', '.join(top_words)}")
                print()
            
            if len(matching_convs) > 20:
                print(f"    ... and {len(matching_convs) - 20} more matches")
        
        except Exception as e:
            print(f"❌ Error searching: {e}")
    
    def search_by_topic(self, topic_words: List[str], analysis_index: int = 0):
        """Search conversations by topic (multiple related words)"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            print(f"\n🔍 Conversations about topic: {', '.join(topic_words)}")
            print("-" * 60)
            
            topic_matches = []
            
            for conv in conversations:
                # Convert top_words list to frequency dict for searching  
                word_freq = {}
                for word, count in conv.get('top_words', []):
                    word_freq[word.lower()] = count
                
                # Calculate topic relevance score
                topic_score = 0
                word_matches = {}
                
                for word in topic_words:
                    word_lower = word.lower()
                    if word_lower in word_freq:
                        count = word_freq[word_lower]
                        topic_score += count
                        word_matches[word] = count
                
                if topic_score > 0:
                    topic_matches.append((conv, topic_score, word_matches))
            
            # Sort by topic relevance
            topic_matches.sort(key=lambda x: x[1], reverse=True)
            
            if not topic_matches:
                print(f"❌ No conversations found containing any of: {', '.join(topic_words)}")
                return
            
            print(f"Found {len(topic_matches)} matching conversations:")
            print()
            
            for i, (conv, topic_score, word_matches) in enumerate(topic_matches[:15], 1):
                title = conv.get('title', f"Conversation {conv.get('conversation_id', 'Unknown')}")
                title = title[:50] + "..." if len(title) > 50 else title
                
                score = conv.get('conversation_score', 0)
                total_words = conv.get('total_words', 0)
                
                print(f"{i:2d}. [{conv.get('conversation_id', 'Unknown'):6}] {title}")
                print(f"    Topic score: {topic_score:3} | Quality: {score:.3f} | Total words: {total_words:,}")
                
                # Show which topic words were found
                matches_str = ', '.join([f"{word}({count})" for word, count in word_matches.items()])
                print(f"    Topic matches: {matches_str}")
                
                # Show other top words for context
                other_words = [f"{w}({c})" for w, c in conv.get('top_words', [])[:3] 
                             if w.lower() not in [tw.lower() for tw in topic_words]]
                print(f"    Other top words: {', '.join(other_words)}")
                print()
            
            if len(topic_matches) > 15:
                print(f"    ... and {len(topic_matches) - 15} more matches")
        
        except Exception as e:
            print(f"❌ Error searching: {e}")
    
    def search_by_title(self, title_query: str, analysis_index: int = 0):
        """Search conversations by title"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            print(f"\n🔍 Conversations with titles containing '{title_query}'")
            print("-" * 60)
            
            matching_convs = []
            
            for conv in conversations:
                title = conv.get('title', f"Conversation {conv.get('conversation_id', 'Unknown')}")
                if title_query.lower() in title.lower():
                    matching_convs.append(conv)
            
            if not matching_convs:
                print(f"❌ No conversations found with titles containing '{title_query}'")
                return
            
            print(f"Found {len(matching_convs)} matching conversations:")
            print()
            
            for i, conv in enumerate(matching_convs[:15], 1):
                title = conv.get('title', f"Conversation {conv.get('conversation_id', 'Unknown')}")
                conv_id = conv.get('conversation_id', 'Unknown')
                score = conv.get('conversation_score', 0)
                total_words = conv.get('total_words', 0)
                
                print(f" {i:2d}. [{conv_id}] {title}")
                print(f"     Score: {score:.3f} | Total words: {total_words:,}")
                
                # Show top words for context
                top_words = conv.get('top_words', [])[:5]
                context_words = ', '.join([f"{word}({count})" for word, count in top_words])
                print(f"     Context: {context_words}")
                print()
            
            if len(matching_convs) > 15:
                print(f"    ... and {len(matching_convs) - 15} more matches")
        
        except Exception as e:
            print(f"❌ Error searching by title: {e}")
    
    def show_conversation_details(self, conversation_id: int, analysis_index: int = 0):
        """Show detailed word cloud for a specific conversation"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            # Find the conversation
            target_conv = None
            for conv in conversations:
                if conv.get('conversation_id') == conversation_id:
                    target_conv = conv
                    break
            
            if not target_conv:
                print(f"❌ Conversation {conversation_id} not found in analysis")
                return
            
            print(f"\n📄 Word Cloud Details: Conversation {conversation_id}")
            print("=" * 60)
            
            title = target_conv.get('title', 'Untitled')
            print(f"Title: {title}")
            print(f"Quality Score: {target_conv.get('conversation_score', 0):.3f}")
            print(f"Total Words: {target_conv.get('total_words', 0):,}")
            print(f"Unique Words: {target_conv.get('unique_words', 0):,}")
            print(f"Primary Topic: {target_conv.get('primary_topic', 'N/A')}")
            print(f"Editorial Potential: {target_conv.get('editorial_potential', 'N/A')}")
            
            # Top words
            print(f"\n🏆 Top Words in This Conversation:")
            print("-" * 40)
            for i, (word, count) in enumerate(target_conv.get('top_words', [])[:25], 1):
                percentage = (count / target_conv.get('total_words', 1)) * 100
                print(f"  {i:2d}. {word:<20} {count:>4}x ({percentage:4.1f}%)")
            
            # Word frequency distribution
            word_freq = target_conv.get('word_frequency', {})
            if word_freq:
                freq_dist = defaultdict(int)
                for word, count in word_freq.items():
                    if count >= 5:  # Words appearing 5+ times
                        freq_dist[count] += 1
                
                if freq_dist:
                    print(f"\n📊 Word Frequency Distribution (5+ occurrences):")
                    print("-" * 45)
                    for freq in sorted(freq_dist.keys(), reverse=True)[:10]:
                        print(f"  {freq:2d}x occurrences: {freq_dist[freq]:2d} words")
        
        except Exception as e:
            print(f"❌ Error loading conversation details: {e}")
    
    def compare_conversations(self, conv_id1: int, conv_id2: int, analysis_index: int = 0):
        """Compare word clouds between two conversations"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            # Find both conversations
            conv1 = conv2 = None
            for conv in conversations:
                if conv.get('conversation_id') == conv_id1:
                    conv1 = conv
                elif conv.get('conversation_id') == conv_id2:
                    conv2 = conv
            
            if not conv1:
                print(f"❌ Conversation {conv_id1} not found")
                return
            if not conv2:
                print(f"❌ Conversation {conv_id2} not found")
                return
            
            print(f"\n🔄 Comparing Word Clouds")
            print("=" * 40)
            print(f"Conversation 1: {conv_id1} - {conv1.get('title', 'Untitled')[:30]}...")
            print(f"Conversation 2: {conv_id2} - {conv2.get('title', 'Untitled')[:30]}...")
            
            # Basic stats comparison
            print(f"\n📊 Basic Statistics:")
            print("-" * 25)
            print(f"{'Metric':<15} {'Conv 1':<10} {'Conv 2':<10} {'Difference':<10}")
            print("-" * 50)
            
            metrics = [
                ('Quality Score', 'conversation_score'),
                ('Total Words', 'total_words'),
                ('Unique Words', 'unique_words'),
            ]
            
            for metric_name, metric_key in metrics:
                val1 = conv1.get(metric_key, 0)
                val2 = conv2.get(metric_key, 0)
                diff = val2 - val1
                diff_str = f"{diff:+.0f}" if isinstance(diff, (int, float)) else str(diff)
                print(f"{metric_name:<15} {val1:<10} {val2:<10} {diff_str:<10}")
            
            # Word overlap analysis
            words1 = set(dict(conv1.get('word_frequency', {})).keys())
            words2 = set(dict(conv2.get('word_frequency', {})).keys())
            
            common_words = words1 & words2
            unique1 = words1 - words2
            unique2 = words2 - words1
            
            print(f"\n🔗 Word Overlap Analysis:")
            print("-" * 28)
            print(f"Common words: {len(common_words):,}")
            print(f"Unique to Conv 1: {len(unique1):,}")
            print(f"Unique to Conv 2: {len(unique2):,}")
            print(f"Overlap percentage: {len(common_words) / len(words1 | words2) * 100:.1f}%")
            
            # Top common words
            if common_words:
                freq1 = dict(conv1.get('word_frequency', {}))
                freq2 = dict(conv2.get('word_frequency', {}))
                
                common_with_freq = [(word, freq1[word], freq2[word]) for word in common_words]
                common_with_freq.sort(key=lambda x: x[1] + x[2], reverse=True)
                
                print(f"\n🏆 Top Common Words:")
                print("-" * 25)
                print(f"{'Word':<15} {'Conv 1':<8} {'Conv 2':<8} {'Total':<8}")
                print("-" * 45)
                
                for word, count1, count2 in common_with_freq[:10]:
                    total = count1 + count2
                    print(f"{word:<15} {count1:<8} {count2:<8} {total:<8}")
        
        except Exception as e:
            print(f"❌ Error comparing conversations: {e}")
    
    def find_trending_words(self, analysis_index: int = 0, min_conversations: int = 3):
        """Find words that appear across multiple conversations"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['json_file'], 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            # Count word appearances across conversations
            word_appearances = defaultdict(list)
            
            for conv in conversations:
                conv_id = conv.get('conversation_id')
                word_freq = dict(conv.get('word_frequency', {}))
                
                for word, count in word_freq.items():
                    if count >= 3:  # Word appears at least 3 times in the conversation
                        word_appearances[word].append((conv_id, count, conv.get('title', 'Untitled')))
            
            # Filter words that appear in multiple conversations
            trending_words = {word: appearances for word, appearances in word_appearances.items() 
                            if len(appearances) >= min_conversations}
            
            print(f"\n🔥 Trending Words (appearing in {min_conversations}+ conversations)")
            print("-" * 60)
            
            # Sort by total appearances across conversations
            trending_sorted = sorted(trending_words.items(), 
                                   key=lambda x: sum(count for _, count, _ in x[1]), 
                                   reverse=True)
            
            for word, appearances in trending_sorted[:20]:
                total_count = sum(count for _, count, _ in appearances)
                avg_count = total_count / len(appearances)
                
                print(f"🔥 '{word}' - {len(appearances)} conversations, {total_count} total occurrences (avg: {avg_count:.1f})")
                
                # Show top conversations for this word
                appearances.sort(key=lambda x: x[1], reverse=True)
                for conv_id, count, title in appearances[:3]:
                    title_short = title[:40] + "..." if len(title) > 40 else title
                    print(f"   [{conv_id:6}] {count:2}x - {title_short}")
                
                if len(appearances) > 3:
                    print(f"   ... and {len(appearances) - 3} more conversations")
                print()
        
        except Exception as e:
            print(f"❌ Error finding trending words: {e}")
    
    def interactive_browse(self):
        """Interactive browsing session"""
        if not self.available_analyses:
            return
        
        print("\n🔍 Interactive Word Cloud Browser")
        print("Commands: list, overview [N], search <word>, topic <word1> <word2>, title <query>, details <conv_id>, compare <id1> <id2>, trending, help, quit")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() in ['quit', 'q', 'exit']:
                    break
                
                elif command == 'list':
                    self.list_analyses()
                
                elif command.startswith('overview'):
                    parts = command.split()
                    index = int(parts[1]) - 1 if len(parts) > 1 else 0
                    self.show_global_overview(index)
                
                elif command.startswith('search '):
                    parts = command.split()
                    if len(parts) >= 2:
                        word = parts[1]
                        min_count = int(parts[2]) if len(parts) > 2 else 1
                        self.search_by_word(word, min_count=min_count)
                    else:
                        print("❌ Usage: search <word> [min_count]")
                
                elif command.startswith('topic '):
                    parts = command.split()[1:]  # Remove 'topic'
                    if parts:
                        self.search_by_topic(parts)
                    else:
                        print("❌ Usage: topic <word1> <word2> ...")
                
                elif command.startswith('title '):
                    query = command[6:].strip()  # Remove 'title '
                    if query:
                        self.search_by_title(query)
                    else:
                        print("❌ Usage: title <search query>")
                
                elif command.startswith('details '):
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            conv_id = int(parts[1])
                            self.show_conversation_details(conv_id)
                        except ValueError:
                            print("❌ Please provide a valid conversation ID")
                    else:
                        print("❌ Usage: details <conversation_id>")
                
                elif command.startswith('compare '):
                    parts = command.split()
                    if len(parts) >= 3:
                        try:
                            conv_id1 = int(parts[1])
                            conv_id2 = int(parts[2])
                            self.compare_conversations(conv_id1, conv_id2)
                        except ValueError:
                            print("❌ Please provide valid conversation IDs")
                    else:
                        print("❌ Usage: compare <conv_id1> <conv_id2>")
                
                elif command == 'trending':
                    self.find_trending_words()
                
                elif command == 'help':
                    print("\n🆘 Available Commands:")
                    print("  list                     - Show all available analyses")
                    print("  overview [N]             - Show global word cloud overview")
                    print("  search <word> [min]      - Find conversations containing word")
                    print("  topic <word1> <word2>    - Search by topic (multiple words)")
                    print("  title <query>            - Search conversations by title")
                    print("  details <conv_id>        - Show word cloud for specific conversation")
                    print("  compare <id1> <id2>      - Compare word clouds between conversations")
                    print("  trending                 - Find words trending across conversations")
                    print("  help                     - Show this help")
                    print("  quit                     - Exit browser")
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Word Cloud Browser - Explore word frequency patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive browsing
  python word_cloud_browser.py browse
  
  # Show global overview
  python word_cloud_browser.py overview
  
  # Search for specific word
  python word_cloud_browser.py search --word consciousness --min-count 5
  
  # Search by topic
  python word_cloud_browser.py topic --words consciousness quantum reality
  
  # Show trending words
  python word_cloud_browser.py trending --min-conversations 5
        """
    )
    
    parser.add_argument('--results-dir', default='test_runs',
                       help='Directory containing word cloud results')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Browse command (interactive)
    browse_parser = subparsers.add_parser('browse', help='Interactive browsing')
    
    # Overview command
    overview_parser = subparsers.add_parser('overview', help='Show global overview')
    overview_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for word')
    search_parser.add_argument('--word', required=True, help='Word to search for')
    search_parser.add_argument('--min-count', type=int, default=1, help='Minimum occurrences')
    search_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Topic search command
    topic_parser = subparsers.add_parser('topic', help='Search by topic')
    topic_parser.add_argument('--words', nargs='+', required=True, help='Topic words')
    topic_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Title search command
    title_parser = subparsers.add_parser('title', help='Search by conversation title')
    title_parser.add_argument('--query', required=True, help='Title search query')
    title_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Details command
    details_parser = subparsers.add_parser('details', help='Show conversation details')
    details_parser.add_argument('--conversation-id', type=int, required=True, help='Conversation ID')
    details_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Trending command
    trending_parser = subparsers.add_parser('trending', help='Show trending words')
    trending_parser.add_argument('--min-conversations', type=int, default=3, help='Minimum conversations')
    trending_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    args = parser.parse_args()
    
    browser = WordCloudBrowser(args.results_dir)
    
    if args.command == 'browse':
        browser.interactive_browse()
    elif args.command == 'overview':
        browser.show_global_overview(args.index - 1)
    elif args.command == 'search':
        browser.search_by_word(args.word, args.index - 1, args.min_count)
    elif args.command == 'topic':
        browser.search_by_topic(args.words, args.index - 1)
    elif args.command == 'title':
        browser.search_by_title(args.query, args.index - 1)
    elif args.command == 'details':
        browser.show_conversation_details(args.conversation_id, args.index - 1)
    elif args.command == 'trending':
        browser.find_trending_words(args.index - 1, args.min_conversations)
    else:
        # Default to showing overview
        browser.show_global_overview(0)

if __name__ == "__main__":
    main()