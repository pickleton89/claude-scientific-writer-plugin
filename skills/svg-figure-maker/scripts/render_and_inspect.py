#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render-and-inspect orchestrator for svg-figure-maker.

Stage 3 + Stage 4 of the render→inspect→fix loop in one script. It:

1. Runs preflight_check.py against the SVG (Stage 3, deterministic safety net).
2. Invokes ../oligon-brand/scripts/render_svg_preview.sh to rasterize the SVG
   to a PNG preview (Stage 4).
3. Emits a unified iteration report JSON that:
   - carries the full preflight result
   - records the preview PNG path
   - tells the caller (Claude) what the next step is:
     * "fix_preflight_failures" — preflight has fail-severity findings; do
       not waste a vision iteration on a structurally broken SVG
     * "vision_critique" — preflight clean (or only warns); proceed to
       Stage 5 (Read the PNG, walk visual_critique_checklist.md)
   - seeds Stage 5 with the checklist categories (canonical labels from
     critique_finding.schema.json) so Claude has the schema-compliant
     vocabulary in hand

Usage:
    uv run python render_and_inspect.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json --iteration 1 -o report.json

Exit codes:
    0 = success — preflight clean, preview rendered, report written
    1 = preflight had fail-severity findings (report still written)
    2 = error (missing input, rasterizer not found, render failure)

Design note (deliberate non-doing):
    This script does NOT attempt the vision critique itself. Stage 5 is
    Claude's job — only a vision-capable agent can Read the PNG. The script
    seeds the structured report so the critique step is one Read away.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
PREFLIGHT_SCRIPT = HERE / "preflight_check.py"
RENDER_SCRIPT = (SKILL_ROOT.parent / "oligon-brand" / "scripts" / "render_svg_preview.sh").resolve()

# Canonical category labels — MUST match schemas/critique_finding.schema.json
# `category` enum. If you change one, change both. The categories below
# correspond 1-to-1 with sections of references/visual_critique_checklist.md.
CRITIQUE_CATEGORIES = [
    {
        "category": "text_legibility",
        "principle_ref": "§2",
        "checklist_section": "Category 1",
        "questions": [
            "Every label fully visible (no clipping)?",
            "Labels readable at rendered scale (no overlap)?",
            "Size ladder used intentionally (titles > body > ticks)?",
            "No fallback / wrong-font rendering?",
        ],
    },
    {
        "category": "hierarchy",
        "principle_ref": "§5",
        "checklist_section": "Category 2",
        "questions": [
            "Takeaway message recognizable from the figure alone?",
            "One focal element draws the eye first?",
            "Secondary elements visibly subordinate?",
            "Direct labels preferred over distant legends?",
        ],
    },
    {
        "category": "alignment",
        "principle_ref": "§6",
        "checklist_section": "Category 3",
        "questions": [
            "Panels share consistent baselines / margins / gutters?",
            "Repeated labels at identical positions across panels?",
            "No elements drifted off relative to neighbors?",
            "Panel labels (A, B, C…) at identical per-panel offsets?",
        ],
    },
    {
        "category": "color_rendering",
        "principle_ref": "§3",
        "checklist_section": "Category 4",
        "questions": [
            "Brand colors render as intended (not muddy / shifted)?",
            "Color encoding is colorblind-safe?",
            "Hierarchy survives grayscale conversion?",
            "Two-channel fluorescence uses magenta + green (not red + green)?",
        ],
    },
    {
        "category": "line_crispness",
        "principle_ref": "§8",
        "checklist_section": "Category 5",
        "questions": [
            "Lines render cleanly at the rasterized scale?",
            "Stroke widths consistent for the same role?",
            "No vanishing fine lines (< 0.75pt equivalent)?",
        ],
    },
    {
        "category": "composition_balance",
        "principle_ref": "§5, §6",
        "checklist_section": "Category 6",
        "questions": [
            "Whitespace intentional (margins, gutters, padding)?",
            "Within complexity budget for this figure type?",
            "Reading order matches the conceptual flow?",
            "Room exists for legends / annotations without colliding with data?",
        ],
    },
    {
        "category": "accessibility",
        "principle_ref": "§4",
        "checklist_section": "Category 7",
        "questions": [
            "Text/background pairs meet WCAG contrast?",
            "Color paired with at least one other encoding per categorical axis?",
            "Uncertainty / significance has a non-color cue?",
        ],
    },
]


