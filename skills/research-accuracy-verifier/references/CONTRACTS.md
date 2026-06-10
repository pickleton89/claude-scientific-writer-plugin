# Locked Contracts — research-accuracy-verifier

Single source of truth for the Verdict enum, Document Type enum, Severity matrix, and JSON schema shapes consumed by every downstream component (SKILL.md prose, JSON schemas in `schemas/`, validators in `scripts/`, router triggers, tests). Changes here cascade — modify with intent.

Phase 1 deliverable. Phase 2 (SKILL.md refactor), Phase 3 (schemas), Phase 4 (scripts), Phase 5 (tests) all consume this file.

---

## Verdict enum (10 values)

The canonical vocabulary used by every stage. No stage may invent a parallel verdict.

| Verdict | Origin stage | Meaning |
|---|---|---|
| `VERIFIED` | 2 | Citation exists **and the resolved record IS the cited paper** — all metadata fields agree, including an explicit author + title cross-check (predicate P9). DOI resolution alone is insufficient: a wrong-but-valid DOI resolves to a real but different paper and is `METADATA_MISMATCH`, not `VERIFIED`. |
| `METADATA_MISMATCH` | 2 | Citation exists; ≥1 field disagrees (year, journal, volume, pages, authors) — OR the venue itself is flagged predatory / non-indexed by OpenAlex `check_venue_quality` (`result_summary` sub-reason `venue_quality_concern`) — OR the citation has a non-empty Scite `editorialNotices` (retraction / correction / expression of concern) |
| `UNSUPPORTED` | 2/3 | No identifier path resolves; or cited source does not contain the claim |
| `OVERGENERALIZED` | 3 | Source supports a weaker / narrower version of the claim |
| `CONTRADICTED` | 3 | Source explicitly contradicts the claim |
| `MISATTRIBUTED` | 3 | Source does not address this claim at all |
| `QUOTE_VERIFIED` | 5 | Quoted text matches source exactly (or after whitespace normalization) |
| `QUOTE_PARAPHRASED` | 5 | Quoted text differs from source — paraphrase presented as verbatim |
| `QUOTE_FABRICATED` | 5 | No matching text in claimed source |
| `UNVERIFIED` | any | Verification could not be completed; **MUST** include `reason` field |

`UNVERIFIED.reason` enum: `paywalled_full_text | preprint_not_indexed | api_timeout | source_not_provided | tier_does_not_cover | other`

Stage 6 (numerical / named-entity sanity) reuses `VERIFIED | METADATA_MISMATCH | CONTRADICTED | MISATTRIBUTED | UNVERIFIED` — no separate vocabulary.

Stage 7 (internal consistency) emits `CONTRADICTED` (same fact, different numbers in two sections), `METADATA_MISMATCH` (inline cite ↔ bibliography drift), or `UNSUPPORTED` (orphan reference) — no separate vocabulary.

**Stage 3 PubTator3 entity pre-filter** (capability: `literature.entity_annotation`). When a claim names structured biomedical entities (gene/drug/disease/variant) and a cited PMID is available, the verifier MAY run `pubtator3 annotations --pmids <PMID> --summary` BEFORE attempting full-text retrieval. If one or more claim entities are absent from PubTator3's BioC-JSON tally for that PMID, the candidate verdict is `MISATTRIBUTED` and the verifier MUST attempt one full-text confirmation (Paperclip / PMC) before finalizing — PubTator3 NER has known gaps. The verification_path entry uses `method: "pubtator3_entity_check"`, `tool: "pubtator3"`, and `result_summary` MUST include the per-entity present/absent flags. False-negative overrides (PubTator3 reported absent, full text contained the entity) MUST be recorded in `evidence[].snippet` for downstream measurement of the pre-filter's precision.

---

## Document type enum (7 values)

| Document type | Severity bias |
|---|---|
| `grant` | Highest weighting (hallucinated citation = CRITICAL) |
| `manuscript` | High weighting; full IMRAD context expected |
| `lit_review` | High weighting for citation errors |
| `slides` | Lower weighting for missing citations (speech context) |
| `report` | Standard weighting |
| `memo` | Lowest weighting; informal context |
| `other` | Standard weighting; requires `document_type_other` free-text label |

---

## Severity matrix (Verdict × DocumentType → Severity, 10×7 = 70 cells)

Severity ∈ `{CRITICAL, MAJOR, MINOR, INFORMATIONAL}`. Cells abbreviate: `CRIT`, `MAJOR`, `MINOR`, `INFO`.

| Verdict \ DocType | grant | manuscript | lit_review | slides | report | memo | other |
|---|---|---|---|---|---|---|---|
| VERIFIED | INFO | INFO | INFO | INFO | INFO | INFO | INFO |
| METADATA_MISMATCH | MAJOR | MAJOR | MAJOR | MINOR | MINOR | MINOR | MINOR |
| UNSUPPORTED | CRIT | CRIT | CRIT | MAJOR | MAJOR | MINOR | MAJOR |
| OVERGENERALIZED | MAJOR | MAJOR | MAJOR | MAJOR | MINOR | MINOR | MAJOR |
| CONTRADICTED | CRIT | CRIT | CRIT | CRIT | MAJOR | MAJOR | CRIT |
| MISATTRIBUTED | CRIT | CRIT | CRIT | MAJOR | MAJOR | MINOR | MAJOR |
| QUOTE_VERIFIED | INFO | INFO | INFO | INFO | INFO | INFO | INFO |
| QUOTE_PARAPHRASED | MAJOR | MAJOR | MAJOR | MINOR | MINOR | MINOR | MINOR |
| QUOTE_FABRICATED | CRIT | CRIT | CRIT | MAJOR | MAJOR | MAJOR | CRIT |
| UNVERIFIED | INFO | INFO | INFO | INFO | INFO | INFO | INFO |

