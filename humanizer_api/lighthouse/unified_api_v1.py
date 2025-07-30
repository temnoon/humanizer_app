#!/usr/bin/env python3
"""
Unified API v1 - Core Pipeline Implementation
Quantum-aware narrative processing with local-first architecture
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import hashlib
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import uuid
import re
from dataclasses import dataclass
import logging
from embedding_service import get_embedding_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified Narrative API v1", version="1.0.0")

# ============================================================================
# Data Models (Pydantic schemas)
# ============================================================================

class Provenance(BaseModel):
    uri: str
    captured_at: str
    platform: str
    metadata: Dict[str, Any] = {}

class Source(BaseModel):
    schema_version: str = "1.0"
    source_id: str
    kind: str  # file|conversation|web|transcript|note|other
    title: Optional[str] = None
    provenance: Provenance
    license_hint: str = "unknown"
    hash: Dict[str, str]
    size_bytes: int

class DocumentStructure(BaseModel):
    type: str  # markdown|plaintext|pdf|json|html
    toc: List[Dict[str, Any]] = []

class Document(BaseModel):
    schema_version: str = "1.0"
    doc_id: str
    source_ids: List[str]
    mime: str
    lang: str = "en"
    structure: DocumentStructure
    text_bytes: int
    created_at: str

class EmbeddingInfo(BaseModel):
    model: str
    dim: int
    vector: Optional[str] = None  # base64 or omitted
    norm: float = 1.0
    faiss_id: Optional[int] = None

class ChunkSpan(BaseModel):
    start: int
    end: int

class Chunk(BaseModel):
    schema_version: str = "1.0"
    chunk_id: str
    doc_id: str
    span: ChunkSpan
    text: str
    section_ref: Optional[str] = None
    embedding: Optional[EmbeddingInfo] = None
    attributes: List[str] = []  # attribute_ids
    extracted_at: str

class AttributeEvidence(BaseModel):
    span: ChunkSpan
    quote: str

class AttributeMethod(BaseModel):
    family: str
    model: str
    calibration: str
    notes: Optional[str] = None

class AttributeScores(BaseModel):
    coherence_with_kernel: float
    support_across_doc: float

class Attribute(BaseModel):
    schema_version: str = "1.0"
    attribute_id: str
    chunk_id: str
    type: str  # namespace|persona|style|motif|theme|claim|citation
    value: str
    confidence: float
    evidence: AttributeEvidence
    method: AttributeMethod
    scores: AttributeScores
    time_extracted: str

class MeaningInfo(BaseModel):
    faiss_ids: List[int]
    dim: int
    model: str
    centroid_norm: float

class AttributePosterior(BaseModel):
    type: str
    distribution: List[Dict[str, Union[str, float]]]

class KernelLineage(BaseModel):
    parents: List[str]
    built_at: str

class Kernel(BaseModel):
    schema_version: str = "1.0"
    kernel_id: str
    scope: Dict[str, Any]
    meaning: MeaningInfo
    attribute_posteriors: List[AttributePosterior]
    claim_graph: Dict[str, Any] = {"nodes": [], "edges": []}
    lineage: KernelLineage

class ProjectionConstraints(BaseModel):
    namespace: Optional[str] = None
    persona: Optional[str] = None
    style: Optional[str] = None
    length: Optional[str] = None
    structure: Optional[str] = None
    citations: Optional[bool] = False

class ProjectionSection(BaseModel):
    section_ref: str
    text: str

class ProjectionRender(BaseModel):
    doc_like: bool
    structure_preserved: bool
    sections: List[ProjectionSection]

class ProjectionFaithfulness(BaseModel):
    kernel_alignment: float
    self_bleu: Optional[float] = None

class ProjectionReproducibility(BaseModel):
    seed: int
    models: Dict[str, str]

class Projection(BaseModel):
    schema_version: str = "1.0"
    projection_id: str
    kernel_id: str
    constraints: ProjectionConstraints
    render: ProjectionRender
    faithfulness: ProjectionFaithfulness
    reproducibility: ProjectionReproducibility
    built_at: str

# Request/Response models
class IngestRequest(BaseModel):
    source: Dict[str, Any]
    document: Dict[str, Any]
    chunking: Dict[str, Any] = {"max_tokens": 600, "overlap_pct": 0.12, "structure_breaks": True}

class SearchRequest(BaseModel):
    text: Optional[str] = None
    embedding: Optional[List[float]] = None
    attribute_filters: Optional[Dict[str, List[str]]] = None
    k: int = 10
    return_embeddings: bool = False

class SearchResult(BaseModel):
    rank: int
    faiss_id: int
    chunk_id: str
    doc_id: str
    section_ref: Optional[str]
    text_preview: str
    similarity_score: float
    l2_distance: float
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

class IngestResponse(BaseModel):
    doc_id: str
    chunk_ids: List[str]

class EmbedRequest(BaseModel):
    chunk_ids: List[str]
    model: str = "local-embed-e5-base-v1"

class AttributesRequest(BaseModel):
    chunk_ids: List[str]
    families: List[str] = ["style_probe_v2", "persona_probe_v1", "namespace_probe_v1"]

class KernelRequest(BaseModel):
    chunk_ids: List[str]
    aggregation: str = "weighted"

class ProjectRequest(BaseModel):
    kernel_id: str
    constraints: ProjectionConstraints
    preserve_document_structure: bool = True
    section_map: Optional[List[str]] = None
    reproducibility: ProjectionReproducibility

# ============================================================================
# Storage Layer
# ============================================================================

class UnifiedStorage:
    def __init__(self, db_path: str = "unified_catalog.db"):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialize SQLite catalog"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                kind TEXT,
                title TEXT,
                provenance TEXT,
                license_hint TEXT,
                hash TEXT,
                size_bytes INTEGER,
                created_at TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                source_ids TEXT,
                mime TEXT,
                lang TEXT,
                structure TEXT,
                text_bytes INTEGER,
                content_hash TEXT,
                created_at TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT,
                span_start INTEGER,
                span_end INTEGER,
                text TEXT,
                section_ref TEXT,
                embedding_model TEXT,
                embedding_dim INTEGER,
                faiss_id INTEGER,
                extracted_at TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attributes (
                attribute_id TEXT PRIMARY KEY,
                chunk_id TEXT,
                type TEXT,
                value TEXT,
                confidence REAL,
                evidence TEXT,
                method TEXT,
                scores TEXT,
                time_extracted TEXT,
                FOREIGN KEY (chunk_id) REFERENCES chunks (chunk_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kernels (
                kernel_id TEXT PRIMARY KEY,
                scope TEXT,
                meaning TEXT,
                attribute_posteriors TEXT,
                claim_graph TEXT,
                lineage TEXT,
                built_at TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projections (
                projection_id TEXT PRIMARY KEY,
                kernel_id TEXT,
                constraints TEXT,
                render TEXT,
                faithfulness TEXT,
                reproducibility TEXT,
                built_at TEXT,
                FOREIGN KEY (kernel_id) REFERENCES kernels (kernel_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_source(self, source: Source):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO sources 
            (source_id, kind, title, provenance, license_hint, hash, size_bytes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source.source_id, source.kind, source.title,
            json.dumps(source.provenance.dict()), source.license_hint,
            json.dumps(source.hash), source.size_bytes,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        conn.close()
    
    def store_document(self, document: Document, content: str):
        conn = sqlite3.connect(self.db_path)
        content_hash = hashlib.blake2b(content.encode()).hexdigest()
        conn.execute("""
            INSERT OR REPLACE INTO documents
            (doc_id, source_ids, mime, lang, structure, text_bytes, content_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document.doc_id, json.dumps(document.source_ids), document.mime,
            document.lang, json.dumps(document.structure.dict()),
            document.text_bytes, content_hash, document.created_at
        ))
        conn.commit()
        conn.close()
        
        # Store content in blob storage
        content_path = Path(f"content_blobs/{content_hash}")
        content_path.parent.mkdir(exist_ok=True)
        content_path.write_text(content)
    
    def store_chunk(self, chunk: Chunk):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO chunks
            (chunk_id, doc_id, span_start, span_end, text, section_ref, 
             embedding_model, embedding_dim, faiss_id, extracted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk.chunk_id, chunk.doc_id, chunk.span.start, chunk.span.end,
            chunk.text, chunk.section_ref,
            chunk.embedding.model if chunk.embedding else None,
            chunk.embedding.dim if chunk.embedding else None,
            chunk.embedding.faiss_id if chunk.embedding else None,
            chunk.extracted_at
        ))
        conn.commit()
        conn.close()
    
    def store_attribute(self, attribute: Attribute):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO attributes
            (attribute_id, chunk_id, type, value, confidence, evidence, method, scores, time_extracted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attribute.attribute_id, attribute.chunk_id, attribute.type,
            attribute.value, attribute.confidence,
            json.dumps(attribute.evidence.dict()),
            json.dumps(attribute.method.dict()),
            json.dumps(attribute.scores.dict()),
            attribute.time_extracted
        ))
        conn.commit()
        conn.close()
    
    def store_kernel(self, kernel: Kernel):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO kernels
            (kernel_id, scope, meaning, attribute_posteriors, claim_graph, lineage, built_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            kernel.kernel_id, json.dumps(kernel.scope),
            json.dumps(kernel.meaning.dict()),
            json.dumps([ap.dict() for ap in kernel.attribute_posteriors]),
            json.dumps(kernel.claim_graph),
            json.dumps(kernel.lineage.dict()),
            kernel.lineage.built_at
        ))
        conn.commit()
        conn.close()
    
    def store_projection(self, projection: Projection):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO projections
            (projection_id, kernel_id, constraints, render, faithfulness, reproducibility, built_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            projection.projection_id, projection.kernel_id,
            json.dumps(projection.constraints.dict()),
            json.dumps(projection.render.dict()),
            json.dumps(projection.faithfulness.dict()),
            json.dumps(projection.reproducibility.dict()),
            projection.built_at
        ))
        conn.commit()
        conn.close()
    
    def get_chunks_by_doc(self, doc_id: str) -> List[Chunk]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT chunk_id, doc_id, span_start, span_end, text, section_ref,
                   embedding_model, embedding_dim, faiss_id, extracted_at
            FROM chunks WHERE doc_id = ?
        """, (doc_id,))
        
        chunks = []
        for row in cursor.fetchall():
            embedding = None
            if row[6]:  # embedding_model exists
                embedding = EmbeddingInfo(
                    model=row[6], dim=row[7], faiss_id=row[8]
                )
            
            chunk = Chunk(
                chunk_id=row[0],
                doc_id=row[1],
                span=ChunkSpan(start=row[2], end=row[3]),
                text=row[4],
                section_ref=row[5],
                embedding=embedding,
                extracted_at=row[9]
            )
            chunks.append(chunk)
        
        conn.close()
        return chunks

# Global storage instance
storage = UnifiedStorage()

# ============================================================================
# Text Processing Utils
# ============================================================================

def blake3_hash(text: str) -> str:
    """Generate blake3 hash for content addressing"""
    return hashlib.blake2b(text.encode()).hexdigest()[:32]

def chunk_text(text: str, max_tokens: int = 600, overlap_pct: float = 0.12) -> List[Dict[str, Any]]:
    """Simple text chunking with overlap"""
    # Rough tokenization (words as proxy for tokens)
    words = text.split()
    chunk_size = max_tokens
    overlap_size = int(chunk_size * overlap_pct)
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(words):
        end_idx = min(start_idx + chunk_size, len(words))
        chunk_words = words[start_idx:end_idx]
        chunk_text = " ".join(chunk_words)
        
        # Calculate character offsets
        char_start = len(" ".join(words[:start_idx]))
        if start_idx > 0:
            char_start += 1  # account for space
        char_end = char_start + len(chunk_text)
        
        chunks.append({
            "text": chunk_text,
            "span": {"start": char_start, "end": char_end},
            "word_count": len(chunk_words)
        })
        
        # Move start with overlap
        start_idx = end_idx - overlap_size
        if start_idx >= len(words):
            break
    
    return chunks

def extract_mock_attributes(text: str, families: List[str]) -> List[Dict[str, Any]]:
    """Mock attribute extraction for prototype"""
    attributes = []
    
    # Simple heuristic-based attribute extraction
    text_lower = text.lower()
    
    if "style_probe_v2" in families:
        if any(word in text_lower for word in ["analysis", "evidence", "conclusion"]):
            style = "analytical_writing"
            confidence = 0.85
        elif any(word in text_lower for word in ["beautiful", "flowing", "graceful"]):
            style = "lyrical_prose"
            confidence = 0.78
        else:
            style = "formal_literary"
            confidence = 0.72
            
        attributes.append({
            "type": "style",
            "value": style,
            "confidence": confidence,
            "family": "style_probe_v2"
        })
    
    if "persona_probe_v1" in families:
        if any(word in text_lower for word in ["we examine", "this study", "research"]):
            persona = "analytical_observer"
            confidence = 0.82
        elif any(word in text_lower for word in ["dear reader", "you might wonder"]):
            persona = "intimate_storyteller"
            confidence = 0.89
        else:
            persona = "authoritative_narrator"
            confidence = 0.75
            
        attributes.append({
            "type": "persona",
            "value": persona,
            "confidence": confidence,
            "family": "persona_probe_v1"
        })
    
    if "namespace_probe_v1" in families:
        if any(word in text_lower for word in ["methodology", "hypothesis", "data"]):
            namespace = "academic_discourse"
            confidence = 0.87
        elif any(word in text_lower for word in ["story", "narrative", "character"]):
            namespace = "literary_fiction"
            confidence = 0.84
        else:
            namespace = "general_prose"
            confidence = 0.70
            
        attributes.append({
            "type": "namespace",
            "value": namespace,
            "confidence": confidence,
            "family": "namespace_probe_v1"
        })
    
    return attributes

def generate_real_embedding(text: str, model: str = "all-mpnet-base-v2") -> np.ndarray:
    """Generate real embedding using sentence-transformers"""
    embedding_service = get_embedding_service()
    return embedding_service.embed_text(text)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/v1/health")
async def health_check():
    embedding_service = get_embedding_service()
    stats = embedding_service.get_stats()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "capabilities": {
            "embedding_models": [stats["model_name"]],
            "attribute_families": ["style_probe_v2", "persona_probe_v1", "namespace_probe_v1"],
            "max_embedding_dim": stats["embedding_dim"]
        },
        "index_stats": stats
    }

@app.post("/v1/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest and normalize document with chunking"""
    
    # Extract content based on document type
    doc_data = request.document
    if doc_data["mime"] == "application/json":
        # Handle conversation format
        messages = doc_data["content"]["messages"]
        content = "\n\n".join([f"{msg['role']}: {msg['text']}" for msg in messages])
    else:
        content = doc_data.get("content", "")
    
    # Generate IDs
    content_hash = blake3_hash(content)
    doc_id = f"doc_{content_hash}"
    source_id = f"src_{blake3_hash(json.dumps(request.source))}"
    
    # Create and store source
    source = Source(
        source_id=source_id,
        kind=request.source["kind"],
        title=request.source.get("title"),
        provenance=Provenance(**request.source["provenance"]),
        hash={"algo": "blake3", "value": content_hash},
        size_bytes=len(content.encode())
    )
    storage.store_source(source)
    
    # Create and store document
    document = Document(
        doc_id=doc_id,
        source_ids=[source_id],
        mime=doc_data["mime"],
        structure=DocumentStructure(**doc_data["structure"]),
        text_bytes=len(content.encode()),
        created_at=datetime.now(timezone.utc).isoformat()
    )
    storage.store_document(document, content)
    
    # Chunk the text
    text_chunks = chunk_text(
        content,
        max_tokens=request.chunking["max_tokens"],
        overlap_pct=request.chunking["overlap_pct"]
    )
    
    # Create and store chunks
    chunk_ids = []
    for i, chunk_data in enumerate(text_chunks):
        chunk_hash = blake3_hash(chunk_data["text"])
        chunk_id = f"chk_{doc_id}_{i}_{chunk_hash[:8]}"
        
        chunk = Chunk(
            chunk_id=chunk_id,
            doc_id=doc_id,
            span=ChunkSpan(**chunk_data["span"]),
            text=chunk_data["text"],
            extracted_at=datetime.now(timezone.utc).isoformat()
        )
        
        storage.store_chunk(chunk)
        chunk_ids.append(chunk_id)
    
    logger.info(f"Ingested document {doc_id} with {len(chunk_ids)} chunks")
    return IngestResponse(doc_id=doc_id, chunk_ids=chunk_ids)

