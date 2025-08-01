#!/usr/bin/env python3
"""
Gutenberg Text Canonicalizer
Implements robust paragraph anchoring with multiple fallback methods
"""

import re
import hashlib
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import requests
from pathlib import Path
import json


@dataclass
class TextAnchor:
    """Multi-layered paragraph anchor for robust referencing"""
    canonical_offsets: Dict[str, int]  # start, end in canonical text
    text_quote: Dict[str, str]         # exact, prefix, suffix  
    content_hash: str                  # SHA-256 of exact text
    rolling_hash: str                  # MinHash for fuzzy matching
    epub_cfi: Optional[str] = None     # EPUB CFI if available
    
    
@dataclass
class CanonicalizationRecord:
    """Track transformations for reproducibility"""
    original_hash: str
    canonical_hash: str 
    canonicalizer_version: str
    transformations_applied: List[str]
    pg_header_removed: bool
    pg_footer_removed: bool


class GutenbergCanonicalizer:
    """Canonical text processor with robust anchoring"""
    
    VERSION = "1.0.0"
    
    # Project Gutenberg header/footer patterns
    PG_START_PATTERNS = [
        r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .* \*\*\*",
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .* \*\*\*",
        r"This eBook is for the use of anyone anywhere",
        r"Project Gutenberg eBooks are created"
    ]
    
    PG_END_PATTERNS = [
        r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .* \*\*\*",
        r"End of (?:the )?Project Gutenberg EBook",
        r"This file should be named"
    ]
    
    def __init__(self):
        self.transformations_log = []
        
    def canonicalize_text(self, raw_text: str, book_id: str) -> Tuple[str, CanonicalizationRecord]:
        """Convert raw Gutenberg text to canonical form"""
        
        original_hash = hashlib.sha256(raw_text.encode()).hexdigest()
        self.transformations_log = []
        
        # Step 1: Strip Project Gutenberg headers/footers
        text, header_removed, footer_removed = self._strip_pg_wrapper(raw_text)
        
        # Step 2: Normalize Unicode (NFKC)
        text = unicodedata.normalize('NFKC', text)
        self.transformations_log.append("unicode_nfkc_normalization")
        
        # Step 3: Standardize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.transformations_log.append("line_ending_standardization")
        
        # Step 4: Collapse excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r'[ \t]+', ' ', text)     # Collapse spaces/tabs
        self.transformations_log.append("whitespace_normalization")
        
        # Step 5: Remove trailing whitespace from lines
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        self.transformations_log.append("trailing_whitespace_removal")
        
        canonical_hash = hashlib.sha256(text.encode()).hexdigest()
        
        record = CanonicalizationRecord(
            original_hash=original_hash,
            canonical_hash=canonical_hash,
            canonicalizer_version=self.VERSION,
            transformations_applied=self.transformations_log.copy(),
            pg_header_removed=header_removed,
            pg_footer_removed=footer_removed
        )
        
        return text, record
    
    def _strip_pg_wrapper(self, text: str) -> Tuple[str, bool, bool]:
        """Remove Project Gutenberg header and footer"""
        header_removed = False
        footer_removed = False
        
        # Find and remove header
        for pattern in self.PG_START_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Keep everything after the header
                text = text[match.end():]
                header_removed = True
                self.transformations_log.append(f"pg_header_removed:{pattern[:20]}")
                break
        
        # Find and remove footer
        for pattern in self.PG_END_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Keep everything before the footer
                text = text[:match.start()]
                footer_removed = True
                self.transformations_log.append(f"pg_footer_removed:{pattern[:20]}")
                break
                
        return text, header_removed, footer_removed
    
    def segment_paragraphs(self, canonical_text: str) -> List[Dict]:
        """Segment text into paragraphs with character positions"""
        paragraphs = []
        
        # Split on double newlines (paragraph breaks)
        parts = canonical_text.split('\n\n')
        
        current_pos = 0
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                current_pos += 2  # Account for the \n\n
                continue
                
            start_pos = canonical_text.find(part, current_pos)
            end_pos = start_pos + len(part)
            
            paragraphs.append({
                'index': i,
                'text': part,
                'start_char': start_pos,
                'end_char': end_pos,
                'word_count': len(part.split()),
                'sentence_count': len(re.findall(r'[.!?]+', part))
            })
            
            current_pos = end_pos + 2  # Move past this paragraph + \n\n
            
        return paragraphs
    
    def create_anchor(self, paragraph: Dict, canonical_text: str, context_chars: int = 100) -> TextAnchor:
        """Create multi-layered anchor for a paragraph"""
        
        text = paragraph['text']
        start_char = paragraph['start_char']
        end_char = paragraph['end_char']
        
        # Extract context for fuzzy matching
        prefix_start = max(0, start_char - context_chars)
        suffix_end = min(len(canonical_text), end_char + context_chars)
        
        prefix = canonical_text[prefix_start:start_char]
        suffix = canonical_text[end_char:suffix_end]
        
        # Create hashes
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Simple rolling hash (MinHash approximation)
        rolling_context = prefix[-50:] + text + suffix[:50]
        rolling_hash = hashlib.md5(rolling_context.encode()).hexdigest()
        
        return TextAnchor(
            canonical_offsets={'start': start_char, 'end': end_char},
            text_quote={'exact': text, 'prefix': prefix[-50:], 'suffix': suffix[:50]},
            content_hash=content_hash,
            rolling_hash=rolling_hash
        )