**Threshold modifier** (`flag_threshold` from intake):

- `conservative` — emit only findings whose verdict ∈ `{CONTRADICTED, MISATTRIBUTED, UNSUPPORTED, QUOTE_FABRICATED}`; suppress UNVERIFIED from `findings[]` (still reported in `verification_matrix[]`).
- `standard` (default) — emit per matrix; UNVERIFIED appears as INFORMATIONAL.
- `strict` — emit per matrix; additionally promote any `METADATA_MISMATCH` or `OVERGENERALIZED` finding whose `verification_path` has only one entry by one severity level.

---

## Hard predicates

P1–P5, P7, and P9 are per-finding predicates enforced by `validate_finding.py`. P8 is a cross-stage post-condition enforced by `validate_audit_report.py` (also invoked transitively from `render_report.generate_report()` so audits cannot render past a P8 violation).

P1. `verdict == UNVERIFIED ⟹ reason ∈ Reason AND severity != CRITICAL`
P2. `severity == CRITICAL ⟹ len(verification_path) >= 2`
P3. `len(evidence) >= 1 AND every evidence entry has a resolvable URL / PMID / DOI`
P4. `verdict ∈ {QUOTE_VERIFIED, QUOTE_PARAPHRASED, QUOTE_FABRICATED} ⟺ claim_type == "direct_quote"`
P5. `severity == SeverityMatrix[document_type][verdict]` — severity is **computed**, not user-supplied; validator rejects mismatches
P6 (advisory, not code-enforced). Verdict glyphs (✅⚠️❌❓) MUST NOT appear as verdict markers in any rendered AuditReport, finding table, or schema enum. Severity is rendered as text. Glyphs may appear in `SKILL.md` / `CONTRACTS.md` only as documentation that they are deprecated.
P7 (Stage-2 Scite retraction probe). When `domain ∈ {biomedical, mixed}` AND `stage == 2` AND `verdict ∈ {VERIFIED, METADATA_MISMATCH, UNSUPPORTED}`, `verification_path[]` MUST contain either (a) an entry with `method == "scite_context"` whose `result_summary` records the editorialNotices outcome (notices found, or empty/no record), OR (b) an entry whose `tool` field matches `/scite/i` and whose `result_summary` documents the probe failure mode (api_timeout / empty_response / not_indexed / other). Silence — no Scite entry at all — is a P7 violation. Validator inputs: `domain`, `stage` are passed as keyword args to `FindingValidator.validate(...)`; when either is `None` the predicate is skipped (back-compat for ad-hoc callers).
P8 (Tier-3 cherry-picking sweep). When `intake.domain ∈ {biomedical, mixed}` AND (`intake.verification_tier == "3"` OR (`intake.verification_tier == "custom"` AND `"uncited_claims" ∈ intake.checks_enabled`)), every `verification_matrix[]` entry satisfying `stage == "3" AND verdict == "VERIFIED"` MUST be covered by one of: (a) a `findings[]` entry whose `id`-or-`claim_ref` links to the same `claim_id`, with `stage == "4"`, `verdict == "OVERGENERALIZED"`, at least one `verification_path[]` entry with `method == "scite_context"`, and a `result_summary` matching `/USI\s*=/` (cherry-picking finding); OR (b) a `header.coverage_caveats[]` string of shape `cherry_picking:<claim_id>: <reason>` (parseable tag prefix `cherry_picking:` immediately followed by the matrix claim_id, a colon, a space, and a free-form reason). Coverage caveats with this tag prefix are auto-detected by `validate_audit_report.py`.
P9 (Stage-2 metadata-agreement gate). When `stage == 2` AND `verdict == VERIFIED` AND `verification_path[]` contains a scholarly-resolution method (`∈ {doi_lookup, pmid_lookup, crossref_search, pubmed_search, pmc_fetch}`), `verification_path[]` MUST contain an entry with `method == "metadata_agreement"`, AND that entry's `result_summary` MUST NOT record `author_match=false` or `title_match=false` (whitespace-insensitive). Resolution proves a record EXISTS; it does not prove the record IS the cited paper — a **wrong-but-valid DOI** (resolves to a real but *different* paper) passes existence yet must fail the author/title cross-check. A recorded mismatch ⟹ verdict is `METADATA_MISMATCH`, not `VERIFIED`. Domain-independent (unlike P7). Purely web-sourced findings (no scholarly-resolution method) are exempt — no resolved record to compare against; governed instead by the P7 web-source carve-out. Validator input: `stage` keyword arg to `FindingValidator.validate(...)`; when `None` the predicate is skipped (back-compat for ad-hoc callers).

---

## Cross-artifact predicates (R1–R6)

