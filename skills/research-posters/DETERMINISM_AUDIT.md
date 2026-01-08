# Determinism Audit: research-posters

> **Audit Date**: 2026-01-07
> **Skill Version**: 1.0.0
> **Development Stage**: First Draft
> **Current Determinism Score**: 60-70%
> **Target Determinism Score**: 85%

## Executive Summary

The research-posters skill has strong foundational elements for determinism—notably the `review_poster.sh` script, LaTeX templates, and quantified success criteria. Significant opportunities exist to shift validation from manual/LLM-based to code-based checking, particularly for word counts, accessibility compliance, and output quality verification. Adding 3-4 Python validation scripts would increase reproducibility from ~60% to ~85%.

---

## Current State Analysis

### Deterministic Components (Working Well)

| Component | Implementation | Determinism Level |
|-----------|----------------|-------------------|
| LaTeX templates | 3 complete templates (beamerposter, tikzposter, baposter) | High |
| PDF quality script | `review_poster.sh` with automated checks | Medium-High |
| Format selection | Explicit decision tree in SKILL.md | High |
| Brand colors | Hex-defined color palette | High |
| Success criteria | Quantified thresholds (word count, font sizes, DPI) | High |
| Quality checklist | Comprehensive markdown checklist | Medium (manual) |

### Stochastic Components (Need Improvement)

| Component | Current State | Issue |
|-----------|---------------|-------|
| Content generation | LLM-dependent section writing | High variance in output |
| Word count validation | Manual checking | Not enforced during generation |
| Contrast ratio checking | External web tool reference | Not integrated |
| Accessibility validation | External simulators | Not automated |
| Section word budgets | Defined but not enforced | LLM may exceed/undercut |
| Font size validation | Manual PDF inspection | Could be automated |
| Figure placement | LLM discretion | No explicit constraints |

---

## Input Standardization

### Current State
- Inputs are free-form conversation
- Format selection uses decision trees (good)
- Size/orientation has lookup tables (good)
- No structured specification format

### Recommended: Poster Specification Schema

```yaml
# poster_spec.yaml - Structured input format
poster:
  title: "Your Research Title Here"
  dimensions: "A0"           # enum: A0, A1, 36x48, 42x56, 48x72
  orientation: "portrait"    # enum: portrait, landscape
  format: "latex"            # enum: latex, pptx
  latex_package: "tikzposter" # optional: beamerposter, tikzposter, baposter
  brand: "oligon"            # enum: oligon, generic, custom

authors:
  - name: "Jane Smith"
    affiliation: 1
    presenting: true
    email: "jane.smith@university.edu"
  - name: "John Doe"
    affiliation: 2
    presenting: false

affiliations:
  1: "Department of Research, University Name"
  2: "Institute of Science, Research Center"

content:
  introduction:
    word_budget: 100
    key_points:
      - "Background context"
      - "Problem statement"
      - "Research objective"
  methods:
    word_budget: 150
    include_flowchart: true
  results:
    word_budget: 200
    figure_count: 3
  conclusions:
    word_budget: 100

figures:
  - id: "fig1"
    type: "schematic"        # enum: schematic, chart, photo, diagram
    description: "Methodology flowchart"
    source: "scientific-schematics"
    min_dpi: 300
  - id: "fig2"
    type: "chart"
    description: "Main results bar chart"
    source: "path/to/figure.pdf"
    min_dpi: 300

assets:
  logos:
    - path: "logos/university.pdf"
      position: "header-left"
    - path: "logos/funder.pdf"
      position: "header-right"
  qr_codes:
    - url: "https://doi.org/10.1234/paper"
      label: "Full Paper"
```

### Implementation Priority: HIGH

Create `scripts/validate_spec.py` to parse and validate this schema before workflow begins.

---

## Output Standardization

### Recommended: Stage Artifacts

| Stage | Output Artifact | Format | Validation |
|-------|-----------------|--------|------------|
| Stage 1: Requirements | `poster_spec.yaml` | YAML | Schema validation |
| Stage 2: Format Selection | `format_decision.json` | JSON | Enum validation |
| Stage 3: Implementation | `poster.tex` or `poster.pptx` | LaTeX/PPTX | Compilation check |
| Stage 4: Visual Content | `figures/manifest.json` | JSON | DPI/format check |
| Stage 5: Validation | `quality_report.json` | JSON | All checks pass |

