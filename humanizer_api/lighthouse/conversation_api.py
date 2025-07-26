"""
Conversation API Endpoints
==========================

FastAPI endpoints for managing imported conversations.
Integrates with the main Lighthouse API system.

Author: Enhanced for conversation management
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
import json
import tempfile
import zipfile
import shutil
from pathlib import Path
import logging

from conversation_importer import ConversationImporter, ImportedConversation
from conversation_browser import ConversationBrowser

logger = logging.getLogger(__name__)

# Initialize conversation management
conversation_browser = ConversationBrowser()

def add_conversation_routes(app: FastAPI):
    """
    Add conversation management routes to an existing FastAPI app.
    """
    
    @app.get("/api/conversations")
    async def list_conversations(
        detailed: bool = False,
        page: int = 1,
        limit: int = 20,
        search: str = "",
        sort_by: str = "timestamp",
        order: str = "desc",
        min_words: int = None,
        max_words: int = None,
        min_messages: int = None,
        max_messages: int = None,
        date_from: str = None,
        date_to: str = None,
        author: str = None
    ):
        """
        List all imported conversations with pagination and search.
        """
        try:
            # Use search if provided
            if search.strip():
                conversations = conversation_browser.search_conversations(search.strip(), limit * 10)  # Get more for filtering
            else:
                conversations = conversation_browser.list_conversations(detailed=detailed)
            
            # Apply additional filters
            filtered_conversations = conversations
            if min_messages:
                filtered_conversations = [c for c in filtered_conversations if c.get('messages', 0) >= min_messages]
            if max_messages:
                filtered_conversations = [c for c in filtered_conversations if c.get('messages', 0) <= max_messages]
            
            # Apply sorting
            if sort_by == "timestamp":
                filtered_conversations.sort(key=lambda x: x.get('imported', ''), reverse=(order == 'desc'))
            elif sort_by == "title":
                filtered_conversations.sort(key=lambda x: x.get('title', ''), reverse=(order == 'desc'))
            elif sort_by == "messages":
                filtered_conversations.sort(key=lambda x: x.get('messages', 0), reverse=(order == 'desc'))
            
            # Apply pagination
            total = len(filtered_conversations)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_conversations = filtered_conversations[start_idx:end_idx]
            
            return {
                "conversations": paginated_conversations,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/{conversation_id}")
    async def get_conversation(conversation_id: str, 
                             max_content_length: int = 500,
                             show_metadata: bool = False):
        """
        Get a specific conversation by ID.
        """
        try:
            conversation = conversation_browser.show_conversation(
                conversation_id, 
                max_content_length=max_content_length,
                show_metadata=show_metadata
            )
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            return conversation
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/{conversation_id}/messages")
    async def get_conversation_messages(conversation_id: str, 
                                      start: int = 0, 
                                      limit: int = 1000):
        """
        Get messages from a conversation with pagination.
        """
        try:
            conversation_data = conversation_browser.show_conversation(
                conversation_id, 
                max_content_length=10000,  # Get full content
                show_metadata=True
            )
            
            if not conversation_data:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            messages = conversation_data.get('messages', [])
            paginated_messages = messages[start:start + limit] if limit > 0 else messages
            
            return {
                "conversation": {
                    "id": conversation_id,
                    "title": conversation_data.get('title', ''),
                    "source_format": conversation_data.get('source_format', 'unknown')
                },
                "messages": paginated_messages,
                "pagination": {
                    "start": start,
                    "limit": limit,
                    "total": len(messages)
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get messages for {conversation_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/conversations/import")
    async def import_conversation(
        conversation_file: UploadFile = File(...),
        format: str = Form("chatgpt"),
        title: Optional[str] = Form(None)
    ):
        """
        Import a conversation from uploaded file(s).
        Supports ChatGPT conversation.json files and zip archives.
        """
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Handle different file types
                if conversation_file.filename.endswith('.zip'):
                    # Extract zip file
                    zip_path = temp_path / "conversation.zip"
                    with open(zip_path, 'wb') as f:
                        shutil.copyfileobj(conversation_file.file, f)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_path / "extracted")
                    
                    conversation_dir = temp_path / "extracted"
                    
                elif conversation_file.filename.endswith('.json'):
                    # Single JSON file
                    conversation_dir = temp_path / "conversation"
                    conversation_dir.mkdir()
                    
                    json_path = conversation_dir / "conversation.json"
                    with open(json_path, 'wb') as f:
                        shutil.copyfileobj(conversation_file.file, f)
                
                else:
                    raise HTTPException(status_code=400, detail="Unsupported file format. Use .json or .zip")
                
                # Import conversation
                if format == "chatgpt":
                    conversation = conversation_browser.importer.import_chatgpt_conversation(str(conversation_dir))
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
                
                # Update title if provided
                if title:
                    # TODO: Update conversation title in metadata
                    pass
                
                return {
                    "success": True,
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "messages": len(conversation.messages),
                    "source_format": conversation.source_format
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to import conversation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/{conversation_id}/export")
    async def export_conversation(conversation_id: str, format: str = "markdown"):
        """
        Export a conversation in the specified format.
        """
        try:
            conversation = conversation_browser.importer.load_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            if format == "markdown":
                markdown_content = conversation_browser.export_conversation_to_markdown(conversation_id)
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                    f.write(markdown_content)
                    temp_path = f.name
                
                # Return file
                filename = f"{conversation.title.replace(' ', '_')}.md"
                return FileResponse(
                    temp_path,
                    media_type="text/markdown",
                    filename=filename
                )
            
            elif format == "json":
                conversation_data = conversation_browser.show_conversation(conversation_id, 
                                                                         max_content_length=-1,
                                                                         show_metadata=True)
                return JSONResponse(conversation_data)
            
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to export conversation {conversation_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/conversations/search")
    async def search_conversations(
        query: str = Form(...),
        limit: int = Form(10)
    ):
        """
        Search conversations using full-text search.
        """
        try:
            results = conversation_browser.search_conversations(query, limit)
            return {
                "query": query,
                "total_results": len(results),
                "conversations": results
            }
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/stats")
    async def get_conversation_stats():
        """
        Get statistics about imported conversations.
        """
        try:
            stats = conversation_browser.get_conversation_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/conversations/{conversation_id}")
    async def delete_conversation(conversation_id: str):
        """
        Delete an imported conversation.
        """
        try:
            success = conversation_browser.delete_conversation(conversation_id)
            if not success:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            return {"success": True, "message": f"Deleted conversation {conversation_id}"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/{conversation_id}/transform")
    async def transform_conversation_message(
        conversation_id: str,
        message_id: str,
        persona: str = "philosopher",
        namespace: str = "philosophical", 
        style: str = "contemplative"
    ):
        """
        Transform a specific message from a conversation using the Lighthouse transformation engine.
        """
        try:
            # Load conversation
            conversation = conversation_browser.importer.load_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Find message
            message = None
            for msg in conversation.messages:
                if msg.id == message_id:
                    message = msg
                    break
            
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")
            
            # Transform using existing Lighthouse API
            # This would call the main transformation endpoint
            transform_data = {
                "text": message.content,
                "persona": persona,
                "namespace": namespace,
                "style": style
            }
            
            # For now, return the transform request
            # In a full implementation, this would call the actual transformation API
            return {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "original_content": message.content,
                "transform_request": transform_data,
                "note": "Transform integration pending - use main /api/transform endpoint"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to transform message: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Standalone app for testing
if __name__ == "__main__":
    import uvicorn
    
    app = FastAPI(title="Conversation API", version="1.0.0")
    add_conversation_routes(app)
    
    @app.get("/")
    async def root():
        return {"message": "Conversation API", "endpoints": "/docs"}
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8200)