"""
Enhanced Conversation API V2
===========================

Updated API endpoints supporting:
1. Proper UUID handling with original ChatGPT IDs
2. Duplicate detection and incremental updates
3. Image gallery and media management
4. Bulk import capabilities
5. Enhanced web interface support

Author: Enhanced for production use
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from typing import List, Dict, Any, Optional
import json
import tempfile
import zipfile
import shutil
from pathlib import Path
import logging
import mimetypes
import os
from PIL import Image
import io

from conversation_importer_v2 import (
    EnhancedConversationImporter, 
    ConversationDatabase,
    import_single_conversation,
    bulk_import_conversations,
    get_image_gallery
)

logger = logging.getLogger(__name__)

# Initialize enhanced systems
enhanced_importer = EnhancedConversationImporter()
conversation_db = ConversationDatabase()

def add_enhanced_conversation_routes(app: FastAPI):
    """
    Add enhanced conversation management routes to FastAPI app.
    """
    
    @app.get("/api/conversations/v2", response_model=List[Dict[str, Any]])
    async def list_conversations_v2(detailed: bool = False, limit: int = 50, offset: int = 0):
        """
        List all imported conversations with enhanced metadata.
        """
        try:
            # This would need database query implementation
            # For now, return placeholder
            return []
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/conversations/import/single")
    async def import_single_conversation_endpoint(
        conversation_file: UploadFile = File(...),
        force_update: bool = Form(False)
    ):
        """
        Import a single conversation.json file with proper duplicate handling.
        """
        try:
            # Validate file type
            if not conversation_file.filename.endswith('.json'):
                raise HTTPException(status_code=400, detail="File must be a .json file")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as temp_file:
                shutil.copyfileobj(conversation_file.file, temp_file)
                temp_path = temp_file.name
            
            try:
                # Import conversation
                conversation, status = import_single_conversation(temp_path, force_update)
                
                # Get message count (either from messages array or metadata for duplicates)
                message_count = len(conversation.messages) if conversation.messages else conversation.metadata.get('total_messages', 0)
                
                return {
                    "success": True,
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "messages": message_count,
                    "source_format": conversation.source_format,
                    "import_status": status,
                    "checksum": conversation.checksum,
                    "has_media": conversation.media_directory is not None
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Failed to import conversation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/conversations/import/bulk")
    async def bulk_import_conversations_endpoint(
        archive_file: UploadFile = File(...),
        force_update: bool = Form(False)
    ):
        """
        Bulk import conversations from a zip archive or folder structure.
        """
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                if archive_file.filename.endswith('.zip'):
                    # Extract zip file
                    zip_path = temp_path / "archive.zip"
                    with open(zip_path, 'wb') as f:
                        shutil.copyfileobj(archive_file.file, f)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_path / "extracted")
                    
                    import_dir = temp_path / "extracted"
                else:
                    raise HTTPException(status_code=400, detail="File must be a .zip archive")
                
                # Perform bulk import
                results = bulk_import_conversations(str(import_dir), force_update)
                
                return {
                    "success": True,
                    "summary": {
                        "total_found": results['total_found'],
                        "new": results['new'],
                        "updated": results['updated'],
                        "duplicates": results['duplicates'],
                        "errors": results['errors']
                    },
                    "conversations": results['conversations']
                }
                
        except Exception as e:
            logger.error(f"Failed to bulk import conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/images")
    async def get_image_gallery_endpoint(
        limit: int = 50,
        offset: int = 0,
        search: str = "",
        filter: str = "all"
    ):
        """
        Get images for gallery view with search and filtering.
        """
        try:
            images = get_image_gallery(limit + 1, offset)  # Get one extra to check if more exist
            
            has_more = len(images) > limit
            if has_more:
                images = images[:limit]
            
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                images = [img for img in images if 
                         search_lower in img['filename'].lower() or 
                         search_lower in (img['conversation_title'] or '').lower()]
            
            # Apply type filter
            if filter == "with_message":
                images = [img for img in images if img['message_id']]
            elif filter == "orphaned":
                images = [img for img in images if not img['message_id']]
            
            return {
                "images": images,
                "has_more": has_more,
                "total_returned": len(images)
            }
            
        except Exception as e:
            logger.error(f"Failed to get image gallery: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/media/{media_id}")
    async def get_media_file(media_id: str):
        """
        Serve a media file by ID.
        """
        try:
            # Get media file info from database
            media_info = conversation_db._get_media_file_info(media_id)
            if not media_info:
                raise HTTPException(status_code=404, detail="Media file not found")
            
            file_path = Path(media_info['stored_path'])
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Media file not found on disk")
            
            # Determine content type
            content_type = media_info['mime_type']
            
            # Return file
            return FileResponse(
                path=str(file_path),
                media_type=content_type,
                filename=media_info['original_filename']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to serve media file {media_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/media/{media_id}/thumbnail")
    async def get_media_thumbnail(media_id: str, size: int = 200):
        """
        Generate and serve a thumbnail for an image.
        """
        try:
            # Get media file info
            media_info = conversation_db._get_media_file_info(media_id)
            if not media_info:
                raise HTTPException(status_code=404, detail="Media file not found")
            
            if media_info['media_type'] != 'image':
                raise HTTPException(status_code=400, detail="Thumbnails only available for images")
            
            file_path = Path(media_info['stored_path'])
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Media file not found on disk")
            
            # Generate thumbnail
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((size, size), Image.Resampling.LANCZOS)
                
                # Save to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=85)
                img_bytes.seek(0)
                
                return StreamingResponse(
                    io.BytesIO(img_bytes.read()),
                    media_type="image/jpeg",
                    headers={"Cache-Control": "max-age=3600"}
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {media_id}: {e}")
            # Fallback to original image
            return await get_media_file(media_id)
    
    @app.get("/api/conversations/{conversation_id}/check-duplicate")
    async def check_conversation_duplicate(conversation_id: str):
        """
        Check if a conversation already exists and get its status.
        """
        try:
            exists = conversation_db.conversation_exists(conversation_id)
            checksum = conversation_db.get_conversation_checksum(conversation_id) if exists else None
            message_count = len(conversation_db.get_message_ids(conversation_id)) if exists else 0
            
            return {
                "exists": exists,
                "conversation_id": conversation_id,
                "checksum": checksum,
                "message_count": message_count
            }
            
        except Exception as e:
            logger.error(f"Failed to check duplicate for {conversation_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/stats/detailed")
    async def get_detailed_conversation_stats():
        """
        Get detailed statistics about conversations and media.
        """
        try:
            # This would need proper database queries
            # For now, return placeholder
            return {
                "conversations": {
                    "total": 0,
                    "by_source": {},
                    "recent_imports": []
                },
                "messages": {
                    "total": 0,
                    "by_role": {}
                },
                "media": {
                    "total_files": 0,
                    "by_type": {},
                    "total_size_bytes": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Add database helper method
def _add_database_helper_methods():
    """Add helper methods to ConversationDatabase class."""
    
    def _get_media_file_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get media file information by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT original_filename, stored_path, media_type, mime_type, file_size
            FROM media_files WHERE id = ?
        """, (media_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'original_filename': result[0],
                'stored_path': result[1],
                'media_type': result[2],
                'mime_type': result[3],
                'file_size': result[4]
            }
        return None
    
    # Monkey patch the method (not ideal, but works for now)
    ConversationDatabase._get_media_file_info = _get_media_file_info

# Apply the helper methods
_add_database_helper_methods()

# Standalone app for testing
if __name__ == "__main__":
    import uvicorn
    
    app = FastAPI(title="Enhanced Conversation API V2", version="2.0.0")
    add_enhanced_conversation_routes(app)
    
    @app.get("/")
    async def root():
        return {"message": "Enhanced Conversation API V2", "endpoints": "/docs"}
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8200)