# Stage 8 — Synthesis and reporting

**Purpose:** Assemble the report per `schemas/audit_report.json`, run final validators (P1–P5/P7/P8), and render the markdown deliverable.

**Predicates enforced:** P1–P5, P7 (per-finding via `scripts/validate_finding.py`); P8 (cross-stage via `scripts/validate_audit_report.py`). See [`../predicates.md`](../predicates.md).

## Procedure

1. **MUST** call `scripts/validate_finding.py` on every finding before assembling the report — passing `--domain <intake.domain>` and `--stage <originating-stage>` so predicate **P7** (Stage-2 Scite probe) fires. On per-finding validation failure, loop back to the offending stage rather than deliver an incomplete report.

2. **MUST** then call `scripts/validate_audit_report.py <audit_report.json> --intake <intake.json>` to enforce predicate **P8** (Tier-3 cherry-picking sweep). On P8 failure, loop back to [Stage 4](./stage_4_uncited.md) — emit either the missing cherry-picking finding(s) or a `cherry_picking:<claim_id>: <reason>` coverage caveat for each uncovered Stage-3 VERIFIED claim. P8 is also enforced transitively: `render_report.generate_report()` invokes `validate_audit_report.run_p8(...)` and raises on failure, so the markdown cannot render past a P8 violation even if the LLM skips the CLI step.

3. **Render** the markdown report via `scripts/render_report.py` (`generate_report(audit_report_dict, intake=...) → str`). When resuming from a partial audit, merge `findings[]` and `verification_matrix[]` from all loaded `0N_<stage>.json` artifacts before assembly. Write the final `audit_report.json` to `research/audits/<slug>/audit_report.json` alongside the per-stage artifacts.

## Self-audit checklist (validator pass required before delivery)

Before delivering the report, the following validators **MUST** pass:

1. `scripts/validate_finding.py --batch findings.json --document-type <type> --domain <domain>` (per-finding P1–P5 + P7). The Stage attribute is supplied implicitly when the validator is invoked via `checkpoint.py`; when calling the CLI directly, pass `--stage <originating-stage>` so P7 fires for biomedical Stage-2 findings.
2. `scripts/validate_audit_report.py audit_report.json --intake intake.json` (cross-stage P8). Enforces the Tier-3 cherry-picking sweep over Stage-3 VERIFIED claims.
3. Every claim in the inventory appears in either `findings[]` or `verification_matrix[]`.
4. Severity is consistent with the matrix.
5. Original document wording is preserved exactly when quoted (string equality against `<document>` content).
6. Coverage caveats are populated whenever a tier-3 check was requested but blocked.

Validator failure forces Stage-8 loop-back. The skill **MUST NOT** deliver a report whose findings have not passed the validator.

## Final outputs

Stage 8 does **not** call `checkpoint.py write` — `checkpoint.write_stage_artifact` raises `ValueError` for `stage > 7` (see `scripts/checkpoint.py:151`). The Stage-8 deliverables are written directly by `render_report.py`:

- `research/audits/<slug>/audit_report.json` — full structured report
- `research/audits/<slug>/report.md` — rendered markdown deliverable
