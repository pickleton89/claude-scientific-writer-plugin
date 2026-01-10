"""
Comprehensive test suite for JSON schema validation of citation reports.

Tests cover:
- Schema file loading and structure
- Valid report validation
- Error detection for invalid reports
- Schema compliance for all error/warning/duplicate types
- Report building from validate_citations.py
"""

import pytest
import sys
import os
import json
import tempfile
from datetime import datetime, timezone

# Add scripts directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from validate_citations import (
    CitationValidator,
    validate_report_schema,
    SCHEMA_VERSION,
)


class TestSchemaFile:
    """Test schema file existence and structure."""

    @pytest.fixture
    def schema_path(self):
        """Path to the schema file."""
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "schemas",
            "validation_report.json",
        )

    def test_schema_file_exists(self, schema_path):
        """Test that schema file exists."""
        assert os.path.exists(schema_path)

    def test_schema_is_valid_json(self, schema_path):
        """Test that schema is valid JSON."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        assert isinstance(schema, dict)

    def test_schema_has_required_top_level_fields(self, schema_path):
        """Test that schema has required top-level fields."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        assert "$schema" in schema
        assert "title" in schema
        assert "type" in schema
        assert "properties" in schema
        assert "definitions" in schema

    def test_schema_defines_required_properties(self, schema_path):
        """Test that schema defines all required properties."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        required = schema.get("required", [])
        assert "filepath" in required
        assert "total_entries" in required
        assert "valid_entries" in required
        assert "errors" in required
        assert "warnings" in required
        assert "duplicates" in required

    def test_schema_defines_error_types(self, schema_path):
        """Test that schema defines error type enum."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        error_def = schema["definitions"]["error"]
        error_types = error_def["properties"]["type"]["enum"]
        expected_types = [
            "missing_required_field",
            "invalid_year",
            "invalid_doi",
            "invalid_author_format",
            "syntax_error",
            "unresolvable_doi",
        ]
        for expected in expected_types:
            assert expected in error_types

    def test_schema_defines_warning_types(self, schema_path):
        """Test that schema defines warning type enum."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        warning_def = schema["definitions"]["warning"]
        warning_types = warning_def["properties"]["type"]["enum"]
        expected_types = [
            "missing_recommended_field",
            "suspicious_year",
            "page_range_format",
            "invalid_doi_format",
        ]
        for expected in expected_types:
            assert expected in warning_types

    def test_schema_defines_duplicate_types(self, schema_path):
        """Test that schema defines duplicate type enum."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        dup_def = schema["definitions"]["duplicate"]
        dup_types = dup_def["properties"]["type"]["enum"]
        expected_types = ["duplicate_doi", "duplicate_key", "similar_title"]
        for expected in expected_types:
            assert expected in dup_types

    def test_schema_has_examples(self, schema_path):
        """Test that schema includes examples."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        assert "examples" in schema
        assert len(schema["examples"]) > 0


class TestValidReportValidation:
    """Test validation of valid reports."""

    @pytest.fixture
    def minimal_valid_report(self):
        """A minimal valid report."""
        return {
            "filepath": "test.bib",
            "total_entries": 0,
            "valid_entries": 0,
            "errors": [],
            "warnings": [],
            "duplicates": [],
        }

    @pytest.fixture
    def full_valid_report(self):
        """A full valid report with all optional fields."""
        return {
            "filepath": "references.bib",
            "validation_date": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0.0",
            "total_entries": 10,
            "valid_entries": 8,
            "entry_types": {
                "article": 7,
                "book": 2,
                "inproceedings": 1,
            },
            "errors": [
                {
                    "type": "missing_required_field",
                    "entry": "Smith2024test",
                    "field": "journal",
                    "severity": "high",
                    "message": "Entry Smith2024test: Missing required field \"journal\"",
                }
            ],
            "warnings": [
                {
                    "type": "missing_recommended_field",
                    "entry": "Jones2023paper",
                    "field": "doi",
                    "severity": "medium",
                    "message": "Entry Jones2023paper: Missing recommended field \"doi\"",
                }
            ],
            "duplicates": [],
            "summary": {
                "error_count": 1,
                "warning_count": 1,
                "duplicate_count": 0,
                "validation_passed": False,
                "errors_by_type": {"missing_required_field": 1},
                "warnings_by_type": {"missing_recommended_field": 1},
            },
        }

    def test_minimal_report_validates(self, minimal_valid_report):
        """Test that minimal valid report passes validation."""
        is_valid, errors = validate_report_schema(minimal_valid_report)
        assert is_valid, f"Validation failed: {errors}"

    def test_full_report_validates(self, full_valid_report):
        """Test that full valid report passes validation."""
        is_valid, errors = validate_report_schema(full_valid_report)
        assert is_valid, f"Validation failed: {errors}"

    def test_report_with_all_error_types(self):
        """Test report with all valid error types."""
        error_types = [
            "missing_required_field",
            "invalid_year",
            "invalid_doi",
            "invalid_author_format",
            "syntax_error",
            "unresolvable_doi",
        ]
        errors = [
            {
                "type": et,
                "entry": f"test_{i}",
                "severity": "high",
                "message": f"Test error {i}",
            }
            for i, et in enumerate(error_types)
        ]
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 3,
            "errors": errors,
            "warnings": [],
            "duplicates": [],
        }
        is_valid, errors_out = validate_report_schema(report)
        assert is_valid, f"Validation failed: {errors_out}"

    def test_report_with_all_warning_types(self):
        """Test report with all valid warning types."""
        warning_types = [
            ("missing_recommended_field", "medium"),
            ("suspicious_year", "medium"),
            ("page_range_format", "low"),
            ("invalid_doi_format", "medium"),
        ]
        warnings = [
            {
                "type": wt,
                "entry": f"test_{i}",
                "severity": sev,
                "message": f"Test warning {i}",
            }
            for i, (wt, sev) in enumerate(warning_types)
        ]
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 10,
            "errors": [],
            "warnings": warnings,
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert is_valid, f"Validation failed: {errors}"

    def test_report_with_all_duplicate_types(self):
        """Test report with all valid duplicate types."""
        duplicates = [
            {
                "type": "duplicate_doi",
                "entries": ["entry1", "entry2"],
                "doi": "10.1234/test",
                "severity": "high",
                "message": "Duplicate DOI found",
            },
            {
                "type": "duplicate_key",
                "entries": ["entry3", "entry3"],
                "key": "entry3",
                "count": 2,
                "severity": "high",
                "message": "Duplicate key found",
            },
            {
                "type": "similar_title",
                "entries": ["entry4", "entry5"],
                "severity": "medium",
                "message": "Similar titles found",
            },
        ]
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 10,
            "errors": [],
            "warnings": [],
            "duplicates": duplicates,
        }
        is_valid, errors = validate_report_schema(report)
        assert is_valid, f"Validation failed: {errors}"


class TestInvalidReportDetection:
    """Test detection of invalid reports."""

    def test_missing_filepath(self):
        """Test that missing filepath is detected."""
        report = {
            "total_entries": 0,
            "valid_entries": 0,
            "errors": [],
            "warnings": [],
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid

    def test_missing_total_entries(self):
        """Test that missing total_entries is detected."""
        report = {
            "filepath": "test.bib",
            "valid_entries": 0,
            "errors": [],
            "warnings": [],
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid

    def test_negative_total_entries(self):
        """Test that negative total_entries is detected."""
        report = {
            "filepath": "test.bib",
            "total_entries": -1,
            "valid_entries": 0,
            "errors": [],
            "warnings": [],
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid

    def test_invalid_error_type(self):
        """Test that invalid error type is detected."""
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 9,
            "errors": [
                {
                    "type": "invalid_type_not_in_enum",
                    "entry": "test",
                    "severity": "high",
                    "message": "Test",
                }
            ],
            "warnings": [],
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid

    def test_invalid_warning_severity(self):
        """Test that invalid warning severity is detected."""
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 10,
            "errors": [],
            "warnings": [
                {
                    "type": "missing_recommended_field",
                    "entry": "test",
                    "severity": "critical",  # Invalid
                    "message": "Test",
                }
            ],
            "duplicates": [],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid

    def test_duplicate_missing_entries_array(self):
        """Test that duplicate without entries array is detected."""
        report = {
            "filepath": "test.bib",
            "total_entries": 10,
            "valid_entries": 10,
            "errors": [],
            "warnings": [],
            "duplicates": [
                {
                    "type": "duplicate_doi",
                    "severity": "high",
                    "message": "Test",
                    # Missing 'entries' array
                }
            ],
        }
        is_valid, errors = validate_report_schema(report)
        assert not is_valid


class TestReportBuilding:
    """Test report building from CitationValidator."""

    @pytest.fixture
    def validator(self):
        return CitationValidator()

    @pytest.fixture
    def sample_bibtex(self):
        """Create a sample BibTeX file for testing."""
        content = """@article{Smith2024protein,
    author = {Smith, John and Doe, Jane},
    title = {Protein folding with {AlphaFold}},
    journal = {Nature},
    year = {2024},
    volume = {123},
    pages = {45--67},
    doi = {10.1234/nature.2024}
}

