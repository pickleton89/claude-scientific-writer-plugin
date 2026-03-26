#!/usr/bin/env python3
"""
Tests for exit_criteria.py

Comprehensive test suite for exit criteria validation across
systematic review stages.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from exit_criteria import (  # noqa: E402
    CriterionResult,
    CriterionStatus,
    StageCheckResult,
    StageData,
    STAGE_CRITERIA,
    check_stage_criteria,
    get_stage_requirements,
    get_all_stages,
    load_check_from_json,
    save_check_to_json,
    generate_exit_report,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestStageCriteria:
    """Tests for stage criteria definitions."""

    def test_all_stages_defined(self):
        """Test all expected stages are defined."""
        expected_stages = [
            "planning",
            "search",
            "screening_title",
            "screening_abstract",
            "screening_fulltext",
            "data_extraction",
            "quality_assessment",
            "synthesis",
            "reporting",
        ]
        for stage in expected_stages:
            assert stage in STAGE_CRITERIA

    def test_each_stage_has_criteria(self):
        """Test each stage has criteria defined."""
        for stage, config in STAGE_CRITERIA.items():
            assert "criteria" in config
            assert len(config["criteria"]) > 0

    def test_each_stage_has_description(self):
        """Test each stage has a description."""
        for stage, config in STAGE_CRITERIA.items():
            assert "description" in config
            assert len(config["description"]) > 0

    def test_systematic_review_thresholds(self):
        """Test systematic review has stricter thresholds."""
        # Check database requirements
        planning = STAGE_CRITERIA["planning"]["criteria"]
        db_thresholds = planning["databases_selected"]["thresholds"]
        assert db_thresholds["systematic"] >= db_thresholds["narrative"]

        # Check paper requirements
        search = STAGE_CRITERIA["search"]["criteria"]
        paper_thresholds = search["minimum_papers"]["thresholds"]
        assert paper_thresholds["systematic"] >= paper_thresholds["rapid"]


# =============================================================================
# CriterionStatus Tests
# =============================================================================


class TestCriterionStatus:
    """Tests for CriterionStatus enum."""

    def test_all_statuses_defined(self):
        """Test all status values exist."""
        assert CriterionStatus.PASSED.value == "passed"
        assert CriterionStatus.FAILED.value == "failed"
        assert CriterionStatus.WARNING.value == "warning"
        assert CriterionStatus.NOT_APPLICABLE.value == "not_applicable"
        assert CriterionStatus.PENDING.value == "pending"


# =============================================================================
# CriterionResult Tests
# =============================================================================


class TestCriterionResult:
    """Tests for CriterionResult dataclass."""

    def test_create_passed_result(self):
        """Test creating a passed result."""
        result = CriterionResult(
            criterion_id="test_criterion",
            description="Test description",
            status=CriterionStatus.PASSED,
            actual_value=5,
            threshold=3,
            message="Test passed",
        )
        assert result.status == CriterionStatus.PASSED
        assert result.actual_value == 5

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = CriterionResult(
            criterion_id="test",
            description="Test",
            status=CriterionStatus.FAILED,
            message="Failed message",
        )
        d = result.to_dict()
        assert d["criterion_id"] == "test"
        assert d["status"] == "failed"
        assert d["message"] == "Failed message"


# =============================================================================
# StageCheckResult Tests
# =============================================================================


class TestStageCheckResult:
    """Tests for StageCheckResult dataclass."""

    @pytest.fixture
    def complete_result(self):
        """Fixture for a complete stage result."""
        result = StageCheckResult(
            stage="search",
            review_type="systematic",
        )
        result.criteria_results = [
            CriterionResult(
                criterion_id="criterion1",
                description="Criterion 1",
                status=CriterionStatus.PASSED,
                is_required=True,
            ),
            CriterionResult(
                criterion_id="criterion2",
                description="Criterion 2",
                status=CriterionStatus.PASSED,
                is_required=True,
            ),
        ]
        return result

    @pytest.fixture
    def incomplete_result(self):
        """Fixture for an incomplete stage result."""
        result = StageCheckResult(
            stage="search",
            review_type="systematic",
        )
        result.criteria_results = [
            CriterionResult(
                criterion_id="criterion1",
                description="Criterion 1",
                status=CriterionStatus.PASSED,
                is_required=True,
            ),
            CriterionResult(
                criterion_id="criterion2",
                description="Criterion 2",
                status=CriterionStatus.FAILED,
                is_required=True,
            ),
        ]
        return result

    def test_is_complete_when_all_passed(self, complete_result):
        """Test is_complete returns True when all required criteria pass."""
        assert complete_result.is_complete() is True

    def test_is_complete_when_failed(self, incomplete_result):
        """Test is_complete returns False when required criteria fail."""
        assert incomplete_result.is_complete() is False

    def test_is_complete_ignores_warnings(self):
        """Test is_complete ignores recommended criteria warnings."""
        result = StageCheckResult(stage="search", review_type="systematic")
        result.criteria_results = [
            CriterionResult(
                criterion_id="required",
                description="Required",
                status=CriterionStatus.PASSED,
                is_required=True,
            ),
            CriterionResult(
                criterion_id="recommended",
                description="Recommended",
                status=CriterionStatus.WARNING,
                is_required=False,
            ),
        ]
        assert result.is_complete() is True

    def test_has_warnings(self):
        """Test has_warnings detects warnings."""
        result = StageCheckResult(stage="search", review_type="systematic")
        result.criteria_results = [
            CriterionResult(
                criterion_id="test",
                description="Test",
                status=CriterionStatus.WARNING,
            ),
        ]
        assert result.has_warnings() is True

    def test_get_failed(self, incomplete_result):
        """Test get_failed returns only failed criteria."""
        failed = incomplete_result.get_failed()
        assert len(failed) == 1
        assert failed[0].criterion_id == "criterion2"

    def test_get_summary(self, complete_result):
        """Test get_summary returns correct counts."""
        summary = complete_result.get_summary()
        assert summary["total_criteria"] == 2
        assert summary["passed"] == 2
        assert summary["failed"] == 0
        assert summary["is_complete"] is True


# =============================================================================
# StageData Tests
# =============================================================================


class TestStageData:
    """Tests for StageData dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        data = StageData(stage="planning", review_type="systematic")
        assert data.protocol_registered is False
        assert data.databases_selected == []
        assert data.kappa_score is None

    def test_custom_values(self):
        """Test custom values are set correctly."""
        data = StageData(
            stage="search",
            review_type="systematic",
            databases_selected=["PubMed", "Cochrane", "Embase"],
            total_papers_retrieved=150,
        )
        assert len(data.databases_selected) == 3
        assert data.total_papers_retrieved == 150


