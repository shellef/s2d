# Starting the LiveKit Integration

The LiveKit integration is now fully configured and ready to use. Follow these steps to start all components:

## Prerequisites

Make sure your `.env` file has these credentials:

```bash
# AssemblyAI API
ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d

# LiveKit Cloud
LIVEKIT_URL=wss://first-lrohe7si.livekit.cloud
LIVEKIT_API_KEY=APIteQkPqYrZbnX
LIVEKIT_API_SECRET=ZYfpBsP7MxeG8ghORhi8BgDxdObehjwNxrJLdFNRvSMB
```

## Starting All Services

You need to run **3 components** in separate terminal windows:

### Terminal 1: Backend Server
```bash
cd /home/eric/work/s2d
python -m backend.main
```

This starts the FastAPI backend on `http://localhost:8000`

### Terminal 2: LiveKit Transcription Agent
```bash
cd /home/eric/work/s2d
export LIVEKIT_URL=wss://first-lrohe7si.livekit.cloud
export LIVEKIT_API_KEY=APIteQkPqYrZbnX
export LIVEKIT_API_SECRET=ZYfpBsP7MxeG8ghORhi8BgDxdObehjwNxrJLdFNRvSMB
export ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d
python transcription_agent.py start
```

This starts the LiveKit agent that:
- Connects to LiveKit Cloud
- Receives audio from browser
- Sends to AssemblyAI for transcription
- Forwards transcriptions to backend WebSocket

### Terminal 3: Frontend Development Server
```bash
cd /home/eric/work/s2d/frontend
npm run dev
```

This starts the React frontend on `http://localhost:5173` (or next available port)

## Testing the Application

1. Open your browser to `http://localhost:5174` (or the port shown in Terminal 3)
2. Click "Start Recording" - this will:
   - Request a LiveKit token from the backend
   - Connect to LiveKit Cloud
   - Enable your microphone
3. Start speaking
4. Watch the transcription appear in real-time
5. Watch GPT-4o generate formatted documentation

## Architecture Flow

```
Browser Microphone
    ↓ (WebRTC)
LiveKit Cloud
    ↓ (LiveKit Protocol)
Transcription Agent (transcription_agent.py)
    ↓ (AssemblyAI Streaming)
AssemblyAI API
    ↓ (Transcription Events)
Transcription Agent
    ↓ (WebSocket)
Backend WebSocket (ws://localhost:8000/ws)
    ↓ (GPT-4o Processing)
Backend
    ↓ (Document Patches via WebSocket)
Frontend React App
```

## Troubleshooting

**Agent fails to start:**
- Make sure environment variables are exported in Terminal 2
- Check that LiveKit credentials are correct

**Frontend fails to get token:**
- Make sure backend is running (Terminal 1)
- Check backend logs for errors

**No transcription appearing:**
- Check Terminal 2 logs - should see "Final: <your speech>"
- Make sure AssemblyAI API key is valid
- Check backend WebSocket connection

**Audio not being captured:**
- Grant microphone permissions in browser
- Check browser console for errors
- Make sure LiveKit Room connects successfully

## Success Indicators

When everything is working, you should see:

**Terminal 1 (Backend):**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 (Agent):**
```
INFO:livekit.agents:registered worker
INFO:livekit.agents:agent_name: "", id: "AW_xxxxx"
INFO:root:Agent ready, waiting for audio tracks...
```

**Terminal 3 (Frontend):**
```
➜  Local:   http://localhost:5174/
```

**Browser Console:**
When you start recording:
```
Microphone enabled
Connected to backend WebSocket
```

## Next Steps

Once you verify everything works:
1. The frontend is already integrated with SimpleAudioCapture
2. Transcriptions flow automatically to GPT-4o
3. Documents update in real-time
4. No more Whisper format errors!
