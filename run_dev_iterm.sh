#!/bin/bash
# Script to run both backend and frontend servers in separate iTerm2 tabs

echo "🎵 Spotify Wrapped Full Stack Application (iTerm2)"
echo "=================================================="
echo ""

# Get the current directory
PROJECT_DIR=$(pwd)

# Function to open new iTerm2 tab and run command
open_iterm_tab() {
    local title=$1
    local command=$2
    
    osascript <<EOF
        tell application "iTerm"
            activate
            tell current window
                create tab with default profile
                tell current session
                    write text "cd '$PROJECT_DIR'"
                    write text "echo '🚀 $title'"
                    write text "$command"
                end tell
            end tell
        end tell
EOF
}

# Function to check if servers are running
check_servers() {
    echo "🔍 Checking for existing servers..."
    
    # Check if backend is running on port 5000
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Backend already running on port 5000"
        echo "   Kill it with: ./kill_servers.sh"
        backend_running=true
    else
        backend_running=false
    fi
    
    # Check if frontend is running on port 3000
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Frontend already running on port 3000"
        echo "   Kill it with: ./kill_servers.sh"
        frontend_running=true
    else
        frontend_running=false
    fi
}

# Check for existing servers
check_servers

# Start backend in new tab if not running
if [ "$backend_running" = false ]; then
    echo "📡 Opening Backend Server in new iTerm2 tab..."
    open_iterm_tab "Backend Server (Port 5000)" "./run_backend.sh"
else
    echo "⏭️  Skipping backend (already running)"
fi

# Wait a bit for backend to start
sleep 2

# Start frontend in new tab if not running
if [ "$frontend_running" = false ]; then
    echo "🎨 Opening Frontend Server in new iTerm2 tab..."
    open_iterm_tab "Frontend Server (Port 3000)" "./run_frontend.sh"
else
    echo "⏭️  Skipping frontend (already running)"
fi

echo ""
echo "✅ Servers starting in separate iTerm2 tabs!"
echo ""
echo "📍 URLs:"
echo "   Backend:  http://127.0.0.1:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "💡 iTerm2 Tips:"
echo "   - Switch between tabs with Cmd+← or Cmd+→"
echo "   - Or use Cmd+[number] to jump to specific tab"
echo "   - Stop a server with Ctrl+C in its tab"
echo "   - Close a tab with Cmd+W"
echo ""

# Wait for servers to fully start then open the browser
sleep 5
echo "🌐 Opening browser (single tab)..."
open http://localhost:3000

echo "✨ Setup complete! Check your iTerm2 tabs and browser."
