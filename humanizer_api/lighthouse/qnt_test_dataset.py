"""
Quantum Narrative Theory Test Dataset
====================================

A comprehensive collection of narrative examples designed to test the full range 
of QNT analysis capabilities across different personas, namespaces, styles, and essence types.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class NarrativeTestCase:
    """A test case for QNT analysis with expected outcomes"""
    id: str
    narrative: str
    description: str
    expected_persona: str
    expected_namespace: str
    expected_style: str
    expected_essence_theme: str
    complexity_level: str  # "simple", "medium", "complex"
    test_focus: List[str]  # What aspects this test primarily evaluates

# Comprehensive Test Dataset
QNT_TEST_CASES = [
    # === CLASSIC LITERATURE SAMPLES ===
    NarrativeTestCase(
        id="shakespeare_hamlet",
        narrative="To be or not to be, that is the question: Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune, or to take arms against a sea of troubles and, by opposing, end them.",
        description="Shakespearean soliloquy - philosophical contemplation",
        expected_persona="philosophical contemplator",
        expected_namespace="renaissance drama",
        expected_style="poetic/elevated",
        expected_essence_theme="existential choice and mortality",
        complexity_level="complex",
        test_focus=["classical_style", "philosophical_content", "metaphorical_language"]
    ),
    
    NarrativeTestCase(
        id="dickens_opening",
        narrative="It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity.",
        description="Dickens' famous opening - paradoxical social observation",
        expected_persona="omniscient narrator",
        expected_namespace="historical/social realism",
        expected_style="rhetorical/balanced",
        expected_essence_theme="duality and contradiction in society",
        complexity_level="medium",
        test_focus=["narrative_voice", "rhetorical_devices", "historical_context"]
    ),
    
    # === MODERN LITERARY STYLES ===
    NarrativeTestCase(
        id="hemingway_style",
        narrative="The sun rose. Jake walked to the café. He ordered coffee. Black. The waiter brought it quickly. Jake paid. He left.",
        description="Hemingway-esque minimalism - sparse, understated",
        expected_persona="detached observer",
        expected_namespace="modern realism",
        expected_style="minimalist/spare",
        expected_essence_theme="understated human experience",
        complexity_level="simple",
        test_focus=["minimalist_style", "modern_voice", "economy_of_language"]
    ),
    
    NarrativeTestCase(
        id="stream_consciousness",
        narrative="Yes I said yes I will Yes and the water running all over me and my hair and my eyes and my face and the smell of the sea and the grass growing and the sun setting and why did he look at me that way when I knew what he was thinking about when he looked at me like that.",
        description="Stream of consciousness - internal monologue flow",
        expected_persona="internal consciousness",
        expected_namespace="psychological realism",
        expected_style="stream_of_consciousness",
        expected_essence_theme="unfiltered human thought",
        complexity_level="complex",
        test_focus=["internal_voice", "psychological_style", "consciousness_flow"]
    ),
    
    # === GENRE FICTION ===
    NarrativeTestCase(
        id="sci_fi_dystopian",
        narrative="The surveillance drones hummed overhead, their crimson scanners sweeping the empty streets. Maya pressed herself against the crumbling concrete wall, her neural implant buzzing with warnings. The resistance network had gone dark three hours ago.",
        description="Dystopian science fiction - technological oppression",
        expected_persona="resistant protagonist",
        expected_namespace="dystopian future",
        expected_style="cinematic/dramatic",
        expected_essence_theme="resistance against technological control",
        complexity_level="medium",
        test_focus=["genre_conventions", "world_building", "technological_vocabulary"]
    ),
    
    NarrativeTestCase(
        id="fantasy_epic",
        narrative="The ancient dragon Smaraethys stirred in her crystal cavern, her emerald scales catching the ethereal light of the moon-touched crystals. For seven centuries she had guarded the Shard of Eternity, waiting for the prophesied one.",
        description="High fantasy - mythical beings and artifacts",
        expected_persona="mythic chronicler",
        expected_namespace="high fantasy",
        expected_style="epic/elevated",
        expected_essence_theme="ancient guardianship and destiny",
        complexity_level="medium",
        test_focus=["fantasy_elements", "mythic_language", "world_building"]
    ),
    
    # === CONTEMPORARY VOICES ===
    NarrativeTestCase(
        id="social_media_voice",
        narrative="OMG you guys this coffee shop is literally the most aesthetic thing ever 💕 the barista is super cute and my latte art is basically a masterpiece??? Posting this everywhere #coffeeart #vibes #blessed",
        description="Social media generation voice - digital native expression",
        expected_persona="digital native",
        expected_namespace="contemporary social media",
        expected_style="informal/digital",
        expected_essence_theme="digital culture and sharing",
        complexity_level="simple",
        test_focus=["contemporary_voice", "digital_language", "generational_markers"]
    ),
    
    NarrativeTestCase(
        id="corporate_speak",
        narrative="We're excited to leverage synergistic solutions to optimize our value proposition and deliver scalable, best-in-class experiences that drive meaningful engagement across all touchpoints in our customer journey ecosystem.",
        description="Corporate jargon - business communication style",
        expected_persona="corporate communicator",
        expected_namespace="business/corporate",
        expected_style="corporate/jargon",
        expected_essence_theme="business optimization and efficiency",
        complexity_level="simple",
        test_focus=["professional_voice", "business_language", "institutional_style"]
    ),
    
    # === TECHNICAL/ACADEMIC ===
    NarrativeTestCase(
        id="academic_paper",
        narrative="This study investigates the correlation between quantum entanglement phenomena and narrative coherence structures, utilizing a mixed-methods approach combining phenomenological analysis with computational linguistics to establish empirical validity.",
        description="Academic writing - scholarly research presentation",
        expected_persona="academic researcher",
        expected_namespace="academic/scientific",
        expected_style="formal/academic",
        expected_essence_theme="systematic knowledge investigation",
        complexity_level="complex",
        test_focus=["academic_voice", "technical_language", "research_methodology"]
    ),
    
    NarrativeTestCase(
        id="technical_manual",
        narrative="Before proceeding with installation, ensure all power sources are disconnected. Remove the protective covering from connector pins. Align the memory module with the slot at a 30-degree angle and press firmly until you hear an audible click.",
        description="Technical instruction - procedural guidance",
        expected_persona="technical instructor",
        expected_namespace="technical/instructional",
        expected_style="procedural/clear",
        expected_essence_theme="systematic process guidance",
        complexity_level="simple",
        test_focus=["instructional_voice", "procedural_style", "technical_clarity"]
    ),
    
    # === EMOTIONAL/PERSONAL ===
    NarrativeTestCase(
        id="grief_memoir",
        narrative="The empty chair at the dinner table spoke louder than any words we could have said. Mom's place setting remained exactly as she had left it, her reading glasses still folded beside her teacup, as if she might return at any moment.",
        description="Personal memoir - grief and loss processing",
        expected_persona="grieving narrator",
        expected_namespace="domestic/personal",
        expected_style="intimate/emotional",
        expected_essence_theme="loss and memory preservation",
        complexity_level="medium",
        test_focus=["emotional_voice", "personal_narrative", "symbolic_objects"]
    ),
    
    NarrativeTestCase(
        id="love_letter",
        narrative="My dearest heart, when I think of you my soul sings like the morning birds greeting the dawn. Your laugh is the music that plays in my dreams, and your touch is the warmth that guides me through every storm.",
        description="Romantic expression - intimate emotional communication",
        expected_persona="romantic lover",
        expected_namespace="intimate/personal",
        expected_style="lyrical/romantic",
        expected_essence_theme="deep romantic devotion",
        complexity_level="medium",
        test_focus=["intimate_voice", "romantic_language", "emotional_intensity"]
    ),
    
    # === CULTURAL/HISTORICAL ===
    NarrativeTestCase(
        id="indigenous_wisdom",
        narrative="The old ones say that every tree holds the memory of the rain, every stone remembers the footsteps of our ancestors. When we walk this land, we walk with all who came before, and our children will walk with us when we join the eternal circle.",
        description="Indigenous wisdom tradition - ancestral connection",
        expected_persona="wisdom keeper",
        expected_namespace="indigenous/traditional",
        expected_style="oral_tradition/sacred",
        expected_essence_theme="ancestral continuity and sacred connection",
        complexity_level="complex",
        test_focus=["cultural_voice", "traditional_wisdom", "sacred_language"]
    ),
    
    NarrativeTestCase(
        id="war_correspondent",
        narrative="The artillery shells whistled overhead as I crouched in the rubble-strewn street, my camera clutched against my chest. Through the smoke and chaos, I could see the faces of civilians caught in this nightmare, their eyes holding stories the world needed to hear.",
        description="War journalism - witnessing conflict and suffering",
        expected_persona="war correspondent",
        expected_namespace="conflict/journalism",
        expected_style="journalistic/urgent",
        expected_essence_theme="bearing witness to human suffering",
        complexity_level="medium",
        test_focus=["journalistic_voice", "crisis_reporting", "moral_urgency"]
    ),
    
    # === EXPERIMENTAL/AVANT-GARDE ===
    NarrativeTestCase(
        id="surreal_experimental",
        narrative="The clockwork butterfly whispered secrets to the melting telephone while purple mathematics rained upward into yesterday's forgotten symphony of crystalline laughter echoing through dimensions that taste like Tuesday.",
        description="Surreal/experimental - non-linear dream logic",
        expected_persona="surreal visionary",
        expected_namespace="surreal/experimental",
        expected_style="avant_garde/surreal",
        expected_essence_theme="reality transcendence and perception",
        complexity_level="complex",
        test_focus=["experimental_style", "surreal_imagery", "non_linear_logic"]
    ),
    
    # === CHILDREN'S LITERATURE ===
    NarrativeTestCase(
        id="childrens_story",
        narrative="Once upon a time, in a forest where the trees giggled when the wind tickled their leaves, there lived a little rabbit named Pip who could talk to butterflies and always wore a bright red scarf.",
        description="Children's story - whimsical and innocent",
        expected_persona="child storyteller",
        expected_namespace="children's fantasy",
        expected_style="whimsical/simple",
        expected_essence_theme="innocent wonder and friendship",
        complexity_level="simple",
        test_focus=["child_appropriate_voice", "whimsical_style", "simple_narrative"]
    ),
    
    # === PHILOSOPHICAL/ABSTRACT ===
    NarrativeTestCase(
        id="philosophical_meditation",
        narrative="What is the nature of consciousness that observes its own thoughts? In the space between the thinker and the thought lies an infinite mystery, a aware awareness that knows itself without becoming an object of knowledge.",
        description="Philosophical meditation - consciousness and being",
        expected_persona="philosophical meditator",
        expected_namespace="philosophical/metaphysical",
        expected_style="contemplative/abstract",
        expected_essence_theme="nature of consciousness and self-awareness",
        complexity_level="complex",
        test_focus=["philosophical_voice", "abstract_concepts", "self_referential_thought"]
    )
]

def get_test_cases_by_focus(focus: str) -> List[NarrativeTestCase]:
    """Get test cases that focus on a specific aspect"""
    return [case for case in QNT_TEST_CASES if focus in case.test_focus]

def get_test_cases_by_complexity(complexity: str) -> List[NarrativeTestCase]:
    """Get test cases by complexity level"""
    return [case for case in QNT_TEST_CASES if case.complexity_level == complexity]

def get_all_personas() -> List[str]:
    """Get all unique expected personas from test cases"""
    return list(set(case.expected_persona for case in QNT_TEST_CASES))

def get_all_namespaces() -> List[str]:
    """Get all unique expected namespaces from test cases"""
    return list(set(case.expected_namespace for case in QNT_TEST_CASES))

def get_all_styles() -> List[str]:
    """Get all unique expected styles from test cases"""
    return list(set(case.expected_style for case in QNT_TEST_CASES))

def create_test_batch_commands() -> List[str]:
    """Generate CLI commands for testing all cases"""
    commands = []
    for case in QNT_TEST_CASES:
        # Basic analysis
        commands.append(f'humanizer analyze "{case.narrative}" --format summary')
        
        # Every 3rd case gets quantum analysis
        if len(commands) % 3 == 0:
            commands.append(f'humanizer analyze "{case.narrative}" --quantum --format table')
    
    return commands

# Test case categories for systematic testing
TEST_CATEGORIES = {
    "classical": ["shakespeare_hamlet", "dickens_opening"],
    "modern_literary": ["hemingway_style", "stream_consciousness"],
    "genre_fiction": ["sci_fi_dystopian", "fantasy_epic"],
    "contemporary": ["social_media_voice", "corporate_speak"],
    "technical": ["academic_paper", "technical_manual"],
    "emotional": ["grief_memoir", "love_letter"],
    "cultural": ["indigenous_wisdom", "war_correspondent"],
    "experimental": ["surreal_experimental"],
    "children": ["childrens_story"],
    "philosophical": ["philosophical_meditation"]
}

def run_category_tests(category: str) -> List[str]:
    """Generate test commands for a specific category"""
    if category not in TEST_CATEGORIES:
        raise ValueError(f"Unknown category: {category}")
    
    commands = []
    case_ids = TEST_CATEGORIES[category]
    
    for case_id in case_ids:
        case = next(case for case in QNT_TEST_CASES if case.id == case_id)
        commands.append(f'# Testing {category}: {case.description}')
        commands.append(f'humanizer analyze "{case.narrative}" --format summary')
        commands.append('')  # Empty line for readability
    
    return commands

if __name__ == "__main__":
    print("QNT Test Dataset Summary")
    print("=" * 50)
    print(f"Total test cases: {len(QNT_TEST_CASES)}")
    print(f"Complexity levels: {len(set(case.complexity_level for case in QNT_TEST_CASES))}")
    print(f"Unique personas: {len(get_all_personas())}")
    print(f"Unique namespaces: {len(get_all_namespaces())}")
    print(f"Unique styles: {len(get_all_styles())}")
    print(f"Test categories: {len(TEST_CATEGORIES)}")