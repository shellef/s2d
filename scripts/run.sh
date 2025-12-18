#!/bin/bash
# Simple startup script for all services

cd /home/eric/work/s2d

# Load environment variables from ~/.env.s2d file
if [ -f ~/.env.s2d ]; then
    echo "Loading environment variables from ~/.env.s2d..."
    set -a
    source ~/.env.s2d
    set +a
else
    echo "ERROR: ~/.env.s2d file not found!"
    echo "Please create ~/.env.s2d based on .env.example"
    exit 1
fi

# Verify required environment variables
required_vars=("LIVEKIT_URL" "LIVEKIT_API_KEY" "LIVEKIT_API_SECRET" "ASSEMBLYAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Required environment variable $var is not set in ~/.env.s2d"
        exit 1
    fi
done

echo "Starting all services..."
echo ""

# Start backend
echo "1. Starting backend server..."
python -m backend.main > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready (retry for up to 10 seconds)
echo "   Waiting for backend to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✓ Backend running (PID: $BACKEND_PID)"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "   ✗ Backend failed to start after 10 seconds"
        echo "   Check logs: tail -f /tmp/backend.log"
        exit 1
    fi
    sleep 0.5
done

# Start LiveKit agent (environment variables already loaded from .env)
echo "2. Starting LiveKit transcription agent..."
python backend/transcription_agent.py start > /tmp/agent.log 2>&1 &
AGENT_PID=$!
sleep 3
echo "   ✓ Agent started (PID: $AGENT_PID)"

# Start frontend
echo "3. Starting frontend dev server..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3
echo "   ✓ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "All services running!"
echo ""
echo "Open your browser to: http://localhost:5173 (or check /tmp/frontend.log for actual port)"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Agent:    tail -f /tmp/agent.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "To stop all:"
echo "  killall -9 python node"
