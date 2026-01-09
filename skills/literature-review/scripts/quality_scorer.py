#!/usr/bin/env python3
"""
Quality Assessment Scoring

Provides standardized quality assessment for systematic reviews using
validated tools: RoB2, NOS, QUADAS-2, CASP, and AMSTAR2.
"""

from dataclasses import dataclass, field
from typing import Literal
import json
import re


# Type definitions
DomainRating = Literal["Low", "Some concerns", "High"]
OverallRating = Literal["Low", "Moderate", "High", "Very Low"]
StudyDesign = Literal[
    "rct",
    "randomized controlled trial",
    "cohort",
    "case-control",
    "cross-sectional",
    "diagnostic",
    "qualitative",
    "systematic review",
    "meta-analysis",
]

# Quality assessment tool definitions
TOOL_DOMAINS: dict[str, list[str]] = {
    "RoB2": [
        "randomization",
        "deviations",
        "missing_data",
        "measurement",
        "selection",
    ],
    "NOS_cohort": [
        "selection",
        "comparability",
        "outcome",
    ],
    "NOS_case_control": [
        "selection",
        "comparability",
        "exposure",
    ],
    "QUADAS2": [
        "patient_selection",
        "index_test",
        "reference_standard",
        "flow_timing",
    ],
    "CASP": [
        "aims",
        "methodology",
        "design",
        "recruitment",
        "data_collection",
        "ethics",
        "analysis",
        "findings",
        "value",
    ],
    "AMSTAR2": [
        "protocol",
        "search",
        "exclusions",
        "rob_tool",
        "meta_methods",
        "rob_interpretation",
        "publication_bias",
    ],
    "JBI_cross_sectional": [
        "inclusion_criteria",
        "subjects_setting",
        "exposure_measurement",
        "objective_criteria",
        "confounders",
        "strategies_confounders",
        "outcome_measurement",
        "statistical_analysis",
    ],
}

# Domain descriptions for guidance
DOMAIN_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "RoB2": {
        "randomization": "Risk of bias arising from the randomization process",
        "deviations": "Risk of bias due to deviations from intended interventions",
        "missing_data": "Risk of bias due to missing outcome data",
        "measurement": "Risk of bias in measurement of the outcome",
        "selection": "Risk of bias in selection of the reported result",
    },
    "NOS_cohort": {
        "selection": "Selection of the cohort (max 4 stars)",
        "comparability": "Comparability of cohorts based on design or analysis (max 2 stars)",
        "outcome": "Assessment of outcome (max 3 stars)",
    },
    "NOS_case_control": {
        "selection": "Selection of cases and controls (max 4 stars)",
        "comparability": "Comparability of cases and controls (max 2 stars)",
        "exposure": "Ascertainment of exposure (max 3 stars)",
    },
    "QUADAS2": {
        "patient_selection": "Could patient selection have introduced bias?",
        "index_test": "Could conduct of the index test have introduced bias?",
        "reference_standard": "Could the reference standard have introduced bias?",
        "flow_timing": "Could patient flow have introduced bias?",
    },
    "CASP": {
        "aims": "Was there a clear statement of the aims of the research?",
        "methodology": "Is a qualitative methodology appropriate?",
        "design": "Was the research design appropriate?",
        "recruitment": "Was the recruitment strategy appropriate?",
        "data_collection": "Was the data collected in a way that addressed the research issue?",
        "ethics": "Has the relationship between researcher and participants been adequately considered?",
        "analysis": "Have ethical issues been taken into consideration?",
        "findings": "Was the data analysis sufficiently rigorous?",
        "value": "Is there a clear statement of findings?",
    },
    "AMSTAR2": {
        "protocol": "Did the research questions include PICO components?",
        "search": "Did the review authors describe their search strategy?",
        "exclusions": "Did the review authors justify their selections?",
        "rob_tool": "Did the review authors use a satisfactory technique for assessing RoB?",
        "meta_methods": "Did the review authors use appropriate methods for meta-analysis?",
        "rob_interpretation": "Did the review authors account for RoB in interpreting results?",
        "publication_bias": "Did the review authors assess publication bias?",
    },
}

# Design to tool mapping
DESIGN_TO_TOOL: dict[str, str] = {
    "rct": "RoB2",
    "randomized controlled trial": "RoB2",
    "randomised controlled trial": "RoB2",
    "cohort": "NOS_cohort",
    "prospective cohort": "NOS_cohort",
    "retrospective cohort": "NOS_cohort",
    "case-control": "NOS_case_control",
    "case control": "NOS_case_control",
    "cross-sectional": "JBI_cross_sectional",
    "cross sectional": "JBI_cross_sectional",
    "diagnostic": "QUADAS2",
    "diagnostic accuracy": "QUADAS2",
    "qualitative": "CASP",
    "systematic review": "AMSTAR2",
    "meta-analysis": "AMSTAR2",
    "meta analysis": "AMSTAR2",
}


