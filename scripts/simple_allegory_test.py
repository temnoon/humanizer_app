#!/usr/bin/env python3
"""
Simple test of the allegory system without heavy dependencies
"""

import sys
sys.path.append('/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse')

from gutenberg_canonicalizer import GutenbergDownloader, GutenbergCanonicalizer
import json

def main():
    print("🚀 Testing Allegory CLI Components")
    
    # Test download and canonicalization
    book_id = "1342"
    print(f"\n📖 Testing book {book_id} (Pride and Prejudice)")
    
    downloader = GutenbergDownloader()
    canonicalizer = GutenbergCanonicalizer()
    
    # Download
    print("  📥 Downloading...")
    raw_text = downloader.download_text(book_id)
    if not raw_text:
        print("  ❌ Download failed")
        return
    
    print(f"  ✅ Downloaded {len(raw_text):,} characters")
    
    # Canonicalize  
    print("  🧹 Canonicalizing...")
    canonical_text, canon_record = canonicalizer.canonicalize_text(raw_text, book_id)
    print(f"  ✅ Canonicalized to {len(canonical_text):,} characters")
    print(f"  📋 Transformations: {canon_record.transformations_applied}")
    
    # Segment paragraphs
    print("  ✂️  Segmenting...")
    paragraphs = canonicalizer.segment_paragraphs(canonical_text)
    valid_paras = [p for p in paragraphs if p['word_count'] >= 10]
    print(f"  ✅ Found {len(paragraphs)} paragraphs, {len(valid_paras)} valid")
    
    # Create anchors for first 5 paragraphs
    print("  ⚓ Creating anchors...")
    anchored_paras = []
    for i, para in enumerate(valid_paras[:5]):
        anchor = canonicalizer.create_anchor(para, canonical_text)
        anchored_paras.append({
            'paragraph': para,
            'anchor': {
                'canonical_offsets': anchor.canonical_offsets,
                'text_quote': anchor.text_quote,
                'content_hash': anchor.content_hash,
                'rolling_hash': anchor.rolling_hash
            }
        })
        print(f"    {i+1}. {para['word_count']} words - Hash: {anchor.content_hash[:8]}...")
    
    # Save test result
    result = {
        'book_id': book_id,
        'canonical_text_length': len(canonical_text),
        'total_paragraphs': len(paragraphs),
        'valid_paragraphs': len(valid_paras),
        'canonicalization_record': {
            'original_hash': canon_record.original_hash,
            'canonical_hash': canon_record.canonical_hash,
            'transformations_applied': canon_record.transformations_applied,
            'pg_header_removed': canon_record.pg_header_removed,
            'pg_footer_removed': canon_record.pg_footer_removed
        },
        'sample_anchored_paragraphs': anchored_paras
    }
    
    with open('/Users/tem/humanizer-lighthouse/scripts/test_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n🎯 TEST COMPLETE")
    print(f"✅ Successfully processed {book_id}")
    print(f"📁 Result saved to test_result.json")
    print(f"📝 Sample paragraph: {valid_paras[0]['text'][:100]}...")

if __name__ == "__main__":
    main()