"""Generation metadata logging for reproducibility.

This module provides structured logging of image generation attempts,
enabling reproducibility analysis and iteration tracking.

Phase 2 Implementation - Core Infrastructure
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class GenerationMetadata:
    """Metadata for a single generation attempt."""

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
    prompt_analysis: Optional[dict[str, Any]] = None
    validation_result: Optional[dict[str, Any]] = None
    generation_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationMetadata":
        """Create from dictionary."""
        # Work on a copy to avoid mutating the input
        data = data.copy()
        # Handle tuple conversion for resolution
        if data.get("resolution") and isinstance(data["resolution"], list):
            data["resolution"] = tuple(data["resolution"])
        return cls(**data)


@dataclass
class GenerationSession:
    """A session containing multiple generation attempts."""

    session_id: str
    created_at: str
    output_path: str
    target_description: str
    attempts: list[GenerationMetadata] = field(default_factory=list)
    final_model: Optional[str] = None
    total_attempts: int = 0
    successful: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["attempts"] = [a.to_dict() if hasattr(a, "to_dict") else a for a in self.attempts]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationSession":
        """Create from dictionary."""
        # Work on a copy to avoid mutating the input
        data = data.copy()
        attempts = [
            GenerationMetadata.from_dict(a) if isinstance(a, dict) else a
            for a in data.get("attempts", [])
        ]
        data["attempts"] = attempts
        return cls(**data)


def _get_meta_path(output_path: str) -> Path:
    """Get the metadata file path for an output image."""
    return Path(output_path).with_suffix(".meta.json")


def _get_image_info(output_path: str) -> tuple[Optional[tuple[int, int]], Optional[int]]:
    """Extract resolution and file size from an image."""
    resolution = None
    file_size = None
    try:
        from PIL import Image

        img = Image.open(output_path)
        resolution = img.size
        file_size = Path(output_path).stat().st_size
    except (OSError, FileNotFoundError, ValueError, ImportError):
        # OSError: file access issues, corrupt images
        # FileNotFoundError: image doesn't exist yet
        # ValueError: PIL couldn't decode the image
        # ImportError: PIL not installed
        pass
    return resolution, file_size


def log_generation(
    output_path: str,
    prompt: str,
    model: str,
    input_image: Optional[str] = None,
    attempt_number: int = 1,
    success: bool = True,
    error: Optional[str] = None,
    prompt_analysis: Optional[dict[str, Any]] = None,
    validation_result: Optional[dict[str, Any]] = None,
    generation_params: Optional[dict[str, Any]] = None,
) -> str:
    """
    Log generation metadata to sidecar JSON file.

    Creates a new metadata file or appends to existing one.

    Args:
        output_path: Path to generated image
        prompt: Generation prompt
        model: Model ID used
        input_image: Optional input image for editing
        attempt_number: Which attempt this is
        success: Whether generation succeeded
        error: Error message if failed
        prompt_analysis: Results from analyze_prompt
        validation_result: Results from validate_output
        generation_params: Additional generation parameters

    Returns:
        Path to metadata file
    """
    meta_path = _get_meta_path(output_path)
    resolution, file_size = _get_image_info(output_path)

    metadata = GenerationMetadata(
        prompt=prompt,
        model=model,
        timestamp=datetime.now().isoformat(),
        output_path=str(output_path),
        input_image=input_image,
        attempt_number=attempt_number,
        resolution=resolution,
        file_size_bytes=file_size,
        success=success,
        error=error,
        prompt_analysis=prompt_analysis,
        validation_result=validation_result,
        generation_params=generation_params or {},
    )

    # Write metadata
    with open(meta_path, "w") as f:
        json.dump(metadata.to_dict(), f, indent=2)

    return str(meta_path)


def append_generation_attempt(
    output_path: str,
    prompt: str,
    model: str,
    input_image: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None,
    prompt_analysis: Optional[dict[str, Any]] = None,
    validation_result: Optional[dict[str, Any]] = None,
    generation_params: Optional[dict[str, Any]] = None,
) -> str:
    """
    Append a new generation attempt to existing metadata.

    If no metadata exists, creates a new file with attempt_number=1.
    Otherwise, increments attempt_number and appends to history.

    Args:
        output_path: Path to generated image
        prompt: Generation prompt
        model: Model ID used
        input_image: Optional input image for editing
        success: Whether generation succeeded
        error: Error message if failed
        prompt_analysis: Results from analyze_prompt
        validation_result: Results from validate_output
        generation_params: Additional generation parameters

    Returns:
        Path to metadata file
    """
    meta_path = _get_meta_path(output_path)
    history = load_generation_history(output_path)
    attempt_number = len(history) + 1

    resolution, file_size = _get_image_info(output_path)

    new_attempt = GenerationMetadata(
        prompt=prompt,
        model=model,
        timestamp=datetime.now().isoformat(),
        output_path=str(output_path),
        input_image=input_image,
        attempt_number=attempt_number,
        resolution=resolution,
        file_size_bytes=file_size,
        success=success,
        error=error,
        prompt_analysis=prompt_analysis,
        validation_result=validation_result,
        generation_params=generation_params or {},
    )

    history.append(new_attempt)

    # Write all attempts as array
    with open(meta_path, "w") as f:
        json.dump([m.to_dict() for m in history], f, indent=2)

    return str(meta_path)


def load_generation_history(output_path: str) -> list[GenerationMetadata]:
    """
    Load all generation attempts for an output path.

    Args:
        output_path: Path to the generated image

    Returns:
        List of GenerationMetadata, empty if no history exists
    """
    meta_path = _get_meta_path(output_path)

    if not meta_path.exists():
        return []

    try:
        with open(meta_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        # JSONDecodeError: corrupted or invalid JSON
        # OSError: file access issues
        # FileNotFoundError: metadata file doesn't exist
        return []

    # Handle both single object and array formats
    if isinstance(data, list):
        return [GenerationMetadata.from_dict(d) for d in data]
    return [GenerationMetadata.from_dict(data)]


def get_latest_metadata(output_path: str) -> Optional[GenerationMetadata]:
    """
    Get the most recent generation metadata for an output.

    Args:
        output_path: Path to the generated image

    Returns:
        Latest GenerationMetadata or None if no history
    """
    history = load_generation_history(output_path)
    return history[-1] if history else None


def create_session(
    output_path: str,
    target_description: str,
    notes: str = "",
) -> GenerationSession:
    """
    Create a new generation session for tracking multiple attempts.

    Args:
        output_path: Target output path for the final image
        target_description: Description of what we're trying to generate
        notes: Optional notes about the session

    Returns:
        New GenerationSession
    """
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return GenerationSession(
        session_id=session_id,
        created_at=datetime.now().isoformat(),
        output_path=str(output_path),
        target_description=target_description,
        notes=notes,
    )


def save_session(session: GenerationSession, path: Optional[str] = None) -> str:
    """
    Save a generation session to JSON.

    Args:
        session: The session to save
        path: Optional custom path (defaults to output_path.session.json)

    Returns:
        Path to saved session file
    """
    if path is None:
        path = str(Path(session.output_path).with_suffix(".session.json"))

    with open(path, "w") as f:
        json.dump(session.to_dict(), f, indent=2)

    return path


def load_session(path: str) -> Optional[GenerationSession]:
    """
    Load a generation session from JSON.

    Args:
        path: Path to session file

    Returns:
        GenerationSession or None if file doesn't exist
    """
    p = Path(path)
    if not p.exists():
        return None

    try:
        with open(p) as f:
            data = json.load(f)
        return GenerationSession.from_dict(data)
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        # JSONDecodeError: corrupted or invalid JSON
        # OSError: file access issues
        # FileNotFoundError: session file doesn't exist
        return None


def format_history(history: list[GenerationMetadata]) -> str:
    """Format generation history for display."""
    if not history:
        return "No generation history found."

    lines = [f"Generation History ({len(history)} attempts):", ""]

    for meta in history:
        lines.append(f"Attempt {meta.attempt_number}:")
        lines.append(f"  Timestamp: {meta.timestamp}")
        lines.append(f"  Model: {meta.model}")
        lines.append(f"  Success: {'Yes' if meta.success else 'No'}")
        if meta.resolution:
            lines.append(f"  Resolution: {meta.resolution[0]}x{meta.resolution[1]}")
        if meta.file_size_bytes:
            lines.append(f"  File Size: {meta.file_size_bytes / 1024:.1f} KB")
        if meta.error:
            lines.append(f"  Error: {meta.error}")
        lines.append(f"  Prompt: {meta.prompt[:80]}{'...' if len(meta.prompt) > 80 else ''}")
        lines.append("")

    return "\n".join(lines)


def get_attempt_stats(history: list[GenerationMetadata]) -> dict[str, Any]:
    """
    Calculate statistics from generation history.

    Args:
        history: List of generation metadata

    Returns:
        Dictionary with statistics
    """
    if not history:
        return {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "success_rate": 0.0,
            "models_used": [],
            "avg_file_size_kb": None,
        }

    successful = [m for m in history if m.success]
    file_sizes = [m.file_size_bytes for m in history if m.file_size_bytes]
    models = list(set(m.model for m in history))

    return {
        "total_attempts": len(history),
        "successful_attempts": len(successful),
        "failed_attempts": len(history) - len(successful),
        "success_rate": len(successful) / len(history) if history else 0.0,
        "models_used": models,
        "avg_file_size_kb": sum(file_sizes) / len(file_sizes) / 1024 if file_sizes else None,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python metadata.py <image_path>")
        print("\nShows generation history for the specified image.")
        sys.exit(1)

    image_path = sys.argv[1]
    history = load_generation_history(image_path)

    print(format_history(history))

    if history:
        print("\nStatistics:")
        stats = get_attempt_stats(history)
        print(f"  Total Attempts: {stats['total_attempts']}")
        print(f"  Success Rate: {stats['success_rate']:.1%}")
        print(f"  Models Used: {', '.join(stats['models_used'])}")
        if stats["avg_file_size_kb"]:
            print(f"  Avg File Size: {stats['avg_file_size_kb']:.1f} KB")
