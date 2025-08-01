#!/bin/bash
# Book Export and Publishing Script
# Converts content through the publishing pipeline

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to display usage
usage() {
    echo "📚 Humanizer Book Export Script"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  promote <file>     Move file through publishing pipeline"
    echo "  publish <file>     Generate final publication formats"
    echo "  list              List content in each pipeline stage"
    echo
    echo "Examples:"
    echo "  $0 promote drafts/essays/my_essay.md"
    echo "  $0 publish approved/my_book.md"
    echo "  $0 list"
    exit 1
}

# Function to promote content through pipeline
promote_content() {
    local file_path="$1"
    local full_path="$PROJECT_ROOT/exports/books/$file_path"
    
    if [[ ! -f "$full_path" ]]; then
        echo "❌ File not found: $file_path"
        exit 1
    fi
    
    local filename=$(basename "$file_path")
    local current_stage=$(dirname "$file_path")
    
    case "$current_stage" in
        "drafts"*|"drafts")
            local next_stage="review"
            ;;
        "review")
            local next_stage="approved"
            ;;
        "approved")
            echo "✅ File is already approved. Use 'publish' command to generate final formats."
            exit 0
            ;;
        *)
            echo "❌ Unknown stage: $current_stage"
            exit 1
            ;;
    esac
    
    local dest_path="$PROJECT_ROOT/exports/books/$next_stage/$filename"
    mkdir -p "$(dirname "$dest_path")"
    mv "$full_path" "$dest_path"
    echo "✅ Promoted: $filename"
    echo "   From: $current_stage"
    echo "   To: $next_stage"
}

# Function to publish content to final formats
publish_content() {
    local file_path="$1"
    local full_path="$PROJECT_ROOT/exports/books/$file_path"
    
    if [[ ! -f "$full_path" ]]; then
        echo "❌ File not found: $file_path"
        exit 1
    fi
    
    local filename=$(basename "$file_path" .md)
    local published_dir="$PROJECT_ROOT/exports/books/published"
    
    # Create published directories
    mkdir -p "$published_dir/pdf" "$published_dir/html" "$published_dir/epub"
    
    # Use format generator for professional conversion
    echo "🔄 Generating publication formats..."
    
    # Generate HTML, PDF, and DOCX using format_generator
    python "$PROJECT_ROOT/scripts/format_generator.py" convert \
        --file "$full_path" \
        --format "html,pdf,docx" \
        --title "$filename" \
        --author "Humanized Content"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Published: $filename to multiple formats (HTML, PDF, DOCX)"
        
        # List generated files
        echo "📋 Generated files:"
        find "$PROJECT_ROOT/exports" -name "*${filename}*" -type f -newer "$full_path" | while read -r generated_file; do
            echo "   📄 $(basename "$generated_file")"
        done
    else
        echo "❌ Format generation failed, copying as markdown"
        cp "$full_path" "$published_dir/html/${filename}.md"
        echo "✅ Published HTML: $published_dir/html/${filename}.md"
    fi
}

# Function to list pipeline contents
list_pipeline() {
    local books_dir="$PROJECT_ROOT/exports/books"
    
    echo "📚 Book Publishing Pipeline Status"
    echo "=================================="
    
    for stage in drafts review approved published; do
        echo
        echo "📁 $stage/"
        if [[ -d "$books_dir/$stage" ]]; then
            find "$books_dir/$stage" -name "*.md" -o -name "*.txt" | head -10 | while read -r file; do
                local rel_path="${file#$books_dir/$stage/}"
                echo "   📄 $rel_path"
            done
            
            local count=$(find "$books_dir/$stage" -name "*.md" -o -name "*.txt" | wc -l)
            if [[ $count -gt 10 ]]; then
                echo "   📋 ... and $((count - 10)) more files"
            fi
            
            if [[ $count -eq 0 ]]; then
                echo "   (empty)"
            fi
        else
            echo "   (directory not found)"
        fi
    done
}

# Main script logic
case "${1:-}" in
    "promote")
        if [[ -z "$2" ]]; then
            echo "❌ Error: File path required"
            usage
        fi
        promote_content "$2"
        ;;
    "publish")
        if [[ -z "$2" ]]; then
            echo "❌ Error: File path required"
            usage
        fi
        publish_content "$2"
        ;;
    "list")
        list_pipeline
        ;;
    *)
        usage
        ;;
esac