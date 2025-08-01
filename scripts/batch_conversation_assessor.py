#!/usr/bin/env python3
"""
Batch Conversation Quality Assessor
Processes entire archive with duplicate detection and hashing
"""

import os
import sys
import json
import re
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
import statistics

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL support not available. Install with: pip install psycopg2-binary")
    sys.exit(1)

@dataclass
class ConversationAssessment:
    """Data structure for conversation quality assessment"""
    conversation_id: int
    title: str
    word_count: int
    message_count: int
    code_density: float
    readability_score: float
    coherence_score: float
    depth_score: float
    completeness_score: float
    composite_score: float
    primary_topic: str
    editorial_potential: str
    justification: str
    participant_count: int
    date_range: str
    content_hash: str
    is_duplicate: bool
    duplicate_of: Optional[int]

class BatchConversationAssessor:
    """Batch processor for entire archive with duplicate detection"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.assessment_version = "v1.1_batch_with_duplicates"
        
        # Quality scoring weights
        self.weights = {
            'depth': 0.25,
            'readability': 0.20,
            'coherence': 0.20,
            'completeness': 0.20,
            'length_bonus': 0.15
        }
        
        # Content analysis patterns
        self.code_patterns = [
            r'```[\s\S]*?```',  # Code blocks
            r'`[^`\n]+`',       # Inline code
            r'^\s*[#$>]\s+',    # Command prompts
            r'Error:|Exception:|Traceback:'  # Error messages
        ]
        
        self.depth_indicators = [
            r'\b(?:because|therefore|however|furthermore|moreover|consequently)\b',
            r'\b(?:analysis|examine|consider|evaluate|assess|determine)\b',
            r'\b(?:principle|theory|concept|framework|methodology)\b',
            r'\?.*\?',  # Questions
            r':\s*$'    # Explanatory colons
        ]
        
        self.topic_keywords = {
            'technical': ['implementation', 'algorithm', 'system', 'architecture', 'database', 'api', 'framework'],
            'philosophical': ['consciousness', 'reality', 'existence', 'meaning', 'truth', 'ethics', 'moral'],
            'creative': ['narrative', 'story', 'character', 'plot', 'creative', 'artistic', 'design'],
            'analytical': ['analysis', 'research', 'methodology', 'evaluation', 'comparison', 'assessment'],
            'educational': ['explain', 'tutorial', 'guide', 'learning', 'teaching', 'example', 'demonstration'],
            'problem_solving': ['problem', 'solution', 'issue', 'challenge', 'debugging', 'troubleshooting']
        }
        
        # Duplicate tracking
        self.content_hashes: Dict[str, int] = {}
        self.duplicate_conversations: Set[int] = set()
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def ensure_duplicate_columns_exist(self):
        """Add duplicate detection columns to assessment table if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if columns exist and add them if not
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_quality_assessments'
                AND column_name IN ('content_hash', 'is_duplicate', 'duplicate_of')
            """)
            
            existing_columns = {row['column_name'] for row in cursor.fetchall()}
            
            if 'content_hash' not in existing_columns:
                cursor.execute("ALTER TABLE conversation_quality_assessments ADD COLUMN content_hash TEXT")
                print("✅ Added content_hash column")
            
            if 'is_duplicate' not in existing_columns:
                cursor.execute("ALTER TABLE conversation_quality_assessments ADD COLUMN is_duplicate BOOLEAN DEFAULT FALSE")
                print("✅ Added is_duplicate column")
            
            if 'duplicate_of' not in existing_columns:
                cursor.execute("ALTER TABLE conversation_quality_assessments ADD COLUMN duplicate_of BIGINT")
                print("✅ Added duplicate_of column")
            
            conn.commit()
    
    def get_all_conversations(self, min_words: int = 100) -> List[Dict]:
        """Get all conversations from archive for processing"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            print(f"🔍 Retrieving all conversations with minimum {min_words} words...")
            
            cursor.execute("""
                SELECT 
                    parent_id as conversation_id,
                    COUNT(*) as message_count,
                    SUM(word_count) as total_words,
                    STRING_AGG(DISTINCT author, ', ') as participants,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    -- Get conversation content for hashing (first 2000 chars of combined messages)
                    LEFT(STRING_AGG(body_text, ' ' ORDER BY timestamp), 2000) as content_sample,
                    -- Full text for analysis (limited to avoid memory issues)
                    STRING_AGG(
                        CASE 
                            WHEN LENGTH(body_text) > 500 THEN LEFT(body_text, 500) || '...'
                            ELSE body_text 
                        END, 
                        ' ' ORDER BY timestamp
                    ) as full_text
                FROM archived_content 
                WHERE content_type = 'message' 
                    AND body_text IS NOT NULL 
                    AND word_count > 10
                    AND parent_id IS NOT NULL
                GROUP BY parent_id
                HAVING SUM(word_count) >= %s 
                    AND COUNT(*) >= 3
                ORDER BY parent_id
            """, (min_words,))
            
            conversations = cursor.fetchall()
            print(f"📊 Found {len(conversations)} conversations to process")
            return conversations
    
    def calculate_content_hash(self, conversation_data: Dict) -> str:
        """Calculate hash of conversation content for duplicate detection"""
        # Convert to float to handle Decimal objects
        message_count = int(conversation_data.get('message_count', 0))
        total_words = int(float(conversation_data.get('total_words', 0)))
        
        # Use content sample and metadata for hashing
        hash_content = f"{message_count}|{total_words}|{conversation_data.get('content_sample', '')}"
        
        # Normalize whitespace and case for better duplicate detection
        normalized_content = re.sub(r'\s+', ' ', hash_content.lower().strip())
        
        return hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
    
    def check_for_duplicate(self, content_hash: str, conversation_id: int) -> Tuple[bool, Optional[int]]:
        """Check if this conversation is a duplicate based on content hash"""
        if content_hash in self.content_hashes:
            original_id = self.content_hashes[content_hash]
            self.duplicate_conversations.add(conversation_id)
            return True, original_id
        else:
            self.content_hashes[content_hash] = conversation_id
            return False, None
    
    def analyze_code_density(self, text: str) -> float:
        """Calculate the density of code content in text"""
        if not text:
            return 0.0
        
        total_chars = len(text)
        code_chars = 0
        
        for pattern in self.code_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            code_chars += sum(len(match) for match in matches)
        
        return min(1.0, code_chars / total_chars) if total_chars > 0 else 0.0
    
    def analyze_readability(self, text: str, code_density: float) -> float:
        """Assess readability based on sentence structure and code density"""
        if not text:
            return 0.0
        
        # Base readability factors
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Calculate average sentence length
        words_per_sentence = [len(s.split()) for s in sentences]
        avg_sentence_length = statistics.mean(words_per_sentence) if words_per_sentence else 0
        
        # Optimal sentence length is around 15-20 words
        length_score = 1.0 - abs(avg_sentence_length - 17.5) / 17.5
        length_score = max(0.0, min(1.0, length_score))
        
        # Penalty for code density
        code_penalty = code_density * 0.7  # Heavy penalty for code
        
        # Bonus for explanation patterns
        explanation_bonus = 0.0
        explanation_patterns = [r'\bfor example\b', r'\bthat is\b', r'\bin other words\b']
        for pattern in explanation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                explanation_bonus += 0.1
        
        readability = (length_score * 0.7) + (explanation_bonus * 0.3) - code_penalty
        return max(0.0, min(1.0, readability))
    
    def analyze_depth(self, text: str) -> float:
        """Assess intellectual depth and rigor"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        depth_score = 0.0
        
        # Count depth indicators
        for pattern in self.depth_indicators:
            matches = len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE))
            depth_score += matches * 0.1
        
        # Look for sustained reasoning (longer paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        substantial_paragraphs = [p for p in paragraphs if len(p.split()) > 50]
        
        if paragraphs:
            substantial_ratio = len(substantial_paragraphs) / len(paragraphs)
            depth_score += substantial_ratio * 0.5
        
        # Bonus for questions and explorations
        question_count = len(re.findall(r'\?', text))
        depth_score += min(0.3, question_count * 0.05)
        
        return min(1.0, depth_score)
    
    def analyze_coherence(self, conversation_data: Dict) -> float:
        """Assess topic coherence using available data"""
        text = conversation_data.get('full_text', '').lower()
        
        if not text:
            return 0.5  # Neutral score
        
        # Count topic keywords
        topic_scores = {}
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                topic_scores[topic] = score
        
        if not topic_scores:
            return 0.5  # Neutral score if no clear topics
        
        # Coherence is higher when one topic dominates
        total_keywords = sum(topic_scores.values())
        max_topic_score = max(topic_scores.values())
        coherence = max_topic_score / total_keywords if total_keywords > 0 else 0.5
        
        return coherence
    
    def analyze_completeness(self, conversation_data: Dict) -> float:
        """Assess conversation completeness using available data"""
        text = conversation_data.get('full_text', '').lower()
        message_count = int(conversation_data.get('message_count', 0))
        
        if not text:
            return 0.0
        
        # Look for completion indicators
        completion_indicators = [
            r'\b(?:conclusion|summary|in summary|to conclude)\b',
            r'\b(?:finally|ultimately|in the end)\b',
            r'\b(?:solution|resolved|answer|result)\b',
            r'\b(?:thank you|thanks|helpful|clear now)\b'
        ]
        
        completeness_score = 0.0
        for pattern in completion_indicators:
            if re.search(pattern, text):
                completeness_score += 0.3
        
        # Bonus for conversations with good message count (not too short, not endless)
        if 5 <= message_count <= 20:
            completeness_score += 0.2
        elif message_count > 20:
            completeness_score += 0.1  # Slight bonus for longer conversations
        
        return max(0.0, min(1.0, completeness_score))
    
    def classify_primary_topic(self, text: str) -> str:
        """Classify the primary topic of the conversation"""
        if not text:
            return 'general'
        
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def assess_editorial_potential(self, assessment: Dict) -> Tuple[str, str]:
        """Determine editorial potential and provide justification"""
        score = assessment['composite_score']
        word_count = assessment['word_count']
        topic = assessment['primary_topic']
        code_density = assessment['code_density']
        is_duplicate = assessment.get('is_duplicate', False)
        
        # Duplicate content has no editorial potential
        if is_duplicate:
            return "duplicate", f"Duplicate of conversation {assessment.get('duplicate_of', 'unknown')}"
        
        # Determine potential type
        if score >= 0.8 and word_count >= 3000:
            if code_density < 0.1:
                potential = "book_chapter"
                justification = f"High-quality {topic} discussion with {word_count} words, minimal code, excellent coherence"
            else:
                potential = "technical_article"
                justification = f"Strong technical content with {word_count} words, good for technical publication"
        elif score >= 0.7 and word_count >= 2000:
            potential = "article"
            justification = f"Solid {topic} content with {word_count} words, good editorial potential"
        elif score >= 0.6:
            potential = "blog_post"
            justification = f"Decent {topic} discussion, suitable for blog or newsletter"
        elif score >= 0.4:
            potential = "reference"
            justification = f"Useful for reference or as supporting material"
        else:
            potential = "low"
            justification = f"Limited editorial value due to {self._get_main_weakness(assessment)}"
        
        return potential, justification
    
    def _get_main_weakness(self, assessment: Dict) -> str:
        """Identify the main weakness in a low-scoring assessment"""
        scores = {
            'readability': assessment['readability_score'],
            'depth': assessment['depth_score'],
            'coherence': assessment['coherence_score'],
            'completeness': assessment['completeness_score']
        }
        
        min_aspect = min(scores.items(), key=lambda x: x[1])
        return min_aspect[0]
    
    def assess_conversation(self, conversation_data: Dict) -> ConversationAssessment:
        """Perform complete assessment of a conversation"""
        
        conversation_id = conversation_data['conversation_id']
        full_text = conversation_data.get('full_text', '')
        
        # Convert numeric fields to float to handle Decimal objects from PostgreSQL
        total_words = float(conversation_data.get('total_words', 0))
        message_count = int(conversation_data.get('message_count', 0))
        
        # Calculate content hash for duplicate detection
        content_hash = self.calculate_content_hash(conversation_data)
        is_duplicate, duplicate_of = self.check_for_duplicate(content_hash, conversation_id)
        
        # If duplicate, create minimal assessment
        if is_duplicate:
            return ConversationAssessment(
                conversation_id=conversation_id,
                title=f"Conversation {conversation_id} (DUPLICATE)",
                word_count=int(total_words),
                message_count=message_count,
                code_density=0.0,
                readability_score=0.0,
                coherence_score=0.0,
                depth_score=0.0,
                completeness_score=0.0,
                composite_score=0.0,
                primary_topic='duplicate',
                editorial_potential='duplicate',
                justification=f"Duplicate of conversation {duplicate_of}",
                participant_count=len(conversation_data['participants'].split(', ')) if conversation_data['participants'] else 1,
                date_range=f"{conversation_data['start_time'].date()} to {conversation_data['end_time'].date()}",
                content_hash=content_hash,
                is_duplicate=True,
                duplicate_of=duplicate_of
            )
        
        # Calculate metrics for original content
        code_density = self.analyze_code_density(full_text)
        readability_score = self.analyze_readability(full_text, code_density)
        depth_score = self.analyze_depth(full_text)
        coherence_score = self.analyze_coherence(conversation_data)
        completeness_score = self.analyze_completeness(conversation_data)
        
        # Calculate composite score
        length_bonus = min(0.2, (total_words - 1500) / 10000)
        
        composite_score = (
            depth_score * self.weights['depth'] +
            readability_score * self.weights['readability'] +
            coherence_score * self.weights['coherence'] +
            completeness_score * self.weights['completeness'] +
            length_bonus * self.weights['length_bonus']
        )
        
        # Topic classification
        primary_topic = self.classify_primary_topic(full_text)
        
        # Editorial potential assessment
        assessment_dict = {
            'composite_score': composite_score,
            'word_count': int(total_words),
            'primary_topic': primary_topic,
            'code_density': code_density,
            'readability_score': readability_score,
            'depth_score': depth_score,
            'coherence_score': coherence_score,
            'completeness_score': completeness_score,
            'is_duplicate': is_duplicate,
            'duplicate_of': duplicate_of
        }
        
        editorial_potential, justification = self.assess_editorial_potential(assessment_dict)
        
        # Create assessment object
        return ConversationAssessment(
            conversation_id=conversation_id,
            title=f"Conversation {conversation_id}",
            word_count=int(total_words),
            message_count=message_count,
            code_density=code_density,
            readability_score=readability_score,
            coherence_score=coherence_score,
            depth_score=depth_score,
            completeness_score=completeness_score,
            composite_score=composite_score,
            primary_topic=primary_topic,
            editorial_potential=editorial_potential,
            justification=justification,
            participant_count=len(conversation_data['participants'].split(', ')) if conversation_data['participants'] else 1,
            date_range=f"{conversation_data['start_time'].date()} to {conversation_data['end_time'].date()}",
            content_hash=content_hash,
            is_duplicate=is_duplicate,
            duplicate_of=duplicate_of
        )
    
    def store_assessment(self, assessment: ConversationAssessment) -> bool:
        """Store assessment in PostgreSQL with duplicate information"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversation_quality_assessments 
                    (conversation_id, word_count, message_count, code_density, 
                     readability_score, coherence_score, depth_score, completeness_score,
                     composite_score, primary_topic, editorial_potential, assessment_version,
                     content_hash, is_duplicate, duplicate_of, assessment_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (conversation_id) 
                    DO UPDATE SET
                        word_count = EXCLUDED.word_count,
                        message_count = EXCLUDED.message_count,
                        code_density = EXCLUDED.code_density,
                        readability_score = EXCLUDED.readability_score,
                        coherence_score = EXCLUDED.coherence_score,
                        depth_score = EXCLUDED.depth_score,
                        completeness_score = EXCLUDED.completeness_score,
                        composite_score = EXCLUDED.composite_score,
                        primary_topic = EXCLUDED.primary_topic,
                        editorial_potential = EXCLUDED.editorial_potential,
                        assessment_version = EXCLUDED.assessment_version,
                        content_hash = EXCLUDED.content_hash,
                        is_duplicate = EXCLUDED.is_duplicate,
                        duplicate_of = EXCLUDED.duplicate_of,
                        assessment_metadata = EXCLUDED.assessment_metadata,
                        updated_at = NOW()
                """, (
                    assessment.conversation_id,
                    assessment.word_count,
                    assessment.message_count,
                    assessment.code_density,
                    assessment.readability_score,
                    assessment.coherence_score,
                    assessment.depth_score,
                    assessment.completeness_score,
                    assessment.composite_score,
                    assessment.primary_topic,
                    assessment.editorial_potential,
                    self.assessment_version,
                    assessment.content_hash,
                    assessment.is_duplicate,
                    assessment.duplicate_of,
                    json.dumps({
                        'justification': assessment.justification,
                        'participant_count': assessment.participant_count,
                        'date_range': assessment.date_range
                    })
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Error storing assessment for {assessment.conversation_id}: {e}")
            return False
    
    def run_full_archive_assessment(self, min_words: int = 100, batch_size: int = 100) -> Dict[str, Any]:
        """Run assessment on entire archive with progress tracking"""
        
        print(f"🚀 BATCH CONVERSATION QUALITY ASSESSMENT")
        print(f"   Version: {self.assessment_version}")
        print(f"   Minimum words: {min_words}")
        print(f"   Batch size: {batch_size}")
        
        # Ensure duplicate columns exist
        self.ensure_duplicate_columns_exist()
        
        # Get all conversations
        all_conversations = self.get_all_conversations(min_words)
        total_conversations = len(all_conversations)
        
        if total_conversations == 0:
            print("❌ No conversations found meeting criteria")
            return {}
        
        print(f"📊 Processing {total_conversations} conversations...")
        
        # Process in batches
        processed = 0
        successful_assessments = 0
        duplicates_found = 0
        errors = 0
        
        start_time = datetime.now()
        
        for i in range(0, total_conversations, batch_size):
            batch = all_conversations[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_conversations + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} conversations)")
            
            for j, conversation in enumerate(batch):
                conv_id = conversation['conversation_id']
                
                try:
                    assessment = self.assess_conversation(conversation)
                    
                    if self.store_assessment(assessment):
                        successful_assessments += 1
                        if assessment.is_duplicate:
                            duplicates_found += 1
                            print(f"   {j+1:3d}/{len(batch)}: Conv {conv_id} - DUPLICATE of {assessment.duplicate_of}")
                        else:
                            print(f"   {j+1:3d}/{len(batch)}: Conv {conv_id} - Score: {assessment.composite_score:.3f} ({assessment.editorial_potential})")
                    else:
                        errors += 1
                        
                except Exception as e:
                    print(f"   {j+1:3d}/{len(batch)}: Conv {conv_id} - ERROR: {e}")
                    errors += 1
                
                processed += 1
                
                # Progress update every 50 conversations
                if processed % 50 == 0:
                    elapsed = datetime.now() - start_time
                    rate = processed / elapsed.total_seconds() * 60  # conversations per minute
                    remaining = (total_conversations - processed) / (rate / 60) if rate > 0 else 0
                    print(f"      📈 Progress: {processed}/{total_conversations} ({processed/total_conversations*100:.1f}%) | "
                          f"Rate: {rate:.1f}/min | ETA: {remaining/60:.1f}min")
        
        # Final statistics
        end_time = datetime.now()
        duration = end_time - start_time
        
        results = {
            'total_conversations': total_conversations,
            'processed': processed,
            'successful_assessments': successful_assessments,
            'duplicates_found': duplicates_found,
            'errors': errors,
            'duration_seconds': duration.total_seconds(),
            'rate_per_minute': processed / duration.total_seconds() * 60 if duration.total_seconds() > 0 else 0,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        print(f"\n{'='*80}")
        print(f"🎉 BATCH ASSESSMENT COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Total conversations: {total_conversations:,}")
        print(f"✅ Successfully processed: {successful_assessments:,}")
        print(f"🔄 Duplicates found: {duplicates_found:,}")
        print(f"❌ Errors: {errors:,}")
        print(f"⏱️  Duration: {duration}")
        print(f"🏃 Rate: {results['rate_per_minute']:.1f} conversations/minute")
        
        return results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Batch Conversation Quality Assessor - Full Archive Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process entire archive with duplicate detection
  python batch_conversation_assessor.py --min-words 100 --batch-size 100

  # Process only substantial conversations
  python batch_conversation_assessor.py --min-words 1500 --batch-size 50

  # Quick test with minimal conversations
  python batch_conversation_assessor.py --min-words 50 --batch-size 20
        """
    )
    
    parser.add_argument('--min-words', type=int, default=100, 
                       help='Minimum word count for conversations (default: 100)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of conversations to process per batch (default: 100)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Show statistics without processing')
    
    args = parser.parse_args()
    
    assessor = BatchConversationAssessor()
    
    if args.stats_only:
        # Just show what would be processed
        conversations = assessor.get_all_conversations(args.min_words)
        print(f"📊 Would process {len(conversations)} conversations with min {args.min_words} words")
        return
    
    # Run full assessment
    results = assessor.run_full_archive_assessment(args.min_words, args.batch_size)
    
    if results:
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_runs/batch_assessment_{timestamp}.json"
        
        Path("test_runs").mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")


if __name__ == "__main__":
    main()