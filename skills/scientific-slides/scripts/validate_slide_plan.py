#!/usr/bin/env python3
"""
Validate slide plan JSON against schema and business rules.

Deterministic validation before generation ensures:
- Valid JSON structure matching schema
- Appropriate slide count for duration
- Required slide types present
- Citation distribution follows best practices
- Color formats are valid

Usage:
    uv run python validate_slide_plan.py plan.json
    uv run python validate_slide_plan.py plan.json --strict
    uv run python validate_slide_plan.py plan.json --schema custom_schema.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import ValidationError, validate

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    ValidationError = Exception  # type: ignore[misc, assignment]


class SlidePlanValidator:
    """Validate slide plans against schema with additional business rules."""

    # Slide count guidelines by duration: (min, recommended, max)
    SLIDE_GUIDELINES: dict[int, tuple[int, int, int]] = {
        3: (3, 4, 5),  # Lightning talk
        5: (5, 6, 8),
        10: (8, 11, 14),
        15: (13, 16, 20),
        20: (18, 22, 26),
        30: (22, 27, 33),
        45: (32, 40, 50),
        60: (40, 52, 65),
        90: (55, 72, 90),
    }

    # Required slide types by talk type
    REQUIRED_SLIDES: dict[str, list[str]] = {
        "conference": ["title", "conclusion"],
        "seminar": ["title", "conclusion"],
        "defense": ["title", "conclusion", "acknowledgments"],
        "grant": ["title", "conclusion"],
        "journal_club": ["title"],
        "lightning": ["title"],
        "industry": ["title", "conclusion"],
        "tutorial": ["title"],
    }

    def __init__(self, schema_path: str | None = None):
        """
        Initialize validator with schema.

        Args:
            schema_path: Optional path to custom schema file
        """
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            # Default to schema in schemas/ directory
            self.schema_path = (
                Path(__file__).parent.parent / "schemas" / "slide_plan_schema.json"
            )

        self.schema = self._load_schema()

    def _load_schema(self) -> dict[str, Any]:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")

        with open(self.schema_path) as f:
            return json.load(f)

    def validate(self, plan: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
        """
        Validate slide plan against schema and business rules.

        Args:
            plan: Slide plan dictionary

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Schema validation — collect errors but continue to business rules so
        # callers get the full picture in a single pass. Only short-circuit if
        # the plan is so malformed that business rules cannot run safely
        # (missing the top-level required fields that downstream code reads).
        if HAS_JSONSCHEMA:
            try:
                validate(instance=plan, schema=self.schema)
            except ValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
        # Require the top-level fields downstream business rules depend on.
        required_fields = ["talk_type", "duration_minutes", "title", "slides"]
        missing = [f for f in required_fields if f not in plan]
        if missing:
            for field in missing:
                errors.append(f"Missing required field: {field}")
            return False, errors, warnings

        # Business rule validation
        talk_type = plan.get("talk_type", "conference")
        duration = plan.get("duration_minutes", 15)
        slides = plan.get("slides", [])
        slide_count = len(slides)

        # Check slide count vs duration
        guidelines = self._get_slide_guidelines(duration)
        if guidelines:
            min_slides, rec_slides, max_slides = guidelines
            if slide_count < min_slides:
                warnings.append(
                    f"Slide count ({slide_count}) below recommended minimum "
                    f"({min_slides}) for {duration}-minute talk"
                )
            elif slide_count > max_slides:
                warnings.append(
                    f"Slide count ({slide_count}) exceeds recommended maximum "
                    f"({max_slides}) for {duration}-minute talk"
                )

        # Check for required slide types
        slide_types = [s.get("slide_type") for s in slides]
        required_types = self.REQUIRED_SLIDES.get(talk_type, ["title"])

        for required_type in required_types:
            if required_type not in slide_types:
                warnings.append(f"No {required_type} slide found (recommended for {talk_type})")

        # Check citation distribution in introduction
        intro_citations = 0
        for i, slide in enumerate(slides):
            if i < len(slides) * 0.3:  # First 30% is intro
                intro_citations += len(slide.get("citations", []))

        if talk_type in ["conference", "seminar", "defense"] and intro_citations < 2:
            warnings.append(
                f"Few citations in introduction ({intro_citations}). "
                "Consider adding research context."
            )

        # Check key points per slide
        for i, slide in enumerate(slides):
            points = slide.get("key_points", [])
            if len(points) > 6:
                warnings.append(
                    f"Slide {i+1} has {len(points)} bullet points (max recommended: 6)"
                )
            # Check point length
            for j, point in enumerate(points):
                if len(point) > 60:
                    warnings.append(
                        f"Slide {i+1}, point {j+1} exceeds 60 characters ({len(point)} chars)"
                    )

        # Validate color formats
        formatting = plan.get("formatting", {})
        color_keys = ["background_color", "text_color", "accent_color", "highlight_color"]
        for color_key in color_keys:
            color = formatting.get(color_key, "")
            if color and not self._is_valid_hex(color):
                errors.append(f"Invalid hex color for {color_key}: {color}")

        # Check title length
        for i, slide in enumerate(slides):
            title = slide.get("title", "")
            if len(title) > 80:
                warnings.append(f"Slide {i+1} title exceeds 80 characters ({len(title)} chars)")

        return len(errors) == 0, errors, warnings

    def _get_slide_guidelines(self, duration: int) -> tuple[int, int, int] | None:
        """Get slide count guidelines for duration."""
        if duration in self.SLIDE_GUIDELINES:
            return self.SLIDE_GUIDELINES[duration]

        # Find nearest duration
        durations = sorted(self.SLIDE_GUIDELINES.keys())
        nearest = min(durations, key=lambda x: abs(x - duration))
        return self.SLIDE_GUIDELINES[nearest]

    def _is_valid_hex(self, color: str) -> bool:
        """Check if string is valid hex color."""
        if not color.startswith("#"):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

    def get_recommendations(self, plan: dict[str, Any]) -> dict[str, Any]:
        """
        Generate recommendations based on plan analysis.

        Returns:
            Dictionary with recommendations for improvement
        """
        duration = plan.get("duration_minutes", 15)
        slides = plan.get("slides", [])
        guidelines = self._get_slide_guidelines(duration)

        recommendations: dict[str, Any] = {
            "slide_count": {
                "current": len(slides),
                "min": guidelines[0] if guidelines else None,
                "recommended": guidelines[1] if guidelines else None,
                "max": guidelines[2] if guidelines else None,
            },
            "time_per_slide": round(duration / len(slides), 1) if slides else None,
            "suggestions": [],
        }

        # Add specific suggestions
        if guidelines:
            if len(slides) < guidelines[0]:
                recommendations["suggestions"].append(
                    f"Add {guidelines[0] - len(slides)} more slides to meet minimum"
                )
            elif len(slides) > guidelines[2]:
                recommendations["suggestions"].append(
                    f"Consider removing {len(slides) - guidelines[2]} slides or extending duration"
                )

        time_per_slide = recommendations["time_per_slide"]
        if time_per_slide and time_per_slide < 0.5:
            recommendations["suggestions"].append(
                "Very fast pacing - less than 30 seconds per slide"
            )
        elif time_per_slide and time_per_slide > 3:
            recommendations["suggestions"].append(
                "Consider breaking up long slides or reducing duration"
            )

        return recommendations


