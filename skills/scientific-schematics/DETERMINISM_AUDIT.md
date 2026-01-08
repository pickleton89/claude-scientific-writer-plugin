# Determinism Audit: Scientific Schematics Skill

> **Audit Date:** 2026-01-07
> **Skill Version:** 2.3.0
> **Development Stage:** First Draft Skill
> **Auditor:** Claude Opus 4.5

---

## Executive Summary

The scientific-schematics skill has a solid foundation with quality thresholds, iteration logic, and score parsing already implemented deterministically in Python. However, significant determinism opportunities exist in pre-generation validation—the decision matrix, complexity limits, and prompt completeness checks are currently prose-only and could be converted to code-based validators. The core image generation and quality review are inherently stochastic (AI-based), but better input standardization would reduce variance in outputs.

**Current Determinism Score:** ~35%
**Target Determinism Score:** ~60%
**Achievable Improvement:** +25%

---

## Input Analysis

### Current State

| Input | Validation | Determinism |
|-------|------------|-------------|
| User prompt | Free-form, no validation | ❌ Low |
| Document type | Enum (8 options + default) | ✅ High |
| Max iterations | Validated (1-2) | ✅ High |
| Output path | String, no validation | ⚠️ Medium |
| Review model | Enum (flash/pro) | ✅ High |

### Recommendations

#### 1. Create Prompt Schema Dataclass

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class SchematicPrompt:
    """Structured prompt with required and optional fields."""

    # Required fields
    diagram_type: Literal[
        "consort", "prisma", "methods_flowchart",
        "transformer", "cnn", "rnn_lstm", "neural_network",
        "pathway", "metabolic", "regulatory", "interaction",
        "system_architecture", "data_flow", "block_diagram", "circuit",
        "conceptual", "hierarchy", "venn"
    ]
    components: list[str]  # Minimum 3 elements
    layout: Literal["top-to-bottom", "left-to-right", "circular", "hierarchical"]

    # Optional fields
    labels: list[str] = field(default_factory=list)
    quantitative_details: str | None = None
    style_notes: str | None = None
    colorblind_safe: bool = True

    def validate(self) -> tuple[bool, list[str]]:
        """Validate prompt meets requirements."""
        issues = []
        if len(self.components) < 3:
            issues.append(f"Need at least 3 components, got {len(self.components)}")
        return len(issues) == 0, issues
```

#### 2. Add Prompt Validator Function

```python
# scripts/validate_prompt.py

import re
from typing import NamedTuple

class PromptAnalysis(NamedTuple):
    valid: bool
    issues: list[str]
    warnings: list[str]
    detected_type: str | None
    component_count: int

# Keywords that indicate diagram types
DIAGRAM_TYPE_KEYWORDS = {
    "consort": ["consort", "participant flow", "rct", "randomized", "clinical trial"],
    "prisma": ["prisma", "systematic review", "screening", "meta-analysis"],
    "transformer": ["transformer", "attention", "encoder-decoder", "bert", "gpt"],
    "cnn": ["cnn", "convolutional", "resnet", "vgg", "image classification"],
    "pathway": ["pathway", "signaling", "mapk", "pi3k", "phosphorylation"],
    "circuit": ["circuit", "op-amp", "resistor", "capacitor", "electronics"],
}

LAYOUT_KEYWORDS = ["top-to-bottom", "left-to-right", "vertical", "horizontal",
                   "circular", "hierarchical"]

