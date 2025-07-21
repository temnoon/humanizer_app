#!/usr/bin/env python3
"""
Proper Node Archive Browser Importer
Reads conversation.json files and imports conversations with their messages correctly
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import asyncpg

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NodeArchiveBrowserImporter:
    """Proper Node Archive Browser importer following NAB structure"""
    
    def __init__(self, archive_path: str, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.archive_path = Path(archive_path)
        self.database_url = database_url
        self.stats = {
            "conversations_processed": 0,
            "messages_processed": 0,
            "conversations_failed": 0,
            "messages_failed": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    async def close_database(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            await self.conn.close()
            logger.info("📝 Database connection closed")
    
    def find_conversation_folders(self) -> List[Path]:
        """Find all conversation folders with conversation.json files"""
        conversation_folders = []
        
        if not self.archive_path.exists():
            logger.error(f"Archive path does not exist: {self.archive_path}")
            return []
        
        # Look for conversation folders (each should have conversation.json)
        for item in self.archive_path.iterdir():
            if item.is_dir():
                conversation_json = item / "conversation.json"
                if conversation_json.exists():
                    conversation_folders.append(item)
        
        logger.info(f"Found {len(conversation_folders)} conversation folders")
        return conversation_folders
    
    def parse_conversation_metadata(self, conversation_data: dict, folder_name: str) -> dict:
        """Extract conversation metadata"""
        return {
            "conversation_id": conversation_data.get("id", folder_name),
            "title": conversation_data.get("title", "Untitled"),
            "create_time": conversation_data.get("create_time"),
            "update_time": conversation_data.get("update_time"), 
            "folder_name": folder_name,
            "message_count": len(conversation_data.get("mapping", {}))
        }
    
    async def load_message_content(self, message_obj: dict, conversation_folder: Path) -> Optional[dict]:
        """Load message content, handling both inline and referenced messages"""
        message = message_obj.get("message")
        if not message:
            return None
        
        # Check if this is a message reference
        if "_reference" in message and message["_reference"].startswith("messages/"):
            # Load the referenced message file
            ref_path = conversation_folder / message["_reference"]
            if ref_path.exists():
                try:
                    with open(ref_path, 'r', encoding='utf-8') as f:
                        referenced_message = json.load(f)
                    return referenced_message
                except Exception as e:
                    logger.warning(f"Failed to load referenced message {ref_path}: {e}")
                    return None
            else:
                logger.warning(f"Referenced message file not found: {ref_path}")
                return None
        else:
            # Message content is inline
            return message
    
    def extract_message_text(self, message: dict) -> str:
        """Extract text content from a message"""
        if not message:
            return ""
        
        text_parts = []
        
        # Check content.parts for text
        content = message.get("content", {})
        if isinstance(content, dict):
            parts = content.get("parts", [])
            if isinstance(parts, list):
                for part in parts:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
        
        return "\n".join(text_parts).strip()
    
    def extract_message_metadata(self, message: dict) -> dict:
        """Extract metadata from a message"""
        if not message:
            return {}
        
        metadata = {}
        
        # Author information
        author = message.get("author", {})
        if isinstance(author, dict):
            metadata["role"] = author.get("role", "unknown")
            metadata["name"] = author.get("name")
        
        # Timestamps
        metadata["create_time"] = message.get("create_time")
        metadata["update_time"] = message.get("update_time")
        
        # Model information
        message_metadata = message.get("metadata", {})
        if isinstance(message_metadata, dict):
            metadata["model_slug"] = message_metadata.get("model_slug")
            metadata["gizmo_id"] = message_metadata.get("gizmo_id")
        
        return metadata
    
    async def import_conversation(self, conversation_folder: Path) -> bool:
        """Import a single conversation with all its messages"""
        try:
            # Load conversation.json
            conversation_json_path = conversation_folder / "conversation.json"
            with open(conversation_json_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            # Extract conversation metadata  
            conv_metadata = self.parse_conversation_metadata(conversation_data, conversation_folder.name)
            
            # Convert timestamps to datetime objects
            create_time = None
            update_time = None
            
            if conv_metadata["create_time"]:
                create_time = datetime.fromtimestamp(conv_metadata["create_time"], tz=timezone.utc)
            if conv_metadata["update_time"]:
                update_time = datetime.fromtimestamp(conv_metadata["update_time"], tz=timezone.utc)
            
            # Insert conversation record
            conversation_db_id = await self.conn.fetchval("""
                INSERT INTO archived_content 
                (source_type, source_id, content_type, title, author, timestamp, 
                 source_metadata, word_count, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """, 
                "node_conversation",  # source_type
                conv_metadata["conversation_id"],  # source_id
                "conversation",  # content_type
                conv_metadata["title"],  # title
                "unknown",  # author (conversations don't have single authors)
                create_time,  # timestamp
                json.dumps(conv_metadata),  # source_metadata
                0,  # word_count (conversations themselves don't have word count)
                datetime.now(timezone.utc),  # created_at
                datetime.now(timezone.utc)   # updated_at
            )
            
            logger.info(f"📁 Imported conversation: {conv_metadata['title']} (ID: {conversation_db_id})")
            
            # Process messages in the conversation
            mapping = conversation_data.get("mapping", {})
            message_count = 0
            
            for message_id, message_obj in mapping.items():
                try:
                    # Load message content (inline or referenced)
                    message_content = await self.load_message_content(message_obj, conversation_folder)
                    
                    if not message_content:
                        continue
                    
                    # Extract message text and metadata
                    message_text = self.extract_message_text(message_content)
                    message_metadata = self.extract_message_metadata(message_content)
                    
                    # Skip empty messages
                    if not message_text.strip():
                        continue
                    
                    # Convert message timestamps
                    msg_create_time = None
                    if message_metadata.get("create_time"):
                        msg_create_time = datetime.fromtimestamp(message_metadata["create_time"], tz=timezone.utc)
                    
                    # Insert message record
                    await self.conn.execute("""
                        INSERT INTO archived_content 
                        (source_type, source_id, parent_id, content_type, body_text, author, 
                         timestamp, source_metadata, word_count, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                        "node_conversation",  # source_type
                        message_id,  # source_id
                        conversation_db_id,  # parent_id (links to conversation)
                        "message",  # content_type
                        message_text,  # body_text
                        message_metadata.get("role", "unknown"),  # author
                        msg_create_time or create_time,  # timestamp (message time or conversation time)
                        json.dumps(message_metadata),  # source_metadata
                        len(message_text.split()) if message_text else 0,  # word_count
                        datetime.now(timezone.utc),  # created_at
                        datetime.now(timezone.utc)   # updated_at
                    )
                    
                    message_count += 1
                    self.stats["messages_processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import message {message_id}: {e}")
                    self.stats["messages_failed"] += 1
                    continue
            
            logger.info(f"  📝 Imported {message_count} messages")
            self.stats["conversations_processed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to import conversation {conversation_folder.name}: {e}")
            self.stats["conversations_failed"] += 1
            return False
    
    async def import_all_conversations(self, max_conversations: Optional[int] = None) -> dict:
        """Import all conversations from the archive"""
        self.stats["start_time"] = datetime.now()
        
        # Find all conversation folders
        conversation_folders = self.find_conversation_folders()
        
        if max_conversations:
            conversation_folders = conversation_folders[:max_conversations]
            logger.info(f"Limiting to {max_conversations} conversations")
        
        # Import each conversation
        for i, folder in enumerate(conversation_folders, 1):
            logger.info(f"Processing conversation {i}/{len(conversation_folders)}: {folder.name}")
            
            success = await self.import_conversation(folder)
            
            # Progress update every 50 conversations
            if i % 50 == 0:
                elapsed = datetime.now() - self.stats["start_time"]
                logger.info(f"📈 Progress: {i}/{len(conversation_folders)} conversations, "
                           f"{self.stats['messages_processed']} messages, "
                           f"elapsed: {elapsed}")
        
        self.stats["end_time"] = datetime.now()
        self.stats["duration"] = self.stats["end_time"] - self.stats["start_time"]
        
        return self.stats
    
    def print_summary(self):
        """Print import summary"""
        logger.info("\n" + "="*60)
        logger.info("🎯 NODE ARCHIVE BROWSER IMPORT COMPLETE")
        logger.info("="*60)
        logger.info(f"✅ Conversations imported: {self.stats['conversations_processed']}")
        logger.info(f"✅ Messages imported: {self.stats['messages_processed']}")
        logger.info(f"❌ Conversations failed: {self.stats['conversations_failed']}")
        logger.info(f"❌ Messages failed: {self.stats['messages_failed']}")
        logger.info(f"⏱️  Duration: {self.stats.get('duration', 'Unknown')}")
        logger.info(f"📁 Archive path: {self.archive_path}")

async def main():
    """Main import function"""
    archive_path = "/Users/tem/nab/exploded_archive_node"
    
    importer = NodeArchiveBrowserImporter(archive_path)
    
    try:
        # Connect to database
        if not await importer.connect_database():
            return 1
        
        # Import all conversations
        logger.info(f"🚀 Starting Node Archive Browser import from {archive_path}")
        stats = await importer.import_all_conversations()
        
        # Print summary
        importer.print_summary()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return 1
    finally:
        await importer.close_database()

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)