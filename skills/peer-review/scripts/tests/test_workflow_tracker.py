"""Tests for workflow tracker module."""

import sys
import tempfile
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_tracker import (
    ReviewStage,
    STAGE_EXIT_CRITERIA,
    WorkflowState,
    print_progress_bar,
    print_workflow_status,
)


class TestReviewStage:
    """Tests for ReviewStage enum."""

    def test_stage_order(self):
        """Test that stages are in correct order."""
        assert ReviewStage.INITIAL_ASSESSMENT < ReviewStage.SECTION_REVIEW
        assert ReviewStage.SECTION_REVIEW < ReviewStage.METHODOLOGY
        assert ReviewStage.METHODOLOGY < ReviewStage.REPRODUCIBILITY
        assert ReviewStage.REPRODUCIBILITY < ReviewStage.FIGURES
        assert ReviewStage.FIGURES < ReviewStage.ETHICS
        assert ReviewStage.ETHICS < ReviewStage.WRITING
        assert ReviewStage.WRITING < ReviewStage.REPORT

    def test_stage_count(self):
        """Test that we have 8 stages."""
        assert len(ReviewStage) == 8

    def test_stage_values(self):
        """Test stage integer values."""
        assert int(ReviewStage.INITIAL_ASSESSMENT) == 1
        assert int(ReviewStage.REPORT) == 8


class TestStageExitCriteria:
    """Tests for stage exit criteria configuration."""

    def test_all_stages_have_criteria(self):
        """Test that all non-report stages have exit criteria."""
        for stage in ReviewStage:
            if stage != ReviewStage.REPORT:
                assert stage in STAGE_EXIT_CRITERIA
                assert len(STAGE_EXIT_CRITERIA[stage]) > 0

    def test_criteria_are_unique(self):
        """Test that criteria names don't repeat within a stage."""
        for stage, criteria in STAGE_EXIT_CRITERIA.items():
            assert len(criteria) == len(set(criteria))

    def test_initial_assessment_criteria(self):
        """Test initial assessment has expected criteria."""
        criteria = STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]
        assert "research_question_identified" in criteria
        assert "main_findings_summarized" in criteria


