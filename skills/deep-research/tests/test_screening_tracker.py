#!/usr/bin/env python3
"""
Tests for screening_tracker.py

Comprehensive test suite for screening audit trail tracking with
inter-rater agreement calculation (kappa) and dual screening support.
"""

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from screening_tracker import (  # noqa: E402
    ScreeningRecord,
    DualScreeningPair,
    ScreeningSession,
    ExclusionReason,
    TIMING_THRESHOLDS,
    KAPPA_INTERPRETATION,
    create_record,
    create_dual_pair,
    load_session_from_json,
    save_session_to_json,
    generate_audit_report,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_timing_thresholds_defined(self):
        """Test timing thresholds are defined for all stages."""
        assert "title" in TIMING_THRESHOLDS
        assert "abstract" in TIMING_THRESHOLDS
        assert "full_text" in TIMING_THRESHOLDS

    def test_timing_threshold_values(self):
        """Test timing thresholds match skill documentation."""
        assert TIMING_THRESHOLDS["title"] == 15
        assert TIMING_THRESHOLDS["abstract"] == 120
        assert TIMING_THRESHOLDS["full_text"] == 900

    def test_kappa_interpretation_covers_range(self):
        """Test kappa interpretation covers full range."""
        # Check that all key ranges are covered
        interpretations = list(KAPPA_INTERPRETATION.values())
        assert "almost perfect" in interpretations
        assert "substantial" in interpretations
        assert "moderate" in interpretations
        assert "fair" in interpretations
        assert "slight" in interpretations
        assert "poor" in interpretations


class TestExclusionReason:
    """Tests for ExclusionReason enum."""

    def test_exclusion_reasons_defined(self):
        """Test all standard exclusion reasons exist."""
        assert ExclusionReason.WRONG_POPULATION.value == "wrong_population"
        assert ExclusionReason.WRONG_INTERVENTION.value == "wrong_intervention"
        assert ExclusionReason.WRONG_OUTCOME.value == "wrong_outcome"
        assert ExclusionReason.WRONG_STUDY_DESIGN.value == "wrong_study_design"
        assert ExclusionReason.DUPLICATE.value == "duplicate"
        assert ExclusionReason.OTHER.value == "other"

    def test_exclusion_reason_count(self):
        """Test number of exclusion reasons."""
        assert len(ExclusionReason) == 12


# =============================================================================
# ScreeningRecord Tests
# =============================================================================


class TestScreeningRecord:
    """Tests for ScreeningRecord dataclass."""

    @pytest.fixture
    def valid_record(self):
        """Fixture for a valid screening record."""
        return ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=45,
        )

    def test_valid_record_passes_validation(self, valid_record):
        """Test valid record has no errors."""
        errors = valid_record.validate()
        assert len(errors) == 0
        assert valid_record.is_valid()

    def test_record_missing_record_id(self):
        """Test validation fails without record ID."""
        record = ScreeningRecord(
            record_id="",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Record ID is required" in e for e in errors)

    def test_record_missing_reviewer_id(self):
        """Test validation fails without reviewer ID."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Reviewer ID is required" in e for e in errors)

    def test_record_invalid_stage(self):
        """Test validation fails with invalid stage."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="invalid_stage",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Invalid stage" in e for e in errors)

    def test_record_invalid_decision(self):
        """Test validation fails with invalid decision."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="invalid_decision",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Invalid decision" in e for e in errors)

    def test_record_exclude_requires_reason(self):
        """Test exclude decision requires exclusion reason."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="exclude",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Exclusion reason required" in e for e in errors)

    def test_record_exclude_with_reason_valid(self):
        """Test exclude decision with reason is valid."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="exclude",
            timestamp=datetime.now().isoformat(),
            exclusion_reason="wrong_population",
        )
        errors = record.validate()
        assert len(errors) == 0

    def test_record_invalid_timestamp(self):
        """Test validation fails with invalid timestamp."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp="not-a-timestamp",
        )
        errors = record.validate()
        assert any("Invalid timestamp" in e for e in errors)