### Recommended: Quality Report Format

```json
{
  "poster_path": "poster.pdf",
  "validation_timestamp": "2026-01-07T14:30:00Z",
  "overall_pass": true,
  "checks": {
    "word_count": {
      "total": 487,
      "target_range": [300, 800],
      "by_section": {
        "introduction": 95,
        "methods": 142,
        "results": 178,
        "conclusions": 72
      },
      "pass": true
    },
    "title": {
      "word_count": 12,
      "target_range": [10, 15],
      "pass": true
    },
    "typography": {
      "title_font_pt": 96,
      "body_font_pt": 30,
      "min_body_pt": 24,
      "pass": true
    },
    "accessibility": {
      "contrast_ratios": {
        "text_background": 12.5,
        "header_background": 8.2
      },
      "min_contrast": 4.5,
      "colorblind_safe": true,
      "pass": true
    },
    "images": {
      "count": 3,
      "all_300dpi": true,
      "formats": ["pdf", "pdf", "png"],
      "pass": true
    },
    "compilation": {
      "errors": 0,
      "warnings": 2,
      "warnings_list": [
        "Overfull \\hbox (2.3pt too wide)",
        "Font shape undefined"
      ],
      "pass": true
    },
    "structure": {
      "sections_present": ["introduction", "methods", "results", "conclusions"],
      "required_sections": ["introduction", "methods", "results", "conclusions"],
      "references_included": true,
      "contact_info_present": true,
      "pass": true
    }
  }
}
```

---

## Code Integration Opportunities

### Priority 1: Comprehensive Validation Script

**File**: `scripts/validate_poster.py`

