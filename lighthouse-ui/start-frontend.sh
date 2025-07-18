#!/bin/bash

# Kill any process running on port 3100
echo "Stopping any existing process on port 3100..."
lsof -ti:3100 | xargs kill -9 2>/dev/null || true

# Wait a moment for the port to be freed
sleep 1

# Start the frontend on port 3100
echo "Starting frontend on port 3100..."
npm run dev -- --port 3100