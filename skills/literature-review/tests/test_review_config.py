#!/usr/bin/env python3
"""
Tests for review_config.py

Comprehensive test suite for review configuration validation and
preflight checks.
"""

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from review_config import (  # noqa: E402
    Criterion,
    ReviewConfig,
    PreflightResult,
    REVIEW_REQUIREMENTS,
    preflight_check,
    create_config_from_dict,
    load_config_from_json,
    save_config_to_json,
    generate_protocol_template,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestReviewRequirements:
    """Tests for review requirements definitions."""

    def test_all_review_types_have_requirements(self):
        """Test all review types have defined requirements."""
        expected_types = ["systematic", "scoping", "narrative", "rapid"]
        for review_type in expected_types:
            assert review_type in REVIEW_REQUIREMENTS

    def test_systematic_requires_three_databases(self):
        """Test systematic review requires 3 databases."""
        assert REVIEW_REQUIREMENTS["systematic"]["min_databases"] == 3

    def test_systematic_requires_protocol(self):
        """Test systematic review requires protocol."""
        assert REVIEW_REQUIREMENTS["systematic"]["requires_protocol"]

    def test_systematic_requires_dual_screening(self):
        """Test systematic review requires dual screening."""
        assert REVIEW_REQUIREMENTS["systematic"]["requires_dual_screening"]

    def test_narrative_less_strict(self):
        """Test narrative review has less strict requirements."""
        narrative = REVIEW_REQUIREMENTS["narrative"]
        systematic = REVIEW_REQUIREMENTS["systematic"]
        assert narrative["min_databases"] <= systematic["min_databases"]
        assert not narrative["requires_protocol"]


# =============================================================================
# Criterion Tests
# =============================================================================


class TestCriterion:
    """Tests for Criterion dataclass."""

    def test_valid_criterion(self):
        """Test valid criterion has no errors."""
        criterion = Criterion(
            criterion="Randomized controlled trials only",
            rationale="RCTs provide highest quality evidence",
            category="study design",
        )
        errors = criterion.validate()
        assert len(errors) == 0

    def test_short_criterion_fails(self):
        """Test criterion too short fails validation."""
        criterion = Criterion(
            criterion="RCT",  # Too short
            rationale="RCTs provide highest quality evidence",
        )
        errors = criterion.validate()
        assert any("Criterion text" in e for e in errors)

    def test_short_rationale_fails(self):
        """Test rationale too short fails validation."""
        criterion = Criterion(
            criterion="Randomized controlled trials only",
            rationale="Quality",  # Too short
        )
        errors = criterion.validate()
        assert any("Rationale" in e for e in errors)

    def test_to_dict(self):
        """Test to_dict conversion."""
        criterion = Criterion(
            criterion="test criterion text",
            rationale="test rationale text",
            category="population",
        )
        d = criterion.to_dict()
        assert d["criterion"] == "test criterion text"
        assert d["category"] == "population"


# =============================================================================
# ReviewConfig Tests
# =============================================================================


class TestReviewConfig:
    """Tests for ReviewConfig dataclass."""

    @pytest.fixture
    def valid_config(self):
        """Fixture for a valid review configuration."""
        return ReviewConfig(
            title="Effects of exercise on depression: A systematic review",
            review_type="systematic",
            research_question={
                "population": "Adults with depression",
                "intervention": "Exercise interventions",
                "comparison": "Usual care",
                "outcome": "Depression symptoms",
            },
            question_type="PICO",
            domain="biomedical",
            subdomain="clinical",
            date_range_start=date(2010, 1, 1),
            date_range_end=date(2024, 12, 31),
            inclusion_criteria=[
                Criterion(
                    criterion="Randomized controlled trials only",
                    rationale="RCTs provide highest quality evidence",
                    category="study design",
                ),
                Criterion(
                    criterion="Adults aged 18 and older",
                    rationale="Focus on adult population",
                    category="population",
                ),
                Criterion(
                    criterion="Depression diagnosis required",
                    rationale="Ensures population has condition of interest",
                    category="population",
                ),
            ],
            exclusion_criteria=[
                Criterion(
                    criterion="Non-English publications",
                    rationale="Resource limitations for translation",
                    category="publication",
                ),
                Criterion(
                    criterion="Studies with <10 participants",
                    rationale="Insufficient statistical power",
                    category="study design",
                ),
            ],
            databases=["PubMed", "Cochrane Library", "PsycINFO", "CINAHL"],
            protocol_registration="PROSPERO: CRD42024000001",
            team_members=["Dr. Smith", "Dr. Jones"],
        )

    def test_valid_config_passes_validation(self, valid_config):
        """Test valid config has no errors."""
        errors = valid_config.validate()
        assert len(errors) == 0
        assert valid_config.is_valid()

    def test_get_requirements(self, valid_config):
        """Test get_requirements returns correct requirements."""
        reqs = valid_config.get_requirements()
        assert reqs["min_databases"] == 3
        assert reqs["requires_protocol"]


class TestReviewConfigValidation:
    """Tests for ReviewConfig validation."""

    def test_short_title_fails(self):
        """Test title too short fails validation."""
        config = ReviewConfig(
            title="Short",  # Too short
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
        )
        errors = config.validate()
        assert any("Title" in e for e in errors)

    def test_invalid_review_type_fails(self):
        """Test invalid review type fails validation."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="invalid_type",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
        )
        errors = config.validate()
        assert any("Invalid review type" in e for e in errors)

    def test_invalid_question_type_fails(self):
        """Test invalid question type fails validation."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="INVALID",
            domain="biomedical",
        )
        errors = config.validate()
        assert any("Invalid question type" in e for e in errors)

    def test_missing_research_question_fails(self):
        """Test missing research question fails validation."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={},  # Empty
            question_type="PICO",
            domain="biomedical",
        )
        errors = config.validate()
        assert any("Research question" in e for e in errors)

    def test_pico_missing_fields_fails(self):
        """Test PICO question missing required fields fails."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={
                "population": "Adults",
                # Missing intervention and outcome
            },
            question_type="PICO",
            domain="biomedical",
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            databases=["DB1", "DB2", "DB3"],
        )
        errors = config.validate()
        assert any("missing required field: intervention" in e for e in errors)
        assert any("missing required field: outcome" in e for e in errors)

    def test_peo_missing_fields_fails(self):
        """Test PEO question missing required fields fails."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={
                "population": "Adults",
                # Missing exposure and outcome
            },
            question_type="PEO",
            domain="biomedical",
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            databases=["DB1", "DB2", "DB3"],
        )
        errors = config.validate()
        assert any("PEO question missing" in e for e in errors)

    def test_spider_missing_fields_fails(self):
        """Test SPIDER question missing required fields fails."""
        config = ReviewConfig(
            title="Valid title for qualitative review",
            review_type="systematic",
            research_question={
                "sample": "Nurses",
                # Missing phenomenon, design, evaluation, research_type
            },
            question_type="SPIDER",
            domain="biomedical",
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion text here", "rationale text here"),
            ],
            databases=["DB1", "DB2", "DB3"],
        )
        errors = config.validate()
        assert any("SPIDER question missing" in e for e in errors)

    def test_insufficient_databases_fails(self):
        """Test insufficient databases fails validation."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed"],  # Only 1, need 3
        )
        errors = config.validate()
        assert any("at least 3 databases" in e for e in errors)

    def test_insufficient_inclusion_criteria_fails(self):
        """Test insufficient inclusion criteria fails."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["DB1", "DB2", "DB3"],
            inclusion_criteria=[
                Criterion("criterion", "rationale here"),
            ],  # Only 1, need 3 for systematic
        )
        errors = config.validate()
        assert any("inclusion criteria" in e.lower() for e in errors)

    def test_invalid_date_range_fails(self):
        """Test end date before start date fails."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2019, 1, 1),  # Before start
        )
        errors = config.validate()
        assert any("End date must be after start date" in e for e in errors)

    def test_future_end_date_fails(self):
        """Test future end date fails."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2030, 1, 1),  # Future date
        )
        errors = config.validate()
        assert any("future" in e.lower() for e in errors)

    def test_missing_protocol_warning(self):
        """Test missing protocol registration generates warning."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["DB1", "DB2", "DB3"],
            inclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
                Criterion("criterion three here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            protocol_registration="",  # Empty
        )
        errors = config.validate()
        assert any("Protocol registration" in e for e in errors)


