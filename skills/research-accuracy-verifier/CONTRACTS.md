# Locked Contracts — research-accuracy-verifier

Single source of truth for the Verdict enum, Document Type enum, Severity matrix, and JSON schema shapes consumed by every downstream component (SKILL.md prose, JSON schemas in `schemas/`, validators in `scripts/`, router triggers, tests). Changes here cascade — modify with intent.

Phase 1 deliverable. Phase 2 (SKILL.md refactor), Phase 3 (schemas), Phase 4 (scripts), Phase 5 (tests) all consume this file.

---

## Verdict enum (10 values)

The canonical vocabulary used by every stage. No stage may invent a parallel verdict.

| Verdict | Origin stage | Meaning |
|---|---|---|
| `VERIFIED` | 2 | Citation exists; all metadata fields agree |
| `METADATA_MISMATCH` | 2 | Citation exists; ≥1 field disagrees (year, journal, volume, pages, authors) |
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
                              "exact_quotes","numerical_sanity","named_entities","internal_consistency" ] } },
                              // required iff verification_tier == "custom"
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
                                                "entity_resolve"] },
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

## What is NOT in Phase-1 contracts (intentionally deferred)

- Per-domain (biomedical vs general) routing rules — live in SKILL.md prose + `shared/tool-lookup.yaml` capability keys
- Oligon-brand HTML rendering shape (markdown only in v1.2)
- Annotated PDF inline-comment shape (out of scope)
- Confidence calibration math (Bayesian re-scoring) — future
- Live MCP tool wiring for Stage 4 uncited-claim search — capability keys declared, live calls deferred to v1.3

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
