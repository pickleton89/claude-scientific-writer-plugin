# Determinism Audit: Executive Summary Skill

> **Audit Date:** January 2026
> **Development Stage:** First Draft
> **Current Determinism:** ~65-70%
> **Target Determinism:** 85%
> **Variance Reduction:** 15-20%

---

## Executive Summary

The executive-summary skill is well-architected for its first-draft stage, with an existing validation script (`validate_summary.py`) implementing 7 deterministic quality checks. The skill achieves ~65-70% determinism—strong for a first draft. Primary improvement opportunities: (1) automating the manual "source comparison" workflow step, (2) strengthening component detection from keyword heuristics to structural markdown validation, and (3) adding source document preprocessing.

**Key Insight:** The validation infrastructure is already mature with quantified thresholds (≤10% length, ≤25% passive voice, 15-20 word sentences) and pattern-based checks. The gap is that several workflow steps described in SKILL.md (source comparison, completeness verification) remain manual rather than enforced programmatically.

---

## Current Deterministic Components

### Already Automated in `validate_summary.py`

| Check | Implementation | Determinism |
|-------|----------------|-------------|
| Word count | `count_words()` with markdown cleanup | 100% |
| Passive voice % | 12 regex patterns against sentences | 95% |
| Sentence length | Word count / sentence count ratio | 100% |
| Section references | 6 regex patterns ("Section X", "Table Y") | 100% |
| CTA specificity | Pattern matching for WHAT/WHO/WHEN | 90% |
| Quantification presence | 6 regex patterns (%, $, decimals) | 95% |
| Component detection | Keyword heuristics | 60% |

### Documented But Not Validated

| Requirement | SKILL.md Location | Current Status |
|-------------|-------------------|----------------|
| Source completeness | Workflow Step 1 | Manual verification |
| Source comparison | Workflow Step 5 | Manual re-reading |
| Originality (no copying) | Writing Rule 5 | Not checked |
| Jargon translation | Writing Rule 4 | Not checked |
| Template structure | Five-Component Structure | Keyword heuristics only |

---

## Implementation Plan

### Phase 1: Quick Wins (P0)

#### 1.1 Source Preprocessing Script

**File:** `scripts/preprocess_source.py`

