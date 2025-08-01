"""
Gutenberg Book Analysis Service
Business logic for downloading, cleaning, and analyzing Project Gutenberg books
"""
import asyncio
import logging
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import aiofiles

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from models import ContentMetadata, ContentType

logger = logging.getLogger(__name__)


@dataclass
class GutenbergBook:
    """Represents a Project Gutenberg book"""
    gutenberg_id: int
    title: str
    author: str
    language: str
    subjects: List[str]
    download_url: str
    file_size: Optional[int] = None
    encoding: str = "utf-8"


@dataclass
class BookParagraph:
    """Represents an analyzed paragraph from a book"""
    paragraph_id: str
    book_id: int
    chapter_title: Optional[str]
    paragraph_text: str
    paragraph_index: int
    word_count: int
    sentence_count: int
    complexity_score: float
    narrative_quality_score: float
    attribute_enrichment_score: float
    extracted_concepts: List[str]
    emotional_tone: str
    literary_devices: List[str]


@dataclass
class BookAnalysisJob:
    """Represents a book analysis batch job"""
    job_id: str
    gutenberg_ids: List[int]
    analysis_type: str  # "full", "sample", "targeted"
    status: str  # "pending", "running", "completed", "failed"
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class GutenbergService:
    """Service for analyzing Project Gutenberg books"""
    
    def __init__(self):
        self.base_url = "https://www.gutenberg.org"
        self.cache_dir = Path("./data/gutenberg_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.active_jobs: Dict[str, BookAnalysisJob] = {}
        
    async def search_books(self, 
                          query: Optional[str] = None,
                          author: Optional[str] = None,
                          subject: Optional[str] = None,
                          language: str = "en",
                          limit: int = 50) -> List[GutenbergBook]:
        """Search Project Gutenberg catalog"""
        
        try:
            # Use Gutenberg's search API or scrape catalog
            search_url = f"{self.base_url}/ebooks/search/"
            params = {
                "query": query or "",
                "submit_search": "Search",
                "sort_order": "downloads"
            }
            
            if author:
                params["author"] = author
            if subject:
                params["subject"] = subject
            if language != "en":
                params["lang"] = language
                
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        books = self._parse_search_results(html_content, limit)
                        return books
                    else:
                        logger.error(f"Search failed with status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching Gutenberg: {e}")
            return []
    
    def _parse_search_results(self, html_content: str, limit: int) -> List[GutenbergBook]:
        """Parse HTML search results into GutenbergBook objects"""
        books = []
        
        # Regex patterns for extracting book information
        book_pattern = r'<li class="booklink">.*?</li>'
        title_pattern = r'<a href="/ebooks/(\d+)"[^>]*>([^<]+)</a>'
        author_pattern = r'<span class="subtitle">by ([^<]+)</span>'
        
        book_matches = re.findall(book_pattern, html_content, re.DOTALL)
        
        for book_html in book_matches[:limit]:
            try:
                title_match = re.search(title_pattern, book_html)
                author_match = re.search(author_pattern, book_html)
                
                if title_match:
                    gutenberg_id = int(title_match.group(1))
                    title = title_match.group(2).strip()
                    author = author_match.group(1).strip() if author_match else "Unknown"
                    
                    # Construct download URL for plain text
                    download_url = f"{self.base_url}/files/{gutenberg_id}/{gutenberg_id}-0.txt"
                    
                    book = GutenbergBook(
                        gutenberg_id=gutenberg_id,
                        title=title,
                        author=author,
                        language="en",  # Default assumption
                        subjects=[],  # Would need additional parsing
                        download_url=download_url
                    )
                    books.append(book)
                    
            except Exception as e:
                logger.warning(f"Error parsing book entry: {e}")
                continue
                
        return books
    
    async def download_book(self, book: GutenbergBook) -> Optional[str]:
        """Download book text and cache locally"""
        
        cache_file = self.cache_dir / f"{book.gutenberg_id}.txt"
        
        # Return cached version if available
        if cache_file.exists():
            async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                return await f.read()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(book.download_url) as response:
                    if response.status == 200:
                        content = await response.text(encoding='utf-8')
                        
                        # Cache the downloaded content
                        async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                            await f.write(content)
                        
                        logger.info(f"Downloaded and cached book {book.gutenberg_id}: {book.title}")
                        return content
                    else:
                        logger.error(f"Failed to download book {book.gutenberg_id}: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error downloading book {book.gutenberg_id}: {e}")
            return None
    
    def clean_gutenberg_text(self, raw_text: str) -> Tuple[str, Dict[str, Any]]:
        """Clean and preprocess Gutenberg text"""
        
        metadata = {
            "original_length": len(raw_text),
            "paragraphs_found": 0,
            "chapters_found": 0,
            "header_removed": False,
            "footer_removed": False
        }
        
        # Remove Gutenberg header (everything before "*** START OF...")
        start_pattern = r'\*\*\*\s*START OF TH[IE] PROJECT GUTENBERG.*?\*\*\*'
        start_match = re.search(start_pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if start_match:
            raw_text = raw_text[start_match.end():]
            metadata["header_removed"] = True
        
        # Remove Gutenberg footer (everything after "*** END OF...")
        end_pattern = r'\*\*\*\s*END OF TH[IE] PROJECT GUTENBERG.*?\*\*\*'
        end_match = re.search(end_pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if end_match:
            raw_text = raw_text[:end_match.start()]
            metadata["footer_removed"] = True
        
        # Clean up formatting
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\n{3,}', '\n\n', raw_text)
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
        
        # Remove page break indicators
        cleaned_text = re.sub(r'\n\s*\d+\s*\n', '\n', cleaned_text)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
        metadata["paragraphs_found"] = len(paragraphs)
        
        # Detect chapters
        chapter_pattern = r'^(CHAPTER|Chapter|chapter)\s+[IVXLCDM\d]+.*$'
        chapters = [p for p in paragraphs if re.match(chapter_pattern, p)]
        metadata["chapters_found"] = len(chapters)
        
        cleaned_text = '\n\n'.join(paragraphs)
        metadata["cleaned_length"] = len(cleaned_text)
        
        return cleaned_text, metadata
    
    async def analyze_paragraph(self, 
                               paragraph: str, 
                               paragraph_index: int,
                               book_id: int,
                               chapter_title: Optional[str] = None) -> BookParagraph:
        """Analyze a single paragraph for attribute enrichment potential"""
        
        # Basic text statistics
        word_count = len(paragraph.split())
        sentence_count = len(re.findall(r'[.!?]+', paragraph))
        
        # Complexity scoring (basic implementation)
        avg_word_length = sum(len(word) for word in paragraph.split()) / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        complexity_score = min((avg_word_length * 0.1) + (avg_sentence_length * 0.05), 1.0)
        
        # Narrative quality indicators
        narrative_indicators = [
            r'\b(he|she|they|I|we)\s+(said|thought|felt|saw|heard|went|came|looked)\b',
            r'\b(suddenly|then|now|later|meanwhile|however|although)\b',
            r'["""'''].*?["""''']',  # Dialogue
            r'\b(character|story|plot|scene|setting)\b'
        ]
        
        narrative_score = 0.0
        for pattern in narrative_indicators:
            matches = len(re.findall(pattern, paragraph, re.IGNORECASE))
            narrative_score += matches * 0.1
        
        narrative_quality_score = min(narrative_score, 1.0)
        
        # Attribute enrichment potential
        enrichment_indicators = [
            r'\b(suddenly|mysterious|ancient|powerful|wise|brave|noble|evil)\b',
            r'\b(magic|spell|enchant|transform|reveal|discover|journey|quest)\b',
            r'\b(palace|castle|forest|mountain|ocean|kingdom|village|city)\b',
            r'\b(love|hate|fear|joy|anger|sorrow|hope|despair)\b'
        ]
        
        enrichment_score = 0.0
        extracted_concepts = []
        
        for pattern in enrichment_indicators:
            matches = re.findall(pattern, paragraph, re.IGNORECASE)
            if matches:
                enrichment_score += len(matches) * 0.15
                extracted_concepts.extend([match.lower() for match in matches])
        
        attribute_enrichment_score = min(enrichment_score, 1.0)
        
        # Emotional tone detection (simplified)
        positive_words = r'\b(happy|joy|love|beautiful|wonderful|amazing|brilliant)\b'
        negative_words = r'\b(sad|angry|fear|dark|terrible|awful|horrible|death)\b'
        neutral_words = r'\b(said|went|came|looked|found|made|took|gave)\b'
        
        pos_count = len(re.findall(positive_words, paragraph, re.IGNORECASE))
        neg_count = len(re.findall(negative_words, paragraph, re.IGNORECASE))
        neu_count = len(re.findall(neutral_words, paragraph, re.IGNORECASE))
        
        if pos_count > neg_count and pos_count > neu_count:
            emotional_tone = "positive"
        elif neg_count > pos_count and neg_count > neu_count:
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"
        
        # Literary devices detection
        literary_devices = []
        if re.search(r'\b\w+\s+like\s+\w+\b', paragraph, re.IGNORECASE):
            literary_devices.append("simile")
        if re.search(r'\b\w+\s+(is|was|are|were)\s+\w+\b', paragraph, re.IGNORECASE):
            literary_devices.append("metaphor")
        if re.search(r'\b(\w)\1{2,}\b', paragraph):
            literary_devices.append("alliteration")
        
        return BookParagraph(
            paragraph_id=str(uuid.uuid4()),
            book_id=book_id,
            chapter_title=chapter_title,
            paragraph_text=paragraph,
            paragraph_index=paragraph_index,
            word_count=word_count,
            sentence_count=sentence_count,
            complexity_score=complexity_score,
            narrative_quality_score=narrative_quality_score,
            attribute_enrichment_score=attribute_enrichment_score,
            extracted_concepts=list(set(extracted_concepts)),
            emotional_tone=emotional_tone,
            literary_devices=literary_devices
        )
    
    async def create_analysis_job(self, 
                                 gutenberg_ids: List[int],
                                 analysis_type: str = "sample") -> str:
        """Create a new book analysis batch job"""
        
        job_id = str(uuid.uuid4())
        job = BookAnalysisJob(
            job_id=job_id,
            gutenberg_ids=gutenberg_ids,
            analysis_type=analysis_type,
            status="pending",
            progress=0.0,
            created_at=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        
        # Start the job asynchronously
        asyncio.create_task(self._run_analysis_job(job))
        
        logger.info(f"Created analysis job {job_id} for {len(gutenberg_ids)} books")
        return job_id
    
    async def _run_analysis_job(self, job: BookAnalysisJob):
        """Execute the book analysis job"""
        
        try:
            job.status = "running"
            job.started_at = datetime.now()
            
            total_books = len(job.gutenberg_ids)
            analyzed_paragraphs = []
            
            for i, gutenberg_id in enumerate(job.gutenberg_ids):
                try:
                    # Create a basic book object for download
                    book = GutenbergBook(
                        gutenberg_id=gutenberg_id,
                        title=f"Book {gutenberg_id}",
                        author="Unknown",
                        language="en",
                        subjects=[],
                        download_url=f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt"
                    )
                    
                    # Download and clean book
                    raw_text = await self.download_book(book)
                    if not raw_text:
                        continue
                    
                    cleaned_text, metadata = self.clean_gutenberg_text(raw_text)
                    paragraphs = cleaned_text.split('\n\n')
                    
                    # Sample paragraphs based on analysis type
                    if job.analysis_type == "sample":
                        # Take every 10th paragraph for sampling
                        sample_paragraphs = paragraphs[::10][:20]  # Max 20 samples per book
                    elif job.analysis_type == "targeted":
                        # Take paragraphs with high potential (simple heuristic)
                        sample_paragraphs = [p for p in paragraphs if len(p.split()) > 50 and len(p.split()) < 200][:30]
                    else:  # "full"
                        sample_paragraphs = paragraphs
                    
                    # Analyze selected paragraphs
                    for j, paragraph in enumerate(sample_paragraphs):
                        if paragraph.strip():
                            analyzed_paragraph = await self.analyze_paragraph(
                                paragraph.strip(), j, gutenberg_id
                            )
                            analyzed_paragraphs.append(analyzed_paragraph)
                    
                    # Update progress
                    job.progress = (i + 1) / total_books
                    
                except Exception as e:
                    logger.error(f"Error analyzing book {gutenberg_id}: {e}")
                    continue
            
            # Filter high-quality paragraphs for attribute enrichment
            high_quality_paragraphs = [
                p for p in analyzed_paragraphs 
                if p.attribute_enrichment_score > 0.3 and p.word_count > 30
            ]
            
            # Sort by enrichment score
            high_quality_paragraphs.sort(key=lambda x: x.attribute_enrichment_score, reverse=True)
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.results_summary = {
                "total_paragraphs_analyzed": len(analyzed_paragraphs),
                "high_quality_candidates": len(high_quality_paragraphs),
                "avg_enrichment_score": sum(p.attribute_enrichment_score for p in high_quality_paragraphs) / max(len(high_quality_paragraphs), 1),
                "top_concepts": self._extract_top_concepts(high_quality_paragraphs),
                "emotional_distribution": self._analyze_emotional_distribution(high_quality_paragraphs)
            }
            
            # Store results (in real implementation, would save to database)
            results_file = self.cache_dir / f"analysis_results_{job.job_id}.json"
            import json
            async with aiofiles.open(results_file, 'w') as f:
                results_data = {
                    "job": asdict(job),
                    "high_quality_paragraphs": [asdict(p) for p in high_quality_paragraphs[:100]]  # Top 100
                }
                await f.write(json.dumps(results_data, default=str, indent=2))
            
            logger.info(f"Analysis job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            logger.error(f"Analysis job {job.job_id} failed: {e}")
    
    def _extract_top_concepts(self, paragraphs: List[BookParagraph]) -> List[str]:
        """Extract most common concepts from analyzed paragraphs"""
        concept_counts = {}
        for paragraph in paragraphs:
            for concept in paragraph.extracted_concepts:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        return sorted(concept_counts.keys(), key=lambda x: concept_counts[x], reverse=True)[:20]
    
    def _analyze_emotional_distribution(self, paragraphs: List[BookParagraph]) -> Dict[str, float]:
        """Analyze emotional tone distribution"""
        tone_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for paragraph in paragraphs:
            tone_counts[paragraph.emotional_tone] += 1
        
        total = len(paragraphs)
        return {tone: count / total for tone, count in tone_counts.items()}
    
    async def get_job_status(self, job_id: str) -> Optional[BookAnalysisJob]:
        """Get status of an analysis job"""
        return self.active_jobs.get(job_id)
    
    async def list_jobs(self) -> List[BookAnalysisJob]:
        """List all analysis jobs"""
        return list(self.active_jobs.values())
    
    async def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get results of a completed analysis job"""
        results_file = self.cache_dir / f"analysis_results_{job_id}.json"
        
        if results_file.exists():
            import json
            async with aiofiles.open(results_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        
        return None


# Global service instance
gutenberg_service = GutenbergService()