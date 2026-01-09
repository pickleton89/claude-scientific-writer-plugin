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
import json
import re
import sys
from dataclasses import dataclass, field
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
    issues: list[str] = field(default_factory=list)


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
    if word.endswith("e") and count > 1:
        count -= 1

    # Adjust for -le endings
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1

    # Adjust for -ed endings (often silent)
    if word.endswith("ed") and len(word) > 3 and word[-3] not in vowels:
        count = max(1, count - 1)

    return max(1, count)


def clean_text(text: str) -> str:
    """Remove markdown formatting for analysis."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Code blocks
    text = re.sub(r"`[^`]+`", "", text)  # Inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links
    text = re.sub(r"[*_#>|]", "", text)  # Formatting
    return text


def split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Handle common abbreviations
    text = re.sub(r"\b(Mr|Mrs|Dr|Ms|Prof|Inc|Ltd|Corp|vs|etc)\.", r"\1<DOT>", text)
    text = re.sub(r"\bi\.e\.", "ie<DOT>", text)
    text = re.sub(r"\be\.g\.", "eg<DOT>", text)

    # Split on sentence-ending punctuation
    sentences = re.split(r"[.!?]+", text)

    # Clean up and filter
    result = []
    for s in sentences:
        s = s.replace("<DOT>", ".").strip()
        if s and len(re.findall(r"\b\w+\b", s)) >= 3:  # At least 3 words
            result.append(s)

    return result


def calculate_readability(text: str) -> ReadabilityResult:
    """Calculate all readability metrics."""
    text = clean_text(text)
    issues = []

    # Count words
    words = re.findall(r"\b[a-zA-Z]+\b", text)
    word_count = len(words)

    # Count sentences
    sentences = split_sentences(text)
    sentence_count = len(sentences)

    if word_count == 0 or sentence_count == 0:
        return ReadabilityResult(
            word_count=word_count,
            sentence_count=sentence_count,
            syllable_count=0,
            avg_sentence_length=0.0,
            avg_syllables_per_word=0.0,
            flesch_reading_ease=0.0,
            flesch_kincaid_grade=0.0,
            status="FAIL",
            issues=["Document is empty or has no valid sentences"],
        )

    # Count syllables
    syllable_count = sum(count_syllables(w) for w in words)

    # Calculate averages
    avg_sentence_length = word_count / sentence_count
    avg_syllables = syllable_count / word_count

    # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    fre = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
    fre = max(0.0, min(100.0, fre))  # Clamp to 0-100

    # Flesch-Kincaid Grade Level: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
    fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables) - 15.59
    fk_grade = max(0.0, fk_grade)

    # Evaluate against targets
    # Target: 15-20 words per sentence, grade level 10-14
    status = "PASS"

    if avg_sentence_length > 30:
        issues.append(
            f"Sentences far too long (avg {avg_sentence_length:.1f} words)"
        )
        status = "FAIL"
    elif avg_sentence_length > 25:
        issues.append(
            f"Sentences too long (avg {avg_sentence_length:.1f} words; target 15-20)"
        )
        status = "WARN"

    if fk_grade > 16:
        issues.append(
            f"Reading level too high (grade {fk_grade:.1f}; target 10-14)"
        )
        if status != "FAIL":
            status = "WARN"
    elif fk_grade < 8:
        issues.append(f"Reading level may be too simple (grade {fk_grade:.1f})")
        if status != "FAIL":
            status = "WARN"

    return ReadabilityResult(
        word_count=word_count,
        sentence_count=sentence_count,
        syllable_count=syllable_count,
        avg_sentence_length=avg_sentence_length,
        avg_syllables_per_word=avg_syllables,
        flesch_reading_ease=fre,
        flesch_kincaid_grade=fk_grade,
        status=status,
        issues=issues,
    )


def interpret_fre_score(score: float) -> str:
    """Interpret Flesch Reading Ease score."""
    if score >= 70:
        return "Easy (general audience)"
    elif score >= 50:
        return "Moderate (high school+)"
    elif score >= 30:
        return "Difficult (college level)"
    else:
        return "Very difficult (professional)"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate readability metrics for executive summary"
    )
    parser.add_argument("file", type=Path, help="Summary file to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text()
    result = calculate_readability(text)

    if args.json:
        output = {
            "word_count": result.word_count,
            "sentence_count": result.sentence_count,
            "syllable_count": result.syllable_count,
            "avg_sentence_length": result.avg_sentence_length,
            "avg_syllables_per_word": result.avg_syllables_per_word,
            "flesch_reading_ease": result.flesch_reading_ease,
            "flesch_kincaid_grade": result.flesch_kincaid_grade,
            "interpretation": interpret_fre_score(result.flesch_reading_ease),
            "status": result.status,
            "issues": result.issues,
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 60)
        print("READABILITY REPORT")
        print("=" * 60)

        print("\nBasic Counts:")
        print(f"  Words: {result.word_count}")
        print(f"  Sentences: {result.sentence_count}")
        print(f"  Syllables: {result.syllable_count}")

        print("\nAverages:")
        print(
            f"  Words per sentence: {result.avg_sentence_length:.1f} (target: 15-20)"
        )
        print(f"  Syllables per word: {result.avg_syllables_per_word:.2f}")

        print("\nReadability Scores:")
        print(f"  Flesch Reading Ease: {result.flesch_reading_ease:.1f}/100")
        print(
            f"  Flesch-Kincaid Grade: {result.flesch_kincaid_grade:.1f} (target: 10-14)"
        )
        print(f"  Interpretation: {interpret_fre_score(result.flesch_reading_ease)}")

        print(f"\n--- Status: {result.status} ---")
        if result.issues:
            for issue in result.issues:
                print(f"  • {issue}")

        print()

    sys.exit(0 if result.status == "PASS" else 1)


if __name__ == "__main__":
    main()
