#!/usr/bin/env python3
"""
Research Question Schema Validation

Provides structured dataclasses for PICO, PEO, and SPIDER research question
frameworks with validation and search term generation.
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional
import json
import re


# Type definitions
QuestionType = Literal["PICO", "PEO", "SPIDER"]
QualitativeDesign = Literal[
    "phenomenological",
    "ethnographic",
    "grounded theory",
    "case study",
    "narrative",
    "action research",
    "descriptive",
]
ResearchType = Literal["qualitative", "mixed"]


@dataclass
class PICOQuestion:
    """
    PICO format for clinical/intervention research questions.

    Used for questions about the effectiveness of interventions:
    "In [Population], does [Intervention] compared to [Comparison]
    improve [Outcome]?"
    """

    population: str
    intervention: str
    comparison: str
    outcome: str
    timeframe: Optional[str] = None

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []

        # Required field checks
        if not self.population or len(self.population.strip()) < 5:
            errors.append("Population must be at least 5 characters - be specific")
        if not self.intervention or len(self.intervention.strip()) < 3:
            errors.append("Intervention is required")
        if not self.outcome or len(self.outcome.strip()) < 3:
            errors.append("Outcome is required for PICO questions")

        # Comparison can be empty (single-arm studies) but warn if so
        if not self.comparison:
            errors.append("Warning: No comparison specified - consider adding one")

        # Check for overly broad terms
        broad_terms = ["patients", "people", "individuals", "subjects"]
        if self.population and self.population.lower().strip() in broad_terms:
            errors.append(
                f"Population '{self.population}' is too broad - "
                "specify age, condition, or setting"
            )

        return errors

    def is_valid(self) -> bool:
        """Check if question has no errors (warnings allowed)."""
        errors = self.validate()
        return all("Warning:" in e for e in errors) or len(errors) == 0

    def to_search_terms(self) -> dict[str, list[str]]:
        """Generate database-agnostic search term groups."""
        return {
            "population": _split_terms(self.population),
            "intervention": _split_terms(self.intervention),
            "comparison": _split_terms(self.comparison) if self.comparison else [],
            "outcome": _split_terms(self.outcome),
        }

    def to_question_string(self) -> str:
        """Generate natural language research question."""
        q = f"In {self.population}, does {self.intervention}"
        if self.comparison:
            q += f" compared to {self.comparison}"
        q += f" improve {self.outcome}?"
        if self.timeframe:
            q = q.rstrip("?") + f" over {self.timeframe}?"
        return q

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"type": "PICO", **asdict(self)}


@dataclass
class PEOQuestion:
    """
    PEO format for observational/exposure research questions.

    Used for questions about associations and risk factors:
    "In [Population], is [Exposure] associated with [Outcome]?"
    """

    population: str
    exposure: str
    outcome: str
    timeframe: Optional[str] = None

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []

        if not self.population or len(self.population.strip()) < 5:
            errors.append("Population must be at least 5 characters - be specific")
        if not self.exposure or len(self.exposure.strip()) < 3:
            errors.append("Exposure/risk factor is required")
        if not self.outcome or len(self.outcome.strip()) < 3:
            errors.append("Outcome is required for PEO questions")

        return errors

    def is_valid(self) -> bool:
        """Check if question has no errors."""
        return len(self.validate()) == 0

    def to_search_terms(self) -> dict[str, list[str]]:
        """Generate database-agnostic search term groups."""
        return {
            "population": _split_terms(self.population),
            "exposure": _split_terms(self.exposure),
            "outcome": _split_terms(self.outcome),
        }

    def to_question_string(self) -> str:
        """Generate natural language research question."""
        q = f"In {self.population}, is {self.exposure} associated with {self.outcome}?"
        if self.timeframe:
            q = q.rstrip("?") + f" over {self.timeframe}?"
        return q

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"type": "PEO", **asdict(self)}


@dataclass
class SPIDERQuestion:
    """
    SPIDER format for qualitative research questions.

    Used for questions about experiences, perceptions, and meanings:
    "What is the [Phenomenon] experienced by [Sample] using
    [Design] and [Research type] approaches?"
    """

    sample: str
    phenomenon: str
    design: QualitativeDesign
    evaluation: str
    research_type: ResearchType

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []

        if not self.sample or len(self.sample.strip()) < 5:
            errors.append("Sample must be at least 5 characters - be specific")
        if not self.phenomenon or len(self.phenomenon.strip()) < 5:
            errors.append("Phenomenon of interest is required")
        if not self.evaluation or len(self.evaluation.strip()) < 3:
            errors.append("Evaluation criteria are required")

        valid_designs = [
            "phenomenological",
            "ethnographic",
            "grounded theory",
            "case study",
            "narrative",
            "action research",
            "descriptive",
        ]
        if self.design not in valid_designs:
            errors.append(f"Design must be one of: {', '.join(valid_designs)}")

        valid_types = ["qualitative", "mixed"]
        if self.research_type not in valid_types:
            errors.append(f"Research type must be one of: {', '.join(valid_types)}")

        return errors

    def is_valid(self) -> bool:
        """Check if question has no errors."""
        return len(self.validate()) == 0

    def to_search_terms(self) -> dict[str, list[str]]:
        """Generate database-agnostic search term groups."""
        return {
            "sample": _split_terms(self.sample),
            "phenomenon": _split_terms(self.phenomenon),
            "design": [self.design],
            "evaluation": _split_terms(self.evaluation),
            "research_type": [self.research_type],
        }

    def to_question_string(self) -> str:
        """Generate natural language research question."""
        return (
            f"What is the {self.phenomenon} experienced by {self.sample} "
            f"using {self.design} {self.research_type} approaches, "
            f"evaluated by {self.evaluation}?"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"type": "SPIDER", **asdict(self)}


# Type alias for any question type
ResearchQuestion = PICOQuestion | PEOQuestion | SPIDERQuestion


def _split_terms(text: str) -> list[str]:
    """Split text into individual search terms."""
    if not text:
        return []
    # Split on commas, semicolons, or "OR"
    terms = re.split(r"[,;]|\bOR\b", text, flags=re.IGNORECASE)
    return [t.strip() for t in terms if t.strip()]


def detect_question_type(text: str) -> QuestionType:
    """
    Detect PICO/PEO/SPIDER from question text.

    Args:
        text: Natural language research question

    Returns:
        Detected question type
    """
    text_lower = text.lower()

    # PICO indicators: intervention, treatment, therapy, effect
    pico_indicators = [
        "intervention",
        "treatment",
        "therapy",
        "effect of",
        "efficacy",
        "effectiveness",
        "compared to",
        "versus",
        "vs",
    ]

    # PEO indicators: exposure, risk factor, association
    peo_indicators = [
        "exposure",
        "risk factor",
        "associated with",
        "association",
        "relationship between",
        "correlation",
        "predictor",
    ]

    # SPIDER indicators: qualitative, experience, perception
    spider_indicators = [
        "qualitative",
        "experience",
        "perception",
        "perspective",
        "lived experience",
        "meaning",
        "understanding",
        "phenomeno",
        "ethnograph",
        "grounded theory",
    ]

    # Count matches for each type
    pico_score = sum(1 for ind in pico_indicators if ind in text_lower)
    peo_score = sum(1 for ind in peo_indicators if ind in text_lower)
    spider_score = sum(1 for ind in spider_indicators if ind in text_lower)

    # Return type with highest score
    if spider_score > pico_score and spider_score > peo_score:
        return "SPIDER"
    elif peo_score > pico_score:
        return "PEO"
    return "PICO"  # Default


def create_question_from_dict(data: dict) -> ResearchQuestion:
    """
    Create a research question from a dictionary.

    Args:
        data: Dictionary with 'type' key and question fields

    Returns:
        Appropriate question dataclass instance

    Raises:
        ValueError: If type is unknown or required fields missing
    """
    question_type = data.get("type", "").upper()

    if question_type == "PICO":
        return PICOQuestion(
            population=data.get("population", ""),
            intervention=data.get("intervention", ""),
            comparison=data.get("comparison", ""),
            outcome=data.get("outcome", ""),
            timeframe=data.get("timeframe"),
        )
    elif question_type == "PEO":
        return PEOQuestion(
            population=data.get("population", ""),
            exposure=data.get("exposure", ""),
            outcome=data.get("outcome", ""),
            timeframe=data.get("timeframe"),
        )
    elif question_type == "SPIDER":
        return SPIDERQuestion(
            sample=data.get("sample", ""),
            phenomenon=data.get("phenomenon", ""),
            design=data.get("design", "phenomenological"),
            evaluation=data.get("evaluation", ""),
            research_type=data.get("research_type", "qualitative"),
        )
    else:
        raise ValueError(f"Unknown question type: {question_type}")


def load_question_from_json(filepath: str) -> ResearchQuestion:
    """Load a research question from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return create_question_from_dict(data)


