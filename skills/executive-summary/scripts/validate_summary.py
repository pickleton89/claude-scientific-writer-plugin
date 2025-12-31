#!/usr/bin/env python3
"""
Validate Executive Summary Quality

Checks executive summaries against best practices:
- Word count and length constraints
- Passive voice percentage
- Component presence (Hook, Solution, Findings, Value, CTA)
- Quantification in findings
- Call-to-action specificity

Usage:
    python validate_summary.py <markdown_file> [--source-words N]

Options:
    --source-words N    Word count of source document (for 10% check)

Exit codes:
    0 = All checks passed
    1 = Warnings present (minor issues)
    2 = Failures present (must fix)

No external dependencies - uses Python standard library only.
"""

import argparse
import re
import sys
from pathlib import Path
from collections import namedtuple


# Result of a single validation check: status (PASS/WARN/FAIL), message, details
ValidationResult = namedtuple("ValidationResult", ["status", "message", "details"])
ValidationResult.__new__.__defaults__ = ("",)  # Make details optional


# Passive voice indicators (common patterns)
PASSIVE_PATTERNS = [
    r"\b(is|are|was|were|been|being)\s+\w+ed\b",
    r"\b(is|are|was|were|been|being)\s+\w+en\b",
    r"\bhas been\b",
    r"\bhave been\b",
    r"\bhad been\b",
    r"\bwill be\b",
    r"\bwould be\b",
    r"\bcould be\b",
    r"\bshould be\b",
    r"\bmight be\b",
    r"\bmust be\b",
    r"\bIt was\b",
    r"\bIt is\b.*\bthat\b",
]

# Patterns indicating quantification
QUANT_PATTERNS = [
    r"\d+%",  # percentages
    r"\$\d+",  # dollar amounts
    r"\d+\.\d+",  # decimals
    r"\b\d{2,}\b",  # numbers 10+
    r"\b(increased|decreased|rose|fell|dropped|grew)\s+\d+",
    r"\b(by|to|from)\s+\d+",
]

# Section references to avoid
SECTION_REF_PATTERNS = [
    r"[Ss]ection\s+\d",
    r"[Cc]hapter\s+\d",
    r"[Ff]igure\s+\d",
    r"[Tt]able\s+\d",
    r"[Aa]ppendix\s+[A-Z]",
    r"see\s+(above|below|page)",
    r"as\s+(shown|described|mentioned)\s+(above|below|earlier|previously)",
]


def count_words(text):
    """Count words in text, excluding markdown syntax."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    text = re.sub(r"`[^`]+`", "", text)
    # Remove markdown links
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove markdown formatting
    text = re.sub(r"[*_#>|]", "", text)
    # Count words
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def count_sentences(text):
    """Count sentences in text."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Count sentence endings
    sentences = re.split(r"[.!?]+", text)
    return len([s for s in sentences if s.strip()])


