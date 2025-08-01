# Gutenberg Book Analysis System

## ✅ Architecture Confirmed

**Business Logic**: 100% in API server
- Book downloading, cleaning, and analysis
- Paragraph scoring and concept extraction
- Batch job management and progress tracking
- Results storage and database enrichment

**CLI Interface**: Thin client for user interaction
- Search interface for finding books
- Job creation and monitoring
- Progress visualization and results display
- Simple command structure for complex operations

## 🔬 Analysis Capabilities

### Book Processing Pipeline
1. **Download**: Fetch books from Project Gutenberg
2. **Clean**: Remove headers/footers, normalize formatting
3. **Analyze**: Score paragraphs for attribute enrichment potential
4. **Extract**: Identify concepts, emotions, literary devices
5. **Rank**: Sort by enrichment score for database selection

### Scoring Metrics
- **Complexity Score**: Word/sentence length analysis
- **Narrative Quality**: Story elements and dialogue detection
- **Attribute Enrichment**: Concept density and thematic richness
- **Emotional Tone**: Sentiment analysis (positive/negative/neutral)
- **Literary Devices**: Simile, metaphor, alliteration detection

### Analysis Types
- **Sample**: Every 10th paragraph (20 max per book) - Fast overview
- **Targeted**: Paragraphs 50-200 words - Quality focused
- **Full**: Complete analysis - Comprehensive but slow

## 🚀 CLI Usage Examples

### Book Discovery
```bash
# Search by title
humanizer gutenberg search --query "pride prejudice"

# Search by author  
humanizer gutenberg search --author "dickens"

# Browse by subject
humanizer gutenberg search --subject "science fiction" --limit 20
```

### Batch Analysis
```bash
# Start analysis job (sample mode)
humanizer gutenberg analyze 1342 11 84

# Full analysis of specific books
humanizer gutenberg analyze 1342 11 --type full

# Targeted analysis for quality content
humanizer gutenberg analyze 74 1661 2542 --type targeted
```

### Job Management
```bash
# List all analysis jobs
humanizer gutenberg jobs --status

# Check specific job
humanizer gutenberg jobs --job-id abc123

# View results
humanizer gutenberg jobs --results abc123

# Cancel running job
humanizer gutenberg jobs --cancel abc123
```

### Live Monitoring
```bash
# Monitor job with live updates
humanizer batch monitor abc123

# Monitor with custom refresh rate
humanizer batch monitor abc123 --refresh 10

# List all batch jobs
humanizer batch list
```

## 📊 Results and Enrichment

### Analysis Output
- **High-quality candidates**: Paragraphs scored >0.3 for enrichment
- **Concept extraction**: Most common themes and topics
- **Emotional distribution**: Tone analysis across content
- **Literary devices**: Style and technique identification

### Database Integration
```bash
# Add results to content database (API endpoint ready)
curl -X POST "http://localhost:8100/gutenberg/jobs/abc123/enrich?min_score=0.5"
```

## 🔧 API Endpoints

### Search and Discovery
- `GET /gutenberg/search` - Search Gutenberg catalog
- `GET /gutenberg/stats` - Analysis statistics

### Job Management
- `POST /gutenberg/analyze` - Create analysis job
- `GET /gutenberg/jobs` - List all jobs
- `GET /gutenberg/jobs/{id}` - Job status
- `GET /gutenberg/jobs/{id}/results` - Job results
- `DELETE /gutenberg/jobs/{id}` - Cancel job

### Database Integration
- `POST /gutenberg/jobs/{id}/enrich` - Add results to database

## 💡 Example Workflow

1. **Discover Books**:
   ```bash
   humanizer gutenberg search --author "jane austen" --limit 5
   ```

2. **Start Analysis**:
   ```bash
   humanizer gutenberg analyze 1342 161  # Pride & Prejudice, Sense & Sensibility
   ```

3. **Monitor Progress**:
   ```bash
   humanizer batch monitor abc123
   ```

4. **Review Results**:
   ```bash
   humanizer gutenberg jobs --results abc123
   ```

5. **Enrich Database** (when API integrated):
   ```bash
   # Will be available once unified API is deployed
   curl -X POST "localhost:8100/gutenberg/jobs/abc123/enrich"
   ```

## 🎯 Integration Points

### Content Service Integration
- Paragraphs tagged with enrichment scores
- Concept metadata for semantic search
- Source attribution to Gutenberg works

### LLM Service Integration  
- Use analyzed content for training data
- Generate attributes based on extracted concepts
- Transform writing styles learned from literature

### Search Service Integration
- Semantic search over analyzed paragraphs
- Find similar content by literary style
- Discover thematic connections

## 🔄 Batch Processing Architecture

### Asynchronous Jobs
- Non-blocking job creation
- Background processing with progress tracking
- Graceful error handling and recovery

### Scalable Design
- Multiple concurrent jobs supported
- Results cached for fast retrieval
- Memory-efficient streaming processing

### Monitoring & Control
- Real-time progress updates
- Job cancellation capability
- Comprehensive status reporting

This system provides a complete pipeline from book discovery to database enrichment, with powerful CLI tools for managing long-running analysis jobs.