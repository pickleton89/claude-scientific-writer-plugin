# Content Reviewer Implementation Plan

> **Status:** Planning
> **Created:** 2026-01-21
> **Author:** Discussion between user and Claude
> **Scope:** Multi-agent content review system for all visual outputs

---

## Executive Summary

This document outlines the implementation of a **Content Reviewer** skill that examines visual outputs (slides, figures, documents, schematics) for correctness, guideline compliance, and visual defects. The system uses Claude's vision capabilities to detect issues like overlapping text, misaligned figures, and brand inconsistencies.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Skill + Specialized Subagents | Manageable context per agent, parallel execution |
| Guidelines | Reference existing docs | No duplication, single source of truth |
| Severity | Tiered (Error/Warning/Info) | Prioritized actionable feedback |
| Integration | Optional post-generation prompt | User controls when review runs |
| User Context | Accept venue/audience info | Tailored checks for specific requirements |

### Goals

1. **Catch visual defects** before delivery (text overflow, misalignment, overlap)
2. **Enforce design standards** (Oligon brand, accessibility, publication specs)
3. **Provide actionable feedback** with severity tiers
4. **Support user context** (venue-specific requirements, audience needs)

---

## Part 1: Problem Statement

### Current State

Visual generation skills (`pptx`, `plotting-libraries`, `scientific-schematics`, `scientific-slides`) produce outputs without systematic quality review. Issues discovered:

| Issue Type | Example | Impact |
|------------|---------|--------|
| Text overflow | Bullet extends beyond slide margin | Unprofessional appearance |
| Misalignment | Figure not centered, uneven spacing | Visual distraction |
| Contrast violation | Light text on light background | Accessibility failure |
| Brand inconsistency | Wrong blue shade, non-standard font | Corporate identity breach |
| Missing elements | No axis labels, missing legend | Scientific incompleteness |

### Inspiration

This approach was inspired by a YouTube demonstration of using Claude's vision to review PPTX output for quality issues. The multimodal capability enables "visual inspection" that catches issues code-based validation cannot.

### Value Proposition

- **Quality gate** before final delivery
- **Reduced rework** by catching issues early
- **Consistent standards** across all outputs
- **Accessibility compliance** verified automatically

---

## Part 2: Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        /review-content                               │
│                     (Orchestrating Skill)                            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  1. Detect output types in target path                       │    │
│  │  2. Parse user context (venue, audience, concerns)           │    │
│  │  3. Dispatch appropriate subagent(s)                         │    │
│  │  4. Aggregate results into unified report                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  review-slides   │    │  review-figures  │    │  review-docs     │
│    subagent      │    │    subagent      │    │    subagent      │
│                  │    │                  │    │                  │
│ • Vision checks  │    │ • Vision checks  │    │ • Vision checks  │
│ • Rule checks    │    │ • Rule checks    │    │ • Rule checks    │
│ • Brand verify   │    │ • Data verify    │    │ • Structure      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │  Unified Report  │
                        │                  │
                        │ • Pass/Fail      │
                        │ • Issues by file │
                        │ • Severity tiers │
                        └──────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Orchestrating Skill** | Entry point, type detection, context parsing, result aggregation |
| **review-slides subagent** | PPTX, PNG slides - layout, text, brand, accessibility |
| **review-figures subagent** | matplotlib, ggplot outputs - data viz standards, labels, colors |
| **review-docs subagent** | DOCX, PDF - structure, formatting, citations, figure placement |
| **review-schematics subagent** | Diagrams, flowcharts - clarity, connections, labels |

### Why This Architecture?

| Alternative | Why Not Chosen |
|-------------|----------------|
| Single monolithic agent | Context too large, slow, single point of failure |
| Per-skill internal checker | Duplicated logic, inconsistent standards |
| Pure rule-based validation | Can't catch visual defects (overlap, alignment) |

**Chosen approach benefits:**
- Focused context per subagent (loads only relevant guidelines)
- Parallel execution when reviewing mixed output types
- Single entry point for user simplicity
- Extensible (add new subagents for new output types)

