# Brand Skill Interface Contract

> Specification for creating alternative brand skills compatible with the skill library
> Version: 1.0.0
> Created: 2025-12-30

## Purpose

This document defines the interface that brand skills must implement to integrate with the skill library. Following this contract ensures that:

1. Skills like `plotting-libraries` can load any brand without code changes
2. SKILL_ROUTER.md can route to the correct brand skill
3. Future brands integrate seamlessly

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
| `<cross_references>` | Links to visual-design, plotting-libraries |
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
│     └─ Use visual-design defaults
```

And to the "Brand Application: Quick Selection" table:

| Output | Brand Skill | Implementation Skill |
|--------|-------------|---------------------|
| Publication figure (Python) | [your-brand] | plotting-libraries |
| ... | ... | ... |

---

## Integration Checklist

Before submitting a new brand skill:

### Structure
- [ ] Directory follows required structure
- [ ] `tokens/brand-tokens.json` follows schema above
- [ ] At least one adapter provided

### API Compliance
- [ ] Adapter exports required functions
- [ ] `set_brand_style()` applies rcParams correctly
- [ ] `get_cycle()` returns list of hex strings
- [ ] `get_color()` returns single hex string

### SKILL.md
- [ ] Has proper frontmatter with `brand-type` and `tokens-file`
- [ ] Has `<cross_references>` to visual-design and plotting-libraries
- [ ] Has `<decision_framework>` for color cycle selection
- [ ] Has `<success_criteria>` checklist

### Accessibility
- [ ] Colors tested for grayscale readability
- [ ] Colors tested for colorblind accessibility
- [ ] Redundant encoding documented (shapes, patterns)

### Integration
- [ ] Added to SKILL_ROUTER.md "Brand Application" section
- [ ] Cross-referenced from visual-design and plotting-libraries
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

*Interface contract version: 1.0.0*
*Compatible with skill library version: 2.10.0+*