def validate_prompt(prompt_text: str) -> PromptAnalysis:
    """
    Validate prompt contains required elements.

    Checks for:
    - Diagram type indicators
    - Component mentions (arrows, nodes, elements)
    - Layout specification
    - Quantitative details
    """
    issues = []
    warnings = []
    prompt_lower = prompt_text.lower()

    # Detect diagram type
    detected_type = None
    for dtype, keywords in DIAGRAM_TYPE_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            detected_type = dtype
            break

    if not detected_type:
        issues.append("No recognizable diagram type detected. Include keywords like "
                     "'CONSORT', 'transformer', 'pathway', 'circuit', etc.")

    # Check for layout specification
    has_layout = any(kw in prompt_lower for kw in LAYOUT_KEYWORDS)
    if not has_layout:
        warnings.append("No layout direction specified. Consider adding "
                       "'top-to-bottom' or 'left-to-right'")

    # Estimate component count (rough heuristic)
    component_indicators = len(re.findall(r'→|->|to |from |connects?|box|node|layer',
                                          prompt_lower))
    if component_indicators < 3:
        warnings.append(f"Low component count detected (~{component_indicators}). "
                       "Consider adding more specific elements.")

    # Check for quantitative details
    has_numbers = bool(re.search(r'n\s*=\s*\d+|\d+\s*(layers?|nodes?|steps?)', prompt_lower))
    if not has_numbers:
        warnings.append("No quantitative details found. Consider adding counts "
                       "like 'n=500' or '6 layers'")

    return PromptAnalysis(
        valid=len(issues) == 0,
        issues=issues,
        warnings=warnings,
        detected_type=detected_type,
        component_count=component_indicators
    )
```

#### 3. Complexity Pre-Check

```python
# scripts/utils/complexity_limits.py

from typing import TypedDict

class ComplexityLimits(TypedDict):
    max_nodes: int
    max_edges: int
    max_levels: int

COMPLEXITY_LIMITS: dict[str, ComplexityLimits] = {
    "flowchart": {"max_nodes": 15, "max_edges": 20, "max_levels": 4},
    "consort": {"max_nodes": 15, "max_edges": 20, "max_levels": 4},
    "prisma": {"max_nodes": 12, "max_edges": 15, "max_levels": 4},
    "neural_network": {"max_nodes": 12, "max_edges": 0, "max_levels": 3},
    "transformer": {"max_nodes": 12, "max_edges": 0, "max_levels": 3},
    "cnn": {"max_nodes": 12, "max_edges": 0, "max_levels": 3},
    "pathway": {"max_nodes": 10, "max_edges": 12, "max_levels": 3},
    "system_architecture": {"max_nodes": 12, "max_edges": 15, "max_levels": 3},
    "block_diagram": {"max_nodes": 10, "max_edges": 12, "max_levels": 2},
    "circuit": {"max_nodes": 15, "max_edges": 20, "max_levels": 2},
}

def check_complexity(diagram_type: str, estimated_nodes: int) -> tuple[bool, str | None]:
    """
    Check if estimated complexity is within limits.

    Returns:
        (within_limits, warning_message)
    """
    limits = COMPLEXITY_LIMITS.get(diagram_type, COMPLEXITY_LIMITS["block_diagram"])

    if estimated_nodes > limits["max_nodes"]:
        return False, (
            f"Estimated {estimated_nodes} nodes exceeds limit of {limits['max_nodes']} "
            f"for {diagram_type}. Consider splitting into multiple figures."
        )

    if estimated_nodes > limits["max_nodes"] * 0.8:
        return True, (
            f"Approaching complexity limit ({estimated_nodes}/{limits['max_nodes']} nodes). "
            "Consider simplifying for better clarity."
        )

    return True, None
```

---

## Output Analysis

### Current State

| Output | Structure | Determinism |
|--------|-----------|-------------|
| PNG images | Versioned naming | ✅ High |
| JSON review log | Consistent schema | ✅ High |
| Quality score | Regex-parsed | ✅ High |
| File organization | Deterministic paths | ✅ High |

### Recommendations

#### 1. Enforce Output Schema with Pydantic

```python
# scripts/utils/schemas.py

from pydantic import BaseModel, Field
from typing import Literal

class IterationResult(BaseModel):
    """Schema for a single generation iteration."""
    iteration: int = Field(ge=1, le=5)
    image_path: str
    prompt: str
    critique: str
    score: float = Field(ge=0, le=10)
    needs_improvement: bool
    success: bool

