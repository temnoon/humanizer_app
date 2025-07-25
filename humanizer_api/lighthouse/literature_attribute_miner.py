"""
Literature Attribute Mining System
=================================

Mine Project Gutenberg literature using QBist semantic tools to discover
comprehensive, literature-grounded attribute taxonomies for narrative transformation.

This system addresses the user's insight that we need more base attributes derived
from actual literary analysis rather than arbitrary lists.

Key Features:
1. Project Gutenberg text fetching and processing
2. QBist M-POVM semantic analysis of literary passages
3. Automatic attribute cluster discovery
4. Multi-dimensional attribute taxonomy generation
5. Semantic anchor points derived from great literature

Author: Enhanced for comprehensive literary analysis
"""

import asyncio
import re
import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from datetime import datetime
import logging
from collections import defaultdict, Counter

# Try to import httpx, fall back to urllib
try:
    import httpx
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.parse
    HTTP_CLIENT_AVAILABLE = False
    print("httpx not available, using urllib for HTTP requests")

# Import our quantum narrative tools
try:
    from narrative_theory import QuantumNarrativeEngine, MeaningState
    from attribute_intelligence import AttributeIntelligenceEngine
    from sentence_transformers import SentenceTransformer
    QUANTUM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Quantum tools not available: {e}")
    QUANTUM_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class LiteraryPassage:
    """Represents a meaningful passage from literature with metadata."""
    text: str
    author: str
    work_title: str
    gutenberg_id: str
    passage_id: str
    word_count: int
    embedding: Optional[np.ndarray] = None
    meaning_state: Optional[Any] = None  # MeaningState when available

@dataclass
class SemanticCluster:
    """Represents a discovered semantic cluster that could be an attribute."""
    cluster_id: str
    representative_passages: List[LiteraryPassage]
    cluster_center: np.ndarray
    semantic_label: str
    confidence: float
    attribute_category: str  # 'persona', 'namespace', 'style', or new category
    defining_characteristics: List[str]

class ProjectGutenbergMiner:
    """
    Fetches and processes texts from Project Gutenberg.
    """
    
    BASE_URL = "https://www.gutenberg.org"
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def fetch_work_metadata(self, gutenberg_id: str) -> Dict[str, str]:
        """Fetch metadata for a Project Gutenberg work."""
        try:
            url = f"{self.BASE_URL}/ebooks/{gutenberg_id}"
            response = await self.session.get(url)
            
            if response.status_code == 200:
                html = response.text
                
                # Extract title and author using regex (basic extraction)
                title_match = re.search(r'<title>([^|]+)', html)
                author_match = re.search(r'by\s+([^<\n]+)', html)
                
                return {
                    "title": title_match.group(1).strip() if title_match else f"Work {gutenberg_id}",
                    "author": author_match.group(1).strip() if author_match else "Unknown",
                    "gutenberg_id": gutenberg_id
                }
            else:
                return {"title": f"Work {gutenberg_id}", "author": "Unknown", "gutenberg_id": gutenberg_id}
                
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for {gutenberg_id}: {e}")
            return {"title": f"Work {gutenberg_id}", "author": "Unknown", "gutenberg_id": gutenberg_id}
    
    async def fetch_text(self, gutenberg_id: str) -> Optional[str]:
        """Fetch the full text of a Project Gutenberg work."""
        try:
            # Try different text formats
            for format_suffix in [".txt", "-0.txt", "-8.txt"]:
                url = f"{self.BASE_URL}/files/{gutenberg_id}/{gutenberg_id}{format_suffix}"
                
                try:
                    response = await self.session.get(url)
                    if response.status_code == 200:
                        text = response.text
                        
                        # Clean up the text (remove headers/footers)
                        text = self._clean_gutenberg_text(text)
                        return text
                        
                except Exception:
                    continue
                    
            logger.warning(f"Could not fetch text for Gutenberg ID {gutenberg_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching text for {gutenberg_id}: {e}")
            return None
    
    def _clean_gutenberg_text(self, text: str) -> str:
        """Clean Project Gutenberg text by removing headers/footers."""
        
        # Remove Project Gutenberg header
        start_markers = [
            "*** START OF THIS PROJECT GUTENBERG",
            "*** START OF THE PROJECT GUTENBERG",
            "***START OF THE PROJECT GUTENBERG"
        ]
        
        for marker in start_markers:
            if marker in text:
                text = text.split(marker, 1)[1]
                break
        
        # Remove Project Gutenberg footer
        end_markers = [
            "*** END OF THIS PROJECT GUTENBERG",
            "*** END OF THE PROJECT GUTENBERG",
            "***END OF THE PROJECT GUTENBERG",
            "End of the Project Gutenberg"
        ]
        
        for marker in end_markers:
            if marker in text:
                text = text.split(marker)[0]
                break
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines -> double newline
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces -> single space
        
        return text.strip()

