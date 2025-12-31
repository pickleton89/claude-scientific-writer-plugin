#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate readability scores for scientific manuscripts.

Metrics:
- Flesch-Kincaid Grade Level (target: 10-14 for scientific writing)
- Flesch Reading Ease (higher = easier)
- Gunning Fog Index
- SMOG Index

Usage:
    python readability_score.py <input_file>
    python readability_score.py --text "Your text here"
    python readability_score.py <input_file> --section Introduction

Output: Readability metrics with pass/fail against targets.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Readability thresholds from SKILL.md
THRESHOLDS = {
    "flesch_kincaid_grade": {
        "excellent_min": 8,
        "excellent_max": 12,
        "target_min": 10,
        "target_max": 14,
        "acceptable_max": 16,
    },
    "flesch_reading_ease": {
        "scientific_min": 30,  # Scientific papers typically 30-50
        "scientific_max": 50,
        "general_min": 60,  # General audience > 60
    },
}

# Common syllable counting exceptions
SYLLABLE_OVERRIDES = {
    "area": 3, "idea": 3, "real": 2, "being": 2, "seeing": 2,
    "science": 2, "patient": 2, "ancient": 2, "coefficient": 4,
    "create": 2, "created": 3, "creates": 2, "creating": 3,
    "data": 2, "via": 2, "trial": 2, "bias": 2,
}


def count_syllables(word: str) -> int:
    """Count syllables in a word using a heuristic approach."""
    word = word.lower().strip()

    # Check overrides first
    if word in SYLLABLE_OVERRIDES:
        return SYLLABLE_OVERRIDES[word]

    # Remove non-alphabetic characters
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    # Adjustments
    # Silent 'e' at end
    if word.endswith("e") and count > 1:
        count -= 1
    # Words ending in 'le' preceded by consonant
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    # Words ending in 'ed' where 'ed' is not pronounced
    if word.endswith("ed") and len(word) > 3:
        if word[-3] not in "dt":
            count -= 1

    return max(1, count)


def count_complex_words(words: list[str]) -> int:
    """Count words with 3+ syllables (for Gunning Fog and SMOG)."""
    complex_count = 0
    for word in words:
        syllables = count_syllables(word)
        # Exclude common suffixes that add syllables but don't indicate complexity
        word_lower = word.lower()
        if syllables >= 3:
            # Don't count as complex if only complex due to -ed, -es, -ing
            base_syllables = syllables
            if word_lower.endswith("ed"):
                base_syllables = count_syllables(word_lower[:-2])
            elif word_lower.endswith("es"):
                base_syllables = count_syllables(word_lower[:-2])
            elif word_lower.endswith("ing"):
                base_syllables = count_syllables(word_lower[:-3])

            if base_syllables >= 3 or syllables >= 3:
                complex_count += 1

    return complex_count


def split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Protect abbreviations
    protected = text
    abbrevs = ["Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "Fig.", "et al.", "e.g.", "i.e.", "vs.", "etc.", "No.", "Vol."]
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', protected)
    sentences = [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]

    return sentences


def get_words(text: str) -> list[str]:
    """Extract words from text."""
    # Remove markdown formatting
    text = re.sub(r"[#*_`\[\]()]", " ", text)
    # Extract words
    words = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", text)
    return words


def calculate_readability(text: str) -> dict:
    """Calculate various readability metrics."""
    sentences = split_sentences(text)
    words = get_words(text)

    if not sentences or not words:
        return {"error": "Insufficient text for analysis"}

    num_sentences = len(sentences)
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)
    num_complex_words = count_complex_words(words)

    # Average calculations
    avg_sentence_length = num_words / num_sentences
    avg_syllables_per_word = num_syllables / num_words
    percent_complex = (num_complex_words / num_words) * 100

    # Flesch-Kincaid Grade Level
    # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59

    # Flesch Reading Ease
    # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    fk_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

    # Gunning Fog Index
    # Formula: 0.4 * ((words/sentences) + 100 * (complex_words/words))
    fog_index = 0.4 * (avg_sentence_length + percent_complex)

    # SMOG Index (for texts with 30+ sentences)
    # Formula: 1.0430 * sqrt(complex_words * (30/sentences)) + 3.1291
    if num_sentences >= 30:
        smog = 1.0430 * ((num_complex_words * (30 / num_sentences)) ** 0.5) + 3.1291
    else:
        # Simplified SMOG for shorter texts
        smog = 1.0430 * ((num_complex_words * (30 / max(num_sentences, 1))) ** 0.5) + 3.1291

    return {
        "statistics": {
            "total_words": num_words,
            "total_sentences": num_sentences,
            "total_syllables": num_syllables,
            "complex_words": num_complex_words,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "percent_complex_words": round(percent_complex, 1),
        },
        "scores": {
            "flesch_kincaid_grade": round(fk_grade, 1),
            "flesch_reading_ease": round(fk_ease, 1),
            "gunning_fog_index": round(fog_index, 1),
            "smog_index": round(smog, 1),
        },
    }