R-predicates are cross-artifact post-conditions enforced by `validate_audit_report.py` when the relevant artifacts are supplied via the `artifacts={}` kwarg (or via the CLI `--claim-inventory / --reference-map / --resolved-sources / --document-inventory / --document` flags). They run alongside P8 at Stage 8. Phase 1 ships Stage-8-only enforcement; Phase 3 adds transitive invocation from `render_report.generate_report()` (matching how P8 is enforced today) so audits cannot render past an R-violation.

**Enforcement** is gated by `scripts/thresholds.ARTIFACT_ENFORCEMENT`:

- `"advisory"` (Phase 1) — R-failures emit warnings; `ok=True`.
- `"required"` (Phase 3) — R-failures emit errors; `ok=False`; render blocked.

P1–P9 are always hard errors regardless of mode.

R1 (Finding.id resolves in claim_inventory). When `claim_inventory.json` is supplied, every `findings[].id` MUST equal some `items[].id`.

R2 (Finding.evidence[].paper_id resolves in resolved_sources). When `resolved_sources.json` is supplied AND `intake.sources_available != "none"`, every non-null `findings[].evidence[].paper_id` MUST equal some `sources[].paper_id`. `paper_id: null` is permitted (web-sourced no-DOI evidence).

R3 (Finding.citations[].key resolves in reference_map). When `reference_map.json` is supplied, every `findings[].citations[].key` MUST equal some `citations[].key`.

R4 (Finding.claim_verbatim matches document at location). When `document_inventory.json` AND the normalized document text are supplied, every `findings[].claim_verbatim` MUST appear as a substring of the paragraph addressed by `findings[].location.{section, paragraph}` (after QuoteVerifier whitespace + unicode normalization).

R5 (verification_path probes have matching external-evidence ledger entries). When `external_evidence.json` is supplied, every `findings[].verification_path[]` step whose `method` is a ledger-routed method (`scite_context`, `pubtator3_entity_check`) MUST have a matching `external_evidence.entries[]` row with the same `(tool, paper_id)`. Method → tool mapping lives in `validate_audit_report._LEDGER_METHODS`. Failure mode: probe text was hallucinated rather than executed via `external_evidence.lookup_or_fetch`.

R6 (verification_matrix[].claim_id resolves in claim_inventory). When `claim_inventory.json` is supplied, every `verification_matrix[].claim_id` MUST equal some `items[].id`.

When the relevant artifact is NOT supplied, the predicate is **skipped** with an advisory warning of shape `R<n> skipped: <artifact>.json not provided to validator`. A skipped R-predicate is not a failure.

The `paper_id` join key is byte-compatible with `deep-research/schemas/sources.json#paper_id` — DOI-preferred, PMID fallback, slug last resort. This enables a future v2 optimization where `intake.pinned_sidecars.sources_path` (from deep-research) can be consumed in lieu of running the verifier's own Stage-2 resolution.

---