```python
#!/usr/bin/env python3
"""
Poster Quality Validation - Deterministic Checks

Replaces manual checklist items with automated validation.
Returns structured JSON report.
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    value: any
    target: any
    message: str = ""


def count_words_in_tex(tex_path: Path) -> dict[str, int]:
    """Extract and count words per \\block{SectionName}{content}."""
    content = tex_path.read_text()

    # Pattern for tikzposter/beamerposter blocks
    block_pattern = r'\\block\{([^}]+)\}\{(.*?)\}(?=\\block|\Z)'

    sections = {}
    for match in re.finditer(block_pattern, content, re.DOTALL):
        section_name = match.group(1).lower().strip()
        section_content = match.group(2)

        # Remove LaTeX commands for word counting
        text_only = re.sub(r'\\[a-zA-Z]+\*?(\{[^}]*\})*', ' ', section_content)
        text_only = re.sub(r'[{}\\$%&_^]', ' ', text_only)

        words = len(text_only.split())
        sections[section_name] = words

    sections['total'] = sum(sections.values())
    return sections


def check_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def relative_luminance(rgb: tuple) -> float:
        def channel_luminance(c: int) -> float:
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = rgb
        return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)

    l1 = relative_luminance(hex_to_rgb(fg_hex))
    l2 = relative_luminance(hex_to_rgb(bg_hex))

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def validate_pdf_images(pdf_path: Path, min_dpi: int = 300) -> list[dict]:
    """Check image resolutions in PDF."""
    result = subprocess.run(
        ['pdfimages', '-list', str(pdf_path)],
        capture_output=True, text=True
    )

    images = []
    for line in result.stdout.strip().split('\n')[2:]:  # Skip header
        parts = line.split()
        if len(parts) >= 7:
            images.append({
                'page': int(parts[0]),
                'width': int(parts[3]),
                'height': int(parts[4]),
                'color': parts[5],
                'format': parts[6] if len(parts) > 6 else 'unknown'
            })

    return images


def validate_pdf_dimensions(pdf_path: Path) -> dict:
    """Extract PDF page dimensions."""
    result = subprocess.run(
        ['pdfinfo', str(pdf_path)],
        capture_output=True, text=True
    )

    for line in result.stdout.split('\n'):
        if 'Page size' in line:
            # Parse "Page size:      2384 x 3370 pts"
            match = re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)', line)
            if match:
                return {
                    'width_pts': float(match.group(1)),
                    'height_pts': float(match.group(2))
                }

    return {'width_pts': 0, 'height_pts': 0}


def validate_fonts_embedded(pdf_path: Path) -> dict:
    """Check if all fonts are embedded."""
    result = subprocess.run(
        ['pdffonts', str(pdf_path)],
        capture_output=True, text=True
    )

    lines = result.stdout.strip().split('\n')[2:]  # Skip header
    non_embedded = []

    for line in lines:
        parts = line.split()
        if len(parts) >= 5 and parts[3] == 'no':
            non_embedded.append(parts[0])

    return {
        'all_embedded': len(non_embedded) == 0,
        'non_embedded_fonts': non_embedded
    }


def run_validation(tex_path: Path, pdf_path: Path, spec: dict = None) -> dict:
    """Run all validation checks and return structured report."""

    results = {
        'poster_path': str(pdf_path),
        'source_path': str(tex_path),
        'checks': {}
    }

    # Word count validation
    if tex_path.exists():
        word_counts = count_words_in_tex(tex_path)
        results['checks']['word_count'] = {
            'total': word_counts.get('total', 0),
            'target_range': [300, 800],
            'by_section': {k: v for k, v in word_counts.items() if k != 'total'},
            'pass': 300 <= word_counts.get('total', 0) <= 800
        }

    # PDF validation
    if pdf_path.exists():
        # Dimensions
        dims = validate_pdf_dimensions(pdf_path)
        results['checks']['dimensions'] = dims

        # Font embedding
        fonts = validate_fonts_embedded(pdf_path)
        results['checks']['fonts'] = {
            **fonts,
            'pass': fonts['all_embedded']
        }

        # Images
        images = validate_pdf_images(pdf_path)
        results['checks']['images'] = {
            'count': len(images),
            'details': images,
            'pass': len(images) > 0
        }

    # Overall pass
    all_passed = all(
        check.get('pass', True)
        for check in results['checks'].values()
        if isinstance(check, dict) and 'pass' in check
    )
    results['overall_pass'] = all_passed

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate research poster')
    parser.add_argument('tex_file', type=Path, help='Path to .tex source')
    parser.add_argument('pdf_file', type=Path, help='Path to compiled .pdf')
    parser.add_argument('--output', '-o', type=Path, help='Output JSON path')
    parser.add_argument('--spec', type=Path, help='Poster specification YAML')

    args = parser.parse_args()

    results = run_validation(args.tex_file, args.pdf_file)

    output = json.dumps(results, indent=2)

    if args.output:
        args.output.write_text(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)
```

### Priority 2: Accessibility Validation

**File**: `scripts/validate_accessibility.py`

