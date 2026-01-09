#!/usr/bin/env python3
"""
Review Configuration Validation

Provides configuration validation and preflight checks for literature reviews.
Ensures all review parameters are properly specified before starting.
"""

from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Literal, Optional, Any
import json


# Type definitions
ReviewType = Literal["systematic", "scoping", "narrative", "rapid"]
QuestionType = Literal["PICO", "PEO", "SPIDER"]

# Review type requirements
REVIEW_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "systematic": {
        "min_databases": 3,
        "requires_protocol": True,
        "requires_dual_screening": True,
        "requires_quality_assessment": True,
        "min_inclusion_criteria": 3,
        "min_exclusion_criteria": 2,
    },
    "scoping": {
        "min_databases": 2,
        "requires_protocol": True,
        "requires_dual_screening": False,
        "requires_quality_assessment": False,
        "min_inclusion_criteria": 2,
        "min_exclusion_criteria": 1,
    },
    "narrative": {
        "min_databases": 2,
        "requires_protocol": False,
        "requires_dual_screening": False,
        "requires_quality_assessment": False,
        "min_inclusion_criteria": 1,
        "min_exclusion_criteria": 1,
    },
    "rapid": {
        "min_databases": 2,
        "requires_protocol": True,
        "requires_dual_screening": False,
        "requires_quality_assessment": True,
        "min_inclusion_criteria": 2,
        "min_exclusion_criteria": 1,
    },
}


@dataclass
class Criterion:
    """Inclusion or exclusion criterion with rationale."""

    criterion: str
    rationale: str
    category: str = ""  # e.g., "population", "intervention", "study design"

    def validate(self) -> list[str]:
        """Validate criterion completeness."""
        errors = []
        if not self.criterion or len(self.criterion.strip()) < 5:
            errors.append("Criterion text must be at least 5 characters")
        if not self.rationale or len(self.rationale.strip()) < 10:
            errors.append("Rationale must be at least 10 characters")
        return errors

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReviewConfig:
    """
    Validated review configuration.

    Contains all parameters needed to start a literature review with
    comprehensive validation and preflight checks.
    """

    title: str
    review_type: ReviewType
    research_question: dict  # PICO, PEO, or SPIDER format
    question_type: QuestionType
    domain: str
    subdomain: Optional[str] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    inclusion_criteria: list[Criterion] = field(default_factory=list)
    exclusion_criteria: list[Criterion] = field(default_factory=list)
    databases: list[str] = field(default_factory=list)
    protocol_registration: str = ""
    team_members: list[str] = field(default_factory=list)
    notes: str = ""

    def validate(self) -> list[str]:
        """Validate configuration completeness and consistency."""
        errors = []

        # Title validation
        if not self.title or len(self.title.strip()) < 10:
            errors.append("Title must be at least 10 characters")

        # Review type validation
        valid_types = ["systematic", "scoping", "narrative", "rapid"]
        if self.review_type not in valid_types:
            errors.append(f"Invalid review type: {self.review_type}")

        # Question type validation
        valid_question_types = ["PICO", "PEO", "SPIDER"]
        if self.question_type not in valid_question_types:
            errors.append(f"Invalid question type: {self.question_type}")

        # Research question validation
        if not self.research_question:
            errors.append("Research question is required")
        else:
            errors.extend(self._validate_research_question())

        # Domain validation
        if not self.domain or len(self.domain.strip()) < 3:
            errors.append("Domain is required")

        # Date range validation
        if self.date_range_start and self.date_range_end:
            if self.date_range_end < self.date_range_start:
                errors.append("End date must be after start date")
            if self.date_range_end > date.today():
                errors.append("End date cannot be in the future")

        # Get requirements for this review type
        requirements = REVIEW_REQUIREMENTS.get(self.review_type, {})

        # Database minimum check
        min_dbs = requirements.get("min_databases", 2)
        if len(self.databases) < min_dbs:
            errors.append(
                f"{self.review_type} review requires at least {min_dbs} databases, "
                f"but only {len(self.databases)} specified"
            )

        # Criteria validation
        min_inclusion = requirements.get("min_inclusion_criteria", 1)
        min_exclusion = requirements.get("min_exclusion_criteria", 1)

        if len(self.inclusion_criteria) < min_inclusion:
            errors.append(
                f"At least {min_inclusion} inclusion criteria required for "
                f"{self.review_type} review"
            )
        if len(self.exclusion_criteria) < min_exclusion:
            errors.append(
                f"At least {min_exclusion} exclusion criteria required for "
                f"{self.review_type} review"
            )

        # Validate individual criteria
        for i, criterion in enumerate(self.inclusion_criteria):
            for error in criterion.validate():
                errors.append(f"Inclusion criterion {i + 1}: {error}")

        for i, criterion in enumerate(self.exclusion_criteria):
            for error in criterion.validate():
                errors.append(f"Exclusion criterion {i + 1}: {error}")

        # Protocol registration for systematic/rapid reviews
        if requirements.get("requires_protocol", False) and not self.protocol_registration:
            errors.append(
                f"Protocol registration recommended for {self.review_type} reviews "
                "(e.g., PROSPERO, OSF)"
            )

        return errors

    def _validate_research_question(self) -> list[str]:
        """Validate research question based on type."""
        errors = []
        q = self.research_question

        if self.question_type == "PICO":
            required_fields = ["population", "intervention", "outcome"]
            for field_name in required_fields:
                if not q.get(field_name):
                    errors.append(f"PICO question missing required field: {field_name}")

        elif self.question_type == "PEO":
            required_fields = ["population", "exposure", "outcome"]
            for field_name in required_fields:
                if not q.get(field_name):
                    errors.append(f"PEO question missing required field: {field_name}")

        elif self.question_type == "SPIDER":
            required_fields = ["sample", "phenomenon", "design", "evaluation", "research_type"]
            for field_name in required_fields:
                if not q.get(field_name):
                    errors.append(f"SPIDER question missing required field: {field_name}")

        return errors

    def is_valid(self) -> bool:
        """Check if configuration has no validation errors."""
        return len(self.validate()) == 0

    def get_requirements(self) -> dict:
        """Get requirements for the current review type."""
        return REVIEW_REQUIREMENTS.get(self.review_type, {})

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = {
            "title": self.title,
            "review_type": self.review_type,
            "research_question": self.research_question,
            "question_type": self.question_type,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "date_range_start": self.date_range_start.isoformat() if self.date_range_start else None,
            "date_range_end": self.date_range_end.isoformat() if self.date_range_end else None,
            "inclusion_criteria": [c.to_dict() for c in self.inclusion_criteria],
            "exclusion_criteria": [c.to_dict() for c in self.exclusion_criteria],
            "databases": self.databases,
            "protocol_registration": self.protocol_registration,
            "team_members": self.team_members,
            "notes": self.notes,
        }
        return data


