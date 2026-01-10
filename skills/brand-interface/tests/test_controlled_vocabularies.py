"""
Tests for controlled_vocabularies.py

Validates enums, normalization functions, and validation helpers for deterministic
brand skill configuration.
"""

import sys
from pathlib import Path

import pytest

# Add validation module to path for imports
validation_dir = Path(__file__).parent.parent / "validation"
sys.path.insert(0, str(validation_dir))

from controlled_vocabularies import (
    # Enums
    BrandType,
    ColorRole,
    CycleName,
    FontWeight,
    FontStyle,
    SpinePosition,
    OutputFormat,
    MarkerShape,
    LineStyle,
    # Functions
    normalize_role,
    validate_enum_value,
    get_valid_values,
    validate_brand_type,
    validate_font_weight,
    validate_cycle_name,
    # Constants
    ROLE_ALIASES,
    REQUIRED_CYCLES,
    RECOMMENDED_CYCLES,
    DEFAULT_MARKER_SEQUENCE,
)


# =============================================================================
# BRAND TYPE ENUM
# =============================================================================


class TestBrandType:
    """Test BrandType enum values and usage."""

    def test_all_values_exist(self):
        assert BrandType.ORGANIZATIONAL.value == "organizational"
        assert BrandType.PERSONAL.value == "personal"
        assert BrandType.INSTITUTIONAL.value == "institutional"
        assert BrandType.JOURNAL.value == "journal"
        assert BrandType.GENERIC.value == "generic"

    def test_value_count(self):
        """Ensure we have exactly 5 brand types."""
        assert len(BrandType) == 5

    def test_string_enum(self):
        """BrandType should be a string enum."""
        assert isinstance(BrandType.ORGANIZATIONAL, str)
        # String enums can be compared directly to strings
        assert BrandType.ORGANIZATIONAL == "organizational"
        assert BrandType.ORGANIZATIONAL.value == "organizational"

    def test_from_string(self):
        """Should be able to create from string value."""
        assert BrandType("organizational") == BrandType.ORGANIZATIONAL


# =============================================================================
# COLOR ROLE ENUM
# =============================================================================


class TestColorRole:
    """Test ColorRole enum for semantic color assignments."""

    def test_primary_roles_exist(self):
        assert ColorRole.PRIMARY_HIGHLIGHT.value == "primary-highlight"
        assert ColorRole.SECONDARY_HIGHLIGHT.value == "secondary-highlight"

    def test_data_roles_exist(self):
        assert ColorRole.DATA_PRIMARY.value == "data-primary"
        assert ColorRole.DATA_SECONDARY.value == "data-secondary"
        assert ColorRole.DATA_TERTIARY.value == "data-tertiary"
        assert ColorRole.DATA_CONTROL.value == "data-control"
        assert ColorRole.DATA_TREATMENT.value == "data-treatment"

    def test_directional_roles_exist(self):
        assert ColorRole.DIRECTION_UP.value == "direction-up"
        assert ColorRole.DIRECTION_DOWN.value == "direction-down"
        assert ColorRole.DIRECTION_NEUTRAL.value == "direction-neutral"

    def test_significance_roles_exist(self):
        assert ColorRole.SIGNIFICANT.value == "significant"
        assert ColorRole.NOT_SIGNIFICANT.value == "not-significant"

    def test_heatmap_roles_exist(self):
        assert ColorRole.HEATMAP_POSITIVE.value == "heatmap-positive"
        assert ColorRole.HEATMAP_NEGATIVE.value == "heatmap-negative"
        assert ColorRole.HEATMAP_CENTER.value == "heatmap-center"

    def test_structure_roles_exist(self):
        assert ColorRole.BACKGROUND.value == "background"
        assert ColorRole.AXES.value == "axes"
        assert ColorRole.TEXT.value == "text"
        assert ColorRole.GRIDLINES.value == "gridlines"
        assert ColorRole.ANNOTATIONS.value == "annotations"

    def test_category_roles_exist(self):
        assert ColorRole.CATEGORY_1.value == "category-1"
        assert ColorRole.CATEGORY_2.value == "category-2"
        assert ColorRole.CATEGORY_3.value == "category-3"
        assert ColorRole.CATEGORY_4.value == "category-4"

    def test_role_count(self):
        """Should have substantial number of predefined roles."""
        assert len(ColorRole) >= 20


# =============================================================================
# CYCLE NAME ENUM
# =============================================================================