@app.post("/v1/embed")
async def embed_chunks(request: EmbedRequest):
    """Generate embeddings for chunks and store in FAISS"""
    
    # Get chunk data from database
    chunks_data = []
    conn = sqlite3.connect(storage.db_path)
    
    for chunk_id in request.chunk_ids:
        cursor = conn.execute("""
            SELECT chunk_id, doc_id, text, section_ref FROM chunks WHERE chunk_id = ?
        """, (chunk_id,))
        row = cursor.fetchone()
        if row:
            chunks_data.append({
                "chunk_id": row[0],
                "doc_id": row[1], 
                "text": row[2],
                "section_ref": row[3]
            })
    
    conn.close()
    
    if not chunks_data:
        raise HTTPException(status_code=404, detail="No chunks found")
    
    # Get embedding service and add chunks
    embedding_service = get_embedding_service()
    
    # Prepare chunks for batch embedding
    embedding_chunks = []
    for chunk_data in chunks_data:
        embedding_chunks.append({
            'chunk_id': chunk_data['chunk_id'],
            'text': chunk_data['text'],
            'doc_id': chunk_data['doc_id'],
            'section_ref': chunk_data['section_ref']
        })
    
    # Add embeddings to FAISS index
    faiss_ids = embedding_service.add_batch_embeddings(embedding_chunks)
    
    # Update chunks table with embedding info
    conn = sqlite3.connect(storage.db_path)
    for i, chunk_data in enumerate(chunks_data):
        faiss_id = faiss_ids[i]
        conn.execute("""
            UPDATE chunks SET embedding_model = ?, embedding_dim = ?, faiss_id = ?
            WHERE chunk_id = ?
        """, (embedding_service.model_name, embedding_service.embedding_dim, faiss_id, chunk_data["chunk_id"]))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Generated real embeddings for {len(chunks_data)} chunks using {embedding_service.model_name}")
    return {
        "embedded_count": len(chunks_data), 
        "model": embedding_service.model_name, 
        "dim": embedding_service.embedding_dim,
        "faiss_ids": faiss_ids
    }

