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
from .output_schema import (
    DocstringStyle as OutputDocstringStyle,
    ProjectType as OutputProjectType,
    DocstringSectionResult,
    ReadmeValidationResult,
    ValidationReport,
    get_section_schema,
    extract_docstring_sections,
    validate_docstring_sections,
    get_readme_template,
    get_required_sections as get_readme_required_sections,
    get_optional_sections,
    normalize_section_name,
    validate_readme_sections as validate_readme_schema,
    create_validation_report,
    format_validation_report,
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
    # Output schema enforcement
    "OutputDocstringStyle",
    "OutputProjectType",
    "DocstringSectionResult",
    "ReadmeValidationResult",
    "ValidationReport",
    "get_section_schema",
    "extract_docstring_sections",
    "validate_docstring_sections",
    "get_readme_template",
    "get_readme_required_sections",
    "get_optional_sections",
    "normalize_section_name",
    "validate_readme_schema",
    "create_validation_report",
    "format_validation_report",
]
