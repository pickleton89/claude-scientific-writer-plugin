"""Tests for scripts/thresholds.py."""

from __future__ import annotations

import pytest

import thresholds


class TestArtifactKinds:
    def test_kinds_listed(self) -> None:
        assert thresholds.ARTIFACT_KINDS == (
            "document_inventory",
            "reference_map",
            "resolved_sources",
            "external_evidence",
        )

    def test_enforcement_is_advisory_in_phase_1(self) -> None:
        assert thresholds.ARTIFACT_ENFORCEMENT == "advisory"


class TestArtifactFilename:
    @pytest.mark.parametrize(
        "kind,expected",
        [
            ("document_inventory", "document_inventory.json"),
            ("reference_map", "reference_map.json"),
            ("resolved_sources", "resolved_sources.json"),
            ("external_evidence", "external_evidence.json"),
        ],
    )
    def test_canonical_filenames(self, kind: str, expected: str) -> None:
        assert thresholds.artifact_filename(kind) == expected

    def test_rejects_unknown_kind(self) -> None:
        with pytest.raises(ValueError, match="Unknown artifact kind"):
            thresholds.artifact_filename("bogus")


class TestRequiredArtifacts:
    def test_tier_1(self) -> None:
        assert thresholds.required_artifacts("1") == (
            "document_inventory",
            "reference_map",
            "resolved_sources",
        )

    def test_tier_2_includes_ledger(self) -> None:
        assert "external_evidence" in thresholds.required_artifacts("2")

    def test_tier_3_includes_ledger(self) -> None:
        assert "external_evidence" in thresholds.required_artifacts("3")

    def test_custom_baseline_only_inventory(self) -> None:
        result = thresholds.required_artifacts("custom", [])
        assert result == ("document_inventory",)

    def test_custom_with_claim_alignment_adds_ledger(self) -> None:
        result = thresholds.required_artifacts("custom", ["claim_alignment"])
        assert "document_inventory" in result
        assert "reference_map" in result
        assert "resolved_sources" in result
        assert "external_evidence" in result

    def test_custom_with_only_quote_checks(self) -> None:
        # exact_quotes has no artifact dependencies → only the baseline.
        result = thresholds.required_artifacts("custom", ["exact_quotes"])
        assert result == ("document_inventory",)

    def test_rejects_unknown_tier(self) -> None:
        with pytest.raises(ValueError, match="Unknown tier"):
            thresholds.required_artifacts("4")

    def test_result_order_follows_artifact_kinds(self) -> None:
        # Custom with checks that pull in every kind should return them in
        # ARTIFACT_KINDS order, not insertion order.
        result = thresholds.required_artifacts(
            "custom",
            ["citation_existence", "claim_alignment", "uncited_claims"],
        )
        # Filter ARTIFACT_KINDS to those present in result; should match exactly.
        expected = tuple(k for k in thresholds.ARTIFACT_KINDS if k in result)
        assert result == expected