@app.post("/v1/attributes")
async def extract_attributes(request: AttributesRequest):
    """Extract attributes using POVM-based probes"""
    
    # Get chunks
    chunks = []
    conn = sqlite3.connect(storage.db_path)
    
    for chunk_id in request.chunk_ids:
        cursor = conn.execute("""
            SELECT chunk_id, text, span_start, span_end FROM chunks WHERE chunk_id = ?
        """, (chunk_id,))
        row = cursor.fetchone()
        if row:
            chunks.append({
                "chunk_id": row[0], 
                "text": row[1],
                "span_start": row[2],
                "span_end": row[3]
            })
    
    conn.close()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found")
    
    # Extract attributes for each chunk
    attribute_ids = []
    for chunk_data in chunks:
        mock_attrs = extract_mock_attributes(chunk_data["text"], request.families)
        
        for attr_data in mock_attrs:
            attr_hash = blake3_hash(f"{chunk_data['chunk_id']}_{attr_data['type']}_{attr_data['value']}")
            attribute_id = f"att_{attr_hash[:16]}"
            
            # Create evidence (sample span)
            evidence_start = chunk_data["span_start"]
            evidence_end = min(chunk_data["span_start"] + 100, chunk_data["span_end"])
            
            attribute = Attribute(
                attribute_id=attribute_id,
                chunk_id=chunk_data["chunk_id"],
                type=attr_data["type"],
                value=attr_data["value"],
                confidence=attr_data["confidence"],
                evidence=AttributeEvidence(
                    span=ChunkSpan(start=evidence_start, end=evidence_end),
                    quote=chunk_data["text"][:100] + "..."
                ),
                method=AttributeMethod(
                    family=attr_data["family"],
                    model="mock-v1",
                    calibration="calib_2025_07"
                ),
                scores=AttributeScores(
                    coherence_with_kernel=0.85,
                    support_across_doc=0.72
                ),
                time_extracted=datetime.now(timezone.utc).isoformat()
            )
            
            storage.store_attribute(attribute)
            attribute_ids.append(attribute_id)
    
    logger.info(f"Extracted {len(attribute_ids)} attributes from {len(chunks)} chunks")
    return {"attribute_ids": attribute_ids, "families_used": request.families}