```python
#!/usr/bin/env python3
"""
Preprocess source document before executive summary generation.

Extracts metrics and validates completeness:
- Word count (for 10% length validation)
- Incomplete markers (TBD, TODO, PLACEHOLDER)
- Section structure analysis
- Existing quantification detection

Usage:
    python preprocess_source.py <source_file>

Output:
    JSON with source metrics for downstream validation
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_words(text: str) -> int:
    """Count words excluding markdown syntax."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Remove code blocks
    text = re.sub(r"`[^`]+`", "", text)  # Remove inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Remove links
    text = re.sub(r"[*_#>|]", "", text)  # Remove formatting
    return len(re.findall(r"\b\w+\b", text))


def detect_incomplete_markers(text: str) -> list[dict]:
    """Find TBD, TODO, PLACEHOLDER markers indicating incomplete content."""
    markers = []
    patterns = [
        (r"\b(TBD|TBC)\b", "TBD marker"),
        (r"\b(TODO|FIXME)\b", "TODO marker"),
        (r"\b(PLACEHOLDER|INSERT|FILL IN)\b", "Placeholder text"),
        (r"\[.*?\.\.\.\]", "Bracketed ellipsis"),
        (r"_{3,}", "Blank line placeholder"),
    ]

    for pattern, marker_type in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Find line number
            line_num = text[:match.start()].count('\n') + 1
            markers.append({
                "type": marker_type,
                "text": match.group(),
                "line": line_num
            })

    return markers


def analyze_sections(text: str) -> dict:
    """Analyze document section structure."""
    h1_count = len(re.findall(r"^#\s+", text, re.MULTILINE))
    h2_count = len(re.findall(r"^##\s+", text, re.MULTILINE))
    h3_count = len(re.findall(r"^###\s+", text, re.MULTILINE))

    # Detect empty sections (header followed by another header or end)
    empty_sections = len(re.findall(r"^##[^\n]+\n\s*\n(?=##|\Z)", text, re.MULTILINE))

    return {
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "total_sections": h1_count + h2_count + h3_count,
        "empty_sections": empty_sections
    }


def extract_quantification(text: str) -> list[str]:
    """Extract quantified statements from source."""
    patterns = [
        r"\d+%",  # percentages
        r"\$[\d,]+(?:\.\d{2})?[KMB]?",  # dollar amounts
        r"\d+\.\d+",  # decimals
        r"\b\d{2,}(?:,\d{3})*\b",  # large numbers
    ]

    quantities = []
    for pattern in patterns:
        quantities.extend(re.findall(pattern, text))

    return list(set(quantities))


def assess_completeness(text: str, markers: list, sections: dict) -> dict:
    """Assess overall document completeness."""
    word_count = count_words(text)

    # Scoring
    issues = []
    score = 100

    if markers:
        score -= 20 * len(markers)
        issues.append(f"{len(markers)} incomplete marker(s) found")

    if sections["empty_sections"] > 0:
        score -= 15 * sections["empty_sections"]
        issues.append(f"{sections['empty_sections']} empty section(s)")

    if word_count < 500:
        score -= 10
        issues.append("Document very short (<500 words)")

    score = max(0, score)

    if score >= 80:
        status = "READY"
    elif score >= 50:
        status = "WARN"
    else:
        status = "INCOMPLETE"

    return {
        "status": status,
        "score": score,
        "issues": issues
    }


def preprocess_source(text: str) -> dict:
    """Run all preprocessing checks on source document."""
    word_count = count_words(text)
    markers = detect_incomplete_markers(text)
    sections = analyze_sections(text)
    quantities = extract_quantification(text)
    completeness = assess_completeness(text, markers, sections)

    return {
        "word_count": word_count,
        "recommended_summary_length": int(word_count * 0.10),
        "max_summary_length": int(word_count * 0.15),
        "incomplete_markers": markers,
        "sections": sections,
        "quantification_found": quantities,
        "quantification_count": len(quantities),
        "completeness": completeness
    }


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess source document for executive summary"
    )
    parser.add_argument("file", type=Path, help="Source document to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = args.file.read_text()
    result = preprocess_source(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print("SOURCE DOCUMENT ANALYSIS")
        print("=" * 60)
        print(f"\nWord count: {result['word_count']}")
        print(f"Recommended summary: ≤{result['recommended_summary_length']} words (10%)")
        print(f"Maximum summary: ≤{result['max_summary_length']} words (15%)")
        print(f"\nSections: {result['sections']['total_sections']} total")
        print(f"Quantification found: {result['quantification_count']} metrics")

        print(f"\n--- Completeness: {result['completeness']['status']} ---")
        if result['completeness']['issues']:
            for issue in result['completeness']['issues']:
                print(f"  • {issue}")

        if result['incomplete_markers']:
            print("\nIncomplete markers found:")
            for marker in result['incomplete_markers']:
                print(f"  Line {marker['line']}: {marker['type']} - '{marker['text']}'")

        print()

    # Exit code based on completeness
    if result['completeness']['status'] == "INCOMPLETE":
        sys.exit(2)
    elif result['completeness']['status'] == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

#### 1.2 Structural Template Validation

**File:** `scripts/validate_structure.py`

```python
#!/usr/bin/env python3
"""
Validate executive summary structural compliance.

Checks that the summary follows the exact template structure:
- ## Executive Summary header
- **Key Findings:** section with numbered items
- **Recommendation:** section

More rigorous than keyword-based component detection.

Usage:
    python validate_structure.py <summary_file>
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StructureResult:
    """Result of structural validation."""
    valid: bool
    has_header: bool
    has_findings_section: bool
    has_recommendation: bool
    finding_count: int
    issues: list[str]


def validate_structure(text: str) -> StructureResult:
    """Validate executive summary structure against template."""
    issues = []

    # Check for ## Executive Summary header
    has_header = bool(re.search(r"^##\s+Executive Summary", text, re.MULTILINE | re.IGNORECASE))
    if not has_header:
        issues.append("Missing '## Executive Summary' header")

    # Check for **Key Findings:** section
    has_findings = bool(re.search(r"\*\*Key Findings:?\*\*", text, re.IGNORECASE))
    if not has_findings:
        issues.append("Missing '**Key Findings:**' section")

    # Count numbered findings (1. **...**:)
    finding_pattern = r"^\d+\.\s+\*\*[^*]+\*\*:?"
    findings = re.findall(finding_pattern, text, re.MULTILINE)
    finding_count = len(findings)

    if finding_count < 3:
        issues.append(f"Only {finding_count} findings (minimum 3 required)")
    elif finding_count > 5:
        issues.append(f"Too many findings ({finding_count}); maximum is 5")

    # Check for **Recommendation:** section
    has_recommendation = bool(re.search(r"\*\*Recommendation:?\*\*", text, re.IGNORECASE))
    if not has_recommendation:
        issues.append("Missing '**Recommendation:**' section")

    # Check component order (Hook before Findings before Recommendation)
    if has_findings and has_recommendation:
        findings_pos = re.search(r"\*\*Key Findings", text, re.IGNORECASE)
        rec_pos = re.search(r"\*\*Recommendation", text, re.IGNORECASE)
        if findings_pos and rec_pos and findings_pos.start() > rec_pos.start():
            issues.append("Findings section should come before Recommendation")

    # Check that Recommendation has specifics
    rec_match = re.search(
        r"\*\*Recommendation:?\*\*:?\s*(.*?)(?=\n\n|\n##|\Z)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if rec_match:
        rec_text = rec_match.group(1)
        # Check for action verb
        if not re.search(r"\b(approve|implement|proceed|launch|create|develop|hire|invest|authorize|initiate)\b", rec_text, re.IGNORECASE):
            issues.append("Recommendation lacks action verb")

    valid = len(issues) == 0

    return StructureResult(
        valid=valid,
        has_header=has_header,
        has_findings_section=has_findings,
        has_recommendation=has_recommendation,
        finding_count=finding_count,
        issues=issues
    )


def main():
    parser = argparse.ArgumentParser(
        description="Validate executive summary template structure"
    )
    parser.add_argument("file", type=Path, help="Summary file to validate")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text()
    result = validate_structure(text)

    print("\n" + "=" * 60)
    print("STRUCTURE VALIDATION REPORT")
    print("=" * 60)

    checks = [
        ("Executive Summary header", result.has_header),
        ("Key Findings section", result.has_findings_section),
        ("Recommendation section", result.has_recommendation),
        (f"Finding count (3-5)", 3 <= result.finding_count <= 5),
    ]

    for name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    if result.issues:
        print("\nIssues found:")
        for issue in result.issues:
            print(f"  • {issue}")

    print(f"\nOverall: {'VALID' if result.valid else 'INVALID'}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
```

---

### Phase 2: Core Infrastructure (P1)

#### 2.1 Source Comparison Script

**File:** `scripts/compare_to_source.py`

```python
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
import re
import sys
from collections import Counter
from dataclasses import dataclass
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
    issues: list[str]


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Remove code blocks
    text = re.sub(r"[*_#>|`]", "", text)  # Remove markdown
    return re.findall(r"\b\w+\b", text.lower())


def get_ngrams(tokens: list[str], n: int) -> Counter:
    """Generate n-gram frequency counter."""
    return Counter(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))


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


