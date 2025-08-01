#!/usr/bin/env python3
"""
Personal Writing Style Extractor
Extracts authentic user-written messages, filters copy/paste content, and analyzes writing style
"""

import os
import re
import json
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import requests
from collections import Counter
import statistics

@dataclass
class WritingSample:
    """Represents a user writing sample"""
    id: int
    content: str
    timestamp: datetime
    word_count: int
    authenticity_score: float  # 0-1, higher = more likely authentic
    style_attributes: Dict[str, Any]
    conversation_context: Optional[str] = None

class PersonalWritingExtractor:
    """Extracts and analyzes personal writing style from user messages"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.ollama_host = "http://localhost:11434"
        
        # Copy/paste detection patterns
        self.external_indicators = [
            # URLs and web content
            r'https?://\S+',
            r'www\.\S+\.\w+',
            
            # Code blocks and technical formatting
            r'```[\s\S]*?```',
            r'`[^`]+`',
            r'^\s*\d+\.\s+.+$',  # Numbered lists
            r'^\s*[-*+]\s+.+$',  # Bullet points
            
            # API responses and JSON
            r'^\s*[{\[][\s\S]*[}\]]\s*$',
            r'"[^"]*":\s*[{\[]',
            
            # Error messages and logs
            r'Error:|ERROR:|Warning:|WARN:',
            r'Traceback|Exception|at line \d+',
            r'^\s*File ".*", line \d+',
            
            # Email/message headers
            r'^From:|^To:|^Subject:|^Date:',
            r'^On .* wrote:',
            
            # Article/document excerpts
            r'^#+\s+',  # Markdown headers
            r'^\s*Chapter \d+|^Part \d+',
            r'Table of Contents|Bibliography',
            
            # Formal document language
            r'pursuant to|whereas|heretofore|aforementioned',
            r'in accordance with|as per|with reference to',
        ]
        
        print("🎯 Personal Writing Style Extractor")
        print("=" * 50)
    
    def detect_external_content(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detect if text is likely copy/pasted external content
        Returns: (is_external, confidence_score, reasons)
        """
        reasons = []
        external_score = 0.0
        
        # Check for external indicators
        for pattern in self.external_indicators:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                reasons.append(f"Pattern: {pattern[:30]}... ({len(matches)} matches)")
                external_score += 0.1 * len(matches)
        
        # Length-based indicators
        if len(text) > 2000:
            reasons.append("Very long content (>2000 chars)")
            external_score += 0.2
        
        # Structural indicators
        lines = text.strip().split('\n')
        
        # Too many short lines (like lists)
        short_lines = [l for l in lines if len(l.strip()) < 50 and len(l.strip()) > 5]
        if len(short_lines) > len(lines) * 0.6:
            reasons.append(f"Many short lines ({len(short_lines)}/{len(lines)})")
            external_score += 0.3
        
        # Consistent formatting (like code or documentation)
        indented_lines = [l for l in lines if l.startswith('  ') or l.startswith('\t')]
        if len(indented_lines) > len(lines) * 0.4:
            reasons.append(f"Heavy indentation ({len(indented_lines)}/{len(lines)})")
            external_score += 0.2
        
        # Perfect grammar/formal language detection
        formal_phrases = [
            'please find attached', 'as previously discussed', 'per your request',
            'please let me know', 'thank you for your time', 'best regards',
            'sincerely yours', 'looking forward to', 'as mentioned earlier'
        ]
        
        formal_count = sum(1 for phrase in formal_phrases if phrase.lower() in text.lower())
        if formal_count > 2:
            reasons.append(f"Formal language ({formal_count} formal phrases)")
            external_score += 0.15 * formal_count
        
        # Inconsistent personal voice
        first_person = len(re.findall(r'\b(I|my|me|myself)\b', text, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|they|it|the user|the system)\b', text, re.IGNORECASE))
        
        if third_person > first_person * 2 and len(text) > 200:
            reasons.append("Lacks personal voice (third person dominant)")
            external_score += 0.2
        
        # Normalize score
        confidence = min(external_score, 1.0)
        is_external = confidence > 0.4
        
        return is_external, confidence, reasons
    
    def analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Extract writing style attributes from text"""
        
        # Basic metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Length metrics
        avg_word_length = np.mean([len(word.strip('.,!?;:"()[]{}')) for word in words]) if words else 0
        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Complexity metrics
        complex_words = [w for w in words if len(w.strip('.,!?;:"()[]{}')) > 6]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        # Punctuation patterns
        exclamations = text.count('!')
        questions = text.count('?')
        ellipses = text.count('...')
        
        # Personal voice indicators
        first_person = len(re.findall(r'\b(I|my|me|myself|we|our|us)\b', text, re.IGNORECASE))
        contractions = len(re.findall(r"\b\w+'[a-z]+\b", text, re.IGNORECASE))
        
        # Conversational markers
        conversation_markers = [
            'you know', 'i think', 'i guess', 'actually', 'basically',
            'honestly', 'seriously', 'obviously', 'definitely', 'probably'
        ]
        conversational_count = sum(text.lower().count(marker) for marker in conversation_markers)
        
        # Technical language
        technical_words = [
            'algorithm', 'function', 'variable', 'database', 'api', 'system',
            'implementation', 'architecture', 'framework', 'protocol', 'interface'
        ]
        technical_count = sum(text.lower().count(word) for word in technical_words)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'complexity_ratio': round(complexity_ratio, 3),
            'exclamation_density': round(exclamations / len(words) * 100, 2) if words else 0,
            'question_density': round(questions / len(words) * 100, 2) if words else 0,
            'ellipses_count': ellipses,
            'first_person_ratio': round(first_person / len(words) * 100, 2) if words else 0,
            'contraction_ratio': round(contractions / len(words) * 100, 2) if words else 0,
            'conversational_score': round(conversational_count / len(words) * 100, 2) if words else 0,
            'technical_score': round(technical_count / len(words) * 100, 2) if words else 0,
        }
    
    def get_llm_style_analysis(self, text: str) -> Dict[str, Any]:
        """Use LLM to analyze writing style attributes"""
        try:
            prompt = f"""Analyze this writing sample for style attributes. Respond with only a JSON object with these exact keys:

{{"tone": "casual/formal/technical/creative", "clarity": 0-10, "directness": 0-10, "creativity": 0-10, "expertise_level": "beginner/intermediate/advanced/expert", "dominant_themes": ["theme1", "theme2"], "writing_strengths": ["strength1", "strength2"]}}

Writing sample:
{text[:1000]}"""
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return json.loads(result.get('response', '{}'))
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    response_text = result.get('response', '')
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
        
        return {
            "tone": "unknown",
            "clarity": 5,
            "directness": 5,
            "creativity": 5,
            "expertise_level": "intermediate",
            "dominant_themes": [],
            "writing_strengths": []
        }
    
    def extract_user_messages(self, min_length: int = 20, max_length: int = 2000,
                            limit: Optional[int] = None) -> List[WritingSample]:
        """Extract user messages with authenticity filtering"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            # Get user messages
            query = """
                SELECT 
                    ac.id,
                    ac.body_text,
                    ac.timestamp,
                    ac.word_count,
                    ac.source_metadata,
                    COALESCE(parent.title, 'Unknown Conversation') as conversation_title
                FROM archived_content ac
                LEFT JOIN archived_content parent ON ac.parent_id = parent.id
                WHERE 
                    ac.content_type = 'message'
                    AND ac.author = 'user'
                    AND ac.body_text IS NOT NULL
                    AND LENGTH(ac.body_text) BETWEEN %s AND %s
                    AND ac.body_text != ''
                ORDER BY ac.timestamp DESC
            """
            
            params = [min_length, max_length]
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
        
        print(f"📊 Found {len(messages)} user messages to analyze")
        
        authentic_samples = []
        external_count = 0
        
        for msg in messages:
            content = msg['body_text'].strip()
            
            # Skip empty or very short messages
            if len(content) < min_length:
                continue
            
            # Detect external content
            is_external, confidence, reasons = self.detect_external_content(content)
            
            if is_external:
                external_count += 1
                continue
            
            # Calculate authenticity score (inverse of external confidence)
            authenticity_score = 1.0 - confidence
            
            # Analyze writing style
            style_attrs = self.analyze_writing_style(content)
            
            # Add LLM analysis for high-quality samples
            if authenticity_score > 0.7 and len(content) > 100:
                llm_attrs = self.get_llm_style_analysis(content)
                style_attrs.update(llm_attrs)
            
            sample = WritingSample(
                id=msg['id'],
                content=content,
                timestamp=msg['timestamp'],
                word_count=msg['word_count'] or len(content.split()),
                authenticity_score=authenticity_score,
                style_attributes=style_attrs,
                conversation_context=msg['conversation_title']
            )
            
            authentic_samples.append(sample)
        
        print(f"✅ Extracted {len(authentic_samples)} authentic writing samples")
        print(f"🚫 Filtered out {external_count} external/copied content")
        
        return authentic_samples
    
    def generate_style_profile(self, samples: List[WritingSample]) -> Dict[str, Any]:
        """Generate comprehensive personal writing style profile"""
        
        if not samples:
            return {}
        
        # Filter high-authenticity samples for core analysis
        high_auth_samples = [s for s in samples if s.authenticity_score > 0.6]
        
        print(f"📊 Generating style profile from {len(high_auth_samples)} high-authenticity samples")
        
        # Aggregate metrics
        all_attrs = [s.style_attributes for s in high_auth_samples]
        
        # Calculate averages for numerical attributes
        numerical_attrs = [
            'avg_word_length', 'avg_sentence_length', 'complexity_ratio',
            'exclamation_density', 'question_density', 'first_person_ratio',
            'contraction_ratio', 'conversational_score', 'technical_score'
        ]
        
        profile = {
            'sample_count': len(high_auth_samples),
            'total_word_count': sum(s.word_count for s in high_auth_samples),
            'avg_authenticity_score': round(np.mean([s.authenticity_score for s in high_auth_samples]), 3),
            'date_range': {
                'earliest': min(s.timestamp for s in high_auth_samples).isoformat(),
                'latest': max(s.timestamp for s in high_auth_samples).isoformat()
            }
        }
        
        # Calculate statistical measures for each attribute
        for attr in numerical_attrs:
            values = [attrs.get(attr, 0) for attrs in all_attrs if attrs.get(attr) is not None]
            if values:
                profile[attr] = {
                    'mean': round(np.mean(values), 3),
                    'median': round(np.median(values), 3),
                    'std': round(np.std(values), 3),
                    'range': [round(min(values), 3), round(max(values), 3)]
                }
        
        # Categorical analysis
        tones = [attrs.get('tone', 'unknown') for attrs in all_attrs if 'tone' in attrs]
        if tones:
            profile['dominant_tone'] = Counter(tones).most_common(3)
        
        themes = []
        for attrs in all_attrs:
            if 'dominant_themes' in attrs:
                themes.extend(attrs['dominant_themes'])
        if themes:
            profile['common_themes'] = Counter(themes).most_common(10)
        
        strengths = []
        for attrs in all_attrs:
            if 'writing_strengths' in attrs:
                strengths.extend(attrs['writing_strengths'])
        if strengths:
            profile['identified_strengths'] = Counter(strengths).most_common(5)
        
        # Writing patterns
        profile['writing_patterns'] = {
            'prefers_questions': profile.get('question_density', {}).get('mean', 0) > 2,
            'uses_exclamations': profile.get('exclamation_density', {}).get('mean', 0) > 1,
            'conversational_style': profile.get('conversational_score', {}).get('mean', 0) > 1,
            'technical_focus': profile.get('technical_score', {}).get('mean', 0) > 2,
            'personal_voice': profile.get('first_person_ratio', {}).get('mean', 0) > 3,
            'uses_contractions': profile.get('contraction_ratio', {}).get('mean', 0) > 1
        }
        
        return profile
    
    def save_results(self, samples: List[WritingSample], profile: Dict[str, Any], 
                    output_dir: str = "personal_writing_analysis") -> str:
        """Save analysis results"""
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed samples
        samples_file = f"{output_dir}/writing_samples_{timestamp}.json"
        samples_data = []
        
        for sample in samples:
            samples_data.append({
                'id': sample.id,
                'content': sample.content,
                'timestamp': sample.timestamp.isoformat(),
                'word_count': sample.word_count,
                'authenticity_score': sample.authenticity_score,
                'style_attributes': sample.style_attributes,
                'conversation_context': sample.conversation_context
            })
        
        with open(samples_file, 'w') as f:
            json.dump(samples_data, f, indent=2)
        
        # Save style profile
        profile_file = f"{output_dir}/style_profile_{timestamp}.json"
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2, default=str)
        
        # Create summary report
        report_file = f"{output_dir}/style_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(f"# Personal Writing Style Analysis Report\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n")
            f.write(f"- **Samples analyzed**: {profile.get('sample_count', 0)}\n")
            f.write(f"- **Total words**: {profile.get('total_word_count', 0):,}\n")
            f.write(f"- **Average authenticity**: {profile.get('avg_authenticity_score', 0):.3f}\n\n")
            
            if 'writing_patterns' in profile:
                f.write("## Writing Patterns\n")
                for pattern, value in profile['writing_patterns'].items():
                    f.write(f"- **{pattern.replace('_', ' ').title()}**: {'✅ Yes' if value else '❌ No'}\n")
                f.write("\n")
            
            if 'dominant_tone' in profile:
                f.write("## Dominant Tones\n")
                for tone, count in profile['dominant_tone']:
                    f.write(f"- **{tone.title()}**: {count} samples\n")
                f.write("\n")
        
        print(f"📁 Results saved to {output_dir}/")
        return output_dir

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract and analyze personal writing style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all user messages and analyze style
  python personal_writing_extractor.py extract

  # Extract specific number of recent messages
  python personal_writing_extractor.py extract --limit 500

  # Custom length filters
  python personal_writing_extractor.py extract --min-length 50 --max-length 1000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract and analyze writing samples')
    extract_parser.add_argument('--limit', type=int, help='Maximum messages to analyze')
    extract_parser.add_argument('--min-length', type=int, default=20, help='Minimum message length')
    extract_parser.add_argument('--max-length', type=int, default=2000, help='Maximum message length')
    extract_parser.add_argument('--output-dir', default='personal_writing_analysis', help='Output directory')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        extractor = PersonalWritingExtractor()
        
        # Extract samples
        samples = extractor.extract_user_messages(
            min_length=args.min_length,
            max_length=args.max_length,
            limit=args.limit
        )
        
        if samples:
            # Generate profile
            profile = extractor.generate_style_profile(samples)
            
            # Save results
            output_dir = extractor.save_results(samples, profile, args.output_dir)
            
            print(f"\n🎉 Personal writing style analysis complete!")
            print(f"📊 {len(samples)} samples analyzed")
            print(f"📁 Results in: {output_dir}")
        else:
            print("❌ No authentic writing samples found")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()