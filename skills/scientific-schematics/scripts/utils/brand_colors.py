"""Brand color palettes for scientific diagrams.

Provides standardized color palettes including brand-specific colors,
colorblind-safe options, and accessibility-compliant schemes.

Usage:
    >>> from utils.brand_colors import get_palette, inject_colors_into_prompt
    >>> palette = get_palette("oligon")
    >>> print(palette.primary)
    '#2DB2E8'
    >>> enhanced_prompt = inject_colors_into_prompt("Create a flowchart", "okabe-ito")
"""

from __future__ import annotations

from typing import NamedTuple


class ColorPalette(NamedTuple):
    """A color palette with primary, contrast, and supporting colors."""

    primary: str  # Main highlight color
    contrast: str  # Contrasting accent color
    text: str  # Primary text color
    secondary: str  # Supporting/muted color
    background: str  # Background color
    name: str  # Human-readable palette name


# Oligon Scientific Brand (default)
OLIGON_BRAND = ColorPalette(
    primary="#2DB2E8",  # Brand Blue - highlights, key components
    contrast="#E8622D",  # Orange - warnings, opposing elements
    text="#222222",  # Dark Gray - primary text
    secondary="#666666",  # Medium Gray - supporting components
    background="#FFFFFF",  # White - clean background
    name="Oligon Scientific",
)

# Okabe-Ito Colorblind-Safe Palette
# https://jfly.uni-koeln.de/color/
OKABE_ITO = ColorPalette(
    primary="#0072B2",  # Blue
    contrast="#D55E00",  # Vermillion
    text="#000000",  # Black
    secondary="#56B4E9",  # Sky Blue
    background="#FFFFFF",  # White
    name="Okabe-Ito (Colorblind Safe)",
)

# Extended Okabe-Ito colors for reference
OKABE_ITO_EXTENDED = {
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "yellow": "#F0E442",
    "bluish_green": "#009E73",
    "sky_blue": "#56B4E9",
    "orange": "#E69F00",
    "reddish_purple": "#CC79A7",
    "black": "#000000",
}

# Generic Scientific (conservative)
GENERIC_SCIENTIFIC = ColorPalette(
    primary="#4A90D9",  # Medium Blue
    contrast="#D94A4A",  # Medium Red
    text="#333333",  # Dark Gray
    secondary="#7A7A7A",  # Medium Gray
    background="#FFFFFF",  # White
    name="Generic Scientific",
)

# Nature Publishing Group style
NATURE_STYLE = ColorPalette(
    primary="#1F77B4",  # Nature blue
    contrast="#FF7F0E",  # Nature orange
    text="#2E2E2E",  # Near black
    secondary="#7F7F7F",  # Gray
    background="#FFFFFF",  # White
    name="Nature Style",
)

# High Contrast (accessibility focused)
HIGH_CONTRAST = ColorPalette(
    primary="#000080",  # Navy blue
    contrast="#800000",  # Maroon
    text="#000000",  # Black
    secondary="#404040",  # Dark gray
    background="#FFFFFF",  # White
    name="High Contrast",
)

# Grayscale (for print without color)
GRAYSCALE = ColorPalette(
    primary="#404040",  # Dark gray
    contrast="#808080",  # Medium gray
    text="#000000",  # Black
    secondary="#A0A0A0",  # Light gray
    background="#FFFFFF",  # White
    name="Grayscale",
)

# All available palettes
PALETTES: dict[str, ColorPalette] = {
    "oligon": OLIGON_BRAND,
    "brand": OLIGON_BRAND,
    "default": OLIGON_BRAND,
    "okabe-ito": OKABE_ITO,
    "okabe_ito": OKABE_ITO,
    "colorblind": OKABE_ITO,
    "colorblind-safe": OKABE_ITO,
    "accessibility": OKABE_ITO,
    "generic": GENERIC_SCIENTIFIC,
    "scientific": GENERIC_SCIENTIFIC,
    "nature": NATURE_STYLE,
    "npg": NATURE_STYLE,
    "high-contrast": HIGH_CONTRAST,
    "high_contrast": HIGH_CONTRAST,
    "contrast": HIGH_CONTRAST,
    "grayscale": GRAYSCALE,
    "greyscale": GRAYSCALE,
    "bw": GRAYSCALE,
}


