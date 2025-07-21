#!/usr/bin/env python3
"""
Folder-by-Folder Archive Processor
Processes Node Archive Browser exports one conversation at a time
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/tem/humanizer-lighthouse/archive_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("folder_processor")


class FolderByFolderProcessor:
    """Process Node Archive Browser exports one conversation folder at a time"""
    
    def __init__(self, archive_path: str):
        self.archive_path = Path(archive_path)
        self.session_id = str(uuid.uuid4())
        self.stats = {
            "total_conversations": 0,
            "processed_conversations": 0,
            "failed_conversations": 0,
            "total_messages": 0,
            "total_media_files": 0,
            "start_time": None,
            "current_folder": None
        }
        
    async def analyze_archive(self) -> Dict[str, Any]:
        """Analyze the archive structure"""
        logger.info(f"🔍 Analyzing archive: {self.archive_path}")
        
        if not self.archive_path.exists():
            raise FileNotFoundError(f"Archive path not found: {self.archive_path}")
        
        # Count conversation folders
        conversation_folders = []
        for item in self.archive_path.iterdir():
            if item.is_dir():
                conversation_folders.append(item)
        
        self.stats["total_conversations"] = len(conversation_folders)
        
        logger.info(f"📊 Found {len(conversation_folders)} conversation folders")
        
        # Sample a few folders to estimate content
        sample_messages = 0
        sample_media = 0
        sample_size = min(5, len(conversation_folders))
        
        for folder in conversation_folders[:sample_size]:
            folder_stats = await self._analyze_folder(folder)
            sample_messages += folder_stats["messages"]
            sample_media += folder_stats["media_files"]
        
        if sample_size > 0:
            avg_messages = sample_messages / sample_size
            avg_media = sample_media / sample_size
            estimated_total_messages = int(avg_messages * len(conversation_folders))
            estimated_total_media = int(avg_media * len(conversation_folders))
        else:
            estimated_total_messages = 0
            estimated_total_media = 0
        
        analysis = {
            "conversation_folders": len(conversation_folders),
            "estimated_messages": estimated_total_messages,
            "estimated_media_files": estimated_total_media,
            "sample_analyzed": sample_size,
            "processing_approach": "folder_by_folder",
            "estimated_time_minutes": len(conversation_folders) * 2  # 2 seconds per folder
        }
        
        logger.info(f"📈 Estimated: {estimated_total_messages:,} messages, {estimated_total_media:,} media files")
        
        return analysis
    
    async def _analyze_folder(self, folder_path: Path) -> Dict[str, int]:
        """Analyze a single conversation folder"""
        stats = {"messages": 0, "media_files": 0}
        
        try:
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix == '.json' and 'message' in file_path.name.lower():
                        stats["messages"] += 1
                    elif file_path.suffix != '.json':
                        stats["media_files"] += 1
        except Exception as e:
            logger.warning(f"Error analyzing folder {folder_path.name}: {e}")
        
        return stats
    
    async def process_all_folders(self, max_conversations: Optional[int] = None) -> Dict[str, Any]:
        """Process all conversation folders one by one"""
        logger.info(f"🚀 Starting folder-by-folder processing")
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Get all conversation folders
        conversation_folders = [item for item in self.archive_path.iterdir() if item.is_dir()]
        conversation_folders.sort()  # Process in order
        
        if max_conversations:
            conversation_folders = conversation_folders[:max_conversations]
            logger.info(f"🔢 Limited to {max_conversations} conversations")
        
        total_folders = len(conversation_folders)
        logger.info(f"📁 Processing {total_folders} conversation folders")
        
        # Process each folder
        for i, folder in enumerate(conversation_folders, 1):
            self.stats["current_folder"] = folder.name
            
            try:
                logger.info(f"📂 Processing folder {i}/{total_folders}: {folder.name}")
                
                folder_result = await self._process_single_folder(folder)
                
                self.stats["processed_conversations"] += 1
                self.stats["total_messages"] += folder_result["messages"]
                self.stats["total_media_files"] += folder_result["media_files"]
                
                # Progress logging
                if i % 50 == 0 or i == total_folders:
                    progress = (i / total_folders) * 100
                    logger.info(f"📊 Progress: {i}/{total_folders} ({progress:.1f}%) - "
                              f"{self.stats['total_messages']:,} messages processed")
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"❌ Failed to process folder {folder.name}: {e}")
                self.stats["failed_conversations"] += 1
        
        # Final results
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.stats["start_time"])
        duration = (end_time - start_time).total_seconds()
        
        results = {
            "session_id": self.session_id,
            "status": "completed",
            "stats": self.stats.copy(),
            "processing_time_seconds": duration,
            "conversations_per_second": self.stats["processed_conversations"] / duration if duration > 0 else 0
        }
        
        logger.info(f"✅ Processing complete!")
        logger.info(f"📈 Results: {self.stats['processed_conversations']} conversations, "
                   f"{self.stats['total_messages']:,} messages, "
                   f"{self.stats['total_media_files']:,} media files")
        logger.info(f"⏱️  Duration: {duration:.1f} seconds")
        
        return results
    
    async def _process_single_folder(self, folder_path: Path) -> Dict[str, int]:
        """Process a single conversation folder"""
        stats = {"messages": 0, "media_files": 0, "size_bytes": 0}
        
        # Look for conversation metadata
        conversation_data = {}
        
        # Check for conversation.json or similar
        for metadata_file in ["conversation.json", "metadata.json", "info.json"]:
            metadata_path = folder_path / metadata_file
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        conversation_data = json.load(f)
                    break
                except Exception as e:
                    logger.warning(f"Could not read {metadata_file}: {e}")
        
        # Process all files in the folder
        messages = []
        media_files = []
        
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                stats["size_bytes"] += file_size
                
                if file_path.suffix == '.json' and 'message' in file_path.name.lower():
                    # Process message file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            message_data = json.load(f)
                        messages.append({
                            "file": file_path.name,
                            "data": message_data,
                            "size": file_size
                        })
                        stats["messages"] += 1
                    except Exception as e:
                        logger.warning(f"Could not read message {file_path.name}: {e}")
                
                elif file_path.suffix != '.json':
                    # Media file
                    media_files.append({
                        "file": file_path.name,
                        "path": str(file_path.relative_to(folder_path)),
                        "size": file_size,
                        "type": file_path.suffix
                    })
                    stats["media_files"] += 1
        
        # Here you would normally store to database
        # For now, just log the processing
        if stats["size_bytes"] > 10 * 1024 * 1024:  # Log if > 10MB
            logger.info(f"  📏 Large folder: {stats['size_bytes'] / 1024 / 1024:.1f}MB, "
                       f"{stats['messages']} messages, {stats['media_files']} media files")
        
        return stats


async def main():
    """Main processing function"""
    archive_path = "/Users/tem/nab/exploded_archive_node"
    
    if not os.path.exists(archive_path):
        logger.error(f"❌ Archive path not found: {archive_path}")
        return
    
    processor = FolderByFolderProcessor(archive_path)
    
    # Analyze first
    analysis = await processor.analyze_archive()
    logger.info(f"📋 Analysis: {json.dumps(analysis, indent=2)}")
    
    # Process (limit for testing)
    results = await processor.process_all_folders(max_conversations=10)
    logger.info(f"🎯 Final Results: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())