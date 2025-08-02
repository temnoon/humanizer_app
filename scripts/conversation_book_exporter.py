#!/usr/bin/env python3
"""
Conversation-to-Book Exporter
Export specific conversations as books with LaTeX support
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from pathlib import Path
from datetime import datetime
import argparse
import sys
import os

class ConversationBookExporter:
    def __init__(self):
        self.database_url = "postgresql://postgres@localhost/humanizer_rails_development"
        
    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def export_conversation(self, conversation_id: str, output_dir: str = None):
        """Export a specific conversation as a book"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get conversation details
            cursor.execute("""
                SELECT id, title, created_at, message_count, word_count
                FROM conversations 
                WHERE id = %s
            """, (conversation_id,))
            
            conversation = cursor.fetchone()
            if not conversation:
                print(f"❌ Conversation {conversation_id} not found")
                return None
                
            print(f"📚 Processing: {conversation['title']}")
            print(f"   Messages: {conversation['message_count']}")
            print(f"   Words: {conversation['word_count']:,}")
            
            # Get all messages for this conversation
            cursor.execute("""
                SELECT role, content, message_index, original_timestamp
                FROM messages 
                WHERE conversation_id = %s
                ORDER BY message_index
            """, (conversation_id,))
            
            messages = cursor.fetchall()
            
            # Create book content
            book_content = self.create_book_content(conversation, messages)
            
            # Set output directory
            if not output_dir:
                output_dir = "/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/advanced_books"
            
            # Create safe filename
            safe_title = self.sanitize_filename(conversation['title'])
            book_filename = f"{safe_title.lower().replace(' ', '_')}.md"
            book_path = Path(output_dir) / book_filename
            
            # Write book file
            book_path.parent.mkdir(parents=True, exist_ok=True)
            book_path.write_text(book_content, encoding='utf-8')
            
            print(f"✅ Book created: {book_path}")
            return str(book_path)
    
    def create_book_content(self, conversation, messages):
        """Create book content from conversation and messages"""
        
        title = conversation['title']
        created_date = conversation['created_at'].strftime('%B %d, %Y')
        
        # Book header
        content = f"""# {title}

*A conversation exploring {title.lower()} from {created_date}*

Generated from {len(messages)} messages with {conversation['word_count']:,} words of rich mathematical discussion.

---

## Book Overview

This book captures a comprehensive conversation about {title.lower()}, containing substantial LaTeX mathematical expressions and deep technical insights. The discussion includes:

- Mathematical formulations and proofs
- Theoretical frameworks and applications  
- In-depth analysis of key concepts
- Rich LaTeX expressions for mathematical clarity

The content has been preserved in its original form to maintain the mathematical rigor and LaTeX formatting.

---

## Table of Contents

"""
        
        # Create chapters from message groups
        chapter_size = max(10, len(messages) // 6)  # Aim for ~6 chapters
        current_chapter = 1
        current_messages = []
        
        for i, message in enumerate(messages):
            current_messages.append(message)
            
            # Create chapter when we reach chapter_size or end
            if len(current_messages) >= chapter_size or i == len(messages) - 1:
                content += f"- [Chapter {current_chapter}: Messages {current_messages[0]['message_index']+1}-{current_messages[-1]['message_index']+1}](#chapter-{current_chapter})\n"
                current_chapter += 1
                current_messages = []
        
        content += "\n---\n\n"
        
        # Create chapter content
        current_chapter = 1
        current_messages = []
        
        for i, message in enumerate(messages):
            current_messages.append(message)
            
            # Create chapter when we reach chapter_size or end
            if len(current_messages) >= chapter_size or i == len(messages) - 1:
                content += f"## Chapter {current_chapter}: Messages {current_messages[0]['message_index']+1}-{current_messages[-1]['message_index']+1}\n\n"
                
                for msg in current_messages:
                    # Format timestamp
                    if msg['original_timestamp']:
                        timestamp = msg['original_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        timestamp = "Unknown time"
                    
                    content += f"### Message {msg['message_index']+1} ({msg['role'].title()})\n"
                    content += f"*{timestamp}*\n\n"
                    content += f"{msg['content']}\n\n"
                    content += "---\n\n"
                
                content += f"\n*End of Chapter {current_chapter}*\n\n"
                content += "---\n\n"
                
                current_chapter += 1
                current_messages = []
        
        # Book footer
        content += f"""

## Book Metadata

- **Original Conversation ID**: {conversation['id']}
- **Title**: {conversation['title']}
- **Created**: {conversation['created_at'].strftime('%Y-%m-%d %H:%M:%S')}
- **Total Messages**: {len(messages)}
- **Word Count**: {conversation['word_count']:,}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*Generated by Humanizer Lighthouse - Conversation Book Exporter*  
*LaTeX expressions preserved in original format*
"""
        
        return content
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        import re
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', ' ', filename)
        filename = filename.strip('._')
        return filename[:100]  # Limit length

def main():
    parser = argparse.ArgumentParser(description='Export specific conversations as books')
    parser.add_argument('conversation_ids', nargs='+', help='Conversation IDs to export')
    parser.add_argument('--output-dir', help='Output directory for books')
    
    args = parser.parse_args()
    
    exporter = ConversationBookExporter()
    
    print("📚 Conversation Book Exporter")
    print("=============================")
    print()
    
    exported_books = []
    
    for conv_id in args.conversation_ids:
        try:
            book_path = exporter.export_conversation(conv_id, args.output_dir)
            if book_path:
                exported_books.append(book_path)
            print()
        except Exception as e:
            print(f"❌ Error exporting {conv_id}: {e}")
            print()
    
    if exported_books:
        print(f"🎉 Successfully exported {len(exported_books)} books:")
        for book_path in exported_books:
            print(f"  📖 {book_path}")
        print()
        print("📋 Next steps:")
        print("1. Use the joplin_markdown_exporter_simple.py to create Joplin exports")
        print("2. Import into Joplin with File → Import → Markdown")
        print("3. Enjoy LaTeX rendering with KaTeX!")
    else:
        print("❌ No books were successfully exported")

if __name__ == '__main__':
    main()