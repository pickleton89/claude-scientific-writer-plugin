"""Oligon brand integration for PaperBanana figures.

Reuses ColorPalette and OLIGON_BRAND from scientific-schematics to maintain
brand consistency across visual skills.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# Load brand_colors directly from scientific-schematics via importlib
# to avoid namespace collision with our own utils/ package.
_BRAND_COLORS_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "scientific-schematics"
    / "scripts"
    / "utils"
    / "brand_colors.py"
)

_spec = importlib.util.spec_from_file_location(
    "schematics_brand_colors", _BRAND_COLORS_PATH
)
_brand_colors = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_brand_colors)

OLIGON_BRAND = _brand_colors.OLIGON_BRAND
ColorPalette = _brand_colors.ColorPalette
format_color_guidance = _brand_colors.format_color_guidance
get_palette = _brand_colors.get_palette

__all__ = [
    "OLIGON_BRAND",
    "ColorPalette",
    "get_oligon_guidelines",
    "create_oligon_style_config",
    "get_palette",
]


def get_oligon_guidelines() -> str:
    """Get Oligon aesthetic guidelines text for Stylist agent prompts.

    Returns:
        Formatted guidelines string suitable for injection into
        PaperBanana's Stylist agent prompt.
    """
    palette = OLIGON_BRAND
    return (
        f"Apply {palette.name} brand styling:\n"
        f"- Primary color (highlights, key components): {palette.primary}\n"
        f"- Contrast color (alerts, emphasis): {palette.contrast}\n"
        f"- Text color (labels, annotations): {palette.text}\n"
        f"- Secondary color (supporting elements): {palette.secondary}\n"
        f"- Background: {palette.background}\n"
        f"\n"
        f"Style: Clean, minimalist design with generous whitespace. "
        f"Professional sans-serif typography. Minimum 4.5:1 contrast ratio. "
        f"Balanced, logical composition."
    )


def create_oligon_style_config(
    palette_name: str = "oligon",
) -> dict:
    """Create Oligon style configuration in PaperBanana's expected format.

    Args:
        palette_name: Palette name (default "oligon")

    Returns:
        Dictionary with color and style configuration compatible
        with PaperBanana's guidelines format
    """
    palette = get_palette(palette_name)
    return {
        "brand": {
            "name": palette.name,
        },
        "color_palette": {
            "primary": palette.primary,
            "contrast": palette.contrast,
            "text": palette.text,
            "secondary": palette.secondary,
            "background": palette.background,
        },
        "style_rules": [
            f"Use {palette.primary} for primary elements and highlights",
            f"Use {palette.contrast} sparingly for alerts and emphasis",
            f"Use {palette.text} for all text and labels",
            f"Use {palette.secondary} for supporting/secondary elements",
            f"Maintain {palette.background} background",
            "Minimum 4.5:1 contrast ratio for text",
            "Clean, minimalist design",
        ],
    }
