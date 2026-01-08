"""Post-generation image validation for scientific schematics.

Validates generated images meet basic quality requirements using
PIL-based analysis without requiring AI review.

Usage:
    >>> from validate_image import validate_output_image
    >>> result = validate_output_image("/path/to/schematic.png")
    >>> print(result.valid, result.issues)
    True []
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore


class ImageMetadata(NamedTuple):
    """Metadata and validation results for an image."""

    valid: bool
    width: int
    height: int
    format: str
    size_kb: float
    aspect_ratio: float
    issues: list[str]
    warnings: list[str]


class ColorAnalysis(NamedTuple):
    """Color analysis results for an image."""

    dominant_colors: list[tuple[int, int, int]]
    has_white_background: bool
    estimated_contrast: float
    is_grayscale: bool
    color_count: int


# Minimum requirements for scientific diagrams
MIN_DIMENSION = 512  # Minimum width or height in pixels
MIN_FILE_SIZE_KB = 2  # Minimum file size to detect corruption (PNG can be very efficient)
MAX_FILE_SIZE_MB = 20  # Maximum reasonable file size
PREFERRED_FORMATS = ("PNG", "JPEG", "WEBP")

# Aspect ratio limits (prevent extremely narrow/wide images)
MIN_ASPECT_RATIO = 0.25  # 1:4
MAX_ASPECT_RATIO = 4.0  # 4:1


def validate_output_image(
    path: str | Path,
    min_dimension: int = MIN_DIMENSION,
    check_colors: bool = True,
) -> ImageMetadata:
    """Verify generated image meets basic requirements.

    Checks:
    - File exists and is readable
    - Dimensions are reasonable
    - File size is not suspiciously small
    - Format is appropriate (PNG preferred)
    - Aspect ratio is reasonable

    Args:
        path: Path to the image file
        min_dimension: Minimum width or height (default 512)
        check_colors: Whether to perform color analysis

    Returns:
        ImageMetadata with validation results
    """
    issues: list[str] = []
    warnings: list[str] = []

    path = Path(path)

    # Check file exists
    if not path.exists():
        return ImageMetadata(
            valid=False,
            width=0,
            height=0,
            format="",
            size_kb=0,
            aspect_ratio=0,
            issues=["File does not exist"],
            warnings=[],
        )

    # Check file size
    size_kb = path.stat().st_size / 1024
    if size_kb < MIN_FILE_SIZE_KB:
        issues.append(f"File suspiciously small ({size_kb:.1f} KB)")
    elif size_kb > MAX_FILE_SIZE_MB * 1024:
        warnings.append(f"File unusually large ({size_kb/1024:.1f} MB)")

    # Require PIL for image analysis
    if Image is None:
        return ImageMetadata(
            valid=len(issues) == 0,
            width=0,
            height=0,
            format="UNKNOWN",
            size_kb=size_kb,
            aspect_ratio=0,
            issues=issues,
            warnings=warnings + ["PIL not available for detailed validation"],
        )

    try:
        img = Image.open(path)
        width, height = img.size
        fmt = img.format or "UNKNOWN"

        # Calculate aspect ratio
        aspect_ratio = width / height if height > 0 else 0

        # Check dimensions
        if width < min_dimension or height < min_dimension:
            issues.append(
                f"Dimensions too small: {width}x{height} "
                f"(minimum {min_dimension}px)"
            )

        # Check format
        if fmt not in PREFERRED_FORMATS:
            warnings.append(f"Unexpected format: {fmt} (PNG recommended)")

        # Check aspect ratio
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            warnings.append(
                f"Unusual aspect ratio: {aspect_ratio:.2f} "
                f"(expected {MIN_ASPECT_RATIO}-{MAX_ASPECT_RATIO})"
            )

        # Check for extremely small images that might be placeholders
        if width * height < 10000:  # Less than 100x100 effective
            issues.append("Image too small - may be a placeholder or error")

        # Optional color analysis
        if check_colors and len(issues) == 0:
            color_analysis = analyze_colors(img)
            if not color_analysis.has_white_background:
                warnings.append(
                    "Background may not be white - "
                    "consider using white for better print compatibility"
                )
            if color_analysis.estimated_contrast < 3.0:
                warnings.append(
                    f"Low contrast detected ({color_analysis.estimated_contrast:.1f}) - "
                    "may be hard to read"
                )

        return ImageMetadata(
            valid=len(issues) == 0,
            width=width,
            height=height,
            format=fmt,
            size_kb=size_kb,
            aspect_ratio=aspect_ratio,
            issues=issues,
            warnings=warnings,
        )

    except Exception as e:
        return ImageMetadata(
            valid=False,
            width=0,
            height=0,
            format="",
            size_kb=size_kb,
            aspect_ratio=0,
            issues=[f"Cannot read image: {e}"],
            warnings=[],
        )


def analyze_colors(img: "Image.Image") -> ColorAnalysis:
    """Analyze color properties of an image.

    Args:
        img: PIL Image object

    Returns:
        ColorAnalysis with color statistics
    """
    # Convert to RGB if necessary
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Sample colors (resize for performance)
    sample_size = 100
    small = img.resize((sample_size, sample_size), Image.Resampling.LANCZOS)
    pixels = list(small.getdata())

    # Check for white background (sample corners)
    corners = [
        pixels[0],  # Top-left
        pixels[sample_size - 1],  # Top-right
        pixels[-sample_size],  # Bottom-left
        pixels[-1],  # Bottom-right
    ]

    def is_near_white(rgb: tuple[int, int, int], threshold: int = 240) -> bool:
        return all(c >= threshold for c in rgb)

    white_corners = sum(1 for c in corners if is_near_white(c))
    has_white_background = white_corners >= 3

    # Check if grayscale
    def is_gray(rgb: tuple[int, int, int], tolerance: int = 10) -> bool:
        return max(rgb) - min(rgb) <= tolerance

    gray_count = sum(1 for p in pixels if is_gray(p))
    is_grayscale = gray_count / len(pixels) > 0.9

    # Count unique colors (quantized)
    def quantize(rgb: tuple[int, int, int], levels: int = 32) -> tuple[int, int, int]:
        step = 256 // levels
        return tuple(c // step * step for c in rgb)  # type: ignore

    unique_colors = set(quantize(p) for p in pixels)
    color_count = len(unique_colors)

    # Estimate contrast (difference between darkest and lightest)
    luminances = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels]
    if luminances:
        min_lum = min(luminances)
        max_lum = max(luminances)
        # Weber contrast
        if min_lum > 0:
            estimated_contrast = max_lum / min_lum
        else:
            estimated_contrast = max_lum / 1.0  # Avoid division by zero
    else:
        estimated_contrast = 1.0

    # Get dominant colors (simple frequency count)
    color_freq: dict[tuple[int, int, int], int] = {}
    for p in pixels:
        q = quantize(p, levels=16)
        color_freq[q] = color_freq.get(q, 0) + 1

    dominant = sorted(color_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    dominant_colors = [c for c, _ in dominant]

    return ColorAnalysis(
        dominant_colors=dominant_colors,
        has_white_background=has_white_background,
        estimated_contrast=estimated_contrast,
        is_grayscale=is_grayscale,
        color_count=color_count,
    )


def format_validation_report(metadata: ImageMetadata) -> str:
    """Format image validation as human-readable report.

    Args:
        metadata: ImageMetadata from validate_output_image()

    Returns:
        Formatted string report
    """
    lines = ["Image Validation Report", "=" * 40]

    # Status
    status = "VALID" if metadata.valid else "INVALID"
    lines.append(f"Status: {status}")

    # Dimensions
    lines.append(f"Dimensions: {metadata.width}x{metadata.height}")
    lines.append(f"Aspect Ratio: {metadata.aspect_ratio:.2f}")
    lines.append(f"Format: {metadata.format}")
    lines.append(f"File Size: {metadata.size_kb:.1f} KB")

    # Issues
    if metadata.issues:
        lines.append("")
        lines.append("ISSUES:")
        for issue in metadata.issues:
            lines.append(f"  - {issue}")

    # Warnings
    if metadata.warnings:
        lines.append("")
        lines.append("WARNINGS:")
        for warning in metadata.warnings:
            lines.append(f"  - {warning}")

    return "\n".join(lines)


def check_publication_ready(
    path: str | Path,
    target_dpi: int = 300,
    min_width_inches: float = 3.0,
) -> tuple[bool, list[str]]:
    """Check if image meets publication requirements.

    Args:
        path: Path to image file
        target_dpi: Target DPI for publication (default 300)
        min_width_inches: Minimum width in inches (default 3")

    Returns:
        Tuple of (is_ready, list of issues)
    """
    issues = []
    metadata = validate_output_image(path, check_colors=False)

    if not metadata.valid:
        return False, metadata.issues

    # Calculate effective size at target DPI
    width_inches = metadata.width / target_dpi

    if width_inches < min_width_inches:
        issues.append(
            f"At {target_dpi} DPI, image is {width_inches:.1f}\" wide "
            f"(minimum {min_width_inches}\")"
        )

    # Check for common publication requirements
    if metadata.format != "PNG" and metadata.format != "TIFF":
        issues.append(f"Format {metadata.format} may not be accepted - use PNG or TIFF")

    return len(issues) == 0, issues
