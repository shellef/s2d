/**
 * Simple Audio Capture - LiveKit audio streaming
 */

import { useState, useEffect } from 'react';
import { LiveKitRoom, useLocalParticipant } from '@livekit/components-react';

export function SimpleAudioCapture({ onRecordingChange, sessionId, onSessionIdChange }) {
  const [token, setToken] = useState('');
  const [livekitUrl, setLivekitUrl] = useState('');
  const [connecting, setConnecting] = useState(false);

  const handleStart = async () => {
    setConnecting(true);
    try {
      // Generate a unique session ID
      const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;

      // Get token from backend - use session ID as room name
      const response = await fetch('http://localhost:8000/livekit/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: newSessionId,
          participant_name: `user-${Date.now()}`
        })
      });

      const data = await response.json();
      setToken(data.token);
      setLivekitUrl(data.url);

      // Set the session ID - this will trigger WebSocket connection
      if (onSessionIdChange) onSessionIdChange(newSessionId);
      if (onRecordingChange) onRecordingChange(true);
    } catch (error) {
      console.error('Failed to get LiveKit token:', error);
      alert('Failed to connect. Make sure LiveKit credentials are set in .env');
      setConnecting(false);
    }
  };

  const handleStop = () => {
    setToken('');
    setLivekitUrl('');
    setConnecting(false);
    if (onSessionIdChange) onSessionIdChange(null);
    if (onRecordingChange) onRecordingChange(false);
  };

  if (!token) {
    return (
      <button
        onClick={handleStart}
        disabled={connecting}
        className="control-button start-button"
      >
        {connecting ? 'Connecting...' : 'Start Recording'}
      </button>
    );
  }

  return (
    <div>
      <LiveKitRoom
        token={token}
        serverUrl={livekitUrl}
        connect={true}
        audio={true}
        video={false}
        onDisconnected={handleStop}
      >
        <AudioPublisher />
      </LiveKitRoom>
      <button onClick={handleStop} className="control-button stop-button">
        Stop Recording
      </button>
    </div>
  );
}

function AudioPublisher() {
  const { localParticipant } = useLocalParticipant();

  // Enable microphone automatically
  useEffect(() => {
    if (localParticipant) {
      localParticipant.setMicrophoneEnabled(true);
      console.log('Microphone enabled');
    }
  }, [localParticipant]);

  return <div className="status-indicator">🎤 Recording...</div>;
}

export default SimpleAudioCapture;
