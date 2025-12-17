/**
 * StatusIndicator Component - Shows connection and recording status.
 */

export function StatusIndicator({ isConnected, isRecording }) {
  return (
    <div className="status-indicator">
      <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
      <span className="status-text">
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>

      {isRecording && (
        <>
          <div className="status-separator">|</div>
          <div className="status-dot recording pulse"></div>
          <span className="status-text">Recording</span>
        </>
      )}
    </div>
  );
}

export default StatusIndicator;
