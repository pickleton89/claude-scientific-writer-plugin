#!/usr/bin/env python3
"""
Output contract builder for the deep-research pipeline.

Produces a frozen structural contract at Phase 1 (Scoping) that the compiler
agent MUST follow during Phase 4 (Composition). The contract reconciles the
skill's mode-specific section schema with any user-provided output format
specifications in the prompt.

Usage:
    python output_contract.py <input.json>
    JSON: {"mode": "full", "user_prompt": "...", "topic": "..."}

Output:
    JSON contract with section ordering, slot mapping, and validation targets.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Imports from sibling modules
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))

# thresholds.py is being updated concurrently. It may raise ValueError at
# module load time if SECTION_SCHEMAS and MANDATORY_SECTIONS_BY_MODE are
# temporarily inconsistent. We catch both ImportError and ValueError so
# output_contract.py remains functional during that transition.
try:
    from thresholds import ALL_MODES, WORD_COUNTS, SECTION_SCHEMAS, FILE_SPECS
except (ImportError, ValueError):
    # Partial-import fallback: try to get what we can.
    try:
        from thresholds import ALL_MODES, WORD_COUNTS  # type: ignore[no-redef]
    except (ImportError, ValueError):
        ALL_MODES: tuple[str, ...] = (  # type: ignore[no-redef]
            "full", "quick", "lit-review", "systematic-review",
            "hypothesis", "fact-check", "socratic", "review",
        )
        WORD_COUNTS: dict[str, dict[str, int]] = {}  # type: ignore[no-redef]
    SECTION_SCHEMAS: dict[str, list[dict]] = {}  # type: ignore[no-redef]
    FILE_SPECS: dict[str, dict] = {}  # type: ignore[no-redef]

# Reuse the token-overlap normaliser from output_validator (don't duplicate).
from output_validator import _normalize_section_tokens

# ---------------------------------------------------------------------------
# Known format mappings: common user-specified deliverables that always map to
# a specific canonical slot. Keys are lowercased user terms; values are
# canonical section names (matching keys in SECTION_SCHEMAS entries).
# ---------------------------------------------------------------------------

_KNOWN_FORMAT_MAPPINGS: dict[str, str] = {
    "comparative matrix": "Results: Overview",
    "comparison matrix": "Results: Overview",
    "evaluation matrix": "Results: Overview",
    "target evaluation matrix": "Results: Overview",
    "risk assessment matrix": "Results: Overview",
    "risk matrix": "Results: Overview",
    "gap analysis": "Gap Analysis",
    "gaps in the literature": "Gap Analysis",
    "critical unknowns": "Gap Analysis",
    "recommended shortlist": "Conclusion",
    "shortlist": "Conclusion",
    "recommended priority": "Conclusion",
    "per-target evidence": "Thematic Synthesis",
    "per-category evidence": "Thematic Synthesis",
    "evidence summaries": "Thematic Synthesis",
    "evidence synthesis": "Thematic Synthesis",
    "integrated risk profile": "Discussion",
    "mitigation strategies": "Discussion",
    "executive summary": "Executive Summary",
    "abstract": "Abstract",
    "methods": "Methods",
    "methodology": "Methods",
    "search strategy": "Search Strategy",
    "prisma flow": "Methods",
    "prisma diagram": "Methods",
    "literature matrix": "Literature Matrix",
    "evidence table": "Literature Matrix",
    "thematic synthesis": "Thematic Synthesis",
    "meta-analysis": "Results: Overview",
    "forest plot": "Results: Overview",
    "limitations": "Limitations",
    "future directions": "Discussion",
    "references": "References",
    "bibliography": "References",
    "ai disclosure": "AI Disclosure",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class SectionSpec:
    """Specification for a single section (or subsection) in the output contract."""

    canonical_name: str
    """Canonical section name, e.g. 'Executive Summary'."""

    heading_level: int
    """Markdown heading level: 2 for ##, 3 for ###."""

    required: bool
    """Whether the section is mandatory for this mode."""

    order_index: int
    """Zero-based position in the document."""

    slot_type: str
    """One of 'fixed', 'repeating', or 'custom-content'."""

    user_label: str | None = None
    """User's preferred heading text (cosmetic override). None = use canonical."""

    word_range: tuple[int, int] | None = None
    """(min_words, max_words) for this section, or None if unconstrained."""

    allows_subsections: bool = False
    """Whether this section may contain child subsections."""

    max_subsections: int | None = None
    """Upper bound on child subsections, or None if unlimited."""

    subsection_specs: list[SectionSpec] = field(default_factory=list)
    """Child section specifications."""


