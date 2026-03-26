"""Tests for validate_input.py - Input schema validation."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_input import (
    ScientificDomain,
    ObservationType,
    ExplanationLevel,
    HypothesisInput,
    validate_input,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def valid_input():
    """Complete valid input dictionary."""
    return {
        "phenomenon_description": "Observed unexpected protein aggregation in neuronal cells under oxidative stress conditions that correlates with mitochondrial dysfunction",
        "domain": "biomedical",
        "observation_type": "unexpected_finding",
        "known_mechanisms": ["oxidative damage", "protein misfolding"],
        "excluded_explanations": ["sample contamination"],
        "explanation_levels": ["molecular", "cellular"],
        "target_hypothesis_count": 3,
        "available_methods": ["western blot", "mass spectrometry", "microscopy"],
        "timeline": "standard",
    }


@pytest.fixture
def minimal_valid_input():
    """Minimum required fields only."""
    return {
        "phenomenon_description": "A " * 25 + "test phenomenon description",  # 50+ chars
        "domain": "chemistry",
        "observation_type": "correlation",
        "explanation_levels": ["molecular"],
        "target_hypothesis_count": 4,
    }


# =============================================================================
# ScientificDomain Enum Tests
# =============================================================================


class TestScientificDomain:
    def test_all_domains_exist(self):
        """All expected domains are defined."""
        expected = [
            "biomedical",
            "chemistry",
            "physics",
            "ecology",
            "materials",
            "computational",
            "neuroscience",
            "engineering",
            "other",
        ]
        for domain in expected:
            assert ScientificDomain(domain).value == domain

    def test_invalid_domain_raises(self):
        """Invalid domain value raises ValueError."""
        with pytest.raises(ValueError):
            ScientificDomain("invalid_domain")


# =============================================================================
# ObservationType Enum Tests
# =============================================================================


class TestObservationType:
    def test_all_observation_types_exist(self):
        """All expected observation types are defined."""
        expected = [
            "unexpected_finding",
            "correlation",
            "pattern",
            "anomaly",
            "mechanism_gap",
            "conflicting_results",
        ]
        for obs_type in expected:
            assert ObservationType(obs_type).value == obs_type

    def test_invalid_observation_type_raises(self):
        """Invalid observation type raises ValueError."""
        with pytest.raises(ValueError):
            ObservationType("invalid_type")


# =============================================================================
# ExplanationLevel Enum Tests
# =============================================================================


class TestExplanationLevel:
    def test_all_levels_exist(self):
        """All expected explanation levels are defined."""
        expected = [
            "molecular",
            "cellular",
            "tissue",
            "organism",
            "population",
            "ecosystem",
        ]
        for level in expected:
            assert ExplanationLevel(level).value == level

    def test_invalid_level_raises(self):
        """Invalid explanation level raises ValueError."""
        with pytest.raises(ValueError):
            ExplanationLevel("atomic")


# =============================================================================
# HypothesisInput Dataclass Tests
# =============================================================================


class TestHypothesisInput:
    def test_valid_input_creates_instance(self, valid_input):
        """Valid input creates HypothesisInput instance."""
        hypothesis_input = HypothesisInput(
            phenomenon_description=valid_input["phenomenon_description"],
            domain=ScientificDomain(valid_input["domain"]),
            observation_type=ObservationType(valid_input["observation_type"]),
            known_mechanisms=valid_input["known_mechanisms"],
            excluded_explanations=valid_input["excluded_explanations"],
            explanation_levels=[
                ExplanationLevel(level) for level in valid_input["explanation_levels"]
            ],
            target_hypothesis_count=valid_input["target_hypothesis_count"],
            available_methods=valid_input["available_methods"],
            timeline=valid_input["timeline"],
        )
        assert hypothesis_input.domain == ScientificDomain.BIOMEDICAL
        assert hypothesis_input.target_hypothesis_count == 3

    def test_short_description_fails(self):
        """Phenomenon description < 50 chars raises ValueError."""
        with pytest.raises(ValueError, match="at least 50 characters"):
            HypothesisInput(
                phenomenon_description="Too short",
                domain=ScientificDomain.BIOMEDICAL,
                observation_type=ObservationType.CORRELATION,
                known_mechanisms=[],
                excluded_explanations=[],
                explanation_levels=[ExplanationLevel.MOLECULAR],
                target_hypothesis_count=3,
                available_methods=[],
                timeline="standard",
            )

    def test_invalid_hypothesis_count_fails(self):
        """Target hypothesis count not in [3, 4, 5] raises ValueError."""
        long_desc = "A " * 30
        for invalid_count in [0, 1, 2, 6, 10]:
            with pytest.raises(ValueError, match="exactly 3, 4, or 5"):
                HypothesisInput(
                    phenomenon_description=long_desc,
                    domain=ScientificDomain.BIOMEDICAL,
                    observation_type=ObservationType.CORRELATION,
                    known_mechanisms=[],
                    excluded_explanations=[],
                    explanation_levels=[ExplanationLevel.MOLECULAR],
                    target_hypothesis_count=invalid_count,
                    available_methods=[],
                    timeline="standard",
                )

    def test_empty_explanation_levels_fails(self):
        """Empty explanation levels raises ValueError."""
        long_desc = "A " * 30
        with pytest.raises(ValueError, match="At least one explanation level"):
            HypothesisInput(
                phenomenon_description=long_desc,
                domain=ScientificDomain.BIOMEDICAL,
                observation_type=ObservationType.CORRELATION,
                known_mechanisms=[],
                excluded_explanations=[],
                explanation_levels=[],
                target_hypothesis_count=3,
                available_methods=[],
                timeline="standard",
            )

    def test_valid_hypothesis_counts(self):
        """Valid hypothesis counts (3, 4, 5) succeed."""
        long_desc = "A " * 30
        for valid_count in [3, 4, 5]:
            hypothesis_input = HypothesisInput(
                phenomenon_description=long_desc,
                domain=ScientificDomain.BIOMEDICAL,
                observation_type=ObservationType.CORRELATION,
                known_mechanisms=[],
                excluded_explanations=[],
                explanation_levels=[ExplanationLevel.MOLECULAR],
                target_hypothesis_count=valid_count,
                available_methods=[],
                timeline="standard",
            )
            assert hypothesis_input.target_hypothesis_count == valid_count


# =============================================================================
# validate_input Function Tests
# =============================================================================


class TestValidateInput:
    def test_valid_input_passes(self, valid_input):
        """Valid input returns success."""
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is True
        assert "successfully" in message
        assert result is not None
        assert result.domain == ScientificDomain.BIOMEDICAL

    def test_minimal_valid_input_passes(self, minimal_valid_input):
        """Minimal valid input with defaults passes."""
        is_valid, message, result = validate_input(minimal_valid_input)
        assert is_valid is True
        assert result.timeline == "standard"  # Default value
        assert result.known_mechanisms == []  # Default empty list

    def test_missing_required_field_fails(self, valid_input):
        """Missing required field returns failure."""
        del valid_input["domain"]
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False
        assert "Missing required fields" in message
        assert "domain" in message
        assert result is None

    def test_multiple_missing_fields(self):
        """Multiple missing fields are all reported."""
        is_valid, message, result = validate_input({})
        assert is_valid is False
        assert "phenomenon_description" in message
        assert "domain" in message
        assert result is None

    def test_invalid_domain_fails(self, valid_input):
        """Invalid domain value returns failure."""
        valid_input["domain"] = "invalid_domain"
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False
        assert "Invalid enum value" in message or "Validation error" in message
        assert result is None

    def test_invalid_observation_type_fails(self, valid_input):
        """Invalid observation type returns failure."""
        valid_input["observation_type"] = "not_a_type"
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False
        assert result is None

    def test_invalid_explanation_level_fails(self, valid_input):
        """Invalid explanation level returns failure."""
        valid_input["explanation_levels"] = ["molecular", "quantum"]
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False
        assert result is None

    def test_short_description_fails(self, valid_input):
        """Short phenomenon description returns failure."""
        valid_input["phenomenon_description"] = "Too short"
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False
        assert "50 characters" in message
        assert result is None


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    def test_exactly_50_char_description(self, valid_input):
        """Exactly 50 character description passes."""
        valid_input["phenomenon_description"] = "A" * 50
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is True

    def test_49_char_description_fails(self, valid_input):
        """49 character description fails."""
        valid_input["phenomenon_description"] = "A" * 49
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is False

    def test_all_domains_validate(self, valid_input):
        """All domain enum values validate successfully."""
        for domain in ScientificDomain:
            valid_input["domain"] = domain.value
            is_valid, message, result = validate_input(valid_input)
            assert is_valid is True, f"Domain {domain.value} should validate"

    def test_all_observation_types_validate(self, valid_input):
        """All observation type enum values validate successfully."""
        for obs_type in ObservationType:
            valid_input["observation_type"] = obs_type.value
            is_valid, message, result = validate_input(valid_input)
            assert is_valid is True, f"Type {obs_type.value} should validate"

    def test_multiple_explanation_levels(self, valid_input):
        """Multiple explanation levels validate successfully."""
        valid_input["explanation_levels"] = [
            "molecular",
            "cellular",
            "tissue",
            "organism",
        ]
        is_valid, message, result = validate_input(valid_input)
        assert is_valid is True
        assert len(result.explanation_levels) == 4
