#!/usr/bin/env python3
"""
Deterministic section marker management.

Updates section markers in summary files without LLM involvement.
Provides reliable, regex-based marker status updates.

Usage:
    python update_markers.py summary.md --status
    python update_markers.py summary.md --complete executive_summary
    python update_markers.py summary.md --skip methods
    python update_markers.py summary.md --pending results
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.schemas import SectionMarker, MarkerStatus


def get_markers(content: str) -> list[SectionMarker]:
    """
    Extract all section markers from content.

    Args:
        content: File content to parse

    Returns:
        List of SectionMarker objects
    """
    pattern = r"<!-- (SECTION|SUBSECTION): (\w+) (PENDING|COMPLETE|SKIPPED) -->"
    markers = []
    for match in re.finditer(pattern, content):
        marker_type, name, status = match.groups()
        markers.append(
            SectionMarker(
                name=name,
                marker_type=marker_type.lower(),
                status=MarkerStatus(status.lower()),
                position=match.start(),
            )
        )
    return markers


def update_marker(content: str, section_name: str, new_status: str) -> str:
    """
    Update a section marker to new status.

    Args:
        content: File content
        section_name: Name of section to update
        new_status: New status (PENDING, COMPLETE, SKIPPED)

    Returns:
        Updated content

    Raises:
        ValueError: If section marker not found
    """
    pattern = rf"(<!-- (?:SECTION|SUBSECTION): {section_name}) (PENDING|COMPLETE|SKIPPED)( -->)"
    replacement = rf"\1 {new_status.upper()}\3"

    new_content, count = re.subn(pattern, replacement, content)

    if count == 0:
        raise ValueError(f"Section marker not found: {section_name}")

    return new_content


def insert_content_before_marker(
    content: str, section_name: str, new_content: str
) -> str:
    """
    Insert content before a section marker (before marking complete).

    Args:
        content: File content
        section_name: Section to insert before
        new_content: Content to insert

    Returns:
        Updated content
    """
    pattern = rf"(<!-- (?:SECTION|SUBSECTION): {section_name}) PENDING( -->)"

    # Escape backslashes in new_content for regex replacement
    escaped_content = new_content.replace("\\", "\\\\")
    replacement = f"{escaped_content}\n\n\\1 COMPLETE\\2"

    return re.sub(pattern, replacement, content)


def reset_all_markers(content: str, to_status: str = "PENDING") -> str:
    """
    Reset all markers to a given status.

    Args:
        content: File content
        to_status: Status to reset to

    Returns:
        Updated content
    """
    pattern = r"(<!-- (?:SECTION|SUBSECTION): \w+) (PENDING|COMPLETE|SKIPPED)( -->)"
    replacement = rf"\1 {to_status.upper()}\3"
    return re.sub(pattern, replacement, content)


def print_status(markers: list[SectionMarker], file_path: str) -> None:
    """Print marker status summary."""
    print(f"\n{'=' * 60}")
    print("Section Markers Status")
    print(f"File: {file_path}")
    print(f"{'=' * 60}\n")

    print(f"{'Section':<30} {'Type':<12} {'Status':<10}")
    print("-" * 52)

    for marker in sorted(markers, key=lambda m: m.position):
        status_icon = {
            MarkerStatus.PENDING: "[  ]",
            MarkerStatus.COMPLETE: "[OK]",
            MarkerStatus.SKIPPED: "[--]",
        }.get(marker.status, "[??]")

        print(f"{marker.name:<30} {marker.marker_type:<12} {status_icon} {marker.status.value}")

    # Summary
    total = len(markers)
    complete = sum(1 for m in markers if m.status == MarkerStatus.COMPLETE)
    pending = sum(1 for m in markers if m.status == MarkerStatus.PENDING)
    skipped = sum(1 for m in markers if m.status == MarkerStatus.SKIPPED)

    print(f"\n{'Summary:'}")
    print(f"  Complete: {complete}/{total}")
    print(f"  Pending:  {pending}/{total}")
    print(f"  Skipped:  {skipped}/{total}")

    if pending == 0 and total > 0:
        print("\n  All sections processed!")
    elif pending > 0:
        print(f"\n  Progress: {(complete + skipped) / total:.0%}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage section markers")
    parser.add_argument("file", help="Summary markdown file")
    parser.add_argument(
        "--complete", metavar="SECTION", help="Mark section as complete"
    )
    parser.add_argument("--skip", metavar="SECTION", help="Mark section as skipped")
    parser.add_argument(
        "--pending", metavar="SECTION", help="Reset section to pending"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show all marker statuses"
    )
    parser.add_argument(
        "--reset-all",
        metavar="STATUS",
        choices=["pending", "complete", "skipped"],
        help="Reset all markers to specified status",
    )
    parser.add_argument(
        "--insert",
        metavar="CONTENT",
        help="Insert content before marking complete",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying file",
    )

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    content = file_path.read_text(encoding="utf-8")
    modified = False
    actions: list[str] = []

    # Status only - no modifications
    if args.status:
        markers = get_markers(content)
        if args.json:
            output = {
                "file": str(file_path),
                "markers": [m.to_dict() for m in markers],
                "summary": {
                    "total": len(markers),
                    "complete": sum(1 for m in markers if m.status == MarkerStatus.COMPLETE),
                    "pending": sum(1 for m in markers if m.status == MarkerStatus.PENDING),
                    "skipped": sum(1 for m in markers if m.status == MarkerStatus.SKIPPED),
                },
            }
            print(json.dumps(output, indent=2))
        else:
            print_status(markers, str(file_path))
        return 0

    # Reset all markers
    if args.reset_all:
        content = reset_all_markers(content, args.reset_all)
        modified = True
        actions.append(f"Reset all markers to {args.reset_all.upper()}")

    # Mark complete
    if args.complete:
        try:
            if args.insert:
                content = insert_content_before_marker(content, args.complete, args.insert)
                actions.append(f"Inserted content before {args.complete}")
            content = update_marker(content, args.complete, "COMPLETE")
            modified = True
            actions.append(f"Marked {args.complete} as COMPLETE")
        except ValueError as e:
            print(f"Error: {e}")
            return 1

    # Mark skipped
    if args.skip:
        try:
            content = update_marker(content, args.skip, "SKIPPED")
            modified = True
            actions.append(f"Marked {args.skip} as SKIPPED")
        except ValueError as e:
            print(f"Error: {e}")
            return 1

    # Reset to pending
    if args.pending:
        try:
            content = update_marker(content, args.pending, "PENDING")
            modified = True
            actions.append(f"Reset {args.pending} to PENDING")
        except ValueError as e:
            print(f"Error: {e}")
            return 1

    # Apply changes
    if modified:
        if args.dry_run:
            print("Dry run - no changes written")
            for action in actions:
                print(f"  Would: {action}")
        else:
            file_path.write_text(content, encoding="utf-8")
            for action in actions:
                print(f"  {action}")
            print(f"\nFile updated: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