@dataclass
class PreflightResult:
    """Result of preflight validation."""

    config_valid: bool
    config_errors: list[str]
    database_coverage: dict
    date_range_appropriate: dict
    criteria_specificity: dict
    recommendations: list[str]

    def is_ready(self) -> bool:
        """Check if review is ready to start."""
        return self.config_valid

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


def preflight_check(config: ReviewConfig) -> PreflightResult:
    """
    Run all preflight validations.

    Args:
        config: ReviewConfig to validate

    Returns:
        PreflightResult with validation details
    """
    config_errors = config.validate()
    recommendations = []

    # Database coverage analysis
    database_coverage = _check_database_coverage(config)
    if database_coverage.get("missing_preprint"):
        recommendations.append(
            f"Consider adding preprint search: {database_coverage['suggested_preprint']}"
        )

    # Date range analysis
    date_range_info = _check_date_range(config)
    if date_range_info.get("warning"):
        recommendations.append(date_range_info["warning"])

    # Criteria specificity analysis
    criteria_info = _check_criteria_specificity(config)
    if criteria_info.get("suggestions"):
        recommendations.extend(criteria_info["suggestions"])

    # Additional recommendations based on review type
    requirements = config.get_requirements()
    if requirements.get("requires_dual_screening") and len(config.team_members) < 2:
        recommendations.append(
            "Systematic reviews recommend dual screening - consider adding team members"
        )

    return PreflightResult(
        config_valid=len(config_errors) == 0,
        config_errors=config_errors,
        database_coverage=database_coverage,
        date_range_appropriate=date_range_info,
        criteria_specificity=criteria_info,
        recommendations=recommendations,
    )


def _check_database_coverage(config: ReviewConfig) -> dict:
    """Analyze database coverage."""
    preprint_servers = ["arxiv", "biorxiv", "medrxiv", "ssrn", "zenodo"]
    has_preprint = any(
        any(ps in db.lower() for ps in preprint_servers) for db in config.databases
    )

    # Domain-specific preprint suggestions
    preprint_map = {
        "biomedical": "bioRxiv/medRxiv",
        "computer_science": "arXiv",
        "physical_sciences": "arXiv",
        "social_sciences": "SSRN",
    }

    suggested_preprint = preprint_map.get(
        config.domain.lower() if config.domain else "", "Zenodo"
    )

    return {
        "total_databases": len(config.databases),
        "has_preprint": has_preprint,
        "missing_preprint": not has_preprint
        and config.review_type in ["systematic", "scoping"],
        "suggested_preprint": suggested_preprint,
        "databases": config.databases,
    }


