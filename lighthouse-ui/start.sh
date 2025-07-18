#!/bin/bash

# Lighthouse UI Startup Script

echo "✨ Starting Lighthouse UI..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "Starting UI on http://localhost:3000..."
npm run dev
