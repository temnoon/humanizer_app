"""
Export Router for Enhanced Lighthouse API
==========================================

Provides export functionality for generated books, conversations, and insights
to various formats including Joplin, Discourse, and Writebook.
"""

import os
import json
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import xml.etree.ElementTree as ET

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Export Router
export_router = APIRouter(prefix="/api/export", tags=["export"])

# Pydantic Models for Export Operations
class ExportOptions(BaseModel):
    """Export configuration options."""
    includeImages: bool = Field(default=True, description="Include images in export")
    includeMetadata: bool = Field(default=True, description="Include metadata")
    preserveFormatting: bool = Field(default=True, description="Preserve text formatting")
    generateToc: bool = Field(default=True, description="Generate table of contents")
    compressOutput: bool = Field(default=False, description="Compress output files")

class ExportRequest(BaseModel):
    """Export request with content selection."""
    content_ids: List[str] = Field(..., description="IDs of content to export")
    options: ExportOptions = Field(default_factory=ExportOptions)

class ExportResult(BaseModel):
    """Result of export operation."""
    success: bool
    export_id: str
    filename: str
    file_size: str
    download_url: str
    format: str
    content_count: int
    created_at: datetime
    
class BookExportData(BaseModel):
    """Structure for book export data."""
    id: str
    title: str
    chapters: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: str
    quality_score: float
    tags: List[str]

# Sample book data for demonstration (replace with real data from API)
SAMPLE_BOOKS = [
    BookExportData(
        id="book_1",
        title="Consciousness and Computing: Reflections on AI and Human Experience",
        chapters=[
            {
                "title": "Introduction: The Question of Machine Consciousness",
                "content": "The question of whether machines can truly be conscious has haunted philosophy and computer science for decades...",
                "section": 1
            },
            {
                "title": "The Hard Problem of Consciousness in AI",
                "content": "David Chalmers' formulation of the hard problem of consciousness presents unique challenges when applied to artificial intelligence...",
                "section": 2
            },
            {
                "title": "Phenomenological Approaches to Machine Experience",
                "content": "Drawing from Husserl and Merleau-Ponty, we can explore what machine experience might feel like from the inside...",
                "section": 3
            }
        ],
        metadata={
            "author": "HAW Book Generator",
            "generator": "Advanced Books Algorithm",
            "word_count": 12500,
            "themes": ["consciousness", "AI", "phenomenology"],
            "complexity_level": "advanced"
        },
        created_at="2025-08-03T10:30:00Z",
        quality_score=0.87,
        tags=["consciousness", "ai", "philosophy", "phenomenology"]
    ),
    BookExportData(
        id="book_2", 
        title="Quantum Narratives: Stories from the Edge of Reality",
        chapters=[
            {
                "title": "Superposition of Stories",
                "content": "In quantum mechanics, particles exist in multiple states simultaneously until observed. What if stories worked the same way?",
                "section": 1
            },
            {
                "title": "Entangled Plots",
                "content": "When two narrative threads become quantum entangled, changing one instantly affects the other, regardless of distance...",
                "section": 2
            }
        ],
        metadata={
            "author": "HAW Book Generator",
            "generator": "Universal Books Algorithm", 
            "word_count": 9800,
            "themes": ["quantum physics", "storytelling", "reality"],
            "complexity_level": "intermediate"
        },
        created_at="2025-08-03T15:45:00Z",
        quality_score=0.78,
        tags=["quantum", "storytelling", "physics", "narrative"]
    )
]

async def get_books_data() -> List[BookExportData]:
    """Fetch book data from the archive system."""
    try:
        # In production, this would call the actual API endpoints
        # For now, return sample data
        return SAMPLE_BOOKS
    except Exception as e:
        logger.error(f"Failed to fetch books data: {e}")
        return []