---

## Part 3: Guideline Reference Strategy

### Principle: Reference, Don't Duplicate

Each subagent references existing documentation rather than maintaining its own copy:

| Subagent | Primary References |
|----------|-------------------|
| **review-slides** | `SCIENTIFIC_OUTPUT_DESIGN_SPEC.md`, `oligon-brand/SKILL.md`, `visual-design/references/publication_specs.md` |
| **review-figures** | `visual-design/SKILL.md`, `plotting-libraries/SKILL.md`, `oligon-brand/references/color_system.md` |
| **review-docs** | `visual-design/references/publication_specs.md`, venue-specific requirements from `venue-templates/` |
| **review-schematics** | `scientific-schematics/SKILL.md`, `visual-design/SKILL.md` |

### Key Documents to Reference

#### SCIENTIFIC_OUTPUT_DESIGN_SPEC.md
- Core design principles (content over decoration)
- Visual hierarchy specifications
- Color system rules
- Quality checklist

#### oligon-brand/SKILL.md
- Brand colors (hex values)
- Typography standards
- Logo usage rules

#### visual-design/references/publication_specs.md
- Journal-specific requirements (Nature, Science, Cell, etc.)
- Resolution requirements
- Font embedding rules

---

## Part 4: Severity Tier Definitions

### Tier Definitions

```
🔴 ERROR   - Must fix before delivery
             Output is incorrect, inaccessible, or unusable

🟡 WARNING - Should fix; impacts quality
             Output works but doesn't meet standards

🔵 INFO    - Consider fixing; enhancement opportunity
             Stylistic suggestion, not a defect
```

### Classification Matrix

| Issue | Severity | Rationale |
|-------|----------|-----------|
| Text cut off / invisible | 🔴 ERROR | Content loss |
| Text overlapping other elements | 🔴 ERROR | Unreadable |
| Missing required element (axis label, legend) | 🔴 ERROR | Scientific incompleteness |
| Contrast ratio < 3:1 | 🔴 ERROR | Accessibility failure |
| Contrast ratio 3:1-4.5:1 | 🟡 WARNING | Partial accessibility |
| Wrong brand color used | 🟡 WARNING | Brand inconsistency |
| Font not in approved list | 🟡 WARNING | Brand inconsistency |
| Minor misalignment (< 5px) | 🟡 WARNING | Visual quality |
| Significant misalignment (≥ 5px) | 🔴 ERROR | Obvious defect |
| Non-colorblind-safe palette | 🟡 WARNING | Accessibility concern |
| Suboptimal whitespace | 🔵 INFO | Design enhancement |
| Could use better hierarchy | 🔵 INFO | Stylistic suggestion |
| Alternative layout suggested | 🔵 INFO | Enhancement opportunity |

### Report Scoring

```
Overall Status:
- PASS: 0 errors, ≤3 warnings
- NEEDS ATTENTION: 0 errors, >3 warnings OR ≥1 error
- FAIL: ≥3 errors OR any critical error (data accuracy issue)
```

---

## Part 5: Subagent Specifications

### 5.1 review-slides Subagent

**Purpose:** Review presentation slides (PPTX, PNG exports) for layout, text, brand compliance, and accessibility.

**Input:**
- File path(s) to slide images or PPTX
- User context (optional): venue, audience, specific concerns

**References Loaded:**
- `SCIENTIFIC_OUTPUT_DESIGN_SPEC.md` (sections: Visual Hierarchy, Color System, Typography)
- `oligon-brand/references/color_system.md`
- `oligon-brand/references/typography.md`

**Vision Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Text overflow | Vision: "Is any text cut off at edges?" | 🔴 ERROR |
| Text overlap | Vision: "Is text overlapping other text or images?" | 🔴 ERROR |
| Alignment | Vision: "Are elements aligned consistently?" | 🟡 WARNING |
| Visual balance | Vision: "Is content well-distributed?" | 🔵 INFO |
| Readability | Vision: "Is all text clearly readable?" | 🔴/🟡 varies |