# =============================================================================
# check_stage_criteria Tests - Planning Stage
# =============================================================================


class TestPlanningStage:
    """Tests for planning stage criteria checks."""

    def test_protocol_registered_pass(self):
        """Test protocol registration passes when registered."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            protocol_registered=True,
            protocol_id="PROSPERO123",
            research_question_format="PICO",
            databases_selected=["PubMed", "Cochrane", "Embase"],
            inclusion_criteria_count=3,
            exclusion_criteria_count=2,
        )
        result = check_stage_criteria(data)
        protocol_result = next(
            r for r in result.criteria_results if r.criterion_id == "protocol_registered"
        )
        assert protocol_result.status == CriterionStatus.PASSED

    def test_protocol_registered_fail(self):
        """Test protocol registration fails when not registered."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            protocol_registered=False,
        )
        result = check_stage_criteria(data)
        protocol_result = next(
            r for r in result.criteria_results if r.criterion_id == "protocol_registered"
        )
        assert protocol_result.status == CriterionStatus.FAILED

    def test_protocol_not_required_for_narrative(self):
        """Test protocol not required for narrative reviews."""
        data = StageData(
            stage="planning",
            review_type="narrative",
            protocol_registered=False,
        )
        result = check_stage_criteria(data)
        protocol_result = next(
            r for r in result.criteria_results if r.criterion_id == "protocol_registered"
        )
        assert protocol_result.status == CriterionStatus.NOT_APPLICABLE

    def test_databases_selected_pass(self):
        """Test database selection passes with enough databases."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            databases_selected=["PubMed", "Cochrane", "Embase"],
        )
        result = check_stage_criteria(data)
        db_result = next(
            r for r in result.criteria_results if r.criterion_id == "databases_selected"
        )
        assert db_result.status == CriterionStatus.PASSED

    def test_databases_selected_fail(self):
        """Test database selection fails with too few databases."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            databases_selected=["PubMed"],  # Only 1, need 3
        )
        result = check_stage_criteria(data)
        db_result = next(
            r for r in result.criteria_results if r.criterion_id == "databases_selected"
        )
        assert db_result.status == CriterionStatus.FAILED

    def test_research_question_pass(self):
        """Test research question passes with valid format."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            research_question_format="PICO",
        )
        result = check_stage_criteria(data)
        rq_result = next(
            r for r in result.criteria_results if r.criterion_id == "research_question_defined"
        )
        assert rq_result.status == CriterionStatus.PASSED

    def test_research_question_all_formats(self):
        """Test all valid research question formats."""
        for fmt in ["PICO", "PEO", "SPIDER"]:
            data = StageData(
                stage="planning",
                review_type="systematic",
                research_question_format=fmt,
            )
            result = check_stage_criteria(data)
            rq_result = next(
                r for r in result.criteria_results if r.criterion_id == "research_question_defined"
            )
            assert rq_result.status == CriterionStatus.PASSED


# =============================================================================
# check_stage_criteria Tests - Search Stage
# =============================================================================


class TestSearchStage:
    """Tests for search stage criteria checks."""

    def test_all_databases_searched_pass(self):
        """Test all databases searched passes."""
        data = StageData(
            stage="search",
            review_type="systematic",
            databases_selected=["PubMed", "Cochrane"],
            databases_searched=["PubMed", "Cochrane"],
        )
        result = check_stage_criteria(data)
        db_result = next(
            r for r in result.criteria_results if r.criterion_id == "all_databases_searched"
        )
        assert db_result.status == CriterionStatus.PASSED

    def test_all_databases_searched_fail(self):
        """Test all databases searched fails when missing."""
        data = StageData(
            stage="search",
            review_type="systematic",
            databases_selected=["PubMed", "Cochrane", "Embase"],
            databases_searched=["PubMed", "Cochrane"],  # Missing Embase
        )
        result = check_stage_criteria(data)
        db_result = next(
            r for r in result.criteria_results if r.criterion_id == "all_databases_searched"
        )
        assert db_result.status == CriterionStatus.FAILED

    def test_search_saturation_pass(self):
        """Test search saturation passes below threshold."""
        data = StageData(
            stage="search",
            review_type="systematic",
            previous_total=100,
            new_papers_last_iteration=3,  # 3%
        )
        result = check_stage_criteria(data)
        sat_result = next(
            r for r in result.criteria_results if r.criterion_id == "search_saturation"
        )
        assert sat_result.status == CriterionStatus.PASSED

    def test_search_saturation_fail(self):
        """Test search saturation fails above threshold."""
        data = StageData(
            stage="search",
            review_type="systematic",
            previous_total=100,
            new_papers_last_iteration=10,  # 10%
        )
        result = check_stage_criteria(data)
        sat_result = next(
            r for r in result.criteria_results if r.criterion_id == "search_saturation"
        )
        assert sat_result.status == CriterionStatus.FAILED

    def test_minimum_papers_pass(self):
        """Test minimum papers passes with enough papers."""
        data = StageData(
            stage="search",
            review_type="systematic",
            total_papers_retrieved=50,
        )
        result = check_stage_criteria(data)
        papers_result = next(
            r for r in result.criteria_results if r.criterion_id == "minimum_papers"
        )
        assert papers_result.status == CriterionStatus.PASSED

    def test_minimum_papers_fail(self):
        """Test minimum papers fails with too few papers."""
        data = StageData(
            stage="search",
            review_type="systematic",
            total_papers_retrieved=20,  # Below 30
        )
        result = check_stage_criteria(data)
        papers_result = next(
            r for r in result.criteria_results if r.criterion_id == "minimum_papers"
        )
        assert papers_result.status == CriterionStatus.FAILED


# =============================================================================
# check_stage_criteria Tests - Screening Stage
# =============================================================================


class TestScreeningStage:
    """Tests for screening stage criteria checks."""

    def test_all_screened_pass(self):
        """Test all screened passes when complete."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            total_to_screen=100,
            screened_count=100,
        )
        result = check_stage_criteria(data)
        screened_result = next(
            r for r in result.criteria_results if r.criterion_id == "all_abstracts_screened"
        )
        assert screened_result.status == CriterionStatus.PASSED

    def test_all_screened_fail(self):
        """Test all screened fails when incomplete."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            total_to_screen=100,
            screened_count=80,
        )
        result = check_stage_criteria(data)
        screened_result = next(
            r for r in result.criteria_results if r.criterion_id == "all_abstracts_screened"
        )
        assert screened_result.status == CriterionStatus.FAILED

    def test_kappa_threshold_pass(self):
        """Test kappa threshold passes when >=0.8."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            kappa_score=0.85,
        )
        result = check_stage_criteria(data)
        kappa_result = next(
            r for r in result.criteria_results if r.criterion_id == "inter_rater_agreement"
        )
        assert kappa_result.status == CriterionStatus.PASSED

    def test_kappa_threshold_fail(self):
        """Test kappa threshold fails when <0.8."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            kappa_score=0.65,
        )
        result = check_stage_criteria(data)
        kappa_result = next(
            r for r in result.criteria_results if r.criterion_id == "inter_rater_agreement"
        )
        assert kappa_result.status == CriterionStatus.FAILED

    def test_dual_screening_required_systematic(self):
        """Test dual screening required for systematic reviews."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            dual_screening_performed=False,
        )
        result = check_stage_criteria(data)
        dual_result = next(
            r for r in result.criteria_results if r.criterion_id == "dual_screening_performed"
        )
        assert dual_result.status == CriterionStatus.FAILED
        assert dual_result.is_required is True

    def test_conflicts_resolved_pass(self):
        """Test conflicts resolved passes when all resolved."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            conflicts_count=10,
            conflicts_resolved=10,
        )
        result = check_stage_criteria(data)
        conflicts_result = next(
            r for r in result.criteria_results if r.criterion_id == "conflicts_resolved"
        )
        assert conflicts_result.status == CriterionStatus.PASSED

    def test_screening_time_compliance(self):
        """Test screening time compliance check."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            average_screening_time=90,  # 90 seconds, under 120
        )
        result = check_stage_criteria(data)
        time_result = next(
            r for r in result.criteria_results if r.criterion_id == "screening_time_compliance"
        )
        assert time_result.status == CriterionStatus.PASSED


