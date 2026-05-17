# Background reading

The following references in this directory provide non-technical conceptual grounding for the verification frameworks operationalized by this skill. They are useful for understanding *why* the pipeline is structured the way it is, but the skill itself never reads them at runtime — they are for human reference only.

- [`Fact-Checking AI - How to spot Errors and Reduce Hallucinations.md`](./Fact-Checking%20AI%20-%20How%20to%20spot%20Errors%20and%20Reduce%20Hallucinations.md) — full course transcript (Birss, Gen AI Academy, 2026); covers the three error flavors (phantom statistic, dead citation, reasoning error in true data), six pre-verification red flags, four logic-failure types, and a three-step verification workflow (risk triage → verify by type → second opinion).
- [`Fact-Check AI - Course Workbook.pdf`](./Fact-Check%20AI%20-%20Course%20Workbook.pdf) — pocket-reference summary of the same frameworks.

## What this skill implements from Birss's frameworks

- Three-error-flavor detection ([Stage 2](./stages/stage_2_citation_existence.md))
- Verify-by-type ordering ([Stages 2](./stages/stage_2_citation_existence.md) → [3](./stages/stage_3_alignment.md) → [6](./stages/stage_6_sanity.md))
- Risk triage (`verification_tier × flag_threshold × severity matrix` — see [`CONTRACTS.md`](./CONTRACTS.md))
- The four logic-failure subtypes ([Stages 3](./stages/stage_3_alignment.md) and [4](./stages/stage_4_uncited.md))

## What this skill does NOT implement

- **Pre-verification red-flag triage** — no Stage 1 priority signals; deferred.
- **Second-LLM critique as a workflow step** — the existing Stage 8 self-audit is schema validation via `validate_finding.py` + `validate_audit_report.py`, not a second-model critique.
- **Birss's "six honesty prompts" / "autonomy ladder"** — these target document drafting and agent-action governance, which are separate concerns from post-hoc document audit (this skill's sole responsibility — see SKILL.md § Out of scope).