class GenerationResults(BaseModel):
    """Schema for complete generation results."""
    user_prompt: str
    doc_type: Literal["journal", "conference", "poster", "presentation",
                      "report", "grant", "thesis", "preprint", "default"]
    quality_threshold: float = Field(ge=0, le=10)
    iterations: list[IterationResult]
    final_image: str | None
    final_score: float = Field(ge=0, le=10)
    success: bool
    early_stop: bool
    early_stop_reason: str | None

    # Metadata for reproducibility
    generation_model: str = "google/gemini-3-pro-image-preview"
    review_model: str = "google/gemini-3-flash"
    prompt_hash: str | None = None  # SHA256 of final prompt

class Config:
    json_schema_extra = {
        "example": {
            "user_prompt": "CONSORT flowchart...",
            "doc_type": "journal",
            "quality_threshold": 8.5,
            "iterations": [...],
            "final_score": 8.7,
            "success": True
        }
    }
```

#### 2. Add Image Metadata Validation

```python
# scripts/validate_image.py

from pathlib import Path
from typing import NamedTuple

class ImageMetadata(NamedTuple):
    valid: bool
    width: int
    height: int
    format: str
    size_kb: float
    issues: list[str]

def validate_output_image(path: str, min_dimension: int = 512) -> ImageMetadata:
    """
    Verify generated image meets basic requirements.

    Checks:
    - File exists and is readable
    - Dimensions are reasonable
    - File size is not suspiciously small
    - Format is PNG
    """
    from PIL import Image

    issues = []
    path = Path(path)

    if not path.exists():
        return ImageMetadata(False, 0, 0, "", 0, ["File does not exist"])

    size_kb = path.stat().st_size / 1024
    if size_kb < 10:
        issues.append(f"File suspiciously small ({size_kb:.1f} KB)")

    try:
        img = Image.open(path)
        width, height = img.size
        fmt = img.format or "UNKNOWN"

        if width < min_dimension or height < min_dimension:
            issues.append(f"Dimensions too small: {width}x{height}")

        if fmt not in ("PNG", "JPEG", "WEBP"):
            issues.append(f"Unexpected format: {fmt}")

        return ImageMetadata(
            valid=len(issues) == 0,
            width=width,
            height=height,
            format=fmt,
            size_kb=size_kb,
            issues=issues
        )
    except Exception as e:
        return ImageMetadata(False, 0, 0, "", size_kb, [f"Cannot read image: {e}"])
```

---

## Deterministic Opportunities

### Summary Matrix

| Component | Current | Target | Effort | Impact | Priority |
|-----------|---------|--------|--------|--------|----------|
| Prompt validation | None | Code validator | Medium | High | 1 |
| Schematic type selection | Prose decision tree | Python function | Low | High | 2 |
| Complexity limits | Markdown table | Python dict + validator | Low | Medium | 3 |
| Brand colors | Prose guidance | Structured lookup | Low | Medium | 4 |
| Output schema | Implicit | Pydantic model | Low | Medium | 5 |
| Quality thresholds | Already code ✅ | n/a | - | - | - |
| Iteration logic | Already code ✅ | n/a | - | - | - |
| Score parsing | Already regex ✅ | n/a | - | - | - |

### Implementation: Schematic Type Selector

```python
# scripts/diagram_type_selector.py

from typing import Literal

Purpose = Literal["study_design", "ml_architecture", "biology", "systems", "abstract"]
Domain = Literal[
    # Study design
    "clinical_trial", "systematic_review", "experimental",
    # ML
    "attention", "image", "sequence", "general",
    # Biology
    "signaling", "metabolic", "gene", "protein",
    # Systems
    "software", "data", "electronics", "hardware",
    # Abstract
    "theory", "classification", "comparison"
]