class TestScreeningRecordTiming:
    """Tests for timing checks."""

    def test_timing_within_limit(self):
        """Test timing check passes when within limit."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="title",
            decision="include",
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=10,
        )
        result = record.check_timing()
        assert result["within_limit"] is True
        assert result["warning"] is None

    def test_timing_exceeds_limit(self):
        """Test timing check warns when exceeding limit."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="title",
            decision="include",
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=30,  # Exceeds 15s threshold
        )
        result = record.check_timing()
        assert result["within_limit"] is False
        assert "exceeds" in result["warning"]

    def test_timing_too_quick(self):
        """Test timing check warns when too quick."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=1,  # Too quick
        )
        result = record.check_timing()
        assert result["within_limit"] is False
        assert "too quick" in result["warning"]

    def test_timing_no_time_recorded(self):
        """Test timing check handles missing time."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        result = record.check_timing()
        assert result["time_spent"] is None
        assert result["within_limit"] is True


class TestScreeningRecordSerialization:
    """Tests for record serialization."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        record = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp="2024-01-15T10:30:00",
            time_spent_seconds=45,
            notes="Test note",
        )
        d = record.to_dict()
        assert d["record_id"] == "PMC123456"
        assert d["reviewer_id"] == "reviewer_a"
        assert d["stage"] == "abstract"
        assert d["decision"] == "include"
        assert d["time_spent_seconds"] == 45
        assert d["notes"] == "Test note"


# =============================================================================
# DualScreeningPair Tests
# =============================================================================


class TestDualScreeningPair:
    """Tests for DualScreeningPair dataclass."""

    @pytest.fixture
    def agreeing_pair(self):
        """Fixture for a pair with agreement."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        return DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)

    @pytest.fixture
    def disagreeing_pair(self):
        """Fixture for a pair with disagreement."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="exclude",
            timestamp=datetime.now().isoformat(),
            exclusion_reason="wrong_population",
        )
        return DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)

    def test_agreement_detected(self, agreeing_pair):
        """Test agreement is correctly detected."""
        assert agreeing_pair.has_agreement() is True
        assert agreeing_pair.get_disagreement_type() is None

    def test_disagreement_detected(self, disagreeing_pair):
        """Test disagreement is correctly detected."""
        assert disagreeing_pair.has_agreement() is False
        assert disagreeing_pair.get_disagreement_type() == "critical"

    def test_critical_disagreement(self, disagreeing_pair):
        """Test include/exclude disagreement is critical."""
        assert disagreeing_pair.get_disagreement_type() == "critical"

    def test_uncertain_disagreement(self):
        """Test maybe disagreement is uncertain."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="maybe",
            timestamp=datetime.now().isoformat(),
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        assert pair.get_disagreement_type() == "uncertain"

    def test_resolve_disagreement(self, disagreeing_pair):
        """Test conflict resolution."""
        disagreeing_pair.resolve("include", "senior_reviewer", "Discussed and agreed")
        assert disagreeing_pair.final_decision == "include"
        assert disagreeing_pair.resolved_by == "senior_reviewer"
        assert disagreeing_pair.resolution_notes == "Discussed and agreed"
        assert disagreeing_pair.resolved_at != ""

    def test_get_final_decision_agreement(self, agreeing_pair):
        """Test final decision for agreeing pair."""
        assert agreeing_pair.get_final_decision() == "include"

    def test_get_final_decision_resolved(self, disagreeing_pair):
        """Test final decision for resolved pair."""
        disagreeing_pair.resolve("exclude", "senior_reviewer")
        assert disagreeing_pair.get_final_decision() == "exclude"

    def test_get_final_decision_unresolved(self, disagreeing_pair):
        """Test final decision for unresolved pair."""
        assert disagreeing_pair.get_final_decision() == "conflict"


