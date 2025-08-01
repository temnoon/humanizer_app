#!/usr/bin/env python3
"""
Hierarchical Embedding CLI
Command-line interface for processing and searching the hierarchical embedding corpus
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

from hierarchical_embedding_engine import HierarchicalEmbeddingEngine

def process_conversations(engine, conversation_ids=None, max_levels=3):
    """Process conversations from the archive into hierarchical embeddings"""
    
    # Import archive integration here to avoid circular imports
    try:
        from archive_cli import ArchiveCLI
        archive = ArchiveCLI()
    except ImportError:
        print("Error: archive_cli not available. Make sure it's in the same directory.")
        return
    
    if conversation_ids:
        conversations = []
        for conv_id in conversation_ids:
            conv = archive.get_conversation(conv_id)
            if conv:
                conversations.append(conv)
    else:
        # Process all conversations (or a subset)
        conversations = archive.list_conversations(limit=100)  # Start with first 100
    
    print(f"Processing {len(conversations)} conversations...")
    
    results = []
    for i, conv in enumerate(conversations):
        print(f"[{i+1}/{len(conversations)}] Processing conversation {conv['id']}")
        
        try:
            # Get full conversation text and messages
            full_conv = archive.get_conversation(conv['id'])
            
            # Combine all messages into conversation text
            conversation_text = ""
            messages = []
            
            if 'messages' in full_conv:
                for msg in full_conv['messages']:
                    conversation_text += f"[{msg.get('role', 'user')}]: {msg.get('content', '')}\n\n"
                    messages.append({
                        'id': msg.get('id'),
                        'content': msg.get('content', ''),
                        'role': msg.get('role', 'user')
                    })
            
            # Process through hierarchical embedding engine
            result = engine.process_conversation(
                conversation_id=conv['id'],
                conversation_text=conversation_text,
                messages=messages,
                max_levels=max_levels
            )
            
            results.append(result)
            
        except Exception as e:
            print(f"Error processing conversation {conv['id']}: {e}")
            continue
    
    return results

def search_corpus(engine, query, levels=None, max_results=20, filter_terms=None):
    """Search the hierarchical embedding corpus"""
    
    print(f"🔍 Searching for: '{query}'")
    if filter_terms:
        print(f"   Filter terms: {', '.join(filter_terms)}")
    
    results = engine.search_semantic(
        query=query,
        max_results=max_results,
        levels=levels,
        filter_terms=filter_terms
    )
    
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:")
    print("=" * 60)
    
    # Group by level for display
    level_groups = defaultdict(list)
    for result in results:
        level_groups[result['level']].append(result)
    
    for level in sorted(level_groups.keys()):
        level_results = level_groups[level]
        level_name = {0: "Original", 1: "Summary", 2: "Distillation"}.get(level, f"Level {level}")
        
        print(f"\n📊 {level_name} ({len(level_results)} results):")
        print("-" * 40)
        
        for i, result in enumerate(level_results[:5]):  # Show top 5 per level
            score = result['relevance_score']
            conv_id = result['conversation_id']
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            
            print(f"{i+1}. Score: {score:.3f} | Conversation: {conv_id}")
            print(f"   {content}")
            print()

def show_lineage(engine, chunk_id):
    """Show the lineage of a specific chunk"""
    
    lineage = engine.get_chunk_lineage(chunk_id)
    
    if not lineage:
        print(f"Chunk {chunk_id} not found.")
        return
    
    chunk = lineage['chunk']
    print(f"🧬 Chunk Lineage: {chunk_id}")
    print("=" * 60)
    
    print(f"Conversation: {chunk['conversation_id']}")
    print(f"Level: {chunk['level']}")
    print(f"Type: {chunk['chunk_type']}")
    print(f"Tokens: {chunk['token_count']}")
    print(f"Created: {chunk['created_at']}")
    
    if lineage['parents']:
        print(f"\n📤 Parents ({len(lineage['parents'])}):")
        for parent in lineage['parents']:
            print(f"  - {parent['chunk_id']} (Level {parent['level']}, {parent['chunk_type']})")
    
    if lineage['children']:
        print(f"\n📥 Children ({len(lineage['children'])}):")
        for child in lineage['children']:
            print(f"  - {child['chunk_id']} (Level {child['level']}, {child['chunk_type']})")

def show_stats(engine):
    """Show corpus statistics"""
    
    import sqlite3
    
    with sqlite3.connect(engine.db_path) as conn:
        # Count chunks by level
        cursor = conn.execute("""
            SELECT level, chunk_type, COUNT(*) as count, AVG(token_count) as avg_tokens
            FROM chunk_provenance 
            GROUP BY level, chunk_type
            ORDER BY level, chunk_type
        """)
        
        level_stats = cursor.fetchall()
        
        print("📊 Corpus Statistics")
        print("=" * 50)
        
        total_chunks = 0
        for level, chunk_type, count, avg_tokens in level_stats:
            total_chunks += count
            level_name = {0: "Original", 1: "Summary", 2: "Distillation"}.get(level, f"Level {level}")
            print(f"{level_name:12} | {chunk_type:12} | {count:6} chunks | {avg_tokens:6.0f} avg tokens")
        
        print(f"\nTotal chunks: {total_chunks}")
        
        # Count conversations processed
        cursor = conn.execute("SELECT COUNT(DISTINCT conversation_id) FROM chunk_provenance")
        conv_count = cursor.fetchone()[0]
        print(f"Conversations: {conv_count}")
        
        # Processing log
        cursor = conn.execute("""
            SELECT processing_stage, SUM(chunks_created) as total_chunks
            FROM processing_log 
            GROUP BY processing_stage
            ORDER BY processing_stage
        """)
        
        print(f"\n📝 Processing History:")
        for stage, chunks in cursor.fetchall():
            print(f"  {stage}: {chunks} chunks created")

def main():
    parser = argparse.ArgumentParser(description="Hierarchical Embedding CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process conversations into hierarchical embeddings')
    process_parser.add_argument('--conversations', nargs='+', type=int, help='Specific conversation IDs to process')
    process_parser.add_argument('--max-levels', type=int, default=3, help='Maximum summarization levels (default: 3)')
    process_parser.add_argument('--all', action='store_true', help='Process all conversations in archive')
    
    # Search command  
    search_parser = subparsers.add_parser('search', help='Search the hierarchical corpus')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--levels', nargs='+', type=int, help='Levels to search (default: all)')
    search_parser.add_argument('--max-results', type=int, default=20, help='Maximum results (default: 20)')
    search_parser.add_argument('--filter-terms', nargs='+', help='Terms to boost in results')
    search_parser.add_argument('--output', help='Save results to JSON file')
    
    # Lineage command
    lineage_parser = subparsers.add_parser('lineage', help='Show chunk lineage')
    lineage_parser.add_argument('chunk_id', help='Chunk ID to examine')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show corpus statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize engine
    engine = HierarchicalEmbeddingEngine()
    
    if args.command == 'process':
        if args.all:
            results = process_conversations(engine, max_levels=args.max_levels)
        elif args.conversations:
            results = process_conversations(engine, args.conversations, args.max_levels)
        else:
            print("Specify --conversations [IDs] or --all")
            return
        
        print(f"\n✅ Processing complete. Processed {len(results)} conversations.")
        
    elif args.command == 'search':
        results = search_corpus(
            engine, 
            args.query, 
            levels=args.levels,
            max_results=args.max_results,
            filter_terms=args.filter_terms
        )
        
        if args.output and results:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")
            
    elif args.command == 'lineage':
        show_lineage(engine, args.chunk_id)
        
    elif args.command == 'stats':
        show_stats(engine)

if __name__ == "__main__":
    main()