## Intake JSON schema (locked field shape)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "intake.json",
  "required": ["document_type", "sources_available", "verification_tier", "domain", "flag_threshold"],
  "properties": {
    "document_type":        { "enum": ["grant","manuscript","lit_review","slides","report","memo","other"] },
    "document_type_other":  { "type": "string" },                                // required iff document_type == "other"
    "sources_available":    { "enum": ["uploaded_files","bibliography_only","none"] },
    "verification_tier":    { "enum": ["1","2","3","custom"] },
    "checks_enabled":       { "type": "array", "items": { "enum": [
                              "citation_existence","claim_alignment","uncited_claims",
                              "exact_quotes","numerical_sanity","named_entities","internal_consistency",
                              "prose_quality_audit" ] } },
                              // required iff verification_tier == "custom"
                              // prose_quality_audit: CUSTOM only (no numbered tier auto-includes it);
                              //   parallel pipeline (style_findings[]); canonical door is /prose-audit
    "domain":               { "enum": ["biomedical","general","mixed"] },
    "flag_threshold":       { "enum": ["conservative","standard","strict"] },
    "cited_papers":         { "type": "array", "items": { "$ref": "#/$defs/citedPaper" } },  // optional — research-paper-summarizer handoff
    "pinned_sidecars":      { "$ref": "#/$defs/pinnedSidecars" }                              // optional — deep-research handoff (Stage 3 diff-mode)
  }
}
```

### Deep-research handoff (`pinned_sidecars`)

When the document under review is a markdown report produced by `deep-research`, the report carries an HTML-comment marker on its first line:

```markdown
<!-- evidence_pinned: true sidecars: sources.json,grading.json,synthesis.json,advocate.json -->
```

Detect the marker and populate `intake.pinned_sidecars` from conventional sibling filenames (do NOT prompt the user). The verifier then activates **Stage 3 diff-mode** (see SKILL.md §Stage 3 — Claim-citation alignment). The cooperation contract mirrors the existing `cited_papers[]` handoff with `research-paper-summarizer`:

- **Upstream emits paths, not inline data.** Each sidecar lives at the canonical filename `{date}_{topic_slug}_{mode}_{kind}.json` (computed via `skills/deep-research/scripts/thresholds.sidecar_filename`).
- **Schemas live with the producer.** Validate with `skills/deep-research/scripts/validate_sidecar.py --kind {sources|grading|synthesis|advocate}` before consumption. On schema failure, drop to standard alignment and append `pinned_sidecars_invalid` to `header.coverage_caveats[]`.
- **Join key:** `paper_id` (DOI-preferred, PMID fallback) is shared across all four deep-research sidecars and is byte-compatible with the verifier's `Finding.citations[].{doi,pmid}` and `cited_papers[].paper_id` fields.
- **New verdict:** drift between report claim and sidecar value emits a Stage 3 finding with verdict `METADATA_MISMATCH` and tag `drift_from_sidecar:<paper_id>`. Severity follows the existing matrix.
- **Compiler-contract violation:** if `advocate.json` contains any finding with `severity == "CRITICAL" AND status == "open"`, emit a single CRITICAL finding with tag `compiler_contract_violation` — the deep-research compiler is contracted to refuse assembly in that state, so its presence in a delivered report indicates the gate was bypassed.

**Symmetric downstream marker** (Phase 3): the verifier's `scripts/render_report.py --audit-dir <dir>` prepends an `<!-- audit_evidence_pinned: true artifacts: ... audit_dir: ... schema_version: 1.0 -->` HTML comment as the first line of the rendered `report.md`. This is the symmetric counterpart to deep-research's `<!-- evidence_pinned: true ... -->` marker: peer-review and scientific-writing detect it on intake (see their respective `SKILL.md` §Prerequisites → "Detecting research-accuracy-verifier audit markers") and populate `intake.pinned_audit_artifacts` from sibling files under `audit_dir`. The motivation is identical to the upstream direction documented above — avoid re-deriving facts that already live in pinned sidecars on disk (`document_inventory.json`, `reference_map.json`, `resolved_sources.json`, `external_evidence.json`, plus the Stage 1 `claim_inventory.json` when present). The verifier itself never re-reads its own emitted marker; the contract is strictly upstream-of-the-marker emits, downstream-of-the-marker reads.

Tier → `checks_enabled` mapping (computed when tier ≠ `custom`):
- Tier 1 → `["citation_existence"]`
- Tier 2 → `["citation_existence","claim_alignment"]`
- Tier 3 → all 7 citation/claim checks (`citation_existence`, `claim_alignment`, `uncited_claims`, `exact_quotes`, `numerical_sanity`, `named_entities`, `internal_consistency`). **`prose_quality_audit` is NOT one of them** — it is `custom`-only and never auto-included by any numbered tier.

---

## ClaimInventoryItem JSON schema (locked)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "claim_inventory_item.json",
  "required": ["id","location","claim_text","claim_type"],
  "properties": {
    "id":          { "type": "string" },                                 // UUID or "C001" sequential
    "location":    { "type": "object", "required": ["section","paragraph"],
                     "properties": { "section": {"type":"string"},
                                     "paragraph": {"type":"integer","minimum":1},
                                     "line": {"type":["integer","null"],"minimum":1} } },
    "claim_text":  { "type": "string", "minLength": 1 },                 // verbatim from document
    "claim_type":  { "enum": ["citation_bearing","direct_quote","numerical",
                              "named_entity","mechanistic","attribution","uncited"] },
    "citations":   { "type": "array", "items": { "type": "object",
                     "required": ["key","raw_text"],
                     "properties": { "key": {"type":"string"},          // "Smith2019" or "[12]"
                                     "doi": {"type":["string","null"]},
                                     "pmid": {"type":["string","null"]},
                                     "raw_text": {"type":"string"} } } }
  }
}
```

---

## Finding JSON schema (locked)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "finding.json",
  "required": ["id","location","claim_verbatim","claim_type","verification_path",
               "evidence","verdict","severity","recommended_action","confidence"],
  "properties": {
    "id":               { "type": "string" },
    "location":         { /* same shape as ClaimInventoryItem.location */ },
    "claim_verbatim":   { "type": "string", "minLength": 1 },
    "claim_type":       { "enum": [/* same as ClaimInventoryItem.claim_type */] },
    "citations":        { /* same shape as ClaimInventoryItem.citations */ },
    "verification_path":{ "type": "array", "minItems": 1, "items": { "type": "object",
                          "required": ["method","tool","result_summary"],
                          "properties": {
                            "method":         { "enum": ["doi_lookup","pmid_lookup","crossref_search",
                                                "pubmed_search","pmc_fetch","metadata_agreement",
                                                "exact_quote_match",
                                                "scite_context","web_search","abstract_check",
                                                "ref_reconcile","acronym_scan","journal_volume_check",
                                                "entity_resolve","pubtator3_entity_check"] },
                            "tool":           { "type": "string" },         // "PubMed MCP", "validate_citations.py"
                            "query":          { "type": "string" },
                            "result_summary": { "type": "string" }
                          } } },
    "evidence":         { "type": "array", "minItems": 1, "items": { "type": "object",
                          "required": ["source","url"],
                          "properties": {
                            "source":  { "type": "string" },
                            "url":     { "type": "string", "minLength": 1 },  // DOI / PMID / resolvable URL
                            "snippet": { "type": "string" }
                          } } },
    "verdict":          { "enum": ["VERIFIED","METADATA_MISMATCH","UNSUPPORTED","OVERGENERALIZED",
                                   "CONTRADICTED","MISATTRIBUTED","QUOTE_VERIFIED","QUOTE_PARAPHRASED",
                                   "QUOTE_FABRICATED","UNVERIFIED"] },
    "severity":         { "enum": ["CRITICAL","MAJOR","MINOR","INFORMATIONAL"] },
    "recommended_action": { "type": "string", "minLength": 1 },
    "confidence":       { "enum": ["high","medium","low"] },
    "reason":           { "enum": ["paywalled_full_text","preprint_not_indexed","api_timeout",
                                   "source_not_provided","tier_does_not_cover","other"] }
                                                                              // required iff verdict == "UNVERIFIED"
  }
}
```

---

## AuditReport JSON schema (locked top-level)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "audit_report.json",
  "required": ["header","executive_summary","findings","verification_matrix","methodology_note"],
  "properties": {
    "header": { "type": "object",
      "required": ["document_title","document_type","date_checked","verification_tier",
                   "sources_consulted","overall_confidence","confidence_justification","coverage_caveats"],
      "properties": {
        "document_title":          { "type": "string" },
        "document_type":           { "enum": [/* DocType */] },
        "date_checked":            { "type": "string", "format": "date" },
        "verification_tier":       { "enum": ["1","2","3","custom"] },
        "sources_consulted":       { "type": "array", "items": {"type":"string"} },
        "overall_confidence":      { "enum": ["high","moderate","low","very_low"] },
        "confidence_justification":{ "type": "string", "minLength": 1 },
        "coverage_caveats":        { "type": "array", "items": {"type":"string"} } } },
    "executive_summary":  { "type": "string", "minLength": 100 },          // 3–5 sentences
    "findings":           { "type": "array", "items": { "$ref": "finding.json" } },
    "verification_matrix":{ "type": "array", "items": { "type": "object",
                            "required": ["claim_id","verdict","severity","stage"],
                            "properties": {
                              "claim_id": {"type":"string"},
                              "verdict":  {"enum": [/* Verdict */]},
                              "severity": {"enum": [/* Severity */]},
                              "stage":    {"enum": ["2","3","4","5","6","7"]} } } },
    "methodology_note":   { "type": "string", "minLength": 1 }
  }
}
```

