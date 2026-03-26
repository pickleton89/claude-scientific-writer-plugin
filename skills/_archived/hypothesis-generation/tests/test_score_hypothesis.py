"""Tests for score_hypothesis.py - Automated quality scoring."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from score_hypothesis import (
    score_testability,
    score_falsifiability,
    score_parsimony,
    score_explanatory_power,
    score_distinctiveness,
    assess_hypothesis,
    assess_hypothesis_set,
    QualityAssessment,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def strong_hypothesis():
    """A hypothesis that should score high on automated criteria."""
    return {
        "id": "H1",
        "title": "AMPK-mediated autophagy",
        "mechanism": {
            "trigger": "Energy stress",
            "pathway": "AMPK activation",
            "outcome": "Autophagy induction",
            "causal_chain": [
                "Energy depletion",
                "AMPK activation",
                "ULK1 phosphorylation",
            ],
        },
        "predictions": [
            {
                "statement": "AMPK inhibition prevents autophagy",
                "condition": "Glucose deprivation for 4 hours",
                "expected_outcome": ">70% reduction in LC3-II",
                "magnitude": "70-90% reduction",
                "falsification_criterion": "If LC3-II increases by >20% despite AMPK inhibition, hypothesis is falsified",
            },
            {
                "statement": "ULK1 phosphomutant blocks autophagy",
                "condition": "ULK1-S317A knockin cells",
                "expected_outcome": "Autophagy flux reduced to baseline",
                "magnitude": "Similar to AMPK-null phenotype",
                "falsification_criterion": "If autophagy proceeds normally in phosphomutant cells, hypothesis is falsified",
            },
        ],
        "assumptions": ["AMPK pathway is functional", "ATP depletion occurs"],
        "quality_scores": {
            "testability": 2,
            "falsifiability": 2,
            "parsimony": 2,
            "explanatory_power": 2,
            "distinctiveness": 1,
        },
    }


@pytest.fixture
def weak_hypothesis():
    """A hypothesis that should score low on automated criteria."""
    return {
        "id": "H2",
        "title": "Multiple factors contribute",
        "mechanism": {
            "trigger": "Various stresses",
            "pathway": "Complex interactions",
            "outcome": "Phenotype changes",
            "causal_chain": [
                "Step 1",
                "Step 2",
                "Step 3",
                "Step 4",
                "Step 5",
                "Step 6",
            ],
        },
        "predictions": [
            {
                "statement": "Something may change",
                "condition": "Under certain conditions",
                "expected_outcome": "Some effect",
                "magnitude": None,
                "falsification_criterion": None,
            }
        ],
        "assumptions": [
            "Assumption 1",
            "Assumption 2",
            "Assumption 3",
            "Assumption 4",
            "Assumption 5",
            "Assumption 6",
        ],
        "quality_scores": {
            "testability": 0,
            "falsifiability": 0,
            "parsimony": 0,
            "explanatory_power": 1,
            "distinctiveness": 0,
        },
    }


@pytest.fixture
def moderate_hypothesis():
    """A hypothesis with moderate scores."""
    return {
        "id": "H3",
        "title": "Moderate complexity hypothesis",
        "mechanism": {
            "trigger": "Oxidative stress",
            "pathway": "ROS signaling",
            "outcome": "Cell adaptation",
            "causal_chain": [
                "ROS production",
                "Nrf2 activation",
                "Antioxidant response",
                "Cell protection",
            ],
        },
        "predictions": [
            {
                "statement": "Nrf2 activation protects cells",
                "condition": "H2O2 treatment",
                "expected_outcome": "Reduced cell death",
                "magnitude": None,
                "falsification_criterion": "If Nrf2 knockdown has no effect",
            },
            {
                "statement": "Antioxidants are upregulated",
                "condition": "Stress conditions",
                "expected_outcome": "Increased expression",
                "magnitude": None,
                "falsification_criterion": None,
            },
        ],
        "assumptions": [
            "ROS levels increase",
            "Nrf2 is expressed",
            "Antioxidant genes are functional",
            "Cells can adapt",
        ],
        "quality_scores": {
            "testability": 1,
            "falsifiability": 1,
            "parsimony": 1,
            "explanatory_power": 1,
            "distinctiveness": 1,
        },
    }


# =============================================================================
# score_testability Tests
# =============================================================================


class TestScoreTestability:
    def test_strong_testability(self, strong_hypothesis):
        """Hypothesis with quantifiable predictions scores 2."""
        score, note = score_testability(strong_hypothesis)
        assert score == 2
        assert "Strong" in note

    def test_no_predictions_scores_zero(self):
        """Hypothesis with no predictions scores 0."""
        h = {"predictions": []}
        score, note = score_testability(h)
        assert score == 0
        assert "No predictions" in note

    def test_missing_predictions_scores_zero(self):
        """Hypothesis missing predictions key scores 0."""
        h = {}
        score, note = score_testability(h)
        assert score == 0

    def test_predictions_without_magnitude(self, moderate_hypothesis):
        """Predictions without magnitude score lower."""
        score, note = score_testability(moderate_hypothesis)
        assert score == 1  # Has outcomes but no magnitude

    def test_predictions_with_outcomes_only(self):
        """Predictions with only expected_outcome score 1."""
        h = {
            "predictions": [
                {"expected_outcome": "Some outcome"},
            ]
        }
        score, note = score_testability(h)
        assert score == 1

    def test_predictions_without_outcomes(self):
        """Predictions without expected_outcome score 0."""
        h = {
            "predictions": [
                {"statement": "Something happens"},
            ]
        }
        score, note = score_testability(h)
        assert score == 0


# =============================================================================
# score_falsifiability Tests
# =============================================================================


class TestScoreFalsifiability:
    def test_strong_falsifiability(self, strong_hypothesis):
        """Hypothesis with clear falsification criteria scores 2."""
        score, note = score_falsifiability(strong_hypothesis)
        assert score == 2
        assert "Strong" in note

    def test_no_predictions_scores_zero(self):
        """No predictions means no falsifiability."""
        h = {"predictions": []}
        score, note = score_falsifiability(h)
        assert score == 0

    def test_short_falsification_criteria(self):
        """Short falsification criteria don't count."""
        h = {
            "predictions": [
                {"falsification_criterion": "If wrong"},  # Too short (< 20 chars)
                {"falsification_criterion": "Nope"},
            ]
        }
        score, note = score_falsifiability(h)
        assert score == 0
        assert "Weak" in note

    def test_one_good_criterion_scores_one(self):
        """One good falsification criterion scores 1."""
        h = {
            "predictions": [
                {
                    "falsification_criterion": "If the predicted effect is not observed under controlled conditions"
                },
                {"falsification_criterion": None},
            ]
        }
        score, note = score_falsifiability(h)
        assert score == 1
        assert "Moderate" in note

    def test_two_good_criteria_scores_two(self):
        """Two good falsification criteria scores 2."""
        h = {
            "predictions": [
                {
                    "falsification_criterion": "If the predicted effect is not observed under controlled conditions"
                },
                {
                    "falsification_criterion": "If the alternative explanation better fits the data observed"
                },
            ]
        }
        score, note = score_falsifiability(h)
        assert score == 2


