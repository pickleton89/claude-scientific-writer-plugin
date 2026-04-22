#!/usr/bin/env python3
"""
Test suite for deterministic skill routing.

Validates that the router produces expected results for canonical test cases.

Usage:
    # Run all tests
    uv run python -m pytest skills/skill-router/tests/test_routing.py -v

    # Run with coverage
    uv run python -m pytest skills/skill-router/tests/test_routing.py --cov=skills.skill_router

    # Run specific test category
    uv run python -m pytest skills/skill-router/tests/test_routing.py -k "plotting"

    # Run standalone (without pytest)
    uv run python skills/skill-router/tests/test_routing.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

# Add parent to path for imports
skill_router_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skill_router_dir))

from route import SkillRouter, route_request  # noqa: E402


@dataclass
class TestResult:
    """Result of a single test case."""

    request: str
    expected_skill: str
    actual_skill: str
    expected_confidence: float
    actual_confidence: float
    passed: bool
    failure_reason: Optional[str] = None


def load_test_cases() -> dict:
    """Load canonical test cases from YAML."""
    test_file = Path(__file__).parent / "canonical_routes.yaml"
    with open(test_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_test_case(
    case: dict,
    router: SkillRouter,
    check_max_confidence: bool = False
) -> TestResult:
    """Run a single test case and return result."""
    request = case["request"]
    expected_skill = case["expected_skill"]
    min_confidence = case.get("min_confidence", 0.5)
    max_confidence = case.get("max_confidence")
    not_expected = case.get("not_expected")

    result = router.route(request)

    # Check skill match
    skill_match = result.primary_skill == expected_skill

    # Check confidence threshold
    if check_max_confidence and max_confidence:
        confidence_ok = result.confidence <= max_confidence
    else:
        confidence_ok = result.confidence >= min_confidence

    # Check negative constraint
    negative_ok = True
    if not_expected:
        negative_ok = result.primary_skill != not_expected

    passed = skill_match and confidence_ok and negative_ok

    # Build failure reason
    failure_reason = None
    if not passed:
        reasons = []
        if not skill_match:
            reasons.append(f"Expected {expected_skill}, got {result.primary_skill}")
        if not confidence_ok:
            if check_max_confidence and max_confidence:
                reasons.append(
                    f"Confidence {result.confidence:.2f} > max {max_confidence}"
                )
            else:
                reasons.append(
                    f"Confidence {result.confidence:.2f} < min {min_confidence}"
                )
        if not negative_ok:
            reasons.append(f"Should NOT have routed to {not_expected}")
        failure_reason = "; ".join(reasons)

    return TestResult(
        request=request,
        expected_skill=expected_skill,
        actual_skill=result.primary_skill,
        expected_confidence=min_confidence,
        actual_confidence=result.confidence,
        passed=passed,
        failure_reason=failure_reason,
    )


def run_category_tests(
    category_cases: list[dict],
    router: SkillRouter,
    check_max_confidence: bool = False
) -> tuple[int, int, list[TestResult]]:
    """Run all tests in a category.

    Returns:
        Tuple of (passed_count, total_count, failed_results)
    """
    passed = 0
    total = 0
    failures = []

    for case in category_cases:
        result = run_test_case(case, router, check_max_confidence)
        total += 1
        if result.passed:
            passed += 1
        else:
            failures.append(result)

    return passed, total, failures


def run_all_tests(verbose: bool = True) -> tuple[int, int, dict[str, list[TestResult]]]:
    """Run all canonical routing tests.

    Returns:
        Tuple of (total_passed, total_tests, failures_by_category)
    """
    test_cases = load_test_cases()
    router = SkillRouter()

    total_passed = 0
    total_tests = 0
    all_failures: dict[str, list[TestResult]] = {}

    # Standard test categories
    standard_categories = [
        "plotting_libraries_cases",
        "scientific_schematics_cases",
        "paperbanana_cases",
        "generate_image_cases",
        "scientific_writing_cases",
        "executive_summary_cases",
        "scientific_slides_cases",
        "research_posters_cases",
        "deep_research_cases",
        "citation_management_cases",
        "peer_review_cases",
        "statistical_analysis_cases",
        "reproducible_research_cases",
        "code_documentation_cases",
        "markitdown_cases",
        "oligon_brand_cases",
        "document_skills_cases",
        "entity_resolution_cases",
        "target_intelligence_cases",
        "drug_intelligence_cases",
        "target_validation_cases",
        "data_enriched_cases",
        "research_paper_summarizer_cases",
        "paper_2_web_cases",
        "venue_templates_cases",
        "design_foundation_cases",
        "markdown_to_pdf_cases",
    ]

    for category in standard_categories:
        if category not in test_cases:
            continue

        cases = test_cases[category]
        passed, total, failures = run_category_tests(cases, router)
        total_passed += passed
        total_tests += total

        if failures:
            all_failures[category] = failures

        if verbose:
            status = "PASS" if not failures else "FAIL"
            print(f"  {category}: {passed}/{total} [{status}]")

    # Ambiguous cases (check max confidence)
    if "ambiguous_cases" in test_cases:
        cases = test_cases["ambiguous_cases"]
        passed, total, failures = run_category_tests(
            cases, router, check_max_confidence=True
        )
        total_passed += passed
        total_tests += total
        if failures:
            all_failures["ambiguous_cases"] = failures
        if verbose:
            status = "PASS" if not failures else "FAIL"
            print(f"  ambiguous_cases: {passed}/{total} [{status}]")

    # Negative cases
    if "negative_cases" in test_cases:
        cases = test_cases["negative_cases"]
        passed, total, failures = run_category_tests(cases, router)
        total_passed += passed
        total_tests += total
        if failures:
            all_failures["negative_cases"] = failures
        if verbose:
            status = "PASS" if not failures else "FAIL"
            print(f"  negative_cases: {passed}/{total} [{status}]")

    return total_passed, total_tests, all_failures


def print_failures(failures: dict[str, list[TestResult]]) -> None:
    """Print detailed failure information."""
    if not failures:
        return

    print("\n" + "=" * 60)
    print("FAILURES")
    print("=" * 60)

    for category, results in failures.items():
        print(f"\n{category}:")
        for result in results:
            print(f"  Request: {result.request}")
            print(f"    Expected: {result.expected_skill} (conf >= {result.expected_confidence})")
            print(f"    Got: {result.actual_skill} (conf = {result.actual_confidence:.2f})")
            print(f"    Reason: {result.failure_reason}")


def generate_report(
    passed: int,
    total: int,
    failures: dict[str, list[TestResult]]
) -> str:
    """Generate a markdown test report."""
    pass_rate = (passed / total * 100) if total > 0 else 0
    status = "PASSING" if pass_rate >= 90 else "NEEDS ATTENTION"

    report = f"""# Skill Router Test Report

