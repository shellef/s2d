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

**2. Update Your ~/.env.s2d File**

```bash
# Create ~/.env.s2d from example
cp .env.example ~/.env.s2d

# Add these secrets to ~/.env.s2d:
OPENAI_API_KEY=<your-existing-key>              # Required
ASSEMBLYAI_API_KEY=your-assemblyai-api-key      # Optional
LIVEKIT_URL=wss://your-project.livekit.cloud    # From step 1
LIVEKIT_API_KEY=<from-livekit-dashboard>        # From step 1
LIVEKIT_API_SECRET=<from-livekit-dashboard>     # From step 1

# Note: Regular configuration (models, ports, etc.) is in config.yaml at repo root
# You can override config.yaml values by adding them to ~/.env.s2d if needed
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
