/**
 * DocumentView Component - Main formatted document display.
 */

import Section from './Section';

function FlowStep({ step, index }) {
  return (
    <div className="flow-step">
      <div className="flow-step-number">{index}</div>
      <div className="flow-step-content">
        <p className="flow-step-description">{step.description || 'Step description...'}</p>
        {step.actor && (
          <span className="flow-step-badge actor-badge">👤 {step.actor}</span>
        )}
        {step.system && (
          <span className="flow-step-badge system-badge">⚙️ {step.system}</span>
        )}
      </div>
    </div>
  );
}

export function DocumentView({ document }) {
  if (!document) {
    return (
      <div className="document-view">
        <p className="text-gray-500">Loading document...</p>
      </div>
    );
  }

  return (
    <div className="document-view">
      {/* Process Name - Large, prominent */}
      <div className="document-header">
        <h1 className="process-name">
          {document.process_name || "Untitled Process"}
        </h1>
      </div>

      {/* Process Goal */}
      <Section title="🎯 Process Goal" collapsible={false}>
        <p className="goal-text">
          {document.process_goal || "Describe the process goal..."}
        </p>
      </Section>

      {/* Scope */}
      <Section title="📋 Scope" collapsible={true} defaultOpen={true}>
        <div className="scope-section">
          <div className="scope-item">
            <h4>Start Trigger</h4>
            <p>{document.scope?.start_trigger || "When does it start?"}</p>
          </div>
          <div className="scope-item">
            <h4>End Condition</h4>
            <p>{document.scope?.end_condition || "When does it end?"}</p>
          </div>
          {document.scope?.in_scope && document.scope.in_scope.length > 0 && (
            <div className="scope-item">
              <h4>In Scope</h4>
              <ul>
                {document.scope.in_scope.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {document.scope?.out_of_scope && document.scope.out_of_scope.length > 0 && (
            <div className="scope-item">
              <h4>Out of Scope</h4>
              <ul>
                {document.scope.out_of_scope.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </Section>

      {/* Actors */}
      <Section title="👥 Actors" collapsible={true}>
        {document.actors && document.actors.length > 0 ? (
          <ul className="actor-list">
            {document.actors.map((actor, i) => (
              <li key={i} className="actor-item">{actor}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No actors defined yet...</p>
        )}
      </Section>

      {/* Systems */}
      <Section title="⚙️ Systems" collapsible={true}>
        {document.systems && document.systems.length > 0 ? (
          <ul className="system-list">
            {document.systems.map((system, i) => (
              <li key={i} className="system-item">{system}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No systems defined yet...</p>
        )}
      </Section>

      {/* Main Flow - Most important */}
      <Section title="🔄 Main Flow" collapsible={true} defaultOpen={true}>
        {document.main_flow && document.main_flow.length > 0 ? (
          <div className="flow-steps">
            {document.main_flow.map((step, i) => (
              <FlowStep key={step.id || i} step={step} index={i + 1} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No process steps defined yet...</p>
        )}
      </Section>

      {/* Exceptions */}
      <Section title="⚠️ Exceptions" collapsible={true}>
        {document.exceptions && document.exceptions.length > 0 ? (
          <ul className="exception-list">
            {document.exceptions.map((exc, i) => (
              <li key={i} className="exception-item">
                <strong>Condition:</strong> {exc.condition}<br />
                <strong>Action:</strong> {exc.action}
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No exceptions defined yet...</p>
        )}
      </Section>

      {/* Metrics */}
      <Section title="📊 Metrics" collapsible={true}>
        {document.metrics && document.metrics.length > 0 ? (
          <ul className="metric-list">
            {document.metrics.map((metric, i) => (
              <li key={i} className="metric-item">
                <strong>{metric.name}:</strong> {metric.description}
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No metrics defined yet...</p>
        )}
      </Section>

      {/* Open Questions */}
      <Section title="❓ Open Questions" collapsible={true}>
        {document.open_questions && document.open_questions.length > 0 ? (
          <ul className="question-list">
            {document.open_questions.map((q, i) => (
              <li key={i} className="question-item">{q}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No open questions yet...</p>
        )}
      </Section>
    </div>
  );
}

export default DocumentView;
