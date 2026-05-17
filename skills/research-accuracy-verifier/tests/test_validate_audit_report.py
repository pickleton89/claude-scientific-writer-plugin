"""Tests for validate_audit_report.py — predicate P8 (Tier-3 cherry-picking sweep)."""

from __future__ import annotations

from typing import Any

from validate_audit_report import AuditReportValidator, run_p8


def _stage3_verified_matrix_entry(claim_id: str = "C012") -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "verdict": "VERIFIED",
        "severity": "INFORMATIONAL",
        "stage": "3",
    }


def _cherry_picking_finding(
    claim_id: str = "C012", *, usi: float = 0.25
) -> dict[str, Any]:
    """Valid Stage-4 cherry-picking finding pinned to `claim_id`."""
    return {
        "id": "F-CP-1",
        "location": {"section": "Discussion", "paragraph": 3, "line": None},
        "claim_verbatim": "Mechanism Z is well-established.",
        "claim_type": "citation_bearing",
        "verification_path": [
            {
                "method": "scite_context",
                "tool": "Scite MCP (search_literature)",
                "result_summary": (
                    f"cherry_picking:{claim_id} — USI={usi:.2f}, supporting=4, "
                    "contrasting=12, per Scite classification"
                ),
            }
        ],
        "evidence": [
            {
                "source": "Scite",
                "url": "https://doi.org/10.1234/example",
                "snippet": (
                    f"USI={usi:.2f}; supporting=4; contrasting=12; "
                    "consensus contested."
                ),
            }
        ],
        "verdict": "OVERGENERALIZED",
        "severity": "MAJOR",
        "recommended_action": "Add a contrasting citation or scope-limit the claim.",
        "confidence": "medium",
    }


def _base_report() -> dict[str, Any]:
    return {
        "header": {
            "document_title": "Test Manuscript",
            "document_type": "manuscript",
            "date_checked": "2026-05-11",
            "verification_tier": "3",
            "sources_consulted": ["PubMed", "Scite", "OpenAlex"],
            "overall_confidence": "moderate",
            "confidence_justification": "Sample audit for P8 testing.",
            "coverage_caveats": [],
        },
        "executive_summary": (
            "Sample Tier-3 audit covering one Stage-3 VERIFIED claim. Used to "
            "exercise P8 cherry-picking sweep enforcement across both the "
            "finding-cover branch and the caveat-cover branch."
        ),
        "findings": [],
        "verification_matrix": [_stage3_verified_matrix_entry("C012")],
        "methodology_note": "Tier-3; PubMed + Scite + OpenAlex.",
    }


def _intake(
    *,
    domain: str = "biomedical",
    tier: str = "3",
    checks: list[str] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "document_type": "manuscript",
        "sources_available": "uploaded_files",
        "verification_tier": tier,
        "domain": domain,
        "flag_threshold": "standard",
    }
    if checks is not None:
        out["checks_enabled"] = checks
    return out


class TestP8Gating:
    """P8 only fires for biomedical/mixed Tier-3 (or custom + uncited_claims)."""

    def test_general_domain_skips_p8(self) -> None:
        report = _base_report()  # no cherry-picking coverage at all
        status, errors = run_p8(report, _intake(domain="general"))
        assert status == "n/a"
        assert errors == []

    def test_tier_1_skips_p8(self) -> None:
        report = _base_report()
        report["header"]["verification_tier"] = "1"
        status, errors = run_p8(report, _intake(tier="1"))
        assert status == "n/a"
        assert errors == []

    def test_tier_2_skips_p8(self) -> None:
        report = _base_report()
        report["header"]["verification_tier"] = "2"
        status, errors = run_p8(report, _intake(tier="2"))
        assert status == "n/a"
        assert errors == []

    def test_custom_tier_without_uncited_claims_skips_p8(self) -> None:
        report = _base_report()
        report["header"]["verification_tier"] = "custom"
        intake = _intake(
            tier="custom",
            checks=["citation_existence", "claim_alignment", "exact_quotes"],
        )
        status, errors = run_p8(report, intake)
        assert status == "n/a"

    def test_custom_tier_with_uncited_claims_activates_p8(self) -> None:
        report = _base_report()  # missing coverage
        report["header"]["verification_tier"] = "custom"
        intake = _intake(
            tier="custom",
            checks=["citation_existence", "claim_alignment", "uncited_claims"],
        )
        status, errors = run_p8(report, intake)
        assert status == "fail"
        assert any("C012" in e for e in errors)

    def test_mixed_domain_tier3_activates_p8(self) -> None:
        report = _base_report()
        status, errors = run_p8(report, _intake(domain="mixed"))
        assert status == "fail"
        assert any("C012" in e for e in errors)


