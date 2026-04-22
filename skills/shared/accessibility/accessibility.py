"""Accessibility validation for scientific figures.

Provides WCAG-compliant contrast checking, colorblind safety validation,
and comprehensive accessibility auditing for figure specifications.
"""

from typing import Dict, Any, List, Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color code (e.g., "#FFFFFF" or "FFFFFF")

    Returns:
        Tuple of (R, G, B) values (0-255)
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color.

    Args:
        rgb: Tuple of (R, G, B) values (0-255)

    Returns:
        Hex color code with # prefix
    """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1.

    Uses the formula from WCAG 2.1:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B

    where R, G, B are linearized sRGB values.

    Args:
        rgb: Tuple of (R, G, B) values (0-255)

    Returns:
        Relative luminance (0.0 to 1.0)
    """

    def channel_luminance(value: int) -> float:
        v = value / 255
        if v <= 0.03928:
            return v / 12.92
        return ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return (
        0.2126 * channel_luminance(r)
        + 0.7152 * channel_luminance(g)
        + 0.0722 * channel_luminance(b)
    )


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    The contrast ratio is calculated as:
    (L1 + 0.05) / (L2 + 0.05)

    where L1 is the lighter color's luminance and L2 is the darker.

    Args:
        color1: First hex color code (e.g., "#FFFFFF")
        color2: Second hex color code (e.g., "#000000")

    Returns:
        Contrast ratio (1.0 to 21.0)
    """
    l1 = relative_luminance(hex_to_rgb(color1))
    l2 = relative_luminance(hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_contrast(
    foreground: str,
    background: str,
    is_large_text: bool = False,
    level: str = "AA",
) -> Dict[str, Any]:
    """Check if color combination meets WCAG contrast requirements.

    WCAG 2.1 defines contrast requirements:
    - Level AA: 4.5:1 for normal text, 3.0:1 for large text
    - Level AAA: 7.0:1 for normal text, 4.5:1 for large text
    - Large text: >= 18pt or >= 14pt bold

    Args:
        foreground: Foreground/text color (hex)
        background: Background color (hex)
        is_large_text: True if text is >= 18pt or >= 14pt bold
        level: "A", "AA", or "AAA"

    Returns:
        Dict with:
            - contrast_ratio: Calculated ratio
            - required_ratio: Minimum required for compliance
            - passed: Whether the combination passes
            - wcag_level: Level checked against
            - text_type: "normal" or "large"
    """
    ratio = contrast_ratio(foreground, background)

    # WCAG thresholds
    thresholds = {
        "A": {"normal": 3.0, "large": 3.0},
        "AA": {"normal": 4.5, "large": 3.0},
        "AAA": {"normal": 7.0, "large": 4.5},
    }

    text_type = "large" if is_large_text else "normal"
    required = thresholds.get(level, thresholds["AA"])[text_type]

    return {
        "contrast_ratio": round(ratio, 2),
        "required_ratio": required,
        "passed": ratio >= required,
        "wcag_level": level,
        "text_type": text_type,
        "foreground": foreground,
        "background": background,
    }


def check_palette_contrast(
    colors: List[str], background: str = "#FFFFFF", min_ratio: float = 3.0
) -> Dict[str, Any]:
    """Check contrast of all palette colors against background.

    Args:
        colors: List of hex color codes
        background: Background color to check against
        min_ratio: Minimum acceptable contrast ratio

    Returns:
        Dict with results for each color and overall assessment
    """
    results = []
    all_passed = True

    for color in colors:
        ratio = contrast_ratio(color, background)
        passed = ratio >= min_ratio
        if not passed:
            all_passed = False
        results.append(
            {"color": color, "ratio": round(ratio, 2), "passed": passed}
        )

    return {
        "background": background,
        "min_ratio_required": min_ratio,
        "all_passed": all_passed,
        "colors": results,
        "failed_count": sum(1 for r in results if not r["passed"]),
    }


def validate_accessibility(specs: Dict[str, Any]) -> Dict[str, Any]:
    """Validate figure specifications against accessibility requirements.

    Checks:
    - Font size minimums (7pt absolute minimum)
    - Line weight minimums (0.5pt minimum)
    - Text/background contrast (WCAG AA)
    - Color count recommendations (<= 7 for categorical)
    - Redundant encoding presence

    Args:
        specs: Figure specification dict with color_palette, typography, etc.

    Returns:
        Validation result with:
            - passed: Overall pass/fail
            - errors: List of critical failures
            - warnings: List of recommendations
            - checks_performed: List of checks run
    """
    errors = []
    warnings = []

    # Font size check
    typography = specs.get("typography", {})
    min_font = typography.get("min_pt", 0)
    if min_font > 0:  # Only check if specified
        if min_font < 7:
            errors.append(f"Minimum font size {min_font}pt is below 7pt threshold")
        elif min_font < 8:
            warnings.append(f"Font size {min_font}pt is at minimum; 8pt+ recommended")

    # Line weight check
    min_line = specs.get("min_line_weight_pt", 0)
    if min_line > 0:  # Only check if specified
        if min_line < 0.5:
            errors.append(f"Line weight {min_line}pt is below 0.5pt minimum")
        elif min_line < 1.0:
            warnings.append(f"Line weight {min_line}pt is thin; 1.0pt+ recommended")

    # Color contrast check
    palette = specs.get("color_palette", {})
    text_color = palette.get("text", palette.get("primary", "#000000"))
    bg_color = palette.get("background", "#FFFFFF")

    contrast_result = check_contrast(text_color, bg_color)
    if not contrast_result["passed"]:
        errors.append(
            f"Text/background contrast {contrast_result['contrast_ratio']}:1 "
            f"is below WCAG AA minimum of {contrast_result['required_ratio']}:1"
        )

    # Data color contrast check (against background)
    data_colors = palette.get("colors", [])
    if data_colors:
        for i, color in enumerate(data_colors):
            ratio = contrast_ratio(color, bg_color)
            if ratio < 3.0:
                warnings.append(
                    f"Data color {i + 1} ({color}) has low contrast {ratio:.1f}:1 "
                    "against background; ensure adequate line weight or marker size"
                )

    # Color count check
    n_colors = len(data_colors) if data_colors else len(
        [k for k in palette.keys() if k not in ["text", "background", "primary"]]
    )
    if n_colors > 7:
        warnings.append(
            f"Palette has {n_colors} colors; <= 7 recommended for categorical data"
        )

    # Redundant encoding check
    redundant = specs.get("accessibility", {}).get("redundant_encoding", [])
    if not redundant and n_colors > 2:
        warnings.append(
            "No redundant encoding specified; add shapes or patterns for colorblind accessibility"
        )

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_performed": [
            "font_size",
            "line_weight",
            "text_contrast",
            "data_color_contrast",
            "color_count",
            "redundant_encoding",
        ],
    }


def simulate_colorblindness(hex_color: str, cvd_type: str = "deuteranopia") -> str:
    """Simulate how a color appears under color vision deficiency.

    This is a simplified simulation. For accurate simulation, use specialized
    libraries like colorspacious or colour-science.

    Args:
        hex_color: Original hex color
        cvd_type: Type of CVD ("deuteranopia", "protanopia", "tritanopia")

    Returns:
        Simulated hex color (approximate)
    """
    r, g, b = hex_to_rgb(hex_color)

    # Simplified transformation matrices (approximations)
    if cvd_type == "deuteranopia":
        # Green-blind: most common form
        new_r = int(0.625 * r + 0.375 * g)
        new_g = int(0.7 * r + 0.3 * g)
        new_b = b
    elif cvd_type == "protanopia":
        # Red-blind
        new_r = int(0.567 * r + 0.433 * g)
        new_g = int(0.558 * r + 0.442 * g)
        new_b = b
    elif cvd_type == "tritanopia":
        # Blue-blind: rare
        new_r = r
        new_g = int(0.95 * g + 0.05 * b)
        new_b = int(0.433 * g + 0.567 * b)
    else:
        return hex_color

    # Clamp values
    new_r = max(0, min(255, new_r))
    new_g = max(0, min(255, new_g))
    new_b = max(0, min(255, new_b))

    return rgb_to_hex((new_r, new_g, new_b))


def check_colorblind_distinguishability(
    colors: List[str], min_difference: float = 30.0
) -> Dict[str, Any]:
    """Check if colors remain distinguishable under color vision deficiency.

    Uses simplified Euclidean distance in RGB space after CVD simulation.
    For rigorous checking, use perceptual color spaces (CIELAB).

    Args:
        colors: List of hex colors to check
        min_difference: Minimum RGB distance to consider distinguishable

    Returns:
        Dict with distinguishability assessment
    """
    issues = []

    for cvd_type in ["deuteranopia", "protanopia"]:
        simulated = [simulate_colorblindness(c, cvd_type) for c in colors]

        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                rgb1 = hex_to_rgb(simulated[i])
                rgb2 = hex_to_rgb(simulated[j])
                distance = (
                    (rgb1[0] - rgb2[0]) ** 2
                    + (rgb1[1] - rgb2[1]) ** 2
                    + (rgb1[2] - rgb2[2]) ** 2
                ) ** 0.5

                if distance < min_difference:
                    issues.append(
                        {
                            "cvd_type": cvd_type,
                            "color1": colors[i],
                            "color2": colors[j],
                            "simulated1": simulated[i],
                            "simulated2": simulated[j],
                            "distance": round(distance, 1),
                        }
                    )

    return {
        "distinguishable": len(issues) == 0,
        "issues": issues,
        "colors_checked": len(colors),
        "cvd_types_checked": ["deuteranopia", "protanopia"],
    }
