#!/usr/bin/env python3
"""
Poster Specification Validator

Validates poster specification YAML files against the defined schema.
Ensures all required fields are present and values are valid before
starting poster generation.

Usage:
    python validate_spec.py poster_spec.yaml
    python validate_spec.py poster_spec.yaml --output validated_spec.json
    python validate_spec.py poster_spec.yaml --strict

Output: Validation result with any errors or warnings.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from utils.dimensions import POSTER_SIZES
from utils.schemas import PosterSpec


# Valid enum values
VALID_ORIENTATIONS = {"portrait", "landscape"}
VALID_FORMATS = {"latex", "pptx"}
VALID_LATEX_PACKAGES = {"beamerposter", "tikzposter", "baposter"}
VALID_BRANDS = {"oligon", "generic", "custom"}
VALID_FIGURE_TYPES = {"schematic", "chart", "photo", "diagram", "table", "graph"}

# Required sections (at minimum)
RECOMMENDED_SECTIONS = {"introduction", "methods", "results", "conclusions"}


def validate_spec_file(spec_path: Path, strict: bool = False) -> dict:
    """
    Validate a poster specification YAML file.

    Args:
        spec_path: Path to the YAML specification file
        strict: If True, treat warnings as errors

    Returns:
        Dictionary with validation results:
        - valid: Boolean overall validity
        - errors: List of error messages
        - warnings: List of warning messages
        - spec: Parsed PosterSpec object (if valid)
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "spec": None,
        "spec_dict": None,
    }

    # Check file exists
    if not spec_path.exists():
        result["errors"].append(f"Specification file not found: {spec_path}")
        result["valid"] = False
        return result

    # Check YAML support
    if not HAS_YAML:
        result["errors"].append("PyYAML not installed. Run: pip install pyyaml")
        result["valid"] = False
        return result

    # Parse YAML
    try:
        content = spec_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        result["errors"].append(f"Invalid YAML syntax: {e}")
        result["valid"] = False
        return result

    if not isinstance(data, dict):
        result["errors"].append("Specification must be a YAML dictionary")
        result["valid"] = False
        return result

    # Handle nested 'poster' key (from example schema)
    if "poster" in data and isinstance(data["poster"], dict):
        poster_data = data["poster"]
        # Merge top-level keys with poster keys
        for key in ["authors", "affiliations", "content", "figures", "assets"]:
            if key in data and key not in poster_data:
                poster_data[key] = data[key]
        data = {**poster_data, **{k: v for k, v in data.items() if k not in ["poster"]}}

    # Validate required fields
    if not data.get("title"):
        result["errors"].append("Missing required field: title")

    if not data.get("dimensions"):
        result["errors"].append("Missing required field: dimensions")
    else:
        # Validate dimensions value
        dims = data["dimensions"].upper()
        if dims not in POSTER_SIZES and not _is_custom_dimension(dims):
            result["warnings"].append(
                f"Non-standard dimension '{data['dimensions']}'. "
                f"Valid sizes: {', '.join(POSTER_SIZES.keys())}"
            )

    # Validate orientation
    orientation = data.get("orientation", "portrait").lower()
    if orientation not in VALID_ORIENTATIONS:
        result["errors"].append(
            f"Invalid orientation: '{orientation}'. Must be: {', '.join(VALID_ORIENTATIONS)}"
        )

    # Validate format
    poster_format = data.get("format", data.get("poster_format", "latex")).lower()
    if poster_format not in VALID_FORMATS:
        result["errors"].append(
            f"Invalid format: '{poster_format}'. Must be: {', '.join(VALID_FORMATS)}"
        )

    # Validate LaTeX package
    if poster_format == "latex":
        latex_pkg = data.get("latex_package", "tikzposter").lower()
        if latex_pkg not in VALID_LATEX_PACKAGES:
            result["errors"].append(
                f"Invalid latex_package: '{latex_pkg}'. "
                f"Must be: {', '.join(VALID_LATEX_PACKAGES)}"
            )

    # Validate brand
    brand = data.get("brand", "oligon").lower()
    if brand not in VALID_BRANDS:
        result["warnings"].append(
            f"Unknown brand: '{brand}'. Known brands: {', '.join(VALID_BRANDS)}"
        )

    # Validate authors
    authors = data.get("authors", [])
    affiliations = data.get("affiliations", {})

    if not authors:
        result["warnings"].append("No authors specified")
    else:
        for i, author in enumerate(authors):
            if not isinstance(author, dict):
                result["errors"].append(f"Author {i} must be a dictionary")
                continue

            if not author.get("name"):
                result["errors"].append(f"Author {i} missing required field: name")

            aff = author.get("affiliation")
            if aff is not None:
                # Handle both string and int affiliation keys
                aff_key = int(aff) if isinstance(aff, (int, str)) and str(aff).isdigit() else aff
                if aff_key not in affiliations:
                    result["errors"].append(
                        f"Author '{author.get('name', i)}' references undefined "
                        f"affiliation: {aff}"
                    )

    # Validate content sections
    content = data.get("content", {})
    if not content:
        result["warnings"].append("No content sections defined")
    else:
        found_sections = set(content.keys())
        missing_recommended = RECOMMENDED_SECTIONS - {s.lower() for s in found_sections}

        if missing_recommended:
            result["warnings"].append(
                f"Missing recommended sections: {', '.join(missing_recommended)}"
            )

        # Validate word budgets
        total_budget = 0
        for section_name, section_data in content.items():
            if isinstance(section_data, dict):
                budget = section_data.get("word_budget", 0)
                if budget < 0:
                    result["errors"].append(
                        f"Section '{section_name}' has negative word budget"
                    )
                total_budget += budget

        if total_budget > 800:
            result["warnings"].append(
                f"Total word budget ({total_budget}) exceeds recommended maximum (800)"
            )
        elif total_budget < 300 and total_budget > 0:
            result["warnings"].append(
                f"Total word budget ({total_budget}) below recommended minimum (300)"
            )

    # Validate figures
    figures = data.get("figures", [])
    figure_ids = set()

    for i, fig in enumerate(figures):
        if not isinstance(fig, dict):
            result["errors"].append(f"Figure {i} must be a dictionary")
            continue

        fig_id = fig.get("id")
        if not fig_id:
            result["errors"].append(f"Figure {i} missing required field: id")
        elif fig_id in figure_ids:
            result["errors"].append(f"Duplicate figure id: {fig_id}")
        else:
            figure_ids.add(fig_id)

        fig_type = fig.get("type", fig.get("figure_type", "")).lower()
        if fig_type and fig_type not in VALID_FIGURE_TYPES:
            result["warnings"].append(
                f"Figure '{fig_id}' has unknown type: '{fig_type}'"
            )

        min_dpi = fig.get("min_dpi", 300)
        if min_dpi < 150:
            result["warnings"].append(
                f"Figure '{fig_id}' has low DPI requirement ({min_dpi})"
            )

    # Check figure references in content
    for section_name, section_data in content.items():
        if isinstance(section_data, dict):
            fig_id = section_data.get("figure_id")
            if fig_id and fig_id not in figure_ids:
                result["errors"].append(
                    f"Section '{section_name}' references undefined figure: {fig_id}"
                )

    # Validate assets
    assets = data.get("assets", {})
    logos = assets.get("logos", data.get("logos", []))
    qr_codes = assets.get("qr_codes", data.get("qr_codes", []))

    for logo in logos:
        if isinstance(logo, dict):
            path = logo.get("path")
            if path and Path(path).suffix.lower() not in {".pdf", ".png", ".jpg", ".jpeg", ".svg"}:
                result["warnings"].append(f"Logo '{path}' may not be optimal format for print")

    for qr in qr_codes:
        if isinstance(qr, dict):
            url = qr.get("url")
            if url and not url.startswith(("http://", "https://")):
                result["warnings"].append(f"QR code URL may be invalid: {url}")

    # Determine overall validity
    if result["errors"]:
        result["valid"] = False
    elif strict and result["warnings"]:
        result["valid"] = False

    # Try to create PosterSpec object
    if result["valid"] or not result["errors"]:
        try:
            spec = PosterSpec.from_dict(data)
            spec_errors = spec.validate()
            if spec_errors:
                result["errors"].extend(spec_errors)
                result["valid"] = False
            else:
                result["spec"] = spec
                result["spec_dict"] = spec.to_dict()
        except Exception as e:
            result["errors"].append(f"Failed to parse specification: {e}")
            result["valid"] = False

    return result


