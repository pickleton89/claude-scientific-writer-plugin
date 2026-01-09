#!/usr/bin/env python3
"""
Figure Quality Checker for Peer Review

Checks image quality against publication standards including resolution,
dimensions, file format, and basic integrity checks.

Usage:
    from scripts.figure_checker import check_figure_quality, FigureQualityResult

    result = check_figure_quality("/path/to/figure.png")
    print(result.summary())

Requirements:
    pip install Pillow

Author: Claude Scientific Writer Plugin
License: MIT
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from enum import Enum

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class QualityTier(Enum):
    """Quality tier classification."""

    EXCELLENT = "excellent"
    TARGET = "target"
    MINIMUM = "minimum"
    BELOW_MINIMUM = "below_minimum"


@dataclass(frozen=True)
class FigureQualityThresholds:
    """
    Thresholds from SKILL.md lines 323-330.

    Each tuple represents (minimum, target, excellent) values.
    """

    resolution_dpi: Tuple[int, int, int] = (150, 300, 600)
    font_size_pt: Tuple[int, int, int] = (7, 8, 10)
    contrast_ratio: Tuple[float, float, float] = (4.5, 7.0, 10.0)
    line_weight_pt: Tuple[float, float, float] = (0.5, 1.0, 1.5)

    # Image dimension constraints (in inches at 300 DPI)
    max_width_inches: float = 7.0  # Typical journal column width
    max_height_inches: float = 9.0  # Typical journal page height

    # File size limits
    max_file_size_mb: float = 10.0


# Default thresholds
THRESHOLDS = FigureQualityThresholds()

# Acceptable publication formats
ACCEPTABLE_FORMATS = {
    "TIFF": "Excellent - lossless, preferred for print",
    "PNG": "Good - lossless, web-friendly",
    "PDF": "Good - vector when applicable",
    "EPS": "Good - vector format",
    "SVG": "Good - vector format",
    "JPEG": "Acceptable - lossy, use only for photographs",
    "JPG": "Acceptable - lossy, use only for photographs",
}


@dataclass
class FigureQualityResult:
    """Result of figure quality check."""

    file_path: str
    is_valid: bool
    overall_tier: QualityTier
    checks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Figure Quality Report: {Path(self.file_path).name}",
            "=" * 50,
            f"Overall: {self.overall_tier.value.upper()}",
            "",
        ]

        if self.metadata:
            lines.append("Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        if self.checks:
            lines.append("Quality Checks:")
            for check_name, result in self.checks.items():
                tier = result.get("tier", "unknown")
                value = result.get("value", "N/A")
                lines.append(f"  {check_name}: {value} ({tier})")
            lines.append("")

        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
            lines.append("")

        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  ✗ {e}")

        return "\n".join(lines)


def classify_tier(value: float, thresholds: Tuple[float, float, float]) -> QualityTier:
    """
    Classify value into quality tier.

    Args:
        value: The measured value
        thresholds: Tuple of (minimum, target, excellent) thresholds

    Returns:
        QualityTier enum value
    """
    if value >= thresholds[2]:
        return QualityTier.EXCELLENT
    elif value >= thresholds[1]:
        return QualityTier.TARGET
    elif value >= thresholds[0]:
        return QualityTier.MINIMUM
    return QualityTier.BELOW_MINIMUM


def check_resolution(image: "Image.Image") -> Dict[str, Any]:
    """
    Check image resolution against thresholds.

    Args:
        image: PIL Image object

    Returns:
        Dict with resolution check results
    """
    dpi = image.info.get("dpi", (72, 72))

    # Handle various DPI representations
    if isinstance(dpi, tuple):
        actual_dpi = min(dpi)
    else:
        actual_dpi = float(dpi)

    tier = classify_tier(actual_dpi, THRESHOLDS.resolution_dpi)

    return {
        "value": f"{actual_dpi:.0f} DPI",
        "actual_dpi": actual_dpi,
        "meets_minimum": actual_dpi >= THRESHOLDS.resolution_dpi[0],
        "meets_target": actual_dpi >= THRESHOLDS.resolution_dpi[1],
        "meets_excellent": actual_dpi >= THRESHOLDS.resolution_dpi[2],
        "tier": tier.value,
    }


def check_dimensions(image: "Image.Image") -> Dict[str, Any]:
    """
    Check image dimensions.

    Args:
        image: PIL Image object

    Returns:
        Dict with dimension check results
    """
    width, height = image.size
    dpi = image.info.get("dpi", (300, 300))

    if isinstance(dpi, tuple):
        dpi_x, dpi_y = dpi
    else:
        dpi_x = dpi_y = float(dpi)

    # Calculate size in inches
    width_inches = width / dpi_x if dpi_x > 0 else 0
    height_inches = height / dpi_y if dpi_y > 0 else 0

    warnings = []
    if width_inches > THRESHOLDS.max_width_inches:
        warnings.append(f"Width ({width_inches:.1f}in) exceeds typical journal column")
    if height_inches > THRESHOLDS.max_height_inches:
        warnings.append(f"Height ({height_inches:.1f}in) exceeds typical page height")

    return {
        "value": f"{width}×{height} px ({width_inches:.1f}×{height_inches:.1f} in)",
        "width_px": width,
        "height_px": height,
        "width_inches": width_inches,
        "height_inches": height_inches,
        "warnings": warnings,
        "tier": QualityTier.TARGET.value if not warnings else QualityTier.MINIMUM.value,
    }


def check_format(image: "Image.Image", file_path: Path) -> Dict[str, Any]:
    """
    Check image format.

    Args:
        image: PIL Image object
        file_path: Path to the image file

    Returns:
        Dict with format check results
    """
    fmt = image.format or file_path.suffix.upper().replace(".", "")

    is_acceptable = fmt.upper() in ACCEPTABLE_FORMATS
    description = ACCEPTABLE_FORMATS.get(fmt.upper(), "Unknown format")

    # Determine tier based on format
    if fmt.upper() in ("TIFF", "PNG", "PDF", "EPS", "SVG"):
        tier = QualityTier.EXCELLENT
    elif fmt.upper() in ("JPEG", "JPG"):
        tier = QualityTier.MINIMUM
    else:
        tier = QualityTier.BELOW_MINIMUM

    return {
        "value": fmt,
        "format": fmt,
        "is_acceptable": is_acceptable,
        "description": description,
        "tier": tier.value,
    }


def check_color_mode(image: "Image.Image") -> Dict[str, Any]:
    """
    Check image color mode.

    Args:
        image: PIL Image object

    Returns:
        Dict with color mode check results
    """
    mode = image.mode

    mode_descriptions = {
        "RGB": "Standard color (suitable for most uses)",
        "RGBA": "Color with transparency",
        "CMYK": "Print-ready color space",
        "L": "Grayscale",
        "1": "Black and white (1-bit)",
        "P": "Palette-based (indexed color)",
    }

    description = mode_descriptions.get(mode, f"Unknown mode: {mode}")

    # For print publications, CMYK is preferred; RGB is acceptable
    if mode in ("CMYK", "RGB", "RGBA"):
        tier = QualityTier.TARGET
    elif mode in ("L", "1"):
        tier = QualityTier.MINIMUM
    else:
        tier = QualityTier.BELOW_MINIMUM

    return {
        "value": mode,
        "mode": mode,
        "description": description,
        "tier": tier.value,
    }


def check_file_size(file_path: Path) -> Dict[str, Any]:
    """
    Check file size.

    Args:
        file_path: Path to the image file

    Returns:
        Dict with file size check results
    """
    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb <= THRESHOLDS.max_file_size_mb:
        tier = QualityTier.TARGET
        warning = None
    else:
        tier = QualityTier.MINIMUM
        warning = "Large file size may cause upload issues"

    return {
        "value": f"{size_mb:.2f} MB",
        "size_bytes": size_bytes,
        "size_mb": size_mb,
        "exceeds_limit": size_mb > THRESHOLDS.max_file_size_mb,
        "warning": warning,
        "tier": tier.value,
    }


def check_figure_quality(
    file_path: str,
    thresholds: Optional[FigureQualityThresholds] = None,
) -> FigureQualityResult:
    """
    Perform comprehensive quality check on a figure.

    Args:
        file_path: Path to the figure file
        thresholds: Optional custom thresholds

    Returns:
        FigureQualityResult with all check results

    Examples:
        >>> result = check_figure_quality("/path/to/figure.png")
        >>> result.is_valid
        True
        >>> print(result.summary())
    """
    if not HAS_PIL:
        return FigureQualityResult(
            file_path=file_path,
            is_valid=False,
            overall_tier=QualityTier.BELOW_MINIMUM,
            errors=["Pillow library not installed. Run: pip install Pillow"],
        )

    path = Path(file_path)

    if not path.exists():
        return FigureQualityResult(
            file_path=file_path,
            is_valid=False,
            overall_tier=QualityTier.BELOW_MINIMUM,
            errors=[f"File not found: {file_path}"],
        )

    try:
        with Image.open(path) as img:
            checks = {}
            warnings = []
            errors = []

            # Run all checks
            checks["resolution"] = check_resolution(img)
            checks["dimensions"] = check_dimensions(img)
            checks["format"] = check_format(img, path)
            checks["color_mode"] = check_color_mode(img)
            checks["file_size"] = check_file_size(path)

            # Collect warnings
            if checks["dimensions"].get("warnings"):
                warnings.extend(checks["dimensions"]["warnings"])
            if checks["file_size"].get("warning"):
                warnings.append(checks["file_size"]["warning"])
            if not checks["resolution"]["meets_minimum"]:
                warnings.append(
                    f"Resolution ({checks['resolution']['actual_dpi']:.0f} DPI) "
                    f"below minimum ({THRESHOLDS.resolution_dpi[0]} DPI)"
                )
            if checks["format"]["format"].upper() in ("JPEG", "JPG"):
                warnings.append("JPEG format uses lossy compression - consider PNG or TIFF for line art")

            # Determine overall tier (lowest tier among checks)
            tiers = [
                QualityTier(checks["resolution"]["tier"]),
                QualityTier(checks["format"]["tier"]),
                QualityTier(checks["color_mode"]["tier"]),
            ]
            tier_order = [
                QualityTier.BELOW_MINIMUM,
                QualityTier.MINIMUM,
                QualityTier.TARGET,
                QualityTier.EXCELLENT,
            ]
            overall_tier = min(tiers, key=lambda t: tier_order.index(t))

            # Build metadata
            metadata = {
                "width": img.size[0],
                "height": img.size[1],
                "format": img.format,
                "mode": img.mode,
            }

            return FigureQualityResult(
                file_path=file_path,
                is_valid=overall_tier != QualityTier.BELOW_MINIMUM,
                overall_tier=overall_tier,
                checks=checks,
                warnings=warnings,
                errors=errors,
                metadata=metadata,
            )

    except Exception as e:
        return FigureQualityResult(
            file_path=file_path,
            is_valid=False,
            overall_tier=QualityTier.BELOW_MINIMUM,
            errors=[f"Error reading image: {str(e)}"],
        )


def check_multiple_figures(
    file_paths: List[str],
) -> Dict[str, FigureQualityResult]:
    """
    Check quality of multiple figures.

    Args:
        file_paths: List of paths to figure files

    Returns:
        Dict mapping file paths to their quality results
    """
    results = {}
    for path in file_paths:
        results[path] = check_figure_quality(path)
    return results


def generate_quality_report(results: Dict[str, FigureQualityResult]) -> str:
    """
    Generate summary report for multiple figures.

    Args:
        results: Dict of file paths to quality results

    Returns:
        Formatted report string
    """
    lines = [
        "=" * 60,
        "FIGURE QUALITY REPORT",
        "=" * 60,
        "",
    ]

    # Summary counts
    tier_counts = {tier: 0 for tier in QualityTier}
    for result in results.values():
        tier_counts[result.overall_tier] += 1

    lines.append("Summary:")
    for tier, count in tier_counts.items():
        if count > 0:
            lines.append(f"  {tier.value.capitalize()}: {count}")
    lines.append("")

    # Individual results
    lines.append("Individual Figures:")
    lines.append("-" * 40)

    for path, result in results.items():
        status = "✓" if result.is_valid else "✗"
        lines.append(f"{status} {Path(path).name}: {result.overall_tier.value}")
        if result.warnings:
            for w in result.warnings[:2]:  # Show first 2 warnings
                lines.append(f"    ⚠ {w}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    print("Figure Quality Checker")
    print("=" * 40)

    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            result = check_figure_quality(path)
            print(result.summary())
            print()
    else:
        print("Usage: python figure_checker.py <image_path> [image_path ...]")
        print("\nExample:")
        print("  python figure_checker.py figure1.png figure2.tiff")
