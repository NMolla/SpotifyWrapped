#!/bin/bash
# Script to run the frontend server

echo "🚀 Starting Spotify Wrapped Frontend..."
echo "======================================"

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

# Run the React app (with browser auto-open disabled)
echo "✅ Starting React server on port 3000..."
BROWSER=none npm start
