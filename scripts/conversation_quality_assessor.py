#!/usr/bin/env python3
"""
Conversation Quality Assessor
Analyzes archive conversations for editorial potential using PostgreSQL with pgvector
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

class ConversationQualityAssessor:
    """PostgreSQL-native conversation quality assessment system"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.assessment_version = "v1.0"
        
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
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_conversation_candidates(self, min_words: int = 1500, limit: int = 100) -> List[Dict]:
        """Get conversations that meet basic criteria for assessment"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get conversations with enough content
            cursor.execute("""
                SELECT 
                    parent_id as conversation_id,
                    COUNT(*) as message_count,
                    SUM(word_count) as total_words,
                    STRING_AGG(DISTINCT author, ', ') as participants,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    -- Get a sample of the conversation for topic analysis
                    STRING_AGG(body_text, ' ' ORDER BY timestamp) as full_text
                FROM archived_content 
                WHERE content_type = 'message' 
                    AND body_text IS NOT NULL 
                    AND word_count > 50
                    AND parent_id IS NOT NULL
                GROUP BY parent_id
                HAVING SUM(word_count) >= %s 
                    AND COUNT(*) >= 5
                ORDER BY SUM(word_count) DESC
                LIMIT %s
            """, (min_words, limit))
            
            return cursor.fetchall()
    
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
    
    def analyze_coherence(self, messages: List[Dict]) -> float:
        """Assess topic coherence across the conversation"""
        if not messages:
            return 0.0
        
        # Extract topics from messages
        all_topics = []
        for msg in messages:
            text = msg.get('body_text', '').lower()
            msg_topics = []
            
            for topic, keywords in self.topic_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in text)
                if keyword_count > 0:
                    msg_topics.append((topic, keyword_count))
            
            if msg_topics:
                # Take the most prominent topic for this message
                dominant_topic = max(msg_topics, key=lambda x: x[1])
                all_topics.append(dominant_topic[0])
        
        if not all_topics:
            return 0.5  # Neutral score if no clear topics
        
        # Calculate topic consistency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Coherence is higher when one topic dominates
        total_msgs = len(all_topics)
        max_topic_count = max(topic_counts.values())
        coherence = max_topic_count / total_msgs
        
        return coherence
    
    def analyze_completeness(self, messages: List[Dict]) -> float:
        """Assess whether the conversation reaches satisfying conclusions"""
        if not messages:
            return 0.0
        
        # Look at the last few messages for resolution indicators
        last_messages = messages[-3:] if len(messages) >= 3 else messages
        last_text = ' '.join([msg.get('body_text', '') for msg in last_messages]).lower()
        
        completion_indicators = [
            r'\b(?:conclusion|summary|in summary|to conclude)\b',
            r'\b(?:finally|ultimately|in the end)\b',
            r'\b(?:solution|resolved|answer|result)\b',
            r'\b(?:thank you|thanks|helpful|clear now)\b'
        ]
        
        completeness_score = 0.0
        for pattern in completion_indicators:
            if re.search(pattern, last_text):
                completeness_score += 0.3
        
        # Bonus for conversations that end with substantial messages
        if last_messages:
            last_msg_length = len(last_messages[-1].get('body_text', '').split())
            if last_msg_length > 30:  # Substantial final message
                completeness_score += 0.2
        
        # Check if conversation doesn't just trail off
        if messages:
            msg_lengths = [len(msg.get('body_text', '').split()) for msg in messages[-5:]]
            if len(msg_lengths) >= 3:
                # Penalty if messages get progressively shorter (trailing off)
                if msg_lengths[-1] < msg_lengths[0] / 2:
                    completeness_score -= 0.2
        
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
        
        # Get detailed messages for this conversation
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT body_text, author, timestamp, word_count
                FROM archived_content 
                WHERE parent_id = %s AND content_type = 'message'
                ORDER BY timestamp
            """, (conversation_id,))
            
            messages = cursor.fetchall()
        
        # Combine all text for analysis
        full_text = ' '.join([msg['body_text'] or '' for msg in messages])
        
        # Calculate metrics
        code_density = self.analyze_code_density(full_text)
        readability_score = self.analyze_readability(full_text, code_density)
        depth_score = self.analyze_depth(full_text)
        coherence_score = self.analyze_coherence(messages)
        completeness_score = self.analyze_completeness(messages)
        
        # Calculate composite score
        length_bonus = min(0.2, (conversation_data['total_words'] - 1500) / 10000)
        
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
            'word_count': conversation_data['total_words'],
            'primary_topic': primary_topic,
            'code_density': code_density,
            'readability_score': readability_score,
            'depth_score': depth_score,
            'coherence_score': coherence_score,
            'completeness_score': completeness_score
        }
        
        editorial_potential, justification = self.assess_editorial_potential(assessment_dict)
        
        # Create assessment object
        return ConversationAssessment(
            conversation_id=conversation_id,
            title=f"Conversation {conversation_id}",  # Could extract from first message
            word_count=conversation_data['total_words'],
            message_count=conversation_data['message_count'],
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
            date_range=f"{conversation_data['start_time'].date()} to {conversation_data['end_time'].date()}"
        )
    
    def store_assessment(self, assessment: ConversationAssessment) -> bool:
        """Store assessment in PostgreSQL"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversation_quality_assessments 
                    (conversation_id, word_count, message_count, code_density, 
                     readability_score, coherence_score, depth_score, completeness_score,
                     composite_score, primary_topic, editorial_potential, assessment_version,
                     assessment_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    json.dumps({
                        'justification': assessment.justification,
                        'participant_count': assessment.participant_count,
                        'date_range': assessment.date_range
                    })
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Error storing assessment: {e}")
            return False
    
    def get_top_conversations(self, limit: int = 10, min_score: float = 0.5) -> List[Dict]:
        """Retrieve top-rated conversations from PostgreSQL"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT qa.*, qa.assessment_metadata
                FROM conversation_quality_assessments qa
                WHERE qa.composite_score >= %s
                ORDER BY qa.composite_score DESC
                LIMIT %s
            """, (min_score, limit))
            
            return cursor.fetchall()
    
    def run_batch_assessment(self, min_words: int = 1500, limit: int = 50) -> List[ConversationAssessment]:
        """Run assessment on a batch of conversations"""
        
        print(f"🔍 Finding conversation candidates (min {min_words} words)...")
        candidates = self.get_conversation_candidates(min_words, limit)
        
        if not candidates:
            print("No conversations found meeting criteria")
            return []
        
        print(f"📊 Assessing {len(candidates)} conversations...")
        assessments = []
        
        for i, candidate in enumerate(candidates):
            print(f"   Processing {i+1}/{len(candidates)}: Conversation {candidate['conversation_id']} ({candidate['total_words']} words)")
            
            try:
                assessment = self.assess_conversation(candidate)
                assessments.append(assessment)
                
                # Store in database
                if self.store_assessment(assessment):
                    print(f"      ✅ Score: {assessment.composite_score:.3f} - {assessment.editorial_potential}")
                else:
                    print(f"      ⚠️  Assessment completed but storage failed")
                    
            except Exception as e:
                print(f"      ❌ Error assessing conversation: {e}")
                continue
        
        return sorted(assessments, key=lambda x: x.composite_score, reverse=True)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Conversation Quality Assessor - PostgreSQL Native",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assess conversations and show top 10
  python conversation_quality_assessor.py assess --min-words 1500 --limit 50

  # Show previously assessed top conversations  
  python conversation_quality_assessor.py top --limit 15 --min-score 0.6

  # Assess specific conversation
  python conversation_quality_assessor.py single --conversation-id 12345
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Assessment command
    assess_parser = subparsers.add_parser('assess', help='Run batch assessment')
    assess_parser.add_argument('--min-words', type=int, default=1500, help='Minimum word count')
    assess_parser.add_argument('--limit', type=int, default=50, help='Maximum conversations to assess')
    assess_parser.add_argument('--store', action='store_true', help='Store results in database')
    
    # Top conversations command
    top_parser = subparsers.add_parser('top', help='Show top-rated conversations')
    top_parser.add_argument('--limit', type=int, default=10, help='Number of conversations to show')
    top_parser.add_argument('--min-score', type=float, default=0.5, help='Minimum composite score')
    
    # Single conversation command
    single_parser = subparsers.add_parser('single', help='Assess single conversation')
    single_parser.add_argument('--conversation-id', type=int, required=True, help='Conversation ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    assessor = ConversationQualityAssessor()
    
    if args.command == 'assess':
        assessments = assessor.run_batch_assessment(args.min_words, args.limit)
        
        print(f"\n{'='*80}")
        print("📊 TOP CONVERSATION QUALITY ASSESSMENTS")
        print('='*80)
        
        for i, assessment in enumerate(assessments[:10], 1):
            print(f"{i:2d}. Score: {assessment.composite_score:.3f} | ID: {assessment.conversation_id}")
            print(f"    📝 {assessment.word_count:,} words, {assessment.message_count} messages")
            print(f"    🎯 Topic: {assessment.primary_topic} | Potential: {assessment.editorial_potential}")
            print(f"    📊 Depth: {assessment.depth_score:.2f} | Read: {assessment.readability_score:.2f} | Code: {assessment.code_density:.2f}")
            print(f"    💭 {assessment.justification}")
            print()
    
    elif args.command == 'top':
        top_conversations = assessor.get_top_conversations(args.limit, args.min_score)
        
        if not top_conversations:
            print("No assessed conversations found. Run 'assess' command first.")
            return
        
        print(f"\n{'='*80}")
        print("🏆 TOP RATED CONVERSATIONS FROM DATABASE")
        print('='*80)
        
        for i, conv in enumerate(top_conversations, 1):
            metadata_raw = conv.get('assessment_metadata', {})
            metadata = metadata_raw if isinstance(metadata_raw, dict) else json.loads(metadata_raw or '{}')
            print(f"{i:2d}. Score: {conv['composite_score']:.3f} | ID: {conv['conversation_id']}")
            print(f"    📝 {conv['word_count']:,} words, {conv['message_count']} messages")
            print(f"    🎯 Topic: {conv['primary_topic']} | Potential: {conv['editorial_potential']}")
            print(f"    📊 Depth: {conv['depth_score']:.2f} | Read: {conv['readability_score']:.2f}")
            print(f"    📅 {metadata.get('date_range', 'Unknown dates')}")
            print(f"    💭 {metadata.get('justification', 'No justification available')}")
            print()
    
    elif args.command == 'single':
        # Implementation for single conversation assessment
        print(f"Assessing single conversation {args.conversation_id}...")
        # This would require additional implementation


if __name__ == "__main__":
    main()