# =============================================================================
# Preflight Check Tests
# =============================================================================


class TestPreflightCheck:
    """Tests for preflight_check function."""

    @pytest.fixture
    def valid_config(self):
        """Fixture for valid config."""
        return ReviewConfig(
            title="Effects of exercise on depression: A systematic review",
            review_type="systematic",
            research_question={
                "population": "Adults with depression",
                "intervention": "Exercise interventions",
                "comparison": "Usual care",
                "outcome": "Depression symptoms",
            },
            question_type="PICO",
            domain="biomedical",
            subdomain="clinical",
            date_range_start=date(2015, 1, 1),
            date_range_end=date(2024, 12, 31),
            inclusion_criteria=[
                Criterion("criterion one here", "rationale text here", "study design"),
                Criterion("criterion two here", "rationale text here", "population"),
                Criterion("criterion three here", "rationale text here", "outcome"),
            ],
            exclusion_criteria=[
                Criterion("criterion one here", "rationale text here", "publication"),
                Criterion("criterion two here", "rationale text here", "study design"),
            ],
            databases=["PubMed", "Cochrane Library", "PsycINFO"],
            protocol_registration="PROSPERO: CRD42024000001",
            team_members=["Dr. Smith", "Dr. Jones"],
        )

    def test_valid_config_is_ready(self, valid_config):
        """Test valid config is ready to start."""
        result = preflight_check(valid_config)
        assert result.is_ready()
        assert result.config_valid

    def test_preflight_returns_all_fields(self, valid_config):
        """Test preflight returns all expected fields."""
        result = preflight_check(valid_config)
        assert hasattr(result, "config_valid")
        assert hasattr(result, "config_errors")
        assert hasattr(result, "database_coverage")
        assert hasattr(result, "date_range_appropriate")
        assert hasattr(result, "criteria_specificity")
        assert hasattr(result, "recommendations")

    def test_preflight_detects_missing_preprint(self):
        """Test preflight warns about missing preprint."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed", "Cochrane", "CINAHL"],  # No preprint
            inclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
                Criterion("criterion three here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            protocol_registration="PROSPERO: test",
        )
        result = preflight_check(config)
        assert result.database_coverage["missing_preprint"]
        assert any("preprint" in r.lower() for r in result.recommendations)

    def test_preflight_warns_broad_date_range(self):
        """Test preflight warns about very broad date range."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            date_range_start=date(1980, 1, 1),
            date_range_end=date(2024, 1, 1),  # 44 years
            databases=["PubMed", "Cochrane", "bioRxiv"],
            inclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
                Criterion("criterion three here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            protocol_registration="PROSPERO: test",
        )
        result = preflight_check(config)
        assert result.date_range_appropriate.get("warning") is not None

    def test_preflight_warns_missing_team_for_dual_screening(self):
        """Test preflight warns about insufficient team for dual screening."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed", "Cochrane", "bioRxiv"],
            inclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
                Criterion("criterion three here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion one here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            protocol_registration="PROSPERO: test",
            team_members=["Dr. Solo"],  # Only one person
        )
        result = preflight_check(config)
        assert any("dual screening" in r.lower() for r in result.recommendations)


# =============================================================================
# Factory and Serialization Tests
# =============================================================================


class TestCreateConfigFromDict:
    """Tests for create_config_from_dict function."""

    def test_create_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "title": "Test Review Title Here",
            "review_type": "systematic",
            "research_question": {
                "population": "Adults",
                "intervention": "Exercise",
                "outcome": "Health",
            },
            "question_type": "PICO",
            "domain": "biomedical",
            "databases": ["PubMed", "Cochrane", "CINAHL"],
            "date_range_start": "2020-01-01",
            "date_range_end": "2024-12-31",
            "inclusion_criteria": [
                {"criterion": "RCTs only", "rationale": "High quality", "category": "design"},
            ],
            "exclusion_criteria": [
                {"criterion": "Non-English", "rationale": "Resource limit", "category": "pub"},
            ],
        }
        config = create_config_from_dict(data)
        assert config.title == "Test Review Title Here"
        assert config.review_type == "systematic"
        assert config.date_range_start == date(2020, 1, 1)
        assert len(config.inclusion_criteria) == 1

    def test_create_from_dict_missing_optional_fields(self):
        """Test creating from dict with missing optional fields."""
        data = {
            "title": "Minimal Review Config",
            "review_type": "narrative",
            "research_question": {"population": "test"},
            "question_type": "PICO",
            "domain": "biomedical",
        }
        config = create_config_from_dict(data)
        assert config.subdomain is None
        assert config.date_range_start is None
        assert config.databases == []


class TestJSONSerialization:
    """Tests for JSON save/load functions."""

    @pytest.fixture
    def sample_config(self):
        """Fixture for sample config."""
        return ReviewConfig(
            title="Test Review Title for JSON",
            review_type="systematic",
            research_question={
                "population": "Adults",
                "intervention": "Exercise",
                "outcome": "Depression",
            },
            question_type="PICO",
            domain="biomedical",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2024, 12, 31),
            databases=["PubMed", "Cochrane"],
            inclusion_criteria=[
                Criterion("RCTs only text here", "Quality evidence rationale"),
            ],
            exclusion_criteria=[
                Criterion("Non-English text", "Translation limits here"),
            ],
        )

    def test_save_and_load_config(self, sample_config):
        """Test round-trip JSON serialization."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_config_to_json(sample_config, filepath)
            loaded = load_config_from_json(filepath)

            assert loaded.title == sample_config.title
            assert loaded.review_type == sample_config.review_type
            assert loaded.date_range_start == sample_config.date_range_start
            assert len(loaded.databases) == len(sample_config.databases)
        finally:
            Path(filepath).unlink()

    def test_json_is_valid_format(self, sample_config):
        """Test saved JSON is properly formatted."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_config_to_json(sample_config, filepath)

            with open(filepath) as f:
                content = f.read()

            # Verify valid JSON
            data = json.loads(content)
            assert "title" in data
            assert "review_type" in data
        finally:
            Path(filepath).unlink()


# =============================================================================
# Protocol Template Tests
# =============================================================================


class TestGenerateProtocolTemplate:
    """Tests for generate_protocol_template function."""

    @pytest.fixture
    def sample_config(self):
        """Fixture for sample config."""
        return ReviewConfig(
            title="Exercise and Depression Review",
            review_type="systematic",
            research_question={
                "population": "Adults with depression",
                "intervention": "Exercise",
                "comparison": "Usual care",
                "outcome": "Depression symptoms",
            },
            question_type="PICO",
            domain="biomedical",
            subdomain="clinical",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2024, 12, 31),
            databases=["PubMed", "Cochrane"],
            inclusion_criteria=[
                Criterion("RCTs only text here", "Quality rationale", "study design"),
            ],
            exclusion_criteria=[
                Criterion("Non-English text", "Translation rationale", "publication"),
            ],
            protocol_registration="PROSPERO: CRD42024000001",
            team_members=["Dr. Smith", "Dr. Jones"],
        )

    def test_protocol_includes_title(self, sample_config):
        """Test protocol includes title."""
        protocol = generate_protocol_template(sample_config)
        assert sample_config.title in protocol

    def test_protocol_includes_research_question(self, sample_config):
        """Test protocol includes research question components."""
        protocol = generate_protocol_template(sample_config)
        assert "RESEARCH QUESTION" in protocol
        assert "Population:" in protocol

    def test_protocol_includes_criteria(self, sample_config):
        """Test protocol includes inclusion/exclusion criteria."""
        protocol = generate_protocol_template(sample_config)
        assert "INCLUSION CRITERIA" in protocol
        assert "EXCLUSION CRITERIA" in protocol

    def test_protocol_includes_databases(self, sample_config):
        """Test protocol includes databases."""
        protocol = generate_protocol_template(sample_config)
        assert "PubMed" in protocol
        assert "Cochrane" in protocol

    def test_protocol_includes_registration(self, sample_config):
        """Test protocol includes registration."""
        protocol = generate_protocol_template(sample_config)
        assert "PROSPERO" in protocol

    def test_protocol_includes_team(self, sample_config):
        """Test protocol includes team members."""
        protocol = generate_protocol_template(sample_config)
        assert "TEAM MEMBERS" in protocol
        assert "Dr. Smith" in protocol


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_narrative_review_less_strict(self):
        """Test narrative review has less strict requirements."""
        config = ReviewConfig(
            title="Narrative Review Title Here",
            review_type="narrative",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed", "Cochrane"],  # 2 is enough for narrative
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
            ],  # 1 is enough for narrative
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
            ],
        )
        # Narrative doesn't require protocol
        errors = config.validate()
        protocol_errors = [e for e in errors if "Protocol" in e]
        assert len(protocol_errors) == 0

    def test_rapid_review_requirements(self):
        """Test rapid review has appropriate requirements."""
        config = ReviewConfig(
            title="Rapid Review Title Here",
            review_type="rapid",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed", "Cochrane"],  # 2 is enough for rapid
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
            ],
            protocol_registration="OSF: test",  # Rapid does require protocol
        )
        errors = config.validate()
        # Should pass if requirements are met
        database_errors = [e for e in errors if "databases" in e.lower()]
        assert len(database_errors) == 0

    def test_scoping_review_requirements(self):
        """Test scoping review requirements."""
        config = ReviewConfig(
            title="Scoping Review Title Here",
            review_type="scoping",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="biomedical",
            databases=["PubMed", "Scopus"],  # 2 is enough
            inclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
                Criterion("criterion two here", "rationale text here"),
            ],
            exclusion_criteria=[
                Criterion("criterion text here", "rationale text here"),
            ],
            protocol_registration="OSF: test",
        )
        errors = config.validate()
        # Scoping doesn't require dual screening or quality assessment
        assert config.get_requirements()["requires_dual_screening"] is False

    def test_empty_domain_fails(self):
        """Test empty domain fails validation."""
        config = ReviewConfig(
            title="Valid title for systematic review",
            review_type="systematic",
            research_question={"population": "test", "intervention": "test", "outcome": "test"},
            question_type="PICO",
            domain="",  # Empty
        )
        errors = config.validate()
        assert any("Domain" in e for e in errors)

    def test_criterion_without_category(self):
        """Test criterion without category is valid."""
        criterion = Criterion(
            criterion="Valid criterion text",
            rationale="Valid rationale text here",
            # No category
        )
        errors = criterion.validate()
        assert len(errors) == 0

    def test_preflight_result_to_dict(self):
        """Test PreflightResult to_dict conversion."""
        result = PreflightResult(
            config_valid=True,
            config_errors=[],
            database_coverage={"total_databases": 3},
            date_range_appropriate={"span_years": 5},
            criteria_specificity={"inclusion_count": 3},
            recommendations=["Consider adding preprint search"],
        )
        d = result.to_dict()
        assert d["config_valid"] is True
        assert "recommendations" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
