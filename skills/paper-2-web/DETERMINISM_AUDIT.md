# Determinism Audit: paper-2-web

**Audit Date:** 2025-01-08
**Skill Version:** 2.1.0
**Development Stage:** First draft skill
**Current Determinism:** ~55%
**Target Determinism:** 85%

---

## Executive Summary

The paper-2-web skill (Paper2All) is a well-structured orchestration wrapper around an external GitHub tool, but it operates at approximately **55% determinism** currently. The majority of outputs depend heavily on LLM interpretation of decision trees, user judgment for quality validation, and undefined iterative refinement processes. The skill's primary opportunity is to **convert advisory guidance into enforceable rules** through structured input schemas, automated validation scripts, parameter lookup tables, and cost estimators.

---

## Audit Dimensions

### 1. Input Standardization

| Aspect | Current State | Score | Recommendation |
|--------|--------------|-------|----------------|
| Input format | Directory conventions only | 4/10 | Add YAML schema |
| Component selection | Decision tree prose | 3/10 | Rule-based router |
| Poster dimensions | Manual conference lookup | 2/10 | Venue database |
| Model selection | Vague "$" pricing | 3/10 | Cost estimator |
| Validation | None before execution | 1/10 | Preflight script |

**Proposed Input Schema:**

```yaml
# schemas/transformation_request.yaml
paper_transformation_request:
  required:
    paper_source:
      type: enum[latex_dir, pdf_file]
      path: string
    outputs:
      - type: enum[website, poster, video, all]
        priority: int[1-3]

  conditional:
    poster_config:
      venue: string  # lookup key for standard sizes
      custom_dimensions:
        width_inches: float
        height_inches: float
        orientation: enum[portrait, landscape]

    video_config:
      target_duration: enum[short_2min, abstract_5min, talk_15min, extended_30min]
      style: enum[academic, conference, public, tutorial]
      talking_head: boolean

  optional:
    model_tier: enum[draft, production, premium]
    branding:
      institution: string
      color_scheme: enum[institutional, professional, vibrant, nature, tech]
    budget_limit_usd: float
```

### 2. Output Standardization

| Aspect | Current State | Score | Recommendation |
|--------|--------------|-------|----------------|
| Directory structure | Well-defined | 9/10 | Maintain |
| Quality metrics | Manual checklists | 4/10 | Automated validation |
| Deployment checklist | Markdown only | 5/10 | Executable script |
| Version tracking | None | 2/10 | Hash manifests |

### 3. Deterministic vs Stochastic Components

**Currently Stochastic (LLM-dependent):**
- Content extraction and summarization from papers
- Layout design decisions
- Script/narration generation for videos
- Section organization and content prioritization
- Visual design choices (color schemes, typography)
- Figure placement and sizing decisions
- Quality assessment (aesthetic, informativeness)

**Currently Deterministic (code-based):**
- File organization and directory structure
- LaTeX/PDF parsing (Paper2All library)
- Image processing and conversion
- QR code generation
- Video rendering/assembly
- PDF generation at specific DPI
- Poster dimension calculations
- API rate limiting
- Batch processing orchestration

### 4. Reproducibility Assessment

**Current Rating: LOW-MEDIUM (4/10)**

**Factors Reducing Reproducibility:**
1. Model drift: No version pinning; "GPT-4" behavior changes over time
2. Undefined iteration: "Iterative refinement" with no termination criteria
3. Subjective quality: "Aesthetic metrics" with no anchoring
4. Prompt variance: Same request interpreted differently
5. External dependency: Paper2All tool version not locked
6. No seed control for random elements

**Factors Supporting Reproducibility:**
1. Directory structure is deterministic
2. Technical output specs (DPI, resolution) well-defined
3. Workflow stages clearly delineated
4. Best practices provide consistent guidance

---

## Implementation Plan

### Phase 1: Quick Wins (P0) - 1-2 days

#### 1.1 Structured Input Schema

```yaml
# data/transformation_request_schema.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
type: object
required: [paper_source, outputs]
properties:
  paper_source:
    type: object
    required: [type, path]
    properties:
      type:
        enum: [latex_dir, pdf_file]
      path:
        type: string
  outputs:
    type: array
    items:
      type: object
      required: [type]
      properties:
        type:
          enum: [website, poster, video]
        priority:
          type: integer
          minimum: 1
          maximum: 3
```

#### 1.2 Venue Poster Size Lookup

