"""
Audit a Claude Code JSONL session transcript for deep-research skill compliance.

Extracts: tool calls, file writes, skill invocations, MCP usage, checkpoint signals,
mode_selector/output_validator invocations, and produces a structured audit report.

Usage:
    python audit_session.py <jsonl_path> [--label <run_label>]
    python audit_session.py --batch <jsonl1> <jsonl2> ... --labels <label1> <label2> ...
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AuditResult:
    """Structured audit findings for a single session."""

    label: str = ""
    jsonl_path: str = ""
    jsonl_size_bytes: int = 0
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0

    # Skill invocation
    skill_invoked: bool = False
    skill_name: str | None = None

    # Mode selection
    mode_selector_invoked: bool = False
    selected_mode: str | None = None
    mode_confidence: str | None = None

    # Output validation
    output_validator_invoked: bool = False
    validation_result: str | None = None

    # Checkpoints (user approval messages between phases)
    checkpoint_count: int = 0
    checkpoint_details: list[str] = field(default_factory=list)

    # MCP tool usage
    mcp_tools_used: Counter = field(default_factory=Counter)

    # File writes
    files_written: list[dict] = field(default_factory=list)
    total_files_written: int = 0

    # Output format
    output_formats: set = field(default_factory=set)

    # Agent usage
    subagents_spawned: int = 0
    agent_types: Counter = field(default_factory=Counter)

    # Timing
    first_timestamp: str | None = None
    last_timestamp: str | None = None

    # Warnings
    warnings: list[str] = field(default_factory=list)


def parse_jsonl(path: str) -> list[dict]:
    """Parse a JSONL file, skipping malformed lines."""
    messages = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # skip malformed lines
    return messages


def audit_session(jsonl_path: str, label: str = "") -> AuditResult:
    """Audit a single JSONL session transcript."""
    result = AuditResult(
        label=label or Path(jsonl_path).stem,
        jsonl_path=jsonl_path,
        jsonl_size_bytes=Path(jsonl_path).stat().st_size,
    )

    messages = parse_jsonl(jsonl_path)
    result.total_messages = len(messages)

    for msg in messages:
        msg_type = msg.get("type", "")
        role = msg.get("role", "")

        # Count message types
        if role == "user" or msg_type == "human":
            result.user_messages += 1
        elif role == "assistant" or msg_type == "assistant":
            result.assistant_messages += 1

        # Extract timestamps
        ts = msg.get("timestamp") or msg.get("createdAt") or msg.get("ts")
        if ts and isinstance(ts, str):
            if not result.first_timestamp:
                result.first_timestamp = ts
            result.last_timestamp = ts

        # Check for skill invocation
        _check_skill_invocation(msg, result)

        # Check for tool calls
        _check_tool_calls(msg, result)

        # Check for mode_selector / output_validator
        _check_deterministic_scripts(msg, result)

        # Check for checkpoint signals
        _check_checkpoints(msg, result)

        # Check for subagent spawning
        _check_subagents(msg, result)

    # Derive output formats from file extensions
    for fw in result.files_written:
        ext = Path(fw.get("path", "")).suffix.lower()
        if ext:
            result.output_formats.add(ext)

    result.total_files_written = len(result.files_written)

    # Generate warnings
    _generate_warnings(result)

    return result


def _check_skill_invocation(msg: dict, result: AuditResult) -> None:
    """Check if a skill was invoked."""
    content = _extract_text(msg)
    # Check for Skill tool invocation
    if "deep-research" in content.lower() or "scientific-writer" in content.lower():
        tool_use = _extract_tool_uses(msg)
        for tool in tool_use:
            if tool.get("name") == "Skill":
                inp = tool.get("input", {})
                skill_name = inp.get("skill", "")
                if "deep-research" in skill_name or "scientific-writer" in skill_name:
                    result.skill_invoked = True
                    result.skill_name = skill_name


def _check_tool_calls(msg: dict, result: AuditResult) -> None:
    """Extract tool call information."""
    tool_uses = _extract_tool_uses(msg)
    for tool in tool_uses:
        name = tool.get("name", "")

        # MCP tools
        if name.startswith("mcp__"):
            result.mcp_tools_used[name] += 1

        # File writes
        if name == "Write":
            inp = tool.get("input", {})
            path = inp.get("file_path", "")
            if path:
                result.files_written.append({
                    "path": path,
                    "tool": "Write",
                })

        # Bash file writes (echo/cat redirects, pdflatex, etc.)
        if name == "Bash":
            inp = tool.get("input", {})
            cmd = inp.get("command", "")
            # Detect file writes in bash
            write_patterns = [
                r">\s*[\"']?(/[^\"'\s>]+)",  # redirect
                r"tee\s+[\"']?(/[^\"'\s]+)",  # tee
                r"pdflatex.*?([^\s]+\.tex)",   # LaTeX compilation
                r"bibtex\s+([^\s]+)",          # BibTeX
            ]
            for pat in write_patterns:
                m = re.search(pat, cmd)
                if m:
                    result.files_written.append({
                        "path": m.group(1),
                        "tool": "Bash",
                        "command_snippet": cmd[:200],
                    })


def _check_deterministic_scripts(msg: dict, result: AuditResult) -> None:
    """Check for invocations of mode_selector.py, output_validator.py."""
    content = _extract_text(msg)
    tool_uses = _extract_tool_uses(msg)

    for tool in tool_uses:
        if tool.get("name") == "Bash":
            cmd = tool.get("input", {}).get("command", "")
            if "mode_selector" in cmd:
                result.mode_selector_invoked = True
                # Try to extract result from subsequent messages
            if "output_validator" in cmd:
                result.output_validator_invoked = True

    # Also check in text content for references to mode selection
    if "mode_selector" in content:
        pass  # mentioned but may not have been invoked
    if re.search(r'selected.?mode["\s:]+(\w[\w-]*)', content, re.IGNORECASE):
        m = re.search(r'selected.?mode["\s:]+(\w[\w-]*)', content, re.IGNORECASE)
        if m:
            result.selected_mode = m.group(1)


def _check_checkpoints(msg: dict, result: AuditResult) -> None:
    """Detect checkpoint approval patterns."""
    content = _extract_text(msg)
    role = msg.get("role", "") or msg.get("type", "")

    # User messages that are short approvals between phases
    if role in ("user", "human"):
        approval_patterns = [
            r"(?i)(yes|approved?|looks?\s+good|proceed|continue|go\s+ahead|lgtm|confirm)",
            r"(?i)checkpoint\s*\d",
            r"(?i)phase\s*\d",
        ]
        for pat in approval_patterns:
            if re.search(pat, content):
                result.checkpoint_count += 1
                result.checkpoint_details.append(content[:100])
                break


def _check_subagents(msg: dict, result: AuditResult) -> None:
    """Detect subagent spawning."""
    tool_uses = _extract_tool_uses(msg)
    for tool in tool_uses:
        if tool.get("name") == "Agent":
            result.subagents_spawned += 1
            inp = tool.get("input", {})
            agent_type = inp.get("subagent_type", "general-purpose")
            result.agent_types[agent_type] += 1


def _extract_text(msg: dict) -> str:
    """Extract text content from a message."""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    parts.append(str(block.get("content", "")))
        return "\n".join(parts)
    return str(content)


def _extract_tool_uses(msg: dict) -> list[dict]:
    """Extract tool_use blocks from a message."""
    content = msg.get("content", [])
    if not isinstance(content, list):
        return []
    tools = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tools.append(block)
    return tools


def _generate_warnings(result: AuditResult) -> None:
    """Generate audit warnings based on findings."""
    if not result.mode_selector_invoked:
        result.warnings.append("mode_selector.py was NOT invoked — mode chosen by LLM heuristic")

    if not result.output_validator_invoked:
        result.warnings.append("output_validator.py was NOT invoked — no post-hoc validation")

    if result.checkpoint_count < 6:
        result.warnings.append(
            f"Only {result.checkpoint_count}/6 checkpoints detected — "
            f"pipeline may have skipped user approval gates"
        )

    if result.total_files_written > 1:
        # Check if multiple output files (not just internal/temp)
        output_files = [
            f for f in result.files_written
            if not f["path"].endswith((".py", ".json", ".yaml"))
        ]
        if len(output_files) > 1:
            result.warnings.append(
                f"{len(output_files)} output files written — "
                f"violates single-file contract"
            )

    formats = result.output_formats - {".py", ".json", ".yaml"}
    non_md = formats - {".md"}
    if non_md:
        result.warnings.append(
            f"Non-markdown output formats detected: {non_md} — "
            f"violates markdown-only contract"
        )

    if not result.skill_invoked:
        result.warnings.append(
            "Deep-research skill was NOT formally invoked via Skill tool — "
            "may have been ad-hoc"
        )


def format_report(results: list[AuditResult]) -> str:
    """Format audit results as a markdown report."""
    lines = ["# Deep Research Session Audit Report\n"]
    lines.append(f"**Generated:** {__import__('datetime').date.today()}\n")
    lines.append(f"**Sessions audited:** {len(results)}\n")

    # Summary table
    lines.append("## Summary Comparison\n")
    lines.append("| Metric | " + " | ".join(r.label for r in results) + " |")
    lines.append("|--------|" + "|".join("-----" for _ in results) + "|")

    metrics = [
        ("JSONL Size", lambda r: f"{r.jsonl_size_bytes / 1024:.0f} KB"),
        ("Total Messages", lambda r: str(r.total_messages)),
        ("User Messages", lambda r: str(r.user_messages)),
        ("Skill Formally Invoked", lambda r: "YES" if r.skill_invoked else "**NO**"),
        ("Mode Selector Invoked", lambda r: "YES" if r.mode_selector_invoked else "**NO**"),
        ("Selected Mode", lambda r: r.selected_mode or "unknown"),
        ("Output Validator Invoked", lambda r: "YES" if r.output_validator_invoked else "**NO**"),
        ("Checkpoints Detected", lambda r: f"{r.checkpoint_count}/6"),
        ("Files Written", lambda r: str(r.total_files_written)),
        ("Output Formats", lambda r: ", ".join(sorted(r.output_formats)) or "none"),
        ("Subagents Spawned", lambda r: str(r.subagents_spawned)),
        ("MCP Tools Used", lambda r: str(sum(r.mcp_tools_used.values()))),
        ("Warnings", lambda r: str(len(r.warnings))),
    ]
    for name, fn in metrics:
        lines.append(f"| {name} | " + " | ".join(fn(r) for r in results) + " |")

    # Per-session details
    for result in results:
        lines.append(f"\n## {result.label}\n")
        lines.append(f"**JSONL:** `{result.jsonl_path}`\n")
        lines.append(f"**Size:** {result.jsonl_size_bytes / 1024:.0f} KB\n")
        lines.append(f"**Time window:** {result.first_timestamp or 'N/A'} → {result.last_timestamp or 'N/A'}\n")

        # Warnings
        if result.warnings:
            lines.append("### Warnings\n")
            for w in result.warnings:
                lines.append(f"- {w}")
            lines.append("")

        # MCP tools
        if result.mcp_tools_used:
            lines.append("### MCP Tools Used\n")
            for tool, count in result.mcp_tools_used.most_common():
                lines.append(f"- `{tool}`: {count} calls")
            lines.append("")

        # Files written
        if result.files_written:
            lines.append("### Files Written\n")
            for fw in result.files_written:
                lines.append(f"- `{fw['path']}` (via {fw['tool']})")
            lines.append("")

        # Checkpoints
        if result.checkpoint_details:
            lines.append("### Checkpoint Signals\n")
            for detail in result.checkpoint_details:
                lines.append(f"- {detail}")
            lines.append("")

        # Agent usage
        if result.agent_types:
            lines.append("### Subagent Types\n")
            for atype, count in result.agent_types.most_common():
                lines.append(f"- `{atype}`: {count}")
            lines.append("")

    # Root cause validation
    lines.append("\n## Root Cause Validation\n")
    lines.append("| Root Cause | Evidence From Audit |")
    lines.append("|-----------|-------------------|")

    any_no_mode = any(not r.mode_selector_invoked for r in results)
    any_no_validator = any(not r.output_validator_invoked for r in results)
    any_multi_file = any(r.total_files_written > 1 for r in results)
    any_non_md = any((r.output_formats - {".md", ".py", ".json", ".yaml"}) for r in results)
    any_low_checkpoints = any(r.checkpoint_count < 6 for r in results)

    lines.append(
        f"| RC1: Prompt overrides template | "
        f"{'CONFIRMED' if any_no_mode else 'Needs manual review'} — "
        f"mode_selector not invoked in {sum(1 for r in results if not r.mode_selector_invoked)}/{len(results)} runs |"
    )
    lines.append(
        f"| RC3: No file structure enforcement | "
        f"{'CONFIRMED' if any_multi_file else 'Not detected'} — "
        f"multi-file in {sum(1 for r in results if r.total_files_written > 1)}/{len(results)} runs |"
    )
    lines.append(
        f"| RC4: Checkpoint non-enforcement | "
        f"{'CONFIRMED' if any_low_checkpoints else 'All checkpoints hit'} — "
        f"<6 checkpoints in {sum(1 for r in results if r.checkpoint_count < 6)}/{len(results)} runs |"
    )
    lines.append(
        f"| RC6: No output validation | "
        f"{'CONFIRMED' if any_no_validator else 'Validators ran'} — "
        f"validator not invoked in {sum(1 for r in results if not r.output_validator_invoked)}/{len(results)} runs |"
    )
    lines.append(
        f"| RC7: Non-markdown formats | "
        f"{'CONFIRMED' if any_non_md else 'Markdown only'} — "
        f"non-MD in {sum(1 for r in results if (r.output_formats - {'.md', '.py', '.json', '.yaml'}))} runs |"
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit deep-research JSONL sessions")
    parser.add_argument("jsonl_paths", nargs="+", help="JSONL file path(s)")
    parser.add_argument("--labels", nargs="*", help="Labels for each session")
    parser.add_argument("--output", "-o", help="Output report path")

    args = parser.parse_args()

    labels = args.labels or [Path(p).stem for p in args.jsonl_paths]
    if len(labels) < len(args.jsonl_paths):
        labels.extend(Path(p).stem for p in args.jsonl_paths[len(labels):])

    results = []
    for path, label in zip(args.jsonl_paths, labels):
        print(f"Auditing {label}: {path}...", file=sys.stderr)
        results.append(audit_session(path, label))

    report = format_report(results)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