@book{Jones2023deep,
    author = {Jones, Robert},
    title = {Deep Learning Fundamentals},
    publisher = {Academic Press},
    year = {2023}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            return f.name

    def test_report_has_schema_version(self, validator, sample_bibtex):
        """Test that report includes schema_version."""
        try:
            report = validator.validate_file(sample_bibtex)
            assert "schema_version" in report
            assert report["schema_version"] == SCHEMA_VERSION
        finally:
            os.unlink(sample_bibtex)

    def test_report_has_validation_date(self, validator, sample_bibtex):
        """Test that report includes validation_date."""
        try:
            report = validator.validate_file(sample_bibtex)
            assert "validation_date" in report
            # Should be ISO format
            datetime.fromisoformat(report["validation_date"].replace("Z", "+00:00"))
        finally:
            os.unlink(sample_bibtex)

    def test_report_has_entry_types(self, validator, sample_bibtex):
        """Test that report includes entry_types breakdown."""
        try:
            report = validator.validate_file(sample_bibtex)
            assert "entry_types" in report
            assert "article" in report["entry_types"]
            assert "book" in report["entry_types"]
        finally:
            os.unlink(sample_bibtex)

    def test_report_has_summary(self, validator, sample_bibtex):
        """Test that report includes summary section."""
        try:
            report = validator.validate_file(sample_bibtex)
            assert "summary" in report
            summary = report["summary"]
            assert "error_count" in summary
            assert "warning_count" in summary
            assert "duplicate_count" in summary
            assert "validation_passed" in summary
            assert "errors_by_type" in summary
            assert "warnings_by_type" in summary
        finally:
            os.unlink(sample_bibtex)

    def test_report_validates_against_schema(self, validator, sample_bibtex):
        """Test that generated report validates against schema."""
        try:
            report = validator.validate_file(sample_bibtex)
            is_valid, errors = validate_report_schema(report)
            assert is_valid, f"Report failed schema validation: {errors}"
        finally:
            os.unlink(sample_bibtex)

    def test_empty_file_report_validates(self, validator):
        """Test that report for empty file validates against schema."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write("")
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            is_valid, errors = validate_report_schema(report)
            assert is_valid, f"Report failed schema validation: {errors}"
        finally:
            os.unlink(filepath)


class TestSummaryCalculations:
    """Test that summary calculations are correct."""

    @pytest.fixture
    def validator(self):
        return CitationValidator()

    def test_error_count_matches(self, validator):
        """Test that summary error_count matches errors array length."""
        content = """@article{test1,
    author = {Smith, John},
    title = {Test},
    year = {2024}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            assert report["summary"]["error_count"] == len(report["errors"])
        finally:
            os.unlink(filepath)

    def test_warning_count_matches(self, validator):
        """Test that summary warning_count matches warnings array length."""
        content = """@article{test1,
    author = {Smith, John},
    title = {Test},
    journal = {Nature},
    year = {2024}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            assert report["summary"]["warning_count"] == len(report["warnings"])
        finally:
            os.unlink(filepath)

    def test_validation_passed_true_when_no_errors(self, validator):
        """Test that validation_passed is True when no errors."""
        content = """@article{test1,
    author = {Smith, John},
    title = {Test Paper},
    journal = {Nature},
    year = {2024},
    volume = {123},
    pages = {1--10},
    doi = {10.1234/test}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            if len(report["errors"]) == 0:
                assert report["summary"]["validation_passed"] is True
        finally:
            os.unlink(filepath)

    def test_validation_passed_false_when_errors(self, validator):
        """Test that validation_passed is False when errors exist."""
        content = """@article{test1,
    title = {Test},
    year = {2024}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            if len(report["errors"]) > 0:
                assert report["summary"]["validation_passed"] is False
        finally:
            os.unlink(filepath)

    def test_errors_by_type_counts_correctly(self, validator):
        """Test that errors_by_type counts each type correctly."""
        content = """@article{test1,
    title = {Test One},
    year = {2024}
}

@article{test2,
    author = {Smith, John},
    title = {Test Two},
    year = {invalid}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name
        try:
            report = validator.validate_file(filepath)
            errors_by_type = report["summary"]["errors_by_type"]
            # Count manually
            manual_counts = {}
            for error in report["errors"]:
                error_type = error["type"]
                manual_counts[error_type] = manual_counts.get(error_type, 0) + 1
            assert errors_by_type == manual_counts
        finally:
            os.unlink(filepath)
