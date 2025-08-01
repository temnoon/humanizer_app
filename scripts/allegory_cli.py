#!/usr/bin/env python3
"""
Allegory CLI - Complete Narrative DNA Extraction Pipeline
Implements the formal POVM framework with robust anchoring and provenance
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import hashlib
from datetime import datetime
import numpy as np

from gutenberg_canonicalizer import GutenbergDownloader, GutenbergCanonicalizer
from narrative_feature_extractor import NarrativeFeatureExtractor
from povm_paragraph_selector import POVMParagraphSelector


class AllegoryCLI:
    """Main CLI orchestrator for narrative DNA extraction"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.downloader = GutenbergDownloader()
        self.canonicalizer = GutenbergCanonicalizer()
        self.feature_extractor = NarrativeFeatureExtractor()
        self.paragraph_selector = POVMParagraphSelector()
        
    def curate_books(self, 
                    book_ids: List[str],
                    output_dir: Path,
                    max_paras_per_book: int = 200,
                    formats: List[str] = ['txt'],
                    selectors: List[str] = ['char', 'quote', 'hash']) -> Dict[str, Any]:
        """Complete curation pipeline for multiple books"""
        
        print(f"🚀 Allegory CLI v{self.VERSION} - Starting curation pipeline")
        print(f"📚 Processing {len(book_ids)} books")
        print(f"📁 Output directory: {output_dir}")
        
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize results tracking
        results = {
            'pipeline_version': self.VERSION,
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'max_paras_per_book': max_paras_per_book,
                'formats': formats,
                'selectors': selectors,
                'canonicalizer_version': self.canonicalizer.VERSION,
                'feature_extractor_version': '1.0.0',
                'selector_version': '1.0.0'
            },
            'books_processed': [],
            'books_failed': [],
            'total_paragraphs_selected': 0,
            'provenance_hashes': {}
        }
        
        # Process each book
        for book_id in book_ids:
            print(f"\n📖 Processing Book {book_id}")
            
            try:
                book_result = self._process_single_book(
                    book_id, output_dir, max_paras_per_book, selectors
                )
                
                if 'error' in book_result:
                    results['books_failed'].append({
                        'book_id': book_id,
                        'error': book_result['error']
                    })
                    print(f"❌ Failed: {book_result['error']}")
                else:
                    results['books_processed'].append(book_result)
                    results['total_paragraphs_selected'] += book_result.get('paragraphs_selected', 0)
                    results['provenance_hashes'][book_id] = book_result.get('provenance_hash')
                    print(f"✅ Success: {book_result.get('paragraphs_selected', 0)} paragraphs selected")
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                results['books_failed'].append({
                    'book_id': book_id,
                    'error': error_msg
                })
                print(f"❌ Failed: {error_msg}")
        
        # Save master manifest
        manifest_path = output_dir / "curation_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n🎯 CURATION COMPLETE")
        print(f"✅ Books processed: {len(results['books_processed'])}")
        print(f"❌ Books failed: {len(results['books_failed'])}")
        print(f"📝 Total paragraphs: {results['total_paragraphs_selected']}")
        print(f"📋 Manifest: {manifest_path}")
        
        return results
    
    def _process_single_book(self, 
                           book_id: str, 
                           output_dir: Path,
                           max_paras: int,
                           selectors: List[str]) -> Dict[str, Any]:
        """Process a single book through the complete pipeline"""
        
        # Step 1: Download and canonicalize
        print(f"  📥 Downloading...")
        raw_text = self.downloader.download_text(book_id)
        if not raw_text:
            return {'error': f'Failed to download book {book_id}'}
        
        print(f"  🧹 Canonicalizing...")
        canonical_text, canon_record = self.canonicalizer.canonicalize_text(raw_text, book_id)
        
        # Step 2: Segment paragraphs
        print(f"  ✂️  Segmenting paragraphs...")
        paragraphs = self.canonicalizer.segment_paragraphs(canonical_text)
        
        if len(paragraphs) < 10:
            return {'error': f'Too few paragraphs found ({len(paragraphs)})'}
        
        # Step 3: Create anchors
        print(f"  ⚓ Creating anchors...")
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
        
        # Step 4: Extract features
        print(f"  🧬 Extracting features...")
        for i, para_data in enumerate(anchored_paragraphs):
            features = self.feature_extractor.extract_features(para_data['paragraph']['text'])
            para_data['features'] = {
                'prosody': features.prosody,
                'syntax': features.syntax,
                'discourse': features.discourse,
                'persona_signature': features.persona_signature,
                'namespace_signature': features.namespace_signature,
                'style_rhythm': features.style_rhythm
            }
        
        # Step 5: Select optimal paragraphs
        print(f"  🎯 Selecting optimal paragraphs...")
        book_data = {
            'book_id': book_id,
            'paragraphs': anchored_paragraphs,
            'canonical_text': canonical_text,
            'canonicalization_record': {
                'original_hash': canon_record.original_hash,
                'canonical_hash': canon_record.canonical_hash,
                'canonicalizer_version': canon_record.canonicalizer_version,
                'transformations_applied': canon_record.transformations_applied,
                'pg_header_removed': canon_record.pg_header_removed,
                'pg_footer_removed': canon_record.pg_footer_removed
            }
        }
        
        selection_budget = min(max_paras, len(anchored_paragraphs))
        selected_paragraphs, scores = self.paragraph_selector.select_optimal_paragraphs(
            book_data, selection_budget
        )
        
        # Step 6: Create essence records (simplified for now)
        print(f"  🔮 Capturing essence...")
        for i, para_data in enumerate(selected_paragraphs):
            essence = self._extract_essence(para_data['paragraph']['text'])
            para_data['essence'] = essence
        
        # Step 7: Create final output with provenance
        final_output = {
            'book_id': book_id,
            'processing_timestamp': datetime.now().isoformat(),
            'pipeline_version': self.VERSION,
            'canonicalization_record': book_data['canonicalization_record'],
            'selection_metadata': {
                'total_candidates': len(anchored_paragraphs),
                'selection_budget': selection_budget,
                'selected_count': len(selected_paragraphs),
                'average_score': np.mean([s.total_score for s in scores]),
                'selection_weights': self.paragraph_selector.weights
            },
            'selected_paragraphs': selected_paragraphs,
            'paragraph_scores': [
                {
                    'paragraph_id': score.paragraph_id,
                    'total_score': score.total_score,
                    'component_scores': {
                        'resonance': score.resonance_score,
                        'info_gain': score.info_gain_score,
                        'redundancy_penalty': score.redundancy_penalty,
                        'clarity': score.clarity_score,
                        'essence_strength': score.essence_strength
                    },
                    'detector_responses': score.detector_responses
                }
                for score in scores
            ],
            'provenance': {
                'tool_versions': {
                    'canonicalizer': self.canonicalizer.VERSION,
                    'feature_extractor': '1.0.0',
                    'paragraph_selector': '1.0.0'
                },
                'processing_chain': [
                    'download', 'canonicalize', 'segment', 'anchor', 
                    'extract_features', 'select_paragraphs', 'extract_essence'
                ]
            }
        }
        
        # Calculate provenance hash
        provenance_string = json.dumps(final_output['provenance'], sort_keys=True)
        provenance_hash = hashlib.sha256(provenance_string.encode()).hexdigest()
        final_output['provenance_hash'] = provenance_hash
        
        # Save individual book result
        output_file = output_dir / f"book_{book_id}_curated.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        # Also save anchors in separate JSONL file  
        anchors_file = output_dir / f"book_{book_id}_anchors.jsonl"
        with open(anchors_file, 'w', encoding='utf-8') as f:
            for para_data in selected_paragraphs:
                anchor_record = {
                    'book_id': book_id,
                    'paragraph_id': para_data['paragraph']['index'],
                    'anchor': para_data['anchor'],
                    'features': para_data['features'],
                    'essence': para_data.get('essence', {})
                }
                f.write(json.dumps(anchor_record) + '\n')
        
        return {
            'book_id': book_id,
            'paragraphs_selected': len(selected_paragraphs),
            'output_file': str(output_file),
            'anchors_file': str(anchors_file),
            'provenance_hash': provenance_hash,
            'average_score': np.mean([s.total_score for s in scores])
        }
    
    def _extract_essence(self, paragraph_text: str) -> Dict[str, Any]:
        """Extract essence/invariants from paragraph (simplified)"""
        
        # This is a simplified essence extractor
        # In full implementation, would use proper SRL, coreference, etc.
        
        essence = {
            'word_count': len(paragraph_text.split()),
            'sentence_count': len([s for s in paragraph_text.split('.') if s.strip()]),
            'narrative_markers': [],
            'thematic_elements': [],
            'emotional_valence': 'neutral',
            'causal_structure': [],
            'agent_mentions': [],
            'temporal_markers': [],
            'constraint_preservation': [
                'maintain_narrative_flow',
                'preserve_character_agency', 
                'retain_causal_relationships'
            ]
        }
        
        # Simple narrative marker detection
        narrative_words = ['said', 'went', 'came', 'saw', 'felt', 'thought', 'knew', 'found', 'became']
        text_lower = paragraph_text.lower()
        for word in narrative_words:
            if word in text_lower:
                essence['narrative_markers'].append(word)
        
        # Simple emotional valence detection
        positive_words = ['love', 'joy', 'happy', 'wonderful', 'beautiful', 'good', 'great']
        negative_words = ['hate', 'sad', 'terrible', 'awful', 'bad', 'wrong', 'dark']
        
        pos_count = sum(text_lower.count(word) for word in positive_words)
        neg_count = sum(text_lower.count(word) for word in negative_words)
        
        if pos_count > neg_count:
            essence['emotional_valence'] = 'positive'
        elif neg_count > pos_count:
            essence['emotional_valence'] = 'negative'
        
        return essence


