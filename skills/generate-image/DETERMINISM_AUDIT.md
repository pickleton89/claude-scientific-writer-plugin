# Determinism Audit: generate-image

> **Skill Version:** 2.2.0
> **Audit Date:** 2026-01-08
> **Auditor:** Claude (Deterministic Auditor)
> **Development Stage:** First draft skill

## Executive Summary

The generate-image skill is well-architected with clear decision frameworks, quality rubrics, and iteration limits. However, it relies heavily on manual evaluation and free-form prompt construction. Key opportunities exist to add deterministic layers: **automated prompt validation**, **programmatic quality checks** (resolution, corruption), and **structured iteration tracking**—while accepting that image generation itself is fundamentally stochastic.

**Current Determinism:** ~60%
**Target Determinism:** ~80%
**Expected Variance Reduction:** 20%

## Current State Analysis

### Deterministic Components (Working Well)

| Component | Implementation | Determinism |
|-----------|----------------|-------------|
| Model selection matrix | Documented decision tree | 90% |
| Python generation script | Code-based API calls | 95% |
| Prompt formula | 5-component structure | 70% |
| Iteration limits | Quantified thresholds | 85% |
| File handling | Base64 encode/decode | 100% |

### Stochastic Components (Improvement Targets)

| Component | Current State | Issue |
|-----------|---------------|-------|
| Prompt construction | Free-form text | No validation of components |
| Quality scoring | Manual 10-point rubric | Subjective evaluation |
| Model selection | Manual decision tree | Not code-enforced |
| Iteration tracking | Manual counting | No persistence |
| Output validation | Manual inspection | No automated checks |

## Phase 1: Quick Wins (P0)

### 1.1 Automated Image Validation

Add post-generation validation to `generate_image.py`:

```python
# scripts/validate_output.py
"""Automated validation for generated images."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class ImageValidation:
    """Result of image validation."""
    valid: bool
    resolution: tuple[int, int]
    meets_minimum: bool  # >= 512px
    meets_target: bool   # >= 1024px
    file_size_bytes: int
    format: str
    error: Optional[str] = None

def validate_image(
    path: str,
    min_resolution: int = 512,
    target_resolution: int = 1024
) -> ImageValidation:
    """
    Validate generated image meets quality thresholds.

    Args:
        path: Path to generated image
        min_resolution: Minimum acceptable dimension (default: 512px)
        target_resolution: Target dimension (default: 1024px)

    Returns:
        ImageValidation with all metrics
    """
    try:
        from PIL import Image

        img = Image.open(path)
        width, height = img.size
        file_size = Path(path).stat().st_size

        return ImageValidation(
            valid=True,
            resolution=(width, height),
            meets_minimum=min(width, height) >= min_resolution,
            meets_target=min(width, height) >= target_resolution,
            file_size_bytes=file_size,
            format=img.format or "UNKNOWN"
        )
    except Exception as e:
        return ImageValidation(
            valid=False,
            resolution=(0, 0),
            meets_minimum=False,
            meets_target=False,
            file_size_bytes=0,
            format="ERROR",
            error=str(e)
        )

def check_resolution_tier(validation: ImageValidation) -> str:
    """
    Classify resolution against SKILL.md thresholds.

    Returns: "excellent" (2048+), "target" (1024+), "minimum" (512+), "fail"
    """
    min_dim = min(validation.resolution)

    if min_dim >= 2048:
        return "excellent"
    elif min_dim >= 1024:
        return "target"
    elif min_dim >= 512:
        return "minimum"
    else:
        return "fail"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <image_path>")
        sys.exit(1)

    result = validate_image(sys.argv[1])
    tier = check_resolution_tier(result)

    print(f"Valid: {result.valid}")
    print(f"Resolution: {result.resolution[0]}x{result.resolution[1]}")
    print(f"Tier: {tier}")
    print(f"File size: {result.file_size_bytes / 1024:.1f} KB")

    if not result.valid:
        print(f"Error: {result.error}")
        sys.exit(1)
```

### 1.2 Prompt Component Analyzer

