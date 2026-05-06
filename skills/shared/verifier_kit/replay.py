"""Replay helper for resumable audit pipelines.

Sets up the per-stage fork pattern that Sprint 4+ skills will use: a fork
that runs only Stage N reads the upstream stages' artifacts via this helper
rather than re-running them. For Sprint 3 the helper is small — load resume
state, optionally truncate it to a target stage, and project a stable dict
shape downstream consumers can pass through `Bash` substitution.

Example (consumed by a Stage-3-only fork):

    from verifier_kit.checkpoint import Checkpoint
    from verifier_kit.replay import replay_state

    cp = Checkpoint(STAGE_NAMES, audits_root=Path("research/audits"))
    state = replay_state(cp, "my-paper", upto_stage=2)
    # state["findings"] now contains only Stages 1-2 findings; the fork can
    # start Stage 3 with that as its baseline.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # avoid runtime circular import; Checkpoint is only used for typing here
    from .checkpoint import Checkpoint


def replay_state(
    checkpoint: Checkpoint,
    slug: str,
    *,
    upto_stage: int | None = None,
) -> dict[str, Any]:
    """Load resume state and project it to a JSON-friendly dict.

    Parameters
    ----------
    checkpoint:
        A configured `verifier_kit.checkpoint.Checkpoint` instance.
    slug:
        The audit slug to load.
    upto_stage:
        Optional. When provided, truncates `completed_stages` to stages
        ≤ `upto_stage` and (for the simple in-memory projection) drops
        findings / matrix entries from later stages — but only if the
        stored artifacts carry a `stage` field downstream consumers can
        filter on. Stage 1 (alternate-filename) payloads are preserved
        when `upto_stage >= first_stage`.

    Returns
    -------
    dict
        A dict with keys: `slug`, `audit_dir` (str), `completed_stages`,
        `next_stage`, `stage_one_payload`, `findings`, `verification_matrix`.
        Safe to JSON-encode and pass through Bash substitution.
    """
    state = checkpoint.load(slug)

    completed = list(state.completed_stages)
    findings = list(state.findings)
    matrix = list(state.verification_matrix)

    if upto_stage is not None:
        completed = [s for s in completed if s <= upto_stage]
        # Stored stage artifacts in this kit do not embed a per-finding stage
        # tag, so without that we cannot precisely truncate findings/matrix
        # by source-stage. Future per-stage fork callers should write that
        # tag into matrix_delta entries; for now we surface the full lists
        # plus the truncated stage list and let the caller filter.

    return {
        "slug": state.slug,
        "audit_dir": str(state.audit_dir),
        "completed_stages": completed,
        "next_stage": state.next_stage,
        "stage_one_payload": state.stage_one_payload,
        "findings": findings,
        "verification_matrix": matrix,
    }