**Rule Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Font size ≥ 18pt body | Extract from PPTX or estimate from image | 🟡 WARNING |
| Title font ≥ 32pt | Extract or estimate | 🟡 WARNING |
| Brand colors used | Color extraction, compare to hex values | 🟡 WARNING |
| Contrast ratio ≥ 4.5:1 | Calculate from extracted colors | 🔴/🟡 varies |
| Max 6 bullets per slide | Count bullet points | 🔵 INFO |
| Image resolution ≥ 150 DPI | Check image metadata | 🟡 WARNING |

**Output Format:**

```markdown
## Slide Review: {filename}

**Status:** PASS | NEEDS ATTENTION | FAIL
**Issues Found:** {count}

### 🔴 Errors ({count})
- **Text overflow** (slide 3): Bullet point 4 extends beyond right margin
- **Low contrast** (slide 7): Subtitle text has 2.8:1 contrast (needs 4.5:1)

### 🟡 Warnings ({count})
- **Font size** (slide 2): Body text appears to be ~16pt (recommend ≥18pt)
- **Brand color** (slide 5): Blue used is #1E90FF, should be #2DB2E8

### 🔵 Info ({count})
- **Whitespace** (slide 4): Consider adding more margin below title
```

---

### 5.2 review-figures Subagent

**Purpose:** Review data visualizations (matplotlib, ggplot, seaborn outputs) for scientific standards, labels, and accessibility.

**Input:**
- File path(s) to figure images (PNG, PDF, SVG)
- User context (optional): target journal, figure type

**References Loaded:**
- `visual-design/SKILL.md` (sections: data visualization)
- `visual-design/references/publication_specs.md`
- `plotting-libraries/SKILL.md` (quality checklist section)
- `oligon-brand/references/color_system.md`

**Vision Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Label legibility | Vision: "Are all labels readable?" | 🔴 ERROR |
| Legend placement | Vision: "Is legend clear and not overlapping data?" | 🟡 WARNING |
| Axis clarity | Vision: "Are axes clearly labeled with units?" | 🔴 ERROR |
| Data point visibility | Vision: "Are all data points visible and distinguishable?" | 🟡 WARNING |
| Overall composition | Vision: "Is the figure well-composed and balanced?" | 🔵 INFO |

**Rule Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Axis labels present | Vision + pattern matching | 🔴 ERROR |
| Units included | Check for unit notation in labels | 🟡 WARNING |
| Error bars present (if statistical) | Vision: "Are error bars shown?" | 🟡 WARNING |
| Colorblind-safe palette | Extract colors, check against Okabe-Ito | 🟡 WARNING |
| Resolution ≥ 300 DPI (publication) | Check metadata | 🟡 WARNING |
| No 3D effects | Vision: "Are there 3D chart effects?" | 🟡 WARNING |

**Venue-Specific Checks:**

When user specifies target venue:

| Venue | Additional Checks |
|-------|------------------|
| Nature | Single column ≤ 89mm width, 600 DPI for line art |
| Science | CMYK ready, specific font requirements |
| Cell | Caption requirements, panel labeling |
| Conference | Lower resolution acceptable (150 DPI) |

**Output Format:**

```markdown
## Figure Review: {filename}

**Status:** PASS | NEEDS ATTENTION | FAIL
**Target Venue:** {venue or "General"}
**Issues Found:** {count}

### 🔴 Errors ({count})
- **Missing axis label**: Y-axis has no label
- **Label overlap**: Legend overlaps data points in upper right

### 🟡 Warnings ({count})
- **No error bars**: Statistical data shown without error bars
- **Color palette**: Not colorblind-safe (red-green combination detected)

### 🔵 Info ({count})
- **Resolution**: 200 DPI is acceptable for presentations, increase to 300+ for publication
```

---

### 5.3 review-docs Subagent

**Purpose:** Review documents (DOCX, PDF) for structure, formatting, citations, and figure placement.

**Input:**
- File path(s) to document files
- User context (optional): document type, target venue

