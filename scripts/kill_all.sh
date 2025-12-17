#!/bin/bash
# Kill all running services

echo "Stopping all services..."

# Kill Python processes (backend + agent)
pkill -9 -f "backend.main"
pkill -9 -f "transcription_agent.py"

# Kill uvicorn processes (in case backend is running via uvicorn)
pkill -9 -f "uvicorn"

# Kill any remaining python processes on port 8000
BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PID" ]; then
    echo "Killing process on port 8000 (PID: $BACKEND_PID)"
    kill -9 $BACKEND_PID 2>/dev/null
fi

# Kill Node/frontend
pkill -9 -f "vite"

sleep 1

echo "All services stopped."
echo ""
echo "Logs preserved at:"
echo "  /tmp/backend.log"
echo "  /tmp/agent.log"
echo "  /tmp/frontend.log"
