"""Tests for scripts/checkpoint.py — stage-boundary resumability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from checkpoint import (
    DEFAULT_AUDITS_ROOT,
    load_resume_state,
    slugify,
    write_stage_artifact,
)


class TestSlugify:
    @pytest.mark.parametrize(
        "title,expected",
        [
            ("My Paper", "my-paper"),
            ("  Whitespace  ", "whitespace"),
            ("Paper: A Subtitle!", "paper-a-subtitle"),
            ("multiple---dashes", "multiple-dashes"),
            ("CT26 anti-PD-1 (2026)", "ct26-anti-pd-1-2026"),
            ("", "untitled"),
            ("///", "untitled"),
        ],
    )
    def test_basic(self, title: str, expected: str) -> None:
        assert slugify(title) == expected

    def test_truncates_to_max_len(self) -> None:
        long = "a" * 200
        assert len(slugify(long)) == 60

    def test_truncation_strips_trailing_hyphen(self) -> None:
        # 59 'a's, then a hyphen, then more chars: truncated at 60 must not end on '-'
        title = ("a" * 59) + "-bbbbb"
        result = slugify(title, max_len=60)
        assert not result.endswith("-")


class TestWriteStage1:
    def test_writes_claim_inventory(self, tmp_path: Path) -> None:
        inventory = {
            "items": [
                {"id": "C001", "claim_text": "x", "claim_type": "uncited",
                 "location": {"section": "Intro", "paragraph": 1}}
            ]
        }
        path = write_stage_artifact(
            "doc-a", 1, [], [], "manuscript",
            claim_inventory=inventory, audits_root=tmp_path,
        )
        assert path == tmp_path / "doc-a" / "claim_inventory.json"
        assert json.loads(path.read_text()) == inventory

    def test_stage1_requires_inventory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="claim_inventory"):
            write_stage_artifact("doc-a", 1, [], [], "manuscript", audits_root=tmp_path)

    def test_stage1_rejects_bare_array(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must be a dict"):
            write_stage_artifact(
                "doc-a", 1, [], [], "manuscript",
                claim_inventory=[{"id": "C001"}],  # type: ignore[arg-type]
                audits_root=tmp_path,
            )

    def test_stage1_rejects_dict_without_items_key(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must be a dict"):
            write_stage_artifact(
                "doc-a", 1, [], [], "manuscript",
                claim_inventory={"claims": []},
                audits_root=tmp_path,
            )


class TestWriteValidatedStages:
    def test_writes_valid_findings(
        self, tmp_path: Path, sample_finding_critical: dict[str, Any]
    ) -> None:
        matrix = [{"claim_id": "F001", "verdict": "UNSUPPORTED",
                   "severity": "CRITICAL", "stage": "2"}]
        path = write_stage_artifact(
            "doc-a", 2, [sample_finding_critical], matrix, "manuscript",
            audits_root=tmp_path,
        )
        assert path == tmp_path / "doc-a" / "02_existence.json"
        artifact = json.loads(path.read_text())
        assert artifact["stage"] == 2
        assert artifact["stage_name"] == "existence"
        assert artifact["findings"] == [sample_finding_critical]
        assert artifact["matrix_delta"] == matrix
        assert "written_at" in artifact

    def test_rejects_invalid_finding(
        self, tmp_path: Path, sample_finding_critical: dict[str, Any]
    ) -> None:
        # Severity mismatch (UNSUPPORTED × manuscript should be CRITICAL, not MINOR)
        bad = {**sample_finding_critical, "severity": "MINOR"}
        with pytest.raises(ValueError, match="failed validation"):
            write_stage_artifact("doc-a", 2, [bad], [], "manuscript", audits_root=tmp_path)
        # Nothing should have been written
        assert not (tmp_path / "doc-a" / "02_existence.json").exists()

    def test_rejects_unknown_stage(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="stage must be 1..7"):
            write_stage_artifact("doc-a", 8, [], [], "manuscript", audits_root=tmp_path)

    def test_creates_audit_dir(self, tmp_path: Path) -> None:
        write_stage_artifact(
            "new-slug", 1, [], [],
            "manuscript", claim_inventory={"items": []}, audits_root=tmp_path,
        )
        assert (tmp_path / "new-slug").is_dir()

    def test_p7_blocks_biomedical_stage2_without_scite(
        self, tmp_path: Path
    ) -> None:
        """Threading domain='biomedical' through write_stage_artifact must
        activate P7 inside the validator closure, rejecting Stage-2
        findings that lack a Scite probe."""
        finding: dict[str, Any] = {
            "id": "F900",
            "location": {"section": "Intro", "paragraph": 1, "line": 1},
            "claim_verbatim": "X causes Y per Smith et al.",
            "claim_type": "citation_bearing",
            "citations": [{"key": "Smith2020", "raw_text": "Smith 2020"}],
            "verification_path": [
                {"method": "doi_lookup", "tool": "Crossref",
                 "result_summary": "DOI resolves"},
            ],
            "evidence": [
                {"source": "Crossref", "url": "https://doi.org/10.1/x",
                 "snippet": "ok"}
            ],
            "verdict": "VERIFIED",
            "severity": "INFORMATIONAL",
            "recommended_action": "No action.",
            "confidence": "high",
        }
        with pytest.raises(ValueError, match="P7"):
            write_stage_artifact(
                "p7-block", 2, [finding], [], "manuscript",
                domain="biomedical", audits_root=tmp_path,
            )
        assert not (tmp_path / "p7-block" / "02_existence.json").exists()

    def test_p7_passes_when_scite_probe_present(self, tmp_path: Path) -> None:
        finding: dict[str, Any] = {
            "id": "F901",
            "location": {"section": "Intro", "paragraph": 1, "line": 1},
            "claim_verbatim": "X causes Y per Smith et al.",
            "claim_type": "citation_bearing",
            "citations": [{"key": "Smith2020", "raw_text": "Smith 2020"}],
            "verification_path": [
                {"method": "doi_lookup", "tool": "Crossref",
                 "result_summary": "DOI resolves"},
                {"method": "scite_context", "tool": "Scite MCP",
                 "result_summary": "editorialNotices: none"},
            ],
            "evidence": [
                {"source": "Crossref", "url": "https://doi.org/10.1/x",
                 "snippet": "ok"}
            ],
            "verdict": "VERIFIED",
            "severity": "INFORMATIONAL",
            "recommended_action": "No action.",
            "confidence": "high",
        }
        path = write_stage_artifact(
            "p7-pass", 2, [finding], [], "manuscript",
            domain="biomedical", audits_root=tmp_path,
        )
        assert path.exists()

    def test_p7_skipped_when_domain_omitted(self, tmp_path: Path) -> None:
        """Back-compat: omitting `domain` keeps P7 dormant even on biomedical
        content — same finding shape that fails with domain='biomedical'
        must pass when domain is unset."""
        finding: dict[str, Any] = {
            "id": "F902",
            "location": {"section": "Intro", "paragraph": 1, "line": 1},
            "claim_verbatim": "X causes Y per Smith et al.",
            "claim_type": "citation_bearing",
            "citations": [{"key": "Smith2020", "raw_text": "Smith 2020"}],
            "verification_path": [
                {"method": "doi_lookup", "tool": "Crossref",
                 "result_summary": "DOI resolves"},
            ],
            "evidence": [
                {"source": "Crossref", "url": "https://doi.org/10.1/x",
                 "snippet": "ok"}
            ],
            "verdict": "VERIFIED",
            "severity": "INFORMATIONAL",
            "recommended_action": "No action.",
            "confidence": "high",
        }
        # No domain kwarg → P7 off → write succeeds.
        path = write_stage_artifact(
            "p7-skip", 2, [finding], [], "manuscript", audits_root=tmp_path,
        )
        assert path.exists()


class TestLoadResumeState:
    def test_no_resumable_state_when_dir_missing(self, tmp_path: Path) -> None:
        state = load_resume_state("nonexistent", audits_root=tmp_path)
        assert state.completed_stages == []
        assert state.next_stage == 1
        assert state.claim_inventory is None

    def test_no_resumable_state_when_dir_empty(self, tmp_path: Path) -> None:
        # Directory exists but Stage 1 inventory missing → start over from Stage 1.
        (tmp_path / "doc-a").mkdir()
        state = load_resume_state("doc-a", audits_root=tmp_path)
        assert state.completed_stages == []
        assert state.next_stage == 1
        assert state.claim_inventory is None

    def test_resumes_after_stage_1(self, tmp_path: Path) -> None:
        inventory = {
            "items": [{"id": "C001", "claim_text": "x", "claim_type": "uncited",
                       "location": {"section": "Intro", "paragraph": 1}}]
        }
        write_stage_artifact(
            "doc-a", 1, [], [], "manuscript",
            claim_inventory=inventory, audits_root=tmp_path,
        )
        state = load_resume_state("doc-a", audits_root=tmp_path)
        assert state.completed_stages == [1]
        assert state.next_stage == 2
        assert state.claim_inventory == inventory
        assert state.findings == []

    def test_resumes_through_multiple_stages(
        self, tmp_path: Path, sample_finding_critical: dict[str, Any]
    ) -> None:
        write_stage_artifact("doc-a", 1, [], [], "manuscript",
                             claim_inventory={"items": []}, audits_root=tmp_path)
        m2 = [{"claim_id": "F001", "verdict": "UNSUPPORTED",
               "severity": "CRITICAL", "stage": "2"}]
        write_stage_artifact("doc-a", 2, [sample_finding_critical], m2,
                             "manuscript", audits_root=tmp_path)
        write_stage_artifact("doc-a", 3, [], [], "manuscript", audits_root=tmp_path)

        state = load_resume_state("doc-a", audits_root=tmp_path)
        assert state.completed_stages == [1, 2, 3]
        assert state.next_stage == 4
        assert len(state.findings) == 1
        assert len(state.verification_matrix) == 1

    def test_gap_stops_scan_at_first_missing(
        self, tmp_path: Path, sample_finding_critical: dict[str, Any]
    ) -> None:
        # Stages 1, 2 present; 3 missing; 4 present → scan stops at 3
        write_stage_artifact("doc-a", 1, [], [], "manuscript",
                             claim_inventory={"items": []}, audits_root=tmp_path)
        write_stage_artifact("doc-a", 2, [sample_finding_critical],
                             [{"claim_id": "F001", "verdict": "UNSUPPORTED",
                               "severity": "CRITICAL", "stage": "2"}],
                             "manuscript", audits_root=tmp_path)
        # Manually drop a stage 4 artifact without stage 3
        (tmp_path / "doc-a" / "04_uncited.json").write_text(
            json.dumps({"stage": 4, "findings": [], "matrix_delta": []})
        )
        state = load_resume_state("doc-a", audits_root=tmp_path)
        assert state.completed_stages == [1, 2]
        assert state.next_stage == 3

    def test_default_audits_root_is_research_audits(self) -> None:
        # Sanity-check the documented default — important for SKILL.md prose
        assert DEFAULT_AUDITS_ROOT == Path("research/audits")
