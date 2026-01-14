#!/usr/bin/env python3
"""
Scientific Schematic Generator - Tiered Architecture

Routes diagram requests to appropriate generation engine:
- Tier 1 (Mermaid): Simple diagrams, free, instant
- Tier 2 (AI): Complex diagrams, publication quality
- Mermaid+AI: Mermaid draft with AI polish

Smart tier selection automatically chooses the best approach based on:
- Diagram complexity (node count, edge count)
- Diagram type (some types require AI)
- Document type quality requirements
- User preference via --engine flag

Usage:
    # Auto-select tier based on complexity (default)
    python generate_schematic.py "Simple flowchart" -o output.png

    # Force Mermaid (free, instant)
    python generate_schematic.py "Process flow" -o output.png --engine mermaid

    # Force AI generation
    python generate_schematic.py "Neural network" -o output.png --engine ai

    # Mermaid draft + AI polish
    python generate_schematic.py "CONSORT flow" -o output.png --engine mermaid+ai
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Import complexity analyzer for tier selection
try:
    from utils.complexity_analyzer import (
        GenerationTier,
        analyze_complexity,
        get_tier_summary,
    )
except ImportError:
    # Handle running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from utils.complexity_analyzer import (
        GenerationTier,
        analyze_complexity,
        get_tier_summary,
    )


def run_mermaid_generation(
    prompt: str,
    output_path: str,
    diagram_type: str | None = None,
    verbose: bool = False,
) -> tuple[bool, str | None]:
    """Run Mermaid generation via generate_mermaid.py.

    Args:
        prompt: Diagram description
        output_path: Output file path
        diagram_type: Optional diagram type hint
        verbose: Enable verbose output

    Returns:
        Tuple of (success, error_message)
    """
    script_dir = Path(__file__).parent
    mermaid_script = script_dir / "generate_mermaid.py"

    if not mermaid_script.exists():
        return False, f"Mermaid generation script not found: {mermaid_script}"

    cmd = [sys.executable, str(mermaid_script), prompt, "-o", output_path]

    if diagram_type:
        cmd.extend(["--type", diagram_type])

    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, check=False, capture_output=not verbose)
        if result.returncode == 0:
            return True, None
        else:
            error = result.stderr.decode() if result.stderr else "Unknown error"
            return False, error
    except Exception as e:
        return False, str(e)


def run_ai_generation(
    prompt: str,
    output_path: str,
    doc_type: str = "default",
    iterations: int = 2,
    review_model: str = "flash",
    api_key: str | None = None,
    verbose: bool = False,
) -> tuple[bool, str | None]:
    """Run AI generation via generate_schematic_ai.py.

    Args:
        prompt: Diagram description
        output_path: Output file path
        doc_type: Document type for quality threshold
        iterations: Max refinement iterations
        review_model: Review model (flash or pro)
        api_key: OpenRouter API key
        verbose: Enable verbose output

    Returns:
        Tuple of (success, error_message)
    """
    script_dir = Path(__file__).parent
    ai_script = script_dir / "generate_schematic_ai.py"

    if not ai_script.exists():
        return False, f"AI generation script not found: {ai_script}"

    cmd = [sys.executable, str(ai_script), prompt, "-o", output_path]

    if doc_type != "default":
        cmd.extend(["--doc-type", doc_type])

    if iterations != 2:
        cmd.extend(["--iterations", str(iterations)])

    if review_model != "flash":
        cmd.extend(["--review-model", review_model])

    if api_key:
        cmd.extend(["--api-key", api_key])

    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, check=False, capture_output=not verbose)
        if result.returncode == 0:
            return True, None
        else:
            error = result.stderr.decode() if result.stderr else "Unknown error"
            return False, error
    except Exception as e:
        return False, str(e)


def run_mermaid_plus_ai(
    prompt: str,
    output_path: str,
    doc_type: str = "default",
    api_key: str | None = None,
    verbose: bool = False,
) -> tuple[bool, str | None]:
    """Run AI generation with Mermaid fallback.

    This hybrid approach:
    1. Creates a Mermaid draft as fallback (in case AI fails)
    2. Uses AI to generate a publication-quality diagram from the prompt
    3. Falls back to Mermaid output if AI generation fails

    Note: The AI generates independently from the text prompt - it does not
    visually refine the Mermaid image. The Mermaid draft serves only as a
    fallback to ensure the user gets some output even if AI fails.

    Args:
        prompt: Diagram description
        output_path: Final output file path
        doc_type: Document type for quality threshold
        api_key: OpenRouter API key
        verbose: Enable verbose output

    Returns:
        Tuple of (success, error_message)
    """
    output = Path(output_path)

    # Step 1: Generate Mermaid draft (for fallback)
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_path = Path(tmpdir) / f"mermaid_draft{output.suffix}"

        if verbose:
            print("\n[Step 1/2] Generating Mermaid fallback...")

        success, error = run_mermaid_generation(
            prompt=prompt,
            output_path=str(draft_path),
            verbose=verbose,
        )

        if not success:
            return False, f"Mermaid fallback generation failed: {error}"

        # Step 2: Generate with AI (primary output)
        if verbose:
            print("\n[Step 2/2] Generating with AI...")

        polish_prompt = f"""Improve this diagram while maintaining its structure:
