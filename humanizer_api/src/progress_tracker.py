#!/usr/bin/env python3
"""
Persistent Progress Tracker for Archive Processing
Provides real-time progress updates that persist across page refreshes
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading

# Setup logging
logger = logging.getLogger(__name__)

class ProgressStatus(str, Enum):
    """Progress status types"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ProgressStep:
    """Individual progress step"""
    id: str
    name: str
    status: ProgressStatus
    progress: float  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

@dataclass
class ProcessingProgress:
    """Complete processing progress state"""
    session_id: str
    overall_status: ProgressStatus
    overall_progress: float  # 0.0 to 1.0
    current_step: str
    steps: List[ProgressStep]
    
    # Statistics
    total_conversations: int = 0
    processed_conversations: int = 0
    failed_conversations: int = 0
    total_chunks: int = 0
    processed_chunks: int = 0
    total_embeddings: int = 0
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Activity breakdown
    activity_breakdown: Dict[str, int] = None
    
    # Error tracking
    errors: List[str] = None
    
    def __post_init__(self):
        if self.activity_breakdown is None:
            self.activity_breakdown = {"today": 0, "this_week": 0, "this_month": 0, "older": 0}
        if self.errors is None:
            self.errors = []
        if self.details is None:
            for step in self.steps:
                if step.details is None:
                    step.details = {}