def find_verbatim_phrases(source: str, summary: str, min_length: int = 6) -> list[str]:
    """Find phrases copied verbatim from source (6+ words)."""
    src_tokens = tokenize(source)
    sum_tokens = tokenize(summary)

    # Build set of source phrases
    src_phrases = set()
    for i in range(len(src_tokens) - min_length + 1):
        phrase = tuple(src_tokens[i:i + min_length])
        src_phrases.add(phrase)

    # Find matching phrases in summary
    verbatim = []
    for i in range(len(sum_tokens) - min_length + 1):
        phrase = tuple(sum_tokens[i:i + min_length])
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


def check_claim_coverage(source: str, summary: str) -> tuple[int, int, list[str]]:
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
                covered.append(claim[:50] + "...")
                break

    return len(source_claims), len(covered), covered


def compare_to_source(source: str, summary: str) -> ComparisonResult:
    """Run all comparison checks."""
    issues = []

    # Similarity check
    similarity = calculate_similarity(source, summary)

    if similarity > 0.6:
        sim_status = "TOO_SIMILAR"
        issues.append(f"Summary may contain too much verbatim text ({similarity:.1%} overlap)")
    elif similarity < 0.1:
        sim_status = "TOO_DIFFERENT"
        issues.append(f"Summary may have drifted from source ({similarity:.1%} overlap)")
    else:
        sim_status = "GOOD"

    # Verbatim check
    verbatim = find_verbatim_phrases(source, summary)
    if verbatim:
        issues.append(f"Found {len(verbatim)} verbatim phrase(s) of 6+ words")

    # Claim coverage
    total_claims, covered, _ = check_claim_coverage(source, summary)
    coverage = covered / total_claims if total_claims > 0 else 0

    if coverage < 0.3 and total_claims > 3:
        issues.append(f"Low claim coverage: only {coverage:.0%} of source claims represented")

    return ComparisonResult(
        trigram_overlap=similarity,
        similarity_status=sim_status,
        verbatim_phrases=verbatim,
        claim_coverage=coverage,
        source_claims=total_claims,
        covered_claims=covered,
        issues=issues
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare executive summary to source document"
    )
    parser.add_argument("summary", type=Path, help="Summary file")
    parser.add_argument("source", type=Path, help="Source document file")
    args = parser.parse_args()

    for f in [args.summary, args.source]:
        if not f.exists():
            print(f"ERROR: File not found: {f}", file=sys.stderr)
            sys.exit(2)

    summary = args.summary.read_text()
    source = args.source.read_text()

    result = compare_to_source(source, summary)

    print("\n" + "=" * 60)
    print("SOURCE COMPARISON REPORT")
    print("=" * 60)

    # Similarity
    status_emoji = {"GOOD": "[PASS]", "TOO_SIMILAR": "[WARN]", "TOO_DIFFERENT": "[WARN]"}
    print(f"\n{status_emoji[result.similarity_status]} Similarity: {result.trigram_overlap:.1%}")
    print(f"       Status: {result.similarity_status}")

    # Verbatim
    if result.verbatim_phrases:
        print(f"\n[WARN] Verbatim phrases found ({len(result.verbatim_phrases)}):")
        for phrase in result.verbatim_phrases[:3]:
            print(f"       \"{phrase}\"")
    else:
        print("\n[PASS] No verbatim phrases (6+ words)")

    # Coverage
    coverage_status = "[PASS]" if result.claim_coverage >= 0.3 else "[WARN]"
    print(f"\n{coverage_status} Claim coverage: {result.covered_claims}/{result.source_claims} ({result.claim_coverage:.0%})")

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
```

#### 2.2 Readability Metrics

**File:** `scripts/check_readability.py`

```python
#!/usr/bin/env python3
"""
Calculate readability metrics for executive summary.

Metrics:
- Flesch-Kincaid Grade Level
- Flesch Reading Ease
- Average sentence length
- Average syllables per word

Usage:
    python check_readability.py <summary_file>
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReadabilityResult:
    """Readability metrics."""
    word_count: int
    sentence_count: int
    syllable_count: int
    avg_sentence_length: float
    avg_syllables_per_word: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    status: str
    issues: list[str]


def count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Adjust for silent e
    if word.endswith("e"):
        count -= 1

    # Adjust for -le endings
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1

    return max(1, count)


def clean_text(text: str) -> str:
    """Remove markdown formatting for analysis."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Code blocks
    text = re.sub(r"`[^`]+`", "", text)  # Inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links
    text = re.sub(r"[*_#>|]", "", text)  # Formatting
    return text