# =============================================================================
# check_stage_criteria Tests - Full-text Stage
# =============================================================================


class TestFulltextStage:
    """Tests for full-text screening stage criteria checks."""

    def test_retrieval_rate_pass(self):
        """Test retrieval rate passes when >=95%."""
        data = StageData(
            stage="screening_fulltext",
            review_type="systematic",
            fulltexts_sought=100,
            fulltexts_retrieved=98,
        )
        result = check_stage_criteria(data)
        retrieval_result = next(
            r for r in result.criteria_results if r.criterion_id == "retrieval_rate"
        )
        assert retrieval_result.status == CriterionStatus.PASSED

    def test_retrieval_rate_warning(self):
        """Test retrieval rate warns when <95%."""
        data = StageData(
            stage="screening_fulltext",
            review_type="systematic",
            fulltexts_sought=100,
            fulltexts_retrieved=90,  # 90%
        )
        result = check_stage_criteria(data)
        retrieval_result = next(
            r for r in result.criteria_results if r.criterion_id == "retrieval_rate"
        )
        assert retrieval_result.status == CriterionStatus.WARNING

    def test_exclusions_documented_pass(self):
        """Test exclusions documented passes when all documented."""
        data = StageData(
            stage="screening_fulltext",
            review_type="systematic",
            exclusions_total=25,
            exclusions_documented=25,
        )
        result = check_stage_criteria(data)
        excl_result = next(
            r for r in result.criteria_results if r.criterion_id == "exclusion_reasons_documented"
        )
        assert excl_result.status == CriterionStatus.PASSED