@dataclass
class QualityAssessment:
    """
    Structured quality assessment result.

    Captures domain-level ratings, rationales, and calculates overall quality.
    """

    tool: str
    study_id: str
    domain_ratings: dict[str, DomainRating]
    support: dict[str, str]  # domain -> rationale
    assessor: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        """Validate assessment completeness."""
        errors = []

        # Check tool is known
        if self.tool not in TOOL_DOMAINS:
            errors.append(f"Unknown assessment tool: {self.tool}")
            return errors

        expected_domains = TOOL_DOMAINS.get(self.tool, [])

        # Check all domains rated
        for domain in expected_domains:
            if domain not in self.domain_ratings:
                errors.append(f"Missing rating for domain: {domain}")
            elif self.domain_ratings[domain] not in ["Low", "Some concerns", "High"]:
                errors.append(
                    f"Invalid rating '{self.domain_ratings[domain]}' for domain: {domain}"
                )
            if domain not in self.support or not self.support[domain].strip():
                errors.append(f"Missing rationale for domain: {domain}")

        # Check for extra domains
        for domain in self.domain_ratings:
            if domain not in expected_domains:
                errors.append(f"Unexpected domain for {self.tool}: {domain}")

        # Study ID required
        if not self.study_id or not self.study_id.strip():
            errors.append("Study ID is required")

        return errors

    def is_valid(self) -> bool:
        """Check if assessment has no validation errors."""
        return len(self.validate()) == 0

    def calculate_overall(self) -> OverallRating:
        """
        Calculate overall rating from domain ratings.

        Rules:
        - 3+ High risk domains -> Very Low quality
        - 2 High risk domains -> Low quality
        - 1 High risk domain -> Moderate quality
        - 3+ Some concerns -> Moderate quality
        - Otherwise -> High quality
        """
        ratings = list(self.domain_ratings.values())
        high_count = sum(1 for r in ratings if r == "High")
        concerns_count = sum(1 for r in ratings if r == "Some concerns")

        if high_count >= 3:
            return "Very Low"
        elif high_count >= 2:
            return "Low"
        elif high_count == 1:
            return "Moderate"
        elif concerns_count >= 3:
            return "Moderate"
        return "High"

    def get_summary(self) -> dict:
        """Generate summary statistics."""
        ratings = list(self.domain_ratings.values())
        return {
            "study_id": self.study_id,
            "tool": self.tool,
            "overall_rating": self.calculate_overall(),
            "high_risk_count": sum(1 for r in ratings if r == "High"),
            "some_concerns_count": sum(1 for r in ratings if r == "Some concerns"),
            "low_risk_count": sum(1 for r in ratings if r == "Low"),
            "total_domains": len(ratings),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tool": self.tool,
            "study_id": self.study_id,
            "domain_ratings": self.domain_ratings,
            "support": self.support,
            "assessor": self.assessor,
            "notes": self.notes,
            "overall_rating": self.calculate_overall(),
        }


@dataclass
class QualityAssessmentSet:
    """Collection of quality assessments for a review."""

    assessments: list[QualityAssessment] = field(default_factory=list)
    review_title: str = ""

    def add_assessment(self, assessment: QualityAssessment) -> None:
        """Add an assessment to the set."""
        self.assessments.append(assessment)

    def validate(self) -> list[str]:
        """Validate all assessments in the set."""
        errors = []

        if not self.assessments:
            errors.append("No assessments in set")
            return errors

        # Check for duplicate study IDs
        study_ids = [a.study_id for a in self.assessments]
        duplicates = [sid for sid in study_ids if study_ids.count(sid) > 1]
        if duplicates:
            errors.append(f"Duplicate study IDs: {set(duplicates)}")

        # Validate each assessment
        for i, assessment in enumerate(self.assessments):
            assessment_errors = assessment.validate()
            for error in assessment_errors:
                errors.append(f"Assessment {i + 1} ({assessment.study_id}): {error}")

        return errors

    def get_summary(self) -> dict:
        """Generate summary statistics for the set."""
        if not self.assessments:
            return {"total_studies": 0}

        overall_ratings = [a.calculate_overall() for a in self.assessments]

        return {
            "review_title": self.review_title,
            "total_studies": len(self.assessments),
            "high_quality": sum(1 for r in overall_ratings if r == "High"),
            "moderate_quality": sum(1 for r in overall_ratings if r == "Moderate"),
            "low_quality": sum(1 for r in overall_ratings if r == "Low"),
            "very_low_quality": sum(1 for r in overall_ratings if r == "Very Low"),
            "tools_used": list({a.tool for a in self.assessments}),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "review_title": self.review_title,
            "assessments": [a.to_dict() for a in self.assessments],
            "summary": self.get_summary(),
        }


