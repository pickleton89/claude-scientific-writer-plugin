#!/usr/bin/env python3
"""Generate publication-quality figures from text using PaperBanana.

Main entry point for the paperbanana skill. Takes prose text (methodology,
abstract, summary) and generates a visual figure via PaperBanana's
multi-agent pipeline with Oligon brand styling.

Usage:
    python generate_figure.py --input text.txt --caption "Overview" --output fig.png
    python generate_figure.py --input text.txt --output fig.png --doc-type journal -v
    python generate_figure.py --input text.txt --output fig.png --no-brand
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
        description="Generate publication-quality figures from text using PaperBanana",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input methods.txt --caption "Methodology overview" --output fig.png
  %(prog)s --input abstract.txt --output graphical_abstract.png --doc-type journal
  %(prog)s --input pipeline.txt --output fig.png --no-brand --iterations 2
  %(prog)s --input methods.txt --output fig.png --variants 3 -v
        """,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Source text file or quoted string to visualize",
    )
    parser.add_argument(
        "--caption",
        default="",
        help="Communicative intent / figure caption",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output image path (PNG or PDF)",
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
        help="Document type for quality threshold (default: default)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Refinement iterations, 1-5 (default: 3)",
    )
    parser.add_argument(
        "--no-brand",
        action="store_true",
        help="Disable Oligon brand styling",
    )
    parser.add_argument(
        "--reference-dir",
        help="Directory with reference/example images",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    # Multi-variant mode
    parser.add_argument(
        "--variants",
        type=int,
        default=0,
        metavar="N",
        help="Generate N variant figures and rank them (1-5, default: off)",
    )
    parser.add_argument(
        "--variant-delay",
        type=float,
        default=30.0,
        metavar="S",
        help="Seconds between pipeline runs in variant mode (default: 30)",
    )
    parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Skip winner refinement in variant mode",
    )
    return parser.parse_args()


def load_input_text(input_arg: str) -> str:
    """Load source text from file path or use as literal string."""
    path = Path(input_arg)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return input_arg


