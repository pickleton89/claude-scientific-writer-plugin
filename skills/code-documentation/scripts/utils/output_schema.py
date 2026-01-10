"""Output schema enforcement for code documentation.

This module provides deterministic schema validation for:
- Docstring section ordering (NumPy/Google styles)
- README template selection and section requirements
- Validation report JSON formatting

Examples
--------
>>> from utils.output_schema import validate_docstring_sections, get_readme_template
>>> result = validate_docstring_sections(docstring_text, style="numpy")
>>> template = get_readme_template("analysis")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
import re


class DocstringStyle(Enum):
    """Supported docstring styles."""

    NUMPY = "numpy"
    GOOGLE = "google"
    SPHINX = "sphinx"
    MINIMAL = "minimal"


class ProjectType(Enum):
    """Project types for README template selection."""

    ANALYSIS = "analysis"
    SOFTWARE = "software"
    DATA_REPO = "data_repo"
    COMPENDIUM = "compendium"


# NumPy style section schema with canonical ordering
NUMPY_SECTIONS = {
    "short_summary": {"required": True, "order": 0, "aliases": ["summary"]},
    "extended_summary": {"required": False, "order": 1, "aliases": []},
    "parameters": {
        "required": "if_has_params",
        "order": 2,
        "aliases": ["params", "arguments", "args"],
    },
    "returns": {"required": "if_returns", "order": 3, "aliases": ["return"]},
    "yields": {"required": "if_generator", "order": 4, "aliases": ["yield"]},
    "raises": {"required": False, "order": 5, "aliases": ["exceptions", "except"]},
    "see_also": {"required": False, "order": 6, "aliases": ["see also", "seealso"]},
    "notes": {"required": False, "order": 7, "aliases": ["note"]},
    "references": {"required": False, "order": 8, "aliases": ["refs", "reference"]},
    "examples": {"required": "recommended", "order": 9, "aliases": ["example"]},
}

# Google style section schema
GOOGLE_SECTIONS = {
    "summary": {"required": True, "order": 0, "aliases": ["description"]},
    "args": {
        "required": "if_has_params",
        "order": 1,
        "aliases": ["arguments", "parameters", "params"],
    },
    "returns": {"required": "if_returns", "order": 2, "aliases": ["return"]},
    "yields": {"required": "if_generator", "order": 3, "aliases": ["yield"]},
    "raises": {"required": False, "order": 4, "aliases": ["exceptions", "except"]},
    "attributes": {"required": False, "order": 5, "aliases": ["attrs"]},
    "example": {"required": "recommended", "order": 6, "aliases": ["examples"]},
}

# README section requirements by project type
README_REQUIREMENTS = {
    ProjectType.ANALYSIS: {
        "required": [
            "title",
            "description",
            "data_requirements",
            "environment",
            "usage",
            "output",
        ],
        "optional": ["citation", "license", "contributing"],
        "template_ref": "references/readme_templates.md#analysis-project",
    },
    ProjectType.SOFTWARE: {
        "required": ["title", "description", "installation", "quick_start"],
        "optional": ["documentation", "contributing", "license", "citation", "badges"],
        "template_ref": "references/readme_templates.md#software-tool",
    },
    ProjectType.DATA_REPO: {
        "required": [
            "title",
            "description",
            "data_dictionary",
            "collection_methods",
            "usage_terms",
        ],
        "optional": ["doi", "related_publications", "citation"],
        "template_ref": "references/readme_templates.md#data-repository",
    },
    ProjectType.COMPENDIUM: {
        "required": [
            "title",
            "description",
            "structure",
            "reproduction",
            "dependencies",
        ],
        "optional": ["citation", "license", "data", "results"],
        "template_ref": "references/readme_templates.md#research-compendium",
    },
}

# Section name aliases for README validation
README_SECTION_ALIASES = {
    "title": ["name", "project"],
    "description": ["overview", "about", "introduction", "summary"],
    "installation": ["install", "setup", "getting started"],
    "quick_start": ["quickstart", "quick-start", "getting started"],
    "data_requirements": ["data", "input data", "data sources", "requirements"],
    "environment": ["environment setup", "setup", "dependencies", "requirements"],
    "usage": ["how to use", "running", "execution"],
    "output": ["outputs", "results", "produced files"],
    "data_dictionary": ["schema", "data schema", "columns", "fields"],
    "collection_methods": ["methodology", "data collection", "methods"],
    "usage_terms": ["license", "terms", "terms of use"],
    "structure": ["project structure", "directory structure", "organization"],
    "reproduction": ["reproducing", "how to reproduce", "replication"],
    "dependencies": ["requirements", "prerequisites"],
    "citation": ["cite", "citing", "how to cite", "reference"],
    "contributing": ["contribute", "contributors", "development"],
    "license": ["licensing"],
    "documentation": ["docs", "api", "api documentation"],
    "badges": ["status", "build status"],
}


@dataclass
class SectionValidation:
    """Result of validating a single section."""

    name: str
    present: bool
    order_correct: bool
    actual_order: Optional[int] = None
    expected_order: Optional[int] = None
    content_preview: str = ""


@dataclass
class DocstringSectionResult:
    """Result of docstring section validation."""

    style: DocstringStyle
    sections_found: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)
    order_violations: list[tuple[str, int, int]] = field(default_factory=list)
    is_valid: bool = True
    validations: list[SectionValidation] = field(default_factory=list)


@dataclass
class ReadmeValidationResult:
    """Result of README section validation."""

    project_type: ProjectType
    required_present: list[str] = field(default_factory=list)
    required_missing: list[str] = field(default_factory=list)
    optional_present: list[str] = field(default_factory=list)
    score: float = 0.0
    template_ref: str = ""
    is_valid: bool = True


@dataclass
class ValidationReport:
    """Complete validation report in JSON-serializable format."""

    file: str
    style: Optional[str] = None
    coverage: Optional[dict] = None
    pydocstyle: Optional[dict] = None
    doctests: Optional[dict] = None
    readme_score: Optional[float] = None
    missing_sections: Optional[list[str]] = None
    is_valid: bool = True

    def to_json(self) -> str:
        """Convert report to JSON string."""
        data = {
            "file": self.file,
            "is_valid": self.is_valid,
        }
        if self.style:
            data["style"] = self.style
        if self.coverage:
            data["coverage"] = self.coverage
        if self.pydocstyle:
            data["pydocstyle"] = self.pydocstyle
        if self.doctests:
            data["doctests"] = self.doctests
        if self.readme_score is not None:
            data["readme_score"] = self.readme_score
        if self.missing_sections:
            data["missing_sections"] = self.missing_sections
        return json.dumps(data, indent=2)

    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return json.loads(self.to_json())


def get_section_schema(style: DocstringStyle) -> dict:
    """Get the section schema for a docstring style.

    Parameters
    ----------
    style : DocstringStyle
        The docstring style to get schema for.

    Returns
    -------
    dict
        Section schema with required/optional sections and ordering.

    Examples
    --------
    >>> schema = get_section_schema(DocstringStyle.NUMPY)
    >>> "parameters" in schema
    True
    """
    if style == DocstringStyle.NUMPY:
        return NUMPY_SECTIONS.copy()
    elif style == DocstringStyle.GOOGLE:
        return GOOGLE_SECTIONS.copy()
    else:
        # Minimal/Sphinx return empty schema (no strict requirements)
        return {}


def extract_docstring_sections(docstring: str, style: DocstringStyle) -> list[str]:
    """Extract section names from a docstring.

    Parameters
    ----------
    docstring : str
        The docstring text to parse.
    style : DocstringStyle
        The expected docstring style.

    Returns
    -------
    list[str]
        List of section names found, in order of appearance.

    Examples
    --------
    >>> doc = '''Summary line.
    ...
    ... Parameters
    ... ----------
    ... x : int
    ...     Input value.
    ...
    ... Returns
    ... -------
    ... int
    ...     Output value.
    ... '''
    >>> extract_docstring_sections(doc, DocstringStyle.NUMPY)
    ['short_summary', 'parameters', 'returns']
    """
    sections = []

    if not docstring or not docstring.strip():
        return sections

    lines = docstring.strip().split("\n")

    # First non-empty line is always summary
    for line in lines:
        if line.strip():
            sections.append("short_summary" if style == DocstringStyle.NUMPY else "summary")
            break

    if style == DocstringStyle.NUMPY:
        # NumPy style: Section\n------ (with optional leading whitespace)
        section_pattern = re.compile(r"^\s*(\w[\w\s]*?)\s*\n\s*-{3,}\s*$", re.MULTILINE)
        matches = section_pattern.findall(docstring)
        for match in matches:
            section_name = match.strip().lower().replace(" ", "_")
            # Normalize aliases
            for canonical, info in NUMPY_SECTIONS.items():
                if section_name == canonical or section_name in [
                    a.replace(" ", "_") for a in info.get("aliases", [])
                ]:
                    if canonical not in sections:
                        sections.append(canonical)
                    break

    elif style == DocstringStyle.GOOGLE:
        # Google style: Section:
        section_pattern = re.compile(r"^\s*(Args|Returns|Yields|Raises|Attributes|Example|Examples):\s*$", re.MULTILINE | re.IGNORECASE)
        matches = section_pattern.findall(docstring)
        for match in matches:
            section_name = match.strip().lower()
            # Normalize aliases
            for canonical, info in GOOGLE_SECTIONS.items():
                if section_name == canonical or section_name in [
                    a.lower() for a in info.get("aliases", [])
                ]:
                    if canonical not in sections:
                        sections.append(canonical)
                    break

    return sections


def validate_docstring_sections(
    docstring: str, style: str | DocstringStyle
) -> DocstringSectionResult:
    """Validate docstring sections against schema.

    Parameters
    ----------
    docstring : str
        The docstring text to validate.
    style : str or DocstringStyle
        The docstring style ("numpy", "google", or DocstringStyle enum).

    Returns
    -------
    DocstringSectionResult
        Validation result with found/missing sections and order violations.

    Examples
    --------
    >>> doc = '''Short summary.
    ...
    ... Parameters
    ... ----------
    ... x : int
    ...     Input.
    ... '''
    >>> result = validate_docstring_sections(doc, "numpy")
    >>> result.is_valid
    True
    """
    if isinstance(style, str):
        style = DocstringStyle(style.lower())

    schema = get_section_schema(style)
    found_sections = extract_docstring_sections(docstring, style)

    result = DocstringSectionResult(style=style, sections_found=found_sections)

    if not schema:
        # No schema for minimal/sphinx - always valid
        return result

    # Check for missing required sections
    for section_name, info in schema.items():
        if info["required"] is True and section_name not in found_sections:
            result.sections_missing.append(section_name)
            result.is_valid = False

    # Check ordering
    expected_order = {name: info["order"] for name, info in schema.items()}
    last_order = -1
    for section in found_sections:
        if section in expected_order:
            current_order = expected_order[section]
            if current_order < last_order:
                result.order_violations.append(
                    (section, current_order, last_order)
                )
                result.is_valid = False
            last_order = max(last_order, current_order)

    return result


def get_readme_template(project_type: str | ProjectType) -> str:
    """Get the README template reference for a project type.

    Parameters
    ----------
    project_type : str or ProjectType
        The project type ("analysis", "software", "data_repo", "compendium").

    Returns
    -------
    str
        Reference path to the README template.

    Examples
    --------
    >>> get_readme_template("analysis")
    'references/readme_templates.md#analysis-project'
    >>> get_readme_template("software")
    'references/readme_templates.md#software-tool'
    """
    if isinstance(project_type, str):
        project_type = ProjectType(project_type.lower())

    requirements = README_REQUIREMENTS.get(project_type)
    if requirements:
        return requirements["template_ref"]
    return README_REQUIREMENTS[ProjectType.SOFTWARE]["template_ref"]


def get_required_sections(project_type: str | ProjectType) -> list[str]:
    """Get required README sections for a project type.

    Parameters
    ----------
    project_type : str or ProjectType
        The project type.

    Returns
    -------
    list[str]
        List of required section names.

    Examples
    --------
    >>> get_required_sections("analysis")
    ['title', 'description', 'data_requirements', 'environment', 'usage', 'output']
    """
    if isinstance(project_type, str):
        project_type = ProjectType(project_type.lower())

    requirements = README_REQUIREMENTS.get(project_type)
    if requirements:
        return requirements["required"].copy()
    return []


def get_optional_sections(project_type: str | ProjectType) -> list[str]:
    """Get optional README sections for a project type.

    Parameters
    ----------
    project_type : str or ProjectType
        The project type.

    Returns
    -------
    list[str]
        List of optional section names.

    Examples
    --------
    >>> get_optional_sections("software")
    ['documentation', 'contributing', 'license', 'citation', 'badges']
    """
    if isinstance(project_type, str):
        project_type = ProjectType(project_type.lower())

    requirements = README_REQUIREMENTS.get(project_type)
    if requirements:
        return requirements["optional"].copy()
    return []


def normalize_section_name(name: str) -> str:
    """Normalize a section name to canonical form.

    Parameters
    ----------
    name : str
        The section name to normalize.

    Returns
    -------
    str
        Canonical section name, or original if no match found.

    Examples
    --------
    >>> normalize_section_name("Getting Started")
    'installation'
    >>> normalize_section_name("About")
    'description'
    """
    name_lower = name.lower().strip()

    for canonical, aliases in README_SECTION_ALIASES.items():
        if name_lower == canonical or name_lower in [a.lower() for a in aliases]:
            return canonical

    return name_lower.replace(" ", "_")


def validate_readme_sections(
    sections: list[str], project_type: str | ProjectType
) -> ReadmeValidationResult:
    """Validate README sections against project type requirements.

    Parameters
    ----------
    sections : list[str]
        List of section names found in the README.
    project_type : str or ProjectType
        The project type to validate against.

    Returns
    -------
    ReadmeValidationResult
        Validation result with score and missing sections.

    Examples
    --------
    >>> sections = ["title", "description", "installation", "usage"]
    >>> result = validate_readme_sections(sections, "software")
    >>> result.score >= 80.0
    True
    """
    if isinstance(project_type, str):
        project_type = ProjectType(project_type.lower())

    result = ReadmeValidationResult(
        project_type=project_type,
        template_ref=get_readme_template(project_type),
    )

    required = get_required_sections(project_type)
    optional = get_optional_sections(project_type)

    # Normalize section names
    normalized_sections = [normalize_section_name(s) for s in sections]

    # Check required sections
    for req in required:
        if req in normalized_sections:
            result.required_present.append(req)
        else:
            result.required_missing.append(req)

    # Check optional sections
    for opt in optional:
        if opt in normalized_sections:
            result.optional_present.append(opt)

    # Calculate score: 80% for required, 20% for optional
    required_score = (
        (len(result.required_present) / len(required)) * 80 if required else 80
    )
    optional_score = (
        (len(result.optional_present) / len(optional)) * 20 if optional else 20
    )
    result.score = required_score + optional_score

    result.is_valid = len(result.required_missing) == 0

    return result


def create_validation_report(
    file_path: str,
    style: Optional[str] = None,
    coverage: Optional[dict] = None,
    pydocstyle_issues: Optional[list[dict]] = None,
    doctest_results: Optional[dict] = None,
    readme_result: Optional[ReadmeValidationResult] = None,
) -> ValidationReport:
    """Create a structured validation report.

    Parameters
    ----------
    file_path : str
        Path to the validated file.
    style : str, optional
        Docstring style used.
    coverage : dict, optional
        Coverage statistics with total_items, documented, percentage.
    pydocstyle_issues : list[dict], optional
        List of pydocstyle issues with code, line, message.
    doctest_results : dict, optional
        Doctest results with total, passed, failed, failures.
    readme_result : ReadmeValidationResult, optional
        README validation result.

    Returns
    -------
    ValidationReport
        Structured validation report.

    Examples
    --------
    >>> report = create_validation_report(
    ...     "module.py",
    ...     style="numpy",
    ...     coverage={"total_items": 10, "documented": 8, "percentage": 80.0}
    ... )
    >>> report.to_dict()["coverage"]["percentage"]
    80.0
    """
    report = ValidationReport(file=file_path, style=style)

    if coverage:
        report.coverage = coverage

    if pydocstyle_issues is not None:
        errors = sum(1 for i in pydocstyle_issues if i.get("code", "").startswith("D"))
        report.pydocstyle = {
            "errors": errors,
            "warnings": len(pydocstyle_issues) - errors,
            "issues": pydocstyle_issues,
        }
        if errors > 0:
            report.is_valid = False

    if doctest_results:
        report.doctests = doctest_results
        if doctest_results.get("failed", 0) > 0:
            report.is_valid = False

    if readme_result:
        report.readme_score = readme_result.score
        report.missing_sections = readme_result.required_missing
        if not readme_result.is_valid:
            report.is_valid = False

    return report


def format_validation_report(report: ValidationReport, verbose: bool = True) -> str:
    """Format a validation report for human-readable output.

    Parameters
    ----------
    report : ValidationReport
        The validation report to format.
    verbose : bool, default True
        If True, include detailed issue information.

    Returns
    -------
    str
        Formatted report string.
    """
    lines = [f"Validation Report: {report.file}", "=" * 50]

    if report.style:
        lines.append(f"Style: {report.style}")

    if report.coverage:
        cov = report.coverage
        lines.append(
            f"Coverage: {cov.get('documented', 0)}/{cov.get('total_items', 0)} "
            f"({cov.get('percentage', 0):.1f}%)"
        )

    if report.pydocstyle:
        pyd = report.pydocstyle
        lines.append(f"pydocstyle: {pyd.get('errors', 0)} errors, {pyd.get('warnings', 0)} warnings")
        if verbose and pyd.get("issues"):
            for issue in pyd["issues"][:5]:  # Show first 5
                lines.append(f"  - {issue.get('code', '???')}: {issue.get('message', '')}")

    if report.doctests:
        dt = report.doctests
        lines.append(f"Doctests: {dt.get('passed', 0)}/{dt.get('total', 0)} passed")

    if report.readme_score is not None:
        lines.append(f"README Score: {report.readme_score:.1f}/100")
        if report.missing_sections:
            lines.append(f"Missing sections: {', '.join(report.missing_sections)}")

    lines.append("-" * 50)
    status = "✓ VALID" if report.is_valid else "✗ INVALID"
    lines.append(f"Status: {status}")

    return "\n".join(lines)