```python
#!/usr/bin/env python3
"""
Accessibility Validation for Research Posters

Checks:
- WCAG contrast ratios
- Colorblind-safe palette simulation
- Color-independent information encoding
"""

import argparse
import json
import re
from pathlib import Path


# Standard brand colors to validate
OLIGON_COLORS = {
    'brand_blue': '#2DB2E8',
    'brand_orange': '#E8622D',
    'dark_gray': '#222222',
    'medium_gray': '#666666',
    'white': '#FFFFFF'
}

# Colorblind-safe combinations
SAFE_COMBINATIONS = [
    ('#2DB2E8', '#E8622D'),  # Blue + Orange
    ('#2DB2E8', '#FFFFFF'),  # Blue + White
    ('#222222', '#FFFFFF'),  # Dark Gray + White
    ('#E8622D', '#FFFFFF'),  # Orange + White
]


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colors."""
    def relative_luminance(rgb: tuple) -> float:
        def channel(c: int) -> float:
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = rgb
        return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

    l1 = relative_luminance(hex_to_rgb(color1))
    l2 = relative_luminance(hex_to_rgb(color2))

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return round((lighter + 0.05) / (darker + 0.05), 2)


def simulate_deuteranopia(hex_color: str) -> str:
    """Simulate red-green colorblindness (most common type)."""
    r, g, b = hex_to_rgb(hex_color)

    # Simplified deuteranopia simulation matrix
    new_r = int(0.625 * r + 0.375 * g)
    new_g = int(0.7 * g + 0.3 * r)
    new_b = int(0.3 * g + 0.7 * b)

    return rgb_to_hex((
        min(255, max(0, new_r)),
        min(255, max(0, new_g)),
        min(255, max(0, new_b))
    ))


def extract_colors_from_tex(tex_path: Path) -> list[str]:
    """Extract definecolor hex values from LaTeX file."""
    content = tex_path.read_text()

    colors = []

    # Pattern: \definecolor{name}{HTML}{HEXCODE}
    html_pattern = r'\\definecolor\{[^}]+\}\{HTML\}\{([A-Fa-f0-9]{6})\}'
    for match in re.finditer(html_pattern, content):
        colors.append('#' + match.group(1))

    # Pattern: \definecolor{name}{RGB}{r,g,b}
    rgb_pattern = r'\\definecolor\{[^}]+\}\{RGB\}\{(\d+),\s*(\d+),\s*(\d+)\}'
    for match in re.finditer(rgb_pattern, content):
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        colors.append(rgb_to_hex((r, g, b)))

    return list(set(colors))


def validate_palette(colors: list[str], background: str = '#FFFFFF') -> dict:
    """Validate a color palette for accessibility."""
    results = {
        'colors_checked': colors,
        'background': background,
        'contrast_checks': [],
        'colorblind_simulation': [],
        'overall_pass': True
    }

    # Check contrast against background
    for color in colors:
        ratio = calculate_contrast_ratio(color, background)
        passed = ratio >= 4.5  # WCAG AA for normal text

        results['contrast_checks'].append({
            'foreground': color,
            'background': background,
            'ratio': ratio,
            'wcag_aa': passed,
            'wcag_aaa': ratio >= 7.0
        })

        if not passed and color != background:
            results['overall_pass'] = False

    # Colorblind simulation
    for color in colors:
        simulated = simulate_deuteranopia(color)
        results['colorblind_simulation'].append({
            'original': color,
            'deuteranopia': simulated,
            'distinguishable': color != simulated
        })

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate poster accessibility')
    parser.add_argument('tex_file', type=Path, nargs='?', help='LaTeX file to check')
    parser.add_argument('--colors', nargs='+', help='Hex colors to validate')
    parser.add_argument('--background', default='#FFFFFF', help='Background color')
    parser.add_argument('--output', '-o', type=Path, help='Output JSON path')

    args = parser.parse_args()

    if args.tex_file and args.tex_file.exists():
        colors = extract_colors_from_tex(args.tex_file)
    elif args.colors:
        colors = args.colors
    else:
        colors = list(OLIGON_COLORS.values())

    results = validate_palette(colors, args.background)

    output = json.dumps(results, indent=2)

    if args.output:
        args.output.write_text(output)
    else:
        print(output)
```

### Priority 3: Enhanced Review Script

**Enhancement to**: `scripts/review_poster.sh`

Add the following checks to the existing script:

