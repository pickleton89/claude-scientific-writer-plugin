"""Offline tests for the deep-research eval runner (evals/run_eval.py).

Exercises the two model-free paths — ``--dry-run`` (prompt assembly) and
``--mock-judge`` (results writing) — against the checked-in quick-mode KRAS
fixture. No model call, no network.
"""

import json
import subprocess
import sys
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1] / "evals"
RUNNER = EVALS / "run_eval.py"
FIX = EVALS / "fixtures" / "quick_kras_g12c"
REPORT = FIX / "2026-06-21_kras-g12c-nsclc_quick_brief.md"
SOURCES = FIX / "2026-06-21_kras-g12c-nsclc_quick_sources.json"
GRADING = FIX / "2026-06-21_kras-g12c-nsclc_quick_grading.json"
MOCK = FIX / "mock_judge_verdict.json"

RQ = "What is the clinical efficacy of KRAS G12C inhibitors in NSCLC?"


def test_dry_run_assembles_prompt():
    proc = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--dry-run",
            "--report",
            str(REPORT),
            "--sources",
            str(SOURCES),
            "--grading",
            str(GRADING),
            "--mode",
            "quick",
            "--query",
            RQ,
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    # every placeholder substituted (none left in the assembled prompt)
    for token in ("{{report}}", "{{sources_json}}", "{{research_question}}"):
        assert token not in out
    # sidecar + report content actually inlined
    assert "Sotorasib" in out  # from the sources sidecar
    assert RQ in out
    # absent sidecars fall back to the MISSING sentinel
    assert "(not provided in this mode)" in out


def test_mock_judge_writes_results(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--mock-judge",
            str(MOCK),
            "--report",
            str(REPORT),
            "--sources",
            str(SOURCES),
            "--grading",
            str(GRADING),
            "--mode",
            "quick",
            "--query-id",
            "fixture-smoke",
            "--model",
            "test",
            "--timestamp",
            "2026-06-21T00:00:00Z",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    result_file = tmp_path / "fixture-smoke.json"
    assert result_file.exists()
    rec = json.loads(result_file.read_text())
    assert rec["query_id"] == "fixture-smoke"
    assert rec["mode"] == "quick"
    assert rec["timestamp"] == "2026-06-21T00:00:00Z"
    assert rec["pass"] is True
    assert set(rec["scores"]) == {
        "factual_accuracy",
        "citation_accuracy",
        "completeness",
        "source_quality",
        "tool_efficiency",
    }
    assert 0.0 <= rec["overall"] <= 1.0


def test_report_required():
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0  # argparse error: --report is required
