#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate scientific writing quality against defined thresholds.

Checks:
- Sentence length (target: 15-20 words, max: 25)
- Paragraph length (target: 100-150 words, max: 200)
- Passive voice usage (target: <=25%, max: 40%)

Usage:
    python validate_writing_quality.py <input_file> [--section SECTION]
    python validate_writing_quality.py --text "Your text here"

Output: JSON report with metrics and pass/fail status.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Quality thresholds from SKILL.md
THRESHOLDS = {
    "sentence_length": {
        "target_min": 15,
        "target_max": 20,
        "maximum": 25,
        "excellent_max": 18,
    },
    "paragraph_length": {
        "target_min": 100,
        "target_max": 150,
        "maximum": 200,
        "excellent_max": 120,
    },
    "passive_voice": {
        "target_max": 0.25,  # 25%
        "maximum": 0.40,  # 40%
        "excellent_max": 0.15,  # 15%
    },
}

# Common passive voice indicators
PASSIVE_PATTERNS = [
    r"\b(is|are|was|were|been|being)\s+(\w+ed|done|made|seen|shown|found|given|taken|known)\b",
    r"\b(has|have|had)\s+been\s+\w+ed\b",
    r"\b(will|shall|can|could|may|might|must|should|would)\s+be\s+\w+ed\b",
]


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling common abbreviations."""
    # Protect common abbreviations
    protected = text
    abbrevs = ["Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "Fig.", "et al.", "e.g.", "i.e.", "vs.", "etc."]
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', protected)

    # Restore abbreviations and clean
    sentences = [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]
    return sentences


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip() and len(p.split()) > 5]


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def detect_passive_voice(sentence: str) -> bool:
    """Check if sentence contains passive voice construction."""
    sentence_lower = sentence.lower()
    for pattern in PASSIVE_PATTERNS:
        if re.search(pattern, sentence_lower):
            return True
    return False


def analyze_text(text: str) -> dict:
    """Analyze text and return quality metrics."""
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)

    # Sentence analysis
    sentence_lengths = [count_words(s) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    max_sentence_length = max(sentence_lengths) if sentence_lengths else 0
    long_sentences = [s for s, l in zip(sentences, sentence_lengths) if l > THRESHOLDS["sentence_length"]["maximum"]]

    # Paragraph analysis
    paragraph_lengths = [count_words(p) for p in paragraphs]
    avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    max_paragraph_length = max(paragraph_lengths) if paragraph_lengths else 0
    long_paragraphs = sum(1 for l in paragraph_lengths if l > THRESHOLDS["paragraph_length"]["maximum"])

    # Passive voice analysis
    passive_sentences = [s for s in sentences if detect_passive_voice(s)]
    passive_ratio = len(passive_sentences) / len(sentences) if sentences else 0

    return {
        "total_words": count_words(text),
        "total_sentences": len(sentences),
        "total_paragraphs": len(paragraphs),
        "sentence_length": {
            "average": round(avg_sentence_length, 1),
            "maximum": max_sentence_length,
            "over_limit_count": len(long_sentences),
            "over_limit_examples": long_sentences[:3],  # Show up to 3 examples
        },
        "paragraph_length": {
            "average": round(avg_paragraph_length, 1),
            "maximum": max_paragraph_length,
            "over_limit_count": long_paragraphs,
        },
        "passive_voice": {
            "ratio": round(passive_ratio, 3),
            "percentage": f"{passive_ratio * 100:.1f}%",
            "passive_sentence_count": len(passive_sentences),
            "examples": passive_sentences[:3],  # Show up to 3 examples
        },
    }


def evaluate_quality(metrics: dict) -> dict:
    """Evaluate metrics against thresholds and return pass/fail status."""
    results = {
        "overall_status": "PASS",
        "checks": {},
    }

    # Sentence length check
    avg_sent = metrics["sentence_length"]["average"]
    sent_thresh = THRESHOLDS["sentence_length"]
    if avg_sent <= sent_thresh["excellent_max"]:
        sent_status = "EXCELLENT"
    elif avg_sent <= sent_thresh["target_max"]:
        sent_status = "TARGET"
    elif avg_sent <= sent_thresh["maximum"]:
        sent_status = "ACCEPTABLE"
    else:
        sent_status = "FAIL"
        results["overall_status"] = "FAIL"

    results["checks"]["sentence_length"] = {
        "status": sent_status,
        "value": avg_sent,
        "threshold": f"Target: {sent_thresh['target_min']}-{sent_thresh['target_max']} words, Max: {sent_thresh['maximum']}",
    }

    # Paragraph length check
    avg_para = metrics["paragraph_length"]["average"]
    para_thresh = THRESHOLDS["paragraph_length"]
    if avg_para <= para_thresh["excellent_max"]:
        para_status = "EXCELLENT"
    elif avg_para <= para_thresh["target_max"]:
        para_status = "TARGET"
    elif avg_para <= para_thresh["maximum"]:
        para_status = "ACCEPTABLE"
    else:
        para_status = "FAIL"
        results["overall_status"] = "FAIL"

    results["checks"]["paragraph_length"] = {
        "status": para_status,
        "value": avg_para,
        "threshold": f"Target: {para_thresh['target_min']}-{para_thresh['target_max']} words, Max: {para_thresh['maximum']}",
    }

    # Passive voice check
    passive_ratio = metrics["passive_voice"]["ratio"]
    passive_thresh = THRESHOLDS["passive_voice"]
    if passive_ratio <= passive_thresh["excellent_max"]:
        passive_status = "EXCELLENT"
    elif passive_ratio <= passive_thresh["target_max"]:
        passive_status = "TARGET"
    elif passive_ratio <= passive_thresh["maximum"]:
        passive_status = "ACCEPTABLE"
    else:
        passive_status = "FAIL"
        results["overall_status"] = "FAIL"

    results["checks"]["passive_voice"] = {
        "status": passive_status,
        "value": metrics["passive_voice"]["percentage"],
        "threshold": f"Target: <={passive_thresh['target_max']*100:.0f}%, Max: {passive_thresh['maximum']*100:.0f}%",
    }

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate scientific writing quality against defined thresholds."
    )
    parser.add_argument("input_file", nargs="?", help="Path to input file (Markdown or plain text)")
    parser.add_argument("--text", "-t", help="Text to analyze directly")
    parser.add_argument("--section", "-s", help="Analyze only a specific section (e.g., 'Introduction')")
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

    # Analyze and evaluate
    metrics = analyze_text(text)
    evaluation = evaluate_quality(metrics)

    report = {
        "metrics": metrics,
        "evaluation": evaluation,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        print("=" * 60)
        print("SCIENTIFIC WRITING QUALITY REPORT")
        print("=" * 60)
        print(f"\nTotal: {metrics['total_words']} words, {metrics['total_sentences']} sentences, {metrics['total_paragraphs']} paragraphs")
        print(f"\nOverall Status: {evaluation['overall_status']}")
        print("-" * 40)

        for check_name, check_data in evaluation["checks"].items():
            status_icon = {"EXCELLENT": "+", "TARGET": "+", "ACCEPTABLE": "~", "FAIL": "X"}[check_data["status"]]
            print(f"[{status_icon}] {check_name.replace('_', ' ').title()}: {check_data['value']} ({check_data['status']})")
            print(f"    {check_data['threshold']}")

        # Show problem areas
        if metrics["sentence_length"]["over_limit_examples"]:
            print("\nLong sentences to revise:")
            for i, sent in enumerate(metrics["sentence_length"]["over_limit_examples"], 1):
                truncated = sent[:100] + "..." if len(sent) > 100 else sent
                print(f"  {i}. {truncated}")

        if metrics["passive_voice"]["examples"]:
            print("\nPassive voice examples:")
            for i, sent in enumerate(metrics["passive_voice"]["examples"], 1):
                truncated = sent[:100] + "..." if len(sent) > 100 else sent
                print(f"  {i}. {truncated}")

    # Exit with appropriate code
    sys.exit(0 if evaluation["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
