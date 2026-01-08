# Hypothesis Generation — Determinism Audit

> Systematic analysis of opportunities to reduce LLM variance through code-based validation, structured schemas, and automated verification.

---

## Executive Summary

**Current Determinism:** ~55-60%
**Target Determinism:** 85%
**Variance Reduction:** 25-30%

The hypothesis-generation skill is comprehensive and well-documented with excellent workflow structure (8 stages), quantified thresholds (≥40 citations, <5% search saturation, quality scores ≥5/10), and detailed reference materials. However, significant LLM variance exists because **thresholds are stated but never validated**. The highest-impact improvements are: (1) implementing structured hypothesis schemas that enforce required components, (2) automating quality scoring for deterministic criteria, and (3) adding validators to verify citation counts and search saturation claims.

**Key Insight:** The skill has the foundational structure for high determinism—the missing piece is a validation layer that transforms aspirational thresholds into enforced requirements.

---

## Deterministic Scorecard

| Component | Current | Target | Strategy |
|-----------|---------|--------|----------|
| **Input validation** | 30% | 85% | Structured input schema with domain enum |
| **Hypothesis structure** | 50% | 95% | JSON schema enforcement before LaTeX |
| **Quality scoring** | 40% | 75% | Automated scoring for 3/5 criteria |
| **Citation tracking** | 20% | 95% | Automated counter with threshold validation |
| **Stage transitions** | 50% | 90% | Exit criteria validators per stage |
| **Output format** | 80% | 95% | LaTeX preflight checker |

---

## Phase 1: Critical Validation (P0)

### 1.1 Structured Input Schema

**File:** `scripts/validate_input.py`

```python
#!/usr/bin/env python3
"""Validate hypothesis generation input against required schema."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import json
import sys


class ScientificDomain(Enum):
    BIOMEDICAL = "biomedical"
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    ECOLOGY = "ecology"
    MATERIALS = "materials"
    COMPUTATIONAL = "computational"
    NEUROSCIENCE = "neuroscience"
    ENGINEERING = "engineering"
    OTHER = "other"


class ObservationType(Enum):
    UNEXPECTED_FINDING = "unexpected_finding"
    CORRELATION = "correlation"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    MECHANISM_GAP = "mechanism_gap"
    CONFLICTING_RESULTS = "conflicting_results"


class ExplanationLevel(Enum):
    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    TISSUE = "tissue"
    ORGANISM = "organism"
    POPULATION = "population"
    ECOSYSTEM = "ecosystem"


@dataclass
class HypothesisInput:
    """Validated input for hypothesis generation."""
    phenomenon_description: str
    domain: ScientificDomain
    observation_type: ObservationType
    known_mechanisms: list[str]
    excluded_explanations: list[str]
    explanation_levels: list[ExplanationLevel]
    target_hypothesis_count: int  # Exact count: 3, 4, or 5
    available_methods: list[str]
    timeline: str  # "pilot", "standard", "comprehensive"

    def __post_init__(self):
        if len(self.phenomenon_description) < 50:
            raise ValueError("Phenomenon description must be at least 50 characters")
        if self.target_hypothesis_count not in [3, 4, 5]:
            raise ValueError("Target hypothesis count must be exactly 3, 4, or 5")
        if not self.explanation_levels:
            raise ValueError("At least one explanation level must be specified")


def validate_input(input_dict: dict) -> tuple[bool, str, Optional[HypothesisInput]]:
    """
    Validate input dictionary against schema.

    Returns:
        (is_valid, message, validated_input or None)
    """
    required_fields = [
        "phenomenon_description",
        "domain",
        "observation_type",
        "target_hypothesis_count",
        "explanation_levels"
    ]

    # Check required fields
    missing = [f for f in required_fields if f not in input_dict]
    if missing:
        return False, f"Missing required fields: {missing}", None

    try:
        validated = HypothesisInput(
            phenomenon_description=input_dict["phenomenon_description"],
            domain=ScientificDomain(input_dict["domain"]),
            observation_type=ObservationType(input_dict["observation_type"]),
            known_mechanisms=input_dict.get("known_mechanisms", []),
            excluded_explanations=input_dict.get("excluded_explanations", []),
            explanation_levels=[ExplanationLevel(l) for l in input_dict["explanation_levels"]],
            target_hypothesis_count=input_dict["target_hypothesis_count"],
            available_methods=input_dict.get("available_methods", []),
            timeline=input_dict.get("timeline", "standard")
        )
        return True, "Input validated successfully", validated
    except ValueError as e:
        return False, f"Validation error: {e}", None
    except KeyError as e:
        return False, f"Invalid enum value: {e}", None


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_input.py <input.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        input_dict = json.load(f)

    is_valid, message, validated = validate_input(input_dict)
    print(f"{'✓' if is_valid else '✗'} {message}")

    if validated:
        print(f"\nValidated input:")
        print(f"  Domain: {validated.domain.value}")
        print(f"  Type: {validated.observation_type.value}")
        print(f"  Target hypotheses: {validated.target_hypothesis_count}")
        print(f"  Levels: {[l.value for l in validated.explanation_levels]}")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
```

