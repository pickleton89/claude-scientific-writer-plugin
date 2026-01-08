#!/usr/bin/env python3
"""
Deterministic validation for generated slide images.

Checks measurable quality criteria without AI:
- Dimensions and aspect ratio (16:9 target)
- File size bounds
- White space estimation
- Contrast analysis
- Brand color compliance

Usage:
    uv run python validate_slide_image.py slide.png
    uv run python validate_slide_image.py slide.png --brand-colors "#2DB2E8" "#E8622D"
    uv run python validate_slide_image.py slide.png --json
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class ValidationResult:
    """Structured validation result."""

    passed: bool
    score: float  # 0-10 deterministic score
    checks: dict[str, bool] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SlideImageValidator:
    """Validate generated slide images with deterministic checks."""

    # Target dimensions for 16:9 slides
    TARGET_ASPECT_RATIO = 16 / 9
    ASPECT_TOLERANCE = 0.05  # 5% tolerance

    # Minimum dimensions
    MIN_WIDTH = 1280
    MIN_HEIGHT = 720
    PREFERRED_WIDTH = 1920

    # File size bounds (KB)
    MIN_FILE_SIZE_KB = 50
    MAX_FILE_SIZE_KB = 5000

    # White space bounds
    MIN_WHITE_SPACE = 0.25
    MAX_WHITE_SPACE = 0.70

    # Contrast threshold
    MIN_CONTRAST = 0.3
    ADEQUATE_CONTRAST = 0.5

    def validate(
        self, image_path: str, expected_colors: list[str] | None = None
    ) -> ValidationResult:
        """
        Run all deterministic validation checks.

        Args:
            image_path: Path to slide image
            expected_colors: Optional list of expected brand colors (hex)

        Returns:
            ValidationResult with pass/fail and detailed scores
        """
        path = Path(image_path)
        checks: dict[str, bool] = {}
        details: dict[str, Any] = {}
        warnings: list[str] = []
        errors: list[str] = []

        # Check 1: File exists and readable
        if not path.exists():
            return ValidationResult(
                passed=False,
                score=0,
                errors=[f"File not found: {image_path}"],
            )

        try:
            img = Image.open(path)
        except Exception as e:
            return ValidationResult(
                passed=False,
                score=0,
                errors=[f"Cannot open image: {e}"],
            )

        # Check 2: Dimensions and aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        aspect_diff = abs(aspect_ratio - self.TARGET_ASPECT_RATIO) / self.TARGET_ASPECT_RATIO

        checks["aspect_ratio"] = aspect_diff <= self.ASPECT_TOLERANCE
        checks["min_dimensions"] = width >= self.MIN_WIDTH and height >= self.MIN_HEIGHT
        checks["preferred_dimensions"] = width >= self.PREFERRED_WIDTH

        details["width"] = width
        details["height"] = height
        details["aspect_ratio"] = round(aspect_ratio, 3)
        details["aspect_deviation"] = f"{aspect_diff * 100:.1f}%"

        if not checks["aspect_ratio"]:
            warnings.append(
                f"Aspect ratio {aspect_ratio:.2f} deviates from 16:9 ({self.TARGET_ASPECT_RATIO:.2f})"
            )
        if not checks["min_dimensions"]:
            errors.append(
                f"Dimensions {width}x{height} below minimum {self.MIN_WIDTH}x{self.MIN_HEIGHT}"
            )

        # Check 3: File size
        file_size_kb = path.stat().st_size / 1024
        checks["file_size_min"] = file_size_kb >= self.MIN_FILE_SIZE_KB
        checks["file_size_max"] = file_size_kb <= self.MAX_FILE_SIZE_KB
        details["file_size_kb"] = round(file_size_kb, 1)

        if not checks["file_size_min"]:
            warnings.append(f"File size {file_size_kb:.0f}KB suspiciously small")
        if not checks["file_size_max"]:
            warnings.append(f"File size {file_size_kb:.0f}KB exceeds {self.MAX_FILE_SIZE_KB}KB")

        # Check 4: Color analysis
        colors = self._extract_dominant_colors(img, k=5)
        details["dominant_colors"] = colors

        # Check 5: White space estimation
        white_space_pct = self._estimate_white_space(img)
        checks["adequate_white_space"] = self.MIN_WHITE_SPACE <= white_space_pct <= self.MAX_WHITE_SPACE
        details["white_space_percent"] = round(white_space_pct * 100, 1)

        if white_space_pct < self.MIN_WHITE_SPACE:
            warnings.append(
                f"Low white space ({white_space_pct*100:.0f}%) - slide may be cluttered"
            )
        elif white_space_pct > self.MAX_WHITE_SPACE:
            warnings.append(
                f"High white space ({white_space_pct*100:.0f}%) - slide may lack content"
            )

        # Check 6: Contrast estimation
        contrast_score = self._estimate_contrast(img)
        checks["adequate_contrast"] = contrast_score >= self.ADEQUATE_CONTRAST
        details["contrast_score"] = round(contrast_score, 2)

        if contrast_score < self.MIN_CONTRAST:
            errors.append("Very low contrast - text may be unreadable")
        elif contrast_score < self.ADEQUATE_CONTRAST:
            warnings.append("Low contrast - consider increasing text/background difference")

        # Check 7: Brand color compliance (if expected colors provided)
        if expected_colors:
            compliance = self._check_color_compliance(colors, expected_colors)
            checks["brand_compliance"] = compliance >= 0.5
            details["brand_compliance"] = round(compliance, 2)

        # Calculate deterministic score (0-10)
        score = self._calculate_score(checks, details)

        # Determine overall pass/fail
        passed = len(errors) == 0 and score >= 5.0

        return ValidationResult(
            passed=passed,
            score=score,
            checks=checks,
            details=details,
            warnings=warnings,
            errors=errors,
        )

    def _extract_dominant_colors(self, img: Image.Image, k: int = 5) -> list[str]:
        """Extract dominant colors as hex codes."""
        # Resize for performance
        img_small = img.copy()
        img_small.thumbnail((150, 150))

        # Convert to RGB if needed
        if img_small.mode != "RGB":
            img_small = img_small.convert("RGB")

        # Get color frequency
        colors = img_small.getcolors(maxcolors=10000)
        if not colors:
            return []

        # Sort by frequency and get top k
        colors.sort(key=lambda x: x[0], reverse=True)
        top_colors = colors[:k]

        # Convert to hex
        return [f"#{r:02x}{g:02x}{b:02x}" for count, (r, g, b) in top_colors]

    def _estimate_white_space(self, img: Image.Image) -> float:
        """Estimate percentage of white/light space in image."""
        img_small = img.copy()
        img_small.thumbnail((200, 200))

        if img_small.mode != "RGB":
            img_small = img_small.convert("RGB")

        pixels = list(img_small.getdata())
        light_threshold = 200
        light_pixels = sum(1 for r, g, b in pixels if (r + g + b) / 3 > light_threshold)

        return light_pixels / len(pixels)

    def _estimate_contrast(self, img: Image.Image) -> float:
        """Estimate overall contrast (0-1 scale)."""
        img_small = img.copy()
        img_small.thumbnail((200, 200))

        if img_small.mode != "L":
            img_gray = img_small.convert("L")
        else:
            img_gray = img_small

        pixels = list(img_gray.getdata())
        if not pixels:
            return 0.5

        min_val = min(pixels)
        max_val = max(pixels)

        # Normalize to 0-1
        return (max_val - min_val) / 255

    def _check_color_compliance(self, actual: list[str], expected: list[str]) -> float:
        """Check how well actual colors match expected brand colors."""
        if not actual or not expected:
            return 0.5

        matches = 0
        check_count = min(3, len(actual))
        for actual_color in actual[:check_count]:
            for expected_color in expected:
                if self._color_distance(actual_color, expected_color) < 50:
                    matches += 1
                    break

        return matches / check_count

    def _color_distance(self, hex1: str, hex2: str) -> float:
        """Calculate Euclidean distance between two hex colors."""
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
        return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    def _calculate_score(self, checks: dict[str, bool], details: dict[str, Any]) -> float:
        """Calculate deterministic quality score (0-10)."""
        score = 0.0

        # Dimensions (2 points)
        if checks.get("preferred_dimensions"):
            score += 2.0
        elif checks.get("min_dimensions"):
            score += 1.0

        # Aspect ratio (2 points)
        if checks.get("aspect_ratio"):
            score += 2.0
        else:
            deviation_str = str(details.get("aspect_deviation", "100%"))
            deviation = float(deviation_str.rstrip("%"))
            score += max(0, 2.0 - (deviation / 10))

        # File size (1 point)
        if checks.get("file_size_min") and checks.get("file_size_max"):
            score += 1.0
        elif checks.get("file_size_min") or checks.get("file_size_max"):
            score += 0.5

        # White space (2 points)
        if checks.get("adequate_white_space"):
            score += 2.0
        else:
            ws = details.get("white_space_percent", 0) / 100
            if 0.15 <= ws <= 0.80:
                score += 1.0

        # Contrast (2 points)
        contrast = details.get("contrast_score", 0)
        score += min(2.0, contrast * 3)

        # Brand compliance (1 point, if checked)
        if "brand_compliance" in details:
            score += details["brand_compliance"]
        else:
            score += 1.0  # Default point if not checking brand

        return min(10.0, round(score, 2))


def main() -> None:
    """Command-line interface for slide image validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate generated slide images")
    parser.add_argument("image", help="Path to slide image")
    parser.add_argument("--brand-colors", nargs="+", help="Expected brand colors (hex)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = SlideImageValidator()
    result = validator.validate(args.image, args.brand_colors)

    if args.json:
        print(
            json.dumps(
                {
                    "passed": result.passed,
                    "score": result.score,
                    "checks": result.checks,
                    "details": result.details,
                    "warnings": result.warnings,
                    "errors": result.errors,
                },
                indent=2,
            )
        )
    else:
        print(f"\n{'='*50}")
        print(f"Slide Image Validation: {args.image}")
        print(f"{'='*50}")
        print(f"\nScore: {result.score}/10")
        print(f"Status: {'PASSED' if result.passed else 'FAILED'}")

        if result.errors:
            print("\nErrors:")
            for e in result.errors:
                print(f"  - {e}")

        if result.warnings:
            print("\nWarnings:")
            for w in result.warnings:
                print(f"  - {w}")

        print("\nDetails:")
        for k, v in result.details.items():
            print(f"  {k}: {v}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
