#!/bin/bash
# Automated Export Organization Script
# Organizes generated files into proper export directories

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔧 Humanizer Export Organizer"
echo "Project root: $PROJECT_ROOT"
echo "Timestamp: $TIMESTAMP"
echo

# Function to move file with timestamp
move_with_timestamp() {
    local src="$1"
    local dest_dir="$2"
    local filename=$(basename "$src")
    local new_name="${TIMESTAMP}_${filename}"
    
    mkdir -p "$dest_dir"
    mv "$src" "$dest_dir/$new_name"
    echo "  ✅ Moved: $filename → $dest_dir/$new_name"
}

# Function to organize by file type
organize_by_type() {
    local src="$1"
    local filename=$(basename "$src")
    local extension="${filename##*.}"
    
    case "$extension" in
        "md")
            move_with_timestamp "$src" "$PROJECT_ROOT/exports/markdown"
            ;;
        "pdf")
            move_with_timestamp "$src" "$PROJECT_ROOT/exports/pdf"
            ;;
        "html"|"htm")
            move_with_timestamp "$src" "$PROJECT_ROOT/exports/html"
            ;;
        "txt")
            if [[ "$filename" == *"transform"* || "$filename" == *"project"* ]]; then
                move_with_timestamp "$src" "$PROJECT_ROOT/exports/transformations"
            else
                move_with_timestamp "$src" "$PROJECT_ROOT/exports/archive"
            fi
            ;;
        "json")
            if [[ "$filename" == *"transform"* || "$filename" == *"result"* ]]; then
                move_with_timestamp "$src" "$PROJECT_ROOT/exports/transformations"
            else
                move_with_timestamp "$src" "$PROJECT_ROOT/exports/archive"
            fi
            ;;
        *)
            move_with_timestamp "$src" "$PROJECT_ROOT/exports/archive"
            ;;
    esac
}

echo "📁 Scanning for files to organize..."

# Find and organize output files from various locations
find "$PROJECT_ROOT" -type f \( \
    -name "*_output.*" -o \
    -name "*_result.*" -o \
    -name "*_transformed.*" -o \
    -name "*_projection.*" -o \
    -name "*test.txt" -o \
    -name "*test.json" \
\) ! -path "*/data/*" ! -path "*/exports/*" ! -path "*/test_runs/*" ! -path "*/_migration_backup/*" ! -path "*/venv/*" ! -path "*/node_modules/*" | while read -r file; do
    echo "Processing: $file"
    organize_by_type "$file"
done

echo
echo "🗂️  Organizing timestamped directories..."

# Find and move timestamped directories to test_runs
find "$PROJECT_ROOT" -type d -name "*20[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]*" ! -path "*/test_runs/*" ! -path "*/exports/*" ! -path "*/_migration_backup/*" | while read -r dir; do
    dirname_base=$(basename "$dir")
    echo "Processing timestamped directory: $dir"
    
    # Determine appropriate test_runs subdirectory
    if [[ "$dirname_base" == *"attribute"* ]]; then
        target="$PROJECT_ROOT/test_runs/attribute_discovery/"
    elif [[ "$dirname_base" == *"projection"* || "$dirname_base" == *"gilgamesh"* ]]; then
        target="$PROJECT_ROOT/test_runs/projections/"
    elif [[ "$dirname_base" == *"batch"* ]]; then
        target="$PROJECT_ROOT/test_runs/batch_processing/"
    else
        target="$PROJECT_ROOT/test_runs/performance/"
    fi
    
    mv "$dir" "$target"
    echo "  ✅ Moved to: $target$dirname_base"
done

echo
echo "🎉 Organization complete!"
echo "Check exports/ and test_runs/ directories for organized content."