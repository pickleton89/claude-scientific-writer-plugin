"""Test suite for scientific-slides deterministic validation utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from validate_slide_image import SlideImageValidator
from validate_slide_plan import SlidePlanValidator
from hybrid_quality_scorer import HybridQualityScorer, format_score_report
from prompt_templates import PromptTemplateEngine


# =============================================================================
# SlideImageValidator Tests
# =============================================================================


class TestSlideImageValidator:
    """Tests for SlideImageValidator class."""

    def test_valid_image_passes(self, valid_slide_image: Path) -> None:
        """Test that a valid 1920x1080 slide image passes validation."""
        validator = SlideImageValidator()
        result = validator.validate(str(valid_slide_image))

        assert result.passed
        assert result.score >= 5.0
        assert result.checks["aspect_ratio"]
        assert result.checks["min_dimensions"]
        assert result.checks["preferred_dimensions"]

    def test_nonexistent_file_fails(self, tmp_path: Path) -> None:
        """Test that a nonexistent file fails validation."""
        validator = SlideImageValidator()
        result = validator.validate(str(tmp_path / "nonexistent.png"))

        assert not result.passed
        assert result.score == 0
        assert "File not found" in result.errors[0]

    def test_small_image_fails(self, small_slide_image: Path) -> None:
        """Test that an undersized image fails validation."""
        validator = SlideImageValidator()
        result = validator.validate(str(small_slide_image))

        assert not result.checks["min_dimensions"]
        assert any("below minimum" in e for e in result.errors)

    def test_wrong_aspect_ratio_warns(self, square_slide_image: Path) -> None:
        """Test that wrong aspect ratio generates warning."""
        validator = SlideImageValidator()
        result = validator.validate(str(square_slide_image))

        assert not result.checks["aspect_ratio"]
        assert any("aspect" in w.lower() for w in result.warnings)

    def test_low_contrast_detected(self, low_contrast_image: Path) -> None:
        """Test that low contrast is detected."""
        validator = SlideImageValidator()
        result = validator.validate(str(low_contrast_image))

        assert result.details["contrast_score"] < 0.5

    def test_high_contrast_detected(self, high_contrast_image: Path) -> None:
        """Test that high contrast is detected."""
        validator = SlideImageValidator()
        result = validator.validate(str(high_contrast_image))

        assert result.details["contrast_score"] > 0.5
        assert result.checks["adequate_contrast"]

    def test_brand_color_compliance(
        self, valid_slide_image: Path, brand_colors: list[str]
    ) -> None:
        """Test brand color compliance checking."""
        validator = SlideImageValidator()
        result = validator.validate(str(valid_slide_image), expected_colors=brand_colors)

        # White image should match white in brand colors
        assert "brand_compliance" in result.details

    def test_white_space_estimation(self, create_test_image) -> None:
        """Test white space percentage calculation."""
        # Create a pure white image for white space testing
        white_image = create_test_image(1920, 1080, (255, 255, 255), "white.png", add_content=False)
        validator = SlideImageValidator()
        result = validator.validate(str(white_image))

        # Pure white image should have ~100% white space
        assert result.details["white_space_percent"] > 90

    def test_dominant_colors_extracted(self, valid_slide_image: Path) -> None:
        """Test that dominant colors are extracted."""
        validator = SlideImageValidator()
        result = validator.validate(str(valid_slide_image))

        assert "dominant_colors" in result.details
        assert len(result.details["dominant_colors"]) > 0
        # White image should have white as dominant
        assert result.details["dominant_colors"][0] == "#ffffff"

    def test_score_components(self, valid_slide_image: Path) -> None:
        """Test that score is calculated from components."""
        validator = SlideImageValidator()
        result = validator.validate(str(valid_slide_image))

        # Valid image should score well on most components
        # Max score is 10, valid image should be 7+
        assert result.score >= 7.0

    def test_file_size_check(self, create_test_image) -> None:
        """Test file size validation."""
        # Create a valid image with content (larger file size)
        img_path = create_test_image(1920, 1080, add_content=True)
        validator = SlideImageValidator()
        result = validator.validate(str(img_path))

        assert "file_size_kb" in result.details
        # Content images should pass size checks
        assert result.checks["file_size_max"]
        # Note: simple test images may still be small, check that bounds work
        assert result.details["file_size_kb"] > 0


# =============================================================================
# SlidePlanValidator Tests
# =============================================================================


class TestSlidePlanValidator:
    """Tests for SlidePlanValidator class."""

    def test_valid_plan_passes(self, valid_slide_plan: dict[str, Any]) -> None:
        """Test that a valid slide plan passes validation."""
        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(valid_slide_plan)

        assert is_valid
        assert len(errors) == 0

    def test_minimal_plan_passes(self, minimal_slide_plan: dict[str, Any]) -> None:
        """Test that a minimal valid plan passes."""
        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(minimal_slide_plan)

        assert is_valid
        assert len(errors) == 0

    def test_missing_title_slide_warns(self) -> None:
        """Test that missing title slide generates warning."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test",
            "slides": [
                {"slide_type": "content", "title": "Intro"},
                {"slide_type": "conclusion", "title": "End"},
            ],
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("title" in w.lower() for w in warnings)

    def test_missing_conclusion_slide_warns(self) -> None:
        """Test that missing conclusion slide generates warning for conference."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test",
            "slides": [
                {"slide_type": "title", "title": "Title"},
                {"slide_type": "content", "title": "Content"},
            ],
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("conclusion" in w.lower() for w in warnings)

    def test_too_many_slides_warns(self, plan_too_many_slides: dict[str, Any]) -> None:
        """Test that excessive slide count generates warning."""
        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan_too_many_slides)

        assert any("exceeds" in w.lower() for w in warnings)

    def test_too_few_slides_warns(self, plan_too_few_slides: dict[str, Any]) -> None:
        """Test that insufficient slide count generates warning."""
        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan_too_few_slides)

        assert any("below" in w.lower() for w in warnings)

    def test_too_many_bullet_points_warns(
        self, minimal_slide_plan: dict[str, Any], slide_with_many_points: dict[str, Any]
    ) -> None:
        """Test that too many bullet points generates warning."""
        plan = minimal_slide_plan.copy()
        plan["slides"] = [slide_with_many_points]

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("bullet points" in w.lower() for w in warnings)

    def test_invalid_color_format_errors(self) -> None:
        """Test that invalid hex color generates error."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test",
            "slides": [{"slide_type": "title", "title": "Title"}],
            "formatting": {"background_color": "not-a-color"},
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert not is_valid
        assert any("hex color" in e.lower() for e in errors)

    def test_valid_color_formats(self, valid_slide_plan: dict[str, Any]) -> None:
        """Test that valid hex colors pass validation."""
        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(valid_slide_plan)

        assert is_valid
        assert not any("hex color" in e.lower() for e in errors)

    def test_slide_count_guidelines(self) -> None:
        """Test slide count guidelines lookup."""
        validator = SlidePlanValidator()

        # Test exact durations
        assert validator._get_slide_guidelines(15) == (13, 16, 20)
        assert validator._get_slide_guidelines(30) == (22, 27, 33)

        # Test interpolation to nearest
        guidelines = validator._get_slide_guidelines(12)
        assert guidelines is not None

    def test_recommendations(self, plan_too_few_slides: dict[str, Any]) -> None:
        """Test that recommendations are generated."""
        validator = SlidePlanValidator()
        recs = validator.get_recommendations(plan_too_few_slides)

        assert "slide_count" in recs
        assert "suggestions" in recs
        assert len(recs["suggestions"]) > 0

    def test_long_title_warns(self) -> None:
        """Test that overly long slide titles generate warnings."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test",
            "slides": [
                {"slide_type": "content", "title": "A" * 100}  # 100 chars
            ],
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("80 characters" in w for w in warnings)


# =============================================================================
# HybridQualityScorer Tests
# =============================================================================


class TestHybridQualityScorer:
    """Tests for HybridQualityScorer class."""

    def test_hybrid_score_calculation(self, valid_slide_image: Path) -> None:
        """Test that hybrid scoring correctly weights components."""
        scorer = HybridQualityScorer(
            deterministic_weight=0.4, ai_weight=0.6, threshold=6.5
        )

        result = scorer.score(str(valid_slide_image), ai_score=8.0)

        # Score should be weighted average
        expected_min = 0.4 * 5.0 + 0.6 * 8.0  # If det score is at least 5
        assert result.total_score >= expected_min - 0.5
        assert result.ai_score == 8.0

    def test_weights_must_sum_to_one(self) -> None:
        """Test that weights must sum to 1.0."""
        with pytest.raises(ValueError):
            HybridQualityScorer(deterministic_weight=0.5, ai_weight=0.3)

    def test_threshold_check(self, valid_slide_image: Path) -> None:
        """Test that threshold is correctly applied."""
        scorer = HybridQualityScorer(threshold=6.5)
        result = scorer.score(str(valid_slide_image), ai_score=8.0)

        # With good deterministic and AI scores, should pass
        assert result.passed_threshold

    def test_low_ai_score_fails(self, valid_slide_image: Path) -> None:
        """Test that low AI score causes failure."""
        scorer = HybridQualityScorer(threshold=6.5)
        result = scorer.score(str(valid_slide_image), ai_score=2.0)

        # Even with good deterministic, low AI should fail
        assert not result.passed_threshold

    def test_should_regenerate_on_error(self, tmp_path: Path) -> None:
        """Test that errors trigger regeneration."""
        from PIL import Image

        # Create undersized image
        img = Image.new("RGB", (640, 480), color="white")
        img_path = tmp_path / "small.png"
        img.save(img_path)

        scorer = HybridQualityScorer()
        result = scorer.score(str(img_path), ai_score=8.0)

        should_regen, reason = scorer.should_regenerate(result)
        assert should_regen
        assert "Deterministic" in reason or "validation" in reason.lower()

    def test_should_not_regenerate_on_success(self, valid_slide_image: Path) -> None:
        """Test that good scores don't trigger regeneration."""
        scorer = HybridQualityScorer(threshold=6.0)
        result = scorer.score(str(valid_slide_image), ai_score=8.0)

        should_regen, reason = scorer.should_regenerate(result)
        assert not should_regen
        assert "acceptable" in reason.lower()

    def test_improvement_suggestions(self, low_contrast_image: Path) -> None:
        """Test that improvement suggestions are generated."""
        scorer = HybridQualityScorer()
        result = scorer.score(str(low_contrast_image), ai_score=6.0)

        suggestions = scorer.get_improvement_suggestions(result)
        assert isinstance(suggestions, list)

    def test_ai_score_clamped(self, valid_slide_image: Path) -> None:
        """Test that AI scores are clamped to 0-10."""
        scorer = HybridQualityScorer()

        result = scorer.score(str(valid_slide_image), ai_score=15.0)
        assert result.ai_score == 10.0

        result = scorer.score(str(valid_slide_image), ai_score=-5.0)
        assert result.ai_score == 0.0

    def test_format_score_report(self, valid_slide_image: Path) -> None:
        """Test score report formatting."""
        scorer = HybridQualityScorer()
        result = scorer.score(str(valid_slide_image), ai_score=7.5)

        report = format_score_report(result)
        assert "Total Score:" in report
        assert "Deterministic:" in report
        assert "AI Review:" in report

    def test_details_structure(self, valid_slide_image: Path) -> None:
        """Test that details contain expected structure."""
        scorer = HybridQualityScorer()
        result = scorer.score(str(valid_slide_image), ai_score=7.0, ai_feedback="Good")

        assert "deterministic_breakdown" in result.details
        assert "ai_breakdown" in result.details
        assert "threshold" in result.details
        assert result.details["ai_breakdown"]["feedback"] == "Good"


