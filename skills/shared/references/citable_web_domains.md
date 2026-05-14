# Citable Web Domains — Trust Tiers for Grey-Lit and Verifier Web Evidence

> **Scope.** This document defines which web domains can ground a verdict in `research-accuracy-verifier`, and which can enter the bibliography of `deep-research` as `[Grey Lit]` entries. It exists because the deep-research Search Contract and the verifier's web fallback both need a defensible answer to "which web sources are citable?" without a peer-review proxy.
>
> **What this is not.** A peer-review substitute. A quality ranking of the underlying content. A statement that everything from a W1 domain is correct. The tier mapping is a **trust floor** — the floor a source must clear before it can ground a verified claim, not a guarantee about that source's accuracy.
>
> **Citation rules that still apply** — see [`../../scientific-writing/references/citation_styles.md`](../../scientific-writing/references/citation_styles.md) § *Citation Integrity Rules (TWS C1–C5)* for the canonical rules. In particular:
>
> - **C4 (cross-reference integrity, CRITICAL)** — every web URL cited in the text must appear in the reference list and resolve at audit time. URL drift is a C4 violation.
> - **C2 (primary research)** — web evidence is acceptable when the page IS the primary source (e.g., the FDA approval letter itself), not when it summarizes one (e.g., a news article reporting on the FDA letter).

## How the tiers are used

| Channel | What W1 can do | What W2 can do | What W3 can do |
|---|---|---|---|
| `research-accuracy-verifier` — Stage 2/3 web-slot | Ground `VERIFIED` directly | Ground `VERIFIED` with `result_summary` tag `"per society/repository source"` | Context-only; can support `UNVERIFIED` (`reason: web_evidence_uncitable_tier`) or `OVERGENERALIZED`. **Cannot** ground `VERIFIED` on its own. `.edu` is the exception — treated like W2. |
| `deep-research` — WebSemantic bibliography | Bibliography entry, tag `[Grey Lit]` | Bibliography entry, tag `[Grey Lit]` | **Not** a bibliography entry. Enters the report narrative tagged `[Context]` only. `.edu` is the exception — treated like W2. |
| Out-of-whitelist | Dropped from bibliography; cannot ground any verdict | — | — |

Both channels MUST capture a `fetched_at` ISO-8601 timestamp in the Search Log / `verification_path[].result_summary`. Resolvability of the URL at audit time is a C4 requirement.

## Tier W1 — Regulatory authorities & registries

Primary-source pages from regulators, public-health authorities, and trial/protocol registries. The page itself is the authoritative record of the event being cited.

- `fda.gov` — FDA approval letters, drug labels, safety alerts, advisory committee briefing docs, 510(k) summaries, MAUDE reports
- `ema.europa.eu` — EMA assessment reports (EPARs), CHMP opinions, referral procedures, PRAC recommendations
- `who.int` — WHO guidelines, technical reports, ICTRP registry entries
- `nih.gov` — NIH funding announcements (RFAs/PAs), program announcements, RePORTER grant pages
- `nice.org.uk` — NICE technology appraisals, clinical guidelines, evidence reviews
- `clinicaltrials.gov` — Trial protocol pages, results modules, posted study documents
- `mhra.gov.uk` — MHRA drug alerts, yellow-card summaries, MD&IVD safety bulletins
- `cdc.gov` — CDC MMWR reports, surveillance summaries, ACIP recommendations
- `ec.europa.eu` — Commission decisions on EMA recommendations, EU pharmacovigilance bulletins
- `prospero.crd.york.ac.uk` — PROSPERO systematic-review protocol registrations

**Grounding rules.** A W1 URL can ground `VERIFIED` directly. `verification_path[]` entry shape (verifier):

```json
{
  "method": "web_search",
  "tool": "mcp__exa__web_search_exa",
  "result_summary": "FDA approval letter for aducanumab; no_doi available for Scite retraction probe; URL=https://www.fda.gov/...; fetched_at=2026-05-14T16:22:18Z"
}
```

The literal token `no_doi` is required by the P7 carve-out in `validate_finding.py`.

## Tier W2 — Professional societies & open repositories

Society sites that publish their own statements, position papers, conference abstracts, and proceedings; reputable open repositories where the deposit itself is the primary record.

**Societies (selection — not exhaustive):**

- `acs.org` — American Chemical Society
- `asco.org` — American Society of Clinical Oncology (includes ASCO Meeting Library abstracts)
- `aacr.org` — American Association for Cancer Research
- `esmo.org` — European Society for Medical Oncology
- `hematology.org` — American Society of Hematology (ASH)
- `ash.confex.com` — ASH annual meeting abstracts
- `cell.com/.../conference-coverage` — Cell Press conference summaries (treat as W2 when the page is the abstract record itself)
- `ahajournals.org/conferences` — American Heart Association conference proceedings
- `idsociety.org` — Infectious Diseases Society of America

**Open repositories & preregistration:**

- `zenodo.org` — Zenodo deposits (datasets, code, posters, preprint variants)
- `figshare.com` — Figshare deposits
- `osf.io` — Open Science Framework registrations, preregistrations, project pages
- `protocols.io` — Method/protocol depositions (peer-curated by community)
- `dataverse.harvard.edu` — Harvard Dataverse research deposits

**Grounding rules.** A W2 URL can ground `VERIFIED` provided the `result_summary` carries the tag `per society/repository source` so the audit trail signals the non-peer-reviewed provenance. Example:

```json
{
  "method": "web_search",
  "tool": "mcp__exa__web_search_exa",
  "result_summary": "ASH 2024 abstract LBA-3 [per society/repository source]; no_doi available; URL=https://ash.confex.com/...; fetched_at=2026-05-14T16:24:02Z"
}
```

## Tier W3 — Academic institutions & curated media

Two sub-classes with different rules.

**W3a — `*.edu` wildcard subset (academic institution pages).** Lab pages, department pages, dissertation deposits, technical reports hosted on `.edu` domains. **Treated like W2** for grounding purposes — can support `VERIFIED` with the `per society/repository source` tag (or a more specific `per institutional source` tag). The `.edu` TLD is a usable trust signal because it requires US-accredited-institution affiliation.

**W3b — Curated biomedical journalism (journal news desks + independent outlets).** News and editorial content from major scientific publishers, plus established independent biomedical/biotech news outlets. **Context-only** — cannot ground `VERIFIED` on its own, but can support `UNVERIFIED` (with `reason: web_evidence_uncitable_tier`) or `OVERGENERALIZED` as supporting context. The underlying primary source (the paper being reported on, the FDA letter being summarized) should be located and cited instead. W3b content in the bibliography is a flag for the user to upgrade the citation.

Recognised W3b sources:

*Publisher news desks:*

- `nature.com/articles/d41586-*` and `nature.com/news` — Nature news desk
- `science.org/news` and `science.org/content/article/news-*` — Science magazine news
- `nejm.org/.../journal-watch` and NEJM editorial pages
- `thelancet.com/journals/lancet/article/...?journalCode=news` — Lancet editorial/news
- `bmj.com/news` — BMJ news desk

*Independent biomedical news:*

- `statnews.com` — STAT (biomedical/biotech reporting)
- `endpts.com` — Endpoints News (biotech reporting)

**Grounding rules.** W3a entries take the W2 shape but with `per institutional source`. W3b entries are emitted as `[Context]` narrative items in deep-research and as `UNVERIFIED` / `OVERGENERALIZED` supporting context in the verifier — never as the sole evidence for `VERIFIED`. Example (verifier, W3b):

```json
{
  "method": "web_search",
  "tool": "mcp__exa__web_search_exa",
  "result_summary": "Nature news desk summary of aducanumab approval [context only, W3b curated media]; no_doi available; URL=https://www.nature.com/articles/d41586-...; fetched_at=2026-05-14T16:24:51Z"
}
```

## Out-of-whitelist hits

Anything not matching W1/W2/W3 is **dropped** before bibliography promotion (deep-research) and **rejected as grounding evidence** (verifier). The verifier can still log an out-of-whitelist URL in `verification_path[]` as documentary trail, but the verdict cannot be `VERIFIED` unless an in-whitelist source corroborates.

Common out-of-whitelist domains the agent will likely encounter:

- Personal blogs (`medium.com`, `substack.com`, `*.wordpress.com`)
- Vendor / company marketing pages (unless the page IS the primary disclosure — sponsor press releases on `.com` are a judgement call; default to context-only)
- Wikipedia (useful for orientation in Phase 1 Scoping but never citable)
- Generic news aggregators (`reddit.com`, `news.ycombinator.com`, `twitter.com`, `x.com`)
- Predatory venues per the verifier's predatory-journal list

## Edge cases

- **Sponsor press releases on .com.** When the page is the sponsor's first-party disclosure of trial results (e.g., on a pharma company's investor-relations site), it is the primary record and may be cited as W2-equivalent with the tag `per sponsor disclosure`. The presence of a corresponding ClinicalTrials.gov entry is preferred.
- **DOI present on a W3b page.** If the news article happens to carry a DOI for its own editorial (some journals issue DOIs for news pieces), the DOI does NOT promote the source above W3b. The page's role as secondary commentary is what places it in W3b, not the absence of an identifier.
- **Wayback / archive.org URLs.** Known gap. For v1, archive.org and web.archive.org URLs are **out-of-whitelist** (not citable). Inheriting the tier of the embedded original URL would require a regex extractor + recursive whitelist evaluation, and a half-implemented fallback is worse than no fallback for audit-critical code. Revisit if archive URLs become a frequent source in practice.
- **Preprint servers.** `biorxiv.org`, `medrxiv.org`, `arxiv.org` are **not** on this whitelist because they have their own first-class scholarly channel in the deep-research Search Contract (Paperclip + bioRxiv MCP). Web access to these domains is redundant with the scholarly channels.

## Programmatic lookup

A YAML sibling, [`citable_web_domains.yaml`](citable_web_domains.yaml), exposes the whitelist for deterministic lookup by `deep-research/agents/bibliography.md` Step 4d and the verifier web-slot routing. Update both files in lockstep when adding or removing a domain.

## Maintenance

- Adding a domain: prefer specific path prefixes over bare TLDs when the domain has both primary-source and marketing content (`fda.gov` covers all of FDA; `nature.com/news` is path-scoped).
- Removing a domain: if a regulator merges or rebrands, keep the old domain alongside the new one through the next minor version release so previously-rendered audits remain self-consistent against the YAML.
- The whitelist is **not** versioned per audit — a verifier run on an old audit report uses the *current* YAML to evaluate domain trust. If a domain is downgraded between audits, the older audit's grounding stands; only new audits use the new tier.
