#!/bin/bash
# Unified development script for Spotify Wrapped

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project directory
PROJECT_DIR=$(pwd)

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to show usage
show_usage() {
    echo "🎵 Spotify Wrapped Development Tool"
    echo "===================================="
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start both backend and frontend servers"
    echo "  stop        - Stop all running servers"
    echo "  backend     - Start backend server only"
    echo "  frontend    - Start frontend server only"
    echo "  status      - Check server status"
    echo "  clean       - Clean cache and temporary files"
    echo "  setup       - Run initial setup"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh start    # Start development servers"
    echo "  ./dev.sh stop     # Stop all servers"
    echo "  ./dev.sh status   # Check what's running"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start backend
start_backend() {
    print_color $BLUE "📡 Starting Backend Server..."
    
    if check_port 5000; then
        print_color $YELLOW "  ⚠️  Backend already running on port 5000"
        return 1
    fi
    
    # Check virtual environment
    if [ ! -d ".venv" ]; then
        print_color $YELLOW "  📦 Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Start backend
    (
        cd backend
        source ../.venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt 2>/dev/null || pip install -q -r requirements-minimal.txt
        export FLASK_PORT=5000
        export FLASK_ENV=development
        print_color $GREEN "  ✅ Backend starting on http://127.0.0.1:5000"
        python app.py
    )
}

# Function to start frontend
start_frontend() {
    print_color $BLUE "🎨 Starting Frontend Server..."
    
    if check_port 3000; then
        print_color $YELLOW "  ⚠️  Frontend already running on port 3000"
        return 1
    fi
    
    # Check node_modules
    if [ ! -d "frontend/node_modules" ]; then
        print_color $YELLOW "  📦 Installing Node dependencies..."
        (cd frontend && npm install --silent)
    fi
    
    # Start frontend
    (
        cd frontend
        print_color $GREEN "  ✅ Frontend starting on http://localhost:3000"
        BROWSER=none npm start
    )
}

# Function to start both servers in tabs
start_servers() {
    print_color $BLUE "🚀 Starting Spotify Wrapped Development Servers..."
    echo ""
    
    # Check if servers are already running
    local backend_running=false
    local frontend_running=false
    
    if check_port 5000; then
        print_color $YELLOW "⚠️  Backend already running on port 5000"
        backend_running=true
    fi
    
    if check_port 3000; then
        print_color $YELLOW "⚠️  Frontend already running on port 3000"
        frontend_running=true
    fi
    
    # Open new terminal tabs for servers
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [ "$backend_running" = false ]; then
            osascript <<EOF
                tell application "Terminal"
                    activate
                    tell application "System Events" to keystroke "t" using command down
                    delay 0.5
                    do script "cd '$PROJECT_DIR' && ./dev.sh backend" in front window
                end tell
EOF
            print_color $GREEN "✅ Backend server opening in new tab..."
        fi
        
        sleep 2
        
        if [ "$frontend_running" = false ]; then
            osascript <<EOF
                tell application "Terminal"
                    activate
                    tell application "System Events" to keystroke "t" using command down
                    delay 0.5
                    do script "cd '$PROJECT_DIR' && ./dev.sh frontend" in front window
                end tell
EOF
            print_color $GREEN "✅ Frontend server opening in new tab..."
        fi
        
        # Open browser after a delay
        sleep 5
        if [ "$frontend_running" = false ]; then
            print_color $BLUE "🌐 Opening browser..."
            open http://localhost:3000
        fi
    else
        # Linux/Other - run in background
        if [ "$backend_running" = false ]; then
            ./dev.sh backend &
            print_color $GREEN "✅ Backend server started in background"
        fi
        
        sleep 2
        
        if [ "$frontend_running" = false ]; then
            ./dev.sh frontend &
            print_color $GREEN "✅ Frontend server started in background"
        fi
    fi
    
    echo ""
    print_color $GREEN "✨ Development servers ready!"
    echo "   Backend:  http://127.0.0.1:5000"
    echo "   Frontend: http://localhost:3000"
}

# Function to stop servers
stop_servers() {
    print_color $RED "🛑 Stopping all servers..."
    echo ""
    
    # Kill backend (port 5000)
    local PIDS=$(lsof -ti:5000 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null
        print_color $GREEN "  ✅ Stopped backend server"
    else
        echo "  ✓ Backend not running"
    fi
    
    # Kill frontend (port 3000)
    PIDS=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null
        print_color $GREEN "  ✅ Stopped frontend server"
    else
        echo "  ✓ Frontend not running"
    fi
    
    echo ""
    print_color $GREEN "✨ All servers stopped"
}

# Function to check server status
check_status() {
    print_color $BLUE "🔍 Checking server status..."
    echo ""
    
    # Check backend
    if check_port 5000; then
        print_color $GREEN "  ✅ Backend:  RUNNING on port 5000"
        echo "     URL: http://127.0.0.1:5000"
        echo "     PID: $(lsof -ti:5000)"
    else
        print_color $RED "  ❌ Backend:  NOT RUNNING"
    fi
    
    echo ""
    
    # Check frontend  
    if check_port 3000; then
        print_color $GREEN "  ✅ Frontend: RUNNING on port 3000"
        echo "     URL: http://localhost:3000"
        echo "     PID: $(lsof -ti:3000)"
    else
        print_color $RED "  ❌ Frontend: NOT RUNNING"
    fi
}

# Function to clean temporary files
clean_project() {
    print_color $BLUE "🧹 Cleaning temporary files..."
    echo ""
    
    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    print_color $GREEN "  ✅ Cleaned Python cache"
    
    # .DS_Store files
    find . -name ".DS_Store" -delete 2>/dev/null
    print_color $GREEN "  ✅ Cleaned .DS_Store files"
    
    # Old logs
    find . -name "*.log" -mtime +7 -delete 2>/dev/null
    print_color $GREEN "  ✅ Cleaned old log files"
    
    echo ""
    print_color $GREEN "✨ Cleanup complete"
}

# Function to run setup
run_setup() {
    print_color $BLUE "🔧 Running project setup..."
    echo ""
    
    # Check prerequisites
    if ! command -v python3 &> /dev/null; then
        print_color $RED "❌ Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_color $RED "❌ Node.js is not installed"
        exit 1
    fi
    
    print_color $GREEN "✅ Prerequisites found:"
    echo "   Python: $(python3 --version)"
    echo "   Node:   $(node --version)"
    echo ""
    
    # Virtual environment
    if [ ! -d ".venv" ]; then
        print_color $YELLOW "📦 Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Python dependencies
    print_color $YELLOW "📚 Installing Python dependencies..."
    source .venv/bin/activate
    pip install -q --upgrade pip setuptools wheel
    pip install -q -r backend/requirements.txt 2>/dev/null || pip install -q -r backend/requirements-minimal.txt
    
    # Node dependencies
    print_color $YELLOW "📦 Installing Node dependencies..."
    (cd frontend && npm install --silent)
    
    # Environment file
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_color $YELLOW "📝 Created .env file - please add your Spotify credentials"
        fi
    fi
    
    # Data directory
    [ ! -d "data" ] && mkdir -p data
    
    echo ""
    print_color $GREEN "✨ Setup complete!"
    echo ""
    echo "Next: Add your Spotify credentials to .env, then run:"
    echo "  ./dev.sh start"
}

# Main command handler
case "$1" in
    start)
        start_servers
        ;;
    stop)
        stop_servers
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    status)
        check_status
        ;;
    clean)
        clean_project
        ;;
    setup)
        run_setup
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        if [ -z "$1" ]; then
            show_usage
        else
            print_color $RED "❌ Unknown command: $1"
            echo ""
            show_usage
            exit 1
        fi
        ;;
esac
