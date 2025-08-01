#!/bin/bash

# Mass Attribute Harvester - Complete Management Script
# Unified interface for batch processing hundreds of narrative DNA attributes

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIGHTHOUSE_DIR="/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse"
OUTPUT_DIR="./mass_attributes"
DB_PATH="./batch_jobs.db"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
🏭 ═══════════════════════════════════════════════════════════════════════════════
   MASS ATTRIBUTE HARVESTER - Batch Processing System
   
   Scalable pipeline for generating hundreds of narrative DNA attributes
   from Project Gutenberg classical literature
═══════════════════════════════════════════════════════════════════════════════ 🏭
EOF
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Python environment
    cd "$LIGHTHOUSE_DIR"
    if [[ ! -d "venv" ]]; then
        echo -e "${RED}❌ Virtual environment not found${NC}"
        echo "Please run: cd $LIGHTHOUSE_DIR && python -m venv venv"
        exit 1
    fi
    
    source venv/bin/activate
    
    # Check Python version
    python_version=$(python --version 2>&1)
    echo -e "${GREEN}✅ Python: $python_version${NC}"
    
    # Check required core components
    required_files=(
        "gutenberg_canonicalizer.py"
        "narrative_feature_extractor.py" 
        "povm_paragraph_selector.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}✅ $file: found${NC}"
        else
            echo -e "${RED}❌ $file: missing${NC}"
            echo "Please ensure all core components are installed"
            exit 1
        fi
    done
    
    # Copy mass harvester to lighthouse directory
    cp "$SCRIPT_DIR/mass_attribute_harvester.py" .
    cp "$SCRIPT_DIR/batch_monitor.py" .
    
    echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
}

# Initialize database and add books
setup_jobs() {
    local job_type="$1"
    local start_id="$2"
    local end_id="$3" 
    local max_paragraphs="${4:-100}"
    
    echo -e "${BLUE}📚 Setting up batch jobs...${NC}"
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    case "$job_type" in
        "classics")
            echo -e "${CYAN}📖 Adding curated classical literature...${NC}"
            python mass_attribute_harvester.py add-classics --max-paragraphs "$max_paragraphs"
            ;;
        "range")
            if [[ -z "$start_id" || -z "$end_id" ]]; then
                echo -e "${RED}❌ Start and end IDs required for range mode${NC}"
                exit 1
            fi
            echo -e "${CYAN}📖 Adding book range $start_id-$end_id...${NC}"
            python mass_attribute_harvester.py add-range \
                --start-id "$start_id" \
                --end-id "$end_id" \
                --max-paragraphs "$max_paragraphs"
            ;;
        *)
            echo -e "${RED}❌ Unknown job type: $job_type${NC}"
            echo "Use 'classics' or 'range'"
            exit 1
            ;;
    esac
}

# Run batch processing
run_processing() {
    local max_workers="$1"
    
    echo -e "${CYAN}🏭 Starting batch processing...${NC}"
    echo -e "${YELLOW}⚠️ This may take several hours depending on job queue size${NC}"
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    # Show current job status first
    echo -e "${BLUE}📊 Current job queue:${NC}"
    python mass_attribute_harvester.py status
    
    echo
    read -p "Proceed with batch processing? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🚀 Processing started...${NC}"
        
        if [[ -n "$max_workers" ]]; then
            python mass_attribute_harvester.py process --max-workers "$max_workers"
        else
            python mass_attribute_harvester.py process
        fi
        
        echo -e "${GREEN}✅ Batch processing complete!${NC}"
        show_results_summary
    else
        echo -e "${YELLOW}🚫 Processing cancelled${NC}"
    fi
}

# Show monitoring dashboard
show_monitoring() {
    local continuous="$1"
    
    echo -e "${CYAN}📊 Opening monitoring dashboard...${NC}"
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    if [[ "$continuous" == "true" ]]; then
        python batch_monitor.py dashboard --continuous
    else
        python batch_monitor.py dashboard
    fi
}

