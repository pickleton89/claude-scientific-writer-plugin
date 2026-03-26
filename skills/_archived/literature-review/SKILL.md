---
name: literature-review
version: 2.3.0
description: "Conduct systematic literature reviews using multiple academic databases with quantified coverage thresholds. Provides structured methodology for search, screening, synthesis, and citation verification with professional output in markdown and PDF formats."
when_to_use: "Systematic, scoping, narrative, or rapid literature reviews requiring multi-database search strategies and PRISMA-compliant documentation"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch]
shared-thresholds: "../QUANTIFICATION_THRESHOLDS.md"
---

# Literature Review

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §1 (Literature Coverage) and §6 (Time-Based Thresholds).

<overview>
Conduct systematic literature reviews with quantified coverage requirements: ≥3 databases, 30-100+ papers depending on review type, and documented search strategies achieving <5% new papers in final iteration. This skill provides structured workflows for multi-database searching, screening, thematic synthesis, and citation verification with professional output generation in markdown and PDF formats.
</overview>

<prerequisites>
## Prerequisites

**Required Tools:**
- **pandoc**: For PDF generation (`brew install pandoc` on macOS, `apt-get install pandoc` on Linux)
- **Python 3.8+**: For running helper scripts

**Python Dependencies:**
```bash
pip install requests beautifulsoup4 bibtexparser
```

**Optional:**
- Reference manager (Zotero, Mendeley) for citation organization
- LaTeX distribution for advanced PDF formatting
</prerequisites>

<scripts>
## Helper Scripts

This skill includes automation scripts in `{baseDir}/scripts/`:

| Script | Purpose | Usage |
|--------|---------|-------|
| `verify_citations.py` | DOI verification and metadata check | `python {baseDir}/scripts/verify_citations.py --input references.bib` |
| `generate_pdf.py` | Convert markdown to formatted PDF | `python {baseDir}/scripts/generate_pdf.py --input review.md --style apa` |

> **For database searching:** Use the `paper-search` skill which provides unified multi-database search:
> ```bash
> python ../paper-search/scripts/search.py "query" --source pubmed,biorxiv,semantic
> ```

**Example Workflow:**
```bash
# 1. Run database searches (using paper-search skill)
python ../paper-search/scripts/search.py "machine learning AND healthcare" --source pubmed,semantic --output results.json

# 2. After writing review, verify all citations
python {baseDir}/scripts/verify_citations.py --input my_review.md --output verification_report.txt

# 3. Generate final PDF
python {baseDir}/scripts/generate_pdf.py --input my_review.md --output my_review.pdf --toc
```
</scripts>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Conducting a systematic literature review for research or publication
- Synthesizing current knowledge on a topic across multiple sources
- Performing meta-analysis, scoping reviews, or rapid reviews
- Writing the literature review section of a paper or thesis
- Investigating state of the art in a research domain
- Identifying research gaps and future directions

Do NOT use this skill when:
- Looking up a single paper or citation → use `paper-search`
- Searching a single database for quick reference → use `paper-search`
- Formatting existing citations → use `citation-management`
- Creating figures for the review → use `scientific-schematics` or `plotting-libraries`
</when_to_use>

<decision_framework>
## Quick Reference: Key Thresholds

| Review Type | Min Databases | Min Papers | Timeline |
|-------------|---------------|------------|----------|
| Systematic | 3-5 | 30+ | 6-18 months |
| Scoping | 2-4 | Variable | 3-6 months |
| Narrative | 2-3 | Variable | 1-3 months |
| Rapid | 2-3 | 10-30 | 2-5 weeks |

**Comprehensive Search Criteria:**
- [ ] ≥3 databases searched with documented strategy
- [ ] Forward/backward citation search performed
- [ ] Gray literature checked (preprints, theses)
- [ ] ≤5% new relevant papers in final iteration

> **Full decision frameworks:** See [`references/decision_frameworks.md`]({baseDir}/references/decision_frameworks.md) for database selection matrix, review type comparison, quality assessment tool selection, and literature recency thresholds.

</decision_framework>

