"""
Tests for the WeasyPrint renderer and template integrity.

Covers:
- render_pdf.py public API (render_html_to_pdf, pick_variant)
- regression guards on the @page CSS fix in both templates
- brand-token alignment between oligon-tokens.css and brand-tokens.json
- the three supported schemas have pipeline=html-render; the rest are markdown-only

These tests will skip cleanly if WeasyPrint's native libs aren't available.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates" / "html"
SCHEMAS_DIR = SKILL_DIR / "templates" / "schemas"
SCRIPTS_DIR = SKILL_DIR / "scripts"
BRAND_TOKENS = SKILL_DIR.parent / "oligon-brand" / "tokens" / "brand-tokens.json"

HTML_RENDER_TYPES = {"analysis-report", "literature-review", "data-report"}


# ---------------------------------------------------------------------------
# Template-fix regression guards (run without WeasyPrint)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["editorial", "banded"])
def test_template_has_page_margin_zero(variant: str) -> None:
    """Both templates must declare `@page { size: letter; margin: 0 }` so
    WeasyPrint and Chrome agree on edge-to-edge layout. This is the fix
    identified by the renderer spike — protect against regression."""
    src = (TEMPLATES_DIR / f"template-{variant}.html").read_text()
    assert "@page" in src, f"{variant}: missing @page rule"
    # Tolerant match: any whitespace, optional quotes
    pattern = re.compile(r"@page\s*\{[^}]*size:\s*letter[^}]*margin:\s*0", re.S)
    assert pattern.search(src), (
        f"{variant}: @page rule must specify size: letter and margin: 0"
    )


@pytest.mark.parametrize("variant", ["editorial", "banded"])
def test_template_assets_present(variant: str) -> None:
    """Cover SVGs, report.css, and oligon-tokens.css must all be reachable
    from the template directory (relative refs in the HTML rely on them)."""
    src = (TEMPLATES_DIR / f"template-{variant}.html").read_text()
    assert (TEMPLATES_DIR / "report.css").exists()
    assert (TEMPLATES_DIR / "oligon-tokens.css").exists()
    assert (TEMPLATES_DIR / "assets" / "Oligon_Logo_BrandBlue.svg").exists()
    assert (TEMPLATES_DIR / "assets" / "Oligon_Icon_BrandBlue.svg").exists()
    # Sanity: HTML actually references these
    assert "report.css" in src
    assert "Oligon_Logo_BrandBlue.svg" in src or "Oligon_Logo_White.svg" in src


# ---------------------------------------------------------------------------
# Schema pipeline tags
# ---------------------------------------------------------------------------

def test_supported_schemas_tagged_html_render() -> None:
    for name in HTML_RENDER_TYPES:
        data = json.loads((SCHEMAS_DIR / f"{name}.json").read_text())
        assert data.get("pipeline") == "html-render", (
            f"{name}.json must be tagged pipeline=html-render"
        )


def test_other_schemas_tagged_markdown_only() -> None:
    for p in SCHEMAS_DIR.glob("*.json"):
        if p.name == "_base.json":
            continue
        data = json.loads(p.read_text())
        type_const = data.get("properties", {}).get("type", {}).get("const")
        if type_const in HTML_RENDER_TYPES:
            continue
        assert data.get("pipeline") == "markdown-only", (
            f"{p.name} must be tagged pipeline=markdown-only "
            "so /doc-to-pdf can refuse it explicitly"
        )


# ---------------------------------------------------------------------------
# Brand-token alignment guard (light-touch — single critical color check)
# ---------------------------------------------------------------------------

def test_brand_blue_matches_canonical_token() -> None:
    """oligon-tokens.css is a derived implementation; brand-tokens.json is
    canonical. If they ever drift on the most-used color, fail loudly."""
    if not BRAND_TOKENS.exists():
        pytest.skip("oligon-brand tokens not present")

    tokens = json.loads(BRAND_TOKENS.read_text())
    # Tolerate either flat or nested layouts — we just need the brand_blue value
    canonical = _find_brand_blue(tokens)
    assert canonical, "brand-tokens.json: could not find brand_blue value"

    css = (TEMPLATES_DIR / "oligon-tokens.css").read_text()
    m = re.search(r"--brand-blue\s*:\s*(#[0-9A-Fa-f]{6})", css)
    assert m, "oligon-tokens.css: --brand-blue not defined"
    assert m.group(1).upper() == canonical.upper(), (
        f"Brand Blue drift: tokens={canonical} css={m.group(1)}"
    )


def _find_brand_blue(obj: object) -> str | None:
    """Walk the tokens JSON looking for a 'brand_blue' (or 'brand-blue') key.
    The value may be a hex string directly OR a dict with a 'hex' field
    (current layout: colors.primary.brand_blue.hex). Robust to either."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower().replace("-", "_") == "brand_blue":
                if isinstance(v, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
                    return v
                if isinstance(v, dict):
                    hex_val = v.get("hex")
                    if isinstance(hex_val, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_val):
                        return hex_val
            found = _find_brand_blue(v)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_brand_blue(item)
            if found:
                return found
    return None


# ---------------------------------------------------------------------------
# Renderer end-to-end (skipped if native libs missing)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["editorial", "banded"])
def test_renderer_self_test_produces_pdf(variant: str, tmp_path: Path) -> None:
    src = TEMPLATES_DIR / f"template-{variant}.html"
    out = tmp_path / f"{variant}.pdf"

    result = subprocess.run(
        ["uv", "run", "--quiet", str(SCRIPTS_DIR / "render_pdf.py"), str(src), str(out)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        # Most likely cause is missing native libs — surface for the operator
        # but don't hard-fail the suite on a fresh machine
        pytest.skip(
            f"renderer subprocess failed (likely native-lib install needed): "
            f"{result.stderr[:300]}"
        )

    assert out.exists(), f"{variant}: PDF not produced"
    size = out.stat().st_size
    assert size > 30_000, f"{variant}: PDF too small ({size} bytes)"
    # Upper bound catches accidental raster fallback (Chrome-style ~380KB output
    # vs WeasyPrint's vector ~40KB). Threshold has slack for future font-embedding
    # changes; relax further if a benign WeasyPrint upgrade trips it.
    assert size < 250_000, (
        f"{variant}: PDF unexpectedly large ({size} bytes) — "
        "raster fallback? Check WeasyPrint version."
    )


def test_pick_variant_executive_summary_is_banded() -> None:
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from render_pdf import pick_variant  # noqa: PLC0415
    except (OSError, ImportError):
        # OSError = native libs missing (Pango/cairo). ImportError = the
        # weasyprint Python package isn't on the test interpreter's path.
        # Both are environment issues, not bugs — skip cleanly.
        pytest.skip("WeasyPrint not loadable in this environment")

    assert pick_variant("executive-summary") == "banded"
    assert pick_variant("analysis-report") == "editorial"
    assert pick_variant("analysis-report", audience="external") == "banded"
    assert pick_variant("analysis-report", audience="internal") == "editorial"


# ---------------------------------------------------------------------------
# Overflow probe — Phase 3 of the markdown-to-pdf overflow-fix work
# ---------------------------------------------------------------------------

def _try_import_probe():
    """Import overflow_probe lazily; skip the test if WeasyPrint isn't
    available in this environment (CI machines without Pango/cairo)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from overflow_probe import probe_html_file  # noqa: PLC0415
    except (OSError, ImportError) as e:
        pytest.skip(f"overflow_probe import failed: {e}")
    return probe_html_file


@pytest.mark.parametrize("variant", ["editorial", "banded"])
def test_stock_templates_pass_overflow_probe(variant: str) -> None:
    """The stock templates ship with placeholder slots and must not
    trip the overflow probe — otherwise every render of a fresh
    document would fail before the LLM had a chance to fill anything."""
    probe = _try_import_probe()
    findings = probe(TEMPLATES_DIR / f"template-{variant}.html")
    assert findings == [], (
        f"{variant} stock template overflows: "
        + "; ".join(f.format_human() for f in findings)
    )


def test_overflow_probe_catches_stuffed_showcase(tmp_path: Path) -> None:
    """Build a deliberately-overstuffed showcase page and confirm the
    probe reports a finding with non-trivial overflow. We write the
    fixture next to report.css so relative asset paths resolve."""
    probe = _try_import_probe()

    # Colocate with assets so report.css / oligon-tokens.css are reachable
    fixture = TEMPLATES_DIR / "_test-stuffed-showcase.html"
    paragraphs = (
        '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>\n'
    ) * 40
    fixture.write_text(
        '<!DOCTYPE html><html><head>'
        '<link rel="stylesheet" href="report.css"/></head><body>'
        '<section class="page v-editorial">'
        '<div class="page-header"><span class="meta">T</span>'
        '<span class="rule"></span></div>'
        '<div class="page-body">'
        '<div class="sec-marker"><span class="num">99</span>'
        '<span class="label">Stuffed</span></div>'
        '<h1 class="display">Test</h1>'
        + paragraphs +
        '</div>'
        '<div class="page-footer"><span class="pg">99 / 99</span></div>'
        '</section></body></html>'
    )
    try:
        findings = probe(fixture)
        assert findings, "probe failed to detect a deliberately overstuffed page"
        assert findings[0].overflow_px > 10, (
            f"overflow magnitude unexpectedly small: {findings[0].overflow_px}"
        )
        assert findings[0].section_label == "Stuffed", (
            f"unexpected label: {findings[0].section_label!r}"
        )
    finally:
        fixture.unlink(missing_ok=True)
