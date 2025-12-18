"""
Prompt Builder - Constructs prompts for LLM with JSON Patch format.

This module builds system and user prompts for LLM to process transcription
and generate JSON Patch operations for document updates.
"""

import json
from typing import Any, Dict, List, Optional


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
    SYSTEM_PROMPT = """Update a process document using JSON Patch (RFC 6902).

Given process_doc (JSON) and new_utterance (text), produce a JSON Patch with ONLY minimal changes.

Output format:
{
  "patch": [
    { "op": "add" | "replace" | "remove", "path": "/a/b/0", "value": ... }
  ]
}

Rules:
- Paths start with "/". Use numeric indices for arrays. Append with "-" (e.g., "/main_flow/-").
- Return minimal, valid JSON. If no update needed: { "patch": [] }.
- Never invent fields not clearly implied.
- Only extract complete, meaningful information. Ignore incomplete sentence fragments.
- Wait for complete phrases before updating fields (e.g., don't update process_name with "this process is called").

Metadata Fields (_instructions):
- Fields starting with "_" (especially "_instructions") are metadata that describe how to interpret each section.
- These fields provide guidance on what to extract and how to structure the data for each section.
- DO NOT modify "_instructions" fields via patches - they are documentation, not data.
- Use the "_instructions" fields to understand:
  * What type of information belongs in each section
  * How to structure extracted data (e.g., step objects with id, description, actor, system)
  * What examples or patterns to look for in utterances
- The instructions are co-located with the data structure they describe for easy reference."""

    return SYSTEM_PROMPT

def build_update_prompt(
    transcription_tail: str,
    current_document: Dict[str, Any],
    patch_history: Optional[List[List[Dict[str, Any]]]] = None
) -> List[Dict[str, str]]:
    """
    Build conversation messages for LLM with current document + transcription tail.

    Args:
        transcription_tail: Overlapping window of recent transcription (typically last 250 words)
        current_document: Current document state for context
        patch_history: Optional history of recent patch operations to prevent repetition

    Returns:
        List of message dictionaries with role and content
    """
    # Format current document as pretty JSON (including instruction fields)
    document_json = json.dumps(current_document, indent=2)

    # Build patch history section if provided
    patch_history_section = ""
    if patch_history:
        patch_history_json = json.dumps(patch_history, indent=2)
        patch_history_section = f"""

Recent patch history (last {len(patch_history)} operations you performed):
{patch_history_json}
"""

    # Build user message
    user_content = f"""Current document:
{document_json}

Recent transcription (last 250 words):
{transcription_tail}{patch_history_section}

Based on the transcription, generate JSON Patch operations to update the document. Extract any new information about the process name, goal, scope, actors, systems, steps, exceptions, metrics, or questions. If you detect corrections (e.g., "actually, change that to..."), use replace or remove operations. Do not repeat operations you've already performed (shown in patch history above). Return ONLY the JSON array of patch operations, no other text."""

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

    Args:
        document: Document dictionary

    Returns:
        Formatted JSON string
    """
    return json.dumps(document, indent=2)


def get_empty_document() -> Dict[str, Any]:
    """
    Get an empty document matching the PROCESS_TEMPLATE schema.

    This is useful for starting a new session.

    Returns:
        Empty document dictionary (with instruction fields for LLM guidance)
    """
    from core.templates import PROCESS_TEMPLATE
    import copy
    return copy.deepcopy(PROCESS_TEMPLATE)