# =============================================================================
# check_stage_criteria Tests - Reporting Stage
# =============================================================================


class TestReportingStage:
    """Tests for reporting stage criteria checks."""

    def test_prisma_complete_pass(self):
        """Test PRISMA complete passes."""
        data = StageData(
            stage="reporting",
            review_type="systematic",
            prisma_complete=True,
        )
        result = check_stage_criteria(data)
        prisma_result = next(
            r for r in result.criteria_results if r.criterion_id == "prisma_complete"
        )
        assert prisma_result.status == CriterionStatus.PASSED

    def test_prisma_validated_pass(self):
        """Test PRISMA validated passes."""
        data = StageData(
            stage="reporting",
            review_type="systematic",
            prisma_validated=True,
        )
        result = check_stage_criteria(data)
        validated_result = next(
            r for r in result.criteria_results if r.criterion_id == "prisma_numbers_validated"
        )
        assert validated_result.status == CriterionStatus.PASSED


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_all_stages(self):
        """Test getting all stages."""
        stages = get_all_stages()
        assert "planning" in stages
        assert "search" in stages
        assert "reporting" in stages
        assert len(stages) >= 9

    def test_get_stage_requirements(self):
        """Test getting stage requirements."""
        reqs = get_stage_requirements("search", "systematic")
        assert reqs["stage"] == "search"
        assert reqs["review_type"] == "systematic"
        assert len(reqs["required_criteria"]) > 0

    def test_get_stage_requirements_different_types(self):
        """Test requirements differ by review type."""
        systematic_reqs = get_stage_requirements("screening_abstract", "systematic")
        narrative_reqs = get_stage_requirements("screening_abstract", "narrative")

        # Systematic should have more required criteria
        assert len(systematic_reqs["required_criteria"]) >= len(narrative_reqs["required_criteria"])


