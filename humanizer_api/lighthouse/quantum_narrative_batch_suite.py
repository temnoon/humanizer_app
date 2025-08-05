#!/usr/bin/env python3
"""
Quantum Narrative Theory Batch Suite
====================================

A comprehensive batch processing system that uses Project Gutenberg texts to compare
transformation methods: vocabulary projection vs. density matrix vs. hybrid approaches.

This suite will:
1. Use existing Gutenberg infrastructure to access books
2. Select "interesting" passages using selection agents  
3. Apply 4 different attribute settings to each passage
4. Generate all transformation method variations (vocabulary/density_matrix/hybrid)
5. Cache generously to avoid redundant API calls
6. Store results for subjective evaluation

The goal is to discover which method produces more "human" transformations
using the quantum narrative theory formalism.
"""

import asyncio
import json
import logging
import sqlite3
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import hashlib
import pickle
import requests
from threading import Lock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AttributeSet:
    """A specific combination of transformation attributes"""
    set_id: str
    name: str
    description: str
    persona_terms: List[str]
    namespace_terms: List[str] 
    style_terms: List[str]
    guidance_words: List[str]
    
    @classmethod
    def create_test_sets(cls) -> List['AttributeSet']:
        """Create 4 different attribute sets for testing"""
        return [
            cls(
                set_id="analytical_scientific",
                name="Analytical Scientific",
                description="Rigorous, analytical approach to scientific concepts",
                persona_terms=["analytical", "systematic", "empirical"],
                namespace_terms=["scientific", "mathematical", "technological"],
                style_terms=["rigorous", "precise", "technical"],
                guidance_words=["data", "evidence", "analysis", "method"]
            ),
            cls(
                set_id="mystical_contemplative", 
                name="Mystical Contemplative",
                description="Intuitive, mystical approach to spiritual concepts",
                persona_terms=["mystical", "intuitive", "contemplative"],
                namespace_terms=["spiritual", "philosophical", "transcendent"],
                style_terms=["flowing", "poetic", "metaphorical"],
                guidance_words=["essence", "being", "consciousness", "unity"]
            ),
            cls(
                set_id="practical_narrative",
                name="Practical Narrative", 
                description="Direct storytelling with practical focus",
                persona_terms=["practical", "narrative", "experiential"],
                namespace_terms=["personal", "social", "cultural"],
                style_terms=["conversational", "direct", "engaging"],
                guidance_words=["story", "experience", "people", "life"]
            ),
            cls(
                set_id="philosophical_abstract",
                name="Philosophical Abstract",
                description="Abstract philosophical reasoning",
                persona_terms=["philosophical", "abstract", "theoretical"],
                namespace_terms=["conceptual", "universal", "existential"],
                style_terms=["nuanced", "complex", "comprehensive"], 
                guidance_words=["meaning", "truth", "reality", "existence"]
            )
        ]

@dataclass
class PassageCandidate:
    """A text passage candidate for transformation"""
    passage_id: str
    book_id: str
    book_title: str
    author: str
    text: str
    chapter_info: Optional[str]
    word_count: int
    interestingness_score: float
    selection_reasons: List[str]
    
    def __post_init__(self):
        if not self.passage_id:
            # Generate hash-based ID from content
            content_hash = hashlib.md5(self.text.encode()).hexdigest()[:12]
            self.passage_id = f"{self.book_id}_{content_hash}"

