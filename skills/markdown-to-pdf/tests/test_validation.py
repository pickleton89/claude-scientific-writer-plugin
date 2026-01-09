"""
Tests for validation module.

Verifies deterministic error handling and message formatting.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validation import (  # noqa: E402
    ErrorCode,
    ERROR_MESSAGES,
    ValidationError,
    ValidationResult,
    format_validation_report,
    format_success_message,
)


# ============================================================================
# ERROR_CODE TESTS
# ============================================================================


class TestErrorCode:
    """Test error code definitions."""

    def test_file_errors_100_range(self):
        """File errors are in 100 range."""
        assert 100 <= ErrorCode.FILE_NOT_FOUND.value < 200
        assert 100 <= ErrorCode.INVALID_EXTENSION.value < 200
        assert 100 <= ErrorCode.READ_ERROR.value < 200

    def test_frontmatter_errors_200_range(self):
        """Frontmatter errors are in 200 range."""
        assert 200 <= ErrorCode.MISSING_FRONTMATTER.value < 300
        assert 200 <= ErrorCode.INVALID_YAML.value < 300
        assert 200 <= ErrorCode.MISSING_TYPE.value < 300

    def test_section_errors_300_range(self):
        """Section errors are in 300 range."""
        assert 300 <= ErrorCode.MISSING_REQUIRED_SECTION.value < 400

    def test_content_errors_400_range(self):
        """Content errors are in 400 range."""
        assert 400 <= ErrorCode.EMPTY_DOCUMENT.value < 500

    def test_all_codes_have_messages(self):
        """Every error code has a message template."""
        for code in ErrorCode:
            assert code in ERROR_MESSAGES, f"Missing message for {code}"


# ============================================================================
# VALIDATION_ERROR TESTS
# ============================================================================


class TestValidationError:
    """Test ValidationError dataclass."""

    def test_message_formatting(self):
        """Message uses template with context."""
        error = ValidationError(
            code=ErrorCode.FILE_NOT_FOUND,
            context={"path": "/test/file.md"},
        )
        assert "/test/file.md" in error.message

    def test_message_without_context(self):
        """Message works without context placeholders."""
        error = ValidationError(code=ErrorCode.MISSING_TYPE)
        assert "type" in error.message.lower()

    def test_severity_file_errors(self):
        """File errors have error severity."""
        error = ValidationError(code=ErrorCode.FILE_NOT_FOUND)
        assert error.severity == "error"

    def test_severity_frontmatter_errors(self):
        """Frontmatter errors have error severity."""
        error = ValidationError(code=ErrorCode.MISSING_FRONTMATTER)
        assert error.severity == "error"

    def test_severity_section_errors(self):
        """Section errors have warning severity."""
        error = ValidationError(code=ErrorCode.MISSING_REQUIRED_SECTION)
        assert error.severity == "warning"

    def test_frozen_dataclass(self):
        """ValidationError is immutable."""
        error = ValidationError(code=ErrorCode.FILE_NOT_FOUND)
        with pytest.raises(Exception):  # FrozenInstanceError
            error.code = ErrorCode.READ_ERROR  # type: ignore


# ============================================================================
# VALIDATION_RESULT TESTS
# ============================================================================


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_is_valid_with_no_errors(self):
        """is_valid True when no errors."""
        result = ValidationResult()
        assert result.is_valid

    def test_is_valid_with_errors(self):
        """is_valid False when errors present."""
        result = ValidationResult()
        result.add_error(ErrorCode.FILE_NOT_FOUND, path="/test.md")
        assert not result.is_valid

    def test_has_warnings(self):
        """has_warnings reflects warning presence."""
        result = ValidationResult()
        assert not result.has_warnings

        result.add_warning(ErrorCode.MISSING_REQUIRED_SECTION, section="Intro")
        assert result.has_warnings

    def test_add_error(self):
        """add_error adds ValidationError with context."""
        result = ValidationResult()
        result.add_error(ErrorCode.INVALID_EXTENSION, ext=".txt")
        assert len(result.errors) == 1
        assert ".txt" in result.errors[0].message

    def test_add_warning(self):
        """add_warning adds ValidationError as warning."""
        result = ValidationResult()
        result.add_warning(ErrorCode.EMPTY_DOCUMENT)
        assert len(result.warnings) == 1

    def test_format_errors(self):
        """format_errors produces deterministic output."""
        result = ValidationResult()
        result.add_error(ErrorCode.FILE_NOT_FOUND, path="/missing.md")
        output = result.format_errors()
        assert "FILE_NOT_FOUND" in output
        assert "/missing.md" in output

    def test_format_errors_empty(self):
        """format_errors handles no errors."""
        result = ValidationResult()
        output = result.format_errors()
        assert "No errors" in output

    def test_format_warnings(self):
        """format_warnings produces deterministic output."""
        result = ValidationResult()
        result.add_warning(ErrorCode.MISSING_REQUIRED_SECTION, section="Methods")
        output = result.format_warnings()
        assert "MISSING_REQUIRED_SECTION" in output
        assert "Methods" in output

    def test_format_report_valid(self):
        """format_report shows VALID for valid result."""
        result = ValidationResult()
        report = result.format_report()
        assert "VALID" in report

    def test_format_report_invalid(self):
        """format_report shows INVALID for invalid result."""
        result = ValidationResult()
        result.add_error(ErrorCode.MISSING_TYPE)
        report = result.format_report()
        assert "INVALID" in report

    def test_format_report_deterministic(self):
        """format_report produces same output repeatedly."""
        result = ValidationResult()
        result.add_error(ErrorCode.FILE_NOT_FOUND, path="/test.md")
        result.add_warning(ErrorCode.EMPTY_DOCUMENT)
        result.metadata["doc_type"] = "readme"

        reports = [result.format_report() for _ in range(3)]
        assert all(r == reports[0] for r in reports)


# ============================================================================
# FORMAT_VALIDATION_REPORT TESTS
# ============================================================================


class TestFormatValidationReport:
    """Test format_validation_report function."""

    def test_compact_valid(self):
        """Compact format for valid result."""
        result = ValidationResult()
        output = format_validation_report(result, verbose=False)
        assert "passed" in output.lower()

    def test_compact_errors(self):
        """Compact format shows error count."""
        result = ValidationResult()
        result.add_error(ErrorCode.FILE_NOT_FOUND, path="/x")
        result.add_error(ErrorCode.READ_ERROR, error="denied")
        output = format_validation_report(result, verbose=False)
        assert "2 error" in output

    def test_verbose_includes_all(self):
        """Verbose format includes everything."""
        result = ValidationResult()
        result.add_error(ErrorCode.MISSING_TYPE)
        result.add_warning(ErrorCode.EMPTY_DOCUMENT)
        result.metadata["test"] = "value"

        output = format_validation_report(result, verbose=True)
        assert "INVALID" in output
        assert "MISSING_TYPE" in output
        assert "EMPTY_DOCUMENT" in output
        assert "test" in output


# ============================================================================
# FORMAT_SUCCESS_MESSAGE TESTS
# ============================================================================


class TestFormatSuccessMessage:
    """Test format_success_message function."""

    def test_basic_message(self):
        """Generates basic success message."""
        msg = format_success_message(
            output_path="output/report.pdf",
            section_count=5,
        )
        assert "✅" in msg
        assert "output/report.pdf" in msg
        assert "5 sections" in msg

    def test_includes_findings(self):
        """Includes FindingCards when present."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            finding_count=2,
        )
        assert "2 FindingCards" in msg

    def test_includes_tables(self):
        """Includes table counts when present."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            status_table_count=1,
            graded_table_count=2,
        )
        assert "1 StatusTables" in msg
        assert "2 GradedTables" in msg

    def test_includes_method_blocks(self):
        """Includes MethodBlocks when present."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            method_block_count=4,
        )
        assert "4 MethodBlocks" in msg

    def test_includes_callouts(self):
        """Includes CalloutBoxes when present."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            callout_count=1,
        )
        assert "1 CalloutBoxes" in msg

    def test_includes_brand(self):
        """Includes brand name."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            brand_name="Oligon",
        )
        assert "Oligon" in msg

    def test_custom_brand(self):
        """Supports custom brand name."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            brand_name="Custom",
        )
        assert "Custom" in msg

    def test_omits_zero_counts(self):
        """Omits elements with zero counts."""
        msg = format_success_message(
            output_path="out.pdf",
            section_count=3,
            finding_count=0,
            status_table_count=0,
        )
        assert "FindingCards" not in msg
        assert "StatusTables" not in msg

    def test_deterministic(self):
        """Same inputs produce same output."""
        kwargs = {
            "output_path": "out.pdf",
            "section_count": 5,
            "finding_count": 2,
            "status_table_count": 1,
        }
        messages = [format_success_message(**kwargs) for _ in range(3)]
        assert all(m == messages[0] for m in messages)
