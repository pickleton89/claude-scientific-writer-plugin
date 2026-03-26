#!/usr/bin/env python3
"""
Calculate quality scores for hypotheses.

Automates scoring for deterministic criteria (testability, falsifiability, parsimony)
while flagging criteria requiring LLM judgment (explanatory_power, distinctiveness).
"""

import json
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class QualityAssessment:
    """Quality assessment for a single hypothesis."""

    hypothesis_id: str
    scores: dict[str, int]
    total: int
    automated_scores: list[str]
    requires_review: list[str]
    notes: list[str]


def score_testability(hypothesis: dict) -> tuple[int, str]:
    """
    Score testability based on prediction specificity.

    2 = Clear experimental approach with quantifiable outcomes
    1 = Testable but vague predictions
    0 = Cannot be empirically tested
    """
    predictions = hypothesis.get("predictions", [])

    if not predictions:
        return 0, "No predictions defined"

    # Check for quantitative elements
    has_magnitude = sum(1 for p in predictions if p.get("magnitude"))
    has_conditions = sum(1 for p in predictions if p.get("condition"))
    has_outcomes = sum(1 for p in predictions if p.get("expected_outcome"))

    if has_magnitude >= 2 and has_conditions >= 2 and has_outcomes >= 2:
        return 2, f"Strong: {len(predictions)} predictions with quantifiable outcomes"
    elif has_outcomes >= 1:
        return 1, f"Moderate: {len(predictions)} predictions, {has_magnitude} with magnitude"
    else:
        return 0, "Weak: predictions lack measurable outcomes"


def score_falsifiability(hypothesis: dict) -> tuple[int, str]:
    """
    Score falsifiability based on explicit falsification criteria.

    2 = Specific falsifying observations defined
    1 = Vague falsification criteria
    0 = No observation could disprove
    """
    predictions = hypothesis.get("predictions", [])

    falsifiable_count = sum(
        1
        for p in predictions
        if p.get("falsification_criterion")
        and len(p.get("falsification_criterion", "")) > 20
    )

    if falsifiable_count >= 2:
        return 2, f"Strong: {falsifiable_count} predictions with clear falsification criteria"
    elif falsifiable_count >= 1:
        return 1, f"Moderate: {falsifiable_count} prediction with falsification criteria"
    else:
        return 0, "Weak: no clear falsification criteria defined"


def score_parsimony(hypothesis: dict) -> tuple[int, str]:
    """
    Score parsimony based on mechanism complexity.

    2 = Simplest fit to evidence (≤3 causal steps)
    1 = Moderate complexity (4-5 steps)
    0 = Unnecessarily complex (>5 steps)
    """
    mechanism = hypothesis.get("mechanism", {})
    causal_chain = mechanism.get("causal_chain", [])

    chain_length = len(causal_chain)
    assumptions = len(hypothesis.get("assumptions", []))

    # Complexity score based on chain length and assumptions
    if chain_length <= 3 and assumptions <= 3:
        return 2, f"Simple: {chain_length} causal steps, {assumptions} assumptions"
    elif chain_length <= 5 and assumptions <= 5:
        return 1, f"Moderate: {chain_length} causal steps, {assumptions} assumptions"
    else:
        return 0, f"Complex: {chain_length} causal steps, {assumptions} assumptions"


def score_explanatory_power(hypothesis: dict) -> tuple[Optional[int], str]:
    """
    Flag explanatory power for LLM review.

    This criterion requires judgment about how much of the phenomenon
    the hypothesis explains - cannot be automated.
    """
    return None, "Requires LLM review: assess % of observations explained"


def score_distinctiveness(
    hypothesis: dict, other_hypotheses: list[dict]
) -> tuple[Optional[int], str]:
    """
    Flag distinctiveness for LLM review with automated assistance.

    Provides mechanism overlap analysis but final score requires judgment.
    """
    if not other_hypotheses:
        return None, "Requires LLM review: no other hypotheses to compare"

    # Basic overlap analysis
    my_chain = set(hypothesis.get("mechanism", {}).get("causal_chain", []))

    overlaps = []
    for other in other_hypotheses:
        other_chain = set(other.get("mechanism", {}).get("causal_chain", []))
        if my_chain and other_chain:
            overlap = len(my_chain & other_chain) / min(len(my_chain), len(other_chain))
            overlaps.append((other.get("id", "?"), round(overlap * 100)))

    overlap_note = ", ".join(f"{h_id}: {pct}% overlap" for h_id, pct in overlaps)
    return None, f"Requires LLM review. Mechanism overlap: {overlap_note}"


