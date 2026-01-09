"""
Markdown-to-PDF Deterministic Utilities

This module provides deterministic functions for document parsing, validation,
and element detection. All outputs are reproducible - same input always produces
same output.

Modules:
    preflight: Document validation with PreflightResult dataclass
    structure_tree: Deterministic ASCII tree generation
    element_detector: Pattern matching for tables, findings, callouts
    validation: ValidationResult and error handling types
"""

from preflight import preflight_check, PreflightResult
from structure_tree import format_structure_tree, DocumentTree, Section
from element_detector import (
    STATUS_SYMBOLS,
    GRADE_VALUES,
    FINDING_PATTERN,
    CALLOUT_PREFIXES,
    METHOD_LANGUAGES,
    detect_element_type,
    count_elements,
    ElementCounts,
)
from validation import ValidationResult, ValidationError, format_validation_report

__all__ = [
    # Preflight
    "preflight_check",
    "PreflightResult",
    # Structure tree
    "format_structure_tree",
    "DocumentTree",
    "Section",
    # Element detection
    "STATUS_SYMBOLS",
    "GRADE_VALUES",
    "FINDING_PATTERN",
    "CALLOUT_PREFIXES",
    "METHOD_LANGUAGES",
    "detect_element_type",
    "count_elements",
    "ElementCounts",
    # Validation
    "ValidationResult",
    "ValidationError",
    "format_validation_report",
]
