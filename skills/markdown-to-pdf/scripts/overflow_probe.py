# /// script
# requires-python = ">=3.11"
# dependencies = ["weasyprint>=68.0"]
# ///
"""
Overflow probe for the markdown-to-pdf showcase pages.

Showcase pages (`<section class="page">`) are fixed 816×1056 canvases with
absolute-positioned chrome. If the LLM stuffs more content into a
`<div class="page-body">` than fits between the header and the footer,
the content is silently clipped (Phase-1 CSS hides it cleanly above the
footer rule, but the data is still gone). This script catches that *before*
the PDF is written.

How it works:
  1. WeasyPrint lays out the document (`Document = HTML(...).render(...)`).
     overflow:hidden on .page-body affects painting only — the laid-out box
     tree still carries the natural positions of overflowing descendants.
  2. We walk every page; for each `.page` showcase section we find the
     enclosed `.page-body` and check whether any descendant's painted bottom
     exceeds the body's content-box bottom (with a small tolerance).
  3. Findings are returned (or printed) with page index, overflow amount,
     element tag, and a short text preview so the operator can find the
     offending content fast.

Flow pages (`<section class="body-flow">`) cannot overflow by construction
— WeasyPrint paginates them. We don't probe them.

Usage:
    uv run scripts/overflow_probe.py <html_path>           # exits 0/1
    uv run scripts/overflow_probe.py <html_path> --json    # machine-readable
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


def _ensure_dyld_path() -> None:
    """Mirror the dyld-path setup from render_pdf.py so this probe can be
    run standalone on macOS without a manual env-var dance."""
    if sys.platform != "darwin":
        return
    homebrew_lib = "/opt/homebrew/lib"
    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if homebrew_lib not in current.split(":"):
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{homebrew_lib}:{current}" if current else homebrew_lib
        )


_ensure_dyld_path()


# Pixels of slop allowed before we call a box "overflowing." WeasyPrint's
# layout uses sub-pixel positions and we don't want to flag a 0.3px rounding
# artifact as a real overflow. 2px ≈ tiny fraction of one text line; anything
# beyond that is meaningful.
_OVERFLOW_TOLERANCE_PX = 2.0


@dataclass(frozen=True)
class OverflowFinding:
    """One overflow record — what the operator needs to act."""
    page_index: int           # 1-based page number in the rendered PDF
    section_label: str        # best-guess label of the overflowing section
    overflow_px: float        # how far the content extends past the body
    overflow_lines: float     # same, expressed in 14px line-heights
    element_tag: str          # offending element's tag (e.g. 'p', 'div')
    text_preview: str         # first ~80 chars of the offending element

    def format_human(self) -> str:
        return (
            f"page {self.page_index} ({self.section_label}): "
            f"body overflows by {self.overflow_px:.0f}px "
            f"(~{self.overflow_lines:.1f} lines)\n"
            f"  offending <{self.element_tag}>: {self.text_preview!r}"
        )


def _walk_boxes(box: Any) -> Iterable[Any]:
    """Depth-first walk of the WeasyPrint box tree."""
    yield box
    for child in getattr(box, "children", ()) or ():
        yield from _walk_boxes(child)


def _box_classes(box: Any) -> set[str]:
    """Extract CSS classes from a box's source element. Anonymous boxes
    (text wrappers, line boxes, etc.) have no element — return empty set."""
    elem = getattr(box, "element", None)
    if elem is None:
        return set()
    cls = elem.get("class")
    if not cls:
        return set()
    return set(cls.split())


def _box_bottom(box: Any) -> float:
    """Painted bottom edge of a box (border-box bottom). Falls back to
    content-box bottom if the API doesn't expose margin_height."""
    pos_y = getattr(box, "position_y", None)
    if pos_y is None:
        return 0.0
    margin_h = getattr(box, "margin_height", None)
    if callable(margin_h):
        try:
            return float(pos_y) + float(margin_h())
        except Exception:  # noqa: BLE001
            pass
    height = getattr(box, "height", 0) or 0
    return float(pos_y) + float(height)


