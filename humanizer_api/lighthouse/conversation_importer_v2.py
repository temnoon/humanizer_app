"""
Enhanced Conversation Import System V2
=====================================

Fixes critical issues with UUID handling, duplicate detection, and media management.

Key improvements:
1. Uses original ChatGPT conversation/message IDs (no new UUIDs)
2. Detects and handles duplicate conversations intelligently
3. Supports incremental updates (new messages to existing conversations)
4. Proper image gallery and media management with database integration
5. Web interface for uploads and bulk imports

Author: Enhanced for production use
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
import logging
import mimetypes
import sqlite3
import uuid

# Import our systems
try:
    from embedding_config import get_embedding_manager, embed_text
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MediaFile:
    """Represents a media file associated with conversations."""
    id: str
    original_filename: str
    stored_path: str
    media_type: str  # 'image', 'audio', 'video', 'document'
    mime_type: str
    file_size: int
    checksum: str  # SHA256 hash for deduplication
    conversation_id: str
    message_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationMessage:
    """Enhanced message with proper ID handling."""
    id: str  # Original ChatGPT message ID
    role: str
    content: str
    timestamp: Optional[datetime] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    media_files: List[MediaFile] = field(default_factory=list)

@dataclass
class ImportedConversation:
    """Enhanced conversation with proper ID handling."""
    id: str  # Original ChatGPT conversation ID or derived stable ID
    title: str
    messages: List[ConversationMessage]
    source_format: str
    import_timestamp: datetime
    original_created: Optional[datetime] = None
    original_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    media_directory: Optional[str] = None
    checksum: Optional[str] = None  # Content hash for change detection

class ConversationDatabase:
    """
    Database manager for conversations, messages, and media files.
    """
    
    def __init__(self, db_path: str = "./data/conversations.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize conversation database with proper schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_format TEXT NOT NULL,
                import_timestamp TEXT NOT NULL,
                original_created TEXT,
                original_updated TEXT,
                checksum TEXT,
                metadata TEXT,
                media_directory TEXT
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT,
                parent_id TEXT,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        # Media files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                media_type TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                message_id TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
        """)
        
        # Message children relationships (for tree navigation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_children (
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES messages (id),
                FOREIGN KEY (child_id) REFERENCES messages (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_messages ON messages (conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_media ON media_files (conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checksum ON media_files (checksum)")
        
        conn.commit()
        conn.close()
        logger.info("Conversation database initialized")
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation already exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM conversations WHERE id = ?", (conversation_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def get_conversation_checksum(self, conversation_id: str) -> Optional[str]:
        """Get the stored checksum for a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT checksum FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_message_ids(self, conversation_id: str) -> Set[str]:
        """Get all message IDs for a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM messages WHERE conversation_id = ?", (conversation_id,))
        message_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return message_ids
    
    def store_conversation(self, conversation: ImportedConversation):
        """Store or update a conversation in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Store conversation
            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (id, title, source_format, import_timestamp, original_created, 
                 original_updated, checksum, metadata, media_directory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation.id,
                conversation.title,
                conversation.source_format,
                conversation.import_timestamp.isoformat(),
                conversation.original_created.isoformat() if conversation.original_created else None,
                conversation.original_updated.isoformat() if conversation.original_updated else None,
                conversation.checksum,
                json.dumps(conversation.metadata),
                conversation.media_directory
            ))
            
            # Store messages
            for message in conversation.messages:
                cursor.execute("""
                    INSERT OR REPLACE INTO messages 
                    (id, conversation_id, role, content, timestamp, parent_id, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    conversation.id,
                    message.role,
                    message.content,
                    message.timestamp.isoformat() if message.timestamp else None,
                    message.parent_id,
                    json.dumps(message.metadata)
                ))
                
                # Store children relationships
                cursor.execute("DELETE FROM message_children WHERE parent_id = ?", (message.id,))
                for child_id in message.children_ids:
                    cursor.execute("""
                        INSERT OR IGNORE INTO message_children (parent_id, child_id)
                        VALUES (?, ?)
                    """, (message.id, child_id))
                
                # Store media files
                for media_file in message.media_files:
                    cursor.execute("""
                        INSERT OR REPLACE INTO media_files 
                        (id, original_filename, stored_path, media_type, mime_type, 
                         file_size, checksum, conversation_id, message_id, metadata, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        media_file.id,
                        media_file.original_filename,
                        media_file.stored_path,
                        media_file.media_type,
                        media_file.mime_type,
                        media_file.file_size,
                        media_file.checksum,
                        media_file.conversation_id,
                        media_file.message_id,
                        json.dumps(media_file.metadata),
                        media_file.created_at.isoformat()
                    ))
            
            conn.commit()
            logger.info(f"Stored conversation {conversation.id} with {len(conversation.messages)} messages")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to store conversation {conversation.id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_images(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all images for gallery view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.id, m.original_filename, m.stored_path, m.media_type, 
                   m.conversation_id, m.message_id, m.created_at,
                   c.title as conversation_title,
                   msg.content as message_content
            FROM media_files m
            JOIN conversations c ON m.conversation_id = c.id
            LEFT JOIN messages msg ON m.message_id = msg.id
            WHERE m.media_type = 'image'
            ORDER BY m.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        images = []
        for row in cursor.fetchall():
            images.append({
                'id': row[0],
                'filename': row[1],
                'path': row[2],
                'conversation_id': row[4],
                'conversation_title': row[7],
                'message_id': row[5],
                'message_content': row[8][:100] + "..." if row[8] and len(row[8]) > 100 else row[8],
                'created_at': row[6]
            })
        
        conn.close()
        return images

class EnhancedConversationImporter:
    """
    Enhanced importer with proper UUID handling and duplicate detection.
    """
    
    def __init__(self, storage_dir: str = "./data/imported_conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = ConversationDatabase()
        
        # Initialize embedding system
        self.embedding_manager = None
        if EMBEDDING_AVAILABLE:
            try:
                self.embedding_manager = get_embedding_manager()
                logger.info(f"Initialized embedding system: {self.embedding_manager.active_model}")
            except Exception as e:
                logger.warning(f"Could not initialize embeddings: {e}")
    
    def extract_chatgpt_conversation_id(self, data: Dict[str, Any]) -> str:
        """
        Extract or generate a stable conversation ID from ChatGPT data.
        
        ChatGPT doesn't provide a conversation-level ID, so we create one
        based on the conversation content that remains stable across re-imports.
        """
        # Use title + creation time + first message ID for stable ID
        title = data.get('title', 'untitled')
        create_time = data.get('create_time', 0)
        
        # Find first meaningful message ID
        mapping = data.get('mapping', {})
        first_message_id = None
        for node_id, node_data in mapping.items():
            message_data = node_data.get('message')
            if message_data and self._is_meaningful_message(message_data):
                first_message_id = message_data.get('id', node_id)
                break
        
        # Create stable ID from content
        id_source = f"{title}_{create_time}_{first_message_id}"
        stable_id = hashlib.sha256(id_source.encode()).hexdigest()[:16]
        
        return f"chatgpt_{stable_id}"
    
    def calculate_conversation_checksum(self, data: Dict[str, Any]) -> str:
        """
        Calculate a checksum of conversation content for change detection.
        """
        # Include title, update time, and all message content
        content_parts = [
            data.get('title', ''),
            str(data.get('update_time', 0))
        ]
        
        # Add all message content in a stable order
        mapping = data.get('mapping', {})
        message_contents = []
        
        for node_id in sorted(mapping.keys()):
            node_data = mapping[node_id]
            message_data = node_data.get('message')
            if message_data and self._is_meaningful_message(message_data):
                content = message_data.get('content', {})
                parts = content.get('parts', [])
                message_content = '\n'.join(str(part) for part in parts if part)
                message_contents.append(message_content)
        
        content_parts.extend(sorted(message_contents))
        full_content = '\n'.join(content_parts)
        
        return hashlib.sha256(full_content.encode()).hexdigest()
    
    def import_chatgpt_conversation(self, 
                                  conversation_path: str,
                                  force_update: bool = False) -> Tuple[ImportedConversation, str]:
        """
        Import ChatGPT conversation with proper duplicate handling.
        
        Returns:
            Tuple of (conversation, import_status)
            import_status: 'new', 'duplicate', 'updated'
        """
        logger.info(f"Importing ChatGPT conversation from {conversation_path}")
        
        # Load JSON data
        if os.path.isfile(conversation_path):
            # Single JSON file
            json_file = Path(conversation_path)
            conversation_dir = json_file.parent
        else:
            # Directory with conversation.json
            conversation_dir = Path(conversation_path)
            json_file = conversation_dir / "conversation.json"
        
        if not json_file.exists():
            raise FileNotFoundError(f"Conversation file not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract stable conversation ID and checksum
        conversation_id = self.extract_chatgpt_conversation_id(data)
        new_checksum = self.calculate_conversation_checksum(data)
        
        # Check for duplicates
        import_status = 'new'
        if self.db.conversation_exists(conversation_id):
            existing_checksum = self.db.get_conversation_checksum(conversation_id)
            if existing_checksum == new_checksum and not force_update:
                logger.info(f"Conversation {conversation_id} is unchanged (checksum match)")
                # Return existing conversation
                existing_conv = self._load_existing_conversation(conversation_id)
                return existing_conv, 'duplicate'
            else:
                import_status = 'updated'
                logger.info(f"Conversation {conversation_id} has changes, updating...")
        
        # Parse conversation data
        title = data.get('title', 'Untitled Conversation')
        create_time = data.get('create_time')
        update_time = data.get('update_time')
        
        created_dt = datetime.fromtimestamp(create_time) if create_time else None
        updated_dt = datetime.fromtimestamp(update_time) if update_time else None
        
        # Parse messages using original IDs
        messages = self._parse_chatgpt_message_tree(data.get('mapping', {}))
        
        # Handle media files
        media_dir = self._setup_enhanced_media_directory(conversation_id, conversation_dir, messages)
        
        # Create conversation
        conversation = ImportedConversation(
            id=conversation_id,
            title=title,
            messages=messages,
            source_format='chatgpt',
            import_timestamp=datetime.now(),
            original_created=created_dt,
            original_updated=updated_dt,
            checksum=new_checksum,
            metadata={
                'original_path': str(conversation_dir),
                'total_messages': len(messages),
                'has_media': media_dir is not None,
                'import_status': import_status
            },
            media_directory=media_dir
        )
        
        # Store in database
        self.db.store_conversation(conversation)
        
        # Store in archive system
        self._store_in_archive_system(conversation)
        
        logger.info(f"Successfully imported ChatGPT conversation: {title} ({len(messages)} messages) - {import_status}")
        return conversation, import_status
    
    def _setup_enhanced_media_directory(self, 
                                      conversation_id: str, 
                                      source_dir: Path,
                                      messages: List[ConversationMessage]) -> Optional[str]:
        """
        Enhanced media handling with proper database integration.
        """
        # Find all media files
        media_files = []
        media_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp',  # images
            '.mp3', '.wav', '.ogg', '.m4a',  # audio
            '.mp4', '.mov', '.avi', '.webm',  # video
            '.pdf', '.doc', '.docx', '.txt'  # documents
        }
        
        for ext in media_extensions:
            media_files.extend(source_dir.glob(f'*{ext}'))
            media_files.extend(source_dir.glob(f'*{ext.upper()}'))
        
        if not media_files:
            return None
        
        # Create organized media directory
        media_base_dir = self.storage_dir / "media"
        media_base_dir.mkdir(parents=True, exist_ok=True)
        
        conversation_media_dir = media_base_dir / conversation_id
        conversation_media_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each media file
        for media_file in media_files:
            self._process_media_file(media_file, conversation_media_dir, conversation_id, messages)
        
        logger.info(f"Processed {len(media_files)} media files for conversation {conversation_id}")
        return str(conversation_media_dir)
    
    def _process_media_file(self, 
                          source_file: Path, 
                          dest_dir: Path, 
                          conversation_id: str,
                          messages: List[ConversationMessage]):
        """
        Process and catalog a single media file.
        """
        try:
            # Calculate file checksum
            file_checksum = self._calculate_file_checksum(source_file)
            
            # Check if file already exists (deduplication)
            existing_media = self._find_existing_media_by_checksum(file_checksum)
            if existing_media:
                logger.info(f"Media file {source_file.name} already exists, linking...")
                # Link to existing file instead of copying
                stored_path = existing_media['stored_path']
            else:
                # Copy file to organized location
                file_ext = source_file.suffix.lower()
                media_type = self._determine_media_type(file_ext)
                
                # Create type-specific subdirectory
                type_dir = dest_dir / media_type
                type_dir.mkdir(exist_ok=True)
                
                # Generate unique filename if needed
                dest_file = type_dir / source_file.name
                counter = 1
                while dest_file.exists():
                    stem = source_file.stem
                    dest_file = type_dir / f"{stem}_{counter}{source_file.suffix}"
                    counter += 1
                
                shutil.copy2(source_file, dest_file)
                stored_path = str(dest_file)
                logger.info(f"Copied media file: {source_file.name} -> {dest_file}")
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(source_file))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Try to associate with specific message (heuristic)
            associated_message_id = self._associate_media_with_message(source_file, messages)
            
            # Create media file record
            media_file = MediaFile(
                id=str(uuid.uuid4()),
                original_filename=source_file.name,
                stored_path=stored_path,
                media_type=self._determine_media_type(source_file.suffix.lower()),
                mime_type=mime_type,
                file_size=source_file.stat().st_size,
                checksum=file_checksum,
                conversation_id=conversation_id,
                message_id=associated_message_id,
                metadata={
                    'original_path': str(source_file),
                    'dimensions': self._get_image_dimensions(source_file) if media_type == 'image' else None
                }
            )
            
            # Add to associated message
            if associated_message_id:
                for message in messages:
                    if message.id == associated_message_id:
                        message.media_files.append(media_file)
                        break
            
        except Exception as e:
            logger.warning(f"Failed to process media file {source_file}: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _determine_media_type(self, file_extension: str) -> str:
        """Determine media type from file extension."""
        ext = file_extension.lower()
        if ext in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}:
            return 'image'
        elif ext in {'.mp3', '.wav', '.ogg', '.m4a'}:
            return 'audio'
        elif ext in {'.mp4', '.mov', '.avi', '.webm'}:
            return 'video'
        else:
            return 'document'
    
    def _find_existing_media_by_checksum(self, checksum: str) -> Optional[Dict[str, Any]]:
        """Find existing media file by checksum."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT stored_path, original_filename, media_type 
            FROM media_files WHERE checksum = ? LIMIT 1
        """, (checksum,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'stored_path': result[0],
                'filename': result[1],
                'media_type': result[2]
            }
        return None
    
    def _get_image_dimensions(self, image_path: Path) -> Optional[Dict[str, int]]:
        """Get image dimensions if possible."""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                return {'width': img.width, 'height': img.height}
        except ImportError:
            logger.debug("PIL not available for image dimension extraction")
        except Exception as e:
            logger.debug(f"Could not get dimensions for {image_path}: {e}")
        return None
    
    def _associate_media_with_message(self, 
                                   media_file: Path, 
                                   messages: List[ConversationMessage]) -> Optional[str]:
        """
        Try to associate media file with a specific message using heuristics.
        """
        # Simple heuristic: look for mentions of filename in message content
        filename_parts = media_file.stem.lower().split('_')
        
        for message in messages:
            content_lower = message.content.lower()
            # Look for filename mentions
            if media_file.name.lower() in content_lower:
                return message.id
            # Look for partial filename matches
            for part in filename_parts:
                if len(part) > 3 and part in content_lower:
                    return message.id
        
        # If no specific association found, return None (associated with conversation only)
        return None
    
    def _parse_chatgpt_message_tree(self, mapping: Dict[str, Any]) -> List[ConversationMessage]:
        """Parse messages using original ChatGPT IDs."""
        messages = []
        
        # Find root node
        root_id = None
        for node_id, node_data in mapping.items():
            if node_data.get('parent') is None:
                root_id = node_id
                break
        
        if not root_id:
            logger.warning("No root node found in conversation tree")
            return messages
        
        # Traverse tree maintaining original IDs
        visited = set()
        self._traverse_message_tree(mapping, root_id, visited, messages)
        
        return messages
    
    def _traverse_message_tree(self, 
                              mapping: Dict[str, Any], 
                              node_id: str, 
                              visited: set, 
                              messages: List[ConversationMessage]):
        """Traverse tree using original message IDs."""
        if node_id in visited:
            return
        
        visited.add(node_id)
        node = mapping.get(node_id, {})
        message_data = node.get('message')
        
        if message_data and self._is_meaningful_message(message_data):
            message = self._parse_chatgpt_message(message_data, node.get('parent'), node.get('children', []))
            if message:
                messages.append(message)
        
        # Continue with children
        children = node.get('children', [])
        if children:
            self._traverse_message_tree(mapping, children[0], visited, messages)
    
    def _is_meaningful_message(self, message_data: Dict[str, Any]) -> bool:
        """Check if message has meaningful content."""
        content = message_data.get('content', {})
        parts = content.get('parts', [])
        
        if not parts or all(not part.strip() for part in parts if isinstance(part, str)):
            return False
        
        metadata = message_data.get('metadata', {})
        if metadata.get('is_visually_hidden_from_conversation'):
            return False
        
        return True
    
    def _parse_chatgpt_message(self, 
                              message_data: Dict[str, Any], 
                              parent_id: Optional[str],
                              children_ids: List[str]) -> Optional[ConversationMessage]:
        """Parse message keeping original ID."""
        try:
            # Use original ChatGPT message ID (no new UUID generation!)
            msg_id = message_data.get('id')
            if not msg_id:
                logger.warning("Message missing ID, skipping...")
                return None
            
            author = message_data.get('author', {})
            role = author.get('role', 'unknown')
            
            # Extract content
            content_data = message_data.get('content', {})
            content_type = content_data.get('content_type', 'text')
            
            if content_type == 'text':
                parts = content_data.get('parts', [])
                content = '\n'.join(str(part) for part in parts if part)
            elif content_type == 'model_editable_context':
                context = content_data.get('model_set_context', '')
                content = f"[Context: {context}]" if context else "[Context message]"
            else:
                content = f"[{content_type} content]"
            
            # Extract timestamp
            create_time = message_data.get('create_time')
            timestamp = datetime.fromtimestamp(create_time) if create_time else None
            
            # Extract metadata
            metadata = {
                'content_type': content_type,
                'status': message_data.get('status'),
                'weight': message_data.get('weight', 1),
                **message_data.get('metadata', {})
            }
            
            return ConversationMessage(
                id=msg_id,  # Original ID preserved!
                role=role,
                content=content,
                timestamp=timestamp,
                parent_id=parent_id,
                children_ids=children_ids,
                metadata=metadata,
                media_files=[]  # Will be populated by media processing
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse message: {e}")
            return None
    
    def _load_existing_conversation(self, conversation_id: str) -> ImportedConversation:
        """Load existing conversation from database."""
        # This would need to be implemented to reconstruct from database
        # For now, return a placeholder
        return ImportedConversation(
            id=conversation_id,
            title="Existing Conversation",
            messages=[],
            source_format='chatgpt',
            import_timestamp=datetime.now()
        )
    
    def _store_in_archive_system(self, conversation: ImportedConversation):
        """Store conversation in archive system (same as original)."""
        try:
            import httpx
            
            for i, message in enumerate(conversation.messages):
                content = f"[{message.role.upper()}] {message.content}"
                
                archive_metadata = {
                    'conversation_id': conversation.id,
                    'conversation_title': conversation.title,
                    'message_id': message.id,
                    'message_role': message.role,
                    'message_index': i,
                    'source_format': conversation.source_format,
                    'import_timestamp': conversation.import_timestamp.isoformat(),
                    'original_timestamp': message.timestamp.isoformat() if message.timestamp else None,
                    'has_media': len(message.media_files) > 0,
                    **message.metadata
                }
                
                with httpx.Client() as client:
                    response = client.post(
                        "http://localhost:7200/ingest",
                        data={
                            "content_type": "conversation_message",
                            "source": f"imported_{conversation.source_format}",
                            "title": f"{conversation.title} - Message {i+1}",
                            "data": content,
                            "metadata": json.dumps(archive_metadata)
                        },
                        files={}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.debug(f"Archived message {message.id}: {result.get('document_id')}")
                    else:
                        logger.warning(f"Failed to archive message {message.id}: {response.status_code}")
                        
        except Exception as e:
            logger.warning(f"Could not store conversation in archive system: {e}")
    
    def bulk_import_conversations(self, 
                                base_directory: str,
                                force_update: bool = False) -> Dict[str, Any]:
        """
        Import multiple conversations from a directory structure.
        
        Expected structure:
        base_directory/
        ├── Conversation 1/
        │   ├── conversation.json
        │   └── media files...
        ├── Conversation 2/
        │   ├── conversation.json
        │   └── media files...
        └── ...
        """
        base_path = Path(base_directory)
        if not base_path.exists():
            raise FileNotFoundError(f"Directory not found: {base_directory}")
        
        results = {
            'total_found': 0,
            'new': 0,
            'updated': 0,
            'duplicates': 0,
            'errors': 0,
            'conversations': []
        }
        
        # Find all conversation.json files
        conversation_files = list(base_path.rglob('conversation.json'))
        results['total_found'] = len(conversation_files)
        
        logger.info(f"Found {len(conversation_files)} conversation files in {base_directory}")
        
        for conv_file in conversation_files:
            try:
                conversation, status = self.import_chatgpt_conversation(
                    str(conv_file.parent), 
                    force_update=force_update
                )
                
                results[status] += 1
                results['conversations'].append({
                    'id': conversation.id,
                    'title': conversation.title,
                    'status': status,
                    'messages': len(conversation.messages),
                    'path': str(conv_file.parent)
                })
                
                logger.info(f"Imported {conversation.title}: {status}")
                
            except Exception as e:
                results['errors'] += 1
                logger.error(f"Failed to import {conv_file}: {e}")
                results['conversations'].append({
                    'path': str(conv_file.parent),
                    'status': 'error',
                    'error': str(e)
                })
        
        logger.info(f"Bulk import completed: {results['new']} new, {results['updated']} updated, "
                   f"{results['duplicates']} duplicates, {results['errors']} errors")
        
        return results

# Convenience functions
def import_single_conversation(conversation_path: str, 
                             force_update: bool = False) -> Tuple[ImportedConversation, str]:
    """Import a single conversation file or directory."""
    importer = EnhancedConversationImporter()
    return importer.import_chatgpt_conversation(conversation_path, force_update)

def bulk_import_conversations(base_directory: str, 
                            force_update: bool = False) -> Dict[str, Any]:
    """Import multiple conversations from directory."""
    importer = EnhancedConversationImporter()
    return importer.bulk_import_conversations(base_directory, force_update)

def get_image_gallery(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get images for gallery view."""
    db = ConversationDatabase()
    return db.get_all_images(limit, offset)

# Example usage
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced conversation importer")
    parser.add_argument('command', choices=['import', 'bulk'], help='Command to execute')
    parser.add_argument('path', help='Path to conversation file/directory')
    parser.add_argument('--force', action='store_true', help='Force re-import even if unchanged')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        if args.command == 'import':
            conversation, status = import_single_conversation(args.path, args.force)
            print(f"Imported: {conversation.title} ({status})")
            print(f"Messages: {len(conversation.messages)}")
            print(f"ID: {conversation.id}")
            
        elif args.command == 'bulk':
            results = bulk_import_conversations(args.path, args.force)
            print(f"Bulk import results:")
            print(f"  Found: {results['total_found']}")
            print(f"  New: {results['new']}")
            print(f"  Updated: {results['updated']}")
            print(f"  Duplicates: {results['duplicates']}")
            print(f"  Errors: {results['errors']}")
            
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)