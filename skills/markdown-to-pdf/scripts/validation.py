"""
Validation Types for Markdown-to-PDF

Provides typed validation results and error handling.
All error messages use fixed templates - no LLM variation.

Usage:
    from scripts.validation import ValidationResult, ValidationError

    result = validate_document(content)
    if not result.is_valid:
        print(result.format_errors())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ============================================================================
# ERROR CODES AND MESSAGES
# ============================================================================


class ErrorCode(Enum):
    """
    Standardized error codes for validation failures.

    Each code maps to a fixed error message template.
    """

    # File errors (1xx)
    FILE_NOT_FOUND = 101
    INVALID_EXTENSION = 102
    READ_ERROR = 103

    # Frontmatter errors (2xx)
    MISSING_FRONTMATTER = 201
    INVALID_YAML = 202
    MISSING_TYPE = 203
    UNKNOWN_TYPE = 204
    MISSING_REQUIRED_FIELD = 205

    # Section errors (3xx)
    MISSING_REQUIRED_SECTION = 301

    # Content errors (4xx)
    EMPTY_DOCUMENT = 401
    INVALID_TABLE_FORMAT = 402
    MALFORMED_CODE_BLOCK = 403


# Fixed message templates for each error code
ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.FILE_NOT_FOUND: "File not found: {path}",
    ErrorCode.INVALID_EXTENSION: "Invalid extension: expected .md, got {ext}",
    ErrorCode.READ_ERROR: "Could not read file: {error}",
    ErrorCode.MISSING_FRONTMATTER: "Missing YAML frontmatter (add --- header)",
    ErrorCode.INVALID_YAML: "Invalid YAML in frontmatter: {error}",
    ErrorCode.MISSING_TYPE: "Missing required field 'type' in frontmatter",
    ErrorCode.UNKNOWN_TYPE: "Unknown document type: {type}. Valid types: {valid_types}",
    ErrorCode.MISSING_REQUIRED_FIELD: "Missing required frontmatter field: {field}",
    ErrorCode.MISSING_REQUIRED_SECTION: "Missing required section: {section}",
    ErrorCode.EMPTY_DOCUMENT: "Document contains no content after frontmatter",
    ErrorCode.INVALID_TABLE_FORMAT: "Invalid table format at line {line}",
    ErrorCode.MALFORMED_CODE_BLOCK: "Unclosed code block starting at line {line}",
}


# ============================================================================
# VALIDATION ERROR DATACLASS
# ============================================================================


@dataclass(frozen=True)
class ValidationError:
    """
    Single validation error with code and context.

    Frozen for immutability and hashability.
    """

    code: ErrorCode
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def message(self) -> str:
        """Format error message using template and context."""
        template = ERROR_MESSAGES.get(self.code, f"Unknown error: {self.code}")
        try:
            return template.format(**self.context)
        except KeyError:
            return template

    @property
    def severity(self) -> str:
        """Get error severity based on code range."""
        code_value = self.code.value
        if code_value < 200:
            return "error"  # File errors are blocking
        if code_value < 300:
            return "error"  # Frontmatter errors are blocking
        if code_value < 400:
            return "warning"  # Section errors may be warnings
        return "warning"  # Content errors are often warnings


# ============================================================================
# VALIDATION RESULT DATACLASS
# ============================================================================


@dataclass
class ValidationResult:
    """
    Complete validation result with errors and warnings.

    Provides deterministic formatting methods.
    """

    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def add_error(self, code: ErrorCode, **context: Any) -> None:
        """Add an error with context."""
        self.errors.append(ValidationError(code=code, context=context))

    def add_warning(self, code: ErrorCode, **context: Any) -> None:
        """Add a warning with context."""
        self.warnings.append(ValidationError(code=code, context=context))

    def format_errors(self) -> str:
        """
        Format errors as deterministic string.

        Returns:
            Fixed-format error list.
        """
        if not self.errors:
            return "No errors"

        lines = ["Errors:"]
        for error in self.errors:
            lines.append(f"  ❌ [{error.code.name}] {error.message}")
        return "\n".join(lines)

    def format_warnings(self) -> str:
        """Format warnings as deterministic string."""
        if not self.warnings:
            return "No warnings"

        lines = ["Warnings:"]
        for warning in self.warnings:
            lines.append(f"  ⚠️ [{warning.code.name}] {warning.message}")
        return "\n".join(lines)

    def format_report(self) -> str:
        """
        Format complete validation report.

        Returns:
            Fixed-format report string.
        """
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        lines = [f"Validation: {status}", ""]

        if self.errors:
            lines.append(self.format_errors())
            lines.append("")

        if self.warnings:
            lines.append(self.format_warnings())
            lines.append("")

        if self.metadata:
            lines.append("Metadata:")
            for key, value in sorted(self.metadata.items()):
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


# ============================================================================
# VALIDATION REPORT FORMATTING
# ============================================================================


def format_validation_report(
    result: ValidationResult,
    verbose: bool = False,
) -> str:
    """
    Format validation result as human-readable report.

    Args:
        result: ValidationResult to format.
        verbose: Include all details if True.

    Returns:
        Deterministic report string.
    """
    if verbose:
        return result.format_report()

    # Compact format
    if result.is_valid and not result.has_warnings:
        return "✅ Validation passed"

    if not result.is_valid:
        return f"❌ {len(result.errors)} error(s)\n{result.format_errors()}"

    return f"⚠️ {len(result.warnings)} warning(s)\n{result.format_warnings()}"


# ============================================================================
# SUCCESS MESSAGE TEMPLATES
# ============================================================================


def format_success_message(
    output_path: str,
    section_count: int,
    finding_count: int = 0,
    status_table_count: int = 0,
    graded_table_count: int = 0,
    method_block_count: int = 0,
    callout_count: int = 0,
    brand_name: str = "Oligon",
) -> str:
    """
    Format deterministic success message.

    Uses fixed template - no LLM variation.

    Args:
        output_path: Path to generated PDF.
        section_count: Number of sections rendered.
        finding_count: Number of FindingCards.
        status_table_count: Number of StatusTables.
        graded_table_count: Number of GradedTables.
        method_block_count: Number of MethodBlocks.
        callout_count: Number of CalloutBoxes.
        brand_name: Brand name applied.

    Returns:
        Fixed-format success message.
    """
    lines = [
        f"✅ PDF generated: {output_path}",
        "",
        "Summary:",
        f"- {section_count} sections rendered",
    ]

    if finding_count > 0:
        lines.append(f"- {finding_count} FindingCards")
    if status_table_count > 0:
        lines.append(f"- {status_table_count} StatusTables")
    if graded_table_count > 0:
        lines.append(f"- {graded_table_count} GradedTables")
    if method_block_count > 0:
        lines.append(f"- {method_block_count} MethodBlocks")
    if callout_count > 0:
        lines.append(f"- {callout_count} CalloutBoxes")

    lines.append(f"- Brand styling: {brand_name}")

    return "\n".join(lines)