def calculate_readability(text: str) -> ReadabilityResult:
    """Calculate all readability metrics."""
    text = clean_text(text)
    issues = []

    # Count words
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    # Count sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = len(sentences)

    # Count syllables
    syllable_count = sum(count_syllables(w) for w in words)

    # Calculate averages
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    avg_syllables = syllable_count / word_count if word_count > 0 else 0

    # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    fre = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
    fre = max(0, min(100, fre))  # Clamp to 0-100

    # Flesch-Kincaid Grade Level: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
    fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables) - 15.59
    fk_grade = max(0, fk_grade)

    # Evaluate against targets
    # Target: 15-20 words per sentence, grade level 10-14
    if avg_sentence_length > 25:
        issues.append(f"Sentences too long (avg {avg_sentence_length:.1f} words; target 15-20)")
        status = "WARN"
    elif avg_sentence_length > 30:
        issues.append(f"Sentences far too long (avg {avg_sentence_length:.1f} words)")
        status = "FAIL"
    elif fk_grade > 16:
        issues.append(f"Reading level too high (grade {fk_grade:.1f}; target 10-14)")
        status = "WARN"
    elif fk_grade < 8:
        issues.append(f"Reading level may be too simple (grade {fk_grade:.1f})")
        status = "WARN"
    else:
        status = "PASS"

    return ReadabilityResult(
        word_count=word_count,
        sentence_count=sentence_count,
        syllable_count=syllable_count,
        avg_sentence_length=avg_sentence_length,
        avg_syllables_per_word=avg_syllables,
        flesch_reading_ease=fre,
        flesch_kincaid_grade=fk_grade,
        status=status,
        issues=issues
    )