<workflow>
## Workflow

### Stage 1: Planning and Protocol

**Objective:** Define scope, research questions, and methodology

**Steps:**
1. Define research question using PICO/PEO/SPIDER framework:
   - **PICO**: Population, Intervention, Comparison, Outcome (clinical)
   - **PEO**: Population, Exposure, Outcome (observational)
   - **SPIDER**: Sample, Phenomenon, Design, Evaluation, Research type (qualitative)

2. Register protocol (for systematic reviews):
   - PROSPERO (health): https://www.crd.york.ac.uk/prospero/
   - OSF Registries (general): https://osf.io/registries

3. Define inclusion/exclusion criteria:

| Criterion | Include | Exclude |
|-----------|---------|---------|
| Date range | {{start}}-{{end}} | Before {{start}} |
| Language | English | Non-English |
| Publication type | Peer-reviewed, preprints | Conference abstracts only |
| Study design | {{designs}} | {{excluded designs}} |
| Population | {{target}} | {{excluded populations}} |

4. Select databases (minimum 3 for systematic reviews)
5. Define search strategy with Boolean operators

6. **Select review mode** based on scope and user intent:

| Mode | Scope | Output | Stages Used |
|------|-------|--------|-------------|
| **Factoid** | Single question / fact-check | `[topic]_factcheck.md` (≤1 page) | 1 → 2 → 7 |
| **Mini-review** | Narrow topic, focused synthesis | `[topic]_review.md` (1-3 pages) | 1 → 2 → 3 → 6 → 7 |
| **Full deep-research** | Comprehensive systematic review | Full PRISMA workflow | All 8 stages |

   - **Factoid mode:** Skip screening/extraction/quality stages. Search 2 databases, verify top 5-10 hits, produce concise answer with citations. Use for "What is the primary target of X?" type questions.
   - **Mini-review mode:** Abbreviated screening (title + abstract only), thematic synthesis of 10-30 papers, no formal quality assessment. Use for focused topics where comprehensive PRISMA is overkill.
   - **Full mode (default):** Complete PRISMA-compliant workflow. Use for systematic reviews, scoping reviews, or any review intended for publication.

**Exit Criteria:**
- [ ] Research question documented (PICO/PEO/SPIDER format)
- [ ] Protocol registered (if systematic review)
- [ ] Inclusion/exclusion criteria table completed
- [ ] ≥3 databases selected (see Database Selection Matrix)
- [ ] Search strategy drafted

---

### Stage 2: Systematic Search

**Objective:** Execute documented database searches meeting coverage thresholds (≥3 databases, <5% new papers in final iteration)

> **Tool:** Use the `paper-search` skill for multi-database searching. It provides unified access to PubMed, bioRxiv, Semantic Scholar, and Google Scholar.

**Steps:**
1. Construct search strings for each database:
   ```
   Concept 1 terms: (term1 OR synonym1 OR synonym2)
   AND
   Concept 2 terms: (term2 OR synonym3 OR synonym4)
   AND
   Concept 3 terms: (term3 OR synonym5)
   ```

2. **Collision-aware search construction** (if `entity-resolution` identity table available):
   - Check collision risk level from identity table
   - If **HIGH collision** (e.g., ACE, SET, CAT): prepend negative filters to all search strings
     ```
     Example: "ACE cardiovascular" → "ACE cardiovascular -\"ACE inhibitor\" -\"angiotensin converting enzyme inhibitor\" -\"ACE2\""
     ```
   - If **LOW collision**: proceed with standard search strings
   - Document collision status and any negative filters applied in search log
   - **ToolUniverse fallback search tools** (when primary databases insufficient):
     - `EuropePMC_search_articles` (capability: `literature.search`) — includes full-text snippet extraction
     - `SemanticScholar_search_papers` (capability: `literature.search`) — cross-domain coverage
   - **Citation network expansion** (after initial results):
     - `EuropePMC_get_citations` (capability: `literature.citations`) — forward citations from Europe PMC (see also: `openalex_citations`, `semantic_scholar_citations` in tool-lookup)
     - `SemanticScholar_get_recommendations` (capability: `literature.recommendations`) — AI-powered related papers

