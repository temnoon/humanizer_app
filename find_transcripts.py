#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import re

conn = psycopg2.connect('postgresql://tem@localhost/humanizer_archive', cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Find messages with substantial content
cursor.execute("""
    SELECT parent_id, body_text, LENGTH(body_text) as content_length
    FROM archived_content
    WHERE source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
        AND content_type = 'message'
        AND body_text IS NOT NULL
        AND LENGTH(body_text) > 500
    ORDER BY LENGTH(body_text) DESC
    LIMIT 5
""")

results = cursor.fetchall()
print(f"Found {len(results)} substantial messages from Journal Recognizer OCR")

for i, row in enumerate(results, 1):
    print(f"\n=== Message {i} (Conversation {row['parent_id']}, {row['content_length']} chars) ===")
    content = row['body_text']
    
    # Look for various patterns
    if '```' in content:
        print("🔍 Contains code blocks")
        # Try different markdown patterns
        patterns = [
            r'```markdown\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```', 
            r'```markdown(.*?)```'
        ]
        
        found_content = False
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches and matches[0].strip():
                markdown_content = matches[0].strip()
                print(f"📝 Found transcript content ({len(markdown_content)} chars):")
                preview = markdown_content[:400] + "..." if len(markdown_content) > 400 else markdown_content
                print(preview)
                found_content = True
                break
        
        if not found_content:
            print("📄 Code block found but empty/no match")
    
    # Show raw preview
    print("\n📄 Raw content preview:")
    raw_preview = content[:300] + "..." if len(content) > 300 else content
    print(raw_preview)
    print("-" * 60)