# Scientific Slides - Determinism Audit & Implementation Plan

> **Audit Date:** January 7, 2026
> **Skill Version:** 2.3.0
> **Development Stage:** First Draft
> **Auditor:** Claude Opus 4.5

---

## Executive Summary

The scientific-slides skill is well-architected with strong foundational structure—deterministic validation scripts, structured templates, and comprehensive reference documentation. However, the core slide generation workflow relies heavily on stochastic AI components (image generation and quality review) without sufficient deterministic guardrails.

**Key Opportunities:**
- Add code-based quality validation for measurable criteria
- Implement structured input schemas for slide plans
- Create hybrid scoring that combines deterministic and AI-based evaluation
- Consolidate overlapping documentation

**Expected Impact:** 40-60% reduction in output variance while maintaining creative flexibility for visual content.

---

## Current State Analysis

### Skill Architecture

```
scientific-slides/
├── SKILL.md                 # Main skill definition (well-structured)
├── references/              # 8 reference documents (some overlap)
│   ├── expert_guide.md
│   ├── slide_design_principles.md
│   ├── talk_types_guide.md
│   ├── presentation_structure.md
│   ├── data_visualization_slides.md
│   ├── output_templates.md
│   ├── beamer_guide.md
│   └── visual_review_workflow.md
├── scripts/                 # Python utilities
│   ├── generate_slide_image.py      # Wrapper (deterministic)
│   ├── generate_slide_image_ai.py   # AI generation (stochastic)
│   ├── validate_presentation.py     # Validation (deterministic)
│   ├── slides_to_pdf.py            # PDF assembly (deterministic)
│   └── pdf_to_images.py            # Image extraction (deterministic)
└── assets/                  # Templates and guides
    ├── beamer_template_*.tex
    ├── timing_guidelines.md
    └── powerpoint_design_guide.md
```

### Stochastic vs Deterministic Components

| Component | Current State | Reproducibility |
|-----------|---------------|-----------------|
| Slide image generation | AI (Nano Banana Pro) | Low |
| Quality review scoring | AI (Gemini 3 Pro) | Low |
| Prompt improvement | AI-based | Low |
| File validation | Code-based | High |
| Slide count guidelines | Lookup table | High |
| Time allocation | Lookup table | High |
| Color schemes | Defined constants | High |
| LaTeX compilation | Deterministic | High |

### Identified Issues

1. **Input Variance:** Free-form prompts lead to inconsistent outputs
2. **Quality Scoring:** Entirely AI-dependent, scores vary across runs
3. **Threshold Calibration:** 6.5/10 threshold lacks documentation
4. **Documentation Duplication:** Guidelines in both SKILL.md and Python scripts
5. **No Post-Generation Validation:** AI output accepted without deterministic checks

---

## Detailed Findings

### Input Analysis

**Current Problems:**
- Talk type is free-text (should be enumerated)
- Slide content prompts have no structure validation
- "FORMATTING GOAL" is semi-structured but not validated
- No schema for slide plans

**Impact:** Same logical request can produce vastly different prompts, leading to output variance.

### Output Analysis

**Current Problems:**
- Generated images not validated post-generation
- No deterministic quality checks before acceptance
- Iteration count depends on stochastic review feedback

**Impact:** Quality inconsistent; some poor outputs accepted, some good outputs rejected.

### Quality Review Analysis

**Current Implementation (generate_slide_image_ai.py:404-516):**
- Uses Gemini 3 Pro to score 0-10
- Five criteria: Visual Impact, Clarity, Readability, Composition, Relevance
- Threshold: 6.5/10 (hardcoded, no calibration docs)

**Problem:** All five criteria use LLM judgment, but 3 are measurable:
- Readability (contrast, font size) - can be measured with image analysis
- Composition (white space, margins) - can be calculated from pixels
- Visual Impact (dimensions, resolution) - deterministic file properties

---

## Implementation Plan

### Phase 1: Deterministic Post-Generation Validation (Week 1-2)

**Goal:** Add code-based validation layer that runs before accepting AI-generated images.

#### Step 1.1: Create Image Validation Module

**File:** `scripts/validate_slide_image.py`