def _is_custom_dimension(dim_str: str) -> bool:
    """Check if dimension string is a valid custom format (e.g., '40x60')."""
    import re

    return bool(re.match(r"^\d+x\d+$", dim_str))


def main():
    parser = argparse.ArgumentParser(
        description="Validate poster specification YAML file."
    )
    parser.add_argument(
        "spec_file",
        type=Path,
        help="Path to poster specification YAML file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output validated specification as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output JSON only (no human-readable summary)",
    )

    args = parser.parse_args()

    # Run validation
    result = validate_spec_file(args.spec_file, strict=args.strict)

    # Output results
    if args.json:
        output = {
            "valid": result["valid"],
            "errors": result["errors"],
            "warnings": result["warnings"],
        }
        if result["spec_dict"]:
            output["spec"] = result["spec_dict"]
        print(json.dumps(output, indent=2))
    else:
        # Human-readable summary
        print("=" * 60)
        print("POSTER SPECIFICATION VALIDATION")
        print("=" * 60)
        print(f"\nFile: {args.spec_file}")
        print(f"Status: {'VALID' if result['valid'] else 'INVALID'}")

        if result["errors"]:
            print(f"\nErrors ({len(result['errors'])}):")
            for err in result["errors"]:
                print(f"  X {err}")

        if result["warnings"]:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warn in result["warnings"]:
                print(f"  ~ {warn}")

        if result["valid"] and result["spec"]:
            spec = result["spec"]
            print("\nParsed Specification:")
            print(f"  Title: {spec.title}")
            print(f"  Dimensions: {spec.dimensions} ({spec.orientation})")
            print(f"  Format: {spec.poster_format}")
            if spec.poster_format == "latex":
                print(f"  LaTeX Package: {spec.latex_package}")
            print(f"  Authors: {len(spec.authors)}")
            print(f"  Sections: {len(spec.content)}")
            print(f"  Figures: {len(spec.figures)}")

        print("")

    # Save validated spec if requested
    if args.output and result["spec_dict"]:
        args.output.write_text(json.dumps(result["spec_dict"], indent=2))
        if not args.json:
            print(f"Validated spec saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
