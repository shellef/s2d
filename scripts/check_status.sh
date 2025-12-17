#!/bin/bash
# Check status of all services

echo "=== SERVICE STATUS ==="
echo ""

# Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend:  Running (http://localhost:8000)"
else
    echo "✗ Backend:  Not running"
fi

# Agent
if pgrep -f "transcription_agent.py" > /dev/null; then
    echo "✓ Agent:    Running (PID: $(pgrep -f 'transcription_agent.py' | head -1))"
    # Check if registered
    if tail -10 /tmp/agent.log 2>/dev/null | grep -q "registered worker"; then
        echo "            Registered with LiveKit Cloud"
    fi
else
    echo "✗ Agent:    Not running"
fi

# Frontend
if pgrep -f "vite" > /dev/null; then
    PORT=$(grep -o "localhost:[0-9]*" /tmp/frontend.log 2>/dev/null | head -1 | cut -d: -f2)
    if [ -n "$PORT" ]; then
        echo "✓ Frontend: Running (http://localhost:$PORT)"
    else
        echo "✓ Frontend: Running (check /tmp/frontend.log for port)"
    fi
else
    echo "✗ Frontend: Not running"
fi

echo ""
echo "=== QUICK ACTIONS ==="
echo "View agent logs:     tail -f /tmp/agent.log | grep -E 'Final|ERROR'"
echo "View backend logs:   tail -f /tmp/backend.log"
echo "View frontend logs:  tail -f /tmp/frontend.log"
echo ""
echo "Restart agent:       ./scripts/restart_agent.sh"
echo "Stop all:            ./scripts/kill_all.sh"
echo "Start all:           ./scripts/run.sh"
