#!/usr/bin/env python3
"""
Exit Criteria Checker

Validates stage completion criteria for systematic review workflows.
Ensures each review stage meets documented thresholds before progression.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Any
from enum import Enum
import json


# Type definitions
ReviewStage = Literal[
    "planning",
    "search",
    "screening_title",
    "screening_abstract",
    "screening_fulltext",
    "data_extraction",
    "quality_assessment",
    "synthesis",
    "reporting",
]

ReviewType = Literal["systematic", "scoping", "narrative", "rapid"]


class CriterionStatus(Enum):
    """Status of an exit criterion check."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"


# Exit criteria thresholds from skill documentation
STAGE_CRITERIA: dict[str, dict[str, Any]] = {
    "planning": {
        "description": "Protocol and methodology planning",
        "criteria": {
            "protocol_registered": {
                "description": "Protocol registered (e.g., PROSPERO, OSF)",
                "required_for": ["systematic"],
                "recommended_for": ["scoping", "rapid"],
            },
            "research_question_defined": {
                "description": "Research question in PICO/PEO/SPIDER format",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "databases_selected": {
                "description": "Minimum databases selected",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
                "thresholds": {
                    "systematic": 3,
                    "scoping": 2,
                    "rapid": 2,
                    "narrative": 2,
                },
            },
            "inclusion_criteria_defined": {
                "description": "Inclusion/exclusion criteria documented",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
        },
    },
    "search": {
        "description": "Literature search execution",
        "criteria": {
            "all_databases_searched": {
                "description": "Search executed in all selected databases",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "search_saturation": {
                "description": "Search saturation achieved (<5% new papers)",
                "threshold": 0.05,
                "required_for": ["systematic", "scoping"],
            },
            "search_documented": {
                "description": "Full search strategy documented",
                "required_for": ["systematic", "scoping", "rapid"],
            },
            "minimum_papers": {
                "description": "Minimum papers retrieved",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
                "thresholds": {
                    "systematic": 30,
                    "scoping": 20,
                    "rapid": 10,
                    "narrative": 5,
                },
            },
        },
    },
    "screening_title": {
        "description": "Title screening stage",
        "criteria": {
            "all_titles_screened": {
                "description": "All titles reviewed",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "screening_time_compliance": {
                "description": "Average screening time ≤15 seconds",
                "threshold": 15,
                "required_for": ["systematic", "scoping"],
            },
        },
    },
    "screening_abstract": {
        "description": "Abstract screening stage",
        "criteria": {
            "all_abstracts_screened": {
                "description": "All abstracts reviewed",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "dual_screening_performed": {
                "description": "Dual independent screening completed",
                "required_for": ["systematic"],
                "recommended_for": ["scoping"],
            },
            "inter_rater_agreement": {
                "description": "Cohen's kappa ≥0.8",
                "threshold": 0.8,
                "required_for": ["systematic"],
                "recommended_for": ["scoping"],
            },
            "conflicts_resolved": {
                "description": "All screening conflicts resolved",
                "required_for": ["systematic", "scoping"],
            },
            "screening_time_compliance": {
                "description": "Average screening time ≤2 minutes",
                "threshold": 120,
                "required_for": ["systematic", "scoping"],
            },
        },
    },
    "screening_fulltext": {
        "description": "Full-text screening stage",
        "criteria": {
            "all_fulltexts_assessed": {
                "description": "All full texts retrieved and assessed",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "retrieval_rate": {
                "description": "Full-text retrieval rate ≥95%",
                "threshold": 0.95,
                "required_for": ["systematic"],
                "recommended_for": ["scoping", "rapid"],
            },
            "exclusion_reasons_documented": {
                "description": "All exclusion reasons documented",
                "required_for": ["systematic", "scoping", "rapid"],
            },
        },
    },
    "data_extraction": {
        "description": "Data extraction stage",
        "criteria": {
            "all_data_extracted": {
                "description": "Data extracted from all included studies",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "dual_extraction_performed": {
                "description": "Dual independent extraction (sample or full)",
                "required_for": ["systematic"],
            },
            "extraction_form_complete": {
                "description": "All required fields populated",
                "required_for": ["systematic", "scoping", "rapid"],
            },
        },
    },
    "quality_assessment": {
        "description": "Quality/risk of bias assessment",
        "criteria": {
            "all_studies_assessed": {
                "description": "Quality assessed for all included studies",
                "required_for": ["systematic", "rapid"],
            },
            "appropriate_tools_used": {
                "description": "Validated quality tools used (RoB2, NOS, etc.)",
                "required_for": ["systematic"],
                "recommended_for": ["rapid"],
            },
            "dual_assessment_performed": {
                "description": "Dual independent assessment",
                "required_for": ["systematic"],
            },
        },
    },
    "synthesis": {
        "description": "Evidence synthesis stage",
        "criteria": {
            "synthesis_method_appropriate": {
                "description": "Synthesis method matches data type",
                "required_for": ["systematic", "scoping", "rapid", "narrative"],
            },
            "heterogeneity_assessed": {
                "description": "Heterogeneity assessed for meta-analysis",
                "required_for": ["systematic"],
            },
            "sensitivity_analyses_performed": {
                "description": "Sensitivity analyses completed",
                "recommended_for": ["systematic"],
            },
        },
    },
    "reporting": {
        "description": "Final reporting stage",
        "criteria": {
            "prisma_complete": {
                "description": "PRISMA flow diagram completed",
                "required_for": ["systematic", "scoping"],
                "recommended_for": ["rapid"],
            },
            "prisma_numbers_validated": {
                "description": "PRISMA numbers arithmetically validated",
                "required_for": ["systematic", "scoping"],
            },
            "all_citations_verified": {
                "description": "All citations verified via DOI/CrossRef",
                "required_for": ["systematic"],
                "recommended_for": ["scoping", "rapid"],
            },
        },
    },
}


@dataclass
class CriterionResult:
    """Result of checking a single exit criterion."""

    criterion_id: str
    description: str
    status: CriterionStatus
    actual_value: Optional[Any] = None
    threshold: Optional[Any] = None
    message: str = ""
    is_required: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "criterion_id": self.criterion_id,
            "description": self.description,
            "status": self.status.value,
            "actual_value": self.actual_value,
            "threshold": self.threshold,
            "message": self.message,
            "is_required": self.is_required,
        }


@dataclass
class StageCheckResult:
    """Result of checking all exit criteria for a stage."""

    stage: ReviewStage
    review_type: ReviewType
    criteria_results: list[CriterionResult] = field(default_factory=list)
    checked_at: str = ""

    def is_complete(self) -> bool:
        """Check if stage can be considered complete."""
        required_results = [r for r in self.criteria_results if r.is_required]
        return all(r.status == CriterionStatus.PASSED for r in required_results)

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(r.status == CriterionStatus.WARNING for r in self.criteria_results)

    def get_failed(self) -> list[CriterionResult]:
        """Get failed criteria."""
        return [r for r in self.criteria_results if r.status == CriterionStatus.FAILED]

    def get_warnings(self) -> list[CriterionResult]:
        """Get warning criteria."""
        return [r for r in self.criteria_results if r.status == CriterionStatus.WARNING]

    def get_summary(self) -> dict:
        """Get summary statistics."""
        return {
            "stage": self.stage,
            "review_type": self.review_type,
            "is_complete": self.is_complete(),
            "total_criteria": len(self.criteria_results),
            "passed": sum(1 for r in self.criteria_results if r.status == CriterionStatus.PASSED),
            "failed": sum(1 for r in self.criteria_results if r.status == CriterionStatus.FAILED),
            "warnings": sum(1 for r in self.criteria_results if r.status == CriterionStatus.WARNING),
            "pending": sum(1 for r in self.criteria_results if r.status == CriterionStatus.PENDING),
            "not_applicable": sum(
                1 for r in self.criteria_results if r.status == CriterionStatus.NOT_APPLICABLE
            ),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "stage": self.stage,
            "review_type": self.review_type,
            "checked_at": self.checked_at,
            "criteria_results": [r.to_dict() for r in self.criteria_results],
            "summary": self.get_summary(),
        }


@dataclass
class StageData:
    """
    Data for evaluating stage exit criteria.

    Collects metrics and status for a review stage.
    """

    stage: ReviewStage
    review_type: ReviewType

    # Planning data
    protocol_registered: bool = False
    protocol_id: str = ""
    research_question_format: str = ""  # PICO, PEO, SPIDER
    databases_selected: list[str] = field(default_factory=list)
    inclusion_criteria_count: int = 0
    exclusion_criteria_count: int = 0

    # Search data
    databases_searched: list[str] = field(default_factory=list)
    total_papers_retrieved: int = 0
    new_papers_last_iteration: int = 0
    previous_total: int = 0
    search_documented: bool = False

    # Screening data
    total_to_screen: int = 0
    screened_count: int = 0
    dual_screening_performed: bool = False
    kappa_score: Optional[float] = None
    conflicts_count: int = 0
    conflicts_resolved: int = 0
    average_screening_time: Optional[float] = None

    # Full-text data
    fulltexts_sought: int = 0
    fulltexts_retrieved: int = 0
    fulltexts_assessed: int = 0
    exclusions_documented: int = 0
    exclusions_total: int = 0

    # Data extraction
    studies_to_extract: int = 0
    studies_extracted: int = 0
    dual_extraction_performed: bool = False
    required_fields: int = 0
    completed_fields: int = 0

    # Quality assessment
    studies_to_assess: int = 0
    studies_assessed: int = 0
    quality_tools_used: list[str] = field(default_factory=list)
    dual_qa_performed: bool = False

    # Synthesis
    synthesis_method: str = ""
    heterogeneity_assessed: bool = False
    sensitivity_analyses_done: bool = False

    # Reporting
    prisma_complete: bool = False
    prisma_validated: bool = False
    citations_verified: bool = False


def check_stage_criteria(data: StageData) -> StageCheckResult:
    """
    Check exit criteria for a review stage.

    Args:
        data: StageData with metrics for evaluation

    Returns:
        StageCheckResult with all criterion evaluations
    """
    from datetime import datetime

    result = StageCheckResult(
        stage=data.stage,
        review_type=data.review_type,
        checked_at=datetime.now().isoformat(),
    )

    stage_config = STAGE_CRITERIA.get(data.stage, {})
    criteria = stage_config.get("criteria", {})

    for criterion_id, criterion_config in criteria.items():
        criterion_result = _evaluate_criterion(criterion_id, criterion_config, data)
        result.criteria_results.append(criterion_result)

    return result


def _evaluate_criterion(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Evaluate a single criterion."""
    description = config.get("description", criterion_id)

    # Determine if required for this review type
    required_for = config.get("required_for", [])
    recommended_for = config.get("recommended_for", [])

    is_required = data.review_type in required_for
    is_recommended = data.review_type in recommended_for

    if not is_required and not is_recommended:
        return CriterionResult(
            criterion_id=criterion_id,
            description=description,
            status=CriterionStatus.NOT_APPLICABLE,
            message=f"Not applicable for {data.review_type} reviews",
            is_required=False,
        )

    # Evaluate based on criterion type
    evaluator = CRITERION_EVALUATORS.get(criterion_id, _default_evaluator)
    result = evaluator(criterion_id, config, data)
    result.is_required = is_required

    # Convert passed to warning if only recommended
    if result.status == CriterionStatus.FAILED and not is_required:
        result.status = CriterionStatus.WARNING
        result.message = f"Recommended: {result.message}"

    return result


def _default_evaluator(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Default evaluator for simple boolean criteria."""
    return CriterionResult(
        criterion_id=criterion_id,
        description=config.get("description", criterion_id),
        status=CriterionStatus.PENDING,
        message="Manual verification required",
    )


def _check_protocol_registered(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check protocol registration."""
    if data.protocol_registered:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=data.protocol_id,
            message=f"Protocol registered: {data.protocol_id}",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        message="Protocol not registered",
    )


def _check_research_question(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check research question format."""
    valid_formats = ["PICO", "PEO", "SPIDER"]
    if data.research_question_format.upper() in valid_formats:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=data.research_question_format,
            message=f"Research question in {data.research_question_format} format",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=data.research_question_format,
        message="Research question not in valid format (PICO/PEO/SPIDER)",
    )


def _check_databases_selected(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check minimum databases selected."""
    thresholds = config.get("thresholds", {})
    required = thresholds.get(data.review_type, 2)
    actual = len(data.databases_selected)

    if actual >= required:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=actual,
            threshold=required,
            message=f"{actual} databases selected (minimum {required})",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=actual,
        threshold=required,
        message=f"Only {actual} databases selected, need at least {required}",
    )


def _check_inclusion_criteria(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check inclusion/exclusion criteria defined."""
    has_inclusion = data.inclusion_criteria_count > 0
    has_exclusion = data.exclusion_criteria_count > 0

    if has_inclusion and has_exclusion:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value={
                "inclusion": data.inclusion_criteria_count,
                "exclusion": data.exclusion_criteria_count,
            },
            message=f"{data.inclusion_criteria_count} inclusion, {data.exclusion_criteria_count} exclusion criteria",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        message="Missing inclusion or exclusion criteria",
    )


def _check_all_databases_searched(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check all selected databases have been searched."""
    selected = set(data.databases_selected)
    searched = set(data.databases_searched)
    missing = selected - searched

    if not missing:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=len(searched),
            message=f"All {len(searched)} databases searched",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=list(searched),
        message=f"Missing searches: {', '.join(missing)}",
    )


def _check_search_saturation(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check search saturation (<5% new papers)."""
    threshold = config.get("threshold", 0.05)

    if data.previous_total == 0:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PENDING,
            message="Need multiple search iterations to assess saturation",
        )

    new_rate = data.new_papers_last_iteration / data.previous_total if data.previous_total > 0 else 0

    if new_rate <= threshold:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=round(new_rate * 100, 1),
            threshold=threshold * 100,
            message=f"Saturation achieved: {new_rate*100:.1f}% new papers",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=round(new_rate * 100, 1),
        threshold=threshold * 100,
        message=f"Not saturated: {new_rate*100:.1f}% new papers (target <{threshold*100}%)",
    )


def _check_minimum_papers(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check minimum papers retrieved."""
    thresholds = config.get("thresholds", {})
    required = thresholds.get(data.review_type, 10)
    actual = data.total_papers_retrieved

    if actual >= required:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=actual,
            threshold=required,
            message=f"{actual} papers retrieved (minimum {required})",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=actual,
        threshold=required,
        message=f"Only {actual} papers retrieved, need at least {required}",
    )


def _check_all_screened(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check all items have been screened."""
    if data.total_to_screen == 0:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PENDING,
            message="No items to screen",
        )

    if data.screened_count >= data.total_to_screen:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=data.screened_count,
            threshold=data.total_to_screen,
            message=f"All {data.total_to_screen} items screened",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=data.screened_count,
        threshold=data.total_to_screen,
        message=f"Screened {data.screened_count}/{data.total_to_screen}",
    )


def _check_screening_time(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check average screening time compliance."""
    threshold = config.get("threshold", 120)

    if data.average_screening_time is None:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PENDING,
            message="No screening time data",
        )

    if data.average_screening_time <= threshold:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=round(data.average_screening_time, 1),
            threshold=threshold,
            message=f"Average {data.average_screening_time:.1f}s (limit {threshold}s)",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.WARNING,
        actual_value=round(data.average_screening_time, 1),
        threshold=threshold,
        message=f"Average {data.average_screening_time:.1f}s exceeds {threshold}s limit",
    )


def _check_dual_screening(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check dual screening performed."""
    if data.dual_screening_performed:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            message="Dual independent screening completed",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        message="Dual screening not performed",
    )


def _check_inter_rater_agreement(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check inter-rater agreement (kappa)."""
    threshold = config.get("threshold", 0.8)

    if data.kappa_score is None:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PENDING,
            message="Kappa not calculated",
        )

    if data.kappa_score >= threshold:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=round(data.kappa_score, 3),
            threshold=threshold,
            message=f"Kappa = {data.kappa_score:.3f} (threshold {threshold})",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=round(data.kappa_score, 3),
        threshold=threshold,
        message=f"Kappa = {data.kappa_score:.3f} below threshold {threshold}",
    )


def _check_conflicts_resolved(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check all conflicts resolved."""
    if data.conflicts_count == 0:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            message="No conflicts to resolve",
        )

    if data.conflicts_resolved >= data.conflicts_count:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=data.conflicts_resolved,
            threshold=data.conflicts_count,
            message=f"All {data.conflicts_count} conflicts resolved",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=data.conflicts_resolved,
        threshold=data.conflicts_count,
        message=f"Resolved {data.conflicts_resolved}/{data.conflicts_count} conflicts",
    )


def _check_retrieval_rate(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check full-text retrieval rate."""
    threshold = config.get("threshold", 0.95)

    if data.fulltexts_sought == 0:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PENDING,
            message="No full-texts sought",
        )

    rate = data.fulltexts_retrieved / data.fulltexts_sought

    if rate >= threshold:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=round(rate * 100, 1),
            threshold=threshold * 100,
            message=f"Retrieval rate {rate*100:.1f}% (target ≥{threshold*100}%)",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.WARNING,
        actual_value=round(rate * 100, 1),
        threshold=threshold * 100,
        message=f"Retrieval rate {rate*100:.1f}% below target {threshold*100}%",
    )


def _check_exclusions_documented(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check exclusion reasons documented."""
    if data.exclusions_total == 0:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            message="No exclusions to document",
        )

    if data.exclusions_documented >= data.exclusions_total:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            actual_value=data.exclusions_documented,
            message=f"All {data.exclusions_total} exclusions documented",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        actual_value=data.exclusions_documented,
        threshold=data.exclusions_total,
        message=f"Documented {data.exclusions_documented}/{data.exclusions_total} exclusions",
    )


def _check_prisma_complete(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check PRISMA diagram complete."""
    if data.prisma_complete:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            message="PRISMA flow diagram completed",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        message="PRISMA flow diagram not complete",
    )


def _check_prisma_validated(
    criterion_id: str,
    config: dict,
    data: StageData,
) -> CriterionResult:
    """Check PRISMA numbers validated."""
    if data.prisma_validated:
        return CriterionResult(
            criterion_id=criterion_id,
            description=config["description"],
            status=CriterionStatus.PASSED,
            message="PRISMA numbers arithmetically validated",
        )
    return CriterionResult(
        criterion_id=criterion_id,
        description=config["description"],
        status=CriterionStatus.FAILED,
        message="PRISMA numbers not validated",
    )


# Register criterion evaluators
CRITERION_EVALUATORS = {
    "protocol_registered": _check_protocol_registered,
    "research_question_defined": _check_research_question,
    "databases_selected": _check_databases_selected,
    "inclusion_criteria_defined": _check_inclusion_criteria,
    "all_databases_searched": _check_all_databases_searched,
    "search_saturation": _check_search_saturation,
    "search_documented": _default_evaluator,
    "minimum_papers": _check_minimum_papers,
    "all_titles_screened": _check_all_screened,
    "all_abstracts_screened": _check_all_screened,
    "all_fulltexts_assessed": _check_all_screened,
    "screening_time_compliance": _check_screening_time,
    "dual_screening_performed": _check_dual_screening,
    "inter_rater_agreement": _check_inter_rater_agreement,
    "conflicts_resolved": _check_conflicts_resolved,
    "retrieval_rate": _check_retrieval_rate,
    "exclusion_reasons_documented": _check_exclusions_documented,
    "all_data_extracted": _default_evaluator,
    "dual_extraction_performed": _default_evaluator,
    "extraction_form_complete": _default_evaluator,
    "all_studies_assessed": _default_evaluator,
    "appropriate_tools_used": _default_evaluator,
    "dual_assessment_performed": _default_evaluator,
    "synthesis_method_appropriate": _default_evaluator,
    "heterogeneity_assessed": _default_evaluator,
    "sensitivity_analyses_performed": _default_evaluator,
    "prisma_complete": _check_prisma_complete,
    "prisma_numbers_validated": _check_prisma_validated,
    "all_citations_verified": _default_evaluator,
}


def get_stage_requirements(stage: ReviewStage, review_type: ReviewType) -> dict:
    """
    Get requirements for a specific stage and review type.

    Args:
        stage: Review stage
        review_type: Type of review

    Returns:
        Dictionary with required and recommended criteria
    """
    stage_config = STAGE_CRITERIA.get(stage, {})
    criteria = stage_config.get("criteria", {})

    required = []
    recommended = []

    for criterion_id, config in criteria.items():
        if review_type in config.get("required_for", []):
            required.append({
                "id": criterion_id,
                "description": config.get("description", criterion_id),
            })
        elif review_type in config.get("recommended_for", []):
            recommended.append({
                "id": criterion_id,
                "description": config.get("description", criterion_id),
            })

    return {
        "stage": stage,
        "review_type": review_type,
        "description": stage_config.get("description", stage),
        "required_criteria": required,
        "recommended_criteria": recommended,
    }


def get_all_stages() -> list[str]:
    """Get list of all defined stages."""
    return list(STAGE_CRITERIA.keys())


def load_check_from_json(filepath: str) -> StageCheckResult:
    """Load stage check result from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = StageCheckResult(
        stage=data.get("stage", "planning"),
        review_type=data.get("review_type", "systematic"),
        checked_at=data.get("checked_at", ""),
    )

    for cr_data in data.get("criteria_results", []):
        cr = CriterionResult(
            criterion_id=cr_data.get("criterion_id", ""),
            description=cr_data.get("description", ""),
            status=CriterionStatus(cr_data.get("status", "pending")),
            actual_value=cr_data.get("actual_value"),
            threshold=cr_data.get("threshold"),
            message=cr_data.get("message", ""),
            is_required=cr_data.get("is_required", True),
        )
        result.criteria_results.append(cr)

    return result


def save_check_to_json(result: StageCheckResult, filepath: str) -> None:
    """Save stage check result to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)


def generate_exit_report(result: StageCheckResult) -> str:
    """
    Generate a text-based exit criteria report.

    Args:
        result: StageCheckResult to report on

    Returns:
        Formatted report string
    """
    summary = result.get_summary()

    lines = [
        "EXIT CRITERIA REPORT",
        "=" * 60,
        "",
        f"Stage: {result.stage}",
        f"Review Type: {result.review_type}",
        f"Checked: {result.checked_at}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Stage Complete: {'YES' if result.is_complete() else 'NO'}",
        f"Total Criteria: {summary['total_criteria']}",
        f"  Passed: {summary['passed']}",
        f"  Failed: {summary['failed']}",
        f"  Warnings: {summary['warnings']}",
        f"  Pending: {summary['pending']}",
        f"  N/A: {summary['not_applicable']}",
        "",
    ]

    # Group results by status
    failed = result.get_failed()
    warnings = result.get_warnings()

    if failed:
        lines.extend(["FAILED CRITERIA (must fix)", "-" * 40])
        for cr in failed:
            lines.append(f"  [ ] {cr.description}")
            lines.append(f"      {cr.message}")
        lines.append("")

    if warnings:
        lines.extend(["WARNINGS (recommended)", "-" * 40])
        for cr in warnings:
            lines.append(f"  [!] {cr.description}")
            lines.append(f"      {cr.message}")
        lines.append("")

    # Passed criteria
    passed = [r for r in result.criteria_results if r.status == CriterionStatus.PASSED]
    if passed:
        lines.extend(["PASSED CRITERIA", "-" * 40])
        for cr in passed:
            lines.append(f"  [✓] {cr.description}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public wrapper: deep-research Phase 2 search audit
# ---------------------------------------------------------------------------


@dataclass
class PhaseGateResult:
    """Result of a deep-research phase-progression gate check."""

    passed: bool
    phase: str
    required_databases: list[str] = field(default_factory=list)
    searched_databases: list[str] = field(default_factory=list)
    missing_databases: list[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to JSON-serialisable dict."""
        return {
            "passed": self.passed,
            "phase": self.phase,
            "required_databases": list(self.required_databases),
            "searched_databases": list(self.searched_databases),
            "missing_databases": list(self.missing_databases),
            "message": self.message,
        }


def audit_phase_2_search(
    required_databases: list[str],
    searched_databases: list[str],
) -> PhaseGateResult:
    """
    Hard gate for Phase 2 → Phase 3 progression in the deep-research pipeline.

    Wraps the existing :func:`_check_all_databases_searched` private helper
    with a deep-research-tailored input/output shape. The Bibliography agent
    calls this at the end of Phase 2 against the frozen Search Contract; if
    ``passed`` is False, the agent MUST loop back and call missing databases
    before requesting Checkpoint 2.

    Args:
        required_databases: Database names from the frozen Search Contract's
            ``required_databases`` block (each item's ``name`` field).
        searched_databases: Database names that were actually called during
            Phase 2 — typically extracted from the Search Log table.

    Returns:
        ``PhaseGateResult`` with ``passed``, missing-databases list, and a
        human-readable message suitable for surfacing to the user.
    """
    data = StageData(
        stage="search",
        review_type="systematic",
        databases_selected=list(required_databases),
        databases_searched=list(searched_databases),
    )
    config = STAGE_CRITERIA["search"]["criteria"]["all_databases_searched"]
    inner = _check_all_databases_searched(
        criterion_id="all_databases_searched",
        config=config,
        data=data,
    )

    selected_set = set(required_databases)
    searched_set = set(searched_databases)
    missing = sorted(selected_set - searched_set)

    return PhaseGateResult(
        passed=inner.status == CriterionStatus.PASSED,
        phase="phase_2_investigation",
        required_databases=list(required_databases),
        searched_databases=list(searched_databases),
        missing_databases=missing,
        message=inner.message,
    )


def main():
    """Example usage and demonstration."""
    print("Exit Criteria Checker Demo")
    print("=" * 60)

    # Show all stages
    print("\nDefined review stages:")
    for stage in get_all_stages():
        config = STAGE_CRITERIA.get(stage, {})
        print(f"  - {stage}: {config.get('description', '')}")

    # Show requirements for systematic review search stage
    print("\n" + "=" * 60)
    print("Requirements for systematic review - search stage:")
    reqs = get_stage_requirements("search", "systematic")
    print(f"\nRequired ({len(reqs['required_criteria'])}):")
    for r in reqs["required_criteria"]:
        print(f"  - {r['description']}")
    print(f"\nRecommended ({len(reqs['recommended_criteria'])}):")
    for r in reqs["recommended_criteria"]:
        print(f"  - {r['description']}")

    # Example check
    print("\n" + "=" * 60)
    print("Example: Checking screening stage completion")
    print("-" * 40)

    data = StageData(
        stage="screening_abstract",
        review_type="systematic",
        total_to_screen=100,
        screened_count=100,
        dual_screening_performed=True,
        kappa_score=0.85,
        conflicts_count=15,
        conflicts_resolved=15,
        average_screening_time=90.5,
    )

    result = check_stage_criteria(data)
    print(generate_exit_report(result))


if __name__ == "__main__":
    main()
