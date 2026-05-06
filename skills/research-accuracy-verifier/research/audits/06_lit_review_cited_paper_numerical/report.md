# Accuracy Audit — Front-Line Pembrolizumab Combinations in PD-L1–High Advanced NSCLC: A Brief Literature Review

- **Document type:** lit_review
- **Date checked:** 2026-05-06
- **Verification tier:** 3
- **Sources consulted:** user-provided full text: regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt, stats.json (research-paper-summarizer cooperation): regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json, source_meta.json: regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_source_meta.json
- **Overall confidence:** moderate

> One CRITICAL contradiction: the document reports '210 patients' enrolled, but the cited Smith 2024 source records 187 patients (Abstract Methods, Results §3.1, and stats.json claim_id C-01). All other numerical claims (47.3% 12-month PFS, 95% CI 38.1–55.9%, prespecified 40% threshold, enrollment dates, 11.2-month median PFS, 7.7-month historical comparator, p < 0.001 by one-sample log-rank) verify exactly against the source. Per the computed-confidence rule, 1 CRITICAL with otherwise clean evidence falls in the 'moderate' band (≤2 CRITICAL). The contradiction is load-bearing (sample size) but isolated and easily corrected.

**Coverage caveats:**
- Cited source DOI 10.0001/jtor.fixture.smith2024 is fixture-reserved and does not resolve online. Per intake instruction and Stage 6 cited_papers[] cooperation contract, the local source_meta.json and stats.json were treated as the canonical record for citation existence and numerical sanity (no online lookup attempted).

## Executive Summary

Audit checked 8 claims (1 reference entry, 1 cited statement, and 6 numerical claims) against the user-provided cited source. Seven of eight claims verify cleanly against the source full text and the cooperating research-paper-summarizer stats.json. One CRITICAL contradiction was found: the document states '210 patients' were enrolled, but the cited Smith 2024 paper reports an enrollment of 187 patients (Abstract Methods, Results §3.1, and stats.json C-01). Recommendation: correct the patient count to 187 before circulating; the rest of the numerical evidence base is intact.

## Findings

### CRITICAL (1)

#### C004 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 2 |
| Claim (verbatim) | "**210 patients** were enrolled with previously untreated PD-L1–high disease between January 2022 and November 2023 (Smith 2024)." |
| Verification path | (1) `abstract_check` via stats.json (research-paper-summarizer cooperation): stats.json claim_id C-01 records value=187, unit=patients, stat_type=sample_size, context='We enrolled 187 patients with previously untreated PD-L1–high (TPS ≥ 50%) advanced non-squamous NSCLC'. Document asserts 210 patients — conflict of 23 patients (12.3% overcount). (2) `abstract_check` via user-provided source (Methods/Results §3.1): Source Abstract Methods: 'We enrolled 187 patients ... between January 2022 and November 2023.' Source Results §3.1 restates 187. No mention of 210 anywhere in the paper. The document's '210 patients' directly contradicts the cited source. |
| Evidence | smith2024_pembro_nsclc.txt Abstract Methods — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt; smith2024_pembro_nsclc_stats.json (C-01) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json |
| Verdict | `CONTRADICTED` |
| Severity | CRITICAL |
| Recommended action | Replace '210 patients' with '187 patients' to match the cited source (Smith 2024 Abstract Methods and Results §3.1; stats.json C-01). The enrollment window (January 2022 — November 2023) is correct as written. |
| Confidence | high |

### INFORMATIONAL (7)

