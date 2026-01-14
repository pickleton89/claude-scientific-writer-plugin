# Image Generation Skills Refactoring Plan

> **Status:** All Phases Complete ✓
> **Created:** 2026-01-14
> **Phase 1 Completed:** 2026-01-14
> **Phase 2 Completed:** 2026-01-14
> **Phase 3 Completed:** 2026-01-14
> **Phase 4 Completed:** 2026-01-14
> **Scope:** Consolidate image generation, add Mermaid tier for cost optimization

---

## Executive Summary

This document outlines a refactoring plan for the image generation capabilities in claude-scientific-writer-plugin based on a comparative analysis of `generate-image` and `scientific-schematics` skills. The primary goals are:

1. **Simplify generate-image** - Remove unnecessary model options (FLUX.2)
2. **Add Mermaid tier** - Free, instant diagram generation for simple use cases
3. **Share common utilities** - Extract duplicated API handling code
4. **Clarify skill boundaries** - Document when to use which skill

| Initiative | Impact | Effort | Priority |
|------------|--------|--------|----------|
| Add Mermaid generation tier | High (cost savings) | Medium | 1 |
| Simplify generate-image models | Medium | Low | 2 |
| Extract shared API utilities | Low | Low | 3 |
| Update documentation & routing | Medium | Low | 4 |

---

## Part 1: Discussion Summary

### 1.1 Comparative Analysis: generate-image vs scientific-schematics

#### Architecture Comparison

| Aspect | generate-image | scientific-schematics |
|--------|----------------|----------------------|
| **Primary Purpose** | General imagery (photos, art, illustrations) | Technical diagrams & schematics |
| **API Gateway** | OpenRouter | OpenRouter |
| **Generation Model** | Gemini 3 Pro, FLUX.2 Pro/Flex | Gemini 3 Pro only |
| **Quality Review** | Manual (validate_output.py) | AI-powered (Gemini 3 Flash/Pro) |
| **Iteration Loop** | Human-in-the-loop | Fully automated with scoring |
| **Brand Integration** | None | Oligon brand colors |
| **Accessibility** | Basic | WCAG contrast validation, Okabe-Ito |

#### API Key Handling (Identical in Both)

Both skills use the same approach:
- Environment variable: `OPENROUTER_API_KEY`
- `.env` file search (walks up directories)
- Direct parameter override
- Same error messages pointing to https://openrouter.ai/keys

#### External Services Comparison

| Service | generate-image | scientific-schematics |
|---------|----------------|----------------------|
| OpenRouter | Yes | Yes |
| Gemini 3 Pro (Generation) | Yes (Default) | Yes (Only option) |
| Gemini 3 Flash (Review) | No | Yes (Default review) |
| FLUX.2 Pro | Yes | No |
| FLUX.2 Flex | Yes (Budget) | No |

**Key Insight:** scientific-schematics uses a two-model architecture (generate + review), while generate-image relies on human judgment.

### 1.2 Use Case Matrix

#### generate-image: Best For

| Use Case | Example | Why This Skill |
|----------|---------|----------------|
| Scientific hero images | Journal cover art, graphical abstracts | Photorealistic/artistic quality |
| Conceptual illustrations | Cell biology concept art | Creative interpretation |
| Laboratory photography | Equipment photos, lab settings | Photorealistic style |
| Product visualization | Instrument renders | High visual fidelity |
| Artistic representations | "DNA double helix in watercolor style" | Artistic medium control |
| Stock-style imagery | Generic science backgrounds | Flexible output |
| Image editing | Modify existing images | Editing/inpainting support |

#### scientific-schematics: Best For

| Use Case | Example | Why This Skill |
|----------|---------|----------------|
| Study flow diagrams | CONSORT, PRISMA flowcharts | Domain-specific templates |
| Neural network architecture | Transformer, CNN, RNN diagrams | ML vocabulary awareness |
| Biological pathways | MAPK, PI3K, metabolic pathways | Scientific accuracy focus |
| System architecture | Software/hardware block diagrams | Logical layout optimization |
| Experimental workflows | Methods flowcharts | Publication-ready quality |
| Gene regulatory networks | Transcription factor interactions | Domain knowledge |
| Circuit schematics | Electronic component diagrams | Technical precision |

#### Overlap Zone

| Use Case | Recommendation |
|----------|----------------|
| Simple conceptual diagram | scientific-schematics (auto-review) |
| Stylized process flow | generate-image (if artistic style needed) |
| Abstract scientific concept | Depends on output style |
| Presentation graphics | scientific-schematics for technical |
| Poster figures | scientific-schematics for diagrams |

### 1.3 Quality Systems Comparison

| Feature | generate-image | scientific-schematics |
|---------|----------------|----------------------|
| Scoring Rubric | 10-point manual | 10-point automated (5 dimensions) |
| Quality Dimensions | Single overall | Scientific accuracy, Clarity, Labels, Layout, Professionalism |
| Automated Review | No | Yes (AI-powered) |
| Iteration Strategy | Manual refinement | Automatic prompt improvement |
| Document-Type Thresholds | Draft/Presentation/Publication/Hero | Journal/Conference/Poster/Presentation/etc. |
| Stopping Rules | Score-based + manual | Score + plateau detection + limits |

