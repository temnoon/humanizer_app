#!/usr/bin/env python3
"""
Non-Lexical Narrative Feature Extractor
Extracts style/persona/namespace carriers without storing lexical content
"""

import re
import numpy as np
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import spacy
from textstat import flesch_reading_ease, syllable_count
import json


@dataclass
class FeatureVector:
    """Container for non-lexical narrative features"""
    prosody: Dict[str, float]
    syntax: Dict[str, float] 
    discourse: Dict[str, float]
    persona_signature: Dict[str, float]
    namespace_signature: Dict[str, float]
    style_rhythm: Dict[str, float]


class NarrativeFeatureExtractor:
    """Extract non-lexical carriers for style/persona/namespace"""
    
    def __init__(self):
        # Load spaCy model for linguistic analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_features(self, paragraph_text: str) -> FeatureVector:
        """Extract all non-lexical features from a paragraph"""
        
        # Parse with spaCy if available
        if self.nlp:
            doc = self.nlp(paragraph_text)
            sentences = list(doc.sents)
            tokens = [token for token in doc if not token.is_space]
        else:
            # Fallback: basic sentence splitting
            sentences = re.split(r'[.!?]+', paragraph_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            tokens = paragraph_text.split()
        
        return FeatureVector(
            prosody=self._extract_prosody_features(paragraph_text, sentences),
            syntax=self._extract_syntax_features(doc if self.nlp else None, sentences),
            discourse=self._extract_discourse_features(paragraph_text, sentences),
            persona_signature=self._extract_persona_features(paragraph_text, doc if self.nlp else None),
            namespace_signature=self._extract_namespace_features(paragraph_text, doc if self.nlp else None),
            style_rhythm=self._extract_style_rhythm_features(paragraph_text, sentences)
        )
    
    def _extract_prosody_features(self, text: str, sentences: List) -> Dict[str, float]:
        """Prosodic and rhythmic features"""
        
        features = {}
        
        # Sentence length statistics
        if sentences:
            sent_lengths = [len(s.split()) if isinstance(s, str) else len([t for t in s if not t.is_punct]) for s in sentences]
            features.update({
                'avg_sentence_length': np.mean(sent_lengths),
                'sentence_length_variance': np.var(sent_lengths),
                'sentence_length_range': max(sent_lengths) - min(sent_lengths) if sent_lengths else 0,
                'sentence_count': len(sentences)
            })
        
        # Punctuation rhythm
        punct_chars = ',.;:!?-—'
        features.update({
            'comma_density': text.count(',') / len(text) if text else 0,
            'semicolon_density': text.count(';') / len(text) if text else 0,
            'dash_density': text.count('—') / len(text) if text else 0,
            'exclamation_density': text.count('!') / len(text) if text else 0,
            'question_density': text.count('?') / len(text) if text else 0,
            'punct_entropy': self._calculate_entropy([text.count(p) for p in punct_chars])
        })
        
        # Pause patterns (approximated by punctuation)
        pause_marks = re.findall(r'[,.;:—]', text)
        if pause_marks:
            features['pause_frequency'] = len(pause_marks) / len(text)
            features['pause_variety'] = len(set(pause_marks)) / len(pause_marks)
        else:
            features['pause_frequency'] = 0
            features['pause_variety'] = 0
        
        # Readability proxy
        try:
            features['flesch_ease'] = flesch_reading_ease(text)
            features['avg_syllables_per_word'] = syllable_count(text) / len(text.split()) if text.split() else 0
        except:
            features['flesch_ease'] = 0
            features['avg_syllables_per_word'] = 0
            
        return features
    
    def _extract_syntax_features(self, doc, sentences: List) -> Dict[str, float]:
        """Syntactic structure features"""
        
        features = {}
        
        if doc is not None and hasattr(doc, '__iter__'):
            # POS tag distributions
            pos_counts = Counter([token.pos_ for token in doc if not token.is_punct])
            total_pos = sum(pos_counts.values())
            
            if total_pos > 0:
                features.update({
                    'noun_ratio': pos_counts.get('NOUN', 0) / total_pos,
                    'verb_ratio': pos_counts.get('VERB', 0) / total_pos,
                    'adj_ratio': pos_counts.get('ADJ', 0) / total_pos,
                    'adv_ratio': pos_counts.get('ADV', 0) / total_pos,
                    'pron_ratio': pos_counts.get('PRON', 0) / total_pos,
                    'det_ratio': pos_counts.get('DET', 0) / total_pos
                })
            
            # Dependency depth and complexity
            dep_depths = []
            subordination_count = 0
            
            for token in doc:
                if not token.is_punct:
                    depth = self._get_dependency_depth(token)
                    dep_depths.append(depth)
                    
                    if token.dep_ in ['advcl', 'ccomp', 'xcomp', 'acl']:
                        subordination_count += 1
            
            if dep_depths:
                features.update({
                    'avg_dependency_depth': np.mean(dep_depths),
                    'max_dependency_depth': max(dep_depths),
                    'subordination_ratio': subordination_count / len([t for t in doc if not t.is_punct])
                })
            
            # Sentence complexity patterns
            complex_sents = 0
            for sent in doc.sents:
                clauses = [token for token in sent if token.dep_ in ['ROOT', 'ccomp', 'xcomp', 'advcl']]
                if len(clauses) > 1:
                    complex_sents += 1
                    
            features['complex_sentence_ratio'] = complex_sents / len(list(doc.sents)) if list(doc.sents) else 0
            
        else:
            # Fallback syntax features without spaCy
            text = ' '.join(sentences) if sentences else ''
            words = text.split()
            
            # Simple approximations
            features.update({
                'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
                'long_word_ratio': len([w for w in words if len(w) > 6]) / len(words) if words else 0,
                'capitalized_ratio': len([w for w in words if w and w[0].isupper()]) / len(words) if words else 0
            })
        
        return features
    
    def _extract_discourse_features(self, text: str, sentences: List) -> Dict[str, float]:
        """Discourse structure and rhetorical features"""
        
        features = {}
        
        # Hedging and intensification markers
        hedge_words = ['seems', 'appears', 'perhaps', 'maybe', 'possibly', 'probably', 'likely', 'might', 'could', 'would']
        intensifiers = ['very', 'extremely', 'absolutely', 'completely', 'totally', 'utterly', 'quite', 'rather']
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        features.update({
            'hedge_density': sum(text_lower.count(word) for word in hedge_words) / word_count if word_count else 0,
            'intensifier_density': sum(text_lower.count(word) for word in intensifiers) / word_count if word_count else 0
        })
        
        # Discourse connectives
        connectives = {
            'causal': ['because', 'since', 'therefore', 'thus', 'consequently'],
            'contrast': ['however', 'nevertheless', 'nonetheless', 'yet', 'although'],
            'additive': ['furthermore', 'moreover', 'additionally', 'also', 'besides'],
            'temporal': ['then', 'next', 'subsequently', 'meanwhile', 'finally']
        }
        
        for conn_type, words in connectives.items():
            density = sum(text_lower.count(word) for word in words) / word_count if word_count else 0
            features[f'{conn_type}_connective_density'] = density
        
        # Question and exclamation patterns
        features.update({
            'interrogative_ratio': text.count('?') / len(sentences) if sentences else 0,
            'exclamatory_ratio': text.count('!') / len(sentences) if sentences else 0
        })
        
        # Repetition patterns (structural, not lexical)
        sentence_starts = [s.strip()[:10] for s in sentences if len(s.strip()) > 10]
        if sentence_starts:
            unique_starts = len(set(sentence_starts))
            features['sentence_start_variety'] = unique_starts / len(sentence_starts)
        else:
            features['sentence_start_variety'] = 1.0
            
        return features
    
    def _extract_persona_features(self, text: str, doc=None) -> Dict[str, float]:
        """Features indicating narrative persona/voice"""
        
        features = {}
        
        # Pronoun usage patterns
        pronouns = {
            'first_person': ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'],
            'second_person': ['you', 'your', 'yours'],
            'third_person': ['he', 'him', 'his', 'she', 'her', 'hers', 'they', 'them', 'their']
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        word_count = len(words)
        
        for pron_type, pron_list in pronouns.items():
            count = sum(words.count(pron) for pron in pron_list)
            features[f'{pron_type}_pronoun_ratio'] = count / word_count if word_count else 0
        
        # Modality markers (epistemic stance)
        modals = {
            'certainty': ['must', 'will', 'shall', 'certainly', 'definitely'],
            'possibility': ['may', 'might', 'could', 'possibly', 'perhaps'],
            'necessity': ['should', 'ought', 'need', 'necessary', 'required']
        }
        
        for modal_type, modal_list in modals.items():
            count = sum(text_lower.count(modal) for modal in modal_list)
            features[f'{modal_type}_modality'] = count / word_count if word_count else 0
        
        # Evidentiality markers
        evidence_markers = ['apparently', 'reportedly', 'allegedly', 'supposedly', 'evidently']
        features['evidentiality_density'] = sum(text_lower.count(marker) for marker in evidence_markers) / word_count if word_count else 0
        
        # Evaluation and stance markers  
        evaluation_words = ['good', 'bad', 'wonderful', 'terrible', 'beautiful', 'ugly', 'amazing', 'awful']
        features['evaluative_density'] = sum(text_lower.count(word) for word in evaluation_words) / word_count if word_count else 0
        
        return features
    
    def _extract_namespace_features(self, text: str, doc=None) -> Dict[str, float]:
        """Features indicating cultural/thematic namespace"""
        
        features = {}
        
        # Semantic field approximations (without storing lexical items)
        semantic_fields = {
            'religious': ['god', 'lord', 'heaven', 'hell', 'soul', 'divine', 'sacred', 'holy', 'pray', 'sin'],
            'military': ['war', 'battle', 'soldier', 'army', 'fight', 'weapon', 'victory', 'defeat', 'enemy', 'sword'],
            'domestic': ['home', 'family', 'house', 'kitchen', 'garden', 'child', 'mother', 'father', 'wife', 'husband'],
            'nature': ['tree', 'flower', 'river', 'mountain', 'sea', 'sky', 'earth', 'wind', 'rain', 'sun'],
            'urban': ['city', 'street', 'building', 'car', 'shop', 'office', 'apartment', 'traffic', 'crowd', 'noise'],
            'courtly': ['lord', 'lady', 'noble', 'court', 'honor', 'grace', 'majesty', 'knight', 'castle', 'realm']
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        for field_name, field_words in semantic_fields.items():
            field_density = sum(text_lower.count(word) for word in field_words) / word_count if word_count else 0
            features[f'{field_name}_field_density'] = field_density
        
        # Temporal markers (historical period indicators)
        temporal_markers = {
            'archaic': ['thou', 'thee', 'thy', 'hath', 'doth', 'wherefore', 'hither', 'thither'],
            'modern': ['computer', 'internet', 'phone', 'car', 'television', 'technology', 'digital'],
            'industrial': ['factory', 'machine', 'engine', 'railway', 'telegraph', 'steam', 'coal']
        }
        
        for period, markers in temporal_markers.items():
            density = sum(text_lower.count(marker) for marker in markers) / word_count if word_count else 0
            features[f'{period}_temporal_density'] = density
        
        # Cultural register markers
        register_markers = {
            'formal': ['furthermore', 'nevertheless', 'consequently', 'therefore', 'moreover'],
            'colloquial': ['gonna', 'wanna', 'gotta', 'yeah', 'okay', 'stuff', 'thing'],
            'literary': ['whereupon', 'thereafter', 'heretofore', 'notwithstanding', 'perchance']
        }
        
        for register, markers in register_markers.items():
            density = sum(text_lower.count(marker) for marker in markers) / word_count if word_count else 0
            features[f'{register}_register_density'] = density
        
        return features
    
    def _extract_style_rhythm_features(self, text: str, sentences: List) -> Dict[str, float]:
        """Rhythmic and stylistic pattern features"""
        
        features = {}
        
        # Alliteration approximation (initial consonant repetition)
        words = text.lower().split()
        if len(words) > 1:
            alliteration_count = 0
            for i in range(len(words) - 1):
                if words[i] and words[i+1] and words[i][0] == words[i+1][0] and words[i][0].isalpha():
                    alliteration_count += 1
            features['alliteration_density'] = alliteration_count / len(words)
        else:
            features['alliteration_density'] = 0
        
        # Vowel/consonant rhythm patterns
        vowels = 'aeiou'
        if text:
            vowel_ratio = sum(1 for c in text.lower() if c in vowels) / len([c for c in text if c.isalpha()])
            features['vowel_ratio'] = vowel_ratio if [c for c in text if c.isalpha()] else 0
        else:
            features['vowel_ratio'] = 0
        
        # Sentence rhythm variety
        if sentences:
            sent_lengths = [len(s.split()) for s in sentences if isinstance(s, str)]
            if sent_lengths and len(sent_lengths) > 1:
                features['rhythm_variety'] = np.std(sent_lengths) / np.mean(sent_lengths)
            else:
                features['rhythm_variety'] = 0
        else:
            features['rhythm_variety'] = 0
        
        # Parenthetical and dash usage (stylistic markers)
        features.update({
            'parenthetical_density': text.count('(') / len(text) if text else 0,
            'em_dash_density': text.count('—') / len(text) if text else 0,
            'semicolon_preference': text.count(';') / (text.count(',') + 1) if text else 0  # Preference for complex punctuation
        })
        
        return features
    
    def _get_dependency_depth(self, token) -> int:
        """Calculate dependency tree depth for a token"""
        depth = 0
        current = token
        while current.head != current:  # Until we reach the root
            depth += 1
            current = current.head
        return depth
    
    def _calculate_entropy(self, counts: List[int]) -> float:
        """Calculate Shannon entropy of a distribution"""
        total = sum(counts)
        if total == 0:
            return 0
        
        probabilities = [count / total for count in counts if count > 0]
        return -sum(p * np.log2(p) for p in probabilities) if probabilities else 0


def main():
    """CLI for testing feature extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract narrative features')
    parser.add_argument('--text', required=True, help='Text to analyze')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    extractor = NarrativeFeatureExtractor()
    features = extractor.extract_features(args.text)
    
    result = {
        'text': args.text,
        'features': {
            'prosody': features.prosody,
            'syntax': features.syntax,
            'discourse': features.discourse,
            'persona_signature': features.persona_signature,
            'namespace_signature': features.namespace_signature,
            'style_rhythm': features.style_rhythm
        }
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Features saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()