### 1.2 Hypothesis Structure Validator

**File:** `scripts/validate_hypothesis.py`

```python
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
        return (self.testability + self.falsifiability + self.parsimony +
                self.explanatory_power + self.distinctiveness)

    def __post_init__(self):
        for field in [self.testability, self.falsifiability, self.parsimony,
                      self.explanatory_power, self.distinctiveness]:
            if field not in [0, 1, 2]:
                raise ValueError(f"Quality scores must be 0, 1, or 2")


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
        errors.append(f"Insufficient supporting evidence ({len(h['supporting_evidence'])}, need ≥3)")
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
            required = ["statement", "condition", "expected_outcome", "falsification_criterion"]
            missing = [f for f in required if f not in p]
            if missing:
                errors.append(f"Prediction {i} missing: {missing}")

    # Quality scores
    if "quality_scores" not in h:
        errors.append("Missing quality_scores")
    else:
        qs = h["quality_scores"]
        required_scores = ["testability", "falsifiability", "parsimony",
                         "explanatory_power", "distinctiveness"]
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
        "warnings": []
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
        report["errors"].append(f"Insufficient hypotheses ({len(hypotheses)}, need ≥3)")
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
            total = sum(qs.get(s, 0) for s in
                       ["testability", "falsifiability", "parsimony",
                        "explanatory_power", "distinctiveness"])
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
        print(f"\n  Quality Scores:")
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
```

### 1.3 Citation Tracker

**File:** `scripts/track_citations.py`

```python
#!/usr/bin/env python3
"""Track and validate citation requirements."""

import json
import sys
import re
from collections import defaultdict


# Thresholds from SKILL.md
TOTAL_CITATIONS_MIN = 40
TOTAL_CITATIONS_TARGET = 50
MAIN_TEXT_CITATIONS_MIN = 10
MAIN_TEXT_CITATIONS_TARGET = 15
RECENT_PAPERS_MIN_PERCENT = 60  # Papers from last 5 years


def extract_citations_from_hypothesis_set(hypothesis_set: dict) -> dict:
    """
    Extract all citations from structured hypothesis data.

    Returns:
        Dictionary with citation lists by source
    """
    citations = {
        "main_text": set(),
        "appendix": set(),
        "all": set()
    }

    for h in hypothesis_set.get("hypotheses", []):
        # Main text citations (from evidence in hypothesis boxes)
        for e in h.get("supporting_evidence", []):
            cit = e.get("citation", "").strip()
            if cit:
                citations["main_text"].add(cit)
                citations["all"].add(cit)

        # Additional appendix citations
        for e in h.get("appendix_evidence", []):
            cit = e.get("citation", "").strip()
            if cit:
                citations["appendix"].add(cit)
                citations["all"].add(cit)

    return {k: list(v) for k, v in citations.items()}


def extract_year(citation: str) -> int | None:
    """Extract publication year from citation string."""
    # Match patterns like (2023), 2023, et al. 2023
    patterns = [
        r'\((\d{4})\)',  # (2023)
        r'(\d{4})[,\.\)]',  # 2023, or 2023. or 2023)
        r'et al\.?\s*(\d{4})',  # et al. 2023
    ]
    for pattern in patterns:
        match = re.search(pattern, citation)
        if match:
            year = int(match.group(1))
            if 1900 < year < 2100:
                return year
    return None


def analyze_citations(citations: dict, current_year: int = 2026) -> dict:
    """
    Analyze citation list against requirements.

    Returns:
        Analysis report dictionary
    """
    all_cits = citations.get("all", [])
    main_cits = citations.get("main_text", [])

    # Extract years
    years = [extract_year(c) for c in all_cits]
    years = [y for y in years if y is not None]

    recent_cutoff = current_year - 5
    recent_count = sum(1 for y in years if y >= recent_cutoff)
    recent_percent = (recent_count / len(years) * 100) if years else 0

    report = {
        "counts": {
            "total": len(all_cits),
            "main_text": len(main_cits),
            "appendix_only": len(citations.get("appendix", []))
        },
        "thresholds": {
            "total_meets_min": len(all_cits) >= TOTAL_CITATIONS_MIN,
            "total_meets_target": len(all_cits) >= TOTAL_CITATIONS_TARGET,
            "main_text_meets_min": len(main_cits) >= MAIN_TEXT_CITATIONS_MIN,
            "main_text_meets_target": len(main_cits) >= MAIN_TEXT_CITATIONS_TARGET,
            "recent_meets_min": recent_percent >= RECENT_PAPERS_MIN_PERCENT
        },
        "recency": {
            "papers_with_year": len(years),
            "recent_count": recent_count,
            "recent_percent": round(recent_percent, 1)
        },
        "gaps": {
            "total_needed": max(0, TOTAL_CITATIONS_MIN - len(all_cits)),
            "main_text_needed": max(0, MAIN_TEXT_CITATIONS_MIN - len(main_cits))
        },
        "overall_valid": True
    }

    # Overall validity
    report["overall_valid"] = (
        report["thresholds"]["total_meets_min"] and
        report["thresholds"]["main_text_meets_min"]
    )

    return report


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: track_citations.py <hypotheses.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        hypothesis_set = json.load(f)

    citations = extract_citations_from_hypothesis_set(hypothesis_set)
    report = analyze_citations(citations)

    valid = report["overall_valid"]
    print(f"\n{'✓' if valid else '✗'} Citation Analysis")

    print(f"\n  Counts:")
    print(f"    Total: {report['counts']['total']} (min: {TOTAL_CITATIONS_MIN}, target: {TOTAL_CITATIONS_TARGET})")
    print(f"    Main text: {report['counts']['main_text']} (min: {MAIN_TEXT_CITATIONS_MIN}, target: {MAIN_TEXT_CITATIONS_TARGET})")
    print(f"    Appendix: {report['counts']['appendix_only']}")

    print(f"\n  Recency (last 5 years):")
    print(f"    {report['recency']['recent_count']}/{report['recency']['papers_with_year']} papers ({report['recency']['recent_percent']}%)")
    print(f"    Threshold: ≥{RECENT_PAPERS_MIN_PERCENT}% {'✓' if report['thresholds']['recent_meets_min'] else '✗'}")

    if report["gaps"]["total_needed"] > 0 or report["gaps"]["main_text_needed"] > 0:
        print(f"\n  Gaps:")
        if report["gaps"]["total_needed"] > 0:
            print(f"    ✗ Need {report['gaps']['total_needed']} more citations for minimum")
        if report["gaps"]["main_text_needed"] > 0:
            print(f"    ✗ Need {report['gaps']['main_text_needed']} more main text citations")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
```

