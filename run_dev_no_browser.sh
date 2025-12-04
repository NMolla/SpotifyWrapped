#!/bin/bash
# Script to run both backend and frontend servers WITHOUT opening browser

echo "🎵 Spotify Wrapped Full Stack Application"
echo "========================================="
echo ""

# Get the current directory
PROJECT_DIR=$(pwd)

# Function to open new terminal tab and run command (macOS)
open_terminal_tab() {
    local title=$1
    local command=$2
    
    osascript <<EOF
        tell application "Terminal"
            activate
            tell application "System Events" to keystroke "t" using command down
            delay 0.5
            do script "cd '$PROJECT_DIR' && echo '🚀 $title' && $command" in front window
        end tell
EOF
}

# Function to check if servers are running
check_servers() {
    echo "🔍 Checking for existing servers..."
    
    # Check if backend is running on port 5000
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Backend already running on port 5000"
        echo "   Kill it with: kill -9 \$(lsof -ti:5000)"
        backend_running=true
    else
        backend_running=false
    fi
    
    # Check if frontend is running on port 3000
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Frontend already running on port 3000"
        echo "   Kill it with: kill -9 \$(lsof -ti:3000)"
        frontend_running=true
    else
        frontend_running=false
    fi
}

# Check for existing servers
check_servers

# Start backend in new tab if not running
if [ "$backend_running" = false ]; then
    echo "📡 Opening Backend Server in new tab..."
    open_terminal_tab "Backend Server (Port 5000)" "./run_backend.sh"
else
    echo "⏭️  Skipping backend (already running)"
fi

# Wait a bit for backend to start
sleep 2

# Start frontend in new tab if not running
if [ "$frontend_running" = false ]; then
    echo "🎨 Opening Frontend Server in new tab..."
    open_terminal_tab "Frontend Server (Port 3000)" "./run_frontend.sh"
else
    echo "⏭️  Skipping frontend (already running)"
fi

echo ""
echo "✅ Servers starting in separate Terminal tabs!"
echo ""
echo "📍 URLs (open manually when ready):"
echo "   Backend:  http://127.0.0.1:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "💡 Tips:"
echo "   - Each server runs in its own tab for easy monitoring"
echo "   - Switch between tabs with Cmd+Shift+[ or Cmd+Shift+]"
echo "   - Stop a server with Ctrl+C in its tab"
echo "   - Close a tab with Cmd+W"
echo ""
echo "✨ Servers starting! Open http://localhost:3000 when ready."