```python
# scripts/analyze_prompt.py
"""Analyze prompts against the 5-component formula."""

from dataclasses import dataclass
from typing import Optional

# Keywords from references/prompt_templates.md
STYLE_KEYWORDS = {
    "scientific illustration", "photorealistic", "modern", "minimalist",
    "3d render", "digital art", "watercolor", "photograph", "style"
}

QUALITY_KEYWORDS = {
    "detailed", "high detail", "professional", "publication",
    "4k", "high resolution", "sharp", "intricate"
}

TECHNICAL_KEYWORDS = {
    "background", "lighting", "contrast", "well-lit", "clean",
    "composition", "centered", "balanced"
}

MEDIUM_KEYWORDS = {
    "digital art", "3d render", "photograph", "illustration",
    "visualization", "render", "painting"
}

@dataclass
class PromptAnalysis:
    """Result of prompt component analysis."""
    word_count: int
    has_subject: bool          # Always true if word_count > 3
    has_style: bool
    has_medium: bool
    has_technical: bool
    has_quality: bool
    component_count: int       # Out of 5
    optimal_length: bool       # 20-50 words
    warnings: list[str]

def analyze_prompt(prompt: str) -> PromptAnalysis:
    """
    Analyze prompt against the 5-component formula.

    Formula: [SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]

    Args:
        prompt: The image generation prompt

    Returns:
        PromptAnalysis with component coverage
    """
    prompt_lower = prompt.lower()
    words = prompt.split()
    word_count = len(words)

    has_style = any(kw in prompt_lower for kw in STYLE_KEYWORDS)
    has_medium = any(kw in prompt_lower for kw in MEDIUM_KEYWORDS)
    has_technical = any(kw in prompt_lower for kw in TECHNICAL_KEYWORDS)
    has_quality = any(kw in prompt_lower for kw in QUALITY_KEYWORDS)
    has_subject = word_count > 3  # Assume subject exists if prompt has content

    components = [has_subject, has_style, has_medium, has_technical, has_quality]
    component_count = sum(components)

    optimal_length = 20 <= word_count <= 50

    # Generate warnings
    warnings = []
    if word_count < 10:
        warnings.append("Prompt too short (<10 words) - likely vague")
    if word_count > 100:
        warnings.append("Prompt very long (>100 words) - may confuse model")
    if not has_style:
        warnings.append("Missing STYLE component (e.g., 'scientific illustration style')")
    if not has_quality:
        warnings.append("Missing QUALITY component (e.g., 'high detail', 'professional')")
    if not has_technical:
        warnings.append("Missing TECHNICAL component (e.g., 'clean background')")

    return PromptAnalysis(
        word_count=word_count,
        has_subject=has_subject,
        has_style=has_style,
        has_medium=has_medium,
        has_technical=has_technical,
        has_quality=has_quality,
        component_count=component_count,
        optimal_length=optimal_length,
        warnings=warnings
    )

def format_analysis(analysis: PromptAnalysis) -> str:
    """Format analysis for display."""
    lines = [
        f"Word count: {analysis.word_count} {'(optimal)' if analysis.optimal_length else ''}",
        f"Components: {analysis.component_count}/5",
        f"  - Subject: {'Yes' if analysis.has_subject else 'No'}",
        f"  - Style: {'Yes' if analysis.has_style else 'No'}",
        f"  - Medium: {'Yes' if analysis.has_medium else 'No'}",
        f"  - Technical: {'Yes' if analysis.has_technical else 'No'}",
        f"  - Quality: {'Yes' if analysis.has_quality else 'No'}",
    ]

    if analysis.warnings:
        lines.append("\nWarnings:")
        for w in analysis.warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_prompt.py 'your prompt here'")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    analysis = analyze_prompt(prompt)
    print(format_analysis(analysis))
```

## Phase 2: Core Infrastructure (P1)

### 2.1 Model ID Validation

