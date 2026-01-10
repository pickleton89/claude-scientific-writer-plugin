"""README validation utilities for code documentation skill.

Validates README files against required sections for different project types.
Implements deterministic section checking based on SKILL.md templates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class ProjectType(Enum):
    """Project types with distinct README requirements.

    Based on SKILL.md <readme_structure> section.
    """

    ANALYSIS = "analysis"
    SOFTWARE = "software"
    DATA_REPO = "data_repo"
    COMPENDIUM = "compendium"
    UNKNOWN = "unknown"


class SectionStatus(Enum):
    """Status of a README section."""

    PRESENT = "present"
    MISSING = "missing"
    PARTIAL = "partial"


@dataclass
class SectionResult:
    """Result of checking a single README section."""

    name: str
    status: SectionStatus
    required: bool
    line_number: int | None = None
    content_preview: str | None = None


@dataclass
class ReadmeValidation:
    """Complete README validation result."""

    path: str
    project_type: ProjectType
    valid: bool
    sections: list[SectionResult] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    extra_sections: list[str] = field(default_factory=list)
    score: float = 0.0
    error: str | None = None

    @property
    def completeness_ratio(self) -> float:
        """Ratio of present sections to total required sections."""
        required = [s for s in self.sections if s.required]
        if not required:
            return 1.0
        present = sum(1 for s in required if s.status == SectionStatus.PRESENT)
        return present / len(required)

    @property
    def summary(self) -> str:
        """One-line summary of validation result."""
        status = "pass" if self.valid else "fail"
        return f"[{self.score:.0f}/100] README: {status} ({self.project_type.value})"


# Required sections by project type (from SKILL.md)
REQUIRED_SECTIONS: dict[ProjectType, list[str]] = {
    ProjectType.ANALYSIS: [
        "title",
        "description",
        "data",
        "environment",
        "usage",
        "output",
        "citation",
    ],
    ProjectType.SOFTWARE: [
        "title",
        "description",
        "installation",
        "quick start",
        "documentation",
        "contributing",
        "license",
    ],
    ProjectType.DATA_REPO: [
        "title",
        "description",
        "data dictionary",
        "collection",
        "usage",
        "license",
    ],
    ProjectType.COMPENDIUM: [
        "title",
        "description",
        "structure",
        "reproduce",
        "data",
        "code",
        "license",
        "citation",
    ],
}

# Optional sections that improve quality
OPTIONAL_SECTIONS: dict[ProjectType, list[str]] = {
    ProjectType.ANALYSIS: ["requirements", "results", "acknowledgments"],
    ProjectType.SOFTWARE: ["badges", "examples", "api", "changelog", "acknowledgments"],
    ProjectType.DATA_REPO: ["publications", "acknowledgments", "contact"],
    ProjectType.COMPENDIUM: ["dependencies", "acknowledgments", "contact"],
}

# Section aliases (common variations)
SECTION_ALIASES: dict[str, list[str]] = {
    "title": ["title", "name", "project"],
    "description": ["description", "overview", "about", "summary", "introduction"],
    "installation": ["installation", "install", "setup", "getting started"],
    "quick start": ["quick start", "quickstart", "usage", "getting started", "tutorial"],
    "usage": ["usage", "how to use", "running", "execution"],
    "data": ["data", "data requirements", "input data", "datasets"],
    "data dictionary": ["data dictionary", "data schema", "schema", "fields", "columns"],
    "environment": ["environment", "setup", "dependencies", "requirements"],
    "output": ["output", "results", "outputs"],
    "documentation": ["documentation", "docs", "api reference", "reference"],
    "contributing": ["contributing", "contribute", "development"],
    "license": ["license", "licensing"],
    "citation": ["citation", "citing", "cite", "how to cite", "references"],
    "collection": ["collection", "data collection", "methodology", "methods"],
    "structure": ["structure", "project structure", "directory", "layout"],
    "reproduce": ["reproduce", "reproducibility", "replication", "run"],
    "code": ["code", "scripts", "source"],
}


def get_required_sections(project_type: ProjectType) -> list[str]:
    """Get list of required sections for a project type.

    Parameters
    ----------
    project_type : ProjectType
        The type of project.

    Returns
    -------
    list[str]
        List of required section names.
    """
    return REQUIRED_SECTIONS.get(project_type, [])


def get_optional_sections(project_type: ProjectType) -> list[str]:
    """Get list of optional sections for a project type.

    Parameters
    ----------
    project_type : ProjectType
        The type of project.

    Returns
    -------
    list[str]
        List of optional section names.
    """
    return OPTIONAL_SECTIONS.get(project_type, [])


def _normalize_section_name(name: str) -> str:
    """Normalize a section name for comparison.

    Parameters
    ----------
    name : str
        Raw section name from markdown.

    Returns
    -------
    str
        Normalized lowercase name.
    """
    # Remove markdown formatting, badges, emojis
    name = re.sub(r"!\[.*?\]\(.*?\)", "", name)  # Remove badge images
    name = re.sub(r"\[.*?\]\(.*?\)", "", name)  # Remove links
    name = re.sub(r"[^\w\s]", "", name)  # Remove special chars
    return name.strip().lower()


def _find_section_match(
    normalized_name: str, target_sections: Sequence[str]
) -> str | None:
    """Find if a normalized section name matches any target section.

    Parameters
    ----------
    normalized_name : str
        Normalized section name from document.
    target_sections : Sequence[str]
        List of target section names to match against.

    Returns
    -------
    str | None
        Matched target section name, or None if no match.
    """
    for target in target_sections:
        # Direct match
        if normalized_name == target:
            return target
        # Alias match
        aliases = SECTION_ALIASES.get(target, [target])
        for alias in aliases:
            if normalized_name == alias or alias in normalized_name:
                return target
    return None


def _extract_sections(content: str) -> list[tuple[str, int, str]]:
    """Extract markdown sections from content.

    Parameters
    ----------
    content : str
        Markdown content.

    Returns
    -------
    list[tuple[str, int, str]]
        List of (section_name, line_number, content_preview) tuples.
    """
    sections = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Match ## Section or # Section headers
        match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if match:
            header_text = match.group(2)
            # Get content preview (next non-empty line)
            preview = ""
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip() and not lines[j].startswith("#"):
                    preview = lines[j].strip()[:100]
                    break
            sections.append((header_text, i + 1, preview))

    return sections


def detect_project_type(path: str | Path) -> ProjectType:
    """Detect project type from directory structure.

    Analyzes the directory structure to determine the most likely
    project type based on file presence and patterns.

    Parameters
    ----------
    path : str | Path
        Path to project directory or README file.

    Returns
    -------
    ProjectType
        Detected project type.
    """
    path = Path(path)
    if path.is_file():
        path = path.parent

    # Check for software package indicators
    software_indicators = [
        "setup.py",
        "pyproject.toml",
        "setup.cfg",
        "DESCRIPTION",  # R package
        "Cargo.toml",  # Rust
        "package.json",  # Node
    ]
    if any((path / ind).exists() for ind in software_indicators):
        return ProjectType.SOFTWARE

    # Check for data repository indicators
    data_indicators = ["data", "datasets", "raw_data"]
    metadata_files = ["metadata.json", "metadata.yaml", "datapackage.json"]
    has_data_dir = any((path / d).is_dir() for d in data_indicators)
    has_metadata = any((path / f).exists() for f in metadata_files)
    if has_data_dir and has_metadata:
        return ProjectType.DATA_REPO

    # Check for research compendium
    compendium_dirs = ["analysis", "paper", "manuscript", "R", "src"]
    data_dirs = ["data", "data-raw"]
    has_compendium = sum(1 for d in compendium_dirs if (path / d).is_dir()) >= 2
    has_data = any((path / d).is_dir() for d in data_dirs)
    if has_compendium and has_data:
        return ProjectType.COMPENDIUM

    # Check for analysis project (notebooks, scripts)
    analysis_indicators = list(path.glob("*.ipynb")) + list(path.glob("*.Rmd"))
    script_files = list(path.glob("*.py")) + list(path.glob("*.R"))
    if analysis_indicators or (script_files and not has_metadata):
        return ProjectType.ANALYSIS

    return ProjectType.UNKNOWN


def validate_readme_sections(
    readme_path: str | Path,
    project_type: ProjectType | str | None = None,
) -> ReadmeValidation:
    """Validate README has all required sections for project type.

    Parameters
    ----------
    readme_path : str | Path
        Path to README file.
    project_type : ProjectType | str | None, optional
        Project type to validate against. If None, auto-detects.

    Returns
    -------
    ReadmeValidation
        Complete validation result with section details.
    """
    readme_path = Path(readme_path)

    # Handle string project type
    if isinstance(project_type, str):
        try:
            project_type = ProjectType(project_type)
        except ValueError:
            project_type = ProjectType.UNKNOWN

    # Auto-detect project type if not provided
    if project_type is None:
        project_type = detect_project_type(readme_path.parent)

    # Read README content
    try:
        content = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ReadmeValidation(
            path=str(readme_path),
            project_type=project_type,
            valid=False,
            error=f"README not found: {readme_path}",
        )
    except Exception as e:
        return ReadmeValidation(
            path=str(readme_path),
            project_type=project_type,
            valid=False,
            error=f"Error reading README: {e}",
        )

    # Get required and optional sections
    required = get_required_sections(project_type)
    optional = get_optional_sections(project_type)

    # Extract sections from content
    found_sections = _extract_sections(content)
    found_normalized = {_normalize_section_name(s[0]): s for s in found_sections}

    # Special handling: first H1 header is the title
    # Find the first H1 header in the content
    first_h1 = None
    lines = content.split("\n")
    for raw, line_num, preview in found_sections:
        # Check if this was an H1 (matches H1 pattern in content)
        if line_num <= len(lines):
            line_content = lines[line_num - 1]
            if line_content.startswith("# ") and not line_content.startswith("## "):
                first_h1 = (raw, line_num, preview)
                break

    # Check each required section
    section_results = []
    missing_required = []
    found_required = set()

    for section_name in required:
        matched = None

        # Special case: "title" is the first H1 header
        if section_name == "title" and first_h1 is not None:
            matched = first_h1
            found_required.add(_normalize_section_name(first_h1[0]))
        else:
            for normalized, (raw, line_num, preview) in found_normalized.items():
                if _find_section_match(normalized, [section_name]):
                    matched = (raw, line_num, preview)
                    found_required.add(normalized)
                    break

        if matched:
            section_results.append(
                SectionResult(
                    name=section_name,
                    status=SectionStatus.PRESENT,
                    required=True,
                    line_number=matched[1],
                    content_preview=matched[2],
                )
            )
        else:
            missing_required.append(section_name)
            section_results.append(
                SectionResult(
                    name=section_name,
                    status=SectionStatus.MISSING,
                    required=True,
                )
            )

    # Check optional sections
    missing_optional = []
    for section_name in optional:
        matched = None
        for normalized, (raw, line_num, preview) in found_normalized.items():
            if _find_section_match(normalized, [section_name]):
                matched = (raw, line_num, preview)
                break

        if matched:
            section_results.append(
                SectionResult(
                    name=section_name,
                    status=SectionStatus.PRESENT,
                    required=False,
                    line_number=matched[1],
                    content_preview=matched[2],
                )
            )
        else:
            missing_optional.append(section_name)

    # Find extra sections not in our lists
    all_known = set(required + optional)
    extra_sections = []
    title_normalized = _normalize_section_name(first_h1[0]) if first_h1 else None
    for normalized, (raw, _, _) in found_normalized.items():
        # Skip the title section (first H1)
        if title_normalized and normalized == title_normalized:
            continue
        if not _find_section_match(normalized, list(all_known)):
            extra_sections.append(raw)

    # Calculate score
    required_count = len(required)
    present_count = required_count - len(missing_required)
    optional_present = len(optional) - len(missing_optional)

    if required_count > 0:
        base_score = (present_count / required_count) * 80
        bonus = min(optional_present * 5, 20)  # Up to 20 points for optional
        score = min(base_score + bonus, 100)
    else:
        score = 100.0

    return ReadmeValidation(
        path=str(readme_path),
        project_type=project_type,
        valid=len(missing_required) == 0,
        sections=section_results,
        missing_required=missing_required,
        missing_optional=missing_optional,
        extra_sections=extra_sections,
        score=score,
    )


def format_validation_report(validation: ReadmeValidation) -> str:
    """Format validation result as human-readable report.

    Parameters
    ----------
    validation : ReadmeValidation
        Validation result to format.

    Returns
    -------
    str
        Formatted report string.
    """
    lines = [
        "README Validation Report",
        "=" * 50,
        f"File: {validation.path}",
        f"Project Type: {validation.project_type.value}",
        f"Valid: {'Yes' if validation.valid else 'No'}",
        f"Score: {validation.score:.1f}/100",
        f"Completeness: {validation.completeness_ratio:.0%}",
        "",
    ]

    if validation.error:
        lines.append(f"Error: {validation.error}")
        return "\n".join(lines)

    if validation.missing_required:
        lines.append("Missing Required Sections:")
        for section in validation.missing_required:
            lines.append(f"  - {section}")
        lines.append("")

    if validation.missing_optional:
        lines.append("Missing Optional Sections:")
        for section in validation.missing_optional:
            lines.append(f"  - {section}")
        lines.append("")

    lines.append("Section Details:")
    for section in validation.sections:
        status_icon = {
            SectionStatus.PRESENT: "[OK]",
            SectionStatus.MISSING: "[--]",
            SectionStatus.PARTIAL: "[??]",
        }[section.status]
        req_marker = "*" if section.required else " "
        line = f"  {status_icon} {req_marker}{section.name}"
        if section.line_number:
            line += f" (line {section.line_number})"
        lines.append(line)

    return "\n".join(lines)
