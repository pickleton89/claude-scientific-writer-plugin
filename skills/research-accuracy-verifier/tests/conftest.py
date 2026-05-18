"""Pytest configuration and shared fixtures for research-accuracy-verifier tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Make scripts/ importable
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture(autouse=True)
def _pin_artifact_enforcement_advisory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin `ARTIFACT_ENFORCEMENT` to "advisory" for the duration of each test.

    Phase 3 flipped the on-disk default to "required"; the pre-Phase-3 test
    suite was written against advisory semantics (R-predicate failures emit
    warnings, missing artifacts emit warnings). Rather than rewrite every
    fixture to supply the full artifact set, this autouse fixture restores the
    legacy default per test.

    Only `thresholds.ARTIFACT_ENFORCEMENT` is patched — `thresholds.resolve_enforcement`
    reads the constant from its own module at call time, so all downstream
    callers (`validate_audit_report.run_predicates`, `checkpoint.finalize_audit`,
    `render_report.generate_report`) see the patched value automatically.

    Tests that exercise required-mode behavior should pass
    `enforcement="required"` explicitly to the validator (preferred), or
    re-monkeypatch `thresholds.ARTIFACT_ENFORCEMENT` within the test body.
    """
    import thresholds  # noqa: PLC0415

    monkeypatch.setattr(thresholds, "ARTIFACT_ENFORCEMENT", "advisory")


@pytest.fixture
def severity_matrix() -> dict[str, dict[str, str]]:
    return json.loads((SCHEMAS_DIR / "severity_matrix.values.json").read_text())["matrix"]


@pytest.fixture
def sample_intake() -> dict[str, Any]:
    return {
        "document_type": "manuscript",
        "sources_available": "uploaded_files",
        "verification_tier": "2",
        "domain": "biomedical",
        "flag_threshold": "standard",
    }


@pytest.fixture
def sample_intake_custom() -> dict[str, Any]:
    return {
        "document_type": "grant",
        "sources_available": "bibliography_only",
        "verification_tier": "custom",
        "checks_enabled": ["citation_existence", "exact_quotes"],
        "domain": "biomedical",
        "flag_threshold": "strict",
    }


@pytest.fixture
def sample_finding_critical() -> dict[str, Any]:
    """A valid CRITICAL finding for a manuscript: UNSUPPORTED with 2 verification paths."""
    return {
        "id": "F001",
        "location": {"section": "Results", "paragraph": 2, "line": 14},
        "claim_verbatim": "CT26 anti-PD-1 monotherapy gave 47% complete response.",
        "claim_type": "citation_bearing",
        "citations": [
            {"key": "Chen2019", "raw_text": "Chen et al., 2019, Nature Cancer 5:1123-1135"}
        ],
        "verification_path": [
            {"method": "doi_lookup", "tool": "Crossref", "result_summary": "no DOI provided"},
            {
                "method": "journal_volume_check",
                "tool": "check_journal_volume.py",
                "result_summary": "Nature Cancer vol 5 in 2019 impossible (journal began 2020)",
            },
        ],
        "evidence": [
            {
                "source": "Crossref ISSN 2662-1347",
                "url": "https://api.crossref.org/journals/2662-1347",
                "snippet": "Nature Cancer first published Jan 2020",
            }
        ],
        "verdict": "UNSUPPORTED",
        "severity": "CRITICAL",
        "recommended_action": "Replace with verified source.",
        "confidence": "high",
    }


