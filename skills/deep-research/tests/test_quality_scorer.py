#!/usr/bin/env python3
"""
Tests for quality_scorer.py

Comprehensive test suite for quality assessment scoring with RoB2, NOS,
QUADAS-2, CASP, and AMSTAR2 tools.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from quality_scorer import (  # noqa: E402
    QualityAssessment,
    QualityAssessmentSet,
    TOOL_DOMAINS,
    DOMAIN_DESCRIPTIONS,
    select_quality_tool,
    get_tool_domains,
    get_domain_description,
    create_assessment_from_dict,
    create_blank_assessment,
    load_assessments_from_json,
    save_assessments_to_json,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestToolDefinitions:
    """Tests for tool domain definitions."""

    def test_all_tools_have_domains(self):
        """Test that all tools have defined domains."""
        expected_tools = [
            "RoB2",
            "NOS_cohort",
            "NOS_case_control",
            "QUADAS2",
            "CASP",
            "AMSTAR2",
            "JBI_cross_sectional",
        ]
        for tool in expected_tools:
            assert tool in TOOL_DOMAINS
            assert len(TOOL_DOMAINS[tool]) > 0

    def test_rob2_has_five_domains(self):
        """Test RoB2 has correct number of domains."""
        assert len(TOOL_DOMAINS["RoB2"]) == 5
        assert "randomization" in TOOL_DOMAINS["RoB2"]
        assert "selection" in TOOL_DOMAINS["RoB2"]

    def test_nos_cohort_has_three_domains(self):
        """Test NOS cohort has correct domains."""
        assert len(TOOL_DOMAINS["NOS_cohort"]) == 3
        assert "selection" in TOOL_DOMAINS["NOS_cohort"]
        assert "comparability" in TOOL_DOMAINS["NOS_cohort"]
        assert "outcome" in TOOL_DOMAINS["NOS_cohort"]

    def test_casp_has_nine_domains(self):
        """Test CASP has correct number of domains."""
        assert len(TOOL_DOMAINS["CASP"]) == 9

    def test_domain_descriptions_exist(self):
        """Test that domain descriptions exist for main tools."""
        for tool in ["RoB2", "NOS_cohort", "QUADAS2", "CASP", "AMSTAR2"]:
            assert tool in DOMAIN_DESCRIPTIONS
            for domain in TOOL_DOMAINS[tool]:
                assert domain in DOMAIN_DESCRIPTIONS[tool]


# =============================================================================
# QualityAssessment Tests
# =============================================================================


class TestQualityAssessment:
    """Tests for QualityAssessment dataclass."""

    @pytest.fixture
    def valid_rob2_assessment(self):
        """Fixture for a valid RoB2 assessment."""
        return QualityAssessment(
            tool="RoB2",
            study_id="Smith2023",
            domain_ratings={
                "randomization": "Low",
                "deviations": "Low",
                "missing_data": "Low",
                "measurement": "Some concerns",
                "selection": "Low",
            },
            support={
                "randomization": "Computer-generated sequence",
                "deviations": "ITT analysis performed",
                "missing_data": "Less than 5% missing",
                "measurement": "Some unblinding possible",
                "selection": "Pre-specified outcomes",
            },
            assessor="JDoe",
        )

    def test_valid_assessment_passes_validation(self, valid_rob2_assessment):
        """Test valid assessment has no errors."""
        errors = valid_rob2_assessment.validate()
        assert len(errors) == 0
        assert valid_rob2_assessment.is_valid()

    def test_assessment_missing_domain_rating(self):
        """Test validation fails when domain rating missing."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={
                "randomization": "Low",
                "deviations": "Low",
                # missing_data is missing
                "measurement": "Low",
                "selection": "Low",
            },
            support={
                "randomization": "test",
                "deviations": "test",
                "missing_data": "test",
                "measurement": "test",
                "selection": "test",
            },
        )
        errors = assessment.validate()
        assert any("Missing rating for domain: missing_data" in e for e in errors)

    def test_assessment_missing_rationale(self):
        """Test validation fails when rationale missing."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={
                "randomization": "Low",
                "deviations": "Low",
                "missing_data": "Low",
                "measurement": "Low",
                "selection": "Low",
            },
            support={
                "randomization": "test",
                "deviations": "test",
                # missing_data support is missing
                "measurement": "test",
                "selection": "test",
            },
        )
        errors = assessment.validate()
        assert any("Missing rationale for domain: missing_data" in e for e in errors)

    def test_assessment_empty_rationale(self):
        """Test validation fails with empty rationale."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "valid rationale" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.support["randomization"] = "   "  # Empty whitespace
        errors = assessment.validate()
        assert any("Missing rationale" in e for e in errors)

    def test_assessment_invalid_rating(self):
        """Test validation fails with invalid rating value."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={
                "randomization": "Invalid",  # Not a valid rating
                "deviations": "Low",
                "missing_data": "Low",
                "measurement": "Low",
                "selection": "Low",
            },
            support={d: "test rationale" for d in TOOL_DOMAINS["RoB2"]},
        )
        errors = assessment.validate()
        assert any("Invalid rating" in e for e in errors)

    def test_assessment_unknown_tool(self):
        """Test validation fails with unknown tool."""
        assessment = QualityAssessment(
            tool="UnknownTool",
            study_id="Test2023",
            domain_ratings={"domain1": "Low"},
            support={"domain1": "test"},
        )
        errors = assessment.validate()
        assert any("Unknown assessment tool" in e for e in errors)

    def test_assessment_missing_study_id(self):
        """Test validation fails with missing study ID."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test rationale" for d in TOOL_DOMAINS["RoB2"]},
        )
        errors = assessment.validate()
        assert any("Study ID is required" in e for e in errors)

    def test_assessment_extra_domain_warning(self):
        """Test validation warns about unexpected domains."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test rationale" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.domain_ratings["extra_domain"] = "Low"
        errors = assessment.validate()
        assert any("Unexpected domain" in e for e in errors)


# =============================================================================
# Overall Rating Calculation Tests
# =============================================================================


class TestOverallRatingCalculation:
    """Tests for overall rating calculation."""

    def test_all_low_risk_gives_high_quality(self):
        """Test all low risk domains results in high quality."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        assert assessment.calculate_overall() == "High"

    def test_one_high_risk_gives_moderate(self):
        """Test one high risk domain results in moderate quality."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.domain_ratings["randomization"] = "High"
        assert assessment.calculate_overall() == "Moderate"

    def test_two_high_risk_gives_low(self):
        """Test two high risk domains results in low quality."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.domain_ratings["randomization"] = "High"
        assessment.domain_ratings["deviations"] = "High"
        assert assessment.calculate_overall() == "Low"

    def test_three_high_risk_gives_very_low(self):
        """Test three+ high risk domains results in very low quality."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.domain_ratings["randomization"] = "High"
        assessment.domain_ratings["deviations"] = "High"
        assessment.domain_ratings["missing_data"] = "High"
        assert assessment.calculate_overall() == "Very Low"

    def test_three_some_concerns_gives_moderate(self):
        """Test three some concerns domains results in moderate quality."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        assessment.domain_ratings["randomization"] = "Some concerns"
        assessment.domain_ratings["deviations"] = "Some concerns"
        assessment.domain_ratings["missing_data"] = "Some concerns"
        assert assessment.calculate_overall() == "Moderate"


