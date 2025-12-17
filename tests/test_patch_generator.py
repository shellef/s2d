"""
Tests for JSON Patch Generator - RFC 6902 support.
"""

import pytest
from core.patch_generator import (
    validate_patch,
    apply_patch,
    parse_llm_response,
    create_add_operation,
    create_replace_operation,
    create_remove_operation,
    normalize_patch,
)


class TestValidatePatch:
    """Test cases for validate_patch function."""

    def test_valid_add_operation(self):
        """Test validating a valid add operation."""
        document = {"actors": ["Sales"]}
        patch = [{"op": "add", "path": "/actors/-", "value": "Customer"}]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is True
        assert error == ""

    def test_valid_replace_operation(self):
        """Test validating a valid replace operation."""
        document = {"process_name": "Old Name"}
        patch = [{"op": "replace", "path": "/process_name", "value": "New Name"}]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is True
        assert error == ""

    def test_valid_remove_operation(self):
        """Test validating a valid remove operation."""
        document = {"actors": ["Sales", "Customer", "Support"]}
        patch = [{"op": "remove", "path": "/actors/1"}]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is True
        assert error == ""

    def test_invalid_patch_not_list(self):
        """Test that non-list patch is invalid."""
        document = {"process_name": "Test"}
        patch = {"op": "add", "path": "/actors/-", "value": "Test"}

        is_valid, error = validate_patch(patch, document)
        assert is_valid is False
        assert "must be a list" in error

    def test_invalid_document_not_dict(self):
        """Test that non-dict document is invalid."""
        document = "not a dict"
        patch = [{"op": "add", "path": "/test", "value": "test"}]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is False
        assert "must be a dictionary" in error

    def test_invalid_path(self):
        """Test that invalid path causes validation failure."""
        document = {"process_name": "Test"}
        patch = [{"op": "replace", "path": "/nonexistent", "value": "Test"}]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is False
        assert "Invalid patch" in error

    def test_multiple_operations(self):
        """Test validating multiple operations at once."""
        document = {
            "process_name": "Test",
            "actors": ["Sales"],
            "systems": []
        }
        patch = [
            {"op": "replace", "path": "/process_name", "value": "New Test"},
            {"op": "add", "path": "/actors/-", "value": "Customer"},
            {"op": "add", "path": "/systems/-", "value": "Salesforce"}
        ]

        is_valid, error = validate_patch(patch, document)
        assert is_valid is True
        assert error == ""


class TestApplyPatch:
    """Test cases for apply_patch function."""

    def test_apply_add_to_array(self):
        """Test applying add operation to array."""
        document = {"actors": ["Sales"]}
        patch = [{"op": "add", "path": "/actors/-", "value": "Customer"}]

        result = apply_patch(patch, document)
        assert result["actors"] == ["Sales", "Customer"]

    def test_apply_replace_string(self):
        """Test applying replace operation on string field."""
        document = {"process_name": "Old Name"}
        patch = [{"op": "replace", "path": "/process_name", "value": "New Name"}]

        result = apply_patch(patch, document)
        assert result["process_name"] == "New Name"

    def test_apply_remove_from_array(self):
        """Test applying remove operation from array."""
        document = {"actors": ["Sales", "Customer", "Support"]}
        patch = [{"op": "remove", "path": "/actors/1"}]

        result = apply_patch(patch, document)
        assert result["actors"] == ["Sales", "Support"]

    def test_apply_nested_path(self):
        """Test applying patch to nested object."""
        document = {
            "scope": {
                "start_trigger": "Old trigger",
                "end_condition": "Old condition"
            }
        }
        patch = [{"op": "replace", "path": "/scope/start_trigger", "value": "New trigger"}]

        result = apply_patch(patch, document)
        assert result["scope"]["start_trigger"] == "New trigger"
        assert result["scope"]["end_condition"] == "Old condition"

    def test_apply_multiple_patches(self):
        """Test applying multiple patches at once."""
        document = {
            "process_name": "Test",
            "actors": ["Sales"],
            "systems": ["Email"]
        }
        patch = [
            {"op": "replace", "path": "/process_name", "value": "Updated Test"},
            {"op": "add", "path": "/actors/-", "value": "Customer"},
            {"op": "add", "path": "/systems/-", "value": "Salesforce"}
        ]

        result = apply_patch(patch, document)
        assert result["process_name"] == "Updated Test"
        assert result["actors"] == ["Sales", "Customer"]
        assert result["systems"] == ["Email", "Salesforce"]

    def test_apply_patch_doesnt_modify_original(self):
        """Test that applying patch doesn't modify original document."""
        document = {"process_name": "Original"}
        patch = [{"op": "replace", "path": "/process_name", "value": "Modified"}]

        result = apply_patch(patch, document)

        # Original should be unchanged
        assert document["process_name"] == "Original"
        # Result should be modified
        assert result["process_name"] == "Modified"

    def test_apply_patch_invalid_raises_error(self):
        """Test that invalid patch raises exception."""
        document = {"process_name": "Test"}
        patch = [{"op": "replace", "path": "/nonexistent", "value": "Test"}]

        with pytest.raises(Exception):
            apply_patch(patch, document)


