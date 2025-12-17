/**
 * ControlPanel Component - Start/stop recording controls.
 */

export function ControlPanel({ onStart, onStop, isRecording, error }) {
  return (
    <div className="control-panel">
      <button
        onClick={isRecording ? onStop : onStart}
        className={`record-button ${isRecording ? 'recording' : ''}`}
        disabled={!!error}
      >
        {isRecording ? (
          <>
            <span className="record-indicator">●</span> Stop Recording
          </>
        ) : (
          <>
            <span className="record-indicator">○</span> Start Recording
          </>
        )}
      </button>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
}

export default ControlPanel;
