"""
Comprehensive test suite for research-posters validation utilities.

Tests cover:
- Brand color utilities and contrast calculation
- Poster dimension handling
- Schema validation
- Word counting from LaTeX
- Accessibility validation
- Spec file validation
"""

import pytest

# Import modules under test
from utils.brand_colors import (
    hex_to_rgb,
    rgb_to_hex,
    calculate_contrast_ratio,
    check_wcag_compliance,
    simulate_deuteranopia,
    simulate_protanopia,
    get_distinguishable_pairs,
    validate_poster_palette,
)
from utils.dimensions import (
    pts_to_inches,
    inches_to_pts,
    get_poster_size,
    match_dimensions,
    validate_dimensions,
    get_recommended_font_sizes,
    calculate_dpi_for_image,
    POSTER_SIZES,
    Orientation,
)
from utils.schemas import (
    ValidationStatus,
    ValidationResult,
    WordCountResult,
    ContrastCheckResult,
    ImageCheckResult,
    FontCheckResult,
    QualityReport,
    PosterSpec,
)


# =============================================================================
# Brand Colors Tests
# =============================================================================


class TestHexRgbConversion:
    """Tests for hex/RGB color conversion."""

    def test_hex_to_rgb_basic(self):
        """Test basic hex to RGB conversion."""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_hex_to_rgb_without_hash(self):
        """Test hex conversion without # prefix."""
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_hex_to_rgb_lowercase(self):
        """Test hex conversion with lowercase."""
        assert hex_to_rgb("#ff00ff") == (255, 0, 255)

    def test_hex_to_rgb_oligon_blue(self):
        """Test conversion of Oligon brand blue."""
        assert hex_to_rgb("#2DB2E8") == (45, 178, 232)

    def test_hex_to_rgb_invalid(self):
        """Test invalid hex raises ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#GGG")

    def test_rgb_to_hex_basic(self):
        """Test basic RGB to hex conversion."""
        assert rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert rgb_to_hex((0, 255, 0)) == "#00ff00"

    def test_rgb_to_hex_mixed(self):
        """Test RGB to hex with mixed values."""
        assert rgb_to_hex((45, 178, 232)) == "#2db2e8"

    def test_rgb_to_hex_invalid_range(self):
        """Test invalid RGB values raise ValueError."""
        with pytest.raises(ValueError):
            rgb_to_hex((256, 0, 0))
        with pytest.raises(ValueError):
            rgb_to_hex((-1, 0, 0))

    def test_roundtrip_conversion(self):
        """Test hex -> RGB -> hex roundtrip."""
        original = "#2DB2E8"
        rgb = hex_to_rgb(original)
        result = rgb_to_hex(rgb)
        assert result.upper() == original.lower() or result.lower() == original.lower()


class TestContrastRatio:
    """Tests for WCAG contrast ratio calculation."""

    def test_black_white_contrast(self):
        """Test maximum contrast (black on white)."""
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert ratio == 21.0

    def test_same_color_contrast(self):
        """Test minimum contrast (same color)."""
        ratio = calculate_contrast_ratio("#808080", "#808080")
        assert ratio == 1.0

    def test_oligon_blue_on_white(self, oligon_colors):
        """Test Oligon blue contrast on white."""
        ratio = calculate_contrast_ratio(oligon_colors["brand_blue"], "#FFFFFF")
        assert 2.0 < ratio < 3.0  # Known to be around 2.48

    def test_dark_gray_on_white(self, oligon_colors):
        """Test dark gray contrast on white (should pass WCAG)."""
        ratio = calculate_contrast_ratio(oligon_colors["dark_gray"], "#FFFFFF")
        assert ratio > 4.5  # Should pass WCAG AA

    def test_symmetric_calculation(self):
        """Test contrast calculation is symmetric."""
        ratio1 = calculate_contrast_ratio("#FF0000", "#0000FF")
        ratio2 = calculate_contrast_ratio("#0000FF", "#FF0000")
        assert ratio1 == ratio2


class TestWCAGCompliance:
    """Tests for WCAG compliance checking."""

    def test_high_contrast_passes_all(self, high_contrast_pair):
        """Test high contrast passes all WCAG levels."""
        result = check_wcag_compliance(
            high_contrast_pair["foreground"],
            high_contrast_pair["background"],
        )
        assert result.aa_normal is True
        assert result.aa_large is True
        assert result.aaa_normal is True
        assert result.aaa_large is True

    def test_low_contrast_fails(self, low_contrast_pair):
        """Test low contrast fails WCAG."""
        result = check_wcag_compliance(
            low_contrast_pair["foreground"],
            low_contrast_pair["background"],
        )
        assert result.aa_normal is False

    def test_returns_ratio(self, high_contrast_pair):
        """Test compliance result includes contrast ratio."""
        result = check_wcag_compliance(
            high_contrast_pair["foreground"],
            high_contrast_pair["background"],
        )
        assert result.contrast_ratio == 21.0


class TestColorblindSimulation:
    """Tests for colorblind simulation functions."""

    def test_deuteranopia_changes_red(self):
        """Test deuteranopia simulation changes red."""
        original = "#FF0000"
        simulated = simulate_deuteranopia(original)
        assert simulated != original.lower()

    def test_protanopia_changes_red(self):
        """Test protanopia simulation changes red."""
        original = "#FF0000"
        simulated = simulate_protanopia(original)
        assert simulated != original.lower()

    def test_gray_unchanged(self):
        """Test gray colors are relatively unchanged."""
        gray = "#808080"
        deut = simulate_deuteranopia(gray)
        # Gray should stay relatively gray (R ~= G ~= B)
        r, g, b = hex_to_rgb(deut)
        assert abs(r - g) < 30 and abs(g - b) < 30

    def test_distinguishable_pairs_detects_safe(self, colorblind_safe_palette):
        """Test distinguishable pairs identifies safe combinations."""
        pairs = get_distinguishable_pairs(colorblind_safe_palette)
        # Blue and orange should be distinguishable
        all_distinguishable = all(is_dist for _, _, is_dist in pairs)
        assert all_distinguishable is True


class TestPaletteValidation:
    """Tests for complete palette validation."""

    def test_validate_oligon_palette(self, oligon_colors):
        """Test Oligon brand palette validation."""
        colors = [oligon_colors["dark_gray"], oligon_colors["brand_blue"]]
        result = validate_poster_palette(colors, background="#FFFFFF")
        assert "contrast_checks" in result
        assert len(result["contrast_checks"]) == 2

    def test_validate_returns_overall_status(self, oligon_colors):
        """Test palette validation returns overall pass status."""
        colors = [oligon_colors["dark_gray"]]
        result = validate_poster_palette(colors)
        assert "overall_pass" in result


# =============================================================================
# Dimensions Tests
# =============================================================================


class TestPointInchConversion:
    """Tests for point/inch conversion."""

    def test_pts_to_inches_72(self):
        """Test 72 points = 1 inch."""
        assert pts_to_inches(72) == 1.0

    def test_inches_to_pts_1(self):
        """Test 1 inch = 72 points."""
        assert inches_to_pts(1.0) == 72.0

    def test_roundtrip_conversion(self):
        """Test pts -> inches -> pts roundtrip."""
        original = 2384
        result = inches_to_pts(pts_to_inches(original))
        assert abs(result - original) < 0.01


class TestPosterSizeLookup:
    """Tests for poster size lookup."""

    def test_get_a0_size(self):
        """Test A0 size lookup."""
        size = get_poster_size("A0")
        assert size is not None
        assert size.name == "A0"
        assert size.width_pts == 2384
        assert size.height_pts == 3370

    def test_get_size_case_insensitive(self):
        """Test size lookup is case insensitive."""
        size1 = get_poster_size("a0")
        size2 = get_poster_size("A0")
        assert size1 == size2

    def test_get_nonexistent_size(self):
        """Test lookup of nonexistent size returns None."""
        assert get_poster_size("INVALID") is None

    def test_all_sizes_have_required_fields(self):
        """Test all defined sizes have required fields."""
        for name, size in POSTER_SIZES.items():
            assert size.width_inches > 0
            assert size.height_inches > 0
            assert size.width_pts > 0
            assert size.height_pts > 0


class TestDimensionMatching:
    """Tests for dimension matching."""

    def test_match_a0_portrait(self, a0_portrait_pts):
        """Test matching A0 portrait dimensions."""
        result = match_dimensions(a0_portrait_pts["width"], a0_portrait_pts["height"])
        assert result.matched is True
        assert result.size_name == "A0"
        assert result.orientation == Orientation.PORTRAIT

    def test_match_a0_landscape(self, a0_landscape_pts):
        """Test matching A0 landscape dimensions."""
        result = match_dimensions(a0_landscape_pts["width"], a0_landscape_pts["height"])
        assert result.matched is True
        assert result.size_name == "A0"
        assert result.orientation == Orientation.LANDSCAPE

    def test_match_us_36x48(self, us_36x48_pts):
        """Test matching US 36x48 dimensions."""
        result = match_dimensions(us_36x48_pts["width"], us_36x48_pts["height"])
        assert result.matched is True
        assert result.size_name == "36x48"

    def test_no_match_nonstandard(self, non_standard_pts):
        """Test non-standard dimensions don't match."""
        result = match_dimensions(non_standard_pts["width"], non_standard_pts["height"])
        assert result.matched is False
        assert result.size_name is None


