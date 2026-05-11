"""Tests for skills/shared/verifier_kit/.

Covers the kit's three public modules:

  * `validate.py` — two-stage SchemaValidator base class. Tested via a tiny
    demo subclass that adds a single predicate, exercising both the schema
    half (continue-past-failure) and the predicate half (errors + warnings).
  * `checkpoint.py` — Checkpoint state machine round-trip with both
    alternate-Stage-1 (verifier-style) and uniform-stage (summarizer-style)
    configurations.
  * `replay.py` — replay_state output shape.

These tests are independent of the verifier and summarizer skills — they
exercise the kit's API directly so a regression in extraction shows up
here, not via test_validation.py / test_checkpoint.py (which exercise the
verifier wrappers and would still pass on a bad-but-functional rewrite).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Add shared directory to path so `verifier_kit` is importable.
sys.path.insert(0, str(Path(__file__).parent.parent))

from verifier_kit import (
    Checkpoint,
    ResumeState,
    SchemaValidator,
    ValidationOutcome,
    replay_state,
    slugify,
)


# ---- SchemaValidator -------------------------------------------------------


DEMO_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "value"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "value": {"type": "integer", "minimum": 0},
        "label": {"type": "string"},
    },
    "additionalProperties": False,
}


class DemoValidator(SchemaValidator):
    """Toy validator for kit tests. Predicate: id must not equal 'forbidden'.

    A second rule emits a warning (advisory only) when label is 'preview'.
    """

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        if record.get("id") == "forbidden":
            errors.append("D1: id 'forbidden' is reserved")
        if record.get("label") == "preview":
            warnings.append("D2: 'preview' label is advisory")


class TestSchemaValidator:
    def test_valid_record_passes(self) -> None:
        v = DemoValidator(DEMO_SCHEMA)
        ok, errors, warnings = v.validate({"id": "ok", "value": 1})
        assert ok, errors
        assert errors == []
        assert warnings == []

    def test_schema_failure_reports_and_continues_to_predicates(self) -> None:
        v = DemoValidator(DEMO_SCHEMA)
        # Both: schema (value < 0) AND predicate (id == 'forbidden') fail.
        ok, errors, _ = v.validate({"id": "forbidden", "value": -1})
        assert not ok
        # Schema error first, then predicate error — both must appear.
        assert any("schema" in e for e in errors)
        assert any("D1" in e for e in errors)

    def test_warnings_do_not_fail_record(self) -> None:
        v = DemoValidator(DEMO_SCHEMA)
        ok, errors, warnings = v.validate({"id": "ok", "value": 0, "label": "preview"})
        assert ok, errors
        assert any("D2" in w for w in warnings)

    def test_loads_schema_from_path(self, tmp_path: Path) -> None:
        import json

        p = tmp_path / "schema.json"
        p.write_text(json.dumps(DEMO_SCHEMA))
        v = DemoValidator(p)
        ok, errors, _ = v.validate({"id": "ok", "value": 1})
        assert ok, errors

    def test_validate_outcome_returns_dataclass(self) -> None:
        v = DemoValidator(DEMO_SCHEMA)
        outcome = v.validate_outcome({"id": "ok", "value": 1})
        assert isinstance(outcome, ValidationOutcome)
        assert outcome.ok is True
        assert outcome.errors == []

    def test_predicate_receives_ctx(self) -> None:
        captured: dict[str, Any] = {}

        class CtxValidator(SchemaValidator):
            def run_predicates(
                self,
                record: dict[str, Any],
                errors: list[str],
                warnings: list[str],
                **ctx: Any,
            ) -> None:
                captured.update(ctx)

        v = CtxValidator(DEMO_SCHEMA)
        v.validate({"id": "ok", "value": 1}, document_type="manuscript", flag="X")
        assert captured == {"document_type": "manuscript", "flag": "X"}


# ---- Checkpoint ------------------------------------------------------------


VERIFIER_STYLE_STAGES = {
    1: "claim_inventory",
    2: "existence",
    3: "alignment",
}

SUMMARIZER_STYLE_STAGES = {
    1: "extract",
    2: "summarize",
    3: "validate",
}


def _findings(*ids: str) -> list[dict[str, Any]]:
    return [{"id": i} for i in ids]


class TestCheckpointAlternateFirstStage:
    """Verifier-style: Stage 1 writes to a fixed alternate filename."""

    def _cp(self, tmp_path: Path) -> Checkpoint:
        return Checkpoint(
            VERIFIER_STYLE_STAGES,
            audits_root=tmp_path,
            stage_one_alternate_filename="claim_inventory.json",
            stage_one_payload_key="claim_inventory",
        )

    def test_stage_one_writes_alternate_filename(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        path = cp.write(
            "doc-a", 1, [], [], "manuscript",
            stage_one_payload={"items": [{"id": "C001"}]},
        )
        assert path == tmp_path / "doc-a" / "claim_inventory.json"

    def test_stage_one_requires_payload(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        with pytest.raises(ValueError, match="claim_inventory"):
            cp.write("doc-a", 1, [], [], "manuscript")

    def test_load_returns_payload(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        cp.write(
            "doc-a", 1, [], [], "manuscript",
            stage_one_payload={"items": [{"id": "C001"}]},
        )
        state = cp.load("doc-a")
        assert state.stage_one_payload == {"items": [{"id": "C001"}]}
        assert state.completed_stages == [1]
        assert state.next_stage == 2

    def test_contiguous_resume_with_gap(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        cp.write("doc-a", 1, [], [], "manuscript",
                 stage_one_payload={"items": []})
        # Skip stage 2; write stage 3 directly.
        cp.write("doc-a", 3, [], [], "manuscript")
        state = cp.load("doc-a")
        assert state.completed_stages == [1]
        assert state.next_stage == 2

    def test_findings_validator_blocks_invalid_writes(self, tmp_path: Path) -> None:
        def reject_all(
            _f: dict[str, Any], _dt: str, **_kw: Any
        ) -> tuple[bool, list[str], list[str]]:
            return False, ["always-reject"], []

        cp = Checkpoint(
            VERIFIER_STYLE_STAGES,
            audits_root=tmp_path,
            findings_validator=reject_all,
            stage_one_alternate_filename="claim_inventory.json",
        )
        cp.write("doc-a", 1, [], [], "manuscript",
                 stage_one_payload={"items": []})
        with pytest.raises(ValueError, match="failed validation"):
            cp.write("doc-a", 2, _findings("F001"), [], "manuscript")


class TestCheckpointUniformStages:
    """Summarizer-style: every stage uses the uniform 0N_<name>.json filename."""

    def _cp(self, tmp_path: Path) -> Checkpoint:
        return Checkpoint(SUMMARIZER_STYLE_STAGES, audits_root=tmp_path)

    def test_round_trip(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        cp.write("paper-x", 1, _findings("F1", "F2"), [], "general")
        cp.write("paper-x", 2, _findings("F3"), [], "general")
        state = cp.load("paper-x")
        assert state.completed_stages == [1, 2]
        assert state.next_stage == 3
        assert {f["id"] for f in state.findings} == {"F1", "F2", "F3"}

    def test_no_audit_dir_returns_empty_state(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        state = cp.load("nonexistent")
        assert state.completed_stages == []
        assert state.next_stage == 1
        assert state.findings == []

    def test_invalid_stage_raises(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        with pytest.raises(ValueError, match="stage must be one of"):
            cp.write("paper-x", 99, [], [], "general")

    def test_next_stage_past_last_completed(self, tmp_path: Path) -> None:
        cp = self._cp(tmp_path)
        for s in (1, 2, 3):
            cp.write("paper-x", s, [], [], "general")
        state = cp.load("paper-x")
        assert state.completed_stages == [1, 2, 3]
        # next_stage = max + 1 when all configured stages are complete
        assert state.next_stage == 4

    def test_payload_without_alt_filename_raises(self, tmp_path: Path) -> None:
        """Passing stage_one_payload to a Checkpoint without
        stage_one_alternate_filename is a misconfiguration — the kit must
        surface it loudly rather than silently drop the payload."""
        cp = self._cp(tmp_path)
        with pytest.raises(ValueError, match="stage_one_alternate_filename"):
            cp.write(
                "paper-x", 1, [], [], "general",
                stage_one_payload={"items": []},
            )


# ---- slugify ---------------------------------------------------------------


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_punctuation(self) -> None:
        assert slugify("A: B/C — D!") == "a-b-c-d"

    def test_truncates_to_max_len(self) -> None:
        assert len(slugify("x" * 200)) == 60

    def test_empty_returns_untitled(self) -> None:
        assert slugify("") == "untitled"
        assert slugify("    ") == "untitled"


# ---- replay_state ----------------------------------------------------------


class TestReplayState:
    def test_returns_dict_shape(self, tmp_path: Path) -> None:
        cp = Checkpoint(SUMMARIZER_STYLE_STAGES, audits_root=tmp_path)
        cp.write("paper-x", 1, _findings("F1"), [], "general")
        cp.write("paper-x", 2, _findings("F2"), [], "general")
        out = replay_state(cp, "paper-x")
        assert set(out.keys()) == {
            "slug",
            "audit_dir",
            "completed_stages",
            "next_stage",
            "stage_one_payload",
            "findings",
            "verification_matrix",
        }
        assert out["slug"] == "paper-x"
        assert out["completed_stages"] == [1, 2]
        assert isinstance(out["audit_dir"], str)

    def test_upto_stage_truncates_completed_list(self, tmp_path: Path) -> None:
        cp = Checkpoint(SUMMARIZER_STYLE_STAGES, audits_root=tmp_path)
        for s in (1, 2, 3):
            cp.write("paper-x", s, _findings(f"F{s}"), [], "general")
        out = replay_state(cp, "paper-x", upto_stage=2)
        assert out["completed_stages"] == [1, 2]

    def test_no_audit_dir_returns_empty_replay(self, tmp_path: Path) -> None:
        cp = Checkpoint(SUMMARIZER_STYLE_STAGES, audits_root=tmp_path)
        out = replay_state(cp, "missing-slug")
        assert out["completed_stages"] == []
        assert out["findings"] == []


# ---- ResumeState dataclass shape ------------------------------------------


def test_resume_state_default_values() -> None:
    state = ResumeState(slug="x", audit_dir=Path("/tmp/x"))
    assert state.completed_stages == []
    assert state.next_stage == 1
    assert state.stage_one_payload is None
    assert state.findings == []
    assert state.verification_matrix == []


# ---- Wrapper modules still import cleanly ---------------------------------


def test_verifier_wrappers_import_and_instantiate() -> None:
    """Regression guard: the verifier's wrapper modules must continue to
    import + instantiate cleanly after Sprint 3 extraction. We don't
    exercise their behavior here (test_validation.py + test_checkpoint.py
    do that); we just confirm the bridge from skill scripts/ to kit works.
    """
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(
        0, str(repo_root / "skills" / "research-accuracy-verifier" / "scripts")
    )
    sys.path.insert(
        0, str(repo_root / "skills" / "research-paper-summarizer" / "scripts")
    )

    from validate_finding import FindingValidator
    from checkpoint import write_stage_artifact, load_resume_state, STAGE_NAMES
    from validate_stats import StatsValidator

    assert STAGE_NAMES[1] == "claim_inventory"
    assert callable(write_stage_artifact)
    assert callable(load_resume_state)
    fv = FindingValidator()
    sv = StatsValidator()
    # Both validators expose the SchemaValidator surface.
    assert hasattr(fv, "validate")
    assert hasattr(sv, "validate")
    assert hasattr(fv, "run_predicates")
    assert hasattr(sv, "run_predicates")
