#!/usr/bin/env python3
"""
Enhanced Autonomous DNA Discoverer
Replaces the broken discovery system with robust POVM-based curation
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add lighthouse path for imports
lighthouse_path = '/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse'
sys.path.insert(0, lighthouse_path)

from gutenberg_canonicalizer import GutenbergDownloader, GutenbergCanonicalizer
from narrative_feature_extractor import NarrativeFeatureExtractor
from povm_paragraph_selector import POVMParagraphSelector


class EnhancedAutonomousDiscoverer:
    """Enhanced autonomous discovery with robust book processing"""
    
    def __init__(self, output_dir: str = "./discovered_attributes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.downloader = GutenbergDownloader()
        self.canonicalizer = GutenbergCanonicalizer()
        
        # Initialize with lightweight feature extraction (no spaCy initially)
        try:
            self.feature_extractor = NarrativeFeatureExtractor()
            self.has_nlp = self.feature_extractor.nlp is not None
        except:
            self.feature_extractor = None
            self.has_nlp = False
            
        self.paragraph_selector = POVMParagraphSelector(max_paragraphs=100)
        
        # Curated list of high-quality literature
        self.quality_book_ids = [
            # Classic Literature
            "1342",  # Pride and Prejudice
            "11",    # Alice's Adventures in Wonderland
            "84",    # Frankenstein
            "74",    # The Adventures of Tom Sawyer
            "76",    # Adventures of Huckleberry Finn
            "345",   # Dracula
            "1513",  # Romeo and Juliet
            "2701",  # Moby Dick
            "1260",  # Jane Eyre
            "105",   # Persuasion
            "35",    # The Time Machine
            "215",   # The Call of the Wild
            
            # Additional classics
            "174",   # The Picture of Dorian Gray
            "145",   # Middlemarch
            "766",   # David Copperfield
            "1661",  # The Adventures of Sherlock Holmes
            "4300",  # Ulysses
            "2554",  # Crime and Punishment
            "2600",  # War and Peace
            "5200",  # Metamorphosis
        ]
        
        self.processed_books = set()
        self.session_stats = {
            'start_time': datetime.now(),
            'books_processed': 0,
            'books_failed': 0,
            'total_paragraphs': 0,
            'processing_errors': []
        }
    
    def run_discovery_session(self, 
                            max_books: int = 10,
                            max_paras_per_book: int = 50,
                            continuous: bool = False):
        """Run a discovery session"""
        
        print(f"🚀 Enhanced Autonomous Discovery Session")
        print(f"📚 Target: {max_books} books, {max_paras_per_book} paragraphs each")
        print(f"📁 Output: {self.output_dir}")
        print(f"🔄 Continuous mode: {continuous}")
        print(f"🧬 NLP available: {self.has_nlp}")
        
        books_to_process = [bid for bid in self.quality_book_ids if bid not in self.processed_books]
        
        if not books_to_process:
            print("📋 All curated books already processed!")
            return
        
        books_to_process = books_to_process[:max_books]
        
        for i, book_id in enumerate(books_to_process, 1):
            print(f"\n📖 [{i}/{len(books_to_process)}] Processing Book {book_id}")
            
            try:
                success = self._process_book(book_id, max_paras_per_book)
                if success:
                    self.session_stats['books_processed'] += 1
                    self.processed_books.add(book_id)
                    print(f"✅ Book {book_id} completed successfully")
                else:
                    self.session_stats['books_failed'] += 1
                    print(f"❌ Book {book_id} failed processing")
                    
            except Exception as e:
                error_msg = f"Book {book_id}: {str(e)}"
                self.session_stats['processing_errors'].append(error_msg)
                self.session_stats['books_failed'] += 1
                print(f"❌ Book {book_id} error: {e}")
            
            # Progress update
            if i % 3 == 0:
                self._print_progress()
            
            # Rate limiting
            time.sleep(2)
        
        self._save_session_summary()
        self._print_final_summary()
    
    def _process_book(self, book_id: str, max_paragraphs: int) -> bool:
        """Process a single book with full pipeline"""
        
        # Step 1: Download
        print(f"  📥 Downloading...")
        raw_text = self.downloader.download_text(book_id)
        if not raw_text:
            return False
        
        # Step 2: Canonicalize
        print(f"  🧹 Canonicalizing...")
        canonical_text, canon_record = self.canonicalizer.canonicalize_text(raw_text, book_id)
        
        # Step 3: Segment paragraphs
        print(f"  ✂️  Segmenting...")
        paragraphs = self.canonicalizer.segment_paragraphs(canonical_text)
        valid_paras = [p for p in paragraphs if p['word_count'] >= 15]  # Slightly higher threshold
        
        if len(valid_paras) < 20:
            print(f"  ⚠️  Too few valid paragraphs: {len(valid_paras)}")
            return False
        
        # Step 4: Create anchors
        print(f"  ⚓ Anchoring {len(valid_paras)} paragraphs...")
        anchored_paras = []
        for para in valid_paras:
            anchor = self.canonicalizer.create_anchor(para, canonical_text)
            anchored_paras.append({
                'paragraph': para,
                'anchor': {
                    'canonical_offsets': anchor.canonical_offsets,
                    'text_quote': anchor.text_quote,
                    'content_hash': anchor.content_hash,
                    'rolling_hash': anchor.rolling_hash
                }
            })
        
        # Step 5: Feature extraction (if available)
        print(f"  🧬 Extracting features...")
        if self.feature_extractor and self.has_nlp:
            try:
                for para_data in anchored_paras:
                    features = self.feature_extractor.extract_features(para_data['paragraph']['text'])
                    para_data['features'] = {
                        'prosody': features.prosody,
                        'syntax': features.syntax,
                        'discourse': features.discourse,
                        'persona_signature': features.persona_signature,
                        'namespace_signature': features.namespace_signature,
                        'style_rhythm': features.style_rhythm
                    }
            except Exception as e:
                print(f"  ⚠️  Feature extraction failed: {e}")
                # Continue without features
        
        # Step 6: Selection (simplified if no features)
        print(f"  🎯 Selecting optimal paragraphs...")
        selection_budget = min(max_paragraphs, len(anchored_paras))
        
        if self.has_nlp and all('features' in p for p in anchored_paras):
            # Use POVM selector
            book_data = {'book_id': book_id, 'paragraphs': anchored_paras}
            try:
                selected_paras, scores = self.paragraph_selector.select_optimal_paragraphs(
                    book_data, selection_budget
                )
            except Exception as e:
                print(f"  ⚠️  POVM selection failed: {e}, using simple selection")
                selected_paras = self._simple_selection(anchored_paras, selection_budget)
                scores = []
        else:
            # Simple diversity-based selection
            selected_paras = self._simple_selection(anchored_paras, selection_budget)
            scores = []
        
        # Step 7: Save results
        print(f"  💾 Saving {len(selected_paras)} selected paragraphs...")
        result = {
            'book_id': book_id,
            'processing_timestamp': datetime.now().isoformat(),
            'canonicalization_record': {
                'original_hash': canon_record.original_hash,
                'canonical_hash': canon_record.canonical_hash,
                'transformations_applied': canon_record.transformations_applied,
                'pg_header_removed': canon_record.pg_header_removed,
                'pg_footer_removed': canon_record.pg_footer_removed
            },
            'selection_metadata': {
                'total_candidates': len(anchored_paras),
                'selection_budget': selection_budget,
                'selected_count': len(selected_paras),
                'selection_method': 'povm' if scores else 'simple_diversity',
                'has_features': self.has_nlp
            },
            'selected_paragraphs': selected_paras,
            'paragraph_scores': [
                {
                    'total_score': s.total_score,
                    'resonance': s.resonance_score,
                    'info_gain': s.info_gain_score,
                    'redundancy_penalty': s.redundancy_penalty,
                    'clarity': s.clarity_score,
                    'essence_strength': s.essence_strength
                } for s in scores
            ] if scores else []
        }
        
        # Save individual book file
        output_file = self.output_dir / f"discovered_book_{book_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Save attributes in legacy format for compatibility
        self._save_legacy_attributes(book_id, selected_paras)
        
        self.session_stats['total_paragraphs'] += len(selected_paras)
        return True
    
    def _simple_selection(self, anchored_paras: list, budget: int) -> list:
        """Simple diversity-based paragraph selection"""
        
        # Score paragraphs by diversity factors
        scored_paras = []
        for i, para_data in enumerate(anchored_paras):
            text = para_data['paragraph']['text']
            word_count = para_data['paragraph']['word_count']
            
            # Simple scoring
            length_score = min(word_count / 100.0, 1.0)  # Prefer moderate length
            variety_score = len(set(text.lower().split())) / len(text.split()) if text.split() else 0
            position_score = 1.0 - (i / len(anchored_paras))  # Slight preference for earlier paragraphs
            
            total_score = length_score + variety_score + 0.3 * position_score
            scored_paras.append((total_score, para_data))
        
        # Sort and select top budget
        scored_paras.sort(reverse=True, key=lambda x: x[0])
        return [para_data for _, para_data in scored_paras[:budget]]
    
    def _save_legacy_attributes(self, book_id: str, selected_paras: list):
        """Save in legacy attributes format for compatibility"""
        
        legacy_attributes = {
            'book_id': book_id,
            'extraction_timestamp': datetime.now().isoformat(),
            'total_paragraphs': len(selected_paras),
            'attributes': []
        }
        
        for i, para_data in enumerate(selected_paras):
            # Create mock DNA attribute
            attribute = {
                'id': f"{book_id}_{i}",
                'source_book': book_id,
                'paragraph_index': para_data['paragraph']['index'],
                'text_sample': para_data['paragraph']['text'][:200] + "..." if len(para_data['paragraph']['text']) > 200 else para_data['paragraph']['text'],
                'word_count': para_data['paragraph']['word_count'],
                'anchor': para_data['anchor'],
                'narrative_dna': {
                    'persona': 'literary_narrator',
                    'namespace': 'classical_literature', 
                    'style': 'prose_narrative',
                    'confidence': 0.8
                },
                'features': para_data.get('features', {})
            }
            legacy_attributes['attributes'].append(attribute)
        
        # Save legacy format
        legacy_file = self.output_dir / f"attributes_{book_id}.json"
        with open(legacy_file, 'w', encoding='utf-8') as f:
            json.dump(legacy_attributes, f, indent=2, ensure_ascii=False)
    
    def _print_progress(self):
        """Print current session progress"""
        elapsed = datetime.now() - self.session_stats['start_time']
        print(f"\n📊 Progress Update:")
        print(f"  ⏱️  Elapsed: {elapsed}")
        print(f"  ✅ Processed: {self.session_stats['books_processed']}")
        print(f"  ❌ Failed: {self.session_stats['books_failed']}")
        print(f"  📝 Paragraphs: {self.session_stats['total_paragraphs']}")
    
    def _save_session_summary(self):
        """Save session summary"""
        summary = {
            'session_id': int(self.session_stats['start_time'].timestamp()),
            'start_time': self.session_stats['start_time'].isoformat(),
            'end_time': datetime.now().isoformat(),
            'books_processed': self.session_stats['books_processed'],
            'books_failed': self.session_stats['books_failed'],
            'total_paragraphs': self.session_stats['total_paragraphs'],
            'processing_errors': self.session_stats['processing_errors'],
            'processed_book_ids': list(self.processed_books),
            'output_directory': str(self.output_dir)
        }
        
        summary_file = self.output_dir / f"session_summary_{int(self.session_stats['start_time'].timestamp())}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _print_final_summary(self):
        """Print final session summary"""
        elapsed = datetime.now() - self.session_stats['start_time']
        
        print(f"\n🎯 SESSION COMPLETE")
        print(f"⏱️  Total time: {elapsed}")
        print(f"✅ Books processed: {self.session_stats['books_processed']}")
        print(f"❌ Books failed: {self.session_stats['books_failed']}")
        print(f"📝 Total paragraphs: {self.session_stats['total_paragraphs']}")
        print(f"📁 Output saved to: {self.output_dir}")
        
        if self.session_stats['processing_errors']:
            print(f"⚠️  Errors encountered:")
            for error in self.session_stats['processing_errors']:
                print(f"  - {error}")


def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(description='Enhanced Autonomous DNA Discoverer')
    parser.add_argument('--max-books', type=int, default=10, help='Maximum books to process')
    parser.add_argument('--max-paras', type=int, default=50, help='Maximum paragraphs per book')
    parser.add_argument('--output-dir', default='./discovered_attributes', help='Output directory')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    
    args = parser.parse_args()
    
    discoverer = EnhancedAutonomousDiscoverer(args.output_dir)
    
    if args.continuous:
        print("🔄 Running in continuous mode (Ctrl+C to stop)")
        try:
            while True:
                discoverer.run_discovery_session(
                    max_books=args.max_books,
                    max_paras_per_book=args.max_paras,
                    continuous=True
                )
                print("\n⏳ Waiting 5 minutes before next session...")
                time.sleep(300)  # 5 minute pause
        except KeyboardInterrupt:
            print("\n🛑 Continuous mode stopped by user")
    else:
        discoverer.run_discovery_session(
            max_books=args.max_books,
            max_paras_per_book=args.max_paras
        )


if __name__ == "__main__":
    main()