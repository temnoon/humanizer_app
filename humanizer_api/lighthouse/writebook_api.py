"""
Writebook Integration API
========================

FastAPI endpoints for integrating with writebook.humanizer.com
Acts as a proxy/bridge for publishing writebooks from the local UI.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Pydantic models for writebook API
class WritebookLeaf(BaseModel):
    type: str = "Page"  # "Page", "Section", "Picture"
    content: str
    position: int
    metadata: Optional[Dict] = None

class WritebookPublishRequest(BaseModel):
    title: str
    is_public: bool = False
    leaves: List[WritebookLeaf]
    source_metadata: Optional[Dict] = None

class WritebookSettings(BaseModel):
    base_url: str = "https://writebook.humanizer.com"
    api_key: Optional[str] = None
    auth_token: Optional[str] = None

# Router for writebook endpoints
writebook_router = APIRouter(prefix="/api/writebook", tags=["writebook"])

@writebook_router.post("/publish")
async def publish_to_writebook(request_data: Dict):
    """
    Publish a writebook to the remote writebook.humanizer.com instance.
    Acts as a proxy to handle authentication and formatting.
    """
    try:
        # Extract request and settings from the incoming data
        settings_data = request_data.get('settings', {})
        settings = WritebookSettings(**settings_data)
        
        # Create request object from the data
        request = WritebookPublishRequest(**{
            k: v for k, v in request_data.items() 
            if k != 'settings'
        })
        
        # Prepare the payload for the remote writebook API
        payload = {
            "title": request.title,
            "is_public": request.is_public,
            "leaves": []
        }
        
        # Convert leaves to writebook format
        for leaf in request.leaves:
            writebook_leaf = {
                "type": leaf.type,
                "content": leaf.content,
                "position": leaf.position
            }
            
            # Add metadata as comments if provided
            if leaf.metadata:
                metadata = leaf.metadata
                content = leaf.content
                
                if metadata.get('original_author'):
                    content = f"<!-- Original Author: {metadata['original_author']} -->\n{content}"
                if metadata.get('original_timestamp'):
                    content = f"<!-- Original Timestamp: {metadata['original_timestamp']} -->\n{content}"
                    
                writebook_leaf["content"] = content
                
            payload["leaves"].append(writebook_leaf)
            
        # Add source metadata if provided
        if request.source_metadata:
            payload["source_metadata"] = request.source_metadata
            
        # Make the API call to writebook.humanizer.com
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add authentication if available
            if settings.api_key:
                headers["Authorization"] = f"Bearer {settings.api_key}"
            elif settings.auth_token:
                headers["Authorization"] = f"Token {settings.auth_token}"
                
            # Try the API endpoint first
            try:
                response = await client.post(
                    f"{settings.base_url}/api/import_conversation",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "book_id": result.get("book_id"),
                        "url": result.get("url", f"{settings.base_url}/books/{result.get('book_id')}"),
                        "message": result.get("message", "Book created successfully"),
                        "leaves_created": result.get("leaves_created", len(payload["leaves"]))
                    }
                elif response.status_code == 404:
                    # API endpoint doesn't exist, provide instructions
                    logger.warning("Writebook API endpoint not found at remote server")
                    return {
                        "success": False,
                        "error": "api_not_found",
                        "message": "The API endpoint doesn't exist on the remote writebook server",
                        "instructions": {
                            "setup_required": True,
                            "manual_url": settings.base_url,
                            "api_setup_guide": "Add the API controller from WRITEBOOK_API_SETUP.md to your writebook installation"
                        }
                    }
                else:
                    # Other error from the API
                    error_text = await response.text()
                    logger.error(f"Writebook API error {response.status_code}: {error_text}")
                    return {
                        "success": False,
                        "error": "api_error",
                        "status_code": response.status_code,
                        "message": f"Remote API error: {error_text}"
                    }
                    
            except httpx.ConnectError:
                # Network connection error
                logger.error(f"Failed to connect to writebook server: {settings.base_url}")
                return {
                    "success": False,
                    "error": "connection_error",
                    "message": f"Could not connect to {settings.base_url}",
                    "instructions": {
                        "manual_url": settings.base_url,
                        "suggestion": "You can manually create the writebook by copying the content"
                    }
                }
                
    except Exception as e:
        logger.error(f"Writebook publish error: {e}")
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")

@writebook_router.post("/test-connection")
async def test_writebook_connection(settings: WritebookSettings):
    """
    Test connection to the writebook server and check for API availability.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test basic connection
            try:
                response = await client.get(f"{settings.base_url}/", timeout=5.0)
                basic_connection = response.status_code == 200
            except:
                basic_connection = False
                
            # Test API endpoint availability
            api_available = False
            if basic_connection:
                try:
                    response = await client.get(f"{settings.base_url}/api/import_conversation")
                    # 404 is expected for GET, 405 means the endpoint exists but wrong method
                    api_available = response.status_code in [404, 405, 422]
                except:
                    api_available = False
                    
            return {
                "base_url": settings.base_url,
                "basic_connection": basic_connection,
                "api_available": api_available,
                "status": "ready" if (basic_connection and api_available) else "setup_needed",
                "recommendations": {
                    "basic_connection": "✅ Server reachable" if basic_connection else "❌ Server not reachable",
                    "api_endpoint": "✅ API endpoint available" if api_available else "❌ API endpoint needs setup"
                }
            }
            
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return {
            "base_url": settings.base_url,
            "basic_connection": False,
            "api_available": False,
            "status": "error",
            "error": str(e)
        }