def _run_preflight(
    svg_path: Path,
    tokens_path: Path | None,
    grid_unit: int,
    strict_grid: bool,
) -> dict[str, Any]:
    """Invoke preflight_check.py as a subprocess and return its parsed JSON."""
    cmd = [
        sys.executable,
        str(PREFLIGHT_SCRIPT),
        str(svg_path),
        "--grid-unit", str(grid_unit),
    ]
    if tokens_path is not None:
        cmd.extend(["--tokens", str(tokens_path)])
    if strict_grid:
        cmd.append("--strict-grid")

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    # preflight returns 0 (pass), 1 (fail), or 2 (error). Only 2 means we
    # could not get a parseable report.
    if proc.returncode == 2:
        raise RuntimeError(
            f"preflight_check.py error (exit {proc.returncode}):\n{proc.stderr or proc.stdout}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"preflight produced unparseable JSON: {e}\n{proc.stdout[:500]}") from e


def _run_rasterizer(svg_path: Path, output_png: Path | None, scale: int) -> Path:
    """Invoke render_svg_preview.sh and return the PNG path."""
    if not RENDER_SCRIPT.exists():
        raise FileNotFoundError(
            f"Rasterizer not found at {RENDER_SCRIPT}. "
            "Expected canonical location skills/oligon-brand/scripts/render_svg_preview.sh."
        )
    if not shutil.which("rsvg-convert"):
        raise RuntimeError(
            "rsvg-convert not on PATH. Install with: brew install librsvg"
        )

    if output_png is None:
        output_png = svg_path.with_suffix(".preview.png")

    cmd = [
        str(RENDER_SCRIPT),
        str(svg_path),
        str(output_png),
        "--scale", str(scale),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"render_svg_preview.sh failed (exit {proc.returncode}):\n{proc.stderr or proc.stdout}"
        )
    if not output_png.exists() or output_png.stat().st_size == 0:
        raise RuntimeError(f"Rasterizer ran but PNG is missing or empty: {output_png}")
    return output_png


def build_report(
    svg_path: Path,
    preview_path: Path | None,
    preflight: dict[str, Any],
    iteration: int,
    render_skipped_reason: str | None = None,
) -> dict[str, Any]:
    """Combine preflight + render into the canonical iteration report."""
    fail_count = preflight["summary"]["fail_count"]

    if fail_count > 0:
        next_step = "fix_preflight_failures"
        next_step_detail = (
            f"Preflight has {fail_count} fail-severity finding(s). Edit the SVG "
            "to clear them before rasterizing again. Do not burn a vision iteration."
        )
    else:
        next_step = "vision_critique"
        next_step_detail = (
            "Preflight clean. Read the preview PNG and walk references/visual_critique_checklist.md. "
            "Emit critique.json per the schema; if findings exist, iterate; otherwise finalize."
        )

    return {
        "schema_version": "1",
        "iteration": iteration,
        "checked_at": _dt.datetime.now(_dt.UTC).isoformat(),
        "svg_path": str(svg_path),
        "preview_path": str(preview_path) if preview_path else None,
        "render_skipped_reason": render_skipped_reason,
        "preflight": preflight,
        "next_step": next_step,
        "next_step_detail": next_step_detail,
        "critique_seed": {
            "checklist_doc": "references/visual_critique_checklist.md",
            "schema": "schemas/critique_finding.schema.json",
            "categories": CRITIQUE_CATEGORIES,
        },
        "summary": {
            "preflight_fail": fail_count,
            "preflight_warn": preflight["summary"]["warn_count"],
            "preview_rendered": preview_path is not None,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an SVG to PNG and emit a structured inspection report.",
    )
    parser.add_argument("svg_path", type=Path, help="Path to the SVG to render and inspect.")
    parser.add_argument(
        "--tokens",
        type=Path,
        default=None,
        help="Path to brand-tokens.json for palette compliance.",
    )
    parser.add_argument(
        "--grid-unit",
        type=int,
        default=8,
        choices=[4, 8],
        help="Grid unit for preflight (default 8).",
    )
    parser.add_argument(
        "--strict-grid",
        action="store_true",
        help="Pass --strict-grid through to preflight.",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=2,
        help="Rasterization scale factor (default 2; use 3 for dense labels).",
    )
    parser.add_argument(
        "--iteration",
        type=int,
        default=1,
        help="Iteration number for the report (Stage 6 loop counter).",
    )
    parser.add_argument(
        "--preview-out",
        type=Path,
        default=None,
        help="Override PNG output path (default: <svg>.preview.png alongside the SVG).",
    )
    parser.add_argument(
        "--skip-render-on-fail",
        action="store_true",
        help="If preflight has any fail-severity finding, do not rasterize.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Write the report JSON to this path (default: stdout).",
    )

    args = parser.parse_args(argv)

    if not args.svg_path.exists():
        print(f"error: SVG not found: {args.svg_path}", file=sys.stderr)
        return 2

    try:
        preflight = _run_preflight(
            svg_path=args.svg_path,
            tokens_path=args.tokens,
            grid_unit=args.grid_unit,
            strict_grid=args.strict_grid,
        )
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    preflight_fail = preflight["summary"]["fail_count"] > 0
    preview_path: Path | None = None
    render_skipped_reason: str | None = None

    if preflight_fail and args.skip_render_on_fail:
        render_skipped_reason = (
            f"preflight had {preflight['summary']['fail_count']} fail finding(s) "
            "and --skip-render-on-fail was set"
        )
    else:
        try:
            preview_path = _run_rasterizer(
                svg_path=args.svg_path,
                output_png=args.preview_out,
                scale=args.scale,
            )
        except (FileNotFoundError, RuntimeError) as e:
            print(f"error: {e}", file=sys.stderr)
            # Render error is fatal — we have no way to continue the loop.
            return 2

    report = build_report(
        svg_path=args.svg_path,
        preview_path=preview_path,
        preflight=preflight,
        iteration=args.iteration,
        render_skipped_reason=render_skipped_reason,
    )

    output_text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(output_text)
    else:
        print(output_text)

    return 1 if preflight_fail else 0


if __name__ == "__main__":
    sys.exit(main())
