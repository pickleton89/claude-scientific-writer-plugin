"""Tests for validate_intake.py and validate_finding.py.

Covers schema validation + business rules + predicates P1-P5 from references/CONTRACTS.md.
Two-stage pattern: schema failures must NOT short-circuit predicate checks.
"""

from __future__ import annotations

from typing import Any

import pytest

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
        assert any("document_type_other" in e for e in errors), (
            "business rule error missing"
        )

    def test_pinned_sidecars_accepted(self, sample_intake: dict[str, Any]) -> None:
        """Deep-research handoff: pinned_sidecars is optional and schema-valid."""
        intake = {
            **sample_intake,
            "pinned_sidecars": {
                "sources_path": "/tmp/2026-05-17_kras-inhibitors_full_sources.json",
                "grading_path": "/tmp/2026-05-17_kras-inhibitors_full_grading.json",
                "synthesis_path": None,
                "advocate_path": None,
            },
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors

    def test_pinned_sidecars_requires_sources_path(
        self, sample_intake: dict[str, Any]
    ) -> None:
        """sources_path is the one required key under pinned_sidecars."""
        intake = {
            **sample_intake,
            "pinned_sidecars": {
                "grading_path": "/tmp/grading.json",
                # sources_path missing
            },
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("sources_path" in e for e in errors), errors

    def test_expand_tier_populates_checks(self, sample_intake: dict[str, Any]) -> None:
        out = IntakeValidator().expand_tier(sample_intake)
        assert out["checks_enabled"] == TIER_CHECKS["2"]

    # ---- prose_quality_audit is custom-only (never auto-included by a tier) ----

    def test_tier3_excludes_prose_quality_audit(self) -> None:
        """Tier 3 is the 7 citation/claim checks only — prose must not ride along."""
        assert "prose_quality_audit" not in TIER_CHECKS["3"]
        assert len(TIER_CHECKS["3"]) == 7

    def test_tier3_expansion_has_no_prose(self) -> None:
        intake = {
            "document_type": "manuscript",
            "sources_available": "none",
            "verification_tier": "3",
            "domain": "biomedical",
            "flag_threshold": "standard",
        }
        out = IntakeValidator().expand_tier(intake)
        assert "prose_quality_audit" not in out["checks_enabled"]

    @pytest.mark.parametrize("tier", ["1", "2", "3"])
    def test_prose_forbidden_at_numbered_tier(self, tier: str) -> None:
        """Explicitly requesting prose at any numbered tier (1/2/3) is an error."""
        intake = {
            "document_type": "manuscript",
            "sources_available": "none",
            "verification_tier": tier,
            "checks_enabled": ["citation_existence", "prose_quality_audit"],
            "domain": "biomedical",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("prose_quality_audit" in e and "custom" in e for e in errors), errors

    def test_prose_allowed_at_custom_tier(self) -> None:
        intake = {
            "document_type": "manuscript",
            "sources_available": "none",
            "verification_tier": "custom",
            "checks_enabled": ["prose_quality_audit"],
            "domain": "general",
            "flag_threshold": "standard",
        }
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors

    def test_prose_as_sole_deviation_skips_canonical_warning(self) -> None:
        """Tier 3 + the 7 canonical checks + prose: emit the hard prose error only,
        not the redundant 'differs from canonical' warning."""
        intake = {
            "document_type": "manuscript",
            "sources_available": "none",
            "verification_tier": "3",
            "checks_enabled": [*TIER_CHECKS["3"], "prose_quality_audit"],
            "domain": "biomedical",
            "flag_threshold": "standard",
        }
        ok, errors, warnings = IntakeValidator().validate(intake)
        assert not ok
        assert any("prose_quality_audit" in e for e in errors), errors
        assert not any("differs from canonical" in w for w in warnings), warnings

    # ---- cited_papers[] (Stage 6 cooperation handoff) ------------------------

    def test_cited_papers_omitted_passes(self, sample_intake: dict[str, Any]) -> None:
        """cited_papers is optional — absence is the default fallback path."""
        intake = dict(sample_intake)
        intake.pop("cited_papers", None)
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors

    def test_cited_papers_valid_entry_passes(
        self, sample_intake: dict[str, Any]
    ) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = [
            {
                "paper_id": "smith2024_cancer",
                "stats_path": "/papers/smith2024_cancer/smith2024_cancer_stats.json",
                "source_meta_path": "/papers/smith2024_cancer/smith2024_cancer_source_meta.json",
                "doi": "10.1000/example.001",
                "pmid": "39000001",
            }
        ]
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors

    def test_cited_papers_missing_stats_path_fails(
        self, sample_intake: dict[str, Any]
    ) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = [
            {
                "paper_id": "smith2024",
                # stats_path missing
                "source_meta_path": "/papers/smith2024_source_meta.json",
            }
        ]
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("stats_path" in e for e in errors)

    def test_cited_papers_empty_paper_id_fails(
        self, sample_intake: dict[str, Any]
    ) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = [
            {
                "paper_id": "",
                "stats_path": "/p/x_stats.json",
                "source_meta_path": "/p/x_source_meta.json",
            }
        ]
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("schema" in e for e in errors)

    def test_cited_papers_additional_props_rejected(
        self, sample_intake: dict[str, Any]
    ) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = [
            {
                "paper_id": "smith2024",
                "stats_path": "/p/smith2024_stats.json",
                "source_meta_path": "/p/smith2024_source_meta.json",
                "abstract": "should not be here",  # additionalProperties: false
            }
        ]
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("schema" in e for e in errors)

    def test_cited_papers_empty_array_passes(
        self, sample_intake: dict[str, Any]
    ) -> None:
        """Empty cited_papers[] is the same as omitting it — fallback path."""
        intake = dict(sample_intake)
        intake["cited_papers"] = []
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors

    def test_cited_papers_non_array_fails(self, sample_intake: dict[str, Any]) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = "not_an_array"
        ok, errors, _ = IntakeValidator().validate(intake)
        assert not ok
        assert any("schema" in e for e in errors)

    def test_cited_papers_multiple_entries_pass(
        self, sample_intake: dict[str, Any]
    ) -> None:
        intake = dict(sample_intake)
        intake["cited_papers"] = [
            {
                "paper_id": "smith2024",
                "stats_path": "/p/smith2024_stats.json",
                "source_meta_path": "/p/smith2024_source_meta.json",
            },
            {
                "paper_id": "jones2023",
                "stats_path": "/p/jones2023_stats.json",
                "source_meta_path": "/p/jones2023_source_meta.json",
                "pmcid": "PMC10000001",
            },
        ]
        ok, errors, _ = IntakeValidator().validate(intake)
        assert ok, errors


# ---------- FindingValidator (P1-P5) ----------------------------------------


class TestFindingValidator:
    def test_valid_critical_finding_passes(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
        ok, errors, _ = FindingValidator().validate(
            sample_finding_critical, "manuscript"
        )
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
                {
                    "method": "web_search",
                    "tool": "WebSearch",
                    "result_summary": "no hits",
                }
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

    def test_p3_evidence_required(
        self, sample_finding_critical: dict[str, Any]
    ) -> None:
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
        ok, errors, _ = FindingValidator().validate(
            sample_finding_quote_verified, "manuscript"
        )
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
        assert any("P3" in e for e in errors), (
            "P3 predicate not run after schema failure"
        )

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
        doc_types = [
            "grant",
            "manuscript",
            "lit_review",
            "slides",
            "report",
            "memo",
            "other",
        ]
        cells = 0
        for dt in doc_types:
            for vd in verdicts:
                sev = v.expected_severity(dt, vd)
                assert sev in {"CRITICAL", "MAJOR", "MINOR", "INFORMATIONAL"}, (
                    dt,
                    vd,
                    sev,
                )
                cells += 1
        assert cells == 70


# ---------- P7: Stage-2 Scite retraction probe ----------------------------


def _stage2_verified_finding(
    *,
    with_scite: bool,
    scite_via_tool: bool = False,
    with_metadata_agreement: bool = True,
) -> dict[str, Any]:
    """Build a minimal valid Stage-2 VERIFIED finding for P7 / P9 tests.

    `with_scite=True` includes a Scite verification_path entry; `scite_via_tool`
    chooses between method=='scite_context' (False) and tool ~ /scite/i (True).
    `with_metadata_agreement=True` (default) includes the author/title
    cross-check entry P9 requires for scholarly Stage-2 VERIFIED findings;
    set it False to exercise the P9 violation path.
    """
    paths: list[dict[str, Any]] = [
        {"method": "doi_lookup", "tool": "Crossref", "result_summary": "DOI resolved"},
    ]
    if with_metadata_agreement:
        paths.append(
            {
                "method": "metadata_agreement",
                "tool": "Crossref",
                "result_summary": "author_match=true; title_match=true; year_match=true",
            }
        )
    if with_scite:
        if scite_via_tool:
            paths.append(
                {
                    "method": "doi_lookup",  # not scite_context — covered by tool match
                    "tool": "Scite MCP (search_literature) — failed",
                    "result_summary": "probe failed: api_timeout",
                }
            )
        else:
            paths.append(
                {
                    "method": "scite_context",
                    "tool": "Scite MCP (search_literature)",
                    "result_summary": "editorialNotices: none (Scite returned no record for DOI)",
                }
            )
    return {
        "id": "F100",
        "location": {"section": "Intro", "paragraph": 1, "line": 3},
        "claim_verbatim": "Foo et al. demonstrated bar.",
        "claim_type": "citation_bearing",
        "citations": [{"key": "Foo2020", "raw_text": "Foo et al. 2020 Nature"}],
        "verification_path": paths,
        "evidence": [
            {
                "source": "Crossref",
                "url": "https://doi.org/10.1038/s41586-020-1234-5",
                "snippet": "metadata agrees",
            }
        ],
        "verdict": "VERIFIED",
        "severity": "INFORMATIONAL",
        "recommended_action": "No action needed.",
        "confidence": "high",
    }


class TestP7ScitePropeRequired:
    """P7: biomedical/mixed Stage-2 findings need a Scite probe entry."""

    def test_p7_biomedical_stage2_verified_without_scite_fails(self) -> None:
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P7" in e for e in errors)

    def test_p7_biomedical_stage2_verified_with_scite_method_passes(self) -> None:
        finding = _stage2_verified_finding(with_scite=True, scite_via_tool=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_biomedical_stage2_verified_with_scite_tool_only_passes(self) -> None:
        """Scite logged via tool field (e.g. failure case) still satisfies P7."""
        finding = _stage2_verified_finding(with_scite=True, scite_via_tool=True)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_mixed_domain_also_active(self) -> None:
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="mixed", stage=2
        )
        assert not ok
        assert any("P7" in e for e in errors)

    def test_p7_general_domain_skipped(self) -> None:
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="general", stage=2
        )
        assert ok, errors

    def test_p7_stage3_skipped(self) -> None:
        """P7 only fires for Stage 2."""
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=3
        )
        assert ok, errors

    def test_p7_unverified_verdict_skipped(self) -> None:
        """UNVERIFIED citations weren't resolved — no DOI to feed Scite."""
        finding = _stage2_verified_finding(with_scite=False)
        finding["verdict"] = "UNVERIFIED"
        finding["severity"] = "INFORMATIONAL"
        finding["reason"] = "api_timeout"
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_no_domain_kwarg_skipped_back_compat(self) -> None:
        """Legacy callers (no domain/stage) MUST still pass — P7 opt-in."""
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(finding, "manuscript")
        assert ok, errors

    def test_p7_no_stage_kwarg_skipped_back_compat(self) -> None:
        """domain alone without stage is insufficient to activate P7."""
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical"
        )
        assert ok, errors

    def test_p7_metadata_mismatch_also_requires_scite(self) -> None:
        """METADATA_MISMATCH (e.g., retraction signaled by editorialNotices)
        still requires the probe to be logged."""
        finding = _stage2_verified_finding(with_scite=False)
        finding["verdict"] = "METADATA_MISMATCH"
        finding["severity"] = "MAJOR"  # matrix[manuscript][METADATA_MISMATCH]
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P7" in e for e in errors)

    def test_p7_unsupported_also_requires_scite(self) -> None:
        """UNSUPPORTED is the third P7-gated verdict.

        matrix[manuscript][UNSUPPORTED] == CRITICAL, so P2 (≥2 verification
        paths) also fires. Append a non-Scite path so P2 is satisfied,
        leaving P7 as the only failure surface.
        """
        finding = _stage2_verified_finding(with_scite=False)
        finding["verdict"] = "UNSUPPORTED"
        finding["severity"] = "CRITICAL"
        finding["verification_path"].append(
            {"method": "pubmed_search", "tool": "PubMed", "result_summary": "no hit"}
        )
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P7" in e for e in errors)
        # Confirm P2 is NOT the blocker (we satisfied it with 2 paths).
        assert not any("P2" in e for e in errors)


# ---------- P7 web-source carve-out ---------------------------------------


def _stage2_web_finding(
    *, with_no_doi_token: bool, scite_also_present: bool = False
) -> dict[str, Any]:
    """Build a minimal valid Stage-2 VERIFIED finding sourced from the web.

    The finding has NO scholarly verification_path entries (no DOI lookup, no
    Scite probe) — only a `method == "web_search"` entry pointing at a W1 URL
    (FDA approval letter). `with_no_doi_token` controls whether the `no_doi`
    literal appears in result_summary (the carve-out's satisfaction token).
    `scite_also_present` toggles whether a Scite entry appears alongside; when
    True, P7 should be satisfied by Scite regardless of the web entry's shape.
    """
    paths: list[dict[str, Any]] = [
        {
            "method": "web_search",
            "tool": "mcp__exa__web_search_exa",
            "result_summary": (
                "web evidence: no_doi available for Scite retraction probe; "
                "URL=https://www.fda.gov/drugs/news-events-human-drugs/"
                "fda-approves-aducanumab-2021; fetched_at=2026-05-14T16:22:18Z"
                if with_no_doi_token
                else "web evidence located at FDA.gov approval page; "
                "URL=https://www.fda.gov/drugs/news-events-human-drugs/"
                "fda-approves-aducanumab-2021; fetched_at=2026-05-14T16:22:18Z"
            ),
        },
    ]
    if scite_also_present:
        paths.append(
            {
                "method": "scite_context",
                "tool": "Scite MCP (search_literature)",
                "result_summary": (
                    "editorialNotices: none (Scite returned no record for DOI)"
                ),
            }
        )
    return {
        "id": "F200",
        "location": {"section": "Intro", "paragraph": 2, "line": 7},
        "claim_verbatim": "The FDA approved aducanumab in 2021.",
        "claim_type": "citation_bearing",
        "citations": [{"key": "FDA2021", "raw_text": "FDA approval letter"}],
        "verification_path": paths,
        "evidence": [
            {
                "source": "FDA",
                "url": "https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-aducanumab-2021",
                "snippet": "Accelerated approval granted June 7, 2021.",
            }
        ],
        "verdict": "VERIFIED",
        "severity": "INFORMATIONAL",
        "recommended_action": "No action needed.",
        "confidence": "high",
    }


class TestP7WebSourceCarveOut:
    """P7 carve-out: web evidence with no DOI satisfies P7 via the no_doi token.

    See skills/shared/references/citable_web_domains.md for the canonical
    result_summary shape and the citable-web-domain whitelist.
    """

    def test_p7_web_search_with_no_doi_token_passes(self) -> None:
        """Web-sourced finding with explicit no_doi token → P7 satisfied."""
        finding = _stage2_web_finding(with_no_doi_token=True)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_web_search_missing_no_doi_token_fails_with_carve_out_error(
        self,
    ) -> None:
        """Web-sourced finding WITHOUT no_doi token → dedicated carve-out error
        (not the generic P7 error), so the LLM knows the issue is the missing
        token, not the missing Scite call."""
        finding = _stage2_web_finding(with_no_doi_token=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        # Carve-out error is distinct from generic P7 error.
        assert any("P7 carve-out" in e for e in errors)
        assert any("no_doi" in e for e in errors)

    def test_p7_web_search_with_scite_present_passes_via_scite(self) -> None:
        """When Scite is also probed, the web entry's no_doi token is moot —
        Scite alone satisfies P7. This covers hybrid findings where the web
        entry is supplementary, not the primary evidence."""
        finding = _stage2_web_finding(with_no_doi_token=False, scite_also_present=True)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_web_search_no_doi_case_insensitive(self) -> None:
        """The no_doi token check is case-insensitive (result_summary is
        lower-cased before substring search)."""
        finding = _stage2_web_finding(with_no_doi_token=True)
        # Force mixed case in result_summary to exercise the .lower() path.
        finding["verification_path"][0]["result_summary"] = (
            "Web evidence: NO_DOI available for Scite retraction probe; "
            "URL=https://www.fda.gov/...; fetched_at=2026-05-14T16:22:18Z"
        )
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_web_search_mixed_domain_carve_out_active(self) -> None:
        """Web-source carve-out applies in mixed domain too (P7_DOMAINS scope)."""
        finding = _stage2_web_finding(with_no_doi_token=True)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="mixed", stage=2
        )
        assert ok, errors

    def test_p7_web_search_general_domain_skipped(self) -> None:
        """Carve-out is moot in general domain — P7 itself doesn't fire there."""
        finding = _stage2_web_finding(with_no_doi_token=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="general", stage=2
        )
        assert ok, errors

    def test_p7_web_search_metadata_mismatch_carve_out_applies(self) -> None:
        """The carve-out applies to all P7-gated verdicts, not just VERIFIED."""
        finding = _stage2_web_finding(with_no_doi_token=True)
        finding["verdict"] = "METADATA_MISMATCH"
        finding["severity"] = "MAJOR"  # matrix[manuscript][METADATA_MISMATCH]
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p7_generic_error_mentions_web_carve_out_path(self) -> None:
        """When P7 fails WITHOUT a web_search entry at all, the generic error
        message should still mention the web-source carve-out path so the LLM
        is told both satisfaction routes."""
        finding = _stage2_verified_finding(with_scite=False)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        # Generic P7 error (not the carve-out error — no web_search present)
        # AND the error text mentions the carve-out path as an alternative.
        p7_errors = [e for e in errors if "P7" in e]
        assert any("carve-out" not in e for e in p7_errors)  # generic P7 present
        assert any("no_doi" in e for e in p7_errors)  # mentions carve-out


# ---------- P9: Stage-2 metadata-agreement gate ---------------------------


class TestP9MetadataAgreement:
    """P9: a Stage-2 VERIFIED finding that resolved a scholarly identifier
    MUST log an author/title cross-check (metadata_agreement). This closes
    the wrong-but-valid-DOI hole — a DOI that resolves to a real BUT
    DIFFERENT paper passes 'does it resolve?' yet fails the author check.
    """

    def test_p9_verified_without_metadata_agreement_fails(self) -> None:
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=False
        )
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P9" in e for e in errors)

    def test_p9_verified_with_metadata_agreement_passes(self) -> None:
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=True
        )
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors

    def test_p9_recorded_author_mismatch_blocks_verified(self) -> None:
        """The F-04 case: DOI resolves to a real but different paper. The
        recorded author_match=false must block a VERIFIED verdict."""
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=True
        )
        for entry in finding["verification_path"]:
            if entry["method"] == "metadata_agreement":
                entry["result_summary"] = "author_match=false; title_match=true"
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P9" in e and "METADATA_MISMATCH" in e for e in errors)

    def test_p9_recorded_title_mismatch_blocks_verified(self) -> None:
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=True
        )
        for entry in finding["verification_path"]:
            if entry["method"] == "metadata_agreement":
                entry["result_summary"] = "author_match=true; title_match=false"
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P9" in e for e in errors)

    def test_p9_token_whitespace_insensitive(self) -> None:
        """'author_match = false' (spaces around =) is still caught."""
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=True
        )
        for entry in finding["verification_path"]:
            if entry["method"] == "metadata_agreement":
                entry["result_summary"] = "author_match = false ; title_match = true"
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert not ok
        assert any("P9" in e for e in errors)

    def test_p9_fires_in_general_domain(self) -> None:
        """Unlike P7, P9 is domain-independent — wrong-but-valid DOIs occur
        in general-domain documents too (Crossref/OpenAlex resolution)."""
        finding = _stage2_verified_finding(
            with_scite=False, with_metadata_agreement=False
        )
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="general", stage=2
        )
        assert not ok
        assert any("P9" in e for e in errors)
        # P7 does NOT fire in general domain — P9 is the only blocker.
        assert not any("P7" in e for e in errors)

    def test_p9_web_only_finding_exempt(self) -> None:
        """Purely web-sourced findings have no resolved scholarly record to
        cross-check, so P9 does not apply (P7 carve-out governs them)."""
        finding = _stage2_web_finding(with_no_doi_token=True)
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        assert ok, errors
        assert not any("P9" in e for e in errors)

    def test_p9_skipped_without_stage(self) -> None:
        """Back-compat: ad-hoc callers omitting stage opt out of P9."""
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=False
        )
        ok, errors, _ = FindingValidator().validate(finding, "manuscript")
        assert ok, errors

    def test_p9_skipped_for_non_verified_verdict(self) -> None:
        """P9 only gates VERIFIED — METADATA_MISMATCH already implies the
        comparison was performed and found a disagreement."""
        finding = _stage2_verified_finding(
            with_scite=True, with_metadata_agreement=False
        )
        finding["verdict"] = "METADATA_MISMATCH"
        finding["severity"] = "MAJOR"  # matrix[manuscript][METADATA_MISMATCH]
        ok, errors, _ = FindingValidator().validate(
            finding, "manuscript", domain="biomedical", stage=2
        )
        # P7 still requires a Scite probe (present via with_scite=True); P9
        # must NOT fire on METADATA_MISMATCH.
        assert ok, errors
        assert not any("P9" in e for e in errors)
