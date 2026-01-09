#!/usr/bin/env python3
"""
Screening Tracker

Provides audit trail tracking for literature review screening decisions.
Supports dual screening, inter-rater agreement calculation (kappa),
and stage-specific decision tracking.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Literal, Optional, Any
from enum import Enum
import json


# Type definitions
ScreeningStage = Literal["title", "abstract", "full_text"]
ScreeningDecision = Literal["include", "exclude", "maybe", "conflict"]


class ExclusionReason(Enum):
    """Standard exclusion reasons for systematic reviews."""

    WRONG_POPULATION = "wrong_population"
    WRONG_INTERVENTION = "wrong_intervention"
    WRONG_COMPARATOR = "wrong_comparator"
    WRONG_OUTCOME = "wrong_outcome"
    WRONG_STUDY_DESIGN = "wrong_study_design"
    DUPLICATE = "duplicate"
    NOT_RETRIEVABLE = "not_retrievable"
    WRONG_PUBLICATION_TYPE = "wrong_publication_type"
    WRONG_LANGUAGE = "wrong_language"
    WRONG_DATE_RANGE = "wrong_date_range"
    INSUFFICIENT_DATA = "insufficient_data"
    OTHER = "other"


# Timing thresholds from skill documentation
TIMING_THRESHOLDS = {
    "title": 15,  # seconds
    "abstract": 120,  # 2 minutes
    "full_text": 900,  # 15 minutes
}

# Inter-rater agreement interpretation
KAPPA_INTERPRETATION = {
    (0.81, 1.00): "almost perfect",
    (0.61, 0.80): "substantial",
    (0.41, 0.60): "moderate",
    (0.21, 0.40): "fair",
    (0.00, 0.20): "slight",
    (-1.00, 0.00): "poor",
}


@dataclass
class ScreeningRecord:
    """
    Individual screening decision record.

    Captures reviewer decision, timing, and rationale for audit trail.
    """

    record_id: str
    reviewer_id: str
    stage: ScreeningStage
    decision: ScreeningDecision
    timestamp: str  # ISO format
    time_spent_seconds: Optional[int] = None
    exclusion_reason: Optional[str] = None
    exclusion_detail: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        """Validate screening record completeness."""
        errors = []

        if not self.record_id or not self.record_id.strip():
            errors.append("Record ID is required")

        if not self.reviewer_id or not self.reviewer_id.strip():
            errors.append("Reviewer ID is required")

        valid_stages = ["title", "abstract", "full_text"]
        if self.stage not in valid_stages:
            errors.append(f"Invalid stage: {self.stage}")

        valid_decisions = ["include", "exclude", "maybe", "conflict"]
        if self.decision not in valid_decisions:
            errors.append(f"Invalid decision: {self.decision}")

        # Exclusion reason required if excluded
        if self.decision == "exclude" and not self.exclusion_reason:
            errors.append("Exclusion reason required for exclude decisions")

        # Validate timestamp format
        try:
            datetime.fromisoformat(self.timestamp)
        except (ValueError, TypeError):
            errors.append("Invalid timestamp format (use ISO format)")

        return errors

    def is_valid(self) -> bool:
        """Check if record has no validation errors."""
        return len(self.validate()) == 0

    def check_timing(self) -> dict:
        """Check if screening time is within recommended limits."""
        threshold = TIMING_THRESHOLDS.get(self.stage, 120)

        result: dict[str, Any] = {
            "stage": self.stage,
            "time_spent": self.time_spent_seconds,
            "threshold": threshold,
            "within_limit": True,
            "warning": None,
        }

        if self.time_spent_seconds is not None:
            if self.time_spent_seconds > threshold:
                result["within_limit"] = False
                result["warning"] = (
                    f"Screening time ({self.time_spent_seconds}s) exceeds "
                    f"recommended {threshold}s for {self.stage} screening"
                )
            elif self.time_spent_seconds < 2:
                result["within_limit"] = False
                result["warning"] = (
                    f"Screening time ({self.time_spent_seconds}s) may be too quick - "
                    "ensure thorough review"
                )

        return result

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DualScreeningPair:
    """
    Paired screening decisions for dual review.

    Captures both reviewers' decisions and resolves conflicts.
    """

    record_id: str
    reviewer1: ScreeningRecord
    reviewer2: ScreeningRecord
    final_decision: Optional[ScreeningDecision] = None
    resolution_notes: str = ""
    resolved_by: str = ""
    resolved_at: str = ""

    def has_agreement(self) -> bool:
        """Check if both reviewers agree."""
        return self.reviewer1.decision == self.reviewer2.decision

    def get_disagreement_type(self) -> Optional[str]:
        """Describe type of disagreement if present."""
        if self.has_agreement():
            return None

        d1, d2 = self.reviewer1.decision, self.reviewer2.decision

        # Include vs exclude is most concerning
        if {d1, d2} == {"include", "exclude"}:
            return "critical"
        # One reviewer unsure
        elif "maybe" in {d1, d2}:
            return "uncertain"
        else:
            return "minor"

    def resolve(
        self,
        final_decision: ScreeningDecision,
        resolved_by: str,
        notes: str = "",
    ) -> None:
        """Record conflict resolution."""
        self.final_decision = final_decision
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now().isoformat()
        self.resolution_notes = notes

    def get_final_decision(self) -> ScreeningDecision:
        """Get final decision (resolved or agreed)."""
        if self.final_decision:
            return self.final_decision
        if self.has_agreement():
            return self.reviewer1.decision
        return "conflict"

    def validate(self) -> list[str]:
        """Validate dual screening pair."""
        errors = []

        # Validate both records
        for error in self.reviewer1.validate():
            errors.append(f"Reviewer 1: {error}")
        for error in self.reviewer2.validate():
            errors.append(f"Reviewer 2: {error}")

        # Check record IDs match
        if self.reviewer1.record_id != self.reviewer2.record_id:
            errors.append("Record IDs do not match between reviewers")

        # Check stages match
        if self.reviewer1.stage != self.reviewer2.stage:
            errors.append("Screening stages do not match between reviewers")

        # Check different reviewers
        if self.reviewer1.reviewer_id == self.reviewer2.reviewer_id:
            errors.append("Dual screening requires different reviewers")

        # Conflict needs resolution
        if not self.has_agreement() and not self.final_decision:
            errors.append("Disagreement requires resolution")

        return errors

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "record_id": self.record_id,
            "reviewer1": self.reviewer1.to_dict(),
            "reviewer2": self.reviewer2.to_dict(),
            "agreement": self.has_agreement(),
            "disagreement_type": self.get_disagreement_type(),
            "final_decision": self.get_final_decision(),
            "resolution_notes": self.resolution_notes,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at,
        }


@dataclass
class ScreeningSession:
    """
    Collection of screening records for a review stage.

    Provides batch validation, statistics, and kappa calculation.
    """

    review_id: str
    stage: ScreeningStage
    records: list[ScreeningRecord] = field(default_factory=list)
    dual_pairs: list[DualScreeningPair] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_record(self, record: ScreeningRecord) -> None:
        """Add a screening record."""
        self.records.append(record)

    def add_dual_pair(self, pair: DualScreeningPair) -> None:
        """Add a dual screening pair."""
        self.dual_pairs.append(pair)

    def get_records_by_reviewer(self, reviewer_id: str) -> list[ScreeningRecord]:
        """Get all records for a specific reviewer."""
        return [r for r in self.records if r.reviewer_id == reviewer_id]

    def get_reviewers(self) -> list[str]:
        """Get list of unique reviewer IDs."""
        return list({r.reviewer_id for r in self.records})

    def calculate_kappa(self) -> Optional[float]:
        """
        Calculate Cohen's kappa for inter-rater agreement.

        Returns None if not enough dual pairs or only one decision type.
        """
        if len(self.dual_pairs) < 2:
            return None

        # Build contingency table (simplified: include vs not-include)
        # Decisions: include=1, exclude/maybe/conflict=0
        def to_binary(decision: str) -> int:
            return 1 if decision == "include" else 0

        n = len(self.dual_pairs)
        a = 0  # Both include
        b = 0  # R1 include, R2 not
        c = 0  # R1 not, R2 include
        d = 0  # Both not include

        for pair in self.dual_pairs:
            r1 = to_binary(pair.reviewer1.decision)
            r2 = to_binary(pair.reviewer2.decision)

            if r1 == 1 and r2 == 1:
                a += 1
            elif r1 == 1 and r2 == 0:
                b += 1
            elif r1 == 0 and r2 == 1:
                c += 1
            else:
                d += 1

        # Calculate observed agreement
        p_o = (a + d) / n

        # Calculate expected agreement
        p_r1_yes = (a + b) / n
        p_r2_yes = (a + c) / n
        p_r1_no = (c + d) / n
        p_r2_no = (b + d) / n

        p_e = (p_r1_yes * p_r2_yes) + (p_r1_no * p_r2_no)

        # Handle edge case where p_e = 1
        if p_e == 1:
            return 1.0 if p_o == 1 else 0.0

        # Calculate kappa
        kappa = (p_o - p_e) / (1 - p_e)

        return round(kappa, 3)

    def interpret_kappa(self, kappa: Optional[float]) -> str:
        """Interpret kappa value."""
        if kappa is None:
            return "insufficient data"

        for (low, high), interpretation in KAPPA_INTERPRETATION.items():
            if low <= kappa <= high:
                return interpretation

        return "undefined"

    def get_statistics(self) -> dict:
        """Calculate screening statistics."""
        total = len(self.records)

        if total == 0:
            return {
                "stage": self.stage,
                "total_records": 0,
                "decisions": {},
            }

        decisions = {}
        for r in self.records:
            decisions[r.decision] = decisions.get(r.decision, 0) + 1

        # Calculate timing stats
        times = [r.time_spent_seconds for r in self.records if r.time_spent_seconds]
        avg_time = sum(times) / len(times) if times else None

        # Calculate exclusion reasons
        exclusion_reasons: dict[str, int] = {}
        for r in self.records:
            if r.decision == "exclude" and r.exclusion_reason:
                exclusion_reasons[r.exclusion_reason] = (
                    exclusion_reasons.get(r.exclusion_reason, 0) + 1
                )

        kappa = self.calculate_kappa()

        return {
            "stage": self.stage,
            "review_id": self.review_id,
            "total_records": total,
            "unique_papers": len({r.record_id for r in self.records}),
            "reviewers": self.get_reviewers(),
            "decisions": decisions,
            "decision_percentages": {
                k: round(v / total * 100, 1) for k, v in decisions.items()
            },
            "exclusion_reasons": exclusion_reasons,
            "average_time_seconds": round(avg_time, 1) if avg_time else None,
            "dual_screening_pairs": len(self.dual_pairs),
            "agreements": sum(1 for p in self.dual_pairs if p.has_agreement()),
            "disagreements": sum(1 for p in self.dual_pairs if not p.has_agreement()),
            "kappa": kappa,
            "kappa_interpretation": self.interpret_kappa(kappa),
        }

    def validate(self) -> list[str]:
        """Validate all records in the session."""
        errors = []

        if not self.review_id:
            errors.append("Review ID is required")

        valid_stages = ["title", "abstract", "full_text"]
        if self.stage not in valid_stages:
            errors.append(f"Invalid stage: {self.stage}")

        # Validate each record
        for i, record in enumerate(self.records):
            for error in record.validate():
                errors.append(f"Record {i + 1}: {error}")

            # Check stage consistency
            if record.stage != self.stage:
                errors.append(
                    f"Record {i + 1}: Stage mismatch ({record.stage} vs {self.stage})"
                )

        # Validate dual pairs
        for i, pair in enumerate(self.dual_pairs):
            for error in pair.validate():
                errors.append(f"Dual pair {i + 1}: {error}")

        # Check for duplicate record IDs within same reviewer
        for reviewer in self.get_reviewers():
            reviewer_records = self.get_records_by_reviewer(reviewer)
            record_ids = [r.record_id for r in reviewer_records]
            duplicates = [rid for rid in record_ids if record_ids.count(rid) > 1]
            if duplicates:
                errors.append(
                    f"Reviewer {reviewer} has duplicate record IDs: {set(duplicates)}"
                )

        return errors

    def is_valid(self) -> bool:
        """Check if session has no validation errors."""
        return len(self.validate()) == 0

    def check_kappa_threshold(self, threshold: float = 0.8) -> dict:
        """
        Check if inter-rater agreement meets threshold.

        Default threshold is kappa >= 0.8 per skill documentation.
        """
        kappa = self.calculate_kappa()

        return {
            "kappa": kappa,
            "threshold": threshold,
            "meets_threshold": kappa is not None and kappa >= threshold,
            "interpretation": self.interpret_kappa(kappa),
            "recommendation": (
                None
                if kappa is None
                else (
                    "Agreement is acceptable"
                    if kappa >= threshold
                    else "Consider reviewer calibration session"
                )
            ),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "review_id": self.review_id,
            "stage": self.stage,
            "created_at": self.created_at,
            "records": [r.to_dict() for r in self.records],
            "dual_pairs": [p.to_dict() for p in self.dual_pairs],
            "statistics": self.get_statistics(),
        }


def create_record(
    record_id: str,
    reviewer_id: str,
    stage: ScreeningStage,
    decision: ScreeningDecision,
    exclusion_reason: Optional[str] = None,
    exclusion_detail: str = "",
    time_spent_seconds: Optional[int] = None,
    notes: str = "",
) -> ScreeningRecord:
    """
    Create a screening record with automatic timestamp.

    Args:
        record_id: Unique identifier for the paper/record
        reviewer_id: ID of the reviewer making the decision
        stage: Screening stage (title, abstract, full_text)
        decision: Screening decision (include, exclude, maybe)
        exclusion_reason: Reason code if excluding
        exclusion_detail: Additional detail about exclusion
        time_spent_seconds: Time spent on screening
        notes: Additional notes

    Returns:
        ScreeningRecord instance
    """
    return ScreeningRecord(
        record_id=record_id,
        reviewer_id=reviewer_id,
        stage=stage,
        decision=decision,
        timestamp=datetime.now().isoformat(),
        time_spent_seconds=time_spent_seconds,
        exclusion_reason=exclusion_reason,
        exclusion_detail=exclusion_detail,
        notes=notes,
    )


def create_dual_pair(
    record_id: str,
    record1: ScreeningRecord,
    record2: ScreeningRecord,
) -> DualScreeningPair:
    """
    Create a dual screening pair from two records.

    Args:
        record_id: Paper/record ID
        record1: First reviewer's record
        record2: Second reviewer's record

    Returns:
        DualScreeningPair instance
    """
    return DualScreeningPair(
        record_id=record_id,
        reviewer1=record1,
        reviewer2=record2,
    )


def load_session_from_json(filepath: str) -> ScreeningSession:
    """Load screening session from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Parse records
    records = [
        ScreeningRecord(
            record_id=r["record_id"],
            reviewer_id=r["reviewer_id"],
            stage=r["stage"],
            decision=r["decision"],
            timestamp=r["timestamp"],
            time_spent_seconds=r.get("time_spent_seconds"),
            exclusion_reason=r.get("exclusion_reason"),
            exclusion_detail=r.get("exclusion_detail", ""),
            notes=r.get("notes", ""),
        )
        for r in data.get("records", [])
    ]

    # Parse dual pairs
    dual_pairs = []
    for p in data.get("dual_pairs", []):
        r1_data = p["reviewer1"]
        r2_data = p["reviewer2"]

        r1 = ScreeningRecord(
            record_id=r1_data["record_id"],
            reviewer_id=r1_data["reviewer_id"],
            stage=r1_data["stage"],
            decision=r1_data["decision"],
            timestamp=r1_data["timestamp"],
            time_spent_seconds=r1_data.get("time_spent_seconds"),
            exclusion_reason=r1_data.get("exclusion_reason"),
            exclusion_detail=r1_data.get("exclusion_detail", ""),
            notes=r1_data.get("notes", ""),
        )

        r2 = ScreeningRecord(
            record_id=r2_data["record_id"],
            reviewer_id=r2_data["reviewer_id"],
            stage=r2_data["stage"],
            decision=r2_data["decision"],
            timestamp=r2_data["timestamp"],
            time_spent_seconds=r2_data.get("time_spent_seconds"),
            exclusion_reason=r2_data.get("exclusion_reason"),
            exclusion_detail=r2_data.get("exclusion_detail", ""),
            notes=r2_data.get("notes", ""),
        )

        pair = DualScreeningPair(
            record_id=p["record_id"],
            reviewer1=r1,
            reviewer2=r2,
            final_decision=p.get("final_decision"),
            resolution_notes=p.get("resolution_notes", ""),
            resolved_by=p.get("resolved_by", ""),
            resolved_at=p.get("resolved_at", ""),
        )
        dual_pairs.append(pair)

    session = ScreeningSession(
        review_id=data.get("review_id", ""),
        stage=data.get("stage", "title"),
        created_at=data.get("created_at", datetime.now().isoformat()),
    )
    session.records = records
    session.dual_pairs = dual_pairs

    return session


