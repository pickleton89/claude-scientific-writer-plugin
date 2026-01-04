---
name: citation-management
version: 2.1.0
description: "Comprehensive citation management for academic research: extract metadata, validate citations, generate formatted BibTeX entries."
allowed-tools: [Read, Write, Edit, Bash, WebSearch, WebFetch]
---

# Citation Management

<overview>
Systematic citation management throughout the research and writing workflow. Extract accurate metadata from multiple sources (CrossRef, PubMed, arXiv), validate citation information, and generate properly formatted BibTeX entries. Critical for maintaining citation accuracy and ensuring reproducible research.

> **For paper discovery:** Use the `paper-search` skill to find papers across multiple databases (PubMed, bioRxiv, Semantic Scholar, Google Scholar). This skill focuses on managing citations after papers have been identified.
</overview>

<setup>
## Prerequisites

**Install dependencies before using scripts:**
```bash
pip install requests
```

**Available Scripts:**

| Script | Purpose | Usage |
|--------|---------|-------|
| `doi_to_bibtex.py` | Convert DOIs to BibTeX | `python {baseDir}/scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2` |
| `extract_metadata.py` | Extract metadata from any identifier | `python {baseDir}/scripts/extract_metadata.py --doi 10.xxxx/xxxxx` |
| `validate_citations.py` | Validate BibTeX file | `python {baseDir}/scripts/validate_citations.py references.bib` |
| `format_bibtex.py` | Clean and format BibTeX | `python {baseDir}/scripts/format_bibtex.py input.bib -o output.bib` |

> **Note:** For paper searching, use the `paper-search` skill which provides unified search across PubMed, bioRxiv, Semantic Scholar, and Google Scholar.

</setup>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Converting DOIs, PMIDs, or arXiv IDs to BibTeX
- Extracting complete metadata for citations
- Validating existing citations for accuracy
- Cleaning and formatting BibTeX files
- Building a bibliography for a manuscript
- Checking for duplicate citations
- Ensuring consistent citation formatting

**For these tasks, use specialized skills instead:**

| Task | Recommended Skill |
|------|-------------------|
| Finding papers across databases | `paper-search` |
| Systematic literature review methodology | `literature-review` |
| Thematic synthesis of findings | `literature-review` |
| Journal-specific manuscript formatting | `venue-templates` |
| Statistical result selection for citation | `statistical-analysis` |

</when_to_use>

<decision_framework>
## Decision Matrix

For detailed decision trees on citation style selection, metadata source routing, and database selection by field, see:
→ `{baseDir}/references/decision_framework.md`

**Quick Reference:**

| Decision | Key Guidance |
|----------|--------------|
| Citation style | Match to venue type (biomedical→Vancouver, CS→IEEE, social sciences→APA) |
| Metadata source | DOI→CrossRef, PMID→PubMed E-utilities, arXiv→arXiv API |
| Database selection | Search ≥2 databases per domain for comprehensive coverage |

</decision_framework>

<workflow>
## Workflow

> **Prerequisite:** Use `paper-search` to find papers before managing citations. This skill assumes papers have already been identified.

### Stage 1: Metadata Extraction

**Progress Milestones:**
- 25%: Identifier types classified
- 50%: Primary API sources queried
- 75%: Required fields verified
- 100%: Gaps filled, author names standardized

**Objective:** Convert paper identifiers to complete, accurate metadata

**Steps:**
1. Identify identifier type (DOI, PMID, arXiv ID, ISBN)
2. Query primary API source (see routing table)
3. Verify all required fields present
4. Fill gaps from secondary sources if needed
5. Standardize author name format (Last, First)

**Exit Criteria:**
- [ ] All required fields populated (see Required Fields table)
- [ ] DOI verified as resolvable via doi.org
- [ ] Author names in consistent format
- [ ] Journal name standardized (not abbreviated inconsistently)

**Required Fields by Entry Type:**

| Field | @article | @inproceedings | @book | @misc (preprint) |
|-------|----------|----------------|-------|------------------|
| author | ✓ Required | ✓ Required | ✓ Required | ✓ Required |
| title | ✓ Required | ✓ Required | ✓ Required | ✓ Required |
| year | ✓ Required | ✓ Required | ✓ Required | ✓ Required |
| journal | ✓ Required | — | — | — |
| booktitle | — | ✓ Required | — | — |
| publisher | — | — | ✓ Required | — |
| doi | ✓ Recommended | ✓ Recommended | ○ Optional | ✓ Recommended |
| volume | ✓ Recommended | — | — | — |
| pages | ✓ Recommended | ✓ Recommended | — | — |
| url | ○ Optional | ○ Optional | ○ Optional | ✓ Required |
| eprint | — | — | — | ✓ Required (arXiv) |

---

### Stage 2: BibTeX Generation

**Progress Milestones:**
- 25%: Entry types selected
- 50%: Citation keys generated
- 75%: Required fields populated
- 100%: Title case protection applied, entries complete