def _check_date_range(config: ReviewConfig) -> dict:
    """Analyze date range appropriateness."""
    result: dict[str, Any] = {
        "start": config.date_range_start.isoformat() if config.date_range_start else None,
        "end": config.date_range_end.isoformat() if config.date_range_end else None,
        "span_years": None,
        "warning": None,
    }

    if config.date_range_start and config.date_range_end:
        span = config.date_range_end - config.date_range_start
        span_years = span.days / 365.25
        result["span_years"] = round(span_years, 1)

        if span_years > 20:
            result["warning"] = (
                f"Date range spans {span_years:.1f} years - consider narrowing "
                "or justifying broad scope"
            )
        elif span_years < 2 and config.review_type == "systematic":
            result["warning"] = (
                f"Date range spans only {span_years:.1f} years - may limit "
                "available literature"
            )

    return result


def _check_criteria_specificity(config: ReviewConfig) -> dict:
    """Analyze criteria specificity."""
    result: dict[str, Any] = {
        "inclusion_count": len(config.inclusion_criteria),
        "exclusion_count": len(config.exclusion_criteria),
        "categories_covered": [],
        "suggestions": [],
    }

    # Check what categories are covered
    categories = set()
    for criterion in config.inclusion_criteria + config.exclusion_criteria:
        if criterion.category:
            categories.add(criterion.category)
    result["categories_covered"] = list(categories)

    # Suggest missing common categories
    recommended_categories = {"population", "intervention", "outcome", "study design"}
    missing = recommended_categories - categories
    if missing and config.review_type == "systematic":
        result["suggestions"].append(
            f"Consider adding criteria for: {', '.join(missing)}"
        )

    # Check for vague criteria
    vague_terms = ["appropriate", "relevant", "suitable", "adequate"]
    for criterion in config.inclusion_criteria + config.exclusion_criteria:
        text_lower = criterion.criterion.lower()
        if any(term in text_lower for term in vague_terms):
            result["suggestions"].append(
                f"Criterion '{criterion.criterion[:30]}...' may be too vague - "
                "consider more specific language"
            )

    return result


def create_config_from_dict(data: dict) -> ReviewConfig:
    """
    Create a ReviewConfig from a dictionary.

    Args:
        data: Dictionary with configuration data

    Returns:
        ReviewConfig instance
    """
    # Parse date strings if present
    date_start = None
    date_end = None
    if data.get("date_range_start"):
        date_start = date.fromisoformat(data["date_range_start"])
    if data.get("date_range_end"):
        date_end = date.fromisoformat(data["date_range_end"])

    # Parse criteria
    inclusion = [
        Criterion(
            criterion=c.get("criterion", ""),
            rationale=c.get("rationale", ""),
            category=c.get("category", ""),
        )
        for c in data.get("inclusion_criteria", [])
    ]

    exclusion = [
        Criterion(
            criterion=c.get("criterion", ""),
            rationale=c.get("rationale", ""),
            category=c.get("category", ""),
        )
        for c in data.get("exclusion_criteria", [])
    ]

    return ReviewConfig(
        title=data.get("title", ""),
        review_type=data.get("review_type", "systematic"),
        research_question=data.get("research_question", {}),
        question_type=data.get("question_type", "PICO"),
        domain=data.get("domain", ""),
        subdomain=data.get("subdomain"),
        date_range_start=date_start,
        date_range_end=date_end,
        inclusion_criteria=inclusion,
        exclusion_criteria=exclusion,
        databases=data.get("databases", []),
        protocol_registration=data.get("protocol_registration", ""),
        team_members=data.get("team_members", []),
        notes=data.get("notes", ""),
    )


def load_config_from_json(filepath: str) -> ReviewConfig:
    """Load review configuration from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return create_config_from_dict(data)


def save_config_to_json(config: ReviewConfig, filepath: str) -> None:
    """Save review configuration to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, default=str)


