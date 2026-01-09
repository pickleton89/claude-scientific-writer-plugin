#!/usr/bin/env python3
"""
Accessibility Validation for Research Posters

Validates color accessibility including:
- WCAG contrast ratios
- Colorblind-safe palette simulation
- Color extraction from LaTeX source

Usage:
    python validate_accessibility.py poster.tex
    python validate_accessibility.py --colors "#2DB2E8" "#E8622D" "#222222"
    python validate_accessibility.py poster.tex --background "#FFFFFF" --output report.json

Output: JSON report with contrast ratios and colorblind simulation results.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from utils.brand_colors import (
    OLIGON_COLORS,
    check_wcag_compliance,
    simulate_deuteranopia,
    simulate_protanopia,
    get_distinguishable_pairs,
)
from utils.schemas import ContrastCheckResult


def extract_colors_from_tex(tex_path: Path) -> list[dict[str, str]]:
    """
    Extract color definitions from LaTeX source.

    Supports:
    - \\definecolor{name}{HTML}{HEXCODE}
    - \\definecolor{name}{RGB}{r,g,b}
    - \\definecolor{name}{rgb}{r,g,b} (0-1 scale)
    - xcolor named colors

    Args:
        tex_path: Path to .tex file

    Returns:
        List of dicts with 'name' and 'hex' keys
    """
    content = tex_path.read_text(encoding="utf-8")
    colors = []

    # Pattern: \definecolor{name}{HTML}{HEXCODE}
    html_pattern = r"\\definecolor\s*\{([^}]+)\}\s*\{HTML\}\s*\{([A-Fa-f0-9]{6})\}"
    for match in re.finditer(html_pattern, content):
        colors.append({
            "name": match.group(1),
            "hex": "#" + match.group(2),
        })

    # Pattern: \definecolor{name}{RGB}{r,g,b} (0-255 scale)
    rgb_pattern = r"\\definecolor\s*\{([^}]+)\}\s*\{RGB\}\s*\{(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\}"
    for match in re.finditer(rgb_pattern, content):
        r, g, b = int(match.group(2)), int(match.group(3)), int(match.group(4))
        colors.append({
            "name": match.group(1),
            "hex": f"#{r:02x}{g:02x}{b:02x}",
        })

    # Pattern: \definecolor{name}{rgb}{r,g,b} (0-1 scale)
    rgb_float_pattern = (
        r"\\definecolor\s*\{([^}]+)\}\s*\{rgb\}\s*\{"
        r"([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)\}"
    )
    for match in re.finditer(rgb_float_pattern, content):
        r = int(float(match.group(2)) * 255)
        g = int(float(match.group(3)) * 255)
        b = int(float(match.group(4)) * 255)
        colors.append({
            "name": match.group(1),
            "hex": f"#{r:02x}{g:02x}{b:02x}",
        })

    # Also check for xcolor package color usage
    # \color{colorname} or \textcolor{colorname}{text}
    used_colors = set(re.findall(r"\\(?:text)?color\s*\{([^}]+)\}", content))

    # Map common xcolor names to hex
    xcolor_map = {
        "black": "#000000",
        "white": "#FFFFFF",
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        "yellow": "#FFFF00",
        "gray": "#808080",
        "darkgray": "#404040",
        "lightgray": "#C0C0C0",
        "brown": "#996633",
        "orange": "#FF9900",
        "purple": "#9900FF",
        "pink": "#FFB6C1",
    }

    for color_name in used_colors:
        # Skip if already defined
        if any(c["name"] == color_name for c in colors):
            continue
        # Check xcolor defaults
        if color_name.lower() in xcolor_map:
            colors.append({
                "name": color_name,
                "hex": xcolor_map[color_name.lower()],
            })

    return colors


def extract_background_color(tex_path: Path) -> str:
    """
    Try to extract background color from LaTeX source.

    Checks for common background setting patterns.

    Args:
        tex_path: Path to .tex file

    Returns:
        Background color as hex string (defaults to white)
    """
    content = tex_path.read_text(encoding="utf-8")

    # Check for tikzposter background setting
    # \usebackgroundstyle[<options>]{<background style>}
    # or direct color in colorThree (often background)
    bg_patterns = [
        r"\\colorlet\s*\{backgroundcolor\}\s*\{([^}]+)\}",
        r"\\definecolor\s*\{backgroundcolor\}\s*\{HTML\}\s*\{([A-Fa-f0-9]{6})\}",
        r"colorThree\s*=\s*\{([^}]+)\}",
    ]

    for pattern in bg_patterns:
        match = re.search(pattern, content)
        if match:
            color = match.group(1)
            if color.startswith("#") or (len(color) == 6 and all(c in "0123456789ABCDEFabcdef" for c in color)):
                return "#" + color.lstrip("#")

    return "#FFFFFF"  # Default to white


def validate_color_pair(
    foreground: str,
    background: str,
    color_name: str = "unnamed",
) -> ContrastCheckResult:
    """
    Validate a single color pair for accessibility.

    Args:
        foreground: Foreground/text color in hex
        background: Background color in hex
        color_name: Optional name for the color

    Returns:
        ContrastCheckResult with all validation data
    """
    compliance = check_wcag_compliance(foreground, background)

    # Determine WCAG level
    if compliance.aaa_normal:
        level = "AAA"
    elif compliance.aa_normal:
        level = "AA"
    elif compliance.aa_large:
        level = "AA-large"
    else:
        level = "FAIL"

    return ContrastCheckResult(
        foreground=foreground,
        background=background,
        ratio=compliance.contrast_ratio,
        wcag_level=level,
        passes_large_text=compliance.aa_large,
        passes_normal_text=compliance.aa_normal,
    )


def run_accessibility_validation(
    colors: list[str],
    background: str = "#FFFFFF",
    color_names: list[str] | None = None,
) -> dict:
    """
    Run complete accessibility validation on a color palette.

    Args:
        colors: List of foreground colors in hex format
        background: Background color in hex format
        color_names: Optional names for each color

    Returns:
        Complete validation report as dictionary
    """
    if color_names is None:
        color_names = [f"color_{i}" for i in range(len(colors))]

    results = {
        "background": background,
        "colors_checked": len(colors),
        "contrast_checks": [],
        "colorblind_simulation": {
            "deuteranopia": [],
            "protanopia": [],
        },
        "distinguishable_pairs": [],
        "summary": {
            "all_pass_large_text": True,
            "all_pass_normal_text": True,
            "colorblind_safe": True,
            "overall_pass": True,
        },
    }

    # Check contrast for each color
    for i, (color, name) in enumerate(zip(colors, color_names)):
        check = validate_color_pair(color, background, name)
        results["contrast_checks"].append({
            "name": name,
            **check.to_dict(),
        })

        if not check.passes_large_text:
            results["summary"]["all_pass_large_text"] = False
            results["summary"]["overall_pass"] = False
        if not check.passes_normal_text:
            results["summary"]["all_pass_normal_text"] = False

    # Colorblind simulation
    for i, (color, name) in enumerate(zip(colors, color_names)):
        deut_sim = simulate_deuteranopia(color)
        prot_sim = simulate_protanopia(color)

        results["colorblind_simulation"]["deuteranopia"].append({
            "name": name,
            "original": color,
            "simulated": deut_sim,
        })
        results["colorblind_simulation"]["protanopia"].append({
            "name": name,
            "original": color,
            "simulated": prot_sim,
        })

    # Check distinguishability between colors
    pairs = get_distinguishable_pairs(colors)
    for c1, c2, is_dist in pairs:
        name1 = color_names[colors.index(c1)] if c1 in colors else c1
        name2 = color_names[colors.index(c2)] if c2 in colors else c2

        results["distinguishable_pairs"].append({
            "color1": {"name": name1, "hex": c1},
            "color2": {"name": name2, "hex": c2},
            "distinguishable_under_cvd": is_dist,
        })

        if not is_dist:
            results["summary"]["colorblind_safe"] = False

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate poster color accessibility (WCAG contrast, colorblind safety)."
    )
    parser.add_argument(
        "tex_file",
        type=Path,
        nargs="?",
        help="Path to .tex file to extract colors from",
    )
    parser.add_argument(
        "--colors",
        "-c",
        nargs="+",
        help="Hex colors to validate (e.g., '#2DB2E8' '#E8622D')",
    )
    parser.add_argument(
        "--background",
        "-b",
        default="#FFFFFF",
        help="Background color (default: white)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON report path",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output JSON only (no human-readable summary)",
    )
    parser.add_argument(
        "--use-oligon",
        action="store_true",
        help="Validate Oligon brand colors instead of extracting from file",
    )

    args = parser.parse_args()

    # Determine which colors to check
    colors = []
    color_names = []

    if args.use_oligon:
        colors = list(OLIGON_COLORS.values())
        color_names = list(OLIGON_COLORS.keys())
    elif args.colors:
        colors = args.colors
        color_names = [f"color_{i}" for i in range(len(colors))]
    elif args.tex_file and args.tex_file.exists():
        extracted = extract_colors_from_tex(args.tex_file)
        colors = [c["hex"] for c in extracted]
        color_names = [c["name"] for c in extracted]

        # Try to extract background
        if args.background == "#FFFFFF":  # Only if not explicitly set
            args.background = extract_background_color(args.tex_file)
    else:
        parser.error("Must provide either --colors, --use-oligon, or a .tex file")

    if not colors:
        print("No colors found to validate", file=sys.stderr)
        sys.exit(1)

    # Run validation
    results = run_accessibility_validation(
        colors=colors,
        background=args.background,
        color_names=color_names,
    )

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Human-readable summary
        print("=" * 60)
        print("ACCESSIBILITY VALIDATION REPORT")
        print("=" * 60)
        print(f"\nBackground: {args.background}")
        print(f"Colors checked: {len(colors)}")
        print(f"\nOverall Status: {'PASS' if results['summary']['overall_pass'] else 'FAIL'}")
        print("-" * 40)

        # Contrast checks
        print("\nContrast Ratios:")
        for check in results["contrast_checks"]:
            status = "+" if check["passes_large_text"] else "X"
            level = check["wcag_level"]
            print(f"  [{status}] {check['name']}: {check['ratio']}:1 ({level})")
            print(f"      {check['foreground']} on {check['background']}")

        # Colorblind safety
        print("\nColorblind Distinguishability:")
        cvd_safe = results["summary"]["colorblind_safe"]
        print(f"  [{'+'if cvd_safe else 'X'}] Palette is {'colorblind-safe' if cvd_safe else 'NOT colorblind-safe'}")

        if not cvd_safe:
            print("\n  Problematic pairs:")
            for pair in results["distinguishable_pairs"]:
                if not pair["distinguishable_under_cvd"]:
                    print(f"    - {pair['color1']['name']} / {pair['color2']['name']}")

        # Summary
        print("\nSummary:")
        summary = results["summary"]
        print(f"  Large text (18pt+): {'PASS' if summary['all_pass_large_text'] else 'FAIL'}")
        print(f"  Normal text: {'PASS' if summary['all_pass_normal_text'] else 'FAIL'}")
        print(f"  Colorblind safe: {'YES' if summary['colorblind_safe'] else 'NO'}")
        print("")

    # Save to file if requested
    if args.output:
        args.output.write_text(json.dumps(results, indent=2))
        if not args.json:
            print(f"Report saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["overall_pass"] else 1)


if __name__ == "__main__":
    main()
