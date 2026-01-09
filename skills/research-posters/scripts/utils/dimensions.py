"""
Poster dimension constants and validation utilities.

Provides:
- Standard poster size definitions (ISO, US)
- PDF point/inch conversion
- Dimension validation and matching
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

# PDF points per inch (standard)
PTS_PER_INCH = 72.0

# Tolerance for dimension matching (in points)
DIMENSION_TOLERANCE_PTS = 5.0


class Orientation(Enum):
    """Poster orientation."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class PosterSize(NamedTuple):
    """Standard poster size definition."""

    name: str
    width_inches: float
    height_inches: float
    width_pts: float
    height_pts: float
    category: str  # "ISO", "US", "custom"


# Standard poster sizes (all in portrait orientation)
POSTER_SIZES: dict[str, PosterSize] = {
    # ISO A-series (poster sizes)
    "A0": PosterSize(
        name="A0",
        width_inches=33.1,
        height_inches=46.8,
        width_pts=2384,
        height_pts=3370,
        category="ISO",
    ),
    "A1": PosterSize(
        name="A1",
        width_inches=23.4,
        height_inches=33.1,
        width_pts=1684,
        height_pts=2384,
        category="ISO",
    ),
    "A2": PosterSize(
        name="A2",
        width_inches=16.5,
        height_inches=23.4,
        width_pts=1191,
        height_pts=1684,
        category="ISO",
    ),
    # US standard sizes
    "36x48": PosterSize(
        name="36x48",
        width_inches=36.0,
        height_inches=48.0,
        width_pts=2592,
        height_pts=3456,
        category="US",
    ),
    "42x56": PosterSize(
        name="42x56",
        width_inches=42.0,
        height_inches=56.0,
        width_pts=3024,
        height_pts=4032,
        category="US",
    ),
    "48x72": PosterSize(
        name="48x72",
        width_inches=48.0,
        height_inches=72.0,
        width_pts=3456,
        height_pts=5184,
        category="US",
    ),
    "36x56": PosterSize(
        name="36x56",
        width_inches=36.0,
        height_inches=56.0,
        width_pts=2592,
        height_pts=4032,
        category="US",
    ),
    # Common conference sizes
    "30x40": PosterSize(
        name="30x40",
        width_inches=30.0,
        height_inches=40.0,
        width_pts=2160,
        height_pts=2880,
        category="US",
    ),
    "24x36": PosterSize(
        name="24x36",
        width_inches=24.0,
        height_inches=36.0,
        width_pts=1728,
        height_pts=2592,
        category="US",
    ),
}


def pts_to_inches(pts: float) -> float:
    """
    Convert PDF points to inches.

    Args:
        pts: Value in PDF points

    Returns:
        Value in inches

    Example:
        >>> pts_to_inches(72)
        1.0
    """
    return pts / PTS_PER_INCH


def inches_to_pts(inches: float) -> float:
    """
    Convert inches to PDF points.

    Args:
        inches: Value in inches

    Returns:
        Value in PDF points

    Example:
        >>> inches_to_pts(1.0)
        72.0
    """
    return inches * PTS_PER_INCH


def get_poster_size(name: str) -> PosterSize | None:
    """
    Look up a standard poster size by name.

    Args:
        name: Size name (e.g., "A0", "36x48")

    Returns:
        PosterSize if found, None otherwise

    Example:
        >>> size = get_poster_size("A0")
        >>> size.width_inches
        33.1
    """
    return POSTER_SIZES.get(name.upper())


@dataclass
class DimensionMatch:
    """Result of dimension matching."""

    matched: bool
    size_name: str | None
    orientation: Orientation | None
    width_pts: float
    height_pts: float
    width_inches: float
    height_inches: float
    deviation_pts: float  # How far off from matched size


def match_dimensions(
    width_pts: float, height_pts: float, tolerance: float = DIMENSION_TOLERANCE_PTS
) -> DimensionMatch:
    """
    Match PDF dimensions to a standard poster size.

    Handles both portrait and landscape orientations.

    Args:
        width_pts: PDF width in points
        height_pts: PDF height in points
        tolerance: Maximum deviation in points to consider a match

    Returns:
        DimensionMatch with results

    Example:
        >>> result = match_dimensions(2384, 3370)
        >>> result.size_name
        'A0'
        >>> result.orientation
        <Orientation.PORTRAIT: 'portrait'>
    """
    width_inches = pts_to_inches(width_pts)
    height_inches = pts_to_inches(height_pts)

    # Determine orientation from input
    if height_pts >= width_pts:
        input_orientation = Orientation.PORTRAIT
        input_w, input_h = width_pts, height_pts
    else:
        input_orientation = Orientation.LANDSCAPE
        input_w, input_h = height_pts, width_pts  # Normalize to portrait for matching

    best_match = None
    best_deviation = float("inf")

    for size in POSTER_SIZES.values():
        # Compare against portrait dimensions
        w_dev = abs(input_w - size.width_pts)
        h_dev = abs(input_h - size.height_pts)
        total_dev = w_dev + h_dev

        if total_dev < best_deviation:
            best_deviation = total_dev
            best_match = size

    # Check if within tolerance
    if best_match and best_deviation <= tolerance * 2:
        return DimensionMatch(
            matched=True,
            size_name=best_match.name,
            orientation=input_orientation,
            width_pts=width_pts,
            height_pts=height_pts,
            width_inches=width_inches,
            height_inches=height_inches,
            deviation_pts=best_deviation,
        )

    return DimensionMatch(
        matched=False,
        size_name=None,
        orientation=input_orientation,
        width_pts=width_pts,
        height_pts=height_pts,
        width_inches=width_inches,
        height_inches=height_inches,
        deviation_pts=best_deviation if best_match else 0,
    )