def main():
    parser = argparse.ArgumentParser(
        description="Calculate readability metrics for executive summary"
    )
    parser.add_argument("file", type=Path, help="Summary file to analyze")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text()
    result = calculate_readability(text)

    print("\n" + "=" * 60)
    print("READABILITY REPORT")
    print("=" * 60)

    print(f"\nBasic Counts:")
    print(f"  Words: {result.word_count}")
    print(f"  Sentences: {result.sentence_count}")
    print(f"  Syllables: {result.syllable_count}")

    print(f"\nAverages:")
    print(f"  Words per sentence: {result.avg_sentence_length:.1f} (target: 15-20)")
    print(f"  Syllables per word: {result.avg_syllables_per_word:.2f}")

    print(f"\nReadability Scores:")
    print(f"  Flesch Reading Ease: {result.flesch_reading_ease:.1f}/100")
    print(f"  Flesch-Kincaid Grade: {result.flesch_kincaid_grade:.1f} (target: 10-14)")

    # Interpret FRE score
    if result.flesch_reading_ease >= 70:
        fre_interp = "Easy (general audience)"
    elif result.flesch_reading_ease >= 50:
        fre_interp = "Moderate (high school+)"
    elif result.flesch_reading_ease >= 30:
        fre_interp = "Difficult (college level)"
    else:
        fre_interp = "Very difficult (professional)"
    print(f"  Interpretation: {fre_interp}")

    print(f"\n--- Status: {result.status} ---")
    if result.issues:
        for issue in result.issues:
            print(f"  • {issue}")

    print()
    sys.exit(0 if result.status == "PASS" else 1)


if __name__ == "__main__":
    main()
```

---

### Phase 3: Advanced Features (P2)

#### 3.1 Jargon Detection

**File:** `scripts/flag_jargon.py`

```python
#!/usr/bin/env python3
"""
Detect technical jargon that may not be understood by decision-makers.

Flags uncommon words not in a general vocabulary unless they're
followed by a definition pattern (parenthetical explanation).

Usage:
    python flag_jargon.py <summary_file>
"""

import argparse
import re
import sys
from pathlib import Path

# Common English words (top 5000 + business terms)
# In production, load from external file
COMMON_WORDS = {
    # Basic words (abbreviated set - full version would have 5000+)
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "over", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "can", "this", "that", "these", "those", "it", "its",
    # Business terms
    "revenue", "profit", "cost", "budget", "quarter", "annual", "growth",
    "market", "customer", "employee", "team", "project", "strategy",
    "analysis", "report", "data", "results", "findings", "recommendation",
    "implementation", "timeline", "milestone", "objective", "goal",
    "performance", "productivity", "efficiency", "improvement", "increase",
    "decrease", "reduction", "savings", "investment", "return", "roi",
    "stakeholder", "management", "leadership", "department", "organization",
    "company", "business", "industry", "competitive", "advantage",
    "opportunity", "risk", "challenge", "solution", "approach", "method",
    "process", "system", "infrastructure", "technology", "platform",
    "percent", "percentage", "million", "billion", "thousand", "dollar",
    # Add more as needed...
}


