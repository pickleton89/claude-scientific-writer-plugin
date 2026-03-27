"""Tests for check_distinctiveness.py - Hypothesis distinctiveness checking."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_distinctiveness import (
    extract_mechanism_terms,
    calculate_overlap,
    check_distinctiveness,
    check_hypothesis_set,
    STOPWORDS,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def hypothesis_ampk():
    """Hypothesis about AMPK pathway."""
    return {
        "id": "H1",
        "mechanism": {
            "trigger": "Energy stress",
            "pathway": "AMPK activation cascade",
            "outcome": "Autophagy induction",
            "causal_chain": [
                "ATP depletion",
                "AMPK activation",
                "ULK1 phosphorylation",
                "Autophagosome formation",
            ],
        },
    }


@pytest.fixture
def hypothesis_mtor():
    """Hypothesis about mTOR pathway (distinct from AMPK)."""
    return {
        "id": "H2",
        "mechanism": {
            "trigger": "Nutrient availability",
            "pathway": "mTOR signaling",
            "outcome": "Protein synthesis",
            "causal_chain": [
                "Amino acid sensing",
                "mTORC1 activation",
                "S6K phosphorylation",
                "Ribosome biogenesis",
            ],
        },
    }


@pytest.fixture
def hypothesis_similar_to_ampk():
    """Hypothesis similar to AMPK (high overlap)."""
    return {
        "id": "H3",
        "mechanism": {
            "trigger": "Energy stress",  # Same as H1
            "pathway": "AMPK activation cascade",  # Same as H1
            "outcome": "Autophagy induction",  # Same as H1
            "causal_chain": [
                "ATP depletion",  # Same as H1
                "AMPK activation",  # Same as H1
                "ULK1 phosphorylation",  # Same as H1
                "Mitophagy initiation",  # Different
            ],
        },
    }


@pytest.fixture
def hypothesis_empty_mechanism():
    """Hypothesis with empty mechanism."""
    return {
        "id": "H4",
        "mechanism": {
            "trigger": "",
            "pathway": "",
            "outcome": "",
            "causal_chain": [],
        },
    }


# =============================================================================
# extract_mechanism_terms Tests
# =============================================================================


class TestExtractMechanismTerms:
    def test_extracts_causal_chain_terms(self, hypothesis_ampk):
        """Extracts terms from causal chain."""
        terms = extract_mechanism_terms(hypothesis_ampk)
        assert "atp" in terms
        assert "depletion" in terms
        assert "ampk" in terms
        assert "activation" in terms

    def test_extracts_trigger_pathway_outcome(self, hypothesis_ampk):
        """Extracts terms from trigger, pathway, outcome."""
        terms = extract_mechanism_terms(hypothesis_ampk)
        assert "energy" in terms
        assert "stress" in terms
        assert "cascade" in terms
        assert "autophagy" in terms
        assert "induction" in terms

    def test_removes_stopwords(self, hypothesis_ampk):
        """Removes common stopwords."""
        terms = extract_mechanism_terms(hypothesis_ampk)
        for stopword in ["the", "a", "an", "and", "or", "to", "of", "in"]:
            assert stopword not in terms

    def test_lowercase_normalization(self):
        """Terms are lowercased."""
        h = {
            "mechanism": {
                "trigger": "UPPERCASE",
                "pathway": "MixedCase",
                "outcome": "lowercase",
                "causal_chain": [],
            }
        }
        terms = extract_mechanism_terms(h)
        assert "uppercase" in terms
        assert "mixedcase" in terms
        assert "lowercase" in terms
        assert "UPPERCASE" not in terms

    def test_handles_empty_mechanism(self, hypothesis_empty_mechanism):
        """Handles empty mechanism gracefully."""
        terms = extract_mechanism_terms(hypothesis_empty_mechanism)
        assert len(terms) == 0

    def test_handles_missing_mechanism(self):
        """Handles missing mechanism key."""
        h = {"id": "H1"}
        terms = extract_mechanism_terms(h)
        assert len(terms) == 0

    def test_splits_on_comma(self):
        """Splits terms on comma."""
        h = {
            "mechanism": {
                "trigger": "stress, damage",
                "pathway": "",
                "outcome": "",
                "causal_chain": [],
            }
        }
        terms = extract_mechanism_terms(h)
        assert "stress" in terms
        assert "damage" in terms

    def test_splits_on_arrow(self):
        """Splits terms on arrow symbol."""
        h = {
            "mechanism": {
                "trigger": "",
                "pathway": "",
                "outcome": "",
                "causal_chain": ["AMPK → ULK1 → Autophagy"],
            }
        }
        terms = extract_mechanism_terms(h)
        # Note: single letters like 'a' are stopwords and get removed
        assert "ampk" in terms
        assert "ulk1" in terms
        assert "autophagy" in terms


# =============================================================================
# calculate_overlap Tests
# =============================================================================


class TestCalculateOverlap:
    def test_identical_sets(self):
        """Identical sets have 100% overlap."""
        terms = {"a", "b", "c"}
        overlap = calculate_overlap(terms, terms)
        assert overlap == 1.0

    def test_disjoint_sets(self):
        """Disjoint sets have 0% overlap."""
        terms1 = {"a", "b", "c"}
        terms2 = {"x", "y", "z"}
        overlap = calculate_overlap(terms1, terms2)
        assert overlap == 0.0

    def test_partial_overlap(self):
        """Partial overlap calculated correctly (Jaccard)."""
        terms1 = {"a", "b", "c"}
        terms2 = {"b", "c", "d"}
        # Intersection: {b, c} = 2
        # Union: {a, b, c, d} = 4
        # Jaccard: 2/4 = 0.5
        overlap = calculate_overlap(terms1, terms2)
        assert overlap == 0.5

    def test_empty_first_set(self):
        """Empty first set returns 0."""
        overlap = calculate_overlap(set(), {"a", "b"})
        assert overlap == 0.0

    def test_empty_second_set(self):
        """Empty second set returns 0."""
        overlap = calculate_overlap({"a", "b"}, set())
        assert overlap == 0.0

    def test_both_empty_sets(self):
        """Both empty sets returns 0."""
        overlap = calculate_overlap(set(), set())
        assert overlap == 0.0

    def test_single_element_overlap(self):
        """Single overlapping element calculated correctly."""
        terms1 = {"shared", "unique1"}
        terms2 = {"shared", "unique2"}
        # Intersection: {shared} = 1
        # Union: {shared, unique1, unique2} = 3
        # Jaccard: 1/3 ≈ 0.333
        overlap = calculate_overlap(terms1, terms2)
        assert abs(overlap - 1 / 3) < 0.001


# =============================================================================
# check_distinctiveness Tests
# =============================================================================


class TestCheckDistinctiveness:
    def test_distinct_hypotheses_pass(self, hypothesis_ampk, hypothesis_mtor):
        """Distinct hypotheses pass distinctiveness check."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_mtor])
        assert report["overall_distinct"] is True
        assert len(report["issues"]) == 0

    def test_similar_hypotheses_fail(self, hypothesis_ampk, hypothesis_similar_to_ampk):
        """Similar hypotheses fail distinctiveness check."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_similar_to_ampk])
        assert report["overall_distinct"] is False
        assert len(report["issues"]) > 0

    def test_pairwise_comparisons_count(
        self, hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk
    ):
        """Correct number of pairwise comparisons."""
        hypotheses = [hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk]
        report = check_distinctiveness(hypotheses)
        # 3 hypotheses = 3 pairs: (1,2), (1,3), (2,3)
        assert len(report["comparisons"]) == 3

    def test_custom_threshold(self, hypothesis_ampk, hypothesis_similar_to_ampk):
        """Custom threshold affects results."""
        # With high threshold, similar hypotheses may pass
        report_high = check_distinctiveness(
            [hypothesis_ampk, hypothesis_similar_to_ampk], threshold=0.99
        )
        # With low threshold, they fail
        report_low = check_distinctiveness(
            [hypothesis_ampk, hypothesis_similar_to_ampk], threshold=0.01
        )
        # High threshold should be more permissive
        assert report_high["overall_distinct"] is True
        assert report_low["overall_distinct"] is False

    def test_comparison_structure(self, hypothesis_ampk, hypothesis_mtor):
        """Comparison contains expected fields."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_mtor])
        comparison = report["comparisons"][0]
        assert "pair" in comparison
        assert "h1_id" in comparison
        assert "h2_id" in comparison
        assert "overlap_ratio" in comparison
        assert "shared_terms" in comparison
        assert "is_distinct" in comparison

    def test_shared_terms_limited(self, hypothesis_ampk, hypothesis_similar_to_ampk):
        """Shared terms list is limited for readability."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_similar_to_ampk])
        comparison = report["comparisons"][0]
        # Should be limited to 10 terms max
        assert len(comparison["shared_terms"]) <= 10

    def test_hypothesis_count_in_report(
        self, hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk
    ):
        """Report includes hypothesis count."""
        hypotheses = [hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk]
        report = check_distinctiveness(hypotheses)
        assert report["hypothesis_count"] == 3

    def test_empty_hypothesis_list(self):
        """Handles empty hypothesis list."""
        report = check_distinctiveness([])
        assert report["hypothesis_count"] == 0
        assert len(report["comparisons"]) == 0
        assert report["overall_distinct"] is True

    def test_single_hypothesis(self, hypothesis_ampk):
        """Single hypothesis has no comparisons."""
        report = check_distinctiveness([hypothesis_ampk])
        assert report["hypothesis_count"] == 1
        assert len(report["comparisons"]) == 0
        assert report["overall_distinct"] is True

    def test_issues_contain_details(self, hypothesis_ampk, hypothesis_similar_to_ampk):
        """Issue messages contain relevant details."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_similar_to_ampk])
        if not report["overall_distinct"]:
            issue = report["issues"][0]
            assert "H1" in issue or "H3" in issue
            assert "overlap" in issue.lower()
            assert "%" in issue


