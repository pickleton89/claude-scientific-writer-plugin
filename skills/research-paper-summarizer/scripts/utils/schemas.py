"""
Data schemas for research paper summarizer validation.

Provides structured dataclasses for:
- Validation results (pass/warn/fail)
- Section marker tracking (pending/complete/skipped)
- Statistics extraction results
- Article type detection
- Summary quality reports
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ValidationStatus(Enum):
    """Status levels for validation checks."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class MarkerStatus(Enum):
    """Status levels for section markers."""

    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


class StatisticType(Enum):
    """Types of statistics that can be extracted."""

    P_VALUE = "p_value"
    CONFIDENCE_INTERVAL = "confidence_interval"
    SAMPLE_SIZE = "sample_size"
    FOLD_CHANGE = "fold_change"
    HAZARD_RATIO = "hazard_ratio"
    ODDS_RATIO = "odds_ratio"
    PERCENT_CHANGE = "percent_change"
    EFFECT_SIZE = "effect_size"
    CORRELATION = "correlation"
    MEAN_SD = "mean_sd"


class ArticleType(Enum):
    """Supported article types for summarization."""

    GENERAL = "general"
    REVIEW = "review"
    COMPBIO = "compbio"
    CELLMOLBIO = "cellmolbio"


# ============================================================================
# Validation Result Schemas
# ============================================================================


@dataclass
class ValidationResult:
    """Result for a single validation check."""

    name: str
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationResult":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            passed=data.get("passed", False),
            message=data.get("message", ""),
            severity=data.get("severity", "info"),
        )


@dataclass
class SectionMarker:
    """Represents a section marker in the summary document."""

    name: str
    marker_type: str  # 'section' or 'subsection'
    status: MarkerStatus
    position: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "marker_type": self.marker_type,
            "status": self.status.value,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SectionMarker":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            marker_type=data.get("marker_type", "section"),
            status=MarkerStatus(data.get("status", "pending")),
            position=data.get("position", 0),
        )


# ============================================================================
# Statistics Schemas
# ============================================================================


@dataclass
class StatisticResult:
    """Represents an extracted statistic from text."""

    stat_type: StatisticType
    value: str  # The raw extracted value
    normalized: str  # Standardized format
    context: str  # Surrounding text
    position: int  # Character position in document

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.stat_type.value,
            "value": self.value,
            "normalized": self.normalized,
            "context": self.context,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatisticResult":
        """Create from dictionary."""
        return cls(
            stat_type=StatisticType(data.get("type", "p_value")),
            value=data.get("value", ""),
            normalized=data.get("normalized", ""),
            context=data.get("context", ""),
            position=data.get("position", 0),
        )


# ============================================================================
# Article Type Detection Schemas
# ============================================================================


@dataclass
class ArticleTypeResult:
    """Result of article type detection."""

    detected_type: ArticleType
    confidence: float  # 0.0 to 1.0
    scores: dict[str, int]  # Scores for each type
    matched_keywords: dict[str, list[str]]  # Keywords matched per type

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "detected_type": self.detected_type.value,
            "confidence": self.confidence,
            "scores": self.scores,
            "matched_keywords": self.matched_keywords,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArticleTypeResult":
        """Create from dictionary."""
        return cls(
            detected_type=ArticleType(data.get("detected_type", "general")),
            confidence=data.get("confidence", 0.0),
            scores=data.get("scores", {}),
            matched_keywords=data.get("matched_keywords", {}),
        )


# ============================================================================
# YAML Validation Schemas
# ============================================================================


@dataclass
class YAMLValidationResult:
    """Result of YAML summary validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YAMLValidationResult":
        """Create from dictionary."""
        return cls(
            valid=data.get("valid", False),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            data=data.get("data", {}),
        )


# ============================================================================
# Summary Validation Report
# ============================================================================


@dataclass
class SummaryValidationReport:
    """
    Complete validation report for a research paper summary.

    Aggregates all validation checks into a single structured report.
    """

    # Metadata
    summary_path: str
    validation_timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # Overall status
    valid: bool = True
    score: float = 0.0  # 0.0 to 1.0

    # Individual check results
    checks: list[ValidationResult] = field(default_factory=list)

    # Section markers
    markers: list[SectionMarker] = field(default_factory=list)
    pending_count: int = 0
    complete_count: int = 0

    # Statistics found
    statistics: list[StatisticResult] = field(default_factory=list)
    stat_count: int = 0

    # Content metrics
    figure_ref_count: int = 0
    quote_count: int = 0
    placeholder_count: int = 0

    # Issues
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_check(self, check: ValidationResult) -> None:
        """Add a validation check result."""
        self.checks.append(check)
        if not check.passed and check.severity == "error":
            self.valid = False

    def add_error(self, message: str) -> None:
        """Add an error and mark report as failed."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning (does not affect overall pass status)."""
        self.warnings.append(message)

    def calculate_score(self) -> float:
        """Calculate validation score based on check results."""
        if not self.checks:
            return 0.0
        passed = sum(1 for c in self.checks if c.passed)
        self.score = passed / len(self.checks)
        return self.score

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary_path": self.summary_path,
            "validation_timestamp": self.validation_timestamp,
            "valid": self.valid,
            "score": self.score,
            "checks": [c.to_dict() for c in self.checks],
            "markers": {
                "items": [m.to_dict() for m in self.markers],
                "pending": self.pending_count,
                "complete": self.complete_count,
            },
            "statistics": {
                "count": self.stat_count,
                "items": [s.to_dict() for s in self.statistics],
            },
            "content": {
                "figure_refs": self.figure_ref_count,
                "quotes": self.quote_count,
                "placeholders": self.placeholder_count,
            },
            "errors": self.errors,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SummaryValidationReport":
        """Create SummaryValidationReport from dictionary."""
        report = cls(
            summary_path=data.get("summary_path", ""),
            validation_timestamp=data.get(
                "validation_timestamp", datetime.now().isoformat()
            ),
            valid=data.get("valid", True),
            score=data.get("score", 0.0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )

        # Restore checks
        for check_data in data.get("checks", []):
            report.checks.append(ValidationResult.from_dict(check_data))

        # Restore markers
        markers_data = data.get("markers", {})
        for marker_data in markers_data.get("items", []):
            report.markers.append(SectionMarker.from_dict(marker_data))
        report.pending_count = markers_data.get("pending", 0)
        report.complete_count = markers_data.get("complete", 0)

        # Restore statistics
        stats_data = data.get("statistics", {})
        report.stat_count = stats_data.get("count", 0)
        for stat_data in stats_data.get("items", []):
            report.statistics.append(StatisticResult.from_dict(stat_data))

        # Restore content metrics
        content_data = data.get("content", {})
        report.figure_ref_count = content_data.get("figure_refs", 0)
        report.quote_count = content_data.get("quotes", 0)
        report.placeholder_count = content_data.get("placeholders", 0)

        return report
