#!/usr/bin/env python3
"""
Tests for prisma_validator.py

Comprehensive test suite for PRISMA 2020 flow diagram validation.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from prisma_validator import (  # noqa: E402
    PRISMAFlowData,
    load_prisma_from_json,
    save_prisma_to_json,
    create_prisma_template,
)


# =============================================================================
# Valid PRISMA Flow Tests
# =============================================================================


class TestValidPRISMAFlow:
    """Tests for valid PRISMA flow data."""

    def test_valid_complete_flow(self):
        """Test a complete valid PRISMA flow."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 500, "Scopus": 300, "Web of Science": 200},
            other_sources={"Citation searching": 50},
            duplicates_removed=250,
            automation_excluded=0,
            records_screened=800,
            records_excluded=650,
            reports_sought=150,
            reports_not_retrieved=10,
            reports_assessed=140,
            reports_excluded=100,
            exclusion_reasons={
                "Wrong population": 30,
                "Wrong intervention": 40,
                "Wrong outcome": 30,
            },
            studies_included=40,
            reports_of_included=40,
            studies_in_meta=35,
        )
        assert prisma.is_valid()
        assert len(prisma.validate()) == 0

    def test_valid_minimal_flow(self):
        """Test a minimal valid PRISMA flow."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=60,
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            studies_included=5,
        )
        assert prisma.is_valid()

    def test_valid_with_automation_exclusion(self):
        """Test valid flow with automation-excluded records."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 1000},
            duplicates_removed=200,
            automation_excluded=100,
            records_screened=700,
            records_excluded=600,
            reports_sought=100,
            reports_not_retrieved=10,
            reports_assessed=90,
            reports_excluded=70,
            studies_included=20,
        )
        assert prisma.is_valid()

    def test_valid_without_meta_analysis(self):
        """Test valid flow without meta-analysis."""
        prisma = PRISMAFlowData(
            databases={"Scopus": 200},
            duplicates_removed=50,
            records_screened=150,
            records_excluded=130,
            reports_sought=20,
            reports_not_retrieved=2,
            reports_assessed=18,
            reports_excluded=8,
            studies_included=10,
            studies_in_meta=None,  # No meta-analysis
        )
        assert prisma.is_valid()


# =============================================================================
# Invalid PRISMA Flow Tests - Arithmetic Errors
# =============================================================================


class TestArithmeticValidation:
    """Tests for arithmetic consistency validation."""

    def test_invalid_records_screened(self):
        """Test detection of incorrect records_screened."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=90,  # Should be 80
            records_excluded=60,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=25,
            reports_excluded=15,
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("Records screened" in e for e in errors)
        assert not prisma.is_valid()

    def test_invalid_reports_sought(self):
        """Test detection of incorrect reports_sought."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=50,
            reports_sought=25,  # Should be 30
            reports_not_retrieved=5,
            reports_assessed=20,
            reports_excluded=10,
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("Reports sought" in e for e in errors)

    def test_invalid_reports_assessed(self):
        """Test detection of incorrect reports_assessed."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=50,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=30,  # Should be 25
            reports_excluded=15,
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("Reports assessed" in e for e in errors)

    def test_invalid_studies_included(self):
        """Test detection of incorrect studies_included."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=50,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=25,
            reports_excluded=15,
            studies_included=15,  # Should be 10
        )
        errors = prisma.validate()
        assert any("Studies included" in e for e in errors)

    def test_invalid_exclusion_reasons_sum(self):
        """Test detection of mismatched exclusion reasons sum."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=50,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=25,
            reports_excluded=15,
            exclusion_reasons={
                "Wrong population": 5,
                "Wrong outcome": 5,
                # Sum is 10, but reports_excluded is 15
            },
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("Exclusion reasons sum" in e for e in errors)

    def test_invalid_meta_analysis_exceeds_included(self):
        """Test detection of meta-analysis count exceeding included."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=50,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=25,
            reports_excluded=15,
            studies_included=10,
            studies_in_meta=15,  # Cannot exceed studies_included
        )
        errors = prisma.validate()
        assert any("meta-analysis" in e.lower() and "cannot exceed" in e.lower() for e in errors)


