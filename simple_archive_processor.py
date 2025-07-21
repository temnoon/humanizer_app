#!/usr/bin/env python3
"""
Simple Archive Processor for Node Archive Browser imports
Works with the Enhanced Lighthouse API
"""

import asyncio
import json
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime


class SimpleArchiveProcessor:
    """Simple archive processor for Node Archive Browser conversations"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.progress = {
            "session_id": self.session_id,
            "status": "idle",
            "current_step": None,
            "progress_percent": 0.0,
            "steps": {
                "analyze": {"status": "pending", "progress": 0.0},
                "import": {"status": "pending", "progress": 0.0}, 
                "process": {"status": "pending", "progress": 0.0},
                "finalize": {"status": "pending", "progress": 0.0}
            },
            "stats": {
                "conversations_found": 0,
                "conversations_processed": 0,
                "files_processed": 0,
                "start_time": None,
                "estimated_completion": None
            }
        }
    
    async def analyze_archive(self, archive_path: str) -> Dict[str, Any]:
        """Analyze uploaded archive structure"""
        self.progress["current_step"] = "analyze"
        self.progress["steps"]["analyze"]["status"] = "in_progress"
        
        analysis = {
            "archive_type": "unknown",
            "conversations_found": 0,
            "files_found": 0,
            "size_mb": 0,
            "estimated_time": "unknown"
        }
        
        try:
            # Check for conversations.json
            conversations_file = Path(archive_path) / "conversations.json"
            if conversations_file.exists():
                # Try to parse conversations
                with open(conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    analysis["conversations_found"] = len(data)
                    analysis["archive_type"] = "openai_export"
                elif isinstance(data, dict):
                    if "conversations" in data:
                        analysis["conversations_found"] = len(data["conversations"])
                    else:
                        analysis["conversations_found"] = len([k for k in data.keys() if k != "metadata"])
                    analysis["archive_type"] = "node_archive_browser"
            
            # Count files and get size
            total_size = 0
            file_count = 0
            for root, dirs, files in os.walk(archive_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except:
                        continue
            
            analysis["files_found"] = file_count
            analysis["size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Estimate processing time (rough)
            conv_count = analysis["conversations_found"]
            if conv_count > 0:
                estimated_seconds = conv_count * 2  # 2 seconds per conversation
                if estimated_seconds < 60:
                    analysis["estimated_time"] = f"{int(estimated_seconds)} seconds"
                elif estimated_seconds < 3600:
                    analysis["estimated_time"] = f"{int(estimated_seconds/60)} minutes"
                else:
                    analysis["estimated_time"] = f"{int(estimated_seconds/3600)} hours"
            
            self.progress["stats"]["conversations_found"] = analysis["conversations_found"]
            self.progress["steps"]["analyze"]["status"] = "completed"
            self.progress["steps"]["analyze"]["progress"] = 1.0
            
            return analysis
            
        except Exception as e:
            self.progress["steps"]["analyze"]["status"] = "failed"
            analysis["error"] = str(e)
            return analysis
    
    async def process_conversations(self, archive_path: str, max_conversations: Optional[int] = None) -> Dict[str, Any]:
        """Process conversations from the archive"""
        self.progress["current_step"] = "import"
        self.progress["steps"]["import"]["status"] = "in_progress"
        self.progress["stats"]["start_time"] = datetime.now().isoformat()
        
        results = {
            "conversations_processed": 0,
            "conversations_failed": 0,
            "total_messages": 0,
            "processing_summary": []
        }
        
        try:
            conversations_file = Path(archive_path) / "conversations.json"
            if not conversations_file.exists():
                raise FileNotFoundError("conversations.json not found")
            
            with open(conversations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conversations = []
            if isinstance(data, list):
                conversations = data[:max_conversations] if max_conversations else data
            elif isinstance(data, dict):
                if "conversations" in data:
                    conversations = data["conversations"][:max_conversations] if max_conversations else data["conversations"]
                else:
                    # Node Archive Browser format
                    conversations = [{"id": k, "data": v} for k, v in data.items() if k != "metadata"]
                    if max_conversations:
                        conversations = conversations[:max_conversations]
            
            total_conversations = len(conversations)
            processed = 0
            failed = 0
            
            for i, conversation in enumerate(conversations):
                try:
                    # Simple processing - count messages
                    message_count = 0
                    if isinstance(conversation, dict):
                        if "mapping" in conversation:
                            # OpenAI format
                            message_count = len([m for m in conversation["mapping"].values() if m.get("message")])
                        elif "data" in conversation:
                            # Node Archive Browser
                            conv_data = conversation["data"]
                            if isinstance(conv_data, dict) and "messages" in conv_data:
                                message_count = len(conv_data["messages"])
                    
                    results["total_messages"] += message_count
                    processed += 1
                    
                    # Update progress
                    progress = (i + 1) / total_conversations
                    self.progress["steps"]["import"]["progress"] = progress
                    self.progress["stats"]["conversations_processed"] = processed
                    self.progress["stats"]["files_processed"] = i + 1
                    
                    # Simulate processing time
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    failed += 1
                    results["processing_summary"].append(f"Failed to process conversation {i}: {str(e)}")
            
            results["conversations_processed"] = processed
            results["conversations_failed"] = failed
            
            self.progress["steps"]["import"]["status"] = "completed"
            self.progress["steps"]["import"]["progress"] = 1.0
            
            return results
            
        except Exception as e:
            self.progress["steps"]["import"]["status"] = "failed"
            results["error"] = str(e)
            return results
    
    async def finalize_processing(self, temp_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Finalize processing and cleanup"""
        self.progress["current_step"] = "finalize"
        self.progress["steps"]["finalize"]["status"] = "in_progress"
        
        try:
            # Cleanup temporary directory
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.progress["steps"]["finalize"]["status"] = "completed"
            self.progress["steps"]["finalize"]["progress"] = 1.0
            self.progress["status"] = "completed"
            
            return {
                "cleanup_completed": True,
                "session_id": self.session_id,
                "total_conversations": self.progress["stats"]["conversations_processed"],
                "processing_time": self.calculate_processing_time()
            }
            
        except Exception as e:
            self.progress["steps"]["finalize"]["status"] = "failed"
            return {"error": str(e)}
    
    def calculate_processing_time(self) -> str:
        """Calculate total processing time"""
        if self.progress["stats"]["start_time"]:
            start = datetime.fromisoformat(self.progress["stats"]["start_time"])
            duration = datetime.now() - start
            return f"{duration.total_seconds():.1f} seconds"
        return "unknown"
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        # Calculate overall progress
        step_weights = {"analyze": 0.1, "import": 0.7, "process": 0.1, "finalize": 0.1}
        total_progress = 0.0
        
        for step, weight in step_weights.items():
            step_progress = self.progress["steps"][step]["progress"]
            total_progress += step_progress * weight
        
        self.progress["progress_percent"] = round(total_progress * 100, 1)
        
        return self.progress.copy()


