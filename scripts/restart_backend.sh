#!/bin/bash
# Restart the backend server

cd /home/eric/work/s2d

echo "Stopping backend..."
pkill -9 -f "backend.main"
sleep 1

echo "Starting backend..."
python -m backend.main > /tmp/backend.log 2>&1 &

BACKEND_PID=$!
sleep 2

# Check if it started
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Backend restarted (PID: $BACKEND_PID)"
    echo "Check logs: tail -f /tmp/backend.log"
else
    echo "Backend failed to start! Check /tmp/backend.log"
fi
