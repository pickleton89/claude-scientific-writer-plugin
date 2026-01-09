#!/usr/bin/env python3
"""
Automated validation for generated images.

Validates image integrity, resolution, and format against SKILL.md quality thresholds.
Part of the generate-image skill determinism improvement initiative (Phase 1).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

# Resolution thresholds from SKILL.md
MINIMUM_RESOLUTION = 512
TARGET_RESOLUTION = 1024
EXCELLENT_RESOLUTION = 2048

# Supported formats
SUPPORTED_FORMATS = {"PNG", "JPEG", "WEBP", "GIF"}

# File size limits (reasonable bounds for generated images)
MIN_FILE_SIZE = 1024  # 1KB - smaller likely indicates corruption
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB - larger likely indicates error

ResolutionTier = Literal["excellent", "target", "minimum", "fail"]


@dataclass
class ImageValidation:
    """Result of image validation."""

    valid: bool
    resolution: tuple[int, int]
    meets_minimum: bool  # >= 512px
    meets_target: bool  # >= 1024px
    meets_excellent: bool  # >= 2048px
    file_size_bytes: int
    format: str
    mode: str  # RGB, RGBA, L, etc.
    has_alpha: bool
    aspect_ratio: float
    error: Optional[str] = None

    @property
    def min_dimension(self) -> int:
        """Return the smaller dimension."""
        return min(self.resolution)

    @property
    def max_dimension(self) -> int:
        """Return the larger dimension."""
        return max(self.resolution)

    @property
    def is_square(self) -> bool:
        """Check if image is square (within 5% tolerance)."""
        if self.resolution[0] == 0 or self.resolution[1] == 0:
            return False
        ratio = self.resolution[0] / self.resolution[1]
        return 0.95 <= ratio <= 1.05

    @property
    def is_portrait(self) -> bool:
        """Check if image is portrait orientation."""
        return self.resolution[1] > self.resolution[0]

    @property
    def is_landscape(self) -> bool:
        """Check if image is landscape orientation."""
        return self.resolution[0] > self.resolution[1]


def validate_image(
    path: str,
    min_resolution: int = MINIMUM_RESOLUTION,
    target_resolution: int = TARGET_RESOLUTION,
    excellent_resolution: int = EXCELLENT_RESOLUTION,
) -> ImageValidation:
    """
    Validate generated image meets quality thresholds.

    Args:
        path: Path to generated image
        min_resolution: Minimum acceptable dimension (default: 512px)
        target_resolution: Target dimension (default: 1024px)
        excellent_resolution: Excellent dimension (default: 2048px)

    Returns:
        ImageValidation with all metrics
    """
    path_obj = Path(path)

    # Check file exists
    if not path_obj.exists():
        return _error_validation(f"File not found: {path}")

    # Check file size
    try:
        file_size = path_obj.stat().st_size
    except OSError as e:
        return _error_validation(f"Cannot read file: {e}")

    if file_size < MIN_FILE_SIZE:
        return _error_validation(
            f"File too small ({file_size} bytes) - likely corrupted or empty"
        )

    if file_size > MAX_FILE_SIZE:
        return _error_validation(
            f"File too large ({file_size / 1024 / 1024:.1f} MB) - exceeds 50MB limit"
        )

    # Load and validate with PIL
    try:
        from PIL import Image

        img = Image.open(path)
        img.verify()  # Verify integrity without loading full image

        # Reopen after verify (verify closes the file)
        img = Image.open(path)
        width, height = img.size
        img_format = img.format or "UNKNOWN"
        mode = img.mode

    except ImportError:
        return _error_validation(
            "PIL/Pillow not installed. Install with: pip install Pillow"
        )
    except Exception as e:
        return _error_validation(f"Image validation failed: {e}")

    # Calculate metrics
    min_dim = min(width, height)
    aspect_ratio = width / height if height > 0 else 0
    has_alpha = mode in ("RGBA", "LA", "PA")

    return ImageValidation(
        valid=True,
        resolution=(width, height),
        meets_minimum=min_dim >= min_resolution,
        meets_target=min_dim >= target_resolution,
        meets_excellent=min_dim >= excellent_resolution,
        file_size_bytes=file_size,
        format=img_format,
        mode=mode,
        has_alpha=has_alpha,
        aspect_ratio=round(aspect_ratio, 3),
    )


def _error_validation(error: str) -> ImageValidation:
    """Create an error validation result."""
    return ImageValidation(
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
        error=error,
    )


def check_resolution_tier(validation: ImageValidation) -> ResolutionTier:
    """
    Classify resolution against SKILL.md thresholds.

    Returns:
        "excellent" (2048+), "target" (1024+), "minimum" (512+), "fail"
    """
    if not validation.valid:
        return "fail"

    min_dim = validation.min_dimension

    if min_dim >= EXCELLENT_RESOLUTION:
        return "excellent"
    elif min_dim >= TARGET_RESOLUTION:
        return "target"
    elif min_dim >= MINIMUM_RESOLUTION:
        return "minimum"
    else:
        return "fail"


def format_validation_report(validation: ImageValidation) -> str:
    """Format validation results as a readable report."""
    lines = []

    if validation.valid:
        tier = check_resolution_tier(validation)
        tier_emoji = {"excellent": "🌟", "target": "✅", "minimum": "⚠️", "fail": "❌"}

        lines.append(f"Status: Valid {tier_emoji.get(tier, '?')}")
        lines.append(f"Resolution: {validation.resolution[0]}x{validation.resolution[1]}")
        lines.append(f"Resolution Tier: {tier.upper()}")
        lines.append(f"Format: {validation.format}")
        lines.append(f"Mode: {validation.mode}")
        lines.append(f"Has Alpha: {'Yes' if validation.has_alpha else 'No'}")
        lines.append(f"Aspect Ratio: {validation.aspect_ratio:.2f}")
        lines.append(f"File Size: {validation.file_size_bytes / 1024:.1f} KB")

        # Orientation
        if validation.is_square:
            lines.append("Orientation: Square")
        elif validation.is_portrait:
            lines.append("Orientation: Portrait")
        else:
            lines.append("Orientation: Landscape")

        # Quality assessment
        lines.append("")
        lines.append("Quality Thresholds:")
        lines.append(f"  - Minimum (512px): {'✅ Pass' if validation.meets_minimum else '❌ Fail'}")
        lines.append(f"  - Target (1024px): {'✅ Pass' if validation.meets_target else '❌ Fail'}")
        lines.append(f"  - Excellent (2048px): {'✅ Pass' if validation.meets_excellent else '❌ Fail'}")
    else:
        lines.append("Status: Invalid ❌")
        lines.append(f"Error: {validation.error}")

    return "\n".join(lines)


def validate_batch(paths: list[str]) -> dict[str, ImageValidation]:
    """
    Validate multiple images.

    Args:
        paths: List of image paths

    Returns:
        Dict mapping path to validation result
    """
    return {path: validate_image(path) for path in paths}


def summarize_batch(validations: dict[str, ImageValidation]) -> dict:
    """
    Summarize batch validation results.

    Returns:
        Summary statistics dict
    """
    total = len(validations)
    valid = sum(1 for v in validations.values() if v.valid)
    meets_minimum = sum(1 for v in validations.values() if v.meets_minimum)
    meets_target = sum(1 for v in validations.values() if v.meets_target)
    meets_excellent = sum(1 for v in validations.values() if v.meets_excellent)

    tiers = {"excellent": 0, "target": 0, "minimum": 0, "fail": 0}
    for v in validations.values():
        tier = check_resolution_tier(v)
        tiers[tier] += 1

    return {
        "total": total,
        "valid": valid,
        "invalid": total - valid,
        "meets_minimum": meets_minimum,
        "meets_target": meets_target,
        "meets_excellent": meets_excellent,
        "tiers": tiers,
        "pass_rate": valid / total if total > 0 else 0,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <image_path> [image_path2 ...]")
        print("\nValidates generated images against SKILL.md quality thresholds.")
        print("\nResolution Tiers:")
        print("  - excellent: >= 2048px minimum dimension")
        print("  - target: >= 1024px minimum dimension")
        print("  - minimum: >= 512px minimum dimension")
        print("  - fail: < 512px minimum dimension")
        sys.exit(1)

    paths = sys.argv[1:]

    if len(paths) == 1:
        # Single image
        result = validate_image(paths[0])
        print(format_validation_report(result))
        sys.exit(0 if result.valid and result.meets_minimum else 1)
    else:
        # Batch validation
        results = validate_batch(paths)
        summary = summarize_batch(results)

        print(f"Batch Validation Summary ({summary['total']} images)")
        print("=" * 50)
        print(f"Valid: {summary['valid']} / {summary['total']}")
        print(f"Pass Rate: {summary['pass_rate']:.1%}")
        print()
        print("Resolution Tiers:")
        for tier, count in summary["tiers"].items():
            print(f"  {tier}: {count}")
        print()

        # Show failures
        failures = [p for p, v in results.items() if not v.valid]
        if failures:
            print("Failed Images:")
            for path in failures:
                print(f"  - {path}: {results[path].error}")

        sys.exit(0 if summary["invalid"] == 0 else 1)