3. Execute searches using `paper-search` and document:
   ```bash
   # PubMed search
   python ../paper-search/scripts/search.py "your query" \
     --source pubmed --max 100 --output pubmed_results.json

   # bioRxiv preprint search
   python ../paper-search/scripts/search.py "your query" \
     --source biorxiv --max 50 --output biorxiv_results.json

   # Multi-source comprehensive search
   python ../paper-search/scripts/search.py "your query" \
     --source pubmed,biorxiv,semantic --max 50 --output combined_results.json
   ```

| Database | Date Searched | Search String | Results |
|----------|--------------|---------------|---------|
| PubMed | YYYY-MM-DD | [full query] | N papers |
| bioRxiv | YYYY-MM-DD | [full query] | N papers |
| Semantic Scholar | YYYY-MM-DD | [full query] | N papers |

4. Export results in structured format (JSON, BibTeX)
5. Search citation networks:
   - Forward citations: Papers citing key papers (use `--source semantic` with paper ID)
   - Backward citations: References from included papers
6. Search grey literature if appropriate (theses, reports, preprints)

**Search Saturation Criteria:**
- [ ] No new relevant papers in last 50 screened titles
- [ ] Citation chaining yields <5% new papers
- [ ] Expert consultation confirms no major gaps

**Exit Criteria:**
- [ ] All selected databases searched
- [ ] Search strategy documented verbatim for each database
- [ ] Search dates recorded
- [ ] All results exported and combined
- [ ] Total unique results counted after initial deduplication

---

### Stage 3: Screening and Selection

**Objective:** Systematically screen papers against criteria

**Screening Time Budgets:**

| Stage | Time per Paper | Action |
|-------|---------------|--------|
| Title screening | ≤15 seconds | Include/Exclude/Maybe |
| Abstract screening | ≤2 minutes | Include/Exclude with reason |
| Full-text screening | 10-20 minutes | Final inclusion decision |

**Steps:**
1. Remove duplicates:
   - Primary: Match by DOI
   - Secondary: Match by title (normalized, ≥90% similarity)
   - Document: N duplicates removed

2. Title screening:
   - Apply inclusion criteria to titles only
   - When uncertain, include for abstract review
   - Document exclusion count

3. Abstract screening:
   - Read abstracts of remaining papers
   - Apply all inclusion/exclusion criteria
   - Record exclusion reason for each paper

4. Full-text screening:
   - Obtain full texts of remaining papers
   - Apply all criteria with detailed review
   - Record specific exclusion reasons

5. Create PRISMA flow diagram (see template in [`references/output_templates.md`]({baseDir}/references/output_templates.md))

**Exit Criteria:**
- [ ] Deduplication complete (documented count)
- [ ] All titles screened (≤15 sec each average)
- [ ] All abstracts screened (exclusion reasons recorded)
- [ ] All full texts assessed
- [ ] PRISMA flow diagram complete with numbers
- [ ] Inter-rater agreement ≥0.8 (if dual screening)

---

### Stage 4: Data Extraction

**Objective:** Extract standardized data from included studies

**Extraction Fields:** Study ID, country, design, sample size, population, intervention/exposure, comparator, outcomes, key findings, limitations, quality score, funding, conflicts (see full template in [`references/output_templates.md`]({baseDir}/references/output_templates.md))

**Steps:**
1. Create extraction spreadsheet with all fields
2. Pilot extraction on 3-5 papers
3. Refine extraction form based on pilot
4. Extract data from all included studies
5. Verify extraction accuracy (dual extraction for ≥20%)

**Exit Criteria:**
- [ ] Extraction form finalized after pilot
- [ ] Data extracted from 100% of included studies
- [ ] Quality assessment completed for all studies
- [ ] Extraction verified (dual extraction ≥20%)
- [ ] Missing data documented as "NR" (not reported)

---

### Stage 5: Quality Assessment

**Objective:** Evaluate risk of bias and study quality