class PersistentProgressTracker:
    """
    Persistent progress tracker that maintains state across restarts
    """
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.progress_file = Path(f"progress_{self.session_id}.json")
        self.subscribers: List[callable] = []
        self.lock = threading.Lock()
        
        # Initialize or load progress
        self.progress = self._load_or_create_progress()
        
    def _load_or_create_progress(self) -> ProcessingProgress:
        """Load existing progress or create new"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                
                # Convert datetime strings back to datetime objects
                for key in ['start_time', 'end_time', 'estimated_completion']:
                    if data.get(key):
                        data[key] = datetime.fromisoformat(data[key])
                
                # Convert steps
                steps = []
                for step_data in data.get('steps', []):
                    for key in ['start_time', 'end_time']:
                        if step_data.get(key):
                            step_data[key] = datetime.fromisoformat(step_data[key])
                    
                    steps.append(ProgressStep(**step_data))
                
                data['steps'] = steps
                
                progress = ProcessingProgress(**data)
                logger.info(f"📥 Loaded existing progress for session {self.session_id}")
                return progress
                
            except Exception as e:
                logger.warning(f"Could not load progress: {e}, creating new")
        
        # Create new progress
        return ProcessingProgress(
            session_id=self.session_id,
            overall_status=ProgressStatus.NOT_STARTED,
            overall_progress=0.0,
            current_step="initialization",
            steps=[
                ProgressStep(
                    id="analyze",
                    name="Analyze Archive Activity",
                    status=ProgressStatus.NOT_STARTED,
                    progress=0.0
                ),
                ProgressStep(
                    id="import",
                    name="Import Conversations",
                    status=ProgressStatus.NOT_STARTED,
                    progress=0.0
                ),
                ProgressStep(
                    id="chunk",
                    name="Generate Chunks",
                    status=ProgressStatus.NOT_STARTED,
                    progress=0.0
                ),
                ProgressStep(
                    id="embed",
                    name="Create Embeddings",
                    status=ProgressStatus.NOT_STARTED,
                    progress=0.0
                ),
                ProgressStep(
                    id="finalize",
                    name="Finalize & Cleanup",
                    status=ProgressStatus.NOT_STARTED,
                    progress=0.0
                )
            ]
        )
    
    def save_progress(self):
        """Save current progress to disk"""
        try:
            with self.lock:
                # Convert to JSON-serializable format
                data = asdict(self.progress)
                
                # Convert datetime objects to ISO strings
                for key in ['start_time', 'end_time', 'estimated_completion']:
                    if data.get(key):
                        data[key] = data[key].isoformat()
                
                # Convert step datetimes
                for step in data['steps']:
                    for key in ['start_time', 'end_time']:
                        if step.get(key):
                            step[key] = step[key].isoformat()
                
                with open(self.progress_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def subscribe(self, callback: callable):
        """Subscribe to progress updates"""
        self.subscribers.append(callback)
    
    def _notify_subscribers(self):
        """Notify all subscribers of progress update"""
        for callback in self.subscribers:
            try:
                callback(self.progress)
            except Exception as e:
                logger.error(f"Subscriber notification failed: {e}")
    
    def start_session(self):
        """Start a new processing session"""
        with self.lock:
            self.progress.overall_status = ProgressStatus.INITIALIZING
            self.progress.start_time = datetime.now(timezone.utc)
            self.progress.current_step = "analyze"
            self.save_progress()
            self._notify_subscribers()
            
        logger.info(f"🚀 Started processing session {self.session_id}")
    
    def start_step(self, step_id: str):
        """Start a specific step"""
        with self.lock:
            for step in self.progress.steps:
                if step.id == step_id:
                    step.status = ProgressStatus.PROCESSING
                    step.start_time = datetime.now(timezone.utc)
                    step.progress = 0.0
                    break
            
            self.progress.current_step = step_id
            self.save_progress()
            self._notify_subscribers()
            
        logger.info(f"📍 Started step: {step_id}")
    
    def update_step_progress(self, step_id: str, progress: float, details: Dict[str, Any] = None):
        """Update progress for a specific step"""
        with self.lock:
            for step in self.progress.steps:
                if step.id == step_id:
                    step.progress = min(1.0, max(0.0, progress))
                    if details:
                        step.details.update(details)
                    break
            
            # Update overall progress (weighted average)
            total_progress = sum(step.progress for step in self.progress.steps)
            self.progress.overall_progress = total_progress / len(self.progress.steps)
            
            self.save_progress()
            self._notify_subscribers()
    
    def complete_step(self, step_id: str, details: Dict[str, Any] = None):
        """Mark a step as completed"""
        with self.lock:
            for step in self.progress.steps:
                if step.id == step_id:
                    step.status = ProgressStatus.COMPLETED
                    step.progress = 1.0
                    step.end_time = datetime.now(timezone.utc)
                    if details:
                        step.details.update(details)
                    break
            
            # Update overall progress
            total_progress = sum(step.progress for step in self.progress.steps)
            self.progress.overall_progress = total_progress / len(self.progress.steps)
            
            self.save_progress()
            self._notify_subscribers()
            
        logger.info(f"✅ Completed step: {step_id}")
    
    def fail_step(self, step_id: str, error_message: str):
        """Mark a step as failed"""
        with self.lock:
            for step in self.progress.steps:
                if step.id == step_id:
                    step.status = ProgressStatus.FAILED
                    step.error_message = error_message
                    step.end_time = datetime.now(timezone.utc)
                    break
            
            self.progress.overall_status = ProgressStatus.FAILED
            self.progress.errors.append(f"{step_id}: {error_message}")
            self.save_progress()
            self._notify_subscribers()
            
        logger.error(f"❌ Failed step {step_id}: {error_message}")
    
    def update_statistics(self, **kwargs):
        """Update processing statistics"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.progress, key):
                    setattr(self.progress, key, value)
            
            # Update estimated completion based on progress
            if (self.progress.overall_progress > 0 and 
                self.progress.start_time and 
                self.progress.overall_status == ProgressStatus.PROCESSING):
                
                elapsed = datetime.now(timezone.utc) - self.progress.start_time
                if self.progress.overall_progress > 0:
                    total_estimated = elapsed / self.progress.overall_progress
                    remaining = total_estimated - elapsed
                    self.progress.estimated_completion = datetime.now(timezone.utc) + remaining
            
            self.save_progress()
            self._notify_subscribers()
    
    def complete_session(self):
        """Mark the entire session as completed"""
        with self.lock:
            self.progress.overall_status = ProgressStatus.COMPLETED
            self.progress.overall_progress = 1.0
            self.progress.end_time = datetime.now(timezone.utc)
            
            # Complete any remaining steps
            for step in self.progress.steps:
                if step.status not in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                    step.status = ProgressStatus.COMPLETED
                    step.progress = 1.0
                    if not step.end_time:
                        step.end_time = datetime.now(timezone.utc)
            
            self.save_progress()
            self._notify_subscribers()
            
        logger.info(f"🎉 Completed processing session {self.session_id}")
    
    def pause_session(self):
        """Pause the processing session"""
        with self.lock:
            self.progress.overall_status = ProgressStatus.PAUSED
            self.save_progress()
            self._notify_subscribers()
            
        logger.info(f"⏸️  Paused processing session {self.session_id}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of current progress"""
        with self.lock:
            elapsed_time = None
            if self.progress.start_time:
                end_time = self.progress.end_time or datetime.now(timezone.utc)
                elapsed_time = (end_time - self.progress.start_time).total_seconds()
            
            return {
                "session_id": self.progress.session_id,
                "overall_status": self.progress.overall_status.value,
                "overall_progress": self.progress.overall_progress,
                "current_step": self.progress.current_step,
                "steps": [
                    {
                        "id": step.id,
                        "name": step.name,
                        "status": step.status.value,
                        "progress": step.progress,
                        "details": step.details
                    }
                    for step in self.progress.steps
                ],
                "statistics": {
                    "total_conversations": self.progress.total_conversations,
                    "processed_conversations": self.progress.processed_conversations,
                    "failed_conversations": self.progress.failed_conversations,
                    "total_chunks": self.progress.total_chunks,
                    "processed_chunks": self.progress.processed_chunks,
                    "total_embeddings": self.progress.total_embeddings,
                    "activity_breakdown": self.progress.activity_breakdown
                },
                "timing": {
                    "start_time": self.progress.start_time.isoformat() if self.progress.start_time else None,
                    "end_time": self.progress.end_time.isoformat() if self.progress.end_time else None,
                    "estimated_completion": self.progress.estimated_completion.isoformat() if self.progress.estimated_completion else None,
                    "elapsed_seconds": elapsed_time
                },
                "errors": self.progress.errors
            }
    
    def cleanup(self):
        """Clean up progress file after successful completion"""
        if self.progress.overall_status == ProgressStatus.COMPLETED:
            try:
                if self.progress_file.exists():
                    self.progress_file.unlink()
                logger.info(f"🧹 Cleaned up progress file for session {self.session_id}")
            except Exception as e:
                logger.warning(f"Could not clean up progress file: {e}")

# Global progress tracker registry
_progress_trackers: Dict[str, PersistentProgressTracker] = {}

def get_progress_tracker(session_id: str = None) -> PersistentProgressTracker:
    """Get or create a progress tracker for a session"""
    if session_id is None:
        # Find the most recent session
        progress_files = list(Path(".").glob("progress_*.json"))
        if progress_files:
            most_recent = max(progress_files, key=lambda p: p.stat().st_mtime)
            session_id = most_recent.stem.replace("progress_", "")
        else:
            session_id = f"session_{int(time.time())}"
    
    if session_id not in _progress_trackers:
        _progress_trackers[session_id] = PersistentProgressTracker(session_id)
    
    return _progress_trackers[session_id]

def list_active_sessions() -> List[str]:
    """List all active/recent processing sessions"""
    progress_files = list(Path(".").glob("progress_*.json"))
    sessions = []
    
    for file in progress_files:
        session_id = file.stem.replace("progress_", "")
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            sessions.append({
                "session_id": session_id,
                "status": data.get("overall_status", "unknown"),
                "progress": data.get("overall_progress", 0.0),
                "start_time": data.get("start_time"),
                "conversations": data.get("total_conversations", 0)
            })
        except Exception as e:
            logger.warning(f"Could not read session file {file}: {e}")
    
    return sorted(sessions, key=lambda s: s.get("start_time", ""), reverse=True)