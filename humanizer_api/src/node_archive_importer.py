"""
Node Archive Browser Importer
Reads conversation folders and imports them into the unified PostgreSQL archive
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
import re

from archive_unified_schema import (
    UnifiedArchiveDB, 
    ArchiveContent, 
    SourceType, 
    ContentType
)

logger = logging.getLogger(__name__)

@dataclass
class NodeConversationMessage:
    """Individual message from Node Archive Browser"""
    message_id: str
    author: str
    timestamp: datetime
    content: str
    raw_data: Dict[str, Any]
    reply_to: Optional[str] = None
    attachments: List[str] = None

@dataclass 
class NodeConversation:
    """Complete conversation from Node Archive Browser"""
    conversation_id: str
    title: str
    participants: List[str]
    messages: List[NodeConversationMessage]
    start_time: datetime
    end_time: datetime
    message_count: int
    raw_metadata: Dict[str, Any]

class NodeArchiveImporter:
    """Imports Node Archive Browser conversations into unified PostgreSQL database"""
    
    def __init__(self, archive_db: UnifiedArchiveDB, node_archive_path: str):
        self.archive_db = archive_db
        self.node_archive_path = Path(node_archive_path)
        self.imported_conversations = 0
        self.imported_messages = 0
        self.skipped_conversations = 0
        self.errors = []
        
    def discover_conversations(self) -> Generator[Path, None, None]:
        """Discover all conversation folders in the Node archive"""
        logger.info(f"Scanning Node archive at: {self.node_archive_path}")
        
        if not self.node_archive_path.exists():
            raise FileNotFoundError(f"Node archive path not found: {self.node_archive_path}")
        
        # Look for conversation folders - typically contain JSON files
        for item in self.node_archive_path.rglob("*"):
            if item.is_dir():
                # Check if this directory contains conversation files
                json_files = list(item.glob("*.json"))
                if json_files:
                    logger.debug(f"Found conversation folder: {item}")
                    yield item
    
    def parse_conversation_folder(self, folder_path: Path) -> Optional[NodeConversation]:
        """Parse a single conversation folder into structured data"""
        try:
            logger.debug(f"Parsing conversation folder: {folder_path}")
            
            # Find the main conversation file (usually conversation.json or similar)
            conversation_files = list(folder_path.glob("*.json"))
            
            if not conversation_files:
                logger.warning(f"No JSON files found in {folder_path}")
                return None
            
            # Try different common file patterns
            main_file = None
            for pattern in ["conversation.json", "messages.json", "chat.json"]:
                potential_file = folder_path / pattern
                if potential_file.exists():
                    main_file = potential_file
                    break
            
            # If no standard file, use the largest JSON file
            if not main_file:
                main_file = max(conversation_files, key=lambda f: f.stat().st_size)
            
            with open(main_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse based on common Node Archive Browser formats
            return self._parse_conversation_data(data, folder_path)
            
        except Exception as e:
            logger.error(f"Error parsing conversation folder {folder_path}: {e}")
            self.errors.append(f"Failed to parse {folder_path}: {e}")
            return None
    
    def _parse_conversation_data(self, data: Dict[str, Any], folder_path: Path) -> Optional[NodeConversation]:
        """Parse conversation data based on detected format"""
        
        # Format 1: Direct messages array
        if "messages" in data and isinstance(data["messages"], list):
            return self._parse_format_messages_array(data, folder_path)
        
        # Format 2: Conversation metadata with separate messages
        elif "conversation" in data and "messages" in data:
            return self._parse_format_conversation_messages(data, folder_path)
        
        # Format 3: Raw message list (array at root)
        elif isinstance(data, list):
            return self._parse_format_raw_array(data, folder_path)
        
        # Format 4: Single conversation object
        elif "participants" in data or "members" in data:
            return self._parse_format_conversation_object(data, folder_path)
        
        else:
            logger.warning(f"Unknown conversation format in {folder_path}")
            return self._parse_generic_format(data, folder_path)
    
    def _parse_format_messages_array(self, data: Dict[str, Any], folder_path: Path) -> NodeConversation:
        """Parse format with direct messages array"""
        messages_data = data["messages"]
        
        # Extract conversation metadata
        conversation_id = str(data.get("id", folder_path.name))
        title = data.get("title", data.get("name", folder_path.name))
        participants = self._extract_participants(data, messages_data)
        
        # Parse messages
        messages = []
        for i, msg_data in enumerate(messages_data):
            message = self._parse_message(msg_data, i)
            if message:
                messages.append(message)
        
        if not messages:
            return None
        
        return NodeConversation(
            conversation_id=conversation_id,
            title=title,
            participants=participants,
            messages=messages,
            start_time=min(msg.timestamp for msg in messages),
            end_time=max(msg.timestamp for msg in messages),
            message_count=len(messages),
            raw_metadata=data
        )
    
    def _parse_format_conversation_messages(self, data: Dict[str, Any], folder_path: Path) -> NodeConversation:
        """Parse format with separate conversation and messages sections"""
        conv_data = data["conversation"]
        messages_data = data["messages"]
        
        conversation_id = str(conv_data.get("id", folder_path.name))
        title = conv_data.get("title", conv_data.get("name", folder_path.name))
        participants = conv_data.get("participants", conv_data.get("members", []))
        
        messages = []
        for i, msg_data in enumerate(messages_data):
            message = self._parse_message(msg_data, i)
            if message:
                messages.append(message)
        
        if not messages:
            return None
        
        return NodeConversation(
            conversation_id=conversation_id,
            title=title,
            participants=participants,
            messages=messages,
            start_time=min(msg.timestamp for msg in messages),
            end_time=max(msg.timestamp for msg in messages),
            message_count=len(messages),
            raw_metadata=data
        )
    
    def _parse_format_raw_array(self, data: List[Dict[str, Any]], folder_path: Path) -> NodeConversation:
        """Parse format with raw message array at root"""
        conversation_id = folder_path.name
        title = folder_path.name
        
        messages = []
        for i, msg_data in enumerate(data):
            message = self._parse_message(msg_data, i)
            if message:
                messages.append(message)
        
        if not messages:
            return None
        
        participants = list(set(msg.author for msg in messages if msg.author))
        
        return NodeConversation(
            conversation_id=conversation_id,
            title=title,
            participants=participants,
            messages=messages,
            start_time=min(msg.timestamp for msg in messages),
            end_time=max(msg.timestamp for msg in messages),
            message_count=len(messages),
            raw_metadata={"messages": data}
        )
    
    def _parse_format_conversation_object(self, data: Dict[str, Any], folder_path: Path) -> NodeConversation:
        """Parse format with conversation as single object"""
        conversation_id = str(data.get("id", folder_path.name))
        title = data.get("title", data.get("name", folder_path.name))
        participants = data.get("participants", data.get("members", []))
        
        # Messages might be embedded or in separate field
        messages_data = data.get("messages", data.get("content", []))
        if not isinstance(messages_data, list):
            messages_data = []
        
        messages = []
        for i, msg_data in enumerate(messages_data):
            message = self._parse_message(msg_data, i)
            if message:
                messages.append(message)
        
        if not messages:
            return None
        
        return NodeConversation(
            conversation_id=conversation_id,
            title=title,
            participants=participants,
            messages=messages,
            start_time=min(msg.timestamp for msg in messages),
            end_time=max(msg.timestamp for msg in messages),
            message_count=len(messages),
            raw_metadata=data
        )
    
    def _parse_generic_format(self, data: Dict[str, Any], folder_path: Path) -> Optional[NodeConversation]:
        """Fallback parser for unknown formats"""
        logger.info(f"Attempting generic parse for {folder_path}")
        
        # Try to find any text content
        text_content = []
        self._extract_text_recursively(data, text_content)
        
        if not text_content:
            return None
        
        # Create synthetic messages from text content
        messages = []
        for i, text in enumerate(text_content):
            if len(text.strip()) > 10:  # Skip very short texts
                timestamp = datetime.now(timezone.utc)  # Synthetic timestamp
                message = NodeConversationMessage(
                    message_id=f"synthetic_{i}",
                    author="unknown",
                    timestamp=timestamp,
                    content=text,
                    raw_data={"synthetic": True, "index": i}
                )
                messages.append(message)
        
        if not messages:
            return None
        
        return NodeConversation(
            conversation_id=folder_path.name,
            title=f"Generic Import: {folder_path.name}",
            participants=["unknown"],
            messages=messages,
            start_time=messages[0].timestamp,
            end_time=messages[-1].timestamp,
            message_count=len(messages),
            raw_metadata=data
        )
    
    def _extract_text_recursively(self, obj: Any, text_list: List[str]):
        """Recursively extract text content from nested structures"""
        if isinstance(obj, str) and len(obj.strip()) > 10:
            text_list.append(obj.strip())
        elif isinstance(obj, dict):
            for value in obj.values():
                self._extract_text_recursively(value, text_list)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_text_recursively(item, text_list)
    
    def _parse_message(self, msg_data: Dict[str, Any], index: int) -> Optional[NodeConversationMessage]:
        """Parse individual message from various formats"""
        try:
            # Extract message ID
            message_id = str(msg_data.get("id", msg_data.get("message_id", f"msg_{index}")))
            
            # Extract author/sender
            author = (
                msg_data.get("author") or 
                msg_data.get("sender") or 
                msg_data.get("from") or 
                msg_data.get("user") or 
                "unknown"
            )
            
            # Extract content/text
            content = (
                msg_data.get("content") or
                msg_data.get("text") or
                msg_data.get("message") or
                msg_data.get("body") or
                ""
            )
            
            if not content or len(content.strip()) < 2:
                return None
            
            # Extract timestamp
            timestamp = self._parse_timestamp(
                msg_data.get("timestamp") or
                msg_data.get("time") or
                msg_data.get("created_at") or
                msg_data.get("date")
            )
            
            # Extract optional fields
            reply_to = msg_data.get("reply_to", msg_data.get("in_reply_to"))
            attachments = msg_data.get("attachments", [])
            
            return NodeConversationMessage(
                message_id=message_id,
                author=str(author),
                timestamp=timestamp,
                content=str(content),
                raw_data=msg_data,
                reply_to=str(reply_to) if reply_to else None,
                attachments=attachments if isinstance(attachments, list) else []
            )
            
        except Exception as e:
            logger.warning(f"Error parsing message at index {index}: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_data: Any) -> datetime:
        """Parse timestamp from various formats"""
        if not timestamp_data:
            return datetime.now(timezone.utc)
        
        # Unix timestamp (seconds)
        if isinstance(timestamp_data, (int, float)):
            # Handle milliseconds vs seconds
            if timestamp_data > 1e10:  # Likely milliseconds
                timestamp_data = timestamp_data / 1000
            return datetime.fromtimestamp(timestamp_data, tz=timezone.utc)
        
        # ISO string
        if isinstance(timestamp_data, str):
            # Try various ISO formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ", 
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]:
                try:
                    return datetime.strptime(timestamp_data, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        
        # Fallback to current time
        logger.warning(f"Could not parse timestamp: {timestamp_data}")
        return datetime.now(timezone.utc)
    
    def _extract_participants(self, conv_data: Dict[str, Any], messages_data: List[Dict[str, Any]]) -> List[str]:
        """Extract conversation participants"""
        participants = set()
        
        # From conversation metadata
        if "participants" in conv_data:
            participants.update(conv_data["participants"])
        if "members" in conv_data:
            participants.update(conv_data["members"])
        
        # From message authors
        for msg in messages_data:
            author = (
                msg.get("author") or 
                msg.get("sender") or 
                msg.get("from") or 
                msg.get("user")
            )
            if author:
                participants.add(str(author))
        
        return list(participants)
    
    def import_conversation(self, conversation: NodeConversation) -> bool:
        """Import a single conversation into the database"""
        try:
            # First, insert the conversation as a container
            conversation_content = ArchiveContent(
                source_type=SourceType.NODE_CONVERSATION,
                source_id=conversation.conversation_id,
                content_type=ContentType.CONVERSATION,
                title=conversation.title,
                body_text=f"Conversation with {len(conversation.participants)} participants, {conversation.message_count} messages",
                raw_content=conversation.raw_metadata,
                author=None,  # Conversation has multiple authors
                participants=conversation.participants,
                timestamp=conversation.start_time,
                source_metadata={
                    "start_time": conversation.start_time.isoformat(),
                    "end_time": conversation.end_time.isoformat(),
                    "message_count": conversation.message_count,
                    "duration_hours": (conversation.end_time - conversation.start_time).total_seconds() / 3600
                }
            )
            
            conversation_db_id = self.archive_db.insert_content(conversation_content)
            logger.debug(f"Inserted conversation {conversation.conversation_id} as DB ID {conversation_db_id}")
            
            # Then insert all messages with parent reference
            message_contents = []
            for message in conversation.messages:
                message_content = ArchiveContent(
                    source_type=SourceType.NODE_CONVERSATION,
                    source_id=f"{conversation.conversation_id}_{message.message_id}",
                    parent_id=conversation_db_id,
                    content_type=ContentType.MESSAGE,
                    title=None,
                    body_text=message.content,
                    raw_content=message.raw_data,
                    author=message.author,
                    participants=conversation.participants,
                    timestamp=message.timestamp,
                    source_metadata={
                        "conversation_id": conversation.conversation_id,
                        "message_id": message.message_id,
                        "reply_to": message.reply_to,
                        "attachments": message.attachments
                    }
                )
                message_contents.append(message_content)
            
            # Batch insert messages
            message_ids = self.archive_db.batch_insert_content(message_contents)
            logger.debug(f"Inserted {len(message_ids)} messages for conversation {conversation.conversation_id}")
            
            self.imported_conversations += 1
            self.imported_messages += len(message_contents)
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing conversation {conversation.conversation_id}: {e}")
            self.errors.append(f"Failed to import conversation {conversation.conversation_id}: {e}")
            return False
    
    def import_all_conversations(self, max_conversations: Optional[int] = None) -> Dict[str, Any]:
        """Import all discovered conversations"""
        logger.info("Starting Node Archive Browser import")
        
        conversation_folders = list(self.discover_conversations())
        logger.info(f"Found {len(conversation_folders)} potential conversation folders")
        
        if max_conversations:
            conversation_folders = conversation_folders[:max_conversations]
            logger.info(f"Limited to first {max_conversations} conversations")
        
        for i, folder_path in enumerate(conversation_folders):
            logger.info(f"Processing conversation {i+1}/{len(conversation_folders)}: {folder_path.name}")
            
            conversation = self.parse_conversation_folder(folder_path)
            if conversation:
                success = self.import_conversation(conversation)
                if not success:
                    self.skipped_conversations += 1
            else:
                self.skipped_conversations += 1
                logger.warning(f"Skipped conversation folder: {folder_path}")
        
        # Final statistics
        stats = {
            "total_folders_processed": len(conversation_folders),
            "conversations_imported": self.imported_conversations,
            "conversations_skipped": self.skipped_conversations,
            "messages_imported": self.imported_messages,
            "errors": self.errors
        }
        
        logger.info(f"Import completed: {stats}")
        return stats
    
    def import_single_conversation(self, conversation_file: Path) -> Optional[Dict[str, Any]]:
        """
        Import a single conversation file
        
        Args:
            conversation_file: Path to conversation.json file
            
        Returns:
            Import result with content_id if successful
        """
        try:
            logger.info(f"Importing single conversation: {conversation_file}")
            
            if not conversation_file.exists():
                logger.error(f"Conversation file not found: {conversation_file}")
                return None
            
            # Parse conversation folder (conversation_file should be folder/conversation.json)
            folder_path = conversation_file.parent
            conversation_data = self.parse_conversation_folder(folder_path)
            if not conversation_data:
                logger.warning(f"Failed to parse conversation: {conversation_file}")
                return None
            
            # Import into database  
            success = self.import_conversation(conversation_data)
            if not success:
                logger.error(f"Failed to import conversation to database: {conversation_file}")
                return None
            
            logger.info(f"✅ Successfully imported conversation {folder_path.name}")
            
            # Return the conversation DB ID (from the import_conversation method)
            # We need to extract this from the recent conversation import
            return {
                "content_id": self.imported_conversations,  # Placeholder - would need proper tracking
                "conversation_id": folder_path.name,
                "source_file": str(conversation_file),
                "message_count": len(conversation_data.messages) if conversation_data else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to import conversation {conversation_file}: {e}")
            return None

# CLI interface for running imports
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Import Node Archive Browser conversations")
    parser.add_argument("node_archive_path", help="Path to Node Archive Browser data")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--max-conversations", type=int, help="Maximum conversations to import (for testing)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        # Initialize database
        archive_db = UnifiedArchiveDB(args.database_url)
        archive_db.create_tables()
        
        # Run import
        importer = NodeArchiveImporter(archive_db, args.node_archive_path)
        stats = importer.import_all_conversations(max_conversations=args.max_conversations)
        
        print(f"\nImport Results:")
        print(f"Conversations imported: {stats['conversations_imported']}")
        print(f"Messages imported: {stats['messages_imported']}")
        print(f"Conversations skipped: {stats['conversations_skipped']}")
        
        if stats['errors']:
            print(f"\nErrors encountered:")
            for error in stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(stats['errors']) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more errors")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)