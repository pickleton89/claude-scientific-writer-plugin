"""Tests for iteration tracking and stopping rules.

Phase 3 Test Suite - Iteration Tracking
"""

import sys
import tempfile
from pathlib import Path


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from iteration_tracker import (
    ACCEPTABLE_THRESHOLD,
    EXCELLENT_THRESHOLD,
    HARD_LIMITS,
    PLATEAU_COUNT,
    PLATEAU_THRESHOLD,
    SOFT_LIMITS,
    IterationLog,
    IterationRecord,
    StopDecision,
    StopReason,
    add_iteration,
    complete_log,
    create_iteration_log,
    format_iteration_log,
    get_iteration_stats,
    get_limits_for_type,
    get_or_create_log,
    load_iteration_log,
    save_iteration_log,
    should_stop,
    validate_output_type,
)


# =============================================================================
# IterationRecord Tests
# =============================================================================


class TestIterationRecord:
    """Tests for IterationRecord dataclass."""

    def test_creation_minimal(self):
        """Test creating IterationRecord with minimal fields."""
        record = IterationRecord(
            attempt=1,
            timestamp="2026-01-09T12:00:00",
            prompt="test prompt",
        )
        assert record.attempt == 1
        assert record.timestamp == "2026-01-09T12:00:00"
        assert record.prompt == "test prompt"
        assert record.quality_score is None
        assert record.notes is None
        assert record.model is None
        assert record.resolution is None
        assert record.success is True
        assert record.error is None

    def test_creation_full(self):
        """Test creating IterationRecord with all fields."""
        record = IterationRecord(
            attempt=2,
            timestamp="2026-01-09T12:05:00",
            prompt="detailed prompt",
            quality_score=7.5,
            notes="Good progress",
            model="google/gemini-3-pro-image-preview",
            resolution=(1024, 1024),
            success=True,
            error=None,
        )
        assert record.attempt == 2
        assert record.quality_score == 7.5
        assert record.notes == "Good progress"
        assert record.model == "google/gemini-3-pro-image-preview"
        assert record.resolution == (1024, 1024)
        assert record.success is True

    def test_creation_failed(self):
        """Test creating a failed IterationRecord."""
        record = IterationRecord(
            attempt=1,
            timestamp="2026-01-09T12:00:00",
            prompt="test prompt",
            success=False,
            error="API rate limit exceeded",
        )
        assert record.success is False
        assert record.error == "API rate limit exceeded"
        assert record.quality_score is None

    def test_to_dict(self):
        """Test converting IterationRecord to dictionary."""
        record = IterationRecord(
            attempt=1,
            timestamp="2026-01-09T12:00:00",
            prompt="test prompt",
            quality_score=6.0,
            resolution=(512, 512),
        )
        data = record.to_dict()
        assert data["attempt"] == 1
        assert data["quality_score"] == 6.0
        assert data["resolution"] == (512, 512)

    def test_from_dict_minimal(self):
        """Test creating IterationRecord from minimal dictionary."""
        data = {
            "attempt": 1,
            "timestamp": "2026-01-09T12:00:00",
            "prompt": "test prompt",
        }
        record = IterationRecord.from_dict(data)
        assert record.attempt == 1
        assert record.prompt == "test prompt"

    def test_from_dict_with_list_resolution(self):
        """Test that list resolution is converted to tuple."""
        data = {
            "attempt": 1,
            "timestamp": "2026-01-09T12:00:00",
            "prompt": "test",
            "resolution": [1024, 768],
        }
        record = IterationRecord.from_dict(data)
        assert record.resolution == (1024, 768)
        assert isinstance(record.resolution, tuple)

    def test_from_dict_does_not_mutate_input(self):
        """Test that from_dict doesn't mutate the input dictionary."""
        data = {
            "attempt": 1,
            "timestamp": "2026-01-09T12:00:00",
            "prompt": "test",
            "resolution": [1024, 768],
        }
        original_resolution = data["resolution"]
        IterationRecord.from_dict(data)
        # Original should still be a list
        assert data["resolution"] == original_resolution
        assert isinstance(data["resolution"], list)

    def test_roundtrip_serialization(self):
        """Test that to_dict/from_dict roundtrip preserves data."""
        original = IterationRecord(
            attempt=3,
            timestamp="2026-01-09T12:15:00",
            prompt="complex prompt",
            quality_score=8.5,
            notes="Excellent result",
            model="test/model",
            resolution=(2048, 2048),
            success=True,
        )
        restored = IterationRecord.from_dict(original.to_dict())
        assert restored.attempt == original.attempt
        assert restored.quality_score == original.quality_score
        assert restored.resolution == original.resolution


