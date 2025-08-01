#!/usr/bin/env python3
"""
Conversation Sampler
Finds the best representative message from top-rated conversations
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
class RepresentativeMessage:
    """Data structure for a representative message sample"""
    conversation_id: int
    message_id: int
    conversation_score: float
    message_score: float
    author: str
    timestamp: datetime
    word_count: int
    content: str
    selection_reason: str
    context_before: str
    context_after: str

class ConversationSampler:
    """Extracts representative messages from top-rated conversations"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        
        # Message scoring criteria
        self.quality_indicators = {
            'depth_patterns': [
                r'\b(?:because|therefore|however|furthermore|moreover|consequently|thus)\b',
                r'\b(?:analysis|examine|consider|evaluate|assess|determine|explore)\b',
                r'\b(?:principle|theory|concept|framework|methodology|approach)\b',
                r'\b(?:understanding|insight|perspective|implications|significance)\b',
                r'\?.*\?',  # Multiple questions
                r':\s*$',   # Explanatory colons
            ],
            'explanation_patterns': [
                r'\bfor example\b',
                r'\bthat is\b', 
                r'\bin other words\b',
                r'\bspecifically\b',
                r'\bto illustrate\b',
                r'\blet me explain\b',
                r'\bthe key point is\b',
                r'\bwhat this means is\b',
            ],
            'synthesis_patterns': [
                r'\bin summary\b',
                r'\bto conclude\b',
                r'\bbringing together\b',
                r'\bcombining these\b',
                r'\bthe overall picture\b',
                r'\bputting it all together\b',
            ],
            'insight_patterns': [
                r'\bI think the key insight\b',
                r'\bwhat\'s interesting is\b',
                r'\bthe important thing to note\b',
                r'\bthis suggests that\b',
                r'\bwhat this reveals\b',
            ]
        }
        
        # Penalties for poor quality indicators
        self.quality_penalties = {
            'code_heavy': r'```[\s\S]*?```|`[^`\n]+`',
            'error_messages': r'Error:|Exception:|Traceback:|Failed to',
            'command_outputs': r'^\s*[#$>]\s+',
            'fragmented': r'^.{1,20}$',  # Very short messages
            'repetitive': r'\b(\w+)\s+\1\b',  # Repeated words
            'json_data': r'^\s*[\{\[].*[\}\]]\s*$',  # JSON objects/arrays
            'api_response': r'"statusCode":|"headers":|"response":|"data":',
            'tool_output': r'^Tool\s+result|^Function\s+result|^API\s+response',
            'system_message': r'^\s*\[system\]|\[assistant\]|\[user\]',
        }
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_top_conversations(self, limit: int = 10, min_score: float = 0.5) -> List[Dict]:
        """Get top-rated conversations from quality assessments"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT qa.conversation_id, qa.composite_score, qa.primary_topic, 
                       qa.editorial_potential, qa.word_count, qa.message_count,
                       qa.assessment_metadata
                FROM conversation_quality_assessments qa
                WHERE qa.composite_score >= %s
                ORDER BY qa.composite_score DESC
                LIMIT %s
            """, (min_score, limit))
            
            return cursor.fetchall()
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages from a conversation with context"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, body_text, author, timestamp, word_count,
                       LAG(body_text, 1) OVER (ORDER BY timestamp) as prev_message,
                       LEAD(body_text, 1) OVER (ORDER BY timestamp) as next_message
                FROM archived_content 
                WHERE parent_id = %s 
                    AND content_type = 'message'
                    AND body_text IS NOT NULL
                    AND word_count > 20
                ORDER BY timestamp
            """, (conversation_id,))
            
            return cursor.fetchall()
    
    def is_editorial_content(self, content: str) -> bool:
        """Check if content looks like editorial/human-readable content"""
        if not content:
            return False
        
        # Major disqualifiers
        disqualifiers = [
            r'^\s*[\{\[].*[\}\]]\s*$',  # Pure JSON
            r'"statusCode":|"headers":|"response":',  # API responses
            r'Tool\s+result|Function\s+result',  # Tool outputs
            r'^\s*<[^>]+>.*<\/[^>]+>\s*$',  # Pure HTML/XML
            r'Error:|Exception:|Traceback:',  # Error messages
        ]
        
        for pattern in disqualifiers:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL):
                return False
        
        # Must have some human-readable characteristics
        sentences = re.split(r'[.!?]+', content)
        readable_sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        
        if len(readable_sentences) < 1:
            return False
        
        # Should have some natural language patterns
        natural_patterns = [
            r'\b(?:I|you|we|they|this|that|these|those)\b',  # Pronouns
            r'\b(?:is|are|was|were|have|has|had|will|would|can|could)\b',  # Common verbs
            r'\b(?:and|but|or|because|since|when|where|how|why)\b',  # Conjunctions
        ]
        
        pattern_matches = sum(1 for pattern in natural_patterns 
                            if re.search(pattern, content, re.IGNORECASE))
        
        return pattern_matches >= 2  # At least 2 natural language patterns
    
    def score_message_quality(self, message: Dict) -> Tuple[float, str]:
        """Score a message for how representative it is of conversation quality"""
        
        content = message.get('body_text', '')
        if not content:
            return 0.0, "Empty content"
        
        # First check if it's editorial content at all
        if not self.is_editorial_content(content):
            return 0.0, "Non-editorial content"
        
        content_lower = content.lower()
        score = 0.0
        reasons = []
        
        # Length scoring (optimal range)
        word_count = message.get('word_count', len(content.split()))
        if 50 <= word_count <= 300:
            length_score = 1.0
            reasons.append("optimal length")
        elif 30 <= word_count <= 500:
            length_score = 0.8
            reasons.append("good length")
        else:
            length_score = 0.5
            reasons.append("length ok")
        
        score += length_score * 0.25
        
        # Quality indicators scoring
        indicator_score = 0.0
        
        for category, patterns in self.quality_indicators.items():
            category_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
                category_matches += matches
            
            if category_matches > 0:
                category_score = min(0.2, category_matches * 0.05)
                indicator_score += category_score
                reasons.append(f"{category.replace('_', ' ')}")
        
        score += indicator_score * 0.4
        
        # Penalties for poor quality
        penalty_score = 0.0
        
        for penalty_type, pattern in self.quality_penalties.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                if penalty_type == 'code_heavy':
                    # Calculate code density
                    code_matches = re.findall(pattern, content)
                    code_chars = sum(len(match) for match in code_matches)
                    code_density = code_chars / len(content) if content else 0
                    penalty_score += code_density * 0.5
                else:
                    penalty_score += 0.2
                    reasons.append(f"penalty: {penalty_type}")
        
        score -= penalty_score
        
        # Completeness bonus - standalone readability
        if len(content.split('.')) >= 3:  # Multiple sentences
            score += 0.1
            reasons.append("complete thoughts")
        
        # Context relevance - check if it references previous discussion
        context_indicators = ['as mentioned', 'following up', 'building on', 'to add to']
        if any(indicator in content_lower for indicator in context_indicators):
            score += 0.1
            reasons.append("builds on context")
        
        # Normalize score
        score = max(0.0, min(1.0, score))
        
        reason_text = ", ".join(reasons[:3]) if reasons else "basic scoring"
        
        return score, reason_text
    
    def find_best_representative_message(self, conversation_id: int, conversation_score: float) -> Optional[RepresentativeMessage]:
        """Find the single best message to represent this conversation"""
        
        messages = self.get_conversation_messages(conversation_id)
        if not messages:
            return None
        
        # Score all messages
        scored_messages = []
        for msg in messages:
            msg_score, reason = self.score_message_quality(msg)
            scored_messages.append((msg, msg_score, reason))
        
        # Sort by score
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        
        # Get the best message
        best_msg, best_score, best_reason = scored_messages[0]
        
        # Prepare context (previous and next messages, truncated)
        context_before = ""
        context_after = ""
        
        if best_msg.get('prev_message'):
            prev = best_msg['prev_message']
            context_before = (prev[:200] + "...") if len(prev) > 200 else prev
        
        if best_msg.get('next_message'):
            next_msg = best_msg['next_message']
            context_after = (next_msg[:200] + "...") if len(next_msg) > 200 else next_msg
        
        return RepresentativeMessage(
            conversation_id=conversation_id,
            message_id=best_msg['id'],
            conversation_score=conversation_score,
            message_score=best_score,
            author=best_msg.get('author', 'Unknown'),
            timestamp=best_msg.get('timestamp'),
            word_count=best_msg.get('word_count', 0),
            content=best_msg.get('body_text', ''),
            selection_reason=best_reason,
            context_before=context_before,
            context_after=context_after
        )
    
    def sample_conversations(self, n: int = 10, min_score: float = 0.5) -> List[RepresentativeMessage]:
        """Find representative messages from top N conversations"""
        
        print(f"🔍 Finding top {n} conversations with score >= {min_score}")
        top_conversations = self.get_top_conversations(n, min_score)
        
        if not top_conversations:
            print("❌ No conversations found meeting criteria")
            return []
        
        print(f"📊 Found {len(top_conversations)} conversations to sample")
        print(f"🎯 Extracting best representative message from each...")
        
        samples = []
        
        for i, conv in enumerate(top_conversations, 1):
            conv_id = conv['conversation_id'] 
            conv_score = conv['composite_score']
            
            print(f"   {i:2d}/{len(top_conversations)}: Conversation {conv_id} (score: {conv_score:.3f})")
            
            try:
                sample = self.find_best_representative_message(conv_id, conv_score)
                if sample:
                    samples.append(sample)
                    print(f"      ✅ Selected message {sample.message_id} ({sample.word_count} words)")
                    print(f"         Reason: {sample.selection_reason}")
                else:
                    print(f"      ❌ No suitable messages found")
                    
            except Exception as e:
                print(f"      ❌ Error processing conversation: {e}")
                continue
        
        return samples
    
    def export_samples(self, samples: List[RepresentativeMessage], output_file: str = None) -> str:
        """Export samples to a readable format"""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_runs/conversation_samples_{timestamp}.md"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Conversation Representative Samples\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total samples: {len(samples)}\n\n")
            f.write("---\n\n")
            
            for i, sample in enumerate(samples, 1):
                f.write(f"## Sample {i}: Conversation {sample.conversation_id}\n\n")
                f.write(f"**Conversation Quality Score:** {sample.conversation_score:.3f}\n")
                f.write(f"**Message Quality Score:** {sample.message_score:.3f}\n") 
                f.write(f"**Author:** {sample.author}\n")
                f.write(f"**Date:** {sample.timestamp.strftime('%Y-%m-%d %H:%M') if sample.timestamp else 'Unknown'}\n")
                f.write(f"**Words:** {sample.word_count}\n")
                f.write(f"**Selection Reason:** {sample.selection_reason}\n\n")
                
                # Context before
                if sample.context_before:
                    f.write("### Context Before:\n")
                    f.write(f"> {sample.context_before}\n\n")
                
                # Main message
                f.write("### Representative Message:\n")
                f.write(f"{sample.content}\n\n")
                
                # Context after  
                if sample.context_after:
                    f.write("### Context After:\n")
                    f.write(f"> {sample.context_after}\n\n")
                
                f.write("---\n\n")
        
        return str(output_path)
    
    def create_json_export(self, samples: List[RepresentativeMessage], output_file: str = None) -> str:
        """Export samples as JSON for programmatic use"""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_runs/conversation_samples_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        samples_data = []
        for sample in samples:
            samples_data.append({
                'conversation_id': sample.conversation_id,
                'message_id': sample.message_id,
                'conversation_score': sample.conversation_score,
                'message_score': sample.message_score,
                'author': sample.author,
                'timestamp': sample.timestamp.isoformat() if sample.timestamp else None,
                'word_count': sample.word_count,
                'content': sample.content,
                'selection_reason': sample.selection_reason,
                'context_before': sample.context_before,
                'context_after': sample.context_after
            })
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_samples': len(samples),
            'samples': samples_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Conversation Sampler - Extract representative messages from top conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sample top 10 conversations  
  python conversation_sampler.py --count 10

  # Sample top 5 with higher quality threshold
  python conversation_sampler.py --count 5 --min-score 0.7

  # Export to specific file
  python conversation_sampler.py --count 15 --output my_samples.md

  # JSON export for programmatic use
  python conversation_sampler.py --count 10 --json samples.json

  # Show samples on screen only (no file export)
  python conversation_sampler.py --count 5 --no-export
        """
    )
    
    parser.add_argument('--count', '-n', type=int, default=10, 
                       help='Number of conversations to sample (default: 10)')
    parser.add_argument('--min-score', type=float, default=0.5,
                       help='Minimum conversation quality score (default: 0.5)')
    parser.add_argument('--output', '-o', help='Output markdown file path')
    parser.add_argument('--json', help='Output JSON file path')
    parser.add_argument('--no-export', action='store_true', 
                       help='Display samples without saving to file')
    
    args = parser.parse_args()
    
    sampler = ConversationSampler()
    
    # Get samples
    samples = sampler.sample_conversations(args.count, args.min_score)
    
    if not samples:
        print("❌ No samples generated")
        return
    
    # Display samples
    print(f"\n{'='*80}")
    print(f"📋 CONVERSATION REPRESENTATIVE SAMPLES")
    print(f"{'='*80}")
    
    for i, sample in enumerate(samples, 1):
        print(f"\n{i:2d}. Conversation {sample.conversation_id} | Score: {sample.conversation_score:.3f}")
        print(f"    👤 {sample.author} | 📅 {sample.timestamp.strftime('%Y-%m-%d') if sample.timestamp else 'Unknown'}")
        print(f"    📝 {sample.word_count} words | 🎯 {sample.selection_reason}")
        print(f"    💬 \"{sample.content[:100]}{'...' if len(sample.content) > 100 else ''}\"")
    
    # Export files
    if not args.no_export:
        if args.output or not args.json:
            # Export markdown
            md_file = sampler.export_samples(samples, args.output)
            print(f"\n📄 Markdown export: {md_file}")
        
        if args.json:
            # Export JSON
            json_file = sampler.create_json_export(samples, args.json)
            print(f"📄 JSON export: {json_file}")
    
    print(f"\n✅ Sampled {len(samples)} representative messages from top conversations")


if __name__ == "__main__":
    main()