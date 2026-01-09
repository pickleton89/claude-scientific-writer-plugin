#!/usr/bin/env python3
"""
JSON Schema Validator for Peer Review

Validates manuscript input and review output against JSON schemas
to ensure data consistency and completeness.

Usage:
    from schemas.validate_schema import validate_manuscript, validate_review

    errors = validate_manuscript({"title": "My Paper", "manuscript_type": "original_research"})
    errors = validate_review(review_data)

Author: Claude Scientific Writer Plugin
License: MIT
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from jsonschema import Draft7Validator, ValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    Draft7Validator = None  # type: ignore
    ValidationError = None  # type: ignore

# Schema file locations
SCHEMA_DIR = Path(__file__).parent
MANUSCRIPT_SCHEMA = SCHEMA_DIR / "manuscript_input.json"
REVIEW_SCHEMA = SCHEMA_DIR / "review_output.json"


def _load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load a JSON schema from file."""
    with open(schema_path, "r") as f:
        return json.load(f)


def _format_validation_error(error: "ValidationError") -> str:
    """Format a validation error into a readable string."""
    path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
    return f"[{path}] {error.message}"


def validate_against_schema(
    data: Dict[str, Any],
    schema_path: Path,
) -> Tuple[bool, List[str]]:
    """
    Validate data against a JSON schema.

    Args:
        data: Dictionary to validate
        schema_path: Path to JSON schema file

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    if not HAS_JSONSCHEMA:
        return (True, ["jsonschema not installed - validation skipped"])

    try:
        schema = _load_schema(schema_path)
        validator = Draft7Validator(schema)

        errors = []
        for error in sorted(validator.iter_errors(data), key=lambda e: str(e.path)):
            errors.append(_format_validation_error(error))

        return (len(errors) == 0, errors)

    except FileNotFoundError:
        return (False, [f"Schema file not found: {schema_path}"])
    except json.JSONDecodeError as e:
        return (False, [f"Invalid JSON schema: {e}"])


def validate_manuscript(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate manuscript input data against schema.

    Args:
        data: Manuscript metadata dictionary

    Returns:
        Tuple of (is_valid, list_of_error_messages)

    Examples:
        >>> is_valid, errors = validate_manuscript({"title": "Paper"})
        >>> is_valid
        False
        >>> "manuscript_type" in str(errors)
        True
    """
    return validate_against_schema(data, MANUSCRIPT_SCHEMA)


def validate_review(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate review output data against schema.

    Args:
        data: Review output dictionary

    Returns:
        Tuple of (is_valid, list_of_error_messages)

    Examples:
        >>> is_valid, errors = validate_review({})
        >>> is_valid
        False
    """
    return validate_against_schema(data, REVIEW_SCHEMA)


def validate_major_comment(comment: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a single major comment against the schema subset.

    Args:
        comment: Major comment dictionary

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    required_fields = ["issue", "location", "severity", "recommendation"]
    for field in required_fields:
        if field not in comment:
            errors.append(f"Missing required field: {field}")

    if "severity" in comment and comment["severity"] not in ("critical", "major"):
        errors.append(f"Invalid severity: {comment['severity']} (must be 'critical' or 'major')")

    if "issue" in comment and len(comment["issue"]) < 20:
        errors.append(f"Issue description too short: {len(comment['issue'])} chars (minimum 20)")

    if "recommendation" in comment and len(comment["recommendation"]) < 20:
        errors.append(f"Recommendation too short: {len(comment['recommendation'])} chars (minimum 20)")

    return (len(errors) == 0, errors)


def validate_minor_comment(comment: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a single minor comment against the schema subset.

    Args:
        comment: Minor comment dictionary

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    required_fields = ["issue", "location"]
    for field in required_fields:
        if field not in comment:
            errors.append(f"Missing required field: {field}")

    return (len(errors) == 0, errors)


def generate_minimal_manuscript() -> Dict[str, Any]:
    """Generate minimal valid manuscript input."""
    return {
        "title": "Untitled Manuscript",
        "manuscript_type": "original_research",
    }


def generate_minimal_review() -> Dict[str, Any]:
    """Generate minimal valid review output."""
    return {
        "summary": {
            "synopsis": "A" * 100,  # Minimum 100 characters
            "recommendation": "major_revisions",
            "strengths": ["Well-written", "Important topic"],
            "weaknesses": ["Methodology needs improvement"],
        },
        "recommendation": "major_revisions",
        "major_comments": [],
        "minor_comments": [],
    }


if __name__ == "__main__":
    # Quick test
    print("Testing schema validation...")

    # Test manuscript validation
    valid_manuscript = generate_minimal_manuscript()
    is_valid, errors = validate_manuscript(valid_manuscript)
    print(f"Minimal manuscript valid: {is_valid}")

    invalid_manuscript = {"title": "Test"}
    is_valid, errors = validate_manuscript(invalid_manuscript)
    print(f"Invalid manuscript (missing type): {is_valid}")
    if errors:
        print(f"  Errors: {errors}")

    # Test review validation
    valid_review = generate_minimal_review()
    is_valid, errors = validate_review(valid_review)
    print(f"Minimal review valid: {is_valid}")

    invalid_review = {}
    is_valid, errors = validate_review(invalid_review)
    print(f"Empty review: {is_valid}")
    if errors:
        print(f"  Errors: {errors[:3]}...")  # Show first 3 errors