class TestDualScreeningPairValidation:
    """Tests for dual pair validation."""

    def test_valid_pair(self):
        """Test valid pair passes validation."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        errors = pair.validate()
        assert len(errors) == 0

    def test_mismatched_record_ids(self):
        """Test validation fails with mismatched record IDs."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC789012",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        errors = pair.validate()
        assert any("Record IDs do not match" in e for e in errors)

    def test_mismatched_stages(self):
        """Test validation fails with mismatched stages."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="title",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        errors = pair.validate()
        assert any("stages do not match" in e for e in errors)

    def test_same_reviewer(self):
        """Test validation fails with same reviewer."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",  # Same reviewer
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        errors = pair.validate()
        assert any("different reviewers" in e for e in errors)

    def test_unresolved_disagreement(self):
        """Test validation fails for unresolved disagreement."""
        r1 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        r2 = ScreeningRecord(
            record_id="PMC123456",
            reviewer_id="reviewer_b",
            stage="abstract",
            decision="exclude",
            timestamp=datetime.now().isoformat(),
            exclusion_reason="wrong_population",
        )
        pair = DualScreeningPair(record_id="PMC123456", reviewer1=r1, reviewer2=r2)
        errors = pair.validate()
        assert any("resolution" in e for e in errors)


# =============================================================================
# ScreeningSession Tests
# =============================================================================


class TestScreeningSession:
    """Tests for ScreeningSession collection."""

    @pytest.fixture
    def session_with_records(self):
        """Fixture for session with multiple records."""
        session = ScreeningSession(review_id="SR2024-001", stage="abstract")
        records = [
            create_record("PMC001", "reviewer_a", "abstract", "include", time_spent_seconds=30),
            create_record("PMC002", "reviewer_a", "abstract", "exclude",
                         exclusion_reason="wrong_population", time_spent_seconds=25),
            create_record("PMC003", "reviewer_a", "abstract", "include", time_spent_seconds=45),
            create_record("PMC001", "reviewer_b", "abstract", "include", time_spent_seconds=35),
            create_record("PMC002", "reviewer_b", "abstract", "exclude",
                         exclusion_reason="wrong_population", time_spent_seconds=28),
            create_record("PMC003", "reviewer_b", "abstract", "maybe", time_spent_seconds=60),
        ]
        for r in records:
            session.add_record(r)
        return session

    def test_add_record(self, session_with_records):
        """Test adding records to session."""
        assert len(session_with_records.records) == 6

    def test_get_reviewers(self, session_with_records):
        """Test getting unique reviewers."""
        reviewers = session_with_records.get_reviewers()
        assert "reviewer_a" in reviewers
        assert "reviewer_b" in reviewers
        assert len(reviewers) == 2

    def test_get_records_by_reviewer(self, session_with_records):
        """Test filtering records by reviewer."""
        records = session_with_records.get_records_by_reviewer("reviewer_a")
        assert len(records) == 3
        assert all(r.reviewer_id == "reviewer_a" for r in records)


