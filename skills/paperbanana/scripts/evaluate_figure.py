#!/usr/bin/env python3
"""Standalone quality evaluation for existing figures.

Evaluates an existing image against source text using PaperBanana's Critic
agent, then maps scores to the 5-point rubric.

Usage:
    python evaluate_figure.py --image fig.png --source methods.txt
    python evaluate_figure.py --image fig.png --source methods.txt --doc-type journal
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add shared utilities to path
_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

# Add local utils to path
_UTILS_DIR = Path(__file__).resolve().parent / "utils"
if str(_UTILS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_UTILS_DIR.parent))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate an existing figure against source text",
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to figure image to evaluate",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source text file the figure should represent",
    )
    parser.add_argument(
        "--doc-type",
        default="default",
        choices=[
            "journal",
            "conference",
            "thesis",
            "grant",
            "preprint",
            "report",
            "poster",
            "presentation",
            "default",
        ],
        help="Document type for quality threshold",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from api_utils import load_api_key

    from utils.quality_bridge import (
        PaperBananaScores,
        get_threshold,
        map_to_rubric,
        meets_threshold,
        rubric_total,
        to_review_dict,
    )

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source text not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    source_text = source_path.read_text(encoding="utf-8")

    api_key = load_api_key(env_var="GOOGLE_API_KEY", caller_file=__file__)
    if not api_key:
        print(
            "Error: GOOGLE_API_KEY not found.\n"
            "Set via: export GOOGLE_API_KEY='your_key'\n"
            "Get from: https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    # Import PaperBanana
    try:
        from paperbanana import PaperBananaPipeline
        from paperbanana.core.config import Settings
    except ImportError:
        print(
            "Error: paperbanana not installed.\n"
            "Install with: pip install paperbanana",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create minimal settings for evaluation only
    settings = Settings(
        vlm_provider="gemini",
        api_key=api_key,
    )

    pipeline = PaperBananaPipeline(settings=settings)

    # Run Critic evaluation
    eval_result = asyncio.run(
        pipeline.evaluate(
            image_path=str(image_path),
            source_context=source_text,
        )
    )

    # Map scores
    pb_scores = PaperBananaScores(
        faithfulness=getattr(eval_result, "faithfulness", 0.0),
        readability=getattr(eval_result, "readability", 0.0),
        conciseness=getattr(eval_result, "conciseness", 0.0),
        aesthetics=getattr(eval_result, "aesthetics", 0.0),
    )

    rubric = map_to_rubric(pb_scores)
    total = rubric_total(rubric)
    threshold_config = get_threshold(args.doc_type)

    score_dict = to_review_dict(pb_scores, rubric)

    result = {
        "image": str(image_path),
        "source": str(source_path),
        "doc_type": args.doc_type,
        "threshold": threshold_config["threshold"],
        **score_dict,
        "meets_threshold": meets_threshold(rubric, threshold_config["threshold"]),
    }

    print(json.dumps(result, indent=2))

    status = "PASS" if result["meets_threshold"] else "BELOW THRESHOLD"
    print(f"\nScore: {total}/10 ({status})")
    print(f"Threshold ({args.doc_type}): {threshold_config['threshold']}/10")


if __name__ == "__main__":
    main()