@app.post("/v1/kernel")
async def build_kernel(request: KernelRequest):
    """Build kernel (ρ snapshot) from chunks and attributes"""
    
    # Get chunks with embeddings
    chunks = []
    conn = sqlite3.connect(storage.db_path)
    
    for chunk_id in request.chunk_ids:
        cursor = conn.execute("""
            SELECT chunk_id, faiss_id, embedding_model, embedding_dim FROM chunks 
            WHERE chunk_id = ? AND faiss_id IS NOT NULL
        """, (chunk_id,))
        row = cursor.fetchone()
        if row:
            chunks.append({
                "chunk_id": row[0],
                "faiss_id": row[1],
                "model": row[2],
                "dim": row[3]
            })
    
    # Get attributes for these chunks
    chunk_ids_str = ",".join([f"'{cid}'" for cid in request.chunk_ids])
    cursor = conn.execute(f"""
        SELECT type, value, confidence FROM attributes 
        WHERE chunk_id IN ({chunk_ids_str})
    """)
    
    attribute_rows = cursor.fetchall()
    conn.close()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks with embeddings found")
    
    # Build attribute posteriors
    attribute_groups = {}
    for attr_type, attr_value, confidence in attribute_rows:
        if attr_type not in attribute_groups:
            attribute_groups[attr_type] = {}
        if attr_value not in attribute_groups[attr_type]:
            attribute_groups[attr_type][attr_value] = []
        attribute_groups[attr_type][attr_value].append(confidence)
    
    # Normalize to posteriors
    attribute_posteriors = []
    for attr_type, values in attribute_groups.items():
        # Average confidences and normalize
        value_probs = {}
        total_conf = 0
        for value, confidences in values.items():
            avg_conf = sum(confidences) / len(confidences)
            value_probs[value] = avg_conf
            total_conf += avg_conf
        
        # Normalize
        if total_conf > 0:
            distribution = [
                {"value": value, "p": prob / total_conf}
                for value, prob in value_probs.items()
            ]
        else:
            distribution = []
        
        attribute_posteriors.append(AttributePosterior(
            type=attr_type,
            distribution=distribution
        ))
    
    # Compute real centroid using embedding service
    embedding_service = get_embedding_service()
    chunk_ids = [c["chunk_id"] for c in chunks]
    centroid = embedding_service.compute_centroid(chunk_ids)
    centroid_norm = float(np.linalg.norm(centroid)) if centroid is not None else 1.0
    
    # Create kernel
    kernel_hash = blake3_hash(f"kernel_{request.chunk_ids}_{request.aggregation}")
    kernel_id = f"ker_{kernel_hash[:16]}"
    
    kernel = Kernel(
        kernel_id=kernel_id,
        scope={
            "chunk_ids": request.chunk_ids,
            "aggregation": request.aggregation
        },
        meaning=MeaningInfo(
            faiss_ids=[c["faiss_id"] for c in chunks],
            dim=chunks[0]["dim"] if chunks else embedding_service.embedding_dim,
            model=chunks[0]["model"] if chunks else embedding_service.model_name,
            centroid_norm=centroid_norm
        ),
        attribute_posteriors=attribute_posteriors,
        lineage=KernelLineage(
            parents=[],
            built_at=datetime.now(timezone.utc).isoformat()
        )
    )
    
    storage.store_kernel(kernel)
    
    logger.info(f"Built kernel {kernel_id} from {len(chunks)} chunks with {len(attribute_posteriors)} attribute types")
    return {"kernel_id": kernel_id, "chunk_count": len(chunks), "attribute_types": len(attribute_posteriors)}

