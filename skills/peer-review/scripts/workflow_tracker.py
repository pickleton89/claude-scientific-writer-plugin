#!/usr/bin/env python3
"""
Workflow State Tracker for Peer Review

Tracks review progress through the 7-stage workflow with enforced exit criteria.
Ensures consistent, complete reviews by verifying each stage's requirements
before allowing progression.

Usage:
    from scripts.workflow_tracker import WorkflowState, ReviewStage

    state = WorkflowState()
    state.mark_complete("research_question_identified")
    state.mark_complete("main_findings_summarized")
    can_advance, missing = state.can_advance()

Author: Claude Scientific Writer Plugin
License: MIT
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import IntEnum
import json
from pathlib import Path


class ReviewStage(IntEnum):
    """Review workflow stages in order of progression."""

    INITIAL_ASSESSMENT = 1
    SECTION_REVIEW = 2
    METHODOLOGY = 3
    REPRODUCIBILITY = 4
    FIGURES = 5
    ETHICS = 6
    WRITING = 7
    REPORT = 8  # Final stage - report drafting


# Exit criteria extracted from references/workflow_transitions.md
STAGE_EXIT_CRITERIA: Dict[ReviewStage, List[str]] = {
    ReviewStage.INITIAL_ASSESSMENT: [
        "research_question_identified",
        "main_findings_summarized",
        "initial_impression_documented",
        "venue_appropriateness_assessed",
        "no_disqualifying_flaws_or_flagged",
    ],
    ReviewStage.SECTION_REVIEW: [
        "all_sections_evaluated",
        "min_2_strengths_per_section",
        "min_2_concerns_per_section",
        "issues_located_by_section",
        "key_claims_identified",
        "citation_coverage_assessed",
    ],
    ReviewStage.METHODOLOGY: [
        "statistical_assumptions_verified",
        "sample_size_checked",
        "controls_assessed",
        "multiple_testing_evaluated",
        "effect_sizes_checked",
        "experimental_design_documented",
    ],
    ReviewStage.REPRODUCIBILITY: [
        "data_availability_assessed",
        "code_availability_checked",
        "reporting_guidelines_verified",
        "protocol_detail_evaluated",
        "materials_availability_confirmed",
    ],
    ReviewStage.FIGURES: [
        "resolution_checked",
        "labeling_assessed",
        "error_bars_verified",
        "colorblind_accessibility_checked",
        "image_integrity_verified",
        "quality_scores_documented",
    ],
    ReviewStage.ETHICS: [
        "irb_verified_if_applicable",
        "iacuc_verified_if_applicable",
        "conflicts_disclosed",
        "funding_disclosed",
        "plagiarism_checked",
        "authorship_assessed",
    ],
    ReviewStage.WRITING: [
        "structure_assessed",
        "language_clarity_evaluated",
        "jargon_minimization_checked",
        "accessibility_considered",
        "all_stages_complete",
    ],
}

# Progress percentage thresholds for each stage
STAGE_PROGRESS_THRESHOLDS: Dict[ReviewStage, Dict[int, str]] = {
    ReviewStage.INITIAL_ASSESSMENT: {
        25: "Central research question identified",
        50: "Main findings and conclusions noted",
        75: "Venue appropriateness assessed",
        100: "Initial impression documented, ready for deep review",
    },
    ReviewStage.SECTION_REVIEW: {
        25: "Abstract/Title and Introduction reviewed",
        50: "Methods section evaluated",
        75: "Results and Discussion reviewed",
        100: "References assessed, all sections documented",
    },
    ReviewStage.METHODOLOGY: {
        25: "Statistical assumptions and test appropriateness checked",
        50: "Sample size and replication verified against thresholds",
        75: "Experimental design assessed",
        100: "Computational methods reviewed, all issues documented",
    },
    ReviewStage.REPRODUCIBILITY: {
        25: "Data availability assessed",
        50: "Code and materials availability checked",
        75: "Reporting guideline compliance verified",
        100: "Protocol detail sufficiency evaluated",
    },
    ReviewStage.FIGURES: {
        25: "Figure resolution and labeling quality checked",
        50: "Error bars and statistical indicators verified",
        75: "Image integrity checked",
        100: "Figure clarity assessed, quality scores documented",
    },
    ReviewStage.ETHICS: {
        25: "Human subjects verified if applicable",
        50: "Animal research verified if applicable",
        75: "Conflicts of interest and funding checked",
        100: "Authorship and integrity concerns assessed",
    },
    ReviewStage.WRITING: {
        25: "Structure and organization assessed",
        50: "Language clarity and conciseness evaluated",
        75: "Jargon minimization and accessibility checked",
        100: "All stages complete, ready for report drafting",
    },
}

# Human-readable stage names
STAGE_NAMES: Dict[ReviewStage, str] = {
    ReviewStage.INITIAL_ASSESSMENT: "Initial Assessment",
    ReviewStage.SECTION_REVIEW: "Section-by-Section Review",
    ReviewStage.METHODOLOGY: "Methodological Rigor",
    ReviewStage.REPRODUCIBILITY: "Reproducibility Assessment",
    ReviewStage.FIGURES: "Figure Evaluation",
    ReviewStage.ETHICS: "Ethical Considerations",
    ReviewStage.WRITING: "Writing Quality",
    ReviewStage.REPORT: "Report Drafting",
}


@dataclass
class WorkflowState:
    """
    Tracks review progress through stages.

    Maintains a checklist of completed criteria and enforces exit gates
    before allowing stage transitions.
    """

    current_stage: ReviewStage = ReviewStage.INITIAL_ASSESSMENT
    checklist: Dict[str, bool] = field(default_factory=dict)
    stage_notes: Dict[int, List[str]] = field(default_factory=dict)
    stage_issues: Dict[int, List[Dict[str, Any]]] = field(default_factory=dict)

    def mark_complete(self, criterion: str, note: Optional[str] = None) -> None:
        """
        Mark a checklist item as complete.

        Args:
            criterion: The criterion key to mark complete
            note: Optional note to attach to this criterion

        Examples:
            >>> state = WorkflowState()
            >>> state.mark_complete("research_question_identified")
            >>> state.is_complete("research_question_identified")
            True
        """
        self.checklist[criterion] = True
        if note:
            stage_num = int(self.current_stage)
            if stage_num not in self.stage_notes:
                self.stage_notes[stage_num] = []
            self.stage_notes[stage_num].append(f"[{criterion}] {note}")

    def mark_incomplete(self, criterion: str) -> None:
        """Mark a checklist item as incomplete."""
        self.checklist[criterion] = False

    def is_complete(self, criterion: str) -> bool:
        """Check if a criterion is complete."""
        return self.checklist.get(criterion, False)

    def add_issue(
        self,
        issue: str,
        severity: str = "minor",
        location: Optional[str] = None,
        recommendation: Optional[str] = None,
    ) -> None:
        """
        Add an issue found during the current stage.

        Args:
            issue: Description of the issue
            severity: Issue severity (critical, major, minor, optional)
            location: Where in the manuscript the issue occurs
            recommendation: Suggested resolution
        """
        stage_num = int(self.current_stage)
        if stage_num not in self.stage_issues:
            self.stage_issues[stage_num] = []

        self.stage_issues[stage_num].append({
            "issue": issue,
            "severity": severity,
            "location": location or "",
            "recommendation": recommendation or "",
            "stage": STAGE_NAMES[self.current_stage],
        })

    def get_stage_issues(self, stage: Optional[ReviewStage] = None) -> List[Dict[str, Any]]:
        """Get all issues from a specific stage or current stage."""
        stage_num = int(stage) if stage else int(self.current_stage)
        return self.stage_issues.get(stage_num, [])

    def get_all_issues(self) -> List[Dict[str, Any]]:
        """Get all issues from all stages."""
        all_issues = []
        for stage_num in sorted(self.stage_issues.keys()):
            all_issues.extend(self.stage_issues[stage_num])
        return all_issues

    def can_advance(self) -> Tuple[bool, List[str]]:
        """
        Check if current stage exit criteria are met.

        Returns:
            Tuple of (can_advance: bool, missing_criteria: List[str])

        Examples:
            >>> state = WorkflowState()
            >>> can_advance, missing = state.can_advance()
            >>> can_advance
            False
            >>> len(missing) > 0
            True
        """
        if self.current_stage == ReviewStage.REPORT:
            return (True, [])  # Final stage - always can "advance" (complete)

        required = STAGE_EXIT_CRITERIA.get(self.current_stage, [])
        missing = [item for item in required if not self.checklist.get(item, False)]
        return (len(missing) == 0, missing)

    def advance_stage(self) -> Tuple[bool, str]:
        """
        Attempt to advance to next stage.

        Returns:
            Tuple of (success: bool, message: str)

        Examples:
            >>> state = WorkflowState()
            >>> # Complete all criteria first...
            >>> success, msg = state.advance_stage()
        """
        can_advance, missing = self.can_advance()

        if not can_advance:
            missing_str = ", ".join(missing)
            return (False, f"Cannot advance: missing criteria - {missing_str}")

        if self.current_stage >= ReviewStage.REPORT:
            return (False, "Already at final stage (Report)")

        old_stage = self.current_stage
        self.current_stage = ReviewStage(self.current_stage + 1)

        return (
            True,
            f"Advanced from {STAGE_NAMES[old_stage]} to {STAGE_NAMES[self.current_stage]}",
        )

    def get_stage_progress(self, stage: Optional[ReviewStage] = None) -> float:
        """
        Calculate progress percentage for a specific stage.

        Args:
            stage: Stage to check (defaults to current stage)

        Returns:
            Progress percentage (0-100)
        """
        stage = stage or self.current_stage
        required = STAGE_EXIT_CRITERIA.get(stage, [])
        if not required:
            return 100.0

        completed = sum(1 for item in required if self.checklist.get(item, False))
        return (completed / len(required)) * 100

    def get_overall_progress(self) -> float:
        """
        Calculate overall progress percentage across all stages.

        Returns:
            Overall progress percentage (0-100)
        """
        total_criteria = sum(len(c) for c in STAGE_EXIT_CRITERIA.values())
        if total_criteria == 0:
            return 100.0

        completed = sum(1 for v in self.checklist.values() if v)
        return (completed / total_criteria) * 100

    def get_progress_description(self, stage: Optional[ReviewStage] = None) -> str:
        """
        Get human-readable progress description for a stage.

        Args:
            stage: Stage to describe (defaults to current stage)

        Returns:
            Progress description string
        """
        stage = stage or self.current_stage
        progress = self.get_stage_progress(stage)
        thresholds = STAGE_PROGRESS_THRESHOLDS.get(stage, {})

        # Find the highest threshold we've passed
        description = "Not started"
        for threshold, desc in sorted(thresholds.items()):
            if progress >= threshold:
                description = desc

        return f"{progress:.0f}% - {description}"

    def get_current_criteria(self) -> List[Tuple[str, bool]]:
        """
        Get all criteria for current stage with their completion status.

        Returns:
            List of (criterion, is_complete) tuples
        """
        required = STAGE_EXIT_CRITERIA.get(self.current_stage, [])
        return [(item, self.checklist.get(item, False)) for item in required]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current workflow state.

        Returns:
            Dictionary with state summary
        """
        return {
            "current_stage": STAGE_NAMES[self.current_stage],
            "current_stage_number": int(self.current_stage),
            "stage_progress": self.get_stage_progress(),
            "overall_progress": self.get_overall_progress(),
            "can_advance": self.can_advance()[0],
            "missing_criteria": self.can_advance()[1],
            "total_issues": len(self.get_all_issues()),
            "issues_by_severity": {
                "critical": len([i for i in self.get_all_issues() if i["severity"] == "critical"]),
                "major": len([i for i in self.get_all_issues() if i["severity"] == "major"]),
                "minor": len([i for i in self.get_all_issues() if i["severity"] == "minor"]),
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary for persistence."""
        return {
            "current_stage": int(self.current_stage),
            "checklist": self.checklist.copy(),
            "stage_notes": {str(k): v for k, v in self.stage_notes.items()},
            "stage_issues": {str(k): v for k, v in self.stage_issues.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Deserialize state from dictionary."""
        state = cls()
        state.current_stage = ReviewStage(data.get("current_stage", 1))
        state.checklist = data.get("checklist", {})
        state.stage_notes = {int(k): v for k, v in data.get("stage_notes", {}).items()}
        state.stage_issues = {int(k): v for k, v in data.get("stage_issues", {}).items()}
        return state

    def save(self, filepath: Path) -> None:
        """Save state to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> "WorkflowState":
        """Load state from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


def print_progress_bar(percentage: float, width: int = 40) -> str:
    """Generate ASCII progress bar."""
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.1f}%"


def print_workflow_status(state: WorkflowState) -> str:
    """Generate formatted workflow status report."""
    lines = [
        "=" * 60,
        "PEER REVIEW WORKFLOW STATUS",
        "=" * 60,
        "",
        f"Current Stage: {STAGE_NAMES[state.current_stage]} (Stage {int(state.current_stage)})",
        "",
        "Stage Progress:",
        f"  {print_progress_bar(state.get_stage_progress())}",
        "",
        "Overall Progress:",
        f"  {print_progress_bar(state.get_overall_progress())}",
        "",
    ]

    # Show current stage criteria
    lines.append(f"Current Stage Criteria ({STAGE_NAMES[state.current_stage]}):")
    for criterion, is_complete in state.get_current_criteria():
        status = "✓" if is_complete else "○"
        lines.append(f"  {status} {criterion.replace('_', ' ').title()}")

    lines.append("")

    # Can advance?
    can_advance, missing = state.can_advance()
    if can_advance:
        lines.append("✓ Ready to advance to next stage")
    else:
        lines.append("✗ Cannot advance yet. Missing:")
        for item in missing:
            lines.append(f"    - {item.replace('_', ' ')}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    print("Peer Review Workflow Tracker Demo")
    print("=" * 40)

    state = WorkflowState()
    print(print_workflow_status(state))

    # Simulate completing initial assessment
    print("\nCompleting Initial Assessment criteria...")
    for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
        state.mark_complete(criterion)

    print(f"Stage progress: {state.get_stage_progress():.1f}%")

    success, msg = state.advance_stage()
    print(f"Advance attempt: {msg}")

    print(f"\nNow at: {STAGE_NAMES[state.current_stage]}")
    print(f"Overall progress: {state.get_overall_progress():.1f}%")
