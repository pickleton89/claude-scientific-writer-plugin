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
        "explanation_levels",
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
            explanation_levels=[
                ExplanationLevel(level) for level in input_dict["explanation_levels"]
            ],
            target_hypothesis_count=input_dict["target_hypothesis_count"],
            available_methods=input_dict.get("available_methods", []),
            timeline=input_dict.get("timeline", "standard"),
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
        print("\nValidated input:")
        print(f"  Domain: {validated.domain.value}")
        print(f"  Type: {validated.observation_type.value}")
        print(f"  Target hypotheses: {validated.target_hypothesis_count}")
        print(f"  Levels: {[level.value for level in validated.explanation_levels]}")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