**Objective:** Generate clean, properly formatted BibTeX entries

**Steps:**
1. Select correct entry type (@article, @inproceedings, etc.)
2. Generate citation key: FirstAuthorYear + keyword (e.g., Smith2024crispr)
3. Populate all required fields
4. Add recommended fields (DOI, URL)
5. Apply title case protection for proper nouns

**Exit Criteria:**
- [ ] Entry type matches publication type
- [ ] Citation key is unique and meaningful
- [ ] All required fields present
- [ ] DOI field included (if available)
- [ ] Special characters properly escaped

**Inline Validation (verify as you generate):**

After generating each entry, immediately verify before proceeding:
```bash
# Quick validation of single entry
python {baseDir}/scripts/validate_citations.py entry.bib

# Or validate DOI resolution manually
curl -sI "https://doi.org/10.xxxx/xxxxx" | head -1
# Should return: HTTP/2 302 or HTTP/1.1 302
```

Fix any errors before generating the next entry. This prevents error accumulation.

**BibTeX Templates:**

```bibtex
@article{AuthorYearkeyword,
  author  = {Last1, First1 and Last2, First2},
  title   = {Article {Title} with {Proper Noun} Protection},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {3},
  pages   = {123--145},
  doi     = {10.1234/example},
}

@inproceedings{AuthorYearkeyword,
  author    = {Last, First},
  title     = {Paper Title},
  booktitle = {Proceedings of Conference Name},
  year      = {2024},
  pages     = {1--10},
  doi       = {10.1234/example},
}

@misc{AuthorYearkeyword,
  author       = {Last, First and Last2, First2},
  title        = {Preprint Title},
  year         = {2024},
  eprint       = {2401.12345},
  eprinttype   = {arXiv},
  eprintclass  = {cs.LG},
  url          = {https://arxiv.org/abs/2401.12345},
}
```

---

### Stage 3: Validation

**Progress Milestones:**
- 25%: BibTeX syntax validated
- 50%: Required fields checked
- 75%: DOIs verified as resolvable
- 100%: Duplicates removed, consistency verified

**Objective:** Verify all citations are accurate and complete

**Steps:**
1. Parse BibTeX file and check syntax
2. Verify required fields for each entry type
3. Validate DOIs resolve correctly
4. Detect duplicate entries (same DOI, similar titles)
5. Check for format consistency

**Exit Criteria:**
- [ ] Zero syntax errors in BibTeX file
- [ ] 100% of entries have required fields
- [ ] 100% of DOIs verified as resolvable
- [ ] Zero duplicate entries
- [ ] Consistent citation key format throughout

**Validation Checklist:**

| Check | Pass Criteria | Severity if Failed |
|-------|---------------|-------------------|
| DOI Resolution | doi.org returns 200 OK | High - fix immediately |
| Required Fields | All present for entry type | High - incomplete citation |
| Year Format | 4 digits, 1900-2030 | Medium - likely typo |
| Page Format | num--num or single page | Low - cosmetic |
| Unique Keys | No duplicates | High - LaTeX will fail |
| Author Format | Last, First throughout | Medium - inconsistent |

---

### Stage 4: Integration

**Progress Milestones:**
- 25%: .bib file copied to manuscript directory
- 50%: Bibliography command added to LaTeX
- 75%: Document compiled, citations checked
- 100%: Reference formatting verified against venue

**Objective:** Integrate validated bibliography into manuscript workflow

**Steps:**
1. Copy validated .bib file to manuscript directory
2. Add `\bibliography{filename}` to LaTeX document
3. Set citation style with `\bibliographystyle{}`
4. Compile document and check all `\cite{}` commands resolve
5. Verify reference formatting matches venue requirements

**Exit Criteria:**
- [ ] No undefined citation warnings in LaTeX log
- [ ] Reference list renders completely
- [ ] Citation style matches target venue
- [ ] All citations appear in references (no orphans)

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| DOI resolution rate | 90% | 98% | 100% |
| Required field completeness | 95% | 100% | 100% |
| Duplicate detection | 90% caught | 98% caught | 100% |
| Citation key uniqueness | 100% | 100% | 100% |
| Author format consistency | 90% | 100% | 100% |

**Completion Checklist:**
- [ ] All entries have required fields for their type
- [ ] 100% of DOIs verified as resolvable
- [ ] Zero duplicate entries detected
- [ ] Consistent citation key format (AuthorYearkeyword)
- [ ] BibTeX file compiles without errors
- [ ] Reference formatting matches target venue style

</success_criteria>

<scope>
## Scope

**In Scope:**
- DOI/PMID/arXiv ID to BibTeX conversion
- Citation metadata extraction and validation
- BibTeX file formatting and deduplication
- Citation style guidance for common venues
- Preprint to published version updating