TYPE_MAP: dict[tuple[Purpose, Domain | None], str] = {
    # Study Design
    ("study_design", "clinical_trial"): "consort",
    ("study_design", "systematic_review"): "prisma",
    ("study_design", "experimental"): "methods_flowchart",
    ("study_design", None): "methods_flowchart",

    # ML Architecture
    ("ml_architecture", "attention"): "transformer",
    ("ml_architecture", "image"): "cnn",
    ("ml_architecture", "sequence"): "rnn_lstm",
    ("ml_architecture", "general"): "neural_network",
    ("ml_architecture", None): "neural_network",

    # Biology
    ("biology", "signaling"): "pathway",
    ("biology", "metabolic"): "metabolic_pathway",
    ("biology", "gene"): "regulatory_network",
    ("biology", "protein"): "interaction_network",
    ("biology", None): "pathway",

    # Systems
    ("systems", "software"): "system_architecture",
    ("systems", "data"): "data_flow_diagram",
    ("systems", "electronics"): "circuit_schematic",
    ("systems", "hardware"): "block_diagram",
    ("systems", None): "block_diagram",

    # Abstract
    ("abstract", "theory"): "conceptual_framework",
    ("abstract", "classification"): "hierarchy_diagram",
    ("abstract", "comparison"): "venn_diagram",
    ("abstract", None): "conceptual_framework",
}

def select_diagram_type(purpose: Purpose, domain: Domain | None = None) -> str:
    """
    Deterministic diagram type selection based on purpose and domain.

    Args:
        purpose: High-level category (study_design, ml_architecture, biology, systems, abstract)
        domain: More specific domain within the purpose category

    Returns:
        Recommended diagram type string

    Examples:
        >>> select_diagram_type("study_design", "clinical_trial")
        'consort'
        >>> select_diagram_type("ml_architecture", "attention")
        'transformer'
        >>> select_diagram_type("biology")
        'pathway'
    """
    # Try exact match first
    result = TYPE_MAP.get((purpose, domain))
    if result:
        return result

    # Fall back to purpose-only match
    result = TYPE_MAP.get((purpose, None))
    if result:
        return result

    # Ultimate fallback
    return "block_diagram"


def infer_type_from_prompt(prompt: str) -> tuple[str, float]:
    """
    Infer diagram type from free-form prompt text.

    Returns:
        (diagram_type, confidence_score)
    """
    prompt_lower = prompt.lower()

    # High-confidence keyword matches
    HIGH_CONFIDENCE_KEYWORDS = {
        "consort": ["consort", "participant flow", "randomized controlled"],
        "prisma": ["prisma", "systematic review", "screening records"],
        "transformer": ["transformer", "self-attention", "encoder-decoder"],
        "cnn": ["cnn", "convolutional neural", "convnet"],
        "pathway": ["signaling pathway", "mapk", "pi3k/akt"],
        "circuit": ["circuit schematic", "op-amp", "resistor capacitor"],
    }

    for dtype, keywords in HIGH_CONFIDENCE_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            return dtype, 0.9

    # Medium-confidence matches
    MEDIUM_CONFIDENCE_KEYWORDS = {
        "flowchart": ["flowchart", "flow chart", "process flow"],
        "neural_network": ["neural network", "deep learning", "layers"],
        "pathway": ["pathway", "signaling", "cascade"],
        "system_architecture": ["architecture", "system diagram", "components"],
        "block_diagram": ["block diagram", "blocks", "modules"],
    }

    for dtype, keywords in MEDIUM_CONFIDENCE_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            return dtype, 0.6

    return "block_diagram", 0.3
```

### Implementation: Brand Colors Lookup

```python
# scripts/utils/brand_colors.py

from typing import NamedTuple

class ColorPalette(NamedTuple):
    primary: str
    contrast: str
    text: str
    secondary: str
    background: str
    name: str

# Oligon Scientific Brand (default)
OLIGON_BRAND = ColorPalette(
    primary="#2DB2E8",      # Brand Blue - highlights, key components
    contrast="#E8622D",     # Orange - warnings, opposing elements
    text="#222222",         # Dark Gray - primary text
    secondary="#666666",    # Medium Gray - supporting components
    background="#FFFFFF",   # White - clean background
    name="Oligon Scientific"
)

