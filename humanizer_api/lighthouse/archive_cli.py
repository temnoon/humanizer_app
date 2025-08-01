#!/usr/bin/env python3
"""
Archive CLI - Direct PostgreSQL Archive Access for Content Processing
Integrates with Humanizer CLI for content transformation pipeline
"""

import sys
import json
import argparse
from typing import Dict, Any, List, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from humanizer_cli import HumanizerCLI
    HUMANIZER_CLI_AVAILABLE = True  
except ImportError:
    HUMANIZER_CLI_AVAILABLE = False
    
import requests

class ArchiveCLI:
    """Direct PostgreSQL archive access CLI"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive", api_base: str = "http://127.0.0.1:8100"):
        self.database_url = database_url
        self.api_base = api_base
        
        if HUMANIZER_CLI_AVAILABLE:
            self.humanizer_cli = HumanizerCLI()
        else:
            self.humanizer_cli = None
        
        if not POSTGRES_AVAILABLE:
            print("❌ PostgreSQL support not available. Install with: pip3 install psycopg2-binary")
            sys.exit(1)
    
    def get_available_attributes(self) -> Dict[str, Any]:
        """Get available personas, namespaces, and styles from API"""
        try:
            response = requests.get(f"{self.api_base}/configurations", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching attributes: {e}")
            return {}
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def list_conversations(self, 
                          page: int = 1, 
                          limit: int = 20, 
                          search: str = "") -> List[Dict[str, Any]]:
        """List conversations from PostgreSQL"""
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build search clause
            search_clause = ""
            params = []
            if search.strip():
                search_clause = "AND (title ILIKE %s OR body_text ILIKE %s)"
                search_param = f"%{search.strip()}%"
                params = [search_param, search_param]
            
            # Get conversations with message counts
            offset = (page - 1) * limit
            
            query = f"""
                SELECT 
                    c.id,
                    c.title,
                    c.timestamp,
                    c.author,
                    COUNT(m.id) as message_count,
                    c.word_count
                FROM archived_content c
                LEFT JOIN archived_content m ON c.id = m.parent_id
                WHERE c.content_type = 'conversation' {search_clause}
                GROUP BY c.id, c.title, c.timestamp, c.author, c.word_count
                ORDER BY c.timestamp DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, params + [limit, offset])
            conversations = []
            
            for row in cursor.fetchall():
                conversations.append({
                    'id': row['id'],
                    'title': row['title'] or 'Untitled Conversation',
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else '',
                    'author': row['author'] or 'Unknown',
                    'message_count': row['message_count'],
                    'word_count': row['word_count'] or 0
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id: int) -> Dict[str, Any]:
        """Get conversation with all messages"""
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get conversation info
            cursor.execute("""
                SELECT id, title, timestamp, author, source_metadata
                FROM archived_content 
                WHERE id = %s AND content_type = 'conversation'
            """, (conversation_id,))
            
            conversation = cursor.fetchone()
            if not conversation:
                conn.close()
                return {}
            
            # Get messages
            cursor.execute("""
                SELECT id, body_text, author, timestamp, source_metadata
                FROM archived_content
                WHERE parent_id = %s AND content_type = 'message'
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            messages = []
            for msg in cursor.fetchall():
                # Parse role from metadata
                metadata = msg['source_metadata'] or {}
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                messages.append({
                    'id': msg['id'],
                    'content': msg['body_text'] or '',
                    'author': msg['author'] or 'Unknown',
                    'role': metadata.get('role', msg['author']),
                    'timestamp': msg['timestamp'].isoformat() if msg['timestamp'] else None
                })
            
            conn.close()
            
            return {
                'conversation': {
                    'id': conversation['id'],
                    'title': conversation['title'] or 'Untitled',
                    'author': conversation['author'] or 'Unknown',
                    'timestamp': conversation['timestamp'].isoformat() if conversation['timestamp'] else None
                },
                'messages': messages
            }
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return {}
    
    def search_content(self, 
                      query: str, 
                      limit: int = 50) -> List[Dict[str, Any]]:
        """Search archived content using PostgreSQL full-text search"""
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Full-text search
            cursor.execute("""
                SELECT 
                    id, content_type, title, body_text, author, timestamp
                FROM archived_content
                WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(body_text, '')) 
                      @@ plainto_tsquery('english', %s)
                ORDER BY timestamp DESC
                LIMIT %s
            """, (query, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'content_type': row['content_type'],
                    'title': row['title'] or 'Untitled',
                    'content': row['body_text'] or '',
                    'author': row['author'] or 'Unknown',
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def transform_text_direct(self,
                            text: str,
                            persona: str = "philosophical_narrator", 
                            namespace: str = "existential_philosophy",
                            style: str = "contemplative_prose") -> Dict[str, Any]:
        """Transform text directly using the humanizer CLI"""
        
        print(f"🔄 Transforming text directly")
        print(f"   Length: {len(text)} characters")
        print(f"   Persona: {persona}")
        print(f"   Namespace: {namespace}")
        print(f"   Style: {style}")
        
        try:
            # Use the humanizer CLI to transform the text
            result = self.humanizer_cli.transform_text(text, persona, namespace, style)
            
            if result:
                return {
                    'input_text': text,
                    'transformation': result,
                    'parameters': {
                        'persona': persona,
                        'namespace': namespace,
                        'style': style
                    }
                }
            else:
                print("❌ Transformation failed")
                return {}
                
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return {}

    def transform_conversation(self, 
                             conversation_id: int,
                             persona: str = "philosophical_narrator",
                             namespace: str = "existential_philosophy",
                             style: str = "contemplative_prose") -> Dict[str, Any]:
        """Get conversation and transform it"""
        
        print(f"🔄 Processing conversation {conversation_id}")
        
        # Get the conversation
        conv_data = self.get_conversation_messages(conversation_id)
        if not conv_data:
            return {}
        
        messages = conv_data.get('messages', [])
        if not messages:
            print("❌ No messages found")
            return {}
        
        # Combine messages into narrative
        combined_text = ""
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            if content.strip():
                combined_text += f"[{role}]: {content}\\n\\n"
        
        if not combined_text.strip():
            print("❌ No content to transform")
            return {}
        
        print(f"📝 Combined {len(messages)} messages ({len(combined_text)} chars)")
        
        # Transform using Humanizer CLI
        transform_result = self.humanizer_cli.transform_text(
            combined_text, persona, namespace, style
        )
        
        if transform_result:
            return {
                'conversation': conv_data['conversation'],
                'original_messages': messages,
                'combined_content': combined_text,
                'transformation': transform_result
            }
        
        return {}
    
    def export_format(self, content: str, format_type: str, 
                     output_file: str = None, metadata: Dict[str, Any] = None) -> str:
        """Export content to various formats using format_generator"""
        import subprocess
        import tempfile
        from pathlib import Path
        
        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
            # Add metadata as frontmatter if provided
            if metadata:
                tmp_file.write('---\n')
                for key, value in metadata.items():
                    tmp_file.write(f'{key}: {value}\n')
                tmp_file.write('---\n\n')
            
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Build format generator command
            cmd = [
                'python', str(Path(__file__).parent.parent.parent / 'scripts' / 'format_generator.py'),
                'convert',
                '--file', tmp_path,
                '--format', format_type
            ]
            
            if output_file:
                cmd.extend(['--output', output_file])
            
            # Execute format generation
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return "✅ Format export successful"
            else:
                return f"❌ Format export failed: {result.stderr}"
                
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    def automated_process(self, input_file: str, persona: str = None, 
                         namespace: str = None, style: str = None,
                         export_formats: List[str] = None) -> Dict[str, Any]:
        """Run full automated processing pipeline"""
        import subprocess
        from pathlib import Path
        
        results = {'steps': [], 'outputs': {}}
        
        # Step 1: Content transformation
        if self.humanizer_cli and HUMANIZER_CLI_AVAILABLE:
            try:
                with open(input_file, 'r') as f:
                    content = f.read()
                
                transform_result = self.transform_text_direct(content, persona, namespace, style)
                
                if transform_result:
                    results['steps'].append('✅ Content transformation successful')
                    results['outputs']['transformation'] = transform_result
                else:
                    results['steps'].append('❌ Content transformation failed')
                    return results
                    
            except Exception as e:
                results['steps'].append(f'❌ Error reading input file: {e}')
                return results
        
        # Step 2: Format generation
        if export_formats:
            try:
                cmd = [
                    'python', str(Path(__file__).parent.parent.parent / 'scripts' / 'format_generator.py'),
                    'convert',
                    '--file', input_file,
                    '--format', ','.join(export_formats)
                ]
                
                format_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if format_result.returncode == 0:
                    results['steps'].append(f'✅ Format generation successful: {", ".join(export_formats)}')
                    results['outputs']['formats'] = export_formats
                else:
                    results['steps'].append(f'❌ Format generation failed: {format_result.stderr}')
                    
            except Exception as e:
                results['steps'].append(f'❌ Error in format generation: {e}')
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Archive CLI - PostgreSQL Archive Access & Processing")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List conversations or attributes
    list_parser = subparsers.add_parser('list', help='List conversations or attributes')
    list_parser.add_argument('attribute_type', nargs='?', help='Attribute type: personas/persona, namespaces/namespace, styles/style, or leave empty for conversations')
    list_parser.add_argument('--page', type=int, default=1, help='Page number (for conversations)')
    list_parser.add_argument('--limit', type=int, default=20, help='Results per page (for conversations)')
    list_parser.add_argument('--search', help='Search in titles/content (for conversations)')
    
    # Get conversation
    get_parser = subparsers.add_parser('get', help='Get conversation with messages')
    get_parser.add_argument('conversation_id', type=int, help='Conversation ID')
    get_parser.add_argument('--output', '-o', help='Save to file')
    
    # Search content
    search_parser = subparsers.add_parser('search', help='Search archive content')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=50, help='Max results')
    search_parser.add_argument('--output', '-o', help='Save to file')
    
    # Transform conversation or text
    transform_parser = subparsers.add_parser('transform', help='Transform conversation content or direct text')
    
    # Input options - either conversation_id OR text (mutually exclusive)
    input_group = transform_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('conversation_id', nargs='?', type=int, help='Conversation ID from database')
    input_group.add_argument('--text', '-t', help='Direct text input to transform')
    input_group.add_argument('--file', '-f', help='Input file to transform')
    
    transform_parser.add_argument('--persona', '-p', default='philosophical_narrator')
    transform_parser.add_argument('--namespace', '-n', default='existential_philosophy')
    transform_parser.add_argument('--style', '-s', default='contemplative_prose')
    transform_parser.add_argument('--output', '-o', help='Save to file')
    
    # Export format command
    export_parser = subparsers.add_parser('export', help='Export content to various formats')
    export_parser.add_argument('content', help='Content to export (text or file path)')
    export_parser.add_argument('--format', required=True, help='Export format: html, pdf, docx')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--title', help='Document title')
    export_parser.add_argument('--author', help='Document author')
    
    # Automated pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run automated processing pipeline')
    pipeline_parser.add_argument('--file', '-f', required=True, help='Input file to process')
    pipeline_parser.add_argument('--persona', '-p', help='Persona for transformation')
    pipeline_parser.add_argument('--namespace', '-n', help='Namespace for transformation')
    pipeline_parser.add_argument('--style', '-s', help='Style for transformation')
    pipeline_parser.add_argument('--formats', help='Export formats (comma-separated): html,pdf,docx')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    archive_cli = ArchiveCLI()
    
    if args.command == 'list':
        # Check if we're listing attributes or conversations
        if args.attribute_type:
            # List attributes - normalize singular/plural forms
            attr_type = args.attribute_type.lower()
            
            # Handle both singular and plural forms
            if attr_type in ['persona', 'personas']:
                attr_key = 'personas'
                display_name = 'PERSONAS'
            elif attr_type in ['namespace', 'namespaces']:
                attr_key = 'namespaces'
                display_name = 'NAMESPACES'
            elif attr_type in ['style', 'styles']:
                attr_key = 'styles'
                display_name = 'STYLES'
            else:
                print(f"❌ Unknown attribute type: {attr_type}")
                print("Valid types: personas/persona, namespaces/namespace, styles/style")
                sys.exit(1)
            
            # Check if API is available
            if not HUMANIZER_CLI_AVAILABLE or not archive_cli.humanizer_cli:
                print("❌ Enhanced API not available. Start with: python api_enhanced.py")
                sys.exit(1)
            
            # Check if API is running
            try:
                response = requests.get(f"{archive_cli.api_base}/health", timeout=5)
                if response.status_code != 200:
                    print("❌ Enhanced API not running. Start with: python api_enhanced.py")
                    sys.exit(1)
            except:
                print("❌ Enhanced API not running. Start with: python api_enhanced.py")
                sys.exit(1)
            
            # Get attributes from API
            attributes = archive_cli.get_available_attributes()
            
            if not attributes or attr_key not in attributes:
                print(f"❌ Could not retrieve {display_name.lower()}")
                sys.exit(1)
            
            items = attributes[attr_key]
            
            print(f"\\n{'='*80}")
            print(f"AVAILABLE {display_name}:")
            print('='*80)
            
            for item in items:
                print(f"ID: {item['id']}")
                print(f"    Name: {item['name']}")
                print(f"    Description: {item['description']}")
                print()
            
            print(f"Total {display_name.lower()}: {len(items)}")
            
        else:
            # List conversations (default behavior)
            search_query = getattr(args, 'search', '') or ''
            conversations = archive_cli.list_conversations(args.page, args.limit, search_query)
            
            print(f"\\n{'='*80}")
            print("ARCHIVED CONVERSATIONS:")
            print('='*80)
            
            for conv in conversations:
                print(f"ID: {conv['id']} | {conv['title'][:60]}...")
                print(f"    Messages: {conv['message_count']} | Words: {conv['word_count']} | Author: {conv['author']}")
                print(f"    Created: {conv['timestamp'][:19] if conv['timestamp'] else 'Unknown'}")
                print()
            
            print(f"Showing page {args.page} (limit {args.limit})")
        
    elif args.command == 'get':
        result = archive_cli.get_conversation_messages(args.conversation_id)
        
        if result:
            conv = result['conversation']
            messages = result['messages']
            
            print(f"\\n{'='*80}")
            print(f"CONVERSATION: {conv['title']}")
            print(f"Author: {conv['author']} | Created: {conv['timestamp'][:19] if conv['timestamp'] else 'Unknown'}")
            print('='*80)
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')[:19] if msg.get('timestamp') else 'Unknown'
                
                print(f"{i}. [{role}] ({timestamp})")
                print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
                print()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Saved to {args.output}")
        
    elif args.command == 'search':
        results = archive_cli.search_content(args.query, args.limit)
        
        print(f"\\n{'='*80}")
        print(f"SEARCH RESULTS: '{args.query}'")
        print('='*80)
        
        for i, item in enumerate(results, 1):
            title = item['title']
            content = item['content']
            content_type = item['content_type']
            
            print(f"{i}. {title} ({content_type})")
            print(f"   {content[:150]}{'...' if len(content) > 150 else ''}")
            print()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"💾 Saved to {args.output}")
    
    elif args.command == 'transform':
        # Check if Enhanced API is running
        if not archive_cli.humanizer_cli.check_api_health():
            print("❌ Enhanced API not running. Start with: python api_enhanced.py")
            sys.exit(1)
        
        # Determine input source
        if args.conversation_id:
            # Transform conversation from database
            result = archive_cli.transform_conversation(
                args.conversation_id, args.persona, args.namespace, args.style
            )
            
            if result:
                conversation = result['conversation']
                transformation = result['transformation']
                
                print(f"\\n{'='*80}")
                print(f"TRANSFORMED CONVERSATION: {conversation['title']}")
                print('='*80)
                
                if 'projection' in transformation:
                    print("TRANSFORMED CONTENT:")
                    print("-" * 40)
                    print(transformation['projection']['narrative'])
                    print("\\nREFLECTION:")
                    print("-" * 40)
                    print(transformation['projection']['reflection'])
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"💾 Saved to {args.output}")
        
        elif args.text:
            # Transform direct text input
            result = archive_cli.transform_text_direct(
                args.text, args.persona, args.namespace, args.style
            )
            
            if result:
                transformation = result['transformation']
                
                print(f"\\n{'='*80}")
                print("TRANSFORMED TEXT:")
                print('='*80)
                
                if 'projection' in transformation:
                    print("ORIGINAL:")
                    print("-" * 40)
                    print(result['input_text'])
                    print("\\nTRANSFORMED:")
                    print("-" * 40)
                    print(transformation['projection']['narrative'])
                    if 'reflection' in transformation['projection']:
                        print("\\nREFLECTION:")
                        print("-" * 40)
                        print(transformation['projection']['reflection'])
                
                if args.output:
                    if args.output.endswith('.json'):
                        with open(args.output, 'w') as f:
                            json.dump(result, f, indent=2)
                    else:
                        with open(args.output, 'w') as f:
                            f.write(transformation['projection']['narrative'])
                    print(f"💾 Saved to {args.output}")
        
        elif args.file:
            # Transform file input
            try:
                with open(args.file, 'r') as f:
                    file_text = f.read().strip()
                
                if not file_text:
                    print(f"❌ File is empty: {args.file}")
                    sys.exit(1)
                
                result = archive_cli.transform_text_direct(
                    file_text, args.persona, args.namespace, args.style
                )
                
                if result:
                    transformation = result['transformation']
                    
                    print(f"\\n{'='*80}")
                    print(f"TRANSFORMED FILE: {args.file}")
                    print('='*80)
                    
                    if 'projection' in transformation:
                        print("TRANSFORMED CONTENT:")
                        print("-" * 40)
                        print(transformation['projection']['narrative'])
                        if 'reflection' in transformation['projection']:
                            print("\\nREFLECTION:")
                            print("-" * 40)
                            print(transformation['projection']['reflection'])
                    
                    if args.output:
                        if args.output.endswith('.json'):
                            with open(args.output, 'w') as f:
                                json.dump(result, f, indent=2)
                        else:
                            with open(args.output, 'w') as f:
                                f.write(transformation['projection']['narrative'])
                        print(f"💾 Saved to {args.output}")
                        
            except FileNotFoundError:
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                sys.exit(1)
    
    elif args.command == 'export':
        # Export content to various formats
        from pathlib import Path
        
        content = args.content
        
        # Check if content is a file path
        if Path(content).exists():
            with open(content, 'r') as f:
                content = f.read()
        
        # Build metadata
        metadata = {}
        if args.title:
            metadata['title'] = args.title
        if args.author:
            metadata['author'] = args.author
        
        result = archive_cli.export_format(content, args.format, args.output, metadata)
        print(result)
    
    elif args.command == 'pipeline':
        # Run automated processing pipeline
        formats = args.formats.split(',') if args.formats else None
        
        result = archive_cli.automated_process(
            args.file,
            persona=args.persona,
            namespace=args.namespace, 
            style=args.style,
            export_formats=formats
        )
        
        print(f"\n{'='*80}")
        print("AUTOMATED PROCESSING PIPELINE RESULTS:")
        print('='*80)
        
        for step in result['steps']:
            print(step)
        
        if result['outputs']:
            print("\nOutputs:")
            for key, value in result['outputs'].items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()