def interpret_scores(scores: dict) -> dict:
    """Interpret readability scores and provide recommendations."""
    fk_grade = scores["flesch_kincaid_grade"]
    fk_ease = scores["flesch_reading_ease"]
    thresh = THRESHOLDS["flesch_kincaid_grade"]

    # Determine status
    if thresh["excellent_min"] <= fk_grade <= thresh["excellent_max"]:
        status = "EXCELLENT"
        message = "Readability is optimal for scientific audiences"
    elif thresh["target_min"] <= fk_grade <= thresh["target_max"]:
        status = "TARGET"
        message = "Readability meets scientific writing standards"
    elif fk_grade <= thresh["acceptable_max"]:
        status = "ACCEPTABLE"
        message = "Readability is acceptable but could be improved"
    elif fk_grade > thresh["acceptable_max"]:
        status = "TOO_COMPLEX"
        message = "Text is too complex; simplify sentence structure and vocabulary"
    else:
        status = "TOO_SIMPLE"
        message = "Text may be too simple for academic audiences"

    # Generate recommendations
    recommendations = []

    if fk_grade > thresh["target_max"]:
        recommendations.append("Reduce average sentence length (target: 15-20 words)")
        recommendations.append("Replace multi-syllable words with simpler alternatives where possible")
        recommendations.append("Break complex sentences into shorter ones")

    if fk_grade < thresh["excellent_min"]:
        recommendations.append("Consider using more precise technical terminology")
        recommendations.append("Ensure writing reflects appropriate academic rigor")

    if fk_ease < 30:
        recommendations.append("Text is very difficult to read; significant simplification recommended")
    elif fk_ease > 60:
        recommendations.append("Consider whether text is sufficiently technical for target journal")

    return {
        "overall_status": status,
        "message": message,
        "recommendations": recommendations,
        "grade_level_interpretation": get_grade_interpretation(fk_grade),
        "reading_ease_interpretation": get_ease_interpretation(fk_ease),
    }


def get_grade_interpretation(grade: float) -> str:
    """Interpret Flesch-Kincaid grade level."""
    if grade < 6:
        return "Elementary school level"
    elif grade < 9:
        return "Middle school level"
    elif grade < 12:
        return "High school level"
    elif grade < 16:
        return "Undergraduate level"
    elif grade < 20:
        return "Graduate level"
    else:
        return "Post-graduate/professional level"


def get_ease_interpretation(ease: float) -> str:
    """Interpret Flesch Reading Ease score."""
    if ease >= 90:
        return "Very easy - 5th grade"
    elif ease >= 80:
        return "Easy - 6th grade"
    elif ease >= 70:
        return "Fairly easy - 7th grade"
    elif ease >= 60:
        return "Standard - 8th-9th grade"
    elif ease >= 50:
        return "Fairly difficult - 10th-12th grade"
    elif ease >= 30:
        return "Difficult - College level"
    else:
        return "Very difficult - Graduate level"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate readability scores for scientific manuscripts."
    )
    parser.add_argument("input_file", nargs="?", help="Path to input file")
    parser.add_argument("--text", "-t", help="Text to analyze directly")
    parser.add_argument("--section", "-s", help="Analyze only a specific section")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON only")

    args = parser.parse_args()

    if not args.input_file and not args.text:
        parser.error("Either input_file or --text must be provided")

    # Get text content
    if args.text:
        text = args.text
    else:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: File not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        text = input_path.read_text(encoding="utf-8")

    # Extract specific section if requested
    if args.section:
        pattern = rf"(?:^|\n)#+\s*{re.escape(args.section)}.*?\n(.*?)(?=\n#+\s|\Z)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1)
        else:
            print(f"Warning: Section '{args.section}' not found, analyzing entire text", file=sys.stderr)

    # Calculate metrics
    results = calculate_readability(text)

    if "error" in results:
        print(f"Error: {results['error']}", file=sys.stderr)
        sys.exit(1)

    interpretation = interpret_scores(results["scores"])

    report = {
        "statistics": results["statistics"],
        "scores": results["scores"],
        "interpretation": interpretation,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        print("=" * 60)
        print("READABILITY ANALYSIS REPORT")
        print("=" * 60)

        print(f"\nText Statistics:")
        stats = results["statistics"]
        print(f"  Words: {stats['total_words']}")
        print(f"  Sentences: {stats['total_sentences']}")
        print(f"  Avg sentence length: {stats['avg_sentence_length']} words")
        print(f"  Avg syllables/word: {stats['avg_syllables_per_word']}")
        print(f"  Complex words (3+ syllables): {stats['complex_words']} ({stats['percent_complex_words']}%)")

        print(f"\nReadability Scores:")
        scores = results["scores"]
        thresh = THRESHOLDS["flesch_kincaid_grade"]
        print(f"  Flesch-Kincaid Grade: {scores['flesch_kincaid_grade']}")
        print(f"    - {interpretation['grade_level_interpretation']}")
        print(f"    - Target for scientific writing: {thresh['target_min']}-{thresh['target_max']}")
        print(f"  Flesch Reading Ease: {scores['flesch_reading_ease']}")
        print(f"    - {interpretation['reading_ease_interpretation']}")
        print(f"  Gunning Fog Index: {scores['gunning_fog_index']}")
        print(f"  SMOG Index: {scores['smog_index']}")

        print(f"\nOverall Status: {interpretation['overall_status']}")
        print(f"Assessment: {interpretation['message']}")

        if interpretation["recommendations"]:
            print(f"\nRecommendations:")
            for rec in interpretation["recommendations"]:
                print(f"  - {rec}")

    # Exit code based on status
    exit_codes = {"EXCELLENT": 0, "TARGET": 0, "ACCEPTABLE": 0, "TOO_COMPLEX": 1, "TOO_SIMPLE": 1}
    sys.exit(exit_codes.get(interpretation["overall_status"], 1))


if __name__ == "__main__":
    main()
