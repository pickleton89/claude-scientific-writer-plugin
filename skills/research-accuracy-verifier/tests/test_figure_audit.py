"""Tests for the FIGURE_INTEGRITY parallel family (Track D inbound audit).

Covers schema + predicates FD-P1..FD-P7 (validate_figure_finding.py) and the
Tier-1 deterministic adapter (figure_axis_lint.py). Mirrors the two-stage
pattern: schema failures must NOT short-circuit predicate checks. The family is
advisory/triage — these tests also pin the two guardrails (categorical tells
dominate; aesthetic/D6 signals can never be CRITICAL; over-minimization is a
valid D6 note, never a flag).
"""

from __future__ import annotations

from typing import Any

import pytest

from figure_axis_lint import (
    check_axis_truncation,
    check_closure_rule,
    run_tier1,
)
from validate_figure_finding import (
    FigureFindingValidator,
    validate_audit_verdict,
)


def _base_finding(**overrides: Any) -> dict[str, Any]:
    """A schema-valid, predicate-clean Tier-1 finding; mutate per test."""
    f: dict[str, Any] = {
        "id": "FA001",
        "figure_ref": {"file": "inbound.svg", "panel": None, "region": "y-axis"},
        "dimension": "D2_quant_semantic",
        "metric_id": "2.2",
        "score": 2,
        "categorical": True,
        "severity": "CRITICAL",
        "tier": "1_deterministic",
        "source_check": "validate_data.check_closure",
        "observation": "pie slices sum to 92%, not 100%",
        "evidence_snippet": None,
        "recommended_action": "obtain source data and reconcile the parts to the whole",
        "confidence": "high",
        "decaying_signal_caveat": None,
    }
    f.update(overrides)
    return f


@pytest.fixture
def validator() -> FigureFindingValidator:
    return FigureFindingValidator()


class TestSchema:
    def test_base_finding_is_valid(self, validator: FigureFindingValidator) -> None:
        ok, errors, _ = validator.validate(_base_finding())
        assert ok, errors

    def test_bad_id_pattern_fails_schema(
        self, validator: FigureFindingValidator
    ) -> None:
        ok, errors, _ = validator.validate(_base_finding(id="001"))
        assert not ok

    def test_unknown_dimension_fails_schema(
        self, validator: FigureFindingValidator
    ) -> None:
        ok, errors, _ = validator.validate(_base_finding(dimension="D9_made_up"))
        assert not ok

    def test_schema_failure_does_not_short_circuit_predicates(
        self, validator: FigureFindingValidator
    ) -> None:
        # bad score (schema) AND a dispositive action (FD-P4) — both must surface.
        bad = _base_finding(score=5, recommended_action="conclude misconduct")
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P4" in e for e in errors)


class TestFDP1:
    def test_categorical_matches_metric(
        self, validator: FigureFindingValidator
    ) -> None:
        ok, errors, _ = validator.validate(
            _base_finding(metric_id="2.2", categorical=True)
        )
        assert ok, errors

    def test_categorical_mismatch_fails(
        self, validator: FigureFindingValidator
    ) -> None:
        # 6.1 is NOT a categorical metric
        bad = _base_finding(
            metric_id="6.1",
            categorical=True,
            dimension="D6_stylistic",
            severity="MINOR",
            score=1,
        )
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P1" in e for e in errors)


class TestFDP2:
    def test_critical_requires_categorical_and_score2(
        self, validator: FigureFindingValidator
    ) -> None:
        # non-categorical metric scored CRITICAL must fail
        bad = _base_finding(
            metric_id="2.3", categorical=False, severity="CRITICAL", score=2
        )
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P2" in e for e in errors)

    def test_categorical_score1_cannot_be_critical(
        self, validator: FigureFindingValidator
    ) -> None:
        bad = _base_finding(severity="CRITICAL", score=1)
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P2" in e for e in errors)


class TestFDP3:
    def test_d6_capped_at_minor(self, validator: FigureFindingValidator) -> None:
        bad = _base_finding(
            dimension="D6_stylistic",
            metric_id="6.2",
            categorical=False,
            severity="MAJOR",
            score=2,
            recommended_action="flag for closer human review",
        )
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P3" in e for e in errors)

    def test_d6_over_minimization_note_is_valid(
        self, validator: FigureFindingValidator
    ) -> None:
        # the two-sided guard: an over-minimization note is legitimate D6 output
        ok, errors, _ = validator.validate(
            _base_finding(
                dimension="D6_stylistic",
                metric_id="6.1",
                categorical=False,
                severity="INFORMATIONAL",
                score=1,
                tier="3_vision_judge",
                source_check=None,
                observation="figure stripped to a bland default; over-minimized",
                recommended_action="flag for closer human review",
            )
        )
        assert ok, errors


