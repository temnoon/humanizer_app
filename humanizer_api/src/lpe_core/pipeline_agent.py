"""Pipeline orchestration agent for LPE transformations.

This agent manages the data flow between transformation steps and ensures
each step receives properly formatted input and produces valid output.
"""
import logging
import json
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class StepValidation:
    """Result of validating a pipeline step."""
    is_valid: bool
    error_message: Optional[str] = None
    suggested_input: Optional[str] = None
    output_format: Optional[str] = None

class PipelineAgent:
    """Orchestrates and validates the LPE transformation pipeline."""
    
    def __init__(self, persona: str, namespace: str, style: str):
        self.persona = persona
        self.namespace = namespace
        self.style = style
        
    def validate_step_output(self, step_type: str, input_text: str, output_text: str) -> StepValidation:
        """Validate that a step produced appropriate output for the next step."""
        
        if step_type == "deconstruct":
            return self._validate_deconstruct_output(output_text)
        elif step_type == "map":
            return self._validate_map_output(output_text)
        elif step_type == "reconstruct":
            return self._validate_reconstruct_output(output_text)
        elif step_type == "stylize":
            return self._validate_stylize_output(output_text)
        elif step_type == "reflect":
            return self._validate_reflect_output(output_text)
        
        return StepValidation(is_valid=True)
    
    def _validate_deconstruct_output(self, output: str) -> StepValidation:
        """Validate deconstruct step produces structured elements."""
        required_elements = ["WHO", "WHAT", "WHY", "HOW", "OUTCOME"]
        
        # Check if output contains the required structure
        found_elements = []
        for element in required_elements:
            if element in output.upper():
                found_elements.append(element)
        
        if len(found_elements) < 3:  # Require at least 3 core elements
            return StepValidation(
                is_valid=False,
                error_message=f"Deconstruct output missing key elements. Found: {found_elements}, Required: {required_elements}",
                suggested_input="Please analyze the narrative and clearly identify WHO (actors), WHAT (actions), WHY (motivations), HOW (methods), and OUTCOME (results)."
            )
        
        return StepValidation(is_valid=True, output_format="structured_elements")
    
    def _validate_map_output(self, output: str) -> StepValidation:
        """Validate map step produces clear element mappings."""
        
        # Look for mapping indicators
        mapping_indicators = ["→", "->", "mapped to", "becomes", "equivalent"]
        has_mappings = any(indicator in output.lower() for indicator in mapping_indicators)
        
        # Check for namespace references
        has_namespace = self.namespace.lower() in output.lower()
        
        if not has_mappings and not has_namespace:
            return StepValidation(
                is_valid=False,
                error_message="Map output lacks clear element mappings to target namespace",
                suggested_input=f"Create specific mappings from the source elements to {self.namespace} equivalents using clear mapping notation (→)."
            )
        
        return StepValidation(is_valid=True, output_format="element_mappings")
    
    def _validate_reconstruct_output(self, output: str) -> StepValidation:
        """Validate reconstruct step produces a coherent narrative."""
        
        # Basic narrative indicators
        narrative_indicators = [".", "!", "?"]  # Sentence endings
        sentence_count = sum(output.count(indicator) for indicator in narrative_indicators)
        
        # Should be a flowing narrative, not fragmented mappings
        has_mapping_fragments = "→" in output or "mapped to" in output.lower()
        
        if sentence_count < 2:
            return StepValidation(
                is_valid=False,
                error_message="Reconstruct output is too fragmented - should be a coherent narrative",
                suggested_input=f"Tell the complete story in {self.persona}'s voice as a flowing narrative, not as fragmented elements."
            )
        
        if has_mapping_fragments:
            return StepValidation(
                is_valid=False,
                error_message="Reconstruct output contains mapping fragments instead of narrative",
                suggested_input=f"Write this as a complete story from {self.persona}'s perspective, not as element mappings."
            )
        
        return StepValidation(is_valid=True, output_format="narrative")
    
    def _validate_stylize_output(self, output: str) -> StepValidation:
        """Validate stylize step maintains narrative while applying style."""
        
        # Should still be narrative format
        narrative_indicators = [".", "!", "?"]
        sentence_count = sum(output.count(indicator) for indicator in narrative_indicators)
        
        if sentence_count < 2:
            return StepValidation(
                is_valid=False,
                error_message="Stylize output lost narrative structure",
                suggested_input=f"Apply {self.style} style to the narrative while maintaining the story structure."
            )
        
        return StepValidation(is_valid=True, output_format="styled_narrative")
    
    def _validate_reflect_output(self, output: str) -> StepValidation:
        """Validate reflect step produces meta-commentary."""
        
        # Should contain analytical language
        analytical_indicators = ["reveals", "illuminates", "shows", "demonstrates", "pattern", "universal"]
        has_analysis = any(indicator in output.lower() for indicator in analytical_indicators)
        
        if not has_analysis:
            return StepValidation(
                is_valid=False,
                error_message="Reflect output lacks analytical meta-commentary",
                suggested_input=f"Provide analytical commentary on how the {self.namespace} transformation illuminates the original narrative."
            )
        
        return StepValidation(is_valid=True, output_format="meta_commentary")
    
    def format_input_for_step(self, step_type: str, input_text: str, previous_step_type: str = None) -> str:
        """Format input text appropriately for the given step type."""
        
        if step_type == "map" and previous_step_type == "deconstruct":
            return f"""Based on these extracted narrative elements, create specific mappings to the {self.namespace} universe:

{input_text}

For each element identified above, provide a direct equivalent in the {self.namespace} setting. Use the format:
Original Element → {self.namespace} Equivalent

Be specific and preserve the relationships between elements."""
        
        elif step_type == "reconstruct" and previous_step_type == "map":
            return f"""Using these element mappings, reconstruct the complete narrative from the {self.persona} perspective:

{input_text}

Tell this as a flowing, coherent story using the mapped elements. Maintain the original sequence of events and relationships, but express it through the {self.persona}'s voice and understanding."""
        
        elif step_type == "stylize" and previous_step_type == "reconstruct":
            return f"""Apply {self.style} language style to this narrative:

{input_text}

Adjust only the tone, voice, and expression to match {self.style} style. Do not change the plot, characters, or core meaning."""
        
        elif step_type == "reflect" and previous_step_type == "stylize":
            return f"""Provide meta-commentary on this allegorical transformation:

Original → {self.namespace} via {self.persona} in {self.style} style:
{input_text}

Analyze how this transformation illuminates universal patterns or deeper truths in the original narrative."""
        
        else:
            # Default formatting
            return input_text
    
    def repair_step_output(self, step_type: str, input_text: str, failed_output: str) -> str:
        """Attempt to repair a failed step output."""
        
        logger.warning(f"Attempting to repair failed {step_type} output")
        
        if step_type == "deconstruct":
            return f"""WHO: Key actors in the narrative
WHAT: Primary actions and events  
WHY: Core motivations and conflicts
HOW: Methods and approaches used
OUTCOME: Results and implications

Analysis of: {input_text[:200]}..."""
        
        elif step_type == "map":
            return f"""MAPPED ELEMENTS for {self.namespace}:
- [Original elements] → [Equivalent {self.namespace} elements]
- [Preserve relationships and structure]
- [Based on: {input_text[:100]}...]"""
        
        elif step_type == "reconstruct":
            return f"""[Reconstructed narrative from {self.persona} perspective using mapped elements from previous step. This should be a flowing story, not fragmented mappings.]

Based on the mappings provided, here is the complete narrative..."""
        
        elif step_type == "stylize":
            return f"""[Apply {self.style} style to the narrative while maintaining story structure]

{failed_output}"""
        
        elif step_type == "reflect":
            return f"""This {self.namespace} transformation reveals universal patterns about [analyze the transformation]. The allegorical shift illuminates [deeper insights]."""
        
        return failed_output
    
    def get_step_instructions(self, step_type: str) -> str:
        """Get clear instructions for each step type."""
        
        instructions = {
            "deconstruct": f"""Extract the core narrative elements in this structure:
WHO: [Identify specific actors/characters]
WHAT: [Identify specific actions/events] 
WHY: [Identify motivations/conflicts]
HOW: [Identify methods/approaches]
OUTCOME: [Identify results/implications]

Be concrete and specific about the actual story elements.""",
            
            "map": f"""Create direct mappings from source elements to {self.namespace} equivalents:
- Source Element A → {self.namespace} Equivalent A
- Source Element B → {self.namespace} Equivalent B
[Continue for all elements]

Preserve relationships and maintain story structure.""",
            
            "reconstruct": f"""Tell the complete story using the mapped elements from {self.persona}'s perspective:
- Use flowing narrative prose
- Maintain the sequence of events
- Preserve character relationships  
- Keep the core conflict and resolution
- Express through {self.persona}'s voice and understanding""",
            
            "stylize": f"""Apply {self.style} language style to the narrative:
- Adjust tone and voice only
- Do not change plot, characters, or meaning
- Maintain narrative structure
- Express in {self.style} style""",
            
            "reflect": f"""Provide analytical meta-commentary:
- Explain how the {self.namespace} version illuminates the original
- Identify universal patterns revealed by the transformation
- Discuss deeper truths made visible through this lens
- Analyze the value of this allegorical perspective"""
        }
        
        return instructions.get(step_type, "Follow the system prompt instructions.")