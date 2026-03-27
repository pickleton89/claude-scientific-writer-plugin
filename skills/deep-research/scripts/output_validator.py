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
    WORD_COUNTS,
)


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


def _find_section(headings: list[str], required: str) -> bool:
    """
    Check if a required section exists via token-overlap fuzzy matching.

    A match requires ≥50% token overlap with the required section name.
    """
    required_tokens = _normalize_section_tokens(required)
    if not required_tokens:
        return False

    for heading in headings:
        heading_tokens = _normalize_section_tokens(heading)
        if not heading_tokens:
            continue
        overlap = len(required_tokens & heading_tokens)
        # Match if ≥50% of required tokens are present
        if overlap >= max(1, len(required_tokens) * 0.5):
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


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: output_validator.py <output.json>")
        print('  JSON format: {"mode": "full", "markdown": "..."}')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    report = validate_from_json(data)

    status = "VALID" if report["valid"] else "INVALID"
    print(f"\n{'=' * 60}")
    print(f"OUTPUT VALIDATION: {status}")
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