---

## Phase 2: Quality Automation (P1)

### 2.1 Automated Quality Scorer

**File:** `scripts/score_hypothesis.py`

```python
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
        1 for p in predictions
        if p.get("falsification_criterion") and len(p.get("falsification_criterion", "")) > 20
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


def score_distinctiveness(hypothesis: dict, other_hypotheses: list[dict]) -> tuple[Optional[int], str]:
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


def assess_hypothesis(hypothesis: dict, all_hypotheses: list[dict]) -> QualityAssessment:
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
        scores["explanatory_power"] = hypothesis.get("quality_scores", {}).get("explanatory_power", 0)
        requires_review.append("explanatory_power")
    else:
        scores["explanatory_power"] = score
    notes.append(f"Explanatory Power: {note}")

    others = [h for h in all_hypotheses if h.get("id") != h_id]
    score, note = score_distinctiveness(hypothesis, others)
    if score is None:
        scores["distinctiveness"] = hypothesis.get("quality_scores", {}).get("distinctiveness", 0)
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
        notes=notes
    )


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

        status = "STRONG" if assessment.total >= 8 else ("viable" if assessment.total >= 5 else "WEAK")
        print(f"\n{assessment.hypothesis_id}: {assessment.total}/10 ({status})")
        print(f"  Automated: {', '.join(assessment.automated_scores)}")
        print(f"  Needs review: {', '.join(assessment.requires_review) if assessment.requires_review else 'none'}")
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
    if max(totals) < 8:
        print("\n⚠ WARNING: No hypothesis scores ≥8/10")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

### 2.2 Hypothesis Distinctiveness Checker

**File:** `scripts/check_distinctiveness.py`

```python
#!/usr/bin/env python3
"""Check that hypotheses are mechanistically distinct."""

import json
import sys
from itertools import combinations


def extract_mechanism_terms(hypothesis: dict) -> set[str]:
    """Extract key terms from hypothesis mechanism."""
    terms = set()

    mechanism = hypothesis.get("mechanism", {})

    # Add causal chain steps
    for step in mechanism.get("causal_chain", []):
        # Normalize: lowercase, split on common delimiters
        words = step.lower().replace(",", " ").replace("→", " ").split()
        terms.update(words)

    # Add trigger, pathway, outcome
    for field in ["trigger", "pathway", "outcome"]:
        if mechanism.get(field):
            words = mechanism[field].lower().split()
            terms.update(words)

    # Remove common stopwords
    stopwords = {"the", "a", "an", "and", "or", "to", "of", "in", "by", "is", "are", "that", "which"}
    terms -= stopwords

    return terms