# Okabe-Ito Colorblind-Safe Palette
OKABE_ITO = ColorPalette(
    primary="#0072B2",      # Blue
    contrast="#D55E00",     # Vermillion
    text="#000000",         # Black
    secondary="#56B4E9",    # Sky Blue
    background="#FFFFFF",   # White
    name="Okabe-Ito"
)

# Generic Scientific
GENERIC = ColorPalette(
    primary="#4A90D9",      # Medium Blue
    contrast="#D94A4A",     # Medium Red
    text="#333333",         # Dark Gray
    secondary="#7A7A7A",    # Medium Gray
    background="#FFFFFF",   # White
    name="Generic Scientific"
)

PALETTES = {
    "oligon": OLIGON_BRAND,
    "okabe-ito": OKABE_ITO,
    "colorblind": OKABE_ITO,
    "accessibility": OKABE_ITO,
    "generic": GENERIC,
    "default": OLIGON_BRAND,
}

def get_palette(name: str = "default") -> ColorPalette:
    """Get color palette by name."""
    return PALETTES.get(name.lower(), OLIGON_BRAND)

def format_color_guidance(palette: ColorPalette) -> str:
    """Format palette as prompt guidance text."""
    return f"""Use {palette.name} color scheme:
- Primary elements: {palette.primary} - highlights, key components
- Contrast/alerts: {palette.contrast} - warnings, opposing elements
- Text/labels: {palette.text} - primary text
- Secondary elements: {palette.secondary} - supporting components
- Background: {palette.background} - clean background"""

def inject_colors_into_prompt(prompt: str, palette_name: str = "default") -> str:
    """Append color guidance to prompt if not already present."""
    # Check if colors are already specified
    if any(word in prompt.lower() for word in ["#", "color:", "palette", "okabe"]):
        return prompt

    palette = get_palette(palette_name)
    color_guidance = format_color_guidance(palette)

    return f"{prompt}\n\n{color_guidance}"
```

---

## Reproducibility Assessment

### Rating: Medium

### Factors Affecting Reproducibility

| Factor | Variance Impact | Mitigation Strategy |
|--------|-----------------|---------------------|
| AI image generation | High (inherent) | Accept; focus on quality gating |
| AI quality review | Medium | Score parsing + thresholds already mitigate |
| Prompt wording variations | High | Structured templates reduce variance |
| API model versions | Unknown | Log model IDs in review JSON |
| Temperature/sampling | Unknown | Not exposed by OpenRouter for this model |

### Recommendations for Improved Reproducibility

1. **Log Model Identifiers:** Already partially done. Ensure both generation and review model IDs are in JSON.

2. **Prompt Hash:** Add SHA256 of final prompt to enable reproducibility tracking:
```python
import hashlib

def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]
```

3. **Score Trend Tracking:** Monitor historical scores to detect model drift:
```python
# Append to scores.jsonl for trend analysis
{"timestamp": "2026-01-07T10:30:00", "diagram_type": "consort",
 "doc_type": "journal", "score": 8.7, "iterations": 2}
```

4. **Version Pinning:** Document tested API model versions in SKILL.md.

---

## Code Integration Recommendations

### File Structure

```
scripts/
├── generate_schematic.py           # Entry point (exists)
├── generate_schematic_ai.py        # Main generator (exists)
├── validate_prompt.py              # NEW: Pre-generation validation
├── diagram_type_selector.py        # NEW: Deterministic type selection
├── validate_image.py               # NEW: Post-generation validation
├── test_ai_generation.py           # Exists
└── utils/
    ├── __init__.py                 # NEW
    ├── brand_colors.py             # NEW: Color palette lookup
    ├── complexity_limits.py        # NEW: Limit definitions
    └── schemas.py                  # NEW: Pydantic models
```

### Integration Points

**Pre-Generation (in generate_schematic_ai.py):**

```python
from validate_prompt import validate_prompt
from utils.complexity_limits import check_complexity
from utils.brand_colors import inject_colors_into_prompt

