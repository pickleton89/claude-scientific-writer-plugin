"""Tests for regression/score.py — evidence-pin matcher (Sprint 4)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REGRESSION_DIR = Path(__file__).parent.parent / "regression"
sys.path.insert(0, str(REGRESSION_DIR))

from score import (  # noqa: E402
    DocScore,
    _evidence_pin_satisfied,
    _finding_matches_expectation,
    _ledger_hit_rate,
    _needle_in_haystack,
    aggregate,
    extract_artifact_coverage,
    extract_r_predicate_audit,
    seeded_error_satisfied,
)


PIN_GT06 = {
    "paper_id": "smith2024_pembro_nsclc",
    "claim_id": "C-01",
    "value_in_source": 187,
}


def _finding_with_evidence(evidence: list[dict], **overrides) -> dict:
    base = {
        "id": "F001",
        "verdict": "CONTRADICTED",
        "severity": "CRITICAL",
        "evidence": evidence,
    }
    base.update(overrides)
    return base


# ----- _needle_in_haystack ---------------------------------------------------


class TestNeedleInHaystack:
    @pytest.mark.parametrize(
        "needle,haystack,expected",
        [
            # plain substring for non-numeric needles
            ("smith2024_pembro_nsclc", "src=smith2024_pembro_nsclc.txt", True),
            ("C-01", "stats.json (C-01)", True),
            ("C-01", "stats.json (C-99)", False),
            # numeric needles must not match inside larger numbers
            ("187", "value=187, unit=patients", True),
            ("187", "1870 patients enrolled", False),
            ("1", "187 patients", False),
            ("1", "n=1 case report", True),
            # decimal needles
            ("47.3", "47.3% (95% CI 38.1–55.9%)", True),
            ("47.3", "147.3 percent", False),
            ("47.3", "47.30 percent", False),
            ("0.001", "p<0.001", True),
            ("0.001", "p=0.0011", False),
            # empty needle is vacuously satisfied
            ("", "anything", True),
        ],
    )
    def test_boundary_matching(self, needle, haystack, expected):
        assert _needle_in_haystack(needle, haystack) is expected


# ----- _evidence_pin_satisfied -----------------------------------------------


class TestEvidencePin:
    def test_empty_expectation_passes(self):
        assert _evidence_pin_satisfied({}, []) is True
        assert _evidence_pin_satisfied(None, []) is True

    def test_missing_evidence_fails_when_pin_required(self):
        assert _evidence_pin_satisfied(PIN_GT06, []) is False
        assert _evidence_pin_satisfied(PIN_GT06, None) is False  # type: ignore[arg-type]

    def test_single_entry_witnesses_all_keys(self):
        evidence = [
            {
                "source": "smith2024_pembro_nsclc_stats.json (C-01)",
                "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json",
                "snippet": "value=187, unit=patients, stat_type=sample_size",
            }
        ]
        assert _evidence_pin_satisfied(PIN_GT06, evidence) is True

    def test_split_across_entries_fails(self):
        # paper_id + value in one entry, claim_id in another — per-entry rule rejects.
        evidence = [
            {
                "source": "smith2024_pembro_nsclc.txt",
                "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt",
                "snippet": "We enrolled 187 patients",
            },
            {
                "source": "stats.json (C-01)",
                "url": "elsewhere",
                "snippet": "claim_id=C-01",
            },
        ]
        assert _evidence_pin_satisfied(PIN_GT06, evidence) is False

    def test_wrong_claim_id_fails(self):
        evidence = [
            {
                "source": "smith2024_pembro_nsclc_stats.json (C-99)",
                "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json",
                "snippet": "value=187, unit=patients",
            }
        ]
        assert _evidence_pin_satisfied(PIN_GT06, evidence) is False

    def test_numeric_value_not_substring_of_larger_number(self):
        # value_in_source=187 must not match an evidence entry that mentions
        # 1870 — protects against false-positive recall as fixtures grow.
        evidence = [
            {
                "source": "smith2024_pembro_nsclc_stats.json (C-01)",
                "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json",
                "snippet": "value=1870, unit=person-years",
            }
        ]
        assert _evidence_pin_satisfied(PIN_GT06, evidence) is False

    def test_non_dict_entries_skipped(self):
        evidence = [
            "garbage string entry",
            {
                "source": "smith2024_pembro_nsclc_stats.json (C-01)",
                "url": "x",
                "snippet": "value=187",
            },
        ]
        assert _evidence_pin_satisfied(PIN_GT06, evidence) is True


# ----- _finding_matches_expectation integration ------------------------------


COOPERATION_EVIDENCE = [
    {
        "source": "smith2024_pembro_nsclc.txt Abstract Methods",
        "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt",
        "snippet": "We enrolled 187 patients",
    },
    {
        "source": "smith2024_pembro_nsclc_stats.json (C-01)",
        "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json",
        "snippet": "value=187, unit=patients, stat_type=sample_size",
    },
]

FALLBACK_EVIDENCE = [
    {
        "source": "smith2024_pembro_nsclc.txt Abstract Methods",
        "url": "regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt",
        "snippet": "We enrolled 187 patients",
    }
]


class TestFindingMatchesExpectation:
    def test_pin_satisfied_matches(self):
        expectation = {
            "verdict": "CONTRADICTED",
            "severity": "CRITICAL",
            "evidence_must_contain": PIN_GT06,
        }
        finding = _finding_with_evidence(COOPERATION_EVIDENCE)
        assert _finding_matches_expectation(expectation, [finding], []) is True

    def test_fallback_evidence_fails_pin(self):
        # Right verdict + severity, but evidence does not pin to claim_id.
        # This is the case Sprint 4 was designed to differentiate.
        expectation = {
            "verdict": "CONTRADICTED",
            "severity": "CRITICAL",
            "evidence_must_contain": PIN_GT06,
        }
        finding = _finding_with_evidence(FALLBACK_EVIDENCE)
        assert _finding_matches_expectation(expectation, [finding], []) is False

    def test_no_pin_unchanged_behavior(self):
        # Backwards-compat: expectations without evidence_must_contain are
        # scored on verdict + severity only (covers GT-01, GT-04).
        expectation = {"verdict": "CONTRADICTED", "severity": "CRITICAL"}
        finding = _finding_with_evidence(FALLBACK_EVIDENCE)
        assert _finding_matches_expectation(expectation, [finding], []) is True

    def test_severity_mismatch_blocks_even_with_good_pin(self):
        expectation = {
            "verdict": "CONTRADICTED",
            "severity": "MAJOR",
            "evidence_must_contain": PIN_GT06,
        }
        finding = _finding_with_evidence(COOPERATION_EVIDENCE, severity="CRITICAL")
        assert _finding_matches_expectation(expectation, [finding], []) is False

    def test_style_finding_with_pin(self):
        expectation = {
            "style_verdict": "STYLE_NONCONFORMING",
            "severity": "MINOR",
            "rule_id": "rule-foo",
            "evidence_must_contain": {"locator": "intro-p1"},
        }
        style_finding = {
            "id": "S001",
            "verdict": "STYLE_NONCONFORMING",
            "severity": "MINOR",
            "rule_id": "rule-foo",
            "evidence": [
                {"source": "draft", "url": "doc.md", "snippet": "matched at intro-p1"}
            ],
        }
        assert _finding_matches_expectation(expectation, [], [style_finding]) is True


# ----- seeded_error_satisfied end-to-end -------------------------------------


class TestSeededErrorSatisfied:
    def test_gt06_shape_with_cooperation_evidence(self):
        seeded = {
            "expected_findings_any_of": [
                {
                    "stage": 6,
                    "verdict": "CONTRADICTED",
                    "severity": "CRITICAL",
                    "evidence_must_contain": PIN_GT06,
                }
            ]
        }
        finding = _finding_with_evidence(COOPERATION_EVIDENCE)
        assert seeded_error_satisfied(seeded, [finding], []) is True

    def test_gt06_shape_with_fallback_evidence_now_misses(self):
        seeded = {
            "expected_findings_any_of": [
                {
                    "stage": 6,
                    "verdict": "CONTRADICTED",
                    "severity": "CRITICAL",
                    "evidence_must_contain": PIN_GT06,
                }
            ]
        }
        finding = _finding_with_evidence(FALLBACK_EVIDENCE)
        assert seeded_error_satisfied(seeded, [finding], []) is False


# ----- must_not_emit (wrong-but-valid-DOI guard, P9) -------------------------


def _doi_finding(verdict: str) -> dict:
    """A Stage-2 citation-existence finding with the given verdict."""
    return {
        "id": "F-08-1",
        "verdict": verdict,
        "severity": "MAJOR" if verdict == "METADATA_MISMATCH" else "INFORMATIONAL",
        "evidence": [
            {"source": "Crossref", "url": "https://doi.org/10.1093/oncolo/oyad180"}
        ],
    }


class TestMustNotEmit:
    """Ground-truth `must_not_emit` makes the VERIFIED false-positive a real,
    scored failure — not just an absent recall match. This is what lets the
    regression bed detect a verifier that falls into the wrong-but-valid-DOI
    trap (predicate P9)."""

    GT08 = {
        "expected_findings_any_of": [
            {"stage": 2, "verdict": "METADATA_MISMATCH", "severity": "MAJOR"}
        ],
        "must_not_emit": [{"stage": 2, "verdict": "VERIFIED"}],
    }

    def test_correct_catch_counts_as_satisfied(self):
        """METADATA_MISMATCH and no forbidden VERIFIED → caught."""
        assert (
            seeded_error_satisfied(self.GT08, [_doi_finding("METADATA_MISMATCH")], [])
            is True
        )

    def test_forbidden_verdict_alone_is_a_miss(self):
        """VERIFIED only (P9 not implemented) → not caught."""
        assert (
            seeded_error_satisfied(self.GT08, [_doi_finding("VERIFIED")], []) is False
        )

    def test_forbidden_verdict_overrides_a_valid_match(self):
        """Even if the right verdict is also present, emitting the forbidden
        VERIFIED for the same citation is a broken audit → not caught."""
        findings = [_doi_finding("METADATA_MISMATCH"), _doi_finding("VERIFIED")]
        assert seeded_error_satisfied(self.GT08, findings, []) is False

    def test_absent_must_not_emit_is_backward_compatible(self):
        """Ground truth without must_not_emit behaves exactly as before."""
        gt = {"expected_findings_any_of": [{"stage": 2, "verdict": "VERIFIED"}]}
        assert seeded_error_satisfied(gt, [_doi_finding("VERIFIED")], []) is True


# ----- artifact coverage extraction ------------------------------------------


def _write_sidecars(run_dir: Path, *, files: dict[str, dict]) -> None:
    import json as _json

    run_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in files.items():
        (run_dir / name).write_text(_json.dumps(payload))


class TestLedgerHitRate:
    def test_no_ledger(self):
        assert _ledger_hit_rate(None) == (0, None)

    def test_no_entries(self):
        assert _ledger_hit_rate({"entries": []}) == (0, None)

    def test_all_misses_no_reuse(self):
        ledger = {
            "entries": [
                {"id": "E1", "consumed_by_findings": ["F1"]},
                {"id": "E2", "consumed_by_findings": ["F2"]},
            ]
        }
        n, rate = _ledger_hit_rate(ledger)
        assert n == 2
        assert rate == 0.0

    def test_reuse_yields_hits(self):
        ledger = {
            "entries": [
                {"id": "E1", "consumed_by_findings": ["F1", "F2", "F3"]},
                {"id": "E2", "consumed_by_findings": ["F4"]},
            ]
        }
        n, rate = _ledger_hit_rate(ledger)
        assert n == 2
        assert rate == pytest.approx(2 / 4)

    def test_unconsumed_entries_ignored_in_total(self):
        ledger = {
            "entries": [
                {"id": "E1", "consumed_by_findings": []},
                {"id": "E2", "consumed_by_findings": ["F1", "F2"]},
            ]
        }
        n, rate = _ledger_hit_rate(ledger)
        assert n == 2
        assert rate == pytest.approx(1 / 2)


class TestArtifactCoverageExtraction:
    def test_all_artifacts_present(self, tmp_path):
        _write_sidecars(
            tmp_path,
            files={
                "document_inventory.json": {"x": 1},
                "reference_map.json": {"x": 1},
                "resolved_sources.json": {"x": 1},
                "external_evidence.json": {
                    "entries": [
                        {"id": "E1", "consumed_by_findings": ["F1", "F2"]},
                    ]
                },
            },
        )
        cov = extract_artifact_coverage(tmp_path)
        assert cov["document_inventory_present"] is True
        assert cov["reference_map_present"] is True
        assert cov["resolved_sources_present"] is True
        assert cov["external_evidence_entries"] == 1
        assert cov["ledger_hit_rate"] == pytest.approx(0.5)

    def test_partial_artifacts_present(self, tmp_path):
        _write_sidecars(
            tmp_path,
            files={
                "document_inventory.json": {"x": 1},
                "external_evidence.json": {"entries": []},
            },
        )
        cov = extract_artifact_coverage(tmp_path)
        assert cov["document_inventory_present"] is True
        assert cov["reference_map_present"] is False
        assert cov["resolved_sources_present"] is False
        assert cov["external_evidence_entries"] == 0
        assert cov["ledger_hit_rate"] is None

    def test_all_artifacts_absent(self, tmp_path):
        cov = extract_artifact_coverage(tmp_path)
        assert cov["document_inventory_present"] is False
        assert cov["reference_map_present"] is False
        assert cov["resolved_sources_present"] is False
        assert cov["external_evidence_entries"] == 0
        assert cov["ledger_hit_rate"] is None

    def test_ledger_with_zero_consumption(self, tmp_path):
        _write_sidecars(
            tmp_path,
            files={
                "external_evidence.json": {
                    "entries": [
                        {"id": "E1", "consumed_by_findings": []},
                    ]
                },
            },
        )
        cov = extract_artifact_coverage(tmp_path)
        assert cov["external_evidence_entries"] == 1
        assert cov["ledger_hit_rate"] is None

    def test_ledger_with_high_reuse(self, tmp_path):
        _write_sidecars(
            tmp_path,
            files={
                "external_evidence.json": {
                    "entries": [
                        {"id": "E1", "consumed_by_findings": ["F1", "F2", "F3", "F4"]},
                    ]
                },
            },
        )
        cov = extract_artifact_coverage(tmp_path)
        assert cov["ledger_hit_rate"] == pytest.approx(0.75)

    def test_malformed_ledger_not_a_dict(self, tmp_path):
        (tmp_path / "external_evidence.json").write_text("[1, 2, 3]")
        cov = extract_artifact_coverage(tmp_path)
        assert cov["external_evidence_entries"] == 0
        assert cov["ledger_hit_rate"] is None


# ----- R-predicate audit extraction ------------------------------------------


class TestRPredicateAuditExtraction:
    def test_all_pass(self):
        audit = {
            "audit_meta": {
                "r_predicate_status": {
                    "R1": "pass",
                    "R2": "pass",
                    "R3": "pass",
                    "R4": "pass",
                    "R5": "pass",
                    "R6": "pass",
                }
            }
        }
        result = extract_r_predicate_audit(audit)
        assert result == {
            "R1": "pass",
            "R2": "pass",
            "R3": "pass",
            "R4": "pass",
            "R5": "pass",
            "R6": "pass",
        }

    def test_mixed_pass_fail(self):
        audit = {
            "audit_meta": {
                "r_predicate_status": {
                    "R1": "pass",
                    "R2": "fail",
                    "R3": "pass",
                    "R4": "fail",
                    "R5": "pass",
                    "R6": "pass",
                }
            }
        }
        result = extract_r_predicate_audit(audit)
        assert result["R2"] == "fail"
        assert result["R4"] == "fail"
        assert result["R1"] == "pass"

    def test_all_fail(self):
        audit = {
            "audit_meta": {
                "r_predicate_status": {
                    name: "fail" for name in ("R1", "R2", "R3", "R4", "R5", "R6")
                }
            }
        }
        result = extract_r_predicate_audit(audit)
        assert all(v == "fail" for v in result.values())

    def test_mixed_with_na(self):
        audit = {
            "audit_meta": {
                "r_predicate_status": {
                    "R1": "pass",
                    "R2": "n/a",
                    "R3": "fail",
                    "R4": "n/a",
                    "R5": "pass",
                }
            }
        }
        result = extract_r_predicate_audit(audit)
        assert result["R2"] == "n/a"
        assert result["R4"] == "n/a"
        assert result["R6"] == "n/a"

    def test_legacy_field_name(self):
        audit = {
            "audit_meta": {
                "r_predicates": {
                    "R1": "pass",
                    "R2": "fail",
                }
            }
        }
        result = extract_r_predicate_audit(audit)
        assert result["R1"] == "pass"
        assert result["R2"] == "fail"
        assert result["R3"] == "n/a"

    def test_missing_audit_meta(self):
        result = extract_r_predicate_audit({})
        assert result == {name: "n/a" for name in ("R1", "R2", "R3", "R4", "R5", "R6")}

    def test_invalid_status_value_coerced_to_na(self):
        audit = {"audit_meta": {"r_predicate_status": {"R1": "maybe", "R2": "pass"}}}
        result = extract_r_predicate_audit(audit)
        assert result["R1"] == "n/a"
        assert result["R2"] == "pass"


# ----- aggregate() new outputs -----------------------------------------------


def _docscore_with(coverage_rows: list[dict], r_rows: list[dict]) -> DocScore:
    s = DocScore(doc_id="d", arm="post_fork")
    s.artifact_coverage_per_run = coverage_rows
    s.r_predicate_audit_per_run = r_rows
    s.verdict_tuples_per_run = [set()] * len(coverage_rows)
    return s


class TestAggregateNewColumns:
    def test_artifact_coverage_rate_all_present(self):
        rows = [
            {
                "document_inventory_present": True,
                "reference_map_present": True,
                "resolved_sources_present": True,
                "external_evidence_entries": 3,
                "ledger_hit_rate": 0.5,
            },
            {
                "document_inventory_present": True,
                "reference_map_present": True,
                "resolved_sources_present": True,
                "external_evidence_entries": 2,
                "ledger_hit_rate": 0.25,
            },
        ]
        s = _docscore_with(rows, [{"R1": "pass"} for _ in rows])
        agg = aggregate([s])
        assert agg["artifact_coverage_rate"] == 1.0
        assert agg["ledger_hit_rate_median"] == pytest.approx(0.375)
        assert agg["ledger_hit_rate_max"] == 0.5
        assert agg["ledger_hit_rate_min"] == 0.25

    def test_artifact_coverage_rate_partial(self):
        rows = [
            {
                "document_inventory_present": True,
                "reference_map_present": True,
                "resolved_sources_present": True,
                "external_evidence_entries": 1,
                "ledger_hit_rate": 0.0,
            },
            {
                "document_inventory_present": False,
                "reference_map_present": True,
                "resolved_sources_present": True,
                "external_evidence_entries": 0,
                "ledger_hit_rate": None,
            },
        ]
        s = _docscore_with(rows, [{} for _ in rows])
        agg = aggregate([s])
        assert agg["artifact_coverage_rate"] == 0.5

    def test_r_predicate_pass_rate_ignores_na(self):
        rows = [
            {
                "R1": "pass",
                "R2": "fail",
                "R3": "n/a",
                "R4": "pass",
                "R5": "pass",
                "R6": "n/a",
            },
            {
                "R1": "pass",
                "R2": "pass",
                "R3": "n/a",
                "R4": "fail",
                "R5": "pass",
                "R6": "n/a",
            },
        ]
        coverage_rows = [
            {
                "document_inventory_present": True,
                "reference_map_present": True,
                "resolved_sources_present": True,
                "external_evidence_entries": 1,
                "ledger_hit_rate": None,
            }
            for _ in rows
        ]
        s = _docscore_with(coverage_rows, rows)
        agg = aggregate([s])
        rates = agg["r_predicate_pass_rate"]
        assert rates["R1"] == 1.0
        assert rates["R2"] == 0.5
        assert rates["R3"] is None
        assert rates["R4"] == 0.5
        assert rates["R5"] == 1.0
        assert rates["R6"] is None
