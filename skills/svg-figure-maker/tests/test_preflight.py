"""Tests for scripts/preflight_check.py.

The preflight script is the deterministic safety net of the svg-figure-maker
render→inspect→fix loop. Phase 2 exit criterion: returns valid JSON and
correctly classifies a known-good and a known-bad SVG fixture.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SKILL_ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
PREFLIGHT = SKILL_ROOT / "scripts" / "preflight_check.py"
TOKENS = SKILL_ROOT.parent / "oligon-brand" / "tokens" / "brand-tokens.json"

# Import the module directly for unit tests.
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import preflight_check as pf  # noqa: E402


# ---------------------------------------------------------------------------
# Module-level unit tests
# ---------------------------------------------------------------------------


class TestFontSizeParser:
    """Parser returns (numeric_value, unit_or_None). Brand contract treats
    the ladder {10,12,14,16} as identical in pt and px — both forms accepted,
    plus bare numbers (matplotlib emits px, Mermaid pt, Inkscape bare)."""

    def test_pt_value(self):
        n, unit = pf._parse_font_size("12pt")
        assert n == pytest.approx(12.0)
        assert unit == "pt"

    def test_px_value(self):
        n, unit = pf._parse_font_size("12px")
        assert n == pytest.approx(12.0)
        assert unit == "px"

    def test_bare_number(self):
        n, unit = pf._parse_font_size("16")
        assert n == pytest.approx(16.0)
        assert unit is None

    def test_invalid_returns_none(self):
        assert pf._parse_font_size("large") is None
        assert pf._parse_font_size("") is None

    def test_decimal_value(self):
        n, unit = pf._parse_font_size("10.5pt")
        assert n == pytest.approx(10.5)
        assert unit == "pt"


class TestFontSizeLadderAcceptance:
    """Integration: check_text_font_size accepts pt/px/bare on the ladder."""

    @staticmethod
    def _make_svg(font_size_attr: str) -> str:
        return f"""<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480">
  <title>t</title><desc>d</desc>
  <text x="40" y="40" font-family="Arial, Helvetica, sans-serif" font-size="{font_size_attr}">Hello</text>
