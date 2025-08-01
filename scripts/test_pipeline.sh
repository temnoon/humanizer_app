#!/bin/bash

# Quick test of the pipeline to verify logging fix

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/test_pipeline_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/test.log"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging function (same as in main script)
log() {
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

echo -e "${CYAN}🧪 Testing Pipeline Initialization${NC}"
echo

# Test logging before directory creation
log "Testing logging function - this should work now"
log "Workspace will be: $WORK_DIR"

# Verify directory was created
if [ -d "$WORK_DIR" ]; then
    echo -e "${GREEN}✅ Directory created successfully: $WORK_DIR${NC}"
else
    echo -e "${RED}❌ Directory creation failed${NC}"
    exit 1
fi

# Verify log file was created
if [ -f "$LOG_FILE" ]; then
    echo -e "${GREEN}✅ Log file created successfully: $LOG_FILE${NC}"
else
    echo -e "${RED}❌ Log file creation failed${NC}"
    exit 1
fi

# Show log contents
echo -e "${YELLOW}📋 Log file contents:${NC}"
cat "$LOG_FILE"

echo
echo -e "${GREEN}✅ Pipeline initialization test passed!${NC}"
echo -e "${CYAN}The main script should now work correctly.${NC}"

# Cleanup test directory
rm -rf "$WORK_DIR"
echo -e "${YELLOW}🧹 Cleaned up test directory${NC}"