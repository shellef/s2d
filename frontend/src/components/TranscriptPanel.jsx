/**
 * TranscriptPanel Component - Collapsible debug panel for raw transcription.
 */

import { useRef, useEffect } from 'react';

export function TranscriptPanel({ transcription, isVisible, onToggle }) {
  const panelRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new transcription arrives
    if (panelRef.current && isVisible) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
  }, [transcription, isVisible]);

  return (
    <>
      {/* Toggle Button */}
      <button
        className="transcript-toggle"
        onClick={onToggle}
        title={isVisible ? "Hide Transcript" : "Show Transcript"}
      >
        🎤 {isVisible ? "Hide" : "Show"} Transcript
      </button>

      {/* Collapsible Panel */}
      <div className={`transcript-panel ${isVisible ? "visible" : "hidden"}`}>
        <div className="transcript-header">
          <h3>🎤 Live Transcription</h3>
          <button className="transcript-close" onClick={onToggle}>✕</button>
        </div>
        <div className="transcript-content" ref={panelRef}>
          <pre>{transcription || "Transcription will appear here..."}</pre>
        </div>
      </div>
    </>
  );
}

export default TranscriptPanel;