class TestParseLLMResponse:
    """Test cases for parse_llm_response function."""

    def test_parse_plain_json_array(self):
        """Test parsing plain JSON array."""
        response = '[{"op": "add", "path": "/actors/-", "value": "Customer"}]'

        result = parse_llm_response(response)
        assert len(result) == 1
        assert result[0]["op"] == "add"
        assert result[0]["path"] == "/actors/-"
        assert result[0]["value"] == "Customer"

    def test_parse_json_in_markdown_code_block(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response = '''Here are the updates:
```json
[
  {"op": "replace", "path": "/process_name", "value": "New Name"},
  {"op": "add", "path": "/actors/-", "value": "Sales"}
]
```
'''

        result = parse_llm_response(response)
        assert len(result) == 2
        assert result[0]["op"] == "replace"
        assert result[1]["op"] == "add"

    def test_parse_json_in_code_block_without_language(self):
        """Test parsing JSON in code block without language specified."""
        response = '''```
[{"op": "add", "path": "/systems/-", "value": "Salesforce"}]
```'''

        result = parse_llm_response(response)
        assert len(result) == 1
        assert result[0]["value"] == "Salesforce"

    def test_parse_json_with_surrounding_text(self):
        """Test parsing JSON with text before and after."""
        response = '''Based on the transcription, here are the patch operations:
[{"op": "add", "path": "/actors/-", "value": "Customer"}]
Hope this helps!'''

        result = parse_llm_response(response)
        assert len(result) == 1
        assert result[0]["value"] == "Customer"

    def test_parse_empty_response(self):
        """Test parsing empty response returns empty list."""
        assert parse_llm_response("") == []
        assert parse_llm_response("   ") == []

    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        response = "This is not JSON at all"

        with pytest.raises(ValueError):
            parse_llm_response(response)

    def test_parse_non_array_json_raises_error(self):
        """Test that JSON object (not array) raises ValueError."""
        response = '{"op": "add", "path": "/test", "value": "test"}'

        with pytest.raises(ValueError) as excinfo:
            parse_llm_response(response)
        assert "not an array" in str(excinfo.value)

    def test_parse_operation_missing_op_field(self):
        """Test that operation missing 'op' field raises ValueError."""
        response = '[{"path": "/test", "value": "test"}]'

        with pytest.raises(ValueError) as excinfo:
            parse_llm_response(response)
        assert "missing 'op' field" in str(excinfo.value)

    def test_parse_operation_missing_path_field(self):
        """Test that operation missing 'path' field raises ValueError."""
        response = '[{"op": "add", "value": "test"}]'

        with pytest.raises(ValueError) as excinfo:
            parse_llm_response(response)
        assert "missing 'path' field" in str(excinfo.value)

    def test_parse_add_operation_missing_value(self):
        """Test that add operation missing 'value' raises ValueError."""
        response = '[{"op": "add", "path": "/test"}]'

        with pytest.raises(ValueError) as excinfo:
            parse_llm_response(response)
        assert "missing 'value' field" in str(excinfo.value)

    def test_parse_remove_operation_without_value_is_valid(self):
        """Test that remove operation without value is valid."""
        response = '[{"op": "remove", "path": "/actors/0"}]'

        result = parse_llm_response(response)
        assert len(result) == 1
        assert result[0]["op"] == "remove"


class TestCreateOperations:
    """Test cases for create_*_operation helper functions."""

    def test_create_add_operation(self):
        """Test creating an add operation."""
        op = create_add_operation("/actors/-", "Customer")

        assert op["op"] == "add"
        assert op["path"] == "/actors/-"
        assert op["value"] == "Customer"

    def test_create_replace_operation(self):
        """Test creating a replace operation."""
        op = create_replace_operation("/process_name", "New Name")

        assert op["op"] == "replace"
        assert op["path"] == "/process_name"
        assert op["value"] == "New Name"

    def test_create_remove_operation(self):
        """Test creating a remove operation."""
        op = create_remove_operation("/actors/2")

        assert op["op"] == "remove"
        assert op["path"] == "/actors/2"
        assert "value" not in op


class TestNormalizePatch:
    """Test cases for normalize_patch function."""

    def test_normalize_single_operation(self):
        """Test that single operation is unchanged."""
        patch = [{"op": "add", "path": "/actors/-", "value": "Customer"}]

        result = normalize_patch(patch)
        assert result == patch

    def test_normalize_multiple_replaces_same_path(self):
        """Test that multiple replaces on same path keep only the last."""
        patch = [
            {"op": "replace", "path": "/process_name", "value": "First"},
            {"op": "replace", "path": "/process_name", "value": "Second"},
            {"op": "replace", "path": "/process_name", "value": "Third"}
        ]

        result = normalize_patch(patch)
        assert len(result) == 1
        assert result[0]["value"] == "Third"

    def test_normalize_different_paths(self):
        """Test that operations on different paths are all kept."""
        patch = [
            {"op": "replace", "path": "/process_name", "value": "Name"},
            {"op": "replace", "path": "/process_goal", "value": "Goal"},
            {"op": "add", "path": "/actors/-", "value": "Sales"}
        ]

        result = normalize_patch(patch)
        assert len(result) == 3

    def test_normalize_add_operations_all_kept(self):
        """Test that all add operations are kept (even same path)."""
        patch = [
            {"op": "add", "path": "/actors/-", "value": "Sales"},
            {"op": "add", "path": "/actors/-", "value": "Customer"},
            {"op": "add", "path": "/actors/-", "value": "Support"}
        ]

        result = normalize_patch(patch)
        assert len(result) == 3

    def test_normalize_mixed_operations(self):
        """Test normalizing mixed operation types."""
        patch = [
            {"op": "replace", "path": "/process_name", "value": "First"},
            {"op": "add", "path": "/actors/-", "value": "Sales"},
            {"op": "replace", "path": "/process_name", "value": "Second"},
            {"op": "remove", "path": "/old_field"}
        ]

        result = normalize_patch(patch)

        # Should have 3 operations: 1 replace (last one), 1 add, 1 remove
        assert len(result) == 3

        # Find the replace operation
        replace_ops = [op for op in result if op["op"] == "replace" and op["path"] == "/process_name"]
        assert len(replace_ops) == 1
        assert replace_ops[0]["value"] == "Second"
