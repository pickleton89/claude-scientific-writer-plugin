#!/usr/bin/env python3
"""
Brand Skill Validation Script

Validates brand skills against the BRAND_SKILL_INTERFACE contract.
Performs deterministic checks for structure, tokens, adapters, and accessibility.

Usage:
    python validate_brand.py /path/to/brand-skill
    python validate_brand.py /path/to/brand-skill --json
    python validate_brand.py /path/to/brand-skill -v  # Show suggestions

Example:
    python validate_brand.py skills/oligon-brand
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Try to import jsonschema for JSON Schema validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# =============================================================================
# CONSTANTS
# =============================================================================

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "brand-tokens.schema.json"

# Required directory structure
REQUIRED_STRUCTURE = {
    "SKILL.md": "file",
    "tokens": "dir",
    "tokens/brand-tokens.json": "file",
    "adapters": "dir",
}

# At least one adapter required
ADAPTER_PATTERNS = [
    "adapters/matplotlib_adapter.py",
    "adapters/ggplot2_adapter.R",
    "adapters/*_adapter.py",
    "adapters/*_adapter.R",
]

# Required adapter exports
REQUIRED_ADAPTER_EXPORTS = {
    "python": {
        "constants": ["BRAND_COLORS"],
        "functions": ["set_brand_style", "get_cycle", "get_color"],
    }
}

# Hex color regex
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Required SKILL.md frontmatter fields
REQUIRED_FRONTMATTER = ["name", "version", "description"]
RECOMMENDED_FRONTMATTER = ["brand-type", "tokens-file", "allowed-tools"]


# =============================================================================
# DATA CLASSES
# =============================================================================

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: Severity
    category: str
    message: str
    path: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "path": self.path,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationReport:
    """Complete validation report for a brand skill."""
    brand_name: str
    brand_path: str
    valid: bool = True
    structure_valid: bool = True
    tokens_valid: bool = True
    adapter_api_valid: bool = True
    accessibility_valid: bool = True
    skill_md_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.valid = False

    def to_dict(self) -> dict:
        return {
            "brand_name": self.brand_name,
            "brand_path": self.brand_path,
            "valid": self.valid,
            "structure_valid": self.structure_valid,
            "tokens_valid": self.tokens_valid,
            "adapter_api_valid": self.adapter_api_valid,
            "accessibility_valid": self.accessibility_valid,
            "skill_md_valid": self.skill_md_valid,
            "error_count": sum(1 for i in self.issues if i.severity == Severity.ERROR),
            "warning_count": sum(1 for i in self.issues if i.severity == Severity.WARNING),
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_structure(brand_path: Path, report: ValidationReport) -> None:
    """Validate brand skill directory structure."""
    for item, item_type in REQUIRED_STRUCTURE.items():
        item_path = brand_path / item
        if item_type == "file":
            if not item_path.is_file():
                report.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="structure",
                    message=f"Required file missing: {item}",
                    path=str(item_path),
                    suggestion=f"Create {item} following the interface specification"
                ))
                report.structure_valid = False
        elif item_type == "dir":
            if not item_path.is_dir():
                report.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="structure",
                    message=f"Required directory missing: {item}",
                    path=str(item_path),
                    suggestion=f"Create directory: mkdir -p {item}"
                ))
                report.structure_valid = False

    # Check for at least one adapter
    adapters_dir = brand_path / "adapters"
    if adapters_dir.is_dir():
        adapters = list(adapters_dir.glob("*_adapter.*"))
        if not adapters:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="structure",
                message="No adapter files found in adapters/",
                path=str(adapters_dir),
                suggestion="Create at least one adapter (e.g., matplotlib_adapter.py)"
            ))
            report.structure_valid = False
        else:
            report.summary["adapters_found"] = [a.name for a in adapters]


def validate_tokens(brand_path: Path, report: ValidationReport) -> dict | None:
    """Validate brand-tokens.json file."""
    tokens_path = brand_path / "tokens" / "brand-tokens.json"

    if not tokens_path.exists():
        report.tokens_valid = False
        return None

    # Try to parse JSON
    try:
        with open(tokens_path, encoding='utf-8') as f:
            tokens = json.load(f)
    except json.JSONDecodeError as e:
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="tokens",
            message=f"Invalid JSON in brand-tokens.json: {e}",
            path=str(tokens_path)
        ))
        report.tokens_valid = False
        return None

    # Validate against JSON Schema if available
    if HAS_JSONSCHEMA and SCHEMA_PATH.exists():
        try:
            with open(SCHEMA_PATH, encoding='utf-8') as f:
                schema = json.load(f)
            jsonschema.validate(tokens, schema)
            report.summary["schema_valid"] = True
        except jsonschema.ValidationError as e:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="tokens",
                message=f"Schema validation failed: {e.message}",
                path=f"brand-tokens.json:{e.json_path}"
            ))
            report.tokens_valid = False
            report.summary["schema_valid"] = False
    else:
        # Manual validation of required fields
        _validate_tokens_manual(tokens, report)

    # Validate all hex colors
    _validate_hex_colors(tokens, report)

    return tokens


def _validate_tokens_manual(tokens: dict, report: ValidationReport) -> None:
    """Manual validation when jsonschema not available."""
    # Check required top-level fields
    required = ["meta", "colors", "color_cycles"]
    for field_name in required:
        if field_name not in tokens:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="tokens",
                message=f"Missing required field: {field_name}",
                suggestion=f"Add '{field_name}' to brand-tokens.json"
            ))
            report.tokens_valid = False

    # Check meta fields
    if "meta" in tokens:
        meta = tokens["meta"]
        if "name" not in meta:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="tokens",
                message="Missing meta.name",
                suggestion="Add 'name' field to meta object"
            ))
            report.tokens_valid = False
        if "version" not in meta:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="tokens",
                message="Missing meta.version",
                suggestion="Add 'version' field to meta object (e.g., '1.0.0')"
            ))
            report.tokens_valid = False

    # Check colors structure
    if "colors" in tokens:
        colors = tokens["colors"]
        required_categories = ["primary", "neutrals", "structure"]
        for cat in required_categories:
            if cat not in colors:
                report.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="tokens",
                    message=f"Missing required color category: colors.{cat}",
                    suggestion=f"Add '{cat}' category to colors object"
                ))
                report.tokens_valid = False


def _validate_hex_colors(tokens: dict, report: ValidationReport) -> None:
    """Recursively validate all hex color values."""
    def check_colors(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if key == "hex" and isinstance(value, str):
                    if not HEX_COLOR_PATTERN.match(value):
                        report.add_issue(ValidationIssue(
                            severity=Severity.ERROR,
                            category="tokens",
                            message=f"Invalid hex color: {value}",
                            path=current_path,
                            suggestion="Use 6-digit hex format: #RRGGBB"
                        ))
                        report.tokens_valid = False
                elif key == "colors" and isinstance(value, list):
                    for i, color in enumerate(value):
                        if isinstance(color, str) and not HEX_COLOR_PATTERN.match(color):
                            report.add_issue(ValidationIssue(
                                severity=Severity.ERROR,
                                category="tokens",
                                message=f"Invalid hex color in array: {color}",
                                path=f"{current_path}[{i}]",
                                suggestion="Use 6-digit hex format: #RRGGBB"
                            ))
                            report.tokens_valid = False
                else:
                    check_colors(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_colors(item, f"{path}[{i}]")

    check_colors(tokens)


def validate_adapter_api(brand_path: Path, report: ValidationReport) -> None:
    """Validate Python adapter exports required API."""
    adapters_dir = brand_path / "adapters"

    # Only matplotlib_adapter.py is required to have the full API
    # Other adapters (docx, pptx, reportlab) have specialized APIs
    matplotlib_adapter = adapters_dir / "matplotlib_adapter.py"

    if matplotlib_adapter.exists():
        _validate_python_adapter(matplotlib_adapter, report)
        report.summary["matplotlib_adapter"] = True
    else:
        # Check for any Python adapter
        python_adapters = list(adapters_dir.glob("*_adapter.py"))
        if not python_adapters:
            report.add_issue(ValidationIssue(
                severity=Severity.WARNING,
                category="adapter",
                message="No Python adapter found",
                suggestion="Consider adding matplotlib_adapter.py for Python support"
            ))
        else:
            # Other adapters exist but no matplotlib adapter
            report.add_issue(ValidationIssue(
                severity=Severity.INFO,
                category="adapter",
                message=f"Found {len(python_adapters)} adapter(s), but no matplotlib_adapter.py",
                suggestion="matplotlib_adapter.py provides the standard API for plotting-libraries"
            ))
            report.summary["matplotlib_adapter"] = False


def _validate_python_adapter(adapter_path: Path, report: ValidationReport) -> None:
    """Validate a single Python adapter file."""
    try:
        with open(adapter_path, encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
    except SyntaxError as e:
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="adapter",
            message=f"Python syntax error: {e}",
            path=str(adapter_path)
        ))
        report.adapter_api_valid = False
        return

    # Extract all top-level definitions
    definitions = set()
    function_signatures = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            definitions.add(node.name)
            function_signatures[node.name] = {
                "args": [arg.arg for arg in node.args.args],
                "defaults": len(node.args.defaults),
            }
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    definitions.add(target.id)

    # Check required constants
    for const in REQUIRED_ADAPTER_EXPORTS["python"]["constants"]:
        if const not in definitions:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="adapter",
                message=f"Missing required constant: {const}",
                path=str(adapter_path),
                suggestion=f"Add '{const}: dict[str, str]' constant"
            ))
            report.adapter_api_valid = False

    # Check required functions
    for func in REQUIRED_ADAPTER_EXPORTS["python"]["functions"]:
        if func not in definitions:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="adapter",
                message=f"Missing required function: {func}()",
                path=str(adapter_path),
                suggestion=f"Implement {func}() function per interface spec"
            ))
            report.adapter_api_valid = False
        elif func in function_signatures:
            # Validate function signature
            sig = function_signatures[func]
            if func == "set_brand_style":
                if "cycle" not in sig["args"] and sig["defaults"] == 0:
                    report.add_issue(ValidationIssue(
                        severity=Severity.WARNING,
                        category="adapter",
                        message=f"{func}() should accept 'cycle' parameter",
                        path=str(adapter_path)
                    ))
            elif func in ("get_cycle", "get_color"):
                if "name" not in sig["args"] and len(sig["args"]) < 2:
                    report.add_issue(ValidationIssue(
                        severity=Severity.WARNING,
                        category="adapter",
                        message=f"{func}() should accept 'name' parameter",
                        path=str(adapter_path)
                    ))

    report.summary["adapter_exports"] = list(definitions)


def validate_skill_md(brand_path: Path, report: ValidationReport) -> None:
    """Validate SKILL.md frontmatter and structure."""
    skill_md_path = brand_path / "SKILL.md"

    if not skill_md_path.exists():
        report.skill_md_valid = False
        return

    with open(skill_md_path, encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="skill_md",
            message="Missing YAML frontmatter",
            path=str(skill_md_path),
            suggestion="Add ---\\n...frontmatter...\\n--- at top of file"
        ))
        report.skill_md_valid = False
        return

    frontmatter_text = frontmatter_match.group(1)

    # Simple YAML parsing (key: value)
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    for field_name in REQUIRED_FRONTMATTER:
        if field_name not in frontmatter:
            report.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="skill_md",
                message=f"Missing required frontmatter field: {field_name}",
                path=str(skill_md_path)
            ))
            report.skill_md_valid = False

    # Check recommended fields
    for field_name in RECOMMENDED_FRONTMATTER:
        if field_name not in frontmatter:
            report.add_issue(ValidationIssue(
                severity=Severity.WARNING,
                category="skill_md",
                message=f"Missing recommended frontmatter field: {field_name}",
                path=str(skill_md_path),
                suggestion=f"Add '{field_name}' for better integration"
            ))

    # Check for required XML sections
    required_sections = [
        "overview", "when_to_use", "decision_framework",
        "workflow", "success_criteria", "cross_references"
    ]
    for section in required_sections:
        pattern = rf"<{section}>"
        if not re.search(pattern, content, re.IGNORECASE):
            report.add_issue(ValidationIssue(
                severity=Severity.WARNING,
                category="skill_md",
                message=f"Missing recommended section: <{section}>",
                path=str(skill_md_path)
            ))

    report.summary["frontmatter"] = frontmatter


def validate_accessibility(tokens: dict | None, report: ValidationReport) -> None:
    """Validate color accessibility (contrast ratios)."""
    if tokens is None:
        return

    # Import accessibility checker if available
    try:
        from . import check_accessibility
        check_accessibility.validate_colors(tokens, report)
    except ImportError:
        # Basic contrast check
        _basic_accessibility_check(tokens, report)


def _basic_accessibility_check(tokens: dict, report: ValidationReport) -> None:
    """Basic accessibility validation without external dependencies."""
    colors = tokens.get("colors", {})

    # Check that structure includes white and black
    structure = colors.get("structure", {})
    if "white" not in structure or "black" not in structure:
        report.add_issue(ValidationIssue(
            severity=Severity.WARNING,
            category="accessibility",
            message="Missing white or black in structure colors",
            suggestion="Add white (#FFFFFF) and black (#000000) to structure colors"
        ))

    # Check for accessibility section
    if "accessibility" not in tokens:
        report.add_issue(ValidationIssue(
            severity=Severity.WARNING,
            category="accessibility",
            message="No accessibility section in tokens",
            suggestion="Add 'accessibility' section with colorblind_safe_pair and requirements"
        ))
        report.accessibility_valid = False

    # Check for preflight_checklist
    if "preflight_checklist" not in tokens:
        report.add_issue(ValidationIssue(
            severity=Severity.INFO,
            category="accessibility",
            message="No preflight_checklist in tokens",
            suggestion="Consider adding preflight_checklist for visual QA"
        ))


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def validate_brand(brand_path: Path) -> ValidationReport:
    """
    Perform complete validation of a brand skill.

    Parameters
    ----------
    brand_path : Path
        Path to the brand skill directory

    Returns
    -------
    ValidationReport
        Complete validation report with issues and summary
    """
    brand_path = Path(brand_path).resolve()

    if not brand_path.is_dir():
        report = ValidationReport(
            brand_name="unknown",
            brand_path=str(brand_path),
            valid=False
        )
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="structure",
            message=f"Brand path does not exist: {brand_path}"
        ))
        return report

    report = ValidationReport(
        brand_name=brand_path.name,
        brand_path=str(brand_path)
    )

    # Run all validations
    validate_structure(brand_path, report)
    tokens = validate_tokens(brand_path, report)
    validate_adapter_api(brand_path, report)
    validate_skill_md(brand_path, report)
    validate_accessibility(tokens, report)

    return report


def print_report(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation report to stdout."""
    status = "PASS" if report.valid else "FAIL"
    print(f"\n{'='*60}")
    print(f"Brand Validation Report: {report.brand_name}")
    print(f"Status: {status}")
    print(f"{'='*60}")

    # Summary
    print("\nChecks:")
    print(f"  Structure:     {'PASS' if report.structure_valid else 'FAIL'}")
    print(f"  Tokens:        {'PASS' if report.tokens_valid else 'FAIL'}")
    print(f"  Adapter API:   {'PASS' if report.adapter_api_valid else 'FAIL'}")
    print(f"  SKILL.md:      {'PASS' if report.skill_md_valid else 'FAIL'}")
    print(f"  Accessibility: {'PASS' if report.accessibility_valid else 'FAIL'}")

    # Issues by severity
    errors = [i for i in report.issues if i.severity == Severity.ERROR]
    warnings = [i for i in report.issues if i.severity == Severity.WARNING]
    infos = [i for i in report.issues if i.severity == Severity.INFO]

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for issue in errors:
            print(f"  [{issue.category}] {issue.message}")
            if issue.path:
                print(f"    Path: {issue.path}")
            if verbose and issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for issue in warnings:
            print(f"  [{issue.category}] {issue.message}")
            if verbose and issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")

    if verbose and infos:
        print(f"\nInfo ({len(infos)}):")
        for issue in infos:
            print(f"  [{issue.category}] {issue.message}")

    print()


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate brand skill against BRAND_SKILL_INTERFACE contract"
    )
    parser.add_argument(
        "brand_path",
        type=Path,
        help="Path to brand skill directory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show suggestions and info messages"
    )

    args = parser.parse_args()

    report = validate_brand(args.brand_path)

    if args.json:
        print(report.to_json())
    else:
        print_report(report, verbose=args.verbose)

    return 0 if report.valid else 1


if __name__ == "__main__":
    sys.exit(main())