#### C001 — citation_bearing

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 1 |
| Claim (verbatim) | "Smith et al. reported a 12-month progression-free survival rate of **47.3%** (95% CI 38.1–55.9%) in their single-center investigator-initiated trial, exceeding the prespecified 40% threshold (Smith 2024)." |
| Verification path | (1) `abstract_check` via user-provided source: Source abstract states '12-month progression-free survival rate was 47.3% (95% CI 38.1–55.9%)' and conclusions state 'exceeding the prespecified 40% threshold'. Direct match. (2) `doi_lookup` via intake.cited_papers source_meta.json: Fixture DOI (10.0001/* reserved for examples; does not resolve online). Local source_meta.json provides canonical record per Stage 6 cooperation contract. |
| Evidence | smith2024_pembro_nsclc.txt (user-provided full text) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt; smith2024_pembro_nsclc_stats.json (claim_id C-03) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required; PFS rate, CI, and 40% threshold framing all match the cited source. |
| Confidence | high |

#### C002 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 1 |
| Claim (verbatim) | "12-month progression-free survival rate of **47.3%** (95% CI 38.1–55.9%)" |
| Verification path | (1) `abstract_check` via stats.json (research-paper-summarizer cooperation): stats.json claim_id C-03 records value=47.3, unit=%, context='12-month progression-free survival rate was 47.3% (95% CI 38.1–55.9%)'. Exact match to document. (2) `abstract_check` via user-provided source: Source abstract and Results §3.2 both state '47.3% (95% CI 38.1–55.9%)'. Verbatim match. |
| Evidence | smith2024_pembro_nsclc_stats.json (C-03) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. |
| Confidence | high |

#### C003 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 1 |
| Claim (verbatim) | "exceeding the prespecified 40% threshold" |
| Verification path | (1) `abstract_check` via user-provided source: Source Abstract Conclusions: 'exceeding the prespecified 40% threshold'. Verbatim match. |
| Evidence | smith2024_pembro_nsclc.txt Abstract Conclusions — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. |
| Confidence | high |

#### C005 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 2 |
| Claim (verbatim) | "between January 2022 and November 2023" |
| Verification path | (1) `abstract_check` via user-provided source: Source Abstract Methods: 'between January 2022 and November 2023'. Verbatim match. |
| Evidence | smith2024_pembro_nsclc.txt Abstract Methods — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. |
| Confidence | high |

#### C006 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 2 |
| Claim (verbatim) | "The reported median PFS of 11.2 months substantially exceeds the historical 7.7-month median for pembrolizumab monotherapy" |
| Verification path | (1) `abstract_check` via stats.json (C-02, C-06): stats.json C-02 records value=11.2, unit=months, stat_type=median (Median PFS). stats.json C-06 records value=7.7, unit=months (historical median PFS for pembrolizumab monotherapy). Both numbers match document. (2) `abstract_check` via user-provided source: Source Abstract Results: 'Median PFS was 11.2 months (95% CI 8.4–14.7) ... historical median PFS of 7.7 months for pembrolizumab monotherapy'. Direct match. |
| Evidence | smith2024_pembro_nsclc.txt Abstract Results — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt; smith2024_pembro_nsclc_stats.json (C-02, C-06) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. |
| Confidence | high |

#### C007 — numerical

| Field | Content |
|---|---|
| Location | 2. Single-arm phase II evidence for pembrolizumab + platinum-doublet, paragraph 2 |
| Claim (verbatim) | "the difference reached statistical significance (p < 0.001 by one-sample log-rank against the historical control) (Smith 2024)." |
| Verification path | (1) `abstract_check` via stats.json (C-05): stats.json C-05 records value='<0.001', stat_type=p_value, context: 'p < 0.001 by one-sample log-rank against the historical control'. Verbatim match including test name. (2) `abstract_check` via user-provided source: Source Abstract Results and §3.2 both state 'p < 0.001 by one-sample log-rank'. Direct match. |
| Evidence | smith2024_pembro_nsclc.txt Abstract Results — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc.txt; smith2024_pembro_nsclc_stats.json (C-05) — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_stats.json |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. |
| Confidence | high |

#### C008 — citation_bearing

| Field | Content |
|---|---|
| Location | References, paragraph 1 |
| Claim (verbatim) | "Smith JR, Patel A, Ng S, Williams T, Okafor C, Lee H, et al. Pembrolizumab plus carboplatin/pemetrexed in PD-L1–high advanced non-squamous NSCLC: a single-center phase II investigator-initiated study. *Journal of Thoracic Oncology Reports* 2024; 12(4): 287-301. DOI: 10.0001/jtor.fixture.smith2024" |
| Verification path | (1) `doi_lookup` via intake.cited_papers source_meta.json: Fixture DOI (10.0001/* prefix is reserved for examples and does not resolve online). Per intake instruction and Stage 6 cited_papers[] cooperation contract, source_meta.json is treated as the canonical record. All metadata fields (authors, title, year, venue, volume/issue/pages, DOI) in source_meta.json match the document's reference entry verbatim. (2) `ref_reconcile` via manual_check (single-citation document): Single inline key 'Smith 2024' appears 4 times; bibliography contains exactly one matching entry. Author/year/venue agree. |
| Evidence | smith2024_pembro_nsclc_source_meta.json — regression/sources/smith2024_pembro_nsclc/smith2024_pembro_nsclc_source_meta.json |
| Verdict | `VERIFIED` |
| Severity | INFORMATIONAL |
| Recommended action | No action required. Note: the cited source is a synthetic regression fixture (DOI 10.0001/* does not resolve online) — this is intentional in the audit context. |
| Confidence | high |

## Verification Matrix

| Claim ID | Stage | Verdict | Severity |
|---|---|---|---|
| C001 | 3 | `VERIFIED` | INFORMATIONAL |
| C002 | 6 | `VERIFIED` | INFORMATIONAL |
| C003 | 6 | `VERIFIED` | INFORMATIONAL |
| C004 | 6 | `CONTRADICTED` | CRITICAL |
| C005 | 6 | `VERIFIED` | INFORMATIONAL |
| C006 | 6 | `VERIFIED` | INFORMATIONAL |
| C007 | 6 | `VERIFIED` | INFORMATIONAL |
| C008 | 2 | `VERIFIED` | INFORMATIONAL |

## Methodology

Tier-3 audit of a lit_review document under standard flag_threshold. Single cited source supplied via intake.cited_papers[] (paper_id=smith2024_pembro_nsclc) per Stage 6 research-paper-summarizer cooperation contract. validate_stats.py confirmed stats.json compliance (Q5/R5 pass). Stage 2 citation existence verification used the local source_meta.json as canonical record (DOI 10.0001/* is fixture-reserved and does not resolve online — explicit intake instruction). Stage 3 alignment and Stage 6 numerical sanity used both the user-provided full text and stats.json claim_ids C-01 through C-07 as cross-checks. Stage 5 (quotes) had no direct quotes in the document. Stage 7 internal consistency: bibliography contains one entry; single inline citation key 'Smith 2024' resolves to it. All 8 findings passed validate_finding.py (P1–P5 predicates; severity computed from matrix). Limitations: online DOI resolution not attempted per intake; no second independent corpus check available for the synthetic fixture, which is by design for this regression case.