def validate_dimensions(
    width_pts: float,
    height_pts: float,
    expected_size: str | None = None,
    expected_orientation: Orientation | None = None,
) -> dict:
    """
    Validate PDF dimensions against poster requirements.

    Args:
        width_pts: PDF width in points
        height_pts: PDF height in points
        expected_size: Optional expected size name (e.g., "A0")
        expected_orientation: Optional expected orientation

    Returns:
        Dictionary with validation results:
        - valid: Boolean overall validity
        - match: DimensionMatch results
        - issues: List of any validation issues

    Example:
        >>> result = validate_dimensions(2384, 3370, expected_size="A0")
        >>> result["valid"]
        True
    """
    match = match_dimensions(width_pts, height_pts)
    issues = []

    # Check if matches expected size
    if expected_size:
        expected = get_poster_size(expected_size)
        if expected:
            if match.size_name != expected.name:
                issues.append(
                    f"Size mismatch: expected {expected_size}, detected {match.size_name or 'non-standard'}"
                )
        else:
            issues.append(f"Unknown expected size: {expected_size}")

    # Check orientation
    if expected_orientation and match.orientation != expected_orientation:
        issues.append(
            f"Orientation mismatch: expected {expected_orientation.value}, "
            f"detected {match.orientation.value if match.orientation else 'unknown'}"
        )

    # Check for non-standard size
    if not match.matched:
        issues.append(
            f"Non-standard dimensions: {match.width_inches:.1f}x{match.height_inches:.1f} inches"
        )

    return {
        "valid": len(issues) == 0,
        "match": match,
        "issues": issues,
        "dimensions": {
            "width_pts": width_pts,
            "height_pts": height_pts,
            "width_inches": match.width_inches,
            "height_inches": match.height_inches,
        },
    }


def get_recommended_font_sizes(size_name: str) -> dict[str, tuple[int, int]]:
    """
    Get recommended font sizes for a poster size.

    Based on readability at typical viewing distances (3-6 feet).

    Args:
        size_name: Poster size name (e.g., "A0", "36x48")

    Returns:
        Dictionary of element -> (min_pt, max_pt) tuples

    Example:
        >>> fonts = get_recommended_font_sizes("A0")
        >>> fonts["title"]
        (72, 120)
    """
    size = get_poster_size(size_name)

    if not size:
        # Default to A0 recommendations
        return {
            "title": (72, 120),
            "section_header": (48, 72),
            "body": (24, 36),
            "caption": (18, 24),
            "references": (14, 18),
        }

    # Scale based on poster area relative to A0
    a0 = POSTER_SIZES["A0"]
    scale = (size.width_inches * size.height_inches) / (
        a0.width_inches * a0.height_inches
    )

    # Smaller posters need proportionally smaller fonts
    # but not linearly - readability matters
    scale_factor = max(0.7, min(1.0, scale**0.3))

    base_fonts = {
        "title": (72, 120),
        "section_header": (48, 72),
        "body": (24, 36),
        "caption": (18, 24),
        "references": (14, 18),
    }

    return {
        element: (int(min_pt * scale_factor), int(max_pt * scale_factor))
        for element, (min_pt, max_pt) in base_fonts.items()
    }


def calculate_dpi_for_image(
    image_width_px: int,
    image_height_px: int,
    print_width_inches: float,
    print_height_inches: float,
) -> tuple[float, float]:
    """
    Calculate effective DPI for an image at given print size.

    Args:
        image_width_px: Image width in pixels
        image_height_px: Image height in pixels
        print_width_inches: Intended print width
        print_height_inches: Intended print height

    Returns:
        Tuple of (horizontal_dpi, vertical_dpi)

    Example:
        >>> calculate_dpi_for_image(3000, 2000, 10, 6.67)
        (300.0, 299.85...)
    """
    h_dpi = image_width_px / print_width_inches if print_width_inches > 0 else 0
    v_dpi = image_height_px / print_height_inches if print_height_inches > 0 else 0
    return (round(h_dpi, 2), round(v_dpi, 2))