---

## Severity matrix as machine-readable JSON

`schemas/severity_matrix.json` (Phase 3) encodes the matrix as:

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "severity_matrix.json",
  "title": "SeverityMatrix",
  "description": "Verdict × DocumentType → Severity. Computed in validate_finding.py.",
  "type": "object",
  "required": ["matrix"],
  "properties": {
    "matrix": {
      "type": "object",
      "patternProperties": {
        "^(grant|manuscript|lit_review|slides|report|memo|other)$": {
          "type": "object",
          "patternProperties": {
            "^(VERIFIED|METADATA_MISMATCH|UNSUPPORTED|OVERGENERALIZED|CONTRADICTED|MISATTRIBUTED|QUOTE_VERIFIED|QUOTE_PARAPHRASED|QUOTE_FABRICATED|UNVERIFIED)$": {
              "enum": ["CRITICAL","MAJOR","MINOR","INFORMATIONAL"]
            }
          }
        }
      }
    }
  }
}
```

Plus a separate `severity_matrix.values.json` data file containing the actual cell values from the table above. Scripts read `.values.json`, not the schema.

---

## Resume artifacts (stage-boundary checkpoints)

Long Tier-3 audits can exhaust the context window mid-pipeline. To make audits resumable across sessions, every stage persists its output to a deterministic per-document directory:

```
research/audits/<slug>/
  claim_inventory.json     # Stage 1 output ({"items": [ClaimInventoryItem, ...]})
  02_existence.json        # Stage 2: { stage, findings[], matrix_delta[], written_at, ... }
  03_alignment.json        # Stage 3
  04_uncited.json          # Stage 4
  05_quotes.json           # Stage 5
  06_sanity.json           # Stage 6
  07_consistency.json      # Stage 7
  audit_report.json        # Final assembled report (Stage 8)