```python
# lib/venue_database.py
VENUE_POSTER_SPECS = {
    # Major ML/AI conferences
    "neurips": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "icml": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "iclr": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "cvpr": {"width": 60, "height": 40, "orientation": "landscape", "dpi": 300},
    "iccv": {"width": 60, "height": 40, "orientation": "landscape", "dpi": 300},
    "aaai": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "acl": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "emnlp": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},

    # Biology/Medical conferences
    "ismb": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "recomb": {"width": 36, "height": 48, "orientation": "portrait", "dpi": 300},
    "ashg": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "cosyne": {"width": 36, "height": 48, "orientation": "portrait", "dpi": 300},
    "sfn": {"width": 45, "height": 45, "orientation": "square", "dpi": 300},

    # Physics/Chemistry
    "aps_march": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
    "acs_national": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},

    # International standards
    "a0_portrait": {"width": 33.1, "height": 46.8, "orientation": "portrait", "dpi": 300},
    "a0_landscape": {"width": 46.8, "height": 33.1, "orientation": "landscape", "dpi": 300},
    "a1_portrait": {"width": 23.4, "height": 33.1, "orientation": "portrait", "dpi": 300},

    # Default
    "standard": {"width": 48, "height": 36, "orientation": "landscape", "dpi": 300},
}

def get_poster_specs(venue: str) -> dict:
    """Deterministic poster dimensions from venue name."""
    venue_key = venue.lower().replace(" ", "_").replace("-", "_")
    return VENUE_POSTER_SPECS.get(venue_key, VENUE_POSTER_SPECS["standard"])

def list_supported_venues() -> list[str]:
    """List all venues with known poster specifications."""
    return sorted([v for v in VENUE_POSTER_SPECS.keys() if v not in ["standard"]])
```

#### 1.3 Automated Link Checker

```python
# scripts/validate_links.py
import asyncio
import aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class LinkCheckResult:
    url: str
    status: int | None
    valid: bool
    error: str | None

async def check_link(session: aiohttp.ClientSession, url: str) -> LinkCheckResult:
    """Check if a single URL is accessible."""
    try:
        async with session.head(url, timeout=10, allow_redirects=True) as response:
            return LinkCheckResult(
                url=url,
                status=response.status,
                valid=response.status < 400,
                error=None
            )
    except Exception as e:
        return LinkCheckResult(url=url, status=None, valid=False, error=str(e))

async def validate_website_links(website_dir: Path) -> list[LinkCheckResult]:
    """Validate all links in generated website."""
    html_files = list(website_dir.glob("**/*.html"))
    all_links = set()

    for html_file in html_files:
        soup = BeautifulSoup(html_file.read_text(), 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('http://', 'https://')):
                all_links.add(href)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[check_link(session, url) for url in all_links])

    return results

def print_link_report(results: list[LinkCheckResult]) -> bool:
    """Print link validation report. Returns True if all valid."""
    valid = [r for r in results if r.valid]
    invalid = [r for r in results if not r.valid]

    print(f"\nLink Validation Report")
    print(f"=" * 50)
    print(f"Total links checked: {len(results)}")
    print(f"Valid: {len(valid)}")
    print(f"Invalid: {len(invalid)}")

    if invalid:
        print(f"\nBroken Links:")
        for r in invalid:
            print(f"  - {r.url}")
            print(f"    Status: {r.status or 'N/A'}, Error: {r.error or 'N/A'}")

    return len(invalid) == 0
```

### Phase 2: Core Infrastructure (P1) - 1 week

#### 2.1 Cost Estimator Module

```python
# lib/cost_estimator.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class CostEstimate:
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    confidence: Literal["high", "medium", "low"]
    breakdown: dict[str, float]

# Token costs per 1K tokens (update as pricing changes)
MODEL_COSTS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4.1": {"input": 0.04, "output": 0.08},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

# Model tier mapping
MODEL_TIERS = {
    "draft": "gpt-3.5-turbo",
    "production": "gpt-4",
    "premium": "gpt-4.1",
}

# Base token estimates per component (empirically derived)
COMPONENT_BASE_TOKENS = {
    "website": {"input": 8000, "output": 15000},
    "poster": {"input": 6000, "output": 10000},
    "video": {"input": 12000, "output": 20000},
}

# Paper complexity multipliers
def get_complexity_multiplier(paper_pages: int) -> float:
    """Deterministic multiplier based on paper length."""
    if paper_pages <= 8:
        return 1.0
    elif paper_pages <= 15:
        return 1.5
    elif paper_pages <= 30:
        return 2.5
    else:
        return 4.0

def estimate_cost(
    paper_pages: int,
    components: list[str],
    model_tier: str = "production"
) -> CostEstimate:
    """Deterministic cost estimation."""
    model = MODEL_TIERS.get(model_tier, "gpt-4")
    multiplier = get_complexity_multiplier(paper_pages)

    breakdown = {}
    total_input = 0
    total_output = 0

    for component in components:
        if component in COMPONENT_BASE_TOKENS:
            base = COMPONENT_BASE_TOKENS[component]
            comp_input = int(base["input"] * multiplier)
            comp_output = int(base["output"] * multiplier)
            total_input += comp_input
            total_output += comp_output

            costs = MODEL_COSTS[model]
            comp_cost = (comp_input / 1000 * costs["input"] +
                        comp_output / 1000 * costs["output"])
            breakdown[component] = round(comp_cost, 2)

    costs = MODEL_COSTS[model]
    total_cost = (total_input / 1000 * costs["input"] +
                  total_output / 1000 * costs["output"])

    return CostEstimate(
        model=model,
        input_tokens=total_input,
        output_tokens=total_output,
        estimated_cost_usd=round(total_cost, 2),
        confidence="medium",
        breakdown=breakdown
    )
```

