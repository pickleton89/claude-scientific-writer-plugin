# Skills Consolidation Implementation Plan

> **Status:** In Progress
> **Created:** 2026-01-02
> **Updated:** 2026-01-03
> **Scope:** 4 consolidation initiatives based on skills audit

---

## Executive Summary

This document outlines the implementation plan for consolidating and improving the claude-scientific-writer-plugin skills based on the January 2026 audit. Four initiatives are planned:

| # | Initiative | Impact | Effort | Status |
|---|------------|--------|--------|--------|
| 1 | Merge ScholarEval scoring into peer-review | Medium | Medium | ✅ Complete |
| 2 | Consolidate poster skills (latex + pptx) | High | High | ✅ Complete |
| 3 | Update document-skills to marketplace references | Low | Low | ✅ Complete |
| 4 | Default-on brand application for visual outputs | Medium | Medium | Pending |

---

## Initiative 1: Merge ScholarEval Scoring into Peer-Review

### Rationale

`peer-review` and `scholar-evaluation` both assess paper quality but serve different purposes:
- **peer-review**: Comprehensive 7-stage evaluation with actionable revision guidance
- **scholar-evaluation**: 8-dimension quantitative scoring with aggregate quality tier

Merging scoring as an optional mode reduces skill count and provides a unified evaluation experience.

### Design

#### New peer-review Structure

```
peer-review/
├── SKILL.md                    # Updated with scoring mode
├── references/
│   ├── ... (existing)
│   ├── scholareval_framework.md    # Migrated from scholar-evaluation
│   └── scoring_rubric.md           # Migrated from scholar-evaluation
├── scripts/
│   ├── ... (existing)
│   └── calculate_scores.py         # Migrated from scholar-evaluation
└── templates/
    └── scoring_report.md           # New template for scoring output
```

#### Output Modes

Add to peer-review workflow after Stage 1 (Initial Assessment):

```markdown
## Output Mode Selection

After initial assessment, select evaluation mode:

| Mode | Output | Best For |
|------|--------|----------|
| **Full Review** (default) | Structured review with Major/Minor comments | Journal submission, detailed feedback |
| **Scoring Only** | 8-dimension scores + quality tier (A-F) | Quick assessment, benchmarking |
| **Review + Scoring** | Both outputs combined | Comprehensive evaluation |

Ask user: "Which evaluation mode would you like?"
1. Full peer review with revision guidance (default)
2. Quick scoring only (8 dimensions, quality tier)
3. Both: scoring summary + detailed review
```

#### Scoring Integration

Add new Stage 1.5 (optional) to peer-review workflow:

```markdown
### Stage 1.5: Quantitative Scoring (Optional)

**Trigger:** User selects "Scoring Only" or "Review + Scoring" mode

**Objective:** Generate 8-dimension quantitative assessment

**The 8 Evaluation Dimensions:**

| # | Dimension | Weight | Key Criteria |
|---|-----------|--------|--------------|
| 1 | Problem Formulation | 15% | Clarity, significance, novelty, feasibility |
| 2 | Literature Review | 15% | Comprehensiveness, synthesis, gap identification |
| 3 | Methodology | 20% | Appropriateness, rigor, reproducibility, ethics |
| 4 | Data Collection | 10% | Quality, sample size, procedures, reliability |
| 5 | Analysis | 15% | Method appropriateness, rigor, coherence |
| 6 | Results | 10% | Clarity, statistical rigor, visualization |
| 7 | Writing | 10% | Organization, clarity, tone, accessibility |
| 8 | Citations | 5% | Completeness, quality, accuracy, balance |

**Scoring Rubric:**

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Exemplary quality, publishable in top venues |
| 4 | Good | Strong quality, minor improvements needed |
| 3 | Adequate | Acceptable quality, notable areas for improvement |
| 2 | Needs Work | Significant revisions required |
| 1 | Poor | Fundamental issues, requires major revision |

**Quality Tiers:**

| Aggregate | Tier | Interpretation |
|-----------|------|----------------|
| 4.5-5.0 | A | Publication-ready for top venues |
| 4.0-4.4 | B | Strong, minor revisions needed |
| 3.5-3.9 | C | Acceptable, moderate revisions |
| 3.0-3.4 | D | Significant revisions required |
| <3.0 | F | Major reconceptualization needed |

**Exit Criteria:**
- [ ] All 8 dimensions scored (1-5)
- [ ] Weighted aggregate calculated
- [ ] Quality tier assigned (A-F)
- [ ] Brief justification for each score

**Output:** Proceed to Stage 2 (Full Review) or generate Scoring Report
```

