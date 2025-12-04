#!/bin/bash
# Script to run both backend and frontend servers

echo "🎵 Spotify Wrapped Full Stack Application"
echo "========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap for clean exit
trap cleanup EXIT INT TERM

# Start backend
echo "📡 Starting Backend Server..."
./run_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Frontend Server..."
./run_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "   Backend:  http://127.0.0.1:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
