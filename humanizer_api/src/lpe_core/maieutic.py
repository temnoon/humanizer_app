"""Maieutic (Socratic) dialogue system for narrative exploration."""
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from .models import DialogueTurn, MaieuticSession
from .llm_provider import get_llm_provider, LLMProvider
from .projection import TranslationChain

logger = logging.getLogger(__name__)

class MaieuticDialogue:
    """Conducts maieutic (Socratic) dialogues to explore narratives."""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self.session = None
        
    def start_session(self, narrative: str, goal: str = "understand") -> MaieuticSession:
        """Start a new maieutic dialogue session."""
        self.session = MaieuticSession(
            initial_narrative=narrative,
            goal=goal
        )
        return self.session
    
    def generate_question(self, depth_level: int = 0) -> str:
        """Generate the next maieutic question based on dialogue history."""
        system_prompt = """You are a Socratic questioner practicing maieutic dialogue.
Your role is to help the user discover deeper truths about their narrative through thoughtful questions.
Do not provide answers or interpretations - only ask questions that guide discovery.
Focus on one aspect at a time, building understanding gradually.
Questions should be open-ended and thought-provoking."""
        
        # Build context from session
        context = f"Initial narrative: {self.session.initial_narrative}\n\n"
        
        if self.session.turns:
            context += "Dialogue so far:\n"
            for turn in self.session.turns[-3:]:  # Last 3 turns for context
                context += f"Q: {turn.question}\n"
                context += f"A: {turn.answer}\n\n"
        
        # Depth-specific prompting
        depth_prompts = {
            0: "Ask an initial question to understand the surface level of the narrative.",
            1: "Ask about the underlying motivations or conflicts.",
            2: "Probe deeper into the root causes or fundamental tensions.",
            3: "Question the assumptions or worldview behind the narrative.",
            4: "Explore the universal or archetypal elements present."
        }
        
        prompt = f"""{context}

Depth level: {depth_level}
Instruction: {depth_prompts.get(depth_level, depth_prompts[2])}

Generate a single, thoughtful question to continue the maieutic dialogue:"""
        
        try:
            question = self.provider.generate(prompt, system_prompt)
            return question.strip()
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            # Fallback questions
            fallbacks = [
                "What do you think is the core conflict in this narrative?",
                "Why do you think this situation arose?",
                "What assumptions might be underlying this story?",
                "What would happen if we looked at this from another perspective?",
                "What deeper pattern might this represent?"
            ]
            return fallbacks[depth_level % len(fallbacks)]
    
    def extract_insights(self, question: str, answer: str) -> List[str]:
        """Extract key insights from an answer."""
        system_prompt = """You are analyzing a maieutic dialogue to extract key insights.
Identify 1-3 brief, specific insights revealed by the answer.
Focus on what was discovered or clarified, not just what was said."""
        
        prompt = f"""Question: {question}
Answer: {answer}

List 1-3 key insights revealed by this answer (one per line):"""
        
        try:
            response = self.provider.generate(prompt, system_prompt)
            insights = [line.strip() for line in response.strip().split('\n') 
                       if line.strip() and not line.strip().startswith('#')]
            return insights[:3]  # Max 3 insights
        except:
            return ["New perspective revealed"]
    
    def synthesize_understanding(self) -> str:
        """Synthesize the final understanding from the dialogue."""
        if not self.session or not self.session.turns:
            return "No dialogue conducted yet."
        
        system_prompt = """You are synthesizing the discoveries from a maieutic dialogue.
Summarize what was collectively discovered through the questioning process.
Focus on insights that emerged, not just a retelling of the conversation."""
        
        dialogue_text = "Maieutic Dialogue Summary:\n\n"
        dialogue_text += f"Original narrative: {self.session.initial_narrative}\n\n"
        
        for i, turn in enumerate(self.session.turns):
            dialogue_text += f"Q{i+1}: {turn.question}\n"
            dialogue_text += f"A{i+1}: {turn.answer}\n"
            if turn.insights:
                dialogue_text += f"Insights: {', '.join(turn.insights)}\n"
            dialogue_text += "\n"
        
        prompt = f"""{dialogue_text}

Based on this maieutic dialogue, synthesize the key understanding that emerged:"""
        
        try:
            return self.provider.generate(prompt, system_prompt)
        except:
            return "Through questioning, deeper layers of meaning were revealed."
    
    def add_turn(self, question: str, answer: str, depth_level: int = 0) -> DialogueTurn:
        """Add a turn to the current session."""
        if not self.session:
            raise ValueError("No session started. Call start_session first.")
        
        # Extract insights
        insights = self.extract_insights(question, answer)
        
        # Create turn
        turn = DialogueTurn(
            question=question,
            answer=answer,
            insights=insights,
            depth_level=depth_level
        )
        
        self.session.turns.append(turn)
        return turn
    
    def suggest_configuration(self) -> Tuple[str, str, str]:
        """Suggest projection configuration based on dialogue insights."""
        if not self.session or not self.session.turns:
            return 'neutral', 'lamish-galaxy', 'standard'
        
        # Analyze dialogue content to suggest configuration
        system_prompt = """Based on a maieutic dialogue, suggest the most appropriate configuration 
for an allegorical projection. Consider the themes, depth, and insights discovered."""
        
        dialogue_summary = f"""Narrative: {self.session.initial_narrative}

Key insights discovered:
"""
        for turn in self.session.turns:
            for insight in turn.insights:
                dialogue_summary += f"- {insight}\n"
        
        dialogue_summary += f"\nFinal understanding: {self.session.final_understanding}"
        
        prompt = f"""{dialogue_summary}

Based on this dialogue, suggest ONE configuration from each category:
Persona: neutral, advocate, critic, philosopher, storyteller
Namespace: lamish-galaxy, medieval-realm, corporate-dystopia, natural-world, quantum-realm  
Style: standard, academic, poetic, technical, casual

Respond with only three words separated by commas: persona,namespace,style"""
        
        try:
            response = self.provider.generate(prompt, system_prompt)
            parts = response.strip().lower().split(',')
            if len(parts) == 3:
                persona = parts[0].strip()
                namespace = parts[1].strip()
                style = parts[2].strip()
                
                # Validate suggestions
                valid_personas = ['neutral', 'advocate', 'critic', 'philosopher', 'storyteller']
                valid_namespaces = ['lamish-galaxy', 'medieval-realm', 'corporate-dystopia', 
                                  'natural-world', 'quantum-realm']
                valid_styles = ['standard', 'academic', 'poetic', 'technical', 'casual']
                
                if persona in valid_personas and namespace in valid_namespaces and style in valid_styles:
                    return persona, namespace, style
        except:
            pass
        
        # Default fallback based on simple heuristics
        if any('conflict' in str(turn.insights).lower() for turn in self.session.turns):
            return 'critic', 'corporate-dystopia', 'technical'
        elif any('meaning' in str(turn.insights).lower() for turn in self.session.turns):
            return 'philosopher', 'quantum-realm', 'poetic'
        else:
            return 'neutral', 'lamish-galaxy', 'standard'
    
    def create_enriched_narrative(self) -> str:
        """Create an enriched narrative that includes dialogue insights."""
        if not self.session:
            return ""
        
        enriched = f"""ORIGINAL NARRATIVE TO TRANSFORM:
{self.session.initial_narrative}

KEY ELEMENTS TO PRESERVE IN THE ALLEGORY:"""
        
        # Extract the most important discovered elements
        key_elements = []
        
        for turn in self.session.turns:
            for insight in turn.insights:
                if len(insight) > 10:  # Filter out very short insights
                    key_elements.append(f"- {insight}")
        
        enriched += "\n".join(key_elements[:5])  # Top 5 key elements
        
        # Add the core understanding
        if self.session.final_understanding:
            enriched += f"\n\nCORE UNDERSTANDING:\n{self.session.final_understanding}"
        
        enriched += "\n\nREMEMBER: Create an allegory that tells THE SAME STORY with different characters/settings."
        
        return enriched
    
    def complete_session(self) -> MaieuticSession:
        """Complete the current session by synthesizing understanding."""
        if not self.session:
            raise ValueError("No session started.")
        
        self.session.final_understanding = self.synthesize_understanding()
        return self.session