# =============================================================================
# Summary and Conversion Tests
# =============================================================================


class TestAssessmentSummary:
    """Tests for assessment summary generation."""

    def test_get_summary_includes_all_fields(self):
        """Test summary includes all expected fields."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={
                "randomization": "Low",
                "deviations": "Some concerns",
                "missing_data": "High",
                "measurement": "Low",
                "selection": "Low",
            },
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        summary = assessment.get_summary()
        assert summary["study_id"] == "Test2023"
        assert summary["tool"] == "RoB2"
        assert summary["overall_rating"] == "Moderate"
        assert summary["high_risk_count"] == 1
        assert summary["some_concerns_count"] == 1
        assert summary["low_risk_count"] == 3
        assert summary["total_domains"] == 5

    def test_to_dict_includes_overall_rating(self):
        """Test to_dict includes calculated overall rating."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Test2023",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        d = assessment.to_dict()
        assert "overall_rating" in d
        assert d["overall_rating"] == "High"


# =============================================================================
# QualityAssessmentSet Tests
# =============================================================================


class TestQualityAssessmentSet:
    """Tests for QualityAssessmentSet collection."""

    @pytest.fixture
    def assessment_set(self):
        """Fixture for assessment set with multiple studies."""
        set_ = QualityAssessmentSet(review_title="Test Review")
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="Study1",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="Study2",
                domain_ratings={d: "High" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )
        return set_

    def test_add_assessment(self, assessment_set):
        """Test adding assessments to set."""
        assert len(assessment_set.assessments) == 2

    def test_validate_detects_duplicate_study_ids(self):
        """Test validation detects duplicate study IDs."""
        set_ = QualityAssessmentSet()
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="DuplicateID",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="DuplicateID",  # Same ID
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )
        errors = set_.validate()
        assert any("Duplicate study IDs" in e for e in errors)

    def test_validate_empty_set(self):
        """Test validation fails for empty set."""
        set_ = QualityAssessmentSet()
        errors = set_.validate()
        assert any("No assessments" in e for e in errors)

    def test_get_summary_counts_quality_levels(self, assessment_set):
        """Test summary correctly counts quality levels."""
        summary = assessment_set.get_summary()
        assert summary["total_studies"] == 2
        assert summary["high_quality"] == 1
        assert summary["very_low_quality"] == 1

    def test_get_summary_identifies_tools_used(self, assessment_set):
        """Test summary identifies tools used."""
        summary = assessment_set.get_summary()
        assert "RoB2" in summary["tools_used"]


