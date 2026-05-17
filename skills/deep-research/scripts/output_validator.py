#!/usr/bin/env python3
"""
Output validation for the deep-research pipeline compiler.

Post-processing validation of compiler output markdown. Checks:
  - Word count within mode-specific hard min/max
  - Mandatory sections present (all-mode + mode-specific)
  - Citation format: [T1-4: source] count and presence
  - Uncited assertion detection (advisory, not blocking)
  - AI disclosure content verification
  - Methods/Database Versions subsection

Section matching uses token-overlap fuzzy matching so "Gaps in the Literature"
matches "Gap Analysis". Code blocks and References section excluded from
word count.

Input JSON: {"mode": "full", "markdown": "..."}
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from thresholds import (
    CITATION_PATTERN,
    MANDATORY_SECTIONS_ALL,
    MANDATORY_SECTIONS_BY_MODE,
    SIDECAR_ENFORCEMENT,
    SIDECAR_SPECS,
    WORD_COUNTS,
    sidecar_filename,
)

try:
    from output_contract import OutputContract  # noqa: F401 — used by validate_against_contract
except ImportError:
    OutputContract = None  # type: ignore[assignment, misc]

try:
    from validate_sidecar import SidecarValidator, _load_paper_ids
except ImportError:
    SidecarValidator = None  # type: ignore[assignment, misc]
    _load_paper_ids = None  # type: ignore[assignment, misc]


@dataclass
class ValidationResult:
    """Result of output validation."""

    mode: str
    valid: bool
    word_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    section_report: dict[str, bool] = field(default_factory=dict)
    citation_count: int = 0
    uncited_assertions: int = 0


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks from markdown."""
    return re.sub(r"```[\s\S]*?```", "", text)


def _strip_references_section(text: str) -> str:
    """Remove everything from '## References' or '# References' to end or next heading."""
    # Find the References heading and remove to end or next same-level heading
    pattern = r"^#{1,2}\s+References\b.*?(?=^#{1,2}\s|\Z)"
    return re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)


def count_words(markdown: str) -> int:
    """Count words in markdown, excluding code blocks and References section."""
    text = _strip_code_blocks(markdown)
    text = _strip_references_section(text)
    # Remove markdown heading markers, bold/italic markers, links
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    words = text.split()
    return len(words)


def _normalize_section_tokens(heading: str) -> set[str]:
    """Extract meaningful tokens from a section heading for fuzzy matching."""
    # Remove markdown heading markers and normalize
    clean = re.sub(r"^#{1,6}\s+", "", heading.strip())
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", clean)
    tokens = set()
    for t in clean.split():
        t_lower = t.lower()
        if len(t_lower) > 2:
            # Basic plural normalization: strip trailing 's' (but not 'ss')
            if len(t_lower) > 3 and t_lower.endswith("s") and not t_lower.endswith("ss"):
                t_lower = t_lower[:-1]
            tokens.add(t_lower)
    return tokens


def _find_section(headings: list[str], required: str, threshold: float = 0.5) -> bool:
    """
    Check if a required section exists via token-overlap fuzzy matching.

    A match requires ≥ *threshold* token overlap with the required section name.

    Args:
        headings: List of markdown heading strings (e.g. ``["## Methods", ...]``).
        required: Canonical section name to look for.
        threshold: Minimum fraction of required tokens that must overlap
            (default 0.5 for backward compatibility).
    """
    required_tokens = _normalize_section_tokens(required)
    if not required_tokens:
        return False

    for heading in headings:
        heading_tokens = _normalize_section_tokens(heading)
        if not heading_tokens:
            continue
        overlap = len(required_tokens & heading_tokens)
        # Match if ≥ threshold of required tokens are present
        if overlap >= max(1, len(required_tokens) * threshold):
            return True
    return False


def _extract_headings(markdown: str) -> list[str]:
    """Extract all markdown headings (lines starting with #)."""
    return re.findall(r"^#{1,6}\s+.+$", markdown, re.MULTILINE)


def count_citations(markdown: str) -> int:
    """Count [T1-4: source] citations in the text."""
    return len(re.findall(CITATION_PATTERN, markdown))