```python
#!/usr/bin/env python3
"""
Deterministic validation for generated slide images.
Checks measurable quality criteria without AI.
"""

from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from colorsys import rgb_to_hls
import math


@dataclass
class ValidationResult:
    """Structured validation result."""
    passed: bool
    score: float  # 0-10 deterministic score
    checks: Dict[str, bool]
    details: Dict[str, any]
    warnings: List[str]
    errors: List[str]


class SlideImageValidator:
    """Validate generated slide images with deterministic checks."""

    # Target dimensions for 16:9 slides
    TARGET_ASPECT_RATIO = 16 / 9
    ASPECT_TOLERANCE = 0.05  # 5% tolerance

    # Minimum dimensions
    MIN_WIDTH = 1280
    MIN_HEIGHT = 720
    PREFERRED_WIDTH = 1920
    PREFERRED_HEIGHT = 1080

    # File size bounds (KB)
    MIN_FILE_SIZE_KB = 50
    MAX_FILE_SIZE_KB = 5000

    # WCAG contrast requirements
    MIN_CONTRAST_RATIO = 4.5  # AA standard
    TARGET_CONTRAST_RATIO = 7.0  # AAA standard

    def validate(self, image_path: str,
                 expected_colors: Optional[List[str]] = None) -> ValidationResult:
        """
        Run all deterministic validation checks.

        Args:
            image_path: Path to slide image
            expected_colors: Optional list of expected brand colors (hex)

        Returns:
            ValidationResult with pass/fail and detailed scores
        """
        path = Path(image_path)
        checks = {}
        details = {}
        warnings = []
        errors = []

        # Check 1: File exists and readable
        if not path.exists():
            return ValidationResult(
                passed=False, score=0, checks={}, details={},
                warnings=[], errors=[f"File not found: {image_path}"]
            )

        try:
            img = Image.open(path)
        except Exception as e:
            return ValidationResult(
                passed=False, score=0, checks={}, details={},
                warnings=[], errors=[f"Cannot open image: {e}"]
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
            warnings.append(f"Aspect ratio {aspect_ratio:.2f} deviates from 16:9 ({self.TARGET_ASPECT_RATIO:.2f})")
        if not checks["min_dimensions"]:
            errors.append(f"Dimensions {width}x{height} below minimum {self.MIN_WIDTH}x{self.MIN_HEIGHT}")

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
        checks["adequate_white_space"] = 0.25 <= white_space_pct <= 0.70
        details["white_space_percent"] = round(white_space_pct * 100, 1)

        if white_space_pct < 0.25:
            warnings.append(f"Low white space ({white_space_pct*100:.0f}%) - slide may be cluttered")
        elif white_space_pct > 0.70:
            warnings.append(f"High white space ({white_space_pct*100:.0f}%) - slide may lack content")

        # Check 6: Contrast estimation
        contrast_score = self._estimate_contrast(img)
        checks["adequate_contrast"] = contrast_score >= 0.5
        details["contrast_score"] = round(contrast_score, 2)

        if contrast_score < 0.3:
            errors.append("Very low contrast - text may be unreadable")
        elif contrast_score < 0.5:
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
            errors=errors
        )

    def _extract_dominant_colors(self, img: Image.Image, k: int = 5) -> List[str]:
        """Extract dominant colors as hex codes."""
        # Resize for performance
        img_small = img.copy()
        img_small.thumbnail((150, 150))

        # Convert to RGB if needed
        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')

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

        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')

        pixels = list(img_small.getdata())
        light_pixels = sum(1 for r, g, b in pixels
                         if (r + g + b) / 3 > 200)  # Light threshold

        return light_pixels / len(pixels)

    def _estimate_contrast(self, img: Image.Image) -> float:
        """Estimate overall contrast (0-1 scale)."""
        img_small = img.copy()
        img_small.thumbnail((200, 200))

        if img_small.mode != 'L':
            img_gray = img_small.convert('L')
        else:
            img_gray = img_small

        pixels = list(img_gray.getdata())
        if not pixels:
            return 0.5

        min_val = min(pixels)
        max_val = max(pixels)

        # Normalize to 0-1
        return (max_val - min_val) / 255

    def _check_color_compliance(self, actual: List[str], expected: List[str]) -> float:
        """Check how well actual colors match expected brand colors."""
        if not actual or not expected:
            return 0.5

        matches = 0
        for actual_color in actual[:3]:  # Check top 3 colors
            for expected_color in expected:
                if self._color_distance(actual_color, expected_color) < 50:
                    matches += 1
                    break

        return matches / min(3, len(actual))

    def _color_distance(self, hex1: str, hex2: str) -> float:
        """Calculate Euclidean distance between two hex colors."""
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
        return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

    def _calculate_score(self, checks: Dict[str, bool], details: Dict) -> float:
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
            deviation = float(details.get("aspect_deviation", "100%").rstrip('%'))
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

        return min(10.0, score)
```

#### Step 1.2: Integrate Validation into Generation Pipeline

**Update:** `scripts/generate_slide_image_ai.py`

