/**
 * LiveKit Transcription Component - Real-time audio transcription using LiveKit + AssemblyAI
 */

import { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  useVoiceAssistant,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
} from '@livekit/components-react';
import '@livekit/components-styles';

export function LiveKitTranscription({ onTranscription }) {
  const [token, setToken] = useState('');
  const [connecting, setConnecting] = useState(false);

  // Get LiveKit token from backend
  const connect = async () => {
    setConnecting(true);
    try {
      const response = await fetch('http://localhost:8000/livekit/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: 'transcription-room',
          participant_name: `user-${Date.now()}`
        })
      });

      const data = await response.json();
      setToken(data.token);
    } catch (error) {
      console.error('Failed to get LiveKit token:', error);
      setConnecting(false);
    }
  };

  if (!token) {
    return (
      <div>
        <button
          onClick={connect}
          disabled={connecting}
          className="control-button start-button"
        >
          {connecting ? 'Connecting...' : 'Start Recording'}
        </button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={import.meta.env.VITE_LIVEKIT_URL || 'ws://localhost:7880'}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={() => setToken('')}
    >
      <TranscriptionHandler onTranscription={onTranscription} />
      <RoomAudioRenderer />
      <VoiceAssistantControlBar />
    </LiveKitRoom>
  );
}

function TranscriptionHandler({ onTranscription }) {
  const { state } = useVoiceAssistant();

  useEffect(() => {
    // Handle transcription from AssemblyAI via LiveKit
    if (state === 'listening' && onTranscription) {
      // LiveKit will provide transcriptions through the voice assistant state
      // This is a simplified version - actual transcription handling
      // will come through LiveKit's transcription events
      console.log('Voice assistant state:', state);
    }
  }, [state, onTranscription]);

  return null;
}

export default LiveKitTranscription;