# =============================================================================
# score_parsimony Tests
# =============================================================================


class TestScoreParsimony:
    def test_simple_mechanism_scores_two(self):
        """Simple mechanism (≤3 steps, ≤3 assumptions) scores 2."""
        h = {
            "mechanism": {"causal_chain": ["Step 1", "Step 2", "Step 3"]},
            "assumptions": ["A1", "A2", "A3"],
        }
        score, note = score_parsimony(h)
        assert score == 2
        assert "Simple" in note

    def test_moderate_mechanism_scores_one(self):
        """Moderate mechanism (4-5 steps or assumptions) scores 1."""
        h = {
            "mechanism": {"causal_chain": ["S1", "S2", "S3", "S4", "S5"]},
            "assumptions": ["A1", "A2", "A3"],
        }
        score, note = score_parsimony(h)
        assert score == 1
        assert "Moderate" in note

    def test_complex_mechanism_scores_zero(self, weak_hypothesis):
        """Complex mechanism (>5 steps or assumptions) scores 0."""
        score, note = score_parsimony(weak_hypothesis)
        assert score == 0
        assert "Complex" in note

    def test_missing_mechanism_scores_two(self):
        """Missing mechanism defaults to simple (0 steps)."""
        h = {"assumptions": []}
        score, note = score_parsimony(h)
        assert score == 2

    def test_empty_causal_chain_scores_two(self):
        """Empty causal chain scores 2 (simple)."""
        h = {"mechanism": {"causal_chain": []}, "assumptions": []}
        score, note = score_parsimony(h)
        assert score == 2

    def test_many_assumptions_reduces_score(self):
        """Many assumptions (>5) reduces score even with short chain."""
        h = {
            "mechanism": {"causal_chain": ["Step 1", "Step 2"]},
            "assumptions": ["A1", "A2", "A3", "A4", "A5", "A6"],
        }
        score, note = score_parsimony(h)
        assert score == 0


