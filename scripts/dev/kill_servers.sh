#!/bin/bash
# Script to kill both backend and frontend servers

echo "🛑 Stopping Spotify Wrapped Servers..."
echo "======================================"
echo ""

# Function to kill process on a port
kill_port() {
    local port=$1
    local name=$2
    
    echo "🔍 Checking port $port ($name)..."
    
    # Get PIDs running on the port
    PIDS=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$PIDS" ]; then
        echo "   ✓ No process running on port $port"
    else
        echo "   ⚠️  Found process(es) on port $port: $PIDS"
        echo "   🗑️  Killing process(es)..."
        kill -9 $PIDS 2>/dev/null
        
        # Verify it's killed
        sleep 1
        if lsof -ti:$port >/dev/null 2>&1; then
            echo "   ❌ Failed to kill process on port $port"
        else
            echo "   ✅ Successfully killed $name on port $port"
        fi
    fi
}

# Kill backend server (port 5000)
kill_port 5000 "Backend Server"

echo ""

# Kill frontend server (port 3000)
kill_port 3000 "Frontend Server"

echo ""
echo "✨ Done! All servers stopped."
echo ""
echo "💡 To restart the servers, run:"
echo "   ./run_dev.sh        (Terminal tabs)"
echo "   ./run_dev_iterm.sh  (iTerm2 tabs)"
