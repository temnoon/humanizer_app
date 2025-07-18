#!/usr/bin/env python3
"""
Minimal Archive API that works with basic dependencies
"""

import json
import uuid
import hashlib
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from fastapi import FastAPI, HTTPException, Form, File, UploadFile
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Simple storage class using SQLite
class SimpleArchiveStorage:
    def __init__(self, db_path: str = "data/archive.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS archived_content (
                id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT,
                content_hash TEXT UNIQUE,
                content_data TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS content_sources (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                source_type TEXT NOT NULL,
                content_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_content(self, content_type: str, source: str, content_data: str, 
                   title: str = None, metadata: Dict = None, tags: List = None):
        """Add content to archive"""
        content_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content_data.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Check for duplicates
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM archived_content WHERE content_hash = ?", (content_hash,))
            if cursor.fetchone():
                return {"status": "duplicate", "content_hash": content_hash}
            
            # Insert content
            cursor.execute('''
                INSERT INTO archived_content 
                (id, content_type, source, title, content_hash, content_data, metadata, tags, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_id, content_type, source, title or f"Content {content_id[:8]}",
                content_hash, content_data, json.dumps(metadata or {}), 
                json.dumps(tags or []), len(content_data.encode())
            ))
            
            # Update source count
            cursor.execute('''
                INSERT OR REPLACE INTO content_sources (id, name, source_type, content_count)
                VALUES (?, ?, ?, COALESCE((SELECT content_count FROM content_sources WHERE name = ?) + 1, 1))
            ''', (str(uuid.uuid4()), source, content_type, source))
            
            conn.commit()
            return {"status": "success", "content_id": content_id, "content_hash": content_hash}
            
        except Exception as e:
            conn.rollback()
            return {"status": "error", "error": str(e)}
        finally:
            conn.close()
    
    def search_content(self, query: str, limit: int = 50) -> List[Dict]:
        """Simple text search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content_type, source, title, content_data, created_at
            FROM archived_content 
            WHERE content_data LIKE ? OR title LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            content_id, content_type, source, title, content_data, created_at = row
            results.append({
                "content_id": content_id,
                "content_type": content_type,
                "source": source,
                "title": title,
                "content_snippet": content_data[:200] + "..." if len(content_data) > 200 else content_data,
                "created_at": created_at
            })
        
        conn.close()
        return results
    
    def get_stats(self) -> Dict:
        """Get archive statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total items
        cursor.execute("SELECT COUNT(*) FROM archived_content")
        total_items = cursor.fetchone()[0]
        
        # Content types
        cursor.execute("SELECT content_type, COUNT(*) FROM archived_content GROUP BY content_type")
        content_types = dict(cursor.fetchall())
        
        # Sources
        cursor.execute("SELECT source, COUNT(*) FROM archived_content GROUP BY source")
        sources = dict(cursor.fetchall())
        
        # Total size
        cursor.execute("SELECT SUM(file_size) FROM archived_content")
        total_size = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_items": total_items,
            "content_types": content_types,
            "sources": sources,
            "total_size_bytes": total_size
        }

# Simple FastAPI app if available
if FASTAPI_AVAILABLE:
    app = FastAPI(title="Simple Archive API", version="1.0.0")
    storage = SimpleArchiveStorage()
    
    @app.post("/ingest")
    async def ingest_content(
        content_type: str = Form(...),
        source: str = Form(...),
        title: str = Form(None),
        data: str = Form(None),
        file: UploadFile = File(None)
    ):
        """Ingest content"""
        if file:
            content = await file.read()
            content_data = content.decode('utf-8', errors='ignore')
            title = title or file.filename
        elif data:
            content_data = data
        else:
            raise HTTPException(status_code=400, detail="Either file or data required")
        
        result = storage.add_content(content_type, source, content_data, title)
        return result
    
    @app.post("/search")
    async def search_content(query: str = Form(...), limit: int = Form(50)):
        """Search content"""
        results = storage.search_content(query, limit)
        return {"query": query, "results": results, "total": len(results)}
    
    @app.get("/stats")
    async def get_stats():
        """Get statistics"""
        return storage.get_stats()
    
    @app.get("/health")
    async def health_check():
        """Health check"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Command line interface for testing
def cli_interface():
    """Simple CLI for testing"""
    storage = SimpleArchiveStorage()
    
    print("🗄️  Simple Archive API - CLI Mode")
    print("================================")
    
    while True:
        print("\nOptions:")
        print("1. Add content")
        print("2. Search content") 
        print("3. View stats")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            content_type = input("Content type: ").strip()
            source = input("Source: ").strip()
            title = input("Title: ").strip()
            data = input("Content data: ").strip()
            
            result = storage.add_content(content_type, source, data, title)
            print(f"Result: {result}")
        
        elif choice == "2":
            query = input("Search query: ").strip()
            results = storage.search_content(query)
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results[:5], 1):
                print(f"{i}. {result['title']} ({result['content_type']}) - {result['source']}")
                print(f"   {result['content_snippet']}")
        
        elif choice == "3":
            stats = storage.get_stats()
            print(f"\nArchive Statistics:")
            print(f"Total items: {stats['total_items']}")
            print(f"Total size: {stats['total_size_bytes']} bytes")
            print(f"Content types: {stats['content_types']}")
            print(f"Sources: {stats['sources']}")
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        print("🚀 Starting Simple Archive API on port 7200...")
        uvicorn.run(app, host="0.0.0.0", port=7200)
    else:
        print("⚠️  FastAPI not available, running CLI mode...")
        cli_interface()