Add validation call after image generation, before AI review:

```python
# After line 621 (image saved to temp file)
from validate_slide_image import SlideImageValidator

validator = SlideImageValidator()
validation_result = validator.validate(str(temp_path))

if not validation_result.passed:
    self._log(f"Deterministic validation failed: {validation_result.errors}")
    # Skip AI review, regenerate immediately
    current_prompt = self.improve_prompt(user_prompt,
        f"Previous attempt failed validation: {validation_result.errors}",
        i + 1, visual_only)
    continue

# Adjust quality threshold based on deterministic score
# Hybrid scoring: 40% deterministic, 60% AI review
deterministic_weight = 0.4
```

#### Step 1.3: Add CLI Interface for Standalone Validation

```python
# Add to validate_slide_image.py

def main():
    """Command-line interface for slide image validation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Validate generated slide images"
    )
    parser.add_argument("image", help="Path to slide image")
    parser.add_argument("--brand-colors", nargs="+",
                       help="Expected brand colors (hex)")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")

    args = parser.parse_args()

    validator = SlideImageValidator()
    result = validator.validate(args.image, args.brand_colors)

    if args.json:
        print(json.dumps({
            "passed": result.passed,
            "score": result.score,
            "checks": result.checks,
            "details": result.details,
            "warnings": result.warnings,
            "errors": result.errors
        }, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"Slide Image Validation: {args.image}")
        print(f"{'='*50}")
        print(f"\nScore: {result.score}/10")
        print(f"Status: {'PASSED' if result.passed else 'FAILED'}")

        if result.errors:
            print(f"\nErrors:")
            for e in result.errors:
                print(f"  - {e}")

        if result.warnings:
            print(f"\nWarnings:")
            for w in result.warnings:
                print(f"  - {w}")

        print(f"\nDetails:")
        for k, v in result.details.items():
            print(f"  {k}: {v}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
```

---

### Phase 2: Structured Input Schema (Week 2-3)

**Goal:** Define and enforce structured inputs to reduce prompt variance.

#### Step 2.1: Create JSON Schema for Slide Plans

**File:** `schemas/slide_plan_schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "slide_plan_schema",
  "title": "Scientific Slide Plan",
  "description": "Structured input for scientific presentation generation",
  "type": "object",
  "required": ["talk_type", "duration_minutes", "title", "slides"],
  "properties": {
    "talk_type": {
      "type": "string",
      "enum": ["conference", "seminar", "defense", "grant", "journal_club", "lightning", "industry", "tutorial"],
      "description": "Type of scientific talk"
    },
    "duration_minutes": {
      "type": "integer",
      "minimum": 3,
      "maximum": 90,
      "description": "Total presentation duration in minutes"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "Presentation title"
    },
    "speaker": {
      "type": "string",
      "default": "K-Dense",
      "description": "Speaker name"
    },
    "affiliation": {
      "type": "string",
      "description": "Speaker affiliation/institution"
    },
    "formatting": {
      "type": "object",
      "properties": {
        "background_color": {
          "type": "string",
          "pattern": "^#[0-9A-Fa-f]{6}$",
          "default": "#FFFFFF"
        },
        "text_color": {
          "type": "string",
          "pattern": "^#[0-9A-Fa-f]{6}$",
          "default": "#222222"
        },
        "accent_color": {
          "type": "string",
          "pattern": "^#[0-9A-Fa-f]{6}$",
          "default": "#2DB2E8"
        },
        "highlight_color": {
          "type": "string",
          "pattern": "^#[0-9A-Fa-f]{6}$",
          "default": "#E8622D"
        },
        "font_family": {
          "type": "string",
          "enum": ["Arial", "Helvetica", "Calibri", "Avenir", "system-ui"],
          "default": "Arial"
        },
        "style": {
          "type": "string",
          "enum": ["minimal", "modern", "academic", "corporate"],
          "default": "minimal"
        }
      }
    },
    "slides": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["slide_type", "title"],
        "properties": {
          "slide_type": {
            "type": "string",
            "enum": ["title", "section", "content", "figure", "comparison", "timeline", "conclusion", "acknowledgments", "backup"]
          },
          "title": {
            "type": "string",
            "maxLength": 80
          },
          "subtitle": {
            "type": "string",
            "maxLength": 120
          },
          "key_points": {
            "type": "array",
            "maxItems": 6,
            "items": {
              "type": "string",
              "maxLength": 60
            }
          },
          "visual_description": {
            "type": "string",
            "maxLength": 300,
            "description": "Description of visual element for AI generation"
          },
          "citations": {
            "type": "array",
            "items": {
              "type": "string",
              "pattern": "^\\(.+\\d{4}\\)$"
            }
          },
          "figure_path": {
            "type": "string",
            "description": "Path to existing figure to include"
          },
          "notes": {
            "type": "string",
            "description": "Speaker notes (not displayed on slide)"
          }
        }
      }
    }
  }
}
```

