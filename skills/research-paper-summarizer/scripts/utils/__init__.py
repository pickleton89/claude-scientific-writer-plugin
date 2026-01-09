"""
Utility modules for research-paper-summarizer validation.

Provides deterministic validation utilities for research paper summary checks:
- schemas: Dataclasses for structured validation I/O
- statistics: Regex-based statistical value extraction
"""

from .schemas import (
    ValidationResult,
    ValidationStatus,
    SectionMarker,
    MarkerStatus,
    StatisticResult,
    StatisticType,
    SummaryValidationReport,
    ArticleType,
    ArticleTypeResult,
    YAMLValidationResult,
)
from .statistics import (
    STAT_PATTERNS,
    extract_statistics,
    summarize_statistics,
    normalize_statistic,
)

__all__ = [
    # schemas
    "ValidationResult",
    "ValidationStatus",
    "SectionMarker",
    "MarkerStatus",
    "StatisticResult",
    "StatisticType",
    "SummaryValidationReport",
    "ArticleType",
    "ArticleTypeResult",
    "YAMLValidationResult",
    # statistics
    "STAT_PATTERNS",
    "extract_statistics",
    "summarize_statistics",
    "normalize_statistic",
]
