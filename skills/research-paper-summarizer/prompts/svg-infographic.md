# SVG Infographic Prompt

Create a single-page research article summary infographic as raw SVG code.

## Source Document

**IMPORTANT**: This visual output is generated from the markdown summary file created in Phase 1.

Before generating the infographic:
1. Read the markdown summary file (`{original_filename}_summary.md`)
2. Identify which summarizer type was used (check the section headers)
3. Use the appropriate article-type layout guidance below
4. Extract key data points, statistics, and findings
5. Map the markdown content to appropriate visual components

---

## Article-Type-Specific Layouts

The infographic structure adapts based on article type. Each type emphasizes different content:

### General Research Papers
*Source: `general_researcher_summarizer.md`*

**Priority Content:**
| Markdown Section | Infographic Element | Priority |
|------------------|---------------------|----------|
| Executive Summary | Header title/subtitle | HIGH |
| Results - Structured Breakdown | Main findings panel | HIGH |
| Experimental Approach | Methods snapshot | MEDIUM |
| Critical Analysis - Strengths | Highlight callout | MEDIUM |
| Actionable Takeaways | Take-home message | HIGH |
| Limitations | Orange warning box | MEDIUM |

**Recommended Components:** DonutChart, HorizontalBarChart, StatCallout, TimelineNode

### Review Articles
*Source: `review_article_summarizer.md`*

**Priority Content:**
| Markdown Section | Infographic Element | Priority |
|------------------|---------------------|----------|
| Executive Summary | Header - central thesis | HIGH |
| Field Landscape | Timeline of developments | HIGH |
| Core Arguments | Thematic groupings | HIGH |
| Knowledge Gaps | Orange callout boxes | MEDIUM |
| Key Papers (Reference Mining) | Sidebar list | MEDIUM |
| Future Directions | Outlook section | MEDIUM |

**Recommended Components:** MilestoneTimeline, HierarchicalTree, FeatureBoxGrid, CircularHub
**Note:** Less quantitative data; focus on conceptual organization and field structure

### Computational Biology / Bioinformatics
*Source: `compbio_bioinformatic_summarizer.md`*

**Priority Content:**
| Markdown Section | Infographic Element | Priority |
|------------------|---------------------|----------|
| Executive Summary | Header - problem solved | HIGH |
| Data Foundation | Data sources badge row | HIGH |
| Computational Approach | Pipeline flow diagram | HIGH |
| Results - Performance | Benchmark comparison bars | HIGH |
| Reproducibility Assessment | Code availability badge | MEDIUM |
| Benchmarking Context | Comparison table/bars | MEDIUM |

**Recommended Components:** ArrowStack (pipeline), GroupedBarChart (benchmarks), StatCallout (performance), ComparisonGrid
**Special:** Include GitHub/data repository badges, accession numbers

### Cell & Molecular Biology
*Source: `cellmolbio_summarizer.md`*

**Priority Content:**
| Markdown Section | Infographic Element | Priority |
|------------------|---------------------|----------|
| Executive Summary | Header - key discovery | HIGH |
| Model Systems | Models badge row | HIGH |
| Mechanistic Depth | Pathway diagram | HIGH |
| Results - Structured Breakdown | Findings by context | HIGH |
| Cancer Biology Assessment | Hallmarks checklist | MEDIUM |
| Translational Assessment | Development stage | MEDIUM |

**Recommended Components:** HierarchicalTree (pathway), HorizontalBarChart, Pictograph (model organisms), TimelineNode (translation stages)
**Special:** Use science icons (DNAHelix, MoleculeIcon) for visual interest

---

## Universal Content (All Types)

The markdown summary provides pre-extracted, validated data including:
- Executive summary for the header
- Key findings with statistics for the main panels
- Methods summary for the methodology section
- Limitations for the conclusions callout

## Component Library Reference

For complex infographics, reference the SVG component libraries in `components/`:
- `svg-components.jsx` - Core components (DonutChart, StatCallout, HorizontalBarChart, etc.)
- `svg-components-expanded.jsx` - Extended chart components
- `svg-science-components.jsx` - Science-specific icons (DNA, atoms, molecules)
- `svg-lab-components.jsx` - Lab equipment (flasks, beakers, test tubes)

## Available Components

