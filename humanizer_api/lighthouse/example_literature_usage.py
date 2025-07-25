#!/usr/bin/env python3
"""
Example: Literature-Grounded Attribute Discovery
==============================================

This example demonstrates how the literature mining system discovers
comprehensive, literature-grounded attributes using QBist semantic analysis.

The system can discover new attribute categories beyond the traditional
persona/namespace/style trinity.
"""

import asyncio
import json
from pathlib import Path

async def example_discovery_process():
    """
    Example workflow for discovering literature-grounded attributes.
    """
    
    print("="*70)
    print("LITERATURE-GROUNDED ATTRIBUTE DISCOVERY EXAMPLE")
    print("="*70)
    print()
    
    print("This system addresses several key insights:")
    print("1. Current attributes (persona/namespace/style) are too limited")
    print("2. Attributes should be grounded in actual literature analysis")  
    print("3. QBist semantic tools can discover hidden attribute dimensions")
    print("4. Great literature contains the full spectrum of narrative possibilities")
    print()
    
    # Demonstrate the process with a small sample
    try:
        from literature_attribute_miner import mine_literature_for_attributes, CLASSIC_LITERATURE_IDS
        
        print("STEP 1: Selecting Classic Literature")
        print("-" * 40)
        
        # Start with a small but diverse sample
        sample_works = [
            ("11", "Alice's Adventures in Wonderland", "Carroll"),
            ("84", "Frankenstein", "Shelley"),
            ("1342", "Pride and Prejudice", "Austen"),
            ("2701", "Moby Dick", "Melville"),
            ("1661", "Sherlock Holmes", "Doyle")
        ]
        
        gutenberg_ids = [work[0] for work in sample_works]
        
        for work_id, title, author in sample_works:
            print(f"  - {title} by {author} (Gutenberg #{work_id})")
        
        print(f"\nMining {len(sample_works)} classic works...")
        print("This demonstrates the approach - full mining would use all 30+ classics")
        print()
        
        print("STEP 2: QBist Semantic Analysis Process")
        print("-" * 40)
        print("For each work, the system will:")
        print("  1. Extract meaningful passages (50-200 words each)")
        print("  2. Generate sentence transformer embeddings (768-dimensional)")
        print("  3. Create quantum meaning-states using M-POVM analysis")
        print("  4. Cluster passages in embedding space")
        print("  5. Discover semantic patterns that become new attributes")
        print()
        
        # Run a small demo (commented out to avoid long execution)
        # results = await mine_literature_for_attributes(
        #     gutenberg_ids=gutenberg_ids[:2],  # Just 2 works for demo
        #     max_passages_per_work=10
        # )
        
        # Simulate what the results would look like
        simulated_results = {
            "total_works_processed": 2,
            "total_passages_analyzed": 18,
            "total_clusters_discovered": 12,
            "attribute_categories": {
                "style": 4,
                "persona": 3,
                "namespace": 2,
                "emotional_register": 2,
                "temporal_perspective": 1
            },
            "discovered_attributes_by_category": {
                "style": [
                    "dialogue_heavy",
                    "elaborate_prose", 
                    "terse_descriptive",
                    "whimsical_narrative"
                ],
                "persona": [
                    "carroll_playful",
                    "shelley_gothic",
                    "scientific_observer"
                ],
                "namespace": [
                    "fantasy_wonderland",
                    "gothic_horror"
                ],
                "emotional_register": [
                    "wonder_curiosity", 
                    "dread_foreboding"
                ],
                "temporal_perspective": [
                    "immediate_present"
                ]
            }
        }
        
        print("STEP 3: Discovered Attribute Categories")
        print("-" * 40)
        
        for category, count in simulated_results["attribute_categories"].items():
            print(f"{category.upper()}: {count} attributes discovered")
            
            attributes = simulated_results["discovered_attributes_by_category"][category]
            for attr in attributes:
                print(f"  - {attr}")
            print()
        
        print("STEP 4: What This Achieves")
        print("-" * 40)
        print("🎯 COMPREHENSIVE COVERAGE:")
        print("   Instead of 18 total attributes (6 personas × 3 namespaces × 3 styles),")
        print("   we discover 50+ literature-grounded attributes across multiple dimensions")
        print()
        print("🎯 NEW ATTRIBUTE CATEGORIES:")
        print("   - emotional_register: wonder_curiosity, dread_foreboding, melancholic_beauty")
        print("   - temporal_perspective: immediate_present, nostalgic_past, prophetic_future") 
        print("   - narrative_distance: intimate_confessional, omniscient_detached, limited_third")
        print("   - rhetorical_mode: persuasive_argument, exploratory_questioning, declarative_truth")
        print()
        print("🎯 LITERATURE-GROUNDED:")
        print("   Each attribute is backed by actual passages from great literature,")
        print("   not arbitrary academic categories")
        print()
        print("🎯 QBIST SEMANTIC ANALYSIS:")
        print("   Uses quantum measurement theory to discover hidden semantic dimensions")
        print("   in the embedding space of literary works")
        print()
        
        print("STEP 5: Integration with Transformation System")
        print("-" * 40)
        print("The discovered attributes can be:")
        print("  1. Used to replace/expand current persona/namespace/style lists")
        print("  2. Integrated with the AI attribute selection system")
        print("  3. Applied in multi-dimensional transformation configurations")
        print("  4. Used to create transformation 'recipes' based on literary models")
        print()
        print("Example enhanced transformation:")
        print("  Original: scientist + scientific + formal")
        print("  Enhanced: darwin_observer + natural_philosophy + patient_descriptive")
        print("           + wonder_curiosity + naturalist_temporal + intimate_observational")
        print()
        
    except ImportError as e:
        print(f"Literature mining system not available: {e}")
        print("This is a demonstration of what the system would accomplish.")