class TestP8FindingCoverage:
    """A valid Stage-4 cherry-picking finding satisfies P8 for its claim_id."""

    def test_missing_coverage_fails(self) -> None:
        status, errors = run_p8(_base_report(), _intake())
        assert status == "fail"
        assert any("C012" in e for e in errors)

    def test_matching_finding_passes(self) -> None:
        report = _base_report()
        report["findings"].append(_cherry_picking_finding("C012"))
        status, errors = run_p8(report, _intake())
        assert status == "pass"
        assert errors == []

    def test_finding_missing_usi_does_not_count(self) -> None:
        """Without USI=, the finding doesn't count as cherry-picking coverage."""
        report = _base_report()
        f = _cherry_picking_finding("C012")
        f["verification_path"][0]["result_summary"] = (
            "cherry_picking:C012 — supporting=4, contrasting=12 (USI omitted)"
        )
        report["findings"].append(f)
        status, errors = run_p8(report, _intake())
        assert status == "fail"

    def test_finding_with_wrong_method_does_not_count(self) -> None:
        report = _base_report()
        f = _cherry_picking_finding("C012")
        f["verification_path"][0]["method"] = "web_search"  # not scite_context
        report["findings"].append(f)
        status, errors = run_p8(report, _intake())
        assert status == "fail"

    def test_finding_with_wrong_verdict_does_not_count(self) -> None:
        report = _base_report()
        f = _cherry_picking_finding("C012")
        f["verdict"] = "VERIFIED"  # cherry-picking must be OVERGENERALIZED
        f["severity"] = "INFORMATIONAL"
        report["findings"].append(f)
        status, errors = run_p8(report, _intake())
        assert status == "fail"

    def test_finding_pinned_to_different_claim_does_not_cover(self) -> None:
        """`cherry_picking:C013` must NOT satisfy a `C012` requirement."""
        report = _base_report()
        report["findings"].append(_cherry_picking_finding("C013"))
        status, errors = run_p8(report, _intake())
        assert status == "fail"
        assert any("C012" in e for e in errors)


class TestP8CaveatCoverage:
    """A `cherry_picking:<id>: <reason>` caveat satisfies P8 in lieu of a finding."""

    def test_caveat_with_reason_passes(self) -> None:
        report = _base_report()
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C012: scite_doi_not_indexed"
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass"

    def test_caveat_without_colon_reason_does_not_cover(self) -> None:
        """Tag prefix `cherry_picking:C012` without `: <reason>` is malformed
        and must not satisfy P8 (forces a real reason on every gap)."""
        report = _base_report()
        report["header"]["coverage_caveats"].append("cherry_picking:C012")
        status, errors = run_p8(report, _intake())
        assert status == "fail"

    def test_caveat_pinned_to_different_claim_does_not_cover(self) -> None:
        report = _base_report()
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C999: scite_doi_not_indexed"
        )
        status, errors = run_p8(report, _intake())
        assert status == "fail"
        assert any("C012" in e for e in errors)

    def test_caveat_for_some_claims_finding_for_others_passes(self) -> None:
        """Mixed coverage: some claims via finding, some via caveat."""
        report = _base_report()
        report["verification_matrix"].append(
            _stage3_verified_matrix_entry("C013")
        )
        report["findings"].append(_cherry_picking_finding("C012"))
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C013: tally_uncontested_USI=0.83"
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass"


class TestP8ClaimIdAmbiguity:
    """Defensive: `C1` should not falsely match `C12` (word-boundary check)."""

    def test_prefix_collision_in_finding_tag(self) -> None:
        """A finding tagged with `cherry_picking:C1` must NOT cover claim C12."""
        report = _base_report()
        report["verification_matrix"] = [_stage3_verified_matrix_entry("C12")]
        # Finding deliberately tagged with the *shorter* id C1
        f = _cherry_picking_finding("C12")
        f["verification_path"][0]["result_summary"] = (
            "cherry_picking:C1 — USI=0.30, supporting=2, contrasting=5"
        )
        report["findings"].append(f)
        status, errors = run_p8(report, _intake())
        assert status == "fail"
        assert any("C12" in e for e in errors)

    def test_prefix_collision_in_caveat(self) -> None:
        report = _base_report()
        report["verification_matrix"] = [_stage3_verified_matrix_entry("C12")]
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C1: misaligned tag"  # short id; should not match C12
        )
        status, errors = run_p8(report, _intake())
        assert status == "fail"


