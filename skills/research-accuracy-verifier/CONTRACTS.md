# Locked Contracts — research-accuracy-verifier

Single source of truth for the Verdict enum, Document Type enum, Severity matrix, and JSON schema shapes consumed by every downstream component (SKILL.md prose, JSON schemas in `schemas/`, validators in `scripts/`, router triggers, tests). Changes here cascade — modify with intent.

Phase 1 deliverable. Phase 2 (SKILL.md refactor), Phase 3 (schemas), Phase 4 (scripts), Phase 5 (tests) all consume this file.

---

## Verdict enum (10 values)

The canonical vocabulary used by every stage. No stage may invent a parallel verdict.

| Verdict | Origin stage | Meaning |
|---|---|---|
| `VERIFIED` | 2 | Citation exists; all metadata fields agree |
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

## Hard predicates (enforced by `validate_finding.py`)

P1. `verdict == UNVERIFIED ⟹ reason ∈ Reason AND severity != CRITICAL`
P2. `severity == CRITICAL ⟹ len(verification_path) >= 2`
P3. `len(evidence) >= 1 AND every evidence entry has a resolvable URL / PMID / DOI`
P4. `verdict ∈ {QUOTE_VERIFIED, QUOTE_PARAPHRASED, QUOTE_FABRICATED} ⟺ claim_type == "direct_quote"`
P5. `severity == SeverityMatrix[document_type][verdict]` — severity is **computed**, not user-supplied; validator rejects mismatches
P6 (advisory, not code-enforced). Verdict glyphs (✅⚠️❌❓) MUST NOT appear as verdict markers in any rendered AuditReport, finding table, or schema enum. Severity is rendered as text. Glyphs may appear in `SKILL.md` / `CONTRACTS.md` only as documentation that they are deprecated. P1–P5 are the hard predicates enforced by `validate_finding.py`.

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
                              // prose_quality_audit: Tier 3 + custom only; parallel pipeline (style_findings[])
    "domain":               { "enum": ["biomedical","general","mixed"] },
    "flag_threshold":       { "enum": ["conservative","standard","strict"] }
  }
}
```

Tier → `checks_enabled` mapping (computed when tier ≠ `custom`):
- Tier 1 → `["citation_existence"]`
- Tier 2 → `["citation_existence","claim_alignment"]`
- Tier 3 → all 7 checks

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
                                                "pubmed_search","pmc_fetch","exact_quote_match",
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

A separate verdict family for prose-quality violations. **Operates on a parallel pipeline** to the citation/claim verdicts above — does NOT enter the 10-value Verdict enum or the 70-cell Severity matrix; uses its own `style_findings[]` array in the AuditReport when the verifier is run with `checks_enabled` including `prose_quality_audit` (Tier 3 + custom only).

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