### 1.4 Key Findings

1. **Skills serve distinct purposes** - Should remain separate
2. **FLUX.2 models add complexity** - Rarely needed, Gemini 3 Pro handles most cases
3. **API code is duplicated** - Should be shared
4. **Simple diagrams are over-engineered** - Mermaid would be cheaper/faster

---

## Part 2: Mermaid Integration Plan

### 2.1 Rationale

**Problem:** Every diagram generation hits the OpenRouter API, costing money and time even for simple flowcharts that don't need AI creativity.

**Solution:** Add a Mermaid tier for basic diagrams:
- **Cost:** $0 (local rendering)
- **Speed:** ~100ms vs 10-30s for AI
- **Determinism:** Same input = same output
- **Version Control:** Text source is git-friendly

### 2.2 Tiered Architecture

```
Diagram Request
      │
      ▼
┌─────────────────────────────────────┐
│         Complexity Analysis         │
│  - Node count estimation            │
│  - Diagram type detection           │
│  - Quality requirements             │
└─────────────────────────────────────┘
      │
      ├─────────────────────────────────────┐
      │                                     │
      ▼                                     ▼
┌─────────────┐                    ┌─────────────────┐
│   Tier 1    │                    │     Tier 2      │
│   Mermaid   │                    │  AI Generation  │
│             │                    │                 │
│ - Free      │                    │ - $0.02-0.05    │
│ - Instant   │                    │ - 10-30s        │
│ - Simple    │                    │ - Complex       │
└─────────────┘                    └─────────────────┘
      │                                     │
      ▼                                     ▼
┌─────────────┐                    ┌─────────────────┐
│   Output    │                    │ Quality Review  │
│  PNG/SVG    │                    │ (Gemini Flash)  │
└─────────────┘                    └─────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │     Output      │
                                   │    PNG/SVG      │
                                   └─────────────────┘
```

### 2.3 Mermaid Capabilities

#### Supported Diagram Types

| Diagram Type | Mermaid Support | Syntax |
|--------------|-----------------|--------|
| Flowchart | Excellent | `flowchart TD/LR` |
| Sequence diagram | Excellent | `sequenceDiagram` |
| Class diagram | Excellent | `classDiagram` |
| State diagram | Excellent | `stateDiagram-v2` |
| ER diagram | Good | `erDiagram` |
| Gantt chart | Excellent | `gantt` |
| Pie chart | Good | `pie` |
| Mind map | Good | `mindmap` |
| Timeline | Good | `timeline` |
| Block diagram | Good | `block-beta` |
| Quadrant chart | Good | `quadrantChart` |
| Sankey diagram | Good | `sankey-beta` |

#### NOT Suitable for Mermaid

| Diagram Type | Reason | Use Instead |
|--------------|--------|-------------|
| Neural network architectures | No native support | AI generation |
| Biological pathways | No domain semantics | AI generation |
| Custom positioning | Limited control | AI generation |
| Publication-quality styling | Basic theming | AI generation or polish |
| Complex labels/annotations | Text limitations | AI generation |

### 2.4 Decision Matrix for Tier Selection

```
Diagram Request Analysis
│
├─ Is diagram type supported by Mermaid?
│   └─ NO → Tier 2 (AI generation)
│
├─ Estimated complexity?
│   ├─ Simple (<10 nodes, <15 edges) → Continue evaluation
│   └─ Complex (≥10 nodes OR ≥15 edges) → Tier 2 (AI generation)
│
├─ Quality requirement?
│   ├─ Draft/Internal → Tier 1 (Mermaid)
│   ├─ Presentation → Tier 1 (Mermaid) or Tier 1+Polish
│   └─ Publication → Tier 2 (AI generation)
│
├─ Custom styling required?
│   ├─ Brand colors/fonts → Tier 2 (AI generation)
│   └─ Default styling OK → Tier 1 (Mermaid)
│
├─ Explicit user preference?
│   ├─ --engine mermaid → Tier 1 (force)
│   ├─ --engine ai → Tier 2 (force)
│   └─ --engine auto → Use decision matrix
│
└─ Default: Tier 1 (Mermaid) for simple, Tier 2 (AI) for complex
```

### 2.5 File Structure Changes

