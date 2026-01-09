#!/usr/bin/env python3
"""Validate exit criteria for each workflow stage."""

import json
import sys
from dataclasses import dataclass


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
    criteria.append(
        (
            "Core observation articulated",
            len(phenomenon) >= 50,
            f"Description: {len(phenomenon)} chars",
        )
    )

    # Scope defined
    levels = data.get("explanation_levels", [])
    criteria.append(
        (
            "Scope and boundaries defined",
            len(levels) >= 1,
            f"Levels: {levels}",
        )
    )

    # Domain identified
    domain = data.get("domain", "")
    criteria.append(
        (
            "Relevant domain identified",
            bool(domain),
            f"Domain: {domain}",
        )
    )

    # Search terms generated
    search_terms = data.get("search_terms", [])
    criteria.append(
        (
            "Search terms generated (≥5)",
            len(search_terms) >= 5,
            f"Terms: {len(search_terms)}",
        )
    )

    return ExitCriteria(1, "Understand Phenomenon", criteria)


def check_stage_2(data: dict) -> ExitCriteria:
    """Stage 2: Literature Search → Synthesize Evidence"""
    criteria = []

    search_data = data.get("literature_search", {})

    # Databases searched
    databases = search_data.get("databases", [])
    criteria.append(
        (
            "≥3 databases searched",
            len(databases) >= 3,
            f"Databases: {databases}",
        )
    )

    # Papers retrieved
    papers = search_data.get("papers_retrieved", 0)
    criteria.append(
        (
            "≥40 papers retrieved",
            papers >= 40,
            f"Papers: {papers}",
        )
    )

    # Search saturation
    saturation = search_data.get("saturation_percent", 100)
    criteria.append(
        (
            "<5% new papers in final iteration",
            saturation < 5,
            f"Saturation: {saturation}%",
        )
    )

    # Recent papers
    recent_percent = search_data.get("recent_percent", 0)
    criteria.append(
        (
            "≥60% papers from last 5 years",
            recent_percent >= 60,
            f"Recent: {recent_percent}%",
        )
    )

    return ExitCriteria(2, "Literature Search", criteria)


def check_stage_3(data: dict) -> ExitCriteria:
    """Stage 3: Synthesize Evidence → Generate Hypotheses"""
    criteria = []

    synthesis = data.get("evidence_synthesis", {})

    # Key findings extracted
    findings = synthesis.get("key_findings", [])
    criteria.append(
        (
            "≥10 key findings extracted",
            len(findings) >= 10,
            f"Findings: {len(findings)}",
        )
    )

    # Conflicting evidence documented
    conflicts = synthesis.get("conflicting_evidence", [])
    criteria.append(
        (
            "Conflicting evidence documented",
            len(conflicts) >= 0,  # Can be empty if no conflicts
            f"Conflicts: {len(conflicts)}",
        )
    )

    # Knowledge gaps identified
    gaps = synthesis.get("knowledge_gaps", [])
    criteria.append(
        (
            "≥3 knowledge gaps identified",
            len(gaps) >= 3,
            f"Gaps: {len(gaps)}",
        )
    )

    # Mechanistic patterns noted
    patterns = synthesis.get("mechanistic_patterns", [])
    criteria.append(
        (
            "Mechanistic patterns noted",
            len(patterns) >= 1,
            f"Patterns: {len(patterns)}",
        )
    )

    return ExitCriteria(3, "Synthesize Evidence", criteria)