### Implementation Steps

| Step | Task | Files Affected |
|------|------|----------------|
| 1.1 | Add output mode selection to peer-review SKILL.md | `peer-review/SKILL.md` |
| 1.2 | Create Stage 1.5 (Quantitative Scoring) section | `peer-review/SKILL.md` |
| 1.3 | Migrate `calculate_scores.py` script | `peer-review/scripts/` |
| 1.4 | Migrate scoring reference docs | `peer-review/references/` |
| 1.5 | Create scoring report template | `peer-review/templates/` |
| 1.6 | Update cross-references in peer-review | `peer-review/SKILL.md` |
| 1.7 | Deprecate scholar-evaluation skill | `scholar-evaluation/SKILL.md` |
| 1.8 | Update SKILL_ROUTER.md | `skills/SKILL_ROUTER.md` |
| 1.9 | Update any skills referencing scholar-evaluation | Various |

### Deprecation Strategy

Add to `scholar-evaluation/SKILL.md`:

```markdown
---
name: scholar-evaluation
version: 2.1.0
status: DEPRECATED
deprecated_date: 2026-01-XX
successor: peer-review (scoring mode)
---

> **DEPRECATED**: This skill has been merged into `peer-review` as an optional scoring mode.
>
> **Migration:** Use `peer-review` and select "Scoring Only" or "Review + Scoring" mode.
>
> This skill will be removed in v2.0.0.
```

### Testing Checklist

- [ ] Scoring mode produces identical output to old scholar-evaluation
- [ ] Full review mode unchanged from current behavior
- [ ] Combined mode produces coherent merged output
- [ ] calculate_scores.py works from new location
- [ ] SKILL_ROUTER correctly routes to peer-review for evaluation tasks

---

## Initiative 2: Consolidate Poster Skills

### Rationale

`latex-posters` and `pptx-posters` are separate skills with significant shared content:
- Same design principles (from visual-design)
- Same content guidelines (300-800 words, 40-50% visual)
- Same quality thresholds
- Different implementation (LaTeX vs PowerPoint)

Consolidation reduces maintenance burden and provides unified entry point.

### Design

#### New Unified Skill Structure

```
research-posters/
├── SKILL.md                    # Unified skill with format selection
├── references/
│   ├── poster_design_principles.md   # Shared
│   ├── poster_content_guide.md       # Shared
│   ├── poster_layout_design.md       # Shared
│   ├── latex_packages.md             # LaTeX-specific
│   ├── pptx_workflows.md             # PowerPoint-specific
│   └── poster_templates.md           # Both formats
├── assets/
│   ├── beamerposter_template.tex
│   ├── tikzposter_template.tex
│   ├── baposter_template.tex
│   └── poster_quality_checklist.md
└── scripts/
    └── review_poster.sh              # PDF quality checks
```

#### Unified SKILL.md Structure

