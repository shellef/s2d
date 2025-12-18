#!/bin/bash
# Start all LiveKit integration services
# This script starts the backend, agent, and frontend in separate tmux panes

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install tmux"
    echo "  macOS: brew install tmux"
    exit 1
fi

# Load environment variables
if [ -f ~/.env.s2d ]; then
    export $(cat ~/.env.s2d | grep -v '^#' | xargs)
fi

# Create new tmux session
SESSION_NAME="s2d-livekit"

# Kill existing session if it exists
tmux kill-session -t $SESSION_NAME 2>/dev/null

# Create new session with backend
tmux new-session -d -s $SESSION_NAME -n "backend" "cd /home/eric/work/s2d && python -m backend.main"

# Split window and start agent
tmux split-window -v -t $SESSION_NAME "cd /home/eric/work/s2d && python backend/transcription_agent.py start"

# Split window and start frontend
tmux split-window -h -t $SESSION_NAME "cd /home/eric/work/s2d/frontend && npm run dev"

# Arrange panes
tmux select-layout -t $SESSION_NAME tiled

# Attach to session
echo "Starting all services in tmux session: $SESSION_NAME"
echo ""
echo "Services will start in separate panes:"
echo "  - Backend (FastAPI)"
echo "  - LiveKit Agent"
echo "  - Frontend (Vite)"
echo ""
echo "To detach: Ctrl+B then D"
echo "To reattach: tmux attach -t $SESSION_NAME"
echo "To kill all: tmux kill-session -t $SESSION_NAME"
echo ""
sleep 2
tmux attach -t $SESSION_NAME
