"""Tests for regression/score.py — evidence-pin matcher (Sprint 4)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REGRESSION_DIR = Path(__file__).parent.parent / "regression"
sys.path.insert(0, str(REGRESSION_DIR))

from score import (  # noqa: E402
    _evidence_pin_satisfied,
    _finding_matches_expectation,
    _needle_in_haystack,
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
