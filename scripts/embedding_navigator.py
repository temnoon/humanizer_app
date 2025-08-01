#!/usr/bin/env python3
"""
Embedding Navigation System
Creates and navigates content embeddings for semantic search and exploration
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
from collections import defaultdict

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

class EmbeddingNavigator:
    """Semantic embedding navigation and exploration system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.data_dir = self.project_root / "data"
        self.embeddings_dir = self.data_dir / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "embeddings.db"
        self.model_name = "all-MiniLM-L6-v2"  # Lightweight, fast model
        
        # Initialize database
        self._init_database()
        
        # Load embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print(f"🔄 Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                print("✅ Embedding model loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load embedding model: {e}")
                self.model = None
        else:
            print("❌ sentence-transformers not available. Install with: pip install sentence-transformers")
            self.model = None
    
    def _init_database(self):
        """Initialize embeddings database"""
        if not SQLITE_AVAILABLE:
            print("❌ SQLite not available")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT UNIQUE,
                    content_text TEXT,
                    content_type TEXT,
                    source_file TEXT,
                    embedding_vector TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_clusters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id INTEGER,
                    content_id TEXT,
                    distance_to_center REAL,
                    cluster_label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES embeddings (content_id)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_id ON embeddings (content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cluster_id ON content_clusters (cluster_id)")
    
    def index_content(self, content: str, content_id: str, 
                     content_type: str = "text", 
                     source_file: str = None,
                     metadata: dict = None) -> bool:
        """Index content with embedding"""
        
        if not self.model:
            print("❌ Embedding model not available")
            return False
        
        try:
            # Generate embedding
            embedding = self.model.encode([content])[0]
            embedding_json = json.dumps(embedding.tolist())  # Convert to JSON
            
            metadata_json = json.dumps(metadata or {})
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO embeddings 
                    (content_id, content_text, content_type, source_file, embedding_vector, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (content_id, content, content_type, source_file, embedding_json, metadata_json))
            
            return True
            
        except Exception as e:
            print(f"❌ Error indexing content: {e}")
            return False
    
    def index_file(self, file_path: Path, chunk_size: int = 1000) -> Dict[str, Any]:
        """Index a file by breaking it into chunks"""
        
        if not file_path.exists():
            return {'error': f'File not found: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': f'Error reading file: {e}'}
        
        # Split content into chunks
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():  # Only non-empty chunks
                chunks.append(chunk)
        
        results = {
            'file': str(file_path),
            'total_chunks': len(chunks),
            'indexed': 0,
            'failed': 0
        }
        
        print(f"📝 Indexing file: {file_path.name}")
        print(f"   Content length: {len(content):,} chars")
        print(f"   Chunks: {len(chunks)}")
        
        for i, chunk in enumerate(chunks):
            content_id = f"{file_path.stem}_chunk_{i:04d}"
            
            metadata = {
                'file_name': file_path.name,
                'chunk_index': i,
                'chunk_size': len(chunk),
                'total_chunks': len(chunks)
            }
            
            if self.index_content(chunk, content_id, "text_chunk", str(file_path), metadata):
                results['indexed'] += 1
            else:
                results['failed'] += 1
        
        print(f"✅ Indexed: {results['indexed']}/{results['total_chunks']} chunks")
        
        return results
    
    def semantic_search(self, query: str, limit: int = 10, 
                       threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for semantically similar content"""
        
        if not self.model:
            print("❌ Embedding model not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Get all embeddings from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT content_id, content_text, content_type, source_file, 
                           embedding_vector, metadata 
                    FROM embeddings
                """)
                
                results = []
                
                for row in cursor.fetchall():
                    content_id, content_text, content_type, source_file, embedding_json, metadata_json = row
                    
                    # Parse embedding
                    stored_embedding = np.array(json.loads(embedding_json))
                    
                    # Calculate similarity
                    similarity = cosine_similarity([query_embedding], [stored_embedding])[0][0]
                    
                    if similarity >= threshold:
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        results.append({
                            'content_id': content_id,
                            'content_text': content_text[:200] + '...' if len(content_text) > 200 else content_text,
                            'content_type': content_type,
                            'source_file': source_file,
                            'similarity': float(similarity),
                            'metadata': metadata
                        })
                
                # Sort by similarity and limit
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:limit]
                
        except Exception as e:
            print(f"❌ Error in semantic search: {e}")
            return []
    
    def cluster_content(self, n_clusters: int = 5) -> Dict[str, Any]:
        """Cluster content by semantic similarity"""
        
        if not SKLEARN_AVAILABLE:
            print("❌ scikit-learn not available. Install with: pip install scikit-learn")
            return {'error': 'scikit-learn required for clustering'}
        
        try:
            # Get all embeddings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT content_id, embedding_vector, content_text 
                    FROM embeddings
                """)
                
                data = []
                content_ids = []
                content_texts = []
                
                for row in cursor.fetchall():
                    content_id, embedding_json, content_text = row
                    embedding = np.array(json.loads(embedding_json))
                    
                    data.append(embedding)
                    content_ids.append(content_id)
                    content_texts.append(content_text)
                
                if len(data) < n_clusters:
                    return {'error': f'Not enough content ({len(data)}) for {n_clusters} clusters'}
                
                # Perform clustering
                embeddings_matrix = np.array(data)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(embeddings_matrix)
                
                # Calculate distances to cluster centers
                distances = []
                for i, embedding in enumerate(embeddings_matrix):
                    cluster_center = kmeans.cluster_centers_[cluster_labels[i]]
                    distance = np.linalg.norm(embedding - cluster_center)
                    distances.append(distance)
                
                # Clear existing clusters
                conn.execute("DELETE FROM content_clusters")
                
                # Store cluster results
                cluster_info = defaultdict(list)
                
                for i, (content_id, label, distance) in enumerate(zip(content_ids, cluster_labels, distances)):
                    # Generate cluster label based on content
                    cluster_samples = [content_texts[j] for j, l in enumerate(cluster_labels) if l == label]
                    cluster_label = f"cluster_{label}"  # Simple label for now
                    
                    conn.execute("""
                        INSERT INTO content_clusters 
                        (cluster_id, content_id, distance_to_center, cluster_label)
                        VALUES (?, ?, ?, ?)
                    """, (int(label), content_id, float(distance), cluster_label))
                    
                    cluster_info[int(label)].append({
                        'content_id': content_id,
                        'distance': float(distance),
                        'text_preview': content_texts[i][:100] + '...' if len(content_texts[i]) > 100 else content_texts[i]
                    })
                
                return {
                    'n_clusters': n_clusters,
                    'total_content': len(data),
                    'clusters': dict(cluster_info)
                }
                
        except Exception as e:
            print(f"❌ Error in clustering: {e}")
            return {'error': str(e)}
    
    def visualize_embeddings(self, output_file: str = None) -> str:
        """Create 2D visualization of content embeddings"""
        
        if not SKLEARN_AVAILABLE or not PLOTTING_AVAILABLE:
            print("❌ Visualization requires scikit-learn and matplotlib")
            return "Visualization libraries not available"
        
        try:
            # Get embeddings and metadata
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT e.content_id, e.embedding_vector, e.content_type, 
                           COALESCE(c.cluster_id, -1) as cluster_id
                    FROM embeddings e
                    LEFT JOIN content_clusters c ON e.content_id = c.content_id
                """)
                
                embeddings = []
                labels = []
                content_types = []
                cluster_ids = []
                
                for row in cursor.fetchall():
                    content_id, embedding_json, content_type, cluster_id = row
                    embedding = np.array(json.loads(embedding_json))
                    
                    embeddings.append(embedding)
                    labels.append(content_id)
                    content_types.append(content_type)
                    cluster_ids.append(cluster_id)
                
                if len(embeddings) < 2:
                    return "Not enough content for visualization"
                
                # Reduce to 2D using PCA
                embeddings_matrix = np.array(embeddings)
                pca = PCA(n_components=2)
                embeddings_2d = pca.fit_transform(embeddings_matrix)
                
                # Create visualization
                plt.figure(figsize=(12, 8))
                
                # Color by cluster if available
                unique_clusters = list(set(cluster_ids))
                colors = plt.cm.Set1(np.linspace(0, 1, len(unique_clusters)))
                
                for i, cluster_id in enumerate(unique_clusters):
                    mask = np.array(cluster_ids) == cluster_id
                    plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                              c=[colors[i]], label=f'Cluster {cluster_id}' if cluster_id >= 0 else 'Unclustered',
                              alpha=0.7, s=50)
                
                plt.title('Content Embedding Visualization (2D PCA)')
                plt.xlabel(f'PC1 (explained variance: {pca.explained_variance_ratio_[0]:.2%})')
                plt.ylabel(f'PC2 (explained variance: {pca.explained_variance_ratio_[1]:.2%})')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                if output_file is None:
                    output_file = str(self.embeddings_dir / f"embedding_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_file
                
        except Exception as e:
            print(f"❌ Error in visualization: {e}")
            return f"Visualization failed: {e}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding database statistics"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic stats
                total_content = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
                content_types = conn.execute("""
                    SELECT content_type, COUNT(*) 
                    FROM embeddings 
                    GROUP BY content_type
                """).fetchall()
                
                source_files = conn.execute("""
                    SELECT COUNT(DISTINCT source_file) 
                    FROM embeddings 
                    WHERE source_file IS NOT NULL
                """).fetchone()[0]
                
                # Cluster stats
                cluster_count = conn.execute("""
                    SELECT COUNT(DISTINCT cluster_id) 
                    FROM content_clusters
                """).fetchone()[0]
                
                clustered_content = conn.execute("SELECT COUNT(*) FROM content_clusters").fetchone()[0]
                
                return {
                    'total_content': total_content,
                    'source_files': source_files,
                    'content_types': dict(content_types),
                    'clusters': cluster_count,
                    'clustered_content': clustered_content,
                    'unclustered_content': total_content - clustered_content
                }
                
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'error': str(e)}


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Embedding Navigation System for Semantic Content Exploration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a file
  python embedding_navigator.py index --file essay.md
  
  # Index directory of files
  python embedding_navigator.py index --dir exports/transformations/
  
  # Search for similar content
  python embedding_navigator.py search --query "philosophy of consciousness"
  
  # Cluster content
  python embedding_navigator.py cluster --clusters 5
  
  # Visualize embeddings
  python embedding_navigator.py visualize --output embedding_map.png
  
  # Get statistics
  python embedding_navigator.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index content for semantic search')
    index_group = index_parser.add_mutually_exclusive_group(required=True)
    index_group.add_argument('--file', type=Path, help='Index single file')
    index_group.add_argument('--dir', type=Path, help='Index directory of files')
    index_parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size for large files')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Semantic search')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    search_parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold')
    
    # Cluster command
    cluster_parser = subparsers.add_parser('cluster', help='Cluster content by similarity')
    cluster_parser.add_argument('--clusters', type=int, default=5, help='Number of clusters')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Create embedding visualization')
    viz_parser.add_argument('--output', help='Output file path')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show embedding statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check dependencies
    missing_deps = []
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        missing_deps.append("sentence-transformers")
    if not SKLEARN_AVAILABLE:
        missing_deps.append("scikit-learn")
    if not PLOTTING_AVAILABLE:
        missing_deps.append("matplotlib seaborn")
    
    if missing_deps and args.command != 'stats':
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print(f"Install with: pip install {' '.join(missing_deps)}")
        return
    
    navigator = EmbeddingNavigator()
    
    if args.command == 'index':
        if args.file:
            result = navigator.index_file(args.file, args.chunk_size)
            if 'error' in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ Indexed {result['indexed']} chunks from {result['file']}")
        
        elif args.dir:
            if not args.dir.exists():
                print(f"❌ Directory not found: {args.dir}")
                return
            
            files = list(args.dir.glob('*.md')) + list(args.dir.glob('*.txt'))
            if not files:
                print(f"❌ No markdown or text files found in {args.dir}")
                return
            
            total_indexed = 0
            for file_path in files:
                result = navigator.index_file(file_path, args.chunk_size)
                if 'error' not in result:
                    total_indexed += result['indexed']
            
            print(f"✅ Total indexed: {total_indexed} chunks from {len(files)} files")
    
    elif args.command == 'search':
        results = navigator.semantic_search(args.query, args.limit, args.threshold)
        
        if not results:
            print(f"❌ No results found for: {args.query}")
            return
        
        print(f"🔍 Search results for: '{args.query}'")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['content_id']} (similarity: {result['similarity']:.3f})")
            print(f"   Source: {result['source_file'] or 'Unknown'}")
            print(f"   Type: {result['content_type']}")
            print(f"   Content: {result['content_text']}")
            print()
    
    elif args.command == 'cluster':
        result = navigator.cluster_content(args.clusters)
        
        if 'error' in result:
            print(f"❌ Clustering failed: {result['error']}")
            return
        
        print(f"🎯 Content clustered into {result['n_clusters']} groups")
        print(f"   Total content: {result['total_content']}")
        print()
        
        for cluster_id, items in result['clusters'].items():
            print(f"Cluster {cluster_id}: {len(items)} items")
            for item in items[:3]:  # Show first 3 items
                print(f"   - {item['content_id']}: {item['text_preview']}")
            if len(items) > 3:
                print(f"   ... and {len(items) - 3} more")
            print()
    
    elif args.command == 'visualize':
        output_file = navigator.visualize_embeddings(args.output)
        print(f"✅ Visualization saved: {output_file}")
    
    elif args.command == 'stats':
        stats = navigator.get_stats()
        
        if 'error' in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        print("📊 Embedding Database Statistics")
        print("=" * 40)
        print(f"Total content: {stats['total_content']}")
        print(f"Source files: {stats['source_files']}")
        print(f"Clusters: {stats['clusters']}")
        print(f"Clustered content: {stats['clustered_content']}")
        print(f"Unclustered content: {stats['unclustered_content']}")
        print()
        print("Content types:")
        for content_type, count in stats['content_types'].items():
            print(f"  {content_type}: {count}")


if __name__ == "__main__":
    main()