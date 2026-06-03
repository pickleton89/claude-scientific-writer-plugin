# claude-scientific-writer-plugin

A Claude Code plugin: a library of ~29 scientific-research skills (biomedical
intelligence, literature analysis, accuracy verification, publication documents,
SVG/figure authoring, ToolUniverse integration). Distributed via the
`.claude-plugin/` marketplace manifest, not pip-installed.

## Layout
- `skills/<name>/SKILL.md` — one skill each; `skills/shared/` holds cross-skill code/refs.
- `skills/SKILL_ROUTER.md` — routing decision trees and scoring/tie-breaking.
- `skills/skill-router/skill_triggers.yaml` — deterministic routing triggers.
- `commands/` — slash commands (currently `prose-audit.md`).
- `docs/`, `scratch/` (gitignored) — design docs and throwaway work.

## Python: no root pyproject — scripts self-bootstrap
There is **no root `pyproject.toml` or lockfile**. CLI scripts carry PEP-723 inline
metadata (`# /// script ... # ///`) and resolve their own deps:
`uv run skills/<skill>/scripts/<tool>.py`. Do not add a top-level project or
`pip install`; keep deps declared inline per script.

Tests follow pytest conventions and live under `skills/<skill>/tests/` and
`skills/shared/tests/` (~140 test files).

## Tool access is indirected through capability keys
Skills reference capability **KEYS** (e.g. `disambiguation.gene_to_ensembl`), never
raw tool names. Resolution + preference tiers (primary MCP → ToolUniverse → fallback)
live in `skills/shared/tool-lookup.yaml`. ToolUniverse param quirks are corrected in
`skills/shared/references/known_param_corrections.md`. When wiring a new tool into a
skill, add/extend a key here rather than hardcoding the tool name in SKILL.md.

## Biomedical pipeline is dossier-first
`entity-resolution` → `target-intelligence` / `drug-intelligence` → `target-validation`.
Downstream skills extract from the upstream dossier before re-querying ToolUniverse.
Data-feed pattern: a TU skill fetches data, an existing skill renders it.

## Verifier contract/predicate system
`research-accuracy-verifier` and `deep-research` are contract-governed:
- Findings are JSON-schema-validated then checked against hard predicates (**P1–P9**,
  defined in CONTRACTS.md) via `skills/shared/verifier_kit/` and each skill's `scripts/`.
- Canonical specs: `skills/research-accuracy-verifier/references/CONTRACTS.md` and
  `references/predicates.md`. Changing a verdict enum, severity matrix, or predicate
  means updating the schema, the validator, CONTRACTS.md/predicates.md, and the
  regression fixtures together.

## Versioning & brand
- Version string is duplicated in `.claude-plugin/plugin.json` **and**
  `.claude-plugin/marketplace.json` — bump both together (`/version-bump` handles it).
- Figures/documents/presentations follow Oligon brand standards (`oligon-brand` skill).