| Category | Components |
|----------|------------|
| **KPI/Stats** | DonutChart, StatCallout, StatWithMiniChart, PieChartRow, DropletBreakdown |
| **Charts** | HorizontalBarChart, VerticalProgressBars, GroupedBarChart, CylinderChart, LineAreaChart, MultiLineChart |
| **Process/Flow** | TimelineNode, MilestoneTimeline, ScientificMethodTimeline, SCurveProcess, ArrowStack, CircularHub |
| **Structure** | HierarchicalTree, IsometricBlocks, ComparisonGrid, FeatureBoxGrid, RankedBarList |
| **Population** | Pictograph, PopulationGrid, GenderComparison |
| **Science Icons** | DNAHelix, AtomIcon, MoleculeIcon, LabFlaskWithBurner, Beaker, TestTubes |

## Brand Color Palette (Strict)

```
BRAND = {
  blue: '#2DB2E8',       // Hero - PRIMARY finding only (1-2 uses max)
  orange: '#E8622D',     // Contrast/Alert - opposing data, warnings
  darkGray: '#222222',   // Primary text/data, Control groups
  mediumGray: '#666666', // Secondary data
  mutedGray: '#999999',  // Tertiary/muted
  lightGray: '#BDBDBD',  // Annotations only (NOT for data)
  white: '#FFFFFF',      // Background only
  black: '#000000',      // All text
  mediumBlue: '#158BBB', // Rare 4th category
  darkTeal: '#0F5D7D'    // Heatmap extremes
}
```

### Color Assignment Rules

| Data Type | Color | HEX |
|-----------|-------|-----|
| Treatment/Intervention | Brand Blue | #2DB2E8 |
| Control/Baseline | Dark Gray | #222222 |
| Adverse/Opposite effect | Orange | #E8622D |
| Secondary comparison | Medium Gray | #666666 |
| Annotations/gridlines | Light Gray | #BDBDBD |

## Typography

| Element | Size | Weight |
|---------|------|--------|
| Title | 14-16pt | Bold |
| Section Headers | 10-12pt | Bold |
| Body/Data | 8-10pt | Regular |
| Annotations | 7-8pt | Regular |

**Font Family**: Arial or Helvetica only

## Layout Structure

### 1. Header Block
- Article title (shortened for visual impact)
- Authors (first author et al.) + Journal/Year
- DOI badge
- Optional: topic-appropriate icon decoration

### 2. Key Metrics Row
Horizontal row of 3-4 stat callouts:
- Sample size (N = X)
- Study duration
- Main effect size
- Significance level

### 3. Main Findings Panel
2-3 key findings as visual elements:
- Donut charts for percentages
- Bar charts for comparisons
- Use Brand Blue for PRIMARY finding only
- Gray for secondary findings

### 4. Methods Snapshot
- Study design badge
- Timeline showing phases
- Key methodology points

### 5. Results Visualization
Select appropriate chart type:
- Two-group comparison → Horizontal bars
- Time trend → Line chart
- Proportions → Donut or pictograph
- Funnel → Arrow stack

### 6. Conclusions Box
- 1-2 sentence take-home message
- Clinical/research implications
- Limitations callout (orange accent)

## SVG Component Patterns

### Donut Chart
```svg
<g class="donut-chart">
  <circle cx="60" cy="60" r="50" fill="none" stroke="#BDBDBD" stroke-width="12"/>
  <circle cx="60" cy="60" r="50" fill="none" stroke="#2DB2E8" stroke-width="12"
    stroke-dasharray="251.2" stroke-dashoffset="62.8" transform="rotate(-90 60 60)"/>
  <text x="60" y="65" text-anchor="middle" font-size="18" font-weight="bold">75%</text>
</g>
```

### Stat Callout
```svg
<g class="stat-callout">
  <circle cx="30" cy="30" r="25" fill="#2DB2E8"/>
  <text x="30" y="80" text-anchor="middle" font-size="24" font-weight="bold" fill="#2DB2E8">1,247</text>
  <text x="30" y="100" text-anchor="middle" font-size="10" fill="#666666">Patients</text>
</g>
```

### Horizontal Bar
```svg
<g class="bar">
  <text x="0" y="20" font-size="11" fill="#222222">Control</text>
  <rect x="80" y="8" width="120" height="20" fill="#222222" rx="3"/>
  <text x="205" y="22" font-size="10" fill="#222222">45%</text>
</g>
```

