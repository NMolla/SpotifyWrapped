#!/bin/bash

echo "🎵 Setting up Spotify Wrapped Dashboard..."
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

echo "✅ Prerequisites detected:"
echo "   Python: $(python3 --version)"
echo "   Node:   $(node --version)"
echo ""

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt
echo "   ✅ Python dependencies installed"

# Install Node dependencies
echo "📦 Installing Node dependencies..."
cd frontend && npm install --silent && cd ..
echo "   ✅ Node dependencies installed"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your Spotify credentials:"
    echo "   1. Go to https://developer.spotify.com/dashboard"
    echo "   2. Create a new app"
    echo "   3. Add http://127.0.0.1:5000/callback as redirect URI"
    echo "   4. Copy your Client ID and Client Secret to .env"
    echo ""
else
    echo "✅ Environment file exists"
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    echo "📁 Created data directory"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   Option 1: ./run_dev.sh    (runs both servers together)"
echo "   Option 2: Run separately:"
echo "     Terminal 1: ./run_backend.sh"
echo "     Terminal 2: ./run_frontend.sh"
echo ""
echo "📱 The app will be available at http://localhost:3000"
echo "
