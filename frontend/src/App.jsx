/**
 * App Component - Main application integrating all functionality.
 */

import { useEffect, useState } from 'react';
import useWebSocket from './hooks/useWebSocket';
import useDocument from './hooks/useDocument';
import DocumentView from './components/DocumentView';
import TranscriptPanel from './components/TranscriptPanel';
import StatusIndicator from './components/StatusIndicator';
import { SimpleAudioCapture } from './components/SimpleAudioCapture';
import './styles/main.css';

function App() {
  const wsUrl = 'ws://localhost:8000/ws';
  const { isConnected, lastMessage, sendMessage } = useWebSocket(wsUrl);

  const {
    document,
    transcription,
    applyDocumentPatch,
    updateTranscription
  } = useDocument();

  const [transcriptVisible, setTranscriptVisible] = useState(false);
  const [status, setStatus] = useState('idle');
  const [isRecording, setIsRecording] = useState(false);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    console.log('Received message:', lastMessage.type);

    switch (lastMessage.type) {
      case 'transcription':
        updateTranscription(lastMessage.text);
        break;

      case 'document_patch':
        // Apply JSON Patch operations
        applyDocumentPatch(lastMessage.patch);
        break;

      case 'status':
        setStatus(lastMessage.status);
        console.log('Status:', lastMessage.status, lastMessage.message);
        break;

      case 'error':
        console.error('Server error:', lastMessage.error);
        break;

      default:
        console.warn('Unknown message type:', lastMessage.type);
    }
  }, [lastMessage, updateTranscription, applyDocumentPatch]);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>Speech-to-Document</h1>
          <p className="header-subtitle">Real-time process documentation</p>
        </div>
        <div className="header-right">
          <StatusIndicator
            isConnected={isConnected}
            isRecording={isRecording}
          />
          <SimpleAudioCapture onRecordingChange={setIsRecording} />
        </div>
      </header>

      <main className="app-main">
        {/* Document View - Primary Focus */}
        <DocumentView document={document} />

        {/* Transcript Panel - Secondary, Hideable */}
        <TranscriptPanel
          transcription={transcription}
          isVisible={transcriptVisible}
          onToggle={() => setTranscriptVisible(!transcriptVisible)}
        />
      </main>

      {/* Processing indicator */}
      {status === 'processing' && (
        <div className="processing-indicator">
          <div className="spinner"></div>
          <span>Processing...</span>
        </div>
      )}
    </div>
  );
}

export default App;