```markdown
---
name: research-posters
version: 1.0.0
extends: visual-design
description: "Create professional research posters in LaTeX or PowerPoint format with structured layouts, brand-compliant styling, and print-ready export."
when_to_use: "Conference posters, academic poster sessions, thesis defense posters, research symposia"
allowed-tools: [Read, Write, Edit, Bash, Glob]
---

# Research Posters

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md)

<overview>
Create publication-quality research posters in either LaTeX (beamerposter, tikzposter, baposter) or PowerPoint format. This skill provides unified workflows for poster design, with format-specific implementation paths.
</overview>

<decision_framework>
## Format Selection

```
Creating a research poster?
│
├─ Complex equations (>5)?
│  └─ YES → LaTeX format
│
├─ Need version control / reproducibility?
│  └─ YES → LaTeX format
│
├─ Timeline < 48 hours?
│  └─ YES → PowerPoint format (faster iteration)
│
├─ Collaborators need to edit?
│  └─ YES → PowerPoint format
│
├─ Template provided by conference?
│  ├─ .tex template → LaTeX format
│  ├─ .pptx template → PowerPoint format
│  └─ No template → Use decision factors above
│
├─ Familiar with LaTeX?
│  ├─ YES → Either format works
│  └─ NO → PowerPoint format (lower barrier)
│
└─ Default: PowerPoint format
```

## Format Comparison

| Criterion | LaTeX | PowerPoint |
|-----------|-------|------------|
| Complex equations | ✅ Excellent | ⚠️ Difficult |
| Precise typography | ✅ Better control | ⚠️ Limited |
| Quick iteration | ⚠️ Slower | ✅ Faster |
| Collaboration | ⚠️ Requires LaTeX | ✅ Easy sharing |
| Version control | ✅ Git-friendly | ⚠️ Binary format |
| Learning curve | ⚠️ Steeper | ✅ Familiar |

</decision_framework>

<workflow>
## Unified Workflow

### Stage 1: Requirements & Planning (Both Formats)
[Shared content - poster size, content outline, core messages]

### Stage 2: Format Selection
Ask user: "Which format would you like?"
1. LaTeX (beamerposter, tikzposter, or baposter)
2. PowerPoint

→ Branch to format-specific Stage 3

### Stage 3A: LaTeX Implementation
[Content from current latex-posters Stage 2-5]

### Stage 3B: PowerPoint Implementation
[Content from current pptx-posters Stage 2-7]

### Stage 4: Visual Content Creation (Both Formats)
[Shared - scientific-schematics integration, figure requirements]

### Stage 5: Quality Validation (Both Formats)
[Shared quality checklist with format-specific checks]

</workflow>
```

### Implementation Steps

| Step | Task | Files Affected |
|------|------|----------------|
| 2.1 | Create `research-posters/` directory | New directory |
| 2.2 | Write unified SKILL.md with format branching | `research-posters/SKILL.md` |
| 2.3 | Merge shared references (design, content, layout) | `research-posters/references/` |
| 2.4 | Create format-specific reference docs | `research-posters/references/` |
| 2.5 | Copy assets from both skills | `research-posters/assets/` |
| 2.6 | Copy scripts | `research-posters/scripts/` |
| 2.7 | Deprecate latex-posters | `latex-posters/SKILL.md` |
| 2.8 | Deprecate pptx-posters | `pptx-posters/SKILL.md` |
| 2.9 | Update SKILL_ROUTER.md | `skills/SKILL_ROUTER.md` |
| 2.10 | Update cross-references in other skills | Various |

### Deprecation Strategy

Add to both `latex-posters/SKILL.md` and `pptx-posters/SKILL.md`:

```markdown
---
name: latex-posters  # or pptx-posters
status: DEPRECATED
deprecated_date: 2026-01-XX
successor: research-posters
---

> **DEPRECATED**: This skill has been consolidated into `research-posters`.
>
> **Migration:** Use `research-posters` and select your preferred format (LaTeX or PowerPoint).
>
> This skill will be removed in v2.0.0.
```

### Testing Checklist

- [ ] LaTeX workflow produces same output as old latex-posters
- [ ] PowerPoint workflow produces same output as old pptx-posters
- [ ] Format selection logic correctly routes
- [ ] All templates accessible from new location
- [ ] SKILL_ROUTER correctly routes poster requests
- [ ] Cross-references in other skills work

