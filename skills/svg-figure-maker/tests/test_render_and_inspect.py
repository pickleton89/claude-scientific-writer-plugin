"""Tests for scripts/render_and_inspect.py.

The render-and-inspect orchestrator combines preflight (Stage 3) and raster
preview (Stage 4) into a unified iteration report. Phase 3 exit criterion:
a structured report on a known-good and a known-bad fixture, with the
next_step hint reflecting preflight status.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SKILL_ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
RENDER_SCRIPT = SKILL_ROOT / "scripts" / "render_and_inspect.py"
TOKENS = SKILL_ROOT.parent / "oligon-brand" / "tokens" / "brand-tokens.json"

sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import render_and_inspect as ri  # noqa: E402


pytestmark = pytest.mark.skipif(
    shutil.which("rsvg-convert") is None,
    reason="rsvg-convert not installed; skipping render tests (brew install librsvg)",
)


# ---------------------------------------------------------------------------
# Unit tests — build_report does not require the rasterizer to be present.
# ---------------------------------------------------------------------------

def _fake_preflight(fail: int = 0, warn: int = 0) -> dict:
    return {
        "svg_path": "x.svg",
        "overall": "fail" if fail > 0 else "pass",
        "summary": {"checks_run": 1, "fail_count": fail, "warn_count": warn, "pass_count": 0},
        "findings": [],
    }


class TestBuildReport:
    def test_clean_preflight_routes_to_vision_critique(self):
        report = ri.build_report(
            svg_path=Path("figure.svg"),
            preview_path=Path("figure.preview.png"),
            preflight=_fake_preflight(),
            iteration=1,
        )
        assert report["next_step"] == "vision_critique"
        assert report["summary"]["preflight_fail"] == 0
        assert report["summary"]["preview_rendered"] is True
        assert report["preview_path"] == "figure.preview.png"

    def test_failing_preflight_routes_to_fix(self):
        report = ri.build_report(
            svg_path=Path("figure.svg"),
            preview_path=None,
            preflight=_fake_preflight(fail=3),
            iteration=2,
            render_skipped_reason="preflight fail",
        )
        assert report["next_step"] == "fix_preflight_failures"
        assert report["summary"]["preflight_fail"] == 3
        assert report["summary"]["preview_rendered"] is False
        assert report["render_skipped_reason"] == "preflight fail"

    def test_critique_seed_categories_match_schema(self):
        """Categories must exactly match critique_finding.schema.json enum."""
        schema = json.loads((SKILL_ROOT / "schemas" / "critique_finding.schema.json").read_text())
        schema_cats = set(schema["properties"]["category"]["enum"])
        seeded_cats = {c["category"] for c in ri.CRITIQUE_CATEGORIES}
        # The seeded set should be a subset of the schema enum (we don't
        # require 'other' to be seeded — it's the catch-all).
        assert seeded_cats.issubset(schema_cats), (
            f"Seeded categories not in schema: {seeded_cats - schema_cats}"
        )

    def test_iteration_number_propagates(self):
        report = ri.build_report(
            svg_path=Path("figure.svg"),
            preview_path=Path("figure.preview.png"),
            preflight=_fake_preflight(),
            iteration=4,
        )
        assert report["iteration"] == 4


# ---------------------------------------------------------------------------
# Integration tests — invoke as a subprocess against the real fixtures.
# ---------------------------------------------------------------------------

def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RENDER_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class TestRenderAndInspectIntegration:
    def test_good_fixture_renders_and_reports_vision_critique(self, tmp_path):
        report_path = tmp_path / "report.json"
        preview_path = tmp_path / "good.preview.png"
        result = _run([
            str(FIXTURES / "good.svg"),
            "--tokens", str(TOKENS),
            "--preview-out", str(preview_path),
            "--iteration", "1",
            "-o", str(report_path),
        ])
        assert result.returncode == 0, result.stderr
        assert preview_path.exists()
        assert preview_path.stat().st_size > 0
        report = json.loads(report_path.read_text())
        assert report["next_step"] == "vision_critique"
        assert report["summary"]["preflight_fail"] == 0
        assert report["preview_path"] == str(preview_path)
        # The seed must be present so Stage 5 has the canonical category set.
        assert "critique_seed" in report
        assert len(report["critique_seed"]["categories"]) >= 7

    def test_bad_fixture_with_skip_render_reports_fix_step(self, tmp_path):
        report_path = tmp_path / "report.json"
        result = _run([
            str(FIXTURES / "bad.svg"),
            "--tokens", str(TOKENS),
            "--iteration", "1",
            "--skip-render-on-fail",
            "-o", str(report_path),
        ])
        # Exit 1 = preflight had fails (expected for the bad fixture).
        assert result.returncode == 1, result.stderr
        report = json.loads(report_path.read_text())
        assert report["next_step"] == "fix_preflight_failures"
        assert report["summary"]["preflight_fail"] > 0
        assert report["summary"]["preview_rendered"] is False
        assert report["render_skipped_reason"] is not None

    def test_bad_fixture_still_renders_without_skip_flag(self, tmp_path):
        """Default behaviour: render anyway so the user can see what 'bad' looks like."""
        report_path = tmp_path / "report.json"
        preview_path = tmp_path / "bad.preview.png"
        result = _run([
            str(FIXTURES / "bad.svg"),
            "--tokens", str(TOKENS),
            "--preview-out", str(preview_path),
            "--iteration", "1",
            "-o", str(report_path),
        ])
        # Exit 1 because preflight still has fails — but render did happen.
        assert result.returncode == 1
        assert preview_path.exists()
        report = json.loads(report_path.read_text())
        assert report["summary"]["preview_rendered"] is True
        assert report["next_step"] == "fix_preflight_failures"

    def test_report_is_valid_json(self, tmp_path):
        result = _run([
            str(FIXTURES / "good.svg"),
            "--tokens", str(TOKENS),
            "--preview-out", str(tmp_path / "preview.png"),
        ])
        assert result.returncode == 0, result.stderr
        json.loads(result.stdout)  # raises on invalid JSON
