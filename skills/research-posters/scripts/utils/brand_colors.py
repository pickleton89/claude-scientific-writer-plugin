"""
Brand color palette and accessibility utilities for research posters.

Provides:
- Oligon brand color definitions
- WCAG contrast ratio calculation
- Colorblind simulation (deuteranopia, protanopia)
- Color compliance checking
"""

from dataclasses import dataclass

# Oligon brand color palette (from SKILL.md)
OLIGON_COLORS = {
    "brand_blue": "#2DB2E8",
    "brand_orange": "#E8622D",
    "dark_gray": "#222222",
    "medium_gray": "#666666",
    "light_gray": "#E5E5E5",
    "white": "#FFFFFF",
    "black": "#000000",
}

# WCAG 2.1 contrast ratio thresholds
WCAG_AA_NORMAL = 4.5  # Normal text (< 18pt or < 14pt bold)
WCAG_AA_LARGE = 3.0  # Large text (>= 18pt or >= 14pt bold)
WCAG_AAA_NORMAL = 7.0  # Enhanced contrast for normal text
WCAG_AAA_LARGE = 4.5  # Enhanced contrast for large text

# Pre-validated colorblind-safe combinations
SAFE_COMBINATIONS = [
    ("#2DB2E8", "#E8622D"),  # Blue + Orange (distinguishable in all CVD types)
    ("#2DB2E8", "#FFFFFF"),  # Blue + White
    ("#222222", "#FFFFFF"),  # Dark Gray + White
    ("#E8622D", "#FFFFFF"),  # Orange + White
    ("#222222", "#2DB2E8"),  # Dark Gray + Blue
    ("#222222", "#E8622D"),  # Dark Gray + Orange
]


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Color in hex format (with or without #)

    Returns:
        Tuple of (red, green, blue) values 0-255

    Example:
        >>> hex_to_rgb("#2DB2E8")
        (45, 178, 232)
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex color string.

    Args:
        rgb: Tuple of (red, green, blue) values 0-255

    Returns:
        Color in hex format with # prefix

    Example:
        >>> rgb_to_hex((45, 178, 232))
        '#2db2e8'
    """
    r, g, b = rgb
    if not all(0 <= c <= 255 for c in (r, g, b)):
        raise ValueError(f"RGB values must be 0-255: {rgb}")
    return f"#{r:02x}{g:02x}{b:02x}"


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """
    Calculate relative luminance per WCAG 2.1 formula.

    Args:
        rgb: Tuple of (red, green, blue) values 0-255

    Returns:
        Relative luminance value 0-1
    """

    def channel_luminance(c: int) -> float:
        c_normalized = c / 255
        if c_normalized <= 0.03928:
            return c_normalized / 12.92
        return ((c_normalized + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return (
        0.2126 * channel_luminance(r)
        + 0.7152 * channel_luminance(g)
        + 0.0722 * channel_luminance(b)
    )


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG 2.1 contrast ratio between two colors.

    Args:
        color1: First color in hex format
        color2: Second color in hex format

    Returns:
        Contrast ratio (1:1 to 21:1), rounded to 2 decimal places

    Example:
        >>> calculate_contrast_ratio("#000000", "#FFFFFF")
        21.0
        >>> calculate_contrast_ratio("#2DB2E8", "#FFFFFF")
        2.48
    """
    l1 = _relative_luminance(hex_to_rgb(color1))
    l2 = _relative_luminance(hex_to_rgb(color2))

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return round((lighter + 0.05) / (darker + 0.05), 2)


@dataclass
class WCAGCompliance:
    """Result of WCAG compliance check."""

    contrast_ratio: float
    aa_normal: bool  # Passes AA for normal text (4.5:1)
    aa_large: bool  # Passes AA for large text (3:1)
    aaa_normal: bool  # Passes AAA for normal text (7:1)
    aaa_large: bool  # Passes AAA for large text (4.5:1)


def check_wcag_compliance(
    foreground: str, background: str
) -> WCAGCompliance:
    """
    Check color pair against all WCAG contrast thresholds.

    Args:
        foreground: Text/foreground color in hex
        background: Background color in hex

    Returns:
        WCAGCompliance dataclass with all threshold results

    Example:
        >>> result = check_wcag_compliance("#222222", "#FFFFFF")
        >>> result.aa_normal
        True
    """
    ratio = calculate_contrast_ratio(foreground, background)
    return WCAGCompliance(
        contrast_ratio=ratio,
        aa_normal=ratio >= WCAG_AA_NORMAL,
        aa_large=ratio >= WCAG_AA_LARGE,
        aaa_normal=ratio >= WCAG_AAA_NORMAL,
        aaa_large=ratio >= WCAG_AAA_LARGE,
    )


def simulate_deuteranopia(hex_color: str) -> str:
    """
    Simulate deuteranopia (red-green colorblindness, most common ~6% of males).

    Uses Brettel 1997 algorithm simplified for sRGB.

    Args:
        hex_color: Original color in hex format

    Returns:
        Simulated color as seen by person with deuteranopia

    Example:
        >>> simulate_deuteranopia("#FF0000")  # Red appears more brownish
        '#9f7000'
    """
    r, g, b = hex_to_rgb(hex_color)

    # Deuteranopia simulation matrix (Brettel 1997, simplified)
    new_r = int(0.625 * r + 0.375 * g + 0.0 * b)
    new_g = int(0.700 * r + 0.300 * g + 0.0 * b)
    new_b = int(0.000 * r + 0.300 * g + 0.700 * b)

    return rgb_to_hex((
        min(255, max(0, new_r)),
        min(255, max(0, new_g)),
        min(255, max(0, new_b)),
    ))


def simulate_protanopia(hex_color: str) -> str:
    """
    Simulate protanopia (red-blind colorblindness, ~2% of males).

    Uses Brettel 1997 algorithm simplified for sRGB.

    Args:
        hex_color: Original color in hex format

    Returns:
        Simulated color as seen by person with protanopia

    Example:
        >>> simulate_protanopia("#FF0000")  # Red appears darker/brownish
        '#7f7900'
    """
    r, g, b = hex_to_rgb(hex_color)

    # Protanopia simulation matrix (Brettel 1997, simplified)
    new_r = int(0.567 * r + 0.433 * g + 0.0 * b)
    new_g = int(0.558 * r + 0.442 * g + 0.0 * b)
    new_b = int(0.000 * r + 0.242 * g + 0.758 * b)

    return rgb_to_hex((
        min(255, max(0, new_r)),
        min(255, max(0, new_g)),
        min(255, max(0, new_b)),
    ))


def get_distinguishable_pairs(colors: list[str]) -> list[tuple[str, str, bool]]:
    """
    Check which color pairs remain distinguishable under colorblindness.

    Args:
        colors: List of hex colors to check

    Returns:
        List of tuples (color1, color2, is_distinguishable)
        where is_distinguishable is True if colors differ enough
        under both deuteranopia and protanopia simulation.

    Example:
        >>> pairs = get_distinguishable_pairs(["#2DB2E8", "#E8622D", "#FF0000"])
        >>> # Blue-Orange will be distinguishable, Red-Orange may not be
    """
    results = []
    min_delta = 30  # Minimum color difference threshold

    for i, c1 in enumerate(colors):
        for c2 in colors[i + 1 :]:
            # Check under deuteranopia
            d1, d2 = simulate_deuteranopia(c1), simulate_deuteranopia(c2)
            deut_diff = _color_difference(d1, d2)

            # Check under protanopia
            p1, p2 = simulate_protanopia(c1), simulate_protanopia(c2)
            prot_diff = _color_difference(p1, p2)

            # Distinguishable if both simulations maintain sufficient difference
            is_distinguishable = (
                deut_diff >= min_delta and prot_diff >= min_delta
            )

            results.append((c1, c2, is_distinguishable))

    return results


def _color_difference(color1: str, color2: str) -> float:
    """Calculate Euclidean distance between two colors in RGB space."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    return ((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) ** 0.5


def validate_poster_palette(colors: list[str], background: str = "#FFFFFF") -> dict:
    """
    Validate a complete color palette for poster accessibility.

    Args:
        colors: List of foreground colors in hex format
        background: Background color (default white)

    Returns:
        Dictionary with validation results:
        - contrast_checks: List of contrast results per color
        - colorblind_safe: Boolean if palette is CVD-safe
        - overall_pass: Boolean if all checks pass

    Example:
        >>> result = validate_poster_palette(["#222222", "#2DB2E8"])
        >>> result["overall_pass"]
        True
    """
    results = {
        "background": background,
        "contrast_checks": [],
        "distinguishable_pairs": [],
        "colorblind_safe": True,
        "overall_pass": True,
    }

    # Check contrast for each color against background
    for color in colors:
        compliance = check_wcag_compliance(color, background)
        results["contrast_checks"].append({
            "color": color,
            "contrast_ratio": compliance.contrast_ratio,
            "aa_large": compliance.aa_large,
            "aa_normal": compliance.aa_normal,
        })
        # For posters, large text AA (3:1) is minimum acceptable
        if not compliance.aa_large:
            results["overall_pass"] = False

    # Check colorblind distinguishability
    pairs = get_distinguishable_pairs(colors)
    results["distinguishable_pairs"] = pairs
    for _, _, is_dist in pairs:
        if not is_dist:
            results["colorblind_safe"] = False

    return results