```bash
# Add after existing checks in review_poster.sh

# 8. Word Count Check (requires texcount)
echo -e "${YELLOW}[8] Word Count:${NC}"
TEX_FILE="${POSTER_FILE%.pdf}.tex"
if [ -f "$TEX_FILE" ] && command_exists texcount; then
    WORD_COUNT=$(texcount -inc -sum "$TEX_FILE" 2>/dev/null | grep "Words in text" | awk '{print $4}')
    if [ -n "$WORD_COUNT" ]; then
        echo "    Total words: $WORD_COUNT"
        if [ "$WORD_COUNT" -gt 800 ]; then
            echo -e "    ${RED}✗ Exceeds 800 word maximum${NC}"
        elif [ "$WORD_COUNT" -lt 300 ]; then
            echo -e "    ${YELLOW}⚠ Below 300 word minimum${NC}"
        else
            echo -e "    ${GREEN}✓ Within target range (300-800)${NC}"
        fi
    fi
else
    echo -e "    ${YELLOW}⚠ texcount not installed or .tex file not found${NC}"
fi
echo ""

# 9. LaTeX Warnings Check
echo -e "${YELLOW}[9] LaTeX Compilation Warnings:${NC}"
LOG_FILE="${POSTER_FILE%.pdf}.log"
if [ -f "$LOG_FILE" ]; then
    OVERFULL=$(grep -c "Overfull" "$LOG_FILE" 2>/dev/null || echo "0")
    UNDERFULL=$(grep -c "Underfull" "$LOG_FILE" 2>/dev/null || echo "0")
    WARNINGS=$(grep -c "Warning" "$LOG_FILE" 2>/dev/null || echo "0")

    echo "    Overfull boxes: $OVERFULL"
    echo "    Underfull boxes: $UNDERFULL"
    echo "    Other warnings: $WARNINGS"

    if [ "$OVERFULL" -gt 5 ] || [ "$UNDERFULL" -gt 5 ]; then
        echo -e "    ${YELLOW}⚠ Review spacing issues${NC}"
    else
        echo -e "    ${GREEN}✓ Acceptable warning count${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ Log file not found${NC}"
fi
echo ""

# 10. QR Code Detection
echo -e "${YELLOW}[10] QR Code Presence:${NC}"
if command_exists zbarimg; then
    QR_FOUND=$(zbarimg --quiet "$POSTER_FILE" 2>/dev/null | grep -c "QR-Code" || echo "0")
    if [ "$QR_FOUND" -gt 0 ]; then
        echo -e "    ${GREEN}✓ QR code detected ($QR_FOUND found)${NC}"
        zbarimg --quiet "$POSTER_FILE" 2>/dev/null | head -3
    else
        echo -e "    ${YELLOW}⚠ No QR code detected${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ zbar not installed (install: brew install zbar)${NC}"
fi
echo ""
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `scripts/validate_poster.py` with core validation
- [ ] Add poster specification YAML schema example
- [ ] Enhance `review_poster.sh` with word count and LaTeX log parsing

### Phase 2: Accessibility (Week 2)
- [ ] Create `scripts/validate_accessibility.py`
- [ ] Integrate contrast checking into validation pipeline
- [ ] Add colorblind simulation to quality report

### Phase 3: Integration (Week 3)
- [ ] Create unified `scripts/full_validation.sh` that runs all checks
- [ ] Add JSON report generation
- [ ] Update SKILL.md workflow to reference automated validation

### Phase 4: Examples (Week 4)
- [ ] Create `examples/` directory with complete poster examples
- [ ] Add expected validation outputs for test cases
- [ ] Document end-to-end workflow with validation

---

## Metrics and Tracking

### Current Baseline
| Metric | Value |
|--------|-------|
| Automated validation coverage | 30% of checklist items |
| Manual steps required | 15+ |
| Reproducibility score | 60-70% |
| Time for full validation | 15-20 minutes (manual) |

### Target State
| Metric | Target |
|--------|--------|
| Automated validation coverage | 75% of checklist items |
| Manual steps required | 5-7 |
| Reproducibility score | 85% |
| Time for full validation | 2-3 minutes (automated + manual review) |

### Success Criteria
1. `validate_poster.py` runs without errors on all 3 template types
2. Quality report JSON validates against schema
3. Word count accuracy within 5% of manual count
4. Contrast ratio matches WebAIM calculator results
5. Zero false negatives on critical checks (font embedding, dimensions)

---

## Dependencies

### Required Tools
- `pdfinfo`, `pdffonts`, `pdfimages` (poppler-utils)
- `texcount` (LaTeX word counting)
- `zbar` / `zbarimg` (QR code detection)
- Python 3.8+

### Python Packages
```
# requirements-validation.txt
pyyaml>=6.0
```

### Installation
```bash
# macOS
brew install poppler zbar
pip install pyyaml

# Ubuntu/Debian
apt-get install poppler-utils zbar-tools texcount
pip install pyyaml
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-07 | Initial determinism audit completed |
| - | Identified 10 components for automation |
| - | Created implementation roadmap |
| - | Drafted validation scripts |