# =============================================================================
# IterationLog Tests
# =============================================================================


class TestIterationLog:
    """Tests for IterationLog dataclass."""

    def test_creation_minimal(self):
        """Test creating IterationLog with minimal fields."""
        log = IterationLog(
            output_type="presentation",
            target_description="Test image",
        )
        assert log.output_type == "presentation"
        assert log.target_description == "Test image"
        assert log.iterations == []
        assert log.completed is False
        assert log.final_score is None
        assert log.stop_reason is None

    def test_soft_limit_property(self):
        """Test soft limit property for each output type."""
        for output_type, expected in SOFT_LIMITS.items():
            log = IterationLog(output_type=output_type, target_description="Test")
            assert log.soft_limit == expected

    def test_hard_limit_property(self):
        """Test hard limit property for each output type."""
        for output_type, expected in HARD_LIMITS.items():
            log = IterationLog(output_type=output_type, target_description="Test")
            assert log.hard_limit == expected

    def test_iteration_count_empty(self):
        """Test iteration count with no iterations."""
        log = IterationLog(output_type="draft", target_description="Test")
        assert log.iteration_count == 0

    def test_iteration_count_with_iterations(self):
        """Test iteration count with iterations."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=6.0),
            ],
        )
        assert log.iteration_count == 2

    def test_scores_property(self):
        """Test scores property extracts quality scores."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=None),
                IterationRecord(3, "t3", "p3", quality_score=7.0),
            ],
        )
        assert log.scores == [5.0, 7.0]

    def test_scores_property_empty(self):
        """Test scores property with no iterations."""
        log = IterationLog(output_type="draft", target_description="Test")
        assert log.scores == []

    def test_latest_score(self):
        """Test latest_score property."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=7.0),
            ],
        )
        assert log.latest_score == 7.0

    def test_latest_score_none(self):
        """Test latest_score when no scores exist."""
        log = IterationLog(output_type="draft", target_description="Test")
        assert log.latest_score is None

    def test_best_score(self):
        """Test best_score property."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=8.0),
                IterationRecord(3, "t3", "p3", quality_score=7.0),
            ],
        )
        assert log.best_score == 8.0

    def test_score_improvements(self):
        """Test score_improvements property."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=6.5),
                IterationRecord(3, "t3", "p3", quality_score=7.0),
            ],
        )
        assert log.score_improvements == [1.5, 0.5]

    def test_score_improvements_empty(self):
        """Test score_improvements with insufficient scores."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
            ],
        )
        assert log.score_improvements == []

    def test_to_dict(self):
        """Test converting IterationLog to dictionary."""
        log = IterationLog(
            output_type="publication",
            target_description="Test image",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
            ],
            completed=True,
            final_score=8.0,
            stop_reason="excellent_score",
        )
        data = log.to_dict()
        assert data["output_type"] == "publication"
        assert data["completed"] is True
        assert data["final_score"] == 8.0
        assert len(data["iterations"]) == 1

    def test_from_dict(self):
        """Test creating IterationLog from dictionary."""
        data = {
            "output_type": "hero",
            "target_description": "Hero image",
            "iterations": [
                {"attempt": 1, "timestamp": "t1", "prompt": "p1", "quality_score": 6.0},
            ],
            "created_at": "2026-01-09T12:00:00",
            "completed": False,
            "final_score": None,
            "stop_reason": None,
        }
        log = IterationLog.from_dict(data)
        assert log.output_type == "hero"
        assert log.iteration_count == 1
        assert log.iterations[0].quality_score == 6.0

    def test_from_dict_does_not_mutate_input(self):
        """Test that from_dict doesn't mutate the input dictionary."""
        data = {
            "output_type": "draft",
            "target_description": "Test",
            "iterations": [
                {"attempt": 1, "timestamp": "t1", "prompt": "p1"},
            ],
            "created_at": "2026-01-09T12:00:00",
            "completed": False,
            "final_score": None,
            "stop_reason": None,
        }
        original_iterations = data["iterations"]
        IterationLog.from_dict(data)
        # Original should still be the same list of dicts
        assert data["iterations"] == original_iterations
        assert isinstance(data["iterations"][0], dict)

    def test_roundtrip_serialization(self):
        """Test that to_dict/from_dict roundtrip preserves data."""
        original = IterationLog(
            output_type="presentation",
            target_description="Complex image",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=7.0),
            ],
            completed=True,
            final_score=7.0,
            stop_reason="acceptable_at_soft_limit",
        )
        restored = IterationLog.from_dict(original.to_dict())
        assert restored.output_type == original.output_type
        assert restored.iteration_count == original.iteration_count
        assert restored.final_score == original.final_score