---

## Initiative 3: Update Document-Skills References

### Rationale

`document-skills` was refactored to a thin adapter pointing to the marketplace plugin. Skills should reference the marketplace directly for clarity.

### Current State

References exist in format: `document-skills:pptx`, `document-skills:docx`, `document-skills:pdf`, `document-skills:xlsx`

### Target State

Update to: `document-skills:pptx`, `document-skills:docx`, `document-skills:pdf`, `document-skills:xlsx`

Note: The namespace `document-skills:X` is actually correct as it routes through the adapter. The real fix is ensuring the adapter properly delegates and documentation is clear.

### Implementation Steps

| Step | Task | Files Affected | Status |
|------|------|----------------|--------|
| 3.1 | Audit all references to document-skills | All skill files | ✅ Complete |
| 3.2 | Verify adapter correctly routes to marketplace | `document-skills/SKILL.md` | ✅ Complete |
| 3.3 | Update adapter documentation for clarity | `document-skills/SKILL.md` | ✅ Complete |
| 3.4 | Ensure consistent namespace usage | Various | ✅ Complete |

### Files to Update

Based on audit, these files reference document-skills:

```
skills/SKILL_ROUTER.md
skills/scientific-slides/SKILL.md
skills/venue-templates/SKILL.md
skills/scientific-slides/assets/powerpoint_design_guide.md
skills/markdown-to-pdf/SKILL.md
```

### Adapter Documentation Update

Update `document-skills/SKILL.md` to clarify routing:

```markdown
---
name: document-skills
version: 1.1.0
description: "Thin adapter routing to anthropic-agent-skills marketplace document capabilities"
---

# Document Skills Adapter

This skill provides a namespace for document creation capabilities powered by the
[anthropic-agent-skills](https://github.com/anthropics/agent-skills) marketplace plugin.

## Available Sub-Skills

| Namespace | Routes To | Purpose |
|-----------|-----------|---------|
| `document-skills:docx` | `document-skills:docx` | Word document creation/editing |
| `document-skills:pptx` | `document-skills:pptx` | PowerPoint creation/editing |
| `document-skills:pdf` | `document-skills:pdf` | PDF manipulation |
| `document-skills:xlsx` | `document-skills:xlsx` | Excel spreadsheet creation |

## Usage

Reference these skills using the `document-skills:` namespace prefix:

```markdown
For PowerPoint output, use `document-skills:pptx`
```

The adapter automatically routes to the installed marketplace plugin.
```

---

## Initiative 4: Default-On Brand Application

### Rationale

Currently, Oligon brand styling is opt-in. Users must explicitly invoke `oligon-brand` or reference brand colors. Making brand application default-on for visual outputs ensures consistent styling.

### Design

#### Affected Skills

Visual output skills that should auto-apply brand:

| Skill | Visual Outputs | Brand Integration |
|-------|----------------|-------------------|
| `plotting-libraries` | matplotlib, seaborn, ggplot2 figures | Auto-load brand color cycles |
| `scientific-schematics` | AI-generated diagrams | Use brand colors in prompts |
| `research-posters` | Poster PDFs | Apply brand color scheme |
| `scientific-slides` | Presentations | Use brand templates |
| `research-paper-summarizer` | HTML, PDF, SVG outputs | Apply brand colors |
| `markdown-to-pdf` | PDF documents | Use brand styling |

#### Implementation Pattern

Add to each visual skill's workflow (Stage 1 or Setup):

```markdown
### Brand Application (Default)

By default, all visual outputs use **Oligon Scientific Brand** styling.

**Auto-loaded settings:**
- Color palette: Brand Blue (#2DB2E8), Orange (#E8622D), Gray scale
- Typography: [Brand fonts if applicable]
- Color cycles: Qualitative, sequential, diverging from brand spec

**To disable brand styling:**
User can explicitly request: "Use default/generic styling" or "No brand colors"

**Brand Reference:** See `oligon-brand` skill for complete specification.
```

