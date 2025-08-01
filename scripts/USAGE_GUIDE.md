# Narrative DNA System - Usage Guide

## 🚨 Fixed Interface Issue

The original "Windows Commander" style interface was broken and unusable. I've replaced it with a **functional menu-driven interface** that actually works.

## 🚀 How to Use the System

### 1. Quick Access to Rich DNA Content

Instead of the broken dashboard, use these **working commands**:

```bash
# Launch functional browser
./launcher.sh commander

# Or use direct commands:
./launcher.sh inspect list                    # See all DNA extractions
./launcher.sh inspect browse                  # Interactive browser
./launcher.sh inspect show <file.json>        # Detailed analysis
./launcher.sh inspect prompts <file.json>     # Transformation prompts
```

### 2. What You Were Missing - Rich DNA Content

The "duplicates" you saw were actually **simplified labels** hiding rich data:

**Simple view:** `gothic_documenter|victorian_gothic_horror|gothic_realism`

**Rich content includes:**
- **Confidence scores:** 0.84, 0.89, 0.87
- **Voice patterns:** epistolary_multiple, omniscient_dramatic
- **Characteristics:** supernatural_dread, scientific_rationalism, moral_certainty
- **Domain markers:** supernatural_forces, scientific_progress, colonial_anxieties
- **Linguistic features:** atmospheric_descriptions, suspenseful_pacing
- **Cultural context:** victorian_england_modernity_clash
- **Analysis metadata:** 64 paragraphs analyzed, 0.84 pattern consistency

### 3. Step-by-Step Usage

#### Step 1: Check System Status
```bash
./launcher.sh status
```

#### Step 2: Browse Available DNA
```bash
./launcher.sh commander
# Choose option 1: List all DNA files
```

#### Step 3: View Detailed Analysis
```bash
./launcher.sh commander  
# Choose option 2: Show detailed DNA analysis
# Enter file path when prompted
```

#### Step 4: See Transformation Prompts
```bash
./launcher.sh commander
# Choose option 3: Show transformation prompts
```

### 4. Command Line Shortcuts

```bash
# Direct detailed analysis
./launcher.sh inspect show expanded_attributes_20250728_003252/narrative_dna_345.json

# View transformation prompts
./launcher.sh inspect prompts expanded_attributes_20250728_003252/narrative_dna_1513.json

# Compare multiple DNA files
./launcher.sh inspect compare file1.json file2.json

# List all available extractions
./launcher.sh inspect list
```

### 5. Understanding the Rich Data Structure

Each DNA file contains:

```json
{
  "data": {
    "results": {
      "narrative_dna": {
        "dominant_persona": {
          "name": "gothic_documenter",
          "confidence": 0.84,
          "characteristics": ["supernatural_dread", "scientific_rationalism"],
          "voice_pattern": "epistolary_multiple",
          "frequency": 0.76
        },
        "consistent_namespace": {
          "name": "victorian_gothic_horror", 
          "confidence": 0.89,
          "domain_markers": ["supernatural_forces", "scientific_progress"],
          "cultural_context": "victorian_england_modernity_clash"
        },
        "predominant_style": {
          "name": "gothic_realism",
          "confidence": 0.87,
          "linguistic_features": ["atmospheric_descriptions", "suspenseful_pacing"],
          "tone": "ominous_methodical"
        },
        "core_essence": {
          "thematic_consistency": 0.82,
          "meaning_density": 0.75,
          "philosophical_depth": 0.73
        }
      }
    }
  }
}
```

### 6. Vector Spaces (Currently Mock Data)

The system references three mathematical spaces:

1. **LLM Embedding Space** (1536-dimensional vectors)
2. **Quantum Density Matrix** (8×8 Hermitian matrices)  
3. **SIC-POVM Measurement** (24-dimensional probability simplex)

```bash
# View vector analysis (currently shows framework)
./launcher.sh inspect vectors <file.json> embedding
./launcher.sh inspect vectors <file.json> density
./launcher.sh inspect vectors <file.json> povm
```

### 7. Transformation with Rich Context

When you transform text, the system uses **all the rich metadata**:

```bash
# Transform using rich DNA context
./launcher.sh transform 'gothic_documenter|victorian_gothic_horror|gothic_realism' 'Hello world'
```

The transformation internally uses:
- **Voice pattern:** epistolary_multiple
- **Characteristics:** supernatural_dread, scientific_rationalism
- **Domain markers:** supernatural_forces, scientific_progress
- **Linguistic features:** atmospheric_descriptions, suspenseful_pacing
- **Cultural context:** victorian_england_modernity_clash

### 8. Working Menu Interface

The functional browser provides:

```
=== DNA Browser Main Menu ===
1. List all DNA files
2. Show detailed DNA analysis  
3. Show transformation prompts
4. Compare DNA files
5. Search by book title
6. System status
7. Quick extract new DNA
0. Exit
```

**This actually works** - no broken keyboard navigation, just simple menu choices.

### 9. Practical Examples

#### View Dracula's DNA in Detail:
```bash
./launcher.sh commander
# Choose 2 (detailed analysis)
# Enter: expanded_attributes_20250728_003252/narrative_dna_345.json
```

#### Compare Shakespeare vs Stoker:
```bash
./launcher.sh commander
# Choose 4 (compare)
# Enter: path/to/narrative_dna_1513.json path/to/narrative_dna_345.json
```

#### Search for Jane Austen books:
```bash
./launcher.sh commander
# Choose 5 (search)
# Enter: Austen
```

## 🎯 Summary

- ❌ **Broken:** Windows Commander interface (unusable)
- ✅ **Working:** Menu-driven browser + direct commands
- 🔍 **Rich data:** Confidence scores, characteristics, linguistic features
- 🧬 **DNA depth:** Voice patterns, cultural context, domain markers
- 📊 **Analysis:** 64 paragraphs, pattern consistency, coherence metrics
- 🤖 **Vectors:** Framework for 3 mathematical spaces
- 🔧 **Functional:** Simple menus that actually respond to input

The system now provides full access to the rich narrative DNA content through a **working interface** instead of the broken dashboard.