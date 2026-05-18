#!/usr/bin/env python3
"""Stage-boundary checkpointing for resumable Tier-3 audits.

Multi-hour audits with many MCP calls can exhaust the context window. To make
audits resumable across sessions, each stage writes its findings + matrix delta
to `research/audits/<slug>/0N_<stage>.json` on completion. Stage 0 (resume
detection) reads the directory and tells the LLM which stages to skip.

Sprint 3 of the skill-chaining pilot extracted the generic state-machine into
`skills/shared/verifier_kit/checkpoint.py`. This module is now a thin wrapper
that supplies the verifier's 7-stage map and `FindingValidator` factory while
preserving the pre-extraction public API (`write_stage_artifact`,
`load_resume_state`, `ResumeState` with `.claim_inventory`).

Per-stage artifacts contain `findings[]` (validated against
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
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make `verifier_kit` importable. Path layout:
#   skills/research-accuracy-verifier/scripts/checkpoint.py
#   skills/shared/verifier_kit/
# parents[2] is the skills/ dir.
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.checkpoint import Checkpoint as _Checkpoint  # noqa: E402
from verifier_kit.checkpoint import slugify  # noqa: E402,F401  (re-export)

from validate_finding import FindingValidator  # noqa: E402

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

# Filenames of the 4 evidence-pinned artifacts that Phase 3's required-mode
# gate refuses to ship without. Kept in sync with render_report._ARTIFACT_KINDS
# (the renderer enumerates these in the first-line marker) and validate_artifact
# (which knows how to schema+predicate-check each one).
FINALIZE_ARTIFACT_FILENAMES: tuple[str, ...] = (
    "document_inventory.json",
    "reference_map.json",
    "resolved_sources.json",
    "external_evidence.json",
)


@dataclass
class ResumeState:
    """Verifier-specific resume state.

    Mirrors the pre-Sprint-3 fields exactly so existing callers and tests
    that read `.claim_inventory` continue to work. The underlying state
    machine is `verifier_kit.checkpoint.Checkpoint`; this wrapper just
    re-shapes the dataclass.
    """

    slug: str
    audit_dir: Path
    completed_stages: list[int] = field(default_factory=list)
    next_stage: int = 1
    claim_inventory: dict[str, Any] | None = None
    findings: list[dict[str, Any]] = field(default_factory=list)
    verification_matrix: list[dict[str, Any]] = field(default_factory=list)


def _make_checkpoint(
    audits_root: Path = DEFAULT_AUDITS_ROOT,
    *,
    domain: str | None = None,
) -> _Checkpoint:
    """Build a Checkpoint with a closure-bound FindingValidator.

    `domain` is captured by the closure and forwarded to every per-finding
    validation call, alongside the `stage` kwarg that `verifier_kit.Checkpoint`
    supplies. Together they gate predicate P7 (Stage-2 Scite retraction probe).
    """
    validator = FindingValidator()

    def validate(
        finding: dict[str, Any], document_type: str, **kwargs: Any
    ) -> tuple[bool, list[str], list[str]]:
        # `stage` arrives via the kit; `domain` is closed over from the
        # surrounding factory call. Either may be None — P7 is skipped in
        # that case, preserving back-compat for callers that never set
        # `domain`.
        stage = kwargs.get("stage")
        return validator.validate(
            finding, document_type, domain=domain, stage=stage
        )

    return _Checkpoint(
        STAGE_NAMES,
        audits_root=audits_root,
        findings_validator=validate,
        stage_one_alternate_filename="claim_inventory.json",
        stage_one_payload_key="claim_inventory",
    )


def write_stage_artifact(
    slug: str,
    stage: int,
    findings: list[dict[str, Any]],
    matrix_delta: list[dict[str, Any]],
    document_type: str,
    *,
    claim_inventory: dict[str, Any] | None = None,
    domain: str | None = None,
    audits_root: Path = DEFAULT_AUDITS_ROOT,
) -> Path:
    """Validate findings, then write the stage artifact. Returns the written path.

    Stage 1: writes `claim_inventory.json` from `claim_inventory` — the wrapper
    object `{"items": [...]}` per `schemas/claim_inventory.json`. The caller is
    responsible for schema-validating the inventory before passing it in.
    Stages 2–7: validates each finding via FindingValidator before writing —
    invalid findings raise ValueError so the caller loops back rather than
    persisting unvalidated state.

    `domain` is the intake domain (`biomedical | general | mixed`). When
    supplied, it activates predicate P7 (Stage-2 Scite retraction probe);
    biomedical/mixed Stage-2 findings without a Scite verification_path
    entry will fail validation and the write raises ValueError. When `None`
    (default), P7 is skipped — back-compat for legacy callers.
    """
    if stage == 1:
        # Preserve the pre-Sprint-3 error message wording for back-compat.
        if claim_inventory is None:
            raise ValueError("stage 1 requires claim_inventory")
        if not isinstance(claim_inventory, dict) or "items" not in claim_inventory:
            raise ValueError(
                "claim_inventory must be a dict with an 'items' key "
                "(per schemas/claim_inventory.json)"
            )
    if stage not in STAGE_NAMES:
        raise ValueError(f"stage must be 1..7, got {stage}")

    cp = _make_checkpoint(audits_root, domain=domain)
    return cp.write(
        slug,
        stage,
        findings,
        matrix_delta,
        document_type,
        stage_one_payload=claim_inventory,
    )


def finalize_audit(
    slug: str,
    *,
    audits_root: Path = DEFAULT_AUDITS_ROOT,
    enforcement: str = "auto",
) -> dict[str, Any]:
    """Pre-ship gate: confirm the audit's full evidence-pinned artifact set
    is present and individually valid before the audit_report.json is
    rendered or handed off to a downstream skill.

    Behavior:
      - `enforcement="auto"` (default): reads `thresholds.ARTIFACT_ENFORCEMENT`.
      - `enforcement="required"`: every artifact in
        `FINALIZE_ARTIFACT_FILENAMES` must exist AND validate against its
        schema + predicates. Missing or invalid artifacts raise `ValueError`.
      - `enforcement="advisory"`: returns a status dict listing missing /
        invalid artifacts; never raises.

    Returns a dict shaped::

        {
          "slug": str,
          "audit_dir": str,
          "enforcement": "advisory" | "required",
          "ok": bool,
          "artifact_status": {
            "document_inventory": {"present": bool, "valid": bool|None,
                                   "errors": [str], "warnings": [str]},
            ...
          },
        }

    `valid` is None when the artifact is absent (no validation attempted).
    Library-only this phase — no CLI surface added in Phase 3. Stages 1-7
    continue to use `write_stage_artifact`; this is the new gate that sits
    between stage-7 completion and audit_report.json assembly/render.
    """
    # Import validate_artifact lazily — only the finalize path needs the
    # schema validator surface; the legacy stages-1-7 callers (write_stage_artifact /
    # load_resume_state) never touch it.
    from validate_artifact import validate_artifact  # noqa: PLC0415
    from thresholds import resolve_enforcement  # noqa: PLC0415

    effective = resolve_enforcement(enforcement)

    audit_dir = Path(audits_root) / slug
    status: dict[str, dict[str, Any]] = {}
    overall_ok = True
    for fname in FINALIZE_ARTIFACT_FILENAMES:
        kind = fname.removesuffix(".json")
        path = audit_dir / fname
        if not path.exists():
            status[kind] = {
                "present": False,
                "valid": None,
                "errors": [f"{fname} not found at {path}"],
                "warnings": [],
            }
            overall_ok = False
            continue
        try:
            ok, errs, warns = validate_artifact(kind, path)
        except Exception as e:  # noqa: BLE001 — surface the failure shape uniformly
            ok, errs, warns = False, [f"validation crashed: {e}"], []
        status[kind] = {
            "present": True,
            "valid": ok,
            "errors": list(errs),
            "warnings": list(warns),
        }
        if not ok:
            overall_ok = False

    result = {
        "slug": slug,
        "audit_dir": str(audit_dir),
        "enforcement": effective,
        "ok": overall_ok,
        "artifact_status": status,
    }

    if effective == "required" and not overall_ok:
        lines = [
            f"Audit {slug!r} cannot be finalized — required artifact set "
            f"incomplete or invalid:",
        ]
        for kind, s in status.items():
            if s["valid"] is True:
                continue
            tag = "MISSING" if not s["present"] else "INVALID"
            lines.append(f"  - {kind}: {tag}")
            for e in s["errors"][:3]:
                lines.append(f"      {e}")
        raise ValueError("\n".join(lines))

    return result


def load_resume_state(
    slug: str, *, audits_root: Path = DEFAULT_AUDITS_ROOT
) -> ResumeState:
    """Inspect `audits_root/slug/` and return resume state.

    Stages are considered complete in contiguous order from 1: the first
    missing stage artifact stops the resume scan. A gap (e.g., 1, 2, 4
    present but 3 missing) is treated as next_stage = 3 — the audit must
    re-run stage 3 before proceeding.
    """
    cp = _make_checkpoint(audits_root)
    raw = cp.load(slug)
    return ResumeState(
        slug=raw.slug,
        audit_dir=raw.audit_dir,
        completed_stages=list(raw.completed_stages),
        next_stage=raw.next_stage,
        claim_inventory=raw.stage_one_payload,
        findings=list(raw.findings),
        verification_matrix=list(raw.verification_matrix),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage-boundary checkpointing")
    sub = parser.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("write", help="Write a stage artifact")
    w.add_argument("--slug", required=True)
    w.add_argument("--stage", type=int, required=True, choices=range(1, 8))
    w.add_argument("--document-type", required=True)
    w.add_argument("--findings", help="Path to findings JSON array (stages 2-7)")
    w.add_argument("--matrix", help="Path to matrix-delta JSON array (stages 2-7)")
    w.add_argument(
        "--claim-inventory",
        help='Path to claim_inventory JSON object (stage 1; {"items": [...]})',
    )
    w.add_argument(
        "--domain",
        choices=["biomedical", "general", "mixed"],
        help=(
            "Intake domain. Activates P7 (Stage-2 Scite retraction probe) "
            "during per-finding validation. Omit to skip P7 (legacy behavior)."
        ),
    )
    w.add_argument("--audits-root", default=str(DEFAULT_AUDITS_ROOT))

    r = sub.add_parser("resume", help="Print resume state for a slug")
    r.add_argument("--slug", required=True)
    r.add_argument("--audits-root", default=str(DEFAULT_AUDITS_ROOT))

    args = parser.parse_args()

    if args.cmd == "write":
        findings = json.loads(Path(args.findings).read_text()) if args.findings else []
        matrix = json.loads(Path(args.matrix).read_text()) if args.matrix else []
        inventory = (
            json.loads(Path(args.claim_inventory).read_text())
            if args.claim_inventory
            else None
        )
        try:
            path = write_stage_artifact(
                args.slug,
                args.stage,
                findings,
                matrix,
                args.document_type,
                claim_inventory=inventory,
                domain=args.domain,
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
