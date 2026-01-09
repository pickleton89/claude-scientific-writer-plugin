#!/usr/bin/env python3
"""
Validate YAML summary against schema before PDF generation.

Performs both structural validation and content quality checks.

Usage:
    python validate_yaml.py summary.yaml
    python validate_yaml.py summary.yaml --schema ../schemas/summary_output.yaml
    python validate_yaml.py summary.yaml --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.schemas import YAMLValidationResult

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def validate_metadata(data: dict) -> tuple[list[str], list[str]]:
    """Validate metadata section."""
    errors = []
    warnings = []

    if "metadata" not in data:
        errors.append("Missing required key: metadata")
        return errors, warnings

    meta = data["metadata"]

    # Required fields
    if "title" not in meta:
        errors.append("metadata.title is required")
    elif len(str(meta["title"])) < 10:
        warnings.append("metadata.title seems too short (<10 chars)")

    if "authors" not in meta:
        errors.append("metadata.authors is required")
    elif len(str(meta["authors"])) < 3:
        warnings.append("metadata.authors seems too short")

    if "year" not in meta:
        warnings.append("metadata.year is recommended")

    # Optional but recommended
    if "doi" not in meta and "pmid" not in meta:
        warnings.append("Consider adding DOI or PMID for reference")

    # Validate DOI format if present
    if "doi" in meta:
        doi = str(meta["doi"])
        if not doi.startswith("10."):
            errors.append(f"Invalid DOI format: {doi} (should start with '10.')")

    # Validate article type if present
    valid_types = ["Primary Research", "Review", "Computational", "Cell & Molecular"]
    if "article_type" in meta and meta["article_type"] not in valid_types:
        warnings.append(
            f"article_type '{meta['article_type']}' not in standard list: {valid_types}"
        )

    return errors, warnings


def validate_overview(data: dict) -> tuple[list[str], list[str]]:
    """Validate overview section."""
    errors = []
    warnings = []

    if "overview" not in data:
        errors.append("Missing required key: overview")
        return errors, warnings

    overview = str(data["overview"])

    if len(overview) < 100:
        errors.append(f"overview too short: {len(overview)} chars (need 100+)")
    elif len(overview) > 1000:
        warnings.append(f"overview may be too long: {len(overview)} chars")

    return errors, warnings


def validate_key_findings(data: dict) -> tuple[list[str], list[str]]:
    """Validate key_findings section."""
    errors = []
    warnings = []

    if "key_findings" not in data:
        errors.append("Missing required key: key_findings")
        return errors, warnings

    findings = data["key_findings"]

    if not isinstance(findings, list):
        errors.append("key_findings must be a list")
        return errors, warnings

    if len(findings) < 3:
        warnings.append(f"Only {len(findings)} key findings (recommend 3+)")

    for i, finding in enumerate(findings):
        if isinstance(finding, dict):
            if "finding" not in finding:
                errors.append(f"key_findings[{i}].finding is required")
            elif len(str(finding["finding"])) < 20:
                warnings.append(f"key_findings[{i}].finding seems too short")

            if "statistics" not in finding:
                warnings.append(f"key_findings[{i}] missing statistics")

            # Validate figure_ref format if present
            if "figure_ref" in finding:
                ref = str(finding["figure_ref"])
                if not re.match(r"^(Figure|Fig|Table)\s*\d+", ref, re.I):
                    warnings.append(
                        f"key_findings[{i}].figure_ref has non-standard format: {ref}"
                    )
        elif isinstance(finding, str):
            if len(finding) < 20:
                warnings.append(f"key_findings[{i}] seems too short")

    return errors, warnings


def validate_methods(data: dict) -> tuple[list[str], list[str]]:
    """Validate methods section."""
    errors = []
    warnings = []

    if "methods" not in data:
        errors.append("Missing required key: methods")
        return errors, warnings

    methods = data["methods"]

    if not isinstance(methods, dict):
        errors.append("methods must be an object")
        return errors, warnings

    # Required fields (matching schema requirements)
    if "study_design" not in methods:
        errors.append("methods.study_design is required")

    if "sample_size" not in methods:
        errors.append("methods.sample_size is required")

    return errors, warnings


def validate_limitations(data: dict) -> tuple[list[str], list[str]]:
    """Validate limitations section."""
    errors = []
    warnings = []

    if "limitations" not in data:
        errors.append("Missing required key: limitations")
        return errors, warnings

    lims = data["limitations"]

    if isinstance(lims, dict):
        author_stated = lims.get("author_stated", [])
        additional = lims.get("additional", [])
        total = len(author_stated) + len(additional)
        if total == 0:
            warnings.append("No limitations specified")
    elif isinstance(lims, list):
        if len(lims) == 0:
            warnings.append("No limitations specified")
    elif isinstance(lims, str):
        if len(lims) < 20:
            warnings.append("Limitations section seems too brief")

    return errors, warnings


def validate_key_figures(data: dict) -> tuple[list[str], list[str]]:
    """Validate key_figures section if present."""
    errors = []
    warnings = []

    if "key_figures" not in data:
        return errors, warnings  # Optional section

    figures = data["key_figures"]

    if not isinstance(figures, list):
        errors.append("key_figures must be a list")
        return errors, warnings

    for i, fig in enumerate(figures):
        if isinstance(fig, dict):
            if "number" not in fig:
                warnings.append(f"key_figures[{i}].number is recommended")
            else:
                num = str(fig["number"])
                if not re.match(r"^(Figure|Table)\s*\d+", num, re.I):
                    warnings.append(
                        f"key_figures[{i}].number has non-standard format: {num}"
                    )

    return errors, warnings


def validate_yaml_summary(
    yaml_path: str, schema_path: str | None = None
) -> YAMLValidationResult:
    """
    Validate YAML summary against schema and quality checks.

    Args:
        yaml_path: Path to YAML file
        schema_path: Optional path to JSON Schema file

    Returns:
        YAMLValidationResult with errors, warnings, and parsed data
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Load YAML
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return YAMLValidationResult(
            valid=False,
            errors=[f"YAML parse error: {e}"],
            warnings=[],
            data={},
        )

    if data is None:
        return YAMLValidationResult(
            valid=False,
            errors=["YAML file is empty"],
            warnings=[],
            data={},
        )

    # Run validation checks
    validators = [
        validate_metadata,
        validate_overview,
        validate_key_findings,
        validate_methods,
        validate_limitations,
        validate_key_figures,
    ]

    for validator in validators:
        errs, warns = validator(data)
        errors.extend(errs)
        warnings.extend(warns)

    # Full schema validation if available
    if HAS_JSONSCHEMA and schema_path and Path(schema_path).exists():
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message}")
        except Exception as e:
            warnings.append(f"Schema validation skipped: {e}")

    return YAMLValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        data=data,
    )


def print_result(result: YAMLValidationResult, yaml_path: str) -> None:
    """Print validation result in readable format."""
    status = "PASS" if result.valid else "FAIL"
    print(f"\n{'=' * 60}")
    print(f"YAML Validation: {status}")
    print(f"File: {yaml_path}")
    print(f"{'=' * 60}\n")

    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  [ERROR] {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  [WARN] {warning}")

    if not result.errors and not result.warnings:
        print("  All checks passed!")

    print(f"\nErrors: {len(result.errors)}, Warnings: {len(result.warnings)}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate YAML summary")
    parser.add_argument("yaml_file", help="Path to YAML summary")
    parser.add_argument("--schema", help="Path to JSON schema", default=None)
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not Path(args.yaml_file).exists():
        print(f"Error: File not found: {args.yaml_file}")
        return 1

    result = validate_yaml_summary(args.yaml_file, args.schema)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_result(result, args.yaml_file)

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
