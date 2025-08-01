#!/usr/bin/env python3
"""
POVM-Based Paragraph Selection
Implements quantum-inspired paragraph scoring for optimal attribute extraction
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from narrative_feature_extractor import NarrativeFeatureExtractor, FeatureVector


@dataclass
class POVMDetector:
    """Quantum measurement operator for narrative attributes"""
    name: str
    measurement_matrix: np.ndarray
    threshold: float = 0.7
    weight: float = 1.0


@dataclass
class ParagraphScore:
    """Complete scoring record for a paragraph"""
    paragraph_id: str
    resonance_score: float
    info_gain_score: float
    redundancy_penalty: float
    clarity_score: float
    essence_strength: float
    total_score: float
    detector_responses: Dict[str, float]
    local_modes: Dict[str, Any]


class POVMParagraphSelector:
    """POVM-based intelligent paragraph selection system"""
    
    def __init__(self, 
                 max_paragraphs: int = 200,
                 resonance_weight: float = 1.0,
                 info_gain_weight: float = 1.0,
                 redundancy_weight: float = 0.5,
                 clarity_weight: float = 0.3,
                 essence_weight: float = 0.8):
        
        self.max_paragraphs = max_paragraphs
        self.weights = {
            'resonance': resonance_weight,
            'info_gain': info_gain_weight,
            'redundancy': redundancy_weight,
            'clarity': clarity_weight,
            'essence': essence_weight
        }
        
        self.feature_extractor = NarrativeFeatureExtractor()
        self.detectors = self._initialize_detectors()
        
    def _initialize_detectors(self) -> Dict[str, POVMDetector]:
        """Initialize POVM detectors for different narrative attributes"""
        
        detectors = {}
        
        # Style detector (focuses on rhythmic and syntactic features)
        style_features = [
            'avg_sentence_length', 'sentence_length_variance', 'comma_density',
            'semicolon_density', 'complex_sentence_ratio', 'subordination_ratio',
            'alliteration_density', 'rhythm_variety'
        ]
        
        # Persona detector (focuses on voice and stance markers)
        persona_features = [
            'first_person_pronoun_ratio', 'second_person_pronoun_ratio', 'third_person_pronoun_ratio',
            'certainty_modality', 'possibility_modality', 'evidentiality_density',
            'evaluative_density', 'hedge_density', 'intensifier_density'
        ]
        
        # Namespace detector (focuses on semantic field and cultural markers)
        namespace_features = [
            'religious_field_density', 'military_field_density', 'domestic_field_density',
            'nature_field_density', 'urban_field_density', 'courtly_field_density',
            'archaic_temporal_density', 'modern_temporal_density', 'formal_register_density'
        ]
        
        # Theme detector (focuses on discourse and emotional patterns)
        theme_features = [
            'causal_connective_density', 'contrast_connective_density', 'additive_connective_density',
            'interrogative_ratio', 'exclamatory_ratio', 'flesch_ease', 'evaluative_density'
        ]
        
        # Create projection matrices (simplified - would be learned from training data)
        detector_configs = {
            'style': style_features,
            'persona': persona_features, 
            'namespace': namespace_features,
            'theme': theme_features
        }
        
        for detector_name, feature_names in detector_configs.items():
            # Create a simple projection matrix (identity-like for now)
            matrix_size = len(feature_names)
            detector_matrix = np.eye(matrix_size) + 0.1 * np.random.random((matrix_size, matrix_size))
            detector_matrix = detector_matrix / np.linalg.norm(detector_matrix, axis=1, keepdims=True)
            
            detectors[detector_name] = POVMDetector(
                name=detector_name,
                measurement_matrix=detector_matrix,
                threshold=0.7,
                weight=1.0
            )
        
        return detectors
    
    def select_optimal_paragraphs(self, 
                                book_data: Dict, 
                                selection_budget: int = None) -> Tuple[List[Dict], List[ParagraphScore]]:
        """Select optimal paragraphs using POVM-based scoring"""
        
        if selection_budget is None:
            selection_budget = min(self.max_paragraphs, len(book_data['paragraphs']))
        
        print(f"Selecting {selection_budget} paragraphs from {len(book_data['paragraphs'])} candidates...")
        
        # Extract features for all paragraphs
        paragraph_features = []
        feature_vectors = []
        
        for para_data in book_data['paragraphs']:
            para_text = para_data['paragraph']['text']
            features = self.feature_extractor.extract_features(para_text)
            
            paragraph_features.append({
                'paragraph_data': para_data,
                'features': features,
                'text': para_text
            })
            
            # Flatten features for matrix operations
            feature_vector = self._flatten_features(features)
            feature_vectors.append(feature_vector)
        
        feature_matrix = np.array(feature_vectors)
        
        # Perform local SVD for mode analysis
        print("Computing local semantic modes...")
        local_modes = self._compute_local_modes(feature_matrix)
        
        # Calculate POVM detector responses
        print("Computing POVM detector responses...")
        detector_responses = self._compute_detector_responses(feature_matrix)
        
        # Score all paragraphs
        print("Scoring paragraphs...")
        paragraph_scores = []
        selected_indices = []
        
        for i, para_features in enumerate(paragraph_features):
            score = self._score_paragraph(
                i, para_features, feature_matrix, local_modes, 
                detector_responses, selected_indices
            )
            paragraph_scores.append(score)
        
        # Greedy selection with submodular objective
        print("Selecting optimal subset...")
        selected_paragraphs, selected_scores = self._greedy_selection(
            paragraph_features, paragraph_scores, selection_budget
        )
        
        return selected_paragraphs, selected_scores
    
    def _flatten_features(self, features: FeatureVector) -> np.ndarray:
        """Flatten feature vector for matrix operations"""
        
        all_features = {}
        all_features.update(features.prosody)
        all_features.update(features.syntax)
        all_features.update(features.discourse)
        all_features.update(features.persona_signature)
        all_features.update(features.namespace_signature)
        all_features.update(features.style_rhythm)
        
        # Ensure consistent ordering
        feature_names = sorted(all_features.keys())
        feature_vector = np.array([all_features.get(name, 0.0) for name in feature_names])
        
        # Handle NaN values
        feature_vector = np.nan_to_num(feature_vector, nan=0.0, posinf=1.0, neginf=0.0)
        
        return feature_vector
    
    def _compute_local_modes(self, feature_matrix: np.ndarray, n_components: int = 10) -> Dict[str, Any]:
        """Compute local semantic modes using SVD"""
        
        if feature_matrix.shape[0] < n_components:
            n_components = min(feature_matrix.shape[0] - 1, feature_matrix.shape[1])
        
        if n_components <= 0:
            return {'U': np.array([]), 'S': np.array([]), 'Vt': np.array([])}
        
        # Normalize features
        feature_mean = np.mean(feature_matrix, axis=0)
        feature_std = np.std(feature_matrix, axis=0)
        feature_std[feature_std == 0] = 1.0  # Avoid division by zero
        
        normalized_features = (feature_matrix - feature_mean) / feature_std
        
        # SVD for mode decomposition
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        U = svd.fit_transform(normalized_features)
        S = svd.singular_values_
        Vt = svd.components_
        
        return {
            'U': U,
            'S': S,
            'Vt': Vt,
            'feature_mean': feature_mean,
            'feature_std': feature_std,
            'explained_variance_ratio': svd.explained_variance_ratio_
        }
    
    def _compute_detector_responses(self, feature_matrix: np.ndarray) -> Dict[str, np.ndarray]:
        """Compute POVM detector responses for all paragraphs"""
        
        responses = {}
        
        for detector_name, detector in self.detectors.items():
            # Extract relevant features for this detector
            if detector_name == 'style':
                feature_indices = self._get_feature_indices(['avg_sentence_length', 'comma_density', 'rhythm_variety'])
            elif detector_name == 'persona':
                feature_indices = self._get_feature_indices(['first_person_pronoun_ratio', 'certainty_modality'])
            elif detector_name == 'namespace':
                feature_indices = self._get_feature_indices(['religious_field_density', 'archaic_temporal_density'])
            else:  # theme
                feature_indices = self._get_feature_indices(['causal_connective_density', 'evaluative_density'])
            
            # Extract features (or use first N features if indices not available)
            if feature_indices:
                relevant_features = feature_matrix[:, feature_indices]
            else:
                n_features = min(detector.measurement_matrix.shape[0], feature_matrix.shape[1])
                relevant_features = feature_matrix[:, :n_features]
            
            # Compute measurement (simplified POVM)
            if relevant_features.shape[1] > 0:
                # Project onto detector subspace
                projections = relevant_features @ detector.measurement_matrix[:relevant_features.shape[1], :relevant_features.shape[1]]
                response_strengths = np.linalg.norm(projections, axis=1)
                responses[detector_name] = response_strengths
            else:
                responses[detector_name] = np.zeros(feature_matrix.shape[0])
        
        return responses
    
    def _get_feature_indices(self, feature_names: List[str]) -> List[int]:
        """Get indices for specific feature names (simplified)"""
        # In a real implementation, this would map feature names to indices
        # For now, return empty list to use fallback behavior
        return []
    
    def _score_paragraph(self, 
                        paragraph_idx: int,
                        para_features: Dict,
                        feature_matrix: np.ndarray,
                        local_modes: Dict,
                        detector_responses: Dict,
                        selected_indices: List[int]) -> ParagraphScore:
        """Score a single paragraph using POVM framework"""
        
        # Resonance score (how strongly paragraph loads on local modes)
        resonance_score = self._calculate_resonance(paragraph_idx, local_modes)
        
        # Information gain (how much new info this adds vs. selected set)
        info_gain_score = self._calculate_info_gain(paragraph_idx, feature_matrix, selected_indices)
        
        # Redundancy penalty (similarity to already selected)
        redundancy_penalty = self._calculate_redundancy(paragraph_idx, feature_matrix, selected_indices)
        
        # Clarity score (single voice, clean syntax)
        clarity_score = self._calculate_clarity(para_features)
        
        # Essence strength (well-formed narrative content)
        essence_strength = self._calculate_essence_strength(para_features)
        
        # Combine scores
        total_score = (
            self.weights['resonance'] * resonance_score +
            self.weights['info_gain'] * info_gain_score -
            self.weights['redundancy'] * redundancy_penalty +
            self.weights['clarity'] * clarity_score +
            self.weights['essence'] * essence_strength
        )
        
        # Get detector responses
        detector_scores = {name: responses[paragraph_idx] for name, responses in detector_responses.items()}
        
        return ParagraphScore(
            paragraph_id=f"para_{paragraph_idx}",
            resonance_score=resonance_score,
            info_gain_score=info_gain_score,
            redundancy_penalty=redundancy_penalty,
            clarity_score=clarity_score,
            essence_strength=essence_strength,
            total_score=total_score,
            detector_responses=detector_scores,
            local_modes={'paragraph_idx': paragraph_idx}
        )
    
    def _calculate_resonance(self, paragraph_idx: int, local_modes: Dict) -> float:
        """Calculate how strongly paragraph resonates with local modes"""
        
        if 'U' not in local_modes or local_modes['U'].size == 0:
            return 0.5  # Default resonance
        
        U = local_modes['U']
        if paragraph_idx >= U.shape[0]:
            return 0.5
        
        # Take norm of top-k mode loadings
        top_k = min(3, U.shape[1])
        mode_loadings = U[paragraph_idx, :top_k]
        resonance = np.linalg.norm(mode_loadings)
        
        return min(resonance, 1.0)  # Clamp to [0, 1]
    
    def _calculate_info_gain(self, paragraph_idx: int, feature_matrix: np.ndarray, selected_indices: List[int]) -> float:
        """Calculate information gain from adding this paragraph"""
        
        if not selected_indices:
            return 1.0  # First paragraph has maximum info gain
        
        current_features = feature_matrix[paragraph_idx]
        selected_features = feature_matrix[selected_indices]
        
        # Calculate distance to selected set centroid
        centroid = np.mean(selected_features, axis=0)
        distance_to_centroid = euclidean_distances([current_features], [centroid])[0, 0]
        
        # Normalize to [0, 1] range
        max_distance = np.sqrt(feature_matrix.shape[1])  # Theoretical maximum
        info_gain = min(distance_to_centroid / max_distance, 1.0)
        
        return info_gain
    
    def _calculate_redundancy(self, paragraph_idx: int, feature_matrix: np.ndarray, selected_indices: List[int]) -> float:
        """Calculate redundancy penalty"""
        
        if not selected_indices:
            return 0.0  # No redundancy for first paragraph
        
        current_features = feature_matrix[paragraph_idx]
        selected_features = feature_matrix[selected_indices]
        
        # Find maximum similarity to any selected paragraph
        similarities = cosine_similarity([current_features], selected_features)[0]
        max_similarity = np.max(similarities)
        
        return max_similarity
    
    def _calculate_clarity(self, para_features: Dict) -> float:
        """Calculate clarity score (single voice, clean syntax)"""
        
        features = para_features['features']
        
        # Favor clear syntax and moderate complexity
        clarity_factors = []
        
        # Sentence length should be moderate
        avg_sent_len = features.prosody.get('avg_sentence_length', 15)
        len_score = 1.0 - abs(avg_sent_len - 15) / 30  # Penalize very short or very long
        clarity_factors.append(max(len_score, 0))
        
        # Low syntactic complexity for clarity
        subordination = features.syntax.get('subordination_ratio', 0)
        subordination_score = 1.0 - min(subordination, 1.0)
        clarity_factors.append(subordination_score)
        
        # Moderate punctuation complexity
        punct_entropy = features.prosody.get('punct_entropy', 0)
        punct_score = 1.0 - min(punct_entropy / 3.0, 1.0)  # Normalize entropy
        clarity_factors.append(punct_score)
        
        return np.mean(clarity_factors)
    
    def _calculate_essence_strength(self, para_features: Dict) -> float:
        """Calculate essence strength (narrative content quality)"""
        
        features = para_features['features']
        text = para_features['text']
        
        strength_factors = []
        
        # Length factor (not too short, not too long)
        word_count = len(text.split())
        length_score = min(word_count / 50.0, 1.0) if word_count < 50 else max(1.0 - (word_count - 100) / 200.0, 0.3)
        strength_factors.append(length_score)
        
        # Narrative content (presence of events, agents)
        # This is simplified - would use proper SRL in full implementation
        narrative_markers = ['said', 'went', 'came', 'saw', 'felt', 'thought', 'knew', 'found']
        narrative_density = sum(text.lower().count(marker) for marker in narrative_markers) / word_count if word_count else 0
        narrative_score = min(narrative_density * 10, 1.0)  # Scale appropriately
        strength_factors.append(narrative_score)
        
        # Emotional content
        evaluative_density = features.persona_signature.get('evaluative_density', 0)
        emotion_score = min(evaluative_density * 20, 1.0)
        strength_factors.append(emotion_score)
        
        return np.mean(strength_factors)
    
    def _greedy_selection(self, 
                         paragraph_features: List[Dict],
                         paragraph_scores: List[ParagraphScore],
                         budget: int) -> Tuple[List[Dict], List[ParagraphScore]]:
        """Greedy selection with submodular objective"""
        
        selected_paragraphs = []
        selected_scores = []
        selected_indices = []
        remaining_indices = list(range(len(paragraph_features)))
        
        for selection_round in range(budget):
            if not remaining_indices:
                break
            
            best_score = -float('inf')
            best_idx = None
            best_para_idx = None
            
            # Evaluate each remaining paragraph
            for i, para_idx in enumerate(remaining_indices):
                # Recalculate score considering current selection
                updated_score = self._score_paragraph(
                    para_idx, 
                    paragraph_features[para_idx],
                    np.array([self._flatten_features(pf['features']) for pf in paragraph_features]),
                    {},  # Local modes would be recomputed
                    {},  # Detector responses would be recomputed  
                    selected_indices
                )
                
                if updated_score.total_score > best_score:
                    best_score = updated_score.total_score
                    best_idx = i
                    best_para_idx = para_idx
            
            if best_idx is not None:
                selected_paragraphs.append(paragraph_features[best_para_idx])
                selected_scores.append(paragraph_scores[best_para_idx])
                selected_indices.append(best_para_idx)
                remaining_indices.pop(best_idx)
        
        print(f"Selected {len(selected_paragraphs)} paragraphs with average score: {np.mean([s.total_score for s in selected_scores]):.3f}")
        
        return selected_paragraphs, selected_scores


def main():
    """CLI for testing paragraph selection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POVM Paragraph Selection')
    parser.add_argument('--input', required=True, help='Input anchored book JSON file')
    parser.add_argument('--budget', type=int, default=50, help='Maximum paragraphs to select')
    parser.add_argument('--output', help='Output file for selected paragraphs')
    
    args = parser.parse_args()
    
    # Load book data
    with open(args.input, 'r') as f:
        book_data = json.load(f)
    
    # Select paragraphs
    selector = POVMParagraphSelector(max_paragraphs=args.budget)
    selected_paragraphs, scores = selector.select_optimal_paragraphs(book_data, args.budget)
    
    # Output results
    result = {
        'book_id': book_data.get('book_id'),
        'selection_budget': args.budget,
        'selected_count': len(selected_paragraphs),
        'selected_paragraphs': selected_paragraphs,
        'scores': [
            {
                'paragraph_id': score.paragraph_id,
                'total_score': score.total_score,
                'resonance': score.resonance_score,
                'info_gain': score.info_gain_score,
                'redundancy_penalty': score.redundancy_penalty,
                'clarity': score.clarity_score,
                'essence_strength': score.essence_strength,
                'detector_responses': score.detector_responses
            }
            for score in scores
        ]
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Selected paragraphs saved to {args.output}")
    else:
        print(f"Selected {len(selected_paragraphs)} paragraphs")
        for i, score in enumerate(scores[:5]):  # Show top 5
            print(f"  {i+1}. Score: {score.total_score:.3f} - {selected_paragraphs[i]['paragraph']['text'][:100]}...")


if __name__ == "__main__":
    main()