#### Step 2.2: Create Schema Validator

**File:** `scripts/validate_slide_plan.py`

```python
#!/usr/bin/env python3
"""
Validate slide plan JSON against schema.
Deterministic validation before generation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class SlidePlanValidator:
    """Validate slide plans against schema with additional business rules."""

    # Slide count guidelines by duration
    SLIDE_GUIDELINES = {
        5: (5, 6, 8),
        10: (8, 11, 14),
        15: (13, 16, 20),
        20: (18, 22, 26),
        30: (22, 27, 33),
        45: (32, 40, 50),
        60: (40, 52, 65),
    }

    def __init__(self, schema_path: Optional[str] = None):
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            # Default to schema in schemas/ directory
            self.schema_path = Path(__file__).parent.parent / "schemas" / "slide_plan_schema.json"

        self.schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")

        with open(self.schema_path) as f:
            return json.load(f)

    def validate(self, plan: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate slide plan against schema and business rules.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Schema validation
        if HAS_JSONSCHEMA:
            try:
                validate(instance=plan, schema=self.schema)
            except ValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
                return False, errors, warnings

        # Business rule validation
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
        if "title" not in slide_types:
            warnings.append("No title slide found")
        if "conclusion" not in slide_types:
            warnings.append("No conclusion slide found")

        # Check citation distribution
        intro_citations = 0
        discussion_citations = 0
        for i, slide in enumerate(slides):
            citations = slide.get("citations", [])
            if i < len(slides) * 0.3:  # First 30% is intro
                intro_citations += len(citations)
            elif i > len(slides) * 0.7:  # Last 30% is discussion
                discussion_citations += len(citations)

        if intro_citations < 2:
            warnings.append(f"Few citations in introduction ({intro_citations}). Consider adding research context.")

        # Check key points per slide
        for i, slide in enumerate(slides):
            points = slide.get("key_points", [])
            if len(points) > 6:
                warnings.append(f"Slide {i+1} has {len(points)} bullet points (max recommended: 6)")

        # Validate color format
        formatting = plan.get("formatting", {})
        for color_key in ["background_color", "text_color", "accent_color"]:
            color = formatting.get(color_key, "")
            if color and not self._is_valid_hex(color):
                errors.append(f"Invalid hex color for {color_key}: {color}")

        return len(errors) == 0, errors, warnings

    def _get_slide_guidelines(self, duration: int) -> Optional[Tuple[int, int, int]]:
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
        try:
            int(color[1:], 16)
            return len(color) == 7
        except ValueError:
            return False


def main():
    """CLI for slide plan validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate slide plan JSON against schema"
    )
    parser.add_argument("plan_file", help="Path to slide plan JSON file")
    parser.add_argument("--schema", help="Path to custom schema file")
    parser.add_argument("--strict", action="store_true",
                       help="Treat warnings as errors")

    args = parser.parse_args()

    # Load plan
    with open(args.plan_file) as f:
        plan = json.load(f)

    # Validate
    validator = SlidePlanValidator(args.schema)
    is_valid, errors, warnings = validator.validate(plan)

    # Output
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

    if args.strict and warnings:
        is_valid = False

    print(f"\nResult: {'VALID' if is_valid else 'INVALID'}")
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
```

#### Step 2.3: Create Prompt Template Engine

**File:** `scripts/prompt_templates.py`

