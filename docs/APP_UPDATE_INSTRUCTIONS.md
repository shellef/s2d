# How to Switch to LiveKit in Your App

Once you have LiveKit credentials in `.env`, make these simple changes to `frontend/src/App.jsx`:

## Option 1: Quick Test (Minimal Changes)

Replace just the audio recorder:

```jsx
// At the top, replace:
import useAudioRecorder from './hooks/useAudioRecorder';

// With:
import { SimpleAudioCapture } from './components/SimpleAudioCapture';

// Then in your JSX, replace the ControlPanel section with:
<SimpleAudioCapture />
```

## Option 2: Full Integration (Recommended)

I can do this for you! Just say "integrate LiveKit into App.jsx" and I'll:
1. Import SimpleAudioCapture component
2. Remove old useAudioRecorder hook
3. Update the UI to use LiveKit
4. Keep all your existing document/transcription logic

The transcriptions will come through your existing WebSocket connection from the LiveKit agent!

## What Stays The Same

- Your WebSocket connection to backend (`useWebSocket`)
- Document state management (`useDocument`)
- GPT-4o processing pipeline
- All UI components

## What Changes

- Audio capture: useAudioRecorder → SimpleAudioCapture
- Audio streaming: Browser → LiveKit → AssemblyAI (instead of Browser → Whisper)

That's it! The rest of your app works exactly the same.