class TestWorkflowState:
    """Tests for WorkflowState class."""

    def test_initial_state(self):
        """Test initial workflow state."""
        state = WorkflowState()
        assert state.current_stage == ReviewStage.INITIAL_ASSESSMENT
        assert len(state.checklist) == 0
        assert state.get_overall_progress() == 0

    def test_mark_complete(self):
        """Test marking criteria as complete."""
        state = WorkflowState()
        state.mark_complete("research_question_identified")
        assert state.is_complete("research_question_identified")
        assert not state.is_complete("main_findings_summarized")

    def test_mark_complete_with_note(self):
        """Test marking criteria complete with a note."""
        state = WorkflowState()
        state.mark_complete("research_question_identified", "Clear hypothesis stated")
        assert state.is_complete("research_question_identified")
        assert len(state.stage_notes.get(1, [])) == 1

    def test_cannot_advance_incomplete(self):
        """Test that cannot advance without completing criteria."""
        state = WorkflowState()
        can_advance, missing = state.can_advance()
        assert not can_advance
        assert len(missing) > 0

    def test_can_advance_complete(self):
        """Test that can advance after completing all criteria."""
        state = WorkflowState()
        for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
            state.mark_complete(criterion)

        can_advance, missing = state.can_advance()
        assert can_advance
        assert len(missing) == 0

    def test_advance_stage(self):
        """Test advancing to next stage."""
        state = WorkflowState()

        # Complete initial assessment
        for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
            state.mark_complete(criterion)

        success, msg = state.advance_stage()
        assert success
        assert state.current_stage == ReviewStage.SECTION_REVIEW

    def test_cannot_advance_past_report(self):
        """Test that cannot advance past report stage."""
        state = WorkflowState()
        state.current_stage = ReviewStage.REPORT

        success, msg = state.advance_stage()
        assert not success
        assert "final stage" in msg.lower()

    def test_add_issue(self):
        """Test adding issues."""
        state = WorkflowState()
        state.add_issue(
            "Missing power analysis",
            severity="major",
            location="Methods",
            recommendation="Add power calculation",
        )

        issues = state.get_stage_issues()
        assert len(issues) == 1
        assert issues[0]["severity"] == "major"
        assert issues[0]["issue"] == "Missing power analysis"

    def test_get_all_issues(self):
        """Test getting issues from all stages."""
        state = WorkflowState()
        state.add_issue("Issue 1", severity="minor")

        # Complete stage and advance
        for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
            state.mark_complete(criterion)
        state.advance_stage()

        state.add_issue("Issue 2", severity="major")

        all_issues = state.get_all_issues()
        assert len(all_issues) == 2

    def test_stage_progress(self):
        """Test stage progress calculation."""
        state = WorkflowState()
        criteria = STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]

        assert state.get_stage_progress() == 0

        # Complete half the criteria
        for criterion in criteria[: len(criteria) // 2]:
            state.mark_complete(criterion)

        progress = state.get_stage_progress()
        assert 40 <= progress <= 60  # Approximately half

        # Complete all
        for criterion in criteria:
            state.mark_complete(criterion)

        assert state.get_stage_progress() == 100

    def test_overall_progress(self):
        """Test overall progress calculation."""
        state = WorkflowState()

        # Complete one stage worth of criteria
        for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
            state.mark_complete(criterion)

        progress = state.get_overall_progress()
        assert 10 <= progress <= 20  # Roughly 1/7 of total

    def test_get_summary(self):
        """Test getting state summary."""
        state = WorkflowState()
        state.add_issue("Test issue", severity="major")

        summary = state.get_summary()
        assert "current_stage" in summary
        assert "stage_progress" in summary
        assert "overall_progress" in summary
        assert "can_advance" in summary
        assert "total_issues" in summary
        assert summary["total_issues"] == 1


class TestSerialization:
    """Tests for state serialization."""

    def test_to_dict(self):
        """Test serialization to dict."""
        state = WorkflowState()
        state.mark_complete("research_question_identified")
        state.add_issue("Test issue", severity="minor")

        data = state.to_dict()
        assert data["current_stage"] == 1
        assert "research_question_identified" in data["checklist"]

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "current_stage": 2,
            "checklist": {"research_question_identified": True},
            "stage_notes": {},
            "stage_issues": {},
        }

        state = WorkflowState.from_dict(data)
        assert state.current_stage == ReviewStage.SECTION_REVIEW
        assert state.is_complete("research_question_identified")

    def test_save_and_load(self):
        """Test saving and loading state."""
        state = WorkflowState()
        state.mark_complete("research_question_identified")
        state.add_issue("Test issue", severity="major")

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as f:
            state.save(Path(f.name))
            temp_path = Path(f.name)

        try:
            loaded = WorkflowState.load(temp_path)
            assert loaded.is_complete("research_question_identified")
            assert len(loaded.get_stage_issues()) == 1
        finally:
            temp_path.unlink()


class TestFormatting:
    """Tests for formatting functions."""

    def test_progress_bar(self):
        """Test progress bar generation."""
        bar = print_progress_bar(50)
        assert "50" in bar
        assert "█" in bar
        assert "░" in bar

    def test_progress_bar_full(self):
        """Test 100% progress bar."""
        bar = print_progress_bar(100)
        assert "100" in bar
        assert "░" not in bar

    def test_progress_bar_empty(self):
        """Test 0% progress bar."""
        bar = print_progress_bar(0)
        assert "0" in bar
        assert "█" not in bar

    def test_workflow_status(self):
        """Test workflow status formatting."""
        state = WorkflowState()
        status = print_workflow_status(state)
        assert "Initial Assessment" in status
        assert "Progress" in status


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_progress_is_deterministic(self):
        """Test that progress calculation is deterministic."""
        for _ in range(10):
            state = WorkflowState()
            state.mark_complete("research_question_identified")
            state.mark_complete("main_findings_summarized")

            progress = state.get_stage_progress()
            assert progress == 40.0  # 2/5 = 40%

    def test_serialization_roundtrip(self):
        """Test that serialization roundtrip is deterministic."""
        state = WorkflowState()
        for criterion in STAGE_EXIT_CRITERIA[ReviewStage.INITIAL_ASSESSMENT]:
            state.mark_complete(criterion)
        state.add_issue("Test", severity="minor")

        for _ in range(5):
            data = state.to_dict()
            loaded = WorkflowState.from_dict(data)
            assert loaded.get_overall_progress() == state.get_overall_progress()
            assert len(loaded.get_all_issues()) == len(state.get_all_issues())