def calculate_overlap(terms1: set[str], terms2: set[str]) -> float:
    """Calculate Jaccard similarity between term sets."""
    if not terms1 or not terms2:
        return 0.0
    intersection = len(terms1 & terms2)
    union = len(terms1 | terms2)
    return intersection / union if union > 0 else 0.0


def check_distinctiveness(hypotheses: list[dict], threshold: float = 0.4) -> dict:
    """
    Check pairwise distinctiveness of hypotheses.

    Args:
        hypotheses: List of hypothesis dictionaries
        threshold: Maximum allowed overlap (default 0.4 = 40%)

    Returns:
        Report dictionary with pairwise comparisons and overall status
    """
    report = {
        "hypothesis_count": len(hypotheses),
        "comparisons": [],
        "overall_distinct": True,
        "issues": []
    }

    # Extract terms for each hypothesis
    hypothesis_terms = {}
    for h in hypotheses:
        h_id = h.get("id", "?")
        hypothesis_terms[h_id] = extract_mechanism_terms(h)

    # Pairwise comparisons
    for (h1_id, terms1), (h2_id, terms2) in combinations(hypothesis_terms.items(), 2):
        overlap = calculate_overlap(terms1, terms2)
        shared = terms1 & terms2

        comparison = {
            "pair": f"{h1_id} vs {h2_id}",
            "overlap_ratio": round(overlap, 3),
            "shared_terms": list(shared)[:10],  # Limit for readability
            "is_distinct": overlap < threshold
        }
        report["comparisons"].append(comparison)

        if not comparison["is_distinct"]:
            report["overall_distinct"] = False
            report["issues"].append(
                f"{h1_id} and {h2_id} share {overlap:.0%} mechanism overlap "
                f"(threshold: {threshold:.0%}). Shared: {', '.join(list(shared)[:5])}"
            )

    return report


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: check_distinctiveness.py <hypotheses.json> [threshold]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4

    hypotheses = data.get("hypotheses", [])
    report = check_distinctiveness(hypotheses, threshold)

    status = "✓" if report["overall_distinct"] else "✗"
    print(f"\n{status} Distinctiveness Check (threshold: {threshold:.0%})")
    print(f"  Hypotheses: {report['hypothesis_count']}")
    print(f"  Comparisons: {len(report['comparisons'])}")

    print("\n  Pairwise Analysis:")
    for comp in report["comparisons"]:
        icon = "✓" if comp["is_distinct"] else "✗"
        print(f"    {icon} {comp['pair']}: {comp['overlap_ratio']:.0%} overlap")
        if comp["shared_terms"]:
            print(f"       Shared: {', '.join(comp['shared_terms'][:5])}")

    if report["issues"]:
        print("\n  Issues:")
        for issue in report["issues"]:
            print(f"    ✗ {issue}")

    sys.exit(0 if report["overall_distinct"] else 1)


if __name__ == "__main__":
    main()
```

---

## Phase 3: Workflow Validation (P2)

### 3.1 Stage Exit Validator

**File:** `scripts/validate_stage_exit.py`

```python
#!/usr/bin/env python3
"""Validate exit criteria for each workflow stage."""

import json
import sys
from dataclasses import dataclass
from typing import Callable


@dataclass
class ExitCriteria:
    """Exit criteria check result."""
    stage: int
    name: str
    criteria: list[tuple[str, bool, str]]  # (criterion, passed, note)

    @property
    def passed(self) -> bool:
        return all(c[1] for c in self.criteria)


def check_stage_1(data: dict) -> ExitCriteria:
    """Stage 1: Understand Phenomenon → Literature Search"""
    criteria = []

    # Core observation articulated
    phenomenon = data.get("phenomenon_description", "")
    criteria.append((
        "Core observation articulated",
        len(phenomenon) >= 50,
        f"Description: {len(phenomenon)} chars"
    ))

    # Scope defined
    levels = data.get("explanation_levels", [])
    criteria.append((
        "Scope and boundaries defined",
        len(levels) >= 1,
        f"Levels: {levels}"
    ))

    # Domain identified
    domain = data.get("domain", "")
    criteria.append((
        "Relevant domain identified",
        bool(domain),
        f"Domain: {domain}"
    ))

    # Search terms generated
    search_terms = data.get("search_terms", [])
    criteria.append((
        "Search terms generated (≥5)",
        len(search_terms) >= 5,
        f"Terms: {len(search_terms)}"
    ))

    return ExitCriteria(1, "Understand Phenomenon", criteria)


