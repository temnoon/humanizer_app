#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import re

conn = psycopg2.connect('postgresql://tem@localhost/humanizer_archive', cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Get transcripts from Being in Field Framework
cursor.execute("""
    SELECT body_text 
    FROM archived_content
    WHERE parent_id = 225015
        AND source_metadata->>'gizmo_id' = 'g-T7bW2qVzx'
        AND content_type = 'message'
        AND body_text IS NOT NULL
    ORDER BY timestamp 
    LIMIT 2
""")

results = cursor.fetchall()
print(f"Found {len(results)} transcripts in conversation 225015 (Being in Field Framework)")
for i, row in enumerate(results, 1):
    print(f"\n--- Transcript {i} ---")
    content = row['body_text']
    if '```markdown' in content:
        matches = re.findall(r'```markdown\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if matches:
            markdown_content = matches[0].strip()
            print(f"📝 Handwritten content ({len(markdown_content)} chars):")
            preview = markdown_content[:400] + "..." if len(markdown_content) > 400 else markdown_content
            print(preview)
        else:
            print("📄 Raw content:")
            preview = content[:300] + "..." if len(content) > 300 else content
            print(preview)
    else:
        print("📄 Non-markdown content:")
        preview = content[:300] + "..." if len(content) > 300 else content  
        print(preview)