</svg>"""

    @pytest.mark.parametrize(
        "value",
        [
            "12pt",
            "12px",
            "12",
            "10pt",
            "10px",
            "10",
            "14pt",
            "14px",
            "14",
            "16pt",
            "16px",
            "16",
        ],
    )
    def test_ladder_values_pass(self, tmp_path, value):
        f = tmp_path / "fig.svg"
        f.write_text(self._make_svg(value))
        result = pf.run_checks(
            svg_path=f, tokens_path=None, grid_unit=8, strict_grid=False
        )
        size_fails = [
            r
            for r in result["findings"]
            if r["check"] == "text_font_size" and r["severity"] == "fail"
        ]
        assert size_fails == [], (
            f"unexpected fails for font-size='{value}': {size_fails}"
        )

    @pytest.mark.parametrize("value", ["8pt", "9px", "9", "11pt", "13px", "15", "20pt"])
    def test_off_ladder_or_below_floor_fails(self, tmp_path, value):
        f = tmp_path / "fig.svg"
        f.write_text(self._make_svg(value))
        result = pf.run_checks(
            svg_path=f, tokens_path=None, grid_unit=8, strict_grid=False
        )
        size_fails = [
            r
            for r in result["findings"]
            if r["check"] == "text_font_size" and r["severity"] == "fail"
        ]
        assert len(size_fails) == 1, (
            f"expected one fail for font-size='{value}', got {size_fails}"
        )


class TestGridDetection:
    def test_on_grid(self):
        assert not pf._is_off_grid(40, 8)
        assert not pf._is_off_grid(0, 8)
        assert not pf._is_off_grid(640, 8)

    def test_off_grid(self):
        assert pf._is_off_grid(41, 8)
        assert pf._is_off_grid(37, 8)
        assert pf._is_off_grid(313, 8)

    def test_4px_grid(self):
        assert not pf._is_off_grid(12, 4)
        assert pf._is_off_grid(13, 4)


class TestPaletteLoader:
    def test_loads_oligon_palette(self):
        if not TOKENS.exists():
            pytest.skip("oligon-brand tokens not found")
        palette = pf.load_palette(TOKENS)
        assert palette is not None
        # Known oligon hexes (brand v5: figure text is #000000, not the pre-v5 #222222)
        assert "#2DB2E8" in palette
        assert "#000000" in palette
        assert "#FFFFFF" in palette

    def test_returns_none_when_no_path(self):
        assert pf.load_palette(None) is None

    def test_raises_when_missing(self):
        with pytest.raises(FileNotFoundError):
            pf.load_palette(Path("/nonexistent/tokens.json"))


# ---------------------------------------------------------------------------
# Integration tests via run_checks()
# ---------------------------------------------------------------------------


class TestGoodFixture:
    @pytest.fixture
    def result(self):
        return pf.run_checks(
            svg_path=FIXTURES / "good.svg",
            tokens_path=TOKENS if TOKENS.exists() else None,
            grid_unit=8,
            strict_grid=False,
        )

    def test_overall_pass(self, result):
        assert result["overall"] == "pass", (
            f"Expected pass, got findings: {[f for f in result['findings'] if f['severity'] == 'fail']}"
        )

    def test_no_fail_findings(self, result):
        fail_findings = [f for f in result["findings"] if f["severity"] == "fail"]
        assert fail_findings == [], f"Unexpected fail findings: {fail_findings}"

    def test_viewbox_passes(self, result):
        viewbox_findings = [
            f for f in result["findings"] if f["check"] == "viewbox_present"
        ]
        assert len(viewbox_findings) == 1
        assert viewbox_findings[0]["severity"] == "pass"

    def test_accessibility_passes(self, result):
        title_findings = [
            f for f in result["findings"] if f["check"] == "root_title_present"
        ]
        desc_findings = [
            f for f in result["findings"] if f["check"] == "root_desc_present"
        ]
        assert len(title_findings) == 1 and title_findings[0]["severity"] == "pass"
        assert len(desc_findings) == 1 and desc_findings[0]["severity"] == "pass"

    def test_summary_consistent(self, result):
        s = result["summary"]
        assert s["checks_run"] == len(result["findings"])
        assert s["fail_count"] == 0


class TestBadFixture:
    @pytest.fixture
    def result(self):
        return pf.run_checks(
            svg_path=FIXTURES / "bad.svg",
            tokens_path=TOKENS if TOKENS.exists() else None,
            grid_unit=8,
            strict_grid=False,
        )

    def test_overall_fail(self, result):
        assert result["overall"] == "fail"

    def test_has_fail_findings(self, result):
        fail_findings = [f for f in result["findings"] if f["severity"] == "fail"]
        assert len(fail_findings) > 0

    def test_detects_missing_title(self, result):
        title_findings = [
            f for f in result["findings"] if f["check"] == "root_title_present"
        ]
        assert len(title_findings) == 1
        assert title_findings[0]["severity"] == "fail"

    def test_detects_missing_desc(self, result):
        desc_findings = [
            f for f in result["findings"] if f["check"] == "root_desc_present"
        ]
        assert len(desc_findings) == 1
        assert desc_findings[0]["severity"] == "fail"

    def test_detects_banned_filter(self, result):
        filter_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_banned_filters" and f["severity"] == "fail"
        ]
        assert len(filter_fails) >= 1

    def test_detects_banned_elements(self, result):
        # <script> and <foreignObject>
        elem_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_banned_elements" and f["severity"] == "fail"
        ]
        assert len(elem_fails) >= 2

    def test_detects_vertical_text(self, result):
        vert_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_vertical_text" and f["severity"] == "fail"
        ]
        assert len(vert_fails) >= 1

    def test_detects_off_ladder_font_size(self, result):
        # bad.svg has font-size="8pt" and "11pt"
        size_fails = [
            f
            for f in result["findings"]
            if f["check"] == "text_font_size" and f["severity"] == "fail"
        ]
        assert len(size_fails) >= 2  # at least the 8pt and 11pt

    def test_detects_forbidden_font_family(self, result):
        # bad.svg has "Times New Roman"
        ff_fails = [
            f
            for f in result["findings"]
            if f["check"] == "text_font_family" and f["severity"] == "fail"
        ]
        assert any("times" in f["message"].lower() for f in ff_fails)

    def test_detects_currentcolor(self, result):
        cc_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_currentcolor" and f["severity"] == "fail"
        ]
        assert len(cc_fails) >= 1

    def test_detects_css_named_color(self, result):
        named_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_css_named_colors" and f["severity"] == "fail"
        ]
        # bad.svg uses "lightblue"
        assert any("lightblue" in f["message"].lower() for f in named_fails)

    def test_detects_off_palette_hex(self, result):
        if not TOKENS.exists():
            pytest.skip("oligon-brand tokens not found")
        # bad.svg uses #3498DB which isn't in the oligon palette
        palette_fails = [
            f
            for f in result["findings"]
            if f["check"] == "palette_compliance" and f["severity"] == "fail"
        ]
        assert any(
            "#3498DB" in f["message"] or "#3498db" in f["message"].lower()
            for f in palette_fails
        )

    def test_warns_root_dimensions(self, result):
        # bad.svg has width/height on root
        dim_findings = [
            f for f in result["findings"] if f["check"] == "no_root_dimensions"
        ]
        assert len(dim_findings) == 1
        assert dim_findings[0]["severity"] == "warn"

    def test_warns_oversized_rounded_corners(self, result):
        # bad.svg has rx="20" ry="20" on one rect
        rx_warns = [
            f
            for f in result["findings"]
            if f["check"] == "no_oversized_rounded_corners" and f["severity"] == "warn"
        ]
        assert len(rx_warns) >= 2  # one for rx, one for ry

    def test_warns_gradient_present(self, result):
        # bad.svg has a linearGradient
        grad_warns = [
            f
            for f in result["findings"]
            if f["check"] == "no_undocumented_gradients" and f["severity"] == "warn"
        ]
        assert len(grad_warns) >= 1

    def test_detects_color_function(self, result):
        # bad.svg has fill="rgb(255,0,0)"
        fn_fails = [
            f
            for f in result["findings"]
            if f["check"] == "no_color_functions" and f["severity"] == "fail"
        ]
        assert len(fn_fails) >= 1
        assert any("rgb(" in f["message"] for f in fn_fails)


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------


class TestCLI:
    def test_good_fixture_exit_zero(self):
        result = subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT),
                str(FIXTURES / "good.svg"),
                "--tokens",
                str(TOKENS) if TOKENS.exists() else "/dev/null",
            ],
            capture_output=True,
            text=True,
        )
        # If tokens don't exist, the script raises — we'd see exit 2 or non-zero
        if not TOKENS.exists():
            pytest.skip("oligon-brand tokens not found")
        assert result.returncode == 0, (
            f"stderr: {result.stderr}\nstdout: {result.stdout}"
        )
        # stdout is valid JSON
        parsed = json.loads(result.stdout)
        assert parsed["overall"] == "pass"

    def test_bad_fixture_exit_nonzero(self):
        if not TOKENS.exists():
            pytest.skip("oligon-brand tokens not found")
        result = subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT),
                str(FIXTURES / "bad.svg"),
                "--tokens",
                str(TOKENS),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        parsed = json.loads(result.stdout)
        assert parsed["overall"] == "fail"
        assert parsed["summary"]["fail_count"] > 0

    def test_output_flag_writes_file(self, tmp_path):
        if not TOKENS.exists():
            pytest.skip("oligon-brand tokens not found")
        out = tmp_path / "result.json"
        subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT),
                str(FIXTURES / "good.svg"),
                "--tokens",
                str(TOKENS),
                "-o",
                str(out),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert out.exists()
        parsed = json.loads(out.read_text())
        assert "overall" in parsed
        assert "findings" in parsed