### Timeline Node
```svg
<g class="timeline">
  <line x1="50" y1="30" x2="350" y2="30" stroke="#BDBDBD" stroke-width="2"/>
  <circle cx="100" cy="30" r="12" fill="#2DB2E8"/>
  <text x="100" y="35" text-anchor="middle" font-size="10" fill="white">1</text>
  <text x="100" y="55" text-anchor="middle" font-size="9">Phase 1</text>
</g>
```

## Design Rules

1. **White background only** (#FFFFFF)
2. **No effects** — no gradients, shadows, 3D elements
3. **Flat icons** — clean, simple, brand colors only
4. **White space** — generous spacing between sections
5. **Visual hierarchy** — Brand Blue draws eye to single most important finding
6. **Accessibility** — blue/orange/gray palette is colorblind-safe

## SVG Template Structure

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1400" width="1000" height="1400">
  <defs>
    <style>
      .title { font-family: Arial, sans-serif; font-size: 22px; font-weight: bold; fill: #000000; }
      .subtitle { font-family: Arial, sans-serif; font-size: 14px; fill: #666666; }
      .section-header { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #000000; }
      .body-text { font-family: Arial, sans-serif; font-size: 12px; fill: #222222; }
      .highlight-text { font-family: Arial, sans-serif; font-size: 12px; fill: #2DB2E8; font-weight: bold; }
      .stat-text { font-family: Arial, sans-serif; font-size: 11px; fill: #222222; }
      .caption { font-family: Arial, sans-serif; font-size: 10px; fill: #666666; font-style: italic; }
    </style>
  </defs>

  <!-- White Background -->
  <rect width="1000" height="1400" fill="#FFFFFF"/>

  <!-- Header with brand accent line -->
  <line x1="40" y1="95" x2="960" y2="95" stroke="#2DB2E8" stroke-width="3"/>

  <!-- Content sections... -->

  <!-- Footer -->
  <line x1="40" y1="1370" x2="960" y2="1370" stroke="#BDBDBD" stroke-width="1"/>
  <text x="40" y="1390" class="caption">Summary from [Authors] ([Year])</text>
</svg>
```

## Data Extraction from Markdown Summary

### Universal Mapping (All Types)

| Markdown Section | Infographic Element |
|------------------|---------------------|
| Executive Summary | Header block title/subtitle |
| Key Findings + Statistics | Main findings panel, stat callouts |
| Methods/Study Design | Methods snapshot badge |
| Sample Size (n) | Key metrics row |
| Limitations | Conclusions box (orange accent) |
| One-Paragraph Synthesis | Take-home message |

### Article-Type-Specific Extraction Checklists

**General Research Papers:**
- [ ] Study objective → Header
- [ ] Population (N) → Key metrics
- [ ] Study duration → Key metrics
- [ ] Primary outcome + effect size → Main finding (Brand Blue)
- [ ] P-value / significance → Stat badges
- [ ] Secondary outcomes → Secondary findings (Gray)
- [ ] Actionable takeaways → Take-home callout
- [ ] Key limitation → Conclusions (Orange)

**Review Articles:**
- [ ] Central thesis → Header subtitle
- [ ] Scope (timeframe, breadth) → Scope badge
- [ ] Key developments → Timeline nodes
- [ ] Major themes → Grouped sections
- [ ] Consensus findings → Main panel
- [ ] Controversies/gaps → Orange callouts
- [ ] Top papers to read → Reference list
- [ ] Future outlook → Conclusions

**Computational Biology:**
- [ ] Problem solved → Header
- [ ] Data sources + accessions → Data badge row
- [ ] Pipeline steps → ArrowStack flow
- [ ] Performance metrics → StatCallouts
- [ ] Benchmark comparisons → GroupedBarChart
- [ ] Code/container availability → Repo badge
- [ ] Reproducibility rating → Badge
- [ ] Key limitation → Orange callout

**Cell & Molecular Biology:**
- [ ] Key discovery → Header
- [ ] Model systems used → Models badge row
- [ ] Pathway/mechanism → HierarchicalTree
- [ ] Effect sizes + p-values → StatCallouts
- [ ] In vitro vs in vivo results → Grouped findings
- [ ] Hallmarks addressed → Checklist icons
- [ ] Translation stage → Timeline
- [ ] Key limitation → Orange callout

## Article-Type-Specific SVG Patterns

### Pipeline Flow (Computational Biology)
```svg
<g class="pipeline-flow">
  <!-- Step boxes connected by arrows -->
  <rect x="40" y="10" width="100" height="40" fill="#F8FAFB" stroke="#222222" rx="4"/>
  <text x="90" y="35" text-anchor="middle" font-size="10">Raw Data</text>
  <path d="M145 30 L165 30 L160 25 M165 30 L160 35" stroke="#222222" fill="none"/>
  <rect x="170" y="10" width="100" height="40" fill="#F8FAFB" stroke="#2DB2E8" rx="4"/>
  <text x="220" y="35" text-anchor="middle" font-size="10" fill="#2DB2E8">Processing</text>
  <!-- Continue pattern... -->
</g>
```

### Model Systems Badge Row (Cell & Mol Bio)
```svg
<g class="model-badges">
  <rect x="40" y="10" width="80" height="28" fill="#F8FAFB" stroke="#222222" rx="14"/>
  <text x="80" y="28" text-anchor="middle" font-size="9">HeLa cells</text>
  <rect x="130" y="10" width="80" height="28" fill="#F8FAFB" stroke="#222222" rx="14"/>
  <text x="170" y="28" text-anchor="middle" font-size="9">C57BL/6</text>
  <rect x="220" y="10" width="100" height="28" fill="#F8FAFB" stroke="#2DB2E8" rx="14"/>
  <text x="270" y="28" text-anchor="middle" font-size="9" fill="#2DB2E8">PDX models</text>
</g>
```

### Field Timeline (Review Articles)
```svg
<g class="field-timeline">
  <line x1="50" y1="50" x2="450" y2="50" stroke="#BDBDBD" stroke-width="2"/>
  <!-- Milestone nodes -->
  <circle cx="100" cy="50" r="8" fill="#666666"/>
  <text x="100" y="75" text-anchor="middle" font-size="8">2015</text>
  <text x="100" y="35" text-anchor="middle" font-size="9">First discovery</text>

  <circle cx="250" cy="50" r="8" fill="#2DB2E8"/>
  <text x="250" y="75" text-anchor="middle" font-size="8">2020</text>
  <text x="250" y="35" text-anchor="middle" font-size="9" fill="#2DB2E8">Key breakthrough</text>

  <circle cx="400" cy="50" r="8" fill="#E8622D"/>
  <text x="400" y="75" text-anchor="middle" font-size="8">2024</text>
  <text x="400" y="35" text-anchor="middle" font-size="9">Current debate</text>
</g>
```

### Reproducibility Badge (Computational Biology)
```svg
<g class="repo-badge">
  <rect x="40" y="10" width="120" height="30" fill="#158BBB" rx="4"/>
  <text x="100" y="30" text-anchor="middle" font-size="10" fill="white">Code Available</text>
  <rect x="170" y="10" width="100" height="30" fill="#2DB2E8" rx="4"/>
  <text x="220" y="30" text-anchor="middle" font-size="10" fill="white">Docker</text>
  <rect x="280" y="10" width="80" height="30" fill="#999999" rx="4"/>
  <text x="320" y="30" text-anchor="middle" font-size="10" fill="white">Docs: Partial</text>
</g>
```

### Hallmarks Checklist (Cell & Mol Bio)
```svg
<g class="hallmarks-check">
  <text x="40" y="20" font-size="10" fill="#222222">Cancer Hallmarks:</text>
  <!-- Checked items -->
  <text x="40" y="40" font-size="9" fill="#2DB2E8">✓ Proliferative signaling</text>
  <text x="40" y="55" font-size="9" fill="#2DB2E8">✓ Resisting cell death</text>
  <!-- Unchecked items -->
  <text x="40" y="70" font-size="9" fill="#999999">○ Immune evasion</text>
  <text x="40" y="85" font-size="9" fill="#999999">○ Angiogenesis</text>
</g>
```

---

## Output

Generate complete, valid SVG code that can be:
- Saved as .svg file
- Opened in browser
- Imported into design tools
- Embedded in documents

## Special Handling by Article Type

**Preprints (any type):**
- Add orange "PREPRINT" badge prominently in header
- Include preprint server name

**Review Articles:**
- May have fewer quantitative stats - focus on structure/organization
- Use more conceptual diagrams (HierarchicalTree, CircularHub)

**Computational Biology:**
- Always include data accession numbers
- Show pipeline/workflow if described
- Include reproducibility indicators

**Cell & Mol Bio:**
- Use science icons (DNAHelix, MoleculeIcon) for visual interest
- Pathway diagrams are high value
- Model systems should be prominently displayed