class TestDimensionValidation:
    """Tests for dimension validation."""

    def test_validate_correct_size(self, a0_portrait_pts):
        """Test validation passes for correct expected size."""
        result = validate_dimensions(
            a0_portrait_pts["width"],
            a0_portrait_pts["height"],
            expected_size="A0",
        )
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_wrong_expected_size(self, a0_portrait_pts):
        """Test validation fails for wrong expected size."""
        result = validate_dimensions(
            a0_portrait_pts["width"],
            a0_portrait_pts["height"],
            expected_size="A1",
        )
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_nonstandard_warns(self, non_standard_pts):
        """Test non-standard dimensions generate issues."""
        result = validate_dimensions(
            non_standard_pts["width"],
            non_standard_pts["height"],
        )
        assert len(result["issues"]) > 0


class TestFontSizeRecommendations:
    """Tests for font size recommendations."""

    def test_a0_font_sizes(self):
        """Test A0 font size recommendations."""
        fonts = get_recommended_font_sizes("A0")
        assert "title" in fonts
        assert "body" in fonts
        assert fonts["title"][0] >= 72  # Min title size

    def test_unknown_size_uses_defaults(self):
        """Test unknown size returns default recommendations."""
        fonts = get_recommended_font_sizes("UNKNOWN")
        assert "title" in fonts