**References Loaded:**
- `visual-design/references/publication_specs.md`
- Venue-specific templates from `venue-templates/`

**Vision Checks (for PDF):**

| Check | Method | Severity |
|-------|--------|----------|
| Page layout consistency | Vision: "Are margins and headers consistent?" | 🟡 WARNING |
| Figure placement | Vision: "Are figures well-positioned and not cutting off?" | 🔴 ERROR |
| Header/footer alignment | Vision: "Are headers/footers consistent?" | 🔵 INFO |
| Text readability | Vision: "Is body text readable throughout?" | 🔴 ERROR |

**Structure Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Section structure complete | Parse headings, check required sections | 🟡 WARNING |
| Figure numbering sequential | Extract figure captions, verify sequence | 🔴 ERROR |
| Citation format consistent | Pattern match citation style | 🟡 WARNING |
| Page numbers present | Check footer content | 🔵 INFO |

**Output Format:**

```markdown
## Document Review: {filename}

**Status:** PASS | NEEDS ATTENTION | FAIL
**Document Type:** {type}
**Issues Found:** {count}

### 🔴 Errors ({count})
- **Figure numbering**: Figure 3 referenced but Figure 2 is missing
- **Figure cutoff**: Figure on page 7 extends beyond margin

### 🟡 Warnings ({count})
- **Citation format**: Inconsistent citation style (APA and MLA mixed)

### 🔵 Info ({count})
- **Header**: Consider adding running title to headers
```

---

### 5.4 review-schematics Subagent

**Purpose:** Review diagrams, flowcharts, and schematics for clarity, connections, and label completeness.

**Input:**
- File path(s) to schematic images
- User context (optional): diagram type, purpose

**References Loaded:**
- `scientific-schematics/SKILL.md`
- `visual-design/SKILL.md`

**Vision Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| Arrow clarity | Vision: "Are all arrows clear and properly directed?" | 🟡 WARNING |
| Node spacing | Vision: "Is there adequate spacing between elements?" | 🟡 WARNING |
| Label overlap | Vision: "Are any labels overlapping each other or nodes?" | 🔴 ERROR |
| Connection completeness | Vision: "Do all connections have clear endpoints?" | 🔴 ERROR |
| Text legibility | Vision: "Are all labels readable?" | 🔴 ERROR |

**Rule Checks:**

| Check | Method | Severity |
|-------|--------|----------|
| All nodes labeled | Vision: count unlabeled shapes | 🟡 WARNING |
| Consistent shape usage | Vision: "Are shapes used consistently for same concepts?" | 🔵 INFO |
| Flow direction clear | Vision: "Is there a clear flow direction?" | 🟡 WARNING |
| No orphan nodes | Vision: "Are there disconnected elements?" | 🟡 WARNING |

**Output Format:**

```markdown
## Schematic Review: {filename}

**Status:** PASS | NEEDS ATTENTION | FAIL
**Diagram Type:** {detected type}
**Issues Found:** {count}

### 🔴 Errors ({count})
- **Label overlap**: "Process A" label overlaps with arrow
- **Disconnected node**: Box in lower right has no connections

### 🟡 Warnings ({count})
- **Spacing**: Nodes in middle section are crowded
- **Unlabeled node**: Decision diamond at step 3 has no label

### 🔵 Info ({count})
- **Flow direction**: Consider adding directional indicators
```

---

## Part 6: User Context Integration

### Context Flow

```
User Input                    Skill Processing                  Subagent Behavior
─────────────────────────────────────────────────────────────────────────────────

"Review ./slides/            Parse context:                     Loads Nature-specific
 for Nature submission"      - venue: "Nature"                  requirements from
                             - audience: journal reviewers       publication_specs.md
                             - quality: publication
                                                                 Applies stricter
                                                                 resolution/format checks

─────────────────────────────────────────────────────────────────────────────────

"Check these figures,        Parse context:                     Adds colorblind checks
 colorblind reviewer         - concern: colorblind              as ERROR not WARNING
 on committee"               - audience: accessibility-focused
                                                                 Suggests Okabe-Ito
                                                                 palette alternatives

─────────────────────────────────────────────────────────────────────────────────

"Review presentation,        Parse context:                     Relaxes some formal
 internal team meeting"      - venue: internal                  requirements
                             - audience: colleagues
                             - quality: draft                    Focuses on content
                                                                 over strict formatting
```

