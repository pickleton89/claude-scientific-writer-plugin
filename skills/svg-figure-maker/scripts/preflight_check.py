#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic SVG preflight linter for svg-figure-maker.

Checks an SVG against the rules in:
- skills/svg-figure-maker/references/svg_authoring_standards.md
- skills/svg-figure-maker/references/grid_and_layout.md
- skills/svg-figure-maker/references/anti_patterns.md
- skills/shared/references/figure_design_principles.md

Outputs JSON findings keyed to section references in those docs.

Usage:
    uv run python preflight_check.py figure.svg
    uv run python preflight_check.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json
    uv run python preflight_check.py figure.svg --strict-grid -o preflight.json

Exit codes:
    0 = pass (no fail-severity findings)
    1 = fail (≥1 fail-severity finding)
    2 = error (invalid input, parse failure)

Limitations (v0.1):
    - Does not parse SVG embedded <style> blocks. Font/color declarations
      made via CSS classes (rather than per-element attributes or inherited
      from an ancestor <g>) are not checked. Hand-authored SVGs rarely use
      embedded CSS; matplotlib and Mermaid emit per-element attributes that
      this linter does cover. If you ship SVGs that rely on <style> blocks,
      either rewrite as per-element attributes or extend this script with a
      real CSS parser.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}

# Type ladder for figure work. Per oligon-brand/SKILL.md <svg_output>, the
# ladder is the same numeric set in both pt and px ("matplotlib emits px,
# Mermaid pt; confirm sizes are in the 10/12/14/16 band"). Bare numbers
# (unitless user-units) are also accepted on the band — Inkscape and other
# editors commonly emit them.
ALLOWED_FONT_SIZES = {10, 12, 14, 16}
MIN_FONT_SIZE = 10

# Font-family must include this substring (case-insensitive).
REQUIRED_FONT_FAMILY_TOKENS = {"arial", "helvetica"}

# Disallowed font-family substrings.
FORBIDDEN_FONT_FAMILIES = {"times", "calibri", "comic sans", "courier", "georgia", "verdana"}

# Default grid unit (px / user units).
DEFAULT_GRID_UNIT = 8

# CSS named colors — partial list of the most common offenders. Anything that's
# not a hex (#RRGGBB or #RGB), "none", or a url(...) reference is flagged.
CSS_NAMED_COLORS_PATTERN = re.compile(
    r"^(?!#[0-9a-fA-F]{3,8}$)(?!none$)(?!url\()(?!rgb\()(?!rgba\()(?!currentcolor$)([a-z]+)$",
    re.IGNORECASE,
)

# Banned attributes / values.
BANNED_FILTER_VALUES = re.compile(r"(drop-shadow|blur|glow)", re.IGNORECASE)

# Color functions (rgb(), hsl(), oklch(), etc.) — banned because palette
# compliance requires hex values from brand-tokens.json. Each function name
# is matched case-insensitively as a prefix of the value (e.g., "rgb(...").
COLOR_FUNCTION_PATTERN = re.compile(
    r"^(rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color)\s*\(",
    re.IGNORECASE,
)

# Maximum rounded-corner radius (anti_patterns.md A.4). Larger reads as
# web-UI ("rounded-2xl"), not editorial figure.
MAX_ROUNDED_CORNER_RADIUS = 10


# ---------------------------------------------------------------------------
# Finding model
# ---------------------------------------------------------------------------

def _finding(
    check: str,
    severity: str,
    message: str,
    principle_ref: str = "",
    location: str | None = None,
) -> dict[str, Any]:
    """Build a finding dict in the canonical shape."""
    return {
        "check": check,
        "severity": severity,  # "pass" | "warn" | "fail"
        "principle_ref": principle_ref,
        "message": message,
        "location": location,
    }


# ---------------------------------------------------------------------------
# Brand token loader
# ---------------------------------------------------------------------------

def load_palette(tokens_path: Path | None) -> set[str] | None:
    """Load the set of allowed hex colors from a brand-tokens.json file.

    Returns a set of uppercase hexes (#RRGGBB) or None if no tokens path given.
    """
    if tokens_path is None:
        return None

    if not tokens_path.exists():
        raise FileNotFoundError(f"Tokens file not found: {tokens_path}")

    data = json.loads(tokens_path.read_text())
    hexes: set[str] = set()

    # The oligon-brand tokens nest as colors.{category}.{name}.{hex}.
    colors = data.get("colors", {})
    for _category, entries in colors.items():
        if not isinstance(entries, dict):
            continue
        for _name, entry in entries.items():
            if isinstance(entry, dict) and "hex" in entry:
                hexes.add(entry["hex"].upper())

    return hexes


