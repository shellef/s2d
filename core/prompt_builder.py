"""
Prompt Builder - Constructs prompts for GPT-4o with JSON Patch format.

This module builds system and user prompts for GPT-4o to process transcription
and generate JSON Patch operations for document updates.
"""

import json
from typing import Any, Dict, List


def build_system_prompt() -> str:
    """
    Build system prompt with JSON Patch instructions and schema description.

    The system prompt includes:
    1. Role description (process documentation assistant)
    2. Document schema from PROCESS_TEMPLATE
    3. JSON Patch operation format (RFC 6902)
    4. Instructions for extracting information and handling corrections

    Returns:
        System prompt string
    """
    return """You are a process documentation assistant. Extract structured information from transcribed speech and generate JSON Patch operations (RFC 6902) to update the process document.

**Document Schema:**

The document follows this structure:

- **process_name** (string): Short, descriptive name for the process (e.g., "New Customer Onboarding")

- **process_goal** (string): What this process aims to achieve - the primary objective

- **scope** (object):
  - **start_trigger** (string): What event or condition initiates this process
  - **end_condition** (string): What condition marks the completion of this process
  - **in_scope** (array of strings): What is included in this process
  - **out_of_scope** (array of strings): What is explicitly excluded from this process

- **actors** (array of strings): People, roles, or personas involved (e.g., "Sales rep", "Customer Success", "Customer")

- **systems** (array of strings): Tools, platforms, or systems used (e.g., "Salesforce", "Slack", "Gmail")

- **main_flow** (array of step objects): Sequential steps in the process. Each step object has:
  - **id** (string): Step identifier (e.g., "S1", "S2", "S3")
  - **description** (string): What happens in this step
  - **actor** (string): Who performs this step
  - **system** (string): What tool/platform is used (optional)

- **exceptions** (array of exception objects): Error cases, alternative paths, or conditional logic. Each exception object has:
  - **condition** (string): When this exception occurs
  - **action** (string): What to do when this exception happens

- **metrics** (array of metric objects): KPIs, measurements, or success criteria. Each metric object has:
  - **name** (string): Name of the metric
  - **description** (string): What this metric measures

- **open_questions** (array of strings): Uncertainties, ambiguities, or questions that need clarification

**JSON Patch Operations (RFC 6902):**

You must generate valid JSON Patch operations to update the document:

- **Add to array**: `{"op": "add", "path": "/actors/-", "value": "New Actor"}`
- **Add to nested array**: `{"op": "add", "path": "/main_flow/-", "value": {"id": "S1", "description": "...", "actor": "...", "system": "..."}}`
- **Replace field**: `{"op": "replace", "path": "/process_name", "value": "New Name"}`
- **Replace nested field**: `{"op": "replace", "path": "/scope/start_trigger", "value": "New trigger"}`
- **Replace array item**: `{"op": "replace", "path": "/main_flow/0/description", "value": "Updated description"}`
- **Remove from array**: `{"op": "remove", "path": "/actors/2"}`
- **Remove field**: `{"op": "remove", "path": "/open_questions/0"}`

**Instructions:**

1. **Extract information** from the transcription tail:
   - Identify actors (people/roles) mentioned
   - Identify systems (tools/platforms) mentioned
   - Identify process steps and their sequence
   - Identify the process name and goal if mentioned
   - Identify scope (what starts it, when it ends, what's included/excluded)
   - Identify exceptions, metrics, and questions

2. **Detect corrections and replacements**:
   - Listen for phrases like "actually", "change that to", "I meant", "delete", "remove"
   - When correction is detected, use "replace" or "remove" operations
   - Example: "The process starts when... actually, change that - it starts when..." → use replace operation

3. **Generate minimal patch operations**:
   - Only include operations for NEW or CHANGED information
   - Don't regenerate patches for information already in the document
   - Use "add" for new items, "replace" for corrections, "remove" for deletions
   - For arrays, use path "/array/-" to append new items

4. **Return format**:
   - Return ONLY a valid JSON array of patch operations
   - Do NOT include explanatory text before or after the JSON
   - Each operation must have "op", "path", and usually "value" fields
   - Ensure all JSON is properly formatted

**Example Response:**

```json
[
  {"op": "replace", "path": "/process_name", "value": "Customer Onboarding"},
  {"op": "add", "path": "/actors/-", "value": "Sales Team"},
  {"op": "add", "path": "/main_flow/-", "value": {"id": "S1", "description": "Receive new lead", "actor": "Sales Team", "system": "Salesforce"}},
  {"op": "replace", "path": "/scope/start_trigger", "value": "Sales receives a lead"}
]
```
"""


def build_update_prompt(
    transcription_tail: str,
    current_document: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Build conversation messages for GPT-4o with current document + transcription tail.

    Args:
        transcription_tail: Overlapping window of recent transcription (typically last 250 words)
        current_document: Current document state for context

    Returns:
        List of message dictionaries with role and content
    """
    # Clean the document by removing instruction fields (they start with _)
    clean_document = {
        k: v for k, v in current_document.items()
        if not k.startswith('_')
    }

    # Also clean nested instruction fields in scope
    if 'scope' in clean_document and isinstance(clean_document['scope'], dict):
        clean_document['scope'] = {
            k: v for k, v in clean_document['scope'].items()
            if not k.startswith('_')
        }

    # Format current document as pretty JSON
    document_json = json.dumps(clean_document, indent=2)

    # Build user message
    user_content = f"""Current document:
{document_json}

Recent transcription (last 250 words):
{transcription_tail}

Based on the transcription, generate JSON Patch operations to update the document. Extract any new information about the process name, goal, scope, actors, systems, steps, exceptions, metrics, or questions. If you detect corrections (e.g., "actually, change that to..."), use replace or remove operations. Return ONLY the JSON array of patch operations, no other text."""

    return [
        {
            "role": "system",
            "content": build_system_prompt()
        },
        {
            "role": "user",
            "content": user_content
        }
    ]


def format_document_state(document: Dict[str, Any]) -> str:
    """
    Format document state as pretty JSON string.

    Removes instruction fields (those starting with _) before formatting.

    Args:
        document: Document dictionary

    Returns:
        Formatted JSON string
    """
    # Clean the document
    clean_document = {
        k: v for k, v in document.items()
        if not k.startswith('_')
    }

    # Clean nested instructions in scope
    if 'scope' in clean_document and isinstance(clean_document['scope'], dict):
        clean_document['scope'] = {
            k: v for k, v in clean_document['scope'].items()
            if not k.startswith('_')
        }

    return json.dumps(clean_document, indent=2)


def get_empty_document() -> Dict[str, Any]:
    """
    Get an empty document matching the PROCESS_TEMPLATE schema.

    This is useful for starting a new session.

    Returns:
        Empty document dictionary (without instruction fields)
    """
    return {
        "process_name": "",
        "process_goal": "",
        "scope": {
            "start_trigger": "",
            "end_condition": "",
            "in_scope": [],
            "out_of_scope": [],
        },
        "actors": [],
        "systems": [],
        "main_flow": [],
        "exceptions": [],
        "metrics": [],
        "open_questions": [],
    }