```python
#!/usr/bin/env python3
"""
Template-based prompt generation for consistent slide creation.
Reduces variance by using structured templates with variable substitution.
"""

from string import Template
from typing import Dict, Any, Optional
from pathlib import Path


# Base template for full slides
FULL_SLIDE_TEMPLATE = Template("""Create a professional presentation slide with these specifications:

SLIDE TYPE: $slide_type
TITLE: $title
$subtitle_line

CONTENT:
$content_section

VISUAL REQUIREMENTS:
$visual_description

FORMATTING:
- Background: $background_color
- Text color: $text_color
- Accent color: $accent_color
- Font: $font_family
- Style: $style

LAYOUT:
- 16:9 aspect ratio
- Clear visual hierarchy
- Minimum 5% margins on all sides
- $white_space_guidance

$citations_section

Generate a high-quality slide image following all specifications above.""")


# Template for visual-only generation
VISUAL_ONLY_TEMPLATE = Template("""Create a presentation visual/figure:

DESCRIPTION: $visual_description

REQUIREMENTS:
- Clean, professional appearance
- High resolution and sharp details
- High contrast for projection readability
- Transparent or white background preferred
- $style style
- Color palette: $accent_color (primary), $background_color (background)

Generate the visual without any slide frame or title text.""")


class PromptTemplateEngine:
    """Generate consistent prompts from structured slide plans."""

    SLIDE_TYPE_GUIDANCE = {
        "title": "Large centered title, speaker name below, minimal design",
        "section": "Section heading prominently displayed, subtle background",
        "content": "Title at top, key points below, supporting visual on right",
        "figure": "Large figure/chart as dominant element, brief caption",
        "comparison": "Side-by-side layout comparing two items",
        "timeline": "Horizontal or vertical timeline visualization",
        "conclusion": "Key takeaways prominently listed, memorable closing visual",
        "acknowledgments": "Funding logos, collaborator names, contact info",
        "backup": "Detailed supporting information for Q&A"
    }

    def __init__(self, formatting: Optional[Dict] = None):
        """
        Initialize with default or custom formatting.

        Args:
            formatting: Dict with color/font settings (uses Oligon brand defaults if None)
        """
        self.formatting = formatting or {
            "background_color": "#FFFFFF",
            "text_color": "#222222",
            "accent_color": "#2DB2E8",
            "highlight_color": "#E8622D",
            "font_family": "Arial",
            "style": "minimal"
        }

    def generate_slide_prompt(self, slide: Dict) -> str:
        """
        Generate prompt for a single slide.

        Args:
            slide: Slide definition from plan

        Returns:
            Formatted prompt string
        """
        slide_type = slide.get("slide_type", "content")

        # Build content section
        content_lines = []
        if slide.get("key_points"):
            content_lines.append("Key Points:")
            for point in slide["key_points"]:
                content_lines.append(f"- {point}")

        content_section = "\n".join(content_lines) if content_lines else "No bullet points"

        # Build subtitle line
        subtitle = slide.get("subtitle", "")
        subtitle_line = f"SUBTITLE: {subtitle}" if subtitle else ""

        # Build citations section
        citations = slide.get("citations", [])
        if citations:
            citations_section = "CITATIONS (display at bottom):\n" + "\n".join(f"- {c}" for c in citations)
        else:
            citations_section = ""

        # Get visual description or default
        visual_description = slide.get("visual_description",
            self.SLIDE_TYPE_GUIDANCE.get(slide_type, "Professional supporting visual"))

        # White space guidance based on content density
        point_count = len(slide.get("key_points", []))
        if point_count <= 2:
            white_space_guidance = "High white space (50%+) - minimal content"
        elif point_count <= 4:
            white_space_guidance = "Moderate white space (40-50%)"
        else:
            white_space_guidance = "Balanced layout with adequate breathing room"

        return FULL_SLIDE_TEMPLATE.substitute(
            slide_type=slide_type.upper(),
            title=slide.get("title", "Untitled"),
            subtitle_line=subtitle_line,
            content_section=content_section,
            visual_description=visual_description,
            background_color=self.formatting["background_color"],
            text_color=self.formatting["text_color"],
            accent_color=self.formatting["accent_color"],
            font_family=self.formatting["font_family"],
            style=self.formatting["style"],
            white_space_guidance=white_space_guidance,
            citations_section=citations_section
        )

    def generate_visual_prompt(self, description: str) -> str:
        """Generate prompt for visual-only generation."""
        return VISUAL_ONLY_TEMPLATE.substitute(
            visual_description=description,
            style=self.formatting["style"],
            accent_color=self.formatting["accent_color"],
            background_color=self.formatting["background_color"]
        )

    def generate_batch_prompts(self, plan: Dict) -> list:
        """
        Generate prompts for all slides in a plan.

        Args:
            plan: Complete slide plan dictionary

        Returns:
            List of (slide_index, prompt) tuples
        """
        # Update formatting from plan if provided
        if plan.get("formatting"):
            self.formatting.update(plan["formatting"])

        prompts = []
        for i, slide in enumerate(plan.get("slides", [])):
            prompt = self.generate_slide_prompt(slide)
            prompts.append((i + 1, prompt))

        return prompts
```

---

### Phase 3: Hybrid Quality Scoring (Week 3-4)

**Goal:** Combine deterministic measurements with AI judgment for balanced scoring.

#### Step 3.1: Implement Hybrid Scorer

**File:** `scripts/hybrid_quality_scorer.py`