async def get_conversations_data(content_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch conversation data from the archive system."""
    try:
        # Sample conversation data
        return [
            {
                "id": "conv_1",
                "title": "Discussion on AI Ethics and Consciousness",
                "messages": [
                    {"role": "user", "content": "What are the ethical implications of conscious AI?"},
                    {"role": "assistant", "content": "The ethical implications are profound..."}
                ],
                "metadata": {"word_count": 2500, "participants": 2},
                "created_at": "2025-08-03T09:15:00Z",
                "quality_score": 0.82,
                "tags": ["ethics", "ai", "consciousness"]
            }
        ]
    except Exception as e:
        logger.error(f"Failed to fetch conversations data: {e}")
        return []

async def get_insights_data(content_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch insights data from the archive system."""
    try:
        # Sample insights data
        return [
            {
                "id": "insight_1",
                "title": "Emergent Properties in Complex Systems",
                "content": "Complex systems often exhibit emergent properties that cannot be predicted from their individual components...",
                "metadata": {"word_count": 800, "complexity": "high"},
                "created_at": "2025-08-03T14:20:00Z",
                "quality_score": 0.91,
                "tags": ["complexity", "emergence", "systems"]
            }
        ]
    except Exception as e:
        logger.error(f"Failed to fetch insights data: {e}")
        return []

def create_joplin_export(books: List[BookExportData], options: ExportOptions) -> str:
    """Create a Joplin .jex export file."""
    
    # Create temporary directory for export
    temp_dir = tempfile.mkdtemp()
    export_path = os.path.join(temp_dir, f"books_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jex")
    
    # Joplin export structure
    export_data = {
        "version": 1,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "generator": "Humanizer Lighthouse Export Hub",
            "book_count": len(books),
            "options": options.dict()
        },
        "folders": [],
        "notes": []
    }
    
    # Create a folder for each book
    for book in books:
        folder_id = f"folder_{book.id}"
        
        # Add folder
        export_data["folders"].append({
            "id": folder_id,
            "title": book.title,
            "created_time": int(datetime.now().timestamp() * 1000),
            "updated_time": int(datetime.now().timestamp() * 1000),
            "parent_id": ""
        })
        
        # Add book metadata note
        if options.includeMetadata:
            metadata_note = {
                "id": f"note_meta_{book.id}",
                "title": f"{book.title} - Metadata",
                "body": f"""# Book Metadata

**Title:** {book.title}
**Quality Score:** {book.quality_score:.2%}
**Created:** {book.created_at}
**Word Count:** {book.metadata.get('word_count', 'N/A')}
**Generator:** {book.metadata.get('generator', 'Unknown')}

**Tags:** {', '.join(book.tags)}
**Themes:** {', '.join(book.metadata.get('themes', []))}

**Generated by Humanizer Lighthouse Export Hub**
""",
                "created_time": int(datetime.now().timestamp() * 1000),
                "updated_time": int(datetime.now().timestamp() * 1000),
                "parent_id": folder_id,
                "is_todo": 0
            }
            export_data["notes"].append(metadata_note)
        
        # Add chapter notes
        for i, chapter in enumerate(book.chapters):
            chapter_note = {
                "id": f"note_{book.id}_ch{i}",
                "title": chapter["title"],
                "body": chapter["content"] if options.preserveFormatting else chapter["content"].replace('\n\n', '\n'),
                "created_time": int(datetime.now().timestamp() * 1000),
                "updated_time": int(datetime.now().timestamp() * 1000),
                "parent_id": folder_id,
                "is_todo": 0
            }
            export_data["notes"].append(chapter_note)
    
    # Create the .jex file (which is actually a tar.gz)
    import tarfile
    import json
    
    with tarfile.open(export_path, "w:gz") as tar:
        # Add the data as JSON
        json_data = json.dumps(export_data, indent=2)
        json_file = os.path.join(temp_dir, "data.json")
        with open(json_file, 'w') as f:
            f.write(json_data)
        tar.add(json_file, arcname="data.json")
    
    return export_path