# =============================================================================
# score_explanatory_power Tests
# =============================================================================


class TestScoreExplanatoryPower:
    def test_returns_none_for_llm_review(self):
        """Explanatory power always requires LLM review."""
        h = {}
        score, note = score_explanatory_power(h)
        assert score is None
        assert "LLM review" in note


# =============================================================================
# score_distinctiveness Tests
# =============================================================================


class TestScoreDistinctiveness:
    def test_returns_none_for_llm_review(self, strong_hypothesis, weak_hypothesis):
        """Distinctiveness requires LLM review but provides overlap info."""
        score, note = score_distinctiveness(strong_hypothesis, [weak_hypothesis])
        assert score is None
        assert "LLM review" in note
        assert "overlap" in note.lower()

    def test_no_other_hypotheses(self, strong_hypothesis):
        """With no other hypotheses, still requires review."""
        score, note = score_distinctiveness(strong_hypothesis, [])
        assert score is None
        assert "no other hypotheses" in note.lower()

    def test_overlap_calculation_in_note(self, strong_hypothesis):
        """Overlap percentage is included in note."""
        other = {
            "id": "H2",
            "mechanism": {
                "causal_chain": ["Energy depletion", "AMPK activation", "Different outcome"]
            },
        }
        score, note = score_distinctiveness(strong_hypothesis, [other])
        assert "H2:" in note
        assert "%" in note


# =============================================================================
# assess_hypothesis Tests
# =============================================================================


