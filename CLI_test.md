I'll provide you with practical CLI command examples for exploring the Humanizer platform, including Gutenberg book analysis for finding interesting
   passages.

  🔍 Sample CLI Commands

  System Health & Setup

  # Check if everything is working
  humanizer health

  # See what LLM providers are available
  humanizer providers

  # View current configuration
  humanizer config

  Basic Narrative Analysis

  # Analyze a simple sentence
  humanizer analyze "The lighthouse stood against the storm."

  # Deep analysis with quantum state
  humanizer analyze "Time is the fire in which we burn." --depth deep --quantum

  # Get JSON output for processing
  humanizer analyze "All great literature asks the eternal questions." --format json

  # Quick summary format
  humanizer analyze "The pen is mightier than the sword." --format summary

  Gutenberg Book Discovery

  # Find books by famous authors
  humanizer gutenberg search --author "jane austen" --limit 10
  humanizer gutenberg search --author "mark twain" --limit 5
  humanizer gutenberg search --author "charles dickens" --limit 8

  # Search by subject/genre
  humanizer gutenberg search --subject "philosophy" --limit 15
  humanizer gutenberg search --subject "adventure" --limit 20
  humanizer gutenberg search --subject "mystery" --limit 10

  # Browse most popular books
  humanizer gutenberg popular --limit 25

  # Browse recent additions
  humanizer gutenberg recent --limit 15

  # Get catalog statistics
  humanizer gutenberg info

  Gutenberg Book Analysis (Finding Good Passages)

  # Analyze classic novels for narrative patterns
  humanizer gutenberg analyze 1342 --type sample  # Pride and Prejudice
  humanizer gutenberg analyze 74 --type sample    # Adventures of Tom Sawyer
  humanizer gutenberg analyze 2701 --type sample  # Moby Dick

  # Target specific narrative elements
  humanizer gutenberg analyze 1513 --type targeted  # Romeo and Juliet
  humanizer gutenberg analyze 84 --type targeted    # Frankenstein

  # Full deep analysis (takes longer but more comprehensive)
  humanizer gutenberg analyze 11 --type full       # Alice in Wonderland

  # Analyze multiple books for comparison
  humanizer gutenberg analyze 1342 74 2701 --type sample

  Monitoring Analysis Jobs

  # Check all running jobs
  humanizer gutenberg jobs --status

  # Get details of a specific job
  humanizer gutenberg jobs --job-id abc123def456

  # Get results when job completes
  humanizer gutenberg jobs --results abc123def456

  # Monitor job progress with live updates
  humanizer batch monitor abc123def456 --refresh 3

  # Cancel a job if needed
  humanizer gutenberg jobs --cancel abc123def456

  Finding Interesting Passages by Theme

  # Look for philosophical works
  humanizer gutenberg search --subject "philosophy" --limit 10
  # Then analyze: humanizer gutenberg analyze [BOOK_IDS] --type targeted

  # Find adventure narratives
  humanizer gutenberg search --subject "adventure" --author "stevenson" --limit 5
  # Analyze for action and setting: humanizer gutenberg analyze [RESULTS] --type sample

  # Discover romantic literature
  humanizer gutenberg search --subject "romance" --limit 8
  # Good for persona and style analysis

  # Find gothic/mystery works
  humanizer gutenberg search --query "gothic" --limit 6
  humanizer gutenberg search --query "mystery" --limit 10

  # Poetry and lyrical works
  humanizer gutenberg search --subject "poetry" --limit 12

  Attribute Management

  # List all saved attributes
  humanizer attributes list

  # Filter by specific types
  humanizer attributes list --type persona
  humanizer attributes list --type style --limit 20

  # Find attributes with specific tags
  humanizer attributes list --tags "classical,literature"
  humanizer attributes list --tags "adventure,narrative"

  # View detailed information about an attribute
  humanizer attributes show abc123ef4567

  # Get statistics about your saved attributes
  humanizer attributes stats

  # See how algorithms work (transparency)
  humanizer attributes algorithm persona
  humanizer attributes algorithm style

  Workflow Examples for Finding Good Passages

  Discover Philosophical Passages

  # 1. Find philosophy books
  humanizer gutenberg search --subject "philosophy" --limit 5

  # 2. Analyze for deep thinking patterns
  humanizer gutenberg analyze 4280 5827 --type targeted  # Example IDs

  # 3. Check results for high-quality passages
  humanizer gutenberg jobs --status
  humanizer gutenberg jobs --results [JOB_ID]

  Find Dramatic Dialogue

  # 1. Search for plays and drama
  humanizer gutenberg search --subject "drama" --limit 8

  # 2. Analyze for persona and style patterns
  humanizer gutenberg analyze 1513 1524 1533 --type sample  # Shakespeare works

  # 3. Look for strong persona indicators
  humanizer gutenberg jobs --results [JOB_ID]

  Discover Descriptive Nature Writing

  # 1. Find nature/travel writing
  humanizer gutenberg search --query "nature" --limit 10
  humanizer gutenberg search --author "thoreau" --limit 3

  # 2. Analyze for rich descriptive passages
  humanizer gutenberg analyze [BOOK_IDS] --type targeted

  # 3. Filter for high essence/style scores

  Testing and Development

  # Run the full test suite
  humanizer test

  # Test specific narrative categories
  humanizer test --category classical
  humanizer test --category modern_literary
  humanizer test --category philosophical

  # Transform text using LPE
  humanizer transform "A simple sentence" --persona academic --style formal

  Advanced Usage Patterns

  # Chain operations with shell commands
  humanizer gutenberg search --author "shakespeare" --limit 3 | grep "ID"

  # Save analysis results to files
  humanizer analyze "Sample text for analysis" --format json > analysis_result.json

  # Monitor multiple jobs
  for job in job1 job2 job3; do
      humanizer batch monitor $job --refresh 5 &
  done

  # Export attributes for backup
  humanizer attributes list --format json > my_attributes_backup.json

  Practical Research Workflows

  Literature Research Pipeline

  # 1. Discover books in your area of interest
  humanizer gutenberg search --subject "science fiction" --limit 15

  # 2. Analyze a sample for quality assessment
  humanizer gutenberg analyze 35 84 131 --type sample

  # 3. Monitor and collect results
  humanizer gutenberg jobs --status
  humanizer gutenberg jobs --results [JOB_ID] > scifi_analysis.json

  # 4. Save interesting attributes found
  # (This would be done through the API based on analysis results)

  Writing Style Analysis

  # 1. Compare different authors' styles
  humanizer gutenberg search --author "hemingway" --limit 3
  humanizer gutenberg search --author "fitzgerald" --limit 3

  # 2. Analyze their works for style patterns
  humanizer gutenberg analyze [HEMINGWAY_IDS] --type targeted
  humanizer gutenberg analyze [FITZGERALD_IDS] --type targeted

  # 3. Review style attributes discovered
  humanizer attributes list --type style --tags "modern,american"

  Debugging and Troubleshooting

  # Verbose output for debugging
  humanizer --verbose health
  humanizer --verbose analyze "test text"

  # Test with custom API endpoint
  humanizer --api-url http://localhost:8100 health

  # Quick connectivity test
  humanizer health && echo "✅ Connected" || echo "❌ Connection failed"

  These commands will help you explore the full capabilities of the Humanizer platform, discover interesting literary passages through the Gutenberg
  integration, and build a collection of narrative attributes for your research or creative work.

  The book analysis features are particularly powerful for finding passages with strong narrative elements - whether you're looking for philosophical
  depth, dramatic dialogue, rich descriptions, or specific stylistic patterns.