class TestCycleName:
    """Test CycleName enum for color cycle identification."""

    def test_default_cycle_exists(self):
        assert CycleName.DEFAULT.value == "default"

    def test_standard_cycles_exist(self):
        assert CycleName.TREATMENT_CONTROL.value == "treatment_control"
        assert CycleName.NEUTRALS_ONLY.value == "neutrals_only"
        assert CycleName.OPPOSING.value == "opposing"
        assert CycleName.MULTI_CATEGORY.value == "multi_category"

    def test_visualization_cycles_exist(self):
        assert CycleName.VOLCANO.value == "volcano"
        assert CycleName.HEATMAP.value == "heatmap"
        assert CycleName.CATEGORICAL.value == "categorical"
        assert CycleName.SEQUENTIAL.value == "sequential"
        assert CycleName.DIVERGING.value == "diverging"

    def test_required_cycles_constant(self):
        assert "default" in REQUIRED_CYCLES

    def test_recommended_cycles_constant(self):
        assert "treatment_control" in RECOMMENDED_CYCLES
        assert "neutrals_only" in RECOMMENDED_CYCLES


# =============================================================================
# FONT ENUMS
# =============================================================================


class TestFontWeight:
    """Test FontWeight enum."""

    def test_all_weights_exist(self):
        assert FontWeight.NORMAL.value == "normal"
        assert FontWeight.BOLD.value == "bold"
        assert FontWeight.LIGHT.value == "light"
        assert FontWeight.MEDIUM.value == "medium"
        assert FontWeight.SEMIBOLD.value == "semibold"


class TestFontStyle:
    """Test FontStyle enum."""

    def test_all_styles_exist(self):
        assert FontStyle.NORMAL.value == "normal"
        assert FontStyle.ITALIC.value == "italic"
        assert FontStyle.OBLIQUE.value == "oblique"


# =============================================================================
# LAYOUT ENUMS
# =============================================================================


class TestSpinePosition:
    """Test SpinePosition enum."""

    def test_all_positions_exist(self):
        assert SpinePosition.LEFT.value == "left"
        assert SpinePosition.RIGHT.value == "right"
        assert SpinePosition.TOP.value == "top"
        assert SpinePosition.BOTTOM.value == "bottom"


class TestOutputFormat:
    """Test OutputFormat enum."""

    def test_common_formats_exist(self):
        assert OutputFormat.PNG.value == "PNG"
        assert OutputFormat.PDF.value == "PDF"
        assert OutputFormat.SVG.value == "SVG"
        assert OutputFormat.TIFF.value == "TIFF"


# =============================================================================
# MARKER AND LINE ENUMS
# =============================================================================


class TestMarkerShape:
    """Test MarkerShape enum for matplotlib markers."""

    def test_basic_shapes_exist(self):
        assert MarkerShape.CIRCLE.value == "o"
        assert MarkerShape.SQUARE.value == "s"
        assert MarkerShape.TRIANGLE_UP.value == "^"
        assert MarkerShape.DIAMOND.value == "D"

    def test_default_sequence(self):
        """Default marker sequence should have at least 4 shapes."""
        assert len(DEFAULT_MARKER_SEQUENCE) >= 4
        assert MarkerShape.CIRCLE in DEFAULT_MARKER_SEQUENCE


class TestLineStyle:
    """Test LineStyle enum for matplotlib line styles."""

    def test_all_styles_exist(self):
        assert LineStyle.SOLID.value == "-"
        assert LineStyle.DASHED.value == "--"
        assert LineStyle.DOTTED.value == ":"
        assert LineStyle.DASHDOT.value == "-."


# =============================================================================
# ROLE NORMALIZATION
# =============================================================================


class TestNormalizeRole:
    """Test role normalization from free-text to standardized roles."""

    def test_exact_match(self):
        """Exact standardized role should match."""
        result = normalize_role("data-primary")
        assert result == ColorRole.DATA_PRIMARY

    def test_exact_match_with_spaces(self):
        """Should handle space-to-dash conversion."""
        result = normalize_role("data primary")
        assert result == ColorRole.DATA_PRIMARY

    def test_alias_hero_highlight(self):
        """Legacy 'hero highlight' should normalize to PRIMARY_HIGHLIGHT."""
        result = normalize_role("hero highlight")
        assert result == ColorRole.PRIMARY_HIGHLIGHT

    def test_alias_treatment_groups(self):
        result = normalize_role("treatment groups")
        assert result == ColorRole.DATA_TREATMENT

    def test_alias_control_groups(self):
        result = normalize_role("control groups")
        assert result == ColorRole.DATA_CONTROL

    def test_alias_baselines(self):
        result = normalize_role("baselines")
        assert result == ColorRole.DATA_CONTROL

    def test_alias_annotations(self):
        result = normalize_role("annotations")
        assert result == ColorRole.ANNOTATIONS

    def test_alias_case_insensitive(self):
        """Normalization should be case-insensitive."""
        result = normalize_role("HERO HIGHLIGHT")
        assert result == ColorRole.PRIMARY_HIGHLIGHT

    def test_unknown_role_returns_none(self):
        """Unknown roles should return None."""
        result = normalize_role("completely unknown role")
        assert result is None

    def test_partial_match(self):
        """Partial alias matches should work."""
        result = normalize_role("this is for annotations and notes")
        assert result == ColorRole.ANNOTATIONS