# =============================================================================
# Tool Selection Tests
# =============================================================================


class TestToolSelection:
    """Tests for select_quality_tool function."""

    def test_select_rob2_for_rct(self):
        """Test RoB2 selected for RCT designs."""
        assert select_quality_tool("rct") == "RoB2"
        assert select_quality_tool("randomized controlled trial") == "RoB2"
        assert select_quality_tool("Randomised Controlled Trial") == "RoB2"

    def test_select_nos_for_cohort(self):
        """Test NOS cohort selected for cohort designs."""
        assert select_quality_tool("cohort") == "NOS_cohort"
        assert select_quality_tool("prospective cohort") == "NOS_cohort"
        assert select_quality_tool("retrospective cohort") == "NOS_cohort"

    def test_select_nos_for_case_control(self):
        """Test NOS case-control selected for case-control designs."""
        assert select_quality_tool("case-control") == "NOS_case_control"
        assert select_quality_tool("case control") == "NOS_case_control"

    def test_select_jbi_for_cross_sectional(self):
        """Test JBI selected for cross-sectional designs."""
        assert select_quality_tool("cross-sectional") == "JBI_cross_sectional"
        assert select_quality_tool("cross sectional") == "JBI_cross_sectional"

    def test_select_quadas2_for_diagnostic(self):
        """Test QUADAS-2 selected for diagnostic designs."""
        assert select_quality_tool("diagnostic") == "QUADAS2"
        assert select_quality_tool("diagnostic accuracy") == "QUADAS2"

    def test_select_casp_for_qualitative(self):
        """Test CASP selected for qualitative designs."""
        assert select_quality_tool("qualitative") == "CASP"

    def test_select_amstar2_for_systematic_review(self):
        """Test AMSTAR2 selected for systematic reviews."""
        assert select_quality_tool("systematic review") == "AMSTAR2"
        assert select_quality_tool("meta-analysis") == "AMSTAR2"
        assert select_quality_tool("meta analysis") == "AMSTAR2"

    def test_default_to_nos_cohort(self):
        """Test defaults to NOS cohort for unknown designs."""
        assert select_quality_tool("unknown design") == "NOS_cohort"
        assert select_quality_tool("observational") == "NOS_cohort"


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_tool_domains(self):
        """Test get_tool_domains returns correct domains."""
        domains = get_tool_domains("RoB2")
        assert len(domains) == 5
        assert "randomization" in domains

    def test_get_tool_domains_unknown_tool(self):
        """Test get_tool_domains returns empty for unknown tool."""
        domains = get_tool_domains("UnknownTool")
        assert domains == []

    def test_get_domain_description(self):
        """Test get_domain_description returns description."""
        desc = get_domain_description("RoB2", "randomization")
        assert "randomization" in desc.lower()

    def test_get_domain_description_unknown(self):
        """Test get_domain_description returns empty for unknown."""
        desc = get_domain_description("RoB2", "unknown_domain")
        assert desc == ""


# =============================================================================
# Factory and Serialization Tests
# =============================================================================


class TestCreateAssessmentFromDict:
    """Tests for create_assessment_from_dict function."""

    def test_create_from_dict(self):
        """Test creating assessment from dictionary."""
        data = {
            "tool": "RoB2",
            "study_id": "Test2023",
            "domain_ratings": {"randomization": "Low"},
            "support": {"randomization": "Test rationale"},
            "assessor": "Reviewer1",
            "notes": "Some notes",
        }
        assessment = create_assessment_from_dict(data)
        assert assessment.tool == "RoB2"
        assert assessment.study_id == "Test2023"
        assert assessment.assessor == "Reviewer1"

    def test_create_from_dict_missing_optional_fields(self):
        """Test creating from dict with missing optional fields."""
        data = {
            "tool": "RoB2",
            "study_id": "Test2023",
            "domain_ratings": {"randomization": "Low"},
            "support": {"randomization": "Test"},
        }
        assessment = create_assessment_from_dict(data)
        assert assessment.assessor == ""
        assert assessment.notes == ""