class TestAssessHypothesis:
    def test_returns_quality_assessment(self, strong_hypothesis):
        """Returns QualityAssessment dataclass."""
        assessment = assess_hypothesis(strong_hypothesis, [strong_hypothesis])
        assert isinstance(assessment, QualityAssessment)
        assert assessment.hypothesis_id == "H1"

    def test_automated_scores_included(self, strong_hypothesis):
        """Testability, falsifiability, parsimony are automated."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        assert "testability" in assessment.automated_scores
        assert "falsifiability" in assessment.automated_scores
        assert "parsimony" in assessment.automated_scores

    def test_llm_scores_flagged(self, strong_hypothesis):
        """Explanatory power and distinctiveness require review."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        assert "explanatory_power" in assessment.requires_review
        assert "distinctiveness" in assessment.requires_review

    def test_total_calculated(self, strong_hypothesis):
        """Total is sum of all scores."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        expected_total = sum(assessment.scores.values())
        assert assessment.total == expected_total

    def test_uses_existing_llm_scores(self, strong_hypothesis):
        """Uses existing quality_scores for LLM-required criteria."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        # Should use the existing explanatory_power from quality_scores
        assert assessment.scores["explanatory_power"] == 2

    def test_notes_populated(self, strong_hypothesis):
        """Notes list is populated with assessment details."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        assert len(assessment.notes) == 5  # One per criterion


# =============================================================================
# assess_hypothesis_set Tests
# =============================================================================


class TestAssessHypothesisSet:
    def test_assesses_all_hypotheses(self, strong_hypothesis, weak_hypothesis):
        """Assesses each hypothesis in the set."""
        hypothesis_set = {"hypotheses": [strong_hypothesis, weak_hypothesis]}
        report = assess_hypothesis_set(hypothesis_set)
        assert report["hypothesis_count"] == 2
        assert len(report["assessments"]) == 2

    def test_summary_statistics(self, strong_hypothesis, weak_hypothesis, moderate_hypothesis):
        """Summary includes counts by category."""
        hypothesis_set = {
            "hypotheses": [strong_hypothesis, weak_hypothesis, moderate_hypothesis]
        }
        report = assess_hypothesis_set(hypothesis_set)
        assert "strong_count" in report["summary"]
        assert "viable_count" in report["summary"]
        assert "weak_count" in report["summary"]

    def test_empty_hypothesis_set(self):
        """Handles empty hypothesis set."""
        report = assess_hypothesis_set({"hypotheses": []})
        assert report["hypothesis_count"] == 0
        assert report["summary"]["max_score"] == 0
        assert report["summary"]["has_strong"] is False

    def test_has_strong_flag(self, strong_hypothesis):
        """has_strong flag is True when max score >= 8."""
        hypothesis_set = {"hypotheses": [strong_hypothesis]}
        report = assess_hypothesis_set(hypothesis_set)
        # Strong hypothesis should score high
        if report["summary"]["max_score"] >= 8:
            assert report["summary"]["has_strong"] is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    def test_strong_hypothesis_scores_high(self, strong_hypothesis):
        """Strong hypothesis gets high automated scores."""
        assessment = assess_hypothesis(strong_hypothesis, [])
        # Automated scores should be high
        assert assessment.scores["testability"] == 2
        assert assessment.scores["falsifiability"] == 2
        assert assessment.scores["parsimony"] == 2

    def test_weak_hypothesis_scores_low(self, weak_hypothesis):
        """Weak hypothesis gets low automated scores."""
        assessment = assess_hypothesis(weak_hypothesis, [])
        assert assessment.scores["testability"] <= 1
        assert assessment.scores["falsifiability"] == 0
        assert assessment.scores["parsimony"] == 0

    def test_assessment_is_deterministic(self, strong_hypothesis):
        """Same input always produces same output."""
        assessment1 = assess_hypothesis(strong_hypothesis, [])
        assessment2 = assess_hypothesis(strong_hypothesis, [])
        assert assessment1.scores == assessment2.scores
        assert assessment1.total == assessment2.total


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_hypothesis_without_id(self):
        """Handles hypothesis without id gracefully."""
        h = {
            "mechanism": {"causal_chain": ["Step 1", "Step 2"]},
            "predictions": [],
            "assumptions": [],
        }
        assessment = assess_hypothesis(h, [])
        assert assessment.hypothesis_id == "?"

    def test_exactly_20_char_falsification(self):
        """Exactly 20 char falsification criterion doesn't count."""
        h = {
            "predictions": [
                {"falsification_criterion": "A" * 20},  # Exactly 20
            ]
        }
        score, note = score_falsifiability(h)
        assert score == 0  # Need > 20

    def test_21_char_falsification(self):
        """21 char falsification criterion counts."""
        h = {
            "predictions": [
                {"falsification_criterion": "A" * 21},
            ]
        }
        score, note = score_falsifiability(h)
        assert score == 1

    def test_exactly_3_causal_steps(self):
        """Exactly 3 causal steps scores 2 (simple)."""
        h = {
            "mechanism": {"causal_chain": ["S1", "S2", "S3"]},
            "assumptions": [],
        }
        score, note = score_parsimony(h)
        assert score == 2

    def test_exactly_4_causal_steps(self):
        """Exactly 4 causal steps scores 1 (moderate)."""
        h = {
            "mechanism": {"causal_chain": ["S1", "S2", "S3", "S4"]},
            "assumptions": [],
        }
        score, note = score_parsimony(h)
        assert score == 1

    def test_exactly_6_causal_steps(self):
        """Exactly 6 causal steps scores 0 (complex)."""
        h = {
            "mechanism": {"causal_chain": ["S1", "S2", "S3", "S4", "S5", "S6"]},
            "assumptions": [],
        }
        score, note = score_parsimony(h)
        assert score == 0
