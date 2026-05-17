# Stage 0 — Resume detection (always runs first)

**Purpose:** Make long Tier-3 audits resumable across sessions. The context window can exhaust mid-pipeline; every stage persists its output to `research/audits/<slug>/` (slug = `slugify(document_title)` from intake — see `scripts/checkpoint.py`).

**Procedure:**

Before Stage 1, call `scripts/checkpoint.py resume --slug <slug>`. The returned `next_stage` says where to begin:

- `next_stage == 1` (fresh or empty dir) → run the full pipeline
- `next_stage == N > 1` → load `claim_inventory.json` and any `0K_<stage>.json` for K in `completed_stages` into working memory, then begin at stage N

A gap in stage artifacts (e.g., 1 and 2 present, 3 missing, 4 present) means the audit must rerun stage 3; the loader stops at the first missing stage. To force a fresh audit, the user deletes `research/audits/<slug>/` before triggering the skill.

**Artifacts:** none written by Stage 0 itself; this stage only reads existing artifacts.
