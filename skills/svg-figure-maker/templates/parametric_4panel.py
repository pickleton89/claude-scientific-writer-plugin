#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["drawsvg>=2.4"]
# ///
"""Parametric 4-panel figure template — the canonical drawsvg starting point.

Demonstrates the discipline that makes programmatic SVG work inside this
skill's render→inspect→fix loop:

- Brand palette loaded from oligon-brand/tokens/brand-tokens.json; no hex
  is ever hard-coded as a literal in the layout code.
- Geometry pinned to the 8px figure-work grid; every coordinate, width, and
  height is divisible by 8.
- Output is byte-identical across runs given identical inputs (drawsvg's
  default `randomize_ids=False` is preserved; no random / time / dict-order
  inputs leak into the SVG).
- Root width/height attributes (drawsvg always emits them) are stripped on
  the way out so preflight's `no_root_dimensions` check passes.
- Accessibility tags (`<title>` + `<desc>`) are inserted via `dw.Title` and
  `dw.Raw` (drawsvg has no `Desc` class as of 2.4).

Usage (note `--script`, not `python`; the PEP-723 deps install via `uv run --script`):
    uv run --script templates/parametric_4panel.py --tokens ../oligon-brand/tokens/brand-tokens.json -o figure.svg
    uv run --script templates/parametric_4panel.py --tokens ../oligon-brand/tokens/brand-tokens.json > figure.svg

The output passes `scripts/preflight_check.py` with zero fail-severity
findings. Two consecutive runs against the same tokens file produce
byte-identical SVG.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

import drawsvg as dw

# --- Canvas geometry ---------------------------------------------------------
# 8px figure-work grid. The viewBox and every panel coordinate below must
# stay divisible by 8 or the preflight grid_alignment check warns.
GRID = 8
VIEWBOX_W = 1024
VIEWBOX_H = 320

# Outer margins + inter-panel gutter. PANEL_W must be a multiple of 16 (not
# just 8) so that PANEL_W // 2 — used to center text within a panel — also
# lands on the grid. Solve 2·MARGIN_X + 3·GUTTER + 4·PANEL_W = VIEWBOX_W
# with VIEWBOX_W=1024, MARGIN_X=16, GUTTER=32 → PANEL_W=224.
MARGIN_X = 16
MARGIN_TOP = 56  # leaves room for the figure title
MARGIN_BOTTOM = 32
GUTTER = 32

PANEL_COUNT = 4
PANEL_W = (VIEWBOX_W - 2 * MARGIN_X - (PANEL_COUNT - 1) * GUTTER) // PANEL_COUNT
PANEL_H = VIEWBOX_H - MARGIN_TOP - MARGIN_BOTTOM
assert PANEL_W % (2 * GRID) == 0, f"PANEL_W={PANEL_W} must be a multiple of {2 * GRID}"
assert PANEL_H % GRID == 0, f"PANEL_H={PANEL_H} must be a multiple of {GRID}"


# --- Panel data --------------------------------------------------------------
# A simple categorical encoding: each panel has a label, a numeric value
# (rendered as a filled bar), and a semantic role that picks a palette token.
# Order matters — the order of this list IS the rendered order.
class Panel(TypedDict):
    label: str
    value: int
    role: str


PANELS: list[Panel] = [
    {"label": "Control", "value": 24, "role": "neutral_primary"},
    {"label": "Treatment A", "value": 64, "role": "neutral_secondary"},
    {"label": "Treatment B", "value": 96, "role": "highlight"},  # the focal panel
    {"label": "Treatment C", "value": 48, "role": "neutral_tertiary"},
]

# Maximum bar value used to scale heights; pinned, not auto-derived, so the
# y-axis stays comparable across re-runs with different data.
VALUE_MAX = 120


# --- Brand-token loader ------------------------------------------------------


def load_palette(tokens_path: Path) -> dict[str, str]:
    """Return the role→hex mapping the demo references by name.

    Each role corresponds to a single canonical Oligon token. If the token
    file is missing a role, KeyError surfaces clearly rather than silently
    falling back to an off-brand color.
    """
    data = json.loads(tokens_path.read_text())
    colors = data["colors"]
    # Brand v5 token structure: anchor (colors.brand_anchor.brand_blue),
    # structure (colors.structure.{white,black,gridline}), and tonal ramps
    # (colors.ramps.{blue,orange,neutral}.{50..900}). Neutrals come from the
    # neutral ramp steps (900 = darkest text, 400 = muted). KeyError still
    # surfaces clearly if a role's token is missing.
    neutral = colors["ramps"]["neutral"]
    return {
        "background": colors["structure"]["white"]["hex"],
        "highlight": colors["brand_anchor"]["brand_blue"]["hex"],
        "neutral_primary": neutral["800"]["hex"],
        "neutral_secondary": neutral["600"]["hex"],
        "neutral_tertiary": neutral["400"]["hex"],
        "axis": colors["structure"]["gridline"]["hex"],
        "text": neutral["900"]["hex"],
    }


# --- Drawing ----------------------------------------------------------------


def build_drawing(palette: dict[str, str]) -> dw.Drawing:
    """Assemble the 4-panel figure. Pure function — same palette → same SVG."""
    d = dw.Drawing(VIEWBOX_W, VIEWBOX_H, origin=(0, 0))

    # Accessibility — preflight requires both <title> and <desc>.
    d.append(dw.Title("Parametric four-panel comparison"))
    d.append(
        dw.Raw(
            "<desc>Four panels comparing one control and three treatments; "
            "Treatment B is highlighted in Brand Blue as the focal condition.</desc>"
        )
    )

    # Background.
    d.append(dw.Rectangle(0, 0, VIEWBOX_W, VIEWBOX_H, fill=palette["background"]))

    # Figure title — 16pt sits at the top of the type ladder.
    d.append(
        dw.Text(
            "Treatment B elevates response 4x over control",
            x=VIEWBOX_W // 2,
            y=32,
            font_family="Arial, Helvetica, sans-serif",
            font_size=16,
            font_weight="bold",
            text_anchor="middle",
            fill=palette["text"],
        )
    )

    # Panel group — declaring font-family on the parent <g> means every
    # <text> child inherits a valid font without repeating the attribute.
    panels = dw.Group(font_family="Arial, Helvetica, sans-serif")

    for i, panel in enumerate(PANELS):
        x = MARGIN_X + i * (PANEL_W + GUTTER)
        y = MARGIN_TOP

        # Panel frame (light gray; uses the axis token so frame and gridlines stay consistent).
        panels.append(
            dw.Rectangle(x, y, PANEL_W, PANEL_H, fill="none", stroke=palette["axis"])
        )

        # Bar height scaled to VALUE_MAX, snapped to grid to keep all coords on the 8px grid.
        bar_h = _snap_to_grid(int(round(PANEL_H * (panel["value"] / VALUE_MAX))))
        bar_w = _snap_to_grid(PANEL_W - 2 * GUTTER)
        bar_x = x + (PANEL_W - bar_w) // 2
        bar_y = y + PANEL_H - bar_h
        panels.append(
            dw.Rectangle(bar_x, bar_y, bar_w, bar_h, fill=palette[panel["role"]])
        )

        # Panel label (12pt body) — sits below the panel frame.
        panels.append(
            dw.Text(
                panel["label"],
                x=x + PANEL_W // 2,
                y=y + PANEL_H + 16,
                font_size=12,
                text_anchor="middle",
                fill=palette["text"],
            )
        )

        # Value annotation (10pt small text) — sits above the bar.
        panels.append(
            dw.Text(
                str(panel["value"]),
                x=bar_x + bar_w // 2,
                y=bar_y - 8,
                font_size=10,
                text_anchor="middle",
                fill=palette["text"],
            )
        )

    d.append(panels)
    return d


def _snap_to_grid(n: int) -> int:
    """Round n to the nearest multiple of GRID (>= 0)."""
    return max(0, int(round(n / GRID)) * GRID)


# --- Post-process -----------------------------------------------------------


def render_clean_svg(d: dw.Drawing) -> str:
    """Return drawsvg output with the root width/height attributes stripped.

    drawsvg always emits `width=… height=…` on the root <svg> alongside the
    viewBox. The preflight `no_root_dimensions` check warns on this (it
    prefers viewBox alone for scalability). The fix is mechanical: pull the
    pair out of the root open-tag. A regex tied to drawsvg's exact output
    format is fine — if drawsvg ever changes its tag layout we want the test
    to fail loudly, not silently emit dimensions.
    """
    svg = d.as_svg()
    return re.sub(
        r'(\s+width="[^"]*"\s+height="[^"]*")(\s+viewBox=)',
        r"\2",
        svg,
        count=1,
    )


# --- CLI --------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parametric 4-panel figure (drawsvg programmatic template).",
    )
    parser.add_argument(
        "--tokens",
        type=Path,
        required=True,
        help="Path to brand-tokens.json.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write SVG to this path (default: stdout).",
    )
    args = parser.parse_args(argv)

    if not args.tokens.exists():
        print(f"error: tokens file not found: {args.tokens}", file=sys.stderr)
        return 2

    palette = load_palette(args.tokens)
    drawing = build_drawing(palette)
    svg = render_clean_svg(drawing)

    if args.output:
        args.output.write_text(svg)
    else:
        sys.stdout.write(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
