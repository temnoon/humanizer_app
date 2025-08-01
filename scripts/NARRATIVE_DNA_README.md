# Narrative DNA Extractor 🧬

Advanced system for extracting the "narrative DNA" of classic literature through strategic paragraph sampling and composite Quantum Narrative Theory (QNT) analysis.

## 🎯 Concept: Narrative DNA

**Narrative DNA** represents the consistent, identifiable patterns that define a book's unique narrative character:

- **🎭 Dominant Persona** - The primary narrative voice and perspective that persists throughout
- **🌍 Consistent Namespace** - The cultural, temporal, and domain context that frames the narrative
- **✍️ Predominant Style** - The linguistic and rhetorical approach that characterizes the prose  
- **💎 Core Essence** - The thematic purpose and invariant elements that give the work meaning

Unlike analyzing famous opening lines or climactic scenes, this system focuses on the "low profile" middle sections that reveal the book's true narrative character.

## 🎯 Strategic Sampling Approach

### Selection Criteria
- **64 paragraphs** scattered across the book
- **Middle 70%** of the text (avoiding first/last 15% with iconic passages)
- **150-600 characters** in length (substantial but not excessive)
- **Low dialogue ratio** - focus on narrative voice, not character speech
- **Rich description** - scenery, introspection, commentary
- **Narrative commentary** - author's voice and perspective

### Paragraph Types Targeted
1. **Descriptive Scenery** - Environmental and atmospheric passages
2. **Character Introspection** - Internal thoughts and reflections
3. **Narrative Commentary** - Author's voice and observations
4. **Dialogue with Context** - Conversations embedded in rich narrative
5. **Philosophical Reflection** - Deeper meaning and thematic content

## 🔧 Technical Implementation

### API Endpoints

#### 1. Strategic Sampling
```bash
POST /gutenberg/strategic-sample
```
**Request:**
```json
{
  "gutenberg_id": 1342,
  "sample_count": 64,
  "min_length": 150,
  "max_length": 600,
  "avoid_first_last_percent": 0.15
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "abc123...",
    "gutenberg_id": 1342,
    "sample_count": 64,
    "status": "pending"
  }
}
```

#### 2. Composite Analysis
```bash
POST /gutenberg/composite-analysis?job_id={sampling_job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "composite_job_id": "def456...",
    "source_job_id": "abc123...",
    "analysis_type": "narrative_dna_extraction",
    "status": "pending"
  }
}
```

### Process Flow

1. **Strategic Sampling Job**
   - Downloads book from Project Gutenberg
   - Parses text into paragraphs
   - Applies selection criteria to find "low profile" narrative-rich paragraphs
   - Returns 64 strategically chosen samples

2. **Composite Analysis Job**
   - Performs QNT analysis on each strategic paragraph
   - Identifies patterns and consistency across samples
   - Extracts dominant narrative DNA elements
   - Provides confidence scores and frequency metrics

## 🚀 Usage

### Quick Test
```bash
cd /Users/tem/humanizer-lighthouse/scripts

# Test the new endpoints
./test_narrative_dna.sh
```

### Full Narrative DNA Extraction
```bash
# Extract narrative DNA from 5 classic books
./narrative_dna_extractor.sh
```

### Custom Book Analysis
You can modify the book list in `narrative_dna_extractor.sh` or create custom analysis:

```bash
# Example: Analyze a specific book
gutenberg_id=1342  # Pride and Prejudice
book_title="Pride and Prejudice"

# The script will:
# 1. Create strategic sampling job
# 2. Wait for completion
# 3. Create composite analysis job  
# 4. Extract and display narrative DNA
# 5. Generate detailed report
```

## 📊 Output Examples

### Narrative DNA Results
```
🧬 NARRATIVE DNA: Pride and Prejudice
════════════════════════════════════════════════════════

🎭 DOMINANT PERSONA:
  Name: contemplative_observer
  Confidence: 87.0%
  Frequency: 73.0%
  Characteristics: philosophical_reflection, descriptive_precision, emotional_depth

🌍 CONSISTENT NAMESPACE:
  Name: literary_realism
  Confidence: 82.0%
  Frequency: 68.0%
  Cultural Context: 19th_century_literary_tradition

✍️ PREDOMINANT STYLE:
  Name: elevated_prose
  Confidence: 85.0%
  Frequency: 79.0%
  Tone: reflective_authoritative

💎 CORE ESSENCE:
  Narrative Purpose: exploration_of_human_condition
  Thematic Consistency: 83.0%
  Meaning Density: 76.0%
```

### Generated Files

Each analysis creates:

- **`narrative_dna_report_{id}.md`** - Detailed individual book report
- **`sampling_results_{id}.json`** - Strategic paragraph sampling data
- **`narrative_dna_{id}.json`** - Complete DNA analysis results
- **`narrative_dna_summary.md`** - Project overview and summary

## 🎯 Applications

### 1. Content Transformation
Use extracted DNA to transform modern text to match classic narrative voices:

```bash
# Apply Pride and Prejudice narrative DNA to modern content
humanizer transform "The meeting was scheduled for 3 PM" \
  --persona "contemplative_observer" \
  --namespace "literary_realism" \
  --style "elevated_prose"
```

### 2. Literary Analysis
- Compare narrative DNA across different authors and periods
- Track evolution of narrative techniques over time
- Identify influence patterns between works
- Classify unknown texts by similarity to known DNA patterns

### 3. Writing Assistance
- Guide authors toward specific narrative styles
- Provide templates for achieving particular narrative voices
- Analyze draft text for consistency with target DNA
- Suggest improvements to match desired narrative character

### 4. AI Training
- Create training datasets for narrative voice classification
- Build style transfer models using DNA as ground truth
- Develop content recommendation systems based on narrative similarity
- Train authorship attribution models using DNA features

## 🔬 Scientific Approach

### Quality Metrics
- **Pattern Consistency:** >80% across strategic samples
- **Narrative Coherence:** >85% thematic alignment
- **Confidence Thresholds:** Minimum 70% for DNA element inclusion
- **Frequency Analysis:** Statistical significance of narrative patterns

### Validation Methods
- **Cross-sampling:** Multiple strategic samples from same book should yield consistent DNA
- **Author Consistency:** Books by same author should show DNA similarities
- **Genre Patterns:** Books in same genre should share namespace/style characteristics
- **Temporal Evolution:** DNA should reflect historical literary development

### Methodological Advantages
1. **Avoids Iconic Bias** - Skips famous opening/closing passages
2. **Representative Sampling** - 64 paragraphs provide statistical significance
3. **Narrative Focus** - Emphasizes author voice over character dialogue
4. **Composite Analysis** - Patterns emerge from multiple samples, not single examples
5. **Algorithmic Transparency** - Full QNT analysis process documented

## 🧪 Research Applications

### Digital Humanities
- **Corpus Analysis** - Large-scale narrative pattern discovery across literature
- **Authorship Studies** - DNA fingerprinting for attribution questions
- **Genre Evolution** - Tracking changes in narrative techniques over time
- **Cultural Analysis** - Understanding how cultural context shapes narrative voice

### Computational Linguistics
- **Style Transfer** - Advanced text transformation using narrative DNA
- **Content Generation** - AI writing systems guided by extracted DNA patterns
- **Similarity Detection** - Automated discovery of narratively similar works
- **Quality Assessment** - Measuring narrative consistency and coherence

### Literary Theory
- **Narrative Voice Analysis** - Quantitative approach to studying narrative perspective
- **Influence Mapping** - Measuring similarity between authors' narrative DNA
- **Period Characterization** - Defining literary periods through narrative patterns
- **Cross-cultural Studies** - Comparing narrative DNA across different literary traditions

## 🔮 Future Enhancements

### Advanced Sampling
- **Adaptive Selection** - Machine learning to optimize paragraph selection criteria
- **Multi-book DNA** - Composite DNA across an author's complete works
- **Temporal DNA** - Tracking how an author's DNA evolves over their career
- **Genre DNA** - Extracting DNA patterns characteristic of specific genres

### Enhanced Analysis
- **Real-time QNT** - Live analysis of actual Project Gutenberg text content
- **Comparative DNA** - Side-by-side DNA comparison and similarity metrics
- **DNA Visualization** - Graphical representation of narrative patterns
- **Predictive Modeling** - Using DNA to predict reader preferences and text quality

### Integration Features
- **Browser Extension** - DNA analysis of web content
- **Writing Plugin** - Real-time DNA feedback for authors
- **Recommendation Engine** - Content suggestions based on DNA similarity
- **Educational Tools** - Interactive DNA exploration for literature students

---

## 🎓 Academic Context

This system represents a novel approach to computational literary analysis, combining:

- **Quantum Narrative Theory** - Mathematical framework for narrative analysis
- **Strategic Sampling** - Representative paragraph selection methodology  
- **Composite Analysis** - Pattern extraction from multiple narrative samples
- **DNA Metaphor** - Genetic approach to identifying persistent narrative characteristics

The resulting "Narrative DNA" provides a quantitative, reproducible method for characterizing the essential narrative identity of literary works, enabling both scientific analysis and practical applications in content transformation and literary studies.

---

**Built for the Humanizer Lighthouse Platform** 🚀  
*Extracting the genetic code of narrative through quantum analysis*