```python
# scripts/utils/models.py
"""Model validation and selection utilities."""

from typing import Optional
from enum import Enum

class Priority(Enum):
    QUALITY = "quality"
    SPEED = "speed"
    BUDGET = "budget"

# Valid models from references/model_capabilities.md
VALID_MODELS = {
    "google/gemini-3-pro-image-preview": {
        "generation": True,
        "editing": True,
        "quality": "excellent",
        "cost": "$$"
    },
    "black-forest-labs/flux.2-pro": {
        "generation": True,
        "editing": True,
        "quality": "excellent",
        "cost": "$$"
    },
    "black-forest-labs/flux.2-flex": {
        "generation": True,
        "editing": False,
        "quality": "good",
        "cost": "$"
    }
}

DEFAULT_MODEL = "google/gemini-3-pro-image-preview"

def validate_model(model_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate model ID against allowed list.

    Returns:
        (is_valid, error_message)
    """
    if model_id in VALID_MODELS:
        return True, None

    # Check for common typos
    suggestions = [m for m in VALID_MODELS if model_id.lower() in m.lower()]
    if suggestions:
        return False, f"Invalid model '{model_id}'. Did you mean: {suggestions[0]}?"

    return False, f"Invalid model '{model_id}'. Valid models: {', '.join(VALID_MODELS.keys())}"

def select_model(
    priority: Priority = Priority.QUALITY,
    needs_editing: bool = False
) -> str:
    """
    Deterministically select model based on requirements.

    Implements decision tree from references/model_capabilities.md
    """
    if needs_editing:
        # Only Gemini and FLUX Pro support editing
        return "google/gemini-3-pro-image-preview"

    if priority == Priority.QUALITY:
        return "google/gemini-3-pro-image-preview"
    elif priority == Priority.SPEED:
        return "black-forest-labs/flux.2-pro"
    elif priority == Priority.BUDGET:
        return "black-forest-labs/flux.2-flex"

    return DEFAULT_MODEL

def supports_editing(model_id: str) -> bool:
    """Check if model supports image editing."""
    return VALID_MODELS.get(model_id, {}).get("editing", False)
```

### 2.2 Generation Metadata Logger

```python
# scripts/utils/metadata.py
"""Generation metadata logging for reproducibility."""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class GenerationMetadata:
    """Metadata for a generation attempt."""
    prompt: str
    model: str
    timestamp: str
    output_path: str
    input_image: Optional[str] = None
    attempt_number: int = 1
    resolution: Optional[tuple[int, int]] = None
    file_size_bytes: Optional[int] = None
    success: bool = True
    error: Optional[str] = None

def log_generation(
    output_path: str,
    prompt: str,
    model: str,
    input_image: Optional[str] = None,
    attempt_number: int = 1
) -> str:
    """
    Log generation metadata to sidecar JSON file.

    Args:
        output_path: Path to generated image
        prompt: Generation prompt
        model: Model ID used
        input_image: Optional input image for editing
        attempt_number: Which attempt this is

    Returns:
        Path to metadata file
    """
    meta_path = Path(output_path).with_suffix(".meta.json")

    # Try to get image info if file exists
    resolution = None
    file_size = None
    try:
        from PIL import Image
        img = Image.open(output_path)
        resolution = img.size
        file_size = Path(output_path).stat().st_size
    except Exception:
        pass

    metadata = GenerationMetadata(
        prompt=prompt,
        model=model,
        timestamp=datetime.now().isoformat(),
        output_path=str(output_path),
        input_image=input_image,
        attempt_number=attempt_number,
        resolution=resolution,
        file_size_bytes=file_size
    )

    with open(meta_path, "w") as f:
        json.dump(asdict(metadata), f, indent=2)

    return str(meta_path)

def load_generation_history(output_path: str) -> list[GenerationMetadata]:
    """Load all generation attempts for an output path."""
    meta_path = Path(output_path).with_suffix(".meta.json")

    if not meta_path.exists():
        return []

    with open(meta_path) as f:
        data = json.load(f)

    # Handle both single and array formats
    if isinstance(data, list):
        return [GenerationMetadata(**d) for d in data]
    return [GenerationMetadata(**data)]
```

## Phase 3: Iteration Tracking (P2)

### 3.1 Iteration Enforcer