def count_uncited_assertions(markdown: str) -> int:
    """
    Heuristic: count declarative sentences in Results/Discussion without [T citations.

    Advisory only — not a blocking validation.
    """
    # Find Results and Discussion sections
    results_pattern = r"(?:^#{1,3}\s+(?:Results?|Discussion|Findings?).*?$)(.*?)(?=^#{1,2}\s|\Z)"
    sections = re.findall(results_pattern, markdown, re.MULTILINE | re.DOTALL)

    uncited = 0
    for section_text in sections:
        # Split into sentences (rough heuristic)
        sentences = re.split(r"(?<=[.!?])\s+", section_text)
        for sentence in sentences:
            sentence = sentence.strip()
            # Skip short sentences, headings, bullets, code
            if len(sentence) < 30:
                continue
            if sentence.startswith(("#", "-", "*", "|", "```", ">")):
                continue
            # Check for citation
            if not re.search(CITATION_PATTERN, sentence):
                # Check it's a declarative sentence (contains a verb-like pattern)
                if re.search(r"\b(is|are|was|were|has|have|show|demonstrate|indicate|suggest|found|report)\b", sentence, re.IGNORECASE):
                    uncited += 1

    return uncited


def _check_ai_disclosure(markdown: str) -> list[str]:
    """Verify AI disclosure section contains required elements."""
    issues = []

    # Find AI Disclosure section
    disclosure_match = re.search(
        r"#{1,3}\s+AI\s+Disclosure(.*?)(?=^#{1,2}\s|\Z)",
        markdown,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    if not disclosure_match:
        issues.append("AI Disclosure section not found")
        return issues

    disclosure_text = disclosure_match.group(1)

    # Check for required elements
    if not re.search(r"search\s+date|searched\s+on|date\s+of\s+search", disclosure_text, re.IGNORECASE):
        issues.append("AI Disclosure missing search date")

    if not re.search(r"database|pubmed|biorxiv|consensus|sources?\s+queried", disclosure_text, re.IGNORECASE):
        issues.append("AI Disclosure missing databases queried")

    if not re.search(r"verif|checked|confirmed|spot[\-\s]?check", disclosure_text, re.IGNORECASE):
        issues.append("AI Disclosure missing sources verified percentage")

    return issues


def _check_database_versions(markdown: str) -> bool:
    """Check for Methods/Database Versions subsection."""
    # Look for database versions anywhere in Methods
    has_methods = bool(re.search(r"#{1,3}\s+Methods?\b", markdown, re.IGNORECASE))
    has_versions = bool(re.search(
        r"database\s+version|data\s+version|api\s+version|accessed\s+on|search\s+date",
        markdown,
        re.IGNORECASE,
    ))
    return has_methods and has_versions


def validate_output(data: dict) -> ValidationResult:
    """
    Validate compiler output against mode-specific requirements.

    Args:
        data: Dict with "mode" (str) and "markdown" (str).

    Returns:
        ValidationResult with errors, warnings, and section report.
    """
    mode = data.get("mode", "full")
    markdown = data.get("markdown", "")

    # Socratic mode: no compiler output expected
    if mode == "socratic":
        return ValidationResult(mode=mode, valid=True, word_count=0)

    result = ValidationResult(mode=mode, valid=True, word_count=0)

    # --- Word count ---
    word_count = count_words(markdown)
    result.word_count = word_count

    limits = WORD_COUNTS.get(mode, WORD_COUNTS["full"])
    hard_min = limits["hard_min"]
    hard_max = limits["hard_max"]
    target_min = limits["target_min"]
    target_max = limits["target_max"]

    if word_count < hard_min:
        result.errors.append(
            f"Word count {word_count} below hard minimum {hard_min} for {mode} mode"
        )
    elif word_count < target_min:
        result.warnings.append(
            f"Word count {word_count} below target minimum {target_min} for {mode} mode"
        )

    if word_count > hard_max:
        result.errors.append(
            f"Word count {word_count} above hard maximum {hard_max} for {mode} mode"
        )
    elif word_count > target_max:
        result.warnings.append(
            f"Word count {word_count} above target maximum {target_max} for {mode} mode"
        )

    # --- Mandatory sections ---
    headings = _extract_headings(markdown)

    # All-mode sections
    for section in MANDATORY_SECTIONS_ALL:
        found = _find_section(headings, section)
        result.section_report[section] = found
        if not found:
            result.errors.append(f"Missing mandatory section: {section}")

    # Mode-specific sections
    mode_sections = MANDATORY_SECTIONS_BY_MODE.get(mode, ())
    for section in mode_sections:
        found = _find_section(headings, section)
        result.section_report[section] = found
        if not found:
            result.errors.append(f"Missing {mode}-specific section: {section}")

    # --- Citations ---
    result.citation_count = count_citations(markdown)
    if result.citation_count == 0 and mode not in ("review",):
        result.errors.append("No [T1-4: source] citations found in output")

    # --- Uncited assertions (advisory) ---
    result.uncited_assertions = count_uncited_assertions(markdown)
    if result.uncited_assertions > 3:
        result.warnings.append(
            f"{result.uncited_assertions} potentially uncited assertions in Results/Discussion"
        )

    # --- AI Disclosure content ---
    ai_issues = _check_ai_disclosure(markdown)
    for issue in ai_issues:
        result.warnings.append(issue)

    # --- Database versions ---
    if mode in ("full", "lit-review", "systematic-review", "hypothesis"):
        if not _check_database_versions(markdown):
            result.warnings.append("Methods section missing database version information")

    # Set overall validity
    result.valid = len(result.errors) == 0

    return result


def validate_from_json(data: dict) -> dict:
    """JSON-friendly wrapper for validate_output."""
    result = validate_output(data)
    return {
        "mode": result.mode,
        "valid": result.valid,
        "word_count": result.word_count,
        "errors": result.errors,
        "warnings": result.warnings,
        "section_report": result.section_report,
        "citation_count": result.citation_count,
        "uncited_assertions": result.uncited_assertions,
    }


# ---------------------------------------------------------------------------
# Contract-based validation
# ---------------------------------------------------------------------------

_LATEX_INDICATORS = (
    r"\begin{", r"\end{", r"\section{", r"\subsection{",
    r"\documentclass", r"\usepackage{", r"\chapter{",
)


def _extract_h2_headings(markdown: str) -> list[str]:
    """Extract ``##``-level headings (not ``#`` or ``###``) preserving order."""
    return re.findall(r"^##\s+(.+)$", markdown, re.MULTILINE)


def _extract_section_text(markdown: str, heading: str) -> str:
    """
    Extract the text belonging to a ``##``-level section (from heading to the
    next ``##`` heading or end-of-file).
    """
    # Escape the heading for regex
    escaped = re.escape(heading)
    pattern = rf"^##\s+{escaped}\s*$\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def _count_h3_subsections(section_text: str) -> int:
    """Count ``###``-level headings inside a section body."""
    return len(re.findall(r"^###\s+.+$", section_text, re.MULTILINE))


def _section_words(section_text: str) -> int:
    """Count words in a section body (strips code blocks)."""
    text = _strip_code_blocks(section_text)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return len(text.split())


def _fuzzy_heading_match(heading: str, canonical_name: str, threshold: float) -> bool:
    """Token-overlap check between a heading string and a canonical name."""
    heading_tokens = _normalize_section_tokens(heading)
    canon_tokens = _normalize_section_tokens(canonical_name)
    if not heading_tokens or not canon_tokens:
        return False
    overlap = len(heading_tokens & canon_tokens)
    return overlap >= max(1, len(canon_tokens) * threshold)


def _check_sidecars(
    mode: str,
    report_dir: Path,
    date: str,
    topic_slug: str,
    result: ValidationResult,
) -> None:
    """Verify required sidecars exist and validate per SIDECAR_SPECS[mode].

    Side effect: appends to result.errors (when SIDECAR_ENFORCEMENT == 'required')
    or result.warnings (when 'advisory'). Also enforces the open-CRITICAL
    advocate block regardless of enforcement mode — that one ALWAYS fails.
    """
    if SidecarValidator is None:
        result.warnings.append(
            "Sidecar enforcement skipped — validate_sidecar.py not importable"
        )
        return

    required = SIDECAR_SPECS.get(mode, ())
    if not required:
        return  # socratic, or mode with no sidecars

    sources_path: Path | None = None
    advocate_data: dict | None = None
    sink = result.errors if SIDECAR_ENFORCEMENT == "required" else result.warnings
    prefix = "Sidecar missing/invalid" if SIDECAR_ENFORCEMENT == "required" else "Sidecar advisory"

    for kind in required:
        filename = sidecar_filename(mode, kind, date, topic_slug)
        path = report_dir / filename
        if not path.exists():
            sink.append(f"{prefix}: {filename} not found in {report_dir}")
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            sink.append(f"{prefix}: {filename} is not valid JSON ({e})")
            continue

        known_ids: set[str] | None = None
        if kind in {"grading", "synthesis"} and sources_path is not None:
            known_ids = _load_paper_ids(sources_path) if _load_paper_ids else None

        validator = SidecarValidator(kind)
        ok, errors, warnings = validator.validate(data, known_paper_ids=known_ids)
        if not ok:
            for err in errors:
                sink.append(f"{prefix}: {filename}: {err}")
        # A3 warnings always passed through as warnings (advisory by nature)
        for warn in warnings:
            result.warnings.append(f"Sidecar {filename}: {warn}")

        # Only feed sources.json into downstream paper_id joins when it
        # validated cleanly. A malformed sources.json would yield an empty
        # paper_id set and trigger spurious G1/Y1 errors on every grading /
        # synthesis entry — confusing on top of the already-surfaced sources
        # error.
        if kind == "sources" and ok:
            sources_path = path
        if kind == "advocate":
            advocate_data = data

    # Open-CRITICAL advocate findings ALWAYS block, regardless of enforcement
    # mode. This is the non-negotiable safety gate from agents/advocate.md.
    if advocate_data is not None:
        open_critical = [
            f for f in (advocate_data.get("findings") or [])
            if f.get("severity") == "CRITICAL" and f.get("status") == "open"
        ]
        if open_critical:
            ids = [f.get("id") for f in open_critical]
            result.errors.append(
                f"Open CRITICAL advocate finding(s) {ids} block compiler assembly. "
                "Address or explicitly defer (with resolution_note) before re-running."
            )


def validate_against_contract(
    markdown: str,
    contract: dict,
    file_count: int = 1,
    report_dir: str | Path | None = None,
    date: str | None = None,
    topic_slug: str | None = None,
) -> ValidationResult:
    """
    Contract-based validation of compiler output.

    Performs all checks from :func:`validate_output` (via internal call), then
    adds contract-specific structural checks:

    * Section ordering relative to contract ``order_index`` values.
    * Extra ``##``-level headings not present in the contract (warning).
    * Subsection count validation for ``slot_type == "repeating"`` sections.
    * Per-section word count advisory checks.
    * File count vs. ``file_spec["max_files"]``.
    * LaTeX content detection.
    * Sidecar presence + schema validation (when ``report_dir``, ``date``, and
      ``topic_slug`` are supplied). Behavior gated by
      ``thresholds.SIDECAR_ENFORCEMENT`` ('advisory' or 'required'). Open
      CRITICAL advocate findings always block assembly regardless of mode.

    Args:
        markdown: The compiler output markdown.
        contract: ``OutputContract`` serialised via ``contract_to_json()``
            (dict with keys ``mode``, ``sections``, ``file_spec``,
            ``total_word_range``, etc.).
        file_count: Number of output files produced (default 1).
        report_dir: Directory holding the report and sidecar files. When
            omitted, sidecar checks are skipped (legacy callers preserved).
        date: Report date string (e.g. '2026-05-17') used to compute sidecar
            filenames. Required if ``report_dir`` is given.
        topic_slug: Topic slug used to compute sidecar filenames. Required if
            ``report_dir`` is given.

    Returns:
        :class:`ValidationResult` combining mode-based and contract-based checks.
    """
    mode = contract.get("mode", "full")

    # Run the standard mode-based validation first.
    base_result = validate_output({"mode": mode, "markdown": markdown})

    # Socratic mode — no compiler output expected, pass through.
    if mode == "socratic":
        return base_result

    contract_sections: list[dict] = contract.get("sections", [])

    # ── (f) LaTeX content detection ─────────────────────────────────────
    for indicator in _LATEX_INDICATORS:
        if indicator in markdown:
            base_result.errors.append("Non-markdown content detected (LaTeX)")
            break

    # ── (e) File count validation ───────────────────────────────────────
    file_spec = contract.get("file_spec", {})
    max_files = file_spec.get("max_files")
    if max_files is not None and file_count > max_files:
        base_result.errors.append(
            f"File count {file_count} exceeds contract maximum {max_files}"
        )

    # ── Work with headings ──────────────────────────────────────────────
    h2_headings = _extract_h2_headings(markdown)

    # ── (a) Section ordering check ──────────────────────────────────────
    # For each heading in the markdown, find the matching contract section
    # and record its order_index.  Then verify order_indexes are
    # non-decreasing (i.e. sections appear in the expected order).
    ORDERING_THRESHOLD = 0.6
    matched_order_indexes: list[tuple[str, int]] = []
    for heading in h2_headings:
        for spec in contract_sections:
            if _fuzzy_heading_match(heading, spec["canonical_name"], ORDERING_THRESHOLD):
                matched_order_indexes.append((heading, spec["order_index"]))
                break  # first match wins

    # Check non-decreasing order.
    for i in range(1, len(matched_order_indexes)):
        prev_heading, prev_idx = matched_order_indexes[i - 1]
        curr_heading, curr_idx = matched_order_indexes[i]
        if curr_idx < prev_idx:
            base_result.errors.append(
                f"Section ordering violation: '{curr_heading}' "
                f"(order {curr_idx}) appears after '{prev_heading}' "
                f"(order {prev_idx})"
            )

    # ── (b) Extra section rejection ─────────────────────────────────────
    EXTRA_THRESHOLD = 0.6
    canonical_names = [s["canonical_name"] for s in contract_sections]
    for heading in h2_headings:
        if not _find_section(
            [f"## {name}" for name in canonical_names],
            heading,
            threshold=EXTRA_THRESHOLD,
        ):
            base_result.warnings.append(
                f"Extra section not in contract: '{heading}'"
            )

    # ── (c) Subsection count validation (repeating slots) ───────────────
    for spec in contract_sections:
        subsection_specs = spec.get("subsection_specs", [])
        repeating_subs = [
            s for s in subsection_specs if s.get("slot_type") == "repeating"
        ]
        if not repeating_subs:
            continue

        # Find the matching heading in the markdown.
        section_heading = None
        for heading in h2_headings:
            if _fuzzy_heading_match(heading, spec["canonical_name"], EXTRA_THRESHOLD):
                section_heading = heading
                break

        if section_heading is None:
            continue  # Section missing — already flagged by base validation.

        section_text = _extract_section_text(markdown, section_heading)
        h3_count = _count_h3_subsections(section_text)

        # Derive bounds from the repeating subsection spec or the parent.
        # The contract may carry min/max on the subsection dict (from thresholds),
        # or we fall back to parent's max_subsections.
        for rep in repeating_subs:
            min_count = rep.get("min", 1)
            max_count = rep.get("max", spec.get("max_subsections"))
            label = f"{spec['canonical_name']}/{rep.get('canonical_name', 'repeating')}"

            if h3_count < min_count:
                base_result.errors.append(
                    f"Subsection count for '{label}': {h3_count} "
                    f"below minimum {min_count}"
                )
            if max_count is not None and h3_count > max_count:
                base_result.errors.append(
                    f"Subsection count for '{label}': {h3_count} "
                    f"exceeds maximum {max_count}"
                )

    # ── (d) Per-section word count check (advisory) ─────────────────────
    for spec in contract_sections:
        word_range = spec.get("word_range")
        if not word_range:
            continue
        # word_range is serialized as [min, max] list.
        if not isinstance(word_range, (list, tuple)) or len(word_range) != 2:
            continue

        wmin, wmax = word_range[0], word_range[1]

        # Find matching heading.
        section_heading = None
        for heading in h2_headings:
            if _fuzzy_heading_match(heading, spec["canonical_name"], EXTRA_THRESHOLD):
                section_heading = heading
                break
        if section_heading is None:
            continue  # Missing section — already flagged.

        section_text = _extract_section_text(markdown, section_heading)
        word_count = _section_words(section_text)

        if word_count < wmin:
            base_result.warnings.append(
                f"Section '{spec['canonical_name']}' word count {word_count} "
                f"below target minimum {wmin}"
            )
        elif word_count > wmax:
            base_result.warnings.append(
                f"Section '{spec['canonical_name']}' word count {word_count} "
                f"above target maximum {wmax}"
            )

    # ── (g) Sidecar presence + schema validation ────────────────────────
    # Gated by report_dir/date/topic_slug. Legacy callers that omit these
    # skip the sidecar gate (back-compat). When supplied, behavior follows
    # thresholds.SIDECAR_ENFORCEMENT ('advisory' | 'required'); open
    # CRITICAL advocate findings always block regardless of mode.
    if report_dir is not None and date is not None and topic_slug is not None:
        _check_sidecars(mode, Path(report_dir), date, topic_slug, base_result)

    # Recompute overall validity (base errors + new errors).
    base_result.valid = len(base_result.errors) == 0

    return base_result


def validate_contract_from_json(data: dict) -> dict:
    """JSON-friendly wrapper for :func:`validate_against_contract`.

    Input dict keys:
        ``markdown`` (str): The compiler output markdown.
        ``contract`` (dict): ``OutputContract`` serialised via ``contract_to_json()``.
        ``file_count`` (int, optional): Number of output files (default 1).
        ``report_dir`` (str, optional): Directory holding sidecar files.
        ``date`` (str, optional): Report date for sidecar filename computation.
        ``topic_slug`` (str, optional): Topic slug for sidecar filename computation.

    Returns:
        Dict with ``mode``, ``valid``, ``word_count``, ``errors``, ``warnings``,
        ``section_report``, ``citation_count``, ``uncited_assertions``.
    """
    result = validate_against_contract(
        markdown=data.get("markdown", ""),
        contract=data.get("contract", {}),
        file_count=data.get("file_count", 1),
        report_dir=data.get("report_dir"),
        date=data.get("date"),
        topic_slug=data.get("topic_slug"),
    )
    return {
        "mode": result.mode,
        "valid": result.valid,
        "word_count": result.word_count,
        "errors": result.errors,
        "warnings": result.warnings,
        "section_report": result.section_report,
        "citation_count": result.citation_count,
        "uncited_assertions": result.uncited_assertions,
    }


def main():
    """CLI entry point.

    Usage::

        output_validator.py <output.json>
        output_validator.py <output.json> --contract <contract.json>

    When ``--contract`` is provided, uses :func:`validate_against_contract`
    instead of :func:`validate_output`.
    """
    if len(sys.argv) < 2:
        print("Usage: output_validator.py <output.json> [--contract <contract.json>]")
        print('  JSON format: {"mode": "full", "markdown": "..."}')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    # Check for --contract flag.
    contract_data = None
    if "--contract" in sys.argv:
        idx = sys.argv.index("--contract")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                contract_data = json.load(f)

    if contract_data is not None:
        report = validate_contract_from_json({
            "markdown": data.get("markdown", ""),
            "contract": contract_data,
            "file_count": data.get("file_count", 1),
        })
    else:
        report = validate_from_json(data)

    status = "VALID" if report["valid"] else "INVALID"
    print(f"\n{'=' * 60}")
    print(f"OUTPUT VALIDATION: {status}")
    if contract_data is not None:
        print("  (contract-based validation)")
    print(f"{'=' * 60}")

    print(f"\n  Mode: {report['mode']}")
    print(f"  Word count: {report['word_count']}")
    print(f"  Citations: {report['citation_count']}")
    print(f"  Uncited assertions: {report['uncited_assertions']}")

    if report["section_report"]:
        print("\n  Section Checklist:")
        for section, found in report["section_report"].items():
            icon = "✓" if found else "✗"
            print(f"    {icon} {section}")

    if report["errors"]:
        print("\n  Errors:")
        for err in report["errors"]:
            print(f"    ✗ {err}")

    if report["warnings"]:
        print("\n  Warnings:")
        for warn in report["warnings"]:
            print(f"    ⚠ {warn}")

    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
