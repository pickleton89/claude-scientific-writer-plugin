"""Tests for model validation and selection utilities.

Phase 2 Test Suite - Core Infrastructure
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils.models import (
    DEFAULT_MODEL,
    VALID_MODELS,
    ModelCapability,
    ModelInfo,
    Priority,
    ValidationResult,
    format_model_list,
    get_cost_tier,
    get_deprecation_message,
    get_model_info,
    get_quality_tier,
    is_deprecated,
    list_models_by_capability,
    select_model,
    supports_editing,
    supports_inpainting,
    validate_model,
)


class TestModelInfo:
    """Tests for ModelInfo dataclass."""

    def test_model_info_creation(self):
        """Test creating ModelInfo with all fields."""
        info = ModelInfo(
            id="test/model",
            display_name="Test Model",
            generation=True,
            editing=True,
            inpainting=False,
            quality_tier="excellent",
            cost_tier="$$",
            max_resolution=2048,
            notes="Test notes",
        )
        assert info.id == "test/model"
        assert info.display_name == "Test Model"
        assert info.generation is True
        assert info.editing is True
        assert info.inpainting is False
        assert info.quality_tier == "excellent"
        assert info.cost_tier == "$$"
        assert info.max_resolution == 2048
        assert info.notes == "Test notes"

    def test_model_info_capabilities_all(self):
        """Test capabilities property with all capabilities."""
        info = ModelInfo(
            id="test/model",
            display_name="Test",
            generation=True,
            editing=True,
            inpainting=True,
            quality_tier="excellent",
            cost_tier="$$",
            max_resolution=2048,
        )
        caps = info.capabilities
        assert ModelCapability.GENERATION in caps
        assert ModelCapability.EDITING in caps
        assert ModelCapability.INPAINTING in caps
        assert len(caps) == 3

    def test_model_info_capabilities_generation_only(self):
        """Test capabilities property with generation only."""
        info = ModelInfo(
            id="test/model",
            display_name="Test",
            generation=True,
            editing=False,
            inpainting=False,
            quality_tier="good",
            cost_tier="$",
            max_resolution=1024,
        )
        caps = info.capabilities
        assert ModelCapability.GENERATION in caps
        assert ModelCapability.EDITING not in caps
        assert ModelCapability.INPAINTING not in caps
        assert len(caps) == 1

    def test_model_info_frozen(self):
        """Test that ModelInfo is immutable."""
        info = ModelInfo(
            id="test/model",
            display_name="Test",
            generation=True,
            editing=False,
            inpainting=False,
            quality_tier="good",
            cost_tier="$",
            max_resolution=1024,
        )
        with pytest.raises(AttributeError):
            info.id = "changed"


class TestValidModels:
    """Tests for VALID_MODELS registry."""

    def test_gemini_in_valid_models(self):
        """Test Gemini model is registered."""
        assert "google/gemini-3-pro-image-preview" in VALID_MODELS

    def test_flux_pro_in_valid_models(self):
        """Test FLUX Pro model is registered."""
        assert "black-forest-labs/flux.2-pro" in VALID_MODELS

    def test_flux_flex_in_valid_models(self):
        """Test FLUX Flex model is registered."""
        assert "black-forest-labs/flux.2-flex" in VALID_MODELS

    def test_all_models_have_required_fields(self):
        """Test all registered models have required fields."""
        for model_id, info in VALID_MODELS.items():
            assert info.id == model_id
            assert info.display_name
            assert isinstance(info.generation, bool)
            assert isinstance(info.editing, bool)
            assert isinstance(info.inpainting, bool)
            assert info.quality_tier in ["excellent", "good", "fair"]
            assert info.cost_tier in ["$", "$$", "$$$"]
            assert info.max_resolution >= 512

    def test_default_model_is_valid(self):
        """Test default model is in valid models."""
        assert DEFAULT_MODEL in VALID_MODELS


class TestValidateModel:
    """Tests for validate_model function."""

    def test_valid_gemini_model(self):
        """Test validating Gemini model."""
        result = validate_model("google/gemini-3-pro-image-preview")
        assert result.valid is True
        assert result.error is None
        assert result.info is not None
        assert result.info.display_name == "Gemini 3 Pro Image"

    def test_valid_flux_pro_model(self):
        """Test validating FLUX Pro model."""
        result = validate_model("black-forest-labs/flux.2-pro")
        assert result.valid is True
        assert result.info.display_name == "FLUX.2 Pro"

    def test_valid_flux_flex_model(self):
        """Test validating FLUX Flex model."""
        result = validate_model("black-forest-labs/flux.2-flex")
        assert result.valid is True
        assert result.info.display_name == "FLUX.2 Flex"

    def test_invalid_model_returns_error(self):
        """Test invalid model returns proper error."""
        result = validate_model("invalid/model")
        assert result.valid is False
        assert result.error is not None
        assert "Invalid model" in result.error

    def test_typo_gemini_suggests_correction(self):
        """Test typo in Gemini model gets suggestion."""
        result = validate_model("gemini-3-pro")
        assert result.valid is False
        assert result.suggestion is not None
        assert "gemini-3-pro-image-preview" in result.suggestion

    def test_typo_flux_pro_suggests_correction(self):
        """Test typo in FLUX Pro model gets suggestion."""
        result = validate_model("flux-pro")
        assert result.valid is False
        assert result.suggestion is not None
        assert "flux.2-pro" in result.suggestion

    def test_typo_flux_flex_suggests_correction(self):
        """Test typo in FLUX Flex model gets suggestion."""
        result = validate_model("flux-flex")
        assert result.valid is False
        assert result.suggestion is not None
        assert "flux.2-flex" in result.suggestion

    def test_partial_match_suggests_correction(self):
        """Test partial match provides suggestion."""
        result = validate_model("gemini")
        assert result.valid is False
        assert result.suggestion is not None

    def test_case_insensitive_typo_detection(self):
        """Test typo detection is case insensitive."""
        result = validate_model("FLUX-PRO")
        assert result.valid is False
        assert result.suggestion is not None

    def test_validation_result_has_correct_model_id(self):
        """Test ValidationResult contains original model ID."""
        result = validate_model("some-invalid-model")
        assert result.model_id == "some-invalid-model"


class TestSelectModel:
    """Tests for select_model function."""

    def test_quality_priority_selects_gemini(self):
        """Test quality priority selects Gemini."""
        model = select_model(priority=Priority.QUALITY)
        assert model == "google/gemini-3-pro-image-preview"

    def test_speed_priority_selects_gemini_since_flux_deprecated(self):
        """Test speed priority selects Gemini (FLUX.2 is deprecated)."""
        model = select_model(priority=Priority.SPEED)
        # FLUX.2 models are deprecated, so Gemini is selected
        assert model == "google/gemini-3-pro-image-preview"

    def test_budget_priority_selects_gemini_since_flux_deprecated(self):
        """Test budget priority selects Gemini (FLUX.2 Flex is deprecated)."""
        model = select_model(priority=Priority.BUDGET)
        # FLUX.2 Flex is deprecated, so Gemini is selected
        assert model == "google/gemini-3-pro-image-preview"

    def test_speed_priority_with_deprecated_models_included(self):
        """Test speed priority selects FLUX Pro when deprecated models included."""
        model = select_model(priority=Priority.SPEED, include_deprecated=True)
        # With deprecated models included, FLUX.2 Pro is selected (excellent quality,
        # alphabetically first among excellent-tier models)
        assert model == "black-forest-labs/flux.2-pro"
        assert is_deprecated(model)

    def test_budget_priority_with_deprecated_models_included(self):
        """Test budget priority selects FLUX Flex when deprecated models included."""
        model = select_model(priority=Priority.BUDGET, include_deprecated=True)
        # With deprecated models included, FLUX.2 Flex is selected (cheapest at $)
        assert model == "black-forest-labs/flux.2-flex"
        assert is_deprecated(model)

    def test_needs_editing_filters_models(self):
        """Test needs_editing filters to editing-capable models."""
        model = select_model(needs_editing=True)
        assert supports_editing(model)

    def test_needs_inpainting_selects_gemini(self):
        """Test needs_inpainting selects Gemini (only option)."""
        model = select_model(needs_inpainting=True)
        assert model == "google/gemini-3-pro-image-preview"

    def test_min_resolution_filters_models(self):
        """Test min_resolution filters models."""
        model = select_model(min_resolution=2048)
        info = get_model_info(model)
        assert info is not None
        assert info.max_resolution >= 2048

    def test_default_priority_is_quality(self):
        """Test default selection uses quality priority."""
        model = select_model()
        assert model == select_model(priority=Priority.QUALITY)

    def test_combined_requirements(self):
        """Test combining multiple requirements."""
        model = select_model(
            priority=Priority.SPEED,
            needs_editing=True,
            min_resolution=1024,
        )
        info = get_model_info(model)
        assert info is not None
        assert info.editing is True
        assert info.max_resolution >= 1024


class TestSupportsEditing:
    """Tests for supports_editing function."""

    def test_gemini_supports_editing(self):
        """Test Gemini supports editing."""
        assert supports_editing("google/gemini-3-pro-image-preview") is True

    def test_flux_pro_supports_editing(self):
        """Test FLUX Pro supports editing."""
        assert supports_editing("black-forest-labs/flux.2-pro") is True

    def test_flux_flex_no_editing(self):
        """Test FLUX Flex does not support editing."""
        assert supports_editing("black-forest-labs/flux.2-flex") is False

    def test_invalid_model_returns_false(self):
        """Test invalid model returns False."""
        assert supports_editing("invalid/model") is False


class TestSupportsInpainting:
    """Tests for supports_inpainting function."""

    def test_gemini_supports_inpainting(self):
        """Test Gemini supports inpainting."""
        assert supports_inpainting("google/gemini-3-pro-image-preview") is True

    def test_flux_pro_no_inpainting(self):
        """Test FLUX Pro does not support inpainting."""
        assert supports_inpainting("black-forest-labs/flux.2-pro") is False

    def test_flux_flex_no_inpainting(self):
        """Test FLUX Flex does not support inpainting."""
        assert supports_inpainting("black-forest-labs/flux.2-flex") is False

    def test_invalid_model_returns_false(self):
        """Test invalid model returns False."""
        assert supports_inpainting("invalid/model") is False


class TestGetModelInfo:
    """Tests for get_model_info function."""

    def test_get_valid_model_info(self):
        """Test getting info for valid model."""
        info = get_model_info("google/gemini-3-pro-image-preview")
        assert info is not None
        assert info.id == "google/gemini-3-pro-image-preview"

    def test_get_invalid_model_returns_none(self):
        """Test getting info for invalid model returns None."""
        info = get_model_info("invalid/model")
        assert info is None


class TestListModelsByCapability:
    """Tests for list_models_by_capability function."""

    def test_list_generation_models(self):
        """Test listing generation-capable models."""
        models = list_models_by_capability(ModelCapability.GENERATION)
        assert len(models) >= 3
        for model in models:
            assert get_model_info(model).generation is True

    def test_list_editing_models(self):
        """Test listing editing-capable models."""
        models = list_models_by_capability(ModelCapability.EDITING)
        assert len(models) >= 2
        for model in models:
            assert get_model_info(model).editing is True

    def test_list_inpainting_models(self):
        """Test listing inpainting-capable models."""
        models = list_models_by_capability(ModelCapability.INPAINTING)
        assert len(models) >= 1
        for model in models:
            assert get_model_info(model).inpainting is True


class TestGetQualityTier:
    """Tests for get_quality_tier function."""

    def test_gemini_quality_tier(self):
        """Test getting Gemini quality tier."""
        tier = get_quality_tier("google/gemini-3-pro-image-preview")
        assert tier == "excellent"

    def test_flux_pro_quality_tier(self):
        """Test getting FLUX Pro quality tier."""
        tier = get_quality_tier("black-forest-labs/flux.2-pro")
        assert tier == "excellent"

    def test_flux_flex_quality_tier(self):
        """Test getting FLUX Flex quality tier."""
        tier = get_quality_tier("black-forest-labs/flux.2-flex")
        assert tier == "good"

    def test_invalid_model_returns_none(self):
        """Test invalid model returns None."""
        tier = get_quality_tier("invalid/model")
        assert tier is None


class TestGetCostTier:
    """Tests for get_cost_tier function."""

    def test_gemini_cost_tier(self):
        """Test getting Gemini cost tier."""
        tier = get_cost_tier("google/gemini-3-pro-image-preview")
        assert tier == "$$"

    def test_flux_flex_cost_tier(self):
        """Test getting FLUX Flex cost tier (budget)."""
        tier = get_cost_tier("black-forest-labs/flux.2-flex")
        assert tier == "$"

    def test_invalid_model_returns_none(self):
        """Test invalid model returns None."""
        tier = get_cost_tier("invalid/model")
        assert tier is None


class TestFormatModelList:
    """Tests for format_model_list function."""

    def test_format_returns_string(self):
        """Test format_model_list returns string."""
        result = format_model_list()
        assert isinstance(result, str)

    def test_format_contains_all_models(self):
        """Test format contains all registered models."""
        result = format_model_list()
        for model_id in VALID_MODELS:
            assert model_id in result

    def test_format_contains_headers(self):
        """Test format contains section headers."""
        result = format_model_list()
        assert "Available Models" in result


class TestPriorityEnum:
    """Tests for Priority enum."""

    def test_quality_value(self):
        """Test QUALITY enum value."""
        assert Priority.QUALITY.value == "quality"

    def test_speed_value(self):
        """Test SPEED enum value."""
        assert Priority.SPEED.value == "speed"

    def test_budget_value(self):
        """Test BUDGET enum value."""
        assert Priority.BUDGET.value == "budget"


class TestModelCapabilityEnum:
    """Tests for ModelCapability enum."""

    def test_generation_value(self):
        """Test GENERATION enum value."""
        assert ModelCapability.GENERATION.value == "generation"

    def test_editing_value(self):
        """Test EDITING enum value."""
        assert ModelCapability.EDITING.value == "editing"

    def test_inpainting_value(self):
        """Test INPAINTING enum value."""
        assert ModelCapability.INPAINTING.value == "inpainting"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result_creation(self):
        """Test creating valid ValidationResult."""
        result = ValidationResult(
            valid=True,
            model_id="test/model",
            info=VALID_MODELS["google/gemini-3-pro-image-preview"],
        )
        assert result.valid is True
        assert result.model_id == "test/model"
        assert result.error is None
        assert result.suggestion is None
        assert result.info is not None

    def test_invalid_result_with_error(self):
        """Test creating invalid ValidationResult with error."""
        result = ValidationResult(
            valid=False,
            model_id="bad/model",
            error="Invalid model",
            suggestion="Try this instead",
        )
        assert result.valid is False
        assert result.error == "Invalid model"
        assert result.suggestion == "Try this instead"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_model_id(self):
        """Test validating empty model ID."""
        result = validate_model("")
        assert result.valid is False

    def test_whitespace_model_id(self):
        """Test validating whitespace model ID."""
        result = validate_model("   ")
        assert result.valid is False

    def test_unicode_model_id(self):
        """Test validating unicode model ID."""
        result = validate_model("模型/测试")
        assert result.valid is False

    def test_very_long_model_id(self):
        """Test validating very long model ID."""
        result = validate_model("a" * 1000)
        assert result.valid is False

    def test_select_with_impossible_requirements(self):
        """Test selection with impossible requirements returns default."""
        # No model has resolution > 10000
        model = select_model(min_resolution=10000)
        assert model == DEFAULT_MODEL


class TestDeprecation:
    """Tests for model deprecation features."""

    def test_flux_pro_is_deprecated(self):
        """Test FLUX.2 Pro is marked as deprecated."""
        assert is_deprecated("black-forest-labs/flux.2-pro") is True

    def test_flux_flex_is_deprecated(self):
        """Test FLUX.2 Flex is marked as deprecated."""
        assert is_deprecated("black-forest-labs/flux.2-flex") is True

    def test_gemini_not_deprecated(self):
        """Test Gemini is not deprecated."""
        assert is_deprecated("google/gemini-3-pro-image-preview") is False

    def test_invalid_model_not_deprecated(self):
        """Test invalid model returns False for is_deprecated."""
        assert is_deprecated("invalid/model") is False

    def test_get_deprecation_message_for_deprecated_model(self):
        """Test get_deprecation_message returns message for deprecated model."""
        msg = get_deprecation_message("black-forest-labs/flux.2-pro")
        assert msg is not None
        assert "deprecated" in msg.lower() or "FLUX" in msg

    def test_get_deprecation_message_for_active_model(self):
        """Test get_deprecation_message returns None for active model."""
        msg = get_deprecation_message("google/gemini-3-pro-image-preview")
        assert msg is None

    def test_get_deprecation_message_for_invalid_model(self):
        """Test get_deprecation_message returns None for invalid model."""
        msg = get_deprecation_message("invalid/model")
        assert msg is None

    def test_validate_deprecated_model_returns_warning(self):
        """Test validate_model returns deprecation_warning for deprecated model."""
        result = validate_model("black-forest-labs/flux.2-pro", warn_deprecated=False)
        assert result.valid is True
        assert result.deprecation_warning is not None
        assert "deprecated" in result.deprecation_warning.lower() or "FLUX" in result.deprecation_warning

    def test_validate_active_model_no_warning(self):
        """Test validate_model returns no warning for active model."""
        result = validate_model("google/gemini-3-pro-image-preview")
        assert result.valid is True
        assert result.deprecation_warning is None

    def test_validate_deprecated_model_emits_warning(self):
        """Test validate_model emits DeprecationWarning for deprecated model."""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_model("black-forest-labs/flux.2-pro", warn_deprecated=True)
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "FLUX.2 Pro" in str(w[0].message)

    def test_validate_deprecated_model_no_warning_when_disabled(self):
        """Test validate_model does not emit warning when warn_deprecated=False."""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_model("black-forest-labs/flux.2-pro", warn_deprecated=False)
            assert len(w) == 0

    def test_model_info_deprecated_field(self):
        """Test ModelInfo has deprecated field."""
        info = get_model_info("black-forest-labs/flux.2-pro")
        assert info is not None
        assert info.deprecated is True
        assert info.deprecation_message != ""

    def test_model_info_active_not_deprecated(self):
        """Test active ModelInfo has deprecated=False."""
        info = get_model_info("google/gemini-3-pro-image-preview")
        assert info is not None
        assert info.deprecated is False

    def test_format_model_list_shows_deprecated(self):
        """Test format_model_list shows DEPRECATED tag."""
        output = format_model_list()
        assert "[DEPRECATED]" in output
        # Check FLUX models are marked as deprecated
        assert "FLUX.2 Pro" in output
        assert "FLUX.2 Flex" in output

    def test_select_model_excludes_deprecated_by_default(self):
        """Test select_model excludes deprecated models by default."""
        # All priorities should return Gemini since FLUX models are deprecated
        for priority in Priority:
            model = select_model(priority=priority)
            assert not is_deprecated(model), f"Priority {priority} selected deprecated model"
