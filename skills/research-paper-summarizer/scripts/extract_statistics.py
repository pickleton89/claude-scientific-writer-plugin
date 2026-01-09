#!/usr/bin/env python3
"""
Extract statistics from research paper text.

Returns structured data with all statistical values found,
enabling deterministic processing before LLM interpretation.

Usage:
    python extract_statistics.py paper.txt
    python extract_statistics.py paper.txt --json
    python extract_statistics.py paper.txt --summary
"""

import argparse
import json
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.statistics import extract_statistics, summarize_statistics
from utils.schemas import StatisticType


def print_detailed_output(stats: list, file_path: str) -> None:
    """Print detailed statistics output."""
    print(f"\n{'=' * 60}")
    print("Statistics Extraction Report")
    print(f"File: {file_path}")
    print(f"{'=' * 60}\n")

    if not stats:
        print("No statistical values found in the text.")
        return

    print(f"Found {len(stats)} statistical values:\n")

    # Group by type
    by_type: dict[str, list] = {}
    for stat in stats:
        type_name = stat.stat_type.value
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(stat)

    for type_name, type_stats in sorted(by_type.items()):
        print(f"\n{type_name.upper().replace('_', ' ')} ({len(type_stats)}):")
        print("-" * 40)
        for stat in type_stats[:5]:  # Show up to 5 per type
            print(f"  {stat.normalized}")
            # Show truncated context
            ctx = stat.context
            if len(ctx) > 70:
                ctx = ctx[:67] + "..."
            print(f"    Context: {ctx}")
        if len(type_stats) > 5:
            print(f"  ... and {len(type_stats) - 5} more")


def print_summary_output(stats: list, file_path: str) -> None:
    """Print summary statistics output."""
    summary = summarize_statistics(stats)

    print(f"\n{'=' * 60}")
    print("Statistics Summary")
    print(f"File: {file_path}")
    print(f"{'=' * 60}\n")

    print(f"Total statistics found: {summary['total']}\n")

    if not summary["by_type"]:
        print("No statistics found.")
        return

    print("By type:")
    for type_name, data in sorted(summary["by_type"].items()):
        print(f"  {type_name}: {data['count']}")
        for example in data["examples"]:
            print(f"    - {example}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract statistics from text")
    parser.add_argument("file", help="Text file to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    parser.add_argument(
        "--type",
        choices=[t.value for t in StatisticType],
        help="Filter by statistic type",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=0,
        help="Only report if at least this many stats found",
    )

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    # Read file
    text = Path(args.file).read_text(encoding="utf-8")

    # Extract statistics
    stats = extract_statistics(text)

    # Filter by type if specified
    if args.type:
        stats = [s for s in stats if s.stat_type.value == args.type]

    # Check minimum count
    if len(stats) < args.min_count:
        if args.json:
            print(json.dumps({"error": f"Found only {len(stats)} stats, need {args.min_count}+"}))
        else:
            print(f"Found only {len(stats)} statistics (need {args.min_count}+)")
        return 1

    # Output
    if args.json:
        output = {
            "file": args.file,
            "statistics": [s.to_dict() for s in stats],
            "summary": summarize_statistics(stats),
            "total_count": len(stats),
        }
        print(json.dumps(output, indent=2))
    elif args.summary:
        print_summary_output(stats, args.file)
    else:
        print_detailed_output(stats, args.file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