@app.post("/v1/project", response_model=Projection)
async def project_narrative(request: ProjectRequest):
    """Project narrative with structure preservation"""
    
    # Get kernel
    conn = sqlite3.connect(storage.db_path)
    cursor = conn.execute("""
        SELECT scope, meaning, attribute_posteriors FROM kernels WHERE kernel_id = ?
    """, (request.kernel_id,))
    
    kernel_row = cursor.fetchone()
    if not kernel_row:
        raise HTTPException(status_code=404, detail="Kernel not found")
    
    scope = json.loads(kernel_row[0])
    meaning = json.loads(kernel_row[1])
    attribute_posteriors = json.loads(kernel_row[2])
    
    # Get original chunks to preserve structure
    chunk_ids = scope["chunk_ids"]
    chunks = []
    for chunk_id in chunk_ids:
        cursor = conn.execute("""
            SELECT chunk_id, text, section_ref FROM chunks WHERE chunk_id = ?
        """, (chunk_id,))
        row = cursor.fetchone()
        if row:
            chunks.append({
                "chunk_id": row[0],
                "text": row[1], 
                "section_ref": row[2] or f"section_{len(chunks)}"
            })
    
    conn.close()
    
    # Mock projection transformation
    projected_sections = []
    for chunk in chunks:
        # Simple mock transformation based on constraints
        original_text = chunk["text"]
        projected_text = original_text
        
        # Apply namespace transformation
        if request.constraints.namespace == "academic_review":
            projected_text = f"In reviewing this content: {projected_text}"
            if "demonstrates" not in projected_text:
                projected_text = projected_text.replace("shows", "demonstrates")
        
        # Apply persona transformation  
        if request.constraints.persona == "reviewer":
            projected_text = projected_text.replace("I think", "This analysis suggests")
            projected_text = projected_text.replace("it seems", "the evidence indicates")
        
        # Apply style transformation
        if request.constraints.style == "concise":
            # Mock: truncate to simulate conciseness
            words = projected_text.split()
            if len(words) > 100:
                projected_text = " ".join(words[:100]) + "..."
        
        projected_sections.append(ProjectionSection(
            section_ref=chunk["section_ref"],
            text=projected_text
        ))
    
    # Create projection
    projection_hash = blake3_hash(f"proj_{request.kernel_id}_{json.dumps(request.constraints.dict())}")
    projection_id = f"proj_{projection_hash[:16]}"
    
    projection = Projection(
        projection_id=projection_id,
        kernel_id=request.kernel_id,
        constraints=request.constraints,
        render=ProjectionRender(
            doc_like=True,
            structure_preserved=request.preserve_document_structure,
            sections=projected_sections
        ),
        faithfulness=ProjectionFaithfulness(
            kernel_alignment=0.87,  # Mock score
            self_bleu=0.42
        ),
        reproducibility=request.reproducibility,
        built_at=datetime.now(timezone.utc).isoformat()
    )
    
    storage.store_projection(projection)
    
    logger.info(f"Created projection {projection_id} with {len(projected_sections)} sections")
    return projection

