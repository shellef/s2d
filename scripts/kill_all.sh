#!/bin/bash
# Kill all running services

echo "Stopping all services..."

# Kill Python processes (backend + agent)
pkill -9 -f "backend.main"
pkill -9 -f "transcription_agent.py"

# Kill Node/frontend
pkill -9 -f "vite"

sleep 1

echo "All services stopped."
echo ""
echo "Logs preserved at:"
echo "  /tmp/backend.log"
echo "  /tmp/agent.log"
echo "  /tmp/frontend.log"