class TestRoleAliases:
    """Test ROLE_ALIASES constant."""

    def test_aliases_map_to_color_roles(self):
        """All alias values should be ColorRole instances."""
        for alias, role in ROLE_ALIASES.items():
            assert isinstance(role, ColorRole)

    def test_common_aliases_exist(self):
        """Common legacy terms should have aliases."""
        assert "hero highlight" in ROLE_ALIASES
        assert "control groups" in ROLE_ALIASES
        assert "annotations" in ROLE_ALIASES


# =============================================================================
# VALIDATION HELPERS
# =============================================================================


class TestValidateEnumValue:
    """Test generic enum value validation."""

    def test_valid_brand_type(self):
        assert validate_enum_value("organizational", BrandType) is True

    def test_invalid_brand_type(self):
        assert validate_enum_value("invalid", BrandType) is False

    def test_valid_font_weight(self):
        assert validate_enum_value("bold", FontWeight) is True

    def test_case_sensitive(self):
        """Validation should be case-sensitive by default."""
        assert validate_enum_value("BOLD", FontWeight) is False


class TestGetValidValues:
    """Test get_valid_values helper."""

    def test_get_brand_types(self):
        values = get_valid_values(BrandType)
        assert "organizational" in values
        assert "personal" in values
        assert len(values) == 5

    def test_get_font_weights(self):
        values = get_valid_values(FontWeight)
        assert "normal" in values
        assert "bold" in values


class TestValidateBrandType:
    """Test validate_brand_type helper."""

    def test_valid_types(self):
        assert validate_brand_type("organizational") is True
        assert validate_brand_type("personal") is True
        assert validate_brand_type("institutional") is True
        assert validate_brand_type("journal") is True
        assert validate_brand_type("generic") is True

    def test_invalid_type(self):
        assert validate_brand_type("invalid") is False
        assert validate_brand_type("") is False


class TestValidateFontWeight:
    """Test validate_font_weight helper."""

    def test_valid_weights(self):
        assert validate_font_weight("normal") is True
        assert validate_font_weight("bold") is True

    def test_invalid_weight(self):
        assert validate_font_weight("extra-bold") is False


class TestValidateCycleName:
    """Test validate_cycle_name with suggestions."""

    def test_standard_cycle_valid(self):
        is_valid, suggestion = validate_cycle_name("default")
        assert is_valid is True
        assert suggestion is None

    def test_treatment_control_valid(self):
        is_valid, suggestion = validate_cycle_name("treatment_control")
        assert is_valid is True
        assert suggestion is None

    def test_hyphenated_suggests_underscore(self):
        """Hyphenated variants should suggest underscore version."""
        is_valid, suggestion = validate_cycle_name("treatment-control")
        assert is_valid is True
        assert suggestion is not None
        assert "treatment_control" in suggestion

    def test_custom_cycle_allowed_with_warning(self):
        """Custom cycle names are allowed but flagged."""
        is_valid, suggestion = validate_cycle_name("my_custom_cycle")
        assert is_valid is True
        assert suggestion is not None
        assert "custom" in suggestion.lower()


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_normalization(self):
        result = normalize_role("")
        assert result is None

    def test_whitespace_only_normalization(self):
        result = normalize_role("   ")
        assert result is None

    def test_special_characters_in_role(self):
        result = normalize_role("role/with/slashes")
        assert result is None

    def test_numeric_role(self):
        result = normalize_role("123")
        assert result is None

    def test_enum_iteration(self):
        """All enums should be iterable."""
        brand_types = list(BrandType)
        assert len(brand_types) > 0

        color_roles = list(ColorRole)
        assert len(color_roles) > 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestVocabularyIntegration:
    """Integration tests for vocabulary system."""

    def test_role_roundtrip(self):
        """Normalized roles should be valid ColorRole values."""
        for alias in ROLE_ALIASES:
            role = normalize_role(alias)
            assert role is not None
            assert isinstance(role, ColorRole)

    def test_cycle_validation_covers_enum(self):
        """All CycleName values should pass validation."""
        for cycle in CycleName:
            is_valid, _ = validate_cycle_name(cycle.value)
            assert is_valid is True

    def test_marker_sequence_are_valid_markers(self):
        """All markers in default sequence should be valid MarkerShape."""
        for marker in DEFAULT_MARKER_SEQUENCE:
            assert isinstance(marker, MarkerShape)

    def test_required_cycles_are_valid(self):
        """All required cycles should be valid CycleName values."""
        for cycle_name in REQUIRED_CYCLES:
            is_valid, _ = validate_cycle_name(cycle_name)
            assert is_valid is True

    def test_recommended_cycles_are_valid(self):
        """All recommended cycles should be valid CycleName values."""
        for cycle_name in RECOMMENDED_CYCLES:
            is_valid, _ = validate_cycle_name(cycle_name)
            assert is_valid is True
