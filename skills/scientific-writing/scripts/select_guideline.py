#!/usr/bin/env python3
"""Select appropriate reporting guideline based on study design."""

from enum import Enum
import json
import sys


class StudyDesign(Enum):
    RCT = "rct"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_REPORT = "case_report"
    QUALITATIVE = "qualitative"
    DIAGNOSTIC_ACCURACY = "diagnostic_accuracy"
    PREDICTION_MODEL = "prediction_model"
    ANIMAL_STUDY = "animal_study"
    QI_STUDY = "quality_improvement"
    ECONOMIC_EVALUATION = "economic_evaluation"


GUIDELINE_MAP = {
    StudyDesign.RCT: {
        "primary": "CONSORT",
        "url": "http://www.consort-statement.org/",
        "items": 25,
        "extensions": ["cluster", "non-inferiority", "pragmatic", "pilot"],
    },
    StudyDesign.COHORT: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": ["molecular_epidemiology", "routinely_collected_data"],
    },
    StudyDesign.CASE_CONTROL: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": [],
    },
    StudyDesign.CROSS_SECTIONAL: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": [],
    },
    StudyDesign.SYSTEMATIC_REVIEW: {
        "primary": "PRISMA",
        "url": "http://www.prisma-statement.org/",
        "items": 27,
        "extensions": ["protocols", "network_meta", "scoping", "IPD", "DTA"],
    },
    StudyDesign.META_ANALYSIS: {
        "primary": "PRISMA",
        "url": "http://www.prisma-statement.org/",
        "items": 27,
        "extensions": [],
    },
    StudyDesign.CASE_REPORT: {
        "primary": "CARE",
        "url": "https://www.care-statement.org/",
        "items": 13,
        "extensions": [],
    },
    StudyDesign.QUALITATIVE: {
        "primary": "SRQR",
        "url": "https://www.equator-network.org/reporting-guidelines/srqr/",
        "items": 21,
        "extensions": ["COREQ"],
    },
    StudyDesign.DIAGNOSTIC_ACCURACY: {
        "primary": "STARD",
        "url": "https://www.equator-network.org/reporting-guidelines/stard/",
        "items": 30,
        "extensions": [],
    },
    StudyDesign.PREDICTION_MODEL: {
        "primary": "TRIPOD",
        "url": "https://www.tripod-statement.org/",
        "items": 22,
        "extensions": [],
    },
    StudyDesign.ANIMAL_STUDY: {
        "primary": "ARRIVE",
        "url": "https://arriveguidelines.org/",
        "items": 10,
        "extensions": ["ARRIVE_2.0"],
    },
    StudyDesign.QI_STUDY: {
        "primary": "SQUIRE",
        "url": "http://www.squire-statement.org/",
        "items": 18,
        "extensions": [],
    },
    StudyDesign.ECONOMIC_EVALUATION: {
        "primary": "CHEERS",
        "url": "https://www.equator-network.org/reporting-guidelines/cheers/",
        "items": 28,
        "extensions": [],
    },
}


def get_valid_study_designs() -> list[str]:
    """Return list of valid study design values."""
    return [d.value for d in StudyDesign]


def select_guideline(study_design: str) -> dict:
    """Select reporting guideline for a given study design.

    Args:
        study_design: The study design type (e.g., "rct", "cohort")

    Returns:
        Dictionary containing guideline information or error details
    """
    try:
        design = StudyDesign(study_design.lower())
    except ValueError:
        return {
            "error": f"Unknown study design: {study_design}",
            "valid_options": get_valid_study_designs(),
        }

    guideline = GUIDELINE_MAP[design]
    return {
        "study_design": design.value,
        "guideline": guideline["primary"],
        "url": guideline["url"],
        "checklist_items": guideline["items"],
        "available_extensions": guideline["extensions"],
        "equator_search": f"https://www.equator-network.org/?s={guideline['primary']}",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python select_guideline.py <study_design>")
        print(f"Valid designs: {get_valid_study_designs()}")
        sys.exit(1)

    result = select_guideline(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