```python
#!/usr/bin/env python3
"""
Hybrid quality scoring combining deterministic and AI-based evaluation.

Scoring Breakdown:
- 40% Deterministic (measurable criteria)
- 60% AI Review (subjective criteria)
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from validate_slide_image import SlideImageValidator, ValidationResult


@dataclass
class HybridScore:
    """Combined quality score with breakdown."""
    total_score: float  # 0-10 final score
    deterministic_score: float  # 0-10 from measurable criteria
    ai_score: float  # 0-10 from AI review
    deterministic_weight: float
    ai_weight: float
    passed_threshold: bool
    details: Dict


class HybridQualityScorer:
    """
    Combines deterministic image analysis with AI quality review.

    Weighting rationale:
    - Deterministic (40%): Objective, reproducible measurements
      - Dimensions/aspect ratio: 10%
      - Contrast/readability: 15%
      - White space/composition: 15%
    - AI Review (60%): Subjective quality assessment
      - Visual appeal: 20%
      - Content relevance: 20%
      - Professional polish: 20%
    """

    DEFAULT_THRESHOLD = 6.5

    def __init__(self,
                 deterministic_weight: float = 0.4,
                 ai_weight: float = 0.6,
                 threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize hybrid scorer.

        Args:
            deterministic_weight: Weight for deterministic score (0-1)
            ai_weight: Weight for AI score (0-1)
            threshold: Minimum score to pass (0-10)
        """
        if abs((deterministic_weight + ai_weight) - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")

        self.deterministic_weight = deterministic_weight
        self.ai_weight = ai_weight
        self.threshold = threshold
        self.validator = SlideImageValidator()

    def score(self,
              image_path: str,
              ai_score: float,
              ai_feedback: str = "",
              expected_colors: Optional[list] = None) -> HybridScore:
        """
        Calculate hybrid quality score.

        Args:
            image_path: Path to generated slide image
            ai_score: Score from AI review (0-10)
            ai_feedback: Text feedback from AI review
            expected_colors: Optional brand colors for compliance check

        Returns:
            HybridScore with combined assessment
        """
        # Get deterministic score
        validation = self.validator.validate(image_path, expected_colors)
        deterministic_score = validation.score

        # Calculate weighted total
        total_score = (
            (deterministic_score * self.deterministic_weight) +
            (ai_score * self.ai_weight)
        )

        # Determine if passed
        passed = total_score >= self.threshold

        # Compile details
        details = {
            "deterministic_breakdown": {
                "score": deterministic_score,
                "checks": validation.checks,
                "measurements": validation.details,
                "warnings": validation.warnings,
                "errors": validation.errors
            },
            "ai_breakdown": {
                "score": ai_score,
                "feedback": ai_feedback
            },
            "threshold": self.threshold,
            "weights": {
                "deterministic": self.deterministic_weight,
                "ai": self.ai_weight
            }
        }

        return HybridScore(
            total_score=round(total_score, 2),
            deterministic_score=deterministic_score,
            ai_score=ai_score,
            deterministic_weight=self.deterministic_weight,
            ai_weight=self.ai_weight,
            passed_threshold=passed,
            details=details
        )

    def should_regenerate(self, hybrid_score: HybridScore) -> Tuple[bool, str]:
        """
        Determine if image should be regenerated based on hybrid score.

        Returns:
            Tuple of (should_regenerate, reason)
        """
        # Hard failures (deterministic)
        if hybrid_score.details["deterministic_breakdown"]["errors"]:
            errors = hybrid_score.details["deterministic_breakdown"]["errors"]
            return True, f"Deterministic validation failed: {errors[0]}"

        # Soft failures (threshold)
        if not hybrid_score.passed_threshold:
            if hybrid_score.deterministic_score < 5.0:
                return True, f"Low deterministic score ({hybrid_score.deterministic_score}/10)"
            elif hybrid_score.ai_score < 5.0:
                return True, f"Low AI score ({hybrid_score.ai_score}/10)"
            else:
                return True, f"Below threshold ({hybrid_score.total_score} < {self.threshold})"

        return False, "Quality acceptable"
```

#### Step 3.2: Update Generation Pipeline with Hybrid Scoring

**Modify:** `scripts/generate_slide_image_ai.py`