#### 2.2 Component Router

```python
# lib/component_router.py
from dataclasses import dataclass
from enum import Enum

class UseCase(Enum):
    CONFERENCE_ORAL = "conference_oral"
    CONFERENCE_POSTER = "conference_poster"
    JOURNAL_PUBLICATION = "journal_publication"
    PREPRINT_PROMOTION = "preprint_promotion"
    LAB_WEBSITE = "lab_website"
    SOCIAL_MEDIA = "social_media"
    VIDEO_ABSTRACT = "video_abstract"

@dataclass
class ComponentRecommendation:
    website: bool
    poster: bool
    video: bool
    video_type: str | None
    priority_order: list[str]
    rationale: str

# Deterministic routing table
COMPONENT_ROUTING: dict[UseCase, ComponentRecommendation] = {
    UseCase.CONFERENCE_ORAL: ComponentRecommendation(
        website=False, poster=False, video=True,
        video_type="talk_15min",
        priority_order=["video"],
        rationale="Oral presentations need video; website/poster optional"
    ),
    UseCase.CONFERENCE_POSTER: ComponentRecommendation(
        website=False, poster=True, video=False,
        video_type=None,
        priority_order=["poster"],
        rationale="Poster session requires print-ready poster"
    ),
    UseCase.JOURNAL_PUBLICATION: ComponentRecommendation(
        website=True, poster=False, video=False,
        video_type=None,
        priority_order=["website"],
        rationale="Journal papers benefit from permanent web presence"
    ),
    UseCase.PREPRINT_PROMOTION: ComponentRecommendation(
        website=True, poster=False, video=True,
        video_type="abstract_5min",
        priority_order=["website", "video"],
        rationale="Preprints need visibility via website and video"
    ),
    UseCase.LAB_WEBSITE: ComponentRecommendation(
        website=True, poster=False, video=False,
        video_type=None,
        priority_order=["website"],
        rationale="Lab portfolio needs only website"
    ),
    UseCase.SOCIAL_MEDIA: ComponentRecommendation(
        website=False, poster=False, video=True,
        video_type="short_2min",
        priority_order=["video"],
        rationale="Social media needs short, engaging video"
    ),
    UseCase.VIDEO_ABSTRACT: ComponentRecommendation(
        website=False, poster=False, video=True,
        video_type="abstract_5min",
        priority_order=["video"],
        rationale="Video abstract for journal submission"
    ),
}

def route_components(use_case: UseCase) -> ComponentRecommendation:
    """Deterministic component selection based on use case."""
    return COMPONENT_ROUTING[use_case]

def infer_use_case(keywords: list[str]) -> UseCase | None:
    """Attempt to infer use case from keywords."""
    keyword_mapping = {
        "oral": UseCase.CONFERENCE_ORAL,
        "talk": UseCase.CONFERENCE_ORAL,
        "presentation": UseCase.CONFERENCE_ORAL,
        "poster": UseCase.CONFERENCE_POSTER,
        "poster session": UseCase.CONFERENCE_POSTER,
        "journal": UseCase.JOURNAL_PUBLICATION,
        "publication": UseCase.JOURNAL_PUBLICATION,
        "preprint": UseCase.PREPRINT_PROMOTION,
        "arxiv": UseCase.PREPRINT_PROMOTION,
        "biorxiv": UseCase.PREPRINT_PROMOTION,
        "lab": UseCase.LAB_WEBSITE,
        "portfolio": UseCase.LAB_WEBSITE,
        "twitter": UseCase.SOCIAL_MEDIA,
        "social": UseCase.SOCIAL_MEDIA,
        "video abstract": UseCase.VIDEO_ABSTRACT,
    }

    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in keyword_mapping:
            return keyword_mapping[keyword_lower]

    return None
```