class TestDPICalculation:
    """Tests for DPI calculation."""

    def test_300_dpi_calculation(self):
        """Test correct DPI calculation."""
        h_dpi, v_dpi = calculate_dpi_for_image(3000, 2000, 10, 6.67)
        assert abs(h_dpi - 300) < 1
        assert abs(v_dpi - 300) < 1

    def test_zero_size_returns_zero(self):
        """Test zero print size returns zero DPI."""
        h_dpi, v_dpi = calculate_dpi_for_image(1000, 1000, 0, 0)
        assert h_dpi == 0
        assert v_dpi == 0


# =============================================================================
# Schema Tests
# =============================================================================


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_result(self):
        """Test creating a validation result."""
        result = ValidationResult(
            check_name="test_check",
            status=ValidationStatus.PASS,
            message="Test passed",
            value=100,
            threshold=50,
        )
        assert result.check_name == "test_check"
        assert result.status == ValidationStatus.PASS

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult(
            check_name="test",
            status=ValidationStatus.PASS,
            message="OK",
        )
        d = result.to_dict()
        assert d["check_name"] == "test"
        assert d["status"] == "pass"


class TestWordCountResult:
    """Tests for WordCountResult dataclass."""

    def test_create_word_count(self, passing_word_count):
        """Test creating word count result."""
        result = WordCountResult(
            total=passing_word_count["total"],
            by_section=passing_word_count["by_section"],
            target_min=300,
            target_max=800,
            status=ValidationStatus.PASS,
        )
        assert result.total == 500
        assert result.passed is True

    def test_to_dict_includes_range(self, passing_word_count):
        """Test to_dict includes target range."""
        result = WordCountResult(
            total=passing_word_count["total"],
            by_section=passing_word_count["by_section"],
            target_min=300,
            target_max=800,
            status=ValidationStatus.PASS,
        )
        d = result.to_dict()
        assert d["target_range"] == [300, 800]