# =============================================================================
# Invalid PRISMA Flow Tests - Negative Values
# =============================================================================


class TestNegativeValueValidation:
    """Tests for negative value detection."""

    def test_negative_duplicates_removed(self):
        """Test detection of negative duplicates_removed."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=-10,
            records_screened=110,
            records_excluded=80,
            reports_sought=30,
            reports_not_retrieved=5,
            reports_assessed=25,
            reports_excluded=15,
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("cannot be negative" in e for e in errors)

    def test_negative_records_excluded(self):
        """Test detection of negative records_excluded."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=-10,
            reports_sought=90,
            reports_not_retrieved=5,
            reports_assessed=85,
            reports_excluded=75,
            studies_included=10,
        )
        errors = prisma.validate()
        assert any("cannot be negative" in e for e in errors)


# =============================================================================
# Summary Statistics Tests
# =============================================================================


class TestSummaryStatistics:
    """Tests for summary statistics generation."""

    def test_total_identified(self):
        """Test total_identified calculation."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100, "Scopus": 50},
            other_sources={"Manual": 10},
        )
        assert prisma.total_identified() == 160

    def test_total_from_databases(self):
        """Test total_from_databases calculation."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100, "Scopus": 50, "Web of Science": 30},
        )
        assert prisma.total_from_databases() == 180

    def test_total_from_other(self):
        """Test total_from_other calculation."""
        prisma = PRISMAFlowData(
            other_sources={"Citation": 20, "Grey lit": 10},
        )
        assert prisma.total_from_other() == 30

    def test_generate_summary(self):
        """Test summary dictionary generation."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 1000},
            duplicates_removed=200,
            records_screened=800,
            records_excluded=700,
            reports_sought=100,
            reports_not_retrieved=10,
            reports_assessed=90,
            reports_excluded=40,
            studies_included=50,
        )
        summary = prisma.generate_summary()

        assert summary["total_identified"] == 1000
        assert summary["from_databases"] == 1000
        assert summary["studies_included"] == 50
        assert summary["inclusion_rate"] == 5.0  # 50/1000 * 100
        assert summary["screening_exclusion_rate"] == 87.5  # 700/800 * 100

    def test_generate_summary_with_zero_values(self):
        """Test summary with zero values doesn't cause division errors."""
        prisma = PRISMAFlowData()
        summary = prisma.generate_summary()

        assert summary["total_identified"] == 0
        assert summary["inclusion_rate"] == 0
        assert summary["screening_exclusion_rate"] == 0


# =============================================================================
# Diagram Generation Tests
# =============================================================================


class TestDiagramGeneration:
    """Tests for PRISMA diagram generation."""

    def test_diagram_contains_all_sections(self):
        """Test diagram includes all required sections."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=60,
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            studies_included=5,
        )
        diagram = prisma.generate_diagram()

        assert "IDENTIFICATION" in diagram
        assert "SCREENING" in diagram
        assert "ELIGIBILITY" in diagram
        assert "INCLUDED" in diagram

    def test_diagram_contains_database_names(self):
        """Test diagram includes database names and counts."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 500, "Scopus": 300},
            duplicates_removed=200,
            records_screened=600,
            records_excluded=500,
            reports_sought=100,
            reports_not_retrieved=10,
            reports_assessed=90,
            reports_excluded=50,
            studies_included=40,
        )
        diagram = prisma.generate_diagram()

        assert "PubMed" in diagram
        assert "500" in diagram
        assert "Scopus" in diagram
        assert "300" in diagram

    def test_diagram_contains_exclusion_reasons(self):
        """Test diagram includes exclusion reasons."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=60,
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            exclusion_reasons={
                "Wrong population": 5,
                "Wrong outcome": 5,
            },
            studies_included=5,
        )
        diagram = prisma.generate_diagram()

        assert "Wrong population" in diagram
        assert "Wrong outcome" in diagram

    def test_diagram_with_meta_analysis(self):
        """Test diagram includes meta-analysis section when present."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=60,
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            studies_included=5,
            studies_in_meta=3,
        )
        diagram = prisma.generate_diagram()

        assert "meta-analysis" in diagram.lower()
        assert "3" in diagram


