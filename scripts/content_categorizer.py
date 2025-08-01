#!/usr/bin/env python3
"""
Content Categorizer
Assigns 1-2 word categories to conversations and messages using local LLM
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL support not available. Install with: pip install psycopg2-binary")
    sys.exit(1)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ Requests not available. Install with: pip install requests")
    sys.exit(1)

@dataclass
class CategoryResult:
    """Result of categorization"""
    content_id: int
    content_type: str  # 'conversation' or 'message'
    category: str
    confidence: float
    raw_response: str
    processing_time: float

class ContentCategorizer:
    """Categorizes conversations and messages using local LLM"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive",
                 ollama_host: str = "http://localhost:11434"):
        self.database_url = database_url
        self.ollama_host = ollama_host
        self.model_name = "llama3.2"  # Default local model
        
        # Predefined categories to guide the model
        self.valid_categories = {
            # Technical
            'technical', 'programming', 'database', 'api', 'security', 'debugging',
            'software', 'hardware', 'networking', 'development', 'coding', 'system',
            
            # Philosophical
            'philosophical', 'consciousness', 'phenomenology', 'metaphysics', 'ontology',
            'epistemology', 'ethics', 'logic', 'existential', 'spiritual', 'buddhist',
            
            # Scientific
            'quantum', 'physics', 'mathematics', 'biology', 'chemistry', 'cosmology',
            'scientific', 'theory', 'research', 'analysis', 'empirical', 'theoretical',
            
            # Academic
            'academic', 'educational', 'scholarly', 'research', 'study', 'learning',
            'teaching', 'literature', 'history', 'linguistic', 'cultural',
            
            # Creative
            'creative', 'artistic', 'design', 'narrative', 'story', 'writing',
            'music', 'visual', 'poetry', 'fiction', 'aesthetic',
            
            # Personal
            'personal', 'diary', 'reflection', 'memoir', 'emotional', 'relationship',
            'health', 'lifestyle', 'travel', 'family', 'social',
            
            # Business
            'business', 'financial', 'economic', 'corporate', 'management',
            'marketing', 'sales', 'legal', 'commercial', 'professional',
            
            # Practical
            'practical', 'howto', 'tutorial', 'guide', 'instruction', 'advice',
            'tips', 'reference', 'documentation', 'manual', 'procedure',
            
            # Communication
            'discussion', 'debate', 'argument', 'conversation', 'dialogue',
            'question', 'answer', 'explanation', 'clarification', 'inquiry',
            
            # Media
            'media', 'news', 'journalism', 'politics', 'current', 'events',
            'social', 'commentary', 'opinion', 'review', 'critique'
        }
        
        # Category pairs that work well together
        self.category_pairs = {
            'quantum physics', 'agent theory', 'heart sutra', 'machine learning',
            'data science', 'web development', 'software engineering', 'system design',
            'consciousness studies', 'phenomenology research', 'buddhist philosophy',
            'artificial intelligence', 'computer science', 'cognitive science',
            'business analysis', 'financial planning', 'creative writing',
            'technical documentation', 'user interface', 'database design'
        }
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def ensure_category_columns_exist(self):
        """Add categorization columns if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check conversation assessments table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_quality_assessments'
                AND column_name IN ('category', 'category_confidence')
            """)
            
            existing_conv_columns = {row['column_name'] for row in cursor.fetchall()}
            
            if 'category' not in existing_conv_columns:
                cursor.execute("ALTER TABLE conversation_quality_assessments ADD COLUMN category TEXT")
                print("✅ Added category column to conversation_quality_assessments")
            
            if 'category_confidence' not in existing_conv_columns:
                cursor.execute("ALTER TABLE conversation_quality_assessments ADD COLUMN category_confidence REAL")
                print("✅ Added category_confidence column to conversation_quality_assessments")
            
            # Check archived_content table for messages
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'archived_content'
                AND column_name IN ('category', 'category_confidence')
            """)
            
            existing_msg_columns = {row['column_name'] for row in cursor.fetchall()}
            
            if 'category' not in existing_msg_columns:
                cursor.execute("ALTER TABLE archived_content ADD COLUMN category TEXT")
                print("✅ Added category column to archived_content")
            
            if 'category_confidence' not in existing_msg_columns:
                cursor.execute("ALTER TABLE archived_content ADD COLUMN category_confidence REAL")
                print("✅ Added category_confidence column to archived_content")
            
            conn.commit()
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is available and model is ready"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                # Check if our preferred model is available
                available_models = [name for name in model_names if self.model_name in name]
                if available_models:
                    self.model_name = available_models[0]  # Use the first match
                    print(f"✅ Using Ollama model: {self.model_name}")
                    return True
                else:
                    print(f"⚠️  Model {self.model_name} not found. Available models: {model_names}")
                    if model_names:
                        self.model_name = model_names[0]
                        print(f"✅ Using available model: {self.model_name}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return False
    
    def categorize_with_llm(self, text: str, content_type: str = "content") -> Tuple[str, float]:
        """Categorize text using local LLM"""
        
        # Prepare a focused prompt
        prompt = f"""TASK: Give me exactly 1-2 words to categorize this text.