```

`<slug>` is `slugify(document_title)` per `scripts/checkpoint.py`: lowercase alnum + single hyphens, trimmed, max 60 chars, falls back to `untitled`.

**No new schemas.** Stages 2–7 artifacts contain `findings[]` (validated against `finding.json` via `FindingValidator` before write) and `matrix_delta[]` (entries with the same shape as `audit_report.json`'s `verification_matrix[]` items). Stage 1's artifact matches the locked `schemas/claim_inventory.json` wrapper shape `{"items": [ClaimInventoryItem, ...]}` — `checkpoint.write_stage_artifact()` rejects anything else.

Stage 0 (resume detection) reads this directory contiguously: the first missing `0N_<stage>.json` stops the scan and becomes `next_stage`. A gap forces re-running the missing stage. Deleting the directory restarts a fresh audit.

The final `audit_report.json` is also written here, replacing the historical "anywhere on disk" assumption — Stage 8 still validates against `audit_report.json` schema.

---

## What is NOT in Phase-1 contracts (intentionally deferred)

- Per-domain (biomedical vs general) routing rules — live in SKILL.md prose + `shared/tool-lookup.yaml` capability keys
- Oligon-brand HTML rendering shape (markdown only in v1.2)
- Annotated PDF inline-comment shape (out of scope)
- Confidence calibration math (Bayesian re-scoring) — future
- Live MCP tool wiring for Stage 4 uncited-claim search — capability keys declared, live calls deferred to v1.3

---

## STYLE_NONCONFORMING verdict family (added v1.3, prose-standards integration)

A separate verdict family for prose-quality violations. **Operates on a parallel pipeline** to the citation/claim verdicts above — does NOT enter the 10-value Verdict enum or the 70-cell Severity matrix; uses its own `style_findings[]` array in the AuditReport when the verifier is run with `checks_enabled` including `prose_quality_audit` (**`custom` tier only** — no numbered tier auto-includes it; canonical entry point is the `/prose-audit` command).

**Source of truth for thresholds:** `../shared/references/prose_standards_thresholds.yaml`. The verifier loads this YAML at startup and uses its severity tags directly (no separate severity matrix — a YAML-tagged CRITICAL is CRITICAL regardless of document type, because prose-standard violations are not document-type-conditional in the way citation errors are).

### Verdict subtypes (10 values, mirrored from YAML rule IDs)

| Verdict | Source rule | Severity (default) | Meaning |
|---|---|---|---|
| `STYLE_PASSIVE_OVERUSE` | V1 (Pass 2) | MAJOR | Passive-voice ratio >25% outside Methods (>50% inside Methods) |
| `STYLE_NOMINALIZATION` | S4 (Pass 2) | MAJOR | Nominalization patterns ("perform an X of," "conduct an X of") detected |
| `STYLE_BURIED_PREDICATE` | S6 (Pass 3) | MAJOR | Subject-to-main-verb gap >12 words |
| `STYLE_LONG_SENTENCE` | S2 (Pass 3) | MAJOR | Sentence >25 words |
| `STYLE_BANANA_VIOLATION` | W6 (Pass 5) | CRITICAL | Synonym substitution for an established term-of-art |
| `STYLE_TORTURED_PHRASE` | AI8 (Pass 5) | CRITICAL | Algorithmic synonym substitution producing unfamiliar substitute for term-of-art |
| `STYLE_AI_TELL` | AI1–AI7 (Pass 9) | MAJOR (AI8 → CRITICAL) | One of the AI-writing-tells blacklist patterns matched |
| `STYLE_NUMERICAL_INCONSISTENCY` | Q5 / R5 (Pass 6, Pass 10) | CRITICAL | Numbers in Abstract ≠ Results ≠ Tables ≠ Figure legends |
| `STYLE_THROAT_CLEARING` | S1 / AI5 (Pass 1) | MAJOR | One of the throat-clearing patterns matched |
| `STYLE_ORPHAN_STATISTIC` | Q2b (Pass 6) | MAJOR | *p*-value with no effect size, CI, or direction-of-effect |

### StyleFinding shape (separate from Finding)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "style_finding.json",
  "required": ["id","location","original_text","verdict","severity","rule_id","suggested_revision","source_section"],
  "properties": {
    "id":                  { "type": "string" },                          // "S001" sequential
    "location":            { /* same shape as ClaimInventoryItem.location */ },
    "original_text":       { "type": "string", "minLength": 1 },
    "verdict":             { "enum": ["STYLE_PASSIVE_OVERUSE","STYLE_NOMINALIZATION","STYLE_BURIED_PREDICATE",
                                       "STYLE_LONG_SENTENCE","STYLE_BANANA_VIOLATION","STYLE_TORTURED_PHRASE",
                                       "STYLE_AI_TELL","STYLE_NUMERICAL_INCONSISTENCY","STYLE_THROAT_CLEARING",
                                       "STYLE_ORPHAN_STATISTIC"] },
    "severity":            { "enum": ["CRITICAL","MAJOR","MINOR","INFORMATIONAL"] },
    "rule_id":             { "type": "string" },                          // "V1", "S6", "W6", "AI8", "Q5"
    "suggested_revision":  { "type": "string" },
    "source_section":      { "type": "string" },                          // "Abstract", "Introduction", etc.
    "blacklist_match":     { "type": "string" }                           // optional: which keyword/regex matched (for AI-tells)
  }
}
```

### AuditReport extension

`audit_report.json` gains an optional `style_findings[]` array (alongside `findings[]` for citation-claim verdicts). Empty array if `prose_quality_audit` is not in `checks_enabled`. The `executive_summary` includes a one-line style summary if any STYLE_* verdict is CRITICAL.

### Output format (mirrors prose_standards.md §12)

Every style finding MUST report: original_text, suggested_revision, rule_id, severity. **No silent rewrites** — verifier surfaces every change as a finding for author review.

### Hard predicates for style findings

S-P1. `severity == CRITICAL ⟹ rule_id ∈ {W6, AI8, Q5, R5}` (only the canonical CRITICAL rules can produce CRITICAL style findings)
S-P2. `verdict matches its rule_id family` (e.g., `STYLE_BANANA_VIOLATION` only with `rule_id == "W6"`)
S-P3. `style findings load thresholds from prose_standards_thresholds.yaml` — verifier MUST refuse to run prose_quality_audit if YAML is missing or schema-invalid

### What is intentionally OUT of style_findings

- Subjective stylistic critique not tied to a numbered rule in `prose_standards.md` — those belong in human peer review (`peer-review` skill), not a deterministic verifier.
- Voice/tone judgments below MAJOR severity — keep verifier output actionable.
- Banana-rule false positives where the substitution is explicitly defined in the document (e.g., "the obese group (BMI ≥ 30, hereafter Group A)") — verifier must respect explicit synonym definitions.

---

## FIGURE_INTEGRITY verdict family (added v1.8, AI-figure-slop integration)

