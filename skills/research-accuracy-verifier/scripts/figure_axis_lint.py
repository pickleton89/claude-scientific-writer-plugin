#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 deterministic figure-audit rules (FIGURE_INTEGRITY, inbound).

Runs ONLY when the user supplies machine-readable source (the generating SVG,
a values table, or axis metadata) — the inbound analogue of the governing
insight: we can only do exact checks when ground truth is available. When no
source is supplied, Tier-1 is skipped and the audit falls through to the
Tier-3 instrumented vision-judge (see references/figure_integrity_audit.md).

This module is a thin adapter that REUSES the Track-B generation-time linters
rather than reimplementing them:
  - plotting-libraries/scripts/validate_data.py :: check_closure,
    check_continuous_as_bars, check_riskratio_as_bars
  - svg-figure-maker/scripts/preflight_check.py :: run_checks
and adds the Misviz axis-metadata rules (axis truncation) that no existing
linter covers. Emits findings in the schemas/figure_audit_finding.json shape.

Stdlib-only. Sibling linters are imported lazily so a missing skill dir
degrades to "rule skipped", never a crash.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS = Path(__file__).resolve().parents[2]
for _sib in ("plotting-libraries/scripts", "svg-figure-maker/scripts"):
    _p = _SKILLS / _sib
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _finding(
    fid: str,
    *,
    figure_file: str,
    dimension: str,
    metric_id: str,
    score: int,
    categorical: bool,
    severity: str,
    observation: str,
    recommended_action: str,
    source_check: str,
    confidence: str = "high",
    region: str | None = None,
) -> dict[str, Any]:
    """Build a Tier-1 FigureAuditFinding (always tier 1_deterministic, so
    source_check is mandatory per FD-P6)."""
    return {
        "id": fid,
        "figure_ref": {"file": figure_file, "panel": None, "region": region},
        "dimension": dimension,
        "metric_id": metric_id,
        "score": score,
        "categorical": categorical,
        "severity": severity,
        "tier": "1_deterministic",
        "source_check": source_check,
        "observation": observation,
        "evidence_snippet": None,
        "recommended_action": recommended_action,
        "confidence": confidence,
        "decaying_signal_caveat": None,
    }


def check_axis_truncation(
    axis_meta: dict[str, Any], *, figure_file: str, fid: str = "FA001"
) -> list[dict[str, Any]]:
    """Misviz rule: a quantitative bar-chart axis whose origin != 0.

    axis_meta = {"chart": "bar", "type": "quantitative",
                 "min": <axis lower bound>, "max": <axis upper bound>,
                 "data_min": <smallest plotted value>}
    Truncation (axis min > 0 on a bar geometry) exaggerates differences. Graded
    (metric 2.3, not a categorical ⚑) — MAJOR with a severity-scaling note.
    """
    chart = str(axis_meta.get("chart", "")).lower()
    if chart not in {"bar", "column", "stacked_bar"}:
        return []
    if str(axis_meta.get("type", "quantitative")).lower() != "quantitative":
        return []
    amin = axis_meta.get("min")
    amax = axis_meta.get("max")
    if amin is None or amax is None:
        return []
    if amin <= 0:
        return []
    full = float(amax) - 0.0
    suppressed = float(amin) - 0.0
    frac = suppressed / full if full > 0 else 0.0
    return [
        _finding(
            fid,
            figure_file=figure_file,
            dimension="D2_quant_semantic",
            metric_id="2.3",
            score=2,
            categorical=False,
            severity="MAJOR",
            observation=(
                f"Bar-chart quantitative axis starts at {amin}, not 0 "
                f"(suppressed/full ≈ {frac:.0%}). Truncation exaggerates the "
                "visual difference between bars (Misviz axis-truncation rule)."
            ),
            recommended_action="request the source data and confirm a zero baseline (or a dot plot)",
            source_check="figure_axis_lint.check_axis_truncation",
            region="quantitative axis",
        )
    ]


