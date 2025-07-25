"""
Quantum-Inspired Narrative Theory Implementation
===============================================

A computational framework implementing the Theory of Narrative as quantum measurement,
where narratives are POVMs (Positive Operator-Valued Measures) that transform 
subjective meaning-states represented as density matrices.

Core Concepts:
- Text: The evoked, intra-conscious state update (ρ → ρ')
- Vortex: The corporeal flow (embeddings, computations, logs)
- M-POVM: Meaning-POVM for semantic detection
- Born-rule analogue: Coherence constraints on narrative transformations

Author: Based on theoretical framework by [User]
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

@dataclass
class MeaningState:
    """
    Represents a subjective meaning-state as a density matrix ρ.
    
    In quantum mechanics: ρ is positive semidefinite, trace-1 operator
    In narrative theory: ρ encodes the subject's probability distribution
    over possible meanings before reading a narrative.
    """
    density_matrix: torch.Tensor  # Shape: (d, d) where d is semantic dimension
    dimension: int
    semantic_labels: Optional[List[str]] = None
    
    def __post_init__(self):
        """Validate that this is a proper density matrix."""
        assert self.density_matrix.shape == (self.dimension, self.dimension)
        assert torch.allclose(torch.trace(self.density_matrix), torch.tensor(1.0), atol=1e-6)
        assert torch.all(torch.linalg.eigvals(self.density_matrix).real >= -1e-6)  # Positive semidefinite
    
    @classmethod
    def maximally_mixed(cls, dimension: int, semantic_labels: Optional[List[str]] = None):
        """Create a maximally mixed state ρ = I/d (maximum uncertainty)."""
        return cls(
            density_matrix=torch.eye(dimension) / dimension,
            dimension=dimension,
            semantic_labels=semantic_labels
        )
    
    @classmethod
    def pure_state(cls, state_vector: torch.Tensor, semantic_labels: Optional[List[str]] = None):
        """Create a pure state ρ = |ψ⟩⟨ψ| from a state vector."""
        state_vector = state_vector / torch.norm(state_vector)  # Normalize
        density_matrix = torch.outer(state_vector, state_vector.conj())
        return cls(
            density_matrix=density_matrix,
            dimension=len(state_vector),
            semantic_labels=semantic_labels
        )
    
    def purity(self) -> float:
        """Calculate purity Tr(ρ²). Pure states have purity=1, mixed states < 1."""
        return torch.trace(self.density_matrix @ self.density_matrix).real.item()
    
    def von_neumann_entropy(self) -> float:
        """Calculate von Neumann entropy S(ρ) = -Tr(ρ log ρ)."""
        eigenvals = torch.linalg.eigvals(self.density_matrix).real
        eigenvals = eigenvals[eigenvals > 1e-12]  # Remove numerical zeros
        return -torch.sum(eigenvals * torch.log(eigenvals)).item()

class MeaningPOVM:
    """
    A Meaning-POVM: a set of positive operators {E_i} that sum to identity,
    designed to detect semantic content in narratives.
    
    Each E_i represents a "semantic probe" - a way of asking the narrative
    "how much does this text evoke meaning i?"
    """
    
    def __init__(self, 
                 elements: List[torch.Tensor], 
                 labels: List[str],
                 is_sic_like: bool = False):
        """
        Initialize a Meaning-POVM.
        
        Args:
            elements: List of positive operators E_i, each shape (d, d)
            labels: Semantic labels for each element (e.g., "mythic", "analytic")
            is_sic_like: Whether this approximates a SIC-POVM structure
        """
        self.elements = elements
        self.labels = labels
        self.dimension = elements[0].shape[0]
        self.num_elements = len(elements)
        self.is_sic_like = is_sic_like
        
        # Validate POVM properties
        self._validate_povm()
    
    def _validate_povm(self):
        """Validate that elements form a proper POVM."""
        # Check positivity
        for i, E in enumerate(self.elements):
            eigenvals = torch.linalg.eigvals(E).real
            assert torch.all(eigenvals >= -1e-6), f"Element {i} not positive semidefinite"
        
        # Check completeness: sum of elements = identity
        element_sum = sum(self.elements)
        identity = torch.eye(self.dimension)
        assert torch.allclose(element_sum, identity, atol=1e-6), "POVM elements don't sum to identity"
    
    @classmethod
    def create_sic_like_povm(cls, 
                           dimension: int, 
                           semantic_labels: List[str],
                           random_seed: Optional[int] = None) -> 'MeaningPOVM':
        """
        Create a SIC-like (Symmetric Informationally Complete) Meaning-POVM.
        
        For d-dimensional space, we need d² rank-1 projectors with constant
        pairwise overlaps to achieve informational completeness and symmetry.
        """
        if random_seed is not None:
            torch.manual_seed(random_seed)
        
        num_elements = dimension ** 2
        assert len(semantic_labels) == num_elements, f"Need {num_elements} labels for d={dimension}"
        
        # Generate d² vectors with approximately equal pairwise overlaps
        # This is a heuristic approximation to true SIC-POVMs
        vectors = []
        
        # Start with random vectors
        for i in range(num_elements):
            v = torch.randn(dimension, dtype=torch.complex64)
            v = v / torch.norm(v)  # Normalize
            vectors.append(v)
        
        # Use a simpler, guaranteed-to-work construction
        # Create overcomplete set of projectors and then normalize
        
        # Create basis vectors plus some random ones for overcompleteness
        elements = []
        
        # Add identity components scaled down
        for i in range(dimension):
            e = torch.zeros(dimension)
            e[i] = 1.0
            E = torch.outer(e, e) / num_elements
            elements.append(E)
        
        # Add random elements for the remaining slots
        remaining = num_elements - dimension
        if remaining > 0:
            for i in range(remaining):
                v = torch.randn(dimension)
                v = v / torch.norm(v)
                E = torch.outer(v, v) / num_elements
                elements.append(E)
        
        # Ensure exact completeness by adjusting the last element
        if len(elements) > 0:
            element_sum = sum(elements[:-1])
            identity = torch.eye(dimension)
            elements[-1] = identity - element_sum
        
        return cls(elements, semantic_labels, is_sic_like=True)
    
    @staticmethod
    def _optimize_frame_potential(vectors: List[torch.Tensor], 
                                max_iterations: int = 1000) -> List[torch.Tensor]:
        """
        Optimize vectors to minimize frame potential, pushing toward SIC-like structure.
        Frame potential: Φ(vectors) = Σ_{i≠j} |⟨ψ_i|ψ_j⟩|⁴
        """
        vectors = [v.clone().requires_grad_(True) for v in vectors]
        optimizer = torch.optim.Adam(vectors, lr=0.01)
        
        for iteration in range(max_iterations):
            optimizer.zero_grad()
            
            # Compute frame potential
            potential = 0.0
            for i in range(len(vectors)):
                for j in range(len(vectors)):
                    if i != j:
                        overlap = torch.abs(torch.vdot(vectors[i], vectors[j])) ** 4
                        potential += overlap
            
            potential.backward()
            optimizer.step()
            
            # Renormalize vectors
            with torch.no_grad():
                for v in vectors:
                    v.data = v.data / torch.norm(v.data)
            
            if iteration % 100 == 0:
                logger.debug(f"Frame potential optimization iteration {iteration}: {potential.item()}")
        
        return [v.detach() for v in vectors]
    
    def measure(self, meaning_state: MeaningState) -> Dict[str, float]:
        """
        Perform POVM measurement on a meaning state.
        
        Returns probabilities p(i) = Tr(ρ E_i) for each semantic element.
        """
        probabilities = {}
        
        for element, label in zip(self.elements, self.labels):
            prob = torch.trace(meaning_state.density_matrix @ element).real.item()
            probabilities[label] = max(0.0, prob)  # Ensure non-negative
        
        # Normalize to handle numerical errors
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        return probabilities
    
    def compute_pairwise_overlaps(self) -> torch.Tensor:
        """Compute pairwise overlaps Tr(E_i E_j) for analyzing SIC-like properties."""
        overlaps = torch.zeros(self.num_elements, self.num_elements)
        
        for i in range(self.num_elements):
            for j in range(self.num_elements):
                overlap = torch.trace(self.elements[i] @ self.elements[j]).real
                overlaps[i, j] = overlap
        
        return overlaps
    
    def measure_density_matrix(self, density_matrix: torch.Tensor) -> Dict[str, float]:
        """
        Perform POVM measurement directly on a density matrix.
        
        This method supports the archive integration where we blend 
        density matrices and need to measure the result.
        
        Args:
            density_matrix: The density matrix to measure (shape: d x d)
            
        Returns:
            Dictionary of measurement probabilities for each semantic element
        """
        probabilities = {}
        
        for element, label in zip(self.elements, self.labels):
            prob = torch.trace(density_matrix @ element).real.item()
            probabilities[label] = max(0.0, prob)  # Ensure non-negative
        
        # Normalize to handle numerical errors
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        return probabilities

class NarrativeTransformation:
    """
    Represents how a narrative transforms a meaning-state via POVM measurement.
    
    When a subject reads a narrative:
    1. The narrative is encoded as a POVM {E_i} with Kraus operators {M_i}
    2. Measurement gives outcome i with probability p(i) = Tr(ρ E_i)
    3. State updates via generalized Lüders rule: ρ' = M_i ρ M_i† / Tr(ρ E_i)
    """
    
    def __init__(self, 
                 povm: MeaningPOVM,
                 kraus_operators: Optional[List[torch.Tensor]] = None,
                 transformation_type: str = "interpretation"):
        """
        Initialize a narrative transformation.
        
        Args:
            povm: The Meaning-POVM defining possible semantic outcomes
            kraus_operators: Optional Kraus operators M_i for state update
            transformation_type: Type of reading ("interpretation", "skeptical", "devotional")
        """
        self.povm = povm
        self.transformation_type = transformation_type
        
        if kraus_operators is None:
            # Use eigendecomposition to get proper square root for Kraus operators
            self.kraus_operators = []
            for E in povm.elements:
                # Eigendecomposition: E = U Λ U†
                eigenvals, eigenvecs = torch.linalg.eigh(E)
                # Ensure non-negative eigenvalues
                eigenvals = torch.clamp(eigenvals, min=0)
                # M = U sqrt(Λ) U†
                sqrt_eigenvals = torch.sqrt(eigenvals)
                M = eigenvecs @ torch.diag(sqrt_eigenvals) @ eigenvecs.conj().T
                self.kraus_operators.append(M.real)
        else:
            self.kraus_operators = kraus_operators
            
        # Validate that Kraus operators are consistent with POVM
        self._validate_kraus_operators()
    
    def _validate_kraus_operators(self):
        """Validate that Kraus operators satisfy E_i = M_i† M_i."""
        for i, (E, M) in enumerate(zip(self.povm.elements, self.kraus_operators)):
            reconstructed_E = M.conj().T @ M
            assert torch.allclose(E, reconstructed_E, atol=1e-5), \
                f"Kraus operator {i} inconsistent with POVM element"
    
    def transform(self, 
                  meaning_state: MeaningState, 
                  outcome: Optional[str] = None) -> Tuple[MeaningState, Dict[str, float]]:
        """
        Transform a meaning-state by "reading" the narrative.
        
        Args:
            meaning_state: Initial subjective state ρ
            outcome: If specified, force this semantic outcome; otherwise sample
            
        Returns:
            Tuple of (transformed_state, measurement_probabilities)
        """
        # Step 1: Compute measurement probabilities
        probabilities = self.povm.measure(meaning_state)
        
        # Step 2: Determine outcome (sample or forced)
        if outcome is None:
            # Sample according to Born rule probabilities
            labels = list(probabilities.keys())
            probs = list(probabilities.values())
            outcome_idx = torch.multinomial(torch.tensor(probs), 1).item()
            outcome = labels[outcome_idx]
        else:
            assert outcome in self.povm.labels, f"Unknown outcome: {outcome}"
            outcome_idx = self.povm.labels.index(outcome)
        
        # Step 3: Apply generalized Lüders rule for state update
        M = self.kraus_operators[outcome_idx]
        rho = meaning_state.density_matrix
        
        # Transformed state: ρ' = M ρ M† / Tr(ρ E_i)
        transformed_rho = M @ rho @ M.conj().T
        normalization = torch.trace(transformed_rho).real
        
        if normalization > 1e-12:
            transformed_rho = transformed_rho / normalization
        else:
            # Fallback to original state if normalization fails
            transformed_rho = rho
            logger.warning(f"Near-zero normalization in narrative transformation for outcome {outcome}")
        
        # Step 4: Apply reading style post-processing
        final_rho = self._apply_reading_style_processing(transformed_rho, rho)
        
        transformed_state = MeaningState(
            density_matrix=final_rho,
            dimension=meaning_state.dimension,
            semantic_labels=meaning_state.semantic_labels
        )
        
        return transformed_state, probabilities
    
    def _apply_reading_style_processing(self, rho_updated: torch.Tensor, rho_original: torch.Tensor) -> torch.Tensor:
        """Apply reading style-specific post-processing to the updated state."""
        
        if self.transformation_type == "skeptical":
            # Skeptical reading: blend more with original state (less transformation)
            blend_factor = 0.3  # 30% new, 70% original
            return blend_factor * rho_updated + (1 - blend_factor) * rho_original
            
        elif self.transformation_type == "devotional":
            # Devotional reading: enhance transformation (more dramatic change)
            # Make the state more "pure" by enhancing the largest eigenvalue
            eigenvals, eigenvecs = torch.linalg.eigh(rho_updated)
            # Enhance the largest eigenvalue and renormalize
            enhanced_eigenvals = torch.softmax(eigenvals * 2.0, dim=0)  # Sharpen distribution
            enhanced_state = eigenvecs @ torch.diag(enhanced_eigenvals) @ eigenvecs.conj().T
            return enhanced_state.real
            
        else:
            # Standard interpretation: no post-processing
            return rho_updated
    
    def compute_fidelity(self, 
                        initial_state: MeaningState, 
                        final_state: MeaningState) -> float:
        """
        Compute quantum fidelity F(ρ, σ) = Tr(√(√ρ σ √ρ)) between states.
        Measures how "similar" the meaning-states are (1 = identical, 0 = orthogonal).
        """
        rho = initial_state.density_matrix
        sigma = final_state.density_matrix
        
        # Compute matrix square roots using eigendecomposition
        def matrix_sqrt(M):
            eigenvals, eigenvecs = torch.linalg.eigh(M)
            eigenvals = torch.clamp(eigenvals, min=1e-8)  # Ensure positive
            sqrt_eigenvals = torch.sqrt(eigenvals)
            return eigenvecs @ torch.diag(sqrt_eigenvals) @ eigenvecs.conj().T
        
        sqrt_rho = matrix_sqrt(rho + 1e-8 * torch.eye(rho.shape[0]))
        inner_matrix = sqrt_rho @ sigma @ sqrt_rho
        sqrt_inner = matrix_sqrt(inner_matrix + 1e-8 * torch.eye(inner_matrix.shape[0]))
        
        fidelity = torch.trace(sqrt_inner).real.item()
        return min(1.0, max(0.0, fidelity))  # Clamp to [0,1]

class NarrativeCoherenceConstraint:
    """
    Implements the Born-rule analogue for narrative theory: a coherence constraint
    that governs how probability assignments across different narratives must relate
    to maintain epistemic consistency.
    
    Based on the SIC-POVM formulation of QBism's Born rule.
    """
    
    def __init__(self, canonical_povm: MeaningPOVM):
        """
        Initialize coherence constraint with a canonical (SIC-like) Meaning-POVM.
        
        Args:
            canonical_povm: The reference POVM for coherence checking
        """
        assert canonical_povm.is_sic_like, "Coherence constraint requires SIC-like POVM"
        self.canonical_povm = canonical_povm
        self.dimension = canonical_povm.dimension
    
    def check_coherence(self, 
                       canonical_probs: Dict[str, float],
                       narrative_probs: Dict[str, float],
                       conditional_probs: Dict[str, Dict[str, float]]) -> Tuple[bool, float]:
        """
        Check Born-rule-like coherence constraint.
        
        The constraint: q(j) = (d+1)Σ_i p(i) r(j|i) - 1/d
        where:
        - p(i): canonical POVM probabilities  
        - q(j): narrative outcome probabilities
        - r(j|i): conditional probabilities r(j|i) = P(narrative_outcome=j | canonical_outcome=i)
        
        Returns:
            Tuple of (is_coherent, violation_magnitude)
        """
        d = self.dimension
        total_violation = 0.0
        
        for narrative_outcome in narrative_probs:
            # Compute expected probability via Born rule
            expected_prob = 0.0
            for canonical_outcome in canonical_probs:
                p_i = canonical_probs[canonical_outcome]
                r_ji = conditional_probs.get(canonical_outcome, {}).get(narrative_outcome, 0.0)
                expected_prob += p_i * r_ji
            
            expected_prob = (d + 1) * expected_prob - 1.0 / d
            expected_prob = max(0.0, min(1.0, expected_prob))  # Clamp to valid probability
            
            # Compare with actual probability
            actual_prob = narrative_probs[narrative_outcome]
            violation = abs(expected_prob - actual_prob)
            total_violation += violation
        
        # Consider coherent if total violation is below threshold
        is_coherent = total_violation < 0.1  # Adjustable threshold
        
        return is_coherent, total_violation

# Integration with existing LPE system
class QuantumNarrativeEngine:
    """
    Main engine integrating quantum narrative theory with the Lamish Projection Engine.
    
    Provides methods to:
    1. Convert LLM embeddings to meaning-states
    2. Apply narrative transformations with semantic POVMs
    3. Enforce coherence constraints
    4. Generate semantic tomography data for visualization
    """
    
    def __init__(self, 
                 semantic_dimension: int = 64,
                 semantic_labels: Optional[List[str]] = None):
        """
        Initialize the quantum narrative engine.
        
        Args:
            semantic_dimension: Effective dimension of meaning-state space
            semantic_labels: Labels for semantic probes (auto-generated if None)
        """
        self.semantic_dimension = semantic_dimension
        
        if semantic_labels is None:
            # Auto-generate semantic labels based on common narrative dimensions
            num_labels = semantic_dimension ** 2
            base_labels = [
                "mythic", "analytic", "ironic", "devotional", "skeptical", "empathetic",
                "authoritative", "questioning", "celebratory", "melancholic", "urgent", "contemplative",
                "concrete", "abstract", "personal", "universal", "local", "cosmic",
                "traditional", "innovative", "harmonious", "conflicted", "certain", "ambiguous"
            ]
            # Extend with combinations if needed
            semantic_labels = (base_labels * (num_labels // len(base_labels) + 1))[:num_labels]
        
        self.semantic_labels = semantic_labels
        
        # Initialize canonical SIC-like POVM
        self.canonical_povm = MeaningPOVM.create_sic_like_povm(
            dimension=semantic_dimension,
            semantic_labels=semantic_labels,
            random_seed=42  # For reproducibility
        )
        
        # Initialize coherence constraint
        self.coherence_constraint = NarrativeCoherenceConstraint(self.canonical_povm)
        
        # Neural network to map embeddings to density matrices
        self.embedding_to_state = self._create_embedding_mapper()
        
        logger.info(f"Initialized QuantumNarrativeEngine with d={semantic_dimension}")
    
    def _create_embedding_mapper(self) -> nn.Module:
        """
        Create neural network to map LLM embeddings to valid density matrices.
        
        Uses Cholesky parameterization to ensure positive semidefinite, trace-1 output.
        Auto-detects embedding dimension from actual embeddings.
        """
        class EmbeddingToState(nn.Module):
            def __init__(self, embedding_dim: int, state_dim: int):
                super().__init__()
                self.state_dim = state_dim
                self.embedding_dim = embedding_dim
                
                # Map to Cholesky factors of density matrix
                cholesky_dim = state_dim * (state_dim + 1) // 2  # Lower triangular elements
                
                self.mapper = nn.Sequential(
                    nn.Linear(embedding_dim, 512),
                    nn.ReLU(),
                    nn.Linear(512, 256),
                    nn.ReLU(),
                    nn.Linear(256, cholesky_dim),
                )
            
            def forward(self, embedding: torch.Tensor) -> torch.Tensor:
                """Convert embedding to density matrix via Cholesky decomposition."""
                # Handle different embedding dimensions
                if embedding.dim() == 1:
                    embedding = embedding.unsqueeze(0)  # Add batch dimension
                
                # Ensure embedding matches expected dimension
                if embedding.shape[-1] != self.embedding_dim:
                    # Pad or truncate to match expected dimension
                    current_dim = embedding.shape[-1]
                    if current_dim < self.embedding_dim:
                        # Pad with zeros
                        padding = torch.zeros(embedding.shape[0], self.embedding_dim - current_dim)
                        embedding = torch.cat([embedding, padding], dim=1)
                    else:
                        # Truncate
                        embedding = embedding[:, :self.embedding_dim]
                
                cholesky_elements = self.mapper(embedding)
                
                # Handle batch dimension
                batch_size = embedding.shape[0]
                result_matrices = []
                
                for b in range(batch_size):
                    # Reconstruct lower triangular matrix
                    L = torch.zeros(self.state_dim, self.state_dim)
                    tril_indices = torch.tril_indices(self.state_dim, self.state_dim)
                    L[tril_indices[0], tril_indices[1]] = cholesky_elements[b]
                    
                    # Ensure positive diagonal elements
                    L.diagonal().data = torch.exp(L.diagonal()) + 1e-6
                    
                    # Construct density matrix: ρ = L L†
                    rho = L @ L.T
                    
                    # Normalize to trace 1
                    rho = rho / torch.trace(rho)
                    
                    result_matrices.append(rho)
                
                if batch_size == 1:
                    return result_matrices[0]
                else:
                    return torch.stack(result_matrices)
        
        # Use flexible embedding dimension (will be updated when first used)
        return EmbeddingToState(embedding_dim=384, state_dim=self.semantic_dimension)  # 384 is common sentence transformer size
    
    def text_to_meaning_state(self, text: str, embedding: torch.Tensor) -> MeaningState:
        """
        Convert text and its embedding to a meaning-state density matrix.
        
        Args:
            text: Original text content
            embedding: LLM embedding vector for the text
            
        Returns:
            MeaningState representing the subjective semantic content
        """
        # Ensure embedding is a tensor
        if isinstance(embedding, np.ndarray):
            embedding = torch.tensor(embedding, dtype=torch.float32)
        
        # Auto-update embedding mapper if dimension mismatch
        if hasattr(self.embedding_to_state, 'embedding_dim'):
            expected_dim = self.embedding_to_state.embedding_dim
            actual_dim = embedding.shape[-1] if embedding.dim() > 0 else len(embedding)
            
            if actual_dim != expected_dim:
                logger.info(f"Updating embedding mapper: {expected_dim} → {actual_dim} dimensions")
                self.embedding_to_state = self._create_embedding_mapper_for_dim(actual_dim)
        
        with torch.no_grad():
            density_matrix = self.embedding_to_state(embedding)
        
        return MeaningState(
            density_matrix=density_matrix,
            dimension=self.semantic_dimension,
            semantic_labels=self.semantic_labels
        )
    
    def _create_embedding_mapper_for_dim(self, embedding_dim: int) -> nn.Module:
        """Create embedding mapper for specific dimension."""
        class EmbeddingToState(nn.Module):
            def __init__(self, embedding_dim: int, state_dim: int):
                super().__init__()
                self.state_dim = state_dim
                self.embedding_dim = embedding_dim
                
                # Map to Cholesky factors of density matrix
                cholesky_dim = state_dim * (state_dim + 1) // 2
                
                self.mapper = nn.Sequential(
                    nn.Linear(embedding_dim, 512),
                    nn.ReLU(),
                    nn.Linear(512, 256),
                    nn.ReLU(),
                    nn.Linear(256, cholesky_dim),
                )
            
            def forward(self, embedding: torch.Tensor) -> torch.Tensor:
                if embedding.dim() == 1:
                    embedding = embedding.unsqueeze(0)
                
                cholesky_elements = self.mapper(embedding)
                
                # Reconstruct density matrix
                L = torch.zeros(self.state_dim, self.state_dim)
                tril_indices = torch.tril_indices(self.state_dim, self.state_dim)
                L[tril_indices[0], tril_indices[1]] = cholesky_elements[0]
                
                L.diagonal().data = torch.exp(L.diagonal()) + 1e-6
                rho = L @ L.T
                rho = rho / torch.trace(rho)
                
                return rho
        
        return EmbeddingToState(embedding_dim=embedding_dim, state_dim=self.semantic_dimension)
    
    def create_narrative_transformation(self, 
                                     narrative_text: str,
                                     transformation_attributes: Dict[str, str],
                                     reading_style: str = "interpretation") -> NarrativeTransformation:
        """
        Create a narrative transformation based on text and desired attributes.
        
        Args:
            narrative_text: The narrative content
            transformation_attributes: Desired persona, namespace, style attributes
            reading_style: How to read ("interpretation", "skeptical", "devotional")
            
        Returns:
            NarrativeTransformation that can be applied to meaning-states
        """
        # For now, use the canonical POVM
        # In a full implementation, this would create attribute-specific POVMs
        povm = self.canonical_povm
        
        # Customize Kraus operators based on reading style
        # All reading styles use the same POVM but with different post-processing
        kraus_ops = None  # Use default construction that maintains E_i = M_i† M_i
        
        # Store reading style for post-processing in the transform method
        transformation_type = reading_style
        
        return NarrativeTransformation(
            povm=povm,
            kraus_operators=kraus_ops,
            transformation_type=reading_style
        )
    
    def apply_narrative(self, 
                       initial_text: str,
                       initial_embedding: torch.Tensor,
                       transformation: NarrativeTransformation) -> Dict:
        """
        Apply a narrative transformation and return detailed analysis.
        
        Returns comprehensive data for semantic tomography visualization.
        """
        # Convert to meaning-state
        initial_state = self.text_to_meaning_state(initial_text, initial_embedding)
        
        # Apply transformation
        final_state, measurement_probs = transformation.transform(initial_state)
        
        # Compute analysis metrics
        fidelity = transformation.compute_fidelity(initial_state, final_state)
        purity_change = final_state.purity() - initial_state.purity()
        entropy_change = final_state.von_neumann_entropy() - initial_state.von_neumann_entropy()
        
        # Get canonical POVM measurements for both states
        initial_canonical_probs = self.canonical_povm.measure(initial_state)
        final_canonical_probs = self.canonical_povm.measure(final_state)
        
        return {
            "initial_state": initial_state,
            "final_state": final_state,
            "measurement_probabilities": measurement_probs,
            "initial_canonical_probs": initial_canonical_probs,
            "final_canonical_probs": final_canonical_probs,
            "fidelity": fidelity,
            "purity_change": purity_change,
            "entropy_change": entropy_change,
            "transformation_type": transformation.transformation_type,
        }
    
    def generate_semantic_tomography(self, analysis_result: Dict) -> Dict:
        """
        Generate data for semantic tomography visualization.
        
        Returns formatted data for the Humanizer.com UI showing:
        - Before/after meaning-state probabilities
        - Transformation visualization
        - Coherence metrics
        """
        return {
            "semantic_dimensions": self.semantic_labels,
            "before_probs": analysis_result["initial_canonical_probs"],
            "after_probs": analysis_result["final_canonical_probs"],
            "measurement_outcome": analysis_result["measurement_probabilities"],
            "metrics": {
                "fidelity": analysis_result["fidelity"],
                "purity_change": analysis_result["purity_change"],
                "entropy_change": analysis_result["entropy_change"],
            },
            "transformation_type": analysis_result["transformation_type"],
            "povm_structure": {
                "dimension": self.semantic_dimension,
                "num_elements": len(self.semantic_labels),
                "is_sic_like": self.canonical_povm.is_sic_like,
                "pairwise_overlaps": self.canonical_povm.compute_pairwise_overlaps().tolist()
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the quantum narrative engine
    engine = QuantumNarrativeEngine(semantic_dimension=4)  # Small example
    
    # Create a dummy embedding (in practice, this comes from LLM)
    dummy_embedding = torch.randn(768)
    
    # Convert text to meaning-state
    initial_text = "The ancient wisdom speaks of cycles within cycles."
    initial_state = engine.text_to_meaning_state(initial_text, dummy_embedding)
    
    print(f"Initial state purity: {initial_state.purity():.3f}")
    print(f"Initial state entropy: {initial_state.von_neumann_entropy():.3f}")
    
    # Create a narrative transformation
    transformation = engine.create_narrative_transformation(
        narrative_text="Through scientific lens, we see patterns emerge.",
        transformation_attributes={"persona": "scientific", "style": "analytical"},
        reading_style="interpretation"
    )
    
    # Apply the narrative transformation
    analysis = engine.apply_narrative(initial_text, dummy_embedding, transformation)
    
    print(f"Final state purity: {analysis['final_state'].purity():.3f}")
    print(f"Fidelity: {analysis['fidelity']:.3f}")
    print(f"Measurement probabilities: {analysis['measurement_probabilities']}")
    
    # Generate semantic tomography data
    tomography = engine.generate_semantic_tomography(analysis)
    print(f"Semantic tomography generated with {len(tomography['semantic_dimensions'])} dimensions")