# ---------------------------------------------------------------------------
# SVG traversal helpers
# ---------------------------------------------------------------------------

def _strip_ns(tag: str) -> str:
    """Strip the {namespace} prefix from an ElementTree tag."""
    return tag.split("}", 1)[1] if "}" in tag else tag


def _iter_elements(root: ET.Element):
    """Yield (element, local_tag) for every element including root."""
    yield root, _strip_ns(root.tag)
    for el in root.iter():
        if el is root:
            continue
        yield el, _strip_ns(el.tag)


def _parse_font_size(value: str) -> tuple[float, str | None] | None:
    """Parse a font-size attribute value into (numeric_value, unit_or_None).

    Returns None for unparseable values. Acceptable units per the brand
    contract (oligon-brand/SKILL.md <svg_output>): "pt", "px", or absent.
    The ladder check {10,12,14,16} applies identically in pt and px per
    that contract — both forms are emitted by tools the brand supports
    (matplotlib emits px, Mermaid pt, hand editors often emit bare).
    """
    if not value:
        return None
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(pt|px)?\s*$", value)
    if not m:
        return None
    return float(m.group(1)), m.group(2)


def _resolve_inherited_font_family(el: ET.Element, parents: dict[int, ET.Element]) -> str | None:
    """Walk up the parent chain looking for a font-family attribute."""
    current: ET.Element | None = el
    while current is not None:
        ff = current.attrib.get("font-family")
        if ff:
            return ff
        # check style attribute
        style = current.attrib.get("style", "")
        m = re.search(r"font-family\s*:\s*([^;]+)", style)
        if m:
            return m.group(1)
        current = parents.get(id(current))
    return None


def _resolve_inherited_font_size(el: ET.Element, parents: dict[int, ET.Element]) -> str | None:
    """Walk up the parent chain looking for a font-size attribute."""
    current: ET.Element | None = el
    while current is not None:
        fs = current.attrib.get("font-size")
        if fs:
            return fs
        style = current.attrib.get("style", "")
        m = re.search(r"font-size\s*:\s*([^;]+)", style)
        if m:
            return m.group(1)
        current = parents.get(id(current))
    return None


def _build_parent_map(root: ET.Element) -> dict[int, ET.Element]:
    """Map id(child) → parent element (ElementTree has no .getparent())."""
    parents: dict[int, ET.Element] = {}
    for parent in root.iter():
        for child in parent:
            parents[id(child)] = parent
    return parents


# ---------------------------------------------------------------------------
# Individual checks — each returns a list of findings.
# ---------------------------------------------------------------------------

def check_viewbox(root: ET.Element) -> list[dict[str, Any]]:
    vb = root.attrib.get("viewBox")
    if not vb:
        return [_finding(
            check="viewbox_present",
            severity="fail",
            principle_ref="svg_authoring_standards.md#viewbox",
            message="Root <svg> has no viewBox attribute. viewBox is required for scalable, distortion-free figures.",
            location="<svg>",
        )]
    parts = vb.strip().split()
    if len(parts) != 4:
        return [_finding(
            check="viewbox_present",
            severity="fail",
            principle_ref="svg_authoring_standards.md#viewbox",
            message=f"viewBox should have 4 values (x y width height); got: '{vb}'",
            location="<svg>",
        )]
    return [_finding(
        check="viewbox_present",
        severity="pass",
        principle_ref="svg_authoring_standards.md#viewbox",
        message=f"viewBox present: '{vb}'",
    )]


