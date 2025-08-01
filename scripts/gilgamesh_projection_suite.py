#!/usr/bin/env python3
"""
Gilgamesh Projection Test Suite
Interactive agent frontend for demonstrating narrative DNA projection
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

# Add lighthouse path for imports
lighthouse_path = '/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse'
sys.path.insert(0, lighthouse_path)

from narrative_projection_engine import NarrativeProjectionEngine, ProjectionParameters


class ProjectionAgent:
    """AI Agent coordinating narrative transformations"""
    
    def __init__(self):
        self.projection_engine = NarrativeProjectionEngine()
        self.session_history = []
        self.available_projections = self.projection_engine.get_available_projections()
        
        # Epic of Gilgamesh sample passages
        self.gilgamesh_passages = {
            'opening': """Gilgamesh, king of Uruk, was two-thirds divine and one-third mortal. 
                         He oppressed his people with his strength, and they cried out to the gods for relief. 
                         The gods heard their pleas and created Enkidu, a wild man of the forest, to challenge the king.""",
            
            'friendship': """When Gilgamesh and Enkidu first met, they fought like wild bulls, 
                           shaking the very foundations of Uruk with their battle. 
                           But when their strength proved equal, they embraced as brothers, 
                           and their friendship became legendary throughout the land.""",
            
            'cedar_forest': """Together, Gilgamesh and Enkidu journeyed to the Cedar Forest, 
                              where the monster Humbaba guarded the sacred trees. 
                              They spoke words of courage to each other, 
                              knowing that death might await them in that dark place.""",
            
            'death_of_enkidu': """Enkidu fell ill and died, and Gilgamesh wept seven days and seven nights. 
                                 He could not believe his friend was gone forever. 
                                 'How can I rest when my friend lies dead?' he cried. 
                                 'I too will die, and will I not be like Enkidu?'""",
            
            'quest_for_immortality': """Gilgamesh set out to find Utnapishtim, the survivor of the great flood, 
                                       who alone among mortals had been granted eternal life. 
                                       He crossed dangerous mountains and traversed the waters of death, 
                                       driven by his terror of mortality.""",
            
            'wisdom': """Utnapishtim told Gilgamesh: 'There is no permanence in life. 
                        The gods alone live forever, but for us humans, 
                        our days are numbered and our achievements are like wind. 
                        Return to Uruk and live well while you may.'"""
        }
        
        print("🏺 Gilgamesh Projection Suite initialized")
        print(f"🎭 Available personas: {', '.join(self.available_projections['personas'])}")
        print(f"🌍 Available namespaces: {', '.join(self.available_projections['namespaces'])}")
        print(f"✍️ Available styles: {', '.join(self.available_projections['styles'])}")
    
    def run_interactive_session(self):
        """Run interactive projection session"""
        
        print("\n" + "="*80)
        print("🏺 THE EPIC OF GILGAMESH - NARRATIVE DNA PROJECTION SUITE")
        print("="*80)
        print("Welcome to the interactive narrative transformation laboratory!")
        print("We will project the Epic of Gilgamesh through different DNA attributes.")
        print("\nType 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\n🎭 projection> ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Thank you for exploring narrative DNA projections!")
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'list':
                    self._list_passages()
                elif command == 'show':
                    self._show_projections()
                elif command.startswith('project '):
                    self._handle_projection_command(command)
                elif command == 'demo':
                    self._run_demo()
                elif command == 'compare':
                    self._compare_projections()
                elif command == 'analyze':
                    self._analyze_transformations()
                elif command == 'random':
                    self._random_projection()
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self):
        """Show available commands"""
        
        help_text = """
🎭 PROJECTION SUITE COMMANDS:

📖 Content Commands:
  list              - Show available Gilgamesh passages
  show              - Show current projection options
  
🔮 Projection Commands:
  project <passage> - Project a specific passage (e.g., 'project opening')
  demo              - Run guided demonstration
  compare           - Compare multiple projections side by side
  random            - Generate random projection combination
  
📊 Analysis Commands:
  analyze           - Analyze transformation patterns
  
🔧 System Commands:
  help              - Show this help
  quit              - Exit the suite

🎯 PROJECTION PARAMETERS:
  After 'project <passage>', you'll be prompted for:
  - Persona (voice/perspective)
  - Namespace (cultural context)  
  - Style (linguistic patterns)
  
📚 AVAILABLE PASSAGES:
  opening, friendship, cedar_forest, death_of_enkidu, 
  quest_for_immortality, wisdom
  
✨ EXAMPLE:
  projection> project friendship
  projection> demo
  projection> compare
        """
        print(help_text)
    
    def _list_passages(self):
        """List available Gilgamesh passages"""
        
        print("\n📚 AVAILABLE GILGAMESH PASSAGES:")
        print("="*50)
        
        for key, passage in self.gilgamesh_passages.items():
            print(f"\n📖 {key.upper().replace('_', ' ')}")
            print(f"   {passage[:100]}...")
            print(f"   Length: {len(passage)} characters")
    
    def _show_projections(self):
        """Show available projection options"""
        
        print("\n🎭 PROJECTION OPTIONS:")
        print("="*40)
        
        print(f"\n👤 PERSONAS ({len(self.available_projections['personas'])}):")
        for persona in self.available_projections['personas']:
            print(f"  • {persona}")
        
        print(f"\n🌍 NAMESPACES ({len(self.available_projections['namespaces'])}):")
        for namespace in self.available_projections['namespaces']:
            print(f"  • {namespace}")
        
        print(f"\n✍️ STYLES ({len(self.available_projections['styles'])}):")
        for style in self.available_projections['styles']:
            print(f"  • {style}")
    
    def _handle_projection_command(self, command: str):
        """Handle projection command"""
        
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("❓ Please specify a passage: project <passage_name>")
            return
        
        passage_name = parts[1].strip()
        
        if passage_name not in self.gilgamesh_passages:
            print(f"❌ Unknown passage '{passage_name}'. Available: {', '.join(self.gilgamesh_passages.keys())}")
            return
        
        # Interactive projection setup
        print(f"\n🎭 Setting up projection for: {passage_name.upper()}")
        print("="*60)
        
        # Show passage
        passage_text = self.gilgamesh_passages[passage_name]
        print(f"📖 Original passage:")
        print(f'   "{passage_text}"')
        
        # Get projection parameters
        persona = self._get_user_choice("persona", self.available_projections['personas'])
        if not persona:
            return
            
        namespace = self._get_user_choice("namespace", self.available_projections['namespaces'])
        if not namespace:
            return
            
        style = self._get_user_choice("style", self.available_projections['styles'])
        if not style:
            return
        
        # Perform projection
        self._perform_projection(passage_name, passage_text, persona, namespace, style)
    
    def _get_user_choice(self, category: str, options: List[str]) -> Optional[str]:
        """Get user choice from options"""
        
        print(f"\n🎯 Select {category}:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"Choose {category} (1-{len(options)}) or 'back': ").strip()
                
                if choice.lower() == 'back':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected = options[choice_num - 1]
                    print(f"✅ Selected {category}: {selected}")
                    return selected
                else:
                    print(f"❌ Please choose a number between 1 and {len(options)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _perform_projection(self, passage_name: str, passage_text: str, 
                           persona: str, namespace: str, style: str):
        """Perform the actual projection"""
        
        print(f"\n🔮 PROJECTING NARRATIVE...")
        print("="*50)
        
        # Show what we're doing
        print(f"📖 Passage: {passage_name}")
        print(f"👤 Persona: {persona}")
        print(f"🌍 Namespace: {namespace}")
        print(f"✍️ Style: {style}")
        
        # Create projection parameters
        params = ProjectionParameters(
            target_persona=persona,
            target_namespace=namespace,
            target_style=style,
            projection_strength=0.8
        )
        
        # Perform projection
        print("\n⏳ Processing...")
        result = self.projection_engine.project_narrative(passage_text, params)
        
        # Display results
        print(f"\n✨ PROJECTION COMPLETE!")
        print("="*60)
        
        print(f"\n📖 ORIGINAL:")
        print(f'   "{result.original_text}"')
        
        print(f"\n🎭 PROJECTED ({persona} • {namespace} • {style}):")
        print(f'   "{result.projected_text}"')
        
        print(f"\n📊 METRICS:")
        print(f"   🔮 Essence Preservation: {result.essence_preservation_score:.2%}")
        print(f"   🎯 Projection Confidence: {result.projection_confidence:.2%}")
        
        print(f"\n🔧 TRANSFORMATION LOG:")
        for i, log_entry in enumerate(result.transformation_log, 1):
            print(f"   {i}. {log_entry}")
        
        # Save to session history
        self.session_history.append({
            'passage_name': passage_name,
            'parameters': params,
            'result': result,
            'timestamp': time.time()
        })
        
        print(f"\n💾 Saved to session history ({len(self.session_history)} projections total)")
    
    def _run_demo(self):
        """Run guided demonstration"""
        
        print("\n🎪 GUIDED DEMONSTRATION")
        print("="*50)
        print("Let's explore how the same passage transforms across different projections!")
        
        # Use friendship passage for demo
        passage_name = 'friendship'
        passage_text = self.gilgamesh_passages[passage_name]
        
        print(f"\n📖 Using passage: {passage_name.upper()}")
        print(f'   "{passage_text}"')
        
        # Define interesting projection combinations
        demo_projections = [
            ('tragic_chorus', 'ancient_mesopotamia', 'epic_verse'),
            ('cyberpunk_hacker', 'cyberpunk_dystopia', 'noir_prose'),
            ('victorian_narrator', 'regency_england', 'stream_of_consciousness')
        ]
        
        print(f"\n🎭 We'll project this through {len(demo_projections)} different combinations:")
        
        for i, (persona, namespace, style) in enumerate(demo_projections, 1):
            print(f"\n--- PROJECTION {i}: {persona} • {namespace} • {style} ---")
            
            params = ProjectionParameters(
                target_persona=persona,
                target_namespace=namespace,
                target_style=style
            )
            
            result = self.projection_engine.project_narrative(passage_text, params)
            
            print(f"🎭 Result: \"{result.projected_text}\"")
            print(f"📊 Essence: {result.essence_preservation_score:.1%} | Confidence: {result.projection_confidence:.1%}")
            
            time.sleep(1)  # Dramatic pause
        
        print(f"\n🎯 Demo complete! Notice how the core friendship theme persists")
        print(f"   across all projections while the expression changes dramatically.")
    
    def _compare_projections(self):
        """Compare multiple projections side by side"""
        
        if len(self.session_history) < 2:
            print("❌ Need at least 2 projections in history to compare.")
            print("   Run some projections first!")
            return
        
        print(f"\n🔍 PROJECTION COMPARISON")
        print("="*60)
        
        print(f"📊 Comparing {len(self.session_history)} projections from session:")
        
        for i, session in enumerate(self.session_history, 1):
            result = session['result']
            params = session['parameters']
            passage = session['passage_name']
            
            print(f"\n--- PROJECTION {i}: {passage.upper()} ---")
            print(f"🎭 {params.target_persona} • {params.target_namespace} • {params.target_style}")
            print(f"📝 \"{result.projected_text[:100]}...\"")
            print(f"📊 Essence: {result.essence_preservation_score:.1%} | Confidence: {result.projection_confidence:.1%}")
    
    def _analyze_transformations(self):
        """Analyze transformation patterns"""
        
        if not self.session_history:
            print("❌ No projections in history to analyze.")
            return
        
        print(f"\n📈 TRANSFORMATION ANALYSIS")
        print("="*50)
        
        # Analyze essence preservation
        preservation_scores = [s['result'].essence_preservation_score for s in self.session_history]
        confidence_scores = [s['result'].projection_confidence for s in self.session_history]
        
        print(f"📊 STATISTICAL SUMMARY ({len(self.session_history)} projections):")
        print(f"   🔮 Essence Preservation: avg={sum(preservation_scores)/len(preservation_scores):.1%}")
        print(f"   🎯 Projection Confidence: avg={sum(confidence_scores)/len(confidence_scores):.1%}")
        
        # Find best and worst projections
        best_idx = max(range(len(preservation_scores)), key=lambda i: preservation_scores[i])
        worst_idx = min(range(len(preservation_scores)), key=lambda i: preservation_scores[i])
        
        print(f"\n🏆 BEST PROJECTION (Essence: {preservation_scores[best_idx]:.1%}):")
        best_session = self.session_history[best_idx]
        print(f"   🎭 {best_session['parameters'].target_persona}")
        print(f"   📝 \"{best_session['result'].projected_text[:80]}...\"")
        
        print(f"\n⚠️ MOST CHALLENGING PROJECTION (Essence: {preservation_scores[worst_idx]:.1%}):")
        worst_session = self.session_history[worst_idx]
        print(f"   🎭 {worst_session['parameters'].target_persona}")
        print(f"   📝 \"{worst_session['result'].projected_text[:80]}...\"")
        
        # Pattern analysis
        persona_usage = {}
        for session in self.session_history:
            persona = session['parameters'].target_persona
            persona_usage[persona] = persona_usage.get(persona, 0) + 1
        
        print(f"\n🎭 PERSONA USAGE PATTERNS:")
        for persona, count in sorted(persona_usage.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {persona}: {count} times")
    
    def _random_projection(self):
        """Generate random projection combination"""
        
        passage_name = random.choice(list(self.gilgamesh_passages.keys()))
        persona = random.choice(self.available_projections['personas'])
        namespace = random.choice(self.available_projections['namespaces'])
        style = random.choice(self.available_projections['styles'])
        
        print(f"\n🎲 RANDOM PROJECTION GENERATOR")
        print("="*50)
        print(f"🎰 Randomly selected:")
        print(f"   📖 Passage: {passage_name}")
        print(f"   👤 Persona: {persona}")
        print(f"   🌍 Namespace: {namespace}")
        print(f"   ✍️ Style: {style}")
        
        proceed = input("\n🎯 Proceed with this projection? (y/n): ").lower().strip()
        if proceed == 'y':
            passage_text = self.gilgamesh_passages[passage_name]
            self._perform_projection(passage_name, passage_text, persona, namespace, style)
        else:
            print("🚫 Random projection cancelled")


def main():
    """Main entry point"""
    
    print("🏺 Initializing Gilgamesh Projection Suite...")
    
    # Check if we have discovered attributes
    attributes_dir = Path("/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/discovered_attributes")
    if not attributes_dir.exists():
        print("❌ No discovered attributes found!")
        print("   Please run the enhanced discovery system first:")
        print("   python enhanced_autonomous_discoverer.py --max-books 3")
        return
    
    # Initialize and run
    agent = ProjectionAgent()
    agent.run_interactive_session()


if __name__ == "__main__":
    main()