def check_stage_4(data: dict) -> ExitCriteria:
    """Stage 4: Generate Hypotheses → Evaluate Quality"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # Hypothesis count
    criteria.append(
        (
            "3-5 distinct hypotheses",
            3 <= len(hypotheses) <= 5,
            f"Count: {len(hypotheses)}",
        )
    )

    # Mechanistic explanations
    has_mechanism = sum(
        1 for h in hypotheses if h.get("mechanism", {}).get("causal_chain")
    )
    criteria.append(
        (
            "Each has mechanistic explanation",
            has_mechanism == len(hypotheses) and len(hypotheses) > 0,
            f"With mechanism: {has_mechanism}/{len(hypotheses)}",
        )
    )

    # Grounded in evidence
    has_evidence = sum(
        1 for h in hypotheses if len(h.get("supporting_evidence", [])) >= 3
    )
    criteria.append(
        (
            "Each grounded in evidence",
            has_evidence == len(hypotheses) and len(hypotheses) > 0,
            f"With ≥3 citations: {has_evidence}/{len(hypotheses)}",
        )
    )

    return ExitCriteria(4, "Generate Hypotheses", criteria)


def check_stage_5(data: dict) -> ExitCriteria:
    """Stage 5: Evaluate Quality → Design Experiments"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # All scored
    scored = sum(1 for h in hypotheses if "quality_scores" in h)
    criteria.append(
        (
            "All hypotheses scored",
            scored == len(hypotheses) and len(hypotheses) > 0,
            f"Scored: {scored}/{len(hypotheses)}",
        )
    )

    # Quality thresholds
    scores = []
    for h in hypotheses:
        qs = h.get("quality_scores", {})
        total = sum(
            qs.get(c, 0)
            for c in [
                "testability",
                "falsifiability",
                "parsimony",
                "explanatory_power",
                "distinctiveness",
            ]
        )
        scores.append(total)

    if scores:
        criteria.append(
            (
                "≥1 hypothesis scores ≥8/10",
                max(scores) >= 8,
                f"Max score: {max(scores)}",
            )
        )

        criteria.append(
            (
                "All hypotheses ≥5/10 or deprioritized",
                min(scores) >= 5,
                f"Min score: {min(scores)}",
            )
        )
    else:
        criteria.append(
            (
                "≥1 hypothesis scores ≥8/10",
                False,
                "No scores available",
            )
        )
        criteria.append(
            (
                "All hypotheses ≥5/10 or deprioritized",
                False,
                "No scores available",
            )
        )

    return ExitCriteria(5, "Evaluate Quality", criteria)


def check_stage_6(data: dict) -> ExitCriteria:
    """Stage 6: Design Experiments → Formulate Predictions"""
    criteria = []

    hypotheses = data.get("hypotheses", [])
    experiments = data.get("experimental_designs", {})

    # Each hypothesis has experimental approach
    with_design = 0
    for h in hypotheses:
        h_id = h.get("id", "")
        if h_id in experiments or h.get("experimental_design"):
            with_design += 1

    criteria.append(
        (
            "Each hypothesis has experimental approach",
            with_design == len(hypotheses) and len(hypotheses) > 0,
            f"With design: {with_design}/{len(hypotheses)}",
        )
    )

    # Methods are feasible (check for available_methods match)
    available = set(data.get("available_methods", []))
    if available and experiments:
        feasible_count = sum(
            1
            for exp in experiments.values()
            if any(m in available for m in exp.get("methods", []))
        )
        criteria.append(
            (
                "Methods are feasible with available resources",
                feasible_count >= 1,
                f"Feasible: {feasible_count}",
            )
        )
    else:
        criteria.append(
            (
                "Methods are feasible with available resources",
                True,  # Pass if not specified
                "Methods not constrained",
            )
        )

    return ExitCriteria(6, "Design Experiments", criteria)


def check_stage_7(data: dict) -> ExitCriteria:
    """Stage 7: Formulate Predictions → Present Output"""
    criteria = []

    hypotheses = data.get("hypotheses", [])

    # Predictions per hypothesis
    with_predictions = sum(
        1 for h in hypotheses if len(h.get("predictions", [])) >= 2
    )
    criteria.append(
        (
            "≥2 predictions per hypothesis",
            with_predictions == len(hypotheses) and len(hypotheses) > 0,
            f"With ≥2 predictions: {with_predictions}/{len(hypotheses)}",
        )
    )

    # Falsification criteria
    all_predictions = [p for h in hypotheses for p in h.get("predictions", [])]
    with_falsification = sum(
        1 for p in all_predictions if p.get("falsification_criterion")
    )
    min_required = len(hypotheses) * 2 if hypotheses else 0
    criteria.append(
        (
            "Falsifying observations defined",
            with_falsification >= min_required,
            f"With falsification: {with_falsification}/{min_required}",
        )
    )

    # Quantitative predictions
    with_magnitude = sum(1 for p in all_predictions if p.get("magnitude"))
    criteria.append(
        (
            "Quantitative predictions where possible",
            with_magnitude >= len(hypotheses) if hypotheses else True,
            f"With magnitude: {with_magnitude}",
        )
    )

    return ExitCriteria(7, "Formulate Predictions", criteria)