class LiterarySemanticAnalyzer:
    """
    Analyzes literature using QBist semantic tools to discover attribute patterns.
    """
    
    def __init__(self, 
                 quantum_engine: Optional[Any] = None,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.quantum_engine = quantum_engine
        
        # Initialize embedding model
        try:
            self.embedder = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedder = None
            
        self.db_path = "./data/literature_attributes.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize database for storing literary analysis."""
        Path("./data").mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Literary passages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS literary_passages (
                passage_id TEXT PRIMARY KEY,
                text TEXT,
                author TEXT,
                work_title TEXT,
                gutenberg_id TEXT,
                word_count INTEGER,
                embedding BLOB,
                created_at TIMESTAMP
            )
        """)
        
        # Semantic clusters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_clusters (
                cluster_id TEXT PRIMARY KEY,
                semantic_label TEXT,
                attribute_category TEXT,
                confidence REAL,
                cluster_center BLOB,
                defining_characteristics TEXT,
                passage_count INTEGER,
                created_at TIMESTAMP
            )
        """)
        
        # Discovered attributes table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_attributes (
                attribute_id TEXT PRIMARY KEY,
                category TEXT,
                label TEXT,
                description TEXT,
                literary_examples TEXT,
                semantic_signature BLOB,
                usage_frequency INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                created_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Literature analysis database initialized")
    
    def extract_meaningful_passages(self, text: str, metadata: Dict[str, str], 
                                  min_words: int = 50, max_words: int = 200) -> List[LiteraryPassage]:
        """Extract meaningful passages from a literary work."""
        
        passages = []
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            # Clean paragraph
            paragraph = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', ' ', paragraph)
            paragraph = ' '.join(paragraph.split())  # Normalize whitespace
            
            word_count = len(paragraph.split())
            
            # Filter by word count
            if min_words <= word_count <= max_words:
                # Additional quality filters
                if self._is_meaningful_passage(paragraph):
                    passage = LiteraryPassage(
                        text=paragraph,
                        author=metadata['author'],
                        work_title=metadata['title'],
                        gutenberg_id=metadata['gutenberg_id'],
                        passage_id=f"{metadata['gutenberg_id']}_{i}",
                        word_count=word_count
                    )
                    passages.append(passage)
        
        return passages
    
    def _is_meaningful_passage(self, text: str) -> bool:
        """Determine if a passage is meaningful for analysis."""
        
        # Skip if too many numbers or special characters
        if len(re.findall(r'\d', text)) > len(text) * 0.2:
            return False
            
        # Skip if mostly dialogue tags
        if text.count('"') > len(text.split()) * 0.5:
            return False
            
        # Skip if very repetitive
        words = text.lower().split()
        if len(set(words)) < len(words) * 0.5:
            return False
            
        # Must contain some complexity
        if text.count(',') + text.count(';') + text.count(':') < 2:
            return False
            
        return True
    
    async def analyze_passage_semantics(self, passage: LiteraryPassage) -> LiteraryPassage:
        """Analyze a passage using embeddings and quantum tools."""
        
        if not self.embedder:
            return passage
            
        try:
            # Generate embedding
            embedding = self.embedder.encode(passage.text)
            passage.embedding = embedding
            
            # Generate quantum meaning-state if available
            if self.quantum_engine and QUANTUM_AVAILABLE:
                # Pass the full embedding - the quantum engine will handle dimension mapping
                meaning_state = self.quantum_engine.text_to_meaning_state(
                    passage.text,
                    torch.tensor(embedding, dtype=torch.float32)  # Use full embedding
                )
                passage.meaning_state = meaning_state
                
            return passage
            
        except Exception as e:
            logger.warning(f"Failed to analyze passage semantics: {e}")
            return passage
    
    def store_passage(self, passage: LiteraryPassage):
        """Store analyzed passage in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            embedding_blob = passage.embedding.tobytes() if passage.embedding is not None else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO literary_passages 
                (passage_id, text, author, work_title, gutenberg_id, word_count, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                passage.passage_id,
                passage.text,
                passage.author, 
                passage.work_title,
                passage.gutenberg_id,
                passage.word_count,
                embedding_blob,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store passage: {e}")

class AttributeDiscoveryEngine:
    """
    Discovers new attribute categories and values by clustering literary passages.
    """
    
    def __init__(self, db_path: str = "./data/literature_attributes.db"):
        self.db_path = db_path
        
    def load_passage_embeddings(self) -> Tuple[List[LiteraryPassage], np.ndarray]:
        """Load all passage embeddings from database."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT passage_id, text, author, work_title, gutenberg_id, word_count, embedding
            FROM literary_passages 
            WHERE embedding IS NOT NULL
        """)
        
        passages = []
        embeddings = []
        
        for row in cursor.fetchall():
            passage_id, text, author, work_title, gutenberg_id, word_count, embedding_blob = row
            
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            passage = LiteraryPassage(
                text=text,
                author=author,
                work_title=work_title,
                gutenberg_id=gutenberg_id,
                passage_id=passage_id,
                word_count=word_count,
                embedding=embedding
            )
            
            passages.append(passage)
            embeddings.append(embedding)
        
        conn.close()
        
        return passages, np.array(embeddings) if embeddings else np.array([])
    
    def discover_semantic_clusters(self, 
                                 passages: List[LiteraryPassage],
                                 embeddings: np.ndarray,
                                 n_clusters: int = 50) -> List[SemanticCluster]:
        """Discover semantic clusters in the embedding space."""
        
        if len(embeddings) == 0:
            return []
            
        # Try scikit-learn first, fall back to simple clustering
        try:
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            
            # Perform clustering
            actual_clusters = min(n_clusters, len(passages))
            kmeans = KMeans(n_clusters=actual_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Calculate silhouette score for quality assessment
            silhouette_avg = silhouette_score(embeddings, cluster_labels)
            logger.info(f"Clustering silhouette score: {silhouette_avg:.3f}")
            
            cluster_centers = kmeans.cluster_centers_
            
        except ImportError:
            logger.warning("scikit-learn not available, using simple clustering")
            # Simple clustering based on similarity to random centers
            cluster_labels, cluster_centers, silhouette_avg = self._simple_clustering(embeddings, n_clusters)
            
        except Exception as e:
            logger.error(f"Advanced clustering failed, falling back to simple method: {e}")
            cluster_labels, cluster_centers, silhouette_avg = self._simple_clustering(embeddings, n_clusters)
        
        # Create semantic clusters
        clusters = []
        actual_clusters = len(cluster_centers)
        
        for cluster_id in range(actual_clusters):
            cluster_mask = cluster_labels == cluster_id
            if not np.any(cluster_mask):
                continue
                
            cluster_passages = [p for i, p in enumerate(passages) if cluster_mask[i]]
            if not cluster_passages:
                continue
                
            cluster_center = cluster_centers[cluster_id]
            
            # Generate semantic label for cluster
            semantic_label = self._generate_cluster_label(cluster_passages)
            
            # Determine attribute category
            attribute_category = self._classify_attribute_category(cluster_passages, semantic_label)
            
            # Extract defining characteristics
            characteristics = self._extract_defining_characteristics(cluster_passages)
            
            cluster = SemanticCluster(
                cluster_id=f"cluster_{cluster_id}",
                representative_passages=cluster_passages[:5],  # Top 5 examples
                cluster_center=cluster_center,
                semantic_label=semantic_label,
                confidence=silhouette_avg,
                attribute_category=attribute_category,
                defining_characteristics=characteristics
            )
            
            clusters.append(cluster)
        
        return clusters
    
    def _simple_clustering(self, embeddings: np.ndarray, n_clusters: int) -> Tuple[np.ndarray, np.ndarray, float]:
        """Simple clustering fallback when scikit-learn is not available."""
        
        n_samples, n_features = embeddings.shape
        actual_clusters = min(n_clusters, max(2, n_samples // 3))  # Better ratio: 3 samples per cluster minimum
        
        if actual_clusters <= 1 or n_samples < 6:  # Need at least 6 samples for meaningful clustering
            # Not enough data for clustering
            return np.zeros(n_samples), embeddings.mean(axis=0).reshape(1, -1), 0.5
        
        # Initialize cluster centers randomly
        np.random.seed(42)
        center_indices = np.random.choice(n_samples, actual_clusters, replace=False)
        cluster_centers = embeddings[center_indices].copy()
        
        # Simple k-means-like iteration
        for iteration in range(20):  # Max 20 iterations
            # Assign points to nearest center
            distances = np.array([
                [np.linalg.norm(embedding - center) for center in cluster_centers]
                for embedding in embeddings
            ])
            cluster_labels = np.argmin(distances, axis=1)
            
            # Update centers
            new_centers = []
            for i in range(actual_clusters):
                cluster_points = embeddings[cluster_labels == i]
                if len(cluster_points) > 0:
                    new_centers.append(cluster_points.mean(axis=0))
                else:
                    new_centers.append(cluster_centers[i])  # Keep old center if no points
            
            cluster_centers = np.array(new_centers)
        
        # Calculate simple quality metric (inverse of average distance to centers)
        total_distance = 0
        for i, embedding in enumerate(embeddings):
            center = cluster_centers[cluster_labels[i]]
            total_distance += np.linalg.norm(embedding - center)
        
        avg_distance = total_distance / n_samples
        quality_score = 1.0 / (1.0 + avg_distance)  # Normalize to [0,1]
        
        return cluster_labels, cluster_centers, quality_score
    
    def _generate_cluster_label(self, passages: List[LiteraryPassage]) -> str:
        """Generate a semantic label for a cluster based on its passages."""
        
        # Extract common themes from authors and works
        authors = [p.author for p in passages]
        works = [p.work_title for p in passages]
        
        # Get the most common author for this cluster
        author_counts = Counter(authors)
        primary_author = author_counts.most_common(1)[0][0] if author_counts else "unknown"
        
        # Simple heuristic labeling based on content analysis
        combined_text = " ".join([p.text[:100] for p in passages[:10]]).lower()
        
        # Clean the author name for labeling
        clean_author = primary_author.lower().replace(' ', '_').replace('.', '').replace(',', '')
        
        # Content-based style indicators
        if "said" in combined_text and ("replied" in combined_text or "asked" in combined_text):
            return "dialogue_rich"
        elif len([w for w in combined_text.split() if len(w) > 8]) > 20:
            return "elaborate_descriptive" 
        elif combined_text.count('.') / max(len(combined_text.split()), 1) > 0.3:
            return "terse_precise"
        elif any(word in combined_text for word in ["nature", "forest", "mountain", "sky", "earth", "sea"]):
            return "nature_lyrical"
        elif any(word in combined_text for word in ["love", "heart", "passion", "dear", "beloved"]):
            return "romantic_tender"
        elif any(word in combined_text for word in ["think", "mind", "reason", "understand", "wonder", "question"]):
            return "philosophical_questioning"
        elif any(word in combined_text for word in ["war", "battle", "conflict", "fight", "struggle"]):
            return "dramatic_conflict"
        elif any(word in combined_text for word in ["strange", "curious", "odd", "wonder", "magic"]):
            return "fantastical_whimsical"
        elif any(word in combined_text for word in ["dark", "shadow", "fear", "terror", "mystery"]):
            return "gothic_mysterious"
        elif any(word in combined_text for word in ["gentle", "quiet", "soft", "calm", "peace"]):
            return "gentle_contemplative"
        elif any(word in combined_text for word in ["suddenly", "quickly", "immediately", "instant"]):
            return "swift_dramatic"
        elif any(word in combined_text for word in ["house", "room", "door", "window", "home"]):
            return "domestic_intimate"
        elif any(word in combined_text for word in ["time", "moment", "hour", "day", "years"]):
            return "temporal_reflective"
        else:
            # Author-based fallback with content hint
            word_length_avg = np.mean([len(w) for w in combined_text.split()]) if combined_text.split() else 4
            
            if word_length_avg > 5.5:
                return f"{clean_author}_elevated"
            elif word_length_avg < 4.0:
                return f"{clean_author}_simple"
            else:
                return f"{clean_author}_balanced"
    
    def _classify_attribute_category(self, passages: List[LiteraryPassage], label: str) -> str:
        """Classify what type of attribute this cluster represents."""
        
        # Style indicators
        style_keywords = ["style", "prose", "dialogue", "terse", "elaborate", "descriptive"]
        if any(keyword in label for keyword in style_keywords):
            return "style"
            
        # Namespace indicators  
        namespace_keywords = ["nature", "romantic", "philosophical", "conflict", "scientific", "mythic"]
        if any(keyword in label for keyword in namespace_keywords):
            return "namespace"
            
        # Persona indicators (based on author patterns)
        if "_style" in label or "voice" in label:
            return "persona"
            
        # New category indicators
        if "emotional" in label or "dramatic" in label:
            return "emotional_register"
        elif "temporal" in label or "historical" in label:
            return "temporal_perspective"
        else:
            return "style"  # Default
    
    def _extract_defining_characteristics(self, passages: List[LiteraryPassage]) -> List[str]:
        """Extract defining characteristics of a cluster."""
        
        characteristics = []
        
        # Word length analysis
        word_lengths = []
        sentence_lengths = []
        
        for passage in passages[:10]:  # Sample
            words = passage.text.split()
            sentences = passage.text.split('.')
            
            word_lengths.extend([len(w) for w in words])
            sentence_lengths.extend([len(s.split()) for s in sentences if s.strip()])
        
        if word_lengths:
            avg_word_length = np.mean(word_lengths)
            if avg_word_length > 5.5:
                characteristics.append("complex_vocabulary")
            elif avg_word_length < 4.5:
                characteristics.append("simple_vocabulary")
                
        if sentence_lengths:
            avg_sentence_length = np.mean(sentence_lengths)
            if avg_sentence_length > 20:
                characteristics.append("long_sentences")
            elif avg_sentence_length < 10:
                characteristics.append("short_sentences")
        
        # Content analysis
        combined_text = " ".join([p.text for p in passages[:5]]).lower()
        
        if combined_text.count('"') > len(combined_text) / 200:
            characteristics.append("dialogue_rich")
        if len(re.findall(r'[!?]', combined_text)) > len(combined_text) / 500:
            characteristics.append("emotionally_expressive")
        if len(re.findall(r'[;:]', combined_text)) > len(combined_text) / 300:
            characteristics.append("complex_syntax")
            
        return characteristics[:5]  # Limit to top 5
    
    def store_discovered_attributes(self, clusters: List[SemanticCluster]):
        """Store discovered attributes in database."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for cluster in clusters:
            # Store cluster
            cursor.execute("""
                INSERT OR REPLACE INTO semantic_clusters 
                (cluster_id, semantic_label, attribute_category, confidence, 
                 cluster_center, defining_characteristics, passage_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cluster.cluster_id,
                cluster.semantic_label,
                cluster.attribute_category,
                cluster.confidence,
                cluster.cluster_center.tobytes(),
                json.dumps(cluster.defining_characteristics),
                len(cluster.representative_passages),
                datetime.now()
            ))
            
            # Store as discovered attribute
            examples = [p.text[:100] + "..." for p in cluster.representative_passages[:3]]
            
            cursor.execute("""
                INSERT OR REPLACE INTO discovered_attributes 
                (attribute_id, category, label, description, literary_examples, 
                 semantic_signature, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{cluster.attribute_category}_{cluster.semantic_label}",
                cluster.attribute_category,
                cluster.semantic_label,
                f"Discovered from {len(cluster.representative_passages)} literary passages",
                json.dumps(examples),
                cluster.cluster_center.tobytes(),
                cluster.confidence,
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(clusters)} discovered attribute clusters")

# Main orchestration function
async def mine_literature_for_attributes(gutenberg_ids: List[str],
                                       max_passages_per_work: int = 50) -> Dict[str, Any]:
    """
    Main function to mine Project Gutenberg literature for comprehensive attributes.
    
    Returns statistics and discovered attributes.
    """
    
    logger.info(f"Starting literature mining for {len(gutenberg_ids)} works")
    
    # Initialize components
    if QUANTUM_AVAILABLE:
        quantum_engine = QuantumNarrativeEngine(semantic_dimension=8)
    else:
        quantum_engine = None
        
    analyzer = LiterarySemanticAnalyzer(quantum_engine=quantum_engine)
    discovery_engine = AttributeDiscoveryEngine()
    
    total_passages = 0
    processed_works = 0
    
    # Mine literature
    async with ProjectGutenbergMiner() as miner:
        for gutenberg_id in gutenberg_ids:
            try:
                logger.info(f"Processing Gutenberg work {gutenberg_id}")
                
                # Fetch metadata and text
                metadata = await miner.fetch_work_metadata(gutenberg_id)
                text = await miner.fetch_text(gutenberg_id)
                
                if not text:
                    logger.warning(f"Could not fetch text for {gutenberg_id}")
                    continue
                
                # Extract passages
                passages = analyzer.extract_meaningful_passages(text, metadata)
                logger.info(f"Extracted {len(passages)} passages from {metadata['title']}")
                
                # Limit passages per work
                passages = passages[:max_passages_per_work]
                
                # Analyze semantics
                for passage in passages:
                    analyzed_passage = await analyzer.analyze_passage_semantics(passage)
                    analyzer.store_passage(analyzed_passage)
                    
                total_passages += len(passages)
                processed_works += 1
                
                logger.info(f"Processed {processed_works}/{len(gutenberg_ids)} works, {total_passages} total passages")
                
            except Exception as e:
                logger.error(f"Error processing work {gutenberg_id}: {e}")
                continue
    
    # Discover attribute clusters
    logger.info("Discovering semantic clusters...")
    passages, embeddings = discovery_engine.load_passage_embeddings()
    
    if len(passages) > 0:
        clusters = discovery_engine.discover_semantic_clusters(passages, embeddings)
        discovery_engine.store_discovered_attributes(clusters)
        
        # Generate summary
        category_counts = defaultdict(int)
        for cluster in clusters:
            category_counts[cluster.attribute_category] += 1
            
        return {
            "total_works_processed": processed_works,
            "total_passages_analyzed": total_passages,
            "total_clusters_discovered": len(clusters),
            "attribute_categories": dict(category_counts),
            "discovered_attributes_by_category": {
                category: [c.semantic_label for c in clusters if c.attribute_category == category]
                for category in category_counts.keys()
            }
        }
    else:
        return {"error": "No passages with embeddings found"}

# Predefined list of high-quality Project Gutenberg works for attribute mining
CLASSIC_LITERATURE_IDS = [
    "11",      # Alice's Adventures in Wonderland - Carroll
    "84",      # Frankenstein - Shelley  
    "345",     # Dracula - Stoker
    "74",      # The Adventures of Tom Sawyer - Twain
    "76",      # The Adventures of Huckleberry Finn - Twain
    "1342",    # Pride and Prejudice - Austen
    "158",     # Emma - Austen
    "161",     # Sense and Sensibility - Austen
    "1260",    # Jane Eyre - Brontë
    "768",     # Wuthering Heights - Brontë
    "2701",    # Moby Dick - Melville
    "25344",   # The Scarlet Letter - Hawthorne
    "145",     # Middlemarch - Eliot
    "1661",    # The Adventures of Sherlock Holmes - Doyle
    "2554",    # Crime and Punishment - Dostoyevsky
    "2600",    # War and Peace - Tolstoy
    "1399",    # Anna Karenina - Tolstoy
    "98",      # A Tale of Two Cities - Dickens
    "1400",    # Great Expectations - Dickens
    "46",      # A Christmas Carol - Dickens
    "174",     # The Picture of Dorian Gray - Wilde
    "4300",    # Ulysses - Joyce
    "5200",    # Metamorphosis - Kafka
    "1232",    # The Prince - Machiavelli
    "2641",    # A Room with a View - Forster
    "6130",    # The Iliad - Homer
    "1727",    # The Odyssey - Homer
    "1998",    # Thus Spoke Zarathustra - Nietzsche
    "844",     # The Importance of Being Earnest - Wilde
    "1184",    # The Count of Monte Cristo - Dumas
]

if __name__ == "__main__":
    # Example usage
    async def main():
        # Mine a small sample first
        sample_ids = CLASSIC_LITERATURE_IDS[:5]  # Start with 5 works
        
        results = await mine_literature_for_attributes(sample_ids, max_passages_per_work=20)
        
        print("Literature Mining Results:")
        print(json.dumps(results, indent=2))
        
    asyncio.run(main())