def assess_hypothesis(
    hypothesis: dict, all_hypotheses: list[dict]
) -> QualityAssessment:
    """
    Generate quality assessment for a hypothesis.
    """
    h_id = hypothesis.get("id", "?")
    scores = {}
    notes = []
    automated = []
    requires_review = []

    # Automated scores
    score, note = score_testability(hypothesis)
    scores["testability"] = score
    notes.append(f"Testability: {note}")
    automated.append("testability")

    score, note = score_falsifiability(hypothesis)
    scores["falsifiability"] = score
    notes.append(f"Falsifiability: {note}")
    automated.append("falsifiability")

    score, note = score_parsimony(hypothesis)
    scores["parsimony"] = score
    notes.append(f"Parsimony: {note}")
    automated.append("parsimony")

    # LLM-required scores
    score, note = score_explanatory_power(hypothesis)
    if score is None:
        scores["explanatory_power"] = hypothesis.get("quality_scores", {}).get(
            "explanatory_power", 0
        )
        requires_review.append("explanatory_power")
    else:
        scores["explanatory_power"] = score
    notes.append(f"Explanatory Power: {note}")

    others = [h for h in all_hypotheses if h.get("id") != h_id]
    score, note = score_distinctiveness(hypothesis, others)
    if score is None:
        scores["distinctiveness"] = hypothesis.get("quality_scores", {}).get(
            "distinctiveness", 0
        )
        requires_review.append("distinctiveness")
    else:
        scores["distinctiveness"] = score
    notes.append(f"Distinctiveness: {note}")

    total = sum(scores.values())

    return QualityAssessment(
        hypothesis_id=h_id,
        scores=scores,
        total=total,
        automated_scores=automated,
        requires_review=requires_review,
        notes=notes,
    )


def assess_hypothesis_set(hypothesis_set: dict) -> dict:
    """
    Assess all hypotheses in a set.

    Returns:
        Assessment report dictionary
    """
    hypotheses = hypothesis_set.get("hypotheses", [])

    assessments = []
    for h in hypotheses:
        assessment = assess_hypothesis(h, hypotheses)
        assessments.append({
            "hypothesis_id": assessment.hypothesis_id,
            "scores": assessment.scores,
            "total": assessment.total,
            "automated_scores": assessment.automated_scores,
            "requires_review": assessment.requires_review,
            "notes": assessment.notes,
        })

    totals = [a["total"] for a in assessments]

    return {
        "hypothesis_count": len(hypotheses),
        "assessments": assessments,
        "summary": {
            "strong_count": sum(1 for t in totals if t >= 8),
            "viable_count": sum(1 for t in totals if 5 <= t < 8),
            "weak_count": sum(1 for t in totals if t < 5),
            "max_score": max(totals) if totals else 0,
            "min_score": min(totals) if totals else 0,
            "has_strong": max(totals) >= 8 if totals else False,
        },
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: score_hypothesis.py <hypotheses.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    hypotheses = data.get("hypotheses", [])

    print("\n" + "=" * 60)
    print("HYPOTHESIS QUALITY ASSESSMENT")
    print("=" * 60)

    all_assessments = []
    for h in hypotheses:
        assessment = assess_hypothesis(h, hypotheses)
        all_assessments.append(assessment)

        status = (
            "STRONG"
            if assessment.total >= 8
            else ("viable" if assessment.total >= 5 else "WEAK")
        )
        print(f"\n{assessment.hypothesis_id}: {assessment.total}/10 ({status})")
        print(f"  Automated: {', '.join(assessment.automated_scores)}")
        print(
            f"  Needs review: {', '.join(assessment.requires_review) if assessment.requires_review else 'none'}"
        )
        print(f"  Scores: {assessment.scores}")
        for note in assessment.notes:
            print(f"    • {note}")

    # Summary
    print("\n" + "-" * 60)
    totals = [a.total for a in all_assessments]
    print(f"Summary: {len(hypotheses)} hypotheses")
    print(f"  Strong (≥8): {sum(1 for t in totals if t >= 8)}")
    print(f"  Viable (5-7): {sum(1 for t in totals if 5 <= t < 8)}")
    print(f"  Weak (<5): {sum(1 for t in totals if t < 5)}")

    # Exit with error if no strong hypothesis
    if totals and max(totals) < 8:
        print("\n⚠ WARNING: No hypothesis scores ≥8/10")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
