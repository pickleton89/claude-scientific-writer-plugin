"""Tests for track_citations.py - Citation tracking and validation."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from track_citations import (
    extract_citations_from_hypothesis_set,
    extract_year,
    analyze_citations,
    TOTAL_CITATIONS_MIN,
    TOTAL_CITATIONS_TARGET,
    MAIN_TEXT_CITATIONS_MIN,
    MAIN_TEXT_CITATIONS_TARGET,
    RECENT_PAPERS_MIN_PERCENT,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def hypothesis_with_citations():
    """A hypothesis with citations in various fields."""
    return {
        "id": "H1",
        "supporting_evidence": [
            {"finding": "Finding 1", "citation": "Smith et al. (2023)"},
            {"finding": "Finding 2", "citation": "Jones et al. (2022)"},
            {"finding": "Finding 3", "citation": "Brown et al. (2024)"},
        ],
        "conflicting_evidence": [
            {"finding": "Conflict 1", "citation": "Lee et al. (2021)"}
        ],
        "appendix_evidence": [
            {"finding": "Appendix 1", "citation": "Wilson et al. (2020)"},
            {"finding": "Appendix 2", "citation": "Taylor et al. (2019)"},
        ],
    }


@pytest.fixture
def hypothesis_set_with_many_citations():
    """Hypothesis set meeting citation requirements."""
    hypotheses = []
    for i in range(5):
        h = {
            "id": f"H{i+1}",
            "supporting_evidence": [
                {"finding": f"Finding {j}", "citation": f"Author{i}_{j} et al. (2023)"}
                for j in range(10)
            ],
            "conflicting_evidence": [],
            "appendix_evidence": [],
        }
        hypotheses.append(h)
    return {"hypotheses": hypotheses}


@pytest.fixture
def hypothesis_set_below_threshold():
    """Hypothesis set below citation requirements."""
    return {
        "hypotheses": [
            {
                "id": "H1",
                "supporting_evidence": [
                    {"finding": "F1", "citation": "A et al. (2023)"},
                    {"finding": "F2", "citation": "B et al. (2023)"},
                ],
                "conflicting_evidence": [],
                "appendix_evidence": [],
            }
        ]
    }


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    def test_citation_thresholds_defined(self):
        """Citation threshold constants are properly defined."""
        assert TOTAL_CITATIONS_MIN == 40
        assert TOTAL_CITATIONS_TARGET == 50
        assert MAIN_TEXT_CITATIONS_MIN == 10
        assert MAIN_TEXT_CITATIONS_TARGET == 15
        assert RECENT_PAPERS_MIN_PERCENT == 60


# =============================================================================
# extract_year Function Tests
# =============================================================================


class TestExtractYear:
    def test_parenthetical_year(self):
        """Extracts year from (2023) format."""
        assert extract_year("Smith et al. (2023)") == 2023

    def test_year_with_comma(self):
        """Extracts year from 2023, format."""
        assert extract_year("Smith, 2023, Journal") == 2023

    def test_year_with_period(self):
        """Extracts year from 2023. format."""
        assert extract_year("Smith 2023. Title") == 2023

    def test_et_al_year(self):
        """Extracts year from 'et al. 2023' format."""
        assert extract_year("Smith et al. 2023") == 2023
        assert extract_year("Smith et al 2022") == 2022

    def test_no_year_returns_none(self):
        """Returns None when no year found."""
        assert extract_year("Smith et al., Journal") is None
        assert extract_year("No year here") is None

    def test_invalid_year_returns_none(self):
        """Returns None for years outside valid range."""
        assert extract_year("Ancient text (1800)") is None  # Too old
        assert extract_year("Future paper (2200)") is None  # Too far future

    def test_valid_year_range(self):
        """Accepts years in valid range (1901-2099)."""
        assert extract_year("Old paper (1901)") == 1901
        assert extract_year("Far future (2099)") == 2099

    def test_multiple_years_returns_first(self):
        """Returns first valid year when multiple present."""
        # First pattern match wins
        result = extract_year("Smith (2020) reviewed Jones (2021)")
        assert result == 2020


# =============================================================================
# extract_citations_from_hypothesis_set Function Tests
# =============================================================================


class TestExtractCitations:
    def test_extracts_supporting_evidence(self, hypothesis_with_citations):
        """Extracts citations from supporting evidence."""
        citations = extract_citations_from_hypothesis_set(
            {"hypotheses": [hypothesis_with_citations]}
        )
        assert "Smith et al. (2023)" in citations["main_text"]
        assert "Jones et al. (2022)" in citations["main_text"]
        assert "Brown et al. (2024)" in citations["main_text"]

    def test_extracts_conflicting_evidence(self, hypothesis_with_citations):
        """Extracts citations from conflicting evidence."""
        citations = extract_citations_from_hypothesis_set(
            {"hypotheses": [hypothesis_with_citations]}
        )
        # Conflicting evidence should be in main_text
        assert "Lee et al. (2021)" in citations["main_text"]

    def test_extracts_appendix_evidence(self, hypothesis_with_citations):
        """Extracts citations from appendix evidence."""
        citations = extract_citations_from_hypothesis_set(
            {"hypotheses": [hypothesis_with_citations]}
        )
        assert "Wilson et al. (2020)" in citations["appendix"]
        assert "Taylor et al. (2019)" in citations["appendix"]

    def test_all_citations_includes_everything(self, hypothesis_with_citations):
        """'all' key includes citations from all sources."""
        citations = extract_citations_from_hypothesis_set(
            {"hypotheses": [hypothesis_with_citations]}
        )
        all_cits = citations["all"]
        assert "Smith et al. (2023)" in all_cits
        assert "Lee et al. (2021)" in all_cits
        assert "Wilson et al. (2020)" in all_cits

    def test_deduplicates_citations(self):
        """Duplicate citations are counted once."""
        hypothesis_set = {
            "hypotheses": [
                {
                    "supporting_evidence": [
                        {"finding": "F1", "citation": "Same (2023)"},
                        {"finding": "F2", "citation": "Same (2023)"},
                    ],
                    "conflicting_evidence": [],
                    "appendix_evidence": [],
                },
                {
                    "supporting_evidence": [
                        {"finding": "F3", "citation": "Same (2023)"},
                    ],
                    "conflicting_evidence": [],
                    "appendix_evidence": [],
                },
            ]
        }
        citations = extract_citations_from_hypothesis_set(hypothesis_set)
        assert len(citations["all"]) == 1

    def test_handles_empty_hypothesis_set(self):
        """Handles empty hypothesis set gracefully."""
        citations = extract_citations_from_hypothesis_set({"hypotheses": []})
        assert citations["main_text"] == []
        assert citations["appendix"] == []
        assert citations["all"] == []

    def test_handles_missing_hypotheses_key(self):
        """Handles missing 'hypotheses' key gracefully."""
        citations = extract_citations_from_hypothesis_set({})
        assert citations["main_text"] == []
        assert citations["appendix"] == []
        assert citations["all"] == []

    def test_strips_whitespace(self):
        """Strips whitespace from citations."""
        hypothesis_set = {
            "hypotheses": [
                {
                    "supporting_evidence": [
                        {"finding": "F", "citation": "  Padded (2023)  "},
                    ],
                    "conflicting_evidence": [],
                    "appendix_evidence": [],
                }
            ]
        }
        citations = extract_citations_from_hypothesis_set(hypothesis_set)
        assert "Padded (2023)" in citations["all"]

    def test_skips_empty_citations(self):
        """Skips empty citation strings."""
        hypothesis_set = {
            "hypotheses": [
                {
                    "supporting_evidence": [
                        {"finding": "F1", "citation": ""},
                        {"finding": "F2", "citation": "Real (2023)"},
                    ],
                    "conflicting_evidence": [],
                    "appendix_evidence": [],
                }
            ]
        }
        citations = extract_citations_from_hypothesis_set(hypothesis_set)
        assert len(citations["all"]) == 1
        assert "Real (2023)" in citations["all"]


# =============================================================================
# analyze_citations Function Tests
# =============================================================================


class TestAnalyzeCitations:
    def test_counts_citations_correctly(self):
        """Counts total, main text, and appendix citations."""
        citations = {
            "all": ["A (2023)", "B (2023)", "C (2023)"],
            "main_text": ["A (2023)", "B (2023)"],
            "appendix": ["C (2023)"],
        }
        report = analyze_citations(citations)
        assert report["counts"]["total"] == 3
        assert report["counts"]["main_text"] == 2
        assert report["counts"]["appendix_only"] == 1

    def test_threshold_checks_below_min(self):
        """Reports thresholds not met when below minimum."""
        citations = {
            "all": ["A (2023)"] * 5,  # 5 < 40
            "main_text": ["A (2023)"] * 3,  # 3 < 10
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["thresholds"]["total_meets_min"] is False
        assert report["thresholds"]["main_text_meets_min"] is False
        assert report["overall_valid"] is False

    def test_threshold_checks_meets_min(self):
        """Reports thresholds met when at or above minimum."""
        citations = {
            "all": [f"Author{i} (2023)" for i in range(45)],
            "main_text": [f"Author{i} (2023)" for i in range(12)],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["thresholds"]["total_meets_min"] is True
        assert report["thresholds"]["main_text_meets_min"] is True
        assert report["overall_valid"] is True

    def test_threshold_checks_meets_target(self):
        """Reports target met when at or above target."""
        citations = {
            "all": [f"Author{i} (2023)" for i in range(55)],
            "main_text": [f"Author{i} (2023)" for i in range(18)],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["thresholds"]["total_meets_target"] is True
        assert report["thresholds"]["main_text_meets_target"] is True

    def test_recency_calculation(self):
        """Calculates recency percentage correctly."""
        # 6 recent (2022-2026), 4 old (before 2021)
        citations = {
            "all": [
                "A (2026)",
                "B (2025)",
                "C (2024)",
                "D (2023)",
                "E (2022)",
                "F (2021)",  # Cutoff at 2021 (2026-5)
                "G (2020)",
                "H (2019)",
                "I (2018)",
                "J (2017)",
            ],
            "main_text": [],
            "appendix": [],
        }
        report = analyze_citations(citations, current_year=2026)
        # Recent: 2026, 2025, 2024, 2023, 2022, 2021 = 6 papers
        assert report["recency"]["papers_with_year"] == 10
        assert report["recency"]["recent_count"] == 6
        assert report["recency"]["recent_percent"] == 60.0

    def test_recency_threshold_check(self):
        """Reports recency threshold met/not met."""
        # All recent
        recent_citations = {
            "all": [f"A{i} (2024)" for i in range(10)],
            "main_text": [],
            "appendix": [],
        }
        report = analyze_citations(recent_citations)
        assert report["thresholds"]["recent_meets_min"] is True

        # All old
        old_citations = {
            "all": [f"A{i} (2010)" for i in range(10)],
            "main_text": [],
            "appendix": [],
        }
        report = analyze_citations(old_citations)
        assert report["thresholds"]["recent_meets_min"] is False

    def test_gap_calculation(self):
        """Calculates gaps to minimum correctly."""
        citations = {
            "all": [f"A{i} (2023)" for i in range(35)],  # Need 5 more
            "main_text": [f"A{i} (2023)" for i in range(7)],  # Need 3 more
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["gaps"]["total_needed"] == 5
        assert report["gaps"]["main_text_needed"] == 3

    def test_no_gap_when_threshold_met(self):
        """Reports zero gap when threshold is met."""
        citations = {
            "all": [f"A{i} (2023)" for i in range(50)],
            "main_text": [f"A{i} (2023)" for i in range(20)],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["gaps"]["total_needed"] == 0
        assert report["gaps"]["main_text_needed"] == 0

    def test_handles_no_years_extractable(self):
        """Handles citations with no extractable years."""
        citations = {
            "all": ["No year here", "Also no year"],
            "main_text": ["No year here"],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["recency"]["papers_with_year"] == 0
        assert report["recency"]["recent_count"] == 0
        assert report["recency"]["recent_percent"] == 0

    def test_handles_empty_citations(self):
        """Handles empty citation lists."""
        citations = {"all": [], "main_text": [], "appendix": []}
        report = analyze_citations(citations)
        assert report["counts"]["total"] == 0
        assert report["overall_valid"] is False


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    def test_full_extraction_and_analysis(self, hypothesis_set_with_many_citations):
        """Full pipeline: extract citations and analyze."""
        citations = extract_citations_from_hypothesis_set(
            hypothesis_set_with_many_citations
        )
        report = analyze_citations(citations)

        # Should have 50 unique citations (5 hypotheses * 10 each)
        assert report["counts"]["total"] == 50
        assert report["overall_valid"] is True

    def test_below_threshold_full_pipeline(self, hypothesis_set_below_threshold):
        """Full pipeline with insufficient citations."""
        citations = extract_citations_from_hypothesis_set(
            hypothesis_set_below_threshold
        )
        report = analyze_citations(citations)

        assert report["counts"]["total"] == 2
        assert report["overall_valid"] is False
        assert report["gaps"]["total_needed"] == 38


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_exactly_at_minimum_threshold(self):
        """Exactly at minimum threshold passes."""
        citations = {
            "all": [f"A{i} (2023)" for i in range(40)],
            "main_text": [f"A{i} (2023)" for i in range(10)],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["thresholds"]["total_meets_min"] is True
        assert report["thresholds"]["main_text_meets_min"] is True
        assert report["overall_valid"] is True

    def test_one_below_minimum_threshold(self):
        """One below minimum threshold fails."""
        citations = {
            "all": [f"A{i} (2023)" for i in range(39)],
            "main_text": [f"A{i} (2023)" for i in range(10)],
            "appendix": [],
        }
        report = analyze_citations(citations)
        assert report["thresholds"]["total_meets_min"] is False
        assert report["overall_valid"] is False

    def test_exactly_60_percent_recent(self):
        """Exactly 60% recent meets threshold."""
        # 6 out of 10 = 60%
        citations = {
            "all": [
                "A1 (2024)",
                "A2 (2024)",
                "A3 (2024)",
                "A4 (2024)",
                "A5 (2024)",
                "A6 (2024)",
                "B1 (2010)",
                "B2 (2010)",
                "B3 (2010)",
                "B4 (2010)",
            ],
            "main_text": [],
            "appendix": [],
        }
        report = analyze_citations(citations, current_year=2026)
        assert report["recency"]["recent_percent"] == 60.0
        assert report["thresholds"]["recent_meets_min"] is True

    def test_59_percent_recent_fails(self):
        """59% recent does not meet 60% threshold."""
        # Need slightly different distribution
        recent = [f"R{i} (2024)" for i in range(59)]
        old = [f"O{i} (2010)" for i in range(41)]
        citations = {"all": recent + old, "main_text": [], "appendix": []}
        report = analyze_citations(citations, current_year=2026)
        assert report["recency"]["recent_percent"] == 59.0
        assert report["thresholds"]["recent_meets_min"] is False

    def test_different_current_year(self):
        """Recency calculation uses provided current year."""
        citations = {
            "all": ["Paper (2020)"],
            "main_text": [],
            "appendix": [],
        }
        # With current_year=2025, 2020 is exactly at 5-year cutoff
        report = analyze_citations(citations, current_year=2025)
        assert report["recency"]["recent_count"] == 1

        # With current_year=2026, 2020 is outside 5-year window
        report = analyze_citations(citations, current_year=2026)
        assert report["recency"]["recent_count"] == 0