# =============================================================================
# StopDecision Tests
# =============================================================================


class TestStopDecision:
    """Tests for StopDecision dataclass."""

    def test_creation(self):
        """Test creating StopDecision."""
        decision = StopDecision(
            should_stop=True,
            reason=StopReason.EXCELLENT_SCORE,
            message="Score 8.5/10 meets excellent threshold",
            current_iteration=2,
            current_score=8.5,
            soft_limit=3,
            hard_limit=4,
        )
        assert decision.should_stop is True
        assert decision.reason == StopReason.EXCELLENT_SCORE
        assert decision.current_score == 8.5

    def test_to_dict(self):
        """Test converting StopDecision to dictionary."""
        decision = StopDecision(
            should_stop=False,
            reason=StopReason.NONE,
            message="Continue iterating",
            current_iteration=1,
            current_score=5.0,
            soft_limit=3,
            hard_limit=4,
        )
        data = decision.to_dict()
        assert data["should_stop"] is False
        assert data["reason"] == "none"
        assert data["current_score"] == 5.0


# =============================================================================
# StopReason Enum Tests
# =============================================================================


class TestStopReason:
    """Tests for StopReason enum."""

    def test_all_values_exist(self):
        """Test that all expected stop reasons exist."""
        expected = ["none", "excellent_score", "acceptable_at_soft_limit",
                    "plateau_detected", "hard_limit_reached", "manual_stop"]
        for value in expected:
            assert StopReason(value) is not None

    def test_enum_values(self):
        """Test enum value strings."""
        assert StopReason.NONE.value == "none"
        assert StopReason.EXCELLENT_SCORE.value == "excellent_score"
        assert StopReason.ACCEPTABLE_AT_SOFT_LIMIT.value == "acceptable_at_soft_limit"
        assert StopReason.PLATEAU_DETECTED.value == "plateau_detected"
        assert StopReason.HARD_LIMIT_REACHED.value == "hard_limit_reached"
        assert StopReason.MANUAL_STOP.value == "manual_stop"


# =============================================================================
# should_stop() Tests - Core Stopping Rules
# =============================================================================


class TestShouldStopNoIterations:
    """Tests for should_stop with no iterations."""

    def test_no_iterations_does_not_stop(self):
        """Test that empty log does not trigger stop."""
        log = IterationLog(output_type="presentation", target_description="Test")
        decision = should_stop(log)
        assert decision.should_stop is False
        assert decision.reason == StopReason.NONE
        assert decision.current_iteration == 0

    def test_no_iterations_message(self):
        """Test message for empty log."""
        log = IterationLog(output_type="draft", target_description="Test")
        decision = should_stop(log)
        assert "No iterations yet" in decision.message