#### Specific Integrations

**plotting-libraries:**
```python
# Add to workflow Stage 2 (Environment Setup)
# Auto-load brand colors before any plotting

import matplotlib.pyplot as plt

# Oligon brand colors - auto-applied
OLIGON_COLORS = {
    'primary': '#2DB2E8',
    'secondary': '#E8622D',
    'dark': '#222222',
    'medium': '#666666',
    'light': '#999999'
}

# Set as default color cycle
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[
    OLIGON_COLORS['primary'],
    OLIGON_COLORS['secondary'],
    OLIGON_COLORS['dark'],
    OLIGON_COLORS['medium'],
    OLIGON_COLORS['light']
])
```

**scientific-schematics:**
```markdown
# Add to prompt generation
When generating diagrams, use these colors:
- Primary elements: #2DB2E8 (Brand Blue)
- Highlighting/alerts: #E8622D (Orange)
- Text/labels: #222222 (Dark Gray)
- Secondary elements: #666666 (Medium Gray)
- Background: #FFFFFF (White)
```

**research-paper-summarizer:**
Already implements brand colors - verify and document as default behavior.

### Implementation Steps

| Step | Task | Files Affected |
|------|------|----------------|
| 4.1 | Add brand auto-load to plotting-libraries | `plotting-libraries/SKILL.md` |
| 4.2 | Add brand colors to scientific-schematics prompts | `scientific-schematics/SKILL.md` |
| 4.3 | Add brand section to research-posters | `research-posters/SKILL.md` |
| 4.4 | Add brand section to scientific-slides | `scientific-slides/SKILL.md` |
| 4.5 | Verify brand in research-paper-summarizer | `research-paper-summarizer/SKILL.md` |
| 4.6 | Add brand section to markdown-to-pdf | `markdown-to-pdf/SKILL.md` |
| 4.7 | Update oligon-brand to document default-on behavior | `oligon-brand/SKILL.md` |
| 4.8 | Add opt-out documentation to each skill | Various |

### Opt-Out Mechanism

Document in each skill:

```markdown
### Disabling Brand Styling

To use generic/default styling instead of Oligon brand:

**Explicit request:** Include in your prompt:
- "Use default colors"
- "No brand styling"
- "Generic color scheme"

**Per-project override:** Add to project CLAUDE.md:
```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```
```

---

## Implementation Timeline

### Phase 1: Low-Effort Changes (Week 1)

| Task | Initiative | Effort |
|------|------------|--------|
| Update document-skills adapter documentation | 3 | 1 day |
| Audit and fix document-skills references | 3 | 1 day |

### Phase 2: Medium-Effort Changes (Week 2)

| Task | Initiative | Effort |
|------|------------|--------|
| Add brand auto-load to 6 visual skills | 4 | 3 days |
| Update oligon-brand documentation | 4 | 1 day |
| Test brand integration | 4 | 1 day |

### Phase 3: High-Effort Changes (Weeks 3-4)

| Task | Initiative | Effort |
|------|------------|--------|
| Merge scholar-evaluation into peer-review | 1 | 3 days |
| Create research-posters unified skill | 2 | 4 days |
| Deprecate old skills | 1, 2 | 1 day |
| Update SKILL_ROUTER.md | 1, 2 | 1 day |
| Update cross-references across all skills | 1, 2 | 1 day |

### Phase 4: Testing & Cleanup (Week 5)

| Task | Initiative | Effort |
|------|------------|--------|
| End-to-end testing of all changes | All | 2 days |
| Documentation review | All | 1 day |
| Remove deprecated skills (or mark for v2.0 removal) | 1, 2 | 1 day |

---

## SKILL_ROUTER.md Updates

### Changes Required

