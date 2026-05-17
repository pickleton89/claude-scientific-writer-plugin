# Stage 1 — Document parsing and claim extraction

**Purpose:** Build a `ClaimInventory` validated against [`schemas/claim_inventory.json`](../../schemas/claim_inventory.json).

For each item record `id`, `location {section, paragraph, line}`, `claim_text` (verbatim), `claim_type`, and `citations[]`.

**Claim type categories:**

- **citation_bearing** — any sentence with an inline citation, footnote, or reference marker
- **direct_quote** — text inside quotation marks attributed to a person or source
- **numerical** — percentages, p-values, sample sizes, effect sizes, doses, kinetic parameters (Kd, IC50, EC50), sequence lengths, gene / protein counts, dates
- **named_entity** — gene / protein symbols, drug names (generic and brand), cell lines, antibody clones, mouse strains, instrument models, software versions
- **mechanistic** — causal or mechanistic statements ("X activates Y", "mutation in A causes B")
- **attribution** — "Smith et al. showed…", "the Anderson lab demonstrated…"
- **uncited** — empirical statements with no citation

**Bipartite map:** build a claim ↔ citation map — each claim links to zero, one, or many citations; each citation links to all claims it nominally supports.

**On stage completion:** call `checkpoint.py write --slug <slug> --stage 1 --claim-inventory <path> --document-type <type>` to persist the inventory.

**Artifact:** `research/audits/<slug>/claim_inventory.json`.
