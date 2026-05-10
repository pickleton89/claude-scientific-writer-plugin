# /// script
# requires-python = ">=3.11"
# dependencies = ["weasyprint>=68.0"]
# ///
"""
Render a populated HTML report (template-editorial.html / template-banded.html
with all {{SLOTS}} filled) to a branded PDF via WeasyPrint.

The HTML templates already carry the full Oligon brand styling (report.css +
oligon-tokens.css). This script's job is just: load HTML, render PDF, with
the right page size and margins for both renderers to agree.

Usage:
    uv run scripts/render_pdf.py <html_path> <output_pdf>
    uv run scripts/render_pdf.py <html_path> <output_pdf> --no-probe
    uv run scripts/render_pdf.py <html_path> <output_pdf> --allow-overflow
    uv run scripts/render_pdf.py --self-test

Every render is validated by the overflow probe before the PDF is written;
showcase pages whose .page-body content exceeds the canvas cause exit 2 and
no PDF on disk. --no-probe skips validation; --allow-overflow runs it but
writes the PDF anyway.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _ensure_dyld_path() -> None:
    """On macOS, WeasyPrint needs Pango/cairo/glib from Homebrew on the dyld
    fallback path. Set it transparently if not already present."""
    if sys.platform != "darwin":
        return
    homebrew_lib = "/opt/homebrew/lib"
    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if homebrew_lib not in current.split(":"):
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{homebrew_lib}:{current}" if current else homebrew_lib
        )


# Side effect: mutates os.environ on darwin so the WeasyPrint import below
# can find Homebrew's Pango/cairo/glib via dlopen. Must run before the import.
_ensure_dyld_path()

try:
    from weasyprint import CSS, HTML
except (OSError, ImportError) as e:
    sys.stderr.write(
        "WeasyPrint failed to load. Most common causes:\n"
        "  • macOS native libs missing: brew install pango cairo glib\n"
        "  • Module not installed: re-run via 'uv run' (PEP-723 deps install automatically)\n"
        f"Original error: {type(e).__name__}: {e}\n"
    )
    raise


PAGE_OVERRIDE_CSS = CSS(string="@page { size: letter; margin: 0; }")


class OverflowProbeError(RuntimeError):
    """Raised when the overflow probe finds clipped content on a showcase
    page. Carries the structured findings so callers can format their own
    diagnostic messages."""
    def __init__(self, findings: list[Any]) -> None:
        self.findings = findings
        super().__init__(f"{len(findings)} showcase page(s) overflow")


def render_html_to_pdf(
    html_path: Path,
    output_path: Path,
    *,
    probe: bool = True,
    allow_overflow: bool = False,
) -> Path:
    """Render a filled HTML template to a PDF.

    Forces letter size with zero page margin (the showcase pages lay out
    their own margins inside .page sections); the named @page flow rule in
    report.css applies its own margins for body-flow content.

    Pipeline:
        1. Render the document (lays out boxes, doesn't write PDF yet).
        2. Probe showcase pages for content overflow.
        3. If clean — or if the caller passed allow_overflow=True — write
           the PDF. Otherwise raise OverflowProbeError with structured findings.

    The probe step adds ~5% to render time and catches the most common
    failure mode (LLM stuffs more content into a fixed-canvas .page than
    fits between header and footer). Set probe=False for a raw render.
    """
    html_path = Path(html_path).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = HTML(filename=str(html_path), base_url=str(html_path.parent)).render(
        stylesheets=[PAGE_OVERRIDE_CSS],
    )

    if probe:
        # Lazy import so a broken probe degrades gracefully instead of
        # blocking PDF generation. The probe is a safety check, not a
        # hard dependency — if it can't run, warn and proceed.
        try:
            from overflow_probe import probe_document  # noqa: PLC0415
            findings = probe_document(doc)
        except ImportError as e:
            sys.stderr.write(
                f"WARNING: overflow probe unavailable ({e}); rendering "
                "without validation. Layout overflow will not be caught.\n"
            )
            findings = []
        if findings and not allow_overflow:
            raise OverflowProbeError(findings)

    doc.write_pdf(target=str(output_path))
    return output_path


def pick_variant(doc_type: str, audience: str | None = None) -> str:
    """Choose Editorial vs Banded based on document type and audience.

    Banded (more assertive, blue-band cover) for executive/external-facing.
    Editorial (restrained, journal-feeling) for everything else — the default.

    Note: accepts `executive-summary` as a hint from the executive-summary skill,
    even though this skill's schemas don't include it as a renderable doc type.
    Cross-skill callers can use this helper to pick a variant before slot-filling.
    """
    if doc_type == "executive-summary":
        return "banded"
    if audience and audience.lower() in {"executive", "external", "stakeholder"}:
        return "banded"
    return "editorial"


def _self_test() -> int:
    """Render both stock templates with placeholders unfilled. Asserts both
    produce 8-page letter-size PDFs of nontrivial size. Used as a smoke test
    before any document-specific rendering."""
    template_dir = Path(__file__).parent.parent / "templates" / "html"
    out_dir = Path(__file__).parent.parent / "tests" / "_self_test_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    failures = []
    for variant in ("editorial", "banded"):
        src = template_dir / f"template-{variant}.html"
        dst = out_dir / f"selftest-{variant}.pdf"
        if not src.exists():
            failures.append(f"missing template: {src}")
            continue
        try:
            render_html_to_pdf(src, dst)
        except Exception as e:  # noqa: BLE001 — we want any failure surfaced
            failures.append(f"{variant}: render failed — {type(e).__name__}: {e}")
            continue
        size = dst.stat().st_size
        if size < 30_000:
            failures.append(f"{variant}: PDF too small ({size} bytes)")
        else:
            print(f"  {variant}: OK ({size:,} bytes) -> {dst}")

    if failures:
        for f in failures:
            sys.stderr.write(f"FAIL: {f}\n")
        return 1
    print("Self-test passed.")
    return 0


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="?", help="Path to filled HTML template")
    parser.add_argument("output", nargs="?", help="Path to output PDF")
    parser.add_argument("--self-test", action="store_true", help="Render both templates with placeholders as a smoke test")
    parser.add_argument(
        "--no-probe",
        action="store_true",
        help="Skip the overflow probe (faster but unsafe)",
    )
    parser.add_argument(
        "--allow-overflow",
        action="store_true",
        help="Run the probe but write the PDF even if showcase pages overflow",
    )
    args = parser.parse_args()

    if args.self_test:
        return _self_test()
    if not args.html or not args.output:
        parser.error("html and output are required (or use --self-test)")
    try:
        out = render_html_to_pdf(
            Path(args.html),
            Path(args.output),
            probe=not args.no_probe,
            allow_overflow=args.allow_overflow,
        )
    except OverflowProbeError as e:
        sys.stderr.write(
            f"OVERFLOW: {len(e.findings)} showcase page(s) have content "
            "exceeding the body band. PDF was NOT written.\n\n"
        )
        for f in e.findings:
            sys.stderr.write(f.format_human() + "\n\n")
        sys.stderr.write(
            "Fix: split the overflowing section across multiple pages, OR "
            "move prose into a <section class=\"body-flow\"> which "
            "paginates automatically. Pass --allow-overflow to write the "
            "PDF anyway (clipped content will be hidden but lost).\n"
        )
        return 2
    print(f"Rendered: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