**Status:** {status}
**Pass Rate:** {passed}/{total} ({pass_rate:.1f}%)
**Date:** Generated by test suite

## Summary

| Category | Status |
|----------|--------|
"""
    # Add category summaries
    test_cases = load_test_cases()
    for category in test_cases:
        if category.endswith("_cases"):
            failed = category in failures
            status_emoji = "FAIL" if failed else "PASS"
            report += f"| {category} | {status_emoji} |\n"

    if failures:
        report += "\n## Failures\n\n"
        for category, results in failures.items():
            report += f"### {category}\n\n"
            for result in results:
                report += f"- **Request:** {result.request}\n"
                report += f"  - Expected: `{result.expected_skill}`\n"
                report += f"  - Got: `{result.actual_skill}` (confidence: {result.actual_confidence:.2f})\n"
                report += f"  - Reason: {result.failure_reason}\n\n"

    return report


# ============================================================
# Pytest-compatible test functions
# ============================================================

def test_plotting_libraries_routing():
    """Test routing for data visualization requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("plotting_libraries_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_scientific_schematics_routing():
    """Test routing for diagram/schematic requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("scientific_schematics_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"


def test_paperbanana_routing():
    """Test routing for text-to-visual requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("paperbanana_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_scientific_writing_routing():
    """Test routing for manuscript/paper writing requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("scientific_writing_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"


def test_deep_research_routing():
    """Test routing for deep-research requests (paper search, lit review, hypothesis, etc.)."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("deep_research_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_statistical_analysis_routing():
    """Test routing for statistics requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("statistical_analysis_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"


def test_entity_resolution_routing():
    """Test routing for entity resolution requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("entity_resolution_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_target_intelligence_routing():
    """Test routing for target intelligence requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("target_intelligence_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_drug_intelligence_routing():
    """Test routing for drug intelligence requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("drug_intelligence_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_target_validation_routing():
    """Test routing for target validation requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("target_validation_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_data_enriched_routing():
    """Test routing for data-enriched requests (routes to output skills, not bio skills)."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("data_enriched_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}, expected {case['expected_skill']}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_research_paper_summarizer_routing():
    """Test routing for paper summarization requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("research_paper_summarizer_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_paper_2_web_routing():
    """Test routing for paper-to-web conversion requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("paper_2_web_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_venue_templates_routing():
    """Test routing for journal formatting requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("venue_templates_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_design_foundation_routing():
    """Test routing for design-foundation and figure-accessibility requests.

    Post visual-design retirement (2026-04-22):
    - Color palette & WCAG/accessibility -> plotting-libraries
    - Design principles/philosophy -> oligon-brand (`<design_foundation>`)
    """
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("design_foundation_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_markdown_to_pdf_routing():
    """Test routing for markdown-to-PDF conversion requests."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("markdown_to_pdf_cases", []):
        result = router.route(case["request"])
        assert result.primary_skill == case["expected_skill"], \
            f"Request '{case['request']}' routed to {result.primary_skill}"
        assert result.confidence >= case.get("min_confidence", 0.5), \
            f"Confidence {result.confidence} below threshold"


def test_negative_cases():
    """Test that negative constraints are respected."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("negative_cases", []):
        result = router.route(case["request"])
        not_expected = case.get("not_expected")
        if not_expected:
            assert result.primary_skill != not_expected, \
                f"Request '{case['request']}' incorrectly routed to {not_expected}"


def test_ambiguous_requires_clarification():
    """Test that ambiguous requests flag for clarification."""
    test_cases = load_test_cases()
    router = SkillRouter()

    for case in test_cases.get("ambiguous_cases", []):
        result = router.route(case["request"])
        max_conf = case.get("max_confidence", 0.7)
        # Ambiguous cases should either have low confidence or require clarification
        assert result.confidence <= max_conf or result.requires_clarification, \
            f"Ambiguous request '{case['request']}' has high confidence {result.confidence}"


def test_empty_request():
    """Test handling of empty requests."""
    router = SkillRouter()
    result = router.route("")
    assert result.requires_clarification
    assert result.confidence == 0.0


def test_xml_output_format():
    """Test XML output formatting."""
    result = route_request("Create a bar chart")
    xml = result.to_xml()
    assert "<routing_decision>" in xml
    assert "<primary_skill>" in xml
    assert "<confidence>" in xml


def test_dict_output_format():
    """Test dictionary output formatting."""
    result = route_request("Create a bar chart")
    d = result.to_dict()
    assert "primary_skill" in d
    assert "confidence" in d
    assert isinstance(d["confidence"], float)


# ============================================================
# Main entry point for standalone execution
# ============================================================

def main():
    """Run tests and print results."""
    import argparse

    parser = argparse.ArgumentParser(description="Run skill router tests")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    args = parser.parse_args()

    print("=" * 60)
    print("SKILL ROUTER TEST SUITE")
    print("=" * 60)
    print()

    passed, total, failures = run_all_tests(verbose=not args.quiet)

    print()
    print("=" * 60)
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"TOTAL: {passed}/{total} ({pass_rate:.1f}%)")
    print("=" * 60)

    if failures:
        print_failures(failures)

    if args.report:
        report = generate_report(passed, total, failures)
        report_path = Path(__file__).parent / "test_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")

    # Exit with error code if tests failed
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
