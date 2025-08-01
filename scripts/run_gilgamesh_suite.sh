#!/bin/bash

# Gilgamesh Projection Suite - Complete Test Runner
# Demonstrates the full narrative DNA projection pipeline

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIGHTHOUSE_DIR="/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse"

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
🏺 ═══════════════════════════════════════════════════════════════════════════════
   THE EPIC OF GILGAMESH - NARRATIVE DNA PROJECTION SUITE
   
   Interactive demonstration of quantum narrative projection theory
   Using discovered DNA attributes from classical literature
═══════════════════════════════════════════════════════════════════════════════ 🏺
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
    
    # Check required packages
    echo -e "${BLUE}📦 Checking packages...${NC}"
    required_packages=("numpy" "scikit-learn" "requests")
    
    for package in "${required_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}✅ $package: installed${NC}"
        else
            echo -e "${RED}❌ $package: missing${NC}"
            echo "Installing $package..."
            pip install "$package"
        fi
    done
}

# Generate sample attributes if missing
generate_sample_attributes() {
    local attributes_dir="$LIGHTHOUSE_DIR/discovered_attributes"
    
    if [[ ! -d "$attributes_dir" ]] || [[ $(find "$attributes_dir" -name "attributes_*.json" | wc -l) -lt 2 ]]; then
        echo -e "${YELLOW}📚 No discovered attributes found. Generating sample data...${NC}"
        
        cd "$LIGHTHOUSE_DIR"
        source venv/bin/activate
        
        # Run enhanced discoverer with small sample
        python "$SCRIPT_DIR/enhanced_autonomous_discoverer.py" --max-books 3 --max-paras 15
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Sample attributes generated${NC}"
        else
            echo -e "${RED}❌ Failed to generate attributes${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Discovered attributes found${NC}"
    fi
}

# Run interactive suite
run_interactive_suite() {
    echo -e "${CYAN}🎭 Launching Interactive Projection Suite...${NC}"
    echo
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    # Copy scripts to lighthouse directory
    cp "$SCRIPT_DIR/narrative_projection_engine.py" .
    cp "$SCRIPT_DIR/gilgamesh_projection_suite.py" .
    
    # Launch interactive suite
    python gilgamesh_projection_suite.py
}

# Run automated demo
run_automated_demo() {
    echo -e "${CYAN}🎪 Running Automated Demo...${NC}"
    echo
    
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    
    # Copy scripts
    cp "$SCRIPT_DIR/narrative_projection_engine.py" .
    
    # Sample Gilgamesh text
    local sample_text="Gilgamesh, king of Uruk, was two-thirds divine and one-third mortal. He oppressed his people with his strength, and they cried out to the gods for relief."
    
    echo -e "${BLUE}📖 Sample text: ${NC}"
    echo "   \"$sample_text\""
    echo
    
    # Test different projections
    local projections=(
        "tragic_chorus ancient_mesopotamia epic_verse"
        "cyberpunk_hacker cyberpunk_dystopia noir_prose"
        "victorian_narrator regency_england stream_of_consciousness"
    )
    
    for projection in "${projections[@]}"; do
        read -r persona namespace style <<< "$projection"
        
        echo -e "${YELLOW}🎭 Testing projection: $persona • $namespace • $style${NC}"
        
        python narrative_projection_engine.py \
            --text "$sample_text" \
            --persona "$persona" \
            --namespace "$namespace" \
            --style "$style"
        
        echo
        echo -e "${GRAY}Press Enter to continue...${NC}"
        read
    done
}

# Show usage
show_usage() {
    cat << EOF
${CYAN}Gilgamesh Projection Suite - Test Runner${NC}

USAGE:
  $0 [COMMAND]

COMMANDS:
  interactive    - Launch interactive projection suite (default)
  demo          - Run automated demo with sample projections
  check         - Check prerequisites only
  help          - Show this help

FEATURES:
  🏺 Epic of Gilgamesh narrative passages
  🎭 Multiple persona transformations (tragic_chorus, cyberpunk_hacker, victorian_narrator)
  🌍 Cultural namespace projections (ancient_mesopotamia, cyberpunk_dystopia, regency_england)
  ✍️ Stylistic transformations (epic_verse, noir_prose, stream_of_consciousness)
  🔮 Essence preservation scoring
  📊 Transformation analysis and comparison tools

INTERACTIVE COMMANDS:
  project <passage>  - Transform specific passage
  demo              - Guided demonstration
  compare           - Compare projections
  random            - Random projection generator
  help              - Show command help
  quit              - Exit

EXAMPLES:
  $0                    # Launch interactive suite
  $0 demo              # Run automated demo
  $0 check             # Check prerequisites

The suite demonstrates how narrative essence is preserved while
surface manifestations transform across different personas, 
namespaces, and stylistic patterns.
EOF
}

# Main execution
main() {
    local command="${1:-interactive}"
    
    case "$command" in
        "interactive"|"")
            show_banner
            check_prerequisites
            generate_sample_attributes
            run_interactive_suite
            ;;
        "demo")
            show_banner
            check_prerequisites
            generate_sample_attributes
            run_automated_demo
            ;;
        "check")
            check_prerequisites
            echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
            ;;
        "help"|"--help"|"-h")
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