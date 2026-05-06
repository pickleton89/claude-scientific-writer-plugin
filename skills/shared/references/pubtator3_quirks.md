# PubTator3 API quirks

Companion to `known_param_corrections.md` (which is reserved for ToolUniverse).
Captures NCBI PubTator3 REST conventions that aren't obvious from a casual read
of the JSON. Wrapper at `skills/shared/scripts/pubtator3.py`.

Base URL: `https://www.ncbi.nlm.nih.gov/research/pubtator3-api`
Auth: none. Rate limit: ~20 req/s (wrapper enforces 50 ms throttle + Retry-After-aware retry).

---

## Entity ID format

Entity IDs use a **symbol-based prefix scheme**, not the underlying database ID:

| Concept | Format | Example | NCBI ID location |
|---|---|---|---|
| gene | `@GENE_<symbol>` | `@GENE_BRAF` | `db_id` (e.g. `673`) |
| disease | `@DISEASE_<MeSH-or-name>` | `@DISEASE_Melanoma` | `db_id` (e.g. `MESH:D008545`) |
| chemical | `@CHEMICAL_<name>` | `@CHEMICAL_vemurafenib` | `db_id` (MeSH or CHEBI) |
| variant | `@VARIANT_<HGVS_gene_species>` | `@VARIANT_p.V600E_BRAF_human` | `db_id` (rsID) |
| species | `@SPECIES_<TaxID-or-name>` | `@SPECIES_9606` | `db_id` |

**Implication:** numeric NCBI IDs (e.g. `Entrez 673`) are NOT valid in `text=`
queries or relations endpoints — use the `@<TYPE>_<symbol>` form returned by
`autocomplete`. When in doubt, autocomplete first.

---

## Search (`/search/`)

- Param is **`size`**, not `limit`. Default 10. Pagination uses 1-indexed `page`.
- Query syntax in `text=`: entity tokens joined with `AND` (spaces preserved).
  Free text is allowed alongside entity tokens. Example:
  `text=@GENE_BRAF AND @DISEASE_Melanoma AND resistance`
- Response shape: `{results, facets, page_size, current, count, total_pages}`.
  Facets give free journal/type/year breakdowns — useful for trend charts without
  extra calls.
- `text_hl` field on each result contains entity-annotated highlighted snippets
  using `@<m>GENE_X</m>` markers. Strip with regex if you want plain text.

---

## Annotations (`/publications/export/biocjson`)

- **PMIDs comma-separated** in `pmids=` query param. Empty / unknown ID returns
  HTTP 400 (`{"detail": "Could not retrieve publications"}`), not 404 or empty array.
- Add `full=true` to include full text where PMC has it.
- Response shape: `{PubTator3: [{passages: [...], pmid, ...}]}` — one document
  per PMID. Each `passage` has its own `annotations` and `relations`.
- Annotation shape per item:
  ```json
  {
    "id": "5",
    "infons": {
      "type": "Disease", "biotype": "disease",
      "identifier": "MESH:D009369", "accession": "@DISEASE_Neoplasms",
      "name": "Neoplasms", "normalized_id": "D009369"
    },
    "text": "cancer",
    "locations": [{"offset": 23, "length": 6}]
  }
  ```
  The `accession` field carries the PubTator3 entity ID (`@<TYPE>_<X>`) — that's
  what the verifier should match claims against, not the surface text.
- An annotation absent from BioC-JSON does **not** prove the entity isn't in the
  paper — PubTator3's NER has known gaps for newer papers. Treat absence as
  "candidate MISATTRIBUTED, escalate to full-text" rather than a hard verdict.

---

## Relations (`/relations`)

- Required: `e1=<entity_id>`. Optional: `type=<relation>` and `e2=<entity_id>`.
- **Type filter is restrictive** — empirically `type=treat` returns `[]` for many
  entities even when relations exist. **Default to omitting `type`** and filter
  client-side. Wrapper's `--summary` groups by type for convenience.
- Response: flat array of `{type, source, target, publications}`. The
  `publications` field is the co-mention count — useful as a co-mention strength
  signal.
- Common relation types: `associate`, `negative_correlate`, `positive_correlate`,
  `treat`, `cause`, `inhibit`, `stimulate`, `interact`, `compare`. List is not
  exhaustive — accept anything.

---

## Autocomplete (`/entity/autocomplete/`)

- Required: `query=<text>`. Optional: `concept=` (one of `gene`, `disease`,
  `chemical`, `variant`, `species`) and `limit=N`.
- Returns up to `limit` candidates ranked by match score. Each candidate has
  `_id` (PubTator3 entity ID), `biotype`, `db_id`, `db`, `name`, `description`,
  `match` (HTML snippet showing why it matched).
- **Disambiguation signal:** if `query="ACE"` (no `concept`) returns >1 candidate
  type (e.g. both `@GENE_ACE` and `@CHEMICAL_acetylcholine`), that's a high-risk
  collision. Escalate to manual disambiguation in entity-resolution Stage 4.
- Synonym matches are flagged via `match: "Matched on synonyms <m>...</m>"` —
  treat synonym hits with lower confidence than `Matched on name`.

---

## Error handling

| HTTP | Meaning | Wrapper behavior |
|---|---|---|
| 200 | OK | parse JSON |
| 400 | Bad request (e.g. invalid PMID) | raise `PubTator3Error(400, ...)` — do NOT retry |
| 429 | Rate-limited | retry up to 3× honoring `Retry-After` |
| 5xx | Transient | retry up to 3× with backoff |

---

## Wrapper conventions

- All subcommands emit JSON to stdout, exit 0 success / 1 input error / 2 remote.
- `--summary` flag on `search`, `annotations`, `relations` returns a token-cheap
  view (counts + top-N) suitable for LLM context. Omit for full payload.
- `compose_search_text` auto-tags bare symbols (`BRAF` → `@GENE_BRAF`) so callers
  don't need to manually prefix common cases.