# =============================================================================
# PromptTemplateEngine Tests
# =============================================================================


class TestPromptTemplateEngine:
    """Tests for PromptTemplateEngine class."""

    def test_generate_content_slide_prompt(self) -> None:
        """Test generating prompt for content slide."""
        engine = PromptTemplateEngine()
        slide = {
            "slide_type": "content",
            "title": "Background",
            "key_points": ["Point 1", "Point 2"],
        }

        prompt = engine.generate_slide_prompt(slide)

        assert "SLIDE TYPE: CONTENT" in prompt
        assert "TITLE: Background" in prompt
        assert "Point 1" in prompt
        assert "Point 2" in prompt

    def test_generate_title_slide_prompt(self) -> None:
        """Test generating prompt for title slide."""
        engine = PromptTemplateEngine()
        slide = {
            "slide_type": "title",
            "title": "My Presentation",
            "speaker": "Dr. Smith",
            "affiliation": "University",
        }

        prompt = engine.generate_slide_prompt(slide)

        assert "My Presentation" in prompt
        assert "Dr. Smith" in prompt
        assert "University" in prompt

    def test_generate_section_slide_prompt(self) -> None:
        """Test generating prompt for section slide."""
        engine = PromptTemplateEngine()
        slide = {
            "slide_type": "section",
            "title": "Methods",
            "subtitle": "Experimental Design",
        }

        prompt = engine.generate_slide_prompt(slide)

        assert "Methods" in prompt
        assert "Experimental Design" in prompt

    def test_generate_visual_only_prompt(self) -> None:
        """Test generating visual-only prompt."""
        engine = PromptTemplateEngine()
        prompt = engine.generate_visual_prompt("Neural network architecture diagram")

        assert "Neural network architecture diagram" in prompt
        assert "visual" in prompt.lower()

    def test_custom_formatting(self) -> None:
        """Test that custom formatting is applied."""
        formatting = {
            "background_color": "#000000",
            "accent_color": "#FF0000",
            "style": "modern",
        }
        engine = PromptTemplateEngine(formatting=formatting)
        slide = {"slide_type": "content", "title": "Test"}

        prompt = engine.generate_slide_prompt(slide)

        assert "#000000" in prompt
        assert "#FF0000" in prompt
        assert "modern" in prompt

    def test_batch_prompts(self, valid_slide_plan: dict[str, Any]) -> None:
        """Test generating batch prompts from plan."""
        engine = PromptTemplateEngine()
        prompts = engine.generate_batch_prompts(valid_slide_plan)

        assert len(prompts) == len(valid_slide_plan["slides"])
        for slide_num, prompt, slide_data in prompts:
            assert slide_num > 0
            assert isinstance(prompt, str)
            assert len(prompt) > 50

    def test_citations_included(self) -> None:
        """Test that citations are included in prompt."""
        engine = PromptTemplateEngine()
        slide = {
            "slide_type": "content",
            "title": "Background",
            "citations": ["(Smith, 2023)", "(Jones, 2022)"],
        }

        prompt = engine.generate_slide_prompt(slide)

        assert "(Smith, 2023)" in prompt
        assert "(Jones, 2022)" in prompt
        assert "CITATIONS" in prompt

    def test_white_space_guidance_varies(self) -> None:
        """Test that white space guidance varies with content density."""
        engine = PromptTemplateEngine()

        # Few points
        slide_few = {"slide_type": "content", "title": "Test", "key_points": ["One"]}
        prompt_few = engine.generate_slide_prompt(slide_few)

        # Many points
        slide_many = {
            "slide_type": "content",
            "title": "Test",
            "key_points": ["1", "2", "3", "4", "5"],
        }
        prompt_many = engine.generate_slide_prompt(slide_many)

        assert "50%" in prompt_few  # High white space
        assert "breathing room" in prompt_many or "Balanced" in prompt_many

    def test_slide_type_options(self) -> None:
        """Test getting available slide types."""
        engine = PromptTemplateEngine()
        options = engine.get_slide_type_options()

        assert "title" in options
        assert "content" in options
        assert "conclusion" in options

    def test_style_options(self) -> None:
        """Test getting available style options."""
        engine = PromptTemplateEngine()
        options = engine.get_style_options()

        assert "minimal" in options
        assert "modern" in options
        assert "academic" in options

    def test_speaker_injected_from_plan(self) -> None:
        """Test that speaker is injected into title slides from plan metadata."""
        engine = PromptTemplateEngine()
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test Talk",
            "speaker": "Dr. Plan Speaker",
            "affiliation": "Plan University",
            "slides": [{"slide_type": "title", "title": "Test Talk"}],
        }

        prompts = engine.generate_batch_prompts(plan)
        _, title_prompt, _ = prompts[0]

        assert "Dr. Plan Speaker" in title_prompt
        assert "Plan University" in title_prompt


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_validation_pipeline(
        self, valid_slide_plan: dict[str, Any], valid_slide_image: Path
    ) -> None:
        """Test running full validation pipeline."""
        # Validate plan
        plan_validator = SlidePlanValidator()
        plan_valid, plan_errors, plan_warnings = plan_validator.validate(valid_slide_plan)
        assert plan_valid

        # Generate prompts
        engine = PromptTemplateEngine()
        prompts = engine.generate_batch_prompts(valid_slide_plan)
        assert len(prompts) > 0

        # Validate image
        img_validator = SlideImageValidator()
        img_result = img_validator.validate(str(valid_slide_image))
        assert img_result.passed

        # Hybrid score
        scorer = HybridQualityScorer()
        hybrid_result = scorer.score(str(valid_slide_image), ai_score=7.5)
        assert hybrid_result.passed_threshold

    def test_regeneration_decision_flow(self, valid_slide_image: Path) -> None:
        """Test the regeneration decision flow."""
        scorer = HybridQualityScorer(threshold=6.5)

        # Good score - no regeneration
        good_result = scorer.score(str(valid_slide_image), ai_score=8.0)
        should_regen, reason = scorer.should_regenerate(good_result)
        assert not should_regen

        # Low AI score - regeneration
        low_result = scorer.score(str(valid_slide_image), ai_score=3.0)
        should_regen, reason = scorer.should_regenerate(low_result)
        assert should_regen
        assert "AI score" in reason

    def test_prompt_to_validation_consistency(
        self, valid_slide_plan: dict[str, Any]
    ) -> None:
        """Test that prompts mention formatting that validator checks."""
        engine = PromptTemplateEngine()
        prompts = engine.generate_batch_prompts(valid_slide_plan)

        for _, prompt, slide_data in prompts:
            # Prompts should mention aspect ratio (validator checks this)
            assert "16:9" in prompt
            # Content slides (not section dividers) should mention margins/layout
            if slide_data.get("slide_type") not in ["section", "title"]:
                assert "margin" in prompt.lower() or "white space" in prompt.lower()