def check_stage_2(data: dict) -> ExitCriteria:
    """Stage 2: Literature Search → Synthesize Evidence"""
    criteria = []

    search_data = data.get("literature_search", {})

    # Databases searched
    databases = search_data.get("databases", [])
    criteria.append((
        "≥3 databases searched",
        len(databases) >= 3,
        f"Databases: {databases}"
    ))

    # Papers retrieved
    papers = search_data.get("papers_retrieved", 0)
    criteria.append((
        "≥40 papers retrieved",
        papers >= 40,
        f"Papers: {papers}"
    ))

    # Search saturation
    saturation = search_data.get("saturation_percent", 100)
    criteria.append((
        "<5% new papers in final iteration",
        saturation < 5,
        f"Saturation: {saturation}%"
    ))

    # Recent papers
    recent_percent = search_data.get("recent_percent", 0)
    criteria.append((
        "≥60% papers from last 5 years",
        recent_percent >= 60,
        f"Recent: {recent_percent}%"
    ))

    return ExitCriteria(2, "Literature Search", criteria)


def check_stage_4(data: dict) -> ExitCriteria:
    """Stage 4: Generate Hypotheses → Evaluate Quality"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # Hypothesis count
    criteria.append((
        "3-5 distinct hypotheses",
        3 <= len(hypotheses) <= 5,
        f"Count: {len(hypotheses)}"
    ))

    # Mechanistic explanations
    has_mechanism = sum(1 for h in hypotheses if h.get("mechanism", {}).get("causal_chain"))
    criteria.append((
        "Each has mechanistic explanation",
        has_mechanism == len(hypotheses),
        f"With mechanism: {has_mechanism}/{len(hypotheses)}"
    ))

    # Grounded in evidence
    has_evidence = sum(1 for h in hypotheses if len(h.get("supporting_evidence", [])) >= 3)
    criteria.append((
        "Each grounded in evidence",
        has_evidence == len(hypotheses),
        f"With ≥3 citations: {has_evidence}/{len(hypotheses)}"
    ))

    return ExitCriteria(4, "Generate Hypotheses", criteria)


def check_stage_5(data: dict) -> ExitCriteria:
    """Stage 5: Evaluate Quality → Design Experiments"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # All scored
    scored = sum(1 for h in hypotheses if "quality_scores" in h)
    criteria.append((
        "All hypotheses scored",
        scored == len(hypotheses),
        f"Scored: {scored}/{len(hypotheses)}"
    ))

    # Quality thresholds
    scores = []
    for h in hypotheses:
        qs = h.get("quality_scores", {})
        total = sum(qs.get(c, 0) for c in
                   ["testability", "falsifiability", "parsimony",
                    "explanatory_power", "distinctiveness"])
        scores.append(total)

    if scores:
        criteria.append((
            "≥1 hypothesis scores ≥8/10",
            max(scores) >= 8,
            f"Max score: {max(scores)}"
        ))

        criteria.append((
            "All hypotheses ≥5/10 or deprioritized",
            min(scores) >= 5,
            f"Min score: {min(scores)}"
        ))

    return ExitCriteria(5, "Evaluate Quality", criteria)


def check_stage_7(data: dict) -> ExitCriteria:
    """Stage 7: Formulate Predictions → Present Output"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # Predictions per hypothesis
    with_predictions = sum(
        1 for h in hypotheses
        if len(h.get("predictions", [])) >= 2
    )
    criteria.append((
        "≥2 predictions per hypothesis",
        with_predictions == len(hypotheses),
        f"With ≥2 predictions: {with_predictions}/{len(hypotheses)}"
    ))

    # Falsification criteria
    all_predictions = [p for h in hypotheses for p in h.get("predictions", [])]
    with_falsification = sum(1 for p in all_predictions if p.get("falsification_criterion"))
    criteria.append((
        "Falsifying observations defined",
        with_falsification >= len(hypotheses) * 2,
        f"With falsification: {with_falsification}"
    ))

    return ExitCriteria(7, "Formulate Predictions", criteria)


STAGE_VALIDATORS = {
    1: check_stage_1,
    2: check_stage_2,
    4: check_stage_4,
    5: check_stage_5,
    7: check_stage_7,
}


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: validate_stage_exit.py <stage_number> <data.json>")
        print(f"Available stages: {list(STAGE_VALIDATORS.keys())}")
        sys.exit(1)

    stage = int(sys.argv[1])
    with open(sys.argv[2]) as f:
        data = json.load(f)

    if stage not in STAGE_VALIDATORS:
        print(f"No validator for stage {stage}")
        sys.exit(1)

    result = STAGE_VALIDATORS[stage](data)

    status = "✓ PASS" if result.passed else "✗ FAIL"
    print(f"\n{status}: Stage {result.stage} - {result.name}")

    print("\n  Exit Criteria:")
    for criterion, passed, note in result.criteria:
        icon = "✓" if passed else "✗"
        print(f"    {icon} {criterion}")
        print(f"       {note}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
```

### 3.2 LaTeX Preflight Checker

**File:** `scripts/latex_preflight.py`

```python
#!/usr/bin/env python3
"""
Pre-flight check for LaTeX hypothesis reports.