@dataclass
class OutputContract:
    """Frozen structural contract produced at Phase 1 (Scoping)."""

    mode: str
    """Deep-research mode (e.g. 'full', 'lit-review')."""

    topic: str
    """Research topic / question."""

    sections: list[SectionSpec]
    """Ordered list of top-level section specs."""

    total_word_range: dict[str, int]
    """Word count targets from WORD_COUNTS (target_min, target_max, hard_min, hard_max)."""

    file_spec: dict
    """File delivery specification from FILE_SPECS (filename pattern, format, etc.)."""

    custom_content_map: dict[str, str]
    """Mapping of user format items to canonical slot names."""

    unmapped_items: list[str]
    """User format items that could not be mapped to any canonical slot."""

    frozen_at: str
    """ISO-8601 timestamp when the contract was frozen."""

    warnings: list[str]
    """Advisory messages generated during contract construction."""


# ---------------------------------------------------------------------------
# User-format extraction
# ---------------------------------------------------------------------------


def _extract_user_format_specs(prompt: str) -> list[str]:
    """
    Extract user-specified output format items from the prompt.

    Searches for:
      1. XML blocks: ``<output_format>`` or ``<output>`` tags.
      2. Natural-language lists: "The report should include: X, Y, Z" or
         "Sections: ...", "Deliverables: ...", etc.
      3. Numbered / bulleted lists following format-related keywords.

    Returns:
        Deduplicated list of extracted format items (strings), in order of
        first appearance.
    """
    items: list[str] = []
    seen: set[str] = set()

    def _add(item: str) -> None:
        cleaned = item.strip().strip(".-*)")
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned).strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            items.append(cleaned)

    # --- 1. XML blocks: <output_format>...</output_format> or <output>...</output>
    xml_pattern = r"<output(?:_format)?>(.*?)</output(?:_format)?>"
    for match in re.finditer(xml_pattern, prompt, re.DOTALL | re.IGNORECASE):
        block = match.group(1)
        # Split block into lines; each non-empty line is an item
        for line in block.splitlines():
            line = line.strip()
            if line:
                _add(line)

    # --- 2. Natural-language list patterns
    #   "should include: A, B, C"  /  "must contain: A, B, and C"
    #   "Sections: A; B; C"  /  "Deliverables: A, B, C"
    nl_pattern = (
        r"(?:should\s+include|must\s+contain|must\s+include|sections?|deliverables?|"
        r"format|structure|outline|components?)\s*:\s*"
        r"(.+?)(?:\.|$)"
    )
    for match in re.finditer(nl_pattern, prompt, re.IGNORECASE | re.MULTILINE):
        fragment = match.group(1)
        # Split on commas, semicolons, or " and "
        parts = re.split(r"[;,]|\band\b", fragment)
        for part in parts:
            _add(part)

    # --- 3. Numbered / bulleted lists after format-triggering keywords
    #   Look for lines starting with "- ", "* ", or "1. " within 3 lines of a
    #   keyword like "format", "structure", "sections".
    lines = prompt.splitlines()
    in_list_zone = False
    zone_countdown = 0
    for line in lines:
        stripped = line.strip()
        if re.search(
            r"\b(format|structure|sections?|outline|deliverables?)\b",
            stripped,
            re.IGNORECASE,
        ):
            in_list_zone = True
            zone_countdown = 5  # allow up to 5 subsequent lines
            continue
        if in_list_zone:
            if re.match(r"^[-*]\s+|^\d+[\.\)]\s+", stripped):
                _add(stripped)
                zone_countdown = 5  # reset while we're still in a list
            else:
                zone_countdown -= 1
                if zone_countdown <= 0:
                    in_list_zone = False

    return items


# ---------------------------------------------------------------------------
# Fuzzy section mapping
# ---------------------------------------------------------------------------