**Out of Scope** (use specialized resources):
- Finding papers across databases → use `paper-search`
- Systematic literature review methodology → use `literature-review`
- Thematic synthesis of findings → use `literature-review`
- Journal-specific manuscript formatting → use `venue-templates`
- Reference manager software (Zotero, Mendeley, EndNote) tutorials → external resources
- Citation network analysis → specialized bibliometric tools

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Skipping Paper Search

**Anti-pattern:**
Manually typing citation metadata or searching databases without using `paper-search`.

**Solution:**
Use `paper-search` to find papers systematically across multiple databases (PubMed, bioRxiv, Semantic Scholar). Export results in BibTeX format for direct import into your bibliography.

---

### 2. Accepting Metadata Blindly

**Anti-pattern:**
```bibtex
% Accepting CrossRef output without verification
@article{wrong2024,
  author = {Smith, J},  % Missing co-authors!
  title = {important study},  % Wrong capitalization
  year = {2023},  % Wrong year - published 2024
}
```

**Solution:**
```bibtex
% Verified against original publication
@article{Smith2024important,
  author = {Smith, John and Jones, Mary and Chen, Wei},
  title = {An Important Study of {CRISPR} Applications},
  year = {2024},
  journal = {Nature Methods},
  volume = {21},
  pages = {100--115},
  doi = {10.1038/s41592-024-01234-5},
}
```

---

### 3. Missing DOI Validation

**Anti-pattern:**
Including DOIs without verifying they resolve.

**Solution:**
Validate every DOI: `curl -sI https://doi.org/10.xxxx/xxxxx | head -1` should return 200 or 302. Remove or fix any non-resolving DOIs.

---

### 4. Inconsistent Citation Keys

**Anti-pattern:**
```bibtex
@article{ref1,  ...}
@article{SMITH2024,  ...}
@article{paper_about_crispr,  ...}
```

**Solution:**
```bibtex
@article{Smith2024crispr,  ...}
@article{Jones2023protein,  ...}
@article{Chen2024method,  ...}
```

Use consistent format: FirstAuthorYearkeyword (e.g., Smith2024crispr).

---

### 5. Citing Outdated Preprints

**Anti-pattern:**
Citing arXiv preprint when peer-reviewed version is published.

**Solution:**
Before finalizing bibliography, check if any preprints have been published:
1. Search DOI registries for arXiv ID
2. Check preprint page for "published in" notice
3. Update entry to journal version with proper DOI

---

### 6. Duplicate Entries

**Anti-pattern:**
Same paper with different citation keys:
```bibtex
@article{Smith2024a,  doi = {10.1234/example}, ...}
@article{smithPaper,  doi = {10.1234/example}, ...}  % Duplicate!
```

**Solution:**
Deduplicate by DOI: Extract all DOIs, identify duplicates, keep entry with best metadata, remove others.

---

### 7. Manual BibTeX Entry

**Anti-pattern:**
Typing BibTeX entries by hand, introducing errors.

**Solution:**
Always extract from authoritative sources:
- CrossRef API for DOIs
- PubMed E-utilities for PMIDs
- arXiv API for arXiv IDs

Never type entries manually; copy-paste introduces errors.

</anti_patterns>

<templates>
## Output Templates

For complete templates with examples, see:
→ `{baseDir}/references/output_templates.md`

**Available Templates:**

| Template | Used In | Purpose |
|----------|---------|---------|
| Validation Report (JSON) | Stage 3 | Machine-readable validation output |

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `paper-search` | Use for finding papers across databases (PubMed, bioRxiv, Semantic Scholar, Google Scholar); citation-management handles metadata extraction and validation |
| `literature-review` | Use for systematic search methodology; citation-management handles technical citation extraction |
| `venue-templates` | Use for journal-specific formatting after citations are validated |
| `scientific-writing` | Integrates validated bibliography into manuscript |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Combined Workflow:**
1. `paper-search` → find papers across multiple databases
2. `citation-management` → extract metadata and generate BibTeX
3. `citation-management` → validate all citations
4. `literature-review` → synthesize findings thematically (if systematic review)
5. `venue-templates` → format for target journal

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/decision_framework.md` | Citation style, metadata routing |
| `{baseDir}/references/output_templates.md` | Validation report templates |
| `{baseDir}/references/metadata_extraction.md` | Metadata sources and field requirements |
| `{baseDir}/references/citation_validation.md` | Validation criteria and quality checks |
| `{baseDir}/references/bibtex_formatting.md` | BibTeX entry types and formatting rules |

> **Search Documentation:** For database search guides (PubMed, Google Scholar, bioRxiv, Semantic Scholar), see the `paper-search` skill.

### External Resources

**Search Engines:**
- Google Scholar: https://scholar.google.com/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- arXiv: https://arxiv.org/

**Metadata APIs:**
- CrossRef API: https://api.crossref.org/
- PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API: https://arxiv.org/help/api/
- DataCite API: https://api.datacite.org/

**Tools:**
- MeSH Browser: https://meshb.nlm.nih.gov/search
- DOI Resolver: https://doi.org/

</references>