class TestScreeningSessionKappa:
    """Tests for kappa calculation."""

    def test_kappa_perfect_agreement(self):
        """Test kappa = 1.0 for perfect agreement."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        # All agree on include
        for i in range(10):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "include")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            session.add_dual_pair(pair)

        kappa = session.calculate_kappa()
        assert kappa == 1.0

    def test_kappa_no_agreement(self):
        """Test kappa for complete disagreement."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        # Complete disagreement
        for i in range(5):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "exclude",
                              exclusion_reason="wrong_population")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            pair.resolve("include", "senior")  # Resolve for validation
            session.add_dual_pair(pair)
        for i in range(5, 10):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "exclude",
                              exclusion_reason="wrong_population")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "include")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            pair.resolve("include", "senior")
            session.add_dual_pair(pair)

        kappa = session.calculate_kappa()
        assert kappa is not None
        assert kappa < 0.2  # Poor agreement

    def test_kappa_insufficient_data(self):
        """Test kappa returns None with insufficient data."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        # Only one pair
        r1 = create_record("PMC001", "rev_a", "abstract", "include")
        r2 = create_record("PMC001", "rev_b", "abstract", "include")
        pair = create_dual_pair("PMC001", r1, r2)
        session.add_dual_pair(pair)

        kappa = session.calculate_kappa()
        assert kappa is None

    def test_interpret_kappa_almost_perfect(self):
        """Test kappa interpretation for high values."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        assert session.interpret_kappa(0.85) == "almost perfect"

    def test_interpret_kappa_substantial(self):
        """Test kappa interpretation for substantial values."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        assert session.interpret_kappa(0.70) == "substantial"

    def test_interpret_kappa_moderate(self):
        """Test kappa interpretation for moderate values."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        assert session.interpret_kappa(0.50) == "moderate"

    def test_interpret_kappa_none(self):
        """Test kappa interpretation for None."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        assert session.interpret_kappa(None) == "insufficient data"

    def test_check_kappa_threshold_pass(self):
        """Test kappa threshold check passes."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        for i in range(10):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "include")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            session.add_dual_pair(pair)

        result = session.check_kappa_threshold()
        assert result["meets_threshold"] is True

    def test_check_kappa_threshold_fail(self):
        """Test kappa threshold check fails."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        # Mixed agreement pattern
        for i in range(3):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "include")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            session.add_dual_pair(pair)

        for i in range(3, 6):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "exclude",
                              exclusion_reason="wrong_population")
            pair = create_dual_pair(f"PMC{i}", r1, r2)
            pair.resolve("include", "senior")
            session.add_dual_pair(pair)

        result = session.check_kappa_threshold()
        # With 50% disagreement, kappa should be below 0.8
        assert result["meets_threshold"] is False
        assert "calibration" in result["recommendation"]


class TestScreeningSessionStatistics:
    """Tests for session statistics."""

    @pytest.fixture
    def session_with_data(self):
        """Fixture for session with complete data."""
        session = ScreeningSession(review_id="SR2024-001", stage="abstract")

        # Add records
        records_data = [
            ("PMC001", "rev_a", "include", 30),
            ("PMC002", "rev_a", "exclude", 25),
            ("PMC003", "rev_a", "include", 45),
            ("PMC004", "rev_a", "maybe", 60),
            ("PMC001", "rev_b", "include", 35),
            ("PMC002", "rev_b", "exclude", 28),
            ("PMC003", "rev_b", "include", 50),
            ("PMC004", "rev_b", "include", 40),
        ]

        for rid, reviewer, decision, time in records_data:
            if decision == "exclude":
                r = create_record(rid, reviewer, "abstract", decision,
                                 exclusion_reason="wrong_population",
                                 time_spent_seconds=time)
            else:
                r = create_record(rid, reviewer, "abstract", decision,
                                 time_spent_seconds=time)
            session.add_record(r)

        # Add dual pairs
        pairs_indices = [(0, 4), (1, 5), (2, 6), (3, 7)]
        for i1, i2 in pairs_indices:
            r1 = session.records[i1]
            r2 = session.records[i2]
            pair = create_dual_pair(r1.record_id, r1, r2)
            if not pair.has_agreement():
                pair.resolve("include", "senior")
            session.add_dual_pair(pair)

        return session

    def test_statistics_total_records(self, session_with_data):
        """Test statistics counts total records."""
        stats = session_with_data.get_statistics()
        assert stats["total_records"] == 8

    def test_statistics_unique_papers(self, session_with_data):
        """Test statistics counts unique papers."""
        stats = session_with_data.get_statistics()
        assert stats["unique_papers"] == 4

    def test_statistics_decisions(self, session_with_data):
        """Test statistics counts decisions."""
        stats = session_with_data.get_statistics()
        assert "include" in stats["decisions"]
        assert "exclude" in stats["decisions"]

    def test_statistics_exclusion_reasons(self, session_with_data):
        """Test statistics tracks exclusion reasons."""
        stats = session_with_data.get_statistics()
        assert "wrong_population" in stats["exclusion_reasons"]
        assert stats["exclusion_reasons"]["wrong_population"] == 2

    def test_statistics_average_time(self, session_with_data):
        """Test statistics calculates average time."""
        stats = session_with_data.get_statistics()
        assert stats["average_time_seconds"] is not None
        assert stats["average_time_seconds"] > 0

    def test_statistics_kappa_included(self, session_with_data):
        """Test statistics includes kappa."""
        stats = session_with_data.get_statistics()
        assert "kappa" in stats
        assert "kappa_interpretation" in stats

    def test_statistics_empty_session(self):
        """Test statistics for empty session."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        stats = session.get_statistics()
        assert stats["total_records"] == 0