1. **Evaluation routing:** Update to route to peer-review with mode selection
2. **Poster routing:** Update to route to research-posters with format selection
3. **Remove:** References to scholar-evaluation, latex-posters, pptx-posters

### Updated Decision Trees

#### Evaluation Routing (Updated)

```markdown
## Decision Tree: Research Workflow

...

├─ Need to EVALUATE a paper or researcher?
│  │
│  ├─ Evaluate paper quality?
│  │  └─ YES → peer-review
│  │            │
│  │            ├─ Need detailed revision guidance?
│  │            │  └─ Full Review mode (default)
│  │            │
│  │            ├─ Need quick quality score?
│  │            │  └─ Scoring Only mode
│  │            │
│  │            └─ Need both?
│  │               └─ Review + Scoring mode
│  │
│  └─ Evaluate researcher/scholar?
│     └─ YES → (bibliometric tools - out of scope)
```

#### Poster Routing (Updated)

```markdown
## Decision Tree: Document Creation

...

│          └─ NO → Is it a POSTER?
│                   │
│                   ├─ YES → research-posters
│                   │         │
│                   │         ├─ Complex equations / version control needed?
│                   │         │  └─ LaTeX format (beamerposter/tikzposter/baposter)
│                   │         │
│                   │         ├─ Quick turnaround / collaboration needed?
│                   │         │  └─ PowerPoint format
│                   │         │
│                   │         └─ Automated from existing paper?
│                   │            └─ paper-2-web (Paper2Poster)
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Medium | High | Deprecation period, clear migration docs |
| Missing functionality in merged skills | Low | High | Comprehensive testing, feature parity check |
| Brand colors conflict with user preferences | Medium | Low | Document opt-out mechanism |
| Cross-reference breakage | Medium | Medium | Automated grep for old skill names |

---

## Success Criteria

### Initiative 1 (Merge scholar-evaluation)
- [ ] peer-review scoring mode produces identical output to old scholar-evaluation
- [ ] Full review mode unchanged
- [ ] SKILL_ROUTER routes correctly
- [ ] scholar-evaluation marked deprecated

### Initiative 2 (Consolidate posters)
- [ ] research-posters LaTeX path produces same output as latex-posters
- [ ] research-posters PowerPoint path produces same output as pptx-posters
- [ ] Format selection works correctly
- [ ] Both old skills marked deprecated

### Initiative 3 (Document-skills references) ✅ COMPLETE
- [x] Adapter documentation is clear
- [x] All references consistent
- [x] Routing works correctly

### Initiative 4 (Default brand)
- [ ] All 6 visual skills auto-apply brand colors
- [ ] Opt-out mechanism documented and works
- [ ] Visual outputs consistent with Oligon brand spec

---

## Appendix: Files Changed Summary

| File | Changes |
|------|---------|
| `peer-review/SKILL.md` | Add scoring mode, Stage 1.5 |
| `peer-review/scripts/calculate_scores.py` | New (migrated) |
| `peer-review/references/scholareval_framework.md` | New (migrated) |
| `peer-review/templates/scoring_report.md` | New |
| `scholar-evaluation/SKILL.md` | Mark deprecated |
| `research-posters/SKILL.md` | New (unified skill) |
| `research-posters/references/*` | New (merged) |
| `research-posters/assets/*` | New (merged) |
| `latex-posters/SKILL.md` | Mark deprecated |
| `pptx-posters/SKILL.md` | Mark deprecated |
| `document-skills/SKILL.md` | Update documentation |
| `plotting-libraries/SKILL.md` | Add brand auto-load |
| `scientific-schematics/SKILL.md` | Add brand colors |
| `scientific-slides/SKILL.md` | Add brand section |
| `markdown-to-pdf/SKILL.md` | Add brand section |
| `research-paper-summarizer/SKILL.md` | Verify/document brand |
| `oligon-brand/SKILL.md` | Document default-on behavior |
| `SKILL_ROUTER.md` | Update routing trees |
