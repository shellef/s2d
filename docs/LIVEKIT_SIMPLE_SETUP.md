# LiveKit + AssemblyAI Simple Setup

## What This Does

Real-time speech-to-text using LiveKit (audio streaming) + AssemblyAI (transcription) - **the simplest possible setup**.

```
Browser → LiveKit → AssemblyAI → Your Backend → Document Updates
```

## Step 1: Get LiveKit Credentials (2 minutes)

1. Go to https://cloud.livekit.io/
2. Sign up (free tier available)
3. Create a new project
4. Copy these three values:
   - WebSocket URL (looks like: `wss://your-project-xxxxx.livekit.cloud`)
   - API Key (starts with `API`)
   - API Secret

## Step 2: Create .env File

```bash
# Copy example
cp .env.example .env

# Edit .env and add:
ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d
LIVEKIT_URL=wss://your-project-xxxxx.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=secretxxxxxxxxx
OPENAI_API_KEY=<your-existing-key>
```

## Step 3: Run Everything

**Terminal 1 - Backend:**
```bash
python -m backend.main
```

**Terminal 2 - Transcription Agent:**
```bash
python transcription_agent.py start
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 4: Update Frontend

Replace the audio recorder in `App.jsx`:

```jsx
// OLD:
import useAudioRecorder from './hooks/useAudioRecorder';

// NEW:
import { SimpleAudioCapture } from './components/SimpleAudioCapture';

// In your component, replace the recorder with:
<SimpleAudioCapture />
```

## How It Works

1. User clicks "Start Recording" in browser
2. Frontend gets LiveKit token from your backend
3. Frontend connects to LiveKit and streams microphone audio
4. `transcription_agent.py` receives audio from LiveKit
5. Agent sends audio to AssemblyAI for real-time transcription
6. Agent forwards transcriptions to your backend WebSocket
7. Your existing GPT-4o pipeline processes transcriptions
8. Document updates sent to frontend

## Benefits

✓ No more WebM fragmentation issues
✓ Real-time (< 100ms latency)
✓ Production-ready audio streaming
✓ Cheaper than Whisper
✓ Better accuracy
✓ Auto-reconnection

## Troubleshooting

**"Failed to connect"**: Check that all three LiveKit env vars are set correctly in .env

**Agent not starting**: Make sure you have AssemblyAI API key in .env or as environment variable

**No transcriptions**: Check that the agent is running in Terminal 2

## That's It!

Once LiveKit credentials are in .env, the whole system works automatically.