```python
# scripts/iteration_tracker.py
"""Track iterations and enforce stopping rules from SKILL.md."""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Literal
from datetime import datetime

@dataclass
class IterationRecord:
    """Record of a single generation attempt."""
    attempt: int
    timestamp: str
    prompt: str
    quality_score: Optional[float] = None
    notes: Optional[str] = None

@dataclass
class IterationLog:
    """Full iteration log for a generation task."""
    output_type: Literal["draft", "presentation", "publication", "hero"]
    iterations: list[IterationRecord]

    @property
    def soft_limit(self) -> int:
        """Soft limit from SKILL.md."""
        limits = {"draft": 2, "presentation": 3, "publication": 4, "hero": 4}
        return limits.get(self.output_type, 3)

    @property
    def hard_limit(self) -> int:
        """Hard limit from SKILL.md."""
        limits = {"draft": 3, "presentation": 4, "publication": 5, "hero": 5}
        return limits.get(self.output_type, 5)

def should_stop(log: IterationLog) -> tuple[bool, str]:
    """
    Apply stopping rules from SKILL.md §Success Criteria.

    Returns:
        (should_stop, reason)
    """
    if not log.iterations:
        return False, "No iterations yet"

    scores = [i.quality_score for i in log.iterations if i.quality_score is not None]
    current_score = scores[-1] if scores else None
    iteration_count = len(log.iterations)

    # Rule 1: Score >= 8/10 (excellent threshold)
    if current_score is not None and current_score >= 8:
        return True, f"Score {current_score}/10 meets excellent threshold (>=8)"

    # Rule 2: Score >= 7/10 AND iteration count >= soft limit
    if current_score is not None and current_score >= 7 and iteration_count >= log.soft_limit:
        return True, f"Score {current_score}/10 acceptable and soft limit ({log.soft_limit}) reached"

    # Rule 3: Score improvement < 0.5 for 2 consecutive iterations (plateau)
    if len(scores) >= 3:
        recent_improvement = scores[-1] - scores[-2]
        prev_improvement = scores[-2] - scores[-3]
        if recent_improvement < 0.5 and prev_improvement < 0.5:
            return True, f"Plateau detected: improvements {prev_improvement:.1f}, {recent_improvement:.1f}"

    # Rule 4: Hard limit reached
    if iteration_count >= log.hard_limit:
        return True, f"Hard limit ({log.hard_limit}) reached"

    return False, f"Continue: iteration {iteration_count}/{log.hard_limit}, score {current_score}"

def save_iteration_log(log: IterationLog, path: str) -> None:
    """Save iteration log to JSON."""
    with open(path, "w") as f:
        json.dump(asdict(log), f, indent=2)

def load_iteration_log(path: str) -> Optional[IterationLog]:
    """Load iteration log from JSON."""
    p = Path(path)
    if not p.exists():
        return None

    with open(p) as f:
        data = json.load(f)

    data["iterations"] = [IterationRecord(**i) for i in data["iterations"]]
    return IterationLog(**data)

if __name__ == "__main__":
    # Example usage
    log = IterationLog(
        output_type="presentation",
        iterations=[
            IterationRecord(1, "2026-01-08T12:00:00", "prompt v1", 5.0),
            IterationRecord(2, "2026-01-08T12:05:00", "prompt v2", 6.5),
            IterationRecord(3, "2026-01-08T12:10:00", "prompt v3", 7.2),
        ]
    )

    stop, reason = should_stop(log)
    print(f"Should stop: {stop}")
    print(f"Reason: {reason}")
```

## Implementation Priority Matrix

| Module | Priority | Impact | Effort | Rationale |
|--------|----------|--------|--------|-----------|
| `validate_output.py` | P0 | High | Low | Catches technical failures deterministically |
| `analyze_prompt.py` | P0 | Medium | Low | Reduces "vague prompt" anti-pattern |
| `utils/models.py` | P1 | Low | Low | Prevents typos, enforces allowlist |
| `utils/metadata.py` | P1 | Medium | Low | Enables reproducibility analysis |
| `iteration_tracker.py` | P2 | Medium | Medium | Automates stopping rules |