A separate verdict family for **inbound third-party figure-integrity audits**
(a figure the user hands us, not one this plugin generated). **Operates on a
parallel pipeline** to the citation/claim verdicts — does NOT enter the 10-value
Verdict enum or the 70-cell Severity matrix; uses its own `figure_findings[]`
array in the AuditReport when the verifier is run with `checks_enabled`
including `figure_integrity_audit` (**`custom` tier only** — no numbered tier
auto-includes it). Same architectural posture as STYLE_NONCONFORMING.

**Advisory/triage only, never dispositive.** A clean audit is "no positive
evidence of AI authorship," never proof of human authorship; the burden it
supports is "obtain source data / provenance," never "conclude misconduct."
Adjudication stays human (FD-P4 enforces this on `recommended_action`).

**Source of truth for the rubric:** `references/figure_integrity_audit.md`
(6 dimensions, 0/1/2 anchors, 5 categorical ⚑ metrics {1.1,1.2,2.1,2.2,3.1}).
The rubric is **PROVISIONAL/UNCALIBRATED**. Why this family is not the citation
enum: a figure audit asserts a property of an *image* (a pixel region with no
DOI/PMID), so it cannot satisfy P3, and forcing `CONTRADICTED`/`UNSUPPORTED`
onto pixel observations would be a category error.

### Audit-level verdicts (3 values — NOT the citation enum)

| Verdict | Trigger |
|---|---|
| `FIGURE_INTEGRITY_FLAG` | any ⚑ metric = 2 OR any Tier-1 deterministic hard mismatch |
| `FIGURE_REVIEW_RECOMMENDED` | converging soft signals, no ⚑=2 |
| `FIGURE_NO_POSITIVE_EVIDENCE` | clean |

### FigureAuditFinding shape (separate from Finding)

Schema: `schemas/figure_audit_finding.json`. Per-metric severity uses the shared
`{CRITICAL,MAJOR,MINOR,INFORMATIONAL}` but is assigned by the rubric's explicit
table (⚑=2 → CRITICAL; non-⚑ score 2 → MAJOR; score 1 → MINOR; D4/D6 ≤ MINOR),
NOT computed from the severity matrix.

### AuditReport extension

`audit_report.json` gains an optional `figure_findings[]` array (alongside
`findings[]` and `style_findings[]`). Empty array if `figure_integrity_audit` is
not in `checks_enabled`.

### Hard predicates for figure findings (FD-P1..FD-P7)

Enforced by `scripts/validate_figure_finding.py` (FD-P1..FD-P6 per-finding;
FD-P7 audit-level in `validate_audit_verdict()`). Full statements in
`predicates.md`. They encode the two guardrails: categorical tells dominate
(FD-P1/P2/P7), aesthetic D6 is weak/two-sided (FD-P3), framing stays advisory
(FD-P4), decaying signals carry their caveat (FD-P5), deterministic findings
name their linter (FD-P6).

### Tier plan

Tier 1 (deterministic, `scripts/figure_axis_lint.py`, reuses the Track-B
linters; only when the user supplies machine-readable source) + Tier 3
(instrumented vision-judge) ship now. Tier 2 (CV) deferred. An "AI-generated"
classifier is **never** built and never gates (SciFigDetect: detectors fail
zero-shot).

---

## Validator pattern reminder

All validators in `scripts/validate_*.py` MUST use the **2-stage continue-on-failure** pattern:

```python
def validate(self, data) -> tuple[bool, list[str], list[str]]:
    errors, warnings = [], []
    # Stage 1: schema — DO NOT return early on failure
    for e in Draft7Validator(self.schema).iter_errors(data):
        errors.append(_format_error(e))
    # Stage 2: business rules — run regardless
    self._check_predicates(data, errors, warnings)
    return (len(errors) == 0, errors, warnings)
```

Pattern model: `skills/scientific-slides/scripts/validate_slide_plan.py` AFTER the Apr-22 fix (the version on `master` short-circuits at line 106 — do **not** copy that). The fix lives on the migrate branch; replicate the *intent*, not the master implementation.

---

## Dry-run validation (Phase 3 enforcement-flip prerequisite)

An end-to-end dry-run of Phases 1+2 on a real audit, plus a perturbation matrix confirming each R-predicate fires exactly when its invariant is broken, is the prerequisite for flipping `ARTIFACT_ENFORCEMENT` from `"advisory"` to `"required"`. The dry-run spec (§7.3 audit-selection prerequisite + §11.2 perturbation matrix) lives in the project plan `~/.claude/plans/let-s-put-together-a-mellow-bumblebee.md` (user-scoped, outside the repo); for in-repo Phase 1+2 history see `EVIDENCE_PINNING_DECISIONS.md` at the repo root.

### Audit under test

- **Audit:** `research/audits/06_lit_review_cited_paper_numerical/`
- **Document:** `regression/docs/06_lit_review_cited_paper_numerical.md` (lit review excerpt; one cited paper — fixture DOI `10.0001/jtor.fixture.smith2024`)
- **Driver:** `scratch/dry_run_perturbations.py` (run with `uv run python scratch/dry_run_perturbations.py` from the verifier root)
- **Dry-run date:** 2026-05-18

### Phase 1+2 artifacts back-generated for the dry-run

Audit 06 was produced before Phases 1+2 shipped, so artifacts were back-generated from existing stage JSONs to reach the Phase-2 expected state. Each artifact validates clean against its schema + predicates.

