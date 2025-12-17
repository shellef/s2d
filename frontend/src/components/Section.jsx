/**
 * Section Component - Collapsible section with header and content.
 */

import { useState } from 'react';

export function Section({ title, children, collapsible = true, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const toggleSection = () => {
    if (collapsible) {
      setIsOpen(!isOpen);
    }
  };

  return (
    <div className="section">
      <div
        className={`section-header ${collapsible ? 'cursor-pointer' : ''}`}
        onClick={toggleSection}
      >
        <h2 className="section-title">{title}</h2>
        {collapsible && (
          <span className="section-toggle">{isOpen ? '▼' : '▶'}</span>
        )}
      </div>

      {isOpen && (
        <div className="section-content">
          {children}
        </div>
      )}
    </div>
  );
}

export default Section;