```python
# Add import at top
from hybrid_quality_scorer import HybridQualityScorer, HybridScore

# In SlideImageGenerator.__init__, add:
self.hybrid_scorer = HybridQualityScorer(
    deterministic_weight=0.4,
    ai_weight=0.6,
    threshold=self.QUALITY_THRESHOLD
)

# Replace the review section in generate_slide() with:

# Deterministic pre-check (fast fail)
from validate_slide_image import SlideImageValidator
pre_validator = SlideImageValidator()
pre_result = pre_validator.validate(str(temp_path))

if pre_result.errors:
    print(f"✗ Deterministic validation failed: {pre_result.errors}")
    results["iterations"].append({
        "iteration": i,
        "success": False,
        "error": f"Validation failed: {pre_result.errors}"
    })
    # Improve prompt based on deterministic feedback
    current_prompt = self.improve_prompt(
        user_prompt,
        f"Image failed validation: {pre_result.errors}. Warnings: {pre_result.warnings}",
        i + 1,
        visual_only
    )
    continue

# AI review (only if deterministic passed)
print(f"Reviewing image with Gemini 3 Pro...")
critique, ai_score, _ = self.review_image(
    str(temp_path), user_prompt, i, visual_only, iterations
)

# Hybrid scoring
hybrid_result = self.hybrid_scorer.score(
    str(temp_path),
    ai_score=ai_score,
    ai_feedback=critique
)

print(f"✓ Hybrid Score: {hybrid_result.total_score}/10")
print(f"  - Deterministic: {hybrid_result.deterministic_score}/10 (weight: {hybrid_result.deterministic_weight})")
print(f"  - AI Review: {hybrid_result.ai_score}/10 (weight: {hybrid_result.ai_weight})")

should_regen, regen_reason = self.hybrid_scorer.should_regenerate(hybrid_result)

results["iterations"].append({
    "iteration": i,
    "hybrid_score": hybrid_result.total_score,
    "deterministic_score": hybrid_result.deterministic_score,
    "ai_score": hybrid_result.ai_score,
    "critique": critique,
    "needs_improvement": should_regen,
    "success": True
})

if not should_regen:
    print(f"\n✓ Quality meets threshold ({hybrid_result.total_score} >= {self.QUALITY_THRESHOLD})")
    final_image_data = image_data
    results["final_score"] = hybrid_result.total_score
    results["success"] = True
    results["early_stop"] = True
    break
```

---

### Phase 4: Documentation Consolidation (Week 4)

**Goal:** Reduce duplication and establish single sources of truth.

#### Step 4.1: Consolidate Reference Documents

**Action:** Merge `expert_guide.md` into `slide_design_principles.md`

The expert_guide.md content overlaps significantly with slide_design_principles.md. Merge the unique content:

1. Move "Core Principles" section to top of slide_design_principles.md
2. Move "Decision Framework" table to new section in main doc
3. Move "Failure Modes" to existing "Common Mistakes" section
4. Move "Quality Signals" to success criteria
5. Delete expert_guide.md after merge

#### Step 4.2: Extract Embedded Guidelines

**Action:** Move Python-embedded guidelines to shared file

Create `references/generation_guidelines.md`:

```markdown
# Slide Generation Guidelines

> Shared guidelines for AI-based slide generation.
> Referenced by: SKILL.md, generate_slide_image_ai.py

## Full Slide Generation

[Content from FULL_SLIDE_GUIDELINES constant]

## Visual-Only Generation

[Content from VISUAL_ONLY_GUIDELINES constant]
```

Update Python to load from file:
```python
def _load_guidelines(self):
    guidelines_path = Path(__file__).parent.parent / "references" / "generation_guidelines.md"
    # Parse and extract sections
```

#### Step 4.3: Update Cross-References

After consolidation, update all references in:
- SKILL.md
- Other reference documents
- Python scripts that reference files

---

## Testing Plan

### Unit Tests

**File:** `tests/test_validation.py`