def show_theoretical_taxonomy():
    """Show what a literature-grounded taxonomy might look like."""
    
    print("THEORETICAL LITERATURE-GROUNDED TAXONOMY")
    print("="*60)
    print()
    
    theoretical_taxonomy = {
        "CLASSICAL PERSONAS": [
            "shakespeare_universal", "dickens_social", "austen_wit", 
            "melville_philosophical", "carroll_whimsical", "poe_gothic",
            "wilde_satirical", "darwin_observational", "thoreau_transcendental"
        ],
        
        "CLASSICAL NAMESPACES": [
            "victorian_society", "romantic_nature", "gothic_mystery",
            "scientific_enlightenment", "mythic_archetypal", "social_realism",
            "pastoral_idyllic", "urban_industrial", "philosophical_metaphysical"
        ],
        
        "CLASSICAL STYLES": [
            "dickensian_elaborate", "hemingway_sparse", "joycean_stream",
            "shakespearean_elevated", "carrollian_nonsense", "gothic_atmospheric",
            "scientific_precise", "romantic_flowing", "modernist_fragmented"
        ],
        
        "EMOTIONAL REGISTERS": [
            "wonder_curiosity", "dread_foreboding", "melancholic_beauty",
            "satirical_wit", "transcendent_awe", "intimate_tenderness",
            "righteous_indignation", "existential_uncertainty", "joyful_celebration"
        ],
        
        "TEMPORAL PERSPECTIVES": [
            "immediate_present", "nostalgic_past", "prophetic_future",
            "cyclical_eternal", "historical_sweep", "momentary_instant",
            "generational_span", "mythic_timeless"
        ],
        
        "NARRATIVE DISTANCES": [
            "intimate_confessional", "omniscient_detached", "limited_third",
            "collective_voice", "dramatic_immediate", "reflective_distant",
            "documentary_objective", "stream_consciousness"
        ],
        
        "RHETORICAL MODES": [
            "persuasive_argument", "exploratory_questioning", "declarative_truth",
            "meditative_reflection", "dramatic_dialogue", "lyrical_expression",
            "analytical_exposition", "narrative_storytelling"
        ]
    }
    
    total_attributes = sum(len(attrs) for attrs in theoretical_taxonomy.values())
    
    print(f"Total attribute dimensions: {len(theoretical_taxonomy)}")
    print(f"Total attributes: {total_attributes}")
    print(f"Possible combinations: {total_attributes ** len(theoretical_taxonomy):,}")
    print()
    
    for category, attributes in theoretical_taxonomy.items():
        print(f"{category} ({len(attributes)} attributes):")
        for attr in attributes:
            print(f"  - {attr}")
        print()
    
    print("TRANSFORMATION EXAMPLES:")
    print("-" * 30)
    print("🎭 Shakespearean Transformation:")
    print("   shakespeare_universal + romantic_nature + shakespearean_elevated")
    print("   + transcendent_awe + mythic_timeless + dramatic_immediate")
    print()
    print("🔬 Scientific Analysis:")
    print("   darwin_observational + scientific_enlightenment + scientific_precise") 
    print("   + wonder_curiosity + immediate_present + analytical_exposition")
    print()
    print("🎪 Whimsical Fantasy:")
    print("   carroll_whimsical + mythic_archetypal + carrollian_nonsense")
    print("   + joyful_celebration + cyclical_eternal + narrative_storytelling")

if __name__ == "__main__":
    print("Literature-Grounded Attribute Discovery System")
    print("Press Enter to run the example...")
    input()
    
    asyncio.run(example_discovery_process())
    
    print("\nPress Enter to see theoretical taxonomy...")
    input()
    
    show_theoretical_taxonomy()
    
    print("\nTo actually run literature mining:")
    print("python run_literature_mining.py --sample-size 3")