def _fuzzy_map_section(
    user_item: str,
    canonical_sections: list[SectionSpec],
    threshold: float = 0.7,
) -> SectionSpec | None:
    """
    Find the best-matching canonical section for a user format item.

    Uses token-overlap matching (reusing ``_normalize_section_tokens`` from
    output_validator) with a 70 % threshold — stricter than the validator's 50 %
    because we need high-confidence mapping at contract-build time.

    Args:
        user_item: User-supplied section / deliverable name.
        canonical_sections: Flat list of canonical SectionSpec objects to match
            against (includes both top-level and subsection specs).
        threshold: Minimum fraction of user tokens that must overlap with a
            canonical section's tokens (default 0.7).

    Returns:
        The best-matching SectionSpec, or None if no match meets the threshold.
    """
    user_tokens = _normalize_section_tokens(user_item)
    if not user_tokens:
        return None

    best_score: float = 0.0
    best_match: SectionSpec | None = None

    for spec in canonical_sections:
        canon_tokens = _normalize_section_tokens(spec.canonical_name)
        if not canon_tokens:
            continue
        overlap = len(user_tokens & canon_tokens)
        # Score = fraction of user tokens matched
        score = overlap / len(user_tokens)
        if score > best_score:
            best_score = score
            best_match = spec

    if best_score >= threshold:
        return best_match
    return None


# ---------------------------------------------------------------------------
# Schema → SectionSpec conversion
# ---------------------------------------------------------------------------


def _schema_dicts_to_specs(schema_dicts: list[dict]) -> list[SectionSpec]:
    """
    Convert a list of section schema dicts (from ``SECTION_SCHEMAS``) into
    ``SectionSpec`` objects.

    Each dict is expected to have at least ``name`` (str) and ``required``
    (bool).  Optional keys: ``heading_level``, ``slot_type``, ``word_range``,
    ``allows_subsections``, ``max_subsections``, ``subsections``.

    Missing keys are filled with sensible defaults.
    """
    specs: list[SectionSpec] = []
    for idx, entry in enumerate(schema_dicts):
        subsection_specs: list[SectionSpec] = []
        raw_subs = entry.get("subsections", [])
        for sub_idx, sub in enumerate(raw_subs):
            # Subsections may be plain strings or dicts.
            if isinstance(sub, str):
                subsection_specs.append(
                    SectionSpec(
                        canonical_name=sub,
                        heading_level=3,
                        required=False,
                        order_index=sub_idx,
                        slot_type="fixed",
                    )
                )
            else:
                subsection_specs.append(
                    SectionSpec(
                        canonical_name=sub.get("name", f"Subsection {sub_idx + 1}"),
                        heading_level=sub.get("heading_level", 3),
                        required=sub.get("required", False),
                        order_index=sub_idx,
                        slot_type=sub.get("slot_type", "fixed"),
                        word_range=tuple(sub["word_range"]) if "word_range" in sub else None,  # type: ignore[arg-type]
                        allows_subsections=sub.get("allows_subsections", False),
                        max_subsections=sub.get("max_subsections", None),
                    )
                )

        # Schema uses "words" for word range tuples, "level" for heading level,
        # and "order" for position.
        raw_words = entry.get("words") or entry.get("word_range")
        word_range = tuple(raw_words) if raw_words else None  # type: ignore[arg-type]
        heading_level = entry.get("level", entry.get("heading_level", 2))
        order_index = entry.get("order", idx)

        specs.append(
            SectionSpec(
                canonical_name=entry.get("name", f"Section {idx + 1}"),
                heading_level=heading_level,
                required=entry.get("required", True),
                order_index=order_index,
                slot_type=entry.get("slot_type", "fixed"),
                word_range=word_range,
                allows_subsections=entry.get("allows_subsections", bool(raw_subs)),
                max_subsections=entry.get("max_subsections", len(raw_subs) if raw_subs else None),
                subsection_specs=subsection_specs,
            )
        )

    return specs


def _flatten_specs(specs: list[SectionSpec]) -> list[SectionSpec]:
    """Return a flat list of all specs including nested subsections."""
    flat: list[SectionSpec] = []
    for spec in specs:
        flat.append(spec)
        if spec.subsection_specs:
            flat.extend(_flatten_specs(spec.subsection_specs))
    return flat


# ---------------------------------------------------------------------------
# Contract builder (main entry point)
# ---------------------------------------------------------------------------