async def process_uploaded_archive(files_data: List[Dict], archive_type: str, max_conversations: Optional[int] = None) -> Dict[str, Any]:
    """Process uploaded archive files"""
    processor = SimpleArchiveProcessor()
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="simple_archive_"))
    
    try:
        # Save uploaded files
        archive_path = None
        for file_data in files_data:
            filename = file_data.get("filename", "unknown")
            content = file_data.get("content", b"")
            
            file_path = temp_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Handle ZIP extraction
            if filename.endswith('.zip'):
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        extract_dir = temp_dir / filename.replace('.zip', '')
                        zip_ref.extractall(extract_dir)
                        archive_path = str(extract_dir)
                except Exception as e:
                    print(f"Failed to extract ZIP: {e}")
            
            if filename == 'conversations.json':
                archive_path = str(temp_dir)
        
        if not archive_path:
            archive_path = str(temp_dir)
        
        # Process the archive
        analysis = await processor.analyze_archive(archive_path)
        processing_results = await processor.process_conversations(archive_path, max_conversations)
        finalization = await processor.finalize_processing(temp_dir)
        
        return {
            "session_id": processor.session_id,
            "status": "completed",
            "analysis": analysis,
            "processing_results": processing_results,
            "finalization": finalization,
            "final_progress": processor.get_progress()
        }
        
    except Exception as e:
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return {
            "session_id": processor.session_id,
            "status": "failed",
            "error": str(e),
            "progress": processor.get_progress()
        }


if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) > 1:
        archive_path = sys.argv[1]
        processor = SimpleArchiveProcessor()
        
        async def test_process():
            analysis = await processor.analyze_archive(archive_path)
            print("Analysis:", json.dumps(analysis, indent=2))
            
            results = await processor.process_conversations(archive_path, max_conversations=5)
            print("Processing:", json.dumps(results, indent=2))
            
            finalization = await processor.finalize_processing()
            print("Finalization:", json.dumps(finalization, indent=2))
            
            print("Final Progress:", json.dumps(processor.get_progress(), indent=2))
        
        asyncio.run(test_process())
    else:
        print("Usage: python simple_archive_processor.py <archive_path>")