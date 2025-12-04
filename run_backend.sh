#!/bin/bash
# Script to run the backend server

echo "🚀 Starting Spotify Wrapped Backend..."
echo "=================================="

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../.venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Install/upgrade requirements
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Set environment variables
export FLASK_PORT=5000
export FLASK_ENV=development

# Run the Flask app
echo "✅ Starting Flask server on port 5000..."
python app.py
