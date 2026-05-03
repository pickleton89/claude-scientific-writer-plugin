"""Tests for render_report.py — JSON in → markdown out."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from render_report import SCITE_BIAS_CAVEAT, generate_report

SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


class TestRenderReport:
    def test_sample_report_validates_against_schema(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        # audit_report.json now inlines Finding in #/definitions; no resolver workaround needed.
        report_schema = json.loads((SCHEMAS_DIR / "audit_report.json").read_text())
        validate(instance=sample_audit_report, schema=report_schema)

    def test_render_produces_required_sections(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        md = generate_report(sample_audit_report)
        assert "# Accuracy Audit" in md
        assert "## Executive Summary" in md
        assert "## Findings" in md
        assert "## Verification Matrix" in md
        assert "## Methodology" in md

    def test_render_groups_findings_by_severity(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        md = generate_report(sample_audit_report)
        # Sample report has CRITICAL + INFORMATIONAL
        assert "### CRITICAL" in md
        assert "### INFORMATIONAL" in md
        # CRITICAL must precede INFORMATIONAL
        assert md.index("### CRITICAL") < md.index("### INFORMATIONAL")

    def test_render_includes_finding_evidence(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        md = generate_report(sample_audit_report)
        # F001 evidence URL must appear
        assert "https://api.crossref.org/journals/2662-1347" in md
        # F002 reason (UNVERIFIED) must appear
        assert "paywalled_full_text" in md

    def test_render_quotes_claim_verbatim(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        md = generate_report(sample_audit_report)
        assert "CT26 anti-PD-1 monotherapy gave 47% complete response." in md

    def test_render_handles_no_findings(self) -> None:
        report = {
            "header": {
                "document_title": "Empty",
                "document_type": "memo",
                "date_checked": "2026-04-25",
                "verification_tier": "1",
                "sources_consulted": [],
                "overall_confidence": "high",
                "confidence_justification": "No claims required verification.",
                "coverage_caveats": [],
            },
            "executive_summary": "No claims; nothing to audit." * 3,
            "findings": [],
            "verification_matrix": [],
            "methodology_note": "n/a",
        }
        md = generate_report(report)
        assert "No findings emitted" in md

    def test_render_escapes_pipes_in_cells(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        # Inject a pipe into the recommended_action of one finding
        rep = json.loads(json.dumps(sample_audit_report))  # deep copy
        rep["findings"][0]["recommended_action"] = "Do A | then B"
        md = generate_report(rep)
        assert "Do A \\| then B" in md

    def test_render_no_scite_caveat_without_scite_context(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        # Sample report has no scite_context in any verification_path → caveat absent
        md = generate_report(sample_audit_report)
        assert SCITE_BIAS_CAVEAT not in md

    def test_render_injects_scite_caveat_when_scite_context_present(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        rep = json.loads(json.dumps(sample_audit_report))  # deep copy
        rep["findings"][0]["verification_path"].append(
            {
                "method": "scite_context",
                "tool": "Scite MCP (search_literature)",
                "result_summary": (
                    "Tally: 4 supporting / 12 contrasting / 8 mentioning; "
                    "USI=0.25, contested per Scite classification."
                ),
            }
        )
        md = generate_report(rep)
        assert SCITE_BIAS_CAVEAT in md
        # original caveat preserved
        assert "1 paywalled full text" in md

    def test_render_scite_caveat_idempotent(
        self, sample_audit_report: dict[str, Any]
    ) -> None:
        # If the caveat is already in coverage_caveats, don't duplicate it
        rep = json.loads(json.dumps(sample_audit_report))
        rep["header"]["coverage_caveats"].append(SCITE_BIAS_CAVEAT)
        rep["findings"][0]["verification_path"].append(
            {"method": "scite_context", "tool": "Scite", "result_summary": "..."}
        )
        md = generate_report(rep)
        assert md.count(SCITE_BIAS_CAVEAT) == 1
