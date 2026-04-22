# Brand Skill Interface Contract

> Specification for creating alternative brand skills compatible with the skill library
> Version: 1.1.0
> Created: 2025-12-30
> Updated: 2026-01-08

## Purpose

This document defines the interface that brand skills must implement to integrate with the skill library. Following this contract ensures that:

1. Skills like `plotting-libraries` can load any brand without code changes
2. SKILL_ROUTER.md can route to the correct brand skill
3. Future brands integrate seamlessly

The executable tooling that enforces this contract — JSON Schema, Python type stubs, validators, and 173 tests — lives in [`brand-interface/`](brand-interface/README.md). That directory is support tooling, not a callable skill.

## Validation Tools

This interface includes automated validation tools to ensure compliance:

```bash
# Validate a brand skill
python skills/brand-interface/validation/validate_brand.py skills/your-brand

# Check color accessibility
python skills/brand-interface/validation/check_accessibility.py skills/your-brand/tokens/brand-tokens.json

# JSON Schema validation (requires jsonschema package)
python -c "import json, jsonschema; \
  schema = json.load(open('skills/brand-interface/schemas/brand-tokens.schema.json')); \
  tokens = json.load(open('skills/your-brand/tokens/brand-tokens.json')); \
  jsonschema.validate(tokens, schema); print('Valid!')"
```

**Validation Artifacts:**
- `brand-interface/schemas/brand-tokens.schema.json` - JSON Schema for tokens validation
- `brand-interface/validation/validate_brand.py` - Complete brand validation script
- `brand-interface/validation/check_accessibility.py` - WCAG contrast checker
- `brand-interface/validation/controlled_vocabularies.py` - Standardized enums
- `brand-interface/type_stubs/adapter_interface.pyi` - Python type definitions

## Required Structure

A brand skill must have this directory structure:

```
skills/<brand-name>/
├── SKILL.md                    # Skill definition (required)
├── tokens/
│   └── brand-tokens.json       # Machine-readable tokens (required)
├── adapters/                   # Format adapters (at least one required)
│   ├── matplotlib_adapter.py   # Python/matplotlib
│   ├── ggplot2_adapter.R       # R/ggplot2
│   └── ...
├── references/
│   └── brand-spec.md           # Human-readable specification
└── assets/                     # Logo files, style files
    └── ...
```

---

## Required: brand-tokens.json Schema

The tokens file must include at minimum:

```json
{
  "meta": {
    "name": "Brand Name",
    "version": "X.Y.Z"
  },
  "colors": {
    "primary": {
      "<primary_color_name>": {"hex": "#XXXXXX", "role": "description"}
    },
    "neutrals": {
      "<neutral_1>": {"hex": "#XXXXXX", "role": "description"},
      "<neutral_2>": {"hex": "#XXXXXX", "role": "description"}
    },
    "structure": {
      "white": {"hex": "#FFFFFF"},
      "black": {"hex": "#000000"}
    }
  },
  "color_cycles": {
    "default": {
      "colors": ["#XXXXXX", "#XXXXXX", "#XXXXXX"]
    }
  }
}
```

### Optional Extensions

Additional fields that may be included:

```json
{
  "typography": {
    "primary_font": "Font Name",
    "fallback_fonts": ["Sans-serif"],
    "heading_size": {"min": 12, "max": 24},
    "body_size": {"min": 7, "max": 10}
  },
  "spacing": {
    "figure_margin": 0.5,
    "line_spacing": 1.2
  }
}
```

---

## Required: Matplotlib Adapter API

If providing a Python/matplotlib adapter, it must export:

```python
# Constants
BRAND_COLORS: dict[str, str]  # Color name → hex mapping

# Functions
def set_brand_style(cycle: str = 'default') -> None:
    """Apply brand rcParams to matplotlib."""
    ...

def get_cycle(name: str) -> list[str]:
    """Return color cycle by name."""
    ...

def get_color(name: str) -> str:
    """Return single color by name."""
    ...
```

### Optional API Extensions

```python
def get_divergent_cmap(name: str = 'default') -> matplotlib.colors.Colormap:
    """Return divergent colormap for heatmaps."""
    ...

def add_panel_label(ax, label: str, **kwargs) -> None:
    """Add panel label (A, B, C...) to axis."""
    ...
```

---

## Required: ggplot2 Adapter API (if R support provided)

```r
# Theme function
theme_<brand>() -> ggplot2::theme
    # Returns theme object with brand styling

# Color scale functions
scale_color_<brand>(cycle = 'default') -> ggplot2::scale_color_manual
scale_fill_<brand>(cycle = 'default') -> ggplot2::scale_fill_manual
    # Returns scale with brand colors

# Constants
BRAND_COLORS <- c(
  primary = "#XXXXXX",
  ...
)
```

---

## Required: SKILL.md Frontmatter

```yaml
---
name: <brand-name>
version: X.Y.Z
description: "..."
brand-type: organizational  # or 'personal', 'institutional'
tokens-file: tokens/brand-tokens.json
allowed-tools: [Read, Glob]
---
```

