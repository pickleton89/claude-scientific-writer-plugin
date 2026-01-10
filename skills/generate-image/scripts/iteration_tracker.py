#!/usr/bin/env python3
"""
Track iterations and enforce stopping rules from SKILL.md.

This module provides structured iteration tracking for image generation workflows,
implementing the stopping rules defined in SKILL.md Success Criteria.

Phase 3 Implementation - Iteration Tracking
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

# Output type definitions from SKILL.md
OutputType = Literal["draft", "presentation", "publication", "hero"]

# Iteration limits from SKILL.md
SOFT_LIMITS: dict[OutputType, int] = {
    "draft": 2,
    "presentation": 3,
    "publication": 4,
    "hero": 4,
}

HARD_LIMITS: dict[OutputType, int] = {
    "draft": 3,
    "presentation": 4,
    "publication": 5,
    "hero": 5,
}

# Quality thresholds from SKILL.md
EXCELLENT_THRESHOLD = 8.0  # Score >= 8 is excellent
ACCEPTABLE_THRESHOLD = 7.0  # Score >= 7 is acceptable
PLATEAU_THRESHOLD = 0.5  # Improvement < 0.5 indicates plateau
PLATEAU_COUNT = 2  # Number of consecutive low improvements for plateau


class StopReason(Enum):
    """Reasons for stopping iteration."""

    NONE = "none"  # Should not stop
    EXCELLENT_SCORE = "excellent_score"  # Score >= 8/10
    ACCEPTABLE_AT_SOFT_LIMIT = "acceptable_at_soft_limit"  # Score >= 7 at soft limit
    PLATEAU_DETECTED = "plateau_detected"  # No improvement for 2+ iterations
    HARD_LIMIT_REACHED = "hard_limit_reached"  # Maximum iterations reached
    MANUAL_STOP = "manual_stop"  # User requested stop


@dataclass
class IterationRecord:
    """Record of a single generation attempt."""

    attempt: int
    timestamp: str
    prompt: str
    quality_score: Optional[float] = None
    notes: Optional[str] = None
    model: Optional[str] = None
    resolution: Optional[tuple[int, int]] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IterationRecord":
        """Create from dictionary."""
        # Work on a copy to avoid mutating the input
        data = data.copy()
        # Handle tuple conversion for resolution
        if data.get("resolution") and isinstance(data["resolution"], list):
            data["resolution"] = tuple(data["resolution"])
        return cls(**data)


@dataclass
class StopDecision:
    """Result of evaluating whether to stop iterating."""

    should_stop: bool
    reason: StopReason
    message: str
    current_iteration: int
    current_score: Optional[float]
    soft_limit: int
    hard_limit: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "should_stop": self.should_stop,
            "reason": self.reason.value,
            "message": self.message,
            "current_iteration": self.current_iteration,
            "current_score": self.current_score,
            "soft_limit": self.soft_limit,
            "hard_limit": self.hard_limit,
        }


@dataclass
class IterationLog:
    """Full iteration log for a generation task."""

    output_type: OutputType
    target_description: str
    iterations: list[IterationRecord] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False
    final_score: Optional[float] = None
    stop_reason: Optional[str] = None

    @property
    def soft_limit(self) -> int:
        """Soft limit from SKILL.md."""
        return SOFT_LIMITS.get(self.output_type, 3)

    @property
    def hard_limit(self) -> int:
        """Hard limit from SKILL.md."""
        return HARD_LIMITS.get(self.output_type, 5)

    @property
    def iteration_count(self) -> int:
        """Number of iterations completed."""
        return len(self.iterations)

    @property
    def scores(self) -> list[float]:
        """All quality scores (excluding None values)."""
        return [i.quality_score for i in self.iterations if i.quality_score is not None]

    @property
    def latest_score(self) -> Optional[float]:
        """Most recent quality score."""
        scores = self.scores
        return scores[-1] if scores else None

    @property
    def best_score(self) -> Optional[float]:
        """Highest quality score achieved."""
        scores = self.scores
        return max(scores) if scores else None

    @property
    def score_improvements(self) -> list[float]:
        """Score improvement between consecutive iterations."""
        scores = self.scores
        if len(scores) < 2:
            return []
        return [scores[i] - scores[i - 1] for i in range(1, len(scores))]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "output_type": self.output_type,
            "target_description": self.target_description,
            "iterations": [i.to_dict() for i in self.iterations],
            "created_at": self.created_at,
            "completed": self.completed,
            "final_score": self.final_score,
            "stop_reason": self.stop_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IterationLog":
        """Create from dictionary."""
        # Work on a copy to avoid mutating the input
        data = data.copy()
        iterations = [
            IterationRecord.from_dict(i) if isinstance(i, dict) else i
            for i in data.get("iterations", [])
        ]
        data["iterations"] = iterations
        return cls(**data)


def should_stop(log: IterationLog) -> StopDecision:
    """
    Apply stopping rules from SKILL.md Success Criteria.

    Rules (in priority order):
    1. Score >= 8/10 (excellent threshold) -> STOP
    2. Score >= 7/10 AND iteration count >= soft limit -> STOP
    3. Score improvement < 0.5 for 2 consecutive iterations (plateau) -> STOP
    4. Hard limit reached -> STOP

    Args:
        log: The iteration log to evaluate

    Returns:
        StopDecision with recommendation and reasoning
    """
    iteration_count = log.iteration_count
    current_score = log.latest_score
    scores = log.scores

    # Base decision for no iterations yet
    if not log.iterations:
        return StopDecision(
            should_stop=False,
            reason=StopReason.NONE,
            message="No iterations yet - ready to begin",
            current_iteration=0,
            current_score=None,
            soft_limit=log.soft_limit,
            hard_limit=log.hard_limit,
        )

    # Rule 1: Score >= 8/10 (excellent threshold)
    if current_score is not None and current_score >= EXCELLENT_THRESHOLD:
        return StopDecision(
            should_stop=True,
            reason=StopReason.EXCELLENT_SCORE,
            message=f"Score {current_score}/10 meets excellent threshold (>={EXCELLENT_THRESHOLD})",
            current_iteration=iteration_count,
            current_score=current_score,
            soft_limit=log.soft_limit,
            hard_limit=log.hard_limit,
        )

    # Rule 2: Score >= 7/10 AND iteration count >= soft limit
    if (
        current_score is not None
        and current_score >= ACCEPTABLE_THRESHOLD
        and iteration_count >= log.soft_limit
    ):
        return StopDecision(
            should_stop=True,
            reason=StopReason.ACCEPTABLE_AT_SOFT_LIMIT,
            message=(
                f"Score {current_score}/10 acceptable (>={ACCEPTABLE_THRESHOLD}) "
                f"and soft limit ({log.soft_limit}) reached"
            ),
            current_iteration=iteration_count,
            current_score=current_score,
            soft_limit=log.soft_limit,
            hard_limit=log.hard_limit,
        )

    # Rule 3: Score improvement < 0.5 for 2 consecutive iterations (plateau)
    if len(scores) >= 3:
        improvements = log.score_improvements
        if len(improvements) >= PLATEAU_COUNT:
            recent_improvements = improvements[-PLATEAU_COUNT:]
            if all(imp < PLATEAU_THRESHOLD for imp in recent_improvements):
                return StopDecision(
                    should_stop=True,
                    reason=StopReason.PLATEAU_DETECTED,
                    message=(
                        f"Plateau detected: last {PLATEAU_COUNT} improvements "
                        f"({', '.join(f'{i:.1f}' for i in recent_improvements)}) "
                        f"all below {PLATEAU_THRESHOLD}"
                    ),
                    current_iteration=iteration_count,
                    current_score=current_score,
                    soft_limit=log.soft_limit,
                    hard_limit=log.hard_limit,
                )

    # Rule 4: Hard limit reached
    if iteration_count >= log.hard_limit:
        return StopDecision(
            should_stop=True,
            reason=StopReason.HARD_LIMIT_REACHED,
            message=f"Hard limit ({log.hard_limit}) reached",
            current_iteration=iteration_count,
            current_score=current_score,
            soft_limit=log.soft_limit,
            hard_limit=log.hard_limit,
        )

    # No stopping condition met - continue
    remaining = log.hard_limit - iteration_count
    return StopDecision(
        should_stop=False,
        reason=StopReason.NONE,
        message=(
            f"Continue: iteration {iteration_count}/{log.hard_limit}, "
            f"score {current_score if current_score else 'N/A'}, "
            f"{remaining} iteration{'s' if remaining != 1 else ''} remaining"
        ),
        current_iteration=iteration_count,
        current_score=current_score,
        soft_limit=log.soft_limit,
        hard_limit=log.hard_limit,
    )


def create_iteration_log(
    output_type: OutputType,
    target_description: str,
) -> IterationLog:
    """
    Create a new iteration log for tracking generation attempts.

    Args:
        output_type: Type of output (draft, presentation, publication, hero)
        target_description: Description of what we're trying to generate

    Returns:
        New IterationLog
    """
    return IterationLog(
        output_type=output_type,
        target_description=target_description,
    )


def add_iteration(
    log: IterationLog,
    prompt: str,
    quality_score: Optional[float] = None,
    notes: Optional[str] = None,
    model: Optional[str] = None,
    resolution: Optional[tuple[int, int]] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> IterationRecord:
    """
    Add a new iteration to the log.

    Args:
        log: The iteration log to add to
        prompt: The prompt used for this iteration
        quality_score: Quality score (0-10) for the result
        notes: Optional notes about this iteration
        model: Model used for generation
        resolution: Output resolution
        success: Whether generation succeeded
        error: Error message if failed

    Returns:
        The created IterationRecord
    """
    record = IterationRecord(
        attempt=log.iteration_count + 1,
        timestamp=datetime.now().isoformat(),
        prompt=prompt,
        quality_score=quality_score,
        notes=notes,
        model=model,
        resolution=resolution,
        success=success,
        error=error,
    )
    log.iterations.append(record)
    return record


def complete_log(
    log: IterationLog,
    final_score: Optional[float] = None,
    stop_reason: Optional[StopReason] = None,
) -> None:
    """
    Mark an iteration log as completed.

    Args:
        log: The iteration log to complete
        final_score: Final quality score (defaults to latest score)
        stop_reason: Reason for stopping (defaults to evaluating should_stop)
    """
    log.completed = True
    log.final_score = final_score if final_score is not None else log.latest_score

    if stop_reason is not None:
        log.stop_reason = stop_reason.value
    else:
        decision = should_stop(log)
        log.stop_reason = decision.reason.value


def _get_log_path(output_path: str) -> Path:
    """Get the iteration log file path for an output image."""
    return Path(output_path).with_suffix(".iterations.json")


def save_iteration_log(log: IterationLog, path: str) -> str:
    """
    Save iteration log to JSON file.

    Args:
        log: The iteration log to save
        path: Output path (image path or explicit log path)

    Returns:
        Path to saved log file
    """
    # If path looks like an image, use .iterations.json suffix
    if not path.endswith(".json"):
        path = str(_get_log_path(path))

    with open(path, "w") as f:
        json.dump(log.to_dict(), f, indent=2)

    return path


def load_iteration_log(path: str) -> Optional[IterationLog]:
    """
    Load iteration log from JSON file.

    Args:
        path: Path to log file or image path

    Returns:
        IterationLog or None if file doesn't exist
    """
    # If path looks like an image, try .iterations.json suffix
    if not path.endswith(".json"):
        path = str(_get_log_path(path))

    p = Path(path)
    if not p.exists():
        return None

    try:
        with open(p) as f:
            data = json.load(f)
        return IterationLog.from_dict(data)
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None


def get_or_create_log(
    output_path: str,
    output_type: OutputType,
    target_description: str,
) -> IterationLog:
    """
    Load existing log or create a new one.

    Args:
        output_path: Path to the output image
        output_type: Type of output for new logs
        target_description: Description for new logs

    Returns:
        Existing or new IterationLog
    """
    existing = load_iteration_log(output_path)
    if existing is not None:
        return existing
    return create_iteration_log(output_type, target_description)


def format_iteration_log(log: IterationLog) -> str:
    """Format iteration log for display."""
    lines = [
        f"Iteration Log: {log.target_description}",
        f"Output Type: {log.output_type}",
        f"Limits: soft={log.soft_limit}, hard={log.hard_limit}",
        f"Status: {'Completed' if log.completed else 'In Progress'}",
        "",
    ]

    if log.iterations:
        lines.append(f"Iterations ({log.iteration_count}):")
        for record in log.iterations:
            score_str = f"{record.quality_score}/10" if record.quality_score is not None else "N/A"
            status = "Success" if record.success else f"Failed: {record.error}"
            lines.append(f"  {record.attempt}. [{score_str}] {status}")
            lines.append(f"     Prompt: {record.prompt[:60]}{'...' if len(record.prompt) > 60 else ''}")
            if record.notes:
                lines.append(f"     Notes: {record.notes}")
        lines.append("")

    # Score analysis
    if log.scores:
        lines.append("Score Analysis:")
        lines.append(f"  Latest: {log.latest_score}")
        lines.append(f"  Best: {log.best_score}")
        if log.score_improvements:
            lines.append(f"  Improvements: {', '.join(f'{i:+.1f}' for i in log.score_improvements)}")
        lines.append("")

    # Current decision
    decision = should_stop(log)
    lines.append("Decision:")
    lines.append(f"  {decision.message}")

    if log.completed:
        lines.append("")
        lines.append(f"Final Score: {log.final_score}")
        lines.append(f"Stop Reason: {log.stop_reason}")

    return "\n".join(lines)


def get_iteration_stats(log: IterationLog) -> dict[str, Any]:
    """
    Calculate statistics from an iteration log.

    Args:
        log: The iteration log to analyze

    Returns:
        Dictionary with statistics
    """
    scores = log.scores
    improvements = log.score_improvements

    return {
        "total_iterations": log.iteration_count,
        "successful_iterations": sum(1 for i in log.iterations if i.success),
        "failed_iterations": sum(1 for i in log.iterations if not i.success),
        "latest_score": log.latest_score,
        "best_score": log.best_score,
        "worst_score": min(scores) if scores else None,
        "score_range": max(scores) - min(scores) if len(scores) >= 2 else None,
        "avg_improvement": sum(improvements) / len(improvements) if improvements else None,
        "total_improvement": scores[-1] - scores[0] if len(scores) >= 2 else None,
        "output_type": log.output_type,
        "soft_limit": log.soft_limit,
        "hard_limit": log.hard_limit,
        "at_soft_limit": log.iteration_count >= log.soft_limit,
        "at_hard_limit": log.iteration_count >= log.hard_limit,
        "completed": log.completed,
        "stop_reason": log.stop_reason,
    }


def validate_output_type(output_type: str) -> tuple[bool, Optional[str]]:
    """
    Validate that output type is valid.

    Args:
        output_type: The output type to validate

    Returns:
        (is_valid, error_message)
    """
    valid_types = ["draft", "presentation", "publication", "hero"]
    if output_type in valid_types:
        return True, None
    return False, f"Invalid output type '{output_type}'. Valid types: {', '.join(valid_types)}"


def get_limits_for_type(output_type: OutputType) -> tuple[int, int]:
    """
    Get soft and hard limits for an output type.

    Args:
        output_type: The output type

    Returns:
        (soft_limit, hard_limit)
    """
    return SOFT_LIMITS.get(output_type, 3), HARD_LIMITS.get(output_type, 5)


if __name__ == "__main__":
    import sys

    # Example usage and demonstration
    if len(sys.argv) < 2:
        print("Usage: python iteration_tracker.py <command> [args]")
        print("\nCommands:")
        print("  demo           - Run demonstration")
        print("  load <path>    - Load and display iteration log")
        print("  limits         - Show iteration limits by output type")
        sys.exit(1)

    command = sys.argv[1]

    if command == "demo":
        # Demonstrate stopping rules
        print("Iteration Tracker Demo")
        print("=" * 50)
        print()

        # Create a log
        log = create_iteration_log("presentation", "DNA double helix illustration")
        print(f"Created log for: {log.target_description}")
        print(f"Output type: {log.output_type}")
        print(f"Limits: soft={log.soft_limit}, hard={log.hard_limit}")
        print()

        # Simulate iterations
        iterations = [
            ("DNA helix, scientific style", 5.0, "Initial attempt, too simple"),
            ("DNA double helix, detailed, scientific illustration", 6.5, "Better detail"),
            ("DNA double helix, 3D render, scientific illustration, high detail", 7.2, "Good quality"),
        ]

        for prompt, score, notes in iterations:
            add_iteration(log, prompt, quality_score=score, notes=notes)
            decision = should_stop(log)
            print(f"Iteration {log.iteration_count}: score={score}")
            print(f"  Decision: {decision.message}")
            print()

        # Show final state
        print("=" * 50)
        print(format_iteration_log(log))

    elif command == "load" and len(sys.argv) >= 3:
        path = sys.argv[2]
        log = load_iteration_log(path)
        if log:
            print(format_iteration_log(log))
        else:
            print(f"No iteration log found at {path}")
            sys.exit(1)

    elif command == "limits":
        print("Iteration Limits by Output Type")
        print("=" * 40)
        print(f"{'Type':<15} {'Soft':<10} {'Hard':<10}")
        print("-" * 40)
        for output_type in ["draft", "presentation", "publication", "hero"]:
            soft, hard = get_limits_for_type(output_type)  # type: ignore
            print(f"{output_type:<15} {soft:<10} {hard:<10}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
