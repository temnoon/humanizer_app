#!/bin/bash

# Quick start script for Humanizer Rails
# This script starts the Rails server and provides useful commands

echo "🚦 Humanizer Rails - Quick Start"
echo "================================"

# Check if we're in the Rails directory
if [ ! -f "Gemfile" ]; then
    echo "❌ Please run this from the humanizer_rails directory"
    echo "   cd /Users/tem/humanizer-lighthouse/humanizer_rails"
    exit 1
fi

# Function to start Rails server
start_server() {
    echo "🚀 Starting Rails server on port 3001..."
    echo "   API will be available at: http://localhost:3001"
    echo "   Press Ctrl+C to stop"
    echo ""
    bundle exec rails server -p 3001
}

# Function to run tests
run_tests() {
    echo "🧪 Running setup verification..."
    ruby test_setup.rb
}

# Function to show useful commands
show_commands() {
    echo "📋 Useful commands:"
    echo ""
    echo "🔧 Setup & Start:"
    echo "  ./setup.sh                     # Initial setup"
    echo "  ./quick_start.sh               # This script"
    echo "  bundle exec rails server -p 3001  # Start server manually"
    echo ""
    echo "🗄️ Database:"
    echo "  bundle exec rails db:migrate   # Run migrations"
    echo "  bundle exec rails db:console   # Database console"
    echo "  bundle exec rails console      # Rails console"
    echo ""
    echo "🧪 Testing:"
    echo "  ruby test_setup.rb             # Verify setup"
    echo "  curl http://localhost:3001/llm_tasks  # Test API"
    echo ""
    echo "📊 API Endpoints:"
    echo "  GET    /llm_tasks              # List LLM tasks"
    echo "  POST   /llm_tasks              # Create LLM task"
    echo "  GET    /writebooks             # List writebooks"
    echo "  POST   /writebooks             # Create writebook"
    echo "  GET    /writebooks/:id/sections # List sections"
    echo "  POST   /api/v1/archive/humanize # Python bridge"
    echo ""
    echo "📚 Documentation:"
    echo "  cat README.md                  # Full documentation"
    echo "  bundle exec rails routes      # Show all routes"
}

# Parse command line arguments
case "${1:-start}" in
    "start"|"server"|"s")
        start_server
        ;;
    "test"|"verify"|"t")
        run_tests
        ;;
    "help"|"commands"|"h")
        show_commands
        ;;
    "setup")
        echo "🔧 Running setup..."
        ./setup.sh
        ;;
    *)
        echo "Usage: $0 [start|test|help|setup]"
        echo ""
        echo "Commands:"
        echo "  start (default) - Start the Rails server"
        echo "  test           - Run verification tests"
        echo "  help           - Show useful commands"
        echo "  setup          - Run initial setup"
        echo ""
        echo "Examples:"
        echo "  $0              # Start server"
        echo "  $0 start        # Start server"
        echo "  $0 test         # Run tests"
        echo "  $0 help         # Show commands"
        ;;
esac
