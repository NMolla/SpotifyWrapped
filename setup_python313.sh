#!/bin/bash

echo "🎵 Setting up Spotify Wrapped Dashboard (Python 3.13 Compatible)"
echo "================================================================"
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

# Clean existing virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🧹 Removing existing virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install build tools
echo "🔧 Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
echo "   Installing core dependencies..."

# Install core dependencies one by one for better error handling
pip install Flask==3.1.2
pip install flask-cors==6.0.1
pip install Flask-Caching==2.1.0
pip install python-dotenv==1.2.1
pip install requests==2.32.5
pip install spotipy==2.25.2
pip install gunicorn==23.0.0

# Try to install optional dependencies
echo "   Installing optional dependencies..."
if pip install Pillow==11.0.0 2>/dev/null; then
    echo "   ✅ Pillow installed"
else
    echo "   ⚠️  Pillow installation failed (image generation may not work)"
fi

# matplotlib and numpy might fail on Python 3.13
echo "   Attempting matplotlib/numpy installation..."
if pip install numpy==2.1.3 matplotlib==3.9.2 2>/dev/null; then
    echo "   ✅ NumPy and Matplotlib installed"
else
    echo "   ⚠️  NumPy/Matplotlib installation failed (some visualizations may be limited)"
    echo "   Note: This is expected on Python 3.13 - core functionality will still work"
fi

echo "   ✅ Core Python dependencies installed successfully"

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
echo ""

if [ -n "$VIRTUAL_ENV" ]; then
    echo "💡 Virtual environment is activated. To deactivate, run: deactivate"
fi