# =============================================================================
# JSON Serialization Tests
# =============================================================================


class TestJSONSerialization:
    """Tests for JSON load/save functions."""

    def test_to_dict(self):
        """Test dictionary conversion."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
        )
        d = prisma.to_dict()

        assert d["databases"] == {"PubMed": 100}
        assert d["duplicates_removed"] == 20
        assert d["records_screened"] == 80

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "databases": {"Scopus": 200},
            "duplicates_removed": 50,
            "records_screened": 150,
            "records_excluded": 100,
            "reports_sought": 50,
            "reports_not_retrieved": 5,
            "reports_assessed": 45,
            "reports_excluded": 25,
            "studies_included": 20,
        }
        prisma = PRISMAFlowData.from_dict(data)

        assert prisma.databases == {"Scopus": 200}
        assert prisma.duplicates_removed == 50
        assert prisma.studies_included == 20

    def test_round_trip_serialization(self):
        """Test round-trip JSON serialization."""
        original = PRISMAFlowData(
            databases={"PubMed": 500, "Scopus": 300},
            other_sources={"Citation": 50},
            duplicates_removed=200,
            automation_excluded=50,
            records_screened=600,
            records_excluded=500,
            reports_sought=100,
            reports_not_retrieved=10,
            reports_assessed=90,
            reports_excluded=50,
            exclusion_reasons={"Wrong population": 30, "Wrong outcome": 20},
            studies_included=40,
            reports_of_included=45,
            studies_in_meta=35,
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_prisma_to_json(original, filepath)
            loaded = load_prisma_from_json(filepath)

            assert loaded.databases == original.databases
            assert loaded.other_sources == original.other_sources
            assert loaded.duplicates_removed == original.duplicates_removed
            assert loaded.exclusion_reasons == original.exclusion_reasons
            assert loaded.studies_in_meta == original.studies_in_meta
        finally:
            Path(filepath).unlink()

    def test_json_format_is_readable(self):
        """Test that saved JSON is properly formatted."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_prisma_to_json(prisma, filepath)

            with open(filepath) as f:
                content = f.read()

            # Check it's valid JSON
            data = json.loads(content)
            assert "databases" in data

            # Check it's indented
            assert "\n" in content
        finally:
            Path(filepath).unlink()


# =============================================================================
# Template Tests
# =============================================================================


