---
name: literature-review
version: 2.2.0
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
| `search_databases.py` | Automated database querying | `python {baseDir}/scripts/search_databases.py --query "terms" --databases pubmed,scopus` |
| `verify_citations.py` | DOI verification and metadata check | `python {baseDir}/scripts/verify_citations.py --input references.bib` |
| `generate_pdf.py` | Convert markdown to formatted PDF | `python {baseDir}/scripts/generate_pdf.py --input review.md --style apa` |

**Example Workflow:**
```bash
# 1. Run database searches
python {baseDir}/scripts/search_databases.py --query "machine learning AND healthcare" --output results.json

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
- Looking up a single paper or citation → use `research-lookup`
- Searching a single database for quick reference → use `research-lookup`
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

**Exit Criteria:**
- [ ] Research question documented (PICO/PEO/SPIDER format)
- [ ] Protocol registered (if systematic review)
- [ ] Inclusion/exclusion criteria table completed
- [ ] ≥3 databases selected (see Database Selection Matrix)
- [ ] Search strategy drafted

---

### Stage 2: Systematic Search

**Objective:** Execute documented database searches meeting coverage thresholds (≥3 databases, <5% new papers in final iteration)

**Steps:**
1. Construct search strings for each database:
   ```
   Concept 1 terms: (term1 OR synonym1 OR synonym2)
   AND
   Concept 2 terms: (term2 OR synonym3 OR synonym4)
   AND
   Concept 3 terms: (term3 OR synonym5)
   ```

2. Execute searches and document:

| Database | Date Searched | Search String | Results |
|----------|--------------|---------------|---------|
| PubMed | YYYY-MM-DD | [full query] | N papers |
| Scopus | YYYY-MM-DD | [full query] | N papers |
| ... | ... | ... | ... |

3. Export results in structured format (RIS, BibTeX, JSON)
4. Search citation networks:
   - Forward citations: Papers citing key papers
   - Backward citations: References from included papers
5. Search grey literature if appropriate (theses, reports, preprints)

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

4. Write thematic synthesis (NOT study-by-study) with 4-6 citations per paragraph
5. Create summary tables per theme (see template in [`references/output_templates.md`]({baseDir}/references/output_templates.md))
6. If meta-analysis: calculate pooled effects, heterogeneity (I²)

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
   - Discussion (interpretation, limitations, implications)
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
- Single paper lookups → use `research-lookup`
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

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `research-lookup` | Use for single paper lookups and quick searches |
| `citation-management` | Use for citation formatting after extraction |
| `scientific-schematics` | Generate PRISMA diagrams and synthesis figures |
| `plotting-libraries` | Create forest plots and summary visualizations |
| `statistical-analysis` | Perform meta-analysis calculations |
| `scientific-writing` | Write manuscript sections from review |
| `venue-templates` | Format for specific journal requirements |
| `research-paper-summarizer` | Summarize individual papers found during review; use for key papers requiring deep analysis |

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