### Context Parameters

| Parameter | Example Values | Effect on Review |
|-----------|----------------|------------------|
| **venue** | Nature, Science, Cell, conference, internal, poster | Loads venue-specific requirements |
| **audience** | reviewers, general public, experts, colorblind | Adjusts accessibility and complexity checks |
| **quality_level** | draft, presentation, publication | Adjusts severity thresholds |
| **specific_concerns** | "check text sizes", "verify brand colors" | Prioritizes mentioned checks |
| **ignore_checks** | "skip resolution check" | Disables specific validations |

### Context Parsing Examples

```
Input: "Review the slides in ./output/ - this is for a Nature submission"

Parsed:
{
  "path": "./output/",
  "venue": "Nature",
  "quality_level": "publication",
  "checks": {
    "resolution": {"min": 300, "recommended": 600},
    "format": "TIFF or PDF preferred",
    "dimensions": {"single_column": "89mm", "double_column": "183mm"}
  }
}
```

```
Input: "Check figures/fig1.png - I'm worried about colorblind accessibility"

Parsed:
{
  "path": "figures/fig1.png",
  "specific_concerns": ["colorblind"],
  "checks": {
    "colorblind_safe": {"severity": "error"},  # Elevated from warning
    "palette_suggestion": true
  }
}
```

---

## Part 7: Post-Generation Integration

### Optional Review Prompt

After a generation skill completes, offer review:

```
┌─────────────────────────────────────────────────────────────────────┐
│  [pptx skill completes]                                             │
│                                                                      │
│  Claude: I've generated 12 slides in ./presentation/                 │
│                                                                      │
│  Would you like me to review these for quality issues?               │
│                                                                      │
│  Options:                                                            │
│  • Yes, run full review                                              │
│  • Yes, quick check only (errors only)                               │
│  • No, I'll review manually                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation Approach

This is NOT a hook - it's guidance for generation skills to add this prompt at completion:

```markdown
## Post-Generation Prompt (for skill authors)

After generating output, add this interaction pattern:

1. Report what was generated and where
2. Ask if user wants quality review
3. If yes, invoke /review-content with appropriate context
```

Skills that should include this prompt:
- `pptx` (document-skills)
- `plotting-libraries`
- `scientific-schematics`
- `research-posters`
- `scientific-slides`

---

## Part 8: File Structure

### Skill Directory Structure

```
skills/content-reviewer/
├── SKILL.md                           # Main skill definition
├── README.md                          # Usage documentation
├── references/
│   ├── check_definitions.md           # Detailed check specifications
│   ├── severity_guidelines.md         # Classification rules
│   └── venue_requirements.md          # Venue-specific requirements summary
├── subagents/
│   ├── review-slides.md               # Slides review subagent definition
│   ├── review-figures.md              # Figures review subagent definition
│   ├── review-docs.md                 # Documents review subagent definition
│   └── review-schematics.md           # Schematics review subagent definition
├── prompts/
│   ├── orchestrator_prompt.md         # Main skill orchestration logic
│   ├── context_parser_prompt.md       # User context parsing instructions
│   └── report_aggregator_prompt.md    # Result aggregation format
└── examples/
    ├── example_slide_review.md        # Sample slide review output
    ├── example_figure_review.md       # Sample figure review output
    └── example_full_report.md         # Sample aggregated report
```

### Integration Points

```
skills/
├── content-reviewer/                  # NEW: This skill
│   └── ...
├── document-skills/                   # MODIFY: Add post-gen prompt
│   └── ...
├── plotting-libraries/                # MODIFY: Add post-gen prompt
│   └── ...
├── scientific-schematics/             # MODIFY: Add post-gen prompt
│   └── ...
└── shared/                            # EXISTING: May add review utilities
    └── ...
