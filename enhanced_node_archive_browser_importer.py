#!/usr/bin/env python3
"""
Enhanced Node Archive Browser Importer
Handles both individual conversation folders AND bulk conversations.json files
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

class EnhancedNodeArchiveBrowserImporter:
    """Enhanced Node Archive Browser importer supporting both folder and bulk JSON formats"""
    
    def __init__(self, archive_path: str, database_url: str = "postgresql://tem@localhost/humanizer_rails_development"):
        self.archive_path = Path(archive_path)
        self.database_url = database_url
        self.stats = {
            "conversations_processed": 0,
            "messages_processed": 0,
            "conversations_failed": 0,
            "messages_failed": 0,
            "individual_folders": 0,
            "bulk_files": 0,
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
    
    def find_conversation_sources(self) -> Dict[str, List[Path]]:
        """Find both individual conversation folders and bulk JSON files"""
        sources = {
            "individual_folders": [],
            "bulk_files": []
        }
        
        if not self.archive_path.exists():
            logger.error(f"Archive path does not exist: {self.archive_path}")
            return sources
        
        # Look for individual conversation folders (each should have conversation.json)
        for item in self.archive_path.iterdir():
            if item.is_dir():
                conversation_json = item / "conversation.json"
                if conversation_json.exists():
                    sources["individual_folders"].append(item)
        
        # Look for bulk conversations.json files
        bulk_files = list(self.archive_path.glob("**/conversations.json"))
        sources["bulk_files"] = bulk_files
        
        logger.info(f"Found {len(sources['individual_folders'])} individual conversation folders")
        logger.info(f"Found {len(sources['bulk_files'])} bulk conversations.json files")
        return sources
    
    def parse_conversation_metadata(self, conversation_data: dict, source_id: str) -> dict:
        """Extract conversation metadata"""
        return {
            "conversation_id": conversation_data.get("id") or conversation_data.get("conversation_id", source_id),
            "title": conversation_data.get("title", "Untitled"),
            "create_time": conversation_data.get("create_time"),
            "update_time": conversation_data.get("update_time"), 
            "source_id": source_id,
            "message_count": len(conversation_data.get("mapping", {}))
        }
    
    async def load_message_content(self, message_obj: dict, conversation_folder: Optional[Path] = None) -> Optional[dict]:
        """Load message content, handling both inline and referenced messages"""
        message = message_obj.get("message")
        if not message:
            return None
        
        # Check if this is a message reference (only for individual folder format)
        if conversation_folder and "_reference" in message and message["_reference"].startswith("messages/"):
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
    
    async def import_single_conversation(self, conversation_data: dict, source_id: str, conversation_folder: Optional[Path] = None) -> bool:
        """Import a single conversation with all its messages"""
        try:
            # Extract conversation metadata  
            conv_metadata = self.parse_conversation_metadata(conversation_data, source_id)
            
            # Convert timestamps to timezone-naive datetime objects (Rails expects this)
            create_time = None
            update_time = None
            
            if conv_metadata["create_time"]:
                create_time = datetime.fromtimestamp(conv_metadata["create_time"])
            if conv_metadata["update_time"]:
                update_time = datetime.fromtimestamp(conv_metadata["update_time"])
            
            # Generate Rails-compatible conversation ID
            conversation_db_id = f"nab-{conv_metadata['conversation_id']}"
            
            # Check if conversation already exists
            existing = await self.conn.fetchval(
                "SELECT id FROM conversations WHERE id = $1", conversation_db_id
            )
            if existing:
                logger.info(f"📁 Skipping existing conversation: {conv_metadata['title']} (ID: {conversation_db_id})")
                return True
            
            # Insert conversation record into Rails conversations table
            await self.conn.execute("""
                INSERT INTO conversations 
                (id, title, source_type, original_id, summary, metadata, 
                 message_count, word_count, original_created_at, original_updated_at, 
                 created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO NOTHING
            """, 
                conversation_db_id,  # id (Rails string primary key)
                conv_metadata["title"],  # title
                "chatgpt",  # source_type (compatible with Rails enum)
                conv_metadata["conversation_id"],  # original_id
                None,  # summary (will be calculated later)
                json.dumps(conv_metadata),  # metadata (jsonb)
                conv_metadata["message_count"],  # message_count
                0,  # word_count (will be calculated from messages)
                create_time,  # original_created_at
                update_time,  # original_updated_at
                datetime.now(),  # created_at
                datetime.now()   # updated_at
            )
            
            logger.info(f"📁 Imported conversation: {conv_metadata['title']} (ID: {conversation_db_id})")
            
            # Process messages in the conversation
            mapping = conversation_data.get("mapping", {})
            message_count = 0
            total_word_count = 0
            
            for idx, (message_id, message_obj) in enumerate(mapping.items()):
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
                    
                    # Convert message timestamps to timezone-naive datetime  
                    msg_create_time = None
                    if message_metadata.get("create_time"):
                        msg_create_time = datetime.fromtimestamp(message_metadata["create_time"])
                    
                    # Calculate word count
                    msg_word_count = len(message_text.split()) if message_text else 0
                    total_word_count += msg_word_count
                    
                    # Generate Rails-compatible message ID
                    message_db_id = f"nab-{message_id}"
                    
                    # Insert message record into Rails messages table
                    await self.conn.execute("""
                        INSERT INTO messages 
                        (id, conversation_id, role, content, parent_message_id, 
                         message_index, word_count, metadata, original_timestamp, 
                         created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (id) DO NOTHING
                    """,
                        message_db_id,  # id (Rails string primary key)
                        conversation_db_id,  # conversation_id (links to conversation)
                        message_metadata.get("role", "unknown"),  # role
                        message_text,  # content
                        None,  # parent_message_id (could be enhanced later)
                        idx,  # message_index (order in conversation)
                        msg_word_count,  # word_count
                        json.dumps(message_metadata),  # metadata (jsonb)
                        msg_create_time or create_time,  # original_timestamp
                        datetime.now(),  # created_at
                        datetime.now()   # updated_at
                    )
                    
                    message_count += 1
                    self.stats["messages_processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import message {message_id}: {e}")
                    self.stats["messages_failed"] += 1
                    continue
            
            # Update conversation word count
            await self.conn.execute("""
                UPDATE conversations 
                SET word_count = $1, message_count = $2 
                WHERE id = $3
            """, total_word_count, message_count, conversation_db_id)
            
            logger.info(f"  📝 Imported {message_count} messages")
            self.stats["conversations_processed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to import conversation {source_id}: {e}")
            self.stats["conversations_failed"] += 1
            return False
    
    async def import_bulk_conversations_file(self, bulk_file: Path) -> int:
        """Import conversations from a bulk conversations.json file"""
        logger.info(f"📦 Processing bulk file: {bulk_file}")
        
        try:
            with open(bulk_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            imported_count = 0
            for i, conversation_data in enumerate(conversations):
                source_id = f"{bulk_file.stem}_{i}"
                success = await self.import_single_conversation(conversation_data, source_id)
                if success:
                    imported_count += 1
                
                # Progress update every 100 conversations
                if (i + 1) % 100 == 0:
                    elapsed = datetime.now() - self.stats["start_time"]
                    logger.info(f"📈 Bulk progress: {i + 1}/{len(conversations)} conversations from {bulk_file.name}, "
                               f"elapsed: {elapsed}")
            
            self.stats["bulk_files"] += 1
            logger.info(f"✅ Completed bulk file: {bulk_file} - {imported_count}/{len(conversations)} conversations")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to process bulk file {bulk_file}: {e}")
            return 0
    
    async def import_individual_folder(self, conversation_folder: Path) -> bool:
        """Import a single conversation from an individual folder"""
        try:
            # Load conversation.json
            conversation_json_path = conversation_folder / "conversation.json"
            with open(conversation_json_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            source_id = conversation_folder.name
            success = await self.import_single_conversation(conversation_data, source_id, conversation_folder)
            if success:
                self.stats["individual_folders"] += 1
            return success
            
        except Exception as e:
            logger.error(f"Failed to import individual folder {conversation_folder.name}: {e}")
            return False
    
    async def import_all_conversations(self, max_conversations: Optional[int] = None) -> dict:
        """Import all conversations from both individual folders and bulk files"""
        self.stats["start_time"] = datetime.now()
        
        # Find all conversation sources
        sources = self.find_conversation_sources()
        
        # Import individual conversation folders
        conversation_folders = sources["individual_folders"]
        if max_conversations:
            conversation_folders = conversation_folders[:max_conversations]
        
        for i, folder in enumerate(conversation_folders, 1):
            logger.info(f"Processing individual folder {i}/{len(conversation_folders)}: {folder.name}")
            await self.import_individual_folder(folder)
        
        # Import bulk conversations files
        bulk_files = sources["bulk_files"]
        for bulk_file in bulk_files:
            await self.import_bulk_conversations_file(bulk_file)
        
        self.stats["end_time"] = datetime.now()
        self.stats["duration"] = self.stats["end_time"] - self.stats["start_time"]
        
        return self.stats
    
    def print_summary(self):
        """Print import summary"""
        logger.info("\n" + "="*60)
        logger.info("🎯 ENHANCED NODE ARCHIVE BROWSER IMPORT COMPLETE")
        logger.info("="*60)
        logger.info(f"✅ Conversations imported: {self.stats['conversations_processed']}")
        logger.info(f"✅ Messages imported: {self.stats['messages_processed']}")
        logger.info(f"❌ Conversations failed: {self.stats['conversations_failed']}")
        logger.info(f"❌ Messages failed: {self.stats['messages_failed']}")
        logger.info(f"📁 Individual folders processed: {self.stats['individual_folders']}")
        logger.info(f"📦 Bulk files processed: {self.stats['bulk_files']}")
        logger.info(f"⏱️  Duration: {self.stats.get('duration', 'Unknown')}")
        logger.info(f"📁 Archive path: {self.archive_path}")

async def main():
    """Main import function"""
    archive_path = "/Users/tem/nab"
    
    importer = EnhancedNodeArchiveBrowserImporter(archive_path)
    
    try:
        # Connect to database
        if not await importer.connect_database():
            return 1
        
        # Import all conversations
        logger.info(f"🚀 Starting Enhanced Node Archive Browser import from {archive_path}")
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