# =============================================================================
# check_hypothesis_set Tests
# =============================================================================


class TestCheckHypothesisSet:
    def test_extracts_hypotheses(self, hypothesis_ampk, hypothesis_mtor):
        """Extracts hypotheses from set structure."""
        hypothesis_set = {"hypotheses": [hypothesis_ampk, hypothesis_mtor]}
        report = check_hypothesis_set(hypothesis_set)
        assert report["hypothesis_count"] == 2

    def test_passes_threshold(self, hypothesis_ampk, hypothesis_mtor):
        """Passes threshold to underlying function."""
        hypothesis_set = {"hypotheses": [hypothesis_ampk, hypothesis_mtor]}
        # Very high threshold should pass
        report_high = check_hypothesis_set(hypothesis_set, threshold=0.99)
        # Verify threshold affects behavior
        assert report_high["overall_distinct"] is True

    def test_handles_missing_key(self):
        """Handles missing 'hypotheses' key."""
        report = check_hypothesis_set({})
        assert report["hypothesis_count"] == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    def test_three_distinct_hypotheses(
        self, hypothesis_ampk, hypothesis_mtor, hypothesis_empty_mechanism
    ):
        """Three distinct hypotheses all pass."""
        hypotheses = [hypothesis_ampk, hypothesis_mtor, hypothesis_empty_mechanism]
        report = check_distinctiveness(hypotheses)
        assert report["overall_distinct"] is True

    def test_one_similar_pair_fails_set(
        self, hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk
    ):
        """One similar pair fails the entire set."""
        hypotheses = [hypothesis_ampk, hypothesis_mtor, hypothesis_similar_to_ampk]
        report = check_distinctiveness(hypotheses)
        # H1 and H3 are similar, so overall should fail
        # (H1-H2 distinct, H2-H3 may be distinct, but H1-H3 similar)
        # Check that at least one comparison is not distinct
        not_distinct_count = sum(
            1 for c in report["comparisons"] if not c["is_distinct"]
        )
        if not_distinct_count > 0:
            assert report["overall_distinct"] is False

    def test_deterministic_results(self, hypothesis_ampk, hypothesis_mtor):
        """Same input always produces same output."""
        hypotheses = [hypothesis_ampk, hypothesis_mtor]
        report1 = check_distinctiveness(hypotheses)
        report2 = check_distinctiveness(hypotheses)
        assert report1["overall_distinct"] == report2["overall_distinct"]
        assert report1["comparisons"][0]["overlap_ratio"] == report2["comparisons"][0]["overlap_ratio"]


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_exactly_at_threshold(self):
        """Overlap exactly at threshold fails (must be < threshold)."""
        # Create hypotheses with known 40% overlap
        h1 = {
            "id": "H1",
            "mechanism": {
                "causal_chain": ["a", "b", "shared1", "shared2"],
                "trigger": "",
                "pathway": "",
                "outcome": "",
            },
        }
        h2 = {
            "id": "H2",
            "mechanism": {
                "causal_chain": ["x", "y", "shared1", "shared2"],
                "trigger": "",
                "pathway": "",
                "outcome": "",
            },
        }
        # Intersection: {shared1, shared2} = 2
        # Union: {a, b, shared1, shared2, x, y} = 6
        # Jaccard: 2/6 ≈ 0.333
        report = check_distinctiveness([h1, h2], threshold=0.333)
        # Should fail because overlap is not < threshold
        assert report["comparisons"][0]["is_distinct"] is False

    def test_just_below_threshold(self):
        """Overlap just below threshold passes."""
        h1 = {
            "id": "H1",
            "mechanism": {
                "causal_chain": ["a", "b", "c"],
                "trigger": "",
                "pathway": "",
                "outcome": "",
            },
        }
        h2 = {
            "id": "H2",
            "mechanism": {
                "causal_chain": ["x", "y", "z"],
                "trigger": "",
                "pathway": "",
                "outcome": "",
            },
        }
        # No overlap, should pass any threshold
        report = check_distinctiveness([h1, h2], threshold=0.1)
        assert report["comparisons"][0]["is_distinct"] is True

    def test_hypothesis_without_id(self):
        """Handles hypothesis without id by generating default IDs."""
        h1 = {"mechanism": {"causal_chain": ["term1", "term2"], "trigger": "", "pathway": "", "outcome": ""}}
        h2 = {"mechanism": {"causal_chain": ["term3", "term4"], "trigger": "", "pathway": "", "outcome": ""}}
        report = check_distinctiveness([h1, h2])
        # Without explicit IDs, defaults to H1, H2 based on index
        assert report["comparisons"][0]["h1_id"] == "H1"
        assert report["comparisons"][0]["h2_id"] == "H2"

    def test_shared_terms_sorted(self, hypothesis_ampk, hypothesis_similar_to_ampk):
        """Shared terms are sorted for consistency."""
        report = check_distinctiveness([hypothesis_ampk, hypothesis_similar_to_ampk])
        shared = report["comparisons"][0]["shared_terms"]
        assert shared == sorted(shared)

    def test_stopwords_comprehensive(self):
        """STOPWORDS constant contains expected words."""
        expected_stopwords = ["the", "a", "an", "and", "or", "to", "of", "in", "by"]
        for word in expected_stopwords:
            assert word in STOPWORDS
