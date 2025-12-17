"""
JSON Patch Generator - RFC 6902 support for document updates.

This module provides functions to validate, apply, and parse JSON Patch operations
for precise document updates including additions, replacements, and deletions.
"""

import json
import re
from typing import Any, Dict, List, Tuple

try:
    import jsonpatch
except ImportError:
    jsonpatch = None


def validate_patch(patch: List[Dict[str, Any]], document: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate JSON Patch operations against a document.

    Args:
        patch: List of JSON Patch operations
        document: Document to validate patch against

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is empty string.

    Raises:
        ImportError: If jsonpatch library is not installed
    """
    if jsonpatch is None:
        raise ImportError(
            "jsonpatch library is required. Install with: pip install jsonpatch"
        )

    if not isinstance(patch, list):
        return False, "Patch must be a list of operations"

    if not isinstance(document, dict):
        return False, "Document must be a dictionary"

    try:
        # Test applying the patch without modifying the original
        jsonpatch.JsonPatch(patch).apply(document, in_place=False)
        return True, ""
    except jsonpatch.JsonPatchException as e:
        return False, f"Invalid patch: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def apply_patch(patch: List[Dict[str, Any]], document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply JSON Patch operations to a document.

    Args:
        patch: List of JSON Patch operations
        document: Document to apply patch to

    Returns:
        Updated document with patches applied

    Raises:
        ImportError: If jsonpatch library is not installed
        jsonpatch.JsonPatchException: If patch is invalid or cannot be applied
    """
    if jsonpatch is None:
        raise ImportError(
            "jsonpatch library is required. Install with: pip install jsonpatch"
        )

    if not isinstance(patch, list):
        raise ValueError("Patch must be a list of operations")

    if not isinstance(document, dict):
        raise ValueError("Document must be a dictionary")

    # Apply patch and return new document
    return jsonpatch.apply_patch(document, patch)


def parse_llm_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response as JSON Patch array.

    Handles various response formats:
    - Plain JSON array
    - JSON wrapped in markdown code blocks
    - JSON with surrounding text

    Args:
        response: LLM response string containing JSON Patch operations

    Returns:
        List of JSON Patch operation dictionaries

    Raises:
        ValueError: If response cannot be parsed as valid JSON Patch array
    """
    if not response or not response.strip():
        return []

    # Try to find JSON in markdown code blocks first
    code_block_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
    code_block_match = re.search(code_block_pattern, response, re.DOTALL)

    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        # Try to find JSON array in the response
        array_pattern = r'\[.*?\]'
        array_match = re.search(array_pattern, response, re.DOTALL)

        if array_match:
            json_str = array_match.group(0)
        else:
            # Try parsing the entire response as JSON
            json_str = response.strip()

    try:
        patch = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}")

    # Validate it's a list
    if not isinstance(patch, list):
        raise ValueError("Parsed JSON is not an array")

    # Validate each operation has required fields
    for i, operation in enumerate(patch):
        if not isinstance(operation, dict):
            raise ValueError(f"Operation {i} is not a dictionary")

        if 'op' not in operation:
            raise ValueError(f"Operation {i} missing 'op' field")

        if 'path' not in operation:
            raise ValueError(f"Operation {i} missing 'path' field")

        # Most operations require 'value' (except 'remove' and 'test')
        if operation['op'] not in ['remove', 'test'] and 'value' not in operation:
            raise ValueError(f"Operation {i} with op '{operation['op']}' missing 'value' field")

    return patch


def create_add_operation(path: str, value: Any) -> Dict[str, Any]:
    """
    Create a JSON Patch 'add' operation.

    Args:
        path: JSON Pointer path (e.g., "/actors/-" to append to array)
        value: Value to add

    Returns:
        JSON Patch add operation dictionary
    """
    return {"op": "add", "path": path, "value": value}


def create_replace_operation(path: str, value: Any) -> Dict[str, Any]:
    """
    Create a JSON Patch 'replace' operation.

    Args:
        path: JSON Pointer path (e.g., "/process_name")
        value: New value

    Returns:
        JSON Patch replace operation dictionary
    """
    return {"op": "replace", "path": path, "value": value}


def create_remove_operation(path: str) -> Dict[str, Any]:
    """
    Create a JSON Patch 'remove' operation.

    Args:
        path: JSON Pointer path (e.g., "/actors/2")

    Returns:
        JSON Patch remove operation dictionary
    """
    return {"op": "remove", "path": path}


def normalize_patch(patch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a patch by removing redundant operations.

    For example, if there are multiple operations on the same path,
    keep only the last one (for replace operations).

    Args:
        patch: List of JSON Patch operations

    Returns:
        Normalized patch with redundant operations removed
    """
    # Track operations by path
    path_ops = {}

    for operation in patch:
        path = operation['path']
        op_type = operation['op']

        # For replace operations on the same path, keep only the latest
        if op_type == 'replace':
            if path in path_ops and path_ops[path]['op'] == 'replace':
                # Replace with newer operation
                path_ops[path] = operation
            else:
                path_ops[path] = operation
        else:
            # For add/remove operations, store all of them with unique keys
            key = f"{path}_{op_type}_{len(path_ops)}"
            path_ops[key] = operation

    # Return normalized patch maintaining relative order
    return list(path_ops.values())
