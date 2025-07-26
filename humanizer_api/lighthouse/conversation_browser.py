"""
Conversation Browser and Viewer
===============================

Simple interface for browsing and viewing imported conversations.
Provides CLI and API access to imported conversation data.

Author: Enhanced for conversation management
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import argparse
import logging

from conversation_importer import ConversationImporter, ImportedConversation

logger = logging.getLogger(__name__)

class ConversationBrowser:
    """
    Browser interface for managing and viewing imported conversations.
    """
    
    def __init__(self, storage_dir: str = "./data/imported_conversations"):
        self.importer = ConversationImporter(storage_dir)
    
    def list_conversations(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """
        List all imported conversations with optional detailed information.
        """
        conversations = self.importer.list_imported_conversations()
        
        if not detailed:
            # Return simplified list
            return [{
                'id': conv['id'],
                'title': conv['title'],
                'source': conv['source_format'],
                'messages': conv['total_messages'],
                'created': conv.get('original_created', ''),
                'imported': conv['import_timestamp']
            } for conv in conversations]
        
        return conversations
    
    def show_conversation(self, conversation_id: str, 
                         max_content_length: int = 200,
                         show_metadata: bool = False) -> Optional[Dict[str, Any]]:
        """
        Display a conversation with formatted output.
        """
        conversation = self.importer.load_conversation(conversation_id)
        if not conversation:
            return None
        
        result = {
            'id': conversation.id,
            'title': conversation.title,
            'source_format': conversation.source_format,
            'total_messages': len(conversation.messages),
            'created': conversation.original_created.isoformat() if conversation.original_created else None,
            'updated': conversation.original_updated.isoformat() if conversation.original_updated else None,
            'imported': conversation.import_timestamp.isoformat(),
            'messages': []
        }
        
        for i, message in enumerate(conversation.messages):
            content = message.content
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            msg_data = {
                'index': i + 1,
                'id': message.id,
                'role': message.role,
                'content': content,
                'timestamp': message.timestamp.isoformat() if message.timestamp else None
            }
            
            if show_metadata:
                msg_data['metadata'] = message.metadata
                msg_data['media_files'] = message.media_files
            
            result['messages'].append(msg_data)
        
        return result
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversations using the archive system.
        """
        return self.importer.search_conversations(query, limit)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about imported conversations.
        """
        conversations = self.importer.list_imported_conversations()
        
        if not conversations:
            return {
                'total_conversations': 0,
                'total_messages': 0,
                'source_formats': {},
                'date_range': None
            }
        
        total_messages = sum(conv['total_messages'] for conv in conversations)
        
        # Count by source format
        source_formats = {}
        for conv in conversations:
            fmt = conv['source_format']
            source_formats[fmt] = source_formats.get(fmt, 0) + 1
        
        # Find date range
        import_dates = [conv['import_timestamp'] for conv in conversations if conv['import_timestamp']]
        date_range = None
        if import_dates:
            date_range = {
                'earliest': min(import_dates),
                'latest': max(import_dates)
            }
        
        return {
            'total_conversations': len(conversations),
            'total_messages': total_messages,
            'source_formats': source_formats,
            'date_range': date_range,
            'average_messages_per_conversation': total_messages / len(conversations) if conversations else 0
        }
    
    def export_conversation_to_markdown(self, conversation_id: str, 
                                      output_file: Optional[str] = None) -> str:
        """
        Export a conversation to markdown format.
        """
        conversation = self.importer.load_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Generate markdown
        lines = []
        lines.append(f"# {conversation.title}")
        lines.append("")
        lines.append(f"**Source:** {conversation.source_format}")
        lines.append(f"**Created:** {conversation.original_created}")
        lines.append(f"**Messages:** {len(conversation.messages)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, message in enumerate(conversation.messages):
            # Format role
            role_display = {
                'user': '👤 **User**',
                'assistant': '🤖 **Assistant**',
                'system': '⚙️ **System**',
                'tool': '🔧 **Tool**'
            }.get(message.role, f"**{message.role.title()}**")
            
            lines.append(f"## Message {i+1}: {role_display}")
            
            if message.timestamp:
                lines.append(f"*{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*")
                lines.append("")
            
            # Add content with proper markdown formatting
            content = message.content.strip()
            if content:
                lines.append(content)
            else:
                lines.append("*[Empty message]*")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        markdown_content = "\n".join(lines)
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Exported conversation to {output_file}")
        
        return markdown_content
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete an imported conversation.
        """
        try:
            conv_dir = self.importer.storage_dir / conversation_id
            if not conv_dir.exists():
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            # Remove directory and all contents
            import shutil
            shutil.rmtree(conv_dir)
            logger.info(f"Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

def print_conversation_list(conversations: List[Dict[str, Any]]):
    """
    Pretty print a list of conversations.
    """
    if not conversations:
        print("No conversations found.")
        return
    
    print(f"{'ID':<8} {'Title':<30} {'Source':<10} {'Messages':<8} {'Created':<12}")
    print("-" * 78)
    
    for conv in conversations:
        conv_id = conv['id'][:8] + "..."
        title = conv['title'][:28] + "..." if len(conv['title']) > 30 else conv['title']
        source = conv['source']
        messages = str(conv['messages'])
        
        # Format date
        created = ""
        if conv.get('created'):
            try:
                dt = datetime.fromisoformat(conv['created'].replace('Z', '+00:00'))
                created = dt.strftime('%Y-%m-%d')
            except:
                created = "Unknown"
        
        print(f"{conv_id:<8} {title:<30} {source:<10} {messages:<8} {created:<12}")

def print_conversation_messages(conversation_data: Dict[str, Any]):
    """
    Pretty print conversation messages.
    """
    print(f"Title: {conversation_data['title']}")
    print(f"Source: {conversation_data['source_format']}")
    print(f"Messages: {conversation_data['total_messages']}")
    print(f"Created: {conversation_data.get('created', 'Unknown')}")
    print("=" * 80)
    print()
    
    for msg in conversation_data['messages']:
        role_emoji = {
            'user': '👤',
            'assistant': '🤖',
            'system': '⚙️',
            'tool': '🔧'
        }.get(msg['role'], '❓')
        
        print(f"{role_emoji} {msg['role'].upper()} (Message {msg['index']}):")
        print(f"{msg['content']}")
        print("-" * 60)
        print()

# CLI Interface
def main():
    parser = argparse.ArgumentParser(description="Browse imported conversations")
    parser.add_argument('command', choices=['list', 'show', 'search', 'stats', 'export', 'import', 'delete'],
                       help='Command to execute')
    parser.add_argument('--id', help='Conversation ID (for show, export, delete)')
    parser.add_argument('--query', help='Search query (for search)')
    parser.add_argument('--path', help='Path to conversation directory (for import)')
    parser.add_argument('--output', help='Output file path (for export)')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--limit', type=int, default=10, help='Limit results (for search)')
    
    args = parser.parse_args()
    
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    browser = ConversationBrowser()
    
    try:
        if args.command == 'list':
            conversations = browser.list_conversations(detailed=args.detailed)
            if args.detailed:
                print(json.dumps(conversations, indent=2))
            else:
                print_conversation_list(conversations)
        
        elif args.command == 'show':
            if not args.id:
                print("Error: --id required for show command")
                return 1
            
            conversation = browser.show_conversation(args.id, show_metadata=args.detailed)
            if conversation:
                if args.detailed:
                    print(json.dumps(conversation, indent=2))
                else:
                    print_conversation_messages(conversation)
            else:
                print(f"Conversation {args.id} not found")
                return 1
        
        elif args.command == 'search':
            if not args.query:
                print("Error: --query required for search command")
                return 1
            
            results = browser.search_conversations(args.query, args.limit)
            if results:
                print(f"Found {len(results)} conversations matching '{args.query}':")
                for result in results:
                    print(f"- {result['title']} ({len(result['matches'])} matches)")
            else:
                print(f"No conversations found matching '{args.query}'")
        
        elif args.command == 'stats':
            stats = browser.get_conversation_stats()
            print("Conversation Statistics:")
            print(f"  Total conversations: {stats['total_conversations']}")
            print(f"  Total messages: {stats['total_messages']}")
            print(f"  Average messages per conversation: {stats['average_messages_per_conversation']:.1f}")
            print(f"  Source formats: {dict(stats['source_formats'])}")
            if stats['date_range']:
                print(f"  Import date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        elif args.command == 'export':
            if not args.id:
                print("Error: --id required for export command")
                return 1
            
            try:
                markdown = browser.export_conversation_to_markdown(args.id, args.output)
                if args.output:
                    print(f"Exported to {args.output}")
                else:
                    print(markdown)
            except ValueError as e:
                print(f"Error: {e}")
                return 1
        
        elif args.command == 'import':
            if not args.path:
                print("Error: --path required for import command")
                return 1
            
            try:
                conversation = browser.importer.import_chatgpt_conversation(args.path)
                print(f"Successfully imported: {conversation.title}")
                print(f"ID: {conversation.id}")
                print(f"Messages: {len(conversation.messages)}")
            except Exception as e:
                print(f"Import failed: {e}")
                return 1
        
        elif args.command == 'delete':
            if not args.id:
                print("Error: --id required for delete command")
                return 1
            
            if browser.delete_conversation(args.id):
                print(f"Deleted conversation {args.id}")
            else:
                print(f"Failed to delete conversation {args.id}")
                return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())