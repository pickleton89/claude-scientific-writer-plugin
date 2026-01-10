"""Utility modules for code documentation validation."""

from .readme_checker import (
    ProjectType,
    ReadmeValidation,
    SectionStatus,
    validate_readme_sections,
    detect_project_type,
    get_required_sections,
)
from .docstring_validator import (
    DocstringStyle,
    DocstringValidation,
    ValidationSeverity,
    validate_docstring_format,
    run_pydocstyle,
    run_doctests,
)
from .infer_style import (
    InferredStyle,
    Language,
    ProjectAnalysis,
    StyleDetectionResult,
    analyze_project,
    detect_existing_style,
    infer_docstring_style,
    format_analysis_report,
)

__all__ = [
    # README validation
    "ProjectType",
    "ReadmeValidation",
    "SectionStatus",
    "validate_readme_sections",
    "detect_project_type",
    "get_required_sections",
    # Docstring validation
    "DocstringStyle",
    "DocstringValidation",
    "ValidationSeverity",
    "validate_docstring_format",
    "run_pydocstyle",
    "run_doctests",
    # Style inference
    "InferredStyle",
    "Language",
    "ProjectAnalysis",
    "StyleDetectionResult",
    "analyze_project",
    "detect_existing_style",
    "infer_docstring_style",
    "format_analysis_report",
]
