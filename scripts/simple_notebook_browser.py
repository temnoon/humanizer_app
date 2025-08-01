#!/usr/bin/env python3
"""
Simple Notebook Browser - Debug version
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def main():
    try:
        print("📔 Simple Notebook Browser")
        print("=" * 30)
        
        # Connect to database
        conn = psycopg2.connect(
            "postgresql://tem@localhost/humanizer_archive", 
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        
        # Get notebook conversations
        print("Searching for Journal Recognizer OCR conversations...")
        cursor.execute("""
            SELECT 
                parent.id,
                COALESCE(parent.title, 'Untitled') as title,
                COUNT(child.id) as transcript_count
            FROM archived_content parent
            JOIN archived_content child ON parent.id = child.parent_id
            WHERE child.source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
                AND child.content_type = 'message'
                AND child.body_text IS NOT NULL
            GROUP BY parent.id, parent.title
            ORDER BY transcript_count DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        print(f"\n✅ Found {len(results)} conversations with notebook transcripts:")
        
        for row in results:
            print(f"  [{row['id']}] {row['title']}")
            print(f"      📊 {row['transcript_count']} transcripts")
        
        if results:
            # Show example transcript
            first_conv_id = results[0]['id']
            print(f"\n📄 Sample transcript from conversation {first_conv_id}:")
            
            cursor.execute("""
                SELECT body_text 
                FROM archived_content
                WHERE parent_id = %s
                    AND source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                ORDER BY timestamp 
                LIMIT 1
            """, (first_conv_id,))
            
            sample = cursor.fetchone()
            if sample:
                preview = sample['body_text'][:500]
                print(f"{preview}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()