| Artifact | Origin |
|---|---|
| `document_inventory.json` | `parse_document.py --document <doc> --slug ... --document-type lit_review` (parser baseline; no overrides needed) |
| `reference_map.json` | Manually backfilled — the document uses `(Smith 2024)` without the comma required by `extract_reference_map.py`'s author-year regex, so the parser baseline contained zero citations. In a live audit, the LLM patches this; here we mirror that patch (one citation `Smith 2024` keyed to paper_id `10.0001/jtor.fixture.smith2024` with 3 inline occurrences). |
| `resolved_sources.json` | Synthesized from `regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_source_meta.json` + Stage 2 `VERIFIED` outcome via `intake.cited_papers source_meta.json` resolution path. |
| `external_evidence.json` | Initialized empty — audit 06 used only user-provided sources (`abstract_check`, `doi_lookup`, `ref_reconcile`); no Scite or PubTator3 probes. R5 passes vacuously. |
| `intake.json` | Created: `lit_review`, `uploaded_files`, tier `3`, `biomedical`, `standard` flag threshold. |

### Baseline result

```
R1: pass  R2: pass  R3: pass  R4: pass  R5: pass  R6: pass
P8: fail  (pre-existing; orthogonal to evidence pinning)
```

R1–R6 all pass — the Phase 3 enforcement flip can proceed without breaking this audit's R-predicate posture.

P8 failure is a **pre-existing** issue with audit 06 unrelated to evidence pinning: the audit lacks Stage-4 cherry-picking probes (`OVERGENERALIZED` with `scite_context` method) that P8 requires for every Stage-3 `VERIFIED` `citation_bearing` claim in biomedical tier-3 audits. This is a known gap in the audit itself, not a regression introduced by Phase 1+2.

### Perturbation matrix outcomes

Each mutation applied to a fresh temp copy of the audit; validator re-run with all artifacts; exactly one expected R-predicate fires per mutation, no cross-contamination.

| ID | Mutation | Expected fail | Actual fail | OK |
|---|---|---|---|---|
| P1 | Drop `Smith 2024` from `reference_map.citations[]` | R3 | R3 | ✓ |
| P2 | Mutate `resolved_sources.sources[0].paper_id` (+ backfill C001 `evidence[0].paper_id` first to lift to Phase-2 state) | R2 | R2 | ✓ |
| P3 | Replace C001 `claim_verbatim` with text not in the paragraph | R4 | R4 | ✓ |
| P4 | Augment C001 `verification_path[]` with a `scite_context` step + matching `evidence[].paper_id`, then leave the ledger empty | R5 | R5 | ✓ |
| P5 | Delete `C001` from `claim_inventory.items[]` | R1, R6 | R1, R6 | ✓ |
| P6 | Drop section `S002` (and its paragraphs) from `document_inventory.json` | R4 | R4 | ✓ |

**Result: MATRIX OK.** All six perturbations produce the expected R-predicate failure and only the expected failure.

### Notes for future re-runs

- P2 + P4 each apply a small audit-side augmentation before the perturbation, because audit 06 predates Phase 2 (null `evidence[].paper_id` throughout, no ledger-routed verification methods). Future audits produced under Phase 1+2 will not need these augmentations.
- The augmentations live only in the temp copy created by the driver; `research/audits/06_lit_review_cited_paper_numerical/` on disk is untouched by the perturbation runs.
- The driver script is self-contained at `scratch/dry_run_perturbations.py`. To re-run after any validator/schema change, simply execute it; non-zero exit means a perturbation diverged from the expected R-pattern.

### Phase 3 gate verdict

R1–R6 baseline pass + 6/6 perturbations fire exactly as specified ⇒ Phase 3 enforcement flip (`ARTIFACT_ENFORCEMENT = "required"`) is **unblocked** from the §7.3 prerequisite. Outstanding Phase 3 work per plan §7.1–7.5: marker on rendered report, CLI `--no-enforce-artifacts` escape hatch, `validate_audit_report.py` enforcement-mode behavior, `checkpoint.py` stage-8 gate, `README_migration.md`, and unit tests.

### Flip shipped — 2026-05-18

`ARTIFACT_ENFORCEMENT = "required"` shipped in the Phase 3 commit on 2026-05-18 (see CHANGELOG). Behavioral changes summarized:

- `validate_audit_report.py`: R-predicate failures AND missing-artifact "skipped" messages now land in `errors` (`ok=False`). Both `--no-enforce-artifacts` CLI flag and `enforcement="advisory"` kwarg force a single-run downgrade for migration scenarios.
- `render_report.py`: new `--audit-dir` CLI flag (and `artifact_paths` + `audit_dir` + `enforcement` kwargs on `generate_report()`). When supplied, prepends the `<!-- audit_evidence_pinned: true ... -->` marker as the first line. In required mode, refuses to render when the artifact set is incomplete.
- `checkpoint.finalize_audit(slug, *, audits_root, enforcement="auto")`: new pre-render gate — validates the 4-artifact set against schemas + predicates via `validate_artifact.validate_artifact(kind, path)`. Raises `ValueError` in required mode when incomplete or invalid. Library-only this phase.
- `scripts/thresholds.ARTIFACT_ENFORCEMENT` constant flipped from `"advisory"` to `"required"`.
- Test infrastructure: `tests/conftest.py` autouse fixture pins the constant to `"advisory"` for legacy tests; new required-mode tests pass `enforcement="required"` explicitly.

Migration guidance for in-flight pre-flip audits lives in `references/README_migration.md`.