class TestScreeningSessionValidation:
    """Tests for session validation."""

    def test_valid_session(self):
        """Test valid session passes validation."""
        session = ScreeningSession(review_id="SR2024-001", stage="abstract")
        r = create_record("PMC001", "rev_a", "abstract", "include")
        session.add_record(r)
        errors = session.validate()
        assert len(errors) == 0
        assert session.is_valid()

    def test_missing_review_id(self):
        """Test validation fails without review ID."""
        session = ScreeningSession(review_id="", stage="abstract")
        errors = session.validate()
        assert any("Review ID is required" in e for e in errors)

    def test_invalid_stage(self):
        """Test validation fails with invalid stage."""
        session = ScreeningSession(review_id="SR001", stage="invalid")
        errors = session.validate()
        assert any("Invalid stage" in e for e in errors)

    def test_stage_mismatch(self):
        """Test validation fails with mismatched record stage."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        r = create_record("PMC001", "rev_a", "title", "include")  # Wrong stage
        session.add_record(r)
        errors = session.validate()
        assert any("Stage mismatch" in e for e in errors)

    def test_duplicate_record_ids(self):
        """Test validation fails with duplicate record IDs for same reviewer."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        r1 = create_record("PMC001", "rev_a", "abstract", "include")
        r2 = create_record("PMC001", "rev_a", "abstract", "exclude",
                          exclusion_reason="wrong_population")  # Same ID, same reviewer
        session.add_record(r1)
        session.add_record(r2)
        errors = session.validate()
        assert any("duplicate record IDs" in e for e in errors)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_record_basic(self):
        """Test create_record basic functionality."""
        record = create_record("PMC001", "rev_a", "abstract", "include")
        assert record.record_id == "PMC001"
        assert record.reviewer_id == "rev_a"
        assert record.stage == "abstract"
        assert record.decision == "include"
        assert record.timestamp  # Auto-generated

    def test_create_record_with_exclusion(self):
        """Test create_record with exclusion details."""
        record = create_record(
            "PMC001", "rev_a", "abstract", "exclude",
            exclusion_reason="wrong_population",
            exclusion_detail="Adults only, not pediatric",
        )
        assert record.exclusion_reason == "wrong_population"
        assert record.exclusion_detail == "Adults only, not pediatric"

    def test_create_record_with_timing(self):
        """Test create_record with timing."""
        record = create_record(
            "PMC001", "rev_a", "abstract", "include",
            time_spent_seconds=45,
        )
        assert record.time_spent_seconds == 45

    def test_create_dual_pair(self):
        """Test create_dual_pair functionality."""
        r1 = create_record("PMC001", "rev_a", "abstract", "include")
        r2 = create_record("PMC001", "rev_b", "abstract", "include")
        pair = create_dual_pair("PMC001", r1, r2)
        assert pair.record_id == "PMC001"
        assert pair.reviewer1 == r1
        assert pair.reviewer2 == r2


# =============================================================================
# JSON Serialization Tests
# =============================================================================


class TestJSONSerialization:
    """Tests for JSON save/load functions."""

    def test_save_and_load_session(self):
        """Test round-trip JSON serialization."""
        session = ScreeningSession(review_id="SR2024-001", stage="abstract")
        r1 = create_record("PMC001", "rev_a", "abstract", "include", time_spent_seconds=30)
        r2 = create_record("PMC001", "rev_b", "abstract", "include", time_spent_seconds=35)
        session.add_record(r1)
        session.add_record(r2)

        pair = create_dual_pair("PMC001", r1, r2)
        session.add_dual_pair(pair)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_session_to_json(session, filepath)
            loaded = load_session_from_json(filepath)

            assert loaded.review_id == "SR2024-001"
            assert loaded.stage == "abstract"
            assert len(loaded.records) == 2
            assert len(loaded.dual_pairs) == 1
        finally:
            Path(filepath).unlink()

    def test_json_structure(self):
        """Test JSON has correct structure."""
        session = ScreeningSession(review_id="SR001", stage="title")
        r = create_record("PMC001", "rev_a", "title", "include")
        session.add_record(r)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_session_to_json(session, filepath)

            with open(filepath) as f:
                data = json.load(f)

            assert "review_id" in data
            assert "stage" in data
            assert "records" in data
            assert "dual_pairs" in data
            assert "statistics" in data
        finally:
            Path(filepath).unlink()