def generate_protocol_template(config: ReviewConfig) -> str:
    """
    Generate a protocol document template from configuration.

    Args:
        config: ReviewConfig object

    Returns:
        Formatted protocol template string
    """
    lines = [
        "SYSTEMATIC REVIEW PROTOCOL",
        "=" * 60,
        "",
        f"Title: {config.title}",
        f"Review Type: {config.review_type}",
        f"Domain: {config.domain}" + (f" / {config.subdomain}" if config.subdomain else ""),
        "",
        "RESEARCH QUESTION",
        "-" * 40,
        f"Type: {config.question_type}",
    ]

    # Format research question
    for key, value in config.research_question.items():
        if value:
            lines.append(f"  {key.capitalize()}: {value}")

    # Date range
    lines.extend(
        [
            "",
            "SEARCH PARAMETERS",
            "-" * 40,
        ]
    )
    if config.date_range_start and config.date_range_end:
        lines.append(
            f"Date Range: {config.date_range_start.isoformat()} to "
            f"{config.date_range_end.isoformat()}"
        )
    lines.append(f"Databases: {', '.join(config.databases)}")

    # Inclusion criteria
    lines.extend(
        [
            "",
            "INCLUSION CRITERIA",
            "-" * 40,
        ]
    )
    for i, criterion in enumerate(config.inclusion_criteria, 1):
        category = f" [{criterion.category}]" if criterion.category else ""
        lines.append(f"  {i}. {criterion.criterion}{category}")
        lines.append(f"     Rationale: {criterion.rationale}")

    # Exclusion criteria
    lines.extend(
        [
            "",
            "EXCLUSION CRITERIA",
            "-" * 40,
        ]
    )
    for i, criterion in enumerate(config.exclusion_criteria, 1):
        category = f" [{criterion.category}]" if criterion.category else ""
        lines.append(f"  {i}. {criterion.criterion}{category}")
        lines.append(f"     Rationale: {criterion.rationale}")

    # Protocol registration
    if config.protocol_registration:
        lines.extend(
            [
                "",
                "PROTOCOL REGISTRATION",
                "-" * 40,
                f"  {config.protocol_registration}",
            ]
        )

    # Team
    if config.team_members:
        lines.extend(
            [
                "",
                "TEAM MEMBERS",
                "-" * 40,
            ]
        )
        for member in config.team_members:
            lines.append(f"  - {member}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Example usage and demonstration."""
    print("Review Configuration Demo")
    print("=" * 60)

    # Create example configuration
    config = ReviewConfig(
        title="Effects of exercise interventions on depression in older adults: A systematic review",
        review_type="systematic",
        research_question={
            "population": "Adults aged 65 and older with depression",
            "intervention": "Exercise interventions (aerobic, resistance, or combined)",
            "comparison": "Usual care, no intervention, or waitlist control",
            "outcome": "Depression symptoms measured by validated scales",
        },
        question_type="PICO",
        domain="biomedical",
        subdomain="clinical",
        date_range_start=date(2010, 1, 1),
        date_range_end=date(2024, 12, 31),
        inclusion_criteria=[
            Criterion(
                criterion="Randomized controlled trials only",
                rationale="RCTs provide highest quality evidence for intervention effectiveness",
                category="study design",
            ),
            Criterion(
                criterion="Participants aged 65 years or older",
                rationale="Focus on geriatric population with unique physiological considerations",
                category="population",
            ),
            Criterion(
                criterion="Depression diagnosis or clinically significant symptoms",
                rationale="Ensures population has condition of interest",
                category="population",
            ),
        ],
        exclusion_criteria=[
            Criterion(
                criterion="Studies with <20 participants per arm",
                rationale="Insufficient statistical power for reliable effect estimates",
                category="study design",
            ),
            Criterion(
                criterion="Non-English language publications",
                rationale="Resource limitations for translation",
                category="publication",
            ),
        ],
        databases=["PubMed", "Cochrane Library", "PsycINFO", "CINAHL"],
        protocol_registration="PROSPERO: CRD42024XXXXXX",
        team_members=["Dr. Jane Smith (PI)", "John Doe (Screening)", "Dr. Alice Johnson (QA)"],
    )

    # Validate
    print("\nValidation:")
    errors = config.validate()
    if errors:
        print("  Errors found:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  Configuration is valid!")

    # Preflight check
    print("\nPreflight Check:")
    preflight = preflight_check(config)
    print(f"  Ready to start: {preflight.is_ready()}")
    print(f"  Database coverage: {preflight.database_coverage['total_databases']} databases")
    if preflight.recommendations:
        print("  Recommendations:")
        for rec in preflight.recommendations:
            print(f"    - {rec}")

    # Generate protocol
    print("\n" + "=" * 60)
    print("Generated Protocol Template:\n")
    print(generate_protocol_template(config))


if __name__ == "__main__":
    main()
