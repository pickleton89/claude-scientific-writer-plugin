#!/usr/bin/env python3
"""Stage-boundary checkpointing for resumable Tier-3 audits.

Multi-hour audits with many MCP calls can exhaust the context window. To make
audits resumable across sessions, each stage writes its findings + matrix delta
to `research/audits/<slug>/0N_<stage>.json` on completion. Stage 0 (resume
detection) reads the directory and tells the LLM which stages to skip.

No new schemas: per-stage artifacts contain `findings[]` (validated against
schemas/finding.json via FindingValidator) and `matrix_delta[]` (entries with
the same shape as audit_report.json's verification_matrix items). Stage 1
writes `claim_inventory.json` matching `schemas/claim_inventory.json` —
the wrapper object `{"items": [ClaimInventoryItem, ...]}`, not a bare array.

Usage:
    uv run python checkpoint.py write --slug my-paper --stage 3 \
        --findings findings.json --matrix matrix.json --document-type manuscript
    uv run python checkpoint.py resume --slug my-paper
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_finding import FindingValidator

STAGE_NAMES: dict[int, str] = {
    1: "claim_inventory",
    2: "existence",
    3: "alignment",
    4: "uncited",
    5: "quotes",
    6: "sanity",
    7: "consistency",
}

DEFAULT_AUDITS_ROOT = Path("research/audits")


def slugify(title: str, max_len: int = 60) -> str:
    """Derive a filesystem-safe slug from a document title.

    Lowercase, alnum + single hyphens, trimmed. Empty input → "untitled".
    """
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")[:max_len].rstrip("-")
    return s or "untitled"


@dataclass
class ResumeState:
    """State loaded from an audit directory.

    `completed_stages` is always a contiguous prefix of [1..7]: the loader
    breaks at the first missing stage artifact. `next_stage == 1` and
    `completed_stages == []` together mean "no resumable state" (either the
    audit directory is missing or it exists without a Stage 1 inventory).
    """

    slug: str
    audit_dir: Path
    completed_stages: list[int] = field(default_factory=list)
    next_stage: int = 1
    claim_inventory: dict[str, Any] | None = None  # {"items": [...]} per schemas/claim_inventory.json
    findings: list[dict[str, Any]] = field(default_factory=list)
    verification_matrix: list[dict[str, Any]] = field(default_factory=list)


def _stage_path(audit_dir: Path, stage: int) -> Path:
    if stage == 1:
        return audit_dir / "claim_inventory.json"
    return audit_dir / f"{stage:02d}_{STAGE_NAMES[stage]}.json"


def write_stage_artifact(
    slug: str,
    stage: int,
    findings: list[dict[str, Any]],
    matrix_delta: list[dict[str, Any]],
    document_type: str,
    *,
    claim_inventory: dict[str, Any] | None = None,
    audits_root: Path = DEFAULT_AUDITS_ROOT,
) -> Path:
    """Validate findings, then write the stage artifact. Returns the written path.

    Stage 1: writes `claim_inventory.json` from `claim_inventory` — the wrapper
    object `{"items": [...]}` per `schemas/claim_inventory.json`. The caller is
    responsible for schema-validating the inventory before passing it in.
    Stages 2–7: validates each finding via FindingValidator before writing —
    invalid findings raise ValueError so the caller loops back rather than
    persisting unvalidated state.
    """
    if stage not in STAGE_NAMES:
        raise ValueError(f"stage must be 1..7, got {stage}")
    audit_dir = audits_root / slug
    audit_dir.mkdir(parents=True, exist_ok=True)

    if stage == 1:
        if claim_inventory is None:
            raise ValueError("stage 1 requires claim_inventory")
        if not isinstance(claim_inventory, dict) or "items" not in claim_inventory:
            raise ValueError("claim_inventory must be a dict with an 'items' key (per schemas/claim_inventory.json)")
        path = _stage_path(audit_dir, 1)
        path.write_text(json.dumps(claim_inventory, indent=2))
        return path

    validator = FindingValidator()
    errors: list[str] = []
    for i, f in enumerate(findings):
        ok, errs, _ = validator.validate(f, document_type)
        if not ok:
            errors.append(f"findings[{i}] (id={f.get('id')}): {'; '.join(errs)}")
    if errors:
        raise ValueError(f"Stage {stage} findings failed validation:\n  " + "\n  ".join(errors))

    artifact = {
        "stage": stage,
        "stage_name": STAGE_NAMES[stage],
        "document_type": document_type,
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "findings": findings,
        "matrix_delta": matrix_delta,
    }
    path = _stage_path(audit_dir, stage)
    path.write_text(json.dumps(artifact, indent=2))
    return path


def load_resume_state(slug: str, *, audits_root: Path = DEFAULT_AUDITS_ROOT) -> ResumeState:
    """Inspect `audits_root/slug/` and return resume state.

    Stages are considered complete in contiguous order from 1: the first
    missing stage artifact stops the resume scan. A gap (e.g., 1, 2, 4
    present but 3 missing) is treated as next_stage = 3 — the audit must
    re-run stage 3 before proceeding.
    """
    audit_dir = audits_root / slug
    state = ResumeState(slug=slug, audit_dir=audit_dir)
    if not audit_dir.exists():
        return state

    inventory_path = _stage_path(audit_dir, 1)
    if inventory_path.exists():
        state.claim_inventory = json.loads(inventory_path.read_text())
        state.completed_stages.append(1)
    else:
        return state

    for stage in range(2, 8):
        path = _stage_path(audit_dir, stage)
        if not path.exists():
            break
        artifact = json.loads(path.read_text())
        state.completed_stages.append(stage)
        state.findings.extend(artifact.get("findings") or [])
        state.verification_matrix.extend(artifact.get("matrix_delta") or [])

    # completed_stages is always a contiguous prefix (the loop above breaks
    # at the first missing stage), so the last element is the highest.
    state.next_stage = (state.completed_stages[-1] + 1) if state.completed_stages else 1
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage-boundary checkpointing")
    sub = parser.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("write", help="Write a stage artifact")
    w.add_argument("--slug", required=True)
    w.add_argument("--stage", type=int, required=True, choices=range(1, 8))
    w.add_argument("--document-type", required=True)
    w.add_argument("--findings", help="Path to findings JSON array (stages 2-7)")
    w.add_argument("--matrix", help="Path to matrix-delta JSON array (stages 2-7)")
    w.add_argument("--claim-inventory", help="Path to claim_inventory JSON object (stage 1; {\"items\": [...]})")
    w.add_argument("--audits-root", default=str(DEFAULT_AUDITS_ROOT))

    r = sub.add_parser("resume", help="Print resume state for a slug")
    r.add_argument("--slug", required=True)
    r.add_argument("--audits-root", default=str(DEFAULT_AUDITS_ROOT))

    args = parser.parse_args()

    if args.cmd == "write":
        findings = json.loads(Path(args.findings).read_text()) if args.findings else []
        matrix = json.loads(Path(args.matrix).read_text()) if args.matrix else []
        inventory = (
            json.loads(Path(args.claim_inventory).read_text()) if args.claim_inventory else None
        )
        try:
            path = write_stage_artifact(
                args.slug,
                args.stage,
                findings,
                matrix,
                args.document_type,
                claim_inventory=inventory,
                audits_root=Path(args.audits_root),
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(str(path))
    else:
        state = load_resume_state(args.slug, audits_root=Path(args.audits_root))
        print(
            json.dumps(
                {
                    "slug": state.slug,
                    "audit_dir": str(state.audit_dir),
                    "completed_stages": state.completed_stages,
                    "next_stage": state.next_stage,
                    "claims_loaded": len((state.claim_inventory or {}).get("items") or []),
                    "findings_loaded": len(state.findings),
                    "matrix_entries_loaded": len(state.verification_matrix),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