def check_closure_rule(
    parts: list[float],
    encoding: str,
    *,
    figure_file: str,
    declared_total: float | None = None,
    fid: str = "FA002",
) -> list[dict[str, Any]]:
    """Categorical ⚑ metric 2.2: pie/stacked parts must sum to the whole.

    Reuses plotting-libraries validate_data.check_closure when importable; falls
    back to inline arithmetic otherwise. A real closure failure -> score 2,
    categorical, CRITICAL.
    """
    failed = False
    detail = ""
    try:
        from validate_data import check_closure  # type: ignore

        # A pie/donut is a parts-of-whole that MUST sum to 100% — force
        # percent-mode so a sum like 105 is flagged (validate_data's auto-detect
        # only enters percent-mode when the sum is already near 100).
        force_percent = (
            True
            if encoding.lower() in {"pie", "donut"} and declared_total is None
            else None
        )
        result = check_closure(
            parts, encoding, declared_total=declared_total, expect_percent=force_percent
        )
        failed = not result.valid
        detail = "; ".join(result.errors) if result.errors else ""
    except Exception:
        whole = declared_total if declared_total is not None else 100.0
        s = sum(p for p in parts if isinstance(p, (int, float)))
        gap = abs(s - whole)
        tol = 1.0 if declared_total is None else max(1e-9, 0.005 * abs(whole))
        failed = gap > tol
        detail = f"parts sum to {s}, whole is {whole} (gap {gap})"

    if not failed:
        return []
    return [
        _finding(
            fid,
            figure_file=figure_file,
            dimension="D2_quant_semantic",
            metric_id="2.2",
            score=2,
            categorical=True,
            severity="CRITICAL",
            observation=(
                f"Parts-of-whole do not reconcile ({detail}). Closure/conservation "
                "failure (a pie that doesn't sum to 100%, or stacked totals that "
                "don't reconcile) is a deterministic Class-B generative tell."
            ),
            recommended_action="obtain source data and reconcile the reported parts to the whole",
            source_check="validate_data.check_closure",
            region="parts-of-whole",
        )
    ]


def check_chart_choice(
    *, plot_type: str, data_label: str, figure_file: str, fid: str = "FA003"
) -> list[dict[str, Any]]:
    """Reuse validate_data.check_riskratio_as_bars: ratio-with-CI drawn as bars.

    Graded (metric 2.1, not categorical), MAJOR.
    """
    try:
        from validate_data import check_riskratio_as_bars  # type: ignore

        result = check_riskratio_as_bars(plot_type, data_label)
    except Exception:
        return []
    if result.valid:
        return []
    return [
        _finding(
            fid,
            figure_file=figure_file,
            dimension="D2_quant_semantic",
            metric_id="2.1",
            score=1,
            categorical=False,
            severity="MAJOR",
            observation=(
                f"A ratio-with-CI estimate ('{data_label}') is drawn as a bar; "
                "bars exaggerate the point estimate over the interval (Fujii 2023)."
            ),
            recommended_action="request the generating code and redraw as point + 95% CI",
            source_check="validate_data.check_riskratio_as_bars",
            region="encoding",
        )
    ]


def run_svg_preflight(
    svg_path: str, *, figure_file: str, fid_start: int = 10
) -> list[dict[str, Any]]:
    """Reuse preflight_check.run_checks on a source SVG; lift its categorical
    garbled-text findings into figure-audit findings (metric 1.1)."""
    try:
        from preflight_check import run_checks  # type: ignore
    except Exception:
        return []
    try:
        report = run_checks(Path(svg_path), None, grid_unit=8, strict_grid=False)
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    n = fid_start
    for f in report.get("findings", []):
        if f.get("check") == "garbled_text" and f.get("severity") == "categorical":
            out.append(
                _finding(
                    f"FA{n:03d}",
                    figure_file=figure_file,
                    dimension="D1_text_symbol",
                    metric_id="1.1",
                    score=2,
                    categorical=True,
                    severity="CRITICAL",
                    observation=f"SVG preflight garbled-text (categorical): {f.get('message', '')}",
                    recommended_action="obtain source data and retype the label from it",
                    source_check="preflight_check.run_checks/garbled_text",
                    region=f.get("location"),
                )
            )
            n += 1
    return out


def run_tier1(
    *,
    figure_file: str = "<inbound figure>",
    svg_path: str | None = None,
    axis_meta: dict[str, Any] | None = None,
    parts: list[float] | None = None,
    closure_encoding: str = "pie",
    declared_total: float | None = None,
    plot_type: str | None = None,
    data_label: str | None = None,
) -> dict[str, Any]:
    """Orchestrate Tier-1. Calls only the checks whose inputs are present.

    Returns {tier, findings, inputs_seen, note}. If NO machine-readable source
    is supplied, returns findings=[] with note='tier1_skipped_no_source' so the
    audit falls through to Tier-3 only.
    """
    inputs_seen: list[str] = []
    findings: list[dict[str, Any]] = []

    if svg_path:
        inputs_seen.append("svg")
        findings.extend(run_svg_preflight(svg_path, figure_file=figure_file))
    if axis_meta:
        inputs_seen.append("axis_meta")
        findings.extend(check_axis_truncation(axis_meta, figure_file=figure_file))
    if parts is not None:
        inputs_seen.append("parts")
        findings.extend(
            check_closure_rule(
                parts,
                closure_encoding,
                figure_file=figure_file,
                declared_total=declared_total,
            )
        )
    if plot_type and data_label:
        inputs_seen.append("plot_type+label")
        findings.extend(
            check_chart_choice(
                plot_type=plot_type, data_label=data_label, figure_file=figure_file
            )
        )

    note = "tier1_skipped_no_source" if not inputs_seen else "ok"
    return {
        "tier": "1_deterministic",
        "findings": findings,
        "inputs_seen": inputs_seen,
        "note": note,
    }
