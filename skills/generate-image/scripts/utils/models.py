"""Model validation and selection utilities for generate-image skill.

This module provides deterministic model selection and validation to prevent
typos and enforce the allowlist from references/model_capabilities.md.

Phase 2 Implementation - Core Infrastructure
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Priority(Enum):
    """Generation priority for model selection."""

    QUALITY = "quality"
    SPEED = "speed"
    BUDGET = "budget"


class ModelCapability(Enum):
    """Capabilities a model may support."""

    GENERATION = "generation"
    EDITING = "editing"
    INPAINTING = "inpainting"


@dataclass(frozen=True)
class ModelInfo:
    """Information about a supported model."""

    id: str
    display_name: str
    generation: bool
    editing: bool
    inpainting: bool
    quality_tier: str  # "excellent", "good", "fair"
    cost_tier: str  # "$$$", "$$", "$"
    max_resolution: int
    notes: str = ""

    @property
    def capabilities(self) -> list[ModelCapability]:
        """Get list of supported capabilities."""
        caps = []
        if self.generation:
            caps.append(ModelCapability.GENERATION)
        if self.editing:
            caps.append(ModelCapability.EDITING)
        if self.inpainting:
            caps.append(ModelCapability.INPAINTING)
        return caps


# Valid models from references/model_capabilities.md
# Each model is defined with its full capability set
VALID_MODELS: dict[str, ModelInfo] = {
    "google/gemini-3-pro-image-preview": ModelInfo(
        id="google/gemini-3-pro-image-preview",
        display_name="Gemini 3 Pro Image",
        generation=True,
        editing=True,
        inpainting=True,
        quality_tier="excellent",
        cost_tier="$$",
        max_resolution=2048,
        notes="Best overall quality, supports all features",
    ),
    "black-forest-labs/flux.2-pro": ModelInfo(
        id="black-forest-labs/flux.2-pro",
        display_name="FLUX.2 Pro",
        generation=True,
        editing=True,
        inpainting=False,
        quality_tier="excellent",
        cost_tier="$$",
        max_resolution=2048,
        notes="Fast, high quality, good for iterations",
    ),
    "black-forest-labs/flux.2-flex": ModelInfo(
        id="black-forest-labs/flux.2-flex",
        display_name="FLUX.2 Flex",
        generation=True,
        editing=False,
        inpainting=False,
        quality_tier="good",
        cost_tier="$",
        max_resolution=1024,
        notes="Budget option, generation only",
    ),
}

DEFAULT_MODEL = "google/gemini-3-pro-image-preview"

# Common model ID typos and their corrections
COMMON_TYPOS: dict[str, str] = {
    "gemini-3-pro": "google/gemini-3-pro-image-preview",
    "gemini-pro": "google/gemini-3-pro-image-preview",
    "gemini3": "google/gemini-3-pro-image-preview",
    "flux-pro": "black-forest-labs/flux.2-pro",
    "flux-2-pro": "black-forest-labs/flux.2-pro",
    "flux.2pro": "black-forest-labs/flux.2-pro",
    "fluxpro": "black-forest-labs/flux.2-pro",
    "flux-flex": "black-forest-labs/flux.2-flex",
    "flux-2-flex": "black-forest-labs/flux.2-flex",
    "flux.2flex": "black-forest-labs/flux.2-flex",
    "fluxflex": "black-forest-labs/flux.2-flex",
}


@dataclass
class ValidationResult:
    """Result of model validation."""

    valid: bool
    model_id: str
    error: Optional[str] = None
    suggestion: Optional[str] = None
    info: Optional[ModelInfo] = None


def validate_model(model_id: str) -> ValidationResult:
    """
    Validate model ID against allowed list.

    Args:
        model_id: The model ID to validate

    Returns:
        ValidationResult with validity status and optional suggestions
    """
    # Exact match
    if model_id in VALID_MODELS:
        return ValidationResult(
            valid=True,
            model_id=model_id,
            info=VALID_MODELS[model_id],
        )

    # Check for known typos
    normalized = model_id.lower().replace("_", "-").replace(" ", "-")
    if normalized in COMMON_TYPOS:
        correct_id = COMMON_TYPOS[normalized]
        return ValidationResult(
            valid=False,
            model_id=model_id,
            error=f"Invalid model '{model_id}'.",
            suggestion=f"Did you mean '{correct_id}'?",
        )

    # Fuzzy match against valid models
    suggestions = []
    for valid_id in VALID_MODELS:
        # Check if input is a substring or partial match
        if model_id.lower() in valid_id.lower():
            suggestions.append(valid_id)
        elif any(
            part in valid_id.lower() for part in model_id.lower().split("/")[-1].split("-") if len(part) > 2
        ):
            suggestions.append(valid_id)

    if suggestions:
        return ValidationResult(
            valid=False,
            model_id=model_id,
            error=f"Invalid model '{model_id}'.",
            suggestion=f"Did you mean: {suggestions[0]}?",
        )

    # No match found
    valid_list = ", ".join(VALID_MODELS.keys())
    return ValidationResult(
        valid=False,
        model_id=model_id,
        error=f"Invalid model '{model_id}'. Valid models: {valid_list}",
    )


def select_model(
    priority: Priority = Priority.QUALITY,
    needs_editing: bool = False,
    needs_inpainting: bool = False,
    min_resolution: Optional[int] = None,
) -> str:
    """
    Deterministically select model based on requirements.

    Implements decision tree from references/model_capabilities.md.

    Args:
        priority: Quality, speed, or budget priority
        needs_editing: Whether image editing is required
        needs_inpainting: Whether inpainting is required
        min_resolution: Minimum required resolution

    Returns:
        Selected model ID
    """
    # Filter by capability requirements
    candidates = list(VALID_MODELS.values())

    if needs_inpainting:
        candidates = [m for m in candidates if m.inpainting]
        # Only Gemini supports inpainting
        if candidates:
            return candidates[0].id
        return DEFAULT_MODEL  # Fallback if no inpainting model

    if needs_editing:
        candidates = [m for m in candidates if m.editing]

    if min_resolution:
        candidates = [m for m in candidates if m.max_resolution >= min_resolution]

    if not candidates:
        return DEFAULT_MODEL

    # Sort by priority
    if priority == Priority.QUALITY:
        # Prefer excellent quality tier, then more capabilities, then stable ID order
        candidates.sort(
            key=lambda m: (
                0 if m.quality_tier == "excellent" else 1,
                -len(m.capabilities),  # More capabilities = better (negative for descending)
                m.id,
            )
        )
    elif priority == Priority.SPEED:
        # FLUX.2 Pro is fastest among high-quality options
        candidates.sort(
            key=lambda m: (
                0 if "flux" in m.id.lower() and m.quality_tier == "excellent" else 1,
                m.id,
            )
        )
    elif priority == Priority.BUDGET:
        # Prefer lower cost tiers
        cost_order = {"$": 0, "$$": 1, "$$$": 2}
        candidates.sort(key=lambda m: (cost_order.get(m.cost_tier, 3), m.id))

    return candidates[0].id


def supports_editing(model_id: str) -> bool:
    """Check if model supports image editing."""
    model = VALID_MODELS.get(model_id)
    return model.editing if model else False


def supports_inpainting(model_id: str) -> bool:
    """Check if model supports inpainting."""
    model = VALID_MODELS.get(model_id)
    return model.inpainting if model else False


def get_model_info(model_id: str) -> Optional[ModelInfo]:
    """Get full info for a model ID."""
    return VALID_MODELS.get(model_id)


def list_models_by_capability(capability: ModelCapability) -> list[str]:
    """List all models that support a given capability."""
    result = []
    for model_id, info in VALID_MODELS.items():
        if capability == ModelCapability.GENERATION and info.generation:
            result.append(model_id)
        elif capability == ModelCapability.EDITING and info.editing:
            result.append(model_id)
        elif capability == ModelCapability.INPAINTING and info.inpainting:
            result.append(model_id)
    return result


def get_quality_tier(model_id: str) -> Optional[str]:
    """Get quality tier for a model."""
    model = VALID_MODELS.get(model_id)
    return model.quality_tier if model else None


def get_cost_tier(model_id: str) -> Optional[str]:
    """Get cost tier for a model."""
    model = VALID_MODELS.get(model_id)
    return model.cost_tier if model else None


def format_model_list() -> str:
    """Format all models for display."""
    lines = ["Available Models:", ""]
    for model_id, info in VALID_MODELS.items():
        caps = ", ".join(c.value for c in info.capabilities)
        lines.append(f"  {info.display_name}")
        lines.append(f"    ID: {model_id}")
        lines.append(f"    Quality: {info.quality_tier} | Cost: {info.cost_tier}")
        lines.append(f"    Capabilities: {caps}")
        lines.append(f"    Max Resolution: {info.max_resolution}px")
        if info.notes:
            lines.append(f"    Notes: {info.notes}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(format_model_list())
        sys.exit(0)

    model_id = sys.argv[1]
    result = validate_model(model_id)

    if result.valid:
        print(f"Model '{model_id}' is valid.")
        if result.info:
            print(f"  Display Name: {result.info.display_name}")
            print(f"  Quality: {result.info.quality_tier}")
            print(f"  Cost: {result.info.cost_tier}")
    else:
        print(f"Error: {result.error}")
        if result.suggestion:
            print(f"Suggestion: {result.suggestion}")
        sys.exit(1)
