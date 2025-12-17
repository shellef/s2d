#!/bin/bash
# Restart the LiveKit transcription agent

cd /home/eric/work/s2d

echo "Stopping old agent processes..."
pkill -9 -f "transcription_agent.py"
sleep 2

echo "Starting LiveKit agent..."
LIVEKIT_URL=wss://first-lrohe7si.livekit.cloud \
LIVEKIT_API_KEY=APIteQkPqYrZbnX \
LIVEKIT_API_SECRET=ZYfpBsP7MxeG8ghORhi8BgDxdObehjwNxrJLdFNRvSMB \
ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d \
python backend/transcription_agent.py start > /tmp/agent.log 2>&1 &

AGENT_PID=$!
sleep 3

echo "Agent restarted (PID: $AGENT_PID)"
echo ""
echo "Check logs: tail -f /tmp/agent.log"
echo "Watch for: tail -f /tmp/agent.log | grep -E 'Final|ERROR|Transcribing'"