def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description='Allegory CLI - Narrative DNA Curation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  allegory-cli curate --book-ids 1342 11 84 --max-paras 100 --out ./curated
  allegory-cli curate --book-ids 74 76 345 --max-paras 200 --selectors char,quote,hash,epubcfi
        """
    )
    
    parser.add_argument('command', choices=['curate'], help='Command to execute')
    
    # Curation arguments
    parser.add_argument('--book-ids', nargs='+', required=True, 
                       help='Gutenberg book IDs to process')
    parser.add_argument('--out', '--output-dir', default='./curated_attributes',
                       help='Output directory (default: ./curated_attributes)')
    parser.add_argument('--max-paras', type=int, default=200,
                       help='Maximum paragraphs per book (default: 200)')
    parser.add_argument('--formats', nargs='+', default=['txt'],
                       choices=['txt', 'epub'], help='File formats to process')
    parser.add_argument('--selectors', default='char,quote,hash',
                       help='Anchor selectors (comma-separated)')
    
    # Feature extraction parameters
    parser.add_argument('--resonance-weight', type=float, default=1.0,
                       help='Weight for resonance score')
    parser.add_argument('--info-gain-weight', type=float, default=1.0,
                       help='Weight for information gain')
    parser.add_argument('--redundancy-weight', type=float, default=0.5,
                       help='Weight for redundancy penalty')
    parser.add_argument('--clarity-weight', type=float, default=0.3,
                       help='Weight for clarity score')
    parser.add_argument('--essence-weight', type=float, default=0.8,
                       help='Weight for essence strength')
    
    args = parser.parse_args()
    
    if args.command == 'curate':
        # Initialize CLI with custom weights
        cli = AllegoryCLI()
        cli.paragraph_selector.weights.update({
            'resonance': args.resonance_weight,
            'info_gain': args.info_gain_weight,
            'redundancy': args.redundancy_weight,
            'clarity': args.clarity_weight,
            'essence': args.essence_weight
        })
        
        # Parse selectors
        selectors = [s.strip() for s in args.selectors.split(',')]
        
        # Run curation
        output_dir = Path(args.out)
        results = cli.curate_books(
            book_ids=args.book_ids,
            output_dir=output_dir,
            max_paras_per_book=args.max_paras,
            formats=args.formats,
            selectors=selectors
        )
        
        # Exit with appropriate code
        if results['books_failed']:
            print(f"\n⚠️  {len(results['books_failed'])} books failed processing")
            sys.exit(1)
        else:
            print(f"\n🎉 All {len(results['books_processed'])} books processed successfully!")
            sys.exit(0)


if __name__ == "__main__":
    main()