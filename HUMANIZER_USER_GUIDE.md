# Humanizer App User Guide

## Introduction to the Humanizer Platform

The Humanizer platform is a complete narrative transformation system that combines AI-powered content analysis with quantum-aware projection techniques. It enables you to discover the "DNA" of great literature and apply those patterns to transform any text while preserving its essential meaning.

## Core Workflow: From Essay to Projection

The Humanizer workflow consists of three main phases:

### Phase 1: Attribute Discovery (DNA Extraction)
First, the system analyzes great literature to discover narrative "DNA" patterns - the underlying structures that make writing compelling.

### Phase 2: Attribute Sampling & Selection  
You review the discovered attributes and select the ones that match your desired transformation goals.

### Phase 3: Narrative Projection
Your original text is transformed using the selected DNA patterns while preserving its essential meaning and intent.

---

## Getting Started

### Prerequisites
Ensure you have the Humanizer platform installed and the environment properly configured:

```bash
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
```

---

## Command Reference

### 1. Allegory CLI - DNA Discovery & Curation

**Command:** `python allegory_cli.py curate`

**Purpose:** Extract narrative DNA from classic literature to build your attribute library.

#### Basic Usage:
```bash
# Extract attributes from specific books
python allegory_cli.py curate --book-ids 1342 11 84 --max-paras 100 --out ./curated

# Process multiple books with more paragraphs
python allegory_cli.py curate --book-ids 74 76 345 --max-paras 200 --out ./my_attributes
```

#### Advanced Options:
```bash
# Custom selection weights for attribute quality
python allegory_cli.py curate \
  --book-ids 1342 11 \
  --max-paras 150 \
  --resonance-weight 1.2 \
  --clarity-weight 0.8 \
  --essence-weight 1.0 \
  --out ./premium_attributes
```

#### Parameters:
- `--book-ids`: Gutenberg book IDs (1342=Pride & Prejudice, 11=Alice in Wonderland, 84=Frankenstein)
- `--max-paras`: Maximum paragraphs to extract per book (default: 200)
- `--out`: Output directory for discovered attributes
- `--resonance-weight`: How much to weight narrative resonance (default: 1.0)
- `--info-gain-weight`: Weight for information richness (default: 1.0)  
- `--clarity-weight`: Weight for text clarity (default: 0.3)
- `--essence-weight`: Weight for essence strength (default: 0.8)

#### Output:
- `book_ID_curated.json`: Complete attribute data for each book
- `book_ID_anchors.jsonl`: Structured anchor data for each paragraph
- `curation_manifest.json`: Master index of all processed content

---

### 2. Attribute Browser & Selection

**Command:** `python simple_projection_demo.py`

**Purpose:** Browse and test discovered attributes before applying them to your content.

#### Usage:
```bash
# Demo mode - see sample projections
python simple_projection_demo.py --demo

# Interactive mode - test your own text
python simple_projection_demo.py --interactive
```

#### Interactive Workflow:
1. Enter your text when prompted
2. System randomly selects 3 attributes from your library
3. Shows side-by-side transformations using different DNA patterns
4. Compare results to choose your preferred style

---

### 3. Full Projection Engine

**Command:** `python narrative_projection_engine.py`

**Purpose:** Advanced narrative transformation with precise control over projection parameters.

#### Basic Usage:
```bash
# Project using specific DNA parameters
python narrative_projection_engine.py \
  --input "Your essay text here" \
  --persona "victorian_narrator" \
  --namespace "classical_literature" \
  --style "prose_narrative" \
  --strength 0.8
```

#### Parameters:
- `--input`: Your original text to transform
- `--persona`: Voice/perspective (e.g., "tragic_chorus", "cyberpunk_hacker", "victorian_narrator")
- `--namespace`: Reference universe (e.g., "classical_literature", "sci_fi", "modern_literary")
- `--style`: Writing style (e.g., "prose_narrative", "dialogue_heavy", "descriptive")
- `--strength`: Projection intensity (0.1-1.0, default: 0.8)
- `--preserve-essence`: How much to preserve original meaning (0.1-1.0, default: 0.9)

---

## Complete Workflow Example

Here's how to perform a full essay transformation from start to finish:

### Step 1: Discover Attributes
```bash
# Extract DNA from classic novels
python allegory_cli.py curate \
  --book-ids 1342 11 84 74 \
  --max-paras 150 \
  --out ./my_essay_attributes
```

### Step 2: Browse & Test Attributes  
```bash
# Test with sample text
python simple_projection_demo.py --interactive
```

When prompted, enter: *"I was walking through the forest when I heard strange sounds. My phone was almost dead and I couldn't call my dad."*

The system will show 3 different transformations, such as:
- **Victorian Style**: *"I found myself traversing the woodland when peculiar sounds reached my ears. My communication device was nearly depleted of energy and I could not reach my father."*
- **Classical Literature**: *"I found myself wandering through the shadowed wood when mysterious whispers caught my attention. My device had nearly expired, leaving me unable to summon aid from my father."*

### Step 3: Apply Full Projection
```bash
# Use your preferred discovered pattern
python narrative_projection_engine.py \
  --input "Your full essay text here..." \
  --persona "victorian_narrator" \
  --namespace "classical_literature" \
  --style "prose_narrative" \
  --strength 0.75 \
  --preserve-essence 0.9
```

---

## Understanding DNA Components

### Persona (Ψ)
The voice and perspective of the narrator:
- `extracted_narrator`: Classical literature narrator
- `tragic_chorus`: Greek drama collective voice  
- `cyberpunk_hacker`: Tech-noir protagonist
- `victorian_narrator`: 19th century formal narrator

### Namespace (Ω) 
The universe of references and concepts:
- `classical_literature`: Timeless literary references
- `modern_urban`: Contemporary city life
- `sci_fi`: Futuristic/technological concepts
- `historical`: Period-specific references

### Style (Σ)
The linguistic and structural approach:
- `prose_narrative`: Flowing descriptive text
- `dialogue_heavy`: Conversation-focused
- `stream_consciousness`: Internal thought flow
- `descriptive`: Rich sensory detail

---

## Tips for Best Results

### Attribute Discovery:
- Start with books similar to your target style
- Use 100-200 paragraphs per book for good coverage
- Experiment with different resonance weights to match your goals

### Projection:
- Start with lower strength (0.6-0.7) and increase gradually
- Keep essence preservation high (0.8-0.95) to maintain meaning
- Test with short passages before processing full essays

### Quality Control:
- Always review projected text for coherence
- Compare multiple projections to find the best fit
- Fine-tune parameters based on output quality

---

## Troubleshooting

### Common Issues:

**"No attributes found"**
- Ensure you've run the curation step first
- Check that output directory contains .json files
- Verify file permissions

**"Poor projection quality"**  
- Lower projection strength (0.5-0.7)
- Increase essence preservation (0.9+)
- Try different persona/namespace combinations

**"Attributes not loading"**
- Check file paths match between curation and projection
- Ensure JSON files are valid and complete
- Verify environment is properly activated

---

## Next Steps

Once comfortable with the basic workflow:

1. **Build Custom Libraries**: Curate attributes from genres matching your writing goals
2. **Experiment with Blending**: Combine multiple DNA patterns for unique voices  
3. **Develop Style Profiles**: Create reusable parameter sets for consistent transformations
4. **Scale Processing**: Apply to longer documents and batch processing

The Humanizer platform grows more powerful as you build larger, more targeted attribute libraries. Each new book you process adds to your creative toolkit for narrative transformation.