class TestFDP4:
    def test_dispositive_verb_rejected(self, validator: FigureFindingValidator) -> None:
        bad = _base_finding(recommended_action="conclude misconduct by the authors")
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P4" in e for e in errors)

    def test_non_template_action_rejected(
        self, validator: FigureFindingValidator
    ) -> None:
        bad = _base_finding(recommended_action="rewrite the whole figure")
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P4" in e for e in errors)

    def test_allowed_template_passes(self, validator: FigureFindingValidator) -> None:
        ok, errors, _ = validator.validate(
            _base_finding(recommended_action="request provenance / AI-use disclosure")
        )
        assert ok, errors


class TestFDP5:
    def test_d4_requires_caveat(self, validator: FigureFindingValidator) -> None:
        bad = _base_finding(
            dimension="D4_render_artifact",
            metric_id="4.1",
            categorical=False,
            severity="MINOR",
            score=1,
            tier="3_vision_judge",
            source_check=None,
            recommended_action="flag for closer human review",
            decaying_signal_caveat=None,
        )
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P5" in e for e in errors)

    def test_d4_with_caveat_passes(self, validator: FigureFindingValidator) -> None:
        ok, errors, _ = validator.validate(
            _base_finding(
                dimension="D4_render_artifact",
                metric_id="4.1",
                categorical=False,
                severity="MINOR",
                score=1,
                tier="3_vision_judge",
                source_check=None,
                recommended_action="flag for closer human review",
                decaying_signal_caveat="2026-gen models pass cleanly; 0 is not exoneration",
            )
        )
        assert ok, errors


class TestFDP6:
    def test_tier1_requires_source_check(
        self, validator: FigureFindingValidator
    ) -> None:
        bad = _base_finding(tier="1_deterministic", source_check=None)
        ok, errors, _ = validator.validate(bad)
        assert not ok
        assert any("FD-P6" in e for e in errors)


class TestFDP7AuditVerdict:
    def test_flag_requires_hard_finding(self) -> None:
        # only a soft D6 finding present -> FIGURE_INTEGRITY_FLAG is illegal
        soft = _base_finding(
            dimension="D6_stylistic",
            metric_id="6.2",
            categorical=False,
            severity="MINOR",
            score=1,
            tier="3_vision_judge",
            source_check=None,
            recommended_action="flag for closer human review",
        )
        ok, errors = validate_audit_verdict("FIGURE_INTEGRITY_FLAG", [soft])
        assert not ok
        assert any("FD-P7" in e for e in errors)

    def test_flag_with_categorical_finding_passes(self) -> None:
        ok, errors = validate_audit_verdict("FIGURE_INTEGRITY_FLAG", [_base_finding()])
        assert ok, errors

    def test_no_positive_evidence_with_empty_findings_passes(self) -> None:
        ok, errors = validate_audit_verdict("FIGURE_NO_POSITIVE_EVIDENCE", [])
        assert ok, errors

    def test_unknown_verdict_fails(self) -> None:
        ok, errors = validate_audit_verdict("CONTRADICTED", [])
        assert not ok


class TestTier1Adapter:
    def test_closure_failure_is_categorical_critical(self) -> None:
        findings = check_closure_rule([40, 35, 30], "pie", figure_file="f.png")
        assert len(findings) == 1
        assert findings[0]["categorical"] is True
        assert findings[0]["severity"] == "CRITICAL"
        assert findings[0]["metric_id"] == "2.2"

    def test_closure_ok_emits_nothing(self) -> None:
        assert check_closure_rule([25, 25, 50], "pie", figure_file="f.png") == []

    def test_axis_truncation_flags_nonzero_baseline(self) -> None:
        findings = check_axis_truncation(
            {
                "chart": "bar",
                "type": "quantitative",
                "min": 80,
                "max": 100,
                "data_min": 0,
            },
            figure_file="f.png",
        )
        assert len(findings) == 1
        assert findings[0]["metric_id"] == "2.3"
        assert findings[0]["categorical"] is False

    def test_axis_zero_baseline_ok(self) -> None:
        assert (
            check_axis_truncation(
                {"chart": "bar", "type": "quantitative", "min": 0, "max": 100},
                figure_file="f.png",
            )
            == []
        )

    def test_run_tier1_skips_when_no_source(self) -> None:
        out = run_tier1()
        assert out["findings"] == []
        assert out["note"] == "tier1_skipped_no_source"

    def test_run_tier1_emits_for_supplied_parts(self) -> None:
        out = run_tier1(parts=[40, 35, 30], closure_encoding="pie", figure_file="f.png")
        assert out["note"] == "ok"
        assert any(f["metric_id"] == "2.2" for f in out["findings"])

    def test_tier1_findings_validate_against_schema_and_predicates(self) -> None:
        """Every Tier-1 finding the adapter emits must pass the validator."""
        out = run_tier1(
            parts=[40, 35, 30],
            closure_encoding="pie",
            axis_meta={"chart": "bar", "type": "quantitative", "min": 80, "max": 100},
            figure_file="f.png",
        )
        v = FigureFindingValidator()
        for f in out["findings"]:
            ok, errors, _ = v.validate(f)
            assert ok, (f["id"], errors)