# =============================================================================
# Audit Report Tests
# =============================================================================


class TestAuditReport:
    """Tests for audit report generation."""

    def test_generate_report_basic(self):
        """Test basic report generation."""
        session = ScreeningSession(review_id="SR2024-001", stage="abstract")
        r = create_record("PMC001", "rev_a", "abstract", "include", time_spent_seconds=30)
        session.add_record(r)

        report = generate_audit_report(session)
        assert "SCREENING AUDIT REPORT" in report
        assert "SR2024-001" in report
        assert "abstract" in report

    def test_report_includes_statistics(self):
        """Test report includes statistics."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        session.add_record(create_record("PMC001", "rev_a", "abstract", "include"))
        session.add_record(create_record("PMC002", "rev_a", "abstract", "exclude",
                                        exclusion_reason="wrong_population"))

        report = generate_audit_report(session)
        assert "DECISIONS" in report
        assert "include" in report
        assert "exclude" in report

    def test_report_includes_kappa(self):
        """Test report includes kappa when dual pairs present."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        for i in range(5):
            r1 = create_record(f"PMC{i}", "rev_a", "abstract", "include")
            r2 = create_record(f"PMC{i}", "rev_b", "abstract", "include")
            session.add_record(r1)
            session.add_record(r2)
            session.add_dual_pair(create_dual_pair(f"PMC{i}", r1, r2))

        report = generate_audit_report(session)
        assert "INTER-RATER AGREEMENT" in report
        assert "Kappa" in report

    def test_report_includes_validation(self):
        """Test report includes validation section."""
        session = ScreeningSession(review_id="SR001", stage="abstract")
        session.add_record(create_record("PMC001", "rev_a", "abstract", "include"))

        report = generate_audit_report(session)
        assert "VALIDATION" in report


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_all_stages(self):
        """Test all screening stages work."""
        for stage in ["title", "abstract", "full_text"]:
            session = ScreeningSession(review_id="SR001", stage=stage)
            r = create_record("PMC001", "rev_a", stage, "include")
            session.add_record(r)
            assert session.is_valid()

    def test_all_decisions(self):
        """Test all decision types work."""
        for decision in ["include", "maybe", "conflict"]:
            r = create_record("PMC001", "rev_a", "abstract", decision)
            assert r.is_valid()

        # Exclude needs reason
        r = create_record("PMC001", "rev_a", "abstract", "exclude",
                         exclusion_reason="wrong_population")
        assert r.is_valid()

    def test_all_exclusion_reasons(self):
        """Test all exclusion reasons work."""
        for reason in ExclusionReason:
            r = create_record("PMC001", "rev_a", "abstract", "exclude",
                             exclusion_reason=reason.value)
            assert r.is_valid()

    def test_large_session(self):
        """Test session with many records."""
        session = ScreeningSession(review_id="SR001", stage="abstract")

        for i in range(100):
            decision = "include" if i % 3 == 0 else "exclude"
            if decision == "exclude":
                r = create_record(f"PMC{i}", "rev_a", "abstract", decision,
                                 exclusion_reason="wrong_population")
            else:
                r = create_record(f"PMC{i}", "rev_a", "abstract", decision)
            session.add_record(r)

        stats = session.get_statistics()
        assert stats["total_records"] == 100

    def test_whitespace_record_id(self):
        """Test whitespace-only record ID fails."""
        record = ScreeningRecord(
            record_id="   ",
            reviewer_id="rev_a",
            stage="abstract",
            decision="include",
            timestamp=datetime.now().isoformat(),
        )
        errors = record.validate()
        assert any("Record ID is required" in e for e in errors)

    def test_timing_boundary_values(self):
        """Test timing at exact boundaries."""
        # Exactly at threshold
        record = ScreeningRecord(
            record_id="PMC001",
            reviewer_id="rev_a",
            stage="title",
            decision="include",
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=15,  # Exactly at threshold
        )
        result = record.check_timing()
        assert result["within_limit"] is True

        # One second over
        record.time_spent_seconds = 16
        result = record.check_timing()
        assert result["within_limit"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