@dataclass 
class TransformationResult:
    """Result of applying one transformation method to a passage"""
    result_id: str
    passage_id: str
    attribute_set_id: str
    transformation_method: str  # vocabulary, density_matrix, hybrid
    transformed_text: str
    transformation_quality: float
    processing_time_ms: float
    
    # Method-specific metrics
    fidelity: Optional[float] = None
    purity_change: Optional[float] = None
    entropy_change: Optional[float] = None
    measurement_probs: Optional[Dict[str, float]] = None
    
    # Metadata
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class CacheManager:
    """Intelligent caching system for API calls and results"""
    
    def __init__(self, cache_dir: Path = Path("./quantum_batch_cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.lock = Lock()
        
        # Cache files
        self.gutenberg_cache = self.cache_dir / "gutenberg_books.json" 
        self.passages_cache = self.cache_dir / "passages.json"
        self.transformations_cache = self.cache_dir / "transformations.json"
        
        # Load existing caches
        self.gutenberg_books = self._load_json_cache(self.gutenberg_cache)
        self.passages = self._load_json_cache(self.passages_cache)
        self.transformations = self._load_json_cache(self.transformations_cache)
        
        logger.info(f"Cache loaded: {len(self.gutenberg_books)} books, "
                   f"{len(self.passages)} passages, {len(self.transformations)} transformations")
    
    def _load_json_cache(self, cache_file: Path) -> Dict:
        """Load JSON cache file"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_file}: {e}")
        return {}
    
    def _save_json_cache(self, cache_file: Path, data: Dict):
        """Save JSON cache file"""
        with self.lock:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Failed to save cache {cache_file}: {e}")
    
    def get_cached_book(self, book_id: str) -> Optional[Dict]:
        """Get cached book metadata"""
        return self.gutenberg_books.get(book_id)
    
    def cache_book(self, book_id: str, book_data: Dict):
        """Cache book metadata"""
        self.gutenberg_books[book_id] = book_data
        self._save_json_cache(self.gutenberg_cache, self.gutenberg_books)
    
    def get_cached_passage(self, passage_id: str) -> Optional[PassageCandidate]:
        """Get cached passage"""
        data = self.passages.get(passage_id)
        if data:
            return PassageCandidate(**data)
        return None
    
    def cache_passage(self, passage: PassageCandidate):
        """Cache passage"""
        self.passages[passage.passage_id] = asdict(passage)
        self._save_json_cache(self.passages_cache, self.passages)
    
    def get_cached_transformation(self, passage_id: str, attribute_set_id: str, 
                                method: str) -> Optional[TransformationResult]:
        """Get cached transformation result"""
        cache_key = f"{passage_id}_{attribute_set_id}_{method}"
        data = self.transformations.get(cache_key)
        if data:
            return TransformationResult(**data)
        return None
    
    def cache_transformation(self, result: TransformationResult):
        """Cache transformation result"""
        cache_key = f"{result.passage_id}_{result.attribute_set_id}_{result.transformation_method}"
        self.transformations[cache_key] = asdict(result)
        self._save_json_cache(self.transformations_cache, self.transformations)

class InterestingnessSelector:
    """Agent that selects 'interesting' passages from books"""
    
    def __init__(self, api_base_url: str = "http://localhost:8100"):
        self.api_base_url = api_base_url
    
    def evaluate_passage(self, text: str, book_context: Dict) -> Tuple[float, List[str]]:
        """
        Evaluate how 'interesting' a passage is for narrative transformation.
        
        Returns:
            Tuple of (interestingness_score, list_of_reasons)
        """
        reasons = []
        score = 0.0
        
        # Basic metrics
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        # Ideal length range (not too short, not too long)
        if 50 <= word_count <= 300:
            score += 0.2
            reasons.append("optimal_length")
        
        # Look for narrative elements
        narrative_indicators = [
            "character", "story", "narrative", "tale", "journey", "adventure",
            "experience", "memory", "dream", "vision", "thought", "feeling"
        ]
        
        text_lower = text.lower()
        narrative_count = sum(1 for indicator in narrative_indicators if indicator in text_lower)
        if narrative_count >= 2:
            score += 0.3
            reasons.append("narrative_rich")
        
        # Look for philosophical/abstract content
        abstract_indicators = [
            "consciousness", "reality", "existence", "meaning", "truth", "being",
            "nature", "essence", "understanding", "knowledge", "wisdom", "insight"
        ]
        
        abstract_count = sum(1 for indicator in abstract_indicators if indicator in text_lower)
        if abstract_count >= 2:
            score += 0.25
            reasons.append("philosophically_rich")
        
        # Look for descriptive/literary quality
        literary_indicators = [
            "beauty", "wonder", "mystery", "sublime", "magnificent", "profound",
            "gentle", "fierce", "brilliant", "shadow", "light", "darkness"
        ]
        
        literary_count = sum(1 for indicator in literary_indicators if indicator in text_lower)
        if literary_count >= 1:
            score += 0.15
            reasons.append("literary_quality")
        
        # Avoid purely dialogue or technical passages
        if text.count('"') / len(text) > 0.1:
            score -= 0.1
            reasons.append("high_dialogue_penalty")
        
        # Bonus for complete thoughts
        if text.strip().endswith(('.', '!', '?')):
            score += 0.1
            reasons.append("complete_thought")
        
        return min(1.0, max(0.0, score)), reasons

class QuantumNarrativeBatchSuite:
    """Main batch processing suite for quantum narrative theory experiments"""
    
    def __init__(self, api_base_url: str = "http://localhost:8100"):
        self.api_base_url = api_base_url
        self.cache = CacheManager()
        self.selector = InterestingnessSelector(api_base_url)
        self.attribute_sets = AttributeSet.create_test_sets()
        self.transformation_methods = ["vocabulary", "density_matrix", "hybrid"]
        
        logger.info(f"Initialized batch suite with {len(self.attribute_sets)} attribute sets")
        logger.info(f"Transformation methods: {self.transformation_methods}")
    
    async def discover_interesting_books(self, max_books: int = 20) -> List[Dict]:
        """Discover interesting books from Gutenberg catalog"""
        logger.info(f"Discovering up to {max_books} interesting books...")
        
        try:
            # Get popular books first
            response = requests.get(f"{self.api_base_url}/gutenberg/catalog/popular", 
                                  params={"limit": max_books * 2})
            if response.status_code == 200:
                books = response.json().get("books", [])
                
                # Filter for interesting books
                interesting_books = []
                for book in books[:max_books]:
                    # Check cache first
                    book_id = str(book.get("id", book.get("gutenberg_id")))
                    if self.cache.get_cached_book(book_id):
                        interesting_books.append(self.cache.get_cached_book(book_id))
                        continue
                    
                    # Evaluate interestingness
                    title = book.get("title", "")
                    subjects = book.get("subjects", [])
                    
                    # Prefer literature, philosophy, narrative works
                    interesting_subjects = {
                        "literature", "fiction", "philosophy", "psychology", 
                        "narrative", "stories", "novels", "tales", "poetry"
                    }
                    
                    subject_match = any(
                        any(interesting in subj.lower() for interesting in interesting_subjects)
                        for subj in subjects
                    )
                    
                    if subject_match or any(word in title.lower() for word in 
                                          ["story", "tale", "narrative", "journey", "life"]):
                        interesting_books.append(book)
                        self.cache.cache_book(book_id, book)
                
                logger.info(f"Found {len(interesting_books)} interesting books")
                return interesting_books[:max_books]
            
        except Exception as e:
            logger.error(f"Failed to discover books: {e}")
        
        return []
    
    async def extract_passages_from_book(self, book: Dict, max_passages: int = 5) -> List[PassageCandidate]:
        """Extract interesting passages from a book"""
        book_id = str(book.get("id", book.get("gutenberg_id")))
        book_title = book.get("title", "Unknown")
        author = book.get("author", "Unknown")
        
        logger.info(f"Extracting passages from '{book_title}' by {author}")
        
        try:
            # Try to get book content via existing Gutenberg API
            response = requests.post(f"{self.api_base_url}/gutenberg/strategic-sample", 
                                   json={
                                       "gutenberg_ids": [int(book_id)],
                                       "sample_size": max_passages * 3,  # Get extra to filter
                                       "min_length": 100,
                                       "max_length": 500
                                   })
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data.get("job_id")
                
                # Wait for job completion (with timeout)
                for _ in range(30):  # 30 second timeout
                    time.sleep(1)
                    status_response = requests.get(f"{self.api_base_url}/gutenberg/jobs/{job_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("status") == "completed":
                            break
                else:
                    logger.warning(f"Job {job_id} did not complete in time")
                    return []
                
                # Get results
                results_response = requests.get(f"{self.api_base_url}/gutenberg/jobs/{job_id}/results")
                if results_response.status_code == 200:
                    results_data = results_response.json()
                    paragraphs = results_data.get("results", [])
                    
                    # Convert to PassageCandidate objects and evaluate
                    candidates = []
                    for para in paragraphs:
                        text = para.get("text", "").strip()
                        if not text or len(text) < 50:
                            continue
                        
                        # Evaluate interestingness
                        score, reasons = self.selector.evaluate_passage(text, book)
                        
                        if score > 0.3:  # Threshold for interestingness
                            candidate = PassageCandidate(
                                passage_id="",  # Will be auto-generated
                                book_id=book_id,
                                book_title=book_title,
                                author=author,
                                text=text,
                                chapter_info=para.get("chapter_title"),
                                word_count=len(text.split()),
                                interestingness_score=score,
                                selection_reasons=reasons
                            )
                            candidates.append(candidate)
                            self.cache.cache_passage(candidate)
                    
                    # Sort by interestingness and return top passages
                    candidates.sort(key=lambda x: x.interestingness_score, reverse=True)
                    selected = candidates[:max_passages]
                    
                    logger.info(f"Selected {len(selected)} passages from {book_title}")
                    return selected
        
        except Exception as e:
            logger.error(f"Failed to extract passages from {book_title}: {e}")
        
        return []
    
    async def transform_passage(self, passage: PassageCandidate, 
                              attribute_set: AttributeSet,
                              method: str) -> Optional[TransformationResult]:
        """Transform a passage using specified attributes and method"""
        
        # Check cache first
        cached = self.cache.get_cached_transformation(
            passage.passage_id, attribute_set.set_id, method
        )
        if cached:
            return cached
        
        logger.info(f"Transforming passage {passage.passage_id} with {attribute_set.name} ({method})")
        
        try:
            start_time = time.time()
            
            # Prepare transformation request
            request_data = {
                "input_text": passage.text,
                "persona_terms": attribute_set.persona_terms,
                "namespace_terms": attribute_set.namespace_terms,
                "style_terms": attribute_set.style_terms,
                "guidance_words": attribute_set.guidance_words,
                "transformation_method": method,
                "projection_intensity": 1.0,
                "reading_style": "interpretation",
                "semantic_dimension": 32,
                "use_vocabulary_system": True,
                "extract_source_attributes": True
            }
            
            response = requests.post(f"{self.api_base_url}/api/density-matrix/transform",
                                   json=request_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result_data = response.json()
                
                if result_data.get("success"):
                    # Extract method-specific metrics
                    metrics = result_data.get("transformation_metrics", {})
                    
                    result = TransformationResult(
                        result_id=str(uuid.uuid4()),
                        passage_id=passage.passage_id,
                        attribute_set_id=attribute_set.set_id,
                        transformation_method=method,
                        transformed_text=result_data.get("transformed_text", ""),
                        transformation_quality=result_data.get("transformation_quality", 0.0),
                        processing_time_ms=processing_time,
                        fidelity=metrics.get("fidelity"),
                        purity_change=metrics.get("purity_change"),
                        entropy_change=metrics.get("entropy_change"),
                        measurement_probs=result_data.get("measurement_probabilities")
                    )
                    
                    self.cache.cache_transformation(result)
                    return result
                else:
                    logger.error(f"Transformation failed: {result_data.get('error_message')}")
            else:
                logger.error(f"API request failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Transformation error: {e}")
        
        return None
    
    async def run_comprehensive_batch(self, max_books: int = 10, 
                                    passages_per_book: int = 3) -> Dict[str, Any]:
        """Run comprehensive batch processing"""
        
        start_time = datetime.now()
        logger.info(f"Starting comprehensive batch processing: {max_books} books, "
                   f"{passages_per_book} passages each")
        
        # Phase 1: Discover books
        books = await self.discover_interesting_books(max_books)
        if not books:
            logger.error("No books discovered")
            return {"error": "No books found"}
        
        # Phase 2: Extract passages
        all_passages = []
        for book in books:
            passages = await self.extract_passages_from_book(book, passages_per_book)
            all_passages.extend(passages)
        
        logger.info(f"Extracted {len(all_passages)} total passages")
        
        # Phase 3: Transform all passages with all attribute sets and methods
        all_results = {}
        total_transformations = len(all_passages) * len(self.attribute_sets) * len(self.transformation_methods)
        completed = 0
        
        for passage in all_passages:
            passage_results = {}
            
            for attribute_set in self.attribute_sets:
                method_results = {}
                
                for method in self.transformation_methods:
                    result = await self.transform_passage(passage, attribute_set, method)
                    if result:
                        method_results[method] = result
                    
                    completed += 1
                    logger.info(f"Progress: {completed}/{total_transformations} "
                               f"({completed/total_transformations*100:.1f}%)")
                
                if method_results:
                    passage_results[attribute_set.set_id] = method_results
            
            if passage_results:
                all_results[passage.passage_id] = {
                    "passage": passage,
                    "transformations": passage_results
                }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = {
            "batch_id": str(uuid.uuid4()),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_seconds": duration,
            "books_processed": len(books),
            "passages_processed": len(all_passages),
            "transformations_completed": completed,
            "results": all_results,
            "attribute_sets": [asdict(attr_set) for attr_set in self.attribute_sets],
            "transformation_methods": self.transformation_methods
        }
        
        # Save comprehensive results
        results_file = Path(f"quantum_batch_results_{start_time.strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Batch processing completed in {duration:.1f} seconds")
        logger.info(f"Results saved to {results_file}")
        
        return summary

def main():
    """Main entry point for batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Narrative Theory Batch Suite")
    parser.add_argument("--books", type=int, default=5, help="Number of books to process")
    parser.add_argument("--passages", type=int, default=3, help="Passages per book") 
    parser.add_argument("--api-url", default="http://localhost:8100", help="API base URL")
    
    args = parser.parse_args()
    
    suite = QuantumNarrativeBatchSuite(api_base_url=args.api_url)
    
    # Run batch processing
    results = asyncio.run(suite.run_comprehensive_batch(
        max_books=args.books,
        passages_per_book=args.passages
    ))
    
    if "error" not in results:
        print(f"\n🎉 Batch processing completed successfully!")
        print(f"📊 Processed {results['passages_processed']} passages")
        print(f"⚡ Completed {results['transformations_completed']} transformations") 
        print(f"⏱️  Total time: {results['duration_seconds']:.1f} seconds")
        print(f"💾 Results available for subjective evaluation")
    else:
        print(f"❌ Batch processing failed: {results['error']}")

if __name__ == "__main__":
    main()