class TestPosterSpec:
    """Tests for PosterSpec dataclass."""

    def test_create_from_dict(self, valid_poster_spec):
        """Test creating PosterSpec from dictionary."""
        spec = PosterSpec.from_dict(valid_poster_spec)
        assert spec.title == "Test Research Poster"
        assert spec.dimensions == "A0"
        assert len(spec.authors) == 2

    def test_validate_valid_spec(self, valid_poster_spec):
        """Test validation passes for valid spec."""
        spec = PosterSpec.from_dict(valid_poster_spec)
        errors = spec.validate()
        assert len(errors) == 0

    def test_validate_missing_title(self):
        """Test validation catches missing title."""
        spec = PosterSpec(title="", dimensions="A0")
        errors = spec.validate()
        assert any("title" in e.lower() for e in errors)

    def test_to_dict_roundtrip(self, valid_poster_spec):
        """Test to_dict/from_dict roundtrip."""
        spec1 = PosterSpec.from_dict(valid_poster_spec)
        spec2 = PosterSpec.from_dict(spec1.to_dict())
        assert spec1.title == spec2.title
        assert spec1.dimensions == spec2.dimensions


class TestQualityReport:
    """Tests for QualityReport dataclass."""

    def test_create_report(self):
        """Test creating quality report."""
        report = QualityReport(
            poster_path="test.pdf",
            source_path="test.tex",
        )
        assert report.overall_pass is True
        assert len(report.errors) == 0

    def test_add_error_sets_fail(self):
        """Test adding error sets overall_pass to False."""
        report = QualityReport(poster_path="test.pdf", source_path=None)
        report.add_error("Test error")
        assert report.overall_pass is False
        assert "Test error" in report.errors

    def test_add_warning_keeps_pass(self):
        """Test adding warning doesn't affect overall_pass."""
        report = QualityReport(poster_path="test.pdf", source_path=None)
        report.add_warning("Test warning")
        assert report.overall_pass is True
        assert "Test warning" in report.warnings

    def test_to_dict_structure(self, sample_quality_report):
        """Test to_dict produces expected structure."""
        report = QualityReport(
            poster_path="test.pdf",
            source_path="test.tex",
        )
        d = report.to_dict()
        assert "poster_path" in d
        assert "checks" in d
        assert "errors" in d
        assert "warnings" in d

    def test_from_dict_basic(self):
        """Test from_dict restores basic fields."""
        data = {
            "poster_path": "restored.pdf",
            "source_path": "restored.tex",
            "overall_pass": False,
            "errors": ["error1"],
            "warnings": ["warning1"],
            "checks": {},
        }
        report = QualityReport.from_dict(data)
        assert report.poster_path == "restored.pdf"
        assert report.source_path == "restored.tex"
        assert report.overall_pass is False
        assert "error1" in report.errors
        assert "warning1" in report.warnings

    def test_from_dict_with_fonts(self):
        """Test from_dict restores font check results."""
        data = {
            "poster_path": "test.pdf",
            "source_path": None,
            "checks": {
                "fonts": {
                    "all_embedded": True,
                    "font_count": 2,
                    "details": [
                        {"font_name": "Helvetica", "font_type": "Type1", "embedded": True, "subset": False},
                        {"font_name": "Times", "font_type": "TrueType", "embedded": True, "subset": True},
                    ],
                }
            },
        }
        report = QualityReport.from_dict(data)
        assert len(report.fonts) == 2
        assert report.fonts[0].font_name == "Helvetica"
        assert report.fonts[0].embedded is True
        assert report.fonts[1].subset is True

    def test_from_dict_with_images(self):
        """Test from_dict restores image check results."""
        data = {
            "poster_path": "test.pdf",
            "source_path": None,
            "checks": {
                "images": {
                    "count": 2,
                    "details": [
                        {
                            "image_index": 0,
                            "page": 1,
                            "dimensions": {"width": 1000, "height": 800},
                            "color_space": "RGB",
                            "format": "jpeg",
                            "estimated_dpi": 300.0,
                            "meets_minimum_dpi": True,
                        },
                        {
                            "image_index": 1,
                            "page": 1,
                            "dimensions": {"width": 500, "height": 400},
                            "color_space": "CMYK",
                            "format": "png",
                            "estimated_dpi": 150.0,
                            "meets_minimum_dpi": False,
                        },
                    ],
                }
            },
        }
        report = QualityReport.from_dict(data)
        assert len(report.images) == 2
        assert report.images[0].width_px == 1000
        assert report.images[0].estimated_dpi == 300.0
        assert report.images[1].meets_minimum_dpi is False

    def test_from_dict_with_contrast(self):
        """Test from_dict restores contrast check results."""
        data = {
            "poster_path": "test.pdf",
            "source_path": None,
            "checks": {
                "accessibility": {
                    "contrast_checks": [
                        {
                            "foreground": "#000000",
                            "background": "#FFFFFF",
                            "ratio": 21.0,
                            "wcag_level": "AAA",
                            "passes_large_text": True,
                            "passes_normal_text": True,
                        },
                        {
                            "foreground": "#666666",
                            "background": "#FFFFFF",
                            "ratio": 5.74,
                            "wcag_level": "AA",
                            "passes_large_text": True,
                            "passes_normal_text": True,
                        },
                    ],
                }
            },
        }
        report = QualityReport.from_dict(data)
        assert len(report.contrast_checks) == 2
        assert report.contrast_checks[0].ratio == 21.0
        assert report.contrast_checks[0].wcag_level == "AAA"
        assert report.contrast_checks[1].passes_normal_text is True

    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves all data."""
        # Create a complete report
        original = QualityReport(
            poster_path="roundtrip.pdf",
            source_path="roundtrip.tex",
            overall_pass=True,
        )
        original.fonts = [
            FontCheckResult(font_name="Arial", font_type="TrueType", embedded=True, subset=True),
        ]
        original.images = [
            ImageCheckResult(
                image_index=0, page=1, width_px=2000, height_px=1500,
                color_space="RGB", format="png", estimated_dpi=300.0, meets_minimum_dpi=True
            ),
        ]
        original.contrast_checks = [
            ContrastCheckResult(
                foreground="#222222", background="#FFFFFF",
                ratio=16.0, wcag_level="AAA", passes_large_text=True, passes_normal_text=True
            ),
        ]
        original.word_count = WordCountResult(
            total=500, by_section={"intro": 100, "methods": 200, "results": 200},
            target_min=300, target_max=800, status=ValidationStatus.PASS
        )

        # Round-trip
        serialized = original.to_dict()
        restored = QualityReport.from_dict(serialized)

        # Verify
        assert restored.poster_path == original.poster_path
        assert len(restored.fonts) == 1
        assert restored.fonts[0].font_name == "Arial"
        assert len(restored.images) == 1
        assert restored.images[0].width_px == 2000
        assert len(restored.contrast_checks) == 1
        assert restored.contrast_checks[0].ratio == 16.0
        assert restored.word_count.total == 500


# =============================================================================
# Integration Tests
# =============================================================================


class TestEndToEndValidation:
    """Integration tests for complete validation workflows."""

    def test_color_to_contrast_workflow(self, oligon_colors):
        """Test complete color validation workflow."""
        # Extract colors
        colors = [oligon_colors["dark_gray"], oligon_colors["brand_blue"]]

        # Validate palette
        result = validate_poster_palette(colors, background="#FFFFFF")

        # Check structure
        assert "contrast_checks" in result
        assert "colorblind_safe" in result
        assert "overall_pass" in result

    def test_dimension_to_validation_workflow(self, a0_portrait_pts):
        """Test complete dimension validation workflow."""
        # Match dimensions
        match = match_dimensions(
            a0_portrait_pts["width"],
            a0_portrait_pts["height"],
        )

        # Validate
        result = validate_dimensions(
            a0_portrait_pts["width"],
            a0_portrait_pts["height"],
            expected_size=match.size_name,
        )

        assert result["valid"] is True

    def test_spec_to_validation_workflow(self, valid_poster_spec):
        """Test spec parsing and validation workflow."""
        # Parse spec
        spec = PosterSpec.from_dict(valid_poster_spec)

        # Validate
        errors = spec.validate()
        assert len(errors) == 0

        # Convert back
        output = spec.to_dict()
        assert output["title"] == valid_poster_spec["title"]
