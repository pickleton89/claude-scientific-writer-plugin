---
name: hypothesis-generation
version: 2.2.0
description: "Generate testable hypotheses with quantified quality criteria. Formulate from observations, design experiments, explore competing explanations, develop predictions, propose mechanisms, for scientific inquiry across domains."
when_to_use: "Use when developing hypotheses from observations, designing experiments to test scientific questions, exploring competing explanations, formulating testable predictions, or planning mechanistic studies across scientific domains."
allowed-tools: [Read, Write, Edit, Bash]
shared-thresholds: "../QUANTIFICATION_THRESHOLDS.md"
---

# Scientific Hypothesis Generation

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §1 (Literature Coverage), §3 (Replication & Sample Size), and §7 (Quality Scoring Rubrics).

## Overview

Hypothesis generation is a systematic process for developing testable explanations with quantified quality criteria. Generate 3-5 competing hypotheses per phenomenon, each meeting testability and falsifiability requirements. Support with ≥40 citations from ≥3 databases, achieving <5% new papers in final search iteration. Apply this skill for scientific inquiry across domains.

## When to Use This Skill

This skill should be used when:
- Developing hypotheses from observations or preliminary data
- Designing experiments to test scientific questions
- Exploring competing explanations for phenomena
- Formulating testable predictions for research
- Conducting literature-based hypothesis generation
- Planning mechanistic studies across scientific domains

## Setup Requirements

### LaTeX Environment

This skill generates professional LaTeX documents requiring specific compiler and packages:

| Requirement | Specification |
|-------------|---------------|
| **Compiler** | XeLaTeX or LuaLaTeX (required for fontspec) |
| **Style file** | `hypothesis_generation.sty` (in `assets/`) |
| **Template** | `hypothesis_report_template.tex` (in `assets/`) |

**Required LaTeX packages:**
- `tcolorbox` - Colored hypothesis boxes
- `xcolor` - Color definitions
- `fontspec` - Font handling (requires XeLaTeX/LuaLaTeX)
- `fancyhdr` - Header/footer formatting
- `titlesec` - Section styling
- `enumitem` - List customization
- `booktabs` - Professional tables
- `natbib` - Citation management

### Verification

Before generating reports, verify the LaTeX environment:

```bash
# Check compiler availability
xelatex --version

# Verify required packages are installed
kpsewhich tcolorbox.sty natbib.sty fontspec.sty

# Test template compilation (from skill directory)
cd {baseDir}/assets && xelatex hypothesis_report_template.tex
```

If packages are missing, install via your TeX distribution (TeX Live, MiKTeX, or MacTeX).

## Visual Enhancement with Scientific Schematics

**⚠️ MANDATORY: Every hypothesis generation report MUST include at least 1-2 AI-generated figures using the scientific-schematics skill.**

This is not optional. Hypothesis reports without visual elements are incomplete. Before finalizing any document:
1. Generate at minimum ONE schematic or diagram (e.g., hypothesis framework showing competing explanations)
2. Prefer 2-3 figures for comprehensive reports (mechanistic pathway, experimental design flowchart, prediction decision tree)

**How to generate figures:**

Invoke the **scientific-schematics** skill to generate AI-powered publication-quality diagrams:
1. Describe your desired diagram in natural language
2. The skill will automatically generate, review, and refine the schematic
3. Outputs are saved as publication-ready images

**Integration with scientific-schematics skill:**
- The scientific-schematics skill handles all figure generation
- Describe the concept; the skill produces the visual
- Figures are automatically formatted for accessibility (colorblind-friendly, high contrast)

**When to add schematics:**
- Hypothesis framework diagrams showing competing explanations
- Experimental design flowcharts
- Mechanistic pathway diagrams
- Prediction decision trees
- Causal relationship diagrams
- Theoretical model visualizations
- Any complex concept that benefits from visualization

For detailed guidance on creating schematics, refer to the scientific-schematics skill documentation.

---

## Workflow

Follow this systematic process to generate robust scientific hypotheses:

### 1. Understand the Phenomenon

**Progress Milestones:**
- 25%: Core observation identified and articulated
- 50%: Scope and boundaries defined
- 75%: Known vs. unknown aspects documented
- 100%: Relevant domain(s) identified, search terms generated

Start by clarifying the observation, question, or phenomenon that requires explanation:

- Identify the core observation or pattern that needs explanation
- Define the scope and boundaries of the phenomenon
- Note any constraints or specific contexts
- Clarify what is already known vs. what is uncertain
- Identify the relevant scientific domain(s)

### 2. Conduct Comprehensive Literature Search

**Progress Milestones:**
- 25%: Search strategy defined, databases selected
- 50%: Primary database searches executed (50% of papers)
- 75%: All databases searched, 70+ papers retrieved
- 100%: Search saturation achieved (<5% new papers), papers organized

Search existing scientific literature to ground hypotheses in current evidence. Use both PubMed (for biomedical topics) and general web search (for broader scientific domains).

**Quantified Search Requirements** (see [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §1):

| Requirement | Minimum | Target |
|-------------|---------|--------|
| Databases searched | 3 | 4-5 |
| Total papers retrieved | 40 | 70+ |
| Recent papers (≤5 years) | 60% | 75% |
| Search saturation | <5% new in final iteration | <2% |

**For biomedical topics:**
- Use WebFetch with PubMed URLs to access relevant literature
- Search for recent reviews (≤3 years), meta-analyses, and primary research
- Look for similar phenomena, related mechanisms, or analogous systems

**For all scientific domains:**
- Use WebSearch to find recent papers, preprints, and reviews
- Search for established theories, mechanisms, or frameworks
- Identify gaps in current understanding

**Search strategy:**
- Begin with broad searches to understand the landscape (expect 100-200 initial hits)
- Narrow to specific mechanisms, pathways, or theories (refine to 40-70 relevant papers)
- Look for contradictory findings or unresolved debates (note ≥2 alternative viewpoints)
- Consult `references/literature_search_strategies.md` for detailed search techniques

### 3. Synthesize Existing Evidence

**Progress Milestones:**
- 25%: Current understanding summarized
- 50%: Key mechanisms and theories catalogued
- 75%: Conflicting evidence and gaps identified
- 100%: Synthesis complete, ready for hypothesis generation

Analyze and integrate findings from literature search:

- Summarize current understanding of the phenomenon
- Identify established mechanisms or theories that may apply
- Note conflicting evidence or alternative viewpoints
- Recognize gaps, limitations, or unanswered questions
- Identify analogies from related systems or domains

### 4. Generate Competing Hypotheses

**Progress Milestones:**
- 25%: First hypothesis drafted with mechanistic explanation
- 50%: 2-3 hypotheses drafted, covering different mechanisms
- 75%: 3-5 hypotheses complete, each grounded in evidence
- 100%: Hypotheses reviewed for distinctiveness and completeness

Develop 3-5 distinct hypotheses that could explain the phenomenon. Each hypothesis should:

- Provide a mechanistic explanation (not just description)
- Be distinguishable from other hypotheses
- Draw on evidence from the literature synthesis
- Consider different levels of explanation (molecular, cellular, systemic, population, etc.)

**Strategies for generating hypotheses:**
- Apply known mechanisms from analogous systems
- Consider multiple causative pathways
- Explore different scales of explanation
- Question assumptions in existing explanations
- Combine mechanisms in novel ways

### 5. Evaluate Hypothesis Quality

**Progress Milestones:**
- 25%: Quality rubric applied to first hypothesis
- 50%: All hypotheses scored on 10-point scale
- 75%: Strengths and weaknesses documented for each
- 100%: Hypotheses ranked, weak ones (<5/10) deprioritized

Assess each hypothesis against the quality rubric below and criteria from `references/hypothesis_quality_criteria.md`.

**Hypothesis Quality Rubric** (10-point scale, 2 points per criterion):

| Criterion | 0 | 1 | 2 |
|-----------|---|---|---|
| **Testability** | Cannot be tested empirically | Testable with significant difficulty | Clear experimental approach exists |
| **Falsifiability** | No observation could disprove | Vague falsification criteria | Specific falsifying observations defined |
| **Parsimony** | Unnecessarily complex | Moderate complexity | Simplest fit to evidence |
| **Explanatory Power** | Explains <50% of observations | Explains 50-80% | Explains >80% of observations |
| **Distinctiveness** | Indistinguishable from alternatives | Partially distinguishable | Unique, testable predictions |

**Scoring thresholds:**
- **Strong hypothesis:** ≥8/10 → Prioritize for experimental testing
- **Viable hypothesis:** 5-7/10 → Include with noted limitations
- **Weak hypothesis:** <5/10 → Document but deprioritize

**Required for each hypothesis:**
- Quality score with criterion breakdown
- ≥2 specific strengths with evidence
- ≥2 specific weaknesses or limitations
- Comparison to at least one competing hypothesis

### 6. Design Experimental Tests

**Progress Milestones:**
- 25%: Primary outcome and controls defined for first hypothesis
- 50%: Experimental designs drafted for all viable hypotheses
- 75%: Sample size rationale and statistical approach added
- 100%: Confound mitigation documented, designs finalized

For each viable hypothesis (score ≥5/10), propose specific experiments or studies to test it. Consult `references/experimental_design_patterns.md` for common approaches.

**Minimum Experimental Design Requirements:**

| Element | Requirement |
|---------|-------------|
| Primary outcome | 1-2 clearly defined |
| Controls | ≥2 (positive + negative) |
| Sample size rationale | Power calculation or literature precedent |
| Statistical approach | Pre-specified test + effect size measure |
| Confound mitigation | ≥3 potential confounds addressed |

**Replication Standards** (see [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §3):
- In vitro: ≥3 biological replicates, ≥3 technical replicates
- In vivo: 6-10 animals per group (per power calculation)
- Human studies: Per IRB-approved power calculation

**Consider multiple approaches:**
- Laboratory experiments (in vitro, in vivo, computational)
- Observational studies (cross-sectional, longitudinal, case-control)
- Clinical trials (if applicable)
- Natural experiments or quasi-experimental designs

### 7. Formulate Testable Predictions

**Progress Milestones:**
- 25%: ≥2 predictions drafted for first hypothesis
- 50%: Predictions drafted for all viable hypotheses
- 75%: Direction/magnitude and conditions specified
- 100%: Distinguishing and falsifying predictions identified

For each hypothesis, generate specific, quantitative predictions:

- State what should be observed if the hypothesis is correct
- Specify expected direction and magnitude of effects when possible
- Identify conditions under which predictions should hold
- Distinguish predictions between competing hypotheses
- Note predictions that would falsify the hypothesis

### 8. Present Structured Output

**Progress Milestones:**
- 25%: LaTeX document structure created from template
- 50%: Main text drafted (executive summary + hypothesis boxes)
- 75%: Appendices complete, citations integrated
- 100%: Visual schematic added, document compiles without errors

Generate a professional LaTeX document using the template in `assets/hypothesis_report_template.tex`. The report should be well-formatted with colored boxes for visual organization and divided into a concise main text with comprehensive appendices.

**Document Structure:**

**Main Text (Maximum 4 pages):**
1. **Executive Summary** - Brief overview in summary box (0.5-1 page)
2. **Competing Hypotheses** - Each hypothesis in its own colored box with brief mechanistic explanation and key evidence (2-2.5 pages for 3-5 hypotheses)
   - **IMPORTANT:** Use `\newpage` before each hypothesis box to prevent content overflow
   - Each box should be ≤0.6 pages maximum
3. **Testable Predictions** - Key predictions in amber boxes (0.5-1 page)
4. **Critical Comparisons** - Priority comparison boxes (0.5-1 page)

Keep main text highly concise - only the most essential information. All details go to appendices.

**Page Break Strategy:**
- Always use `\newpage` before hypothesis boxes to ensure they start on fresh pages
- This prevents content from overflowing off page boundaries
- LaTeX boxes (tcolorbox) do not automatically break across pages

**Appendices (Comprehensive, Detailed):**
- **Appendix A:** Comprehensive literature review with extensive citations
- **Appendix B:** Detailed experimental designs with full protocols
- **Appendix C:** Quality assessment tables and detailed evaluations
- **Appendix D:** Supplementary evidence and analogous systems

**Colored Box Usage:**

Use the custom box environments from `hypothesis_generation.sty`:

- `hypothesisbox1` through `hypothesisbox5` - For each competing hypothesis (blue, green, purple, teal, orange)
- `predictionbox` - For testable predictions (amber)
- `comparisonbox` - For critical comparisons (steel gray)
- `evidencebox` - For supporting evidence highlights (light blue)
- `summarybox` - For executive summary (blue)

**Each hypothesis box should contain (keep concise for 4-page limit):**
- **Mechanistic Explanation:** 1-2 brief paragraphs (6-10 sentences max) explaining HOW and WHY
- **Key Supporting Evidence:** 2-3 bullet points with citations (most important evidence only)
- **Core Assumptions:** 1-2 critical assumptions

All detailed explanations, additional evidence, and comprehensive discussions belong in the appendices.

**Critical Overflow Prevention:**
- Insert `\newpage` before each hypothesis box to start it on a fresh page
- Keep each complete hypothesis box to ≤0.6 pages (approximately 15-20 lines of content)
- If content exceeds this, move additional details to Appendix A
- Never let boxes overflow off page boundaries - this creates unreadable PDFs

**Citation Requirements:**

Aim for extensive citation to support all claims:
- **Main text:** 10-15 key citations for most important evidence only (keep concise for 4-page limit)
- **Appendix A:** 40-70+ comprehensive citations covering all relevant literature
- **Total target:** 50+ references in bibliography

Main text citations should be selective - cite only the most critical papers. All comprehensive citation and detailed literature discussion belongs in the appendices. Use `\citep{author2023}` for parenthetical citations.

**LaTeX Compilation:**

The template requires XeLaTeX or LuaLaTeX for proper rendering:

```bash
xelatex hypothesis_report.tex
bibtex hypothesis_report
xelatex hypothesis_report.tex
xelatex hypothesis_report.tex
```

**Required packages:** The `hypothesis_generation.sty` style package must be in the same directory or LaTeX path. It requires: tcolorbox, xcolor, fontspec, fancyhdr, titlesec, enumitem, booktabs, natbib.

**Ensuring Proper Page Layout:**

Follow these guidelines for professional document formatting:

1. **Size Each Box Appropriately:** Each hypothesis box fits comfortably on a single page when content stays within ~0.6 pages:
   - Mechanistic explanation: 1-2 brief paragraphs (6-10 sentences max)
   - Key evidence: 2-3 bullet points
   - Core assumptions: 1-2 items
   - Move additional details to appendices

2. **Use Strategic Page Breaks:** Start substantial boxes on fresh pages with `\newpage`:
   ```latex
   \newpage
   \begin{hypothesisbox1}[Hypothesis 1: Title]
   % Content here
   \end{hypothesisbox1}
   ```

3. **Split Long Content Across Sections:** For hypotheses requiring extensive explanation:
   - Main text box: Brief mechanistic overview + 2-3 key evidence points
   - Appendix A: Detailed mechanism, comprehensive evidence, extended discussion

4. **Maintain the 4-Page Main Text Limit:** Allocate space intentionally:
   - Executive summary: 0.5-1 page
   - Each hypothesis box: ≤0.6 pages
   - Predictions and comparisons: 0.5-1 page each

5. **Check Remaining Space:** Before each new box, verify sufficient page space remains. If less than 0.6 pages remain, use `\newpage`.

6. **Structure Appendices Clearly:** Use `\newpage` between major appendix sections for clean organization.

**Quick Reference:** See `assets/FORMATTING_GUIDE.md` for detailed examples of all box types, color schemes, and common formatting patterns.

## Workflow Transitions

### Stage 1 → 2: Understand Phenomenon → Literature Search
**Exit criteria:**
□ Core observation/question clearly articulated in 1-2 sentences
□ Scope and boundaries defined (what's included/excluded)
□ Relevant scientific domain(s) identified
□ Known vs. unknown aspects documented
□ Initial search terms generated (≥5 keywords/phrases)

### Stage 2 → 3: Literature Search → Synthesize Evidence
**Exit criteria:**
□ ≥3 databases searched (per QUANTIFICATION_THRESHOLDS.md §1)
□ ≥40 papers retrieved, ≥70 for comprehensive reviews
□ Search saturation achieved (<5% new papers in final iteration)
□ ≥60% papers from last 5 years
□ Both supporting and contradictory evidence identified

### Stage 3 → 4: Synthesize Evidence → Generate Hypotheses
**Exit criteria:**
□ Current understanding summarized in ≤1 page
□ ≥2 alternative viewpoints documented
□ Key gaps in knowledge identified (≥3)
□ Relevant mechanisms/theories catalogued
□ Analogies from related systems noted

### Stage 4 → 5: Generate Hypotheses → Evaluate Quality
**Exit criteria:**
□ 3-5 distinct hypotheses generated
□ Each hypothesis provides mechanistic explanation
□ Hypotheses are mutually distinguishable
□ Each hypothesis grounded in literature evidence
□ Multiple levels of explanation considered

### Stage 5 → 6: Evaluate Quality → Design Experiments
**Exit criteria:**
□ All hypotheses scored on 10-point quality rubric
□ Each score includes criterion breakdown
□ ≥1 hypothesis scores ≥8/10 (strong)
□ All hypotheses score ≥5/10 (viable) or marked as deprioritized
□ Strengths and weaknesses documented for each

### Stage 6 → 7: Design Experiments → Formulate Predictions
**Exit criteria:**
□ Experimental design for each viable hypothesis (score ≥5/10)
□ 1-2 primary outcomes defined per experiment
□ ≥2 controls per experiment (positive + negative)
□ Sample size rationale provided
□ Statistical approach pre-specified
□ ≥3 potential confounds addressed per design

### Stage 7 → 8: Formulate Predictions → Present Output
**Exit criteria:**
□ ≥2 specific predictions per hypothesis
□ Direction and magnitude of expected effects stated
□ Conditions under which predictions hold specified
□ Distinguishing predictions between hypotheses identified
□ Falsifying observations defined

### Stage 8 Complete: Present Structured Output
**Exit criteria:**
□ LaTeX document compiles without errors
□ Main text ≤4 pages with executive summary
□ Each hypothesis in colored box (≤0.6 pages each)
□ No page overflow (content stays within boundaries)
□ ≥40 citations in bibliography (≥10-15 in main text)
□ ≥1 visual schematic included
□ Appendices contain comprehensive details

## Quality Standards

Ensure all generated hypotheses meet these quantified standards:

| Standard | Minimum Requirement | Target |
|----------|---------------------|--------|
| **Evidence-based** | ≥3 citations per hypothesis | ≥5 citations from peer-reviewed sources |
| **Testable** | ≥2 specific predictions per hypothesis | ≥3 with expected effect sizes |
| **Mechanistic** | Causal pathway described | Multi-step mechanism with intermediates |
| **Comprehensive** | ≥3 competing hypotheses | 3-5 spanning mechanistic levels |
| **Rigorous** | Experimental design for each hypothesis | Design with power calculation |

**Report Completeness Checklist:**
- [ ] 3-5 competing hypotheses presented
- [ ] All hypotheses score ≥5/10 on quality rubric
- [ ] ≥1 hypothesis scores ≥8/10 (strong)
- [ ] ≥40 citations in bibliography
- [ ] ≥1 visual schematic included
- [ ] Experimental designs for all viable hypotheses

## Resources

### references/

- `hypothesis_quality_criteria.md` - Framework for evaluating hypothesis quality (testability, falsifiability, parsimony, explanatory power, scope, consistency)
- `experimental_design_patterns.md` - Common experimental approaches across domains (RCTs, observational studies, lab experiments, computational models)
- `literature_search_strategies.md` - Effective search techniques for PubMed and general scientific sources

### assets/

- `hypothesis_generation.sty` - LaTeX style package providing colored boxes, professional formatting, and custom environments for hypothesis reports
- `hypothesis_report_template.tex` - Complete LaTeX template with main text structure and comprehensive appendix sections
- `FORMATTING_GUIDE.md` - Quick reference guide with examples of all box types, color schemes, citation practices, and troubleshooting tips

### Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

When preparing hypothesis-driven research for publication, consult these related skills:

**venue-templates**: Writing style guidance
- `venue_writing_styles.md` - Master guide comparing styles across venues
- Venue-specific guides for Nature/Science, Cell Press, medical journals, and ML/CS conferences
- `reviewer_expectations.md` - What reviewers look for when evaluating research hypotheses

**statistical-analysis**: Quantitative planning
- Power analysis and sample size estimation for testing hypotheses
- Test selection based on data characteristics
- Effect size calculation for meaningful hypothesis evaluation

**reproducible-research**: Experimental documentation
- Pre-registration of hypotheses and analysis plans
- Project structure for hypothesis-driven research
- Data management for experimental validation