**Steps:**
1. Select tool from [`references/quality_assessment_tools.md`]({baseDir}/references/quality_assessment_tools.md)
2. Assess each study independently
3. Create summary table with domain-level and overall ratings
4. Create risk of bias visualization (traffic light plot)
5. Consider excluding very low quality studies

**Ratings:** High (all low RoB) → Moderate (1 high) → Low (≥2 high) → Very Low (≥3 high)

**Exit Criteria:**
- [ ] All studies assessed with selected tool
- [ ] Summary table complete
- [ ] Risk of bias plot generated
- [ ] Quality ratings assigned (High/Moderate/Low/Very Low)
- [ ] Decision made on study exclusions (if any)

---

### Stage 6: Synthesis and Analysis

**Objective:** Synthesize findings thematically across studies

**Synthesis Approaches:**

| Data Type | Approach | Output |
|-----------|----------|--------|
| Quantitative, similar outcomes | Meta-analysis | Forest plot, pooled effect |
| Quantitative, diverse outcomes | Narrative synthesis | Comparison tables |
| Qualitative | Thematic analysis | Theme framework |
| Mixed | Integrated synthesis | Mixed methods matrix |

**Steps:**
1. Identify 3-7 major themes from extracted data
2. Group studies by theme (studies may appear in multiple themes)
3. For each theme, synthesize across studies:
   - Consensus areas (≥80% agreement)
   - Conflicting findings (document discrepancies)
   - Gaps (what's not studied)

4. **Apply T1-T4 evidence grading** per `../shared/references/evidence_grading.md`:
   - Grade every key claim with inline evidence label: `[T{n}: source]`
   - T1 (Mechanistic/Direct): causal mechanism demonstrated, human clinical proof
   - T2 (Functional): model organism data, biochemical assays with phenotype
   - T3 (Association): GWAS, screen hits, correlations without mechanism
   - T4 (Mention/Review): review mentions, computational predictions, annotations
   - **Theme-level evidence summary** per theme:
     ```
     Theme: EGFR in NSCLC resistance — Strong (8 mechanistic [T1], 3 functional [T2], 1 association [T3])
     ```
   - Flag themes supported only by T3/T4 evidence as evidence gaps

5. **Theme clustering and sizing:**
   - Extract keywords from each paper -> group into semantic clusters
   - Minimum 3 papers per theme to be considered a valid cluster
   - Size labels: **Major** (10+ papers), **Minor** (3-9 papers), **Insufficient** (<3 papers — merge or note as gap)
   - Report theme distribution in results section

6. Write thematic synthesis (NOT study-by-study) with 4-6 citations per paragraph
7. Create summary tables per theme (see template in [`references/output_templates.md`]({baseDir}/references/output_templates.md))
8. If meta-analysis: calculate pooled effects, heterogeneity (I²)

> **The "So What?" Test:** For each theme, don't just describe *what* the literature says—explain *why it matters*. If a reader could ask "So what?" after reading your synthesis, you haven't explained the significance. Every theme should connect to: implications for the field, gaps that need addressing, or actionable conclusions.

**Exit Criteria:**
- [ ] 3-7 themes identified and documented
- [ ] All studies mapped to themes
- [ ] Thematic synthesis written (not study-by-study)
- [ ] Consensus/conflict/gaps identified per theme
- [ ] Summary tables created
- [ ] Meta-analysis complete (if applicable)

---

### Stage 7: Citation Verification

**Objective:** Verify accuracy of all citations

**Steps:**
1. Extract all DOIs and citations from document
2. Verify each DOI resolves correctly
3. Cross-check metadata (authors, title, year, journal)
4. Format citations consistently (see Citation Style Matrix)

5. **Full-text verification** for high-value claims (T1/T2 evidence, controversial findings):

   | Tier | Tool | Use Case | Capability Key |
   |------|------|----------|----------------|
   | 1 (preferred) | `EuropePMC_get_fulltext_snippets` | Quick, OA articles, bounded snippets | `literature.full_text_snippets` |
   | 2 | `SemanticScholar_get_pdf_snippets` | High-value papers with OA PDFs | `literature.full_text_snippets` |
   | 3 (deepest) | `get_full_text_article` (PubMed MCP) | PMC full text, detailed verification | `literature.full_text` |

   - Prioritize full-text verification for: claims that drive conclusions, contradictory findings, T1 evidence supporting major themes
   - Document coverage: "Full-text verification on X/Y papers (Z% coverage)"
   - Flag papers where full text was unavailable: "Abstract-only verification — full text behind paywall"
   - Minimum target: verify ≥50% of T1 claims and ≥30% of T2 claims via full text

**Citation Verification Checklist:**

- [ ] All DOIs tested and resolve
- [ ] Author names match source
- [ ] Publication year correct
- [ ] Journal name correct (abbreviated or full per style)
- [ ] Page numbers/article IDs correct
- [ ] In-text citations match reference list

**Citation Styles:** See [`references/citation_styles.md`]({baseDir}/references/citation_styles.md) for APA, Nature, Vancouver, IEEE formats.

**Exit Criteria:**
- [ ] 100% of DOIs verified
- [ ] All metadata cross-checked
- [ ] Citation style consistent throughout
- [ ] No [?] or broken references
- [ ] Reference list formatted correctly

---

### Stage 8: Document Generation

**Objective:** Produce final review document

**Steps:**
1. Compile review from template:
   - Abstract (structured: Background, Methods, Results, Conclusions)
   - Introduction (context, rationale, objectives)
   - Methods (search strategy, selection, assessment)
   - Results (PRISMA, synthesis by theme, quality summary)
   - Discussion (interpretation, limitations, implications—**must explain why findings matter**)
   - Conclusions (key findings, future directions)

2. Generate PDF with citations formatted
3. Review and proofread

**Document Quality Checklist:**

- [ ] Abstract covers all sections (≤350 words for structured)
- [ ] PRISMA flow diagram included
- [ ] Search strategy fully reproducible
- [ ] Results organized thematically (not study-by-study)
- [ ] Quality assessment summarized
- [ ] Limitations section included
- [ ] All references verified
- [ ] PDF generates without errors

**Exit Criteria:**
- [ ] All sections complete
- [ ] PRISMA diagram included
- [ ] Citations verified and formatted
- [ ] PDF generated successfully
- [ ] Proofread for errors

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Systematic Review |
|--------|---------|--------|-------------------|
| Databases searched | 2 | 3 | ≥4 |
| Search documentation | Dates only | Full queries | Reproducible queries |
| Included studies | ≥10 | ≥20 | ≥30 |
| Quality assessment | Informal | Standardized tool | Dual assessment |
| Citation verification | Spot-check | 100% DOIs | 100% + metadata |
| PRISMA compliance | None | Partial | Full checklist |

**Completion Checklist:**
- [ ] Research question in structured format (PICO/PEO/SPIDER)
- [ ] ≥3 databases searched with documented queries
- [ ] PRISMA flow diagram with complete numbers
- [ ] Quality assessment using standardized tool
- [ ] Thematic synthesis (not study-by-study)
- [ ] 100% of DOIs verified and resolving
- [ ] PDF generates without citation errors
- [ ] All PRISMA checklist items addressed (for systematic reviews)

</success_criteria>

<scope>
## Scope

**In Scope:**
- Systematic, scoping, narrative, and rapid reviews
- Multi-database literature searching
- Screening and selection workflows
- Quality assessment guidance
- Thematic synthesis methodology
- Citation verification
- PRISMA-compliant documentation
- PDF generation

**Out of Scope** (use specialized resources):
- Meta-analysis statistical calculations → use `statistical-analysis`
- Single paper lookups → use `paper-search`
- Citation formatting only → use `citation-management`
- Figure creation → use `plotting-libraries` or `scientific-schematics`
- Full-text retrieval → manual or institutional access

</scope>

<best_practices>
## Best Practices Summary

| Practice | Requirement |
|----------|-------------|
| Multi-database coverage | ≥3 databases, domain-appropriate |
| Thematic synthesis | Organize by themes, not study-by-study |
| Reproducible documentation | Verbatim search strings with dates |
| Quality assessment | Use validated tools (RoB 2.0, NOS, AMSTAR 2) |
| Citation verification | 100% DOIs verified before submission |
| Exclusion tracking | Reasons documented at each stage |

> **Detailed guidance:** See [`references/common_pitfalls.md`]({baseDir}/references/common_pitfalls.md) for expanded best practices and solutions.

</best_practices>

<templates>
## Output Templates

Available templates in [`references/output_templates.md`]({baseDir}/references/output_templates.md):

| Template | Purpose |
|----------|---------|
| PRISMA Flow Diagram | Complete flow with all PRISMA 2020 sections |
| Search Documentation | Database-by-database search recording |
| Data Extraction Form | Comprehensive study data capture |
| Characteristics Table | Summary of included studies |
| Summary of Findings | GRADE evidence quality summaries |
| Thematic Synthesis | Theme-based results structure |

**Quick PRISMA Structure:**
```
Identification → Screening → Eligibility → Included
```

**Factoid Template** (for Factoid mode):
```markdown
# Factoid: {QUESTION}

**Answer:** {concise answer, 1-3 sentences}

**Evidence:**
| # | Source | Year | Finding | Tier |
|---|--------|------|---------|------|
| 1 | {Author et al.} | {year} | {key finding} | T{n} |
| 2 | ... | ... | ... | ... |

**Databases searched:** {list}
**Search date:** {date}
**Confidence:** {High/Medium/Low} based on {N} concordant sources
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `entity-resolution` | **Prerequisite** (if biomedical) — provides collision filters for search construction |
| `paper-search` | Use for multi-database searching in Stage 2 (PubMed, bioRxiv, Semantic Scholar, Google Scholar) |
| `citation-management` | Use for citation formatting after extraction |
| `scientific-schematics` | Generate PRISMA diagrams and synthesis figures |
| `plotting-libraries` | Create forest plots and summary visualizations |
| `statistical-analysis` | Perform meta-analysis calculations |
| `scientific-writing` | Write manuscript sections from review |
| `venue-templates` | Format for specific journal requirements |
| `research-paper-summarizer` | Summarize individual papers found during review; use for key papers requiring deep analysis |
| `target-validation` | **Downstream** — consumes literature evidence with T1-T4 grading for validation scoring |

**Shared References:**
- `../shared/references/evidence_grading.md` — T1-T4 tier definitions for evidence grading
- `../shared/tool-lookup.yaml` — capability keys for ToolUniverse search/citation tools

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| [`references/decision_frameworks.md`]({baseDir}/references/decision_frameworks.md) | Database selection, review types, quality tools, thresholds |
| [`references/output_templates.md`]({baseDir}/references/output_templates.md) | PRISMA, search docs, extraction, synthesis templates |
| [`references/common_pitfalls.md`]({baseDir}/references/common_pitfalls.md) | Best practices and solutions for common mistakes |
| [`references/quality_assessment_tools.md`]({baseDir}/references/quality_assessment_tools.md) | RoB 2.0, NOS, QUADAS-2, CASP, AMSTAR 2 guidance |
| [`references/prisma_checklist.md`]({baseDir}/references/prisma_checklist.md) | Full PRISMA 2020 checklist with extensions |
| [`references/citation_styles.md`]({baseDir}/references/citation_styles.md) | APA, Nature, Vancouver, IEEE formatting |
| [`references/database_strategies.md`]({baseDir}/references/database_strategies.md) | Database-specific search optimization |
| [`references/expert_guide.md`]({baseDir}/references/expert_guide.md) | Expert synthesis and advanced patterns |

## External Resources

| Resource | URL |
|----------|-----|
| PRISMA Statement | http://www.prisma-statement.org/ |
| Cochrane Handbook | https://training.cochrane.org/handbook |
| PROSPERO Registry | https://www.crd.york.ac.uk/prospero/ |
| MeSH Browser | https://meshb.nlm.nih.gov/search |
| AMSTAR 2 | https://amstar.ca/ |

</references>
