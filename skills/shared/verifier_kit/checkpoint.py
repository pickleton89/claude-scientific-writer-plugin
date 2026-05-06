"""Generic stage-checkpoint state machine for resumable audit-style pipelines.

Extracted from `skills/research-accuracy-verifier/scripts/checkpoint.py`
(Sprint 3 of the skill-chaining pilot). The verifier wraps this module with
its 7 stages and the `FindingValidator` factory; other skills can adopt the
same pattern by passing their own `stage_names` and (optionally) a
finding-validation callable.

The state machine writes per-stage artifacts to
`<audits_root>/<slug>/<stage_filename>.json`. On resume, the loader scans
the directory and returns the contiguous prefix of completed stages — a gap
in the middle is treated as "next_stage = first missing", forcing the
caller to re-run that stage rather than silently skipping it.

Skill specialization:
    * `stage_names`: ordered dict-like map of int → str. The first stage may
      use a separate filename (e.g. the verifier's `claim_inventory.json`)
      via `stage_one_alternate_filename`.
    * `findings_validator`: optional callable
      `(finding, document_type) -> (ok, errors, warnings)`. Stages 2+ refuse
      to write findings that fail validation. Pass `None` to skip — useful
      for skills whose stages emit non-finding artifacts only.
    * `stage_one_payload_key`: the dict key under which Stage 1's payload is
      passed (defaults to `"claim_inventory"`). The payload is written
      verbatim to `stage_one_alternate_filename` if provided.

The class API (`Checkpoint(...).write(...)` / `Checkpoint(...).load(...)`)
is the canonical surface; module-level functions
`write_stage_artifact` / `load_resume_state` exist for back-compat with the
original verifier API and accept the same parameters as Checkpoint methods.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


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

    `completed_stages` is always a contiguous prefix of the configured stage
    range: the loader breaks at the first missing stage artifact. If
    `completed_stages` is empty, `next_stage` is the lowest configured stage
    number (typically 1) and no resumable state exists.
    """

    slug: str
    audit_dir: Path
    completed_stages: list[int] = field(default_factory=list)
    next_stage: int = 1
    stage_one_payload: dict[str, Any] | None = None
    findings: list[dict[str, Any]] = field(default_factory=list)
    verification_matrix: list[dict[str, Any]] = field(default_factory=list)


FindingsValidator = Callable[
    [dict[str, Any], str], tuple[bool, list[str], list[str]]
]


