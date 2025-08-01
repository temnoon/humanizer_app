Humanizer CLI Command Cheat Sheet

  🎯 Core Commands Overview

  Allegory CLI - DNA Discovery & Curation

  # Extract narrative DNA from classic literature
  python allegory_cli.py curate --book-ids 1342 11 84 --max-paras 100 --out ./attributes

  # Advanced curation with custom weights
  python allegory_cli.py curate --book-ids 1342 --max-paras 200 \
    --resonance-weight 1.2 --clarity-weight 0.8 --essence-weight 1.0

  Humanizer CLI - Multi-Purpose Interface

  # Transform text with specific parameters
  python humanizer_cli.py transform --text "Your text here" \
    --persona victorian_narrator --namespace classical --style prose

  # Process file with batch mode
  python humanizer_cli.py transform --file input.txt --out output.txt \
    --persona cyberpunk_hacker --strength 0.8

  # List available DNA components
  python humanizer_cli.py list --personas
  python humanizer_cli.py list --namespaces
  python humanizer_cli.py list --styles

  Archive CLI - Conversation Discovery

  # Search conversation archive
  python archive_cli.py search --query "technology" --limit 10

  # Browse conversations by date
  python archive_cli.py browse --date 2024-01-01 --format json

  # Export conversation data
  python archive_cli.py export --format csv --out conversations.csv

  ---
  🧬 DNA Discovery Commands

  Book Processing

  # Single book extraction
  python allegory_cli.py curate --book-ids 1342 --out ./pride_prejudice

  # Multiple books with high quality
  python allegory_cli.py curate --book-ids 1342 11 84 74 76 \
    --max-paras 150 --resonance-weight 1.5

  Quality Control Parameters

  --resonance-weight 1.0    # Narrative resonance importance
  --info-gain-weight 1.0    # Information richness weight
  --clarity-weight 0.3      # Text clarity weight
  --essence-weight 0.8      # Essence strength weight
  --redundancy-weight 0.5   # Redundancy penalty weight

  ---
  🔄 Text Transformation Commands

  Simple Projection

  # Interactive demo mode
  python simple_projection_demo.py --interactive

  # Batch demo with examples
  python simple_projection_demo.py --demo

  Advanced Projection

  # Enhanced transformations
  python enhanced_projection_demo.py

  # Full workflow test
  python test_full_workflow.py

  Narrative Projection Engine

  python narrative_projection_engine.py \
    --input "Your essay text" \
    --persona literary_narrator \
    --namespace classical_literature \
    --style prose_narrative \
    --strength 0.8 \
    --preserve-essence 0.9

  ---
  📚 Content Management Commands

  Mass Processing

  # Batch attribute harvesting
  python mass_attribute_harvester.py --books 100 --concurrent 5

  # Monitor batch jobs
  python batch_monitor.py --status --jobs all

  # Setup test dataset
  python setup_100_book_test.py --output ./test_books

  Literature Mining

  # Mine specific literature corpus
  python literature_attribute_miner.py --corpus gutenberg --limit 50

  # Regenerate sample attributes
  python regenerate_sample_attributes.py --count 10

  ---
  🔧 System Management Commands

  API & Services

  # Start enhanced API server
  python api_enhanced.py

  # Test system health
  python check_system.py --verbose

  # Test unified API
  python test_unified_api.py --endpoint transform

  Database Operations

  # PostgreSQL conversation API
  python postgres_conversation_api.py --import ./conversations

  # Conversation browser interface
  python conversation_browser.py --port 8080

  # Archive server
  python archive_cli.py server --port 7200

  ---
  🎛️ Configuration & Setup

  Environment Setup

  # Install CLI tools globally
  ./install_cli.sh

  # Local installation
  ./install_local.sh

  # Install system commands
  ./install_commands.sh

  Testing Commands

  # Test attribute extraction
  python test_real_dna_extraction.py

  # Test projection variations
  python test_varied_projection.py

  # Production harvester test
  python production_harvester_test.py

  ---
  📖 Quick Reference Parameters

  Common Book IDs

  - 1342 - Pride and Prejudice
  - 11 - Alice's Adventures in Wonderland
  - 84 - Frankenstein
  - 74 - The Adventures of Tom Sawyer
  - 76 - Adventures of Huckleberry Finn

  DNA Components

  Personas: literary_narrator, tragic_chorus, cyberpunk_hacker, victorian_narrator
  Namespaces: classical_literature, modern_urban, sci_fi, historicalStyles: prose_narrative, dialogue_heavy, stream_consciousness, descriptive

  File Formats

  - --format json - JSON output
  - --format csv - CSV export
  - --format txt - Plain text
  - --format jsonl - JSON Lines

  ---
  ⚡ One-Liner Examples

  # Quick DNA extraction
  python allegory_cli.py curate --book-ids 1342 --max-paras 50 --out ./quick

  # Fast transformation test
  python simple_projection_demo.py --demo

  # System health check
  python check_system.py && echo "✅ System OK"

  # Search conversations
  python archive_cli.py search --query "AI" --limit 5

  # Start development server
  python api_enhanced.py &

  ---
  🚀 Production Workflows

  Full Processing Pipeline

  # 1. Extract DNA
  python allegory_cli.py curate --book-ids 1342 11 84 --max-paras 200 --out ./production_dna

  # 2. Test transformations
  python enhanced_projection_demo.py

  # 3. Process your content
  python humanizer_cli.py transform --file your_essay.txt --persona literary_narrator --out transformed.txt

  Batch Processing

  # Setup batch jobs
  python mass_attribute_harvester.py --books 50 --output ./batch_results

  # Monitor progress
  python batch_monitor.py --watch --interval 30

  # Process results
  python production_harvest_summary.py --input ./batch_results

  💡 Pro Tip: Always activate the lighthouse venv first: source venv/bin/activate