def create_discourse_export(content: List[Dict[str, Any]], options: ExportOptions) -> str:
    """Create a Discourse-compatible JSON export."""
    
    temp_dir = tempfile.mkdtemp()
    export_path = os.path.join(temp_dir, f"discourse_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Discourse format structure
    discourse_data = {
        "meta": {
            "export_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "generator": "Humanizer Lighthouse",
            "content_count": len(content)
        },
        "categories": [
            {
                "id": 1,
                "name": "AI & Consciousness",
                "description": "Discussions about artificial intelligence and consciousness",
                "color": "3AB54A"
            },
            {
                "id": 2, 
                "name": "Philosophy",
                "description": "Philosophical insights and discussions",
                "color": "12A89D"
            }
        ],
        "topics": [],
        "posts": []
    }
    
    # Convert content to Discourse topics and posts
    for i, item in enumerate(content):
        topic_id = i + 1
        
        # Create topic
        topic = {
            "id": topic_id,
            "title": item.get("title", f"Imported Content {topic_id}"),
            "category_id": 1 if "ai" in item.get("tags", []) else 2,
            "created_at": item.get("created_at", datetime.now().isoformat()),
            "views": 0,
            "posts_count": 1,
            "archived": False,
            "closed": False
        }
        discourse_data["topics"].append(topic)
        
        # Create main post
        post = {
            "id": topic_id,
            "topic_id": topic_id,
            "post_number": 1,
            "raw": item.get("content", ""),
            "created_at": item.get("created_at", datetime.now().isoformat()),
            "username": "imported_user",
            "name": "Imported User"
        }
        
        # Add metadata if requested
        if options.includeMetadata and "metadata" in item:
            metadata_text = f"\n\n---\n**Metadata:**\n"
            for key, value in item["metadata"].items():
                metadata_text += f"- **{key.title()}:** {value}\n"
            post["raw"] += metadata_text
        
        discourse_data["posts"].append(post)
    
    # Write to file
    with open(export_path, 'w') as f:
        json.dump(discourse_data, f, indent=2)
    
    return export_path

def create_writebook_export(content: List[Dict[str, Any]], options: ExportOptions) -> str:
    """Create a Writebook-compatible export."""
    
    temp_dir = tempfile.mkdtemp()
    export_path = os.path.join(temp_dir, f"writebook_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    # Writebook format - structured markdown
    writebook_content = f"""# Exported Content from Humanizer Lighthouse

*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*

---

"""
    
    for i, item in enumerate(content):
        writebook_content += f"\n## {item.get('title', f'Content {i+1}')}\n\n"
        
        if options.includeMetadata and "metadata" in item:
            writebook_content += "**Metadata:**\n"
            for key, value in item["metadata"].items():
                writebook_content += f"- {key.title()}: {value}\n"
            writebook_content += "\n"
        
        # Add content
        content_text = item.get("content", "")
        if "chapters" in item:
            # Handle book format
            for chapter in item["chapters"]:
                writebook_content += f"### {chapter.get('title', 'Untitled Chapter')}\n\n"
                writebook_content += f"{chapter.get('content', '')}\n\n"
        else:
            writebook_content += f"{content_text}\n\n"
        
        writebook_content += "---\n\n"
    
    # Write to file
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(writebook_content)
    
    return export_path

def get_file_size(file_path: str) -> str:
    """Get human-readable file size."""
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# API Endpoints

@export_router.get("/books/list")
async def list_available_books():
    """Get list of available books for export."""
    books = await get_books_data()
    return {
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "chapters": len(book.chapters),
                "words": book.metadata.get("word_count", 0),
                "quality_score": book.quality_score,
                "created_at": book.created_at,
                "tags": book.tags
            }
            for book in books
        ]
    }