class TestCreateBlankAssessment:
    """Tests for create_blank_assessment function."""

    def test_create_blank_rob2(self):
        """Test creating blank RoB2 assessment."""
        assessment = create_blank_assessment("RoB2", "NewStudy")
        assert assessment.tool == "RoB2"
        assert assessment.study_id == "NewStudy"
        assert len(assessment.domain_ratings) == 5
        assert all(r == "Low" for r in assessment.domain_ratings.values())
        assert all(s == "" for s in assessment.support.values())

    def test_create_blank_casp(self):
        """Test creating blank CASP assessment."""
        assessment = create_blank_assessment("CASP", "QualStudy")
        assert assessment.tool == "CASP"
        assert len(assessment.domain_ratings) == 9


class TestJSONSerialization:
    """Tests for JSON save/load functions."""

    def test_save_and_load_assessment_set(self):
        """Test round-trip JSON serialization."""
        set_ = QualityAssessmentSet(review_title="Test Review")
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="Study1",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test rationale" for d in TOOL_DOMAINS["RoB2"]},
                assessor="Tester",
            )
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_assessments_to_json(set_, filepath)
            loaded = load_assessments_from_json(filepath)

            assert loaded.review_title == "Test Review"
            assert len(loaded.assessments) == 1
            assert loaded.assessments[0].study_id == "Study1"
        finally:
            Path(filepath).unlink()

    def test_json_is_valid_format(self):
        """Test saved JSON is properly formatted."""
        set_ = QualityAssessmentSet(review_title="Test")
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="Study1",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_assessments_to_json(set_, filepath)

            with open(filepath) as f:
                content = f.read()

            # Verify valid JSON
            data = json.loads(content)
            assert "review_title" in data
            assert "assessments" in data
            assert "summary" in data
        finally:
            Path(filepath).unlink()


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_assessment_with_all_high_risk(self):
        """Test assessment where all domains are high risk."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="HighRiskStudy",
            domain_ratings={d: "High" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "Critical issues identified" for d in TOOL_DOMAINS["RoB2"]},
        )
        assert assessment.is_valid()
        assert assessment.calculate_overall() == "Very Low"

    def test_assessment_with_all_some_concerns(self):
        """Test assessment where all domains have some concerns."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="ConcernsStudy",
            domain_ratings={d: "Some concerns" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "Minor issues noted" for d in TOOL_DOMAINS["RoB2"]},
        )
        assert assessment.is_valid()
        # 5 some concerns > 3, so should be Moderate
        assert assessment.calculate_overall() == "Moderate"

    def test_nos_cohort_with_three_domains(self):
        """Test NOS cohort has only three domains."""
        assessment = create_blank_assessment("NOS_cohort", "CohortStudy")
        assert len(assessment.domain_ratings) == 3
        assert "selection" in assessment.domain_ratings
        assert "comparability" in assessment.domain_ratings
        assert "outcome" in assessment.domain_ratings

    def test_whitespace_in_study_id(self):
        """Test whitespace-only study ID fails validation."""
        assessment = QualityAssessment(
            tool="RoB2",
            study_id="   ",
            domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
            support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
        )
        errors = assessment.validate()
        assert any("Study ID is required" in e for e in errors)

    def test_mixed_tools_in_set(self):
        """Test assessment set can have mixed tools."""
        set_ = QualityAssessmentSet(review_title="Mixed Review")
        set_.add_assessment(
            QualityAssessment(
                tool="RoB2",
                study_id="RCT1",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["RoB2"]},
                support={d: "test" for d in TOOL_DOMAINS["RoB2"]},
            )
        )
        set_.add_assessment(
            QualityAssessment(
                tool="NOS_cohort",
                study_id="Cohort1",
                domain_ratings={d: "Low" for d in TOOL_DOMAINS["NOS_cohort"]},
                support={d: "test" for d in TOOL_DOMAINS["NOS_cohort"]},
            )
        )
        errors = set_.validate()
        assert len(errors) == 0
        summary = set_.get_summary()
        assert "RoB2" in summary["tools_used"]
        assert "NOS_cohort" in summary["tools_used"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
