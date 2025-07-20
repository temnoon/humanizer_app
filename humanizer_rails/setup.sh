#!/bin/bash

# Humanizer Rails Setup Script

echo "🚦 Setting up Humanizer Rails Backend..."

# Check if we're in the right directory
if [ ! -f "Gemfile" ]; then
    echo "❌ Error: Please run this script from the humanizer_rails directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Check Ruby version
echo "🔍 Checking Ruby version..."
ruby_version=$(ruby -v)
echo "Ruby version: $ruby_version"

# Check if Rails is installed
if ! command -v rails &> /dev/null; then
    echo "📦 Installing Rails..."
    gem install rails
else
    echo "✅ Rails is already installed: $(rails -v)"
fi

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please install with: brew install postgresql"
    exit 1
fi

# Install gems
echo "📦 Installing gems..."
if command -v bundle &> /dev/null; then
    bundle install
else
    echo "📦 Installing bundler first..."
    gem install bundler
    bundle install
fi

# Database setup
echo "🗄️  Setting up database..."
if bundle exec rails db:version 2>/dev/null; then
    echo "✅ Database already exists"
else
    echo "🔨 Creating database..."
    bundle exec rails db:create
fi

echo "🔄 Running migrations..."
bundle exec rails db:migrate

# Check if Python API is running
echo "🐍 Checking Python API connection..."
if curl -s http://localhost:5000/status > /dev/null; then
    echo "✅ Python API is accessible at localhost:5000"
else
    echo "⚠️  Python API not accessible at localhost:5000"
    echo "   Please start your Python backend first"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the Rails server: bundle exec rails server -p 3001"
echo "2. Test the API: curl http://localhost:3001/llm_tasks"
echo "3. Check routes: bundle exec rails routes"
echo ""
echo "🔗 API will be available at http://localhost:3001"
echo "📚 See README.md for full documentation"
