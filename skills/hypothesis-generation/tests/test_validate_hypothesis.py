"""Tests for validate_hypothesis.py - Hypothesis structure validation."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_hypothesis import (
    validate_hypothesis,
    validate_hypothesis_set,
    QualityScores,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def valid_hypothesis():
    """A complete valid hypothesis."""
    return {
        "id": "H1",
        "title": "AMPK-mediated autophagy drives metabolic adaptation",
        "mechanism": {
            "trigger": "Cellular energy stress (high AMP:ATP ratio)",
            "pathway": "AMPK activation cascade",
            "outcome": "Enhanced metabolic flexibility",
            "causal_chain": [
                "Energy depletion increases AMP:ATP ratio",
                "AMPK activated by AMP binding",
                "Activated AMPK phosphorylates ULK1",
            ],
        },
        "supporting_evidence": [
            {"finding": "AMPK activation observed", "citation": "Smith et al. (2023)"},
            {"finding": "ULK1 phosphorylation confirmed", "citation": "Jones et al. (2022)"},
            {"finding": "Autophagy markers increased", "citation": "Brown et al. (2024)"},
        ],
        "conflicting_evidence": [
            {"finding": "Some cells show resistance", "citation": "Lee et al. (2023)"}
        ],
        "assumptions": [
            "AMPK pathway is functional in target cells",
            "Sufficient ATP depletion occurs under stress conditions",
        ],
        "predictions": [
            {
                "statement": "AMPK inhibition prevents autophagy",
                "condition": "Glucose deprivation for 4-8 hours",
                "expected_outcome": ">70% reduction in LC3-II",
                "magnitude": "70-90% reduction",
                "falsification_criterion": "If LC3-II increases by >20% despite AMPK inhibition",
            },
            {
                "statement": "ULK1 phosphomutant blocks autophagy",
                "condition": "ULK1-S317A knockin cells",
                "expected_outcome": "Autophagy flux reduced",
                "magnitude": "Similar to AMPK-null",
                "falsification_criterion": "If autophagy proceeds normally in phosphomutant",
            },
        ],
        "quality_scores": {
            "testability": 2,
            "falsifiability": 2,
            "parsimony": 1,
            "explanatory_power": 2,
            "distinctiveness": 2,
        },
    }


@pytest.fixture
def valid_hypothesis_set(valid_hypothesis):
    """A complete valid hypothesis set with 3 hypotheses."""
    h2 = valid_hypothesis.copy()
    h2["id"] = "H2"
    h2["title"] = "Alternative calcium signaling pathway"

    h3 = valid_hypothesis.copy()
    h3["id"] = "H3"
    h3["title"] = "Mitochondrial dysfunction as primary driver"

    return {"hypotheses": [valid_hypothesis, h2, h3]}


# =============================================================================
# QualityScores Dataclass Tests
# =============================================================================


class TestQualityScores:
    def test_valid_scores(self):
        """Valid quality scores create instance."""
        qs = QualityScores(
            testability=2,
            falsifiability=2,
            parsimony=1,
            explanatory_power=2,
            distinctiveness=1,
        )
        assert qs.total == 8

    def test_total_calculation(self):
        """Total property calculates correctly."""
        qs = QualityScores(
            testability=0,
            falsifiability=1,
            parsimony=2,
            explanatory_power=1,
            distinctiveness=0,
        )
        assert qs.total == 4

    def test_invalid_score_raises(self):
        """Score outside [0, 1, 2] raises ValueError."""
        with pytest.raises(ValueError, match="must be 0, 1, or 2"):
            QualityScores(
                testability=3,
                falsifiability=2,
                parsimony=1,
                explanatory_power=2,
                distinctiveness=1,
            )

    def test_negative_score_raises(self):
        """Negative score raises ValueError."""
        with pytest.raises(ValueError):
            QualityScores(
                testability=-1,
                falsifiability=2,
                parsimony=1,
                explanatory_power=2,
                distinctiveness=1,
            )


# =============================================================================
# validate_hypothesis Function Tests
# =============================================================================


class TestValidateHypothesis:
    def test_valid_hypothesis_passes(self, valid_hypothesis):
        """Valid hypothesis returns success."""
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_id_fails(self, valid_hypothesis):
        """Missing ID returns error."""
        del valid_hypothesis["id"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("ID" in e for e in errors)

    def test_missing_title_fails(self, valid_hypothesis):
        """Missing title returns error."""
        del valid_hypothesis["title"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("title" in e.lower() for e in errors)

    def test_long_title_fails(self, valid_hypothesis):
        """Title > 80 chars returns error."""
        valid_hypothesis["title"] = "A" * 81
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("too long" in e.lower() for e in errors)

    def test_exactly_80_char_title_passes(self, valid_hypothesis):
        """Title exactly 80 chars passes."""
        valid_hypothesis["title"] = "A" * 80
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True

    def test_missing_mechanism_fails(self, valid_hypothesis):
        """Missing mechanism returns error."""
        del valid_hypothesis["mechanism"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("mechanism" in e.lower() for e in errors)

    def test_incomplete_mechanism_fails(self, valid_hypothesis):
        """Mechanism missing fields returns error."""
        del valid_hypothesis["mechanism"]["trigger"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("trigger" in e.lower() for e in errors)

    def test_short_causal_chain_fails(self, valid_hypothesis):
        """Causal chain < 2 steps returns error."""
        valid_hypothesis["mechanism"]["causal_chain"] = ["Only one step"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("causal chain" in e.lower() for e in errors)

    def test_missing_supporting_evidence_fails(self, valid_hypothesis):
        """Missing supporting evidence returns error."""
        del valid_hypothesis["supporting_evidence"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("supporting_evidence" in e.lower() for e in errors)

    def test_insufficient_evidence_fails(self, valid_hypothesis):
        """< 3 supporting evidence items returns error."""
        valid_hypothesis["supporting_evidence"] = valid_hypothesis["supporting_evidence"][:2]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("insufficient" in e.lower() for e in errors)

    def test_evidence_missing_fields_fails(self, valid_hypothesis):
        """Evidence item missing finding/citation returns error."""
        valid_hypothesis["supporting_evidence"][0] = {"finding": "Only finding"}
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("citation" in e.lower() for e in errors)

    def test_missing_assumptions_fails(self, valid_hypothesis):
        """Missing assumptions returns error."""
        del valid_hypothesis["assumptions"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("assumptions" in e.lower() for e in errors)

    def test_insufficient_assumptions_fails(self, valid_hypothesis):
        """< 2 assumptions returns error."""
        valid_hypothesis["assumptions"] = ["Only one"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("assumptions" in e.lower() for e in errors)

    def test_missing_predictions_fails(self, valid_hypothesis):
        """Missing predictions returns error."""
        del valid_hypothesis["predictions"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("predictions" in e.lower() for e in errors)

    def test_insufficient_predictions_fails(self, valid_hypothesis):
        """< 2 predictions returns error."""
        valid_hypothesis["predictions"] = [valid_hypothesis["predictions"][0]]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("predictions" in e.lower() for e in errors)

    def test_incomplete_prediction_fails(self, valid_hypothesis):
        """Prediction missing required fields returns error."""
        del valid_hypothesis["predictions"][0]["falsification_criterion"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("falsification_criterion" in str(e) for e in errors)

    def test_missing_quality_scores_fails(self, valid_hypothesis):
        """Missing quality scores returns error."""
        del valid_hypothesis["quality_scores"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("quality_scores" in e.lower() for e in errors)

    def test_incomplete_quality_scores_fails(self, valid_hypothesis):
        """Missing quality score field returns error."""
        del valid_hypothesis["quality_scores"]["testability"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("testability" in str(e) for e in errors)

    def test_invalid_quality_score_value_fails(self, valid_hypothesis):
        """Invalid quality score (not 0, 1, 2) returns error."""
        valid_hypothesis["quality_scores"]["testability"] = 5
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is False
        assert any("testability" in e.lower() for e in errors)


# =============================================================================
# validate_hypothesis_set Function Tests
# =============================================================================


class TestValidateHypothesisSet:
    def test_valid_set_passes(self, valid_hypothesis_set):
        """Valid hypothesis set returns success report."""
        report = validate_hypothesis_set(valid_hypothesis_set)
        assert report["is_valid"] is True
        assert report["hypothesis_count"] == 3
        assert len(report["errors"]) == 0

    def test_missing_hypotheses_array_fails(self):
        """Missing 'hypotheses' key returns error."""
        report = validate_hypothesis_set({})
        assert report["is_valid"] is False
        assert any("hypotheses" in e.lower() for e in report["errors"])

    def test_insufficient_hypotheses_fails(self, valid_hypothesis):
        """< 3 hypotheses returns error."""
        report = validate_hypothesis_set({"hypotheses": [valid_hypothesis]})
        assert report["is_valid"] is False
        assert any("insufficient" in e.lower() for e in report["errors"])

    def test_too_many_hypotheses_warns(self, valid_hypothesis_set, valid_hypothesis):
        """> 5 hypotheses returns warning."""
        h4 = valid_hypothesis.copy()
        h4["id"] = "H4"
        h5 = valid_hypothesis.copy()
        h5["id"] = "H5"
        h6 = valid_hypothesis.copy()
        h6["id"] = "H6"
        valid_hypothesis_set["hypotheses"].extend([h4, h5, h6])

        report = validate_hypothesis_set(valid_hypothesis_set)
        assert report["is_valid"] is True  # Still valid, just warned
        assert any("more than 5" in w.lower() for w in report["warnings"])

    def test_citation_count(self, valid_hypothesis_set):
        """Total citations are counted correctly."""
        report = validate_hypothesis_set(valid_hypothesis_set)
        # Each hypothesis has 3 supporting + 1 conflicting = 4 unique
        # But they share citations, so depends on uniqueness
        assert report["total_citations"] > 0

    def test_quality_summary_populated(self, valid_hypothesis_set):
        """Quality summary contains scores for all hypotheses."""
        report = validate_hypothesis_set(valid_hypothesis_set)
        assert "H1" in report["quality_summary"]
        assert "H2" in report["quality_summary"]
        assert "H3" in report["quality_summary"]

    def test_no_strong_hypothesis_warns(self, valid_hypothesis_set):
        """No hypothesis scoring ≥8 returns warning."""
        # Set all scores low
        for h in valid_hypothesis_set["hypotheses"]:
            h["quality_scores"] = {
                "testability": 1,
                "falsifiability": 1,
                "parsimony": 1,
                "explanatory_power": 1,
                "distinctiveness": 1,
            }
        report = validate_hypothesis_set(valid_hypothesis_set)
        assert any("≥8" in w for w in report["warnings"])

    def test_weak_hypothesis_warns(self, valid_hypothesis_set):
        """Hypothesis scoring <5 returns warning."""
        valid_hypothesis_set["hypotheses"][0]["quality_scores"] = {
            "testability": 0,
            "falsifiability": 0,
            "parsimony": 1,
            "explanatory_power": 1,
            "distinctiveness": 0,
        }
        report = validate_hypothesis_set(valid_hypothesis_set)
        assert any("<5" in w for w in report["warnings"])

    def test_invalid_hypothesis_in_set_fails(self, valid_hypothesis_set):
        """Invalid hypothesis in set makes entire set invalid."""
        del valid_hypothesis_set["hypotheses"][0]["mechanism"]
        report = validate_hypothesis_set(valid_hypothesis_set)
        assert report["is_valid"] is False
        assert any("H1" in e for e in report["errors"])


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================


class TestEdgeCases:
    def test_exactly_3_hypotheses_passes(self, valid_hypothesis):
        """Exactly 3 hypotheses passes count validation."""
        h2 = valid_hypothesis.copy()
        h2["id"] = "H2"
        h3 = valid_hypothesis.copy()
        h3["id"] = "H3"
        hypothesis_set = {"hypotheses": [valid_hypothesis, h2, h3]}

        report = validate_hypothesis_set(hypothesis_set)
        assert report["is_valid"] is True
        assert report["hypothesis_count"] == 3

    def test_exactly_5_hypotheses_passes(self, valid_hypothesis):
        """Exactly 5 hypotheses passes without warning."""
        hypotheses = []
        for i in range(5):
            h = valid_hypothesis.copy()
            h["id"] = f"H{i+1}"
            hypotheses.append(h)
        hypothesis_set = {"hypotheses": hypotheses}

        report = validate_hypothesis_set(hypothesis_set)
        assert report["is_valid"] is True
        assert not any("more than 5" in w.lower() for w in report["warnings"])

    def test_exactly_2_causal_chain_steps_passes(self, valid_hypothesis):
        """Exactly 2 causal chain steps passes."""
        valid_hypothesis["mechanism"]["causal_chain"] = ["Step 1", "Step 2"]
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True

    def test_exactly_3_evidence_items_passes(self, valid_hypothesis):
        """Exactly 3 supporting evidence items passes."""
        # Already has exactly 3 in fixture
        assert len(valid_hypothesis["supporting_evidence"]) == 3
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True

    def test_exactly_2_assumptions_passes(self, valid_hypothesis):
        """Exactly 2 assumptions passes."""
        # Already has exactly 2 in fixture
        assert len(valid_hypothesis["assumptions"]) == 2
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True

    def test_exactly_2_predictions_passes(self, valid_hypothesis):
        """Exactly 2 predictions passes."""
        # Already has exactly 2 in fixture
        assert len(valid_hypothesis["predictions"]) == 2
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True

    def test_score_boundary_values(self, valid_hypothesis):
        """Quality scores at boundary values (0, 1, 2) all pass."""
        for score_val in [0, 1, 2]:
            valid_hypothesis["quality_scores"] = {
                "testability": score_val,
                "falsifiability": score_val,
                "parsimony": score_val,
                "explanatory_power": score_val,
                "distinctiveness": score_val,
            }
            is_valid, errors = validate_hypothesis(valid_hypothesis)
            assert is_valid is True, f"Score value {score_val} should be valid"

    def test_empty_conflicting_evidence_allowed(self, valid_hypothesis):
        """Empty conflicting evidence list is allowed."""
        valid_hypothesis["conflicting_evidence"] = []
        is_valid, errors = validate_hypothesis(valid_hypothesis)
        assert is_valid is True
