#!/bin/bash
# Restart the LiveKit transcription agent

cd /home/eric/work/s2d

# Load environment variables from ~/.env.s2d file
if [ -f ~/.env.s2d ]; then
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

echo "Stopping old agent processes..."
pkill -9 -f "transcription_agent.py"
sleep 2

echo "Starting LiveKit agent..."
python backend/transcription_agent.py start > /tmp/agent.log 2>&1 &

AGENT_PID=$!
sleep 3

echo "Agent restarted (PID: $AGENT_PID)"
echo ""
echo "Check logs: tail -f /tmp/agent.log"
echo "Watch for: tail -f /tmp/agent.log | grep -E 'Final|ERROR|Transcribing'"