```

---

## Part 9: Implementation Plan

### Phase 1: Foundation (Skill Structure + First Subagent)

**Goal:** Create skill skeleton and implement review-slides subagent as proof of concept.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 1.1 | Create skill directory structure | None | `skills/content-reviewer/` skeleton |
| 1.2 | Write SKILL.md with orchestration logic | None | Main skill definition |
| 1.3 | Create check_definitions.md reference | None | Documented check specifications |
| 1.4 | Create severity_guidelines.md reference | None | Classification rules |
| 1.5 | Implement review-slides subagent | 1.1-1.4 | `subagents/review-slides.md` |
| 1.6 | Create context_parser_prompt.md | None | Context parsing logic |
| 1.7 | Test slide review with sample PPTX | 1.5 | Validated slide checks work |
| 1.8 | Create example_slide_review.md | 1.7 | Sample output documentation |

**Validation Criteria:**
- [ ] `/review-content ./slides/` detects slide files
- [ ] Vision-based checks identify text overflow
- [ ] Brand color verification works
- [ ] Report output matches specified format
- [ ] Severity tiers correctly applied

---

### Phase 2: Figure Review Subagent

**Goal:** Add figure review capability for data visualizations.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 2.1 | Implement review-figures subagent | Phase 1 | `subagents/review-figures.md` |
| 2.2 | Add colorblind palette detection | 2.1 | Color extraction and validation |
| 2.3 | Add venue-specific figure checks | 2.1 | Publication requirement validation |
| 2.4 | Test with matplotlib/ggplot outputs | 2.1-2.3 | Validated figure checks |
| 2.5 | Create example_figure_review.md | 2.4 | Sample output documentation |

**Validation Criteria:**
- [ ] Detects missing axis labels
- [ ] Identifies non-colorblind-safe palettes
- [ ] Applies venue-specific requirements when specified
- [ ] Error bars check works for statistical figures

---

### Phase 3: Document and Schematic Subagents

**Goal:** Complete subagent coverage for all output types.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 3.1 | Implement review-docs subagent | Phase 1 | `subagents/review-docs.md` |
| 3.2 | Implement review-schematics subagent | Phase 1 | `subagents/review-schematics.md` |
| 3.3 | Test document review with DOCX/PDF | 3.1 | Validated document checks |
| 3.4 | Test schematic review with diagrams | 3.2 | Validated schematic checks |
| 3.5 | Create remaining example files | 3.3-3.4 | Complete examples |

**Validation Criteria:**
- [ ] Document figure numbering validation works
- [ ] Schematic connection completeness detection works
- [ ] Citation format checking functions
- [ ] All four output types reviewable

---

### Phase 4: Orchestration and Aggregation

**Goal:** Complete skill with parallel dispatch and unified reporting.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 4.1 | Implement file type detection | Phase 1-3 | Automatic routing logic |
| 4.2 | Implement parallel subagent dispatch | 4.1 | Concurrent review execution |
| 4.3 | Create report_aggregator_prompt.md | 4.2 | Result combination logic |
| 4.4 | Implement unified report format | 4.3 | Single combined output |
| 4.5 | Test mixed-type directory review | 4.1-4.4 | End-to-end validation |
| 4.6 | Create example_full_report.md | 4.5 | Complete report example |

**Validation Criteria:**
- [ ] Mixed directories (slides + figures) reviewed together
- [ ] Parallel execution reduces total time
- [ ] Unified report combines all subagent findings
- [ ] Overall status correctly calculated

---

### Phase 5: User Context and Integration

**Goal:** Add context-aware review and generation skill integration.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 5.1 | Implement full context parsing | Phase 4 | venue_requirements.md reference |
| 5.2 | Add venue-specific check loading | 5.1 | Dynamic requirement application |
| 5.3 | Document post-generation integration | Phase 4 | Integration guide |
| 5.4 | Update pptx skill with review prompt | 5.3 | Modified document-skills |
| 5.5 | Update plotting-libraries with prompt | 5.3 | Modified plotting skill |
| 5.6 | End-to-end workflow testing | 5.4-5.5 | Validated integration |

**Validation Criteria:**
- [ ] "for Nature submission" triggers correct venue checks
- [ ] "colorblind reviewer" elevates accessibility checks
- [ ] Post-generation prompt appears and works
- [ ] Context flows correctly to subagents

---

### Phase 6: Documentation and Polish

**Goal:** Complete documentation, examples, and refinements.

| Step | Task | Dependencies | Deliverable |
|------|------|--------------|-------------|
| 6.1 | Write comprehensive README.md | Phase 5 | User documentation |
| 6.2 | Add troubleshooting section | 6.1 | Common issues guide |
| 6.3 | Create quick reference card | 6.1 | One-page usage summary |
| 6.4 | Update CHANGELOG.md | All phases | Release notes |
| 6.5 | Update SKILLS_DOCUMENTATION.md | 6.4 | Skill catalog entry |
| 6.6 | Final review and refinement | 6.1-6.5 | Production-ready skill |

**Validation Criteria:**
- [ ] README covers all use cases
- [ ] Examples demonstrate all features
- [ ] Documentation matches implementation
- [ ] Skill appears in catalog

---

## Part 10: Testing Strategy

### Test Categories

#### Vision Check Tests

Test with known-defective images:

| Test Case | Input | Expected Detection |
|-----------|-------|-------------------|
| Text overflow | Slide with text beyond margin | 🔴 ERROR: text overflow |
| Text overlap | Figure with overlapping labels | 🔴 ERROR: text overlap |
| Low contrast | Light gray text on white | 🔴 ERROR: contrast violation |
| Misalignment | Uncentered figure | 🟡 WARNING: misalignment |

#### Rule Check Tests

Test with controlled inputs:

| Test Case | Input | Expected Result |
|-----------|-------|-----------------|
| Missing axis label | matplotlib plot without ylabel | 🔴 ERROR: missing Y-axis label |
| Wrong brand color | Slide using #0000FF instead of #2DB2E8 | 🟡 WARNING: brand color |
| Figure numbering gap | Doc with Fig 1, Fig 3 (no Fig 2) | 🔴 ERROR: numbering gap |

#### Context Integration Tests

| Test Case | Context | Expected Behavior |
|-----------|---------|-------------------|
| Nature submission | venue: Nature | Applies 300+ DPI requirement |
| Colorblind concern | concern: colorblind | Elevates palette check to ERROR |
| Internal draft | quality: draft | Relaxes formatting requirements |

#### Aggregation Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Mixed directory | 5 slides + 3 figures | Both subagents run, combined report |
| All pass | Clean outputs | Status: PASS |
| Multiple errors | 3+ issues | Status: FAIL |

### Test File Creation

Create test assets in:

```
skills/content-reviewer/tests/
├── fixtures/
│   ├── slides/
│   │   ├── good_slide.png
│   │   ├── text_overflow.png
│   │   ├── low_contrast.png
│   │   └── wrong_brand_color.png
│   ├── figures/
│   │   ├── good_figure.png
│   │   ├── missing_labels.png
│   │   ├── red_green_palette.png
│   │   └── overlapping_legend.png
│   └── schematics/
│       ├── good_flowchart.png
│       ├── disconnected_node.png
│       └── overlapping_labels.png
└── expected_outputs/
    ├── slide_review_expected.md
    └── figure_review_expected.md
