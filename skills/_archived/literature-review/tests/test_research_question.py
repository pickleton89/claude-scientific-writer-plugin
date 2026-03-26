#!/usr/bin/env python3
"""
Tests for research_question.py

Comprehensive test suite for PICO, PEO, and SPIDER research question schemas.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from research_question import (  # noqa: E402
    PICOQuestion,
    PEOQuestion,
    SPIDERQuestion,
    detect_question_type,
    create_question_from_dict,
    load_question_from_json,
    save_question_to_json,
)


# =============================================================================
# PICO Question Tests
# =============================================================================


class TestPICOQuestion:
    """Tests for PICOQuestion dataclass."""

    def test_valid_pico_question(self):
        """Test creating a valid PICO question."""
        pico = PICOQuestion(
            population="adults with type 2 diabetes aged 40-65",
            intervention="metformin monotherapy",
            comparison="lifestyle modification alone",
            outcome="HbA1c reduction",
        )
        assert pico.is_valid()
        assert len(pico.validate()) == 0

    def test_pico_with_timeframe(self):
        """Test PICO question with optional timeframe."""
        pico = PICOQuestion(
            population="hypertensive adults over 50",
            intervention="ACE inhibitors",
            comparison="placebo",
            outcome="blood pressure reduction",
            timeframe="6 months",
        )
        assert pico.is_valid()
        assert "6 months" in pico.to_question_string()

    def test_pico_missing_population(self):
        """Test validation fails with short population."""
        pico = PICOQuestion(
            population="pts",  # Too short
            intervention="drug therapy",
            comparison="placebo",
            outcome="improvement",
        )
        errors = pico.validate()
        assert any("Population" in e for e in errors)

    def test_pico_missing_intervention(self):
        """Test validation fails with empty intervention."""
        pico = PICOQuestion(
            population="adults with chronic pain",
            intervention="",
            comparison="placebo",
            outcome="pain reduction",
        )
        errors = pico.validate()
        assert any("Intervention" in e for e in errors)

    def test_pico_missing_outcome(self):
        """Test validation fails with empty outcome."""
        pico = PICOQuestion(
            population="children with asthma",
            intervention="inhaled corticosteroids",
            comparison="placebo",
            outcome="",
        )
        errors = pico.validate()
        assert any("Outcome" in e for e in errors)

    def test_pico_missing_comparison_warning(self):
        """Test warning (not error) for missing comparison."""
        pico = PICOQuestion(
            population="elderly patients with osteoarthritis",
            intervention="physical therapy",
            comparison="",  # Empty comparison
            outcome="mobility improvement",
        )
        errors = pico.validate()
        assert any("Warning" in e and "comparison" in e.lower() for e in errors)
        # Should still be valid (warnings don't fail validation)
        assert pico.is_valid()

    def test_pico_too_broad_population(self):
        """Test validation fails with overly broad population."""
        pico = PICOQuestion(
            population="patients",  # Too broad
            intervention="surgery",
            comparison="conservative treatment",
            outcome="recovery time",
        )
        errors = pico.validate()
        assert any("too broad" in e.lower() for e in errors)

    def test_pico_to_search_terms(self):
        """Test search term generation."""
        pico = PICOQuestion(
            population="adults with diabetes, obesity",
            intervention="metformin, lifestyle intervention",
            comparison="placebo",
            outcome="weight loss, HbA1c",
        )
        terms = pico.to_search_terms()
        assert "population" in terms
        assert "adults with diabetes" in terms["population"]
        assert "obesity" in terms["population"]
        assert "metformin" in terms["intervention"]
        assert "lifestyle intervention" in terms["intervention"]

    def test_pico_to_question_string(self):
        """Test natural language question generation."""
        pico = PICOQuestion(
            population="adults with insomnia",
            intervention="cognitive behavioral therapy",
            comparison="sleep medication",
            outcome="sleep quality",
        )
        question = pico.to_question_string()
        assert "adults with insomnia" in question
        assert "cognitive behavioral therapy" in question
        assert "compared to" in question
        assert "sleep medication" in question
        assert question.endswith("?")

    def test_pico_to_dict(self):
        """Test dictionary conversion."""
        pico = PICOQuestion(
            population="test population",
            intervention="test intervention",
            comparison="test comparison",
            outcome="test outcome",
        )
        d = pico.to_dict()
        assert d["type"] == "PICO"
        assert d["population"] == "test population"


# =============================================================================
# PEO Question Tests
# =============================================================================


class TestPEOQuestion:
    """Tests for PEOQuestion dataclass."""

    def test_valid_peo_question(self):
        """Test creating a valid PEO question."""
        peo = PEOQuestion(
            population="children under 5 in urban areas",
            exposure="air pollution (PM2.5 > 35 μg/m³)",
            outcome="respiratory infections",
        )
        assert peo.is_valid()
        assert len(peo.validate()) == 0

    def test_peo_with_timeframe(self):
        """Test PEO question with optional timeframe."""
        peo = PEOQuestion(
            population="pregnant women",
            exposure="prenatal stress",
            outcome="birth weight",
            timeframe="third trimester",
        )
        assert peo.is_valid()
        assert "third trimester" in peo.to_question_string()

    def test_peo_missing_population(self):
        """Test validation fails with short population."""
        peo = PEOQuestion(
            population="ppl",  # Too short
            exposure="smoking",
            outcome="lung cancer",
        )
        errors = peo.validate()
        assert any("Population" in e for e in errors)

    def test_peo_missing_exposure(self):
        """Test validation fails with empty exposure."""
        peo = PEOQuestion(
            population="adults over 40",
            exposure="",
            outcome="heart disease",
        )
        errors = peo.validate()
        assert any("Exposure" in e for e in errors)

    def test_peo_missing_outcome(self):
        """Test validation fails with empty outcome."""
        peo = PEOQuestion(
            population="healthcare workers",
            exposure="shift work",
            outcome="",
        )
        errors = peo.validate()
        assert any("Outcome" in e for e in errors)

    def test_peo_to_search_terms(self):
        """Test search term generation."""
        peo = PEOQuestion(
            population="adults, elderly",
            exposure="sedentary lifestyle, physical inactivity",
            outcome="cardiovascular disease",
        )
        terms = peo.to_search_terms()
        assert "population" in terms
        assert "exposure" in terms
        assert "outcome" in terms
        assert len(terms["exposure"]) == 2

    def test_peo_to_question_string(self):
        """Test natural language question generation."""
        peo = PEOQuestion(
            population="office workers",
            exposure="prolonged sitting",
            outcome="back pain",
        )
        question = peo.to_question_string()
        assert "associated with" in question
        assert question.endswith("?")

    def test_peo_to_dict(self):
        """Test dictionary conversion."""
        peo = PEOQuestion(
            population="test population",
            exposure="test exposure",
            outcome="test outcome",
        )
        d = peo.to_dict()
        assert d["type"] == "PEO"
        assert d["exposure"] == "test exposure"


# =============================================================================
# SPIDER Question Tests
# =============================================================================


class TestSPIDERQuestion:
    """Tests for SPIDERQuestion dataclass."""

    def test_valid_spider_question(self):
        """Test creating a valid SPIDER question."""
        spider = SPIDERQuestion(
            sample="nurses in intensive care units",
            phenomenon="burnout and moral distress",
            design="phenomenological",
            evaluation="thematic analysis",
            research_type="qualitative",
        )
        assert spider.is_valid()
        assert len(spider.validate()) == 0

    def test_spider_all_design_types(self):
        """Test all valid design types."""
        valid_designs = [
            "phenomenological",
            "ethnographic",
            "grounded theory",
            "case study",
            "narrative",
            "action research",
            "descriptive",
        ]
        for design in valid_designs:
            spider = SPIDERQuestion(
                sample="healthcare professionals",
                phenomenon="work experience",
                design=design,
                evaluation="analysis",
                research_type="qualitative",
            )
            assert spider.is_valid(), f"Design '{design}' should be valid"

    def test_spider_mixed_research_type(self):
        """Test mixed research type."""
        spider = SPIDERQuestion(
            sample="cancer survivors",
            phenomenon="quality of life",
            design="case study",
            evaluation="mixed methods analysis",
            research_type="mixed",
        )
        assert spider.is_valid()
        assert spider.research_type == "mixed"

    def test_spider_invalid_design(self):
        """Test validation fails with invalid design."""
        spider = SPIDERQuestion(
            sample="patients with chronic illness",
            phenomenon="coping strategies",
            design="invalid_design",  # Not a valid design
            evaluation="content analysis",
            research_type="qualitative",
        )
        errors = spider.validate()
        assert any("Design must be one of" in e for e in errors)

    def test_spider_invalid_research_type(self):
        """Test validation fails with invalid research type."""
        spider = SPIDERQuestion(
            sample="elderly caregivers",
            phenomenon="caregiving burden",
            design="phenomenological",
            evaluation="thematic analysis",
            research_type="quantitative",  # Invalid for SPIDER
        )
        errors = spider.validate()
        assert any("Research type must be" in e for e in errors)

    def test_spider_missing_sample(self):
        """Test validation fails with short sample."""
        spider = SPIDERQuestion(
            sample="pts",  # Too short
            phenomenon="experiences of treatment",
            design="narrative",
            evaluation="narrative analysis",
            research_type="qualitative",
        )
        errors = spider.validate()
        assert any("Sample" in e for e in errors)

    def test_spider_missing_phenomenon(self):
        """Test validation fails with short phenomenon."""
        spider = SPIDERQuestion(
            sample="medical students",
            phenomenon="exp",  # Too short
            design="grounded theory",
            evaluation="constant comparison",
            research_type="qualitative",
        )
        errors = spider.validate()
        assert any("Phenomenon" in e for e in errors)

    def test_spider_to_search_terms(self):
        """Test search term generation."""
        spider = SPIDERQuestion(
            sample="parents, caregivers",
            phenomenon="decision making, healthcare choices",
            design="ethnographic",
            evaluation="observation, interviews",
            research_type="qualitative",
        )
        terms = spider.to_search_terms()
        assert "sample" in terms
        assert "phenomenon" in terms
        assert "design" in terms
        assert terms["design"] == ["ethnographic"]
        assert terms["research_type"] == ["qualitative"]

    def test_spider_to_question_string(self):
        """Test natural language question generation."""
        spider = SPIDERQuestion(
            sample="adolescents with eating disorders",
            phenomenon="recovery journey",
            design="narrative",
            evaluation="narrative analysis",
            research_type="qualitative",
        )
        question = spider.to_question_string()
        assert "adolescents with eating disorders" in question
        assert "recovery journey" in question
        assert "narrative" in question
        assert question.endswith("?")

    def test_spider_to_dict(self):
        """Test dictionary conversion."""
        spider = SPIDERQuestion(
            sample="test sample",
            phenomenon="test phenomenon",
            design="case study",
            evaluation="test evaluation",
            research_type="qualitative",
        )
        d = spider.to_dict()
        assert d["type"] == "SPIDER"
        assert d["design"] == "case study"


# =============================================================================
# Question Type Detection Tests
# =============================================================================


class TestQuestionTypeDetection:
    """Tests for detect_question_type function."""

    def test_detect_pico_intervention(self):
        """Test detection of PICO from intervention keywords."""
        assert detect_question_type("What is the effect of treatment X?") == "PICO"
        assert detect_question_type("Is intervention A effective?") == "PICO"
        assert detect_question_type("Drug therapy versus placebo") == "PICO"

    def test_detect_pico_comparison(self):
        """Test detection of PICO from comparison keywords."""
        assert detect_question_type("Compared to standard care...") == "PICO"
        assert detect_question_type("Treatment A vs treatment B") == "PICO"

    def test_detect_peo_exposure(self):
        """Test detection of PEO from exposure keywords."""
        assert detect_question_type("Is exposure to X associated with Y?") == "PEO"
        assert detect_question_type("Risk factor for disease") == "PEO"
        assert detect_question_type("Association between smoking and cancer") == "PEO"

    def test_detect_spider_qualitative(self):
        """Test detection of SPIDER from qualitative keywords."""
        assert detect_question_type("Qualitative study of experiences") == "SPIDER"
        assert detect_question_type("What are patients' perceptions?") == "SPIDER"
        assert detect_question_type("Lived experience of chronic pain") == "SPIDER"
        assert detect_question_type("Phenomenological exploration") == "SPIDER"

    def test_detect_defaults_to_pico(self):
        """Test that ambiguous questions default to PICO."""
        assert detect_question_type("General research question") == "PICO"
        assert detect_question_type("Study of outcomes") == "PICO"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateQuestionFromDict:
    """Tests for create_question_from_dict function."""

    def test_create_pico_from_dict(self):
        """Test creating PICO from dictionary."""
        data = {
            "type": "PICO",
            "population": "adults with diabetes",
            "intervention": "insulin",
            "comparison": "oral medication",
            "outcome": "blood sugar control",
        }
        question = create_question_from_dict(data)
        assert isinstance(question, PICOQuestion)
        assert question.population == "adults with diabetes"

    def test_create_peo_from_dict(self):
        """Test creating PEO from dictionary."""
        data = {
            "type": "PEO",
            "population": "workers in factories",
            "exposure": "chemical fumes",
            "outcome": "respiratory illness",
        }
        question = create_question_from_dict(data)
        assert isinstance(question, PEOQuestion)
        assert question.exposure == "chemical fumes"

    def test_create_spider_from_dict(self):
        """Test creating SPIDER from dictionary."""
        data = {
            "type": "SPIDER",
            "sample": "new mothers",
            "phenomenon": "postpartum depression experience",
            "design": "phenomenological",
            "evaluation": "interpretive analysis",
            "research_type": "qualitative",
        }
        question = create_question_from_dict(data)
        assert isinstance(question, SPIDERQuestion)
        assert question.design == "phenomenological"

    def test_create_with_lowercase_type(self):
        """Test that type detection is case-insensitive."""
        data = {
            "type": "pico",
            "population": "test population",
            "intervention": "test",
            "comparison": "test",
            "outcome": "test",
        }
        question = create_question_from_dict(data)
        assert isinstance(question, PICOQuestion)

    def test_create_with_unknown_type_raises(self):
        """Test that unknown type raises ValueError."""
        data = {"type": "UNKNOWN", "field": "value"}
        with pytest.raises(ValueError, match="Unknown question type"):
            create_question_from_dict(data)


# =============================================================================
# JSON Serialization Tests
# =============================================================================


class TestJSONSerialization:
    """Tests for JSON load/save functions."""

    def test_save_and_load_pico(self):
        """Test round-trip JSON serialization for PICO."""
        pico = PICOQuestion(
            population="adults with hypertension",
            intervention="beta blockers",
            comparison="ACE inhibitors",
            outcome="blood pressure",
            timeframe="1 year",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_question_to_json(pico, filepath)
            loaded = load_question_from_json(filepath)

            assert isinstance(loaded, PICOQuestion)
            assert loaded.population == pico.population
            assert loaded.timeframe == pico.timeframe
        finally:
            Path(filepath).unlink()

    def test_save_and_load_peo(self):
        """Test round-trip JSON serialization for PEO."""
        peo = PEOQuestion(
            population="adolescents",
            exposure="social media use",
            outcome="mental health",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_question_to_json(peo, filepath)
            loaded = load_question_from_json(filepath)

            assert isinstance(loaded, PEOQuestion)
            assert loaded.exposure == peo.exposure
        finally:
            Path(filepath).unlink()

    def test_save_and_load_spider(self):
        """Test round-trip JSON serialization for SPIDER."""
        spider = SPIDERQuestion(
            sample="palliative care nurses",
            phenomenon="end of life care experiences",
            design="phenomenological",
            evaluation="hermeneutic analysis",
            research_type="qualitative",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_question_to_json(spider, filepath)
            loaded = load_question_from_json(filepath)

            assert isinstance(loaded, SPIDERQuestion)
            assert loaded.design == spider.design
        finally:
            Path(filepath).unlink()

    def test_json_format_is_readable(self):
        """Test that saved JSON is properly formatted."""
        pico = PICOQuestion(
            population="test",
            intervention="test",
            comparison="test",
            outcome="test",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            filepath = f.name

        try:
            save_question_to_json(pico, filepath)

            with open(filepath) as f:
                content = f.read()

            # Check it's valid JSON
            data = json.loads(content)
            assert "type" in data

            # Check it's indented (pretty-printed)
            assert "\n" in content
        finally:
            Path(filepath).unlink()


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_search_terms_with_or_separator(self):
        """Test search terms split on 'OR' keyword."""
        pico = PICOQuestion(
            population="adults OR elderly",
            intervention="drug",
            comparison="placebo",
            outcome="recovery",
        )
        terms = pico.to_search_terms()
        assert "adults" in terms["population"]
        assert "elderly" in terms["population"]

    def test_search_terms_with_semicolon_separator(self):
        """Test search terms split on semicolon."""
        peo = PEOQuestion(
            population="men; women",
            exposure="pollution",
            outcome="asthma",
        )
        terms = peo.to_search_terms()
        assert len(terms["population"]) == 2

    def test_empty_comparison_search_terms(self):
        """Test empty comparison produces empty list."""
        pico = PICOQuestion(
            population="test population",
            intervention="test",
            comparison="",
            outcome="test",
        )
        terms = pico.to_search_terms()
        assert terms["comparison"] == []

    def test_whitespace_handling_in_validation(self):
        """Test that whitespace-only fields fail validation."""
        pico = PICOQuestion(
            population="   ",  # Whitespace only
            intervention="drug",
            comparison="placebo",
            outcome="effect",
        )
        errors = pico.validate()
        assert any("Population" in e for e in errors)

    def test_unicode_characters_in_fields(self):
        """Test handling of unicode characters."""
        peo = PEOQuestion(
            population="adults with café-au-lait spots",
            exposure="UV radiation (≥50 mJ/cm²)",
            outcome="melanoma risk",
        )
        assert peo.is_valid()
        question = peo.to_question_string()
        assert "≥" in question


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
