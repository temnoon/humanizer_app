#!/bin/bash

# Quick Attribute Discovery Test
# A smaller version for testing the pipeline with fewer books and paragraphs

set -euo pipefail

# Configuration for quick testing
TARGET_PARAGRAPHS=20
TARGET_ATTRIBUTES=16
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Quick Attribute Discovery Test${NC}"
echo -e "${YELLOW}Target: $TARGET_PARAGRAPHS paragraphs → $TARGET_ATTRIBUTES attributes${NC}"
echo

# Test with a small set of well-known books
echo "Testing with specific high-quality books..."

# Test books (known to have good content)
test_books=(1342 74 2701 1513)  # Pride & Prejudice, Tom Sawyer, Moby Dick, Romeo & Juliet

echo "Selected test books:"
echo "  1342 - Pride and Prejudice (Jane Austen)"
echo "  74   - The Adventures of Tom Sawyer (Mark Twain)" 
echo "  2701 - Moby Dick (Herman Melville)"
echo "  1513 - Romeo and Juliet (William Shakespeare)"
echo

# Create temporary directory
WORK_DIR="${SCRIPT_DIR}/quick_test_$(date +%H%M%S)"
mkdir -p "$WORK_DIR"

echo "Working directory: $WORK_DIR"

# Save test books to file
printf '%s\n' "${test_books[@]}" > "$WORK_DIR/discovered_books.txt"

echo -e "${GREEN}✓ Test setup complete${NC}"
echo

# Run the main pipeline with reduced targets
export TARGET_PARAGRAPHS TARGET_ATTRIBUTES

# Call the main script with our test setup
"$SCRIPT_DIR/gutenberg_attribute_discovery.sh"