def generate_iterative(self, user_prompt: str, ...):
    # NEW: Validate prompt before expensive API calls
    analysis = validate_prompt(user_prompt)
    if not analysis.valid:
        raise ValueError(f"Invalid prompt: {'; '.join(analysis.issues)}")

    for warning in analysis.warnings:
        self._log(f"⚠ {warning}")

    # NEW: Check complexity
    ok, complexity_warning = check_complexity(
        analysis.detected_type,
        analysis.component_count
    )
    if complexity_warning:
        self._log(f"⚠ {complexity_warning}")

    # NEW: Inject brand colors if not specified
    user_prompt = inject_colors_into_prompt(user_prompt)

    # ... existing generation logic ...
```

**Post-Generation:**

```python
from validate_image import validate_output_image
from utils.schemas import GenerationResults

# After saving image
img_meta = validate_output_image(str(iter_path))
if not img_meta.valid:
    self._log(f"⚠ Image issues: {img_meta.issues}")

# When saving results
results = GenerationResults(**results_dict)  # Validates schema
with open(log_path, "w") as f:
    f.write(results.model_dump_json(indent=2))
```

---

## Best Practices Evaluation

### Strengths

| Practice | Status | Notes |
|----------|--------|-------|
| Clear workflow stages | ✅ | 5 stages with exit criteria |
| Decision guidance | ✅ | Decision matrix in SKILL.md |
| Anti-patterns documented | ✅ | 6 common pitfalls with solutions |
| Quality scoring rubric | ✅ | 5 dimensions, clear scoring |
| Smart iteration logic | ✅ | Early stopping when threshold met |
| Cross-references | ✅ | Links to related skills |
| Error handling table | ✅ | Common errors with solutions |

### Areas for Improvement

| Area | Current | Recommended |
|------|---------|-------------|
| Prompt templates | Examples only | Enforced structure |
| Pre-flight validation | None | validate_prompt() |
| Single source of truth | Duplicated (SKILL.md + diagram_types.md) | Consolidate to code |
| Automated testing | Manual only | pytest suite |

---

## Maintainability Score

### Rating: Medium-High

### Justification

**Strengths:**
- Clean code organization (wrapper → generator)
- Constants externalized (QUALITY_THRESHOLDS dict)
- Comprehensive logging (verbose mode + JSON)
- Minimal dependencies (just `requests`)
- Good docstrings and comments

**Concerns:**
- Decision tree disconnected from code
- Complexity limits as documentation only
- No automated tests for validators

### Recommendations

1. Create `tests/` directory with pytest tests
2. Single source of truth: code dicts imported by SKILL.md examples
3. Add type hints throughout (partial currently)

---

## Complexity Assessment

### Is Complexity Appropriate?

**Yes**, mostly appropriate for the task.

### Justified Complexity

| Component | Justification |
|-----------|---------------|
| Iterative refinement loop | Necessary for quality improvement |
| Quality threshold system | Appropriate for different document types |
| Review model selection | Useful cost/quality tradeoff |
| Smart early stopping | Reduces unnecessary API calls |

### Unnecessary Complexity

None identified. The skill is appropriately scoped.

### Missing Beneficial Structure

| Missing | Benefit | Priority |
|---------|---------|----------|
| Input validation layer | Catch errors early, save API costs | High |
| Structured prompt builder | Reduce prompt variance | Medium |
| Output schema validation | Ensure downstream reliability | Medium |

---

## Prioritized Recommendations

### Priority 1: Create Prompt Validator Script
**Effort:** Medium | **Impact:** High

- Validate prompts have required elements before API calls
- Reduces wasted API spend on inadequate prompts
- Provides actionable feedback to users
- File: `scripts/validate_prompt.py`

### Priority 2: Implement Schematic Type Selector
**Effort:** Low | **Impact:** High

- Convert prose decision tree to Python lookup
- Enables programmatic type resolution
- Reduces ambiguity in multi-skill workflows
- File: `scripts/diagram_type_selector.py`

### Priority 3: Add Complexity Pre-Check
**Effort:** Low | **Impact:** Medium

- Validate against diagram type limits before generation
- Warn users about overcrowded diagrams early
- Python dict with simple count comparisons
- File: `scripts/utils/complexity_limits.py`

### Priority 4: Create Brand Color Lookup Module
**Effort:** Low | **Impact:** Medium

- Centralize color definitions
- Enable programmatic color injection into prompts
- Single source of truth for brand compliance
- File: `scripts/utils/brand_colors.py`

### Priority 5: Add Output Schema Validation
**Effort:** Low | **Impact:** Medium

- Use Pydantic for GenerationResults schema
- Ensures consistent JSON structure
- Enables downstream tooling reliability
- File: `scripts/utils/schemas.py`

---

## Implementation Roadmap

### Phase 1: Pre-Generation Validation (v2.4.0)

**Files to create:**
- `scripts/validate_prompt.py`
- `scripts/utils/__init__.py`
- `scripts/utils/complexity_limits.py`

**Integration:**
- Add validation call at start of `generate_iterative()`
- Log warnings for missing optional elements
- Fail fast on invalid prompts

**Testing:**
- Add `tests/test_validate_prompt.py`
- Test keyword detection
- Test complexity limits

### Phase 2: Deterministic Selection (v2.5.0)

**Files to create:**
- `scripts/diagram_type_selector.py`
- `scripts/utils/brand_colors.py`

**Integration:**
- Use type selector in workflow automation
- Auto-inject brand colors when not specified

**Testing:**
- Add `tests/test_diagram_selector.py`
- Add `tests/test_brand_colors.py`

### Phase 3: Output Validation (v2.6.0)

**Files to create:**
- `scripts/validate_image.py`
- `scripts/utils/schemas.py`

**Integration:**
- Validate images after generation
- Use Pydantic for JSON output

**Testing:**
- Add `tests/test_validate_image.py`
- Add `tests/test_schemas.py`

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Pre-generation validation | 0% | 100% | All prompts validated before API call |
| Prompt rejection rate | N/A | <10% | Invalid prompts caught before API |
| API call waste | Unknown | -30% | Fewer retries due to bad prompts |
| Output schema compliance | Implicit | 100% | All outputs pass Pydantic validation |
| Code coverage | 0% | 80% | pytest coverage report |

---

## Appendix: Testing Plan

### Unit Tests

```python
# tests/test_validate_prompt.py

