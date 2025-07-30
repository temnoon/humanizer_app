"""
PostgreSQL Conversation API
===========================

API to access conversations stored in PostgreSQL humanizer_archive database.
This connects the React GUI to the existing PostgreSQL data.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class PostgresConversationAPI:
    """
    API for accessing conversations from PostgreSQL archive.
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('POSTGRES_URL', 'postgresql://tem@localhost/humanizer_archive')
    
    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def list_conversations(self, 
                          page: int = 1, 
                          limit: int = 20,
                          search: str = "",
                          sort_by: str = "timestamp",
                          order: str = "desc") -> Dict[str, Any]:
        """
        List conversations grouped by parent_id from archived_content messages.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build WHERE clause for search
            search_clause = ""
            params = []
            
            if search.strip():
                search_clause = "AND (conv_data.title ILIKE %s OR conv_data.body_text ILIKE %s)"
                search_param = f"%{search.strip()}%"
                params.extend([search_param, search_param])
            
            # Build ORDER clause
            order_mapping = {
                'timestamp': 'first_message_time',
                'title': 'title',
                'created_at': 'created_at'
            }
            sort_column = order_mapping.get(sort_by, 'first_message_time')
            order_direction = 'ASC' if order.lower() == 'asc' else 'DESC'
            
            # Count unique conversations (by parent_id)
            count_query = f"""
                WITH conversation_groups AS (
                    SELECT DISTINCT parent_id
                    FROM archived_content 
                    WHERE source_type = 'node_conversation' 
                      AND parent_id IS NOT NULL
                )
                SELECT COUNT(*) as total FROM conversation_groups
            """
            cursor.execute(count_query)
            total_count = cursor.fetchone()['total']
            
            # Calculate pagination
            offset = (page - 1) * limit
            total_pages = (total_count + limit - 1) // limit
            
            # Get conversations grouped by parent_id
            query = f"""
                WITH conversation_summary AS (
                    SELECT 
                        parent_id,
                        COUNT(*) as message_count,
                        MIN((source_metadata->>'create_time')::float) as first_message_time,
                        MAX((source_metadata->>'create_time')::float) as last_message_time,
                        MIN(created_at) as imported_time,
                        -- Get title from first user message or first message with title
                        (SELECT COALESCE(title, LEFT(body_text, 100)) 
                         FROM archived_content a2 
                         WHERE a2.parent_id = a1.parent_id 
                           AND a2.source_type = 'node_conversation'
                           AND (a2.title IS NOT NULL AND a2.title <> '' 
                                OR a2.source_metadata->>'role' = 'user')
                         ORDER BY (a2.source_metadata->>'create_time')::float ASC 
                         LIMIT 1) as conversation_title
                    FROM archived_content a1
                    WHERE source_type = 'node_conversation' 
                      AND parent_id IS NOT NULL
                    GROUP BY parent_id
                ),
                filtered_conversations AS (
                    SELECT *
                    FROM conversation_summary conv_data
                    WHERE 1=1 {search_clause}
                )
                SELECT 
                    parent_id::text as id,
                    COALESCE(conversation_title, 'Untitled Conversation') as title,
                    'node_conversation' as source,
                    message_count as messages,
                    to_timestamp(first_message_time) as created,
                    imported_time as imported
                FROM filtered_conversations
                ORDER BY {sort_column} {order_direction}
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, params + [limit, offset])
            conversations = []
            
            for row in cursor.fetchall():
                conv_data = {
                    'id': row['id'],
                    'title': row['title'] or 'Untitled Conversation',
                    'source': row['source'],
                    'messages': row['messages'],
                    'created': row['created'].isoformat() if row['created'] else '',
                    'imported': row['imported'].isoformat() if row['imported'] else ''
                }
                conversations.append(conv_data)
            
            conn.close()
            
            return {
                'conversations': conversations,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_conversation_messages(self, 
                                conversation_id: str,
                                start: int = 0,
                                limit: int = 1000) -> Dict[str, Any]:
        """
        Get messages for a specific conversation by parent_id.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert conversation_id to parent_id (should be numeric)
            try:
                parent_id = int(conversation_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid conversation ID format")
            
            # Get all messages for this conversation
            cursor.execute("""
                SELECT 
                    source_id,
                    source_metadata->>'role' as role,
                    body_text as content,
                    (source_metadata->>'create_time')::float as create_time,
                    source_metadata
                FROM archived_content 
                WHERE parent_id = %s 
                  AND source_type = 'node_conversation'
                ORDER BY (source_metadata->>'create_time')::float ASC
            """, (parent_id,))
            
            message_rows = cursor.fetchall()
            if not message_rows:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Convert to message format
            messages = []
            conversation_title = "Untitled Conversation"
            
            for row in message_rows:
                # Use first user message content as conversation title if available
                if (row['role'] == 'user' and conversation_title == "Untitled Conversation" 
                    and row['content'] and len(row['content'].strip()) > 0):
                    # Take first 100 chars as title
                    conversation_title = row['content'][:100].strip()
                    if len(row['content']) > 100:
                        conversation_title += "..."
                
                messages.append({
                    'id': row['source_id'],
                    'role': row['role'] or 'unknown',
                    'content': row['content'] or '',
                    'timestamp': datetime.fromtimestamp(row['create_time']).isoformat() if row['create_time'] else None,
                    'metadata': row['source_metadata'] or {}
                })
            
            # Apply pagination to messages
            total_messages = len(messages)
            paginated_messages = messages[start:start + limit] if limit > 0 else messages
            
            conn.close()
            
            return {
                'conversation': {
                    'id': conversation_id,
                    'title': conversation_title,
                    'source_format': 'node_conversation'
                },
                'messages': paginated_messages,
                'pagination': {
                    'start': start,
                    'limit': limit,
                    'total': total_messages
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation messages: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Global instance
postgres_api = PostgresConversationAPI()

def add_postgres_conversation_routes(app: FastAPI):
    """
    Add PostgreSQL conversation routes to FastAPI app.
    """
    
    @app.get("/api/conversations/postgres")
    async def list_postgres_conversations(
        page: int = 1,
        limit: int = 20,
        search: str = "",
        sort_by: str = "timestamp",
        order: str = "desc"
    ):
        """List conversations from PostgreSQL archive."""
        return postgres_api.list_conversations(page, limit, search, sort_by, order)
    
    @app.get("/api/conversations/postgres/{conversation_id}/messages")
    async def get_postgres_conversation_messages(
        conversation_id: str,
        start: int = 0,
        limit: int = 1000
    ):
        """Get messages from PostgreSQL conversation."""
        return postgres_api.get_conversation_messages(conversation_id, start, limit)

def replace_conversation_routes(app: FastAPI):
    """
    Replace the existing conversation routes to use PostgreSQL.
    """
    
    @app.get("/api/conversations")
    async def list_conversations_pg(
        page: int = 1,
        limit: int = 20,
        search: str = "",
        sort_by: str = "timestamp",
        order: str = "desc",
        detailed: bool = False,
        min_words: int = None,
        max_words: int = None,
        min_messages: int = None,
        max_messages: int = None,
        date_from: str = None,
        date_to: str = None,
        author: str = None
    ):
        """List conversations from PostgreSQL archive - enhanced version."""
        return postgres_api.list_conversations(page, limit, search, sort_by, order)
    
    @app.get("/api/conversations/{conversation_id}/messages")
    async def get_conversation_messages_pg(
        conversation_id: str,
        start: int = 0,
        limit: int = 1000
    ):
        """Get messages from PostgreSQL conversation - enhanced version."""
        return postgres_api.get_conversation_messages(conversation_id, start, limit)