```python
import pytest
from scripts.validate_slide_image import SlideImageValidator
from scripts.validate_slide_plan import SlidePlanValidator


class TestSlideImageValidator:

    def test_valid_image_passes(self, tmp_path):
        """Test that a valid slide image passes validation."""
        # Create test image with PIL
        from PIL import Image
        img = Image.new('RGB', (1920, 1080), color='white')
        img_path = tmp_path / "test_slide.png"
        img.save(img_path)

        validator = SlideImageValidator()
        result = validator.validate(str(img_path))

        assert result.passed
        assert result.score >= 5.0
        assert result.checks["aspect_ratio"]
        assert result.checks["min_dimensions"]

    def test_wrong_aspect_ratio_warns(self, tmp_path):
        """Test that wrong aspect ratio generates warning."""
        from PIL import Image
        img = Image.new('RGB', (1024, 1024), color='white')  # 1:1 ratio
        img_path = tmp_path / "square_slide.png"
        img.save(img_path)

        validator = SlideImageValidator()
        result = validator.validate(str(img_path))

        assert not result.checks["aspect_ratio"]
        assert any("aspect" in w.lower() for w in result.warnings)

    def test_low_contrast_detected(self, tmp_path):
        """Test that low contrast is detected."""
        from PIL import Image
        # Create very low contrast image
        img = Image.new('RGB', (1920, 1080), color=(200, 200, 200))
        img_path = tmp_path / "low_contrast.png"
        img.save(img_path)

        validator = SlideImageValidator()
        result = validator.validate(str(img_path))

        assert result.details["contrast_score"] < 0.5


class TestSlidePlanValidator:

    def test_valid_plan_passes(self):
        """Test that a valid slide plan passes validation."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test Presentation",
            "slides": [
                {"slide_type": "title", "title": "My Talk"},
                {"slide_type": "content", "title": "Introduction"},
                {"slide_type": "conclusion", "title": "Summary"}
            ]
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert is_valid
        assert len(errors) == 0

    def test_missing_title_slide_warns(self):
        """Test that missing title slide generates warning."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 15,
            "title": "Test",
            "slides": [
                {"slide_type": "content", "title": "Intro"},
                {"slide_type": "conclusion", "title": "End"}
            ]
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("title slide" in w.lower() for w in warnings)

    def test_too_many_slides_warns(self):
        """Test that excessive slide count generates warning."""
        plan = {
            "talk_type": "conference",
            "duration_minutes": 10,
            "title": "Test",
            "slides": [{"slide_type": "content", "title": f"Slide {i}"}
                      for i in range(25)]  # Way over for 10 min
        }

        validator = SlidePlanValidator()
        is_valid, errors, warnings = validator.validate(plan)

        assert any("exceeds" in w.lower() for w in warnings)
```

### Integration Tests

```python
class TestHybridScoring:

    def test_hybrid_score_calculation(self, tmp_path):
        """Test that hybrid scoring correctly weights components."""
        from PIL import Image
        from scripts.hybrid_quality_scorer import HybridQualityScorer

        # Create valid test image
        img = Image.new('RGB', (1920, 1080), color='white')
        img_path = tmp_path / "test.png"
        img.save(img_path)

        scorer = HybridQualityScorer(
            deterministic_weight=0.4,
            ai_weight=0.6,
            threshold=6.5
        )

        result = scorer.score(str(img_path), ai_score=8.0)

        # Deterministic should be ~7-8 for valid image
        # Total = 0.4 * det + 0.6 * 8.0
        assert 6.0 <= result.total_score <= 9.0
        assert result.ai_score == 8.0
```

---

## Success Metrics

### Quantitative Targets

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Output variance (same prompt) | High | Medium | Compare 5 generations of same prompt |
| Validation coverage | 40% | 80% | % of quality criteria with deterministic checks |
| False rejection rate | Unknown | <10% | Good images incorrectly rejected |
| False acceptance rate | Unknown | <15% | Bad images incorrectly accepted |
| Generation efficiency | ~2 iterations avg | ~1.5 iterations avg | Average iterations to acceptance |

### Qualitative Targets

- [ ] All measurable criteria have deterministic validation
- [ ] Input schema prevents obviously invalid configurations
- [ ] Documentation has single source of truth for each concept
- [ ] Hybrid scoring provides consistent, explainable results

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Deterministic Validation | Week 1-2 | `validate_slide_image.py`, integration with pipeline |
| Phase 2: Structured Input | Week 2-3 | JSON schema, `validate_slide_plan.py`, prompt templates |
| Phase 3: Hybrid Scoring | Week 3-4 | `hybrid_quality_scorer.py`, updated pipeline |
| Phase 4: Documentation | Week 4 | Consolidated references, updated cross-refs |
| Testing & Validation | Week 5 | Unit tests, integration tests, threshold calibration |

---

## Appendix: File Change Summary

### New Files to Create

1. `scripts/validate_slide_image.py` - Deterministic image validation
2. `scripts/validate_slide_plan.py` - Slide plan schema validation
3. `scripts/prompt_templates.py` - Template-based prompt generation
4. `scripts/hybrid_quality_scorer.py` - Combined scoring system
5. `schemas/slide_plan_schema.json` - JSON Schema for plans
6. `references/generation_guidelines.md` - Shared guidelines
7. `tests/test_validation.py` - Unit tests

### Files to Modify

1. `scripts/generate_slide_image_ai.py` - Integrate hybrid scoring
2. `references/slide_design_principles.md` - Merge expert_guide content
3. `SKILL.md` - Update references, add schema documentation

### Files to Delete (after merge)

1. `references/expert_guide.md` - Content merged into slide_design_principles.md
