# Gutenberg Attribute Discovery Scripts 📚

Automated pipeline for discovering, analyzing, and selecting diverse narrative attributes from Project Gutenberg books using the Humanizer CLI.

## 🎯 Overview

These scripts implement a comprehensive pipeline that:

1. **Discovers** diverse books across genres and influential authors
2. **Analyzes** content using Quantum Narrative Theory (QNT)
3. **Selects** 100 paragraphs for maximum variety of personas, namespaces, and styles
4. **Creates** attributes from the selected content
5. **Judges** and selects the best 64 attributes based on quality and diversity

## 📄 Scripts

### `gutenberg_attribute_discovery.sh`
**Main pipeline script** - Full production run targeting 100 paragraphs and 64 final attributes.

**Usage:**
```bash
cd /Users/tem/humanizer-lighthouse/scripts
./gutenberg_attribute_discovery.sh
```

**Features:**
- Searches across 10+ subject categories
- Includes 10+ influential authors
- Implements sophisticated diversity selection
- Quality-based attribute ranking
- Comprehensive progress monitoring
- Detailed reporting

### `quick_attribute_test.sh`
**Testing script** - Smaller version for quick validation with 20 paragraphs and 16 attributes.

**Usage:**
```bash
cd /Users/tem/humanizer-lighthouse/scripts
./quick_attribute_test.sh
```

**Features:**
- Uses 4 pre-selected high-quality books
- Faster execution for testing
- Same pipeline logic as main script
- Good for debugging and validation

## 🔧 Prerequisites

### Required Tools
- **humanizer CLI** - Must be installed and working
- **jq** - JSON processing (`brew install jq` on macOS)
- **bash** - Version 4+ recommended

### API Requirements
- Humanizer API server running on localhost:8100
- Working Gutenberg integration
- Sufficient API rate limits for bulk operations

### Verification Commands
```bash
# Check CLI availability
humanizer health

# Check Gutenberg integration
humanizer gutenberg search --author "shakespeare" --limit 1

# Check jq installation
jq --version
```

## 🚀 Quick Start

### 1. Test Run (Recommended First)
```bash
cd /Users/tem/humanizer-lighthouse/scripts
./quick_attribute_test.sh
```

This will:
- Take ~5-10 minutes
- Process 4 books
- Generate 16 test attributes
- Verify the pipeline works

### 2. Full Production Run
```bash
cd /Users/tem/humanizer-lighthouse/scripts
./gutenberg_attribute_discovery.sh
```

This will:
- Take ~30-60 minutes
- Process 50+ books
- Generate 64 high-quality attributes
- Create comprehensive reports

## 📊 Output Structure

Each run creates a timestamped workspace directory:

```
scripts/gutenberg_analysis_YYYYMMDD_HHMMSS/
├── analysis.log                  # Detailed execution log
├── discovered_books.txt          # List of book IDs found
├── job_mapping.txt              # Job ID to book ID mapping
├── job_ids.txt                  # List of analysis job IDs
├── results.json                 # Raw paragraph analysis results
├── selected_paragraphs.json     # 100 diverse paragraphs chosen
├── all_attributes.json          # All extracted attributes
├── selected_attributes.json     # Final 64 best attributes
└── analysis_report.md           # Comprehensive summary report
```

## 🎯 Selection Algorithms

### Book Discovery Strategy
```
Subject Categories (27 books):
├── Classical Literature (5)
├── Philosophy (3) 
├── Poetry (3)
├── Drama (3)
├── Science Fiction (2)
├── Adventure (2)
├── Romance (2)
├── History (3)
├── Biography (2)
└── Essays (2)

Influential Authors (17 books):
├── Shakespeare (3)
├── Dickens (2)
├── Austen (2)
├── Twain (2)
├── Wilde (2)
├── Poe (2)
├── Carroll (1)
├── Stoker (1)
├── Shelley (1)
└── Wells (1)
```

### Paragraph Selection Criteria
```python
diversity_score = (
    persona_confidence * 0.3 +
    namespace_confidence * 0.3 + 
    style_confidence * 0.3 +
    text_length_bonus * 0.1
)
```

**Filters:**
- Text length: 100-1000 characters (optimal for analysis)
- Analysis completeness: All QNT components present
- Confidence threshold: Minimum viable scores
- Diversity maximization: Unique personas, namespaces, styles

### Attribute Quality Ranking
```python
combined_score = (
    confidence * 0.4 +           # Analysis confidence
    quality_score * 0.3 +        # Component-specific quality
    text_length_bonus * 0.2 +    # Optimal text length
    value_validity * 0.1         # Non-null, meaningful values
)
```

