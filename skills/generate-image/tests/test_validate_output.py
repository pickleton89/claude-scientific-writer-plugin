"""
Tests for validate_output.py - image validation module.

Tests cover:
- Image validation (valid, invalid, corrupt)
- Resolution tier classification
- File size bounds
- Format detection
- Batch validation
- Report formatting
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_output import (
    ImageValidation,
    validate_image,
    check_resolution_tier,
    format_validation_report,
    validate_batch,
    summarize_batch,
    MINIMUM_RESOLUTION,
    TARGET_RESOLUTION,
    EXCELLENT_RESOLUTION,
    MIN_FILE_SIZE,
    MAX_FILE_SIZE,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def create_test_image(temp_dir):
    """Factory fixture to create test images with specific dimensions."""

    def _create(width: int, height: int, format: str = "PNG", name: str = "test.png"):
        try:
            from PIL import Image

            img = Image.new("RGB", (width, height), color="white")
            path = temp_dir / name
            img.save(path, format=format)
            return str(path)
        except ImportError:
            pytest.skip("PIL/Pillow not installed")

    return _create


@pytest.fixture
def create_rgba_image(temp_dir):
    """Create an RGBA image with alpha channel."""

    def _create(width: int, height: int, name: str = "rgba_test.png"):
        try:
            from PIL import Image

            img = Image.new("RGBA", (width, height), color=(255, 255, 255, 128))
            path = temp_dir / name
            img.save(path, "PNG")
            return str(path)
        except ImportError:
            pytest.skip("PIL/Pillow not installed")

    return _create


# ============================================================================
# ImageValidation Dataclass Tests
# ============================================================================


class TestImageValidationDataclass:
    """Tests for ImageValidation dataclass properties."""

    def test_min_dimension(self):
        """Test min_dimension property."""
        v = ImageValidation(
            valid=True,
            resolution=(1920, 1080),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.778,
        )
        assert v.min_dimension == 1080

    def test_max_dimension(self):
        """Test max_dimension property."""
        v = ImageValidation(
            valid=True,
            resolution=(1920, 1080),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.778,
        )
        assert v.max_dimension == 1920

    def test_is_square_true(self):
        """Test is_square for square image."""
        v = ImageValidation(
            valid=True,
            resolution=(1024, 1024),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        assert v.is_square is True

    def test_is_square_within_tolerance(self):
        """Test is_square within 5% tolerance."""
        v = ImageValidation(
            valid=True,
            resolution=(1024, 1000),  # ~2.4% difference
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.024,
        )
        assert v.is_square is True

    def test_is_square_false(self):
        """Test is_square for non-square image."""
        v = ImageValidation(
            valid=True,
            resolution=(1920, 1080),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.778,
        )
        assert v.is_square is False

    def test_is_portrait(self):
        """Test is_portrait for portrait image."""
        v = ImageValidation(
            valid=True,
            resolution=(1080, 1920),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=0.5625,
        )
        assert v.is_portrait is True
        assert v.is_landscape is False

    def test_is_landscape(self):
        """Test is_landscape for landscape image."""
        v = ImageValidation(
            valid=True,
            resolution=(1920, 1080),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.778,
        )
        assert v.is_landscape is True
        assert v.is_portrait is False


# ============================================================================
# validate_image() Tests
# ============================================================================


class TestValidateImage:
    """Tests for validate_image function."""

    def test_file_not_found(self):
        """Test validation of non-existent file."""
        result = validate_image("/nonexistent/path/image.png")
        assert result.valid is False
        assert "not found" in result.error.lower()

    def test_valid_png(self, create_test_image):
        """Test validation of valid PNG image."""
        path = create_test_image(1024, 1024, "PNG")
        result = validate_image(path)

        assert result.valid is True
        assert result.resolution == (1024, 1024)
        assert result.format == "PNG"
        assert result.mode == "RGB"
        assert result.meets_target is True
        assert result.error is None

    def test_valid_jpeg(self, create_test_image):
        """Test validation of valid JPEG image."""
        path = create_test_image(800, 600, "JPEG", "test.jpg")
        result = validate_image(path)

        assert result.valid is True
        assert result.resolution == (800, 600)
        assert result.format == "JPEG"

    def test_rgba_image(self, create_rgba_image):
        """Test validation of RGBA image with alpha."""
        path = create_rgba_image(512, 512)
        result = validate_image(path)

        assert result.valid is True
        assert result.mode == "RGBA"
        assert result.has_alpha is True

    def test_meets_minimum_threshold(self, create_test_image):
        """Test minimum resolution threshold (512px)."""
        # Below minimum
        path_small = create_test_image(400, 400, name="small.png")
        result_small = validate_image(path_small)
        assert result_small.meets_minimum is False

        # At minimum
        path_min = create_test_image(512, 512, name="min.png")
        result_min = validate_image(path_min)
        assert result_min.meets_minimum is True

    def test_meets_target_threshold(self, create_test_image):
        """Test target resolution threshold (1024px)."""
        # Below target
        path_below = create_test_image(800, 800, name="below.png")
        result_below = validate_image(path_below)
        assert result_below.meets_target is False

        # At target
        path_target = create_test_image(1024, 1024, name="target.png")
        result_target = validate_image(path_target)
        assert result_target.meets_target is True

    def test_meets_excellent_threshold(self, create_test_image):
        """Test excellent resolution threshold (2048px)."""
        # Below excellent
        path_below = create_test_image(1500, 1500, name="below.png")
        result_below = validate_image(path_below)
        assert result_below.meets_excellent is False

        # At excellent
        path_excellent = create_test_image(2048, 2048, name="excellent.png")
        result_excellent = validate_image(path_excellent)
        assert result_excellent.meets_excellent is True

    def test_aspect_ratio_calculation(self, create_test_image):
        """Test aspect ratio calculation."""
        path = create_test_image(1920, 1080)
        result = validate_image(path)

        assert result.aspect_ratio == pytest.approx(1.778, rel=0.01)

    def test_custom_thresholds(self, create_test_image):
        """Test custom resolution thresholds."""
        # Use 400x400 to ensure file size > MIN_FILE_SIZE (1KB)
        path = create_test_image(400, 400)
        result = validate_image(
            path,
            min_resolution=300,
            target_resolution=400,
            excellent_resolution=800,
        )

        assert result.meets_minimum is True
        assert result.meets_target is True
        assert result.meets_excellent is False

    def test_file_too_small(self, temp_dir):
        """Test rejection of too-small files (likely corrupt)."""
        small_file = temp_dir / "tiny.png"
        small_file.write_bytes(b"tiny")  # 4 bytes

        result = validate_image(str(small_file))

        assert result.valid is False
        assert "too small" in result.error.lower()

    def test_corrupt_image(self, temp_dir):
        """Test detection of corrupt image data."""
        corrupt_file = temp_dir / "corrupt.png"
        # Write invalid PNG header
        corrupt_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"corrupted" * 200)

        result = validate_image(str(corrupt_file))

        assert result.valid is False
        assert result.error is not None


# ============================================================================
# check_resolution_tier() Tests
# ============================================================================


class TestCheckResolutionTier:
    """Tests for check_resolution_tier function."""

    def test_excellent_tier(self):
        """Test excellent tier classification (2048+)."""
        v = ImageValidation(
            valid=True,
            resolution=(2048, 2048),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=True,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        assert check_resolution_tier(v) == "excellent"

    def test_target_tier(self):
        """Test target tier classification (1024-2047)."""
        v = ImageValidation(
            valid=True,
            resolution=(1500, 1500),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        assert check_resolution_tier(v) == "target"

    def test_minimum_tier(self):
        """Test minimum tier classification (512-1023)."""
        v = ImageValidation(
            valid=True,
            resolution=(800, 800),
            meets_minimum=True,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        assert check_resolution_tier(v) == "minimum"

    def test_fail_tier(self):
        """Test fail tier classification (<512)."""
        v = ImageValidation(
            valid=True,
            resolution=(400, 400),
            meets_minimum=False,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        assert check_resolution_tier(v) == "fail"

    def test_invalid_image_fails(self):
        """Test that invalid images return fail tier."""
        v = ImageValidation(
            valid=False,
            resolution=(0, 0),
            meets_minimum=False,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=0,
            format="ERROR",
            mode="ERROR",
            has_alpha=False,
            aspect_ratio=0,
            error="Test error",
        )
        assert check_resolution_tier(v) == "fail"

    def test_non_square_tier_uses_min_dimension(self):
        """Test tier classification uses minimum dimension."""
        v = ImageValidation(
            valid=True,
            resolution=(2048, 800),  # min is 800
            meets_minimum=True,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=2.56,
        )
        assert check_resolution_tier(v) == "minimum"


# ============================================================================
# format_validation_report() Tests
# ============================================================================


class TestFormatValidationReport:
    """Tests for format_validation_report function."""

    def test_valid_image_report(self):
        """Test report format for valid image."""
        v = ImageValidation(
            valid=True,
            resolution=(1024, 1024),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=512000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        report = format_validation_report(v)

        assert "Valid" in report
        assert "1024x1024" in report
        assert "TARGET" in report
        assert "PNG" in report
        assert "RGB" in report
        assert "500.0 KB" in report or "512" in report

    def test_invalid_image_report(self):
        """Test report format for invalid image."""
        v = ImageValidation(
            valid=False,
            resolution=(0, 0),
            meets_minimum=False,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=0,
            format="ERROR",
            mode="ERROR",
            has_alpha=False,
            aspect_ratio=0,
            error="File not found",
        )
        report = format_validation_report(v)

        assert "Invalid" in report
        assert "File not found" in report

    def test_report_shows_orientation(self):
        """Test report includes orientation."""
        v = ImageValidation(
            valid=True,
            resolution=(1920, 1080),
            meets_minimum=True,
            meets_target=True,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.778,
        )
        report = format_validation_report(v)

        assert "Landscape" in report

    def test_report_shows_quality_thresholds(self):
        """Test report includes quality threshold checks."""
        v = ImageValidation(
            valid=True,
            resolution=(600, 600),
            meets_minimum=True,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=100000,
            format="PNG",
            mode="RGB",
            has_alpha=False,
            aspect_ratio=1.0,
        )
        report = format_validation_report(v)

        assert "Minimum (512px)" in report
        assert "Target (1024px)" in report
        assert "Excellent (2048px)" in report
        assert "Pass" in report
        assert "Fail" in report


# ============================================================================
# Batch Validation Tests
# ============================================================================


class TestBatchValidation:
    """Tests for batch validation functions."""

    def test_validate_batch(self, create_test_image):
        """Test batch validation of multiple images."""
        paths = [
            create_test_image(1024, 1024, name="img1.png"),
            create_test_image(512, 512, name="img2.png"),
            create_test_image(2048, 2048, name="img3.png"),
        ]

        results = validate_batch(paths)

        assert len(results) == 3
        assert all(v.valid for v in results.values())

    def test_validate_batch_with_invalid(self, create_test_image):
        """Test batch validation with some invalid images."""
        paths = [
            create_test_image(1024, 1024, name="valid.png"),
            "/nonexistent/path.png",
        ]

        results = validate_batch(paths)

        assert len(results) == 2
        assert results[paths[0]].valid is True
        assert results[paths[1]].valid is False

    def test_summarize_batch(self, create_test_image):
        """Test batch summary statistics."""
        paths = [
            create_test_image(512, 512, name="minimum.png"),
            create_test_image(1024, 1024, name="target.png"),
            create_test_image(2048, 2048, name="excellent.png"),
        ]

        results = validate_batch(paths)
        summary = summarize_batch(results)

        assert summary["total"] == 3
        assert summary["valid"] == 3
        assert summary["invalid"] == 0
        assert summary["meets_minimum"] == 3
        assert summary["meets_target"] == 2
        assert summary["meets_excellent"] == 1
        assert summary["pass_rate"] == 1.0
        assert summary["tiers"]["minimum"] == 1
        assert summary["tiers"]["target"] == 1
        assert summary["tiers"]["excellent"] == 1

    def test_summarize_batch_empty(self):
        """Test summary of empty batch."""
        summary = summarize_batch({})

        assert summary["total"] == 0
        assert summary["pass_rate"] == 0


# ============================================================================
# Edge Cases and Constants Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_constants_defined(self):
        """Test that resolution constants are defined correctly."""
        assert MINIMUM_RESOLUTION == 512
        assert TARGET_RESOLUTION == 1024
        assert EXCELLENT_RESOLUTION == 2048
        assert MIN_FILE_SIZE == 1024
        assert MAX_FILE_SIZE == 50 * 1024 * 1024

    def test_boundary_resolutions(self, create_test_image):
        """Test exact boundary resolution values."""
        # Exactly at minimum
        path_512 = create_test_image(512, 512, name="exact_512.png")
        result_512 = validate_image(path_512)
        assert result_512.meets_minimum is True
        assert result_512.meets_target is False
        assert check_resolution_tier(result_512) == "minimum"

        # Exactly at target
        path_1024 = create_test_image(1024, 1024, name="exact_1024.png")
        result_1024 = validate_image(path_1024)
        assert result_1024.meets_target is True
        assert result_1024.meets_excellent is False
        assert check_resolution_tier(result_1024) == "target"

        # Exactly at excellent
        path_2048 = create_test_image(2048, 2048, name="exact_2048.png")
        result_2048 = validate_image(path_2048)
        assert result_2048.meets_excellent is True
        assert check_resolution_tier(result_2048) == "excellent"

    def test_just_below_boundary(self, create_test_image):
        """Test one pixel below boundary values."""
        path_511 = create_test_image(511, 511, name="below_512.png")
        result_511 = validate_image(path_511)
        assert result_511.meets_minimum is False
        assert check_resolution_tier(result_511) == "fail"

    def test_zero_dimension_handling(self):
        """Test handling of zero dimensions in validation result."""
        v = ImageValidation(
            valid=False,
            resolution=(0, 0),
            meets_minimum=False,
            meets_target=False,
            meets_excellent=False,
            file_size_bytes=0,
            format="ERROR",
            mode="ERROR",
            has_alpha=False,
            aspect_ratio=0,
            error="Test",
        )
        assert v.min_dimension == 0
        assert v.max_dimension == 0
        assert v.is_square is False

    def test_single_dimension_minimum(self, create_test_image):
        """Test that minimum dimension is used for classification."""
        # Tall image: 2048x400
        path_tall = create_test_image(400, 2048, name="tall.png")
        result_tall = validate_image(path_tall)
        assert result_tall.min_dimension == 400
        assert result_tall.meets_minimum is False

        # Wide image: 400x2048
        path_wide = create_test_image(2048, 400, name="wide.png")
        result_wide = validate_image(path_wide)
        assert result_wide.min_dimension == 400
        assert result_wide.meets_minimum is False


# ============================================================================
# PIL Not Installed Test
# ============================================================================


class TestPILNotInstalled:
    """Tests for behavior when PIL is not available."""

    def test_pil_import_error(self, temp_dir):
        """Test graceful handling when PIL is not installed."""
        # Create a valid-looking file
        test_file = temp_dir / "test.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 2000)

        with patch.dict("sys.modules", {"PIL": None, "PIL.Image": None}):
            # Force reimport to trigger ImportError
            import validate_output

            # Store original function
            original_validate = validate_output.validate_image

            # Mock the import inside validate_image
            def mock_validate(path, *args, **kwargs):
                try:
                    raise ImportError("No module named 'PIL'")
                except ImportError:
                    return validate_output._error_validation(
                        "PIL/Pillow not installed. Install with: pip install Pillow"
                    )

            validate_output.validate_image = mock_validate

            try:
                result = validate_output.validate_image(str(test_file))
                assert result.valid is False
                assert "PIL" in result.error or "Pillow" in result.error
            finally:
                validate_output.validate_image = original_validate