VALID OPTIONS: technical, philosophical, quantum, scientific, creative, personal, business, practical, discussion, media

TEXT: {text[:800]}

CATEGORY:"""
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistency
                        "top_p": 0.9,
                        "num_predict": 20  # Allow enough tokens for full response
                    }
                },
                timeout=30
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result.get('response', '').strip()
                
                # Debug: uncomment for troubleshooting
                # print(f"        Raw LLM response: '{raw_response}'")
                
                # Clean and validate the response
                category = self.clean_category_response(raw_response)
                confidence = self.calculate_confidence(category, text)
                
                return category, confidence
            else:
                print(f"❌ LLM request failed: {response.status_code}")
                return "unknown", 0.0
                
        except Exception as e:
            print(f"❌ LLM categorization error: {e}")
            return "unknown", 0.0
    
    def clean_category_response(self, raw_response: str) -> str:
        """Clean and validate LLM response to extract category"""
        
        # Remove common LLM prefacing
        response = raw_response.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            'the category is', 'category:', 'answer:', 'response:',
            'i would categorize this as', 'this appears to be',
            'this is', 'this content is', 'based on the content',
            'this falls under', 'i classify this as',
            'i would categorize the text as', 'the text as'
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Remove punctuation and extra words
        response = re.sub(r'[^\w\s]', '', response)
        response = response.strip()
        
        # Split into words and take first 1-2 meaningful words
        words = response.split()
        meaningful_words = []
        
        skip_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'this', 'that', 'these', 'those', 'it', 'its', 'of', 'for', 'in', 'on'}
        
        for word in words[:4]:  # Check first 4 words max
            if word not in skip_words and len(word) > 2:
                meaningful_words.append(word)
                if len(meaningful_words) >= 2:
                    break
        
        if not meaningful_words:
            return "unknown"
        
        # Join words and check against valid categories
        if len(meaningful_words) == 1:
            category = meaningful_words[0]
        else:
            # Try two-word combination first
            two_word = ' '.join(meaningful_words[:2])
            if two_word in self.category_pairs:
                category = two_word
            else:
                category = meaningful_words[0]  # Fall back to first word
        
        # Validate against known categories
        if category in self.valid_categories or any(cat in category for cat in self.valid_categories):
            return category
        
        # If not in valid list, try to map to closest valid category
        for valid_cat in self.valid_categories:
            if valid_cat in category or category in valid_cat:
                return valid_cat
        
        return "unknown"
    
    def calculate_confidence(self, category: str, text: str) -> float:
        """Calculate confidence score for categorization"""
        
        if category == "unknown":
            return 0.0
        
        # Base confidence
        confidence = 0.7
        
        # Increase confidence if category words appear in text
        text_lower = text.lower()
        category_words = category.split()
        
        for word in category_words:
            if word in text_lower:
                confidence += 0.2
                break
        
        # Increase confidence for technical terms
        technical_indicators = ['api', 'database', 'code', 'function', 'error', 'server']
        if category == 'technical' and any(term in text_lower for term in technical_indicators):
            confidence += 0.1
        
        # Increase confidence for philosophical terms
        philosophical_indicators = ['consciousness', 'experience', 'reality', 'existence', 'phenomenology']
        if category == 'philosophical' and any(term in text_lower for term in philosophical_indicators):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def categorize_conversation(self, conversation_id: int) -> Optional[CategoryResult]:
        """Categorize a single conversation"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get conversation text
            cursor.execute("""
                SELECT STRING_AGG(body_text, ' ' ORDER BY timestamp) as full_text
                FROM archived_content 
                WHERE parent_id = %s 
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                    AND word_count > 10
            """, (conversation_id,))
            
            result = cursor.fetchone()
            if not result or not result['full_text']:
                return None
            
            # Limit text length for efficiency
            text = result['full_text'][:2000]  # First 2000 chars
            
            start_time = time.time()
            category, confidence = self.categorize_with_llm(text, "conversation")
            processing_time = time.time() - start_time
            
            return CategoryResult(
                content_id=conversation_id,
                content_type='conversation',
                category=category,
                confidence=confidence,
                raw_response=f"Processed {len(text)} chars",
                processing_time=processing_time
            )
    
    def categorize_message(self, message_id: int) -> Optional[CategoryResult]:
        """Categorize a single message"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get message text
            cursor.execute("""
                SELECT body_text, word_count
                FROM archived_content 
                WHERE id = %s 
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
            """, (message_id,))
            
            result = cursor.fetchone()
            if not result or not result['body_text']:
                return None
            
            # Skip very short messages
            if result['word_count'] < 10:
                return CategoryResult(
                    content_id=message_id,
                    content_type='message',
                    category='short',
                    confidence=1.0,
                    raw_response="Too short to categorize",
                    processing_time=0.0
                )
            
            text = result['body_text'][:1000]  # First 1000 chars
            
            start_time = time.time()
            category, confidence = self.categorize_with_llm(text, "message")
            processing_time = time.time() - start_time
            
            return CategoryResult(
                content_id=message_id,
                content_type='message',
                category=category,
                confidence=confidence,
                raw_response=f"Processed {len(text)} chars",
                processing_time=processing_time
            )
    
    def store_categorization(self, result: CategoryResult) -> bool:
        """Store categorization result in database"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if result.content_type == 'conversation':
                    cursor.execute("""
                        UPDATE conversation_quality_assessments 
                        SET category = %s, category_confidence = %s
                        WHERE conversation_id = %s
                    """, (result.category, result.confidence, result.content_id))
                    
                else:  # message
                    cursor.execute("""
                        UPDATE archived_content 
                        SET category = %s, category_confidence = %s
                        WHERE id = %s
                    """, (result.category, result.confidence, result.content_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"❌ Error storing categorization: {e}")
            return False
    
    def run_conversation_categorization(self, limit: int = 100, min_score: float = 0.0) -> List[CategoryResult]:
        """Categorize conversations"""
        
        print(f"🔍 Categorizing conversations (limit: {limit}, min_score: {min_score})")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get conversations to categorize
            cursor.execute("""
                SELECT conversation_id, composite_score
                FROM conversation_quality_assessments
                WHERE is_duplicate = FALSE
                    AND composite_score >= %s
                    AND (category IS NULL OR category = '')
                ORDER BY composite_score DESC
                LIMIT %s
            """, (min_score, limit))
            
            conversations = cursor.fetchall()
        
        if not conversations:
            print("❌ No conversations found needing categorization")
            return []
        
        print(f"📊 Processing {len(conversations)} conversations...")
        results = []
        
        for i, conv in enumerate(conversations, 1):
            conv_id = conv['conversation_id']
            
            print(f"   {i:3d}/{len(conversations)}: Categorizing conversation {conv_id}")
            
            try:
                result = self.categorize_conversation(conv_id)
                if result:
                    if self.store_categorization(result):
                        results.append(result)
                        print(f"      ✅ {result.category} (confidence: {result.confidence:.2f})")
                    else:
                        print(f"      ⚠️  Categorized but storage failed")
                else:
                    print(f"      ❌ Categorization failed")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        return results
    
    def run_message_categorization(self, conversation_limit: int = 10, messages_per_conv: int = 10) -> List[CategoryResult]:
        """Categorize messages from top conversations"""
        
        print(f"🔍 Categorizing messages from top {conversation_limit} conversations")
        print(f"   Up to {messages_per_conv} messages per conversation")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get top conversations
            cursor.execute("""
                SELECT conversation_id
                FROM conversation_quality_assessments
                WHERE is_duplicate = FALSE
                ORDER BY composite_score DESC
                LIMIT %s
            """, (conversation_limit,))
            
            conversations = cursor.fetchall()
        
        if not conversations:
            print("❌ No conversations found")
            return []
        
        results = []
        total_messages = 0
        
        for i, conv in enumerate(conversations, 1):
            conv_id = conv['conversation_id']
            
            print(f"   Conv {i:2d}/{len(conversations)}: Processing conversation {conv_id}")
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get messages needing categorization
                cursor.execute("""
                    SELECT id, word_count
                    FROM archived_content
                    WHERE parent_id = %s
                        AND content_type = 'message'
                        AND body_text IS NOT NULL
                        AND word_count >= 10
                        AND (category IS NULL OR category = '')
                    ORDER BY timestamp
                    LIMIT %s
                """, (conv_id, messages_per_conv))
                
                messages = cursor.fetchall()
            
            if not messages:
                print(f"      ⚠️  No messages need categorization")
                continue
            
            print(f"      📝 Processing {len(messages)} messages")
            
            for j, msg in enumerate(messages, 1):
                msg_id = msg['id']
                
                try:
                    result = self.categorize_message(msg_id)
                    if result:
                        if self.store_categorization(result):
                            results.append(result)
                            print(f"         {j:2d}/{len(messages)}: Msg {msg_id} → {result.category}")
                            total_messages += 1
                        else:
                            print(f"         {j:2d}/{len(messages)}: Msg {msg_id} → Storage failed")
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"         {j:2d}/{len(messages)}: Msg {msg_id} → Error: {e}")
                    continue
        
        print(f"✅ Categorized {total_messages} messages from {len(conversations)} conversations")
        return results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Content Categorizer - Assign 1-2 word categories using local LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Categorize top 50 conversations
  python content_categorizer.py conversations --limit 50

  # Categorize messages from top 10 conversations  
  python content_categorizer.py messages --conv-limit 10 --msg-limit 20

  # Test LLM connection
  python content_categorizer.py test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Conversation categorization
    conv_parser = subparsers.add_parser('conversations', help='Categorize conversations')
    conv_parser.add_argument('--limit', type=int, default=100, help='Max conversations to process')
    conv_parser.add_argument('--min-score', type=float, default=0.0, help='Minimum quality score')
    
    # Message categorization
    msg_parser = subparsers.add_parser('messages', help='Categorize messages')
    msg_parser.add_argument('--conv-limit', type=int, default=10, help='Max conversations to process')
    msg_parser.add_argument('--msg-limit', type=int, default=10, help='Max messages per conversation')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test LLM connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    categorizer = ContentCategorizer()
    
    if args.command == 'test':
        print("🧪 Testing Ollama connection...")
        if categorizer.test_ollama_connection():
            print("✅ Ollama is ready for categorization")
            
            # Test sample categorization
            test_text = "This is a discussion about quantum mechanics and consciousness in phenomenology"
            category, confidence = categorizer.categorize_with_llm(test_text, "test")
            print(f"📝 Test categorization: '{category}' (confidence: {confidence:.2f})")
        else:
            print("❌ Ollama connection failed. Make sure Ollama is running with a model loaded.")
        return
    
    # Ensure database columns exist
    categorizer.ensure_category_columns_exist()
    
    # Test LLM connection
    if not categorizer.test_ollama_connection():
        print("❌ Cannot proceed without working LLM connection")
        return
    
    if args.command == 'conversations':
        results = categorizer.run_conversation_categorization(args.limit, args.min_score)
        
        print(f"\n{'='*80}")
        print(f"🎉 CONVERSATION CATEGORIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Conversations categorized: {len(results)}")
        
        # Show category distribution
        categories = {}
        for result in results:
            categories[result.category] = categories.get(result.category, 0) + 1
        
        print(f"📈 Category distribution:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")
    
    elif args.command == 'messages':
        results = categorizer.run_message_categorization(args.conv_limit, args.msg_limit)
        
        print(f"\n{'='*80}")
        print(f"🎉 MESSAGE CATEGORIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Messages categorized: {len(results)}")
        
        # Show category distribution
        categories = {}
        for result in results:
            categories[result.category] = categories.get(result.category, 0) + 1
        
        print(f"📈 Category distribution:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")


if __name__ == "__main__":
    main()