def is_defined(word: str, text: str, word_pos: int) -> bool:
    """Check if word is followed by a definition pattern."""
    # Look for patterns like "word (meaning...)" or "word, meaning..."
    after_word = text[word_pos:word_pos + 100]

    # Parenthetical definition
    if re.match(rf"{word}\s*\([^)]+\)", after_word, re.IGNORECASE):
        return True

    # Comma definition
    if re.match(rf"{word},?\s+(meaning|i\.?e\.?|that is|which means)", after_word, re.IGNORECASE):
        return True

    return False


def flag_jargon(text: str) -> list[dict]:
    """Find potentially jargon words."""
    # Clean text
    clean = re.sub(r"```[\s\S]*?```", "", text)
    clean = re.sub(r"`[^`]+`", "", clean)
    clean = re.sub(r"[*_#>|]", "", clean)

    # Extract words
    words = re.findall(r"\b([a-zA-Z]{4,})\b", clean)

    flagged = []
    seen = set()

    for word in words:
        word_lower = word.lower()

        if word_lower in seen:
            continue
        seen.add(word_lower)

        if word_lower in COMMON_WORDS:
            continue

        # Check if it's defined in context
        pos = clean.lower().find(word_lower)
        if is_defined(word_lower, clean, pos):
            continue

        # Flag it
        flagged.append({
            "word": word,
            "suggestion": "Consider defining or replacing with plain language"
        })

    return flagged


def main():
    parser = argparse.ArgumentParser(
        description="Flag potential jargon in executive summary"
    )
    parser.add_argument("file", type=Path, help="Summary file to analyze")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text()
    flagged = flag_jargon(text)

    print("\n" + "=" * 60)
    print("JARGON DETECTION REPORT")
    print("=" * 60)

    if flagged:
        print(f"\nFound {len(flagged)} potentially unfamiliar term(s):\n")
        for item in flagged[:15]:  # Limit output
            print(f"  • {item['word']}")

        if len(flagged) > 15:
            print(f"\n  ... and {len(flagged) - 15} more")

        print("\n[WARN] Consider defining these terms or using plain language.")
        print("       Decision-makers span domains and may not recognize technical terms.")
    else:
        print("\n[PASS] No obvious jargon detected.")

    print()
    sys.exit(1 if len(flagged) > 5 else 0)


if __name__ == "__main__":
    main()
```

---

## Determinism Scorecard

### Current State

| Component | Current | Notes |
|-----------|---------|-------|
| Input validation | 40% | Source word count manual; no completeness check |
| Template compliance | 60% | Keyword heuristics in validate_summary.py |
| Source fidelity | 0% | Step 5 entirely manual |
| Quality metrics | 85% | 7 checks in validation script |
| Readability | 70% | Sentence length only |
| Jargon detection | 0% | Relies on LLM judgment |

### After Phase 1 (P0)

| Component | Target | Improvement |
|-----------|--------|-------------|
| Input validation | 80% | preprocess_source.py |
| Template compliance | 90% | validate_structure.py |
| Source fidelity | 0% | (Phase 2) |
| Quality metrics | 85% | No change |
| Readability | 70% | No change |
| Jargon detection | 0% | (Phase 3) |

**Phase 1 Determinism:** ~75%

### After Phase 2 (P1)

| Component | Target | Improvement |
|-----------|--------|-------------|
| Input validation | 80% | No change |
| Template compliance | 90% | No change |
| Source fidelity | 75% | compare_to_source.py |
| Quality metrics | 90% | check_readability.py |
| Readability | 95% | check_readability.py |
| Jargon detection | 0% | (Phase 3) |

**Phase 2 Determinism:** ~80%

### After Phase 3 (P2)

| Component | Target | Improvement |
|-----------|--------|-------------|
| Input validation | 85% | Enhanced preprocessing |
| Template compliance | 95% | Edge case handling |
| Source fidelity | 80% | Improved claim extraction |
| Quality metrics | 95% | All checks automated |
| Readability | 95% | No change |
| Jargon detection | 70% | flag_jargon.py |

**Phase 3 Determinism:** ~85%

---

## Priority Matrix

| Priority | Script | Impact | Effort | Status |
|----------|--------|--------|--------|--------|
| **P0** | `preprocess_source.py` | High | Low | Ready to implement |
| **P0** | `validate_structure.py` | High | Low | Ready to implement |
| **P1** | `compare_to_source.py` | High | Medium | Ready to implement |
| **P1** | `check_readability.py` | Medium | Low | Ready to implement |
| **P2** | `flag_jargon.py` | Medium | Medium | Ready to implement |

---

## Success Metrics

| Metric | Current | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|---------|
| Overall determinism | 65-70% | 75% | 80% | 85% |
| Input validation coverage | 40% | 80% | 80% | 85% |
| Template compliance accuracy | 60% | 90% | 90% | 95% |
| Source comparison automation | 0% | 0% | 75% | 80% |
| Readability automation | 70% | 70% | 95% | 95% |
| Jargon detection | 0% | 0% | 0% | 70% |

---

## Testing Plan

### Unit Tests

```python
# tests/test_preprocess_source.py
import pytest
from scripts.preprocess_source import (
    count_words,
    detect_incomplete_markers,
    analyze_sections,
)

