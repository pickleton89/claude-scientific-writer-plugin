"""
Utility modules for reproducible research validation.

Provides dataclass schemas for structured validation input/output.
"""

try:
    from .schemas import (
        CategoryScore,
        ChecklistItem,
        CodeScanResult,
        DataScanResult,
        DocumentationScanResult,
        EnvironmentScanResult,
        EnvironmentValidationResult,
        ProjectScanResult,
        ReproducibilityAssessment,
        ValidationSummary,
    )
except ImportError:
    from schemas import (
        CategoryScore,
        ChecklistItem,
        CodeScanResult,
        DataScanResult,
        DocumentationScanResult,
        EnvironmentScanResult,
        EnvironmentValidationResult,
        ProjectScanResult,
        ReproducibilityAssessment,
        ValidationSummary,
    )

__all__ = [
    "ChecklistItem",
    "CategoryScore",
    "EnvironmentScanResult",
    "DataScanResult",
    "CodeScanResult",
    "DocumentationScanResult",
    "ReproducibilityAssessment",
    "ProjectScanResult",
    "EnvironmentValidationResult",
    "ValidationSummary",
]