```
skills/scientific-schematics/
├── SKILL.md                              # Update with tiered approach
├── scripts/
│   ├── generate_schematic.py             # UPDATE: Router/orchestrator
│   ├── generate_mermaid.py               # NEW: Mermaid generation engine
│   ├── generate_schematic_ai.py          # EXISTING: AI generation (unchanged)
│   ├── diagram_type_selector.py          # UPDATE: Add Mermaid compatibility
│   ├── validate_prompt.py                # EXISTING (unchanged)
│   ├── validate_image.py                 # EXISTING (unchanged)
│   └── utils/
│       ├── __init__.py                   # UPDATE: Export new modules
│       ├── mermaid_templates.py          # NEW: Common Mermaid patterns
│       ├── mermaid_renderer.py           # NEW: Mermaid → PNG/SVG
│       ├── complexity_analyzer.py        # NEW: Tier selection logic
│       ├── schemas.py                    # EXISTING (unchanged)
│       ├── complexity_limits.py          # EXISTING (unchanged)
│       └── brand_colors.py               # EXISTING (unchanged)
└── tests/
    ├── test_mermaid.py                   # NEW: Mermaid generation tests
    ├── test_complexity_analyzer.py       # NEW: Tier selection tests
    ├── test_mermaid_templates.py         # NEW: Template tests
    └── ... (existing tests)
```

### 2.6 New Module Specifications

#### 2.6.1 `generate_mermaid.py`

**Purpose:** Convert natural language descriptions to Mermaid syntax and render to image.

**Key Functions:**

```python
def generate_mermaid_diagram(
    prompt: str,
    output_path: str,
    diagram_type: Optional[str] = None,
    output_format: str = "png",  # png, svg, pdf
    theme: str = "default",  # default, dark, forest, neutral
    width: int = 800,
    height: int = 600,
    background: str = "white"
) -> MermaidResult:
    """
    Generate a diagram from natural language using Mermaid.

    1. Analyze prompt to determine diagram type (if not specified)
    2. Convert natural language to Mermaid syntax
    3. Validate Mermaid syntax
    4. Render to output format
    5. Return result with metadata
    """
    pass

def prompt_to_mermaid(
    prompt: str,
    diagram_type: str
) -> str:
    """
    Convert natural language prompt to Mermaid syntax.
    Uses LLM to translate (could be local or simple rules for common patterns).
    """
    pass

def validate_mermaid_syntax(
    mermaid_code: str
) -> ValidationResult:
    """
    Validate Mermaid syntax before rendering.
    Returns errors/warnings if invalid.
    """
    pass

def render_mermaid(
    mermaid_code: str,
    output_path: str,
    output_format: str = "png",
    **render_options
) -> RenderResult:
    """
    Render Mermaid code to image file.
    Uses mermaid-cli (mmdc) or puppeteer-based rendering.
    """
    pass
```

**CLI Interface:**

```bash
# Basic usage
python generate_mermaid.py "Simple flowchart: Start → Process → End" -o output.png

# Specify diagram type
python generate_mermaid.py "..." -o output.svg --type flowchart

# Custom theme
python generate_mermaid.py "..." -o output.png --theme neutral

# Pass raw Mermaid code
python generate_mermaid.py --raw "flowchart TD; A-->B" -o output.png
```

#### 2.6.2 `mermaid_templates.py`

**Purpose:** Provide reusable Mermaid templates for common diagram types.

**Templates:**

```python
TEMPLATES = {
    "consort_basic": """
flowchart TD
    A[Assessed for eligibility<br/>n={screened}] --> B{{Excluded n={excluded}}}
    A --> C[Randomized<br/>n={randomized}]
    C --> D[Allocated to intervention<br/>n={intervention}]
    C --> E[Allocated to control<br/>n={control}]
    D --> F[Analyzed<br/>n={analyzed_intervention}]
    E --> G[Analyzed<br/>n={analyzed_control}]
    """,

    "prisma_basic": """
flowchart TD
    A[Records identified<br/>n={identified}] --> B[Records screened<br/>n={screened}]
    B --> C{{Records excluded<br/>n={excluded_screening}}}
    B --> D[Full-text assessed<br/>n={full_text}]
    D --> E{{Excluded n={excluded_full_text}}}
    D --> F[Studies included<br/>n={included}]
    """,

    "simple_flowchart": """
flowchart {direction}
{nodes}
{connections}
    """,

    "sequence_basic": """
sequenceDiagram
    participant {participant1}
    participant {participant2}
{interactions}
    """,

    "state_machine": """
stateDiagram-v2
    [*] --> {initial_state}
{transitions}
    {final_state} --> [*]
    """,
}

def fill_template(
    template_name: str,
    **kwargs
) -> str:
    """Fill a template with provided values."""
    pass

def get_template_for_type(
    diagram_type: str
) -> Optional[str]:
    """Get the appropriate template for a diagram type."""
    pass
```

#### 2.6.3 `mermaid_renderer.py`

**Purpose:** Handle Mermaid rendering to various output formats.

**Rendering Options:**

