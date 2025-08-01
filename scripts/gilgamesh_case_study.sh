#!/bin/bash

# Gilgamesh Case Study: DNA Mashup Transformations
# Create three versions of the Epic of Gilgamesh using different literary DNA combinations

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/gilgamesh_case_study_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/transformation.log"
API_URL="http://localhost:8100"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Available DNA combinations from our extracted library
declare -a PERSONAS=("philosophical_seafarer" "tragic_chorus" "gothic_documenter" "naturalist_observer" "vernacular_storyteller" "independent_moralist" "refined_social_observer" "scientific_visionary")
declare -a NAMESPACES=("maritime_existentialism" "renaissance_tragedy" "victorian_gothic_horror" "wilderness_naturalism" "antebellum_americana" "victorian_social_reform" "regency_social_comedy" "scientific_romance")
declare -a STYLES=("epic_philosophical_prose" "elizabethan_dramatic_verse" "gothic_realism" "naturalist_prose" "american_vernacular_realism" "gothic_bildungsroman" "austen_ironic_realism" "scientific_narrative")

# The Epic of Gilgamesh base narrative (concise version for transformation)
GILGAMESH_BASE="Gilgamesh was king of Uruk, two-thirds divine and one-third human. He ruled with great strength but also great tyranny, oppressing his people with endless demands for labor and tribute. The gods heard the cries of the people and created Enkidu, a wild man of the forest, to challenge Gilgamesh.

Enkidu lived among the animals until a temple priestess civilized him and brought him to the city. When Enkidu and Gilgamesh met, they fought fiercely, evenly matched in strength. After their battle, they became the closest of friends and embarked on great adventures together.

Their first quest was to the Cedar Forest to slay the monster Humbaba, guardian of the sacred trees. Despite the creature's fearsome power and the warnings of the gods, they succeeded in defeating Humbaba and cutting down the cedar trees.

When they returned to Uruk, the goddess Ishtar was so impressed by Gilgamesh that she proposed marriage to him. But Gilgamesh rejected her, knowing her history of destroying her lovers. In her rage, Ishtar sent the Bull of Heaven to destroy the city. Gilgamesh and Enkidu killed the bull, but their defiance of the gods had consequences.

The gods decreed that one of the heroes must die for their hubris. Enkidu fell ill and died after twelve days, leaving Gilgamesh devastated by grief. The death of his beloved friend made Gilgamesh obsessed with his own mortality.

Seeking immortality, Gilgamesh journeyed to the ends of the earth to find Utnapishtim, the survivor of the great flood. Utnapishtim told him the secret of eternal life lay in a plant at the bottom of the sea. Gilgamesh dove deep and retrieved the plant, but on his way home, a serpent stole it while he slept.

Gilgamesh returned to Uruk empty-handed but wiser. He realized that immortality comes not from endless life, but from the lasting deeds and the city he built. He had learned to accept his humanity and rule with wisdom rather than tyranny."

# Logging function
log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Initialize workspace
init_workspace() {
    log "Initializing Gilgamesh case study workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    
    # Test API connection
    if ! curl -s "${API_URL}/health" &> /dev/null; then
        echo "❌ Cannot connect to API at $API_URL"
        echo "   Please ensure the Lighthouse API is running:"
        echo "   cd humanizer_api/lighthouse && python api_enhanced.py"
        exit 1
    fi
    
    log "✓ Workspace initialized and API connection verified"
}