def get_palette(name: str = "default") -> ColorPalette:
    """Get color palette by name.

    Args:
        name: Palette name (case-insensitive). Options include:
            - "oligon", "brand", "default" - Oligon Scientific brand
            - "okabe-ito", "colorblind", "accessibility" - Colorblind-safe
            - "generic", "scientific" - Conservative scientific
            - "nature", "npg" - Nature Publishing Group style
            - "high-contrast", "contrast" - High contrast for accessibility
            - "grayscale", "bw" - Black and white / grayscale

    Returns:
        ColorPalette with primary, contrast, text, secondary, background colors
    """
    return PALETTES.get(name.lower().replace(" ", "-"), OLIGON_BRAND)


def get_extended_okabe_ito() -> dict[str, str]:
    """Get the full Okabe-Ito colorblind-safe palette.

    Returns:
        Dictionary mapping color names to hex values
    """
    return OKABE_ITO_EXTENDED.copy()


def format_color_guidance(palette: ColorPalette) -> str:
    """Format palette as prompt guidance text.

    Args:
        palette: ColorPalette to format

    Returns:
        Formatted text suitable for inclusion in AI prompts
    """
    return f"""Use the {palette.name} color scheme:
- Primary elements: {palette.primary} - highlights, key components
- Contrast/alerts: {palette.contrast} - warnings, opposing elements
- Text/labels: {palette.text} - primary text
- Secondary elements: {palette.secondary} - supporting components
- Background: {palette.background} - clean background"""


def inject_colors_into_prompt(
    prompt: str,
    palette_name: str = "default",
    force: bool = False,
) -> str:
    """Append color guidance to prompt if not already present.

    Args:
        prompt: Original user prompt
        palette_name: Name of palette to use
        force: If True, add guidance even if colors already specified

    Returns:
        Prompt with color guidance appended (if needed)
    """
    # Check if colors are already specified (unless force=True)
    if not force:
        color_indicators = [
            "#",  # Hex color
            "color:",
            "palette",
            "okabe",
            "colorblind",
            "rgb(",
            "hsl(",
        ]
        prompt_lower = prompt.lower()
        if any(indicator in prompt_lower for indicator in color_indicators):
            return prompt

    palette = get_palette(palette_name)
    color_guidance = format_color_guidance(palette)

    return f"{prompt}\n\n{color_guidance}"


def validate_contrast(
    foreground: str,
    background: str,
    min_ratio: float = 4.5,
) -> tuple[bool, float]:
    """Check if two colors meet WCAG contrast requirements.

    Args:
        foreground: Hex color for foreground (e.g., "#000000")
        background: Hex color for background (e.g., "#FFFFFF")
        min_ratio: Minimum contrast ratio (4.5 for AA, 7.0 for AAA)

    Returns:
        Tuple of (meets_requirement, actual_ratio)
    """

    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore

    def relative_luminance(rgb: tuple[int, int, int]) -> float:
        """Calculate relative luminance per WCAG 2.1."""
        r, g, b = [x / 255.0 for x in rgb]

        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    lum1 = relative_luminance(hex_to_rgb(foreground))
    lum2 = relative_luminance(hex_to_rgb(background))

    # Ensure lighter color is in numerator
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    ratio = (lighter + 0.05) / (darker + 0.05)

    return ratio >= min_ratio, ratio


def get_palette_names() -> list[str]:
    """Get list of available palette names (unique).

    Returns:
        Sorted list of unique palette names
    """
    # Get unique palettes by their actual name
    seen_names = set()
    unique_keys = []
    for key, palette in PALETTES.items():
        if palette.name not in seen_names:
            seen_names.add(palette.name)
            unique_keys.append(key)
    return sorted(unique_keys)