def save_question_to_json(question: ResearchQuestion, filepath: str) -> None:
    """Save a research question to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(question.to_dict(), f, indent=2)


def main():
    """Example usage and validation."""
    import sys

    if len(sys.argv) > 1:
        # Load and validate from JSON file
        filepath = sys.argv[1]
        try:
            question = load_question_from_json(filepath)
            print(f"Loaded {type(question).__name__} from {filepath}")
            print(f"\nQuestion: {question.to_question_string()}")
            print(f"\nSearch terms: {json.dumps(question.to_search_terms(), indent=2)}")

            errors = question.validate()
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
        print("Research Question Schema Demo")
        print("=" * 60)

        # PICO example
        pico = PICOQuestion(
            population="adults with type 2 diabetes aged 40-65",
            intervention="metformin monotherapy",
            comparison="lifestyle modification alone",
            outcome="HbA1c reduction",
            timeframe="12 months",
        )
        print(f"\nPICO Question:\n{pico.to_question_string()}")
        print(f"Valid: {pico.is_valid()}")

        # PEO example
        peo = PEOQuestion(
            population="children under 5 in urban areas",
            exposure="air pollution (PM2.5 > 35 μg/m³)",
            outcome="respiratory infections",
        )
        print(f"\nPEO Question:\n{peo.to_question_string()}")
        print(f"Valid: {peo.is_valid()}")

        # SPIDER example
        spider = SPIDERQuestion(
            sample="nurses in intensive care units",
            phenomenon="burnout and moral distress",
            design="phenomenological",
            evaluation="thematic analysis",
            research_type="qualitative",
        )
        print(f"\nSPIDER Question:\n{spider.to_question_string()}")
        print(f"Valid: {spider.is_valid()}")

        # Detection example
        print("\n" + "=" * 60)
        print("Question Type Detection:")
        test_questions = [
            "What is the effect of exercise on depression?",
            "Is smoking associated with lung cancer risk?",
            "What are nurses' experiences of end-of-life care?",
        ]
        for q in test_questions:
            detected = detect_question_type(q)
            print(f"  '{q[:50]}...' -> {detected}")


if __name__ == "__main__":
    main()