@export_router.post("/joplin")
async def export_to_joplin(request: ExportRequest):
    """Export content to Joplin .jex format."""
    try:
        # Get book data for the requested IDs
        all_books = await get_books_data()
        selected_books = [book for book in all_books if book.id in request.content_ids]
        
        if not selected_books:
            raise HTTPException(status_code=404, detail="No books found for the provided IDs")
        
        # Create Joplin export
        export_path = create_joplin_export(selected_books, request.options)
        file_size = get_file_size(export_path)
        
        # Generate export result
        export_id = f"joplin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = os.path.basename(export_path)
        
        return ExportResult(
            success=True,
            export_id=export_id,
            filename=filename,
            file_size=file_size,
            download_url=f"/api/export/download/{export_id}",
            format="joplin",
            content_count=len(selected_books),
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Joplin export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@export_router.post("/discourse")
async def export_to_discourse(request: ExportRequest):
    """Export content to Discourse JSON format."""
    try:
        # Get conversation data for the requested IDs
        conversations = await get_conversations_data(request.content_ids)
        
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found for the provided IDs")
        
        # Create Discourse export
        export_path = create_discourse_export(conversations, request.options)
        file_size = get_file_size(export_path)
        
        export_id = f"discourse_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = os.path.basename(export_path)
        
        return ExportResult(
            success=True,
            export_id=export_id,
            filename=filename,
            file_size=file_size,
            download_url=f"/api/export/download/{export_id}",
            format="discourse",
            content_count=len(conversations),
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Discourse export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@export_router.post("/writebook")
async def export_to_writebook(request: ExportRequest):
    """Export content to Writebook markdown format."""
    try:
        # Get mixed content data
        books = await get_books_data()
        selected_books = [book.dict() for book in books if book.id in request.content_ids]
        
        conversations = await get_conversations_data(request.content_ids)
        insights = await get_insights_data(request.content_ids)
        
        all_content = selected_books + conversations + insights
        
        if not all_content:
            raise HTTPException(status_code=404, detail="No content found for the provided IDs")
        
        # Create Writebook export
        export_path = create_writebook_export(all_content, request.options)
        file_size = get_file_size(export_path)
        
        export_id = f"writebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = os.path.basename(export_path)
        
        return ExportResult(
            success=True,
            export_id=export_id,
            filename=filename,
            file_size=file_size,
            download_url=f"/api/export/download/{export_id}",
            format="writebook",
            content_count=len(all_content),
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Writebook export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@export_router.get("/download/{export_id}")
async def download_export(export_id: str):
    """Download an exported file."""
    # In production, this would look up the file path from a database
    # For now, we'll simulate the download
    
    # Generate a sample file for demonstration
    temp_dir = tempfile.mkdtemp()
    sample_file = os.path.join(temp_dir, f"{export_id}.jex")
    
    with open(sample_file, 'w') as f:
        f.write(f"Sample export file for {export_id}\nGenerated at {datetime.now()}")
    
    return FileResponse(
        sample_file,
        media_type='application/octet-stream',
        filename=f"{export_id}.jex"
    )

@export_router.get("/formats")
async def get_export_formats():
    """Get available export formats and their capabilities."""
    return {
        "formats": [
            {
                "id": "joplin",
                "name": "Joplin Notes",
                "description": "Export as .jex file for Joplin import",
                "supports": ["books", "notes", "metadata", "hierarchical_structure"],
                "file_extension": "jex",
                "mime_type": "application/x-joplin-export"
            },
            {
                "id": "discourse", 
                "name": "Discourse Forum",
                "description": "Export as Discourse-compatible JSON",
                "supports": ["conversations", "topics", "posts", "categories"],
                "file_extension": "json",
                "mime_type": "application/json"
            },
            {
                "id": "writebook",
                "name": "Writebook",
                "description": "Export as Writebook-compatible Markdown",
                "supports": ["books", "chapters", "mixed_content", "markdown"],
                "file_extension": "md", 
                "mime_type": "text/markdown"
            }
        ]
    }

# Function to add export routes to main app
def add_export_routes(app):
    """Add export routes to the FastAPI application."""
    app.include_router(export_router)