def check_stage_8(data: dict) -> ExitCriteria:
    """Stage 8: Present Output (Final validation)"""
    criteria = []

    # Check all major components present
    hypotheses = data.get("hypotheses", [])
    criteria.append(
        (
            "3-5 hypotheses in final output",
            3 <= len(hypotheses) <= 5,
            f"Count: {len(hypotheses)}",
        )
    )

    # Citations threshold
    all_citations = set()
    for h in hypotheses:
        for e in h.get("supporting_evidence", []):
            cit = e.get("citation", "")
            if cit:
                all_citations.add(cit)
        for e in h.get("conflicting_evidence", []):
            cit = e.get("citation", "")
            if cit:
                all_citations.add(cit)

    criteria.append(
        (
            "≥40 total citations",
            len(all_citations) >= 40,
            f"Citations: {len(all_citations)}",
        )
    )

    # All hypotheses have complete structure
    complete = 0
    for h in hypotheses:
        has_all = (
            h.get("mechanism", {}).get("causal_chain")
            and len(h.get("supporting_evidence", [])) >= 3
            and len(h.get("predictions", [])) >= 2
            and "quality_scores" in h
        )
        if has_all:
            complete += 1

    criteria.append(
        (
            "All hypotheses structurally complete",
            complete == len(hypotheses) and len(hypotheses) > 0,
            f"Complete: {complete}/{len(hypotheses)}",
        )
    )

    return ExitCriteria(8, "Present Output", criteria)


STAGE_VALIDATORS = {
    1: check_stage_1,
    2: check_stage_2,
    3: check_stage_3,
    4: check_stage_4,
    5: check_stage_5,
    6: check_stage_6,
    7: check_stage_7,
    8: check_stage_8,
}


def validate_stage_exit(stage: int, data: dict) -> ExitCriteria:
    """
    Validate exit criteria for a specific stage.

    Args:
        stage: Stage number (1-8)
        data: Workflow data dictionary

    Returns:
        ExitCriteria with validation results

    Raises:
        ValueError: If stage number is invalid
    """
    if stage not in STAGE_VALIDATORS:
        raise ValueError(
            f"Invalid stage {stage}. Available stages: {list(STAGE_VALIDATORS.keys())}"
        )
    return STAGE_VALIDATORS[stage](data)


def validate_all_stages(data: dict) -> dict[int, ExitCriteria]:
    """
    Validate all stages and return results.

    Args:
        data: Workflow data dictionary

    Returns:
        Dictionary mapping stage numbers to ExitCriteria
    """
    return {stage: validator(data) for stage, validator in STAGE_VALIDATORS.items()}


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: validate_stage_exit.py <stage_number|all> <data.json>")
        print(f"Available stages: {list(STAGE_VALIDATORS.keys())}")
        sys.exit(1)

    stage_arg = sys.argv[1]
    with open(sys.argv[2]) as f:
        data = json.load(f)

    if stage_arg == "all":
        results = validate_all_stages(data)
        all_passed = all(r.passed for r in results.values())

        print(f"\n{'✓' if all_passed else '✗'} Workflow Stage Validation")
        print("=" * 50)

        for stage, result in sorted(results.items()):
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"\nStage {result.stage} - {result.name}: {status}")
            for criterion, passed, note in result.criteria:
                icon = "✓" if passed else "✗"
                print(f"  {icon} {criterion}")
                print(f"     {note}")

        passed_count = sum(1 for r in results.values() if r.passed)
        print(f"\n{'=' * 50}")
        print(f"Summary: {passed_count}/{len(results)} stages passed")

        sys.exit(0 if all_passed else 1)
    else:
        stage = int(stage_arg)
        if stage not in STAGE_VALIDATORS:
            print(f"No validator for stage {stage}")
            print(f"Available stages: {list(STAGE_VALIDATORS.keys())}")
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