#### 2.3 Preflight Validation Script

```python
# scripts/preflight_check.py
from pathlib import Path
from dataclasses import dataclass, field
import subprocess
import os

@dataclass
class PreflightResult:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cost_estimate: float | None = None

def run_preflight_checks(
    input_dir: Path,
    components: list[str],
    model_tier: str = "production"
) -> PreflightResult:
    """Deterministic pre-flight validation before pipeline execution."""

    result = PreflightResult(passed=True)

    # Check 1: Input files exist
    tex_files = list(input_dir.glob("*.tex"))
    pdf_files = list(input_dir.glob("*.pdf"))
    result.checks["input_exists"] = len(tex_files) > 0 or len(pdf_files) > 0
    if not result.checks["input_exists"]:
        result.errors.append(f"No .tex or .pdf files found in {input_dir}")
        result.passed = False

    # Check 2: LaTeX compiles (if LaTeX input)
    if tex_files:
        main_tex = tex_files[0]
        try:
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
                capture_output=True, timeout=120, cwd=input_dir
            )
            result.checks["latex_compiles"] = proc.returncode == 0
            if not result.checks["latex_compiles"]:
                result.warnings.append("LaTeX compilation had errors (may still work)")
        except FileNotFoundError:
            result.checks["latex_compiles"] = None
            result.warnings.append("pdflatex not found; skipping compilation check")
        except subprocess.TimeoutExpired:
            result.checks["latex_compiles"] = False
            result.errors.append("LaTeX compilation timed out after 120s")

    # Check 3: Dependencies installed
    result.checks["libreoffice"] = subprocess.run(
        ["which", "libreoffice"], capture_output=True
    ).returncode == 0
    result.checks["poppler"] = subprocess.run(
        ["which", "pdftoppm"], capture_output=True
    ).returncode == 0

    if not result.checks["libreoffice"]:
        result.errors.append("LibreOffice not found in PATH")
        result.passed = False
    if not result.checks["poppler"]:
        result.errors.append("Poppler utilities not found")
        result.passed = False

    # Check 4: Figure resolution (for poster)
    if "poster" in components:
        figures_dir = input_dir / "figures"
        if figures_dir.exists():
            try:
                from PIL import Image
                for img in figures_dir.glob("*.png"):
                    with Image.open(img) as im:
                        min_width = 6 * 300  # 1800 pixels for 6" at 300 DPI
                        if im.width < min_width:
                            result.warnings.append(
                                f"{img.name}: {im.width}px width may be low for poster"
                            )
            except ImportError:
                result.warnings.append("PIL not installed; skipping resolution check")

    # Check 5: API keys configured
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    result.checks["api_key"] = has_openai or has_openrouter
    if not result.checks["api_key"]:
        result.errors.append("No API key configured (OPENAI_API_KEY or OPENROUTER_API_KEY)")
        result.passed = False

    # Check 6: Cost estimation
    try:
        from lib.cost_estimator import estimate_cost
        # Estimate paper pages from tex file length
        if tex_files:
            content = tex_files[0].read_text()
            estimated_pages = max(1, len(content) // 4000)  # ~4000 chars per page
        else:
            estimated_pages = 10  # Default estimate for PDF

        estimate = estimate_cost(estimated_pages, components, model_tier)
        result.cost_estimate = estimate.estimated_cost_usd
    except Exception:
        result.warnings.append("Could not estimate cost")

    return result

def print_preflight_report(result: PreflightResult) -> None:
    """Print formatted preflight report."""
    print("\n" + "=" * 60)
    print("PREFLIGHT CHECK REPORT")
    print("=" * 60)

    for check, passed in result.checks.items():
        status = "PASS" if passed else ("SKIP" if passed is None else "FAIL")
        symbol = "[OK]" if passed else ("[--]" if passed is None else "[!!]")
        print(f"  {symbol} {check}")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  - {e}")

    if result.cost_estimate:
        print(f"\nEstimated cost: ${result.cost_estimate:.2f}")

    print("\n" + "-" * 60)
    print(f"READY TO PROCEED: {'YES' if result.passed else 'NO'}")
    print("=" * 60)
```

### Phase 3: Advanced (P2) - 2+ weeks

#### 3.1 Reproducibility Manifest System

