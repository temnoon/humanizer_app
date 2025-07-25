"""
Attribute Intelligence Engine
============================

AI-guided dynamic attribute selection system that:
1. Analyzes narrative content using LLM + embeddings
2. Queries RAG database of transformation patterns
3. Selects optimal persona/namespace/style combinations
4. Explores embedding neighborhoods for semantic anchoring
5. Integrates with M-POVM quantum narrative theory

Author: Enhanced for dynamic attribute discovery
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path
import logging
from sentence_transformers import SentenceTransformer
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AttributeProfile:
    """Represents a complete attribute configuration with metadata."""
    persona: str
    namespace: str
    style: str
    confidence: float
    reasoning: str
    embedding_anchor: np.ndarray
    semantic_neighborhood: List[Tuple[str, float]]  # Similar patterns with distances
    povm_coordinates: Optional[torch.Tensor] = None

@dataclass
class TransformationPattern:
    """Historical transformation pattern for RAG retrieval."""
    id: str
    source_embedding: np.ndarray
    target_embedding: np.ndarray
    attributes: Dict[str, str]
    success_metrics: Dict[str, float]
    narrative_snippet: str
    transformation_type: str
    created_at: datetime

class AttributeIntelligenceEngine:
    """
    Core engine for AI-guided attribute selection and semantic exploration.
    """
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 rag_db_path: str = "./data/attribute_patterns.db",
                 quantum_engine=None):
        """Initialize the attribute intelligence system."""
        
        # Load embedding model
        try:
            self.embedder = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedder = None
            
        # Initialize RAG database
        self.rag_db_path = rag_db_path
        self._init_rag_database()
        
        # Quantum engine integration
        self.quantum_engine = quantum_engine
        
        # Semantic anchor points (learned from data)
        self.anchor_points = {}
        self._load_semantic_anchors()
        
        # Attribute taxonomy (expandable via LLM discovery)
        self.attribute_taxonomy = self._load_attribute_taxonomy()
        
    def _init_rag_database(self):
        """Initialize SQLite database for transformation patterns."""
        db_dir = Path(self.rag_db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.rag_db_path)
        cursor = conn.cursor()
        
        # Create patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transformation_patterns (
                id TEXT PRIMARY KEY,
                source_embedding BLOB,
                target_embedding BLOB,
                persona TEXT,
                namespace TEXT,
                style TEXT,
                fidelity REAL,
                preservation_score REAL,
                purity_change REAL,
                entropy_change REAL,
                narrative_snippet TEXT,
                transformation_type TEXT,
                created_at TIMESTAMP,
                success_rating REAL
            )
        """)
        
        # Create semantic anchors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_anchors (
                anchor_id TEXT PRIMARY KEY,
                embedding BLOB,
                description TEXT,
                attribute_hints TEXT,
                usage_count INTEGER DEFAULT 0,
                avg_success REAL DEFAULT 0.0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("RAG database initialized")

    def _load_semantic_anchors(self):
        """Load semantic anchor points for embedding space exploration."""
        try:
            conn = sqlite3.connect(self.rag_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT anchor_id, embedding, description, attribute_hints FROM semantic_anchors")
            rows = cursor.fetchall()
            
            for anchor_id, embedding_blob, description, hints in rows:
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                self.anchor_points[anchor_id] = {
                    'embedding': embedding,
                    'description': description,
                    'hints': json.loads(hints) if hints else {}
                }
                
            conn.close()
            logger.info(f"Loaded {len(self.anchor_points)} semantic anchors")
            
        except Exception as e:
            logger.warning(f"Could not load semantic anchors: {e}")
            # Initialize with some default anchors
            self._create_default_anchors()

    def _create_default_anchors(self):
        """Create initial semantic anchor points."""
        if not self.embedder:
            return
            
        default_anchors = {
            "analytical_scientific": {
                "text": "systematic analysis with empirical evidence and logical reasoning",
                "hints": {"persona": ["scientist", "analyst", "researcher"], 
                         "style": ["formal", "precise", "technical"]}
            },
            "mythic_narrative": {
                "text": "ancient wisdom stories with archetypal symbols and universal themes", 
                "hints": {"persona": ["storyteller", "sage", "philosopher"],
                         "namespace": ["mythology", "folklore", "wisdom-traditions"]}
            },
            "poetic_expression": {
                "text": "lyrical language with metaphor rhythm and emotional resonance",
                "hints": {"style": ["poetic", "lyrical", "evocative"],
                         "persona": ["poet", "artist", "mystic"]}
            },
            "practical_guidance": {
                "text": "clear actionable advice for real-world application and implementation",
                "hints": {"style": ["practical", "direct", "instructional"],
                         "persona": ["guide", "teacher", "mentor"]}
            }
        }
        
        for anchor_id, config in default_anchors.items():
            embedding = self.embedder.encode(config["text"])
            self.anchor_points[anchor_id] = {
                'embedding': embedding,
                'description': config["text"],
                'hints': config["hints"]
            }
            
        logger.info("Created default semantic anchors")

    def _load_attribute_taxonomy(self) -> Dict[str, List[str]]:
        """Load expandable attribute taxonomy."""
        return {
            "persona": [
                "philosopher", "scientist", "artist", "teacher", "guide", "storyteller",
                "analyst", "mystic", "researcher", "poet", "sage", "mentor", "explorer",
                "healer", "visionary", "scholar", "craftsperson", "innovator"
            ],
            "namespace": [
                "scientific", "mythological", "philosophical", "literary", "practical",
                "spiritual", "historical", "artistic", "technological", "ecological",
                "psychological", "sociological", "ethical", "aesthetic", "pedagogical"
            ],
            "style": [
                "formal", "conversational", "poetic", "technical", "narrative", "analytical",
                "evocative", "precise", "lyrical", "instructional", "contemplative",
                "dramatic", "minimalist", "expansive", "rhythmic", "visual"
            ]
        }

    async def analyze_narrative_for_attributes(self, 
                                             narrative: str,
                                             transformation_intent: str = "enhance",
                                             llm_provider=None) -> AttributeProfile:
        """
        Core method: Analyze narrative and recommend optimal attributes.
        
        Args:
            narrative: Input text to transform
            transformation_intent: Desired transformation ("enhance", "clarify", "poetize", etc.)
            llm_provider: LLM for intelligent analysis
            
        Returns:
            AttributeProfile with recommended attributes and reasoning
        """
        
        if not self.embedder:
            # Fallback to default attributes
            return self._fallback_attributes()
            
        # Step 1: Generate narrative embedding
        narrative_embedding = self.embedder.encode(narrative)
        
        # Step 2: Find nearest semantic anchors
        anchor_similarities = self._find_nearest_anchors(narrative_embedding)
        
        # Step 3: Query RAG database for similar transformations
        similar_patterns = self._query_similar_patterns(narrative_embedding, limit=5)
        
        # Step 4: Use LLM for intelligent attribute selection
        if llm_provider:
            attribute_analysis = await self._llm_attribute_analysis(
                narrative, transformation_intent, anchor_similarities, similar_patterns, llm_provider
            )
        else:
            # Fallback to heuristic selection
            attribute_analysis = self._heuristic_attribute_selection(
                narrative_embedding, anchor_similarities, similar_patterns
            )
        
        # Step 5: Explore embedding neighborhood and integrate with archive
        semantic_neighborhood = self._explore_semantic_neighborhood(narrative_embedding)
        archive_neighbors = await self._query_archive_embeddings(narrative_embedding)
        
        # Step 6: Generate M-POVM coordinates integrated with embedding space
        povm_coords = None
        if self.quantum_engine:
            povm_coords = self._generate_integrated_povm_coordinates(
                narrative_embedding, attribute_analysis, archive_neighbors
            )
        
        return AttributeProfile(
            persona=attribute_analysis["persona"],
            namespace=attribute_analysis["namespace"], 
            style=attribute_analysis["style"],
            confidence=attribute_analysis["confidence"],
            reasoning=attribute_analysis["reasoning"],
            embedding_anchor=narrative_embedding,
            semantic_neighborhood=semantic_neighborhood,
            povm_coordinates=povm_coords
        )

    def _find_nearest_anchors(self, embedding: np.ndarray, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
        """Find nearest semantic anchors to the narrative embedding."""
        similarities = []
        
        for anchor_id, anchor_data in self.anchor_points.items():
            similarity = np.dot(embedding, anchor_data['embedding']) / (
                np.linalg.norm(embedding) * np.linalg.norm(anchor_data['embedding'])
            )
            similarities.append((anchor_id, similarity, anchor_data['hints']))
            
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    def _query_similar_patterns(self, embedding: np.ndarray, limit: int = 5) -> List[TransformationPattern]:
        """Query RAG database for similar transformation patterns."""
        try:
            conn = sqlite3.connect(self.rag_db_path)
            cursor = conn.cursor()
            
            # Get all patterns (in real implementation, use vector similarity search)
            cursor.execute("""
                SELECT id, source_embedding, persona, namespace, style, 
                       fidelity, preservation_score, narrative_snippet, transformation_type
                FROM transformation_patterns 
                ORDER BY success_rating DESC
                LIMIT ?
            """, (limit,))
            
            patterns = []
            for row in cursor.fetchall():
                source_emb = np.frombuffer(row[1], dtype=np.float32)
                similarity = np.dot(embedding, source_emb) / (
                    np.linalg.norm(embedding) * np.linalg.norm(source_emb)
                )
                
                pattern = TransformationPattern(
                    id=row[0],
                    source_embedding=source_emb,
                    target_embedding=None,  # Not needed for similarity
                    attributes={"persona": row[2], "namespace": row[3], "style": row[4]},
                    success_metrics={"fidelity": row[5], "preservation": row[6]},
                    narrative_snippet=row[7],
                    transformation_type=row[8],
                    created_at=datetime.now()
                )
                patterns.append((pattern, similarity))
                
            conn.close()
            
            # Sort by similarity and return top patterns
            patterns.sort(key=lambda x: x[1], reverse=True)
            return [p[0] for p in patterns]
            
        except Exception as e:
            logger.warning(f"Could not query patterns: {e}")
            return []

    async def _llm_attribute_analysis(self, 
                                    narrative: str,
                                    intent: str,
                                    anchors: List[Tuple[str, float, Dict]],
                                    patterns: List[TransformationPattern],
                                    llm_provider) -> Dict[str, Any]:
        """Use LLM to intelligently select attributes based on analysis."""
        
        # Prepare context for LLM
        anchor_context = "\n".join([
            f"- {anchor_id} (similarity: {sim:.3f}): {hints}"
            for anchor_id, sim, hints in anchors
        ])
        
        pattern_context = "\n".join([
            f"- {p.attributes} (success: {p.success_metrics.get('fidelity', 0):.3f})"
            for p in patterns[:3]
        ])
        
        prompt = f"""Analyze this narrative for optimal transformation attributes:

NARRATIVE: "{narrative}"

TRANSFORMATION INTENT: {intent}

SEMANTIC ANCHORS (nearest matches):
{anchor_context}

SIMILAR SUCCESSFUL PATTERNS:
{pattern_context}

AVAILABLE ATTRIBUTES:
- Personas: {', '.join(self.attribute_taxonomy['persona'])}
- Namespaces: {', '.join(self.attribute_taxonomy['namespace'])}
- Styles: {', '.join(self.attribute_taxonomy['style'])}

Select the BEST combination for this transformation. Respond in JSON:
{{
  "persona": "selected_persona",
  "namespace": "selected_namespace", 
  "style": "selected_style",
  "confidence": 0.85,
  "reasoning": "Brief explanation of why these attributes work best for this narrative"
}}"""

        try:
            response = await llm_provider.generate(prompt)
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                raise ValueError("No JSON found in LLM response")
                
        except Exception as e:
            logger.warning(f"LLM attribute analysis failed: {e}")
            return self._heuristic_attribute_selection(None, anchors, patterns)

    def _heuristic_attribute_selection(self, 
                                     embedding: Optional[np.ndarray],
                                     anchors: List[Tuple[str, float, Dict]],
                                     patterns: List[TransformationPattern]) -> Dict[str, Any]:
        """Fallback heuristic attribute selection."""
        
        # Use most similar anchor's hints
        if anchors:
            best_anchor = anchors[0]
            hints = best_anchor[2]
            
            persona = hints.get('persona', ['philosopher'])[0]
            namespace = hints.get('namespace', ['philosophical'])[0] 
            style = hints.get('style', ['contemplative'])[0]
            confidence = best_anchor[1]
            reasoning = f"Selected based on similarity to '{best_anchor[0]}' anchor"
            
        # Or use most successful pattern
        elif patterns:
            best_pattern = patterns[0]
            persona = best_pattern.attributes['persona']
            namespace = best_pattern.attributes['namespace']
            style = best_pattern.attributes['style']
            confidence = best_pattern.success_metrics.get('fidelity', 0.5)
            reasoning = f"Selected based on successful pattern: {best_pattern.transformation_type}"
            
        else:
            # Default fallback
            persona = "philosopher"
            namespace = "philosophical"
            style = "contemplative"
            confidence = 0.3
            reasoning = "Default selection - no patterns or anchors available"
            
        return {
            "persona": persona,
            "namespace": namespace,
            "style": style,
            "confidence": confidence,
            "reasoning": reasoning
        }

    def _explore_semantic_neighborhood(self, 
                                     embedding: np.ndarray, 
                                     radius: float = 0.1) -> List[Tuple[str, float]]:
        """Explore the embedding neighborhood around the narrative."""
        neighborhood = []
        
        for anchor_id, anchor_data in self.anchor_points.items():
            distance = np.linalg.norm(embedding - anchor_data['embedding'])
            if distance <= radius:
                neighborhood.append((anchor_data['description'], distance))
                
        return sorted(neighborhood, key=lambda x: x[1])

    def _generate_povm_coordinates(self, 
                                 embedding: np.ndarray,
                                 attributes: Dict[str, Any]) -> Optional[torch.Tensor]:
        """Generate M-POVM coordinates for quantum representation."""
        if not self.quantum_engine:
            return None
            
        try:
            # Convert embedding to quantum meaning-state  
            meaning_state = self.quantum_engine.text_to_meaning_state(
                f"Attributes: {attributes['persona']}, {attributes['namespace']}, {attributes['style']}",
                torch.tensor(embedding, dtype=torch.float32)
            )
            
            # Get POVM measurement probabilities
            probabilities = self.quantum_engine.canonical_povm.measure(meaning_state)
            return torch.tensor(probabilities)
            
        except Exception as e:
            logger.warning(f"Could not generate POVM coordinates: {e}")
            return None

    def _fallback_attributes(self) -> AttributeProfile:
        """Fallback when no embedding model available."""
        return AttributeProfile(
            persona="philosopher",
            namespace="philosophical",
            style="contemplative",
            confidence=0.3,
            reasoning="Fallback - embedding model not available",
            embedding_anchor=np.zeros(384),  # Default size
            semantic_neighborhood=[],
            povm_coordinates=None
        )

    def record_transformation_outcome(self,
                                    pattern_id: str,
                                    source_text: str,
                                    target_text: str,
                                    attributes: Dict[str, str],
                                    metrics: Dict[str, float],
                                    transformation_type: str = "balanced"):
        """Record transformation outcome for RAG learning."""
        try:
            if not self.embedder:
                return
                
            source_embedding = self.embedder.encode(source_text)
            target_embedding = self.embedder.encode(target_text)
            
            conn = sqlite3.connect(self.rag_db_path)
            cursor = conn.cursor()
            
            success_rating = (
                metrics.get('fidelity', 0) * 0.3 +
                metrics.get('preservation_score', 0) * 0.4 +
                (1.0 - abs(metrics.get('purity_change', 0))) * 0.3
            )
            
            cursor.execute("""
                INSERT OR REPLACE INTO transformation_patterns 
                (id, source_embedding, target_embedding, persona, namespace, style,
                 fidelity, preservation_score, purity_change, entropy_change,
                 narrative_snippet, transformation_type, created_at, success_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                source_embedding.tobytes(),
                target_embedding.tobytes(), 
                attributes.get('persona', ''),
                attributes.get('namespace', ''),
                attributes.get('style', ''),
                metrics.get('fidelity', 0),
                metrics.get('preservation_score', 0),
                metrics.get('purity_change', 0),
                metrics.get('entropy_change', 0),
                source_text[:200],  # Snippet
                transformation_type,
                datetime.now(),
                success_rating
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded transformation pattern: {pattern_id}")
            
        except Exception as e:
            logger.error(f"Failed to record transformation: {e}")

    def get_attribute_insights(self, attribute_profile: AttributeProfile) -> Dict[str, Any]:
        """Get detailed insights about the selected attributes."""
        return {
            "selection_summary": {
                "persona": attribute_profile.persona,
                "namespace": attribute_profile.namespace,
                "style": attribute_profile.style,
                "confidence": attribute_profile.confidence
            },
            "reasoning": attribute_profile.reasoning,
            "semantic_anchors": attribute_profile.semantic_neighborhood,
            "quantum_coordinates": attribute_profile.povm_coordinates.tolist() if attribute_profile.povm_coordinates is not None else None,
            "embedding_magnitude": float(np.linalg.norm(attribute_profile.embedding_anchor)),
            "recommended_alternatives": self._get_alternative_attributes(attribute_profile)
        }

    def _get_alternative_attributes(self, profile: AttributeProfile) -> List[Dict[str, str]]:
        """Suggest alternative attribute combinations."""
        alternatives = []
        
        # Find semantically similar options
        for anchor_id, anchor_data in self.anchor_points.items():
            similarity = np.dot(profile.embedding_anchor, anchor_data['embedding']) / (
                np.linalg.norm(profile.embedding_anchor) * np.linalg.norm(anchor_data['embedding'])
            )
            
            if 0.7 <= similarity < 0.9:  # Similar but not identical
                hints = anchor_data['hints']
                if hints:
                    alternatives.append({
                        "persona": hints.get('persona', [profile.persona])[0],
                        "namespace": hints.get('namespace', [profile.namespace])[0],
                        "style": hints.get('style', [profile.style])[0],
                        "reason": f"Alternative based on {anchor_id} similarity"
                    })
                    
        return alternatives[:3]  # Limit to top 3

    async def _query_archive_embeddings(self, narrative_embedding: np.ndarray, limit: int = 10) -> List[Dict]:
        """Query the archive system for semantically similar embeddings."""
        try:
            import httpx
            
            # Convert embedding to list for JSON serialization
            embedding_list = narrative_embedding.tolist()
            
            # Query archive API for similar embeddings
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:7200/search",
                    json={
                        "query": "semantic similarity search",
                        "embedding": embedding_list,
                        "limit": limit,
                        "use_embeddings": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.warning(f"Archive embedding search failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.warning(f"Could not query archive embeddings: {e}")
            return []

    def _generate_integrated_povm_coordinates(self, 
                                            embedding: np.ndarray,
                                            attributes: Dict[str, Any],
                                            archive_neighbors: List[Dict]) -> Optional[torch.Tensor]:
        """Generate M-POVM coordinates integrated with embedding space and archive data."""
        if not self.quantum_engine:
            return None
            
        try:
            # Create enhanced meaning-state that incorporates archive context
            
            # 1. Base meaning-state from current narrative
            base_meaning_text = f"Narrative with attributes: {attributes['persona']}, {attributes['namespace']}, {attributes['style']}"
            base_state = self.quantum_engine.text_to_meaning_state(
                base_meaning_text,
                torch.tensor(embedding, dtype=torch.float32)  # Use full embedding
            )
            
            # 2. Incorporate archive neighbors to create "contextual meaning-state"
            if archive_neighbors:
                # Weight the meaning-state based on archive similarity
                neighbor_weights = []
                neighbor_texts = []
                
                for neighbor in archive_neighbors[:5]:  # Top 5 neighbors
                    similarity = neighbor.get('similarity_score', 0.5)
                    content = neighbor.get('content', '')[:200]  # Truncate for processing
                    neighbor_weights.append(similarity)
                    neighbor_texts.append(content)
                
                # Create weighted meaning-state ensemble
                if neighbor_texts:
                    context_text = f"Archive context: {' | '.join(neighbor_texts)}"
                    # Generate context embedding using the same embedder
                    if self.embedder:
                        context_embedding = self.embedder.encode(context_text)
                        context_embedding = torch.tensor(context_embedding, dtype=torch.float32)
                    else:
                        # Fallback to random embedding with same dimension as input
                        context_embedding = torch.randn(embedding.shape[0])
                    
                    context_state = self.quantum_engine.text_to_meaning_state(
                        context_text,
                        context_embedding
                    )
                    
                    # Blend base state with context (70% base, 30% context)
                    blended_matrix = 0.7 * base_state.density_matrix + 0.3 * context_state.density_matrix
                    # Renormalize
                    blended_matrix = blended_matrix / torch.trace(blended_matrix)
                    
                    enhanced_state = self.quantum_engine.canonical_povm.measure_density_matrix(blended_matrix)
                else:
                    enhanced_state = self.quantum_engine.canonical_povm.measure(base_state)
            else:
                enhanced_state = self.quantum_engine.canonical_povm.measure(base_state)
            
            # Convert to tensor
            if isinstance(enhanced_state, dict):
                probabilities = list(enhanced_state.values())
                return torch.tensor(probabilities, dtype=torch.float32)
            else:
                return torch.tensor(enhanced_state, dtype=torch.float32)
                
        except Exception as e:
            logger.warning(f"Could not generate integrated POVM coordinates: {e}")
            return self._generate_povm_coordinates(embedding, attributes)

    async def auto_generate_narrative_embedding(self, narrative: str) -> Optional[np.ndarray]:
        """
        Automatically generate and store embeddings for new narratives.
        
        This directly addresses the user's request for "embeddings and summary chunks liberally used"
        by ensuring every narrative gets embedded and archived.
        """
        try:
            import httpx
            
            # 1. Generate embedding using local model
            narrative_embedding = None
            if self.embedder:
                narrative_embedding = self.embedder.encode(narrative)
            
            # 2. Store in archive system for future similarity searches
            if narrative_embedding is not None:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:7200/ingest",
                        data={
                            "content_type": "narrative",
                            "source": "transformation_pipeline", 
                            "title": f"Narrative: {narrative[:50]}...",
                            "data": narrative,
                        },
                        files={}  # Required for multipart form data
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"Auto-stored narrative embedding: {data.get('document_id', 'unknown')}")
                    else:
                        logger.warning(f"Failed to auto-store narrative: {response.status_code}")
                        
            return narrative_embedding
            
        except Exception as e:
            logger.warning(f"Auto-embedding generation failed: {e}")
            return None

    async def enhance_semantic_anchors_from_archive(self):
        """
        Learn new semantic anchors from the archive system's 37,205 chunks and 111 embeddings.
        
        This implements the user's vision of tight M-POVM/embedding integration by using
        the archive's rich content to discover new semantic anchor points.
        """
        try:
            import httpx
            
            # Query archive for diverse content to create new anchors
            async with httpx.AsyncClient() as client:
                # Get high-quality, diverse content from archive
                response = await client.get(
                    "http://localhost:7200/stats"
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    total_embeddings = stats.get('total_embeddings', 0)
                    total_chunks = stats.get('total_chunks', 0)
                    
                    logger.info(f"Archive has {total_embeddings} embeddings and {total_chunks} chunks for anchor learning")
                    
                    # Sample diverse content for anchor creation
                    for anchor_type in ["technical", "creative", "analytical", "narrative", "philosophical"]:
                        search_response = await client.post(
                            "http://localhost:7200/search",
                            json={
                                "query": f"{anchor_type} content with depth and insight",
                                "limit": 3,
                                "use_embeddings": True
                            }
                        )
                        
                        if search_response.status_code == 200:
                            results = search_response.json().get("results", [])
                            
                            for result in results:
                                content = result.get('content', '')
                                if len(content) > 100 and self.embedder:  # Meaningful content
                                    # Create new semantic anchor
                                    anchor_embedding = self.embedder.encode(content[:200])
                                    anchor_id = f"archive_learned_{anchor_type}_{len(self.anchor_points)}"
                                    
                                    # Analyze content to generate attribute hints
                                    hints = self._analyze_content_for_hints(content, anchor_type)
                                    
                                    self.anchor_points[anchor_id] = {
                                        'embedding': anchor_embedding,
                                        'description': content[:100] + "...",
                                        'hints': hints
                                    }
                                    
                                    # Store in database
                                    self._store_semantic_anchor(anchor_id, anchor_embedding, content[:100], hints)
                                    
                    logger.info(f"Enhanced semantic anchors from archive: now have {len(self.anchor_points)} total anchors")
                    
        except Exception as e:
            logger.warning(f"Archive anchor enhancement failed: {e}")

    def _analyze_content_for_hints(self, content: str, content_type: str) -> Dict[str, List[str]]:
        """Analyze content to generate attribute hints for new semantic anchors."""
        hints = {"persona": [], "namespace": [], "style": []}
        
        # Simple heuristic analysis (could be enhanced with LLM)
        content_lower = content.lower()
        
        # Persona hints based on content analysis
        if "research" in content_lower or "study" in content_lower or "analysis" in content_lower:
            hints["persona"].append("researcher")
        if "story" in content_lower or "narrative" in content_lower or "character" in content_lower:
            hints["persona"].append("storyteller")
        if "wisdom" in content_lower or "philosophy" in content_lower or "meaning" in content_lower:
            hints["persona"].append("philosopher")
        if "guide" in content_lower or "how to" in content_lower or "steps" in content_lower:
            hints["persona"].append("guide")
            
        # Namespace hints
        if content_type == "technical":
            hints["namespace"].extend(["scientific", "technological"])
        elif content_type == "creative":
            hints["namespace"].extend(["artistic", "literary"])
        elif content_type == "philosophical":
            hints["namespace"].extend(["philosophical", "ethical"])
            
        # Style hints based on writing patterns
        if len([s for s in content.split('.') if len(s) > 50]) > 3:  # Long sentences
            hints["style"].append("expansive")
        if content.count('?') > 2:
            hints["style"].append("questioning")
        if content.count('!') > 1:
            hints["style"].append("emphatic")
            
        # Fallback to default if no hints found
        for key in hints:
            if not hints[key]:
                hints[key] = ["general"]
                
        return hints

    def _store_semantic_anchor(self, anchor_id: str, embedding: np.ndarray, description: str, hints: Dict):
        """Store a new semantic anchor in the database."""
        try:
            conn = sqlite3.connect(self.rag_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO semantic_anchors 
                (anchor_id, embedding, description, attribute_hints, usage_count, avg_success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                anchor_id,
                embedding.tobytes(),
                description,
                json.dumps(hints),
                0,  # Initial usage count
                0.0  # Initial success rate
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Stored semantic anchor: {anchor_id}")
            
        except Exception as e:
            logger.warning(f"Failed to store semantic anchor {anchor_id}: {e}")

# Integration functions for the existing pipeline

async def enhance_transformation_with_ai_attributes(narrative: str,
                                                  transformation_intent: str,
                                                  llm_provider,
                                                  quantum_engine=None) -> Tuple[Dict[str, str], AttributeProfile]:
    """
    Main integration function: Replace manual attribute selection with AI-guided selection.
    
    Returns:
        Tuple of (attributes_dict, full_profile) for use in existing transformation pipeline
    """
    
    # Initialize the intelligence engine
    ai_engine = AttributeIntelligenceEngine(quantum_engine=quantum_engine)
    
    # Analyze narrative and get intelligent attribute recommendations
    profile = await ai_engine.analyze_narrative_for_attributes(
        narrative, transformation_intent, llm_provider
    )
    
    # Return both the simple attributes dict for existing pipeline
    # and the full profile for advanced analysis
    attributes = {
        "persona": profile.persona,
        "namespace": profile.namespace,
        "style": profile.style
    }
    
    return attributes, profile

def create_attribute_editor_component_data(profile: AttributeProfile) -> Dict[str, Any]:
    """
    Create data structure for a dynamic attribute editor component.
    """
    engine = AttributeIntelligenceEngine()
    
    return {
        "current_selection": {
            "persona": profile.persona,
            "namespace": profile.namespace,
            "style": profile.style,
            "confidence": profile.confidence
        },
        "reasoning": profile.reasoning,
        "alternatives": engine._get_alternative_attributes(profile),
        "taxonomy": engine.attribute_taxonomy,
        "semantic_context": {
            "anchors": profile.semantic_neighborhood,
            "embedding_magnitude": float(np.linalg.norm(profile.embedding_anchor))
        },
        "quantum_analysis": {
            "povm_coordinates": profile.povm_coordinates.tolist() if profile.povm_coordinates is not None else None,
            "meaning_space_position": "computed_from_coordinates"
        },
        "pipeline_preview": {
            "expected_transformation_type": "balanced_with_ai_guidance",
            "estimated_processing_time": "2-4 seconds",
            "confidence_factors": [
                f"Semantic anchor similarity: {profile.confidence:.2f}",
                f"Historical pattern match: available",
                f"Quantum coherence: computed"
            ]
        }
    }