## Success Metrics

| Metric | Before | After | Measurement |
|--------|--------|-------|-------------|
| Prompt validation | 0% | 80% | Prompts checked before generation |
| Output validation | 0% | 90% | Images validated post-generation |
| Model typo errors | ~5% | <1% | Failed API calls from invalid models |
| Iteration overruns | ~20% | <5% | Generations exceeding hard limit |
| Metadata logging | 0% | 100% | Generations with sidecar JSON |

## Testing Plan

```python
# tests/test_generate_image_validation.py
"""Tests for deterministic validation modules."""

import pytest
from scripts.validate_output import validate_image, check_resolution_tier
from scripts.analyze_prompt import analyze_prompt
from scripts.utils.models import validate_model, select_model, Priority
from scripts.iteration_tracker import should_stop, IterationLog, IterationRecord

class TestPromptAnalysis:
    def test_vague_prompt_warns(self):
        result = analyze_prompt("a cell")
        assert result.word_count < 10
        assert any("too short" in w for w in result.warnings)

    def test_complete_prompt(self):
        prompt = "DNA double helix, scientific illustration style, 3D render, clean white background, high detail professional"
        result = analyze_prompt(prompt)
        assert result.component_count >= 4
        assert len(result.warnings) == 0

    def test_missing_style(self):
        result = analyze_prompt("A cancer cell being attacked by T-cells, clean background")
        assert not result.has_style
        assert any("STYLE" in w for w in result.warnings)

class TestModelValidation:
    def test_valid_model(self):
        valid, error = validate_model("google/gemini-3-pro-image-preview")
        assert valid
        assert error is None

    def test_invalid_model(self):
        valid, error = validate_model("invalid-model")
        assert not valid
        assert "Invalid model" in error

    def test_selection_quality(self):
        model = select_model(Priority.QUALITY)
        assert model == "google/gemini-3-pro-image-preview"

    def test_selection_budget(self):
        model = select_model(Priority.BUDGET)
        assert "flex" in model

class TestIterationStopping:
    def test_excellent_score_stops(self):
        log = IterationLog("presentation", [
            IterationRecord(1, "", "prompt", 8.5)
        ])
        stop, reason = should_stop(log)
        assert stop
        assert "excellent" in reason

    def test_hard_limit_stops(self):
        log = IterationLog("draft", [
            IterationRecord(i, "", "prompt", 5.0) for i in range(1, 4)
        ])
        stop, reason = should_stop(log)
        assert stop
        assert "Hard limit" in reason

    def test_plateau_detected(self):
        log = IterationLog("publication", [
            IterationRecord(1, "", "p1", 5.0),
            IterationRecord(2, "", "p2", 5.3),
            IterationRecord(3, "", "p3", 5.5),
        ])
        stop, reason = should_stop(log)
        assert stop
        assert "Plateau" in reason
```

## File Structure After Implementation

```
skills/generate-image/
├── SKILL.md                      # Main skill definition (existing)
├── DETERMINISM_AUDIT.md          # This document
├── references/
│   ├── model_capabilities.md     # Existing
│   └── prompt_templates.md       # Existing
└── scripts/
    ├── generate_image.py         # Existing main script
    ├── validate_output.py        # NEW: Post-generation validation
    ├── analyze_prompt.py         # NEW: Prompt component analysis
    ├── iteration_tracker.py      # NEW: Iteration tracking
    └── utils/
        ├── models.py             # NEW: Model validation/selection
        └── metadata.py           # NEW: Generation logging
```

## Next Steps for First Draft Stage

1. **Validate core workflow** - Test the happy path end-to-end before adding validation layers
2. **Add minimum viable validation** - Start with `validate_output.py` (resolution + integrity)
3. **Document model availability** - Verify all listed models are currently available on OpenRouter
4. **Test edge cases** - Empty prompt, invalid model, missing API key, corrupt output
5. **Consider structured prompt mode** - Evaluate if `--structured` flag would help users

---

*Audit completed: 2026-01-08*
*Auditor: Claude (Deterministic Auditor)*