```python
# lib/reproducibility.py
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib
import json
import sys

@dataclass
class ReproducibilityConfig:
    """Configuration for reproducible runs."""
    model_version: str = "gpt-4-0613"
    temperature: float = 0.0
    seed: int | None = 42
    max_refinement_iterations: int = 3
    refinement_threshold: float = 0.85
    paper2all_version: str = "1.2.0"
    paper2all_commit: str | None = None

@dataclass
class ReproducibilityManifest:
    """Manifest for reproducing outputs."""
    config: dict
    output_hashes: dict[str, str]
    timestamp: str
    environment: dict
    input_hash: str

def hash_file(path: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def hash_directory(dir_path: Path) -> str:
    """Compute hash of directory contents."""
    sha256 = hashlib.sha256()
    for path in sorted(dir_path.rglob('*')):
        if path.is_file():
            sha256.update(path.name.encode())
            sha256.update(hash_file(path).encode())
    return sha256.hexdigest()

def generate_manifest(
    config: ReproducibilityConfig,
    input_dir: Path,
    output_dir: Path
) -> ReproducibilityManifest:
    """Generate manifest for reproducing outputs."""

    output_hashes = {}
    for subdir in ["website", "poster", "video"]:
        subpath = output_dir / subdir
        if subpath.exists():
            output_hashes[subdir] = hash_directory(subpath)

    return ReproducibilityManifest(
        config=asdict(config),
        output_hashes=output_hashes,
        timestamp=datetime.utcnow().isoformat() + "Z",
        environment={
            "python_version": sys.version,
            "platform": sys.platform,
        },
        input_hash=hash_directory(input_dir)
    )

def save_manifest(manifest: ReproducibilityManifest, output_path: Path) -> None:
    """Save manifest to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(asdict(manifest), f, indent=2)

def verify_reproduction(
    manifest_path: Path,
    output_dir: Path
) -> tuple[bool, list[str]]:
    """Verify outputs match manifest."""
    with open(manifest_path) as f:
        manifest = json.load(f)

    mismatches = []
    for component, expected_hash in manifest["output_hashes"].items():
        subpath = output_dir / component
        if subpath.exists():
            actual_hash = hash_directory(subpath)
            if actual_hash != expected_hash:
                mismatches.append(f"{component}: hash mismatch")
        else:
            mismatches.append(f"{component}: directory missing")

    return len(mismatches) == 0, mismatches
```

#### 3.2 Automated Quality Scorer

```python
# lib/quality_scorer.py
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

@dataclass
class QualityScore:
    component: str
    metric: str
    value: float
    threshold: float
    passed: bool
    severity: Literal["critical", "major", "minor"]

@dataclass
class QualityReport:
    component: str
    overall_score: float
    passed: bool
    scores: list[QualityScore]

def score_website(output_dir: Path) -> QualityReport:
    """Score website quality with deterministic metrics."""
    website_dir = output_dir / "website"
    scores = []

    # Metric 1: All HTML files valid
    html_files = list(website_dir.glob("**/*.html"))
    html_valid = all(validate_html(f) for f in html_files)
    scores.append(QualityScore(
        component="website", metric="html_valid",
        value=1.0 if html_valid else 0.0, threshold=1.0,
        passed=html_valid, severity="critical"
    ))

    # Metric 2: All images have alt text
    # ... additional metrics

    critical_passed = all(s.passed for s in scores if s.severity == "critical")
    overall = sum(s.value for s in scores) / len(scores) if scores else 0

    return QualityReport(
        component="website",
        overall_score=overall,
        passed=critical_passed and overall >= 0.7,
        scores=scores
    )
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Input interpretation variance | High | Low | Same request produces same component selection |
| Cost estimation accuracy | N/A | ±20% | Compare estimate to actual API costs |
| Quality check automation | 10% | 80% | Automated checks / total checks |
| Reproducibility | Low | High | Hash match rate for repeated runs |
| Preflight catch rate | 0% | 90% | Errors caught before LLM calls |

---

## File Structure After Implementation

```
skills/paper-2-web/
├── SKILL.md                    # Main skill document
├── DETERMINISM_AUDIT.md        # This audit document
├── schemas/
│   └── transformation_request.yaml  # Input schema
├── data/
│   └── venue_poster_specs.yaml      # Venue database
├── lib/
│   ├── __init__.py
│   ├── cost_estimator.py       # Cost calculation
│   ├── component_router.py     # Use case routing
│   ├── venue_database.py       # Poster specs lookup
│   ├── quality_scorer.py       # Automated scoring
│   └── reproducibility.py      # Manifest generation
├── scripts/
│   ├── preflight_check.py      # Pre-execution validation
│   └── validate_links.py       # Link checker
└── references/
    └── ... (existing)
```

---

## Changelog

- **2025-01-08**: Initial determinism audit completed
  - Baseline assessment: 55% deterministic
  - Identified 12 improvement opportunities
  - Created 3-phase implementation plan
  - Target: 85% determinism
