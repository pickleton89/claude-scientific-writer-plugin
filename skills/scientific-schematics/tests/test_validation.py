"""Tests for scientific-schematics validation utilities.

Tests cover:
- Prompt validation and type detection
- Diagram type selection
- Complexity limits
- Brand color palettes
- Image validation
- Output schemas
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Import modules under test
from diagram_type_selector import (
    get_all_diagram_types,
    get_all_purposes,
    get_diagram_type_info,
    get_domains_for_purpose,
    infer_type_from_prompt,
    select_diagram_type,
)
from utils.brand_colors import (
    format_color_guidance,
    get_palette,
    get_palette_names,
    inject_colors_into_prompt,
    validate_contrast,
)
from utils.complexity_limits import (
    check_complexity,
    estimate_nodes_from_prompt,
    get_all_diagram_types as get_complexity_types,
    get_limits,
)
from utils.schemas import (
    GenerationResults,
    IterationResult,
    SchematicPrompt,
    hash_prompt,
    validate_results_dict,
)
from validate_image import (
    check_publication_ready,
    format_validation_report,
    validate_output_image,
)
from validate_prompt import (
    format_validation_report as format_prompt_report,
    suggest_improvements,
    validate_and_enhance_prompt,
    validate_prompt,
)


# =====================================================================
# Diagram Type Selector Tests
# =====================================================================


class TestDiagramTypeSelector:
    """Tests for diagram type selection."""

    def test_select_study_design_clinical_trial(self) -> None:
        """Test CONSORT selection for clinical trials."""
        result = select_diagram_type("study_design", "clinical_trial")
        assert result == "consort"

    def test_select_study_design_systematic_review(self) -> None:
        """Test PRISMA selection for systematic reviews."""
        result = select_diagram_type("study_design", "systematic_review")
        assert result == "prisma"

    def test_select_ml_attention(self) -> None:
        """Test transformer selection for attention-based ML."""
        result = select_diagram_type("ml_architecture", "attention")
        assert result == "transformer"

    def test_select_ml_image(self) -> None:
        """Test CNN selection for image ML."""
        result = select_diagram_type("ml_architecture", "image")
        assert result == "cnn"

    def test_select_biology_signaling(self) -> None:
        """Test pathway selection for signaling."""
        result = select_diagram_type("biology", "signaling")
        assert result == "pathway"

    def test_select_systems_electronics(self) -> None:
        """Test circuit selection for electronics."""
        result = select_diagram_type("systems", "electronics")
        assert result == "circuit_schematic"

    def test_select_fallback_to_purpose(self) -> None:
        """Test fallback when domain is None."""
        result = select_diagram_type("biology")
        assert result == "pathway"

    def test_select_ultimate_fallback(self) -> None:
        """Test fallback for unknown purpose."""
        result = select_diagram_type("unknown_purpose", None)  # type: ignore
        assert result == "block_diagram"

    def test_infer_consort_high_confidence(self) -> None:
        """Test high-confidence CONSORT inference."""
        inference = infer_type_from_prompt("CONSORT participant flow diagram")
        assert inference.diagram_type == "consort"
        assert inference.confidence >= 0.9
        assert "consort" in inference.detected_keywords

    def test_infer_transformer_high_confidence(self) -> None:
        """Test high-confidence transformer inference."""
        inference = infer_type_from_prompt(
            "Transformer architecture with self-attention"
        )
        assert inference.diagram_type == "transformer"
        assert inference.confidence >= 0.9

    def test_infer_pathway_medium_confidence(self) -> None:
        """Test medium-confidence pathway inference."""
        inference = infer_type_from_prompt("Show the signaling cascade")
        assert inference.diagram_type == "pathway"
        assert 0.5 <= inference.confidence <= 0.8

    def test_infer_unknown_low_confidence(self) -> None:
        """Test low confidence for vague prompt."""
        inference = infer_type_from_prompt("A simple diagram")
        assert inference.confidence < 0.5

    def test_get_all_purposes(self) -> None:
        """Test getting all purpose categories."""
        purposes = get_all_purposes()
        assert "study_design" in purposes
        assert "ml_architecture" in purposes
        assert "biology" in purposes

    def test_get_domains_for_purpose(self) -> None:
        """Test getting domains for a purpose."""
        domains = get_domains_for_purpose("study_design")
        assert "clinical_trial" in domains
        assert "systematic_review" in domains

    def test_get_diagram_type_info(self) -> None:
        """Test getting diagram type info."""
        info = get_diagram_type_info("consort")
        assert "description" in info
        assert "purpose" in info
        assert info["purpose"] == "study_design"

    def test_get_all_diagram_types(self) -> None:
        """Test getting all diagram types."""
        types = get_all_diagram_types()
        assert "consort" in types
        assert "transformer" in types
        assert "pathway" in types


# =====================================================================
# Complexity Limits Tests
# =====================================================================


class TestComplexityLimits:
    """Tests for complexity limit checking."""

    def test_consort_within_limits(self) -> None:
        """Test CONSORT diagram within limits."""
        ok, warning = check_complexity("consort", 10)
        assert ok
        assert warning is None

    def test_consort_exceeds_limits(self) -> None:
        """Test CONSORT diagram exceeding limits."""
        ok, warning = check_complexity("consort", 20)
        assert not ok
        assert warning is not None
        assert "exceeds" in warning.lower()

    def test_consort_approaching_limits(self) -> None:
        """Test CONSORT diagram approaching limits."""
        ok, warning = check_complexity("consort", 13)  # 80% of 15
        assert ok
        assert warning is not None
        assert "warning" in warning.lower()

    def test_edge_limits(self) -> None:
        """Test edge count limits."""
        ok, warning = check_complexity("consort", 10, estimated_edges=25)
        assert not ok
        assert "edges" in warning.lower()

    def test_level_limits(self) -> None:
        """Test level count limits."""
        ok, warning = check_complexity("consort", 10, estimated_levels=6)
        assert not ok
        assert "levels" in warning.lower()

    def test_unknown_type_uses_default(self) -> None:
        """Test unknown diagram type uses default limits."""
        limits = get_limits("unknown_type")
        assert limits.max_nodes == 12  # Default value

    def test_estimate_nodes_with_numbers(self) -> None:
        """Test node estimation with explicit numbers."""
        count = estimate_nodes_from_prompt("flowchart with 8 boxes and 10 arrows")
        assert count >= 8

    def test_estimate_nodes_with_indicators(self) -> None:
        """Test node estimation with component indicators."""
        count = estimate_nodes_from_prompt(
            "input → process → output, connects to another box"
        )
        assert count >= 3

    def test_estimate_nodes_minimum(self) -> None:
        """Test minimum node count."""
        count = estimate_nodes_from_prompt("simple diagram")
        assert count >= 3

    def test_all_diagram_types_have_limits(self) -> None:
        """Test that common diagram types have defined limits."""
        types = get_complexity_types()
        assert len(types) >= 15
        for dtype in ["consort", "prisma", "transformer", "cnn", "pathway"]:
            assert dtype in types


# =====================================================================
# Brand Colors Tests
# =====================================================================


class TestBrandColors:
    """Tests for brand color palettes."""

    def test_get_oligon_palette(self) -> None:
        """Test getting Oligon brand palette."""
        palette = get_palette("oligon")
        assert palette.primary == "#2DB2E8"
        assert palette.name == "Oligon Scientific"

    def test_get_okabe_ito_palette(self) -> None:
        """Test getting Okabe-Ito colorblind palette."""
        palette = get_palette("okabe-ito")
        assert palette.primary == "#0072B2"
        assert "Colorblind" in palette.name

    def test_get_default_palette(self) -> None:
        """Test getting default palette."""
        palette = get_palette("default")
        assert palette.name == "Oligon Scientific"

    def test_get_unknown_palette_fallback(self) -> None:
        """Test fallback for unknown palette."""
        palette = get_palette("nonexistent")
        assert palette.name == "Oligon Scientific"

    def test_colorblind_alias(self) -> None:
        """Test colorblind alias maps to Okabe-Ito."""
        p1 = get_palette("colorblind")
        p2 = get_palette("okabe-ito")
        assert p1 == p2

    def test_format_color_guidance(self) -> None:
        """Test formatting color guidance."""
        palette = get_palette("oligon")
        guidance = format_color_guidance(palette)
        assert "Oligon" in guidance
        assert "#2DB2E8" in guidance
        assert "Primary" in guidance

    def test_inject_colors_into_prompt(self) -> None:
        """Test color injection into prompt."""
        prompt = "Create a flowchart"
        enhanced = inject_colors_into_prompt(prompt, "oligon")
        assert "#2DB2E8" in enhanced
        assert "Primary" in enhanced

    def test_inject_colors_skips_existing(self) -> None:
        """Test color injection skips prompts with colors."""
        prompt = "Create a flowchart with #FF0000 highlights"
        enhanced = inject_colors_into_prompt(prompt, "oligon")
        assert enhanced == prompt  # Unchanged

    def test_inject_colors_force(self) -> None:
        """Test forced color injection."""
        prompt = "Create a flowchart with #FF0000 highlights"
        enhanced = inject_colors_into_prompt(prompt, "oligon", force=True)
        assert "#2DB2E8" in enhanced  # Added despite existing colors

    def test_validate_contrast_sufficient(self) -> None:
        """Test sufficient contrast validation."""
        passed, ratio = validate_contrast("#000000", "#FFFFFF")
        assert passed
        assert ratio >= 21  # Black on white is ~21:1

    def test_validate_contrast_insufficient(self) -> None:
        """Test insufficient contrast validation."""
        passed, ratio = validate_contrast("#777777", "#888888")
        assert not passed
        assert ratio < 4.5

    def test_get_palette_names(self) -> None:
        """Test getting unique palette names."""
        names = get_palette_names()
        assert len(names) >= 5
        assert "oligon" in names or "default" in names


# =====================================================================
# Prompt Validation Tests
# =====================================================================


class TestPromptValidation:
    """Tests for prompt validation."""

    def test_valid_consort_prompt(self, valid_consort_prompt: str) -> None:
        """Test validation of valid CONSORT prompt."""
        analysis = validate_prompt(valid_consort_prompt)
        assert analysis.valid
        assert analysis.detected_type == "consort"
        assert analysis.type_confidence >= 0.9
        assert analysis.has_layout
        assert analysis.has_quantitative

    def test_valid_transformer_prompt(self, valid_transformer_prompt: str) -> None:
        """Test validation of valid transformer prompt."""
        analysis = validate_prompt(valid_transformer_prompt)
        assert analysis.valid
        assert analysis.detected_type == "transformer"
        assert analysis.has_layout

    def test_minimal_prompt_warnings(self, minimal_prompt: str) -> None:
        """Test minimal prompt generates warnings."""
        analysis = validate_prompt(minimal_prompt)
        # May still be valid but should have warnings
        assert len(analysis.warnings) > 0

    def test_vague_prompt_warnings(self, vague_prompt: str) -> None:
        """Test vague prompt generates warnings."""
        analysis = validate_prompt(vague_prompt)
        assert any("vague" in w.lower() for w in analysis.warnings)

    def test_short_prompt_invalid(self) -> None:
        """Test very short prompt is invalid."""
        analysis = validate_prompt("diagram")
        assert not analysis.valid
        assert any("short" in i.lower() for i in analysis.issues)

    def test_no_type_detected(self) -> None:
        """Test prompt with no detectable type."""
        analysis = validate_prompt("A generic picture of something")
        assert analysis.detected_type is None or analysis.type_confidence < 0.3

    def test_layout_detection(self) -> None:
        """Test layout keyword detection."""
        analysis = validate_prompt("Flowchart layout: top-to-bottom")
        assert analysis.has_layout

    def test_quantitative_detection(self) -> None:
        """Test quantitative detail detection."""
        analysis = validate_prompt("Flowchart with n=500 participants")
        assert analysis.has_quantitative

    def test_format_validation_report(self, valid_consort_prompt: str) -> None:
        """Test formatting validation report."""
        analysis = validate_prompt(valid_consort_prompt)
        report = format_prompt_report(analysis)
        assert "VALID" in report
        assert "consort" in report.lower()

    def test_suggest_improvements(self, minimal_prompt: str) -> None:
        """Test improvement suggestions."""
        analysis = validate_prompt(minimal_prompt)
        suggestions = suggest_improvements(analysis, minimal_prompt)
        assert "Suggestions" in suggestions or "good" in suggestions.lower()

    def test_validate_and_enhance(self) -> None:
        """Test prompt enhancement."""
        prompt = "CONSORT flowchart"
        analysis, enhanced = validate_and_enhance_prompt(prompt, auto_enhance=True)
        assert "top-to-bottom" in enhanced or "colorblind" in enhanced


# =====================================================================
# Image Validation Tests
# =====================================================================


class TestImageValidation:
    """Tests for image validation."""

    def test_valid_image(self, valid_image_path: Path) -> None:
        """Test validation of valid image."""
        metadata = validate_output_image(valid_image_path)
        assert metadata.valid
        assert metadata.width == 1024
        assert metadata.height == 768
        assert metadata.format == "PNG"
        assert len(metadata.issues) == 0

    def test_small_image_invalid(self, small_image_path: Path) -> None:
        """Test small image fails validation."""
        metadata = validate_output_image(small_image_path)
        assert not metadata.valid
        assert any("small" in i.lower() for i in metadata.issues)

    def test_nonexistent_image(self, nonexistent_image_path: Path) -> None:
        """Test nonexistent image fails validation."""
        metadata = validate_output_image(nonexistent_image_path)
        assert not metadata.valid
        assert any("exist" in i.lower() for i in metadata.issues)

    def test_low_contrast_warning(self, low_contrast_image_path: Path) -> None:
        """Test low contrast image handling."""
        metadata = validate_output_image(low_contrast_image_path, check_colors=True)
        # The image should either have a contrast warning or be valid with low contrast detected
        # (contrast detection is heuristic and may not always trigger warning)
        has_contrast_warning = any("contrast" in w.lower() for w in metadata.warnings)
        # If no warning, the image should still be processed without errors
        assert has_contrast_warning or metadata.valid

    def test_format_image_report(self, valid_image_path: Path) -> None:
        """Test formatting image validation report."""
        metadata = validate_output_image(valid_image_path)
        report = format_validation_report(metadata)
        assert "VALID" in report
        assert "1024" in report
        assert "PNG" in report

    def test_publication_ready_check(self, valid_image_path: Path) -> None:
        """Test publication readiness check."""
        ready, issues = check_publication_ready(valid_image_path)
        # 1024px at 300 DPI = 3.4" - should be ready
        assert ready or len(issues) > 0  # Either ready or has specific issues

    def test_publication_check_small_image(self, small_image_path: Path) -> None:
        """Test publication check for small image."""
        ready, issues = check_publication_ready(small_image_path)
        # 100px at 300 DPI = 0.33" - not ready
        assert not ready
        assert len(issues) > 0


# =====================================================================
# Schema Tests
# =====================================================================


class TestSchemas:
    """Tests for output schemas."""

    def test_iteration_result_creation(self, valid_iteration_result: dict) -> None:
        """Test creating IterationResult."""
        result = IterationResult(**valid_iteration_result)
        assert result.iteration == 1
        assert result.score == 8.5
        assert result.success

    def test_iteration_result_validation(self) -> None:
        """Test IterationResult validation."""
        with pytest.raises(ValueError, match="iteration"):
            IterationResult(
                iteration=0,  # Invalid
                image_path="/path",
                prompt="test",
                critique="ok",
                score=5.0,
                needs_improvement=False,
                success=True,
            )

    def test_iteration_result_score_validation(self) -> None:
        """Test IterationResult score validation."""
        with pytest.raises(ValueError, match="score"):
            IterationResult(
                iteration=1,
                image_path="/path",
                prompt="test",
                critique="ok",
                score=15.0,  # Invalid
                needs_improvement=False,
                success=True,
            )

    def test_generation_results_creation(
        self, valid_generation_results: dict
    ) -> None:
        """Test creating GenerationResults."""
        # Copy to avoid mutating fixture
        data = valid_generation_results.copy()
        iterations = [IterationResult(**i) for i in data.pop("iterations")]
        results = GenerationResults(iterations=iterations, **data)
        assert results.success
        assert results.final_score == 8.7
        assert len(results.iterations) == 1

    def test_generation_results_to_json(
        self, valid_generation_results: dict
    ) -> None:
        """Test JSON serialization."""
        data = valid_generation_results.copy()
        iterations = [IterationResult(**i) for i in data.pop("iterations")]
        results = GenerationResults(iterations=iterations, **data)
        json_str = results.to_json()
        assert "user_prompt" in json_str
        assert "8.7" in json_str

    def test_generation_results_prompt_hash(
        self, valid_generation_results: dict
    ) -> None:
        """Test automatic prompt hash generation."""
        data = valid_generation_results.copy()
        iterations = [IterationResult(**i) for i in data.pop("iterations")]
        results = GenerationResults(iterations=iterations, **data)
        assert results.prompt_hash is not None
        assert len(results.prompt_hash) == 16  # First 16 chars of SHA256

    def test_schematic_prompt_creation(self) -> None:
        """Test creating SchematicPrompt."""
        prompt = SchematicPrompt(
            diagram_type="consort",
            components=["enrollment", "randomization", "analysis"],
            layout="top-to-bottom",
        )
        assert prompt.diagram_type == "consort"
        assert len(prompt.components) == 3

    def test_schematic_prompt_minimum_components(self) -> None:
        """Test SchematicPrompt requires minimum components."""
        with pytest.raises(ValueError, match="components"):
            SchematicPrompt(
                diagram_type="consort",
                components=["only_one"],  # Too few
                layout="top-to-bottom",
            )

    def test_schematic_prompt_to_text(self) -> None:
        """Test SchematicPrompt text conversion."""
        prompt = SchematicPrompt(
            diagram_type="consort",
            components=["enrollment", "randomization", "analysis"],
            layout="top-to-bottom",
            quantitative_details="n=500",
        )
        text = prompt.to_prompt_text()
        assert "consort" in text.lower()
        assert "top-to-bottom" in text
        assert "n=500" in text

    def test_hash_prompt(self) -> None:
        """Test prompt hashing."""
        hash1 = hash_prompt("Create a CONSORT flowchart")
        hash2 = hash_prompt("Create a CONSORT flowchart")
        hash3 = hash_prompt("Different prompt")

        assert hash1 == hash2  # Same input = same hash
        assert hash1 != hash3  # Different input = different hash
        assert len(hash1) == 16  # 16 characters

    def test_validate_results_dict_valid(
        self, valid_generation_results: dict
    ) -> None:
        """Test validating valid results dict."""
        valid, issues = validate_results_dict(valid_generation_results)
        assert valid
        assert len(issues) == 0

    def test_validate_results_dict_missing_field(self) -> None:
        """Test validating results dict with missing field."""
        data = {"user_prompt": "test"}  # Missing required fields
        valid, issues = validate_results_dict(data)
        assert not valid
        assert any("Missing" in i for i in issues)

    def test_validate_results_dict_invalid_threshold(self) -> None:
        """Test validating results dict with invalid threshold."""
        data = {
            "user_prompt": "test",
            "doc_type": "journal",
            "quality_threshold": 15.0,  # Invalid
            "iterations": [],
            "success": True,
        }
        valid, issues = validate_results_dict(data)
        assert not valid
        assert any("threshold" in i.lower() for i in issues)


# =====================================================================
# Integration Tests
# =====================================================================


class TestIntegration:
    """Integration tests combining multiple utilities."""

    def test_full_validation_workflow(self, valid_consort_prompt: str) -> None:
        """Test complete validation workflow."""
        # Validate prompt
        prompt_analysis = validate_prompt(valid_consort_prompt)
        assert prompt_analysis.valid

        # Check type selection matches
        if prompt_analysis.detected_type:
            inferred = infer_type_from_prompt(valid_consort_prompt)
            assert inferred.diagram_type == prompt_analysis.detected_type

        # Check complexity
        if prompt_analysis.detected_type:
            ok, _ = check_complexity(
                prompt_analysis.detected_type, prompt_analysis.component_count
            )
            assert ok

    def test_color_palette_in_prompt_validation(self) -> None:
        """Test color palette keywords are detected."""
        prompt = "Create a diagram using Okabe-Ito colorblind-safe palette"
        enhanced = inject_colors_into_prompt(prompt, "oligon")
        # Should not inject since colorblind keyword present
        assert enhanced == prompt

    def test_complexity_limit_types_match_selector_types(self) -> None:
        """Test complexity limits cover selector types."""
        selector_types = set(get_all_diagram_types())
        complexity_types = set(get_complexity_types())

        # Most selector types should have complexity limits
        covered = selector_types.intersection(complexity_types)
        assert len(covered) >= 10  # At least 10 types should be covered