class TestShouldStopExcellentScore:
    """Tests for Rule 1: Excellent score (>= 8/10)."""

    def test_excellent_score_stops(self):
        """Test that score >= 8 triggers stop."""
        log = IterationLog(
            output_type="presentation",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=8.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.EXCELLENT_SCORE

    def test_excellent_score_8_5(self):
        """Test that score 8.5 triggers stop."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=8.5),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert "8.5" in decision.message

    def test_excellent_score_10(self):
        """Test that perfect score triggers stop."""
        log = IterationLog(
            output_type="hero",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=10.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.EXCELLENT_SCORE

    def test_below_excellent_does_not_stop(self):
        """Test that score 7.9 does not trigger excellent stop."""
        log = IterationLog(
            output_type="presentation",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=7.9),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False
        assert decision.reason == StopReason.NONE

    def test_excellent_threshold_constant(self):
        """Test that EXCELLENT_THRESHOLD is 8.0."""
        assert EXCELLENT_THRESHOLD == 8.0


class TestShouldStopAcceptableAtSoftLimit:
    """Tests for Rule 2: Acceptable score (>= 7/10) at soft limit."""

    def test_acceptable_at_soft_limit_stops_draft(self):
        """Test draft stops at soft limit (2) with score >= 7."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=7.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.ACCEPTABLE_AT_SOFT_LIMIT

    def test_acceptable_at_soft_limit_stops_presentation(self):
        """Test presentation stops at soft limit (3) with score >= 7."""
        log = IterationLog(
            output_type="presentation",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=6.0),
                IterationRecord(3, "t3", "p3", quality_score=7.5),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.ACCEPTABLE_AT_SOFT_LIMIT

    def test_acceptable_at_soft_limit_stops_publication(self):
        """Test publication stops at soft limit (4) with score >= 7."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=5.0 + i * 0.5)
                for i in range(1, 5)
            ],
        )
        # Last score: 5.0 + 4*0.5 = 7.0
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.ACCEPTABLE_AT_SOFT_LIMIT

    def test_below_acceptable_at_soft_limit_continues(self):
        """Test that score 6.9 at soft limit continues."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=6.9),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False

    def test_acceptable_before_soft_limit_continues(self):
        """Test that score >= 7 before soft limit continues."""
        log = IterationLog(
            output_type="presentation",  # soft limit = 3
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=7.5),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False

    def test_acceptable_threshold_constant(self):
        """Test that ACCEPTABLE_THRESHOLD is 7.0."""
        assert ACCEPTABLE_THRESHOLD == 7.0


class TestShouldStopPlateau:
    """Tests for Rule 3: Plateau detection."""

    def test_plateau_detected_two_low_improvements(self):
        """Test plateau detection with 2 consecutive low improvements."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=5.3),
                IterationRecord(3, "t3", "p3", quality_score=5.5),
            ],
        )
        # Improvements: 0.3, 0.2 - both < 0.5
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.PLATEAU_DETECTED

    def test_plateau_detected_no_improvement(self):
        """Test plateau with zero improvements."""
        log = IterationLog(
            output_type="hero",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=6.0),
                IterationRecord(2, "t2", "p2", quality_score=6.0),
                IterationRecord(3, "t3", "p3", quality_score=6.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.PLATEAU_DETECTED

    def test_plateau_detected_negative_improvement(self):
        """Test plateau with negative improvements."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=6.0),
                IterationRecord(2, "t2", "p2", quality_score=5.9),
                IterationRecord(3, "t3", "p3", quality_score=5.8),
            ],
        )
        # Improvements: -0.1, -0.1 - both < 0.5
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.PLATEAU_DETECTED

    def test_no_plateau_with_one_good_improvement(self):
        """Test no plateau when one improvement is >= 0.5."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=5.3),
                IterationRecord(3, "t3", "p3", quality_score=6.0),
            ],
        )
        # Improvements: 0.3, 0.7 - second is >= 0.5
        decision = should_stop(log)
        assert decision.should_stop is False

    def test_no_plateau_with_two_iterations(self):
        """Test no plateau detection with only 2 iterations."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=5.1),
            ],
        )
        decision = should_stop(log)
        # Not enough iterations for plateau detection
        assert decision.reason != StopReason.PLATEAU_DETECTED

    def test_plateau_threshold_constant(self):
        """Test that PLATEAU_THRESHOLD is 0.5."""
        assert PLATEAU_THRESHOLD == 0.5

    def test_plateau_count_constant(self):
        """Test that PLATEAU_COUNT is 2."""
        assert PLATEAU_COUNT == 2


