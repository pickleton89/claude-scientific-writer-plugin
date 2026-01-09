"""
Dataclass schemas for reproducible research validation.

Provides structured types for validation input/output, ensuring
deterministic serialization and type safety.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ChecklistItem:
    """Single item from the 20-point reproducibility checklist."""

    id: str
    category: str
    points: int
    status: bool
    max_points: int = 0

    def __post_init__(self) -> None:
        # If max_points not provided, infer from points (for passing items)
        # or keep as-is (for failing items where points=0 but max_points should be set)
        if self.max_points == 0 and self.points > 0:
            self.max_points = self.points
        # Recalculate actual points based on status
        self.points = self.max_points if self.status else 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ChecklistItem":
        return cls(**data)


@dataclass
class CategoryScore:
    """Score for a single category (environment, data, code, documentation)."""

    name: str
    score: int
    max_score: int = 25

    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryScore":
        return cls(
            name=data["name"],
            score=data["score"],
            max_score=data.get("max_score", 25),
        )


@dataclass
class EnvironmentScanResult:
    """Results from scanning environment configuration."""

    env_file_present: bool = False
    env_file_type: Optional[str] = None
    versions_pinned: bool = False
    pinned_percentage: float = 0.0
    python_version_specified: bool = False
    system_requirements_documented: bool = False
    dockerfile_present: bool = False
    dockerfile_pinned: bool = False
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentScanResult":
        return cls(**data)


@dataclass
class DataScanResult:
    """Results from scanning data management practices."""

    raw_data_archived: bool = False
    data_processing_scripts: bool = False
    random_seeds_set: bool = False
    checksums_present: bool = False
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DataScanResult":
        return cls(**data)


@dataclass
class CodeScanResult:
    """Results from scanning code quality practices."""

    all_code_in_repo: bool = True
    no_hardcoded_paths: bool = True
    readme_present: bool = False
    license_present: bool = False
    hardcoded_paths_found: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CodeScanResult":
        return cls(**data)


@dataclass
class DocumentationScanResult:
    """Results from scanning documentation quality."""

    methods_documented: bool = False
    parameters_documented: bool = False
    expected_outputs_described: bool = False
    execution_order_documented: bool = False
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentationScanResult":
        return cls(**data)


@dataclass
class ReproducibilityAssessment:
    """Complete reproducibility assessment with score and level."""

    score: int
    max_score: int
    percentage: float
    threshold_met: bool
    level: int
    level_name: str
    category_scores: dict[str, CategoryScore] = field(default_factory=dict)
    checklist: list[ChecklistItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "threshold_met": self.threshold_met,
            "level": self.level,
            "level_name": self.level_name,
            "category_scores": {k: v.to_dict() for k, v in self.category_scores.items()},
            "checklist": [item.to_dict() for item in self.checklist],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReproducibilityAssessment":
        category_scores = {
            k: CategoryScore.from_dict(v) for k, v in data.get("category_scores", {}).items()
        }
        checklist = [ChecklistItem.from_dict(item) for item in data.get("checklist", [])]
        return cls(
            score=data["score"],
            max_score=data["max_score"],
            percentage=data["percentage"],
            threshold_met=data["threshold_met"],
            level=data["level"],
            level_name=data["level_name"],
            category_scores=category_scores,
            checklist=checklist,
        )


@dataclass
class ProjectScanResult:
    """Complete project scan results."""

    project_path: str
    environment: EnvironmentScanResult
    data: DataScanResult
    code: CodeScanResult
    documentation: DocumentationScanResult
    assessment: ReproducibilityAssessment
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "project_path": self.project_path,
            "scan_results": {
                "environment": self.environment.to_dict(),
                "data": self.data.to_dict(),
                "code": self.code.to_dict(),
                "documentation": self.documentation.to_dict(),
            },
            "assessment": self.assessment.to_dict(),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectScanResult":
        scan_results = data.get("scan_results", {})
        return cls(
            project_path=data["project_path"],
            environment=EnvironmentScanResult.from_dict(scan_results.get("environment", {})),
            data=DataScanResult.from_dict(scan_results.get("data", {})),
            code=CodeScanResult.from_dict(scan_results.get("code", {})),
            documentation=DocumentationScanResult.from_dict(scan_results.get("documentation", {})),
            assessment=ReproducibilityAssessment.from_dict(data.get("assessment", {})),
            issues=data.get("issues", []),
            recommendations=data.get("recommendations", []),
            error=data.get("error"),
        )


@dataclass
class ValidationSummary:
    """Summary of environment validation results."""

    errors: int
    warnings: int
    deps_count: int = 0
    unpinned_count: int = 0
    loose_pinned_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationSummary":
        return cls(**data)


@dataclass
class EnvironmentValidationResult:
    """Results from validating an environment file."""

    valid: bool
    score: int = 0
    error: Optional[str] = None
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: Optional[ValidationSummary] = None

    def to_dict(self) -> dict:
        result = {
            "valid": self.valid,
            "score": self.score,
            "issues": self.issues,
            "warnings": self.warnings,
        }
        if self.error:
            result["error"] = self.error
        if self.summary:
            result["summary"] = self.summary.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentValidationResult":
        summary = None
        if "summary" in data and data["summary"]:
            summary = ValidationSummary.from_dict(data["summary"])
        return cls(
            valid=data["valid"],
            score=data.get("score", 0),
            error=data.get("error"),
            issues=data.get("issues", []),
            warnings=data.get("warnings", []),
            summary=summary,
        )