```

---

## Part 11: Success Criteria

### Phase 1 Complete When:
- [ ] Skill structure created with all directories
- [ ] review-slides subagent detects text overflow via vision
- [ ] Brand color verification working
- [ ] Report format matches specification

### Phase 2 Complete When:
- [ ] review-figures subagent detects missing labels
- [ ] Colorblind palette detection working
- [ ] Venue-specific checks applied

### Phase 3 Complete When:
- [ ] All four subagents implemented
- [ ] Document structure validation working
- [ ] Schematic connection checking working

### Phase 4 Complete When:
- [ ] File type detection routes correctly
- [ ] Parallel execution implemented
- [ ] Unified report aggregates all findings

### Phase 5 Complete When:
- [ ] Context parsing handles all parameters
- [ ] Post-generation integration documented
- [ ] At least one generation skill updated

### Phase 6 Complete When:
- [ ] README complete and accurate
- [ ] All examples created
- [ ] Skill in production use

### Overall Success Metrics:

| Metric | Target |
|--------|--------|
| Defect detection rate | >90% of intentional defects caught |
| False positive rate | <10% of flagged issues are non-issues |
| Review time | <30 seconds per file average |
| User adoption | Used in >50% of generation workflows |

---

## Part 12: Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Vision checks unreliable | Medium | High | Combine with rule-based checks, user verification |
| Context parsing misinterprets | Medium | Medium | Clear examples, confirmation for ambiguous input |
| Subagent context too large | Low | Medium | Careful reference selection, load only needed docs |
| False positives frustrate users | Medium | Medium | INFO tier for uncertain issues, easy dismissal |
| Missing defect types | Medium | Low | Extensible check system, user feedback loop |

---

## Appendix A: Report Format Template

```markdown
# Content Review Report