def main() -> None:
    """CLI for slide plan validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate slide plan JSON against schema")
    parser.add_argument("plan_file", help="Path to slide plan JSON file")
    parser.add_argument("--schema", help="Path to custom schema file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--recommendations", action="store_true", help="Show recommendations"
    )

    args = parser.parse_args()

    # Load plan
    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print(f"Error: File not found: {args.plan_file}")
        sys.exit(1)

    with open(plan_path) as f:
        try:
            plan = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            sys.exit(1)

    # Validate
    validator = SlidePlanValidator(args.schema)
    is_valid, errors, warnings = validator.validate(plan)

    if args.strict and warnings:
        is_valid = False

    if args.json:
        output = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
        }
        if args.recommendations:
            output["recommendations"] = validator.get_recommendations(plan)
        print(json.dumps(output, indent=2))
    else:
        print(f"\nValidating: {args.plan_file}")
        print("=" * 50)

        if errors:
            print("\nErrors:")
            for e in errors:
                print(f"  - {e}")

        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  - {w}")

        if args.recommendations:
            recs = validator.get_recommendations(plan)
            print("\nRecommendations:")
            print(f"  Slide count: {recs['slide_count']['current']}")
            print(
                f"  Guideline: {recs['slide_count']['min']}-{recs['slide_count']['max']} "
                f"(recommended: {recs['slide_count']['recommended']})"
            )
            print(f"  Time per slide: {recs['time_per_slide']} minutes")
            if recs["suggestions"]:
                print("  Suggestions:")
                for s in recs["suggestions"]:
                    print(f"    - {s}")

        print(f"\nResult: {'VALID' if is_valid else 'INVALID'}")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
