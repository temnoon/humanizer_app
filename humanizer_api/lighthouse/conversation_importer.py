"""
Conversation Import System
=========================

Import and parse conversations from various sources including:
1. ChatGPT conversation downloads (conversation.json + media files)
2. Other chat exports and conversation formats
3. Handle images, audio, and other media attachments

Integrates with the archive system for storage and retrieval.

Author: Enhanced for comprehensive conversation handling
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import mimetypes
import hashlib
import uuid

# Import our systems
try:
    from embedding_config import get_embedding_manager, embed_text
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[datetime] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    metadata: Dict[str, Any] = None
    media_files: List[str] = None  # Paths to associated media
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.metadata is None:
            self.metadata = {}
        if self.media_files is None:
            self.media_files = []

@dataclass
class ImportedConversation:
    """Represents a complete imported conversation."""
    id: str
    title: str
    messages: List[ConversationMessage]
    source_format: str  # 'chatgpt', 'claude', etc.
    import_timestamp: datetime
    original_created: Optional[datetime] = None
    original_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    media_directory: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ConversationImporter:
    """
    Main class for importing conversations from various formats.
    """
    
    def __init__(self, storage_dir: str = "./data/imported_conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding system if available
        self.embedding_manager = None
        if EMBEDDING_AVAILABLE:
            try:
                self.embedding_manager = get_embedding_manager()
                logger.info(f"Initialized embedding system: {self.embedding_manager.active_model}")
            except Exception as e:
                logger.warning(f"Could not initialize embeddings: {e}")
    
    def import_chatgpt_conversation(self, 
                                  conversation_dir: str,
                                  conversation_file: str = "conversation.json") -> ImportedConversation:
        """
        Import a ChatGPT conversation from downloaded files.
        
        Args:
            conversation_dir: Directory containing conversation.json and media files
            conversation_file: Name of the JSON file (default: conversation.json)
            
        Returns:
            ImportedConversation object
        """
        logger.info(f"Importing ChatGPT conversation from {conversation_dir}")
        
        conversation_path = Path(conversation_dir)
        json_file = conversation_path / conversation_file
        
        if not json_file.exists():
            raise FileNotFoundError(f"Conversation file not found: {json_file}")
        
        # Load and parse JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract metadata
        title = data.get('title', 'Untitled Conversation')
        create_time = data.get('create_time')
        update_time = data.get('update_time')
        
        # Convert timestamps
        created_dt = datetime.fromtimestamp(create_time) if create_time else None
        updated_dt = datetime.fromtimestamp(update_time) if update_time else None
        
        # Parse message tree
        messages = self._parse_chatgpt_message_tree(data.get('mapping', {}))
        
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Handle media files
        media_dir = self._setup_media_directory(conversation_id, conversation_path)
        
        conversation = ImportedConversation(
            id=conversation_id,
            title=title,
            messages=messages,
            source_format='chatgpt',
            import_timestamp=datetime.now(),
            original_created=created_dt,
            original_updated=updated_dt,
            metadata={
                'original_path': str(conversation_path),
                'total_messages': len(messages),
                'has_media': media_dir is not None
            },
            media_directory=media_dir
        )
        
        # Store conversation
        self._store_conversation(conversation)
        
        logger.info(f"Successfully imported ChatGPT conversation: {title} ({len(messages)} messages)")
        return conversation
    
    def _parse_chatgpt_message_tree(self, mapping: Dict[str, Any]) -> List[ConversationMessage]:
        """
        Parse ChatGPT's tree-based message structure into a linear conversation.
        
        ChatGPT uses a tree structure where messages can have multiple children
        (representing different conversation branches). We'll extract the main path.
        """
        messages = []
        
        # Find root node (node with parent=None)
        root_id = None
        for node_id, node_data in mapping.items():
            if node_data.get('parent') is None:
                root_id = node_id
                break
        
        if not root_id:
            logger.warning("No root node found in conversation tree")
            return messages
        
        # Traverse the tree depth-first, following the main conversation path
        visited = set()
        self._traverse_message_tree(mapping, root_id, visited, messages)
        
        return messages
    
    def _traverse_message_tree(self, 
                              mapping: Dict[str, Any], 
                              node_id: str, 
                              visited: set, 
                              messages: List[ConversationMessage]):
        """
        Recursively traverse the message tree and extract messages.
        """
        if node_id in visited:
            return
        
        visited.add(node_id)
        node = mapping.get(node_id, {})
        message_data = node.get('message')
        
        # Skip empty or system messages that are just structural
        if message_data and self._is_meaningful_message(message_data):
            message = self._parse_chatgpt_message(message_data, node.get('parent'), node.get('children', []))
            if message:
                messages.append(message)
        
        # Continue with children (take first child for main conversation path)
        children = node.get('children', [])
        if children:
            # For now, follow the first child (main conversation path)
            # TODO: In the future, we could handle branching conversations
            self._traverse_message_tree(mapping, children[0], visited, messages)
    
    def _is_meaningful_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Check if a message contains meaningful content (not just system/structural).
        """
        content = message_data.get('content', {})
        parts = content.get('parts', [])
        
        # Skip empty messages
        if not parts or all(not part.strip() for part in parts if isinstance(part, str)):
            return False
        
        # Skip hidden system messages
        metadata = message_data.get('metadata', {})
        if metadata.get('is_visually_hidden_from_conversation'):
            return False
        
        return True
    
    def _parse_chatgpt_message(self, 
                              message_data: Dict[str, Any], 
                              parent_id: Optional[str],
                              children_ids: List[str]) -> Optional[ConversationMessage]:
        """
        Parse a single ChatGPT message into our format.
        """
        try:
            # Extract basic info
            msg_id = message_data.get('id', str(uuid.uuid4()))
            author = message_data.get('author', {})
            role = author.get('role', 'unknown')
            
            # Extract content
            content_data = message_data.get('content', {})
            content_type = content_data.get('content_type', 'text')
            
            # Handle different content types
            if content_type == 'text':
                parts = content_data.get('parts', [])
                content = '\n'.join(str(part) for part in parts if part)
            elif content_type == 'model_editable_context':
                # This is a special ChatGPT context message
                context = content_data.get('model_set_context', '')
                content = f"[Context: {context}]" if context else "[Context message]"
            else:
                content = f"[{content_type} content]"
            
            # Extract timestamp
            create_time = message_data.get('create_time')
            timestamp = datetime.fromtimestamp(create_time) if create_time else None
            
            # Extract metadata
            metadata = {
                'original_id': msg_id,
                'content_type': content_type,
                'status': message_data.get('status'),
                'weight': message_data.get('weight', 1),
                **message_data.get('metadata', {})
            }
            
            return ConversationMessage(
                id=msg_id,
                role=role,
                content=content,
                timestamp=timestamp,
                parent_id=parent_id,
                children_ids=children_ids,
                metadata=metadata
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse message: {e}")
            return None
    
    def _setup_media_directory(self, 
                              conversation_id: str, 
                              source_dir: Path) -> Optional[str]:
        """
        Set up media directory and copy media files if they exist.
        """
        # Look for media files in source directory
        media_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.mp3', '.wav', '.mp4', '.mov']:
            media_files.extend(source_dir.glob(f'*{ext}'))
            media_files.extend(source_dir.glob(f'*{ext.upper()}'))
        
        if not media_files:
            return None
        
        # Create media directory
        media_dir = self.storage_dir / conversation_id / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy media files
        for media_file in media_files:
            dest_file = media_dir / media_file.name
            shutil.copy2(media_file, dest_file)
            logger.info(f"Copied media file: {media_file.name}")
        
        return str(media_dir)
    
    def _store_conversation(self, conversation: ImportedConversation):
        """
        Store conversation to disk and optionally to archive system.
        """
        # Create conversation directory
        conv_dir = self.storage_dir / conversation.id
        conv_dir.mkdir(parents=True, exist_ok=True)
        
        # Save conversation metadata
        metadata_file = conv_dir / "metadata.json"
        metadata = {
            'id': conversation.id,
            'title': conversation.title,
            'source_format': conversation.source_format,
            'import_timestamp': conversation.import_timestamp.isoformat(),
            'original_created': conversation.original_created.isoformat() if conversation.original_created else None,
            'original_updated': conversation.original_updated.isoformat() if conversation.original_updated else None,
            'total_messages': len(conversation.messages),
            'metadata': conversation.metadata,
            'media_directory': conversation.media_directory
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Save messages
        messages_file = conv_dir / "messages.json"
        messages_data = []
        
        for msg in conversation.messages:
            msg_data = {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                'parent_id': msg.parent_id,
                'children_ids': msg.children_ids,
                'metadata': msg.metadata,
                'media_files': msg.media_files
            }
            messages_data.append(msg_data)
        
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, indent=2, ensure_ascii=False)
        
        # Generate embeddings and store in archive system
        self._store_in_archive_system(conversation)
        
        logger.info(f"Stored conversation: {conversation.id}")
    
    def _store_in_archive_system(self, conversation: ImportedConversation):
        """
        Store conversation messages in the archive system for search and retrieval.
        """
        try:
            import httpx
            
            for i, message in enumerate(conversation.messages):
                # Create content for archiving
                content = f"[{message.role.upper()}] {message.content}"
                
                # Prepare metadata
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
                
                # Store in archive via API
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
                        files={}  # Required for multipart
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.debug(f"Archived message {message.id}: {result.get('document_id')}")
                    else:
                        logger.warning(f"Failed to archive message {message.id}: {response.status_code}")
                        
        except Exception as e:
            logger.warning(f"Could not store conversation in archive system: {e}")
    
    def list_imported_conversations(self) -> List[Dict[str, Any]]:
        """
        List all imported conversations with metadata.
        """
        conversations = []
        
        for conv_dir in self.storage_dir.iterdir():
            if not conv_dir.is_dir():
                continue
                
            metadata_file = conv_dir / "metadata.json"
            if not metadata_file.exists():
                continue
                
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                conversations.append(metadata)
            except Exception as e:
                logger.warning(f"Could not load metadata for {conv_dir.name}: {e}")
        
        # Sort by import timestamp (newest first)
        conversations.sort(key=lambda x: x.get('import_timestamp', ''), reverse=True)
        return conversations
    
    def load_conversation(self, conversation_id: str) -> Optional[ImportedConversation]:
        """
        Load a previously imported conversation.
        """
        conv_dir = self.storage_dir / conversation_id
        if not conv_dir.exists():
            return None
        
        try:
            # Load metadata
            with open(conv_dir / "metadata.json", 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load messages
            with open(conv_dir / "messages.json", 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            # Reconstruct messages
            messages = []
            for msg_data in messages_data:
                timestamp = None
                if msg_data['timestamp']:
                    timestamp = datetime.fromisoformat(msg_data['timestamp'])
                
                message = ConversationMessage(
                    id=msg_data['id'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=timestamp,
                    parent_id=msg_data['parent_id'],
                    children_ids=msg_data['children_ids'],
                    metadata=msg_data['metadata'],
                    media_files=msg_data['media_files']
                )
                messages.append(message)
            
            # Reconstruct conversation
            original_created = None
            original_updated = None
            if metadata['original_created']:
                original_created = datetime.fromisoformat(metadata['original_created'])
            if metadata['original_updated']:
                original_updated = datetime.fromisoformat(metadata['original_updated'])
            
            conversation = ImportedConversation(
                id=metadata['id'],
                title=metadata['title'],
                messages=messages,
                source_format=metadata['source_format'],
                import_timestamp=datetime.fromisoformat(metadata['import_timestamp']),
                original_created=original_created,
                original_updated=original_updated,
                metadata=metadata['metadata'],
                media_directory=metadata['media_directory']
            )
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return None
    
    def search_conversations(self, 
                           query: str, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversations using the archive system.
        """
        try:
            import httpx
            
            with httpx.Client() as client:
                response = client.post(
                    "http://localhost:7200/search",
                    json={
                        "query": query,
                        "limit": limit,
                        "filters": {
                            "content_type": "conversation_message"
                        }
                    }
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    
                    # Group results by conversation
                    conversations = {}
                    for result in results:
                        metadata = result.get('metadata', {})
                        conv_id = metadata.get('conversation_id')
                        if conv_id:
                            if conv_id not in conversations:
                                conversations[conv_id] = {
                                    'conversation_id': conv_id,
                                    'title': metadata.get('conversation_title', 'Unknown'),
                                    'source_format': metadata.get('source_format', 'unknown'),
                                    'matches': []
                                }
                            
                            conversations[conv_id]['matches'].append({
                                'content': result.get('content', ''),
                                'score': result.get('score', 0),
                                'message_role': metadata.get('message_role', 'unknown'),
                                'message_index': metadata.get('message_index', 0)
                            })
                    
                    return list(conversations.values())
                else:
                    logger.warning(f"Search failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []

# Utility functions for easy access

def import_chatgpt_conversation(conversation_dir: str) -> ImportedConversation:
    """
    Convenience function to import a ChatGPT conversation.
    """
    importer = ConversationImporter()
    return importer.import_chatgpt_conversation(conversation_dir)

def list_conversations() -> List[Dict[str, Any]]:
    """
    Convenience function to list all imported conversations.
    """
    importer = ConversationImporter()
    return importer.list_imported_conversations()

def search_conversations(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to search conversations.
    """
    importer = ConversationImporter()
    return importer.search_conversations(query, limit)

# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python conversation_importer.py <conversation_directory>")
        sys.exit(1)
    
    conversation_dir = sys.argv[1]
    
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Import conversation
        importer = ConversationImporter()
        conversation = importer.import_chatgpt_conversation(conversation_dir)
        
        print(f"Successfully imported: {conversation.title}")
        print(f"Messages: {len(conversation.messages)}")
        print(f"Created: {conversation.original_created}")
        print(f"Media directory: {conversation.media_directory}")
        
        # Show first few messages
        print("\nFirst few messages:")
        for i, msg in enumerate(conversation.messages[:3]):
            print(f"{i+1}. [{msg.role}] {msg.content[:100]}...")
        
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)