#!/usr/bin/env python3
"""Generate an HTML review page from a PaperBanana variant review JSON log.

Reads a variant_review_log.json and produces a self-contained HTML file
for comparing, annotating, and selecting figure variants.

Usage:
    python review_variants.py --input review.json
    python review_variants.py --input review.json --output review.html --embed-images --open
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

# Add shared utilities to path
_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "variant-review-template.html"


def _image_to_data_uri(image_path: str) -> str:
    """Read an image file and return a base64 data URI string."""
    p = Path(image_path)
    if not p.is_file():
        return image_path  # Return original path if file not found
    mime, _ = mimetypes.guess_type(str(p))
    if mime is None:
        mime = "image/png"
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _build_metadata(data: dict) -> dict:
    """Extract metadata fields from the review log (everything except variants)."""
    return {
        "caption": data.get("caption", ""),
        "source_text_preview": data.get("source_text_preview", ""),
        "doc_type": data.get("doc_type", "document"),
        "quality_threshold": data.get("quality_threshold"),
        "brand_enabled": data.get("brand_enabled", True),
        "ranking_rationale": data.get("ranking_rationale", ""),
        "winner_index": data.get("winner_index"),
        "refined_image_path": data.get("refined_image_path", ""),
    }


def generate_review_html(
    review_data: dict,
    output_path: Path,
    embed_images: bool = False,
) -> Path:
    """Generate an HTML review page from variant review data.

    Args:
        review_data: Parsed variant review JSON data.
        output_path: Where to write the HTML file.
        embed_images: If True, embed images as base64 data URIs.

    Returns:
        The resolved output path.
    """
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")

    variants = review_data.get("variants", [])

    if embed_images:
        for v in variants:
            if v.get("image_path"):
                v["image_path"] = _image_to_data_uri(v["image_path"])

    metadata = _build_metadata(review_data)
    timestamp = review_data.get("timestamp", datetime.now().isoformat())

    html = template
    html = html.replace("{{ variants_json }}", json.dumps(variants))
    html = html.replace("{{ metadata_json }}", json.dumps(metadata))
    html = html.replace("{{ timestamp }}", timestamp)

    output_path = Path(output_path).resolve()
    output_path.write_text(html, encoding="utf-8")
    return output_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate HTML review page from PaperBanana variant review JSON",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Path to variant_review_log.json",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output HTML path (default: {input_stem}_review.html)",
    )
    parser.add_argument(
        "--embed-images",
        action="store_true",
        help="Embed images as base64 data URIs for a fully portable file",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Open the generated HTML in the default browser",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    input_path = args.input.resolve()
    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    review_data = json.loads(input_path.read_text(encoding="utf-8"))

    output_path = args.output
    if output_path is None:
        output_path = input_path.with_name(input_path.stem + "_review.html")

    result = generate_review_html(review_data, output_path, embed_images=args.embed_images)
    print(f"Review HTML written to: {result}")

    if args.open_browser:
        webbrowser.open(result.as_uri())


if __name__ == "__main__":
    main()
