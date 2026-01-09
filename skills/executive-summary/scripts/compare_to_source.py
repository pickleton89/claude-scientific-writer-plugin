#!/usr/bin/env python3
"""
Compare executive summary to source document.

Checks:
- Similarity score (flag both too-high and too-low)
- Claim coverage (key source claims appear in summary)
- Originality (no verbatim copying)

Usage:
    python compare_to_source.py <summary_file> <source_file>
"""

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ComparisonResult:
    """Result of source comparison."""

    trigram_overlap: float
    similarity_status: str
    verbatim_phrases: list[str]
    claim_coverage: float
    source_claims: int
    covered_claims: int
    issues: list[str] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Remove code blocks
    text = re.sub(r"[*_#>|`]", "", text)  # Remove markdown
    return re.findall(r"\b\w+\b", text.lower())


def get_ngrams(tokens: list[str], n: int) -> Counter:
    """Generate n-gram frequency counter."""
    if len(tokens) < n:
        return Counter()
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def calculate_similarity(source: str, summary: str, n: int = 3) -> float:
    """Calculate n-gram overlap between source and summary."""
    src_tokens = tokenize(source)
    sum_tokens = tokenize(summary)

    src_ngrams = get_ngrams(src_tokens, n)
    sum_ngrams = get_ngrams(sum_tokens, n)

    if not sum_ngrams:
        return 0.0

    overlap = sum((src_ngrams & sum_ngrams).values())
    total = sum(sum_ngrams.values())

    return overlap / total if total > 0 else 0.0


def find_verbatim_phrases(
    source: str, summary: str, min_length: int = 6
) -> list[str]:
    """Find phrases copied verbatim from source (6+ words)."""
    src_tokens = tokenize(source)
    sum_tokens = tokenize(summary)

    if len(src_tokens) < min_length or len(sum_tokens) < min_length:
        return []

    # Build set of source phrases
    src_phrases = set()
    for i in range(len(src_tokens) - min_length + 1):
        phrase = tuple(src_tokens[i : i + min_length])
        src_phrases.add(phrase)

    # Find matching phrases in summary
    verbatim = []
    for i in range(len(sum_tokens) - min_length + 1):
        phrase = tuple(sum_tokens[i : i + min_length])
        if phrase in src_phrases:
            verbatim.append(" ".join(phrase))

    return list(set(verbatim))


def extract_claims(text: str) -> list[str]:
    """Extract sentences likely to be key claims (contain numbers or findings verbs)."""
    sentences = re.split(r"[.!?]+", text)
    claim_patterns = [
        r"\d+%",
        r"\$\d+",
        r"\b(found|shows?|demonstrates?|indicates?|reveals?)\b",
        r"\b(increased|decreased|improved|reduced|grew|fell)\b",
    ]

    claims = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
        for pattern in claim_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                claims.append(sentence)
                break

    return claims


def check_claim_coverage(
    source: str, summary: str
) -> tuple[int, int, list[str]]:
    """Check how many source claims are represented in summary."""
    source_claims = extract_claims(source)
    summary_lower = summary.lower()

    covered = []
    for claim in source_claims:
        # Extract key numbers and percentages from claim
        numbers = re.findall(r"\d+(?:\.\d+)?%?", claim)
        # Check if any of these numbers appear in summary
        for num in numbers:
            if num in summary_lower:
                covered.append(claim[:50] + "..." if len(claim) > 50 else claim)
                break

    return len(source_claims), len(covered), covered


def compare_to_source(source: str, summary: str) -> ComparisonResult:
    """Run all comparison checks."""
    issues = []

    # Similarity check
    similarity = calculate_similarity(source, summary)

    if similarity > 0.6:
        sim_status = "TOO_SIMILAR"
        issues.append(
            f"Summary may contain too much verbatim text ({similarity:.1%} overlap)"
        )
    elif similarity < 0.1:
        sim_status = "TOO_DIFFERENT"
        issues.append(
            f"Summary may have drifted from source ({similarity:.1%} overlap)"
        )
    else:
        sim_status = "GOOD"

    # Verbatim check
    verbatim = find_verbatim_phrases(source, summary)
    if verbatim:
        issues.append(f"Found {len(verbatim)} verbatim phrase(s) of 6+ words")

    # Claim coverage
    total_claims, covered, _ = check_claim_coverage(source, summary)
    coverage = covered / total_claims if total_claims > 0 else 1.0

    if coverage < 0.3 and total_claims > 3:
        issues.append(
            f"Low claim coverage: only {coverage:.0%} of source claims represented"
        )

    return ComparisonResult(
        trigram_overlap=similarity,
        similarity_status=sim_status,
        verbatim_phrases=verbatim,
        claim_coverage=coverage,
        source_claims=total_claims,
        covered_claims=covered,
        issues=issues,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare executive summary to source document"
    )
    parser.add_argument("summary", type=Path, help="Summary file")
    parser.add_argument("source", type=Path, help="Source document file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    for f in [args.summary, args.source]:
        if not f.exists():
            print(f"ERROR: File not found: {f}", file=sys.stderr)
            sys.exit(2)

    summary = args.summary.read_text()
    source = args.source.read_text()

    result = compare_to_source(source, summary)

    if args.json:
        output = {
            "trigram_overlap": result.trigram_overlap,
            "similarity_status": result.similarity_status,
            "verbatim_phrases": result.verbatim_phrases,
            "claim_coverage": result.claim_coverage,
            "source_claims": result.source_claims,
            "covered_claims": result.covered_claims,
            "issues": result.issues,
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 60)
        print("SOURCE COMPARISON REPORT")
        print("=" * 60)

        # Similarity
        status_label = {
            "GOOD": "[PASS]",
            "TOO_SIMILAR": "[WARN]",
            "TOO_DIFFERENT": "[WARN]",
        }
        print(
            f"\n{status_label[result.similarity_status]} Similarity: {result.trigram_overlap:.1%}"
        )
        print(f"       Status: {result.similarity_status}")

        # Verbatim
        if result.verbatim_phrases:
            print(f"\n[WARN] Verbatim phrases found ({len(result.verbatim_phrases)}):")
            for phrase in result.verbatim_phrases[:3]:
                print(f'       "{phrase}"')
        else:
            print("\n[PASS] No verbatim phrases (6+ words)")

        # Coverage
        coverage_status = "[PASS]" if result.claim_coverage >= 0.3 else "[WARN]"
        print(
            f"\n{coverage_status} Claim coverage: {result.covered_claims}/{result.source_claims} ({result.claim_coverage:.0%})"
        )

        # Issues
        if result.issues:
            print("\n" + "-" * 60)
            print("Issues to address:")
            for issue in result.issues:
                print(f"  • {issue}")

        print()

    sys.exit(1 if result.issues else 0)


if __name__ == "__main__":
    main()