def check_no_root_dimensions(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    if "width" in root.attrib or "height" in root.attrib:
        findings.append(_finding(
            check="no_root_dimensions",
            severity="warn",
            principle_ref="svg_authoring_standards.md#viewbox",
            message="Root <svg> declares width/height attributes. Prefer viewBox alone for scalability; remove width/height.",
            location="<svg>",
        ))
    else:
        findings.append(_finding(
            check="no_root_dimensions",
            severity="pass",
            principle_ref="svg_authoring_standards.md#viewbox",
            message="No explicit width/height on root <svg>; uses viewBox alone.",
        ))
    return findings


def check_accessibility_tags(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    title_el = root.find(f"{{{SVG_NS}}}title")
    desc_el = root.find(f"{{{SVG_NS}}}desc")
    if title_el is None or not (title_el.text or "").strip():
        findings.append(_finding(
            check="root_title_present",
            severity="fail",
            principle_ref="figure_design_principles.md§4.2",
            message="Root <svg> has no non-empty <title> element. Required for screen-reader accessibility.",
            location="<svg>",
        ))
    else:
        findings.append(_finding(
            check="root_title_present",
            severity="pass",
            principle_ref="figure_design_principles.md§4.2",
            message=f"<title>: '{(title_el.text or '').strip()[:80]}'",
        ))

    if desc_el is None or not (desc_el.text or "").strip():
        findings.append(_finding(
            check="root_desc_present",
            severity="fail",
            principle_ref="figure_design_principles.md§4.2",
            message="Root <svg> has no non-empty <desc> element. Required for the 2-sentence alt-text formula.",
            location="<svg>",
        ))
    else:
        text = (desc_el.text or "").strip()
        findings.append(_finding(
            check="root_desc_present",
            severity="pass",
            principle_ref="figure_design_principles.md§4.2",
            message=f"<desc>: '{text[:80]}{'...' if len(text) > 80 else ''}'",
        ))
    return findings


def check_text_font_family(root: ET.Element, parents: dict[int, ET.Element]) -> list[dict[str, Any]]:
    findings = []
    fail_count = 0
    pass_count = 0
    for el, tag in _iter_elements(root):
        if tag not in ("text", "tspan"):
            continue
        ff = _resolve_inherited_font_family(el, parents)
        if not ff:
            fail_count += 1
            findings.append(_finding(
                check="text_font_family",
                severity="fail",
                principle_ref="figure_design_principles.md§2.2",
                message=f"<{tag}> has no font-family (not even inherited from a parent <g>). Add font-family='Arial, Helvetica, sans-serif'.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        ff_lower = ff.lower()
        # Must include arial OR helvetica
        if not any(token in ff_lower for token in REQUIRED_FONT_FAMILY_TOKENS):
            fail_count += 1
            findings.append(_finding(
                check="text_font_family",
                severity="fail",
                principle_ref="figure_design_principles.md§2.2",
                message=f"<{tag}> font-family='{ff}' missing Arial/Helvetica.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        # Must not include forbidden families
        forbidden_hit = [f for f in FORBIDDEN_FONT_FAMILIES if f in ff_lower]
        if forbidden_hit:
            fail_count += 1
            findings.append(_finding(
                check="text_font_family",
                severity="fail",
                principle_ref="figure_design_principles.md§2.2",
                message=f"<{tag}> font-family contains forbidden family {forbidden_hit}: '{ff}'.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        pass_count += 1

    if not findings:
        findings.append(_finding(
            check="text_font_family",
            severity="pass",
            principle_ref="figure_design_principles.md§2.2",
            message="No <text>/<tspan> elements found, or all have valid font-family.",
        ))
    elif pass_count > 0 and fail_count == 0:
        # all warnings somehow? shouldn't happen, but pass through
        pass

    return findings


def check_text_font_size(root: ET.Element, parents: dict[int, ET.Element]) -> list[dict[str, Any]]:
    findings = []
    for el, tag in _iter_elements(root):
        if tag not in ("text", "tspan"):
            continue
        fs_raw = _resolve_inherited_font_size(el, parents)
        if not fs_raw:
            findings.append(_finding(
                check="text_font_size",
                severity="warn",
                principle_ref="figure_design_principles.md§2.1",
                message=f"<{tag}> has no font-size declaration. Set explicitly from the ladder {sorted(ALLOWED_FONT_SIZES)}.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        parsed = _parse_font_size(fs_raw)
        if parsed is None:
            findings.append(_finding(
                check="text_font_size",
                severity="fail",
                principle_ref="figure_design_principles.md§2.1",
                message=f"<{tag}> font-size='{fs_raw}' could not be parsed as pt, px, or a bare number.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        n, unit = parsed
        # Tolerance for fractional values that round to a ladder integer.
        n_rounded = round(n)
        if abs(n - n_rounded) > 0.01:
            findings.append(_finding(
                check="text_font_size",
                severity="fail",
                principle_ref="figure_design_principles.md§2.1",
                message=f"<{tag}> font-size='{fs_raw}' is fractional. Use a ladder integer: {sorted(ALLOWED_FONT_SIZES)}.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        if n_rounded < MIN_FONT_SIZE:
            unit_display = unit or "user-units"
            findings.append(_finding(
                check="text_font_size",
                severity="fail",
                principle_ref="figure_design_principles.md§2.1",
                message=f"<{tag}> font-size '{fs_raw}' = {n_rounded} {unit_display} < {MIN_FONT_SIZE} floor.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
            continue
        if n_rounded not in ALLOWED_FONT_SIZES:
            findings.append(_finding(
                check="text_font_size",
                severity="fail",
                principle_ref="figure_design_principles.md§2.1",
                message=f"<{tag}> font-size '{fs_raw}' = {n_rounded} not on ladder {sorted(ALLOWED_FONT_SIZES)}.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
    if not findings:
        findings.append(_finding(
            check="text_font_size",
            severity="pass",
            principle_ref="figure_design_principles.md§2.1",
            message="All <text>/<tspan> font sizes on the 10/12/14/16 ladder.",
        ))
    return findings


def check_no_banned_filters(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    for el, tag in _iter_elements(root):
        if tag == "filter":
            findings.append(_finding(
                check="no_banned_filters",
                severity="fail",
                principle_ref="anti_patterns.md#A.1",
                message="<filter> element present. Drop-shadow/blur/glow filters are banned.",
                location=f"#{el.attrib.get('id', 'filter')}",
            ))
        if tag in ("feDropShadow", "feGaussianBlur"):
            findings.append(_finding(
                check="no_banned_filters",
                severity="fail",
                principle_ref="anti_patterns.md#A.1",
                message=f"<{tag}> element present (banned filter primitive).",
                location=f"<{tag}>",
            ))
        # Inline style filter
        style = el.attrib.get("style", "")
        if "filter" in style.lower() and BANNED_FILTER_VALUES.search(style):
            findings.append(_finding(
                check="no_banned_filters",
                severity="fail",
                principle_ref="anti_patterns.md#A.1",
                message=f"<{tag}> inline style contains banned filter: '{style}'",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
        # filter= attribute
        if el.attrib.get("filter"):
            findings.append(_finding(
                check="no_banned_filters",
                severity="fail",
                principle_ref="anti_patterns.md#A.1",
                message=f"<{tag}> has filter attribute: '{el.attrib['filter']}' — references a banned filter.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
    if not findings:
        findings.append(_finding(
            check="no_banned_filters",
            severity="pass",
            principle_ref="anti_patterns.md#A.1",
            message="No drop-shadow / blur / glow filters present.",
        ))
    return findings


def check_no_banned_elements(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    for el, tag in _iter_elements(root):
        if tag == "script":
            findings.append(_finding(
                check="no_banned_elements",
                severity="fail",
                principle_ref="anti_patterns.md#E.3",
                message="<script> element present. Figures are static; scripts are banned.",
                location=f"<{tag}>",
            ))
        if tag == "foreignObject":
            findings.append(_finding(
                check="no_banned_elements",
                severity="fail",
                principle_ref="anti_patterns.md#E.4",
                message="<foreignObject> element present. Breaks portability across renderers.",
                location=f"<{tag}>",
            ))
    if not findings:
        findings.append(_finding(
            check="no_banned_elements",
            severity="pass",
            principle_ref="anti_patterns.md#E",
            message="No <script> or <foreignObject> elements present.",
        ))
    return findings


def check_no_vertical_text(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    for el, tag in _iter_elements(root):
        if tag not in ("text", "tspan"):
            continue
        style = el.attrib.get("style", "")
        if "writing-mode" in style and "vertical" in style:
            findings.append(_finding(
                check="no_vertical_text",
                severity="fail",
                principle_ref="anti_patterns.md#C.4",
                message=f"<{tag}> uses vertical writing-mode: '{style}'.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
        if el.attrib.get("writing-mode", "").startswith("vertical"):
            findings.append(_finding(
                check="no_vertical_text",
                severity="fail",
                principle_ref="anti_patterns.md#C.4",
                message=f"<{tag}> uses vertical writing-mode attribute.",
                location=el.attrib.get("id") or f"<{tag}>",
            ))
    if not findings:
        findings.append(_finding(
            check="no_vertical_text",
            severity="pass",
            principle_ref="anti_patterns.md#C.4",
            message="No vertical writing-mode text elements.",
        ))
    return findings


def _collect_color_values(root: ET.Element) -> list[tuple[ET.Element, str, str]]:
    """Yield (element, attribute_name, value) for every fill/stroke/stop-color encountered."""
    out: list[tuple[ET.Element, str, str]] = []
    for el, _tag in _iter_elements(root):
        for attr in ("fill", "stroke", "stop-color"):
            val = el.attrib.get(attr)
            if val:
                out.append((el, attr, val))
        # also parse style
        style = el.attrib.get("style", "")
        for match in re.finditer(r"(fill|stroke|stop-color)\s*:\s*([^;]+)", style):
            out.append((el, match.group(1), match.group(2).strip()))
    return out


def check_no_oversized_rounded_corners(root: ET.Element) -> list[dict[str, Any]]:
    """Flag <rect> elements with rx/ry > MAX_ROUNDED_CORNER_RADIUS (anti_patterns.md A.4)."""
    findings = []
    for el, tag in _iter_elements(root):
        if tag != "rect":
            continue
        for attr in ("rx", "ry"):
            val = el.attrib.get(attr)
            if val is None:
                continue
            try:
                num = float(val)
            except ValueError:
                continue
            if num > MAX_ROUNDED_CORNER_RADIUS:
                findings.append(_finding(
                    check="no_oversized_rounded_corners",
                    severity="warn",
                    principle_ref="anti_patterns.md#A.4",
                    message=f"<rect> {attr}='{val}' > {MAX_ROUNDED_CORNER_RADIUS}. Reads as web-UI rather than editorial figure; cap at {MAX_ROUNDED_CORNER_RADIUS}.",
                    location=el.attrib.get("id") or "<rect>",
                ))
    if not findings:
        findings.append(_finding(
            check="no_oversized_rounded_corners",
            severity="pass",
            principle_ref="anti_patterns.md#A.4",
            message=f"No <rect> with rx/ry exceeding {MAX_ROUNDED_CORNER_RADIUS}.",
        ))
    return findings


def check_no_undocumented_gradients(root: ET.Element) -> list[dict[str, Any]]:
    """Flag any linearGradient / radialGradient (anti_patterns.md A.5).

    Gradients usually introduce off-palette colors via interpolation. If a
    gradient is genuinely needed (e.g., a colorbar derived from a CVD-safe
    sequential map), the operator can accept the warn — but the default
    posture is to flag them.
    """
    findings = []
    for el, tag in _iter_elements(root):
        if tag in ("linearGradient", "radialGradient"):
            findings.append(_finding(
                check="no_undocumented_gradients",
                severity="warn",
                principle_ref="anti_patterns.md#A.5",
                message=f"<{tag}> element present. Gradients introduce off-palette interpolation; prefer flat palette fills. If essential (colorbar), document stops in the metadata sidecar.",
                location=f"#{el.attrib.get('id', tag)}",
            ))
    if not findings:
        findings.append(_finding(
            check="no_undocumented_gradients",
            severity="pass",
            principle_ref="anti_patterns.md#A.5",
            message="No <linearGradient> or <radialGradient> elements present.",
        ))
    return findings


def check_no_color_functions(root: ET.Element) -> list[dict[str, Any]]:
    """Flag color functions (rgb/hsl/oklch/lab/etc.) in fill/stroke/stop-color.

    Brand contract: all colors come from the palette as hex values. Color
    functions defeat palette compliance because they bypass the hex check.
    """
    findings = []
    for el, attr, val in _collect_color_values(root):
        v = val.strip()
        if COLOR_FUNCTION_PATTERN.match(v):
            findings.append(_finding(
                check="no_color_functions",
                severity="fail",
                principle_ref="figure_design_principles.md§3.5",
                message=f"{attr}='{val}' uses a color function. All colors must be hex values from the palette.",
                location=el.attrib.get("id") or _strip_ns(el.tag),
            ))
    if not findings:
        findings.append(_finding(
            check="no_color_functions",
            severity="pass",
            principle_ref="figure_design_principles.md§3.5",
            message="No color functions (rgb/hsl/oklch/etc.) found.",
        ))
    return findings


def check_no_css_named_colors(root: ET.Element) -> list[dict[str, Any]]:
    findings = []
    for el, attr, val in _collect_color_values(root):
        v = val.strip()
        # Allow: hex, "none", url(...), currentColor (which gets its own check), rgb(...), rgba(...)
        if v.lower() == "currentcolor":
            findings.append(_finding(
                check="no_currentcolor",
                severity="fail",
                principle_ref="anti_patterns.md#B.3",
                message=f"{attr}='{val}' uses currentColor; defeats deterministic styling.",
                location=el.attrib.get("id") or _strip_ns(el.tag),
            ))
            continue
        if CSS_NAMED_COLORS_PATTERN.match(v):
            findings.append(_finding(
                check="no_css_named_colors",
                severity="fail",
                principle_ref="anti_patterns.md#B.2",
                message=f"{attr}='{val}' is a CSS named color; use a hex from the palette.",
                location=el.attrib.get("id") or _strip_ns(el.tag),
            ))
    if not findings:
        findings.append(_finding(
            check="no_css_named_colors",
            severity="pass",
            principle_ref="anti_patterns.md#B.2",
            message="No CSS named colors or currentColor references found.",
        ))
    return findings


def check_palette_compliance(root: ET.Element, palette: set[str] | None) -> list[dict[str, Any]]:
    if palette is None:
        return [_finding(
            check="palette_compliance",
            severity="warn",
            principle_ref="figure_design_principles.md§3.5",
            message="No --tokens path provided; skipping palette compliance check.",
        )]
    findings = []
    seen_hexes: set[str] = set()
    for el, attr, val in _collect_color_values(root):
        v = val.strip()
        m = re.match(r"^#([0-9A-Fa-f]{3,8})$", v)
        if not m:
            continue
        hex_full = v.upper()
        # normalize #RGB to #RRGGBB
        if len(hex_full) == 4:
            hex_full = "#" + "".join(c * 2 for c in hex_full[1:])
        # strip alpha if 8-char
        if len(hex_full) == 9:
            hex_full = hex_full[:7]
        seen_hexes.add(hex_full)
        if hex_full not in palette:
            findings.append(_finding(
                check="palette_compliance",
                severity="fail",
                principle_ref="figure_design_principles.md§3.5",
                message=f"{attr}='{val}' is not in the brand palette. Allowed: {sorted(palette)}.",
                location=el.attrib.get("id") or _strip_ns(el.tag),
            ))
    if not findings:
        findings.append(_finding(
            check="palette_compliance",
            severity="pass",
            principle_ref="figure_design_principles.md§3.5",
            message=f"All hex colors in palette. Used: {sorted(seen_hexes)}.",
        ))
    return findings


def _is_off_grid(value: float, unit: int) -> bool:
    return abs(value - round(value / unit) * unit) > 0.001


def check_grid_alignment(root: ET.Element, grid_unit: int, strict: bool) -> list[dict[str, Any]]:
    findings = []
    off_grid_count = 0
    total_coord_count = 0

    # Grid-eligible attributes on layout elements.
    layout_tags = {"rect", "line", "circle", "ellipse", "g", "use", "image", "text", "tspan", "polyline", "polygon"}
    layout_attrs = ("x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "width", "height")

    for el, tag in _iter_elements(root):
        if tag not in layout_tags:
            continue
        for attr in layout_attrs:
            val = el.attrib.get(attr)
            if val is None:
                continue
            try:
                num = float(val)
            except ValueError:
                continue
            total_coord_count += 1
            if _is_off_grid(num, grid_unit):
                off_grid_count += 1
                if strict:
                    findings.append(_finding(
                        check="grid_alignment",
                        severity="fail",
                        principle_ref="figure_design_principles.md§6.1",
                        message=f"<{tag}> {attr}='{val}' is off the {grid_unit}px grid.",
                        location=el.attrib.get("id") or f"<{tag}>",
                    ))

    if not strict:
        # Single summary finding (warn) instead of per-coord noise.
        if total_coord_count == 0:
            findings.append(_finding(
                check="grid_alignment",
                severity="pass",
                principle_ref="figure_design_principles.md§6.1",
                message="No layout coordinates to check.",
            ))
        elif off_grid_count == 0:
            findings.append(_finding(
                check="grid_alignment",
                severity="pass",
                principle_ref="figure_design_principles.md§6.1",
                message=f"All {total_coord_count} layout coords on the {grid_unit}px grid.",
            ))
        else:
            pct = 100 * off_grid_count / total_coord_count
            findings.append(_finding(
                check="grid_alignment",
                severity="warn",
                principle_ref="figure_design_principles.md§6.1",
                message=f"{off_grid_count}/{total_coord_count} layout coords ({pct:.0f}%) are off the {grid_unit}px grid. Run with --strict-grid for per-element findings.",
            ))
    elif not findings:
        findings.append(_finding(
            check="grid_alignment",
            severity="pass",
            principle_ref="figure_design_principles.md§6.1",
            message=f"All {total_coord_count} layout coords on the {grid_unit}px grid (strict mode).",
        ))
    return findings


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_checks(svg_path: Path, tokens_path: Path | None, grid_unit: int, strict_grid: bool) -> dict[str, Any]:
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError as e:
        return {
            "svg_path": str(svg_path),
            "checked_at": _dt.datetime.now(_dt.UTC).isoformat(),
            "overall": "fail",
            "summary": {"checks_run": 0, "fail_count": 1, "warn_count": 0, "pass_count": 0},
            "findings": [_finding(
                check="parse_svg",
                severity="fail",
                principle_ref="N/A",
                message=f"Could not parse SVG: {e}",
            )],
        }

    root = tree.getroot()
    if _strip_ns(root.tag) != "svg":
        return {
            "svg_path": str(svg_path),
            "checked_at": _dt.datetime.now(_dt.UTC).isoformat(),
            "overall": "fail",
            "summary": {"checks_run": 0, "fail_count": 1, "warn_count": 0, "pass_count": 0},
            "findings": [_finding(
                check="parse_svg",
                severity="fail",
                principle_ref="N/A",
                message=f"Root element is <{_strip_ns(root.tag)}>, expected <svg>.",
            )],
        }

    palette = load_palette(tokens_path) if tokens_path else None
    parents = _build_parent_map(root)

    findings: list[dict[str, Any]] = []
    findings.extend(check_viewbox(root))
    findings.extend(check_no_root_dimensions(root))
    findings.extend(check_accessibility_tags(root))
    findings.extend(check_text_font_family(root, parents))
    findings.extend(check_text_font_size(root, parents))
    findings.extend(check_no_banned_filters(root))
    findings.extend(check_no_banned_elements(root))
    findings.extend(check_no_vertical_text(root))
    findings.extend(check_no_css_named_colors(root))
    findings.extend(check_no_color_functions(root))
    findings.extend(check_no_oversized_rounded_corners(root))
    findings.extend(check_no_undocumented_gradients(root))
    findings.extend(check_palette_compliance(root, palette))
    findings.extend(check_grid_alignment(root, grid_unit, strict_grid))

    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    warn_count = sum(1 for f in findings if f["severity"] == "warn")
    pass_count = sum(1 for f in findings if f["severity"] == "pass")

    return {
        "svg_path": str(svg_path),
        "tokens_path": str(tokens_path) if tokens_path else None,
        "grid_unit_px": grid_unit,
        "strict_grid": strict_grid,
        "checked_at": _dt.datetime.now(_dt.UTC).isoformat(),
        "overall": "fail" if fail_count > 0 else "pass",
        "summary": {
            "checks_run": len(findings),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "pass_count": pass_count,
        },
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preflight linter for svg-figure-maker SVG output.",
    )
    parser.add_argument("svg_path", type=Path, help="Path to the SVG file to check.")
    parser.add_argument(
        "--tokens",
        type=Path,
        default=None,
        help="Path to brand-tokens.json for palette compliance check.",
    )
    parser.add_argument(
        "--grid-unit",
        type=int,
        default=DEFAULT_GRID_UNIT,
        choices=[4, 8],
        help="Grid unit in user units (default 8).",
    )
    parser.add_argument(
        "--strict-grid",
        action="store_true",
        help="Emit per-coord findings for off-grid layout values (default: summary warn only).",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Write JSON findings to this path. If omitted, prints to stdout.",
    )

    args = parser.parse_args(argv)

    if not args.svg_path.exists():
        print(f"error: SVG file not found: {args.svg_path}", file=sys.stderr)
        return 2

    result = run_checks(
        svg_path=args.svg_path,
        tokens_path=args.tokens,
        grid_unit=args.grid_unit,
        strict_grid=args.strict_grid,
    )

    output_text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(output_text)
    else:
        print(output_text)

    return 0 if result["overall"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
