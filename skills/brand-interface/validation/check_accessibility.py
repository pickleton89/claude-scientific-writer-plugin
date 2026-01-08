#!/usr/bin/env python3
"""
Color Accessibility Validation

Validates brand colors against WCAG accessibility guidelines:
- Contrast ratio calculations (WCAG 2.1)
- Colorblind simulation (deuteranopia, protanopia, tritanopia)
- Grayscale distinguishability

Usage:
    python check_accessibility.py /path/to/brand-tokens.json
    python check_accessibility.py /path/to/brand-tokens.json --simulate colorblind

References:
    - WCAG 2.1 Contrast Guidelines: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
    - Relative Luminance: https://www.w3.org/TR/WCAG20/#relativeluminancedef
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .validate_brand import ValidationReport


# =============================================================================
# WCAG CONTRAST CALCULATIONS
# =============================================================================

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_relative_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate relative luminance per WCAG 2.1.

    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    Where R, G, B are linearized sRGB values.
    """
    def linearize(channel: int) -> float:
        c = channel / 255.0
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Returns ratio between 1:1 (no contrast) and 21:1 (max contrast).

    WCAG Requirements:
        - Normal text: minimum 4.5:1
        - Large text: minimum 3:1
        - UI components/graphics: minimum 3:1
    """
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    l1 = rgb_to_relative_luminance(r1, g1, b1)
    l2 = rgb_to_relative_luminance(r2, g2, b2)

    # Lighter color goes in numerator
    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def passes_wcag_aa(foreground: str, background: str, is_large_text: bool = False) -> bool:
    """Check if color pair passes WCAG AA requirements."""
    ratio = contrast_ratio(foreground, background)
    threshold = 3.0 if is_large_text else 4.5
    return ratio >= threshold


def passes_wcag_aaa(foreground: str, background: str, is_large_text: bool = False) -> bool:
    """Check if color pair passes WCAG AAA requirements."""
    ratio = contrast_ratio(foreground, background)
    threshold = 4.5 if is_large_text else 7.0
    return ratio >= threshold


# =============================================================================
# GRAYSCALE CONVERSION
# =============================================================================

def to_grayscale(hex_color: str) -> int:
    """
    Convert color to grayscale value (0-255).

    Uses luminosity method: 0.299*R + 0.587*G + 0.114*B
    """
    r, g, b = hex_to_rgb(hex_color)
    return int(0.299 * r + 0.587 * g + 0.114 * b)


def grayscale_distance(color1: str, color2: str) -> int:
    """Calculate absolute difference in grayscale values."""
    g1 = to_grayscale(color1)
    g2 = to_grayscale(color2)
    return abs(g1 - g2)


def colors_distinguishable_grayscale(color1: str, color2: str, min_distance: int = 30) -> bool:
    """Check if two colors are distinguishable when printed in grayscale."""
    return grayscale_distance(color1, color2) >= min_distance


# =============================================================================
# COLORBLIND SIMULATION
# =============================================================================

# Transformation matrices for colorblind simulation
# Based on: http://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html

COLORBLIND_MATRICES = {
    "protanopia": [  # Red-blind
        [0.567, 0.433, 0.000],
        [0.558, 0.442, 0.000],
        [0.000, 0.242, 0.758],
    ],
    "deuteranopia": [  # Green-blind
        [0.625, 0.375, 0.000],
        [0.700, 0.300, 0.000],
        [0.000, 0.300, 0.700],
    ],
    "tritanopia": [  # Blue-blind
        [0.950, 0.050, 0.000],
        [0.000, 0.433, 0.567],
        [0.000, 0.475, 0.525],
    ],
}


def simulate_colorblind(hex_color: str, cvd_type: str) -> str:
    """
    Simulate how a color appears to someone with color vision deficiency.

    Parameters
    ----------
    hex_color : str
        Original hex color
    cvd_type : str
        Type of color vision deficiency: 'protanopia', 'deuteranopia', 'tritanopia'

    Returns
    -------
    str
        Simulated hex color
    """
    if cvd_type not in COLORBLIND_MATRICES:
        raise ValueError(f"Unknown CVD type: {cvd_type}. Use: {list(COLORBLIND_MATRICES.keys())}")

    r, g, b = hex_to_rgb(hex_color)
    matrix = COLORBLIND_MATRICES[cvd_type]

    # Apply transformation matrix
    new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
    new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
    new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b

    # Clamp to valid range
    new_r = max(0, min(255, int(new_r)))
    new_g = max(0, min(255, int(new_g)))
    new_b = max(0, min(255, int(new_b)))

    return f"#{new_r:02X}{new_g:02X}{new_b:02X}"


def colors_distinguishable_colorblind(
    color1: str,
    color2: str,
    cvd_type: str,
    min_distance: int = 30
) -> bool:
    """Check if two colors remain distinguishable under colorblind simulation."""
    sim1 = simulate_colorblind(color1, cvd_type)
    sim2 = simulate_colorblind(color2, cvd_type)
    return grayscale_distance(sim1, sim2) >= min_distance


# =============================================================================
# BRAND TOKEN VALIDATION
# =============================================================================

@dataclass
class AccessibilityResult:
    """Result of accessibility check for a color pair."""
    color1_name: str
    color1_hex: str
    color2_name: str
    color2_hex: str
    contrast_ratio: float
    passes_aa: bool
    passes_aaa: bool
    grayscale_distance: int
    grayscale_ok: bool
    colorblind_issues: list[str]

    @property
    def fully_accessible(self) -> bool:
        return self.passes_aa and self.grayscale_ok and len(self.colorblind_issues) == 0


def check_color_pair(
    name1: str,
    hex1: str,
    name2: str,
    hex2: str,
    is_text: bool = False
) -> AccessibilityResult:
    """
    Comprehensive accessibility check for a color pair.

    Parameters
    ----------
    name1, name2 : str
        Color names for reporting
    hex1, hex2 : str
        Hex color values
    is_text : bool
        If True, apply text contrast requirements (stricter)

    Returns
    -------
    AccessibilityResult
        Complete accessibility analysis
    """
    ratio = contrast_ratio(hex1, hex2)
    gs_dist = grayscale_distance(hex1, hex2)

    # Check colorblind distinguishability
    cb_issues = []
    for cvd_type in COLORBLIND_MATRICES:
        if not colors_distinguishable_colorblind(hex1, hex2, cvd_type):
            cb_issues.append(cvd_type)

    return AccessibilityResult(
        color1_name=name1,
        color1_hex=hex1,
        color2_name=name2,
        color2_hex=hex2,
        contrast_ratio=round(ratio, 2),
        passes_aa=ratio >= (4.5 if is_text else 3.0),
        passes_aaa=ratio >= (7.0 if is_text else 4.5),
        grayscale_distance=gs_dist,
        grayscale_ok=gs_dist >= 30,
        colorblind_issues=cb_issues,
    )


def extract_all_colors(tokens: dict) -> dict[str, str]:
    """Extract all color definitions from tokens as flat dict."""
    colors = {}

    def extract(obj: dict | list, prefix: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                if key == "hex" and isinstance(value, str):
                    # Use parent key as color name
                    parent = prefix.rsplit(".", 1)[-1] if "." in prefix else prefix
                    colors[parent] = value
                elif isinstance(value, (dict, list)):
                    extract(value, path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item.startswith("#"):
                    colors[f"{prefix}[{i}]"] = item
                elif isinstance(item, (dict, list)):
                    extract(item, f"{prefix}[{i}]")

    if "colors" in tokens:
        extract(tokens["colors"], "colors")
    if "color_cycles" in tokens:
        extract(tokens["color_cycles"], "cycles")

    return colors


def validate_colors(tokens: dict, report: "ValidationReport") -> None:
    """
    Validate all colors in tokens for accessibility.

    Adds issues to the provided ValidationReport.
    """
    from .validate_brand import ValidationIssue, Severity

    colors = extract_all_colors(tokens)

    if not colors:
        report.add_issue(ValidationIssue(
            severity=Severity.WARNING,
            category="accessibility",
            message="No colors found to validate"
        ))
        return

    # Get background color (usually white)
    background = colors.get("white", "#FFFFFF")
    text_color = colors.get("black", "#000000")

    # Check each data color against background
    data_colors = {k: v for k, v in colors.items()
                   if k not in ("white", "black", "gridline")}

    issues_found = []

    for name, hex_val in data_colors.items():
        result = check_color_pair("background", background, name, hex_val)

        if not result.passes_aa:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="accessibility",
                message=f"Color '{name}' ({hex_val}) fails WCAG AA contrast on white background (ratio: {result.contrast_ratio}:1, need 3:1)",
                suggestion="Darken this color or use a darker background"
            ))
            issues_found.append(name)

        if not result.grayscale_ok:
            # Only warn if it's supposed to be distinguishable from background
            if result.grayscale_distance < 20:
                report.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="accessibility",
                    message=f"Color '{name}' may not be visible in grayscale print (distance: {result.grayscale_distance})",
                    suggestion="Ensure figure uses redundant encoding (shapes, patterns)"
                ))

    # Check text color contrast
    text_result = check_color_pair("background", background, "text", text_color, is_text=True)
    if not text_result.passes_aa:
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="accessibility",
            message=f"Text color fails WCAG AA contrast (ratio: {text_result.contrast_ratio}:1, need 4.5:1)",
        ))

    # Check declared colorblind-safe pairs
    accessibility = tokens.get("accessibility", {})
    safe_pair = accessibility.get("colorblind_safe_pair", [])
    if len(safe_pair) == 2:
        pair_result = check_color_pair("safe[0]", safe_pair[0], "safe[1]", safe_pair[1])
        if pair_result.colorblind_issues:
            report.add_issue(ValidationIssue(
                severity=Severity.WARNING,
                category="accessibility",
                message=f"Declared colorblind_safe_pair may have issues under: {', '.join(pair_result.colorblind_issues)}",
            ))

    if not issues_found:
        report.summary["accessibility_passed"] = True
    else:
        report.summary["accessibility_issues"] = issues_found
        report.accessibility_valid = False


# =============================================================================
# CLI
# =============================================================================

def analyze_tokens_file(tokens_path: Path, verbose: bool = False) -> None:
    """Standalone analysis of a tokens file."""
    with open(tokens_path, encoding='utf-8') as f:
        tokens = json.load(f)

    colors = extract_all_colors(tokens)

    print(f"\nAnalyzing {tokens_path.name}")
    print(f"Found {len(colors)} colors\n")

    # Get background
    background = colors.get("white", "#FFFFFF")
    print(f"Background: {background}\n")

    print("Color Accessibility Report")
    print("=" * 70)
    print(f"{'Color':<20} {'Hex':<10} {'Contrast':<10} {'WCAG AA':<10} {'Grayscale':<10}")
    print("-" * 70)

    for name, hex_val in colors.items():
        if name in ("white", "gridline"):
            continue

        result = check_color_pair("bg", background, name, hex_val)
        aa_status = "PASS" if result.passes_aa else "FAIL"
        gs_status = f"{result.grayscale_distance}" + (" OK" if result.grayscale_ok else " LOW")

        print(f"{name:<20} {hex_val:<10} {result.contrast_ratio:>6.2f}:1  {aa_status:<10} {gs_status:<10}")

        if verbose and result.colorblind_issues:
            print(f"  Colorblind issues: {', '.join(result.colorblind_issues)}")

    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check color accessibility in brand tokens")
    parser.add_argument("tokens_path", type=Path, help="Path to brand-tokens.json")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed analysis")
    parser.add_argument("--simulate", choices=list(COLORBLIND_MATRICES.keys()),
                        help="Show colors under colorblind simulation")

    args = parser.parse_args()

    if not args.tokens_path.exists():
        print(f"Error: File not found: {args.tokens_path}")
        return 1

    analyze_tokens_file(args.tokens_path, verbose=args.verbose)

    if args.simulate:
        with open(args.tokens_path, encoding='utf-8') as f:
            tokens = json.load(f)
        colors = extract_all_colors(tokens)

        print(f"\nColorblind Simulation: {args.simulate}")
        print("=" * 50)
        print(f"{'Original':<15} {'Simulated':<15} {'Color'}")
        print("-" * 50)
        for name, hex_val in colors.items():
            simulated = simulate_colorblind(hex_val, args.simulate)
            print(f"{hex_val:<15} {simulated:<15} {name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