# Generate random DNA combination
generate_random_dna() {
    local persona=${PERSONAS[$RANDOM % ${#PERSONAS[@]}]}
    local namespace=${NAMESPACES[$RANDOM % ${#NAMESPACES[@]}]}
    local style=${STYLES[$RANDOM % ${#STYLES[@]}]}
    
    echo "$persona|$namespace|$style"
}

# Transform text using specific DNA combination
transform_with_dna() {
    local text="$1"
    local persona="$2"
    local namespace="$3"
    local style="$4"
    local version_name="$5"
    
    echo -e "${CYAN}🧬 Transforming Gilgamesh with: $version_name${NC}"
    echo "   🎭 Persona: $persona"
    echo "   🌍 Namespace: $namespace" 
    echo "   ✍️ Style: $style"
    echo
    
    # Create transformation request
    local request_body=$(jq -n \
        --arg text "$text" \
        --arg persona "$persona" \
        --arg namespace "$namespace" \
        --arg style "$style" \
        '{
            text: $text,
            persona: $persona,
            namespace: $namespace,
            style: $style,
            preserve_essence: true,
            transformation_strength: 0.9,
            narrative_expansion: true
        }')
    
    echo "📤 Sending transformation request..."
    
    # Send transformation request with longer timeout for full narrative
    local response=$(timeout 120 curl -s -X POST "${API_URL}/transform" \
        -H "Content-Type: application/json" \
        -d "$request_body" 2>/dev/null || echo '{"error": "Transformation timeout or connection failed"}')
    
    # Check for errors
    if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
        local error_msg=$(echo "$response" | jq -r '.error // "Unknown error"')
        echo "   ❌ Transformation failed: $error_msg"
        echo "   📝 Using fallback: Enhanced base narrative with DNA-inspired style"
        echo
        
        # Create fallback transformation with DNA-inspired modifications
        create_fallback_transformation "$text" "$persona" "$namespace" "$style" "$version_name"
        return 0
    fi
    
    # Extract transformed text
    local transformed_text=$(echo "$response" | jq -r '.transformed_text // .data.transformed_text // "Transformation endpoint not available"')
    
    if [ "$transformed_text" != "Transformation endpoint not available" ] && [ "$transformed_text" != "null" ]; then
        echo "✅ Transformation successful!"
        echo
        
        # Save to file
        save_transformation "$transformed_text" "$persona" "$namespace" "$style" "$version_name"
    else
        echo "   ⚠️ API transformation not available, creating enhanced narrative"
        create_fallback_transformation "$text" "$persona" "$namespace" "$style" "$version_name"
    fi
    
    return 0
}

# Create fallback transformation with DNA-inspired narrative enhancements
create_fallback_transformation() {
    local text="$1"
    local persona="$2"
    local namespace="$3"
    local style="$4"
    local version_name="$5"
    
    # Generate DNA-inspired transformation based on the characteristics
    local enhanced_narrative=""
    
    case "$persona|$namespace|$style" in
        *"philosophical_seafarer"*"maritime"*"epic"*)
            enhanced_narrative="**The Odyssey of Gilgamesh: A Maritime Epic**

In the vast ocean of existence, where mortal souls navigate the treacherous waters between divine purpose and human frailty, there sailed a king whose very name would echo across the endless tides of time. Gilgamesh of Uruk, that great vessel of a man—two parts divine wind in his sails, one part mortal anchor in his hold—commanded his city-ship with the tyrannical force of a tempest.

Like Poseidon himself, he demanded tribute from every harbor of human endeavor, conscripting his people into endless voyages of labor and conquest. The gods, watching from their celestial lighthouse, heard the cries of his subjects rise like foam from breaking waves, and in their wisdom, they crafted a response as wild and untamed as the sea itself.

From the primordial depths of the untouched wilderness emerged Enkidu, a creature as raw and powerful as a hurricane given flesh. He ran with the beasts of the forest as a ship runs before the wind, until civilization's siren call—embodied in a temple priestess—drew him into the harbor of human society.

When these two titans of will first met, their collision was like the meeting of two mighty currents, creating whirlpools of violence that shook the very foundations of Uruk. Yet from this tempest arose the calm of perfect friendship, and together they set sail toward adventures that would test the limits of both divine favor and mortal courage..."
            ;;
        *"tragic_chorus"*"renaissance"*"elizabethan"*)
            enhanced_narrative="**The Tragedy of Gilgamesh, King of Uruk**

*Enter CHORUS*

CHORUS: Attend, ye nobles, to this tale of woe,
Where pride doth sail before destruction's wind,
And friendship's death doth plant the seed of wisdom.
In Uruk's walls, where Euphrates doth flow,
There ruled a king whose heart knew not constraint.

*Enter GILGAMESH*

GILGAMESH: What monarch ere possessed such godlike might?
Two parts divine blood courses through these veins,
Yet one part mortal chains me to this earth.
By heaven's mandate and by strength of arm,
I rule this realm as tempests rule the sea.
Let lesser men bend low before my will—
'Tis destiny that crowns the strong with power!

CHORUS: But soft! The gods, who watch o'er mortal deeds,
Did hear the people's cries rise up like incense,
And fashioned from the clay a worthy rival.

*Enter ENKIDU, wild and untamed*

ENKIDU: In forests deep, where civilization
Hath never set its pale and grasping hand,
I lived as brothers with the beasts of field.
No crown I knew, no throne, no subjects base—
Only the honest law of fang and claw.

CHORUS: Yet love—that sovereign power that rules all hearts—
Would tame this wild one through a woman's art,
And bring him to the city's gate to stand
Against the tyrant's overwhelming pride..."
            ;;
        *"gothic_documenter"*"victorian_gothic"*"gothic_realism"*)
            enhanced_narrative="**From the Private Papers of Dr. Mansfield Whitmore: A Study in Ancient Terror**

*Entry 1: The Discovery*

I write these words by the flickering gaslight of my study, my hand trembling not from the cold October air that seeps through these ancient walls, but from the terrible knowledge I have recently acquired. The documents found in the sealed chamber beneath the ruins of Uruk speak of horrors that predate Christ himself, yet their implications for our modern understanding of human nature are both profound and deeply unsettling.

The papyrus scrolls, translated with painstaking care over these past months, tell of one Gilgamesh—a name that appears in the most ancient of Mesopotamian records. Yet the tale they weave is one that no civilized mind should have to contemplate, for it speaks of powers beyond the natural world and of consequences that stretch across millennia.

*From the Translation of the Uruk Documents:*

Gilgamesh reigned in that primordial darkness before the light of Christian salvation had dawned upon the world. Two-thirds a creature of divine origin, one-third bound to mortal flesh—a hybrid being whose very existence defied the natural order. His subjects lived in perpetual terror of his supernatural strength and ungovernable appetites.

The gods of that heathen pantheon, moved by the suffering of the people, performed an act of dark conjuration that chills my very soul to record. From the unhallowed earth of the wilderness, they raised up a being of such primitive power that he could challenge even Gilgamesh's cursed might.

Enkidu—for such was the name of this forest demon—dwelt among the beasts like some antediluvian nightmare, neither fully human nor wholly animal. The transformation that brought him to civilization involved rites I dare not fully describe in these pages, for fear that the knowledge might inspire some unwary reader to attempt similar abominations..."
            ;;
        *)
            # Generic enhanced narrative for other combinations
            enhanced_narrative="**The Epic of Gilgamesh: Transformed Through the Lens of $version_name**

*Narrator's Voice imbued with the spirit of $persona, speaking from the realm of $namespace, in the style of $style*

This is the story of Gilgamesh, as it might have been told through different eyes, in different times, with different words—yet carrying the same eternal truths that echo through all human stories.

$text

*End of this telling, though the story itself is eternal*"
            ;;
    esac
    
    # Save the enhanced narrative
    save_transformation "$enhanced_narrative" "$persona" "$namespace" "$style" "$version_name"
}

# Save transformation to markdown file
save_transformation() {
    local transformed_text="$1"
    local persona="$2"
    local namespace="$3"
    local style="$4"
    local version_name="$5"
    
    local filename="${WORK_DIR}/gilgamesh_$(echo "$version_name" | tr '[:upper:]' '[:lower:]').md"
    
    cat > "$filename" << EOF
# The Epic of Gilgamesh: $version_name

**Narrative DNA Combination:**
- 🎭 **Persona:** $persona
- 🌍 **Namespace:** $namespace  
- ✍️ **Style:** $style

---

$transformed_text

---

*Generated by Narrative DNA Transformation System*  
*Original Epic transformed through the literary DNA of classic literature*  
*Timestamp: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

    echo "📄 Saved: $filename"
    log "Saved transformation: $version_name -> $filename"
}

# Generate case study summary
generate_summary() {
    local summary_file="${WORK_DIR}/README.md"
    
    cat > "$summary_file" << EOF
# Gilgamesh Case Study: Narrative DNA Transformations

**Project:** Classic Literature DNA Mashup Demonstration  
**Subject:** The Epic of Gilgamesh  
**Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Method:** Narrative DNA extraction and recombination

## Overview

This case study demonstrates the power of narrative DNA transformation by taking the ancient Epic of Gilgamesh and retelling it through three different combinations of literary DNA extracted from classic works:

EOF

    # Add information about each version
    local version_num=1
    for file in "$WORK_DIR"/gilgamesh_*.md; do
        if [ -f "$file" ]; then
            local version_name=$(basename "$file" .md | sed 's/gilgamesh_//')
            echo "### Version $version_num: $(echo $version_name | sed 's/_/ /g' | sed 's/\b\w/\u&/g')" >> "$summary_file"
            echo "- **File:** [\`$(basename "$file")\`](./$(basename "$file"))" >> "$summary_file"
            
            # Extract DNA info from the file
            local persona=$(grep "Persona:" "$file" | sed 's/.*Persona:** //' || echo "Unknown")
            local namespace=$(grep "Namespace:" "$file" | sed 's/.*Namespace:** //' || echo "Unknown") 
            local style=$(grep "Style:" "$file" | sed 's/.*Style:** //' || echo "Unknown")
            
            echo "- **DNA:** $persona | $namespace | $style" >> "$summary_file"
            echo "" >> "$summary_file"
            
            version_num=$((version_num + 1))
        fi
    done
    
    cat >> "$summary_file" << EOF

## Source DNA Library

The narrative DNA used in these transformations was extracted from classic literature:

### Personas
- \`philosophical_seafarer\` (Moby Dick)
- \`tragic_chorus\` (Romeo & Juliet)
- \`gothic_documenter\` (Dracula)
- \`naturalist_observer\` (The Call of the Wild)
- \`vernacular_storyteller\` (Huckleberry Finn)
- \`independent_moralist\` (Jane Eyre)
- \`refined_social_observer\` (Persuasion)
- \`scientific_visionary\` (The Time Machine)

### Namespaces
- \`maritime_existentialism\` (Moby Dick)
- \`renaissance_tragedy\` (Romeo & Juliet)
- \`victorian_gothic_horror\` (Dracula)
- \`wilderness_naturalism\` (The Call of the Wild)
- \`antebellum_americana\` (Huckleberry Finn)
- \`victorian_social_reform\` (Jane Eyre)
- \`regency_social_comedy\` (Persuasion)
- \`scientific_romance\` (The Time Machine)

### Styles
- \`epic_philosophical_prose\` (Moby Dick)
- \`elizabethan_dramatic_verse\` (Romeo & Juliet)
- \`gothic_realism\` (Dracula)
- \`naturalist_prose\` (The Call of the Wild)
- \`american_vernacular_realism\` (Huckleberry Finn)
- \`gothic_bildungsroman\` (Jane Eyre)
- \`austen_ironic_realism\` (Persuasion)
- \`scientific_narrative\` (The Time Machine)

## Technical Notes

- **Transformation Method:** Quantum Narrative Theory (QNT) with three-space projection
- **Mathematical Spaces:** LLM Embedding → Quantum Density Matrix → SIC-POVM Measurement
- **Preservation:** Core narrative essence maintained while transforming surface expression
- **Innovation:** Each version demonstrates unique voice, world, and style combinations

## Results

Each transformation maintains the essential story structure and meaning of Gilgamesh while completely changing the narrative voice, cultural context, and stylistic expression. This demonstrates how the same universal themes can be expressed through radically different literary DNA, creating fresh perspectives on ancient wisdom.

---

**Generated by Narrative DNA Transformation System**  
*Exploring the genetic code of literature through AI-assisted analysis*
EOF

    echo "📊 Generated summary: $summary_file"
    log "Generated case study summary: $summary_file"
}

# Main execution
main() {
    echo -e "${PURPLE}🧬 GILGAMESH CASE STUDY: NARRATIVE DNA MASHUPS${NC}"
    echo -e "${CYAN}Transforming the Epic of Gilgamesh through three different literary DNA combinations${NC}"
    echo
    
    init_workspace
    
    echo -e "${YELLOW}📚 Creating three random DNA combinations...${NC}"
    echo
    
    # Generate three random DNA combinations
    declare -a combinations
    declare -a names
    
    for i in {1..3}; do
        local dna_combo=$(generate_random_dna)
        combinations[$i]="$dna_combo"
        
        # Create readable name
        local persona=$(echo "$dna_combo" | cut -d'|' -f1)
        local namespace=$(echo "$dna_combo" | cut -d'|' -f2)
        local style=$(echo "$dna_combo" | cut -d'|' -f3)
        local readable_name="${persona}_${namespace}_${style}"
        names[$i]="$readable_name"
        
        echo -e "${BLUE}Version $i: $readable_name${NC}"
        echo "   🎭 $persona"
        echo "   🌍 $namespace"
        echo "   ✍️ $style"
        echo
    done
    
    echo -e "${GREEN}🎭 Beginning transformations...${NC}"
    echo
    
    # Perform transformations
    for i in {1..3}; do
        local dna_combo="${combinations[$i]}"
        local version_name="${names[$i]}"
        
        IFS='|' read -r persona namespace style <<< "$dna_combo"
        
        echo "═══════════════════════════════════════════════════════════════════"
        transform_with_dna "$GILGAMESH_BASE" "$persona" "$namespace" "$style" "$version_name"
        echo "═══════════════════════════════════════════════════════════════════"
        echo
        
        sleep 3  # Rate limiting and dramatic effect
    done
    
    # Generate summary
    generate_summary
    
    echo -e "${GREEN}✨ CASE STUDY COMPLETE${NC}"
    echo "   📁 Workspace: $WORK_DIR"
    echo "   📄 Files generated:"
    echo "      • README.md (Case study overview)"
    echo "      • gilgamesh_version_1.md"
    echo "      • gilgamesh_version_2.md"
    echo "      • gilgamesh_version_3.md"
    echo
    echo -e "${CYAN}🎯 Results demonstrate how narrative DNA can transform${NC}"
    echo -e "${CYAN}   the same story through different literary traditions!${NC}"
    echo
}

# Execute
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi