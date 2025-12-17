# Quick Start Guide - LiveKit + AssemblyAI Integration

## Current Status

I've set up the foundation for LiveKit + AssemblyAI integration. Here's what's ready and what you need to do:

### ✅ Completed

1. **Backend Setup**
   - LiveKit service for token generation
   - API endpoint `/livekit/token` for getting room tokens
   - AssemblyAI plugin installed
   - Configuration updated

2. **Frontend Setup**
   - LiveKit React components installed
   - Basic component structure created

### 🔧 What You Need To Do

**1. Get LiveKit Cloud Credentials**

Visit: https://cloud.livekit.io/
- Sign up (free tier available)
- Create a new project
- Copy these values:

```
LIVEKIT_URL=wss://your-project-XXXXX.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=secretxxxxxxxx
```

**2. Update Your .env File**

```bash
# Create .env from example
cp .env.example .env

# Add these to .env:
ASSEMBLYAI_API_KEY=c62f057171f846cba51cf6d27a1d689d
LIVEKIT_URL=wss://your-project.livekit.cloud  # From step 1
LIVEKIT_API_KEY=<from-livekit-dashboard>       # From step 1
LIVEKIT_API_SECRET=<from-livekit-dashboard>    # From step 1
OPENAI_API_KEY=<your-existing-key>
```

**3. Test the Current Whisper Fix**

Before switching to LiveKit, let's test if the chunk accumulation fix works:

```bash
# Start backend
python -m backend.main

# Start frontend (in another terminal)
cd frontend && npm run dev

# Try recording - it should work now with complete WebM blobs!
```

## Next Steps

Once you have LiveKit credentials, I'll complete the integration to replace Whisper with AssemblyAI real-time transcription.

**OR** if the current Whisper fix works well enough, we can stick with that!

Let me know which path you prefer.