def build_contract(
    mode: str,
    user_prompt: str,
    topic: str = "",
) -> OutputContract:
    """
    Build a frozen output contract for the given mode and user prompt.

    This is the primary entry point. The contract freezes structural
    expectations at Phase 1 so the compiler agent has an unambiguous spec
    to follow in Phase 4.

    Args:
        mode: Deep-research mode (must be in ``ALL_MODES``).
        user_prompt: The user's original research prompt / question.
        topic: Short topic label (extracted upstream or derived from prompt).

    Returns:
        An ``OutputContract`` ready for serialisation or rendering.

    Raises:
        ValueError: If *mode* is not recognised.
    """
    if mode not in ALL_MODES:
        raise ValueError(
            f"Unknown mode '{mode}'. Must be one of: {', '.join(ALL_MODES)}"
        )

    warnings: list[str] = []

    # --- 1. Load section schema for this mode ---------------------------------
    raw_schema = SECTION_SCHEMAS.get(mode, [])
    if not raw_schema:
        warnings.append(
            f"No SECTION_SCHEMAS entry for mode '{mode}' — using empty section list. "
            "This constant is being added to thresholds.py concurrently."
        )

    sections = _schema_dicts_to_specs(raw_schema)

    # --- 2. Parse user-specified format items ---------------------------------
    user_items = _extract_user_format_specs(user_prompt)

    custom_content_map: dict[str, str] = {}
    unmapped_items: list[str] = []

    if user_items:
        flat_specs = _flatten_specs(sections)

        for item in user_items:
            item_lower = item.lower().strip()

            # Skip preamble phrases that aren't actual section names
            if any(item_lower.startswith(p) for p in (
                "the final report", "the report should", "report should",
                "output should", "include:", "produce:",
            )):
                continue

            # Check known hard-coded mappings (exact match, then substring)
            canonical_target = _KNOWN_FORMAT_MAPPINGS.get(item_lower)
            if canonical_target is None:
                # Try substring: if a known key appears in the item
                for known_key, known_target in _KNOWN_FORMAT_MAPPINGS.items():
                    if known_key in item_lower:
                        canonical_target = known_target
                        break
            if canonical_target is not None:
                custom_content_map[item] = canonical_target
                # Set user_label on the matching spec (if it exists)
                for spec in flat_specs:
                    if spec.canonical_name == canonical_target:
                        spec.user_label = item
                        break
                continue

            # Fuzzy match against canonical sections
            matched = _fuzzy_map_section(item, flat_specs, threshold=0.7)
            if matched is not None:
                custom_content_map[item] = matched.canonical_name
                matched.user_label = item
            else:
                unmapped_items.append(item)
                warnings.append(
                    f"User format item '{item}' could not be reliably mapped to a "
                    f"canonical section. Review the mapped sections at Checkpoint 1; "
                    f"you can approve the contract with unmapped items, or revise "
                    f"your request."
                )

    # --- 3. Word count targets ------------------------------------------------
    total_word_range = WORD_COUNTS.get(mode, WORD_COUNTS.get("full", {}))

    # --- 4. File spec ---------------------------------------------------------
    file_spec = FILE_SPECS.get(mode, {})
    if not file_spec:
        warnings.append(
            f"No FILE_SPECS entry for mode '{mode}' — file_spec is empty. "
            "This constant is being added to thresholds.py concurrently."
        )

    # --- 5. Freeze timestamp --------------------------------------------------
    frozen_at = datetime.now(timezone.utc).isoformat()

    return OutputContract(
        mode=mode,
        topic=topic,
        sections=sections,
        total_word_range=total_word_range,
        file_spec=file_spec,
        custom_content_map=custom_content_map,
        unmapped_items=unmapped_items,
        frozen_at=frozen_at,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _section_spec_to_dict(spec: SectionSpec) -> dict:
    """Recursively convert a SectionSpec to a JSON-serialisable dict."""
    d: dict = {
        "canonical_name": spec.canonical_name,
        "heading_level": spec.heading_level,
        "required": spec.required,
        "order_index": spec.order_index,
        "slot_type": spec.slot_type,
        "user_label": spec.user_label,
        "word_range": list(spec.word_range) if spec.word_range else None,
        "allows_subsections": spec.allows_subsections,
        "max_subsections": spec.max_subsections,
    }
    if spec.subsection_specs:
        d["subsection_specs"] = [
            _section_spec_to_dict(sub) for sub in spec.subsection_specs
        ]
    else:
        d["subsection_specs"] = []
    return d


def contract_to_json(contract: OutputContract) -> dict:
    """
    Serialise an ``OutputContract`` to a JSON-compatible dict.

    Suitable for writing to disk or passing between pipeline stages.
    """
    return {
        "mode": contract.mode,
        "topic": contract.topic,
        "sections": [_section_spec_to_dict(s) for s in contract.sections],
        "total_word_range": contract.total_word_range,
        "file_spec": contract.file_spec,
        "custom_content_map": contract.custom_content_map,
        "unmapped_items": contract.unmapped_items,
        "frozen_at": contract.frozen_at,
        "warnings": contract.warnings,
    }


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------


def format_contract_for_user(contract: OutputContract) -> str:
    """
    Render the contract as readable markdown for Checkpoint 1 review.

    Includes: mode, section structure with user-label overrides, word count
    targets, file spec, custom-content mappings, and warnings.
    """
    lines: list[str] = []

    lines.append("# Output Contract")
    lines.append("")
    lines.append(f"**Mode:** {contract.mode}")
    lines.append(f"**Topic:** {contract.topic or '(not specified)'}")
    lines.append(f"**Frozen at:** {contract.frozen_at}")
    lines.append("")

    # --- Word count targets ---
    lines.append("## Word Count Targets")
    lines.append("")
    if contract.total_word_range:
        wc = contract.total_word_range
        lines.append("| Metric | Words |")
        lines.append("|--------|-------|")
        lines.append(f"| Target min | {wc.get('target_min', '—')} |")
        lines.append(f"| Target max | {wc.get('target_max', '—')} |")
        lines.append(f"| Hard min | {wc.get('hard_min', '—')} |")
        lines.append(f"| Hard max | {wc.get('hard_max', '—')} |")
    else:
        lines.append("_No word count targets available for this mode._")
    lines.append("")

    # --- Section structure ---
    lines.append("## Section Structure")
    lines.append("")

    if contract.sections:
        for spec in contract.sections:
            _render_section_line(spec, lines, indent=0)
    else:
        lines.append("_No section schema available for this mode._")
    lines.append("")

    # --- Custom content map ---
    if contract.custom_content_map:
        lines.append("## User Format Mappings")
        lines.append("")
        lines.append("| User Item | Mapped To |")
        lines.append("|-----------|-----------|")
        for user_item, canonical in contract.custom_content_map.items():
            lines.append(f"| {user_item} | {canonical} |")
        lines.append("")

    # --- Unmapped items ---
    if contract.unmapped_items:
        lines.append("## Unmapped Items")
        lines.append("")
        lines.append(
            "The following user-specified items could not be mapped to canonical "
            "sections and require manual resolution:"
        )
        lines.append("")
        for item in contract.unmapped_items:
            lines.append(f"- {item}")
        lines.append("")

    # --- File spec ---
    if contract.file_spec:
        lines.append("## File Specification")
        lines.append("")
        for key, value in contract.file_spec.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

    # --- Warnings ---
    if contract.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in contract.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    return "\n".join(lines)


def _render_section_line(
    spec: SectionSpec,
    lines: list[str],
    indent: int,
) -> None:
    """Render a single section spec as an indented markdown line."""
    prefix = "  " * indent
    marker = "#" * spec.heading_level
    req_tag = " **(required)**" if spec.required else ""
    label_note = f' [user label: "{spec.user_label}"]' if spec.user_label else ""
    word_note = ""
    if spec.word_range:
        word_note = f" ({spec.word_range[0]}-{spec.word_range[1]} words)"

    lines.append(
        f"{prefix}- `{marker}` **{spec.canonical_name}**{req_tag}"
        f"{label_note}{word_note} — slot: {spec.slot_type}"
    )

    for sub in spec.subsection_specs:
        _render_section_line(sub, lines, indent=indent + 1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """
    CLI entry point.

    Reads a JSON file with keys ``mode``, ``user_prompt``, and optionally
    ``topic``.  Prints the contract as both human-readable markdown and
    raw JSON.
    """
    if len(sys.argv) < 2:
        print("Usage: output_contract.py <input.json>")
        print('  JSON format: {"mode": "full", "user_prompt": "...", "topic": "..."}')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    mode = data.get("mode", "full")
    user_prompt = data.get("user_prompt", "")
    topic = data.get("topic", "")

    contract = build_contract(mode=mode, user_prompt=user_prompt, topic=topic)

    # Print human-readable contract
    print(format_contract_for_user(contract))

    # Print JSON to stdout (for piping)
    print("\n---\n")
    print(json.dumps(contract_to_json(contract), indent=2))

    # Exit with 1 if there are unmapped items (requires manual attention)
    sys.exit(1 if contract.unmapped_items else 0)


if __name__ == "__main__":
    main()