def _section_label(page_box: Any) -> str:
    """Best-effort label for the showcase section on this page. Reads the
    `.label` text inside `.sec-marker` (when present), or the `.eyebrow`
    text. Falls back to '<unlabeled>'."""
    for box in _walk_boxes(page_box):
        classes = _box_classes(box)
        if "sec-marker" in classes:
            for inner in _walk_boxes(box):
                if "label" in _box_classes(inner):
                    text = _collect_text(inner).strip()
                    if text:
                        return text
        if "eyebrow" in classes:
            text = _collect_text(box).strip()
            if text:
                return text
    return "<unlabeled>"


def _collect_text(box: Any) -> str:
    """Concatenate text content from a box subtree. Used for previews and
    section labels — keeps things simple by walking element.text/tail.
    Comment nodes are skipped (lxml exposes them with a non-str tag) so
    the preview reflects what's actually rendered."""
    elem = getattr(box, "element", None)
    parts: list[str] = []
    if elem is not None:
        if isinstance(elem.tag, str) and elem.text:
            parts.append(elem.text)
        for sub in elem.iter():
            if sub is elem:
                continue
            if not isinstance(sub.tag, str):
                continue  # skip <!-- comments --> and processing instructions
            if sub.text:
                parts.append(sub.text)
            if sub.tail:
                parts.append(sub.tail)
    return " ".join(p.strip() for p in parts if p and p.strip())


def _find_descendant_with_class(box: Any, cls: str) -> Any | None:
    for b in _walk_boxes(box):
        if cls in _box_classes(b):
            return b
    return None


def probe_document(doc: Any) -> list[OverflowFinding]:
    """Walk a rendered WeasyPrint Document and return any overflow findings
    on showcase pages. Empty list = the render is clean."""
    findings: list[OverflowFinding] = []
    for page_idx, page in enumerate(doc.pages, start=1):
        page_box = page._page_box
        # A showcase page is a `.page` section. Flow pages don't carry the
        # `.page` class, so they're naturally excluded.
        showcase_section = _find_descendant_with_class(page_box, "page")
        if showcase_section is None:
            continue
        body_box = _find_descendant_with_class(showcase_section, "page-body")
        if body_box is None:
            continue

        body_bottom = float(body_box.position_y) + float(body_box.height)
        # Find the deepest-overflowing descendant. One finding per page is
        # enough — once you fix that, the next-deepest may resolve too.
        worst: tuple[float, Any] | None = None
        for descendant in _walk_boxes(body_box):
            if descendant is body_box:
                continue
            if getattr(descendant, "element", None) is None:
                continue  # skip anonymous wrappers — they're layout artifacts
            bottom = _box_bottom(descendant)
            overflow = bottom - body_bottom
            if overflow <= _OVERFLOW_TOLERANCE_PX:
                continue
            if worst is None or overflow > worst[0]:
                worst = (overflow, descendant)

        if worst is not None:
            overflow_px, box = worst
            preview = _collect_text(box)[:80]
            findings.append(OverflowFinding(
                page_index=page_idx,
                section_label=_section_label(showcase_section),
                overflow_px=round(overflow_px, 1),
                overflow_lines=round(overflow_px / 14.0, 2),
                element_tag=getattr(box, "element_tag", "?"),
                text_preview=preview,
            ))
    return findings


def probe_html_file(html_path: Path) -> list[OverflowFinding]:
    """Convenience wrapper: render an HTML file and probe it."""
    try:
        from weasyprint import CSS, HTML
    except (OSError, ImportError) as e:
        sys.stderr.write(
            "WeasyPrint failed to load. Most common causes:\n"
            "  • macOS native libs missing: brew install pango cairo glib\n"
            "  • Module not installed: re-run via 'uv run'\n"
            f"Original error: {type(e).__name__}: {e}\n"
        )
        raise

    html_path = Path(html_path).resolve()
    page_override = CSS(string="@page { size: letter; margin: 0; }")
    doc = HTML(filename=str(html_path), base_url=str(html_path.parent)).render(
        stylesheets=[page_override]
    )
    return probe_document(doc)


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", help="Path to the populated HTML template")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    findings = probe_html_file(Path(args.html))

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        if not findings:
            print(f"OK: no showcase-page overflow detected in {args.html}")
        else:
            print(f"FAIL: {len(findings)} showcase page(s) overflow:")
            for f in findings:
                print()
                print(f.format_human())
            print()
            print(
                "Fix: split the overflowing section across multiple pages, OR "
                "move prose into a <section class=\"body-flow\"> which "
                "paginates automatically."
            )

    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