**Final Selection:**
- 16 personas (diverse character archetypes)
- 16 namespaces (varied cultural/domain contexts)
- 16 styles (different linguistic approaches) 
- 16 essences (core meaning patterns)

## 📈 Expected Results

### Quality Metrics
- **Average Confidence**: 0.75-0.85
- **Minimum Confidence**: 0.60+
- **Diversity Coverage**: 15+ unique values per attribute type
- **Text Quality**: Well-formed paragraphs from classic literature

### Attribute Examples

**Personas:**
- philosophical_contemplator, wise_elder, curious_child
- romantic_idealist, practical_realist, tragic_hero
- scholarly_observer, passionate_advocate, gentle_narrator

**Namespaces:**
- renaissance_drama, victorian_society, american_frontier
- gothic_horror, classical_mythology, modern_realism
- maritime_adventure, pastoral_poetry, urban_naturalism

**Styles:**
- elevated_poetic, conversational_prose, dramatic_dialogue
- descriptive_rich, minimalist_precise, ornate_elaborate
- philosophical_dense, narrative_flowing, satirical_wit

**Essences:**
- existential_questioning, moral_instruction, emotional_expression
- social_commentary, personal_growth, universal_truth
- conflict_resolution, beauty_appreciation, wisdom_sharing

## 🔍 Monitoring and Debugging

### Progress Monitoring
The scripts provide real-time progress bars for:
- Book discovery across categories
- Analysis job startup
- Job completion monitoring  
- Paragraph collection
- Attribute creation and selection

### Log Analysis
```bash
# Follow live progress
tail -f gutenberg_analysis_*/analysis.log

# Check for errors
grep -i error gutenberg_analysis_*/analysis.log

# See job status
grep "job" gutenberg_analysis_*/analysis.log
```

### Common Issues

**API Connection Problems:**
```bash
# Test API connectivity
humanizer health
# Should show "OK" status

# Check Gutenberg integration
humanizer gutenberg search --author "test" --limit 1
# Should return without errors
```

**Job Timeout Issues:**
- Default timeout: 30 minutes
- For slow APIs, edit `max_wait_time=1800` in script
- Monitor job status manually: `humanizer gutenberg jobs --status`

**Insufficient Results:**
- Check book discovery count in logs
- Verify analysis jobs completed successfully
- Ensure paragraph extraction worked properly

## 🛠️ Customization

### Modify Target Numbers
```bash
# Edit script parameters
TARGET_PARAGRAPHS=200  # More paragraphs for larger dataset
TARGET_ATTRIBUTES=32   # Fewer attributes for focused set
```

### Add Custom Book Sources
```bash
# Add to search_criteria in discover_books()
["your_category"]="--subject 'Your Subject' --limit 5"

# Add to author_searches
["your_author"]="--author 'Author Name' --limit 3"
```

### Adjust Selection Criteria
```bash
# Modify selection_script in select_diverse_paragraphs()
# Change weights in combined_score calculation
# Add custom filtering logic
```

## 📋 Example Usage Session

```bash
# 1. Preparation
cd /Users/tem/humanizer-lighthouse/scripts
humanizer health  # Verify API connection

# 2. Quick test first
./quick_attribute_test.sh
# [Wait 5-10 minutes for completion]

# 3. Review test results
ls quick_test_*/
cat quick_test_*/analysis_report.md

# 4. Run full pipeline if test succeeded
./gutenberg_attribute_discovery.sh
# [Wait 30-60 minutes for completion]

# 5. Analyze results
ls gutenberg_analysis_*/
jq '.[] | {type, value, confidence}' gutenberg_analysis_*/selected_attributes.json | head -20
```

## 🎨 Advanced Features

### Parallel Processing
The scripts include built-in parallelization:
- Concurrent book searches
- Batch job submission
- Parallel result collection

### Quality Assurance
- Confidence threshold filtering
- Text length optimization
- Duplicate detection and removal
- Comprehensive error handling

### Reporting
- Markdown summary reports
- JSON data exports
- Progress logging
- Statistical analysis

## 🔮 Future Enhancements

- **Machine Learning Integration**: Use discovered attributes to train classification models
- **Interactive Selection**: Web interface for manual attribute curation
- **Continuous Discovery**: Regular updates with new Gutenberg releases
- **Cross-Language Support**: Multi-language attribute discovery
- **Semantic Clustering**: Advanced grouping of similar attributes

---

**Built for the Humanizer Lighthouse Platform** 🚀  
*Combining quantum narrative theory with classic literature to create the future of content analysis.*