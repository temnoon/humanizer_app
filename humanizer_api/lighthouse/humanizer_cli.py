#!/usr/bin/env python3
"""
Humanizer CLI - Minimal command-line interface for the Enhanced API
Pure CLI with file output support - no GUI, all business logic in API
"""

import requests
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile

API_BASE = "http://127.0.0.1:8100"
ARCHIVE_API_BASE = "http://127.0.0.1:7200"

class HumanizerCLI:
    """Minimal CLI client for Humanizer Enhanced API with Archive Integration"""
    
    def __init__(self, api_base: str = API_BASE, archive_api_base: str = ARCHIVE_API_BASE):
        self.api_base = api_base
        self.archive_api_base = archive_api_base
        self.session = requests.Session()
    
    def check_api_health(self) -> bool:
        """Check if API is responding"""
        try:
            response = self.session.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def transform_text(self, 
                      narrative: str,
                      persona: str = "philosophical_narrator",
                      namespace: str = "existential_philosophy", 
                      style: str = "contemplative_prose",
                      output_file: Optional[str] = None) -> Dict[str, Any]:
        """Transform narrative text"""
        
        payload = {
            "narrative": narrative,
            "target_persona": persona,
            "target_namespace": namespace,
            "target_style": style
        }
        
        print(f"🔄 Transforming text (persona: {persona}, namespace: {namespace}, style: {style})")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/transform", json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Transform completed in {duration:.1f}s")
            
            # Save to file if requested
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Result saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def extract_attributes(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Extract narrative attributes from text"""
        
        payload = {"text": text, "mode": "comprehensive"}
        
        print("🧬 Extracting narrative attributes...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/api/extract-attributes", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Attributes extracted in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Attributes saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def analyze_meaning(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text using Lamish meaning analysis"""
        
        payload = {"text": text, "analysis_depth": "comprehensive"}
        
        print("🧠 Analyzing meaning with Lamish engine...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/lamish/analyze", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Analysis completed in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Analysis saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def quantum_analysis(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run quantum narrative theory analysis"""
        
        payload = {"text": text, "analysis_depth": "comprehensive"}
        
        print("⚛️ Running quantum narrative analysis...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/api/narrative-theory/analyze", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Quantum analysis completed in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Analysis saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get LLM provider status"""
        try:
            response = self.session.get(f"{self.api_base}/api/llm/status", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def check_archive_health(self) -> bool:
        """Check if Archive API is responding"""
        try:
            response = self.session.get(f"{self.archive_api_base}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_conversations(self, 
                          page: int = 1, 
                          limit: int = 20, 
                          search: str = "", 
                          output_file: Optional[str] = None) -> Dict[str, Any]:
        """List archived conversations"""
        
        params = {
            "page": page,
            "limit": limit,
            "search": search,
            "sort_by": "timestamp",
            "order": "desc"
        }
        
        print(f"📋 Listing conversations (page {page}, limit {limit})")
        if search:
            print(f"🔍 Search: '{search}'")
        
        try:
            response = self.session.get(f"{self.archive_api_base}/conversations", params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            conversations = result.get('conversations', [])
            pagination = result.get('pagination', {})
            
            print(f"✅ Found {len(conversations)} conversations")
            print(f"📄 Page {pagination.get('page', 1)} of {pagination.get('pages', 1)} ({pagination.get('total', 0)} total)")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Results saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ Archive API Error: {e}")
            return {}
    
    def get_conversation(self, 
                        conversation_id: int, 
                        output_file: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific conversation with messages"""
        
        print(f"📖 Getting conversation {conversation_id}")
        
        try:
            response = self.session.get(f"{self.archive_api_base}/conversations/{conversation_id}/messages", timeout=30)
            response.raise_for_status()
            
            result = response.json()
            conversation = result.get('conversation', {})
            messages = result.get('messages', [])
            
            print(f"✅ Loaded conversation: {conversation.get('title', 'Untitled')}")
            print(f"💬 {len(messages)} messages")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Conversation saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ Archive API Error: {e}")
            return {}
    
    def search_archive(self, 
                      query: str, 
                      semantic: bool = False,
                      limit: int = 50,
                      output_file: Optional[str] = None) -> Dict[str, Any]:
        """Search archived content"""
        
        payload = {
            "query": query,
            "semantic_search": semantic,
            "limit": limit
        }
        
        search_type = "semantic" if semantic else "text"
        print(f"🔍 Searching archive ({search_type}): '{query}'")
        
        try:
            response = self.session.post(f"{self.archive_api_base}/search", data=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            results = result.get('results', [])
            
            print(f"✅ Found {len(results)} results")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Search results saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ Archive API Error: {e}")
            return {}
    
    def process_conversation_content(self, 
                                   conversation_id: int,
                                   persona: str = "philosophical_narrator",
                                   namespace: str = "existential_philosophy", 
                                   style: str = "contemplative_prose",
                                   output_file: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation content and transform it"""
        
        print(f"🔄 Processing conversation {conversation_id}")
        
        # First get the conversation
        conversation_result = self.get_conversation(conversation_id)
        if not conversation_result:
            return {}
        
        messages = conversation_result.get('messages', [])
        if not messages:
            print("❌ No messages found in conversation")
            return {}
        
        # Combine all message content
        combined_text = ""
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('body_text', msg.get('content', ''))
            if content.strip():
                combined_text += f"[{role}]: {content}\n\n"
        
        if not combined_text.strip():
            print("❌ No content found in conversation messages")
            return {}
        
        print(f"📝 Combined {len(messages)} messages ({len(combined_text)} chars)")
        
        # Now transform the combined content
        transform_result = self.transform_text(combined_text, persona, namespace, style)
        
        if transform_result:
            # Combine the conversation metadata with transform result
            full_result = {
                "conversation": conversation_result.get('conversation', {}),
                "original_messages": messages,
                "combined_content": combined_text,
                "transformation": transform_result
            }
            
            if output_file:
                self.save_result(full_result, output_file)
                print(f"💾 Processing result saved to {output_file}")
            
            return full_result
        
        return {}
    
    def save_result(self, result: Dict[str, Any], filename: str):
        """Save result to file"""
        output_path = Path(filename)
        
        if filename.endswith('.json'):
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            # Save as formatted text
            with open(output_path, 'w') as f:
                if 'projection' in result:
                    # Transform result
                    f.write("NARRATIVE TRANSFORMATION\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("ORIGINAL:\n")
                    f.write(result['original']['narrative'] + "\n\n")
                    f.write("TRANSFORMED:\n")
                    f.write(result['projection']['narrative'] + "\n\n")
                    f.write("REFLECTION:\n")
                    f.write(result['projection']['reflection'] + "\n\n")
                    f.write("PROCESS STEPS:\n")
                    for step in result.get('steps', []):
                        f.write(f"- {step['name']}: {step['duration_ms']}ms\n")
                elif 'attributes' in result:
                    # Attributes result
                    f.write("NARRATIVE ATTRIBUTES\n")
                    f.write("=" * 50 + "\n\n")
                    for attr in result['attributes']:
                        f.write(f"{attr['type'].upper()}: {attr['value']} (confidence: {attr['confidence']:.2f})\n")
                elif 'analysis' in result:
                    # Analysis result
                    f.write("NARRATIVE ANALYSIS\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(json.dumps(result, indent=2))
                else:
                    # Generic JSON result
                    f.write(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Humanizer CLI - Narrative transformation and analysis with Archive integration")
    parser.add_argument("command", choices=["transform", "attributes", "analyze", "quantum", "status", 
                                           "list-conversations", "get-conversation", "search-archive", "process-conversation"], 
                       help="Command to execute")
    parser.add_argument("--text", "-t", help="Text to process (or use --file)")
    parser.add_argument("--file", "-f", help="Input file containing text")
    parser.add_argument("--output", "-o", help="Output file (JSON if .json, formatted text otherwise)")
    parser.add_argument("--persona", "-p", default="philosophical_narrator", 
                       help="Target persona for transformation")
    parser.add_argument("--namespace", "-n", default="existential_philosophy",
                       help="Target namespace for transformation") 
    parser.add_argument("--style", "-s", default="contemplative_prose",
                       help="Target style for transformation")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    parser.add_argument("--archive-api-base", default=ARCHIVE_API_BASE, help="Archive API base URL")
    
    # Archive-specific arguments
    parser.add_argument("--conversation-id", type=int, help="Conversation ID for archive operations")
    parser.add_argument("--page", type=int, default=1, help="Page number for conversation listing")
    parser.add_argument("--limit", type=int, default=20, help="Number of results per page")
    parser.add_argument("--search", help="Search query for conversations or archive content")
    parser.add_argument("--semantic", action="store_true", help="Use semantic search instead of text search")
    
    args = parser.parse_args()
    
    cli = HumanizerCLI(args.api_base, args.archive_api_base)
    
    # Check API health based on command
    archive_commands = ["list-conversations", "get-conversation", "search-archive", "process-conversation"]
    
    if args.command in archive_commands:
        if not cli.check_archive_health():
            print(f"❌ Cannot connect to Archive API at {args.archive_api_base}")
            print("Make sure the Archive Upload Server is running:")
            print("  python archive_upload_server.py")
            sys.exit(1)
        
        # For process-conversation, also check main API
        if args.command == "process-conversation":
            if not cli.check_api_health():
                print(f"❌ Cannot connect to Main API at {args.api_base}")
                print("Make sure the Enhanced API server is running:")
                print("  python api_enhanced.py")
                sys.exit(1)
    else:
        if not cli.check_api_health():
            print(f"❌ Cannot connect to API at {args.api_base}")
            print("Make sure the Enhanced API server is running:")
            print("  python api_enhanced.py")
            sys.exit(1)
    
    # Get input text
    if args.text:
        input_text = args.text
    elif args.file:
        try:
            input_text = Path(args.file).read_text()
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    elif args.command in ["status", "list-conversations", "get-conversation", "search-archive", "process-conversation"]:
        input_text = None
    else:
        # Read from stdin
        print("📝 Enter text (Ctrl+D to finish):")
        input_text = sys.stdin.read().strip()
        if not input_text:
            print("❌ No input text provided")
            sys.exit(1)
    
    # Execute command
    if args.command == "transform":
        result = cli.transform_text(input_text, args.persona, args.namespace, args.style, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("TRANSFORMED TEXT:")
            print("="*60)
            print(result['projection']['narrative'])
            
    elif args.command == "attributes":
        result = cli.extract_attributes(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60) 
            print("EXTRACTED ATTRIBUTES:")
            print("="*60)
            for attr in result.get('attributes', []):
                print(f"{attr['type'].upper()}: {attr['value']} (confidence: {attr['confidence']:.2f})")
                
    elif args.command == "analyze":
        result = cli.analyze_meaning(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("MEANING ANALYSIS:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
    elif args.command == "quantum":
        result = cli.quantum_analysis(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("QUANTUM ANALYSIS:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
    elif args.command == "status":
        status = cli.get_provider_status()
        print("\n" + "="*60)
        print("LLM PROVIDER STATUS:")
        print("="*60)
        for provider, info in status.items():
            status_icon = "✅" if info.get('available') else "❌"
            print(f"{status_icon} {provider}: {info.get('status_message', 'Unknown')}")
            
    elif args.command == "list-conversations":
        search_query = args.search or ""
        result = cli.list_conversations(args.page, args.limit, search_query, args.output)
        if result and not args.output:
            conversations = result.get('conversations', [])
            pagination = result.get('pagination', {})
            print("\n" + "="*80)
            print("ARCHIVED CONVERSATIONS:")
            print("="*80)
            for conv in conversations:
                print(f"ID: {conv['id']} | {conv['title'][:60]}...")
                print(f"    Messages: {conv['messages']} | Created: {conv['created'][:19] if conv['created'] else 'Unknown'}")
                print()
            print(f"Page {pagination.get('page', 1)} of {pagination.get('pages', 1)} | Total: {pagination.get('total', 0)}")
            
    elif args.command == "get-conversation":
        if not args.conversation_id:
            print("❌ --conversation-id required for get-conversation command")
            sys.exit(1)
        result = cli.get_conversation(args.conversation_id, args.output)
        if result and not args.output:
            conversation = result.get('conversation', {})
            messages = result.get('messages', [])
            print("\n" + "="*80)
            print(f"CONVERSATION: {conversation.get('title', 'Untitled')}")
            print("="*80)
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('body_text', msg.get('content', ''))
                timestamp = msg.get('timestamp', '')[:19] if msg.get('timestamp') else 'Unknown'
                print(f"{i}. [{role}] ({timestamp})")
                print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
                print()
                
    elif args.command == "search-archive":
        if not args.search:
            print("❌ --search query required for search-archive command")
            sys.exit(1)
        result = cli.search_archive(args.search, args.semantic, args.limit, args.output)
        if result and not args.output:
            results = result.get('results', [])
            search_type = result.get('search_type', 'text')
            print("\n" + "="*80)
            print(f"ARCHIVE SEARCH RESULTS ({search_type.upper()}):")
            print("="*80)
            for i, item in enumerate(results, 1):
                title = item.get('title', 'Untitled')
                content = item.get('body_text', '')
                content_type = item.get('content_type', 'unknown')
                author = item.get('author', 'Unknown')
                print(f"{i}. {title} ({content_type})")
                print(f"   Author: {author}")
                print(f"   {content[:150]}{'...' if len(content) > 150 else ''}")
                print()
                
    elif args.command == "process-conversation":
        if not args.conversation_id:
            print("❌ --conversation-id required for process-conversation command")
            sys.exit(1)
        result = cli.process_conversation_content(args.conversation_id, args.persona, args.namespace, args.style, args.output)
        if result and not args.output:
            conversation = result.get('conversation', {})
            transformation = result.get('transformation', {})
            print("\n" + "="*80)
            print(f"PROCESSED CONVERSATION: {conversation.get('title', 'Untitled')}")
            print("="*80)
            if transformation and 'projection' in transformation:
                print("TRANSFORMED CONTENT:")
                print("-" * 40)
                print(transformation['projection']['narrative'])
                print("\nREFLECTION:")
                print("-" * 40)
                print(transformation['projection']['reflection'])

if __name__ == "__main__":
    main()