class TestShouldStopHardLimit:
    """Tests for Rule 4: Hard limit reached."""

    def test_hard_limit_draft(self):
        """Test hard limit for draft (3)."""
        # Use increments >= 0.5 to avoid plateau, and scores < 7 at soft limit
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=4.0),
                IterationRecord(2, "t2", "p2", quality_score=5.0),  # soft limit, < 7
                IterationRecord(3, "t3", "p3", quality_score=6.0),  # hard limit
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.HARD_LIMIT_REACHED

    def test_hard_limit_presentation(self):
        """Test hard limit for presentation (4)."""
        log = IterationLog(
            output_type="presentation",
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=4.0 + i * 0.6)
                for i in range(1, 5)
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.HARD_LIMIT_REACHED

    def test_hard_limit_publication(self):
        """Test hard limit for publication (5)."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=4.0 + i * 0.5)
                for i in range(1, 6)
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.HARD_LIMIT_REACHED

    def test_hard_limit_hero(self):
        """Test hard limit for hero (5)."""
        log = IterationLog(
            output_type="hero",
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=4.0 + i * 0.5)
                for i in range(1, 6)
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True

    def test_before_hard_limit_continues(self):
        """Test that iteration before hard limit continues."""
        log = IterationLog(
            output_type="draft",  # hard limit = 3
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=5.8),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False


class TestShouldStopRulePriority:
    """Tests for rule priority order."""

    def test_excellent_takes_priority_over_hard_limit(self):
        """Test excellent score stops before hard limit check."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=8.0)
                for i in range(1, 4)
            ],
        )
        decision = should_stop(log)
        assert decision.reason == StopReason.EXCELLENT_SCORE

    def test_excellent_takes_priority_over_plateau(self):
        """Test excellent score stops before plateau check."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=7.9),
                IterationRecord(2, "t2", "p2", quality_score=8.0),
                IterationRecord(3, "t3", "p3", quality_score=8.0),
            ],
        )
        decision = should_stop(log)
        assert decision.reason == StopReason.EXCELLENT_SCORE

    def test_acceptable_at_soft_limit_takes_priority_over_plateau(self):
        """Test acceptable at soft limit stops before plateau check."""
        log = IterationLog(
            output_type="draft",  # soft limit = 2
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=6.8),
                IterationRecord(2, "t2", "p2", quality_score=7.0),
            ],
        )
        decision = should_stop(log)
        assert decision.reason == StopReason.ACCEPTABLE_AT_SOFT_LIMIT


class TestShouldStopWithNoneScores:
    """Tests for should_stop with None quality scores."""

    def test_all_none_scores_continues_until_hard_limit(self):
        """Test that None scores don't trigger score-based rules."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=None),
                IterationRecord(2, "t2", "p2", quality_score=None),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False
        assert decision.current_score is None

    def test_none_scores_reach_hard_limit(self):
        """Test that None scores reach hard limit."""
        log = IterationLog(
            output_type="draft",  # hard limit = 3
            target_description="Test",
            iterations=[
                IterationRecord(i, f"t{i}", f"p{i}", quality_score=None)
                for i in range(1, 4)
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.HARD_LIMIT_REACHED


# =============================================================================
# Limit Constants Tests
# =============================================================================


class TestLimitConstants:
    """Tests for limit constants."""

    def test_soft_limits(self):
        """Test SOFT_LIMITS values."""
        assert SOFT_LIMITS["draft"] == 2
        assert SOFT_LIMITS["presentation"] == 3
        assert SOFT_LIMITS["publication"] == 4
        assert SOFT_LIMITS["hero"] == 4

    def test_hard_limits(self):
        """Test HARD_LIMITS values."""
        assert HARD_LIMITS["draft"] == 3
        assert HARD_LIMITS["presentation"] == 4
        assert HARD_LIMITS["publication"] == 5
        assert HARD_LIMITS["hero"] == 5

    def test_hard_greater_than_soft(self):
        """Test that hard limit > soft limit for all types."""
        for output_type in SOFT_LIMITS:
            assert HARD_LIMITS[output_type] > SOFT_LIMITS[output_type]


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestCreateIterationLog:
    """Tests for create_iteration_log function."""

    def test_creates_empty_log(self):
        """Test creating a new iteration log."""
        log = create_iteration_log("presentation", "Test image")
        assert log.output_type == "presentation"
        assert log.target_description == "Test image"
        assert log.iteration_count == 0
        assert log.completed is False

    def test_sets_created_at(self):
        """Test that created_at is set."""
        log = create_iteration_log("draft", "Test")
        assert log.created_at is not None
        assert "T" in log.created_at  # ISO format


class TestAddIteration:
    """Tests for add_iteration function."""

    def test_adds_iteration(self):
        """Test adding an iteration."""
        log = create_iteration_log("draft", "Test")
        record = add_iteration(log, "test prompt", quality_score=6.0)
        assert log.iteration_count == 1
        assert record.attempt == 1
        assert record.quality_score == 6.0

    def test_increments_attempt_number(self):
        """Test that attempt numbers increment."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt 1")
        add_iteration(log, "prompt 2")
        add_iteration(log, "prompt 3")
        assert log.iterations[0].attempt == 1
        assert log.iterations[1].attempt == 2
        assert log.iterations[2].attempt == 3

    def test_adds_all_fields(self):
        """Test that all fields are set."""
        log = create_iteration_log("presentation", "Test")
        record = add_iteration(
            log,
            prompt="detailed prompt",
            quality_score=7.5,
            notes="Good progress",
            model="test/model",
            resolution=(1024, 1024),
            success=True,
        )
        assert record.prompt == "detailed prompt"
        assert record.notes == "Good progress"
        assert record.model == "test/model"
        assert record.resolution == (1024, 1024)

    def test_adds_failed_iteration(self):
        """Test adding a failed iteration."""
        log = create_iteration_log("draft", "Test")
        record = add_iteration(
            log,
            prompt="test",
            success=False,
            error="API error",
        )
        assert record.success is False
        assert record.error == "API error"


class TestCompleteLog:
    """Tests for complete_log function."""

    def test_marks_completed(self):
        """Test that complete_log marks log as completed."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=8.0)
        complete_log(log)
        assert log.completed is True

    def test_sets_final_score(self):
        """Test that final score is set."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=7.5)
        complete_log(log)
        assert log.final_score == 7.5

    def test_explicit_final_score(self):
        """Test setting explicit final score."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=7.0)
        complete_log(log, final_score=7.5)
        assert log.final_score == 7.5

    def test_sets_stop_reason(self):
        """Test that stop reason is set."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=8.5)
        complete_log(log)
        assert log.stop_reason == "excellent_score"

    def test_explicit_stop_reason(self):
        """Test setting explicit stop reason."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=6.0)
        complete_log(log, stop_reason=StopReason.MANUAL_STOP)
        assert log.stop_reason == "manual_stop"


class TestValidateOutputType:
    """Tests for validate_output_type function."""

    def test_valid_types(self):
        """Test all valid output types."""
        for output_type in ["draft", "presentation", "publication", "hero"]:
            valid, error = validate_output_type(output_type)
            assert valid is True
            assert error is None

    def test_invalid_type(self):
        """Test invalid output type."""
        valid, error = validate_output_type("invalid")
        assert valid is False
        assert "Invalid output type" in error

    def test_case_sensitive(self):
        """Test that validation is case sensitive."""
        valid, error = validate_output_type("Draft")
        assert valid is False


class TestGetLimitsForType:
    """Tests for get_limits_for_type function."""

    def test_draft_limits(self):
        """Test limits for draft."""
        soft, hard = get_limits_for_type("draft")
        assert soft == 2
        assert hard == 3

    def test_presentation_limits(self):
        """Test limits for presentation."""
        soft, hard = get_limits_for_type("presentation")
        assert soft == 3
        assert hard == 4

    def test_publication_limits(self):
        """Test limits for publication."""
        soft, hard = get_limits_for_type("publication")
        assert soft == 4
        assert hard == 5

    def test_hero_limits(self):
        """Test limits for hero."""
        soft, hard = get_limits_for_type("hero")
        assert soft == 4
        assert hard == 5


# =============================================================================
# Persistence Tests
# =============================================================================


class TestSaveAndLoadIterationLog:
    """Tests for save/load iteration log functions."""

    def test_save_creates_file(self):
        """Test that save creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = create_iteration_log("draft", "Test")
            path = save_iteration_log(log, f"{tmpdir}/test.iterations.json")
            assert Path(path).exists()

    def test_save_and_load_roundtrip(self):
        """Test save and load roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = create_iteration_log("presentation", "Complex test")
            add_iteration(log, "prompt 1", quality_score=5.0)
            add_iteration(log, "prompt 2", quality_score=7.0)
            complete_log(log)

            path = save_iteration_log(log, f"{tmpdir}/test.iterations.json")
            loaded = load_iteration_log(path)

            assert loaded is not None
            assert loaded.output_type == "presentation"
            assert loaded.iteration_count == 2
            assert loaded.completed is True

    def test_save_with_image_path(self):
        """Test saving with image path (auto-suffix)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = create_iteration_log("draft", "Test")
            path = save_iteration_log(log, f"{tmpdir}/image.png")
            assert path.endswith(".iterations.json")
            assert Path(path).exists()

    def test_load_nonexistent_returns_none(self):
        """Test loading nonexistent file returns None."""
        result = load_iteration_log("/nonexistent/path/file.json")
        assert result is None

    def test_load_with_image_path(self):
        """Test loading with image path (auto-suffix)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = create_iteration_log("draft", "Test")
            save_iteration_log(log, f"{tmpdir}/image.png")
            loaded = load_iteration_log(f"{tmpdir}/image.png")
            assert loaded is not None

    def test_load_corrupted_returns_none(self):
        """Test loading corrupted JSON returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/test.iterations.json"
            with open(path, "w") as f:
                f.write("not valid json")
            result = load_iteration_log(path)
            assert result is None


class TestGetOrCreateLog:
    """Tests for get_or_create_log function."""

    def test_creates_new_log(self):
        """Test creating new log when none exists."""
        log = get_or_create_log("/nonexistent/path.png", "draft", "Test")
        assert log is not None
        assert log.output_type == "draft"
        assert log.iteration_count == 0

    def test_loads_existing_log(self):
        """Test loading existing log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save a log
            original = create_iteration_log("presentation", "Existing")
            add_iteration(original, "prompt", quality_score=6.0)
            save_iteration_log(original, f"{tmpdir}/image.png")

            # Load it
            loaded = get_or_create_log(f"{tmpdir}/image.png", "draft", "New")
            assert loaded.output_type == "presentation"  # Original type
            assert loaded.target_description == "Existing"
            assert loaded.iteration_count == 1


# =============================================================================
# Formatting Tests
# =============================================================================


class TestFormatIterationLog:
    """Tests for format_iteration_log function."""

    def test_formats_empty_log(self):
        """Test formatting empty log."""
        log = create_iteration_log("draft", "Test image")
        output = format_iteration_log(log)
        assert "Test image" in output
        assert "draft" in output

    def test_formats_iterations(self):
        """Test formatting log with iterations."""
        log = create_iteration_log("presentation", "Complex image")
        add_iteration(log, "prompt 1", quality_score=5.0, notes="First try")
        add_iteration(log, "prompt 2", quality_score=7.0)
        output = format_iteration_log(log)
        assert "5.0/10" in output
        assert "7.0/10" in output
        assert "First try" in output

    def test_formats_completed_log(self):
        """Test formatting completed log."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=8.5)
        complete_log(log)
        output = format_iteration_log(log)
        assert "Completed" in output
        assert "8.5" in output


class TestGetIterationStats:
    """Tests for get_iteration_stats function."""

    def test_empty_log_stats(self):
        """Test stats for empty log."""
        log = create_iteration_log("draft", "Test")
        stats = get_iteration_stats(log)
        assert stats["total_iterations"] == 0
        assert stats["latest_score"] is None
        assert stats["best_score"] is None

    def test_populated_log_stats(self):
        """Test stats for populated log."""
        log = create_iteration_log("presentation", "Test")
        add_iteration(log, "p1", quality_score=5.0)
        add_iteration(log, "p2", quality_score=7.0)
        add_iteration(log, "p3", quality_score=6.5)

        stats = get_iteration_stats(log)
        assert stats["total_iterations"] == 3
        assert stats["successful_iterations"] == 3
        assert stats["latest_score"] == 6.5
        assert stats["best_score"] == 7.0
        assert stats["worst_score"] == 5.0
        assert stats["score_range"] == 2.0  # 7.0 - 5.0
        assert stats["total_improvement"] == 1.5  # 6.5 - 5.0

    def test_stats_with_failures(self):
        """Test stats with failed iterations."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "p1", quality_score=5.0, success=True)
        add_iteration(log, "p2", success=False, error="API error")

        stats = get_iteration_stats(log)
        assert stats["successful_iterations"] == 1
        assert stats["failed_iterations"] == 1


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_score_exactly_at_thresholds(self):
        """Test scores exactly at threshold values."""
        # Exactly 8.0 (excellent threshold)
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[IterationRecord(1, "t1", "p1", quality_score=8.0)],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.EXCELLENT_SCORE

        # Exactly 7.0 at soft limit
        log2 = IterationLog(
            output_type="draft",  # soft = 2
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=7.0),
            ],
        )
        decision2 = should_stop(log2)
        assert decision2.should_stop is True

    def test_improvement_exactly_at_plateau_threshold(self):
        """Test improvement exactly at 0.5 (not plateau)."""
        log = IterationLog(
            output_type="publication",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=5.0),
                IterationRecord(2, "t2", "p2", quality_score=5.5),
                IterationRecord(3, "t3", "p3", quality_score=6.0),
            ],
        )
        # Improvements: 0.5, 0.5 - exactly at threshold, not below
        decision = should_stop(log)
        assert decision.reason != StopReason.PLATEAU_DETECTED

    def test_very_long_prompt_truncated_in_format(self):
        """Test that very long prompts are truncated in formatting."""
        log = create_iteration_log("draft", "Test")
        long_prompt = "x" * 200
        add_iteration(log, long_prompt, quality_score=5.0)
        output = format_iteration_log(log)
        assert "..." in output
        assert len(output) < len(long_prompt) + 500

    def test_negative_scores(self):
        """Test handling of negative scores (edge case)."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=-1.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is False
        assert decision.current_score == -1.0

    def test_zero_score_displays_correctly(self):
        """Test that a score of 0.0 displays as '0.0/10' not 'N/A'."""
        log = create_iteration_log("draft", "Test")
        add_iteration(log, "prompt", quality_score=0.0)
        output = format_iteration_log(log)
        assert "0.0/10" in output
        assert "N/A" not in output or "N/A" not in output.split("0.0/10")[0]

    def test_score_above_10(self):
        """Test handling of scores above 10 (edge case)."""
        log = IterationLog(
            output_type="draft",
            target_description="Test",
            iterations=[
                IterationRecord(1, "t1", "p1", quality_score=11.0),
            ],
        )
        decision = should_stop(log)
        assert decision.should_stop is True
        assert decision.reason == StopReason.EXCELLENT_SCORE

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        log = create_iteration_log("draft", "Test")
        record = add_iteration(log, "", quality_score=5.0)
        assert record.prompt == ""
        assert log.iteration_count == 1

    def test_empty_target_description(self):
        """Test handling of empty target description."""
        log = create_iteration_log("draft", "")
        assert log.target_description == ""