def select_quality_tool(study_design: str) -> str:
    """
    Deterministically select quality assessment tool from study design.

    Args:
        study_design: Description of study design

    Returns:
        Name of appropriate quality assessment tool
    """
    design_lower = study_design.lower().strip()

    # Direct mapping
    if design_lower in DESIGN_TO_TOOL:
        return DESIGN_TO_TOOL[design_lower]

    # Pattern matching for fuzzy cases
    if re.search(r"random(ized|ised)", design_lower):
        return "RoB2"
    if "cohort" in design_lower:
        return "NOS_cohort"
    if "case" in design_lower and "control" in design_lower:
        return "NOS_case_control"
    if "cross" in design_lower and "section" in design_lower:
        return "JBI_cross_sectional"
    if "diagnos" in design_lower:
        return "QUADAS2"
    if "qualitative" in design_lower:
        return "CASP"
    if "systematic" in design_lower or "meta" in design_lower:
        return "AMSTAR2"

    # Default fallback
    return "NOS_cohort"


def get_tool_domains(tool: str) -> list[str]:
    """Get the list of domains for a quality assessment tool."""
    return TOOL_DOMAINS.get(tool, [])


def get_domain_description(tool: str, domain: str) -> str:
    """Get the description for a specific domain."""
    tool_descriptions = DOMAIN_DESCRIPTIONS.get(tool, {})
    return tool_descriptions.get(domain, "")


def create_assessment_from_dict(data: dict) -> QualityAssessment:
    """
    Create a QualityAssessment from a dictionary.

    Args:
        data: Dictionary with assessment data

    Returns:
        QualityAssessment instance
    """
    return QualityAssessment(
        tool=data.get("tool", ""),
        study_id=data.get("study_id", ""),
        domain_ratings=data.get("domain_ratings", {}),
        support=data.get("support", {}),
        assessor=data.get("assessor", ""),
        notes=data.get("notes", ""),
    )


def load_assessments_from_json(filepath: str) -> QualityAssessmentSet:
    """Load quality assessments from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assessment_set = QualityAssessmentSet(review_title=data.get("review_title", ""))

    for assessment_data in data.get("assessments", []):
        assessment = create_assessment_from_dict(assessment_data)
        assessment_set.add_assessment(assessment)

    return assessment_set


def save_assessments_to_json(assessment_set: QualityAssessmentSet, filepath: str) -> None:
    """Save quality assessments to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(assessment_set.to_dict(), f, indent=2)


def create_blank_assessment(tool: str, study_id: str) -> QualityAssessment:
    """
    Create a blank assessment template for a given tool.

    Args:
        tool: Quality assessment tool name
        study_id: Study identifier

    Returns:
        QualityAssessment with empty ratings and support
    """
    domains = TOOL_DOMAINS.get(tool, [])
    return QualityAssessment(
        tool=tool,
        study_id=study_id,
        domain_ratings={d: "Low" for d in domains},  # Default to Low
        support={d: "" for d in domains},  # Empty rationales
    )


def main():
    """Example usage and demonstration."""
    import sys

    if len(sys.argv) > 1:
        # Load and validate from JSON file
        filepath = sys.argv[1]
        try:
            assessment_set = load_assessments_from_json(filepath)
            print(f"Loaded {len(assessment_set.assessments)} assessments from {filepath}")
            print(f"\nSummary: {json.dumps(assessment_set.get_summary(), indent=2)}")

            errors = assessment_set.validate()
            if errors:
                print("\nValidation issues:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("\nValidation: PASSED")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Demo mode
        print("Quality Assessment Scoring Demo")
        print("=" * 60)

        # Show available tools
        print("\nAvailable tools and their domains:")
        for tool, domains in TOOL_DOMAINS.items():
            print(f"  {tool}: {', '.join(domains)}")

        # Tool selection demo
        print("\n" + "=" * 60)
        print("Tool selection from study design:")
        test_designs = [
            "randomized controlled trial",
            "prospective cohort study",
            "case-control study",
            "cross-sectional survey",
            "diagnostic accuracy study",
            "qualitative interview study",
            "systematic review with meta-analysis",
        ]
        for design in test_designs:
            tool = select_quality_tool(design)
            print(f"  '{design}' -> {tool}")

        # Assessment demo
        print("\n" + "=" * 60)
        print("Example RoB2 Assessment:")

        assessment = QualityAssessment(
            tool="RoB2",
            study_id="Smith2023",
            domain_ratings={
                "randomization": "Low",
                "deviations": "Some concerns",
                "missing_data": "Low",
                "measurement": "Low",
                "selection": "Low",
            },
            support={
                "randomization": "Computer-generated sequence with allocation concealment",
                "deviations": "Some protocol deviations noted but unlikely to affect outcome",
                "missing_data": "ITT analysis with <5% missing data",
                "measurement": "Blinded outcome assessors",
                "selection": "Pre-specified primary outcome reported",
            },
            assessor="JDoe",
        )

        print(f"  Study: {assessment.study_id}")
        print(f"  Tool: {assessment.tool}")
        print(f"  Overall Rating: {assessment.calculate_overall()}")
        print(f"  Valid: {assessment.is_valid()}")
        print(f"  Summary: {json.dumps(assessment.get_summary(), indent=4)}")


if __name__ == "__main__":
    main()
