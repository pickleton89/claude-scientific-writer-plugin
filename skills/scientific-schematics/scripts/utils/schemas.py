"""Output schemas for scientific schematic generation.

Provides structured data classes for generation results, iteration tracking,
and reproducibility metadata. Uses dataclasses for validation without
requiring external dependencies.

Usage:
    >>> from utils.schemas import GenerationResults, IterationResult
    >>> result = IterationResult(
    ...     iteration=1,
    ...     image_path="/path/to/image.png",
    ...     prompt="Create a flowchart",
    ...     critique="Good clarity, needs better labels",
    ...     score=7.5,
    ...     needs_improvement=True,
    ...     success=True
    ... )
    >>> result.to_dict()
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


DocType = Literal[
    "journal",
    "conference",
    "poster",
    "presentation",
    "report",
    "grant",
    "thesis",
    "preprint",
    "default",
]


@dataclass
class IterationResult:
    """Schema for a single generation iteration."""

    iteration: int
    image_path: str
    prompt: str
    critique: str
    score: float
    needs_improvement: bool
    success: bool
    error: str | None = None

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.iteration < 1 or self.iteration > 5:
            raise ValueError(f"iteration must be 1-5, got {self.iteration}")
        if self.score < 0 or self.score > 10:
            raise ValueError(f"score must be 0-10, got {self.score}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class GenerationResults:
    """Schema for complete generation results."""

    user_prompt: str
    doc_type: DocType
    quality_threshold: float
    iterations: list[IterationResult]
    final_image: str | None
    final_score: float
    success: bool
    early_stop: bool
    early_stop_reason: str | None

    # Metadata for reproducibility
    generation_model: str = "google/gemini-3-pro-image-preview"
    review_model: str = "google/gemini-3-flash"
    prompt_hash: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Validate fields and compute prompt hash."""
        if self.quality_threshold < 0 or self.quality_threshold > 10:
            raise ValueError(
                f"quality_threshold must be 0-10, got {self.quality_threshold}"
            )
        if self.final_score < 0 or self.final_score > 10:
            raise ValueError(f"final_score must be 0-10, got {self.final_score}")

        # Compute prompt hash if not provided
        if self.prompt_hash is None:
            self.prompt_hash = hash_prompt(self.user_prompt)

    def to_dict(self) -> dict:
        """Convert to dictionary with nested iterations."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str | Path) -> None:
        """Save results to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: dict) -> GenerationResults:
        """Create from dictionary."""
        iterations = [
            IterationResult(**iter_data) for iter_data in data.pop("iterations", [])
        ]
        return cls(iterations=iterations, **data)

    @classmethod
    def load(cls, path: str | Path) -> GenerationResults:
        """Load results from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class SchematicPrompt:
    """Structured prompt with required and optional fields.

    Use this to build prompts programmatically with validation.
    """

    # Required fields
    diagram_type: str
    components: list[str]
    layout: Literal["top-to-bottom", "left-to-right", "circular", "hierarchical"]

    # Optional fields
    description: str | None = None
    labels: list[str] = field(default_factory=list)
    quantitative_details: str | None = None
    style_notes: str | None = None
    colorblind_safe: bool = True
    palette: str = "default"

    def __post_init__(self) -> None:
        """Validate fields."""
        if len(self.components) < 2:
            raise ValueError(
                f"Need at least 2 components, got {len(self.components)}"
            )

    def validate(self) -> tuple[bool, list[str]]:
        """Validate prompt meets requirements.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if len(self.components) < 3:
            issues.append(
                f"Recommend at least 3 components for clarity, got {len(self.components)}"
            )

        return len(issues) == 0, issues

    def to_prompt_text(self) -> str:
        """Convert to natural language prompt."""
        parts = []

        if self.description:
            parts.append(self.description)
        else:
            parts.append(f"Create a {self.diagram_type} diagram")

        parts.append(f"Layout: {self.layout}")
        parts.append(f"Components: {', '.join(self.components)}")

        if self.labels:
            parts.append(f"Labels: {', '.join(self.labels)}")

        if self.quantitative_details:
            parts.append(f"Details: {self.quantitative_details}")

        if self.style_notes:
            parts.append(f"Style: {self.style_notes}")

        if self.colorblind_safe:
            parts.append("Use colorblind-safe colors")

        return "\n".join(parts)


@dataclass
class ScoreTrend:
    """Track score trends for quality monitoring."""

    timestamp: str
    diagram_type: str
    doc_type: str
    score: float
    iterations: int
    success: bool
    prompt_hash: str

    def to_jsonl(self) -> str:
        """Convert to JSONL format (single line)."""
        return json.dumps(asdict(self))

    @classmethod
    def from_results(cls, results: GenerationResults, diagram_type: str) -> ScoreTrend:
        """Create from GenerationResults."""
        return cls(
            timestamp=results.timestamp,
            diagram_type=diagram_type,
            doc_type=results.doc_type,
            score=results.final_score,
            iterations=len([i for i in results.iterations if i.success]),
            success=results.success,
            prompt_hash=results.prompt_hash or "",
        )


def hash_prompt(prompt: str) -> str:
    """Create SHA256 hash of prompt for reproducibility tracking.

    Args:
        prompt: The prompt text to hash

    Returns:
        First 16 characters of SHA256 hash
    """
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def validate_results_dict(data: dict) -> tuple[bool, list[str]]:
    """Validate a results dictionary matches expected schema.

    Args:
        data: Dictionary to validate

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    required_fields = [
        "user_prompt",
        "doc_type",
        "quality_threshold",
        "iterations",
        "success",
    ]

    for field_name in required_fields:
        if field_name not in data:
            issues.append(f"Missing required field: {field_name}")

    if "quality_threshold" in data:
        threshold = data["quality_threshold"]
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 10:
            issues.append(f"quality_threshold must be 0-10, got {threshold}")

    if "final_score" in data:
        score = data["final_score"]
        if not isinstance(score, (int, float)) or score < 0 or score > 10:
            issues.append(f"final_score must be 0-10, got {score}")

    if "iterations" in data:
        if not isinstance(data["iterations"], list):
            issues.append("iterations must be a list")
        else:
            for i, iteration in enumerate(data["iterations"]):
                if not isinstance(iteration, dict):
                    issues.append(f"iteration {i} must be a dict")
                elif "iteration" in iteration:
                    iter_num = iteration["iteration"]
                    if not isinstance(iter_num, int) or iter_num < 1:
                        issues.append(f"iteration {i} has invalid iteration number")

    return len(issues) == 0, issues
