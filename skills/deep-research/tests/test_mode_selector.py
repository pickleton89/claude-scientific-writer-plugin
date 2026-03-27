"""Tests for mode_selector.py — deterministic mode selection from user input."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mode_selector import (
    ModeSelection,
    MODE_KEYWORDS,
    VAGUE_INDICATORS,
    select_mode,
    select_mode_from_json,
)
from thresholds import ALL_MODES


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    def test_all_keyword_modes_are_valid(self):
        """Every mode in MODE_KEYWORDS must be in ALL_MODES."""
        for mode in MODE_KEYWORDS:
            assert mode in ALL_MODES, f"{mode} not in ALL_MODES"

    def test_mode_keywords_has_six_primary_modes(self):
        """Six primary keyword-matched modes exist."""
        expected = {"systematic-review", "hypothesis", "fact-check", "socratic", "quick", "lit-review"}
        assert set(MODE_KEYWORDS.keys()) == expected

    def test_vague_indicators_not_empty(self):
        """Vague indicators list has entries."""
        assert len(VAGUE_INDICATORS) > 0


# =============================================================================
# Priority Ordering Tests
# =============================================================================


class TestPriorityOrdering:
    def test_systematic_review_beats_lit_review(self):
        """'systematic review of cancer' → systematic-review, not lit-review."""
        result = select_mode("systematic review of cancer treatments")
        assert result.selected_mode == "systematic-review"

    def test_hypothesis_beats_full(self):
        """'generate hypotheses about EGFR' → hypothesis mode."""
        result = select_mode("generate hypotheses about EGFR resistance")
        assert result.selected_mode == "hypothesis"

    def test_fact_check_beats_quick(self):
        """'fact-check this claim about ivermectin' → fact-check, not quick."""
        result = select_mode("fact-check this claim about ivermectin efficacy")
        assert result.selected_mode == "fact-check"

    def test_systematic_review_beats_review_mode(self):
        """'review this systematic review' → systematic-review, not review."""
        result = select_mode("review this systematic review manuscript", has_provided_text=True)
        assert result.selected_mode == "systematic-review"

    def test_quick_search_beats_lit_review(self):
        """'find papers on p53' → quick, not lit-review."""
        result = select_mode("find papers on p53 mutations")
        assert result.selected_mode == "quick"


# =============================================================================
# Keyword Matching Tests
# =============================================================================


class TestKeywordMatching:
    def test_systematic_review_keywords(self):
        """Each systematic-review keyword triggers correct mode."""
        inputs = [
            "conduct a systematic review",
            "perform PRISMA analysis",
            "meta-analysis of clinical trials",
            "forest plot for treatment effects",
            "risk of bias assessment needed",
            "registered on PROSPERO",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "systematic-review", f"Failed for: {inp}"
            assert result.confidence == "high"

    def test_hypothesis_keywords(self):
        """Hypothesis keywords trigger hypothesis mode."""
        inputs = [
            "generate hypotheses for this phenomenon",
            "propose a testable prediction",
            "competing explanations for the data",
            "propose mechanism for drug resistance",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "hypothesis", f"Failed for: {inp}"

    def test_fact_check_keywords(self):
        """Fact-check keywords trigger fact-check mode."""
        inputs = [
            "fact-check this statement",
            "verify this claim about vaccines",
            "is it true that aspirin prevents cancer",
            "debunk this myth about GMOs",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "fact-check", f"Failed for: {inp}"

    def test_socratic_keywords(self):
        """Socratic keywords trigger socratic mode with high confidence."""
        inputs = [
            "guide my research on autophagy",
            "help me think about this problem",
            "walk me through the evidence",
            "let's explore this topic together",
            "brainstorm with me about CRISPR applications",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "socratic", f"Failed for: {inp}"
            assert result.confidence == "high"

    def test_quick_keywords(self):
        """Quick-search keywords trigger quick mode."""
        inputs = [
            "find papers on BRCA2",
            "search pubmed for autophagy inhibitors",
            "quick search for recent EGFR studies",
            "any papers on ferroptosis",
            "look up recent papers on mRNA vaccines",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "quick", f"Failed for: {inp}"

    def test_lit_review_keywords(self):
        """Literature review keywords trigger lit-review mode."""
        inputs = [
            "write a literature review on immunotherapy",
            "what does the literature say about exercise and depression",
            "state of the art in gene editing",
            "scoping review of telehealth interventions",
        ]
        for inp in inputs:
            result = select_mode(inp)
            assert result.selected_mode == "lit-review", f"Failed for: {inp}"


# =============================================================================
# Review Mode Tests
# =============================================================================


class TestReviewMode:
    def test_review_with_text_high_confidence(self):
        """'review this' + text provided → review mode, high confidence."""
        result = select_mode("review this manuscript", has_provided_text=True)
        assert result.selected_mode == "review"
        assert result.confidence == "high"

    def test_review_without_text_medium_confidence(self):
        """'review this' without text → review mode, medium confidence + note."""
        result = select_mode("review this manuscript", has_provided_text=False)
        assert result.selected_mode == "review"
        assert result.confidence == "medium"
        assert any("no text provided" in n.lower() for n in result.notes)

    def test_critique_with_text(self):
        """'critique this paper' + text → review mode."""
        result = select_mode("critique this paper", has_provided_text=True)
        assert result.selected_mode == "review"

    def test_evaluate_with_text(self):
        """'evaluate this draft' + text → review mode."""
        result = select_mode("evaluate this manuscript", has_provided_text=True)
        assert result.selected_mode == "review"

    def test_give_feedback_with_text(self):
        """'give feedback on this' + text → review mode."""
        result = select_mode("give me feedback on this", has_provided_text=True)
        assert result.selected_mode == "review"


# =============================================================================
# Vague/Exploratory Input Tests
# =============================================================================


class TestVagueInputs:
    def test_interested_triggers_socratic(self):
        """'I'm interested in...' → socratic mode, medium confidence."""
        result = select_mode("I'm interested in protein folding")
        assert result.selected_mode == "socratic"
        assert result.confidence == "medium"

    def test_where_to_start_triggers_socratic(self):
        """'where do I start' → socratic mode."""
        result = select_mode("where do I start with this topic")
        assert result.selected_mode == "socratic"

    def test_how_would_i_approach_triggers_socratic(self):
        """'how would I approach' → socratic mode."""
        result = select_mode("how would I approach studying this disease")
        assert result.selected_mode == "socratic"