class GutenbergDownloader:
    """Download and process Gutenberg texts"""
    
    BASE_URL = "https://www.gutenberg.org"
    
    def __init__(self):
        self.canonicalizer = GutenbergCanonicalizer()
        
    def download_text(self, book_id: str) -> Optional[str]:
        """Download text file from Project Gutenberg"""
        
        # Try different URL patterns
        url_patterns = [
            f"{self.BASE_URL}/files/{book_id}/{book_id}-0.txt",
            f"{self.BASE_URL}/files/{book_id}/{book_id}.txt",
            f"{self.BASE_URL}/cache/epub/{book_id}/pg{book_id}.txt"
        ]
        
        for url in url_patterns:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return response.text
            except requests.RequestException:
                continue
                
        return None
    
    def process_book(self, book_id: str, output_dir: Path) -> Dict:
        """Download, canonicalize, and anchor a book"""
        
        print(f"Processing book {book_id}...")
        
        # Download
        raw_text = self.download_text(book_id)
        if not raw_text:
            return {'error': f'Failed to download book {book_id}'}
        
        # Canonicalize
        canonical_text, canon_record = self.canonicalizer.canonicalize_text(raw_text, book_id)
        
        # Segment paragraphs
        paragraphs = self.canonicalizer.segment_paragraphs(canonical_text)
        
        # Create anchors
        anchored_paragraphs = []
        for para in paragraphs:
            if para['word_count'] >= 10:  # Skip very short paragraphs
                anchor = self.canonicalizer.create_anchor(para, canonical_text)
                
                anchored_paragraphs.append({
                    'paragraph': para,
                    'anchor': {
                        'canonical_offsets': anchor.canonical_offsets,
                        'text_quote': anchor.text_quote,
                        'content_hash': anchor.content_hash,
                        'rolling_hash': anchor.rolling_hash,
                        'epub_cfi': anchor.epub_cfi
                    }
                })
        
        # Save results
        book_data = {
            'book_id': book_id,
            'canonical_text': canonical_text,
            'canonicalization_record': {
                'original_hash': canon_record.original_hash,
                'canonical_hash': canon_record.canonical_hash,
                'canonicalizer_version': canon_record.canonicalizer_version,
                'transformations_applied': canon_record.transformations_applied,
                'pg_header_removed': canon_record.pg_header_removed,
                'pg_footer_removed': canon_record.pg_footer_removed
            },
            'paragraphs': anchored_paragraphs,
            'stats': {
                'total_paragraphs': len(anchored_paragraphs),
                'total_words': sum(p['paragraph']['word_count'] for p in anchored_paragraphs),
                'avg_para_length': sum(p['paragraph']['word_count'] for p in anchored_paragraphs) / len(anchored_paragraphs) if anchored_paragraphs else 0
            }
        }
        
        # Save to file
        output_file = output_dir / f"book_{book_id}_anchored.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Book {book_id}: {len(anchored_paragraphs)} paragraphs anchored")
        return book_data


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gutenberg Text Canonicalizer')
    parser.add_argument('--book-ids', nargs='+', required=True, help='Gutenberg book IDs to process')
    parser.add_argument('--output-dir', default='./canonicalized_books', help='Output directory')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    downloader = GutenbergDownloader()
    
    for book_id in args.book_ids:
        try:
            result = downloader.process_book(book_id, output_dir)
            if 'error' in result:
                print(f"❌ {result['error']}")
        except Exception as e:
            print(f"❌ Error processing book {book_id}: {e}")


if __name__ == "__main__":
    main()