"""Tests for templates/parametric_4panel.py — the programmatic drawsvg demo.

Phase 4 exit criterion: parametric 4-panel demo generates identical output
across two runs. We also exercise preflight to confirm the demo passes
15/15 checks with zero warnings — proving the patterns documented in
references/programmatic_authoring.md hold end-to-end.

These tests run the demo as a PEP-723 self-bootstrapped script
(`uv run --script`). They are skipped if `uv` is not available in PATH.
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
DEMO = SKILL_ROOT / "templates" / "parametric_4panel.py"
PREFLIGHT = SKILL_ROOT / "scripts" / "preflight_check.py"
TOKENS = SKILL_ROOT.parent / "oligon-brand" / "tokens" / "brand-tokens.json"


pytestmark = pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv not on PATH; PEP-723 self-bootstrap tests skipped",
)


def _run_demo(out_path: Path) -> subprocess.CompletedProcess:
    """Invoke the demo via `uv run --script` so PEP-723 deps install."""
    return subprocess.run(
        ["uv", "run", "--script", str(DEMO), "--tokens", str(TOKENS), "-o", str(out_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def _run_preflight(svg_path: Path) -> dict:
    """Run preflight on the demo output and return the parsed JSON report."""
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), str(svg_path),
         "--tokens", str(TOKENS), "--strict-grid"],
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(proc.stdout)


class TestDeterminism:
    def test_two_runs_byte_identical(self, tmp_path):
        a = tmp_path / "a.svg"
        b = tmp_path / "b.svg"
        ra = _run_demo(a)
        rb = _run_demo(b)
        assert ra.returncode == 0, ra.stderr
        assert rb.returncode == 0, rb.stderr
        assert a.read_bytes() == b.read_bytes(), (
            "Demo output differs across runs — determinism contract broken. "
            "Check for: random/datetime leakage, dict-order sensitivity, "
            "randomize_ids=True, mutable global state."
        )

    def test_output_is_nontrivial(self, tmp_path):
        """Guard against a regression where the demo emits an empty <svg/>."""
        out = tmp_path / "out.svg"
        result = _run_demo(out)
        assert result.returncode == 0, result.stderr
        contents = out.read_text()
        # 9 <rect>: 1 background + 4 panel frames + 4 bars.
        assert contents.count("<rect") >= 9, f"too few <rect> elements: {contents.count('<rect')}"
        # 9 <text>: 1 figure title + 4 panel labels + 4 value annotations.
        assert contents.count("<text") >= 9, f"too few <text> elements: {contents.count('<text')}"
        assert "Treatment B" in contents
        assert "viewBox" in contents


class TestPreflightCompliance:
    def test_demo_passes_preflight(self, tmp_path):
        out = tmp_path / "demo.svg"
        result = _run_demo(out)
        assert result.returncode == 0, result.stderr
        report = _run_preflight(out)
        assert report["overall"] == "pass", (
            f"Demo failed preflight: {[f for f in report['findings'] if f['severity'] == 'fail']}"
        )
        assert report["summary"]["fail_count"] == 0
        # Phase 4 standard: zero warnings under --strict-grid. The demo's
        # whole point is to demonstrate grid-clean parametric output.
        assert report["summary"]["warn_count"] == 0, (
            f"Demo produced warnings under --strict-grid: "
            f"{[f for f in report['findings'] if f['severity'] == 'warn']}"
        )

    def test_demo_strips_root_dimensions(self, tmp_path):
        """The render_clean_svg post-process must remove width/height from <svg>."""
        out = tmp_path / "demo.svg"
        result = _run_demo(out)
        assert result.returncode == 0, result.stderr
        first_line = out.read_text().split("<svg", 1)[1].split(">", 1)[0]
        assert "viewBox" in first_line
        assert ' width="' not in first_line, (
            f"Root <svg> still has width= attribute; render_clean_svg failed. "
            f"Tag: <svg{first_line}>"
        )
        assert ' height="' not in first_line, (
            "Root <svg> still has height= attribute; render_clean_svg failed."
        )

    def test_demo_has_accessibility_tags(self, tmp_path):
        out = tmp_path / "demo.svg"
        result = _run_demo(out)
        assert result.returncode == 0, result.stderr
        contents = out.read_text()
        assert "<title>" in contents
        assert "<desc>" in contents


class TestErrorHandling:
    def test_missing_tokens_returns_error(self, tmp_path):
        out = tmp_path / "out.svg"
        result = subprocess.run(
            ["uv", "run", "--script", str(DEMO),
             "--tokens", str(tmp_path / "nonexistent.json"),
             "-o", str(out)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 2
        assert "tokens file not found" in result.stderr
