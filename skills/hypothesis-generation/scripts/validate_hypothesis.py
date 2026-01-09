#!/usr/bin/env python3
"""Validate hypothesis structure against required schema."""

from dataclasses import dataclass
from typing import Optional
import json
import sys


@dataclass
class Evidence:
    finding: str
    citation: str


@dataclass
class Prediction:
    statement: str
    condition: str
    expected_outcome: str
    magnitude: Optional[str]
    falsification_criterion: str


@dataclass
class Mechanism:
    trigger: str
    pathway: str
    outcome: str
    causal_chain: list[str]


@dataclass
class QualityScores:
    testability: int  # 0, 1, or 2
    falsifiability: int
    parsimony: int
    explanatory_power: int
    distinctiveness: int

    @property
    def total(self) -> int:
        return (
            self.testability
            + self.falsifiability
            + self.parsimony
            + self.explanatory_power
            + self.distinctiveness
        )

    def __post_init__(self):
        for field in [
            self.testability,
            self.falsifiability,
            self.parsimony,
            self.explanatory_power,
            self.distinctiveness,
        ]:
            if field not in [0, 1, 2]:
                raise ValueError("Quality scores must be 0, 1, or 2")


@dataclass
class Hypothesis:
    id: str  # H1, H2, etc.
    title: str
    mechanism: Mechanism
    supporting_evidence: list[Evidence]
    conflicting_evidence: list[Evidence]
    assumptions: list[str]
    predictions: list[Prediction]
    quality_scores: QualityScores


def validate_hypothesis(h: dict) -> tuple[bool, list[str]]:
    """
    Validate a single hypothesis against required structure.

    Returns:
        (is_valid, list of error messages)
    """
    errors = []

    # Required fields
    if "id" not in h:
        errors.append("Missing hypothesis ID")
    if "title" not in h:
        errors.append("Missing title")
    elif len(h["title"]) > 80:
        errors.append(f"Title too long ({len(h['title'])} chars, max 80)")

    # Mechanism structure
    if "mechanism" not in h:
        errors.append("Missing mechanism")
    else:
        mech = h["mechanism"]
        for field in ["trigger", "pathway", "outcome", "causal_chain"]:
            if field not in mech:
                errors.append(f"Mechanism missing '{field}'")
        if "causal_chain" in mech and len(mech["causal_chain"]) < 2:
            errors.append("Causal chain must have at least 2 steps")

    # Evidence requirements
    if "supporting_evidence" not in h:
        errors.append("Missing supporting_evidence")
    elif len(h["supporting_evidence"]) < 3:
        errors.append(
            f"Insufficient supporting evidence ({len(h['supporting_evidence'])}, need ≥3)"
        )
    else:
        for i, e in enumerate(h["supporting_evidence"]):
            if "finding" not in e or "citation" not in e:
                errors.append(f"Evidence item {i} missing finding or citation")

    # Assumptions (minimum 2)
    if "assumptions" not in h:
        errors.append("Missing assumptions")
    elif len(h["assumptions"]) < 2:
        errors.append(f"Insufficient assumptions ({len(h['assumptions'])}, need ≥2)")

    # Predictions (minimum 2)
    if "predictions" not in h:
        errors.append("Missing predictions")
    elif len(h["predictions"]) < 2:
        errors.append(f"Insufficient predictions ({len(h['predictions'])}, need ≥2)")
    else:
        for i, p in enumerate(h["predictions"]):
            required = [
                "statement",
                "condition",
                "expected_outcome",
                "falsification_criterion",
            ]
            missing = [f for f in required if f not in p]
            if missing:
                errors.append(f"Prediction {i} missing: {missing}")

    # Quality scores
    if "quality_scores" not in h:
        errors.append("Missing quality_scores")
    else:
        qs = h["quality_scores"]
        required_scores = [
            "testability",
            "falsifiability",
            "parsimony",
            "explanatory_power",
            "distinctiveness",
        ]
        missing = [s for s in required_scores if s not in qs]
        if missing:
            errors.append(f"Quality scores missing: {missing}")
        else:
            for s in required_scores:
                if qs[s] not in [0, 1, 2]:
                    errors.append(f"Invalid {s} score: {qs[s]} (must be 0, 1, or 2)")

    return len(errors) == 0, errors


def validate_hypothesis_set(hypothesis_set: dict) -> dict:
    """
    Validate complete hypothesis set.

    Returns:
        Validation report dictionary
    """
    report = {
        "is_valid": True,
        "hypothesis_count": 0,
        "total_citations": 0,
        "quality_summary": {},
        "errors": [],
        "warnings": [],
    }

    if "hypotheses" not in hypothesis_set:
        report["is_valid"] = False
        report["errors"].append("Missing 'hypotheses' array")
        return report

    hypotheses = hypothesis_set["hypotheses"]
    report["hypothesis_count"] = len(hypotheses)

    # Count check
    if len(hypotheses) < 3:
        report["is_valid"] = False
        report["errors"].append(
            f"Insufficient hypotheses ({len(hypotheses)}, need ≥3)"
        )
    elif len(hypotheses) > 5:
        report["warnings"].append(f"More than 5 hypotheses ({len(hypotheses)})")

    # Validate each hypothesis
    all_citations = set()
    quality_totals = []

    for i, h in enumerate(hypotheses):
        is_valid, errors = validate_hypothesis(h)
        if not is_valid:
            report["is_valid"] = False
            for e in errors:
                report["errors"].append(f"H{i+1}: {e}")

        # Collect citations
        for e in h.get("supporting_evidence", []):
            all_citations.add(e.get("citation", ""))
        for e in h.get("conflicting_evidence", []):
            all_citations.add(e.get("citation", ""))

        # Collect quality scores
        if "quality_scores" in h:
            qs = h["quality_scores"]
            total = sum(
                qs.get(s, 0)
                for s in [
                    "testability",
                    "falsifiability",
                    "parsimony",
                    "explanatory_power",
                    "distinctiveness",
                ]
            )
            quality_totals.append(total)
            report["quality_summary"][h.get("id", f"H{i+1}")] = total

    report["total_citations"] = len(all_citations)

    # Quality threshold checks
    if quality_totals:
        if max(quality_totals) < 8:
            report["warnings"].append("No hypothesis scores ≥8/10 (strong)")
        if any(q < 5 for q in quality_totals):
            report["warnings"].append("Some hypotheses score <5/10 (weak)")

    return report


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_hypothesis.py <hypotheses.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        hypothesis_set = json.load(f)

    report = validate_hypothesis_set(hypothesis_set)

    print(f"\n{'✓' if report['is_valid'] else '✗'} Hypothesis Set Validation")
    print(f"  Hypotheses: {report['hypothesis_count']}")
    print(f"  Citations: {report['total_citations']}")

    if report["quality_summary"]:
        print("\n  Quality Scores:")
        for h_id, score in report["quality_summary"].items():
            status = "strong" if score >= 8 else ("viable" if score >= 5 else "WEAK")
            print(f"    {h_id}: {score}/10 ({status})")

    if report["errors"]:
        print(f"\n  Errors ({len(report['errors'])}):")
        for e in report["errors"]:
            print(f"    ✗ {e}")

    if report["warnings"]:
        print(f"\n  Warnings ({len(report['warnings'])}):")
        for w in report["warnings"]:
            print(f"    ⚠ {w}")

    sys.exit(0 if report["is_valid"] else 1)


if __name__ == "__main__":
    main()