def test_count_words_excludes_markdown():
    text = "This has **five** words here"
    assert count_words(text) == 5

def test_detect_tbd_markers():
    text = "Section 1\nContent here\n\nSection 2\nTBD"
    markers = detect_incomplete_markers(text)
    assert len(markers) == 1
    assert markers[0]["type"] == "TBD marker"

def test_analyze_sections():
    text = "# Title\n## Section 1\nContent\n## Section 2\nMore content"
    sections = analyze_sections(text)
    assert sections["h1_count"] == 1
    assert sections["h2_count"] == 2
```

### Integration Tests

```python
# tests/test_validation_pipeline.py
def test_full_validation_pipeline():
    """Test complete validation workflow."""
    # 1. Preprocess source
    source_result = preprocess_source(SOURCE_TEXT)
    assert source_result["completeness"]["status"] == "READY"

    # 2. Validate structure
    struct_result = validate_structure(SUMMARY_TEXT)
    assert struct_result.valid

    # 3. Run existing validation
    # ...

    # 4. Compare to source
    compare_result = compare_to_source(SOURCE_TEXT, SUMMARY_TEXT)
    assert compare_result.similarity_status == "GOOD"
```

---

## Appendix: Detection Patterns Reference

### Component Detection (Current)

```python
# Hook indicators (first 500 chars)
HOOK_INDICATORS = [
    "problem", "challenge", "opportunity", "issue", "need",
    "gap", "risk", "threat", "potential", "crisis"
]

# Or presence of statistics in opening
HOOK_STATS = r"\d+%|\$\d+"
```

### Template Structure (Proposed)

```python
# Required markdown patterns
REQUIRED_PATTERNS = {
    "header": r"^##\s+Executive Summary",
    "findings": r"\*\*Key Findings:?\*\*",
    "recommendation": r"\*\*Recommendation:?\*\*",
    "numbered_finding": r"^\d+\.\s+\*\*[^*]+\*\*:?",
}

# Finding count range
FINDING_RANGE = (3, 5)  # Minimum 3, maximum 5
```

### Passive Voice Patterns (Existing)

```python
PASSIVE_PATTERNS = [
    r"\b(is|are|was|were|been|being)\s+\w+ed\b",
    r"\b(is|are|was|were|been|being)\s+\w+en\b",
    r"\bhas been\b", r"\bhave been\b", r"\bhad been\b",
    r"\bwill be\b", r"\bwould be\b", r"\bcould be\b",
    r"\bshould be\b", r"\bmight be\b", r"\bmust be\b",
    r"\bIt was\b", r"\bIt is\b.*\bthat\b",
]
```

### Quantification Patterns (Existing)

```python
QUANT_PATTERNS = [
    r"\d+%",           # percentages
    r"\$\d+",          # dollar amounts
    r"\d+\.\d+",       # decimals
    r"\b\d{2,}\b",     # numbers 10+
    r"\b(increased|decreased|rose|fell|dropped|grew)\s+\d+",
    r"\b(by|to|from)\s+\d+",
]
```