@pytest.fixture
def sample_finding_unverified() -> dict[str, Any]:
    """A valid UNVERIFIED finding (paywalled). Severity must be INFORMATIONAL."""
    return {
        "id": "F002",
        "location": {"section": "Discussion", "paragraph": 1, "line": None},
        "claim_verbatim": "Recent work supports the role of X in Y.",
        "claim_type": "citation_bearing",
        "citations": [{"key": "Smith2024", "raw_text": "Smith 2024 Cell"}],
        "verification_path": [
            {
                "method": "pmc_fetch",
                "tool": "PMC",
                "result_summary": "Open access not available; full text behind paywall",
            }
        ],
        "evidence": [
            {
                "source": "PubMed abstract",
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                "snippet": "Abstract only; alignment cannot be assessed.",
            }
        ],
        "verdict": "UNVERIFIED",
        "severity": "INFORMATIONAL",
        "recommended_action": "Acquire full text and re-check.",
        "confidence": "medium",
        "reason": "paywalled_full_text",
    }


@pytest.fixture
def sample_finding_quote_verified() -> dict[str, Any]:
    """A QUOTE_VERIFIED finding."""
    return {
        "id": "F003",
        "location": {"section": "Introduction", "paragraph": 1, "line": 5},
        "claim_verbatim": "the result was significant",
        "claim_type": "direct_quote",
        "verification_path": [
            {
                "method": "exact_quote_match",
                "tool": "verify_exact_quote.py",
                "result_summary": "exact match at offset 14",
            }
        ],
        "evidence": [
            {
                "source": "user-provided source",
                "url": "file://refs/source.txt",
                "snippet": "the result was significant",
            }
        ],
        "verdict": "QUOTE_VERIFIED",
        "severity": "INFORMATIONAL",
        "recommended_action": "No action needed.",
        "confidence": "high",
    }


@pytest.fixture
def sample_audit_report(
    sample_finding_critical: dict[str, Any], sample_finding_unverified: dict[str, Any]
) -> dict[str, Any]:
    return {
        "header": {
            "document_title": "Test Manuscript",
            "document_type": "manuscript",
            "date_checked": "2026-04-25",
            "verification_tier": "2",
            "sources_consulted": ["PubMed", "Crossref"],
            "overall_confidence": "moderate",
            "confidence_justification": (
                "One CRITICAL hallucinated citation found and one UNVERIFIED claim "
                "due to paywalled full text."
            ),
            "coverage_caveats": ["1 paywalled full text (Smith 2024) — alignment not assessed."],
        },
        "executive_summary": (
            "Audited 2 claims against PubMed and Crossref. One CRITICAL finding "
            "(hallucinated citation, journal-volume impossibility) and one UNVERIFIED "
            "finding (paywalled full text). Recommend replacing the Chen 2019 citation "
            "before submission and acquiring full text for Smith 2024."
        ),
        "findings": [sample_finding_critical, sample_finding_unverified],
        "verification_matrix": [
            {"claim_id": "F001", "verdict": "UNSUPPORTED", "severity": "CRITICAL", "stage": "2"},
            {"claim_id": "F002", "verdict": "UNVERIFIED", "severity": "INFORMATIONAL", "stage": "3"},
        ],
        "methodology_note": "Tier-2 audit: citation existence + claim alignment.",
    }


@pytest.fixture
def sample_document_with_acronyms() -> str:
    return (
        "Introduction. We use Chimeric Antigen Receptor (CAR) T cells. "
        "Methods. The CAR construct was paired with PD-1 inhibitors. "
        "Later we describe CAR (Coxsackievirus and Adenovirus Receptor) binding too. "
        "Note that DNA was extracted but never defined here."
    )


@pytest.fixture
def sample_bibliography_bibtex() -> str:
    return """@article{smith_2019,
  author = {Smith, J. and Jones, A.},
  title = {A study of X},
  journal = {Nature},
  year = {2019},
  doi = {10.1038/s41586-019-1234-5}
}
@article{anderson_2020,
  author = {Anderson, B.},
  title = {A different study},
  journal = {Cell},
  year = {2020}
}
"""


@pytest.fixture
def sample_document_with_inline_cites() -> str:
    return (
        "We adopt the framework of Smith and Jones (2019) for analysis. "
        "Other groups have used different methods (Anderson, 2020). "
        "An older method by Brown (2015) is also worth noting."
    )