@writebook_router.get("/status")
async def get_writebook_status():
    """
    Get status of writebook integration capabilities.
    """
    return {
        "service": "writebook_integration",
        "status": "available",
        "endpoints": {
            "publish": "/api/writebook/publish",
            "test_connection": "/api/writebook/test-connection",
            "status": "/api/writebook/status"
        },
        "features": [
            "Proxy publishing to remote writebook servers",
            "Authentication handling",
            "Error recovery and fallback instructions",
            "Connection testing"
        ]
    }

@writebook_router.post("/convert-conversation")
async def convert_conversation_to_writebook(conversation_data: Dict):
    """
    Convert conversation data to writebook format.
    Helper endpoint for formatting conversations before publishing.
    """
    try:
        # Extract conversation metadata
        metadata = conversation_data.get('metadata', {})
        messages = conversation_data.get('messages', [])
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found in conversation")
            
        # Create writebook structure
        title = metadata.get('title', f"Conversation from {datetime.now().strftime('%Y-%m-%d')}")
        leaves = []
        
        # Add a title section
        leaves.append(WritebookLeaf(
            type="Section",
            content=title,
            position=1
        ))
        
        # Convert messages to pages
        position = 2
        for i, message in enumerate(messages):
            # Create page content
            content = message.get('content', '')
            author = message.get('author', 'Unknown')
            timestamp = message.get('timestamp', '')
            
            # Format the message
            page_content = f"## Message from {author}\n\n{content}"
            
            if timestamp:
                page_content += f"\n\n*Sent: {timestamp}*"
                
            leaves.append(WritebookLeaf(
                type="Page",
                content=page_content,
                position=position,
                metadata={
                    "original_author": author,
                    "original_timestamp": timestamp,
                    "original_message_id": message.get('id', f'msg_{i}')
                }
            ))
            position += 1
            
        return {
            "title": title,
            "leaves": [leaf.dict() for leaf in leaves],
            "source_metadata": {
                "conversation_id": metadata.get('conversation_id'),
                "exported_at": datetime.now().isoformat(),
                "participant_count": len(set(msg.get('author') for msg in messages if msg.get('author'))),
                "message_count": len(messages)
            }
        }
        
    except Exception as e:
        logger.error(f"Conversation conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

# Note: CORS headers are handled by the main FastAPI app's CORSMiddleware