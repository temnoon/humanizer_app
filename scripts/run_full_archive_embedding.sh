#!/bin/bash
# Full Archive Hierarchical Embedding Runner
# Processes all suitable conversations in manageable batches with monitoring

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BATCH_SIZE=50
MAX_TIMEOUT_MINUTES=120
LOG_DIR="$SCRIPT_DIR/logs"
RESULTS_DIR="$SCRIPT_DIR/test_runs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 FULL ARCHIVE HIERARCHICAL EMBEDDING${NC}"
echo "=================================================================="
echo "📊 Processing ALL suitable conversations in batches of $BATCH_SIZE"
echo "⏰ Timeout: $MAX_TIMEOUT_MINUTES minutes per batch"
echo "📁 Logs: $LOG_DIR/"
echo "📁 Results: $RESULTS_DIR/"
echo ""

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$RESULTS_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}✅ Activating lighthouse venv${NC}"
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please run from lighthouse directory.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "../../scripts/hierarchical_embedder.py" ]; then
    echo -e "${RED}❌ Please run this script from humanizer_api/lighthouse directory${NC}"
    exit 1
fi

# Get total conversation count
echo -e "${BLUE}📊 Checking archive statistics...${NC}"
TOTAL_CONVERSATIONS=$(psql -U tem humanizer_archive -t -c "SELECT COUNT(*) FROM conversation_quality_assessments WHERE is_duplicate = FALSE AND composite_score > 0.3 AND word_count > 200;")
TOTAL_CONVERSATIONS=$(echo $TOTAL_CONVERSATIONS | xargs)  # Trim whitespace

if [ -z "$TOTAL_CONVERSATIONS" ] || [ "$TOTAL_CONVERSATIONS" -eq 0 ]; then
    echo -e "${RED}❌ No suitable conversations found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found $TOTAL_CONVERSATIONS suitable conversations${NC}"

# Calculate number of batches
TOTAL_BATCHES=$(( ($TOTAL_CONVERSATIONS + $BATCH_SIZE - 1) / $BATCH_SIZE ))
echo -e "${BLUE}📦 Will process in $TOTAL_BATCHES batches${NC}"

# Estimate total time
ESTIMATED_MINUTES=$(( $TOTAL_BATCHES * 5 ))  # Rough estimate: 5 minutes per batch
echo -e "${YELLOW}⏰ Estimated total time: ~$ESTIMATED_MINUTES minutes${NC}"

# Confirm before starting
echo ""
read -p "🤔 Proceed with full archive embedding? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚫 Operation cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 STARTING FULL ARCHIVE EMBEDDING${NC}"
echo "=================================================================="

# Main processing loop
CURRENT_OFFSET=0
BATCH_NUM=1
TOTAL_CHUNKS_CREATED=0
TOTAL_CONVERSATIONS_PROCESSED=0
FAILED_BATCHES=0

while [ $CURRENT_OFFSET -lt $TOTAL_CONVERSATIONS ]; do
    echo ""
    echo -e "${BLUE}📦 BATCH $BATCH_NUM/$TOTAL_BATCHES${NC}"
    echo "   Conversations: $((CURRENT_OFFSET + 1))-$((CURRENT_OFFSET + BATCH_SIZE))"
    echo "   Progress: $(( (CURRENT_OFFSET * 100) / TOTAL_CONVERSATIONS ))%"
    
    # Run the batch
    BATCH_START_TIME=$(date +%s)
    
    if python ../../scripts/hierarchical_embedder.py embed --limit $BATCH_SIZE --timeout $MAX_TIMEOUT_MINUTES 2>&1 | tee -a "$LOG_DIR/full_archive_$(date +%Y%m%d_%H%M%S).log"; then
        echo -e "${GREEN}✅ Batch $BATCH_NUM completed successfully${NC}"
        
        # Extract results from the last run
        LATEST_RESULT=$(ls -t $RESULTS_DIR/hierarchical_embedding_*.json | head -1)
        if [ -f "$LATEST_RESULT" ]; then
            BATCH_CHUNKS=$(python -c "import json; data=json.load(open('$LATEST_RESULT')); print(data.get('total_chunks_created', 0))")
            BATCH_PROCESSED=$(python -c "import json; data=json.load(open('$LATEST_RESULT')); print(data.get('processed_conversations', 0))")
            
            TOTAL_CHUNKS_CREATED=$((TOTAL_CHUNKS_CREATED + BATCH_CHUNKS))
            TOTAL_CONVERSATIONS_PROCESSED=$((TOTAL_CONVERSATIONS_PROCESSED + BATCH_PROCESSED))
            
            echo -e "${GREEN}   📝 Batch chunks: $BATCH_CHUNKS${NC}"
            echo -e "${GREEN}   📊 Running totals: $TOTAL_CONVERSATIONS_PROCESSED conversations, $TOTAL_CHUNKS_CREATED chunks${NC}"
        fi
        
    else
        echo -e "${RED}❌ Batch $BATCH_NUM failed${NC}"
        FAILED_BATCHES=$((FAILED_BATCHES + 1))
        
        # Ask whether to continue
        echo ""
        read -p "🤔 Continue with next batch? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}🚫 Processing stopped by user${NC}"
            break
        fi
    fi
    
    BATCH_END_TIME=$(date +%s)
    BATCH_DURATION=$((BATCH_END_TIME - BATCH_START_TIME))
    echo -e "${BLUE}   ⏱️ Batch took: $((BATCH_DURATION / 60))m $((BATCH_DURATION % 60))s${NC}"
    
    # Update counters
    CURRENT_OFFSET=$((CURRENT_OFFSET + BATCH_SIZE))
    BATCH_NUM=$((BATCH_NUM + 1))
    
    # Brief pause between batches
    if [ $CURRENT_OFFSET -lt $TOTAL_CONVERSATIONS ]; then
        echo -e "${YELLOW}⏸️ Pausing 10 seconds between batches...${NC}"
        sleep 10
    fi
done

# Final summary
echo ""
echo "=================================================================="
echo -e "${GREEN}🎉 FULL ARCHIVE EMBEDDING COMPLETE${NC}"
echo "=================================================================="
echo -e "${GREEN}📊 Total conversations processed: $TOTAL_CONVERSATIONS_PROCESSED${NC}"
echo -e "${GREEN}📝 Total chunks created: $TOTAL_CHUNKS_CREATED${NC}"
echo -e "${GREEN}✅ Successful batches: $((TOTAL_BATCHES - FAILED_BATCHES))${NC}"

if [ $FAILED_BATCHES -gt 0 ]; then
    echo -e "${RED}❌ Failed batches: $FAILED_BATCHES${NC}"
fi

echo -e "${BLUE}📁 All logs saved to: $LOG_DIR/${NC}"
echo -e "${BLUE}📁 All results saved to: $RESULTS_DIR/${NC}"

# Show monitoring command
echo ""
echo -e "${YELLOW}💡 Monitor batch progress with:${NC}"
echo "   python ../../scripts/embedding_monitor.py dashboard"
echo ""
echo -e "${YELLOW}💡 Search the embedded archive with:${NC}"
echo "   python ../../scripts/hierarchical_embedder.py search \"your query here\""

echo ""
echo -e "${GREEN}🎊 Full archive hierarchical embedding complete!${NC}"