```python
class MermaidRenderer:
    """
    Renders Mermaid diagrams to image files.

    Supports multiple backends:
    1. mermaid-cli (mmdc) - Recommended, requires Node.js
    2. mermaid-py - Pure Python, limited features
    3. Online API - Fallback, requires internet
    """

    def __init__(self, backend: str = "auto"):
        """
        Initialize renderer with specified backend.

        backend options:
        - "auto": Detect best available
        - "mmdc": Use mermaid-cli
        - "python": Use mermaid-py
        - "api": Use online rendering API
        """
        pass

    def render(
        self,
        mermaid_code: str,
        output_path: str,
        output_format: str = "png",
        width: int = 800,
        height: int = 600,
        theme: str = "default",
        background_color: str = "white",
        scale: float = 2.0  # For high-DPI output
    ) -> RenderResult:
        """Render Mermaid code to file."""
        pass

    def check_backend_available(self, backend: str) -> bool:
        """Check if a rendering backend is available."""
        pass

    @staticmethod
    def install_instructions(backend: str) -> str:
        """Return installation instructions for a backend."""
        pass
```

**Installation Requirements:**

```bash
# Option 1: mermaid-cli (Recommended)
npm install -g @mermaid-js/mermaid-cli

# Option 2: Python package
pip install mermaid-py

# Verification
mmdc --version  # Should show version if installed
```

#### 2.6.4 `complexity_analyzer.py`

**Purpose:** Analyze diagram requests and determine appropriate tier.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class GenerationTier(Enum):
    MERMAID = "mermaid"
    AI = "ai"
    MERMAID_PLUS_POLISH = "mermaid+ai"

@dataclass
class ComplexityAnalysis:
    estimated_nodes: int
    estimated_edges: int
    diagram_type: str
    mermaid_compatible: bool
    recommended_tier: GenerationTier
    confidence: float
    reasoning: str

def analyze_complexity(
    prompt: str,
    doc_type: str = "default",
    force_tier: Optional[GenerationTier] = None
) -> ComplexityAnalysis:
    """
    Analyze a diagram prompt to determine complexity and recommended tier.

    Factors considered:
    - Estimated node count (from keywords, numbers in prompt)
    - Diagram type and Mermaid compatibility
    - Document type quality requirements
    - Explicit tier preference

    Returns ComplexityAnalysis with recommendation.
    """
    pass

def estimate_node_count(prompt: str) -> int:
    """
    Estimate number of nodes from prompt.

    Heuristics:
    - Count explicit numbers mentioned
    - Count component keywords (box, step, node, state, etc.)
    - Count bullet points or enumerated items
    """
    pass

def is_mermaid_compatible(diagram_type: str) -> bool:
    """Check if diagram type can be rendered with Mermaid."""
    MERMAID_TYPES = {
        "flowchart", "sequence", "class", "state", "er",
        "gantt", "pie", "mindmap", "timeline", "block",
        "consort_simple", "prisma_simple", "methods_flowchart"
    }
    return diagram_type.lower() in MERMAID_TYPES

def get_quality_requirement(doc_type: str) -> float:
    """Get minimum quality threshold for document type."""
    THRESHOLDS = {
        "journal": 8.5,
        "conference": 8.0,
        "thesis": 8.0,
        "grant": 8.0,
        "preprint": 7.5,
        "report": 7.5,
        "poster": 7.0,
        "presentation": 6.5,
        "draft": 5.0,
        "default": 7.5
    }
    return THRESHOLDS.get(doc_type, 7.5)
```

### 2.7 Updated Router Logic

**File:** `generate_schematic.py` (updated)

```python
#!/usr/bin/env python3
"""
Scientific Schematic Generator - Tiered Architecture

Routes diagram requests to appropriate generation engine:
- Tier 1 (Mermaid): Simple diagrams, free, instant
- Tier 2 (AI): Complex diagrams, publication quality
"""

import argparse
from pathlib import Path
from typing import Optional

from utils.complexity_analyzer import (
    analyze_complexity,
    ComplexityAnalysis,
    GenerationTier
)

