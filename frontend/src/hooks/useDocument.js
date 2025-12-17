/**
 * Document Hook - Manages document state with JSON Patch application.
 */

import { useState, useCallback } from 'react';
import { applyPatch } from 'fast-json-patch';

const EMPTY_DOCUMENT = {
  process_name: "",
  process_goal: "",
  scope: {
    start_trigger: "",
    end_condition: "",
    in_scope: [],
    out_of_scope: []
  },
  actors: [],
  systems: [],
  main_flow: [],
  exceptions: [],
  metrics: [],
  open_questions: []
};

export function useDocument() {
  const [document, setDocument] = useState(EMPTY_DOCUMENT);
  const [transcription, setTranscription] = useState("");

  const applyDocumentPatch = useCallback((patchOps) => {
    setDocument(prevDoc => {
      try {
        // Deep clone the document
        const docCopy = JSON.parse(JSON.stringify(prevDoc));

        // Apply patches
        const result = applyPatch(docCopy, patchOps, true, false);

        // Return the updated document
        return result.newDocument;
      } catch (error) {
        console.error('Failed to apply document patch:', error);
        console.error('Patch operations:', patchOps);
        // Return previous document on error (graceful degradation)
        return prevDoc;
      }
    });
  }, []);

  const updateTranscription = useCallback((text) => {
    setTranscription(prev => {
      // Add space before appending if prev already has content
      if (prev) {
        return prev + " " + text;
      }
      return text;
    });
  }, []);

  const resetDocument = useCallback(() => {
    setDocument(EMPTY_DOCUMENT);
    setTranscription("");
  }, []);

  return {
    document,
    transcription,
    applyDocumentPatch,
    updateTranscription,
    resetDocument
  };
}

export default useDocument;
