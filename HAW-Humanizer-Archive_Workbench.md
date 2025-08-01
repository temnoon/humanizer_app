
  🤖 HAW Commands - Comprehensive Function Guide

  📊 System Management

  haw status                  # System health & active processes
  haw processes              # Show active humanizer processes
  haw logs                   # View recent log activity
  haw setup                  # Setup/repair Python environment

  🔍 Content Discovery & Analysis

  # Archive Exploration
  haw archive list                    # List archived conversations
  haw archive search "consciousness"  # Search archive content
  haw archive get <id>               # Get specific conversation
  haw archive stats                  # Archive statistics

  # Metadata & Intelligence
  haw browse browse                  # Interactive metadata browser
  haw browse overview               # System overview
  haw browse search [filters]       # Search with filters
  haw browse export                 # Export metadata

  # Semantic Analysis
  haw browse-chunks browse          # Interactive semantic chunks browser
  haw browse-chunks list           # List conversations by chunk count
  haw browse-chunks explore <id>   # Explore specific conversation chunks
  haw browse-chunks search <term>  # Search chunk summaries

  # Word Pattern Analysis
  haw browse-wordclouds browse                    # Interactive word cloud browser
  haw browse-wordclouds search --word <word>     # Find conversations with word
  haw browse-wordclouds topic --words <words>    # Multi-word topic search
  haw browse-wordclouds title --query <query>    # **Search by conversation title**
  haw browse-wordclouds trending                 # Cross-conversation patterns

  # Content Assessment
  haw assess                        # Batch conversation quality assessment
  haw sample                       # Extract representative samples
  haw wordcloud                    # Generate archive word clouds
  haw categorize                   # Content categorization
  haw agentic assess <task_type>   # Intelligent content assessment
  haw agentic results [filters]    # View assessment results

  📝 Writing & Style Analysis

  # Personal Writing Analysis
  haw extract-writing extract --limit 1000       # Extract writing patterns
  haw browse-writing browse                       # Interactive writing browser
  haw browse-writing summary                      # Writing style summary
  haw browse-writing details                      # Detailed style analysis
  haw browse-writing samples [filter]            # View writing samples

  🧬 Narrative DNA & Attributes

  # Core DNA Extraction Tools
  haw allegory curate <book_ids>                 # Extract narrative DNA from books
  haw attribute list                             # List available attributes
  haw attribute browse                           # Interactive attribute browser
  haw attribute summary                          # Attribute collection overview
  haw attribute extract <conversation_id>       # Extract attributes from conversation

  # Advanced Attribute Discovery (via scripts)
  ./scripts/narrative_dna_extractor.sh          # Extract DNA from conversations
  ./scripts/mass_attribute_harvester.py         # Bulk attribute extraction
  ./scripts/attribute_discovery_v2.sh           # Advanced attribute discovery
  ./scripts/transform_with_dna.sh              # Apply DNA to transform text
  ./scripts/dna_navigator.sh                   # Navigate extracted DNA
  ./scripts/dna_inspector.sh                   # Inspect DNA quality

  🔄 Content Transformation Pipeline

  # Pipeline Management
  haw pipeline process [filters]                # Transform content
  haw pipeline status                          # Pipeline status
  haw pipeline config                          # Pipeline configuration
  haw pipeline-mgr rules list                 # List transformation rules
  haw pipeline-mgr execute --min-quality 0.8  # Execute with quality filter
  haw pipeline-mgr stats                      # Pipeline statistics

  # Pre-defined Pipelines
  haw pipeline run full-analysis               # Complete analysis pipeline
  haw pipeline run writing-profile            # Writing style analysis
  haw pipeline run content-audit              # Content quality audit
  haw pipeline run embedding-refresh          # Refresh embeddings

  🧠 Embedding & Search

  haw embed --limit N --timeout N             # Hierarchical embedding (test)
  haw embed-full --batch-size 50 --timeout 120  # Full archive embedding
  haw monitor dashboard                        # Embedding progress dashboard
  haw monitor status                          # Embedding status
  haw monitor stats                           # Embedding statistics
  haw embedding-cli                           # Embedding corpus management

  🌐 API Services

  haw api list                                # List available services
  haw api start lighthouse-api                # Start transformation API
  haw api start archive-api                   # Start archive API
  haw api start lpe-api                       # Start LPE transformation API
  haw api start lawyer-api                    # Start content quality API
  haw api start pipeline-api                  # Start pipeline API
  haw api stop <service>                      # Stop specific service
  haw api restart <service>                   # Restart service

  ---
  🧬 Narrative Transformation Workflow

  Step 1: Select & Analyze Narratives

  # Find conversations by content or title
  haw browse-wordclouds title --query "consciousness"
  haw browse-wordclouds search --word "phenomenology"
  haw archive search "quantum mechanics"

  # Analyze conversation quality and attributes
  haw assess                                   # Quality assessment
  haw browse-chunks explore <conversation_id>  # View semantic structure

  Step 2: Extract Narrative DNA (Persona, Namespace, Style)

  # Extract comprehensive attributes from selected conversations
  haw allegory curate <conversation_ids>       # Formal DNA extraction
  haw attribute extract <conversation_id>      # Quick attribute extraction

  # Advanced DNA extraction (for multiple conversations)
  ./scripts/narrative_dna_extractor.sh <conversation_id>
  ./scripts/mass_attribute_harvester.py --conversations <ids>

  # Inspect extracted DNA
  haw attribute browse                         # Interactive DNA browser
  ./scripts/dna_inspector.sh                 # Quality inspection
  ./scripts/dna_navigator.sh                 # Navigate DNA structure

  Step 3: Browse & Select DNA Attributes

  # Interactive exploration of extracted attributes
  haw attribute browse
  > list                                      # Show available attribute sets
  > summary                                   # Overview of collection
  > explore <book_id>                        # Explore specific DNA
  > search persona                           # Find persona attributes
  > search namespace                         # Find namespace attributes
  > search style                            # Find style attributes
  > export <selection>                      # Export selected attributes

  Step 4: Apply DNA to Transform New Narrative

  # Direct transformation using extracted DNA
  ./scripts/transform_with_dna.sh <source_text> <target_dna>

  # Pipeline-based transformation
  haw pipeline process --source <text> --dna <dna_id> --output <file>

  # API-based transformation (requires lighthouse-api running)
  curl -X POST http://localhost:8100/transform \
    -H "Content-Type: application/json" \
    -d '{
      "text": "Your narrative text here",
      "persona": "extracted_persona_id",
      "namespace": "extracted_namespace_id",
      "style": "extracted_style_id",
      "transformation_type": "allegory"
    }'

  Step 5: Validation & Refinement

  # Assess transformation quality
  haw assess --input <transformed_text>

  # Compare original vs transformed
  haw pipeline-mgr compare --original <text1> --transformed <text2>

  # Iterate with refined DNA
  ./scripts/dna_inspector.sh <transformation_result>
  haw attribute refine <dna_id> --feedback <quality_score>

  ---
  🎯 Example Complete Workflow

  # 1. Find consciousness-related conversations
  haw browse-wordclouds title --query "consciousness"

  # 2. Extract DNA from best conversation (e.g. ID 208808)
  haw allegory curate 208808
  ./scripts/narrative_dna_extractor.sh 208808

  # 3. Browse extracted attributes
  haw attribute browse
  > explore 208808
  > search persona "phenomenological"
  > search style "academic_philosophical"
  > export consciousness_dna_set

  # 4. Transform new text using extracted DNA
  ./scripts/transform_with_dna.sh \
    --source "my_new_narrative.txt" \
    --dna "consciousness_dna_set" \
    --output "transformed_narrative.txt"

  # 5. Validate transformation
  haw assess --input transformed_narrative.txt

  This gives you a complete pipeline from narrative discovery → DNA extraction → attribute selection → transformation application →
  quality validation.