Original request: {prompt}

Enhance visual quality for {doc_type} publication.
Keep the same logical flow and components.
Make it publication-ready with professional styling."""

        success, error = run_ai_generation(
            prompt=polish_prompt,
            output_path=output_path,
            doc_type=doc_type,
            iterations=1,  # Single polish pass
            api_key=api_key,
            verbose=verbose,
        )

        if not success:
            # Fallback: if AI fails, use the Mermaid draft
            if verbose:
                print(f"AI generation failed: {error}")
                print("Falling back to Mermaid output...")

            shutil.copy(draft_path, output_path)
            return True, None

        return True, None


def main() -> int:
    """Command-line interface with tiered generation."""
    parser = argparse.ArgumentParser(
        description="Generate scientific diagrams with tiered approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Generation Tiers:
  Tier 1 (Mermaid):
    - Cost: $0.00 (local rendering)
    - Speed: ~100ms
    - Best for: Simple flowcharts, drafts, presentations

  Tier 2 (AI):
    - Cost: ~$0.02-0.05 per generation
    - Speed: 10-30 seconds
    - Best for: Complex diagrams, publication figures

  Mermaid+AI:
    - Cost: ~$0.02-0.05 (single AI polish pass)
    - Best for: Publication-quality versions of simple diagrams

Engine Selection:
  auto (default)    Auto-select based on complexity analysis
  mermaid           Force Mermaid (Tier 1) - free, instant
  ai                Force AI (Tier 2) - publication quality
  mermaid+ai        Mermaid draft + AI polish

Document Types (quality thresholds):
  journal      8.5/10  - Nature, Science, peer-reviewed journals
  conference   8.0/10  - Conference papers
  thesis       8.0/10  - Dissertations, theses
  grant        8.0/10  - Grant proposals
  preprint     7.5/10  - arXiv, bioRxiv, etc.
  report       7.5/10  - Technical reports
  poster       7.0/10  - Academic posters
  presentation 6.5/10  - Slides, talks
  default      7.5/10  - General purpose

Examples:
  # Auto-select tier (recommended)
  python generate_schematic.py "Simple 5-step process" -o flow.png

  # Force Mermaid for free instant generation
  python generate_schematic.py "Input → Process → Output" -o flow.png --engine mermaid

  # Force AI for complex diagrams
  python generate_schematic.py "Transformer architecture" -o arch.png --engine ai

  # Mermaid draft with AI polish for publication
  python generate_schematic.py "CONSORT flowchart" -o consort.png --engine mermaid+ai --doc-type journal

  # Analyze complexity without generating
  python generate_schematic.py "Complex pathway diagram" --analyze

Environment Variables:
  OPENROUTER_API_KEY    Required for AI generation (Tier 2)
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Description of the diagram to generate",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path",
    )
    parser.add_argument(
        "--engine",
        choices=["auto", "mermaid", "ai", "mermaid+ai"],
        default="auto",
        help="Generation engine (default: auto-select based on complexity)",
    )
    parser.add_argument(
        "--doc-type",
        default="default",
        choices=[
            "journal",
            "conference",
            "poster",
            "presentation",
            "report",
            "grant",
            "thesis",
            "preprint",
            "default",
        ],
        help="Document type for quality threshold (default: default)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=2,
        help="Maximum refinement iterations for AI (default: 2, max: 2)",
    )
    parser.add_argument(
        "--api-key",
        help="OpenRouter API key (or use OPENROUTER_API_KEY env var)",
    )
    parser.add_argument(
        "--review-model",
        default="flash",
        choices=["flash", "pro"],
        help="AI review model: flash (default, faster) or pro (higher quality)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze complexity without generating (no output required)",
    )

    args = parser.parse_args()

    # Handle analysis-only mode
    if args.analyze:
        if not args.prompt:
            parser.error("prompt is required for --analyze")

        analysis = analyze_complexity(args.prompt, args.doc_type)

        print()
        print("=" * 60)
        print("Complexity Analysis")
        print("=" * 60)
        print(f"Diagram type: {analysis.diagram_type}")
        print(f"Estimated nodes: {analysis.estimated_nodes}")
        print(f"Estimated edges: {analysis.estimated_edges}")
        print(f"Mermaid compatible: {analysis.mermaid_compatible}")
        print(f"Recommended tier: {analysis.recommended_tier.value}")
        print(f"Confidence: {analysis.confidence:.0%}")
        print(f"Reasoning: {analysis.reasoning}")

        tier_info = get_tier_summary(analysis.recommended_tier)
        print()
        print(f"Recommended: {tier_info['name']}")
        print(f"  Cost: {tier_info['cost']}")
        print(f"  Speed: {tier_info['speed']}")
        print(f"  Quality: {tier_info['quality']}")
        print("=" * 60)
        return 0

    # Validate required args for generation
    if not args.prompt:
        parser.error("prompt is required for generation")

    if not args.output:
        parser.error("-o/--output is required for generation")

    # Determine tier
    if args.engine == "auto":
        analysis = analyze_complexity(args.prompt, args.doc_type)
        tier = analysis.recommended_tier

        if args.verbose:
            print()
            print("=" * 60)
            print("Complexity Analysis (auto-selection)")
            print("=" * 60)
            print(f"Diagram type: {analysis.diagram_type}")
            print(f"Estimated nodes: {analysis.estimated_nodes}")
            print(f"Mermaid compatible: {analysis.mermaid_compatible}")
            print(f"Selected tier: {tier.value}")
            print(f"Reasoning: {analysis.reasoning}")
            print("=" * 60)
    else:
        tier = GenerationTier(args.engine)

    # Get tier info for display
    tier_info = get_tier_summary(tier)

    print()
    print("=" * 60)
    print("Scientific Schematic Generator")
    print("=" * 60)
    print(f"Input: {args.prompt[:60]}{'...' if len(args.prompt) > 60 else ''}")
    print(f"Output: {args.output}")
    print(f"Engine: {tier.value} ({tier_info['name']})")
    print(f"Estimated cost: {tier_info['cost']}")
    print("=" * 60)
    print()

    # Route to appropriate engine
    if tier == GenerationTier.MERMAID:
        success, error = run_mermaid_generation(
            prompt=args.prompt,
            output_path=args.output,
            verbose=args.verbose,
        )

    elif tier == GenerationTier.AI:
        # Check for API key for AI generation
        api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY required for AI generation")
            print()
            print("Options:")
            print("  1. Set OPENROUTER_API_KEY environment variable")
            print("  2. Use --api-key flag")
            print("  3. Use --engine mermaid for free generation")
            print()
            print("Get your API key from: https://openrouter.ai/keys")
            return 1

        success, error = run_ai_generation(
            prompt=args.prompt,
            output_path=args.output,
            doc_type=args.doc_type,
            iterations=min(args.iterations, 2),
            review_model=args.review_model,
            api_key=api_key,
            verbose=args.verbose,
        )

    elif tier == GenerationTier.MERMAID_PLUS_POLISH:
        # Check for API key for AI polish
        api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Warning: No API key - falling back to Mermaid-only")
            success, error = run_mermaid_generation(
                prompt=args.prompt,
                output_path=args.output,
                verbose=args.verbose,
            )
        else:
            success, error = run_mermaid_plus_ai(
                prompt=args.prompt,
                output_path=args.output,
                doc_type=args.doc_type,
                api_key=api_key,
                verbose=args.verbose,
            )

    else:
        print(f"Error: Unknown tier: {tier}")
        return 1

    # Report results
    if success:
        print()
        print(f"Generated: {args.output}")
        print(f"Engine used: {tier.value}")
        return 0
    else:
        print()
        print(f"Generation failed: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
