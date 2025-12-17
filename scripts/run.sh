#!/bin/bash
# Simple startup script for all services

cd /home/eric/work/s2d

echo "Starting all services..."
echo ""

# Start backend
echo "1. Starting backend server..."
python -m backend.main > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Check backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✓ Backend running (PID: $BACKEND_PID)"
else
    echo "   ✗ Backend failed to start"
    exit 1
fi

# Start LiveKit agent
echo "2. Starting LiveKit transcription agent..."
LIVEKIT_URL=wss://first-lrohe7si.livekit.cloud \
LIVEKIT_API_KEY=APIteQkPqYrZbnX \
LIVEKIT_API_SECRET=ZYfpBsP7MxeG8ghORhi8BgDxdObehjwNxrJLdFNRvSMB \
ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d \
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
