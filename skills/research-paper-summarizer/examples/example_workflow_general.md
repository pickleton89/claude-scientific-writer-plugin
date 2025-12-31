# Example Workflow: General Research Paper

This document walks through the complete summarization workflow for a general research paper using the chunked subagent pipeline.

---

## Scenario

**Input**: A 24-page primary research paper on aptamer-siRNA chimeras
**Article Type**: General Research
**Processing Mode**: Chunked (>12 pages)

---

## Phase 0: Initialization

### User provides PDF

```
User: Summarize this paper for me
[Uploads chen2024_aptamer_sirna_chimeras.pdf]
```

### Claude reads and analyzes PDF

```
Claude: I've received your paper. Let me analyze it...

This paper has 24 pages. Using Chunked processing mode.

Processing: chen2024_aptamer_sirna_chimeras.pdf (24 pages)
Mode: Chunked subagent pipeline
```

---

## Phase 1a: Article Type Selection

```
Claude: What type of article is this?

1. General research paper
2. Review article / meta-analysis
3. Computational biology / bioinformatics
4. Cell & molecular biology

User: 1
```

---

## Phase 1b: Section Detection

Claude runs section detection on the PDF:

```json
{
  "abstract": {"start": 1, "end": 1},
  "introduction": {"start": 1, "end": 3},
  "methods": {"start": 4, "end": 8},
  "results": {"start": 9, "end": 17},
  "discussion": {"start": 17, "end": 21},
  "references": {"start": 22, "end": 24}
}
```

---

## Phase 1c: Skeleton Creation

Claude creates the summary skeleton file:

```
Creating summary file: chen2024_aptamer_sirna_chimeras_summary.md
Template: templates/summary-skeleton.md
Article type customizations applied
```

---

## Phase 1d: Subagent Pipeline

### Agent 1: Overview Agent

```
[■□□□□□] Step 1/6: Extracting overview...
  ◉ Overview in progress
  ○ Methods pending
  ○ Results pending
  ○ Critical analysis pending
  ○ Context pending
  ○ Synthesis pending

Reading pages 1-3 (Abstract + Introduction)
Writing to: executive_summary, background, hypothesis sections
```

### Agent 2: Methods Agent

```
[■■□□□□] Step 2/6: Analyzing methods...
  ✓ Overview extracted
  ◉ Methods in progress
  ○ Results pending
  ○ Critical analysis pending
  ○ Context pending
  ○ Synthesis pending

Reading pages 4-8 (Methods section)
Writing to: methods sections
```

### Agent 3: Results Agent

```
[■■■□□□] Step 3/6: Analyzing results...
  ✓ Overview extracted
  ✓ Methods analyzed
  ◉ Results in progress
  ○ Critical analysis pending
  ○ Context pending
  ○ Synthesis pending

Reading pages 9-17 (Results section)
Writing to: key_findings, key_figures, statistics sections
```

### Agent 4: Critique Agent

```
[■■■■□□] Step 4/6: Critical analysis...
  ✓ Overview extracted
  ✓ Methods analyzed
  ✓ Results analyzed
  ◉ Critical analysis in progress
  ○ Context pending
  ○ Synthesis pending

Reading pages 17-21 (Discussion section)
Writing to: strengths, limitations, red_flags sections
```

### Agent 5: Context Agent

```
[■■■■■□] Step 5/6: Assessing context...
  ✓ Overview extracted
  ✓ Methods analyzed
  ✓ Results analyzed
  ✓ Critical analysis complete
  ◉ Context in progress
  ○ Synthesis pending

Reading pages 1-3, 17-21 (Introduction + Discussion)
Writing to: field_impact, future_directions sections
```

### Agent 6: Synthesis Agent

```
[■■■■■■] Step 6/6: Generating synthesis...
  ✓ Overview extracted
  ✓ Methods analyzed
  ✓ Results analyzed
  ✓ Critical analysis complete
  ✓ Context assessed
  ◉ Synthesis in progress

Reading: summary file only (no PDF)
Writing to: insights, takeaways, synthesis sections
```

---

## Phase 1e: Summary Complete

```
Claude: ✓ Summary complete!

Saved to: chen2024_aptamer_sirna_chimeras_summary.md

All sections completed:
  ✓ Executive Summary
  ✓ Background & Motivation
  ✓ Experimental Approach
  ✓ Results
  ✓ Critical Analysis
  ✓ Bigger Picture
  ✓ Creative Insights
  ✓ Actionable Takeaways
  ✓ One-Paragraph Synthesis
```

---

## Phase 2: Visual Output Selection

```
Claude: Which visual output format(s) would you like?

1. Interactive HTML report (web presentation)
2. PDF summary (printable document)
3. SVG infographic (visual poster)
4. Multiple formats
5. None (markdown summary only)

User: 1
```

---

## Phase 2b: HTML Generation

```
Claude: Generating Interactive HTML report...

Reading: chen2024_aptamer_sirna_chimeras_summary.md
Applying: prompts/html-report.md template
Using: Oligon brand colors (see oligon-brand skill)

✓ HTML report generated!
Saved to: chen2024_aptamer_sirna_chimeras_report.html

Features:
- Sticky navigation bar
- Collapsible sections
- Statistical badges with significance styling
- Key figures table
- Critical analysis callouts
```

---

## Complete File Outputs

After the workflow completes, the user has:

```
chen2024_aptamer_sirna_chimeras.pdf          (original)
chen2024_aptamer_sirna_chimeras_summary.md   (markdown summary)
chen2024_aptamer_sirna_chimeras_report.html  (HTML report)
```

---

## Timing Expectations

| Phase | Typical Duration |
|-------|------------------|
| Initialization | ~10 seconds |
| Article type selection | User interaction |
| Section detection | ~30 seconds |
| Subagent pipeline (6 agents) | ~3-5 minutes |
| Visual output generation | ~1-2 minutes |
| **Total** | **~5-8 minutes** |

*Note: Timing varies based on paper length and complexity.*

---

## Troubleshooting This Workflow

### If section detection fails

Claude will use page-ratio fallback:
```
Section detection incomplete. Using estimated page ranges:
- Introduction: pages 1-4 (first 15%)
- Methods: pages 4-7 (15-30%)
- Results: pages 7-16 (30-65%)
- Discussion: pages 16-21 (65-85%)
```

### If a subagent fails

Claude retries once, then falls back:
```
Results agent failed to complete. Retrying...
[Retry successful] or [Falling back to Standard Mode]
```

### If context is exceeded

Claude reduces page range:
```
Context limit reached. Reducing page range for methods agent.
Reading pages 4-6 (reduced from 4-8)
```