def main() -> None:
    args = parse_args()

    # Lazy imports after arg parsing for fast --help
    from api_utils import load_api_key

    from utils.config import create_settings
    from utils.quality_bridge import (
        PaperBananaScores,
        get_threshold,
        map_to_rubric,
        meets_threshold,
        rubric_total,
        to_review_dict,
    )

    # Load API key
    api_key = load_api_key(env_var="GOOGLE_API_KEY", caller_file=__file__)
    if not api_key:
        print(
            "Error: GOOGLE_API_KEY not found.\n"
            "Set via: export GOOGLE_API_KEY='your_key'\n"
            "Get from: https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load source text
    source_text = load_input_text(args.input)
    if not source_text.strip():
        print("Error: Input text is empty.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        preview = source_text[:200] + ("..." if len(source_text) > 200 else "")
        print(f"Source text ({len(source_text)} chars): {preview}")
        print(f"Caption: {args.caption or '(none)'}")
        print(f"Doc type: {args.doc_type}")
        print(f"Iterations: {args.iterations}")
        print(f"Brand: {'enabled' if not args.no_brand else 'disabled'}")
        if args.variants > 0:
            print(f"Variants: {args.variants}")

    # Multi-variant mode dispatch
    if args.variants > 0:
        _run_variant_mode(args, source_text, api_key)
        return

    # Import PaperBanana
    try:
        from paperbanana import DiagramType, GenerationInput, PaperBananaPipeline
    except ImportError:
        print(
            "Error: paperbanana not installed.\n"
            "Install with: pip install paperbanana",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create settings
    settings = create_settings(
        api_key=api_key,
        iterations=args.iterations,
        brand_enabled=not args.no_brand,
        reference_dir=Path(args.reference_dir) if args.reference_dir else None,
    )

    # Prepare generation input
    gen_input = GenerationInput(
        source_context=source_text,
        communicative_intent=args.caption or "Visual summary of the provided text",
        diagram_type=DiagramType.METHODOLOGY,
    )

    # Run pipeline
    if args.verbose:
        print("\nStarting PaperBanana pipeline...")

    pipeline = PaperBananaPipeline(settings=settings)
    result = asyncio.run(pipeline.generate(gen_input))

    # Save output image
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(result, "image_path") and result.image_path:
        # Copy/move the generated image to output path
        import shutil

        shutil.copy2(result.image_path, output_path)
    elif hasattr(result, "image_data") and result.image_data:
        output_path.write_bytes(result.image_data)
    else:
        print("Warning: No image data in result.", file=sys.stderr)

    # Quality evaluation via bridge
    threshold_config = get_threshold(args.doc_type)
    review_log: dict = {
        "source_text_preview": source_text[:200],
        "caption": args.caption or "",
        "doc_type": args.doc_type,
        "quality_threshold": threshold_config["threshold"],
        "brand_enabled": not args.no_brand,
        "iterations": [],
        "final_score": 0.0,
        "final_image": str(output_path),
    }

    # Extract scores from result if available
    if hasattr(result, "evaluation") and result.evaluation:
        eval_data = result.evaluation
        pb_scores = PaperBananaScores(
            faithfulness=getattr(eval_data, "faithfulness", 0.0),
            readability=getattr(eval_data, "readability", 0.0),
            conciseness=getattr(eval_data, "conciseness", 0.0),
            aesthetics=getattr(eval_data, "aesthetics", 0.0),
        )
        rubric = map_to_rubric(pb_scores)
        total = rubric_total(rubric)
        score_dict = to_review_dict(pb_scores, rubric)

        review_log["iterations"].append(
            {
                "iteration": 1,
                "image_path": str(output_path),
                **score_dict,
                "meets_threshold": meets_threshold(
                    rubric, threshold_config["threshold"]
                ),
            }
        )
        review_log["final_score"] = total

        if args.verbose:
            print(f"\nQuality score: {total}/10")
            print(
                f"Threshold ({args.doc_type}): {threshold_config['threshold']}/10"
            )
            status = "PASS" if total >= threshold_config["threshold"] else "BELOW"
            print(f"Status: {status}")

    # Save review log
    log_path = output_path.with_name(
        output_path.stem + "_review_log.json"
    )
    log_path.write_text(json.dumps(review_log, indent=2), encoding="utf-8")

    print(f"\nOutput: {output_path}")
    print(f"Review log: {log_path}")


def _run_variant_mode(
    args: argparse.Namespace, source_text: str, api_key: str
) -> None:
    """Run multi-variant generation, ranking, and review."""
    import logging

    from utils.config import create_settings
    from variant_orchestrator import (
        MultiVariantResult,
        VariantConfig,
        build_variant_review_log,
        run_multi_variant,
    )

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    output_path = Path(args.output)
    output_dir = str(output_path.parent)
    output_stem = output_path.stem

    caption = args.caption or "Visual summary of the provided text"
    ref_dir = Path(args.reference_dir) if args.reference_dir else None

    def settings_factory(iterations: int):
        return create_settings(
            api_key=api_key,
            iterations=iterations,
            brand_enabled=not args.no_brand,
            reference_dir=ref_dir,
        )

    config = VariantConfig(
        n_variants=args.variants,
        delay_between_runs=args.variant_delay,
        refine_winner=not args.no_refine,
        verbose=args.verbose,
    )

    result: MultiVariantResult = asyncio.run(
        run_multi_variant(
            source_text=source_text,
            caption=caption,
            output_dir=output_dir,
            output_stem=output_stem,
            settings_factory=settings_factory,
            api_key=api_key,
            config=config,
        )
    )

    # Build and save review log
    review_log = build_variant_review_log(
        result=result,
        source_text=source_text,
        caption=caption,
        doc_type=args.doc_type,
        brand_enabled=not args.no_brand,
    )

    log_path = output_path.with_name(output_stem + "_variant_review_log.json")
    log_path.write_text(json.dumps(review_log, indent=2), encoding="utf-8")

    # Generate HTML review
    try:
        from review_variants import generate_review_html

        html_path = output_path.with_name(output_stem + "_variant_review.html")
        generate_review_html(review_log, html_path)
        print(f"Review tool: {html_path}")
    except ImportError:
        pass  # review_variants not available

    # Copy final winner to output path
    final_path = Path(output_dir) / f"{output_stem}_final.png"
    if final_path.exists() and final_path != output_path:
        import shutil

        shutil.copy2(final_path, output_path)

    print(f"\nOutput: {output_path}")
    print(f"Review log: {log_path}")
    print(f"Variants generated: {len(result.variants)}")
    if result.ranking:
        print(f"Winner: variant {result.ranking.winner_index}")


if __name__ == "__main__":
    main()
