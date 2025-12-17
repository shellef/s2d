# LiveKit + AssemblyAI Setup Guide

## Overview

We're replacing the problematic MediaRecorder → Whisper API flow with LiveKit + AssemblyAI for real-time transcription.

## Setup Steps

### 1. Add API Keys to .env

```bash
# Get your AssemblyAI API key from: https://www.assemblyai.com/dashboard
ASSEMBLYAI_API_KEY=your-actual-key-here

# LiveKit - Use Cloud or Local
# For local development:
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# For LiveKit Cloud:
# LIVEKIT_URL=wss://your-project.livekit.cloud
# LIVEKIT_API_KEY=<from LiveKit dashboard>
# LIVEKIT_API_SECRET=<from LiveKit dashboard>
```

### 2. Run LiveKit Server Locally (Development)

```bash
# Option A: Using Docker
docker run --rm -p 7880:7880 \
  -e LIVEKIT_API_KEY=devkey \
  -e LIVEKIT_API_SECRET=secret \
  live

kitio/livekit-server:latest \
  --dev

# Option B: Download binary
# Visit: https://github.com/livekit/livekit/releases
# Download for your OS and run:
./livekit-server --dev
```

### 3. Architecture

```
Frontend (React + LiveKit)
    ↓ (Audio Stream via WebRTC)
LiveKit Server
    ↓ (Audio Stream)
AssemblyAI Real-Time STT
    ↓ (Transcripts)
Your Backend WebSocket
    ↓ (Process with GPT-4o)
Frontend (Document Updates)
```

## Benefits

✓ No more WebM fragmentation issues
✓ Real-time transcription (< 100ms latency)
✓ Production-ready WebRTC audio
✓ Automatic reconnection
✓ Better quality transcripts
✓ Cheaper ($0.00037/sec vs $0.006/min for Whisper)

## Next: Update Your .env

Copy `.env.example` to `.env` and add your AssemblyAI API key!
