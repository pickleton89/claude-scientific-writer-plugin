"""Tests for validate_intake.py and validate_finding.py.

Covers schema validation + business rules + predicates P1-P5 from CONTRACTS.md.
Two-stage pattern: schema failures must NOT short-circuit predicate checks.
"""

from __future__ import annotations

from typing import Any


from validate_finding import FindingValidator
from validate_intake import IntakeValidator, TIER_CHECKS


# ---------- IntakeValidator -----------------------------------------------


class TestIntakeValidator:
    def test_valid_tier_intake_passes(self, sample_intake: dict[str, Any]) -> None:
        ok, errors, _ = IntakeValidator().validate(sample_intake)
        assert ok, errors

    def test_custom_tier_requires_checks_enabled(
        self, sample_intake_custom: dict[str, Any]
    ) -> None:
        ok, errors, _ = IntakeValidator().validate(sample_intake_custom)
        assert ok, errors

    def test_custom_tier_without_checks_fails(self) -> None:
        intake = {
            "document_type": "manuscript",
            "sources_available": "none",
            "verification_tier": "custom",
            "domain": "general",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("checks_enabled" in e for e in errors)

    def test_other_doctype_requires_other_label(self) -> None:
        intake = {
            "document_type": "other",
            "sources_available": "none",
            "verification_tier": "1",
            "domain": "general",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("document_type_other" in e for e in errors)

    def test_invalid_enum_fails(self) -> None:
        intake = {
            "document_type": "novella",  # not in enum
            "sources_available": "none",
            "verification_tier": "1",
            "domain": "general",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("schema" in e for e in errors)

    def test_schema_failure_does_not_short_circuit_business_rules(self) -> None:
        """Two-stage pattern: even when schema fails, business rules MUST also report."""
        intake = {
            "document_type": "other",
            # missing document_type_other (business rule)
            "sources_available": "garbage",  # schema failure
            "verification_tier": "1",
            "domain": "general",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        # Both schema and business rule errors must appear
        assert any("schema" in e for e in errors), "schema error missing"
        assert any("document_type_other" in e for e in errors), "business rule error missing"

    def test_expand_tier_populates_checks(self, sample_intake: dict[str, Any]) -> None:
        out = IntakeValidator().expand_tier(sample_intake)
        assert out["checks_enabled"] == TIER_CHECKS["2"]


# ---------- FindingValidator (P1-P5) ----------------------------------------


class TestFindingValidator:
    def test_valid_critical_finding_passes(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        ok, errors, _ = FindingValidator().validate(sample_finding_critical, "manuscript")
        assert ok, errors

    def test_p1_unverified_critical_fails(
        self, sample_finding_unverified: dict[str, Any]
    ) -> None:
        """P1: UNVERIFIED MUST NOT have severity == CRITICAL."""
        bad = dict(sample_finding_unverified)
        bad["severity"] = "CRITICAL"
        ok, errors, _ = FindingValidator().validate(bad, "manuscript")
        assert not ok
        assert any("P1" in e for e in errors)

    def test_p1_unverified_without_reason_fails(self) -> None:
        finding = {
            "id": "F",
            "location": {"section": "X", "paragraph": 1},
            "claim_verbatim": "claim",
            "claim_type": "uncited",
            "verification_path": [
                {"method": "web_search", "tool": "WebSearch", "result_summary": "no hits"}
            ],
            "evidence": [{"source": "WebSearch", "url": "https://example.com"}],
            "verdict": "UNVERIFIED",
            "severity": "INFORMATIONAL",
            "recommended_action": "do something",
            "confidence": "low",
            # missing reason
        }
        ok, errors, _ = FindingValidator().validate(finding, "manuscript")
        assert not ok
        assert any("P1" in e and "reason" in e for e in errors)

    def test_p2_critical_requires_two_verification_paths(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        """P2: CRITICAL severity requires len(verification_path) >= 2."""
        bad = dict(sample_finding_critical)
        bad["verification_path"] = [bad["verification_path"][0]]  # only 1
        ok, errors, _ = FindingValidator().validate(bad, "manuscript")
        assert not ok
        assert any("P2" in e for e in errors)

    def test_p3_evidence_required(self, sample_finding_critical: dict[str, Any]) -> None:
        """P3: ≥1 evidence with resolvable URL/PMID/DOI."""
        bad = dict(sample_finding_critical)
        bad["evidence"] = [{"source": "ghost", "url": "  "}]  # blank URL
        ok, errors, _ = FindingValidator().validate(bad, "manuscript")
        assert not ok
        assert any("P3" in e for e in errors)

    def test_p4_quote_verdicts_require_quote_claim_type(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        """P4: QUOTE_* verdicts only valid for direct_quote claim type."""
        bad = dict(sample_finding_critical)
        bad["verdict"] = "QUOTE_VERIFIED"
        # claim_type is citation_bearing, not direct_quote — must fail
        # also need to update severity to match QUOTE_VERIFIED × manuscript = INFORMATIONAL
        bad["severity"] = "INFORMATIONAL"
        ok, errors, _ = FindingValidator().validate(bad, "manuscript")
        assert not ok
        assert any("P4" in e for e in errors)

    def test_p5_severity_must_match_matrix(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        """P5: severity is computed from matrix; user override is rejected."""
        # UNSUPPORTED × memo = MINOR per matrix; finding has CRITICAL
        ok, errors, _ = FindingValidator().validate(sample_finding_critical, "memo")
        assert not ok
        assert any("P5" in e for e in errors)

    def test_p5_correct_severity_for_memo(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        """Same finding with severity matching memo matrix should pass."""
        good = dict(sample_finding_critical)
        good["severity"] = "MINOR"  # matrix[memo][UNSUPPORTED]
        # Adjust verification_path: P2 only triggers for CRITICAL, so MINOR is fine with 2 paths
        ok, errors, _ = FindingValidator().validate(good, "memo")
        assert ok, errors

    def test_quote_verified_finding_passes(
        self, sample_finding_quote_verified: dict[str, Any]
    ) -> None:
        ok, errors, _ = FindingValidator().validate(sample_finding_quote_verified, "manuscript")
        assert ok, errors

    def test_schema_failure_does_not_short_circuit_predicates(self) -> None:
        """Two-stage: even with bad enum, predicate checks must also run."""
        finding = {
            "id": "F",
            "location": {"section": "X", "paragraph": 1},
            "claim_verbatim": "claim",
            "claim_type": "citation_bearing",
            "verification_path": [],  # P2 violation: empty
            "evidence": [],  # P3 violation: empty
            "verdict": "INVENTED_VERDICT",  # schema failure
            "severity": "CRITICAL",
            "recommended_action": "x",
            "confidence": "high",
        }
        ok, errors, _ = FindingValidator().validate(finding, "manuscript")
        assert not ok
        assert any("schema" in e for e in errors), "schema error missing"
        assert any("P3" in e for e in errors), "P3 predicate not run after schema failure"

    def test_matrix_lookup_covers_all_70_cells(self) -> None:
        v = FindingValidator()
        verdicts = [
            "VERIFIED",
            "METADATA_MISMATCH",
            "UNSUPPORTED",
            "OVERGENERALIZED",
            "CONTRADICTED",
            "MISATTRIBUTED",
            "QUOTE_VERIFIED",
            "QUOTE_PARAPHRASED",
            "QUOTE_FABRICATED",
            "UNVERIFIED",
        ]
        doc_types = ["grant", "manuscript", "lit_review", "slides", "report", "memo", "other"]
        cells = 0
        for dt in doc_types:
            for vd in verdicts:
                sev = v.expected_severity(dt, vd)
                assert sev in {"CRITICAL", "MAJOR", "MINOR", "INFORMATIONAL"}, (dt, vd, sev)
                cells += 1
        assert cells == 70