# =============================================================================
# JSON Serialization Tests
# =============================================================================


class TestJSONSerialization:
    """Tests for JSON save/load functions."""

    def test_save_and_load_result(self):
        """Test round-trip JSON serialization."""
        data = StageData(
            stage="search",
            review_type="systematic",
            databases_selected=["PubMed", "Cochrane", "Embase"],
            databases_searched=["PubMed", "Cochrane", "Embase"],
            total_papers_retrieved=100,
        )
        original = check_stage_criteria(data)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_check_to_json(original, filepath)
            loaded = load_check_from_json(filepath)

            assert loaded.stage == original.stage
            assert loaded.review_type == original.review_type
            assert len(loaded.criteria_results) == len(original.criteria_results)
        finally:
            Path(filepath).unlink()

    def test_json_structure(self):
        """Test saved JSON has correct structure."""
        data = StageData(stage="planning", review_type="scoping")
        result = check_stage_criteria(data)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_check_to_json(result, filepath)

            with open(filepath) as f:
                json_data = json.load(f)

            assert "stage" in json_data
            assert "review_type" in json_data
            assert "criteria_results" in json_data
            assert "summary" in json_data
        finally:
            Path(filepath).unlink()


# =============================================================================
# Report Generation Tests
# =============================================================================


class TestReportGeneration:
    """Tests for report generation."""

    def test_generate_report_basic(self):
        """Test basic report generation."""
        data = StageData(
            stage="search",
            review_type="systematic",
            databases_selected=["PubMed"],
        )
        result = check_stage_criteria(data)
        report = generate_exit_report(result)

        assert "EXIT CRITERIA REPORT" in report
        assert "search" in report
        assert "systematic" in report

    def test_report_shows_failed(self):
        """Test report shows failed criteria."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            databases_selected=["PubMed"],  # Only 1, need 3
        )
        result = check_stage_criteria(data)
        report = generate_exit_report(result)

        assert "FAILED" in report

    def test_report_shows_passed(self):
        """Test report shows passed criteria."""
        data = StageData(
            stage="planning",
            review_type="systematic",
            protocol_registered=True,
            protocol_id="PROSPERO123",
            research_question_format="PICO",
            databases_selected=["PubMed", "Cochrane", "Embase"],
            inclusion_criteria_count=3,
            exclusion_criteria_count=2,
        )
        result = check_stage_criteria(data)
        report = generate_exit_report(result)

        assert "PASSED" in report


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_exact_threshold_kappa(self):
        """Test kappa exactly at threshold (0.8)."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            kappa_score=0.8,
        )
        result = check_stage_criteria(data)
        kappa_result = next(
            r for r in result.criteria_results if r.criterion_id == "inter_rater_agreement"
        )
        assert kappa_result.status == CriterionStatus.PASSED

    def test_exact_threshold_papers(self):
        """Test papers exactly at threshold."""
        data = StageData(
            stage="search",
            review_type="systematic",
            total_papers_retrieved=30,  # Exactly at minimum
        )
        result = check_stage_criteria(data)
        papers_result = next(
            r for r in result.criteria_results if r.criterion_id == "minimum_papers"
        )
        assert papers_result.status == CriterionStatus.PASSED

    def test_zero_to_screen(self):
        """Test handling of zero items to screen."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            total_to_screen=0,
            screened_count=0,
        )
        result = check_stage_criteria(data)
        screened_result = next(
            r for r in result.criteria_results if r.criterion_id == "all_abstracts_screened"
        )
        assert screened_result.status == CriterionStatus.PENDING

    def test_zero_conflicts(self):
        """Test handling of zero conflicts."""
        data = StageData(
            stage="screening_abstract",
            review_type="systematic",
            conflicts_count=0,
            conflicts_resolved=0,
        )
        result = check_stage_criteria(data)
        conflicts_result = next(
            r for r in result.criteria_results if r.criterion_id == "conflicts_resolved"
        )
        assert conflicts_result.status == CriterionStatus.PASSED

    def test_all_review_types(self):
        """Test all review types are handled."""
        for review_type in ["systematic", "scoping", "rapid", "narrative"]:
            data = StageData(stage="planning", review_type=review_type)
            result = check_stage_criteria(data)
            assert result is not None
            assert len(result.criteria_results) > 0

    def test_all_stages(self):
        """Test all stages are handled."""
        for stage in get_all_stages():
            data = StageData(stage=stage, review_type="systematic")
            result = check_stage_criteria(data)
            assert result is not None
            assert result.stage == stage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