def calculate_passive_voice_percent(text):
    """Estimate percentage of passive voice constructions."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0.0

    passive_count = 0
    for sentence in sentences:
        for pattern in PASSIVE_PATTERNS:
            if re.search(pattern, sentence, re.IGNORECASE):
                passive_count += 1
                break

    return (passive_count / len(sentences)) * 100


def check_component_presence(text):
    """Check for presence of five executive summary components."""
    text_lower = text.lower()

    components = {
        "hook": False,
        "solution": False,
        "findings": False,
        "value": False,
        "cta": False,
    }

    # Hook: Usually first paragraph with problem/opportunity statement
    # Look for problem-indicating words in first 200 chars
    first_section = text[:500].lower()
    hook_indicators = ["problem", "challenge", "opportunity", "issue", "need",
                       "gap", "risk", "threat", "potential", "crisis"]
    components["hook"] = any(ind in first_section for ind in hook_indicators) or bool(
        re.search(r"\d+%|\$\d+", text[:300])  # Stats in opening
    )

    # Solution: Methodology or approach description
    solution_indicators = ["method", "approach", "analysis", "study", "examined",
                          "investigated", "assessed", "evaluated", "reviewed"]
    components["solution"] = any(ind in text_lower for ind in solution_indicators)

    # Findings: Look for numbered or bulleted findings with "key findings" header
    components["findings"] = bool(
        re.search(r"\*\*key\s+findings\*\*|##\s*key\s+findings", text_lower) or
        re.search(r"findings?:", text_lower)
    )

    # Value: ROI, benefits, implications
    value_indicators = ["roi", "return", "benefit", "implication", "significance",
                       "impact", "value", "saving", "advantage", "position"]
    components["value"] = any(ind in text_lower for ind in value_indicators)

    # CTA: Recommendation with action words
    cta_indicators = ["recommend", "action", "approve", "implement", "proceed",
                     "next step", "decision", "should", "must", "by q"]
    components["cta"] = (
        bool(re.search(r"\*\*recommendation\*\*", text_lower)) or
        any(ind in text_lower for ind in cta_indicators)
    )

    return components


def check_quantification(text):
    """Count quantified statements and return examples."""
    # Focus on findings section if present
    findings_match = re.search(
        r"\*\*key\s+findings\*\*:?(.*?)(?=\n\n|\*\*recommendation|\Z)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    search_text = findings_match.group(1) if findings_match else text

    quantities = []
    for pattern in QUANT_PATTERNS:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        quantities.extend(matches)

    return len(set(quantities)), list(set(quantities))[:5]


def check_section_references(text):
    """Find any references to main document sections."""
    references = []
    for pattern in SECTION_REF_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        references.extend(matches)
    return references


def check_cta_specificity(text):
    """Check if call to action specifies WHAT, WHO, WHEN."""
    # Find recommendation section (case-insensitive, colon optional before or after **)
    cta_match = re.search(
        r"\*\*[Rr]ecommendation:?\*\*:?\s*(.*?)(?=\n\n|\n##|\Z)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not cta_match:
        return {"what": False, "who": False, "when": False, "found": False}

    cta_text = cta_match.group(1).lower()

    return {
        "found": True,
        "what": bool(re.search(r"(approve|implement|proceed|launch|create|develop|hire|invest)", cta_text)),
        "who": bool(re.search(r"(manager|director|vp|ceo|team|department|by\s+\w+)", cta_text)),
        "when": bool(re.search(r"(q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}|by\s+\w+\s+\d+|within\s+\d+)", cta_text)),
    }


def validate_summary(text, source_words=None):
    """Run all validation checks on executive summary text."""
    results = []

    # 1. Word count check
    word_count = count_words(text)
    if source_words:
        ratio = (word_count / source_words) * 100
        if ratio > 15:
            results.append(ValidationResult(
                "FAIL",
                f"Summary too long: {word_count} words ({ratio:.1f}% of source)",
                f"Target: ≤10% ({source_words * 0.1:.0f} words)"
            ))
        elif ratio > 10:
            results.append(ValidationResult(
                "WARN",
                f"Summary slightly long: {word_count} words ({ratio:.1f}% of source)",
                f"Target: ≤10% ({source_words * 0.1:.0f} words)"
            ))
        else:
            results.append(ValidationResult(
                "PASS",
                f"Length OK: {word_count} words ({ratio:.1f}% of source)"
            ))
    else:
        if word_count > 600:
            results.append(ValidationResult(
                "WARN",
                f"Summary may be too long: {word_count} words",
                "Consider providing --source-words for accurate ratio check"
            ))
        else:
            results.append(ValidationResult(
                "PASS",
                f"Word count: {word_count} words"
            ))

    # 2. Passive voice check
    passive_pct = calculate_passive_voice_percent(text)
    if passive_pct > 50:
        results.append(ValidationResult(
            "FAIL",
            f"Too much passive voice: {passive_pct:.1f}%",
            "Target: ≤25%. Rewrite passive constructions to active voice."
        ))
    elif passive_pct > 40:
        results.append(ValidationResult(
            "WARN",
            f"High passive voice: {passive_pct:.1f}%",
            "Target: ≤25%. Consider revising some passive constructions."
        ))
    elif passive_pct > 25:
        results.append(ValidationResult(
            "PASS",
            f"Passive voice acceptable: {passive_pct:.1f}%",
            "Target: ≤25%"
        ))
    else:
        results.append(ValidationResult(
            "PASS",
            f"Active voice strong: {passive_pct:.1f}% passive"
        ))

    # 3. Component presence check
    components = check_component_presence(text)
    missing = [k for k, v in components.items() if not v]
    if len(missing) > 2:
        results.append(ValidationResult(
            "FAIL",
            f"Missing components: {', '.join(missing)}",
            "Executive summary must include: Hook, Solution, Findings, Value, CTA"
        ))
    elif missing:
        results.append(ValidationResult(
            "WARN",
            f"Possibly missing: {', '.join(missing)}",
            "Verify all 5 components are present"
        ))
    else:
        results.append(ValidationResult(
            "PASS",
            "All 5 components detected"
        ))

    # 4. Quantification check
    quant_count, examples = check_quantification(text)
    if quant_count < 2:
        results.append(ValidationResult(
            "FAIL",
            f"Insufficient quantification: {quant_count} metrics found",
            "Findings should include 3-5 quantified results"
        ))
    elif quant_count < 3:
        results.append(ValidationResult(
            "WARN",
            f"Low quantification: {quant_count} metrics found",
            f"Found: {', '.join(examples)}"
        ))
    else:
        results.append(ValidationResult(
            "PASS",
            f"Good quantification: {quant_count} metrics",
            f"Examples: {', '.join(examples)}"
        ))

    # 5. Section reference check
    references = check_section_references(text)
    if references:
        results.append(ValidationResult(
            "FAIL",
            f"Contains section references: {', '.join(references[:3])}",
            "Summary must stand alone. Restate content instead of referencing."
        ))
    else:
        results.append(ValidationResult(
            "PASS",
            "No section references (standalone OK)"
        ))

    # 6. CTA specificity check
    cta = check_cta_specificity(text)
    if not cta["found"]:
        results.append(ValidationResult(
            "FAIL",
            "No clear recommendation/call-to-action found",
            "Add **Recommendation:** section with specific action"
        ))
    else:
        missing_cta = []
        if not cta["what"]:
            missing_cta.append("WHAT (action)")
        if not cta["who"]:
            missing_cta.append("WHO (owner)")
        if not cta["when"]:
            missing_cta.append("WHEN (timeline)")

        if len(missing_cta) > 1:
            results.append(ValidationResult(
                "WARN",
                f"CTA missing specifics: {', '.join(missing_cta)}",
                "Recommendation should specify: action, owner, and timeline"
            ))
        elif missing_cta:
            results.append(ValidationResult(
                "PASS",
                f"CTA mostly complete (consider adding: {missing_cta[0]})"
            ))
        else:
            results.append(ValidationResult(
                "PASS",
                "CTA fully specified (WHAT, WHO, WHEN)"
            ))

    # 7. Sentence length check
    sentence_count = count_sentences(text)
    if sentence_count > 0:
        avg_words_per_sentence = word_count / sentence_count
        if avg_words_per_sentence > 30:
            results.append(ValidationResult(
                "FAIL",
                f"Sentences too long: avg {avg_words_per_sentence:.1f} words",
                "Target: 15-20 words per sentence"
            ))
        elif avg_words_per_sentence > 25:
            results.append(ValidationResult(
                "WARN",
                f"Sentences somewhat long: avg {avg_words_per_sentence:.1f} words",
                "Target: 15-20 words per sentence"
            ))
        else:
            results.append(ValidationResult(
                "PASS",
                f"Sentence length OK: avg {avg_words_per_sentence:.1f} words"
            ))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate executive summary against best practices"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Markdown file containing executive summary"
    )
    parser.add_argument(
        "--source-words",
        type=int,
        default=None,
        help="Word count of source document (for 10%% length check)"
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}")
        sys.exit(2)

    text = args.file.read_text()
    results = validate_summary(text, args.source_words)

    # Print results
    print("\n" + "=" * 60)
    print("EXECUTIVE SUMMARY VALIDATION REPORT")
    print("=" * 60 + "\n")

    fail_count = 0
    warn_count = 0

    for result in results:
        if result.status == "FAIL":
            prefix = "[FAIL]"
            fail_count += 1
        elif result.status == "WARN":
            prefix = "[WARN]"
            warn_count += 1
        else:
            prefix = "[PASS]"

        print(f"{prefix} {result.message}")
        if result.details:
            print(f"       {result.details}")

    print("\n" + "-" * 60)

    if fail_count > 0:
        print(f"RESULT: {fail_count} FAILURES, {warn_count} WARNINGS")
        print("Status: Must fix FAIL items before delivery")
        sys.exit(2)
    elif warn_count > 0:
        print(f"RESULT: {warn_count} WARNINGS")
        print("Status: Review warnings, fix if possible")
        sys.exit(1)
    else:
        print("RESULT: ALL CHECKS PASSED")
        print("Status: Ready for delivery")
        sys.exit(0)


if __name__ == "__main__":
    main()
