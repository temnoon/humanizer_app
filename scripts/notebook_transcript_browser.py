#!/usr/bin/env python3
"""
Notebook Transcript Browser
Specialized tool for discovering and analyzing handwritten notebook transcripts
Created for the Journal Recognizer OCR conversations (gizmo_id: g-T7bW2qVzx)
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

class NotebookTranscriptBrowser:
    """Browser for handwritten notebook transcripts from Journal Recognizer OCR"""
    
    JOURNAL_OCR_GIZMO_ID = "g-T7bW2qVzx"
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://tem@localhost/humanizer_archive"
        self.database_url = database_url
        
        print("📔 Notebook Transcript Browser")
        print("==============================")
        print(f"Target: Journal Recognizer OCR (gizmo_id: {self.JOURNAL_OCR_GIZMO_ID})")
        
        # Test connection immediately
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def list_notebook_conversations(self) -> List[Dict]:
        """List all conversations containing notebook transcripts"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        parent.id,
                        COALESCE(parent.title, 'Untitled') as title,
                        parent.timestamp,
                        COUNT(child.id) as transcript_count
                    FROM archived_content parent
                    JOIN archived_content child ON parent.id = child.parent_id
                    WHERE child.source_metadata->>'gizmo_id' = %s
                        AND child.content_type = 'message'
                        AND child.body_text IS NOT NULL
                    GROUP BY parent.id, parent.title, parent.timestamp
                    ORDER BY transcript_count DESC, parent.timestamp DESC
                """, (self.JOURNAL_OCR_GIZMO_ID,))
                
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def get_conversation_transcripts(self, conversation_id: int) -> List[Dict]:
        """Get all notebook transcripts from a specific conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    body_text,
                    author,
                    timestamp,
                    source_metadata
                FROM archived_content
                WHERE parent_id = %s
                    AND source_metadata->>'gizmo_id' = %s
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                ORDER BY timestamp
            """, (conversation_id, self.JOURNAL_OCR_GIZMO_ID))
            
            return cursor.fetchall()
    
    def extract_handwritten_content(self, body_text: str) -> Dict[str, Any]:
        """Extract handwritten content from OCR transcript"""
        result = {
            'has_markdown_block': False,
            'markdown_content': '',
            'raw_content': body_text,
            'content_type': 'unknown',
            'word_count': 0,
            'key_phrases': [],
            'emotional_indicators': [],
            'philosophical_concepts': []
        }
        
        # Check for markdown code blocks
        markdown_pattern = r'```markdown\s*(.*?)\s*```'
        markdown_matches = re.findall(markdown_pattern, body_text, re.DOTALL | re.IGNORECASE)
        
        if markdown_matches:
            result['has_markdown_block'] = True
            result['markdown_content'] = markdown_matches[0].strip()
            result['content_type'] = 'handwritten_transcript'
            
            # Analyze the markdown content
            content = result['markdown_content']
            result['word_count'] = len(content.split())
            
            # Look for philosophical concepts
            philosophical_terms = [
                'consciousness', 'phenomenology', 'being', 'existence', 'reality', 
                'subjective', 'objective', 'experience', 'awareness', 'perception',
                'ontology', 'epistemology', 'metaphysics', 'qualia', 'intentionality'
            ]
            
            found_concepts = []
            for term in philosophical_terms:
                if re.search(r'\b' + re.escape(term) + r'\b', content, re.IGNORECASE):
                    found_concepts.append(term)
            result['philosophical_concepts'] = found_concepts
            
            # Look for emotional/personal indicators
            emotional_patterns = [
                r'\bi\s+feel\b', r'\bi\s+think\b', r'\bi\s+believe\b',
                r'\bmy\s+sense\b', r'\bpersonal\b', r'\bexperience\b',
                r'!\s*', r'\?\s*', r'\b(love|fear|joy|anxiety|wonder)\b'
            ]
            
            emotional_matches = []
            for pattern in emotional_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                emotional_matches.extend(matches)
            result['emotional_indicators'] = list(set(emotional_matches))
            
            # Extract key phrases (sentences or meaningful fragments)
            sentences = re.split(r'[.!?]+', content)
            meaningful_sentences = [
                s.strip() for s in sentences 
                if len(s.strip()) > 20 and len(s.strip()) < 200
            ]
            result['key_phrases'] = meaningful_sentences[:5]  # Top 5
        
        return result
    
    def analyze_conversation(self, conversation_id: int):
        """Analyze all transcripts in a conversation"""
        transcripts = self.get_conversation_transcripts(conversation_id)
        
        if not transcripts:
            print(f"❌ No transcripts found for conversation {conversation_id}")
            return
        
        # Get conversation title
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM archived_content WHERE id = %s", (conversation_id,))
            conv_result = cursor.fetchone()
            title = conv_result['title'] if conv_result else f"Conversation {conversation_id}"
        
        print(f"\n📖 Notebook Analysis: {title}")
        print("=" * 60)
        print(f"Conversation ID: {conversation_id}")
        print(f"Total transcripts: {len(transcripts)}")
        
        total_words = 0
        all_concepts = []
        all_key_phrases = []
        
        for i, transcript in enumerate(transcripts, 1):
            print(f"\n--- Transcript {i} ---")
            print(f"Timestamp: {transcript['timestamp']}")
            print(f"Author: {transcript['author']}")
            
            analysis = self.extract_handwritten_content(transcript['body_text'])
            
            if analysis['has_markdown_block']:
                print(f"📝 Type: {analysis['content_type']}")
                print(f"📊 Words: {analysis['word_count']}")
                total_words += analysis['word_count']
                
                if analysis['philosophical_concepts']:
                    print(f"🧠 Concepts: {', '.join(analysis['philosophical_concepts'][:5])}")
                    all_concepts.extend(analysis['philosophical_concepts'])
                
                if analysis['key_phrases']:
                    print("💭 Key insights:")
                    for phrase in analysis['key_phrases'][:3]:
                        print(f"   • {phrase}")
                    all_key_phrases.extend(analysis['key_phrases'])
                
                # Show a preview of the content
                content_preview = analysis['markdown_content'][:200]
                if len(analysis['markdown_content']) > 200:
                    content_preview += "..."
                print(f"📄 Preview: {content_preview}")
            else:
                print("ℹ️  Non-transcript content (possibly system message)")
        
        # Summary
        print(f"\n📈 Conversation Summary:")
        print(f"Total handwritten words: {total_words:,}")
        
        # Top concepts
        from collections import Counter
        concept_counts = Counter(all_concepts)
        if concept_counts:
            print("🏆 Top concepts:")
            for concept, count in concept_counts.most_common(5):
                print(f"   • {concept}: {count}x")
        
        # Sample key insights
        if all_key_phrases:
            print("💡 Notable insights:")
            for phrase in all_key_phrases[:3]:
                print(f"   • {phrase}")
    
    def export_transcripts(self, conversation_id: int, output_file: str = None):
        """Export all transcripts from a conversation to a file"""
        transcripts = self.get_conversation_transcripts(conversation_id)
        
        if not transcripts:
            print(f"❌ No transcripts found for conversation {conversation_id}")
            return
        
        # Get conversation title for filename
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM archived_content WHERE id = %s", (conversation_id,))
            conv_result = cursor.fetchone()
            title = conv_result['title'] if conv_result else f"Conversation {conversation_id}"
        
        if output_file is None:
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"notebook_transcripts_{safe_title}_{timestamp}.md"
        
        output_path = Path("exports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Notebook Transcripts: {title}\n\n")
            f.write(f"**Conversation ID:** {conversation_id}\n")
            f.write(f"**Exported:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Transcripts:** {len(transcripts)}\n\n")
            f.write("---\n\n")
            
            for i, transcript in enumerate(transcripts, 1):
                f.write(f"## Transcript {i}\n\n")
                f.write(f"**Timestamp:** {transcript['timestamp']}\n")
                f.write(f"**Author:** {transcript['author']}\n\n")
                
                analysis = self.extract_handwritten_content(transcript['body_text'])
                
                if analysis['has_markdown_block']:
                    f.write("### Handwritten Content\n\n")
                    f.write(analysis['markdown_content'])
                    f.write("\n\n")
                    
                    if analysis['philosophical_concepts']:
                        f.write(f"**Concepts:** {', '.join(analysis['philosophical_concepts'])}\n\n")
                else:
                    f.write("### System/Non-transcript Content\n\n")
                    f.write(f"```\n{transcript['body_text'][:500]}\n```\n\n")
                
                f.write("---\n\n")
        
        print(f"✅ Exported to: {output_path}")
        return str(output_path)
    
    def interactive_browse(self):
        """Interactive browsing mode"""
        try:
            conversations = self.list_notebook_conversations()
            
            if not conversations:
                print("❌ No notebook transcript conversations found!")
                return
            
            print(f"\n📋 Found {len(conversations)} conversations with notebook transcripts")
            print("\nCommands: list, analyze <id>, export <id>, search <term>, quit")
        except Exception as e:
            print(f"❌ Error loading conversations: {e}")
            return
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() in ['quit', 'q', 'exit']:
                    break
                
                elif command == 'list':
                    print(f"\n📔 Notebook Transcript Conversations:")
                    print("-" * 60)
                    for i, conv in enumerate(conversations[:20], 1):
                        timestamp = conv['timestamp'].strftime("%Y-%m-%d") if conv['timestamp'] else "Unknown"
                        print(f" {i:2d}. [{conv['id']}] {conv['title']}")
                        print(f"     📊 {conv['transcript_count']} transcripts | {timestamp}")
                        print()
                    
                    if len(conversations) > 20:
                        print(f"    ... and {len(conversations) - 20} more")
                
                elif command.startswith('analyze '):
                    try:
                        conv_id = int(command.split()[1])
                        self.analyze_conversation(conv_id)
                    except (ValueError, IndexError):
                        print("❌ Usage: analyze <conversation_id>")
                
                elif command.startswith('export '):
                    try:
                        conv_id = int(command.split()[1])
                        self.export_transcripts(conv_id)
                    except (ValueError, IndexError):
                        print("❌ Usage: export <conversation_id>")
                
                elif command.startswith('search '):
                    search_term = command[7:].strip()
                    if search_term:
                        matching_convs = [
                            conv for conv in conversations
                            if search_term.lower() in conv['title'].lower()
                        ]
                        print(f"\n🔍 Found {len(matching_convs)} conversations matching '{search_term}':")
                        for conv in matching_convs[:10]:
                            print(f"  [{conv['id']}] {conv['title']} ({conv['transcript_count']} transcripts)")
                    else:
                        print("❌ Usage: search <term>")
                
                elif command == 'help':
                    print("\n🆘 Available Commands:")
                    print("  list                  - Show all notebook transcript conversations")
                    print("  analyze <conv_id>     - Analyze transcripts in a conversation")
                    print("  export <conv_id>      - Export transcripts to markdown file")
                    print("  search <term>         - Search conversation titles")
                    print("  quit                  - Exit browser")
                
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
        description="Browse and analyze handwritten notebook transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python notebook_transcript_browser.py browse           # Interactive mode
  python notebook_transcript_browser.py list            # List all conversations
  python notebook_transcript_browser.py analyze 225015  # Analyze specific conversation
  python notebook_transcript_browser.py export 225015   # Export to markdown
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Browse command (interactive)
    browse_parser = subparsers.add_parser('browse', help='Interactive browsing')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all notebook conversations')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze conversation transcripts')
    analyze_parser.add_argument('conversation_id', type=int, help='Conversation ID to analyze')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export transcripts to file')
    export_parser.add_argument('conversation_id', type=int, help='Conversation ID to export')
    export_parser.add_argument('--output', help='Output filename (optional)')
    
    args = parser.parse_args()
    
    try:
        browser = NotebookTranscriptBrowser()
        
        if args.command == 'browse':
            browser.interactive_browse()
        elif args.command == 'list':
            conversations = browser.list_notebook_conversations()
            print(f"\n📔 Found {len(conversations)} notebook transcript conversations:")
            for conv in conversations:
                try:
                    timestamp = conv['timestamp'].strftime("%Y-%m-%d") if conv.get('timestamp') else "Unknown"
                    print(f"  [{conv['id']}] {conv['title']}")
                    print(f"      📊 {conv['transcript_count']} transcripts | {timestamp}")
                except Exception as e:
                    print(f"  Error displaying conversation: {e}")
                    print(f"  Raw data: {dict(conv)}")
        elif args.command == 'analyze':
            browser.analyze_conversation(args.conversation_id)
        elif args.command == 'export':
            browser.export_transcripts(args.conversation_id, args.output)
        else:
            # Default to interactive mode
            browser.interactive_browse()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()