Validates document structure before compilation to catch common issues.
"""

import re
import sys
from pathlib import Path


# Required components
REQUIRED_ENVIRONMENTS = [
    "summarybox",
    "hypothesisbox",  # Any of hypothesisbox1-5
    "predictionbox",
    "comparisonbox"
]

REQUIRED_SECTIONS = [
    r"\\section\*?\{.*Executive Summary.*\}",
    r"\\section\*?\{.*Competing Hypotheses.*\}",
    r"\\section\*?\{.*Testable Predictions.*\}",
    r"\\section\*?\{.*Critical Comparisons.*\}",
]

REQUIRED_APPENDICES = [
    "Appendix A",
    "Appendix B",
    "Appendix C"
]


def check_latex_structure(content: str) -> dict:
    """
    Check LaTeX document structure.

    Returns:
        Report dictionary with findings
    """
    report = {
        "environments": {},
        "sections": {},
        "appendices": {},
        "citations": {},
        "warnings": [],
        "errors": [],
        "overall_valid": True
    }

    # Check for required environments
    for env in REQUIRED_ENVIRONMENTS:
        pattern = rf"\\begin\{{{env}"
        matches = re.findall(pattern, content)
        count = len(matches)
        report["environments"][env] = count

        if count == 0:
            if env == "hypothesisbox":
                # Check for numbered variants
                numbered = sum(len(re.findall(rf"\\begin\{{hypothesisbox{i}\}}", content))
                              for i in range(1, 6))
                if numbered == 0:
                    report["errors"].append(f"No hypothesis boxes found")
                    report["overall_valid"] = False
                else:
                    report["environments"]["hypothesisbox"] = numbered
            else:
                report["errors"].append(f"Missing {env} environment")
                report["overall_valid"] = False

    # Check hypothesis count
    hyp_count = sum(len(re.findall(rf"\\begin\{{hypothesisbox{i}\}}", content))
                   for i in range(1, 6))
    if hyp_count < 3:
        report["errors"].append(f"Only {hyp_count} hypothesis boxes (need ≥3)")
        report["overall_valid"] = False
    elif hyp_count > 5:
        report["warnings"].append(f"{hyp_count} hypothesis boxes (expected 3-5)")

    # Check for required sections
    for pattern in REQUIRED_SECTIONS:
        match = re.search(pattern, content, re.IGNORECASE)
        section_name = pattern.split(".*")[1].split(".*")[0] if ".*" in pattern else pattern
        report["sections"][section_name] = bool(match)
        if not match:
            report["errors"].append(f"Missing section: {section_name}")
            report["overall_valid"] = False

    # Check for appendices
    for appendix in REQUIRED_APPENDICES:
        found = appendix in content
        report["appendices"][appendix] = found
        if not found:
            report["warnings"].append(f"Missing {appendix}")

    # Count citations
    citep_count = len(re.findall(r"\\citep?\{[^}]+\}", content))
    report["citations"]["count"] = citep_count
    if citep_count < 10:
        report["warnings"].append(f"Only {citep_count} citations (recommend ≥40 total)")

    # Check for bibliography
    has_bib = bool(re.search(r"\\bibliography\{", content) or
                   re.search(r"\\begin\{thebibliography\}", content))
    report["citations"]["has_bibliography"] = has_bib
    if not has_bib:
        report["errors"].append("No bibliography found")
        report["overall_valid"] = False

    # Check for page breaks before hypothesis boxes (overflow prevention)
    hyp_box_pattern = r"\\begin\{hypothesisbox[1-5]\}"
    newpage_pattern = r"\\newpage"

    hyp_positions = [m.start() for m in re.finditer(hyp_box_pattern, content)]
    newpage_positions = [m.start() for m in re.finditer(newpage_pattern, content)]

    missing_pagebreaks = 0
    for pos in hyp_positions:
        # Check if there's a \newpage within 200 chars before the box
        nearby_newpages = [np for np in newpage_positions if pos - 200 < np < pos]
        if not nearby_newpages:
            missing_pagebreaks += 1

    if missing_pagebreaks > 0:
        report["warnings"].append(
            f"{missing_pagebreaks} hypothesis boxes without preceding \\newpage (overflow risk)"
        )

    return report


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: latex_preflight.py <document.tex>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    content = filepath.read_text()
    report = check_latex_structure(content)

    status = "✓ PASS" if report["overall_valid"] else "✗ FAIL"
    print(f"\n{status}: LaTeX Preflight Check")
    print(f"  File: {filepath.name}")

    print("\n  Environments:")
    for env, count in report["environments"].items():
        icon = "✓" if count > 0 else "✗"
        print(f"    {icon} {env}: {count}")

    print("\n  Sections:")
    for section, found in report["sections"].items():
        icon = "✓" if found else "✗"
        print(f"    {icon} {section}")

    print("\n  Appendices:")
    for appendix, found in report["appendices"].items():
        icon = "✓" if found else "⚠"
        print(f"    {icon} {appendix}")

    print(f"\n  Citations: {report['citations']['count']}")
    print(f"  Bibliography: {'✓' if report['citations']['has_bibliography'] else '✗'}")

    if report["warnings"]:
        print("\n  Warnings:")
        for w in report["warnings"]:
            print(f"    ⚠ {w}")

    if report["errors"]:
        print("\n  Errors:")
        for e in report["errors"]:
            print(f"    ✗ {e}")

    sys.exit(0 if report["overall_valid"] else 1)


if __name__ == "__main__":
    main()
```

---

## Priority Matrix

| Script | Priority | Impact | Effort | Dependencies |
|--------|----------|--------|--------|--------------|
| `validate_input.py` | P0 | HIGH | LOW | None |
| `validate_hypothesis.py` | P0 | HIGH | MEDIUM | None |
| `track_citations.py` | P0 | MEDIUM | LOW | None |
| `score_hypothesis.py` | P1 | HIGH | MEDIUM | validate_hypothesis.py |
| `check_distinctiveness.py` | P1 | MEDIUM | LOW | None |
| `validate_stage_exit.py` | P2 | MEDIUM | MEDIUM | All above |
| `latex_preflight.py` | P2 | MEDIUM | LOW | None |

---

## Success Metrics

| Metric | Current | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|---------|
| Input validation coverage | ~30% | 85% | 85% | 85% |
| Hypothesis structure validation | ~50% | 95% | 95% | 95% |
| Quality score automation | 0% | 0% | 60% | 60% |
| Citation tracking | ~20% | 95% | 95% | 95% |
| Distinctiveness validation | 0% | 0% | 80% | 80% |
| Stage exit validation | ~50% | 50% | 75% | 90% |
| LaTeX preflight | 0% | 0% | 0% | 85% |
| **Overall determinism** | **55-60%** | **70%** | **80%** | **85%** |

---

## Workflow Integration

Add to `SKILL.md` workflow stages:

```markdown
### Stage 4 → 5 Transition Validation

Before proceeding from Generate Hypotheses to Evaluate Quality:

1. Run `python scripts/validate_hypothesis.py --input hypotheses.json`
   - Must show: ✓ All hypotheses have mechanism, evidence, assumptions

2. Run `python scripts/check_distinctiveness.py --input hypotheses.json`
   - Must show: All pairwise overlap_ratio < 0.4

Exit criteria validated. Proceeding to Stage 5.

### Stage 7 → 8 Transition Validation

Before proceeding from Formulate Predictions to Present Output:

1. Run `python scripts/track_citations.py --input hypotheses.json`
   - Must show: ✓ Total ≥40, Main text ≥10, Recent ≥60%

2. Run `python scripts/score_hypothesis.py --input hypotheses.json`
   - Must show: ≥1 hypothesis scoring ≥8/10

Exit criteria validated. Proceeding to Stage 8.

### Stage 8 Completion Validation

Before marking report complete:

1. Run `python scripts/latex_preflight.py --input hypothesis_report.tex`
   - Must show: ✓ All required environments, sections, bibliography

Report validated. Ready for compilation.
```

---

## Calibration Examples

### Strong Hypothesis (Score ≥8/10)

```json
{
  "id": "H1",
  "title": "AMPK-mediated autophagy drives metabolic adaptation",
  "mechanism": {
    "trigger": "Cellular energy stress (high AMP:ATP ratio)",
    "pathway": "AMPK → ULK1 phosphorylation → autophagy initiation",
    "outcome": "Enhanced metabolic flexibility and survival",
    "causal_chain": [
      "Energy depletion increases AMP:ATP ratio",
      "AMPK activated by AMP binding and LKB1 phosphorylation",
      "Activated AMPK phosphorylates ULK1 at Ser317/Ser777",
      "ULK1 complex translocates to ER-mitochondria contact sites",
      "Autophagosome formation initiated",
      "Selective degradation of damaged organelles"
    ]
  },
  "predictions": [
    {
      "statement": "AMPK inhibition will prevent autophagy induction during starvation",
      "condition": "Glucose deprivation for 4-8 hours",
      "expected_outcome": ">70% reduction in LC3-II accumulation",
      "magnitude": "70-90% reduction vs control",
      "falsification_criterion": "If LC3-II increases by >20% despite AMPK inhibition"
    },
    {
      "statement": "ULK1 phosphomutant will block AMPK-mediated autophagy",
      "condition": "ULK1-S317A/S777A knockin cells under starvation",
      "expected_outcome": "Autophagy flux reduced to baseline levels",
      "magnitude": "Similar to AMPK-null phenotype",
      "falsification_criterion": "If autophagy proceeds normally in phosphomutant cells"
    }
  ],
  "quality_scores": {
    "testability": 2,
    "falsifiability": 2,
    "parsimony": 1,
    "explanatory_power": 2,
    "distinctiveness": 2
  }
}
```

**Why this scores 9/10:**
- Clear 6-step mechanism with intermediate steps
- Quantitative predictions (>70% reduction)
- Explicit falsification criteria
- Well-established pathway (parsimony: 1 due to known complexity)
- Makes testable predictions distinct from alternatives

### Weak Hypothesis (Score <5/10)

```json
{
  "id": "H3",
  "title": "Multiple factors contribute to the phenotype",
  "mechanism": {
    "trigger": "Various cellular stresses",
    "pathway": "Complex interactions between pathways",
    "outcome": "Phenotypic changes",
    "causal_chain": ["Stress occurs", "Pathways activated", "Phenotype emerges"]
  },
  "predictions": [
    {
      "statement": "The phenotype may be affected by pathway perturbation",
      "condition": "Under certain conditions",
      "expected_outcome": "Some change in phenotype",
      "magnitude": null,
      "falsification_criterion": null
    }
  ],
  "quality_scores": {
    "testability": 0,
    "falsifiability": 0,
    "parsimony": 1,
    "explanatory_power": 1,
    "distinctiveness": 0
  }
}
```

**Why this scores 2/10:**
- Vague mechanism ("complex interactions")
- No specific predictions
- No falsification criteria
- Not distinguishable from alternatives
- Explains nothing concrete

---

## Detection Patterns (Appendix)

### Domain Classification Keywords

```python
DOMAIN_KEYWORDS = {
    "biomedical": ["protein", "gene", "cell", "patient", "disease", "receptor",
                   "pathway", "expression", "mutation", "clinical"],
    "chemistry": ["reaction", "catalyst", "synthesis", "molecule", "compound",
                  "bond", "oxidation", "reduction", "yield"],
    "physics": ["energy", "force", "field", "quantum", "particle", "wave",
                "momentum", "entropy", "temperature"],
    "ecology": ["population", "species", "ecosystem", "habitat", "biodiversity",
                "community", "niche", "competition"],
    "neuroscience": ["neuron", "brain", "cognitive", "synapse", "cortex",
                     "dopamine", "behavior", "memory"]
}
```

### Prediction Completeness Indicators

```python
STRONG_PREDICTION_MARKERS = [
    r"\d+%",  # Percentage
    r"[<>≥≤]\s*\d+",  # Inequality with number
    r"\d+-fold",  # Fold change
    r"within \d+ (hours|days|weeks)",  # Timeframe
    r"(increase|decrease|reduce|enhance) by",  # Direction + magnitude
]

WEAK_PREDICTION_MARKERS = [
    r"\bmay\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bpossibly\b",
    r"\bsome\b change",
    r"\baffect\b",  # Without direction
]
```

---

## Testing Plan

### Unit Tests

```python
# tests/test_validate_hypothesis.py

def test_valid_hypothesis_passes():
    """Complete hypothesis should validate."""
    h = create_complete_hypothesis()
    is_valid, errors = validate_hypothesis(h)
    assert is_valid
    assert len(errors) == 0

def test_missing_mechanism_fails():
    """Hypothesis without mechanism should fail."""
    h = create_complete_hypothesis()
    del h["mechanism"]
    is_valid, errors = validate_hypothesis(h)
    assert not is_valid
    assert "Missing mechanism" in errors

def test_insufficient_evidence_fails():
    """Hypothesis with <3 citations should fail."""
    h = create_complete_hypothesis()
    h["supporting_evidence"] = h["supporting_evidence"][:2]
    is_valid, errors = validate_hypothesis(h)
    assert not is_valid
    assert any("evidence" in e.lower() for e in errors)
```

### Integration Tests

```python
# tests/test_workflow_integration.py

def test_stage_5_exit_requires_scores():
    """Stage 5 exit should fail without quality scores."""
    data = create_hypotheses_without_scores()
    result = check_stage_5(data)
    assert not result.passed

def test_full_workflow_validation():
    """Complete workflow should pass all validators."""
    data = create_complete_hypothesis_set()

    assert check_stage_4(data).passed
    assert check_stage_5(data).passed
    assert check_stage_7(data).passed
```

---

## Changelog

- **v1.0.0** (2026-01-08): Initial determinism audit
  - Identified 55-60% current determinism
  - Proposed 3-phase implementation plan
  - Created 7 validation scripts
  - Added calibration examples for quality scoring