class TestP8WebSourceCarveOut:
    """Stage-3 VERIFIED claims sourced from the web (no DOI) cannot be swept
    via Scite tally. They satisfy P8 via a `coverage_caveats[]` entry of shape
    `cherry_picking:<claim_id>: web_source_no_doi_for_scite_tally`. The
    validator's `_caveat_covers_claim` already accepts any reason text after
    the `cherry_picking:<id>: ` prefix — this carve-out is a Stage-4 emit
    convention, not a validator code path. These tests pin the convention so
    a Stage-4 emit regression is caught.

    See skills/research-accuracy-verifier/references/stages/stage_4_uncited.md
    § "Web-sourced VERIFIED claims carve-out" for the canonical reason token.
    """

    def test_web_source_caveat_with_canonical_reason_passes(self) -> None:
        """The canonical reason token web_source_no_doi_for_scite_tally is the
        Stage-4 emit convention. Validator accepts via the generic prefix
        check — no special-case code, just the prefix + free-form reason."""
        report = _base_report()
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C012: web_source_no_doi_for_scite_tally"
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass", errors

    def test_web_source_caveat_pinned_to_different_claim_does_not_cover(
        self,
    ) -> None:
        """A web-source carve-out caveat for a different claim_id does NOT
        cover the actual Stage-3 VERIFIED claim. Same word-boundary logic as
        the standard P8 caveat path — the web-source reason doesn't relax it."""
        report = _base_report()
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C999: web_source_no_doi_for_scite_tally"
        )
        status, errors = run_p8(report, _intake())
        assert status == "fail"
        assert any("C012" in e for e in errors)

    def test_mixed_web_source_and_scite_caveats_pass(self) -> None:
        """Two Stage-3 VERIFIED claims: one DOI-based (covered by Scite-tally
        caveat), one web-sourced (covered by web-source carve-out caveat)."""
        report = _base_report()
        report["verification_matrix"].append(
            _stage3_verified_matrix_entry("C013")
        )
        report["header"]["coverage_caveats"].extend(
            [
                "cherry_picking:C012: tally_uncontested_USI=0.83",
                "cherry_picking:C013: web_source_no_doi_for_scite_tally",
            ]
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass", errors

    def test_mixed_finding_and_web_source_caveat_pass(self) -> None:
        """Two Stage-3 VERIFIED claims: one DOI-based with a real Stage-4
        cherry-picking finding (USI < 0.5), one web-sourced with a carve-out
        caveat. Both coverage paths exercised in the same audit."""
        report = _base_report()
        report["verification_matrix"].append(
            _stage3_verified_matrix_entry("C013")
        )
        report["findings"].append(_cherry_picking_finding("C012", usi=0.25))
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C013: web_source_no_doi_for_scite_tally"
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass", errors

    def test_multiple_web_sourced_claims_each_need_a_caveat(self) -> None:
        """One caveat per web-sourced VERIFIED claim — silence on any one is a
        P8 violation. Validates the standard P8 invariant carries through the
        web-source carve-out (the carve-out is not a blanket exemption)."""
        report = _base_report()
        report["verification_matrix"].append(
            _stage3_verified_matrix_entry("C013")
        )
        # Only one caveat for two web-sourced claims — fails.
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C012: web_source_no_doi_for_scite_tally"
        )
        status, errors = run_p8(report, _intake())
        assert status == "fail"
        assert any("C013" in e for e in errors)
        # Adding the missing caveat resolves it.
        report["header"]["coverage_caveats"].append(
            "cherry_picking:C013: web_source_no_doi_for_scite_tally"
        )
        status, errors = run_p8(report, _intake())
        assert status == "pass", errors


class TestAuditReportValidatorSchemaAndPredicate:
    """End-to-end: AuditReportValidator runs schema + P8 in one call."""

    def test_valid_report_passes_both_stages(self) -> None:
        report = _base_report()
        report["findings"].append(_cherry_picking_finding("C012"))
        ok, errors, _ = AuditReportValidator().validate(report, _intake())
        assert ok, errors

    def test_schema_failure_does_not_short_circuit_p8(self) -> None:
        """Two-stage: schema error AND P8 violation must both surface."""
        report = _base_report()
        # Schema violation: missing executive_summary minLength
        report["executive_summary"] = "too short"
        # P8 violation: no cherry-picking coverage
        ok, errors, _ = AuditReportValidator().validate(report, _intake())
        assert not ok
        assert any("schema" in e for e in errors)
        assert any("P8" in e for e in errors)

    def test_p8_failure_emits_p8_tag(self) -> None:
        report = _base_report()
        ok, errors, _ = AuditReportValidator().validate(report, _intake())
        assert not ok
        assert any(e.startswith("P8:") for e in errors)


class TestNoStage3VerifiedClaims:
    """P8 is trivially satisfied when there are no Stage-3 VERIFIED claims."""

    def test_empty_matrix_passes(self) -> None:
        report = _base_report()
        report["verification_matrix"] = []
        status, errors = run_p8(report, _intake())
        assert status == "pass"

    def test_only_unverified_stage3_passes(self) -> None:
        report = _base_report()
        report["verification_matrix"] = [
            {
                "claim_id": "C001",
                "verdict": "UNVERIFIED",
                "severity": "INFORMATIONAL",
                "stage": "3",
            }
        ]
        status, errors = run_p8(report, _intake())
        assert status == "pass"