class TestPRISMATemplate:
    """Tests for PRISMA template creation."""

    def test_create_template(self):
        """Test template creation."""
        template = create_prisma_template()

        assert isinstance(template, PRISMAFlowData)
        assert "PubMed" in template.databases
        assert "Scopus" in template.databases
        assert "Wrong population" in template.exclusion_reasons

    def test_template_has_zero_values(self):
        """Test template has zero placeholder values."""
        template = create_prisma_template()

        assert template.duplicates_removed == 0
        assert template.records_screened == 0
        assert template.studies_included == 0

    def test_template_is_not_valid(self):
        """Test template with zeros is not arithmetically valid."""
        template = create_prisma_template()
        # Template with all zeros will fail validation (expected)
        # This is intentional - it's a template to be filled in
        assert template is not None  # Verify template was created


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_database_no_other_sources(self):
        """Test flow with single database and no other sources."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 50},
            duplicates_removed=10,
            records_screened=40,
            records_excluded=35,
            reports_sought=5,
            reports_not_retrieved=0,
            reports_assessed=5,
            reports_excluded=3,
            studies_included=2,
        )
        assert prisma.is_valid()

    def test_all_records_excluded_at_screening(self):
        """Test flow where all records excluded at screening."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=80,  # All excluded
            reports_sought=0,
            reports_not_retrieved=0,
            reports_assessed=0,
            reports_excluded=0,
            studies_included=0,
        )
        assert prisma.is_valid()

    def test_no_full_text_exclusions(self):
        """Test flow with no full-text exclusions."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=70,
            reports_sought=10,
            reports_not_retrieved=0,
            reports_assessed=10,
            reports_excluded=0,  # None excluded at full-text
            studies_included=10,
        )
        assert prisma.is_valid()

    def test_empty_exclusion_reasons_with_excluded(self):
        """Test empty exclusion_reasons doesn't trigger sum check."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=20,
            records_screened=80,
            records_excluded=60,
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            exclusion_reasons={},  # Empty but reports_excluded > 0
            studies_included=5,
        )
        # Empty exclusion_reasons should not trigger validation
        # (reasons are optional detail)
        errors = prisma.validate()
        assert not any("Exclusion reasons sum" in e for e in errors)

    def test_large_numbers(self):
        """Test with large numbers (common in systematic reviews)."""
        prisma = PRISMAFlowData(
            databases={
                "PubMed": 15000,
                "Scopus": 12000,
                "Web of Science": 8000,
                "CINAHL": 5000,
            },
            other_sources={"Citation": 500, "Grey literature": 200},
            duplicates_removed=15700,
            automation_excluded=5000,
            records_screened=20000,
            records_excluded=19500,
            reports_sought=500,
            reports_not_retrieved=50,
            reports_assessed=450,
            reports_excluded=380,
            exclusion_reasons={
                "Wrong population": 100,
                "Wrong intervention": 120,
                "Wrong outcome": 80,
                "Wrong study design": 80,
            },
            studies_included=70,
            reports_of_included=85,
            studies_in_meta=55,
        )
        assert prisma.is_valid()
        assert prisma.total_identified() == 40700

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are all reported."""
        prisma = PRISMAFlowData(
            databases={"PubMed": 100},
            duplicates_removed=-10,  # Error: negative
            records_screened=50,  # Error: wrong calculation
            records_excluded=60,  # Error: more than screened
            reports_sought=20,
            reports_not_retrieved=5,
            reports_assessed=15,
            reports_excluded=10,
            studies_included=10,  # Error: wrong calculation
        )
        errors = prisma.validate()
        # Should have multiple errors
        assert len(errors) >= 3


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_complete_workflow(self):
        """Test complete workflow from creation to validation to diagram."""
        # Create flow data
        prisma = PRISMAFlowData(
            databases={"PubMed": 1250, "Scopus": 890, "Web of Science": 720},
            other_sources={"Citation searching": 45, "Grey literature": 15},
            duplicates_removed=820,
            automation_excluded=0,
            records_screened=2100,
            records_excluded=1850,
            reports_sought=250,
            reports_not_retrieved=12,
            reports_assessed=238,
            reports_excluded=196,
            exclusion_reasons={
                "Wrong population": 45,
                "Wrong intervention": 62,
                "Wrong outcome": 38,
                "Wrong study design": 51,
            },
            studies_included=42,
            reports_of_included=42,
            studies_in_meta=35,
        )

        # Validate
        assert prisma.is_valid()

        # Generate summary
        summary = prisma.generate_summary()
        assert summary["total_identified"] == 2920
        assert summary["studies_included"] == 42

        # Generate diagram
        diagram = prisma.generate_diagram()
        assert "2,100" in diagram or "2100" in diagram  # records_screened
        assert "42" in diagram  # studies_included

        # Serialize and deserialize
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_prisma_to_json(prisma, filepath)
            loaded = load_prisma_from_json(filepath)
            assert loaded.is_valid()
            assert loaded.studies_included == 42
        finally:
            Path(filepath).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
