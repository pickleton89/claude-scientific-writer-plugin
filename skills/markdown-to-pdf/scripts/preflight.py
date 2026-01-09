"""
Preflight Validation for Markdown-to-PDF

Provides deterministic document validation before PDF generation.
Returns structured PreflightResult - no LLM-generated prose.

Usage:
    from scripts.preflight import preflight_check

    result = preflight_check("document.md")
    if result.is_valid:
        print("Ready for PDF generation")
    else:
        print(result.format_errors())
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from element_detector import count_elements, ElementCounts

# ============================================================================
# TEMPLATE DEFINITIONS (Single Source of Truth)
# ============================================================================

# Template types with their required/optional frontmatter fields
TEMPLATE_SCHEMAS: dict[str, dict[str, Any]] = {
    # Scientific templates
    "analysis-report": {
        "category": "scientific",
        "required": ["type", "title", "date"],
        "optional": ["author", "version", "status", "project"],
        "required_sections": ["Objective", "Methodology", "Findings"],
        "optional_sections": ["Executive Summary", "Key Questions", "Recommendations", "Appendix"],
    },
    "literature-review": {
        "category": "scientific",
        "required": ["type", "title", "date"],
        "optional": ["author", "topic", "scope"],
        "required_sections": ["Introduction", "Methods", "Results"],
        "optional_sections": ["Discussion", "Conclusion", "References"],
    },
    "data-report": {
        "category": "scientific",
        "required": ["type", "title", "date"],
        "optional": ["author", "dataset", "version"],
        "required_sections": ["Data Overview", "Analysis"],
        "optional_sections": ["Methodology", "Visualizations", "Conclusions"],
    },
    # Project management templates
    "meeting-notes": {
        "category": "project-mgmt",
        "required": ["type", "title", "date"],
        "optional": ["attendees", "location"],
        "required_sections": ["Attendees", "Agenda"],
        "optional_sections": ["Discussion", "Action Items", "Next Meeting"],
    },
    "project-status": {
        "category": "project-mgmt",
        "required": ["type", "title", "date"],
        "optional": ["project", "period", "author"],
        "required_sections": ["Summary", "Progress"],
        "optional_sections": ["Blockers", "Next Steps", "Metrics"],
    },
    "phase-plan": {
        "category": "project-mgmt",
        "required": ["type", "title", "date"],
        "optional": ["project", "phase", "owner"],
        "required_sections": ["Objectives", "Timeline"],
        "optional_sections": ["Resources", "Risks", "Dependencies"],
    },
    "task-list": {
        "category": "project-mgmt",
        "required": ["type", "title", "date"],
        "optional": ["project", "assignee", "priority"],
        "required_sections": ["Tasks"],
        "optional_sections": ["Completed", "Blocked", "Notes"],
    },
    # Technical templates
    "technical-spec": {
        "category": "technical",
        "required": ["type", "title", "date"],
        "optional": ["author", "version", "status"],
        "required_sections": ["Overview", "Requirements"],
        "optional_sections": ["Architecture", "API", "Implementation", "Testing"],
    },
    "method-guide": {
        "category": "technical",
        "required": ["type", "title", "date"],
        "optional": ["author", "version"],
        "required_sections": ["Purpose", "Procedure"],
        "optional_sections": ["Prerequisites", "Troubleshooting", "References"],
    },
    "standards-guide": {
        "category": "technical",
        "required": ["type", "title", "date"],
        "optional": ["author", "version", "scope"],
        "required_sections": ["Standards"],
        "optional_sections": ["Rationale", "Examples", "Exceptions"],
    },
    # Meta templates
    "agent-definition": {
        "category": "meta",
        "required": ["type", "title"],
        "optional": ["version", "author"],
        "required_sections": ["Overview", "Capabilities"],
        "optional_sections": ["Triggers", "Workflow", "Limitations"],
    },
    "readme": {
        "category": "meta",
        "required": ["type", "title"],
        "optional": ["project", "version"],
        "required_sections": ["Description"],
        "optional_sections": ["Installation", "Usage", "Contributing", "License"],
    },
}


# ============================================================================
# PREFLIGHT RESULT DATACLASS
# ============================================================================


@dataclass
class PreflightResult:
    """
    Structured validation result for document preflight check.

    All fields have deterministic values - no LLM-generated content.
    """

    # File validation
    file_exists: bool = True
    file_path: str = ""
    file_extension_valid: bool = True

    # Frontmatter validation
    frontmatter_present: bool = True
    frontmatter_valid: bool = True
    frontmatter_errors: list[str] = field(default_factory=list)
    detected_type: str | None = None
    detected_category: str | None = None

    # Section validation
    required_sections_present: bool = True
    missing_sections: list[str] = field(default_factory=list)
    optional_sections_missing: list[str] = field(default_factory=list)

    # Element counts
    element_counts: ElementCounts | None = None

    @property
    def is_valid(self) -> bool:
        """Check if document passes all required validations."""
        return (
            self.file_exists
            and self.file_extension_valid
            and self.frontmatter_present
            and self.frontmatter_valid
            and self.required_sections_present
        )

    def format_report(self) -> str:
        """
        Format preflight result as deterministic report string.

        Returns:
            Fixed-format report for consistent output.
        """
        lines = []

        # File status
        status_icon = "✅" if self.is_valid else "❌"
        lines.append(f"{status_icon} Preflight Check: {'PASS' if self.is_valid else 'FAIL'}")
        lines.append("")

        # File info
        lines.append(f"📄 File: {self.file_path}")
        if not self.file_exists:
            lines.append("   ❌ File not found")
        if not self.file_extension_valid:
            lines.append("   ❌ Invalid extension (expected .md)")

        # Frontmatter
        lines.append("")
        lines.append("📋 Frontmatter:")
        if not self.frontmatter_present:
            lines.append("   ❌ Missing YAML frontmatter")
        elif not self.frontmatter_valid:
            lines.append("   ❌ Invalid frontmatter:")
            for error in self.frontmatter_errors:
                lines.append(f"      - {error}")
        else:
            lines.append(f"   ✅ Type: {self.detected_type} ({self.detected_category})")

        # Sections
        lines.append("")
        lines.append("📑 Sections:")
        if not self.required_sections_present:
            lines.append("   ❌ Missing required sections:")
            for section in self.missing_sections:
                lines.append(f"      - {section}")
        else:
            lines.append("   ✅ All required sections present")

        if self.optional_sections_missing:
            lines.append("   ⚠️ Missing optional sections:")
            for section in self.optional_sections_missing:
                lines.append(f"      - {section}")

        # Elements
        if self.element_counts:
            lines.append("")
            lines.append("🔍 Elements Detected:")
            lines.append(self.element_counts.to_summary())

        return "\n".join(lines)

    def format_errors(self) -> str:
        """Format only error messages for quick troubleshooting."""
        errors = []

        if not self.file_exists:
            errors.append(f"FileNotFoundError: {self.file_path}")
        if not self.file_extension_valid:
            errors.append("ValidationError: Invalid extension (expected .md)")
        if not self.frontmatter_present:
            errors.append("KeyError: Missing YAML frontmatter")
        if self.frontmatter_errors:
            errors.extend(self.frontmatter_errors)
        if self.missing_sections:
            errors.append(f"ValidationError: Missing sections: {', '.join(self.missing_sections)}")

        return "\n".join(errors) if errors else "No errors"


# ============================================================================
# PREFLIGHT CHECK FUNCTION
# ============================================================================


def _extract_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """
    Extract YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict or None, content_without_frontmatter)
    """
    if not content.startswith("---"):
        return None, content

    # Find closing ---
    end_match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
    if not end_match:
        return None, content

    yaml_content = content[3:end_match.start() + 3]
    remaining_content = content[end_match.end() + 3:].strip()

    try:
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter if isinstance(frontmatter, dict) else None, remaining_content
    except yaml.YAMLError:
        return None, content


def _extract_sections(content: str) -> list[str]:
    """
    Extract section headings from markdown content.

    Returns list of section names (H1 and H2 headings).
    """
    pattern = re.compile(r"^#{1,2}\s+(.+)$", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(content)]


def _normalize_section_name(name: str) -> str:
    """Normalize section name for comparison."""
    # Remove common prefixes like numbers and punctuation
    normalized = re.sub(r"^[\d.]+\s*", "", name)
    return normalized.lower().strip()


def _check_sections(
    content: str, required: list[str], optional: list[str]
) -> tuple[list[str], list[str]]:
    """
    Check for required and optional sections.

    Returns:
        Tuple of (missing_required, missing_optional)
    """
    found_sections = _extract_sections(content)
    found_normalized = {_normalize_section_name(s) for s in found_sections}

    missing_required = []
    for req in required:
        if _normalize_section_name(req) not in found_normalized:
            missing_required.append(req)

    missing_optional = []
    for opt in optional:
        if _normalize_section_name(opt) not in found_normalized:
            missing_optional.append(opt)

    return missing_required, missing_optional


def preflight_check(file_path: str | Path) -> PreflightResult:
    """
    Run preflight validation on a markdown document.

    Checks:
        1. File exists and has .md extension
        2. YAML frontmatter is present and valid
        3. Required sections for template type are present
        4. Counts document elements

    Args:
        file_path: Path to markdown file.

    Returns:
        PreflightResult with all validation details.
    """
    result = PreflightResult()
    path = Path(file_path)
    result.file_path = str(path)

    # Check file exists
    if not path.exists():
        result.file_exists = False
        return result

    # Check extension
    if path.suffix.lower() != ".md":
        result.file_extension_valid = False
        return result

    # Read content
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result.file_exists = False
        result.frontmatter_errors.append(f"Read error: {e}")
        return result

    # Extract frontmatter
    frontmatter, body_content = _extract_frontmatter(content)

    if frontmatter is None:
        result.frontmatter_present = False
        result.frontmatter_valid = False
        result.frontmatter_errors.append("Missing or invalid YAML frontmatter")
        # Still count elements even without valid frontmatter
        result.element_counts = count_elements(content)
        return result

    # Validate frontmatter type
    doc_type = frontmatter.get("type")
    if not doc_type:
        result.frontmatter_valid = False
        result.frontmatter_errors.append("Missing required field: type")
    elif doc_type not in TEMPLATE_SCHEMAS:
        result.frontmatter_valid = False
        result.frontmatter_errors.append(
            f"Unknown type: '{doc_type}'. Valid types: {', '.join(sorted(TEMPLATE_SCHEMAS.keys()))}"
        )
    else:
        result.detected_type = doc_type
        schema = TEMPLATE_SCHEMAS[doc_type]
        result.detected_category = schema["category"]

        # Check required frontmatter fields
        for required_field in schema["required"]:
            if required_field not in frontmatter:
                result.frontmatter_valid = False
                result.frontmatter_errors.append(f"Missing required field: {required_field}")

        # Check sections
        if result.frontmatter_valid:
            missing_req, missing_opt = _check_sections(
                body_content,
                schema.get("required_sections", []),
                schema.get("optional_sections", []),
            )
            if missing_req:
                result.required_sections_present = False
                result.missing_sections = missing_req
            result.optional_sections_missing = missing_opt

    # Count elements
    result.element_counts = count_elements(content)

    return result


def list_templates() -> list[dict[str, str]]:
    """
    List all available templates.

    Returns:
        List of template info dictionaries with type, category, description.
    """
    templates = []
    for template_type, schema in sorted(TEMPLATE_SCHEMAS.items()):
        templates.append({
            "type": template_type,
            "category": schema["category"],
            "description": _get_template_description(template_type),
        })
    return templates


def _get_template_description(template_type: str) -> str:
    """Get human-readable description for template type."""
    descriptions = {
        "analysis-report": "Structured analysis with findings",
        "literature-review": "Systematic literature review",
        "data-report": "Data analysis and visualization",
        "meeting-notes": "Meeting documentation",
        "project-status": "Project status update",
        "phase-plan": "Implementation phase planning",
        "task-list": "Task tracking document",
        "technical-spec": "Technical specification",
        "method-guide": "Methodology documentation",
        "standards-guide": "Standards and guidelines",
        "agent-definition": "AI agent behavior definition",
        "readme": "Project documentation",
    }
    return descriptions.get(template_type, "Document template")
