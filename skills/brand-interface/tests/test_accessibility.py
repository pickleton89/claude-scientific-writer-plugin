"""
Tests for check_accessibility.py

Validates WCAG calculations, colorblind simulation, and color accessibility checks.
"""

import sys
from pathlib import Path

import pytest

# Add validation module to path for imports
validation_dir = Path(__file__).parent.parent / "validation"
sys.path.insert(0, str(validation_dir))

from check_accessibility import (
    hex_to_rgb,
    rgb_to_relative_luminance,
    contrast_ratio,
    passes_wcag_aa,
    passes_wcag_aaa,
    to_grayscale,
    grayscale_distance,
    colors_distinguishable_grayscale,
    simulate_colorblind,
    colors_distinguishable_colorblind,
    check_color_pair,
    extract_all_colors,
    AccessibilityResult,
    COLORBLIND_MATRICES,
)


# =============================================================================
# HEX TO RGB CONVERSION
# =============================================================================


class TestHexToRgb:
    """Test hex color to RGB conversion."""

    def test_black(self):
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_red(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_green(self):
        assert hex_to_rgb("#00FF00") == (0, 255, 0)

    def test_blue(self):
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_lowercase(self):
        assert hex_to_rgb("#aabbcc") == (170, 187, 204)

    def test_mixed_case(self):
        assert hex_to_rgb("#AaBbCc") == (170, 187, 204)

    def test_brand_blue(self):
        """Test a typical brand color."""
        assert hex_to_rgb("#2DB2E8") == (45, 178, 232)

    def test_without_hash(self):
        """Function should handle colors without # prefix."""
        assert hex_to_rgb("FF0000") == (255, 0, 0)


# =============================================================================
# RELATIVE LUMINANCE
# =============================================================================


class TestRelativeLuminance:
    """Test WCAG relative luminance calculations."""

    def test_black_luminance(self):
        """Black has minimum luminance (0)."""
        assert rgb_to_relative_luminance(0, 0, 0) == pytest.approx(0.0)

    def test_white_luminance(self):
        """White has maximum luminance (1)."""
        assert rgb_to_relative_luminance(255, 255, 255) == pytest.approx(1.0)

    def test_red_luminance(self):
        """Pure red luminance is 0.2126."""
        assert rgb_to_relative_luminance(255, 0, 0) == pytest.approx(0.2126, rel=0.01)

    def test_green_luminance(self):
        """Pure green luminance is 0.7152."""
        assert rgb_to_relative_luminance(0, 255, 0) == pytest.approx(0.7152, rel=0.01)

    def test_blue_luminance(self):
        """Pure blue luminance is 0.0722."""
        assert rgb_to_relative_luminance(0, 0, 255) == pytest.approx(0.0722, rel=0.01)

    def test_gray_luminance(self):
        """Mid-gray should have ~0.2 luminance."""
        lum = rgb_to_relative_luminance(128, 128, 128)
        assert 0.15 < lum < 0.25


# =============================================================================
# CONTRAST RATIO
# =============================================================================


class TestContrastRatio:
    """Test WCAG contrast ratio calculations."""

    def test_black_white_max_contrast(self):
        """Black and white should have 21:1 contrast."""
        ratio = contrast_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_same_color_no_contrast(self):
        """Same color has 1:1 contrast."""
        ratio = contrast_ratio("#FF0000", "#FF0000")
        assert ratio == pytest.approx(1.0)

    def test_order_independent(self):
        """Contrast ratio should be the same regardless of order."""
        ratio1 = contrast_ratio("#000000", "#FFFFFF")
        ratio2 = contrast_ratio("#FFFFFF", "#000000")
        assert ratio1 == ratio2

    def test_red_on_white(self):
        """Red on white should have good contrast."""
        ratio = contrast_ratio("#FF0000", "#FFFFFF")
        assert ratio > 3.0  # Should pass large text AA

    def test_blue_on_white(self):
        """Pure blue on white passes AA for large text."""
        ratio = contrast_ratio("#0000FF", "#FFFFFF")
        assert ratio > 3.0


# =============================================================================
# WCAG COMPLIANCE
# =============================================================================


class TestWcagCompliance:
    """Test WCAG AA and AAA compliance checks."""

    def test_black_on_white_passes_aa(self):
        assert passes_wcag_aa("#000000", "#FFFFFF") is True

    def test_black_on_white_passes_aaa(self):
        assert passes_wcag_aaa("#000000", "#FFFFFF") is True

    def test_light_gray_on_white_fails_aa(self):
        """Light gray on white has poor contrast."""
        assert passes_wcag_aa("#CCCCCC", "#FFFFFF") is False

    def test_large_text_threshold(self):
        """Large text has lower threshold (3:1 for AA)."""
        # This color might fail regular AA but pass large text AA
        # Medium gray on white
        assert passes_wcag_aa("#777777", "#FFFFFF", is_large_text=True) is True

    def test_aa_threshold_normal_text(self):
        """Normal text needs 4.5:1 for AA."""
        # Find a color that's between 3:1 and 4.5:1
        # Dark gray should be above 4.5:1
        assert passes_wcag_aa("#595959", "#FFFFFF") is True  # ~7:1

    def test_aaa_threshold_normal_text(self):
        """Normal text needs 7:1 for AAA."""
        # Mid-gray might pass AA but fail AAA
        assert passes_wcag_aaa("#767676", "#FFFFFF") is False  # ~4.5:1


# =============================================================================
# GRAYSCALE CONVERSION
# =============================================================================


class TestGrayscale:
    """Test grayscale conversion and distance calculations."""

    def test_black_grayscale(self):
        assert to_grayscale("#000000") == 0

    def test_white_grayscale(self):
        assert to_grayscale("#FFFFFF") == 255

    def test_pure_red_grayscale(self):
        """Red should convert to ~76 (0.299 * 255)."""
        gray = to_grayscale("#FF0000")
        assert 70 < gray < 80

    def test_pure_green_grayscale(self):
        """Green should convert to ~150 (0.587 * 255)."""
        gray = to_grayscale("#00FF00")
        assert 145 < gray < 155

    def test_pure_blue_grayscale(self):
        """Blue should convert to ~29 (0.114 * 255)."""
        gray = to_grayscale("#0000FF")
        assert 25 < gray < 35

    def test_grayscale_distance_black_white(self):
        assert grayscale_distance("#000000", "#FFFFFF") == 255

    def test_grayscale_distance_same_color(self):
        assert grayscale_distance("#FF0000", "#FF0000") == 0

    def test_colors_distinguishable_grayscale(self):
        """Black and white are clearly distinguishable."""
        assert colors_distinguishable_grayscale("#000000", "#FFFFFF") is True

    def test_similar_colors_not_distinguishable(self):
        """Very similar colors may not be distinguishable."""
        assert colors_distinguishable_grayscale("#888888", "#999999") is False


# =============================================================================
# COLORBLIND SIMULATION
# =============================================================================


class TestColorblindSimulation:
    """Test colorblind simulation functions."""

    def test_valid_cvd_types(self):
        """All three CVD types should be supported."""
        assert "protanopia" in COLORBLIND_MATRICES
        assert "deuteranopia" in COLORBLIND_MATRICES
        assert "tritanopia" in COLORBLIND_MATRICES

    def test_simulate_protanopia(self):
        """Red should change under protanopia simulation."""
        original = "#FF0000"
        simulated = simulate_colorblind(original, "protanopia")
        assert simulated != original

    def test_simulate_deuteranopia(self):
        """Green should change under deuteranopia simulation."""
        original = "#00FF00"
        simulated = simulate_colorblind(original, "deuteranopia")
        assert simulated != original

    def test_simulate_tritanopia(self):
        """Blue should change under tritanopia simulation."""
        original = "#0000FF"
        simulated = simulate_colorblind(original, "tritanopia")
        assert simulated != original

    def test_black_unchanged(self):
        """Black should remain black."""
        for cvd_type in COLORBLIND_MATRICES:
            simulated = simulate_colorblind("#000000", cvd_type)
            assert simulated == "#000000"

    def test_white_unchanged(self):
        """White should remain approximately white (within rounding tolerance)."""
        for cvd_type in COLORBLIND_MATRICES:
            simulated = simulate_colorblind("#FFFFFF", cvd_type)
            # Due to floating point math, white may not be exactly #FFFFFF
            # Check each channel is 254 or 255
            r, g, b = hex_to_rgb(simulated)
            assert r >= 254 and g >= 254 and b >= 254

    def test_invalid_cvd_type_raises(self):
        """Invalid CVD type should raise ValueError."""
        with pytest.raises(ValueError):
            simulate_colorblind("#FF0000", "invalid_type")

    def test_colors_distinguishable_colorblind(self):
        """Black and white should be distinguishable under any CVD."""
        for cvd_type in COLORBLIND_MATRICES:
            assert colors_distinguishable_colorblind(
                "#000000", "#FFFFFF", cvd_type
            ) is True


# =============================================================================
# COLOR PAIR ANALYSIS
# =============================================================================


class TestCheckColorPair:
    """Test comprehensive color pair accessibility analysis."""

    def test_black_white_pair(self):
        result = check_color_pair("white", "#FFFFFF", "black", "#000000")
        assert result.passes_aa is True
        assert result.passes_aaa is True
        assert result.grayscale_ok is True
        assert result.colorblind_issues == []
        assert result.fully_accessible is True

    def test_contrast_ratio_stored(self):
        result = check_color_pair("white", "#FFFFFF", "black", "#000000")
        assert result.contrast_ratio == pytest.approx(21.0, rel=0.01)

    def test_grayscale_distance_stored(self):
        result = check_color_pair("white", "#FFFFFF", "black", "#000000")
        assert result.grayscale_distance == 255

    def test_text_and_ui_modes_return_valid_results(self):
        """Both text and UI modes should return valid AccessibilityResult objects."""
        result_ui = check_color_pair("bg", "#FFFFFF", "color", "#767676", is_text=False)
        result_text = check_color_pair("bg", "#FFFFFF", "color", "#767676", is_text=True)
        # Both should return valid boolean AA status
        assert isinstance(result_ui.passes_aa, bool)
        assert isinstance(result_text.passes_aa, bool)
        # Both should have valid contrast ratios
        assert result_ui.contrast_ratio > 0
        assert result_text.contrast_ratio > 0

    def test_accessibility_result_fields(self):
        result = check_color_pair("a", "#FF0000", "b", "#00FF00")
        assert result.color1_name == "a"
        assert result.color1_hex == "#FF0000"
        assert result.color2_name == "b"
        assert result.color2_hex == "#00FF00"


# =============================================================================
# COLOR EXTRACTION
# =============================================================================


class TestExtractAllColors:
    """Test color extraction from token files."""

    def test_extract_from_colors_section(self):
        tokens = {
            "colors": {
                "primary": {
                    "brand_blue": {"hex": "#2DB2E8", "role": "highlight"}
                }
            }
        }
        colors = extract_all_colors(tokens)
        assert "brand_blue" in colors
        assert colors["brand_blue"] == "#2DB2E8"

    def test_extract_from_cycles(self):
        tokens = {
            "color_cycles": {
                "default": {
                    "colors": ["#FF0000", "#00FF00", "#0000FF"]
                }
            }
        }
        colors = extract_all_colors(tokens)
        assert "cycles.default.colors[0]" in colors

    def test_empty_tokens(self):
        colors = extract_all_colors({})
        assert colors == {}

    def test_nested_colors(self):
        tokens = {
            "colors": {
                "structure": {
                    "white": {"hex": "#FFFFFF"},
                    "black": {"hex": "#000000"}
                }
            }
        }
        colors = extract_all_colors(tokens)
        assert "white" in colors
        assert "black" in colors


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_standard_six_digit_hex(self):
        """Standard 6-digit hex format should work correctly."""
        result = hex_to_rgb("#FF0000")
        assert result == (255, 0, 0)

    def test_contrast_ratio_never_below_one(self):
        """Contrast ratio should never be below 1:1."""
        ratio = contrast_ratio("#888888", "#888888")
        assert ratio >= 1.0

    def test_contrast_ratio_never_above_21(self):
        """Contrast ratio should never exceed 21:1."""
        ratio = contrast_ratio("#000000", "#FFFFFF")
        assert ratio <= 21.1  # Small tolerance for floating point

    def test_grayscale_range(self):
        """Grayscale should always be 0-255."""
        for color in ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFFFF"]:
            gray = to_grayscale(color)
            assert 0 <= gray <= 255


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestAccessibilityIntegration:
    """Integration tests for complete accessibility workflows."""

    def test_full_brand_color_analysis(self):
        """Test analyzing a complete set of brand colors."""
        tokens = {
            "colors": {
                "primary": {
                    "brand_blue": {"hex": "#2DB2E8"},
                    "orange": {"hex": "#E67E22"}
                },
                "structure": {
                    "white": {"hex": "#FFFFFF"},
                    "black": {"hex": "#000000"}
                }
            }
        }
        colors = extract_all_colors(tokens)

        # Check all colors against white background
        background = colors.get("white", "#FFFFFF")
        issues = []

        for name, hex_val in colors.items():
            if name == "white":
                continue
            result = check_color_pair("bg", background, name, hex_val)
            if not result.fully_accessible:
                issues.append(name)

        # Should find at least one color to analyze
        assert len(colors) > 0

    def test_colorblind_safe_pair_validation(self):
        """Test validating a declared colorblind-safe pair."""
        # Blue and orange are often colorblind-safe
        result = check_color_pair(
            "blue", "#0000FF",
            "orange", "#FF8800"
        )
        # Should not have all three colorblind issues
        assert len(result.colorblind_issues) < 3
