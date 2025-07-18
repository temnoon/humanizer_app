# 🔦 Humanizer Lighthouse API

The single brilliant beacon that demonstrates the core magic of narrative transformation.

## What is the Lighthouse?

The Lighthouse is a focused, beautiful demonstration of the Lamish Projection Engine's power. It takes any text and:

1. **Deconstructs** it into its essence and subjective layers (Persona Ψ, Namespace Ω, Style Σ)
2. **Visualizes** these components in an intuitive way
3. **Allows transformation** through different personas, namespaces, and styles
4. **Shows the magic** of how meaning can be preserved while expression transforms

## Quick Start

```bash
# 1. Navigate to the lighthouse directory
cd ~/humanizer_api/lighthouse

# 2. Copy and configure environment
cp .env.example .env
# Edit .env and add at least one LLM API key

# 3. Start the API
./start.sh
```

The API will be available at: http://localhost:8100

## Core Endpoints

### 1. Deconstruct a Narrative
```bash
POST /deconstruct
{
  "narrative": "The team struggled with the deadline, but their determination saw them through."
}
```

Returns the essence and detected layers:
```json
{
  "essence": "A group faced time pressure but succeeded through persistence",
  "detected_persona": "optimistic",
  "detected_namespace": "earth-2024",
  "detected_style": "conversational",
  "entities": ["team", "deadline", "determination"],
  "themes": ["perseverance", "teamwork", "success"],
  "linguistic_features": {
    "formality": "medium",
    "complexity": "low",
    "emotional_tone": "encouraging"
  }
}
```

### 2. Transform in One Call
```bash
POST /transform
{
  "narrative": "The team struggled with the deadline...",
  "target_persona": "philosopher",
  "target_namespace": "lamish-galaxy",
  "target_style": "poetic"
}
```

Returns both the deconstruction and the new projection.

### 3. Get Available Options
```bash
GET /options
```

Returns all available personas, namespaces, and styles with descriptions.

## Available Transformations

### Personas (Ψ)
- **philosopher**: Contemplative, seeking deeper meanings
- **poet**: Aesthetic, metaphorical, emotionally resonant
- **scientist**: Analytical, precise, evidence-based
- **journalist**: Factual, balanced, investigative
- **child**: Wonder-filled, innocent, imaginative
- **mystic**: Spiritual, symbolic, transcendent
- **cynic**: Skeptical, critical, questioning
- **optimist**: Hopeful, positive, possibility-focused

### Namespaces (Ω)
- **earth-2024**: Contemporary world with current references
- **lamish-galaxy**: Cosmic civilization of light and wisdom
- **cosmic-ocean**: Universe as vast ocean of consciousness
- **digital-realm**: Reality as computational substrate
- **dreamscape**: Surreal landscape of subconscious
- **ancient-myths**: Timeless stories and archetypes
- **future-utopia**: Optimistic vision of tomorrow
- **quantum-reality**: Probabilistic, observer-dependent world

### Styles (Σ)
- **academic**: Formal, structured, citation-heavy
- **poetic**: Lyrical, rhythmic, imagery-rich
- **conversational**: Casual, friendly, accessible
- **technical**: Precise, jargon-filled, systematic
- **mythological**: Epic, archetypal, timeless
- **minimalist**: Spare, essential, stripped-down
- **baroque**: Ornate, complex, elaborate
- **stream-of-consciousness**: Flowing, associative, unfiltered

## The Lamish Pulse Protocol

When enabled, each transformation is signed with a unique cryptographic signature based on prime number sequences. This creates an unforgeable "seal of authenticity" for transformed content.

## Architecture

```
┌─────────────────────────────────────────┐
│           Input Narrative               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Deconstruction                 │
│   • Extract Essence (N_E)               │
│   • Identify Persona (Ψ)                │
│   • Detect Namespace (Ω)                │
│   • Analyze Style (Σ)                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Projection                     │
│   • Apply new Persona                   │
│   • Translate to new Namespace          │
│   • Render in new Style                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Lamish Pulse Signature             │
│   • Generate cryptographic proof        │
│   • Timestamp and seal                  │
└─────────────────────────────────────────┘
```

## Next Steps

1. **Build the Web Interface**: A beautiful, interactive UI that visualizes the transformation
2. **Add More Namespaces**: Let users create custom universes
3. **Enhance the Diff Viewer**: Show exactly what changed in the transformation
4. **Connect to Discourse**: Add "Post to Lamen" functionality

## Philosophy

The Lighthouse embodies the core insight: **communication consists of essence wrapped in layers of subjectivity**. By making these layers visible and editable, we enable new forms of understanding and expression.

This is not just a tool—it's an instrument for thought that reveals how meaning and expression can be separated and recombined in infinite ways.

## Support

Built with ❤️ for the Humanizer project.
