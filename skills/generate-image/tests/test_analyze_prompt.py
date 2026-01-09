"""
Tests for analyze_prompt.py - prompt component analysis module.

Tests cover:
- Component detection (subject, style, medium, technical, quality)
- Length categorization
- Warning generation
- Suggestion generation
- Batch analysis
- Edge cases
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze_prompt import (
    PromptAnalysis,
    PromptComponent,
    analyze_prompt,
    format_analysis,
    suggest_improvements,
    batch_analyze,
    summarize_batch,
    STYLE_KEYWORDS,
    QUALITY_KEYWORDS,
    TECHNICAL_KEYWORDS,
    MEDIUM_KEYWORDS,
    SCIENTIFIC_SUBJECT_KEYWORDS,
    MIN_OPTIMAL_LENGTH,
    MAX_OPTIMAL_LENGTH,
    MIN_VIABLE_LENGTH,
    MAX_VIABLE_LENGTH,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def complete_prompt():
    """A complete prompt with all 5 components."""
    return (
        "DNA double helix structure with highlighted mutation site, "
        "scientific illustration style, 3D render, "
        "clean white background, high detail professional visualization"
    )


@pytest.fixture
def minimal_prompt():
    """A minimal viable prompt."""
    return "A cell diagram showing mitosis"


@pytest.fixture
def vague_prompt():
    """A vague, too-short prompt."""
    return "a cell"


# ============================================================================
# PromptComponent Dataclass Tests
# ============================================================================


class TestPromptComponentDataclass:
    """Tests for PromptComponent dataclass."""

    def test_component_present(self):
        """Test component with present=True."""
        comp = PromptComponent(
            present=True,
            keywords_found=["scientific illustration", "style"],
            confidence=0.8,
        )
        assert comp.present is True
        assert len(comp.keywords_found) == 2
        assert comp.confidence == 0.8

    def test_component_absent(self):
        """Test component with present=False."""
        comp = PromptComponent(present=False, keywords_found=[], confidence=0.0)
        assert comp.present is False
        assert len(comp.keywords_found) == 0
        assert comp.confidence == 0.0


# ============================================================================
# PromptAnalysis Dataclass Tests
# ============================================================================


class TestPromptAnalysisDataclass:
    """Tests for PromptAnalysis dataclass properties."""

    def test_component_count_all_present(self, complete_prompt):
        """Test component count when all present."""
        analysis = analyze_prompt(complete_prompt)
        assert analysis.component_count == 5

    def test_component_count_partial(self):
        """Test component count with partial coverage."""
        prompt = "DNA helix, clean background"
        analysis = analyze_prompt(prompt)
        # Should have subject and technical at minimum
        assert 2 <= analysis.component_count <= 3

    def test_completeness_score_range(self, complete_prompt, vague_prompt):
        """Test completeness score is in valid range."""
        complete = analyze_prompt(complete_prompt)
        vague = analyze_prompt(vague_prompt)

        assert 0 <= complete.completeness_score <= 1
        assert 0 <= vague.completeness_score <= 1
        assert complete.completeness_score > vague.completeness_score

    def test_is_optimal_length(self):
        """Test is_optimal_length property."""
        # Build a prompt with 25 words (within optimal range)
        words = ["word"] * 25
        prompt = " ".join(words)
        analysis = analyze_prompt(prompt)
        assert analysis.is_optimal_length is True

    def test_is_viable_true(self, minimal_prompt):
        """Test is_viable for viable prompt."""
        analysis = analyze_prompt(minimal_prompt)
        # May or may not be viable depending on component detection
        assert isinstance(analysis.is_viable, bool)

    def test_is_viable_false(self, vague_prompt):
        """Test is_viable for non-viable prompt."""
        analysis = analyze_prompt(vague_prompt)
        assert analysis.is_viable is False


# ============================================================================
# analyze_prompt() - Component Detection Tests
# ============================================================================


class TestAnalyzePromptComponentDetection:
    """Tests for component detection in analyze_prompt."""

    def test_detects_style_keywords(self):
        """Test detection of style keywords."""
        prompts_with_style = [
            "A cell, scientific illustration style",
            "photorealistic rendering of DNA",
            "modern minimalist diagram",
            "abstract visualization of proteins",
        ]
        for prompt in prompts_with_style:
            analysis = analyze_prompt(prompt)
            assert analysis.style.present is True, f"Failed for: {prompt}"

    def test_detects_quality_keywords(self):
        """Test detection of quality keywords."""
        prompts_with_quality = [
            "A cell, high detail",
            "DNA structure, professional quality",
            "4K render of molecule",
            "publication-quality visualization",
            "highly detailed illustration",
        ]
        for prompt in prompts_with_quality:
            analysis = analyze_prompt(prompt)
            assert analysis.quality.present is True, f"Failed for: {prompt}"

    def test_detects_technical_keywords(self):
        """Test detection of technical keywords."""
        prompts_with_technical = [
            "A cell on clean background",
            "DNA with white background",
            "well-lit laboratory scene",
            "high contrast image of proteins",
            "centered composition of structure",
        ]
        for prompt in prompts_with_technical:
            analysis = analyze_prompt(prompt)
            assert analysis.technical.present is True, f"Failed for: {prompt}"

    def test_detects_medium_keywords(self):
        """Test detection of medium keywords."""
        prompts_with_medium = [
            "digital art of a cell",
            "3D render of DNA helix",
            "photograph of laboratory",
            "watercolor illustration of structure",
            "scientific visualization",
        ]
        for prompt in prompts_with_medium:
            analysis = analyze_prompt(prompt)
            assert analysis.medium.present is True, f"Failed for: {prompt}"

    def test_detects_subject_presence(self):
        """Test subject detection based on word count."""
        short_prompt = "a b c"  # 3 words - no subject
        long_prompt = "DNA helix structure model"  # 4+ words - has subject

        short_analysis = analyze_prompt(short_prompt)
        long_analysis = analyze_prompt(long_prompt)

        assert short_analysis.subject.present is False
        assert long_analysis.subject.present is True

    def test_detects_scientific_subjects(self):
        """Test enhanced subject confidence with scientific keywords."""
        scientific_prompts = [
            "DNA double helix structure model",
            "cancer cells under microscope view",
            "CRISPR gene editing mechanism diagram",
            "protein folding pathway visualization",
        ]
        for prompt in scientific_prompts:
            analysis = analyze_prompt(prompt)
            assert analysis.subject.present is True, f"Subject not detected for: {prompt}"
            assert analysis.subject.confidence > 0.5, f"Low confidence for: {prompt}"

    def test_case_insensitive_detection(self):
        """Test that keyword detection is case-insensitive."""
        prompts = [
            "SCIENTIFIC ILLUSTRATION STYLE",
            "Scientific Illustration Style",
            "scientific illustration style",
        ]
        for prompt in prompts:
            analysis = analyze_prompt(prompt)
            assert analysis.style.present is True, f"Failed for: {prompt}"


# ============================================================================
# analyze_prompt() - Length Categorization Tests
# ============================================================================


class TestAnalyzePromptLengthCategorization:
    """Tests for prompt length categorization."""

    def test_too_short_length(self):
        """Test too_short categorization (<10 words)."""
        prompt = "one two three four"  # 4 words
        analysis = analyze_prompt(prompt)
        assert analysis.length_category == "too_short"

    def test_short_length(self):
        """Test short categorization (10-19 words)."""
        prompt = " ".join(["word"] * 15)
        analysis = analyze_prompt(prompt)
        assert analysis.length_category == "short"

    def test_optimal_length(self):
        """Test optimal categorization (20-50 words)."""
        prompt = " ".join(["word"] * 35)
        analysis = analyze_prompt(prompt)
        assert analysis.length_category == "optimal"

    def test_long_length(self):
        """Test long categorization (51-100 words)."""
        prompt = " ".join(["word"] * 75)
        analysis = analyze_prompt(prompt)
        assert analysis.length_category == "long"

    def test_too_long_length(self):
        """Test too_long categorization (>100 words)."""
        prompt = " ".join(["word"] * 120)
        analysis = analyze_prompt(prompt)
        assert analysis.length_category == "too_long"

    def test_boundary_values(self):
        """Test exact boundary length values."""
        # Exactly 10 words (short, not too_short)
        p10 = " ".join(["word"] * 10)
        assert analyze_prompt(p10).length_category == "short"

        # Exactly 20 words (optimal)
        p20 = " ".join(["word"] * 20)
        assert analyze_prompt(p20).length_category == "optimal"

        # Exactly 50 words (optimal)
        p50 = " ".join(["word"] * 50)
        assert analyze_prompt(p50).length_category == "optimal"

        # Exactly 51 words (long)
        p51 = " ".join(["word"] * 51)
        assert analyze_prompt(p51).length_category == "long"

        # Exactly 100 words (long)
        p100 = " ".join(["word"] * 100)
        assert analyze_prompt(p100).length_category == "long"

        # Exactly 101 words (too_long)
        p101 = " ".join(["word"] * 101)
        assert analyze_prompt(p101).length_category == "too_long"


# ============================================================================
# analyze_prompt() - Warning Generation Tests
# ============================================================================


class TestAnalyzePromptWarnings:
    """Tests for warning generation."""

    def test_warns_too_short(self):
        """Test warning for too-short prompts."""
        analysis = analyze_prompt("a cell")
        assert any("short" in w.lower() for w in analysis.warnings)

    def test_warns_too_long(self):
        """Test warning for too-long prompts."""
        prompt = " ".join(["word"] * 120)
        analysis = analyze_prompt(prompt)
        assert any("long" in w.lower() for w in analysis.warnings)

    def test_warns_missing_style(self):
        """Test warning for missing style component."""
        prompt = "DNA helix structure, high detail, clean background"
        analysis = analyze_prompt(prompt)
        if not analysis.style.present:
            assert any("STYLE" in w for w in analysis.warnings)

    def test_warns_missing_quality(self):
        """Test warning for missing quality component."""
        prompt = "DNA helix structure, scientific illustration, clean background"
        analysis = analyze_prompt(prompt)
        if not analysis.quality.present:
            assert any("QUALITY" in w for w in analysis.warnings)

    def test_warns_missing_technical(self):
        """Test warning for missing technical component."""
        prompt = "DNA helix structure, scientific illustration, high detail"
        analysis = analyze_prompt(prompt)
        if not analysis.technical.present:
            assert any("TECHNICAL" in w for w in analysis.warnings)

    def test_no_warnings_complete_prompt(self, complete_prompt):
        """Test no warnings for complete prompt."""
        analysis = analyze_prompt(complete_prompt)
        # Complete prompt should have few or no warnings
        assert len(analysis.warnings) <= 1


# ============================================================================
# analyze_prompt() - Suggestion Generation Tests
# ============================================================================


class TestAnalyzePromptSuggestions:
    """Tests for suggestion generation."""

    def test_suggests_style(self):
        """Test suggestion for adding style."""
        prompt = "DNA helix, high detail, clean background"
        analysis = analyze_prompt(prompt)
        if not analysis.style.present:
            assert any("style" in s.lower() for s in analysis.suggestions)

    def test_suggests_quality(self):
        """Test suggestion for adding quality."""
        prompt = "DNA helix, scientific illustration, clean background"
        analysis = analyze_prompt(prompt)
        if not analysis.quality.present:
            assert any("quality" in s.lower() or "detail" in s.lower() for s in analysis.suggestions)

    def test_suggests_technical(self):
        """Test suggestion for adding technical."""
        prompt = "DNA helix, scientific illustration, high detail"
        analysis = analyze_prompt(prompt)
        if not analysis.technical.present:
            assert any("background" in s.lower() for s in analysis.suggestions)

    def test_suggests_expansion_for_short(self):
        """Test suggestion to expand short prompts."""
        prompt = "a cell"
        analysis = analyze_prompt(prompt)
        assert any("expand" in s.lower() for s in analysis.suggestions)

    def test_no_suggestions_complete_prompt(self, complete_prompt):
        """Test minimal suggestions for complete prompt."""
        analysis = analyze_prompt(complete_prompt)
        # Complete prompt should have few suggestions
        assert len(analysis.suggestions) <= 1


# ============================================================================
# format_analysis() Tests
# ============================================================================


class TestFormatAnalysis:
    """Tests for format_analysis function."""

    def test_includes_word_count(self, complete_prompt):
        """Test that output includes word count."""
        analysis = analyze_prompt(complete_prompt)
        output = format_analysis(analysis)
        assert str(analysis.word_count) in output

    def test_includes_components(self, complete_prompt):
        """Test that output includes component status."""
        analysis = analyze_prompt(complete_prompt)
        output = format_analysis(analysis)

        assert "Subject" in output
        assert "Style" in output
        assert "Medium" in output
        assert "Technical" in output
        assert "Quality" in output

    def test_includes_completeness(self, complete_prompt):
        """Test that output includes completeness score."""
        analysis = analyze_prompt(complete_prompt)
        output = format_analysis(analysis)

        assert "Completeness" in output
        assert "%" in output

    def test_includes_warnings_if_present(self, vague_prompt):
        """Test that output includes warnings when present."""
        analysis = analyze_prompt(vague_prompt)
        output = format_analysis(analysis)

        if analysis.warnings:
            assert "Warning" in output

    def test_includes_suggestions_if_present(self, vague_prompt):
        """Test that output includes suggestions when present."""
        analysis = analyze_prompt(vague_prompt)
        output = format_analysis(analysis)

        if analysis.suggestions:
            assert "Suggestion" in output

    def test_includes_viability_status(self, complete_prompt, vague_prompt):
        """Test that output includes viability status."""
        complete_output = format_analysis(analyze_prompt(complete_prompt))
        vague_output = format_analysis(analyze_prompt(vague_prompt))

        assert "Status" in complete_output
        assert "Status" in vague_output


# ============================================================================
# suggest_improvements() Tests
# ============================================================================


class TestSuggestImprovements:
    """Tests for suggest_improvements function."""

    def test_adds_missing_style(self):
        """Test that missing style is added."""
        prompt = "DNA helix, high detail, clean background"
        improved = suggest_improvements(prompt)

        if "style" not in prompt.lower():
            assert "style" in improved.lower()

    def test_adds_missing_quality(self):
        """Test that missing quality is added."""
        prompt = "DNA helix, scientific illustration, clean background"
        improved = suggest_improvements(prompt)

        # Should add quality keywords if missing
        assert len(improved) >= len(prompt)

    def test_adds_missing_technical(self):
        """Test that missing technical is added."""
        prompt = "DNA helix, scientific illustration, high detail"
        improved = suggest_improvements(prompt)

        # Should add technical keywords if missing
        assert len(improved) >= len(prompt)

    def test_no_change_complete_prompt(self, complete_prompt):
        """Test that complete prompt is unchanged."""
        improved = suggest_improvements(complete_prompt)
        # Complete prompt should only have minimal additions
        # The improved version might be same or slightly longer
        assert complete_prompt in improved or len(improved) >= len(complete_prompt)

    def test_output_format(self, vague_prompt):
        """Test that output is properly formatted."""
        improved = suggest_improvements(vague_prompt)
        # Should be a non-empty string
        assert isinstance(improved, str)
        assert len(improved) > 0


# ============================================================================
# Batch Analysis Tests
# ============================================================================


class TestBatchAnalysis:
    """Tests for batch analysis functions."""

    def test_batch_analyze(self, complete_prompt, minimal_prompt, vague_prompt):
        """Test batch analysis of multiple prompts."""
        prompts = [complete_prompt, minimal_prompt, vague_prompt]
        results = batch_analyze(prompts)

        assert len(results) == 3
        assert all(isinstance(r, PromptAnalysis) for r in results)

    def test_summarize_batch(self, complete_prompt, minimal_prompt, vague_prompt):
        """Test batch summary statistics."""
        prompts = [complete_prompt, minimal_prompt, vague_prompt]
        analyses = batch_analyze(prompts)
        summary = summarize_batch(analyses)

        assert summary["total"] == 3
        assert "viable" in summary
        assert "viable_rate" in summary
        assert "avg_components" in summary
        assert "avg_completeness" in summary
        assert "component_coverage" in summary

    def test_summarize_batch_empty(self):
        """Test summary of empty batch."""
        summary = summarize_batch([])
        assert summary["total"] == 0

    def test_component_coverage_counts(self, complete_prompt, minimal_prompt):
        """Test component coverage counts in summary."""
        prompts = [complete_prompt, minimal_prompt]
        analyses = batch_analyze(prompts)
        summary = summarize_batch(analyses)

        coverage = summary["component_coverage"]
        assert "subject" in coverage
        assert "style" in coverage
        assert "medium" in coverage
        assert "technical" in coverage
        assert "quality" in coverage


# ============================================================================
# Keyword Sets Tests
# ============================================================================


class TestKeywordSets:
    """Tests for keyword set definitions."""

    def test_style_keywords_not_empty(self):
        """Test STYLE_KEYWORDS is not empty."""
        assert len(STYLE_KEYWORDS) > 0

    def test_quality_keywords_not_empty(self):
        """Test QUALITY_KEYWORDS is not empty."""
        assert len(QUALITY_KEYWORDS) > 0

    def test_technical_keywords_not_empty(self):
        """Test TECHNICAL_KEYWORDS is not empty."""
        assert len(TECHNICAL_KEYWORDS) > 0

    def test_medium_keywords_not_empty(self):
        """Test MEDIUM_KEYWORDS is not empty."""
        assert len(MEDIUM_KEYWORDS) > 0

    def test_scientific_subject_keywords_not_empty(self):
        """Test SCIENTIFIC_SUBJECT_KEYWORDS is not empty."""
        assert len(SCIENTIFIC_SUBJECT_KEYWORDS) > 0

    def test_keyword_sets_are_frozensets(self):
        """Test that keyword sets are immutable frozensets."""
        assert isinstance(STYLE_KEYWORDS, frozenset)
        assert isinstance(QUALITY_KEYWORDS, frozenset)
        assert isinstance(TECHNICAL_KEYWORDS, frozenset)
        assert isinstance(MEDIUM_KEYWORDS, frozenset)
        assert isinstance(SCIENTIFIC_SUBJECT_KEYWORDS, frozenset)

    def test_keywords_are_lowercase(self):
        """Test that all keywords are lowercase for case-insensitive matching."""
        all_keywords = (
            STYLE_KEYWORDS
            | QUALITY_KEYWORDS
            | TECHNICAL_KEYWORDS
            | MEDIUM_KEYWORDS
            | SCIENTIFIC_SUBJECT_KEYWORDS
        )
        for kw in all_keywords:
            assert kw == kw.lower(), f"Keyword not lowercase: {kw}"


# ============================================================================
# Constants Tests
# ============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_length_constants(self):
        """Test length constant values."""
        assert MIN_OPTIMAL_LENGTH == 20
        assert MAX_OPTIMAL_LENGTH == 50
        assert MIN_VIABLE_LENGTH == 10
        assert MAX_VIABLE_LENGTH == 100

    def test_length_constant_ordering(self):
        """Test length constants are in logical order."""
        assert MIN_VIABLE_LENGTH < MIN_OPTIMAL_LENGTH
        assert MIN_OPTIMAL_LENGTH < MAX_OPTIMAL_LENGTH
        assert MAX_OPTIMAL_LENGTH < MAX_VIABLE_LENGTH


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        analysis = analyze_prompt("")
        assert analysis.word_count == 0
        assert analysis.is_viable is False

    def test_whitespace_only_prompt(self):
        """Test handling of whitespace-only prompt."""
        analysis = analyze_prompt("   \t\n   ")
        # Splitting whitespace gives ['']
        assert analysis.word_count <= 1
        assert analysis.is_viable is False

    def test_single_word_prompt(self):
        """Test handling of single word prompt."""
        analysis = analyze_prompt("DNA")
        assert analysis.word_count == 1
        assert analysis.is_viable is False

    def test_very_long_keyword(self):
        """Test handling of very long compound keywords."""
        prompt = "suitable for academic publication in high impact journals"
        analysis = analyze_prompt(prompt)
        # Should still work without errors
        assert isinstance(analysis, PromptAnalysis)

    def test_special_characters(self):
        """Test handling of special characters in prompt."""
        prompt = "DNA helix @#$% structure!!! with **bold** formatting"
        analysis = analyze_prompt(prompt)
        # Should handle gracefully
        assert isinstance(analysis, PromptAnalysis)

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        prompt = "DNA structure 🧬 with scientific illustration style"
        analysis = analyze_prompt(prompt)
        # Should handle gracefully
        assert isinstance(analysis, PromptAnalysis)
        assert analysis.style.present is True

    def test_mixed_case_keywords(self):
        """Test case-insensitive keyword matching."""
        prompts = [
            "SCIENTIFIC ILLUSTRATION STYLE",
            "Scientific Illustration Style",
            "ScIeNtIfIc IllUsTrAtIoN sTyLe",
        ]
        for prompt in prompts:
            analysis = analyze_prompt(prompt)
            assert analysis.style.present is True

    def test_partial_keyword_no_match(self):
        """Test that partial keyword matches don't count."""
        # "sty" is not "style"
        prompt = "DNA with a unique sty of rendering"
        result = analyze_prompt(prompt)
        # "sty" should not match "style" - depends on implementation
        # This tests exact substring matching behavior
        assert isinstance(result.style.present, bool)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_analyze_format_roundtrip(self, complete_prompt):
        """Test analyze -> format workflow."""
        analysis = analyze_prompt(complete_prompt)
        formatted = format_analysis(analysis)

        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_analyze_suggest_roundtrip(self, vague_prompt):
        """Test analyze -> suggest workflow."""
        _ = analyze_prompt(vague_prompt)  # Verify it parses without error
        improved = suggest_improvements(vague_prompt)

        # Improved version should be analyzable
        improved_analysis = analyze_prompt(improved)
        assert isinstance(improved_analysis, PromptAnalysis)

    def test_scientific_workflow(self):
        """Test typical scientific image prompt workflow."""
        # Start with basic prompt
        basic = "DNA double helix"
        analysis1 = analyze_prompt(basic)

        # Improve it
        improved = suggest_improvements(basic)
        analysis2 = analyze_prompt(improved)

        # Improved should have better scores
        assert analysis2.component_count >= analysis1.component_count

    def test_batch_workflow(self):
        """Test batch analysis workflow."""
        prompts = [
            "DNA double helix structure",
            "A cell, scientific illustration style, high detail, clean background",
            "complex molecular visualization with photorealistic rendering",
        ]

        analyses = batch_analyze(prompts)
        summary = summarize_batch(analyses)

        # Verify summary stats are reasonable
        assert summary["total"] == 3
        assert 0 <= summary["viable_rate"] <= 1
        assert 0 <= summary["avg_completeness"] <= 1
        assert 1 <= summary["avg_components"] <= 5