### Required XML Sections

Brand skills should include these sections:

| Section | Purpose |
|---------|---------|
| `<overview>` | Brief description of brand purpose |
| `<when_to_use>` | Trigger conditions for using this brand |
| `<decision_framework>` | Color cycle selection guidance |
| `<workflow>` | Steps to load and apply brand |
| `<success_criteria>` | Visual compliance checklist |
| `<adapters>` | List of available format adapters |
| `<cross_references>` | Links to plotting-libraries, skills/shared/accessibility/ |
| `<references>` | Links to full specifications |

---

## SKILL_ROUTER.md Integration

New brand skills must be added to the "Brand Application" decision tree:

```
├─ Which brand?
│  │
│  ├─ Oligon brand?
│  │  └─ YES → oligon-brand
│  │
│  ├─ [Your brand]?
│  │  └─ YES → [your-brand-skill]
│  │
│  └─ Other/None?
│     └─ Use oligon-brand `<design_foundation>` generic-fallback section
│        (viridis/Okabe-Ito/ColorBrewer; no brand tokens applied)
```

And to the "Brand Application: Quick Selection" table:

| Output | Brand Skill | Implementation Skill |
|--------|-------------|---------------------|
| Publication figure (Python) | [your-brand] | plotting-libraries |
| ... | ... | ... |

---

## Controlled Vocabularies

To ensure deterministic behavior, use standardized values from `controlled_vocabularies.py`:

### Brand Types (frontmatter `brand-type`)
| Value | Description |
|-------|-------------|
| `organizational` | Company/organization brand |
| `personal` | Individual researcher's style |
| `institutional` | University/institute brand |
| `journal` | Journal-specific styling |
| `generic` | General-purpose/no affiliation |

### Color Roles (for `role` field in tokens)
| Role | Description |
|------|-------------|
| `primary-highlight` | Main emphasis color |
| `data-primary` | Primary data series |
| `data-secondary` | Secondary data series |
| `data-control` | Control/baseline data |
| `data-treatment` | Treatment/experimental data |
| `direction-up` | Upregulated, positive |
| `direction-down` | Downregulated, negative |
| `background` | Figure background |
| `text` | Labels, titles, legends |
| `axes` | Axis lines, ticks |
| `annotations` | Annotation text/lines |

### Cycle Names
| Name | Use Case |
|------|----------|
| `default` | Default cycle (required) |
| `treatment_control` | Control vs treatment comparison |
| `neutrals_only` | All groups equal weight |
| `opposing` | Bidirectional effects (up/down) |
| `multi_category` | 4+ categories |
| `volcano` | Differential expression plots |

---

## Integration Checklist

Before submitting a new brand skill, run the validation tools:

```bash
# Run full validation
python skills/brand-interface/validation/validate_brand.py skills/your-brand -v

# The validator checks all items below automatically
```

### Structure (automated)
- [ ] Directory follows required structure
- [ ] `tokens/brand-tokens.json` follows JSON Schema
- [ ] At least one adapter provided

### API Compliance (automated)
- [ ] Adapter exports required functions (`BRAND_COLORS`, `set_brand_style`, `get_cycle`, `get_color`)
- [ ] Function signatures match interface specification
- [ ] Type stub compliance (optional: use mypy with `adapter_interface.pyi`)

### SKILL.md (automated)
- [ ] Has proper YAML frontmatter with required fields
- [ ] Has `brand-type` from controlled vocabulary
- [ ] Has recommended XML sections

### Accessibility (automated)
- [ ] All colors pass WCAG AA contrast (3:1 minimum)
- [ ] Text colors pass WCAG AA (4.5:1 minimum)
- [ ] Grayscale distinguishability >= 30
- [ ] Colorblind simulation check (protanopia, deuteranopia, tritanopia)

### Integration (manual)
- [ ] Added to SKILL_ROUTER.md "Brand Application" section
- [ ] Cross-referenced from plotting-libraries and skills/shared/accessibility/
- [ ] CHANGELOG.md updated

---

## Example: Minimal Brand Skill

A minimal brand skill would include:

```
skills/my-brand/
├── SKILL.md
├── tokens/
│   └── brand-tokens.json
└── adapters/
    └── matplotlib_adapter.py
```

With `brand-tokens.json`:

```json
{
  "meta": {"name": "My Brand", "version": "1.0.0"},
  "colors": {
    "primary": {"highlight": {"hex": "#FF0000", "role": "emphasis"}},
    "neutrals": {
      "dark": {"hex": "#333333", "role": "text"},
      "light": {"hex": "#CCCCCC", "role": "secondary"}
    },
    "structure": {"white": {"hex": "#FFFFFF"}, "black": {"hex": "#000000"}}
  },
  "color_cycles": {
    "default": {"colors": ["#333333", "#FF0000", "#CCCCCC"]}
  }
}
```

---

## Reference Implementation

See `skills/oligon-brand/` for a complete reference implementation of this interface contract.

---

*Interface contract version: 1.1.0*
*Compatible with skill library version: 2.10.0+*
*Validation tools version: 1.0.0*