# =============================================================================
# Default / Fallback Tests
# =============================================================================


class TestDefaults:
    def test_empty_input_defaults_full(self):
        """Empty input → full mode, low confidence."""
        result = select_mode("")
        assert result.selected_mode == "full"
        assert result.confidence == "low"

    def test_whitespace_input_defaults_full(self):
        """Whitespace-only input → full mode."""
        result = select_mode("   ")
        assert result.selected_mode == "full"
        assert result.confidence == "low"

    def test_no_keywords_defaults_full(self):
        """Input with no matching keywords → full mode."""
        result = select_mode("EGFR resistance in non-small cell lung cancer")
        assert result.selected_mode == "full"
        assert result.confidence == "low"

    def test_default_includes_note(self):
        """Default selection includes explanatory note."""
        result = select_mode("some generic research topic")
        assert len(result.notes) > 0


# =============================================================================
# JSON Interface Tests
# =============================================================================


class TestJSONInterface:
    def test_json_wrapper_basic(self):
        """select_mode_from_json returns correct dict keys."""
        result = select_mode_from_json({"user_input": "systematic review of EGFR"})
        assert result["selected_mode"] == "systematic-review"
        assert result["confidence"] == "high"
        assert "matched_keywords" in result
        assert "notes" in result

    def test_json_wrapper_with_text(self):
        """JSON wrapper passes has_provided_text correctly."""
        result = select_mode_from_json({
            "user_input": "review this",
            "has_provided_text": True,
        })
        assert result["selected_mode"] == "review"
        assert result["confidence"] == "high"

    def test_json_wrapper_defaults(self):
        """JSON wrapper handles missing keys with defaults."""
        result = select_mode_from_json({})
        assert result["selected_mode"] == "full"
        assert result["confidence"] == "low"


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_case_insensitive(self):
        """Keyword matching is case-insensitive."""
        result = select_mode("SYSTEMATIC REVIEW of treatment outcomes")
        assert result.selected_mode == "systematic-review"

    def test_meta_analysis_hyphenated(self):
        """'meta-analysis' triggers systematic-review."""
        result = select_mode("meta-analysis of RCTs")
        assert result.selected_mode == "systematic-review"

    def test_metaanalysis_no_space(self):
        """'metaanalysis' triggers systematic-review."""
        result = select_mode("metaanalysis of outcomes")
        assert result.selected_mode == "systematic-review"

    def test_deterministic_output(self):
        """Same input always produces same mode."""
        for _ in range(10):
            result = select_mode("systematic review of EGFR inhibitors")
            assert result.selected_mode == "systematic-review"

    def test_matched_keywords_populated(self):
        """High-confidence results include matched keywords."""
        result = select_mode("meta-analysis of treatment effects")
        assert result.confidence == "high"
        assert len(result.matched_keywords) > 0

    def test_mode_selection_dataclass(self):
        """ModeSelection dataclass works correctly."""
        ms = ModeSelection(selected_mode="full", confidence="low")
        assert ms.selected_mode == "full"
        assert ms.matched_keywords == []
        assert ms.notes == []

    def test_all_returned_modes_valid(self):
        """Every mode returned by select_mode is in ALL_MODES."""
        test_inputs = [
            "systematic review", "hypotheses", "fact-check",
            "guide my research", "find papers", "literature review",
            "some random topic", "",
        ]
        for inp in test_inputs:
            result = select_mode(inp)
            assert result.selected_mode in ALL_MODES, (
                f"Mode '{result.selected_mode}' for input '{inp}' not in ALL_MODES"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
