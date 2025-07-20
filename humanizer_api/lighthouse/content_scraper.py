"""
Intelligent Content Scraping System for Attribute Generation
Scrapes high-quality public sources and processes them through the advanced attribute system.
"""

import asyncio
import aiohttp
import logging
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib
import time

from advanced_attribute_system import AdvancedAttributeGenerator, AdvancedAttribute

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ContentSource:
    """Defines a content source for scraping."""
    name: str
    base_url: str
    content_patterns: List[str]  # CSS selectors or XPath expressions
    quality_threshold: float = 0.7
    rate_limit_delay: float = 1.0  # Seconds between requests
    allowed_content_types: Set[str] = field(default_factory=lambda: {"text/html", "application/json"})
    extraction_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScrapedContent:
    """Represents scraped content with metadata."""
    url: str
    title: str
    content: str
    source: str
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    content_hash: str = field(default="")
    quality_score: float = 0.0
    word_count: int = 0
    language: str = "en"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.content_hash = hashlib.md5(self.content.encode()).hexdigest()
        self.word_count = len(self.content.split())

class QualityAnalyzer:
    """Analyzes content quality for attribute generation suitability."""
    
    def __init__(self):
        self.quality_metrics = {
            "min_word_count": 50,
            "max_word_count": 5000,
            "min_sentence_length": 5,
            "coherence_threshold": 0.3,
            "complexity_threshold": 0.2
        }
    
    def analyze_quality(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze content quality and return score with detailed metrics."""
        metrics = {}
        
        # Basic length metrics
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        metrics['word_count'] = word_count
        metrics['sentence_count'] = sentence_count
        metrics['avg_sentence_length'] = avg_sentence_length
        
        # Length score
        if word_count < self.quality_metrics["min_word_count"]:
            length_score = word_count / self.quality_metrics["min_word_count"]
        elif word_count > self.quality_metrics["max_word_count"]:
            length_score = self.quality_metrics["max_word_count"] / word_count
        else:
            length_score = 1.0
        
        # Sentence structure score
        if avg_sentence_length < self.quality_metrics["min_sentence_length"]:
            structure_score = 0.3
        elif avg_sentence_length > 50:
            structure_score = 0.7
        else:
            structure_score = 1.0
        
        # Coherence indicators
        coherence_markers = ["therefore", "however", "moreover", "furthermore", "consequently", 
                           "in addition", "for example", "in contrast", "similarly", "meanwhile"]
        coherence_count = sum(1 for marker in coherence_markers if marker in content.lower())
        coherence_score = min(1.0, coherence_count / (sentence_count * 0.1)) if sentence_count > 0 else 0
        
        # Complexity indicators
        complexity_markers = ["although", "nevertheless", "whereas", "notwithstanding", 
                            "complexity", "nuanced", "sophisticated", "intricate"]
        complexity_count = sum(1 for marker in complexity_markers if marker in content.lower())
        complexity_score = min(1.0, complexity_count / (sentence_count * 0.05)) if sentence_count > 0 else 0
        
        # Repetition penalty
        words = content.lower().split()
        unique_words = len(set(words))
        repetition_score = unique_words / len(words) if words else 0
        
        metrics.update({
            'length_score': length_score,
            'structure_score': structure_score,
            'coherence_score': coherence_score,
            'complexity_score': complexity_score,
            'repetition_score': repetition_score
        })
        
        # Overall quality score
        quality_score = (
            length_score * 0.2 +
            structure_score * 0.2 +
            coherence_score * 0.25 +
            complexity_score * 0.25 +
            repetition_score * 0.1
        )
        
        return quality_score, metrics

class ContentScraper:
    """Intelligent content scraper with quality filtering."""
    
    def __init__(self):
        self.quality_analyzer = QualityAnalyzer()
        self.scraped_urls = set()
        self.content_cache = {}
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LighthouseAttributeBot/1.0)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def scrape_source(self, source: ContentSource, max_pages: int = 10) -> List[ScrapedContent]:
        """Scrape content from a specific source."""
        scraped_content = []
        
        try:
            # Discover URLs to scrape
            urls_to_scrape = await self._discover_urls(source, max_pages)
            
            # Scrape each URL with rate limiting
            for url in urls_to_scrape:
                if url in self.scraped_urls:
                    continue
                
                try:
                    content = await self._scrape_url(url, source)
                    if content:
                        # Analyze quality
                        quality_score, metrics = self.quality_analyzer.analyze_quality(content.content)
                        content.quality_score = quality_score
                        
                        # Only keep high-quality content
                        if quality_score >= source.quality_threshold:
                            scraped_content.append(content)
                            self.scraped_urls.add(url)
                            logger.info(f"Scraped high-quality content from {url} (quality: {quality_score:.2f})")
                        else:
                            logger.debug(f"Rejected low-quality content from {url} (quality: {quality_score:.2f})")
                    
                    # Rate limiting
                    await asyncio.sleep(source.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping source {source.name}: {e}")
        
        return scraped_content
    
    async def _discover_urls(self, source: ContentSource, max_pages: int) -> List[str]:
        """Discover URLs to scrape from a source."""
        urls = []
        
        try:
            # Start with base URL
            async with self.session.get(source.base_url) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    # Extract links based on source configuration
                    if source.name == "philosophical_essays":
                        # Look for essay or article links
                        pattern = r'href="([^"]*(?:essay|article|post)[^"]*)"'
                    elif source.name == "academic_papers":
                        # Look for paper or publication links
                        pattern = r'href="([^"]*(?:paper|publication|journal)[^"]*)"'
                    else:
                        # Generic content links
                        pattern = r'href="([^"]*)"'
                    
                    found_links = re.findall(pattern, text, re.IGNORECASE)
                    
                    # Convert relative URLs to absolute
                    for link in found_links[:max_pages]:
                        absolute_url = urljoin(source.base_url, link)
                        if self._is_valid_url(absolute_url, source):
                            urls.append(absolute_url)
                            
        except Exception as e:
            logger.error(f"Error discovering URLs for {source.name}: {e}")
        
        return urls
    
    async def _scrape_url(self, url: str, source: ContentSource) -> Optional[ScrapedContent]:
        """Scrape content from a single URL."""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                content_type = response.headers.get('content-type', '').lower()
                if not any(allowed in content_type for allowed in source.allowed_content_types):
                    return None
                
                html = await response.text()
                
                # Extract content based on patterns
                extracted_content = self._extract_content(html, source)
                if not extracted_content:
                    return None
                
                # Extract title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else "Untitled"
                
                return ScrapedContent(
                    url=url,
                    title=title,
                    content=extracted_content,
                    source=source.name
                )
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return None
    
    def _extract_content(self, html: str, source: ContentSource) -> str:
        """Extract meaningful content from HTML."""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Try to extract content based on common patterns
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*entry[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*>(.*?)</p>'  # Fallback to paragraphs
        ]
        
        for pattern in content_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            if matches:
                content = ' '.join(matches)
                # Clean HTML tags
                content = re.sub(r'<[^>]+>', ' ', content)
                # Clean whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                
                if len(content) > 100:  # Minimum content length
                    return content
        
        return ""
    
    def _is_valid_url(self, url: str, source: ContentSource) -> bool:
        """Check if URL is valid for scraping."""
        parsed = urlparse(url)
        
        # Must be from same domain
        if parsed.netloc not in source.base_url:
            return False
        
        # Skip certain file types
        skip_extensions = {'.pdf', '.doc', '.docx', '.zip', '.tar', '.gz'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip common non-content pages
        skip_patterns = ['login', 'register', 'cart', 'checkout', 'contact', 'privacy', 'terms']
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        return True

class BatchAttributeProcessor:
    """Processes scraped content in batches to generate attributes."""
    
    def __init__(self):
        self.attribute_generator = AdvancedAttributeGenerator()
        self.scraper = ContentScraper()
        
    async def process_content_batch(self, sources: List[ContentSource], 
                                  negative_scope: Set[str] = None,
                                  target_namespace: str = None) -> Dict[str, Any]:
        """Process multiple content sources and generate attributes."""
        
        if negative_scope is None:
            negative_scope = {"Earth", "America", "Europe", "Asia", "human", "people", "society"}
        
        all_content = []
        generated_attributes = []
        processing_stats = {
            "sources_processed": 0,
            "content_pieces_scraped": 0,
            "high_quality_content": 0,
            "attributes_generated": 0,
            "processing_time": 0,
            "errors": []
        }
        
        start_time = time.time()
        
        try:
            async with self.scraper:
                # Process each source
                for source in sources:
                    try:
                        logger.info(f"Processing source: {source.name}")
                        scraped_content = await self.scraper.scrape_source(source)
                        
                        all_content.extend(scraped_content)
                        processing_stats["sources_processed"] += 1
                        processing_stats["content_pieces_scraped"] += len(scraped_content)
                        
                        # Generate attributes from high-quality content
                        for content in scraped_content:
                            if content.quality_score >= 0.7:
                                try:
                                    attributes = await self.attribute_generator.generate_from_content(
                                        content.content,
                                        target_namespace=target_namespace,
                                        negative_scope=negative_scope
                                    )
                                    
                                    # Add source metadata to attributes
                                    for attr in attributes:
                                        attr.source_content_hash = content.content_hash
                                        attr.derivation_path = [source.name, content.url]
                                        attr.usage_contexts.append({
                                            "source": source.name,
                                            "url": content.url,
                                            "scraped_at": content.scraped_at,
                                            "quality_score": content.quality_score
                                        })
                                    
                                    generated_attributes.extend(attributes)
                                    processing_stats["high_quality_content"] += 1
                                    processing_stats["attributes_generated"] += len(attributes)
                                    
                                except Exception as e:
                                    error_msg = f"Error generating attributes from {content.url}: {e}"
                                    logger.error(error_msg)
                                    processing_stats["errors"].append(error_msg)
                        
                    except Exception as e:
                        error_msg = f"Error processing source {source.name}: {e}"
                        logger.error(error_msg)
                        processing_stats["errors"].append(error_msg)
                
                processing_stats["processing_time"] = time.time() - start_time
                
                # Generate summary report
                report = self._generate_processing_report(generated_attributes, processing_stats)
                
                return {
                    "attributes": generated_attributes,
                    "content": all_content,
                    "statistics": processing_stats,
                    "report": report
                }
                
        except Exception as e:
            error_msg = f"Fatal error in batch processing: {e}"
            logger.error(error_msg)
            processing_stats["errors"].append(error_msg)
            processing_stats["processing_time"] = time.time() - start_time
            
            return {
                "attributes": generated_attributes,
                "content": all_content,
                "statistics": processing_stats,
                "report": f"Processing failed: {error_msg}"
            }
    
    def _generate_processing_report(self, attributes: List[AdvancedAttribute], 
                                  stats: Dict[str, Any]) -> str:
        """Generate a comprehensive processing report."""
        
        # Analyze attribute types
        type_counts = {}
        confidence_scores = []
        noetic_patterns_count = 0
        
        for attr in attributes:
            attr_type = attr.type.value
            type_counts[attr_type] = type_counts.get(attr_type, 0) + 1
            confidence_scores.append(attr.confidence_score)
            if attr.noetic_patterns:
                noetic_patterns_count += len(attr.noetic_patterns)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        report = f"""
# Batch Attribute Processing Report

## Summary Statistics
- **Sources Processed**: {stats['sources_processed']}
- **Content Pieces Scraped**: {stats['content_pieces_scraped']}
- **High-Quality Content**: {stats['high_quality_content']}
- **Total Attributes Generated**: {stats['attributes_generated']}
- **Processing Time**: {stats['processing_time']:.2f} seconds
- **Average Confidence Score**: {avg_confidence:.3f}

## Attribute Type Distribution
"""
        
        for attr_type, count in type_counts.items():
            percentage = (count / len(attributes)) * 100 if attributes else 0
            report += f"- **{attr_type.replace('_', ' ').title()}**: {count} ({percentage:.1f}%)\n"
        
        report += f"""
## Noetic Analysis
- **Total Consciousness Patterns Detected**: {noetic_patterns_count}
- **Average Patterns per Attribute**: {noetic_patterns_count / len(attributes):.1f}

## Quality Metrics
- **Content Quality Threshold**: 70%
- **Attribute Confidence Range**: {min(confidence_scores):.2f} - {max(confidence_scores):.2f}
- **Processing Efficiency**: {stats['attributes_generated'] / stats['processing_time']:.2f} attributes/second
"""
        
        if stats["errors"]:
            report += f"\n## Errors Encountered\n"
            for error in stats["errors"][:5]:  # Show first 5 errors
                report += f"- {error}\n"
            if len(stats["errors"]) > 5:
                report += f"- ... and {len(stats['errors']) - 5} more errors\n"
        
        return report

# Predefined high-quality content sources
def get_default_content_sources() -> List[ContentSource]:
    """Get a list of high-quality public content sources."""
    return [
        ContentSource(
            name="philosophical_essays",
            base_url="https://plato.stanford.edu",
            content_patterns=["article", "main", ".entry-content"],
            quality_threshold=0.8,
            rate_limit_delay=2.0
        ),
        ContentSource(
            name="academic_papers",
            base_url="https://arxiv.org",
            content_patterns=[".abstract", ".full-text"],
            quality_threshold=0.75,
            rate_limit_delay=1.5
        ),
        ContentSource(
            name="thoughtful_blogs",
            base_url="https://waitbutwhy.com",
            content_patterns=[".post-content", "article", "main"],
            quality_threshold=0.7,
            rate_limit_delay=1.0
        )
    ]

# Example usage
if __name__ == "__main__":
    async def test_batch_processing():
        processor = BatchAttributeProcessor()
        sources = get_default_content_sources()
        
        # Define negative scoping for Earth-free namespace
        earth_scope = {
            "Earth", "Earth's", "terrestrial", "earthly",
            "America", "American", "USA", "United States",
            "Europe", "European", "Asia", "Asian", "Africa", "African",
            "human", "humanity", "people", "society", "civilization",
            "country", "nation", "world", "global", "international"
        }
        
        results = await processor.process_content_batch(
            sources=sources[:1],  # Test with one source
            negative_scope=earth_scope,
            target_namespace="Zephyrian Consciousness Domain"
        )
        
        print("Batch Processing Results:")
        print("=" * 50)
        print(results["report"])
        print(f"\nGenerated {len(results['attributes'])} attributes")
        
        # Show example attributes
        for i, attr in enumerate(results["attributes"][:3]):
            print(f"\n--- Attribute {i+1} ---")
            print(f"Type: {attr.type.value}")
            print(f"Name: {attr.name}")
            print(f"Description: {attr.description}")
            if attr.proxy_mappings:
                print(f"Proxy Mappings: {attr.proxy_mappings}")
    
    # Run test
    # asyncio.run(test_batch_processing())
    print("Batch attribute processing system ready. Uncomment test to run.")