**Generated:** {timestamp}
**Reviewed:** {file_count} files in {path}
**Context:** {venue/audience if provided}

## Summary

| Status | Overall |
|--------|---------|
| Result | {PASS / NEEDS ATTENTION / FAIL} |
| Errors | {count} |
| Warnings | {count} |
| Info | {count} |

---

## Detailed Findings

### Slides ({count} files)

#### {filename}
**Status:** {status}

🔴 **Errors**
- {issue description} (location: {specific location})

🟡 **Warnings**
- {issue description}

🔵 **Info**
- {suggestion}

---

### Figures ({count} files)

#### {filename}
**Status:** {status}

{... same format ...}

---

## Recommendations

1. **High Priority:** {fix errors first}
2. **Medium Priority:** {address warnings}
3. **Optional:** {consider info suggestions}

---

*Review performed by content-reviewer skill v{version}*
```

---

## Appendix B: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    /review-content Quick Reference                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BASIC USAGE                                                         │
│  ───────────                                                         │
│  /review-content ./output/           Review all files in directory   │
│  /review-content fig1.png fig2.png   Review specific files           │
│                                                                      │
│  WITH CONTEXT                                                        │
│  ────────────                                                        │
│  "Review ./slides/ for Nature submission"                            │
│  "Check figures, colorblind reviewer on committee"                   │
│  "Review presentation for internal meeting"                          │
│                                                                      │
│  SEVERITY TIERS                                                      │
│  ──────────────                                                      │
│  🔴 ERROR   - Must fix (content loss, accessibility failure)         │
│  🟡 WARNING - Should fix (brand/style issues)                        │
│  🔵 INFO    - Consider (enhancement suggestions)                     │
│                                                                      │
│  STATUS                                                              │
│  ──────                                                              │
│  PASS           - 0 errors, ≤3 warnings                              │
│  NEEDS ATTENTION - 0 errors, >3 warnings OR 1-2 errors               │
│  FAIL           - ≥3 errors                                          │
│                                                                      │
│  SUPPORTED FILE TYPES                                                │
│  ────────────────────                                                │
│  Slides:     .pptx, .png (slide exports)                             │
│  Figures:    .png, .pdf, .svg (data visualizations)                  │
│  Documents:  .docx, .pdf                                             │
│  Schematics: .png, .svg (diagrams, flowcharts)                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-21 | Initial planning document |

---

## Related Documents

- `docs/SCIENTIFIC_OUTPUT_DESIGN_SPEC.md` — Design standards being checked
- `docs/IMAGE_GENERATION_REFACTORING_PLAN.md` — Similar implementation plan format
- `skills/visual-design/SKILL.md` — Design philosophy
- `skills/oligon-brand/SKILL.md` — Brand standards