@app.post("/v1/search")
async def search_chunks(request: SearchRequest) -> List[SearchResult]:
    """Search for similar chunks using text or embedding query"""
    
    embedding_service = get_embedding_service()
    
    if request.text:
        # Text-based search
        results = embedding_service.search_similar(
            query=request.text,
            k=request.k,
            return_embeddings=request.return_embeddings
        )
    elif request.embedding:
        # Embedding-based search
        query_embedding = np.array(request.embedding, dtype=np.float32)
        results = embedding_service.search_by_embedding(
            embedding=query_embedding,
            k=request.k,
            return_embeddings=request.return_embeddings
        )
    else:
        raise HTTPException(status_code=400, detail="Either 'text' or 'embedding' must be provided")
    
    # Filter by attributes if specified
    if request.attribute_filters:
        filtered_results = []
        conn = sqlite3.connect(storage.db_path)
        
        for result in results:
            chunk_id = result['chunk_id']
            
            # Check if chunk matches attribute filters
            matches_filters = True
            for attr_type, allowed_values in request.attribute_filters.items():
                cursor = conn.execute("""
                    SELECT value FROM attributes 
                    WHERE chunk_id = ? AND type = ?
                """, (chunk_id, attr_type))
                
                chunk_values = [row[0] for row in cursor.fetchall()]
                if not any(value in allowed_values for value in chunk_values):
                    matches_filters = False
                    break
            
            if matches_filters:
                filtered_results.append(result)
        
        conn.close()
        results = filtered_results[:request.k]
    
    # Convert to Pydantic models
    search_results = []
    for result in results:
        search_result = SearchResult(
            rank=result['rank'],
            faiss_id=result['faiss_id'],
            chunk_id=result['chunk_id'],
            doc_id=result['doc_id'],
            section_ref=result['section_ref'],
            text_preview=result['text_preview'],
            similarity_score=result['similarity_score'],
            l2_distance=result['l2_distance'],
            metadata=result['metadata'],
            embedding=result.get('embedding')
        )
        search_results.append(search_result)
    
    logger.info(f"Search returned {len(search_results)} results")
    return search_results

@app.get("/v1/embedding-stats")
async def get_embedding_stats():
    """Get embedding service statistics"""
    embedding_service = get_embedding_service()
    return embedding_service.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8101)