import pytest
from scripts.validate_prompt import validate_prompt

def test_valid_consort_prompt():
    prompt = "CONSORT flowchart with 500 screened, 150 excluded, 350 randomized"
    result = validate_prompt(prompt)
    assert result.valid
    assert result.detected_type == "consort"

def test_missing_diagram_type():
    prompt = "A diagram with some boxes and arrows"
    result = validate_prompt(prompt)
    assert not result.valid
    assert "No recognizable diagram type" in result.issues[0]

def test_warns_missing_layout():
    prompt = "CONSORT flowchart with enrollment and randomization"
    result = validate_prompt(prompt)
    assert result.valid  # Still valid, just warning
    assert any("layout" in w.lower() for w in result.warnings)
```

```python
# tests/test_diagram_selector.py

import pytest
from scripts.diagram_type_selector import select_diagram_type, infer_type_from_prompt

def test_exact_match():
    assert select_diagram_type("study_design", "clinical_trial") == "consort"
    assert select_diagram_type("ml_architecture", "attention") == "transformer"

def test_fallback_to_purpose():
    assert select_diagram_type("biology") == "pathway"
    assert select_diagram_type("systems") == "block_diagram"

def test_infer_from_prompt():
    dtype, conf = infer_type_from_prompt("CONSORT participant flow diagram")
    assert dtype == "consort"
    assert conf >= 0.9
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-07 | Audit v1.0 | Initial determinism audit completed |

---

*This audit follows the determinism audit methodology established for the claude-scientific-writer-plugin project.*