class Checkpoint:
    """Stage-checkpoint state machine parameterized for the calling skill.

    Construct once per audit pipeline; reuse for write + load calls.
    """

    def __init__(
        self,
        stage_names: Mapping[int, str],
        *,
        audits_root: Path | str = Path("research/audits"),
        findings_validator: FindingsValidator | None = None,
        stage_one_alternate_filename: str | None = None,
        stage_one_payload_key: str = "claim_inventory",
    ) -> None:
        if not stage_names:
            raise ValueError("stage_names must not be empty")
        self.stage_names: dict[int, str] = dict(stage_names)
        self.audits_root = Path(audits_root)
        self.findings_validator = findings_validator
        self.stage_one_alternate_filename = stage_one_alternate_filename
        self.stage_one_payload_key = stage_one_payload_key
        self._stage_keys = sorted(self.stage_names.keys())
        self._first_stage = self._stage_keys[0]

    # -- internals ---------------------------------------------------------

    def _stage_path(self, audit_dir: Path, stage: int) -> Path:
        if stage == self._first_stage and self.stage_one_alternate_filename:
            return audit_dir / self.stage_one_alternate_filename
        return audit_dir / f"{stage:02d}_{self.stage_names[stage]}.json"

    # -- public API --------------------------------------------------------

    def write(
        self,
        slug: str,
        stage: int,
        findings: list[dict[str, Any]],
        matrix_delta: list[dict[str, Any]],
        document_type: str,
        *,
        stage_one_payload: dict[str, Any] | None = None,
    ) -> Path:
        """Validate findings (if a validator is configured), then write.

        Stage 1 (the first configured stage): when `stage_one_alternate_filename`
        is set, writes `stage_one_payload` verbatim to that filename — the
        caller is responsible for schema-validating that payload itself, since
        Stage 1 schemas vary by skill (the verifier's claim_inventory shape
        differs from any future skill's intake artifact).

        Stages 2+: each finding is validated via `findings_validator(finding,
        document_type)` if present; any failure raises `ValueError` so the
        caller loops back rather than persisting unvalidated state.
        """
        if stage not in self.stage_names:
            raise ValueError(
                f"stage must be one of {self._stage_keys}, got {stage}"
            )
        if stage_one_payload is not None and not self.stage_one_alternate_filename:
            # Surface misconfiguration loudly — silently dropping the payload
            # would lose state the caller intended to persist.
            raise ValueError(
                "stage_one_payload was provided but Checkpoint was configured "
                "without stage_one_alternate_filename — pass the alt filename "
                "to opt into the alternate-Stage-1 path, or omit the payload."
            )
        audit_dir = self.audits_root / slug
        audit_dir.mkdir(parents=True, exist_ok=True)

        if stage == self._first_stage and self.stage_one_alternate_filename:
            if stage_one_payload is None:
                raise ValueError(
                    f"stage {stage} requires {self.stage_one_payload_key} "
                    "(passed as stage_one_payload=...)"
                )
            if not isinstance(stage_one_payload, dict):
                raise ValueError(
                    f"{self.stage_one_payload_key} must be a dict (got "
                    f"{type(stage_one_payload).__name__})"
                )
            path = self._stage_path(audit_dir, stage)
            path.write_text(json.dumps(stage_one_payload, indent=2))
            return path

        if self.findings_validator is not None:
            errors: list[str] = []
            for i, f in enumerate(findings):
                ok, errs, _ = self.findings_validator(f, document_type)
                if not ok:
                    errors.append(
                        f"findings[{i}] (id={f.get('id')}): {'; '.join(errs)}"
                    )
            if errors:
                raise ValueError(
                    f"Stage {stage} findings failed validation:\n  "
                    + "\n  ".join(errors)
                )

        artifact = {
            "stage": stage,
            "stage_name": self.stage_names[stage],
            "document_type": document_type,
            "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "findings": findings,
            "matrix_delta": matrix_delta,
        }
        path = self._stage_path(audit_dir, stage)
        path.write_text(json.dumps(artifact, indent=2))
        return path

    def load(self, slug: str) -> ResumeState:
        """Inspect `audits_root/slug/` and return resume state.

        Stages are considered complete in contiguous order from the lowest
        configured stage: the first missing stage artifact stops the resume
        scan. A gap (e.g., 1, 2, 4 present but 3 missing) is treated as
        next_stage = 3 — the audit must re-run stage 3 before proceeding.
        """
        audit_dir = self.audits_root / slug
        state = ResumeState(
            slug=slug, audit_dir=audit_dir, next_stage=self._first_stage
        )
        if not audit_dir.exists():
            return state

        # Stage 1 — alternate filename when configured.
        first = self._first_stage
        first_path = self._stage_path(audit_dir, first)
        if first_path.exists():
            payload = json.loads(first_path.read_text())
            if self.stage_one_alternate_filename:
                state.stage_one_payload = payload
            else:
                # Same shape as later stages: pull findings + matrix.
                state.findings.extend(payload.get("findings") or [])
                state.verification_matrix.extend(payload.get("matrix_delta") or [])
            state.completed_stages.append(first)
        else:
            return state

        # Stages 2..N — uniform shape.
        for stage in self._stage_keys[1:]:
            path = self._stage_path(audit_dir, stage)
            if not path.exists():
                break
            artifact = json.loads(path.read_text())
            state.completed_stages.append(stage)
            state.findings.extend(artifact.get("findings") or [])
            state.verification_matrix.extend(artifact.get("matrix_delta") or [])

        if state.completed_stages:
            last = state.completed_stages[-1]
            # next_stage = the stage just past `last`, or `last + 1` if `last`
            # is the highest configured stage (caller treats == max as "done").
            idx = self._stage_keys.index(last)
            state.next_stage = (
                self._stage_keys[idx + 1]
                if idx + 1 < len(self._stage_keys)
                else last + 1
            )
        return state
