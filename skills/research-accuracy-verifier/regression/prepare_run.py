#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare a single regression run: emit intake.json + create the run dir.

Usage:
    uv run --script regression/prepare_run.py \
        --doc-id 06_lit_review_cited_paper_numerical \
        --arm baseline \
        --run-idx 1

Reads `regression/manifest.json`, locates the named doc entry, and writes
`regression/runs/{arm}/{doc_id}/run{N}/intake.json` populated from the
manifest's per-doc config fields.

The baseline / post_fork split is intake-only — no skill code branches on
arm. For `--arm baseline`, intake omits `cited_papers[]` so Stage 6 falls
back to full-text re-extraction (the pre-cooperation-contract path). For
`--arm post_fork`, intake carries the manifest's `cited_papers[]` block so
Stage 6 joins the document's numerical claims against `stats.json` by
`paper_id` (the cooperation-contract path).

Run-directory layout:

    regression/runs/{arm}/{doc_id}/run{N}/
        intake.json                  (this script writes)
        audit_report.json            (copy from research/audits/<slug>/ post-run)
        document_inventory.json      (copy from research/audits/<slug>/ post-run)
        reference_map.json           (copy from research/audits/<slug>/ post-run)
        resolved_sources.json        (copy from research/audits/<slug>/ post-run)
        external_evidence.json       (copy from research/audits/<slug>/ post-run)
        return.json                  (orchestrator writes — the ~800-token
                                      fork return summary; filename matches
                                      what score.py reads at line ~263)
        tokens.json                  (orchestrator writes —
                                      `{"main_context_tokens": N}`, total
                                      tokens at fork-return time; shape
                                      matches what score.py reads at
                                      line ~258. Omit the file entirely
                                      when no real count is available —
                                      score.py falls back to approximating
                                      from return.json)

See `regression/RUN_PROTOCOL.md` for the full per-run contract that the
orchestrator (Claude Code agent, shell script, or human) executes after
this script prepares the run dir.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ARMS = ("baseline", "post_fork")
SKILL_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SKILL_ROOT / "regression" / "manifest.json"
RUNS_ROOT = SKILL_ROOT / "regression" / "runs"


def build_intake(doc: dict, arm: str) -> dict:
    """Construct an intake dict from a manifest doc entry."""
    intake = {
        "document_type": doc["document_type"],
        "sources_available": "uploaded_files",
        "verification_tier": doc["verification_tier"],
        "domain": doc["domain"],
        "flag_threshold": doc["flag_threshold"],
    }
    if doc.get("checks_enabled"):
        intake["checks_enabled"] = doc["checks_enabled"]
    if arm == "post_fork" and doc.get("cited_papers"):
        intake["cited_papers"] = doc["cited_papers"]
    return intake


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a regression run intake + run dir.")
    parser.add_argument("--doc-id", required=True, help="manifest.documents[].doc_id")
    parser.add_argument("--arm", required=True, choices=ARMS)
    parser.add_argument("--run-idx", type=int, required=True, help="1-based run index")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"error: manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        return 2
    manifest = json.loads(MANIFEST_PATH.read_text())
    docs = {d["doc_id"]: d for d in manifest.get("documents", [])}
    if args.doc_id not in docs:
        print(f"error: unknown doc_id '{args.doc_id}'", file=sys.stderr)
        print(f"available: {sorted(docs)}", file=sys.stderr)
        return 2
    doc = docs[args.doc_id]
    status = doc.get("content_status")
    if status != "authored":
        print(
            f"error: doc '{args.doc_id}' has content_status={status!r}, not 'authored' — "
            f"regression bed only runs against authored docs",
            file=sys.stderr,
        )
        return 2

    intake = build_intake(doc, args.arm)
    run_dir = RUNS_ROOT / args.arm / args.doc_id / f"run{args.run_idx}"
    run_dir.mkdir(parents=True, exist_ok=True)
    intake_path = run_dir / "intake.json"
    intake_path.write_text(json.dumps(intake, indent=2) + "\n")

    # Audit slug = doc_id by convention; the protocol clears
    # research/audits/<slug>/ between sequential runs of the same (arm, doc).
    # Parallel runs across distinct (arm, doc) pairs use distinct slugs
    # naturally and do not collide.
    audit_slug = args.doc_id

    rel = lambda p: p.relative_to(SKILL_ROOT).as_posix()  # noqa: E731
    print(f"intake_path={rel(intake_path)}")
    print(f"run_dir={rel(run_dir)}")
    print(f"audit_slug={audit_slug}")
    print(f"doc_path={doc['doc_path']}")
    print(f"ground_truth_path={doc['ground_truth_path']}")
    if args.arm == "post_fork" and "cited_papers" in intake:
        print(f"cited_papers_count={len(intake['cited_papers'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