def save_session_to_json(session: ScreeningSession, filepath: str) -> None:
    """Save screening session to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session.to_dict(), f, indent=2)


def generate_audit_report(session: ScreeningSession) -> str:
    """
    Generate a text-based audit report for the screening session.

    Args:
        session: ScreeningSession to report on

    Returns:
        Formatted audit report string
    """
    stats = session.get_statistics()
    kappa_check = session.check_kappa_threshold()

    lines = [
        "SCREENING AUDIT REPORT",
        "=" * 60,
        "",
        f"Review ID: {session.review_id}",
        f"Stage: {session.stage}",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Total Records: {stats['total_records']}",
        f"Unique Papers: {stats['unique_papers']}",
        f"Reviewers: {', '.join(stats['reviewers'])}",
        "",
        "DECISIONS",
        "-" * 40,
    ]

    for decision, count in stats["decisions"].items():
        pct = stats["decision_percentages"].get(decision, 0)
        lines.append(f"  {decision}: {count} ({pct}%)")

    if stats["exclusion_reasons"]:
        lines.extend(["", "EXCLUSION REASONS", "-" * 40])
        for reason, count in sorted(
            stats["exclusion_reasons"].items(), key=lambda x: -x[1]
        ):
            lines.append(f"  {reason}: {count}")

    if stats["average_time_seconds"]:
        lines.extend(
            [
                "",
                "TIMING",
                "-" * 40,
                f"Average time: {stats['average_time_seconds']}s",
                f"Recommended max: {TIMING_THRESHOLDS.get(session.stage, 120)}s",
            ]
        )

    if stats["dual_screening_pairs"] > 0:
        lines.extend(
            [
                "",
                "INTER-RATER AGREEMENT",
                "-" * 40,
                f"Dual screening pairs: {stats['dual_screening_pairs']}",
                f"Agreements: {stats['agreements']}",
                f"Disagreements: {stats['disagreements']}",
                f"Cohen's Kappa: {kappa_check['kappa']}",
                f"Interpretation: {kappa_check['interpretation']}",
                f"Threshold (0.8): {'PASS' if kappa_check['meets_threshold'] else 'FAIL'}",
            ]
        )

        if kappa_check["recommendation"]:
            lines.append(f"Recommendation: {kappa_check['recommendation']}")

    # Validation
    errors = session.validate()
    lines.extend(["", "VALIDATION", "-" * 40])
    if errors:
        lines.append("Issues found:")
        for error in errors:
            lines.append(f"  - {error}")
    else:
        lines.append("No validation issues found.")

    lines.append("")
    return "\n".join(lines)


def main():
    """Example usage and demonstration."""
    print("Screening Tracker Demo")
    print("=" * 60)

    # Create a screening session
    session = ScreeningSession(
        review_id="SR2024-001",
        stage="abstract",
    )

    # Add some records
    records = [
        create_record("PMC123456", "reviewer_a", "abstract", "include", time_spent_seconds=45),
        create_record("PMC123457", "reviewer_a", "abstract", "exclude",
                     exclusion_reason="wrong_population", time_spent_seconds=30),
        create_record("PMC123458", "reviewer_a", "abstract", "include", time_spent_seconds=60),
        create_record("PMC123456", "reviewer_b", "abstract", "include", time_spent_seconds=50),
        create_record("PMC123457", "reviewer_b", "abstract", "exclude",
                     exclusion_reason="wrong_population", time_spent_seconds=35),
        create_record("PMC123458", "reviewer_b", "abstract", "maybe", time_spent_seconds=90),
    ]

    for record in records:
        session.add_record(record)

    # Create dual pairs
    pair1 = create_dual_pair(
        "PMC123456",
        records[0],  # reviewer_a: include
        records[3],  # reviewer_b: include
    )
    pair2 = create_dual_pair(
        "PMC123457",
        records[1],  # reviewer_a: exclude
        records[4],  # reviewer_b: exclude
    )
    pair3 = create_dual_pair(
        "PMC123458",
        records[2],  # reviewer_a: include
        records[5],  # reviewer_b: maybe
    )

    # Resolve disagreement
    pair3.resolve("include", "senior_reviewer", "After discussion, agreed to include")

    session.add_dual_pair(pair1)
    session.add_dual_pair(pair2)
    session.add_dual_pair(pair3)

    # Generate report
    print(generate_audit_report(session))

    # Show kappa check
    print("\nKappa threshold check:")
    kappa_result = session.check_kappa_threshold()
    print(f"  Kappa: {kappa_result['kappa']}")
    print(f"  Meets threshold (0.8): {kappa_result['meets_threshold']}")


if __name__ == "__main__":
    main()