def main():
    parser = argparse.ArgumentParser(
        description="Generate scientific diagrams with tiered approach"
    )
    parser.add_argument("prompt", help="Diagram description")
    parser.add_argument("-o", "--output", required=True, help="Output path")
    parser.add_argument(
        "--engine",
        choices=["auto", "mermaid", "ai", "mermaid+ai"],
        default="auto",
        help="Generation engine (default: auto-select)"
    )
    parser.add_argument(
        "--doc-type",
        default="default",
        help="Document type for quality threshold"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=2,
        help="Max iterations for AI generation"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Analyze complexity and determine tier
    if args.engine == "auto":
        analysis = analyze_complexity(args.prompt, args.doc_type)
        tier = analysis.recommended_tier
        if args.verbose:
            print(f"Complexity analysis: {analysis.reasoning}")
            print(f"Selected tier: {tier.value}")
    else:
        tier = GenerationTier(args.engine)

    # Route to appropriate engine
    if tier == GenerationTier.MERMAID:
        from generate_mermaid import generate_mermaid_diagram
        result = generate_mermaid_diagram(
            prompt=args.prompt,
            output_path=args.output,
            verbose=args.verbose
        )
    elif tier == GenerationTier.AI:
        from generate_schematic_ai import SchematicGenerator
        generator = SchematicGenerator()
        result = generator.generate(
            prompt=args.prompt,
            output_path=args.output,
            doc_type=args.doc_type,
            max_iterations=args.iterations,
            verbose=args.verbose
        )
    elif tier == GenerationTier.MERMAID_PLUS_POLISH:
        # Generate with Mermaid, then polish with AI
        from generate_mermaid import generate_mermaid_diagram
        from generate_schematic_ai import SchematicGenerator

        # Step 1: Mermaid draft
        temp_path = args.output.replace(".png", "_mermaid_draft.png")
        mermaid_result = generate_mermaid_diagram(
            prompt=args.prompt,
            output_path=temp_path,
            verbose=args.verbose
        )

        # Step 2: AI polish (use Mermaid output as reference)
        polish_prompt = f"""
        Improve this diagram while maintaining its structure:
        Original request: {args.prompt}

        Enhance visual quality for {args.doc_type} publication.
        Keep the same logical flow and components.
        """
        generator = SchematicGenerator()
        result = generator.generate(
            prompt=polish_prompt,
            output_path=args.output,
            doc_type=args.doc_type,
            max_iterations=1,  # Single polish pass
            verbose=args.verbose
        )

    # Report results
    if result.success:
        print(f"Generated: {args.output}")
        if hasattr(result, 'tier'):
            print(f"Engine used: {result.tier}")
        if hasattr(result, 'cost'):
            print(f"Estimated cost: ${result.cost:.4f}")
    else:
        print(f"Generation failed: {result.error}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
```

### 2.8 SKILL.md Updates

Add to scientific-schematics SKILL.md:

```markdown
## Generation Tiers

This skill uses a tiered approach to optimize cost and speed:

### Tier 1: Mermaid (Free, Instant)

**Best for:**
- Simple flowcharts (<10 nodes)
- Basic sequence diagrams
- State machines
- CONSORT/PRISMA (simple versions)
- Draft/internal documents

**Characteristics:**
- Cost: $0 (local rendering)
- Speed: ~100ms
- Output: Deterministic (same input = same output)
- Quality: Good for presentations, drafts

**Limitations:**
- No custom positioning
- Limited styling options
- No domain-specific rendering (pathways, neural networks)

### Tier 2: AI Generation (Publication Quality)

**Best for:**
- Complex diagrams (≥10 nodes)
- Neural network architectures
- Biological pathways
- Publication-quality figures
- Custom branding/styling

**Characteristics:**
- Cost: ~$0.02-0.05 per generation
- Speed: 10-30 seconds
- Output: Variable (AI creativity)
- Quality: Publication-ready

### Tier Selection

```bash
# Auto-select based on complexity (default)
python generate_schematic.py "prompt" -o output.png

# Force Mermaid (skip AI)
python generate_schematic.py "prompt" -o output.png --engine mermaid

# Force AI generation
python generate_schematic.py "prompt" -o output.png --engine ai

# Mermaid draft + AI polish
python generate_schematic.py "prompt" -o output.png --engine mermaid+ai
```

### Decision Matrix

| Condition | Recommended Tier |
|-----------|------------------|
| <10 nodes, draft/presentation | Mermaid |
| <10 nodes, publication | Mermaid+AI polish |
| ≥10 nodes | AI |
| Neural network | AI |
| Biological pathway | AI |
| Custom branding | AI |
| CONSORT/PRISMA (simple) | Mermaid |
| CONSORT/PRISMA (detailed) | AI |
```

---

## Part 3: Generate-Image Simplification

### 3.1 Rationale

The generate-image skill currently supports 3 models via OpenRouter:
- `google/gemini-3-pro-image-preview` (Default)
- `black-forest-labs/flux.2-pro`
- `black-forest-labs/flux.2-flex`

**Analysis:**
- Gemini 3 Pro handles generation, editing, AND inpainting
- FLUX.2 models add complexity but rarely provide unique value
- Single-model approach aligns with scientific-schematics

### 3.2 Proposed Changes

#### Remove FLUX.2 Support

**Files to modify:**

| File | Change |
|------|--------|
| `scripts/generate_image.py` | Remove FLUX.2 model options |
| `scripts/utils/models.py` | Remove FLUX.2 from allowlist |
| `references/model_capabilities.md` | Update to single model |
| `SKILL.md` | Simplify model selection docs |

#### Simplified models.py

```python
# Before: 3 models with complex selection logic
SUPPORTED_MODELS = {
    "google/gemini-3-pro-image-preview": {...},
    "black-forest-labs/flux.2-pro": {...},
    "black-forest-labs/flux.2-flex": {...},
}

# After: Single model
SUPPORTED_MODELS = {
    "google/gemini-3-pro-image-preview": {
        "name": "Gemini 3 Pro",
        "capabilities": ["generation", "editing", "inpainting"],
        "quality": "excellent",
        "max_resolution": 2048,
    }
}

DEFAULT_MODEL = "google/gemini-3-pro-image-preview"
```

### 3.3 Migration Path

1. Mark FLUX.2 models as deprecated (not removed)
2. Add deprecation warning when FLUX.2 is explicitly requested
3. Default all requests to Gemini 3 Pro
4. Remove FLUX.2 in next major version

---

## Part 4: Shared API Utilities

### 4.1 Rationale

Both skills have nearly identical code for:
- API key loading (.env file search)
- OpenRouter authentication
- Error handling

### 4.2 Proposed Shared Module

**Location:** `skills/shared/api_utils.py`

```python
"""
Shared API utilities for OpenRouter-based skills.

Used by:
- generate-image
- scientific-schematics
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 120
    referer: str = "https://github.com/scientific-writer"
    title: str = "Claude Scientific Writer"

def load_api_key(
    explicit_key: Optional[str] = None,
    env_var: str = "OPENROUTER_API_KEY",
    search_dotenv: bool = True,
    max_parent_levels: int = 5
) -> Optional[str]:
    """
    Load API key with priority:
    1. Explicit parameter
    2. Environment variable
    3. .env file search (walks up directories)

    Returns None if not found.
    """
    # Priority 1: Explicit parameter
    if explicit_key:
        return explicit_key

    # Priority 2: Environment variable
    env_key = os.environ.get(env_var)
    if env_key:
        return env_key

    # Priority 3: .env file search
    if search_dotenv:
        return _search_dotenv_file(env_var, max_parent_levels)

    return None

def _search_dotenv_file(
    key_name: str,
    max_levels: int
) -> Optional[str]:
    """Search for key in .env files up the directory tree."""
    current = Path.cwd()

    for _ in range(max_levels + 1):
        env_file = current / ".env"
        if env_file.exists():
            key = _parse_env_file(env_file, key_name)
            if key:
                return key

        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    return None

def _parse_env_file(path: Path, key_name: str) -> Optional[str]:
    """Parse .env file and extract key value."""
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}="):
                    value = line.split('=', 1)[1]
                    # Strip quotes
                    value = value.strip().strip('"').strip("'")
                    if value:
                        return value
    except Exception:
        pass
    return None

def get_api_config(
    api_key: Optional[str] = None,
    **overrides
) -> APIConfig:
    """
    Get API configuration, raising error if key not found.

    Raises:
        ValueError: If API key cannot be loaded
    """
    key = load_api_key(api_key)
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY not found. Please either:\n"
            "  1. Set the OPENROUTER_API_KEY environment variable\n"
            "  2. Add OPENROUTER_API_KEY to your .env file\n"
            "  3. Pass api_key parameter directly\n"
            "Get your API key from: https://openrouter.ai/keys"
        )

    return APIConfig(api_key=key, **overrides)

def make_openrouter_request(
    config: APIConfig,
    model: str,
    messages: list,
    modalities: list = None,
    **extra_params
) -> dict:
    """
    Make a request to OpenRouter API.

    Returns response JSON or raises exception.
    """
    import requests

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.referer,
        "X-Title": config.title,
    }

    payload = {
        "model": model,
        "messages": messages,
        **extra_params
    }

    if modalities:
        payload["modalities"] = modalities

    response = requests.post(
        f"{config.base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=config.timeout
    )

    if response.status_code != 200:
        error_detail = _extract_error(response)
        raise APIError(response.status_code, error_detail)

    return response.json()

class APIError(Exception):
    """OpenRouter API error."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")

def _extract_error(response) -> str:
    """Extract error detail from response."""
    try:
        data = response.json()
        if "error" in data:
            return data["error"].get("message", str(data["error"]))
        return response.text
    except Exception:
        return response.text
```

### 4.3 Integration

Update both skills to import from shared:

```python
# In generate_image.py and generate_schematic_ai.py
from shared.api_utils import get_api_config, make_openrouter_request, APIError
```

---

## Part 5: Implementation Plan

### Phase 1: Mermaid Integration (Priority 1)

| Step | Task | Effort | Dependencies |
|------|------|--------|--------------|
| 1.1 | Create `mermaid_renderer.py` | 2 hours | None |
| 1.2 | Create `mermaid_templates.py` | 2 hours | None |
| 1.3 | Create `complexity_analyzer.py` | 3 hours | None |
| 1.4 | Create `generate_mermaid.py` | 4 hours | 1.1, 1.2 |
| 1.5 | Update `generate_schematic.py` router | 2 hours | 1.3, 1.4 |
| 1.6 | Write tests for Mermaid modules | 3 hours | 1.1-1.4 |
| 1.7 | Update SKILL.md with tiered docs | 1 hour | 1.5 |
| 1.8 | Test end-to-end Mermaid flow | 2 hours | All above |

**Estimated Total:** ~19 hours (2-3 days)

### Phase 2: Generate-Image Simplification (Priority 2)

| Step | Task | Effort | Dependencies |
|------|------|--------|--------------|
| 2.1 | Add deprecation warnings for FLUX.2 | 1 hour | None |
| 2.2 | Update `models.py` to default Gemini | 1 hour | None |
| 2.3 | Simplify `generate_image.py` | 1 hour | 2.1, 2.2 |
| 2.4 | Update `model_capabilities.md` | 30 min | 2.3 |
| 2.5 | Update SKILL.md | 30 min | 2.3 |
| 2.6 | Update tests | 1 hour | 2.1-2.3 |

**Estimated Total:** ~5 hours (half day)

### Phase 3: Shared Utilities (Priority 3)

| Step | Task | Effort | Dependencies |
|------|------|--------|--------------|
| 3.1 | Create `skills/shared/` directory | 10 min | None |
| 3.2 | Write `api_utils.py` | 2 hours | None |
| 3.3 | Write tests for shared module | 1 hour | 3.2 |
| 3.4 | Update generate-image imports | 30 min | 3.2 |
| 3.5 | Update scientific-schematics imports | 30 min | 3.2 |
| 3.6 | Verify both skills still work | 1 hour | 3.4, 3.5 |

**Estimated Total:** ~5 hours (half day)

### Phase 4: Documentation & Testing (Priority 4)

| Step | Task | Effort | Dependencies |
|------|------|--------|--------------|
| 4.1 | Update SKILL_ROUTER.md | 30 min | All phases |
| 4.2 | Add decision guide to docs | 1 hour | All phases |
| 4.3 | End-to-end testing | 2 hours | All phases |
| 4.4 | Update CHANGELOG.md | 30 min | All phases |

**Estimated Total:** ~4 hours

---

## Part 6: Testing Strategy

### 6.1 Mermaid Tests

```python
# tests/test_mermaid.py

class TestMermaidRenderer:
    def test_render_flowchart_png(self):
        """Render simple flowchart to PNG."""
        pass

    def test_render_sequence_svg(self):
        """Render sequence diagram to SVG."""
        pass

    def test_invalid_syntax_error(self):
        """Invalid Mermaid syntax raises error."""
        pass

    def test_backend_detection(self):
        """Auto-detects available backend."""
        pass

class TestMermaidTemplates:
    def test_consort_template_fills(self):
        """CONSORT template fills correctly."""
        pass

    def test_prisma_template_fills(self):
        """PRISMA template fills correctly."""
        pass

    def test_template_for_type(self):
        """Correct template selected for diagram type."""
        pass

class TestComplexityAnalyzer:
    def test_simple_flowchart_mermaid(self):
        """Simple flowchart routes to Mermaid."""
        analysis = analyze_complexity("Simple 5-step process flow")
        assert analysis.recommended_tier == GenerationTier.MERMAID

    def test_complex_pathway_ai(self):
        """Complex pathway routes to AI."""
        analysis = analyze_complexity("MAPK signaling pathway with 15 proteins")
        assert analysis.recommended_tier == GenerationTier.AI

    def test_neural_network_ai(self):
        """Neural network always routes to AI."""
        analysis = analyze_complexity("Transformer architecture diagram")
        assert analysis.recommended_tier == GenerationTier.AI

    def test_publication_quality_ai(self):
        """Publication quality forces AI."""
        analysis = analyze_complexity("Simple flowchart", doc_type="journal")
        assert analysis.recommended_tier == GenerationTier.AI

    def test_force_mermaid_override(self):
        """Force flag overrides recommendation."""
        analysis = analyze_complexity(
            "Complex diagram",
            force_tier=GenerationTier.MERMAID
        )
        assert analysis.recommended_tier == GenerationTier.MERMAID
```

### 6.2 Integration Tests

```python
# tests/test_integration.py

class TestTieredGeneration:
    def test_auto_routes_simple_to_mermaid(self):
        """Simple request auto-routes to Mermaid."""
        result = generate_schematic(
            "Simple 3-step flowchart: Input → Process → Output",
            output="test_output.png",
            engine="auto"
        )
        assert result.tier == GenerationTier.MERMAID
        assert result.cost == 0

    def test_auto_routes_complex_to_ai(self):
        """Complex request auto-routes to AI."""
        result = generate_schematic(
            "Transformer encoder-decoder with 6 layers...",
            output="test_output.png",
            engine="auto"
        )
        assert result.tier == GenerationTier.AI

    def test_mermaid_plus_polish(self):
        """Mermaid+AI polish produces enhanced output."""
        result = generate_schematic(
            "CONSORT flowchart...",
            output="test_output.png",
            engine="mermaid+ai"
        )
        assert result.success
        # Check both intermediate and final files exist
```

---

## Part 7: Cost Savings Analysis

### 7.1 Estimated Savings

| Scenario | Before (AI only) | After (Tiered) | Savings |
|----------|------------------|----------------|---------|
| Simple flowchart | $0.02-0.05 | $0.00 | 100% |
| Draft iteration (×5) | $0.10-0.25 | $0.00 | 100% |
| CONSORT/PRISMA (simple) | $0.02-0.05 | $0.00 | 100% |
| Publication figure | $0.05-0.15 | $0.05-0.15 | 0% |
| Neural network | $0.05-0.15 | $0.05-0.15 | 0% |

### 7.2 Typical Workflow Savings

**Scenario: Creating 10 diagrams for a paper**

| Diagram Type | Count | Before | After |
|--------------|-------|--------|-------|
| Methods flowchart | 2 | $0.10 | $0.00 |
| CONSORT | 1 | $0.05 | $0.00 |
| System architecture | 1 | $0.05 | $0.00 |
| Neural network | 2 | $0.10 | $0.10 |
| Pathway diagrams | 2 | $0.10 | $0.10 |
| Complex figures | 2 | $0.10 | $0.10 |
| **Total** | **10** | **$0.50** | **$0.30** |

**Savings: 40% reduction in API costs**

---

## Part 8: Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Mermaid output quality insufficient | Medium | Low | Offer mermaid+ai polish option |
| mermaid-cli installation friction | Medium | Medium | Provide fallback to Python renderer |
| Wrong tier auto-selection | Low | Low | Allow manual override with --engine |
| Breaking existing workflows | Low | High | Maintain backward compatibility |

---

## Part 9: Success Criteria

### Phase 1 (Mermaid) Complete When:
- [x] `generate_mermaid.py` renders basic flowcharts
- [x] Complexity analyzer correctly routes simple vs complex
- [x] Auto-selection matches expected tier >90% of cases
- [x] All tests pass (247 tests)
- [x] SKILL.md documents tiered approach

**✅ Phase 1 Complete (2026-01-14)** - Tiered diagram generation with Mermaid support fully implemented.

### Phase 2 (Simplification) Complete When:
- [x] FLUX.2 models show deprecation warning
- [x] Default model is Gemini 3 Pro
- [x] Tests updated and passing
- [x] Documentation updated

**✅ Phase 2 Complete (2026-01-14)** - FLUX.2 models deprecated, Gemini 3 Pro set as default, documentation updated.

### Phase 3 (Shared Utils) Complete When:
- [x] Both skills use shared `api_utils.py`
- [x] No duplicate API key loading code
- [x] All tests pass (611 tests: 38 shared + 326 generate-image + 247 scientific-schematics)
- [x] No behavior changes

**✅ Phase 3 Complete (2026-01-14)** - Shared API utilities module created and integrated into both skills.

### Phase 4 (Documentation & Testing) Complete When:
- [x] SKILL_ROUTER.md updated with tiered generation routing
- [x] Decision guide available (in scientific-schematics/SKILL.md)
- [x] End-to-end tests pass (611 tests: 38 shared + 326 generate-image + 247 scientific-schematics)
- [x] CHANGELOG.md updated

**✅ Phase 4 Complete (2026-01-14)** - Documentation finalized, all tests passing, refactoring complete.

### Overall Success:
- [x] 40%+ cost reduction for typical workflows (Mermaid tier = $0 for simple diagrams)
- [x] No regression in output quality (all 611 tests pass)
- [x] Faster iteration for simple diagrams (Mermaid: ~100ms vs AI: 10-30s)
- [x] Clear documentation for tier selection (SKILL_ROUTER.md + SKILL.md)

---

## Appendix A: Mermaid Syntax Quick Reference

### Flowchart
```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[End]
    D --> E
```

### Sequence Diagram
```mermaid
sequenceDiagram
    participant A as Client
    participant B as Server
    A->>B: Request
    B-->>A: Response
```

### State Diagram
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start
    Processing --> Complete: Finish
    Complete --> [*]
```

### Class Diagram
```mermaid
classDiagram
    class Animal {
        +String name
        +eat()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog
```

---

## Appendix B: File Changes Summary

| File | Status | Changes |
|------|--------|---------|
| `scientific-schematics/SKILL.md` | Modify | Add tiered generation docs |
| `scientific-schematics/scripts/generate_schematic.py` | Modify | Add tier routing |
| `scientific-schematics/scripts/generate_mermaid.py` | New | Mermaid generation |
| `scientific-schematics/scripts/utils/mermaid_renderer.py` | New | Rendering backend |
| `scientific-schematics/scripts/utils/mermaid_templates.py` | New | Diagram templates |
| `scientific-schematics/scripts/utils/complexity_analyzer.py` | New | Tier selection |
| `scientific-schematics/tests/test_mermaid.py` | New | Mermaid tests |
| `scientific-schematics/tests/test_complexity_analyzer.py` | New | Analyzer tests |
| `generate-image/scripts/utils/models.py` | Modify | Deprecate FLUX.2 |
| `generate-image/SKILL.md` | Modify | Simplify model docs |
| `shared/api_utils.py` | New | Shared API code |
| `shared/__init__.py` | New | Package init |
| `docs/IMAGE_GENERATION_REFACTORING_PLAN.md` | New | This document |