# Show results summary
show_results_summary() {
    echo -e "${BLUE}📈 Processing Results Summary${NC}"
    echo "-" * 50
    
    if [[ -d "$OUTPUT_DIR" ]]; then
        # Count output files
        mass_files=$(find "$OUTPUT_DIR" -name "mass_attributes_*.json" | wc -l)
        legacy_files=$(find "$OUTPUT_DIR" -name "attributes_*.json" | wc -l)
        
        echo -e "${GREEN}📁 Mass format files: $mass_files${NC}"
        echo -e "${GREEN}📁 Legacy format files: $legacy_files${NC}"
        
        # Sample recent file
        recent_file=$(find "$OUTPUT_DIR" -name "mass_attributes_*.json" -type f -exec ls -t {} + | head -1)
        if [[ -n "$recent_file" ]]; then
            echo -e "${BLUE}📄 Most recent file: $(basename "$recent_file")${NC}"
            
            # Show brief content summary
            if command -v jq >/dev/null 2>&1; then
                echo -e "${CYAN}📊 Sample content:${NC}"
                echo "   Book ID: $(jq -r '.book_id' "$recent_file")"
                echo "   Paragraphs: $(jq -r '.selected_paragraphs | length' "$recent_file")"
                echo "   Processing time: $(jq -r '.processing_time_seconds' "$recent_file")s"
            fi
        fi
        
        echo -e "${GREEN}📂 Output directory: $OUTPUT_DIR${NC}"
    else
        echo -e "${YELLOW}⚠️ No output directory found${NC}"
    fi
}

# Quick status check
show_status() {
    echo -e "${BLUE}📊 System Status${NC}"
    echo "=" * 40
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    # Job status
    python mass_attribute_harvester.py status
    
    # Output status
    show_results_summary
}

# Show usage
show_usage() {
    cat << EOF
${CYAN}Mass Attribute Harvester - Management Script${NC}

USAGE:
  $0 [COMMAND] [OPTIONS]

COMMANDS:
  setup-classics [PARAGRAPHS]     - Add curated classical literature to queue
  setup-range START END [PARA]    - Add book ID range to queue  
  process [WORKERS]               - Run batch processing
  monitor [--continuous]          - Show monitoring dashboard
  status                          - Show current system status
  help                           - Show this help

SETUP EXAMPLES:
  $0 setup-classics              # Add ~200 curated classics (100 paragraphs each)
  $0 setup-classics 150          # Add classics with 150 paragraphs max
  $0 setup-range 1000 1100       # Add books 1000-1100 (100 paragraphs each)
  $0 setup-range 2000 2050 75    # Add books 2000-2050 (75 paragraphs each)

PROCESSING EXAMPLES:
  $0 process                     # Process with default workers
  $0 process 4                   # Process with 4 concurrent workers
  
MONITORING EXAMPLES:
  $0 monitor                     # One-time dashboard view
  $0 monitor --continuous        # Live updating dashboard
  $0 status                      # Quick status summary

WORKFLOW:
  1. $0 setup-classics           # Add books to processing queue
  2. $0 monitor --continuous     # Start monitoring in another terminal
  3. $0 process                  # Begin batch processing
  4. $0 status                   # Check final results

OUTPUT:
  📁 Enhanced format: mass_attributes_BOOKID.json
  📁 Legacy format: attributes_BOOKID.json  
  📁 Location: $OUTPUT_DIR
  💾 Job database: $DB_PATH

The system processes Project Gutenberg books through the complete 
Narrative DNA pipeline: canonicalization → segmentation → anchoring → 
feature extraction → POVM selection → attribute generation.
EOF
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        "setup-classics")
            local max_paragraphs="${2:-100}"
            show_banner
            check_prerequisites
            setup_jobs "classics" "" "" "$max_paragraphs"
            echo -e "${GREEN}✅ Classical literature queue setup complete${NC}"
            ;;
        "setup-range")
            local start_id="$2"
            local end_id="$3"
            local max_paragraphs="${4:-100}"
            show_banner
            check_prerequisites
            setup_jobs "range" "$start_id" "$end_id" "$max_paragraphs"
            echo -e "${GREEN}✅ Book range queue setup complete${NC}"
            ;;
        "process")
            local max_workers="$2"
            show_banner
            check_prerequisites
            run_processing "$max_workers"
            ;;
        "monitor")
            local continuous="false"
            if [[ "$2" == "--continuous" ]]; then
                continuous="true"
            fi
            check_prerequisites
            show_monitoring "$continuous"
            ;;
        "status")
            check_prerequisites
            show_status
            ;;
        "help"|"--help"|"-h"|"")
            show_usage
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi