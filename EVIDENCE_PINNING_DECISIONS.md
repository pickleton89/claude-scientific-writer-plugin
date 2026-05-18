# Phase 1 Implementation Decisions Log

Running log of decisions made during Phase 1 (mellow-bumblebee plan) that **were not in the plan**, OR where plan-as-written had to be adjusted in light of code reality. Each entry records what changed and why.

The plan file lives at `~/.claude/plans/let-s-put-together-a-mellow-bumblebee.md`.

---

## Conventions

- **Plan ref** — section of the plan this relates to.
- **Decision** — what we chose.
- **Rationale** — why.
- **Trade-off** — what we gave up.
- Entries are append-only and timestamped.

---

## Entries

### 2026-05-18 — Schema design refinements (Task 1)

**Plan ref:** §5.1 (new schemas)

**Decisions diverging from / extending the plan:**

1. **`editorial_notices.type` gained a `NONE` enum value.**
   - Plan sketch wrote `"type": "RETRACTION|CORRECTION|EOC|null"` (the type field itself nullable).
   - Implementation: outer field is nullable (`oneOf: [null, EditorialNotices]`), AND when probed-with-no-notices we encode `{type: "NONE", fetched_at: ...}` rather than `null`.
   - **Why:** P7 audit trail needs to distinguish "Scite probe never ran" (null) from "probe ran, found nothing" (NONE). Otherwise we can't tell a forgotten probe from a clean paper.
   - **Trade-off:** slightly more verbose; field has tri-state semantics (null / NONE / found-something).
   - Applied symmetrically to `venue_quality.concern` (added `"none"` enum value).

2. **`Override.before` is optional; `Override.after` is required.**
   - Plan sketch implied both were present.
   - Implementation: only `after` is required because that's all override application needs. `before` is kept for diff readability.
   - **Trade-off:** less symmetric, but matches actual usage — the LLM may not know what the parser produced before overriding.

3. **Kept both `Section.paragraph_ids[]` AND `Paragraph.section_id`.**
   - Redundant data; could be derived either way.
   - **Why kept:** mirrors deep-research convention of slight redundancy for read-time convenience. Documented `paragraphs[].section_id` as authoritative — predicates resolve against it; `paragraph_ids[]` is a convenience index.
   - **Risk:** the two can drift if a writer edits one but not the other. Mitigated by candidate D5 predicate (deferred — would enforce that every `Section.paragraph_ids[]` entry has a matching `Paragraph` with the same `section_id`).

4. **`resolution_paths.minItems: 1`** (not in plan).
   - **Why added:** Stage 2 always logs at least one identifier-lookup attempt, even if it fails. An empty list would indicate the source was added without any verification — that should fail validation, not silently pass.

5. **`document_inventory.metadata.parser_version`** (added; not in plan sketch).
   - **Why added:** mirrors `deep-research/schemas/sources.json` `metadata.search_contract_version` pattern. Lets us invalidate inventories built with an outdated parser without rebuilding the whole audit.

6. **Section/Paragraph ID patterns enforced as regex** (`^S\d{3,}$`, `^P\d{3,}$`).
   - Plan sketch wrote them informally ("S001, P001").
   - **Why added:** validator-enforced format prevents the LLM-emitted overrides from drifting to ad-hoc IDs (`section_1`, `intro-p2`).

### 2026-05-18 — parse_document.py (Task 4)

**Plan ref:** §5.3

1. **Preamble section is lazily allocated.**
   - First pass pre-allocated a Preamble synthetic section at S001, then dropped it if no pre-heading content arrived. Result: docs without preamble started at S002, which looked wrong.
   - Fixed to lazy allocation — Preamble is only created when pre-heading content arrives.
   - Docs that start with a heading now have IDs starting at S001, as expected.

2. **Plaintext-heading detection is intentionally conservative.**
   - Plan said "all-caps line on its own line". My regex requires 3-80 chars, no lowercase, contains at least one letter, and does NOT end in a period (to avoid matching sentences typed in CAPS).
   - **Trade-off:** may miss some genuine plaintext headings (e.g. "INTRODUCTION." with a period). The LLM-override mechanism handles edge cases.

3. **SHA-256 anchors normalized content**, not raw.
   - Normalization is NFC + LF + per-line trailing whitespace strip.
   - **Why:** raw SHA depends on file-system line endings; normalized SHA survives CRLF/LF differences and incidental whitespace edits, but still catches semantic changes.

### 2026-05-18 — extract_reference_map.py (Task 5)

**Plan ref:** §5.4

1. **Citation key uniqueness is NOT validated at Stage 1.**
   - The same paper may be referenced as `Smith2019` (BibTeX form) AND `Smith et al. 2019` (narrative form) AND `[1]` (numeric). All three become separate entries in `citations[]`.
   - **Why:** at Stage 1 we don't yet know they're the same paper. Stage 2 fills `paper_id` for all three, and predicate R3 / M-predicates can detect collisions then.
   - **Trade-off:** `reference_map.json` can have many keys pointing at the same paper. Downstream consumers must group by `paper_id`, not by `key`.

2. **Numeric range expansion has a sanity cap** (`end - start < 100`).
   - `[1-9999]` won't expand. Prevents pathological inputs.

3. **BibTeX parsing is intentionally minimal.**
   - Plan said "regex sweep for common patterns". I extract keys via the `@TYPE{KEY,` header regex and capture the body as raw_text. Does not parse fields (`author`, `year`, `doi`). Stage 2 calls Crossref/PubMed/OpenAlex with the raw_text anyway, so deeper parsing has no payoff at this layer.
   - Numbered-ref fallback supports `[N] Author...` style lists for PDFs converted via markitdown.

4. **Inventory dependency is hard.**
   - `extract_reference_map.py` requires a prior `document_inventory.json` because every occurrence needs section_id / paragraph_id. Citations found in headings get dropped (no paragraph_id), which is correct — headings shouldn't carry citations.

### 2026-05-18 — validate_audit_report.py / R-predicates (Task 7)

**Plan ref:** §5.7

1. **🚨 Hidden duplication: `audit_report.json` inlines `Finding` instead of `$ref`-ing `finding.json`.**
   - Discovered when the R-predicate integration test failed with `Additional properties are not allowed ('paper_id' was unexpected)` even though I'd already added `paper_id` to `schemas/finding.json`.
   - Root cause: `audit_report.json` carries a comment `"Inlined from finding.json so audit_report.json validates without an external $ref resolver. Keep in sync with schemas/finding.json."` (line 104). So every change to finding.json must be mirrored in audit_report.json.
   - Fix: added `paper_id` to BOTH `schemas/finding.json` `evidence.items.properties` AND `schemas/audit_report.json` `definitions.Finding.properties.evidence.items.properties`.
   - **Follow-up for future plan:** Worth refactoring the inlining to a proper `$ref` (with a one-time bundling step) so this drift can't happen again. Out of scope here; flagged.

2. **`document_text` is passed to R4 as a separate kwarg, not embedded in `document_inventory.json`.**
   - Plan §5.7 implied R4 would do "string-equals the substring of the source-of-truth text at location" but didn't say where the text comes from. Two options:
     - (a) Embed paragraph text in `document_inventory.json`. Bloats the artifact by ~doc size.
     - (b) Require the caller to also supply the document text (CLI: `--document PATH`; programmatic: `document_text` kwarg).
   - Chose (b). The inventory stays small + composable; R4 transparently skips with a WARN when text isn't supplied.
   - **Trade-off:** R4 has a two-input requirement (`document_inventory` + `document_text`); callers must thread both.

3. **R4 section lookup is fuzzy-by-name** (case-insensitive + prefix match).
   - The existing `Finding.location.section` field is free text like `"Significance, paragraph 3"` while `document_inventory.sections[].name` is the heading name like `"Significance"`.
   - R4 first tries exact case-insensitive match, then prefix match either direction. Imperfect — emits a clear failure when no match found.
   - **Future:** Stage 1 prompt should encourage findings to use section names from the inventory verbatim (or carry an explicit `section_id`). Not changing the Finding schema in Phase 1 to keep the addition strictly additive.

4. **Advisory/required mode is implemented as bucket selection at predicate run time.**
   - `r_bucket = errors if ARTIFACT_ENFORCEMENT == 'required' else warnings`. Each R-predicate appends to that bucket.
   - Pre-existing P8 always emits to `errors` regardless — it's a hard gate by design.
   - Skip messages (`R{n} skipped: ...`) always emit to `warnings` regardless of enforcement, because skipping isn't a failure — it's a missing input.

5. **`run_r_predicates()` companion function added.**
   - Mirrors the existing `run_p8()` companion. Returns per-predicate `pass | fail | n/a` map.
   - **Why added:** `render_report.generate_report()` will need this in Phase 3 (transitive R-enforcement at render time) and tests need it too.

6. **`_run_p8()` extracted from inline logic.**
   - Refactored the existing P8 implementation into a private method on the validator so it can be invoked separately (matches the structure of the new R-predicate methods).
   - `run_p8()` companion now delegates to `_run_p8`. Behavior unchanged; all 28 existing tests still pass.

### 2026-05-18 — checkpoint.py integration (Task 8) — scope reduced

**Plan ref:** §5.10, §9.2

**Decision:** SCOPE REDUCED. Plan §5.10 said `checkpoint.py write` should accept optional `--document-inventory`, `--reference-map`, `--resolved-sources` flags that validate when supplied. **I deferred the flag-threading to Phase 2/3** and only landed the `update_paper_ids` helper (the §9.2 piece).

**Rationale:**
- Phase 1 callers can run `validate_artifact.py` themselves — bundling validation into `checkpoint.py write` is an ergonomic improvement, not a correctness requirement.
- `checkpoint.py` is hot-path code (tested by 28 P8 tests + checkpoint_test suite). Adding optional flags risks touching the back-compat contract.
- The `update_paper_ids()` helper already exists in `extract_reference_map.py` (the natural home — it knows the citation shape). I did NOT add a thin re-export wrapper in `checkpoint.py` because that would mean two import paths for the same function with no functional gain.

**Trade-off:** Stage 2 callers must explicitly invoke both `update_paper_ids` (to backfill `reference_map.json`) AND `validate_artifact.py --kind reference_map` (to re-validate) — the integration isn't bundled. Acceptable for Phase 1; revisit if it becomes friction.

**Files NOT modified** as a result: `scripts/checkpoint.py`. Existing 28 + checkpoint tests untouched.

### 2026-05-18 — Phase 1 complete

**Test suite:**
- `skills/research-accuracy-verifier/tests/` → **265 passed** (was 188 pre-Phase-1; net +77 new tests across the 4 new test files + the R-predicate class).
- `skills/shared/tests/` → **93 passed** (unchanged — no shared-module regression).

**End-to-end CLI on the `tests/fixtures/audit_minimal/` happy-path fixture:**

```
audit_report.json: VALID (enforcement=advisory, P8: n/a, R1:pass R2:pass R3:pass R4:pass R6:pass)
```

**New file inventory (Phase 1):**

Schemas:
- `schemas/document_inventory.json`
- `schemas/reference_map.json`
- `schemas/resolved_sources.json`
- `schemas/finding.json` — `evidence[].paper_id` added
- `schemas/audit_report.json` — same field added to inlined `Finding` copy (hidden-duplication gotcha)

Scripts:
- `scripts/thresholds.py` — `ARTIFACT_KINDS`, `ARTIFACT_SPECS_BY_TIER`, `ARTIFACT_ENFORCEMENT`, helpers
- `scripts/parse_document.py` — hybrid baseline parser + `resolve_location()` override applier
- `scripts/extract_reference_map.py` — citation sweep + bibliography parser + `update_paper_ids()`
- `scripts/validate_artifact.py` — multi-kind validator (D1–D4, M1–M3, S1/S2/S4/V1/V2)
- `scripts/validate_audit_report.py` — extended with R1–R4, R6; CLI gains 5 artifact-path flags

Tests:
- `tests/test_thresholds.py` (10 tests)
- `tests/test_parse_document.py` (29 tests)
- `tests/test_extract_reference_map.py` (16 tests)
- `tests/test_validate_artifact.py` (18 tests)
- `tests/test_validate_audit_report.py` — `TestRPredicatesHappyPath`, `TestR1`, `TestR2`, `TestR3`, `TestR4`, `TestR6`, `TestRequiredModeFlip` (11 new tests; 28 pre-existing P8 tests still green)

Fixtures:
- `tests/fixtures/audit_minimal/` — 7 files: `document.md`, `intake.json`, `claim_inventory.json`, `document_inventory.json`, `reference_map.json`, `resolved_sources.json`, `audit_report.json`, `bibliography.txt`

Prose:
- `SKILL.md` — §Pinned artifacts (new section between pipeline and Stage 0)
- `references/CONTRACTS.md` — §Cross-artifact predicates (R1–R6) (after §Hard predicates)
- `references/predicates.md` — appended R1–R6 sections + intro-line tweak about enforcement modes
- `references/stages/stage_1_parse.md` — §Emit pinned artifacts (Phase 1+)
- `references/stages/stage_2_citation_existence.md` — §Emit `resolved_sources.json` + backfill `reference_map.json` paper_ids

**Phase 1 deferred (in plan but not landed):**
- `checkpoint.py write` optional artifact-path flags (decision: defer to Phase 2/3, scope-reduce — see entry above).
- D5 candidate predicate (Section.paragraph_ids ↔ Paragraph.section_id symmetry).
- Refactoring the inlined Finding in audit_report.json into a proper `$ref` (flagged as a future cleanup).

**Ready for Phase 2** (external-evidence ledger + R5 + memoization).

### 2026-05-18 — Fresh-eyes review fixes

Six issues surfaced by `/fresh-eyes`; all addressed before `/ship`:

1. **Premature truth claims for R1–R6 transitivity at render time** (3 spots).
   - SKILL.md §Pinned artifacts, predicates.md intro, CONTRACTS.md §Cross-artifact predicates — each said R1–R6 run "transitively from `render_report.generate_report()`". Today only P8 is transitive; Phase 3 ships the R-transitivity.
   - Fixed: qualified each clause to clarify Phase 1 ships Stage-8-only enforcement; Phase 3 adds transitivity.

2. **`ArtifactValidator("external_evidence")` raised raw `FileNotFoundError`** for programmatic callers (CLI handled it, library users didn't).
   - Fixed: constructor now raises `NotImplementedError` with a clear "Phase 2" message when the kind is `external_evidence` and the schema file is absent.

3. **R4 fuzzy section match had a false-positive on 1-char section names** (`startswith` matched a section named "A" against any location starting with "a").
   - Fixed: prefix-match now requires `min(len(name_lower), len(section_name)) >= 3`. Real-world sections always satisfy this; pathological one-letter sections no longer over-match.

4. **`_strip_wrapper` and `_normalize_text` duplicated** between `parse_document.py` and `extract_reference_map.py` (with a separate copy of the wrapper-strip regex in `validate_audit_report.py`'s late import).
   - Fixed: extracted to `scripts/_text_norm.py` (private util, leading underscore). All three callers now import from there. SHA-256 anchoring and char-offset alignment cannot drift between producers.

5. **`predicates.md` section order** put R1–R6 *after* "Operating principles", visually orphaning the new predicates at the end.
   - Fixed: reordered to P1–P8 → R1–R6 → Operating principles.

6. **`parse_document.py --json` help text was misleading** ("Force pretty-printed JSON to stdout. Implied when --output is omitted") — output is always pretty-printed; the flag's only effect is echo-to-stdout when `--output` is set.
   - Fixed: clearer wording.

**Post-fix verification:**
- `ruff check` clean across all scripts.
- Full verifier test suite: 265/265 pass.
- End-to-end CLI on minimal fixture: `VALID (enforcement=advisory, P8: n/a, R1:pass R2:pass R3:pass R4:pass R6:pass)`.

### 2026-05-18 — Phase 2 implementation (external-evidence ledger + R5)

**Plan ref:** §6 (Phase 2).

**Decisions diverging from / extending the plan:**

1. **Cache key includes `paper_id` scope** (plan implied only `query_hash`).
   - `lookup_or_fetch` matches `(tool, query_hash, paper_id)` together, not just `(tool, query_hash)`.
   - **Why:** the same `query_params` may return paper-scoped vs free-text data depending on whether `paper_id` is set. Conflating the two would surface false cache hits.
   - **Trade-off:** a tool called twice with the same query but different `paper_id` scopes produces two ledger entries (correct but slightly more storage).

2. **`canonicalize_query` lowercases string VALUES only, not keys.**
   - Considered lowercasing keys too. Decided against: API param names (`PMID` vs `pmid`) are case-sensitive at the tool layer; the same caller will reliably pass the same key convention, so key case isn't a real cache-miss risk. Value case (DOI casing) is the realistic case-insensitive axis.
   - Documented inline.

3. **E3 sort-order check is advisory-only** (plan §6.5 marked it `(advisory)`).
   - Append-only writes via `lookup_or_fetch` produce sorted ledgers by construction. Out-of-order entries imply manual edit or clock skew — worth flagging, not blocking. Matches user's pre-impl choice.

4. **`_LEDGER_METHODS` registry hard-coded in `validate_audit_report.py`** (instead of `thresholds.py`).
   - Considered colocating with `ARTIFACT_FRESHNESS_DAYS`. Decided to keep the method→tool mapping next to its sole consumer (R5) to avoid coupling the runtime helper (`external_evidence.py`) to the predicate's concept of "ledger-routed methods". Matches user's pre-impl choice.
   - Two entries land in Phase 2: `scite_context → scite`, `pubtator3_entity_check → pubtator3`. The `verification_path[].method` enum in `schemas/finding.json` already includes both — no schema change needed.
   - Future ledger methods (e.g., a hypothetical `openalex_venue_quality`) will need: enum addition + `_LEDGER_METHODS` entry + `ARTIFACT_FRESHNESS_DAYS` entry. Documented in predicates.md §R5.

5. **`external_evidence.py` is library-only** (no CLI).
   - Plan §6.2 didn't specify a CLI; matches user's pre-impl choice. Stages 2-4 import the helper directly. A future debugging CLI (`external_evidence.py list --slug X`) is a candidate follow-up.

6. **`R5` uses set-membership matching** (any of a finding's `evidence[].paper_id`s matches a ledger entry → R5 passes for that step).
   - A finding can carry multiple `evidence[]` entries with different `paper_id`s (e.g., a cross-paper alignment finding). R5 fires only if NONE of them have a matching ledger row for the probe's tool.
   - **Trade-off:** could miss a partial-probe-coverage case (probe ran for paper A but not paper B in the same finding). Acceptable for Phase 2 — the alternative (per-`paper_id` enforcement) would over-fire on legitimate cross-paper findings.

7. **`record_consumption` is idempotent and silent on missing entries** (returns `False`, doesn't raise).
   - Not in plan §6.2 — added because stages may attempt to record consumption against a stale entry_id if the ledger was rewritten. Silent-no-op is safer than raising.

8. **Fixture ledger added at `tests/fixtures/audit_minimal/external_evidence.json`.**
   - The existing fixture's `audit_report.json` has a `scite_context` step against `paper_id=10.1126/science.1258096`. The new ledger ships one E0001 entry that matches it so the happy-path suite still prints VALID on all six R-predicates.

**Test deltas (+33 net):**
- `tests/test_external_evidence.py` — 21 new (canonicalize / lookup_or_fetch / record_consumption).
- `tests/test_validate_artifact.py` — +6 (TestExternalEvidence{HappyPath:1, E1:1, E2:2, E3:2}).
- `tests/test_validate_audit_report.py` — +5 (TestR5ExternalEvidenceLedger × 5) + 1 (TestRequiredModeFlip.test_required_mode_promotes_r5_to_error).
- Phase 1 + Phase 2 total: **298 passed**.

**End-to-end CLI on `tests/fixtures/audit_minimal/`:**

```
audit_report.json: VALID (enforcement=advisory, P8: n/a, R1:pass R2:pass R3:pass R4:pass R5:pass R6:pass)
```

**New file inventory (Phase 2):**

Schemas:
- `schemas/external_evidence.json`

Scripts:
- `scripts/external_evidence.py` — `lookup_or_fetch`, `record_consumption`, `canonicalize_query`, `query_hash`
- `scripts/validate_artifact.py` — `_external_evidence_predicates` (E1-E3); dropped Phase-1 `NotImplementedError` gate; docstring updated
- `scripts/validate_audit_report.py` — `_run_r5`, `_LEDGER_METHODS`, `--external-evidence` CLI flag, R5 added to `_R_PREDICATES`

Tests:
- `tests/test_external_evidence.py` (21 tests)
- `tests/test_validate_artifact.py` — +TestExternalEvidence{HappyPath,E1,E2,E3} (7 tests)
- `tests/test_validate_audit_report.py` — +TestR5ExternalEvidenceLedger (5 tests) + R5 case in TestRequiredModeFlip

Fixtures:
- `tests/fixtures/audit_minimal/external_evidence.json` — 1 entry matching the fixture's scite_context probe

Prose:
- `SKILL.md` §Pinned artifacts — ledger row promoted from "deferred" to "Stage 2+ append-only"; predicate list updated to include E1-E3
- `references/CONTRACTS.md` §Cross-artifact predicates — R5 prose fleshed out (was "reserved for Phase 2")
- `references/predicates.md` — new §R5 section + §Ledger predicates (E1-E3) section
- `references/stages/stage_2_citation_existence.md` — new §Route Scite + OpenAlex probes through the external-evidence ledger
- `references/stages/stage_3_alignment.md` — new §Route PubTator3 entity-check through the external-evidence ledger
- `references/stages/stage_4_uncited.md` — Stage 4 §Cherry-picking finding emitted updated to route through `lookup_or_fetch` (memoization payoff inline)

**Phase 2 deferred (in plan but not landed):**
- E4 cross-artifact (`consumed_by_findings[]` ↔ finding IDs) — explicitly deferred per plan §6.5 to "R5's territory"; not implemented because R5 currently checks the inverse direction (verification_path → ledger), not (ledger → findings). Could land in Phase 3 as a paired check if dry-run shows orphaned consumption records.
- Real-world dry-run / perturbation matrix — gates Phase 3 per plan §7.3.

**Ready for the dry-run audit** (plan §7.3, prerequisite to Phase 3 enforcement flip).
