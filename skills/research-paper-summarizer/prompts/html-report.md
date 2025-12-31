# Interactive HTML Report Prompt

Generate an interactive HTML report by filling in the template at `templates/report-template.html`.

## Workflow

1. **Read** the markdown summary (`{original_filename}_summary.md`)
2. **Read** the template file (`templates/report-template.html`)
3. **Fill in** the placeholders with content from the summary
4. **Write** the complete HTML to `{original_filename}_report.html`

---

## Template Placeholders

Replace these placeholders in the template:

| Placeholder | Content |
|-------------|---------|
| `{{TITLE}}` | Paper title |
| `{{NAV_LINKS}}` | Navigation links (see format below) |
| `{{PUBLICATION_BADGE}}` | Badge HTML for publication type |
| `{{AUTHORS}}` | Author list (first author et al. if >6) |
| `{{INSTITUTION}}` | Institution(s) |
| `{{DATE}}` | Publication date |
| `{{DOI_LINK}}` | DOI as clickable link |
| `{{MAIN_CONTENT}}` | All content sections (see mappings below) |
| `{{SYNTHESIS}}` | One-paragraph synthesis (italicized) |
| `{{CITATION}}` | Full citation |
| `{{PREPRINT_WARNING}}` | Warning div if preprint, empty otherwise |
| `{{TIMESTAMP}}` | Generation timestamp |

### Navigation Links Format

```html
<a href="#overview">Overview</a>
<a href="#context">Context</a>
<a href="#findings">Key Findings</a>
<a href="#methods">Methods</a>
<a href="#analysis">Critical Analysis</a>
<a href="#implications">Implications</a>
```

### Publication Badge Format

```html
<!-- For preprint -->
<span class="badge badge-preprint">Preprint</span>

<!-- For peer-reviewed -->
<span class="badge badge-peer-reviewed">Peer-Reviewed</span>

<!-- For review article -->
<span class="badge badge-review">Review</span>
```

### Preprint Warning Format

```html
<div class="preprint-warning">
    This summary is based on a preprint that has not been peer-reviewed.
    Conclusions should be interpreted with caution.
</div>
```

---

## Section Content Mappings

Map markdown sections to HTML sections based on article type:

### Universal Sections (All Types)

| Section ID | Source | HTML Structure |
|------------|--------|----------------|
| `overview` | Executive Summary | `<section id="overview"><h2>Overview</h2>...` |
| `context` | Background/Motivation | Collapsible section |
| `findings` | Results | Tabbed interface if multiple contexts |
| `methods` | Methodology | Collapsible subsections |
| `analysis` | Critical Analysis | Split cards for strengths/limitations |
| `implications` | Implications/Conclusions | Standard section |

### Article-Type-Specific Sections

**Cell & Molecular Biology** - Add:
- Model Systems table
- Hallmarks checklist panel
- Mechanism diagram (if pathway data exists)
- Translation pipeline table

**Computational Biology** - Add:
- Data Sources panel with accession numbers
- Reproducibility card with rating badges
- Benchmarking comparison table
- Technical glossary (collapsible)

**Review Articles** - Add:
- Scope badge (systematic/narrative, timeframe)
- Key Papers sidebar
- Open Questions panel (Rose accent)

---

## Visual Components (Enhanced)

### Summary Dashboard (Required - Place After Header)

A dark hero section displaying key metrics at a glance. **Always include this.**

```html
<div class="summary-dashboard">
    <h2>At a Glance</h2>
    <div class="metric-row stagger-children">
        <div class="metric">
            <div class="metric-icon">📊</div>
            <div class="metric-value highlight-indigo">p &lt; 0.001</div>
            <div class="metric-label">Key Finding</div>
        </div>
        <div class="metric">
            <div class="metric-icon">🧫</div>
            <div class="metric-value">8</div>
            <div class="metric-label">Cell Lines</div>
        </div>
        <div class="metric">
            <div class="metric-icon">🐁</div>
            <div class="metric-value">3</div>
            <div class="metric-label">In Vivo Models</div>
        </div>
        <div class="metric">
            <div class="metric-icon">🎯</div>
            <div class="metric-value highlight-emerald">Validated</div>
            <div class="metric-label">Target Status</div>
        </div>
    </div>
</div>
```

**Icons by category:**
| Category | Icon |
|----------|------|
| Statistics | 📊 |
| Cell lines | 🧫 |
| Organoids | 🔬 |
| Mouse models | 🐁 |
| Patient samples | 🧬 |
| Target/Drug | 🎯 |
| Mechanism | ⚙️ |
| Time/Duration | ⏱️ |
| Sample size | 👥 |

**Value highlight classes:** `highlight-indigo`, `highlight-emerald`, `highlight-rose`, `highlight-amber`

---

### Evidence Strength Meter

Visual gauge showing strength of mechanistic evidence. Map evidence levels to percentages:

| Evidence Level | Percentage |
|----------------|------------|
| Correlative only | 15% |
| Loss-of-function supports | 30% |
| Gain-of-function supports | 45% |
| Both LOF and GOF consistent | 60% |
| Rescue experiments confirm | 75% |
| Epistasis establishes order | 85% |
| Direct biochemical mechanism | 100% |

```html
<div class="evidence-meter">
    <div class="meter-header">
        <span class="meter-label">Evidence Strength</span>
        <span class="meter-value">Rescue Confirmed</span>
    </div>
    <div class="meter-track">
        <div class="meter-fill" style="width: 75%"></div>
    </div>
    <div class="meter-markers">
        <span>Correlative</span>
        <span class="active">LOF</span>
        <span class="active">GOF</span>
        <span class="active">Rescue</span>
        <span>Epistasis</span>
    </div>
</div>
```

---

### Workflow Timeline (Methods Section)

Show experimental progression as a horizontal timeline:

```html
<div class="workflow-timeline">
    <div class="timeline-step completed">
        <div class="step-icon">1</div>
        <div class="step-content">
            <h4>Knockdown</h4>
            <p>siRNA/shRNA</p>
        </div>
    </div>
    <div class="timeline-connector completed"></div>
    <div class="timeline-step completed">
        <div class="step-icon">2</div>
        <div class="step-content">
            <h4>Validation</h4>
            <p>Western blot, qPCR</p>
        </div>
    </div>
    <div class="timeline-connector completed"></div>
    <div class="timeline-step current">
        <div class="step-icon">3</div>
        <div class="step-content">
            <h4>Phenotype</h4>
            <p>Proliferation, migration</p>
        </div>
    </div>
    <div class="timeline-connector"></div>
    <div class="timeline-step">
        <div class="step-icon">4</div>
        <div class="step-content">
            <h4>In Vivo</h4>
            <p>Xenograft studies</p>
        </div>
    </div>
</div>
```

**Step states:** `completed`, `current`, (default = pending)

---

### Hallmarks Radar Chart (Cell/Mol Bio)

Replace the checklist with a visual radar chart. Generate SVG based on which hallmarks are addressed:

```html
<div class="card neutral">
    <h4>Cancer Hallmarks Addressed</h4>
    <div class="radar-container">
        <svg class="radar-chart" viewBox="0 0 300 300">
            <!-- Grid circles -->
            <circle class="radar-grid" cx="150" cy="150" r="120"/>
            <circle class="radar-grid" cx="150" cy="150" r="80"/>
            <circle class="radar-grid" cx="150" cy="150" r="40"/>

            <!-- Axes (10 hallmarks = 36° apart) -->
            <line class="radar-axis" x1="150" y1="150" x2="150" y2="30"/>
            <line class="radar-axis" x1="150" y1="150" x2="264" y2="108"/>
            <line class="radar-axis" x1="150" y1="150" x2="264" y2="192"/>
            <line class="radar-axis" x1="150" y1="150" x2="150" y2="270"/>
            <line class="radar-axis" x1="150" y1="150" x2="36" y2="192"/>
            <line class="radar-axis" x1="150" y1="150" x2="36" y2="108"/>

            <!-- Data shape - connect addressed hallmarks -->
            <polygon class="radar-shape" points="150,30 264,108 150,150 150,270 36,192 36,108"/>

            <!-- Data points -->
            <circle class="radar-point addressed" cx="150" cy="30" r="5"/>
            <circle class="radar-point addressed" cx="264" cy="108" r="5"/>
            <circle class="radar-point not-addressed" cx="264" cy="192" r="5"/>
            <circle class="radar-point addressed" cx="150" cy="270" r="5"/>
            <circle class="radar-point addressed" cx="36" cy="192" r="5"/>
            <circle class="radar-point addressed" cx="36" cy="108" r="5"/>
        </svg>
    </div>
    <div class="radar-legend">
        <div class="radar-legend-item">
            <div class="radar-legend-dot addressed"></div>
            <span>Addressed</span>
        </div>
        <div class="radar-legend-item">
            <div class="radar-legend-dot partial"></div>
            <span>Partial</span>
        </div>
        <div class="radar-legend-item">
            <div class="radar-legend-dot not-addressed"></div>
            <span>Not Addressed</span>
        </div>
    </div>
</div>
```

---

### Model Systems Grid

Visual cards for each experimental model:

```html
<div class="models-grid">
    <div class="model-card">
        <div class="model-card-icon">🧫</div>
        <div class="model-card-type">Cell Line</div>
        <div class="model-card-name">MDA-MB-231</div>
        <div class="model-card-details">Triple-negative breast cancer</div>
        <span class="model-card-badge primary">Primary Model</span>
    </div>
    <div class="model-card">
        <div class="model-card-icon">🔬</div>
        <div class="model-card-type">Organoid</div>
        <div class="model-card-name">Patient-Derived</div>
        <div class="model-card-details">3 patient samples</div>
        <span class="model-card-badge validated">STR Validated</span>
    </div>
    <div class="model-card">
        <div class="model-card-icon">🐁</div>
        <div class="model-card-type">Xenograft</div>
        <div class="model-card-name">NSG Mouse</div>
        <div class="model-card-details">Orthotopic, n=10/group</div>
    </div>
    <div class="model-card">
        <div class="model-card-icon">🧬</div>
        <div class="model-card-type">Patient Samples</div>
        <div class="model-card-name">TCGA + Local</div>
        <div class="model-card-details">n=847 tumors</div>
    </div>
</div>
```

---

### Confidence Indicators

Three variants for showing confidence/quality levels:

**Pip variant (5 levels):**
```html
<div class="confidence-indicator">
    <span class="confidence-pip filled high"></span>
    <span class="confidence-pip filled high"></span>
    <span class="confidence-pip filled high"></span>
    <span class="confidence-pip filled"></span>
    <span class="confidence-pip"></span>
</div>
```

**Star variant:**
```html
<div class="confidence-stars">
    <span class="star filled">★</span>
    <span class="star filled">★</span>
    <span class="star filled">★</span>
    <span class="star">★</span>
    <span class="star">★</span>
</div>
```

**Bar variant:**
```html
<div class="confidence-bar">
    <div class="confidence-bar-track">
        <div class="confidence-bar-fill high" style="width: 80%"></div>
    </div>
    <span class="confidence-label high">Strong</span>
</div>
```

**Level classes:** `high` (emerald), `medium` (amber), `low` (rose)

---

### Before/After Comparison Cards

For treatment effects, expression changes, or any comparative data:

```html
<div class="comparison-container">
    <div class="comparison-card before">
        <div class="comparison-label">Control</div>
        <div class="comparison-value">100%</div>
        <div class="comparison-metric">Cell viability</div>
    </div>
    <div class="comparison-arrow">→</div>
    <div class="comparison-card after improved">
        <div class="comparison-label">Treatment</div>
        <div class="comparison-value">23%</div>
        <div class="comparison-metric">Cell viability</div>
        <div class="comparison-change positive">↓ 77%</div>
    </div>
</div>
```

**After card modifiers:** `improved` (emerald), `worsened` (rose), default (teal)
**Change classes:** `positive`, `negative`

---

### Heatmap Tables

Color-coded tables for expression data, significance matrices:

```html
<table class="heatmap-table">
    <thead>
        <tr>
            <th>Gene</th>
            <th>Control</th>
            <th>Treatment A</th>
            <th>Treatment B</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>TP53</td>
            <td class="heatmap-cell intensity-3">1.0</td>
            <td class="heatmap-cell intensity-5">4.2</td>
            <td class="heatmap-cell intensity-4">2.8</td>
        </tr>
        <tr>
            <td>MYC</td>
            <td class="heatmap-cell intensity-3">1.0</td>
            <td class="heatmap-cell intensity-1">0.3</td>
            <td class="heatmap-cell intensity-0">0.1</td>
        </tr>
    </tbody>
</table>
<div class="heatmap-legend">
    <div class="heatmap-legend-item">
        <div class="heatmap-legend-swatch" style="background: rgba(225, 29, 72, 0.25)"></div>
        <span>Low</span>
    </div>
    <div class="heatmap-legend-item">
        <div class="heatmap-legend-swatch" style="background: rgba(245, 158, 11, 0.25)"></div>
        <span>Medium</span>
    </div>
    <div class="heatmap-legend-item">
        <div class="heatmap-legend-swatch" style="background: rgba(16, 185, 129, 0.4)"></div>
        <span>High</span>
    </div>
</div>
```

**Intensity classes:** `intensity-0` through `intensity-5` (red→green gradient)
**Significance classes:** `sig-high`, `sig-medium`, `sig-low`

---

### Reference Network Mini-Map

Visual citation network showing paper relationships:

```html
<div class="reference-network">
    <div class="network-header">
        <span class="network-title">Citation Context</span>
    </div>
    <svg class="network-svg" viewBox="0 0 400 200">
        <!-- Links first (behind nodes) -->
        <line class="network-link strong" x1="200" y1="100" x2="100" y2="50"/>
        <line class="network-link" x1="200" y1="100" x2="300" y2="60"/>
        <line class="network-link" x1="200" y1="100" x2="150" y2="160"/>

        <!-- Current paper (center) -->
        <g class="network-node current">
            <circle cx="200" cy="100" r="12"/>
            <text y="130">This Paper</text>
        </g>

        <!-- Seminal papers -->
        <g class="network-node seminal">
            <circle cx="100" cy="50" r="8"/>
            <text y="75">Hanahan 2011</text>
        </g>

        <!-- Supporting papers -->
        <g class="network-node supporting">
            <circle cx="300" cy="60" r="6"/>
            <text y="85">Smith 2020</text>
        </g>
    </svg>
    <div class="network-legend">
        <div class="network-legend-item">
            <div class="network-legend-dot current"></div>
            <span>This Paper</span>
        </div>
        <div class="network-legend-item">
            <div class="network-legend-dot seminal"></div>
            <span>Seminal Work</span>
        </div>
        <div class="network-legend-item">
            <div class="network-legend-dot supporting"></div>
            <span>Supporting</span>
        </div>
    </div>
</div>
```

---

### Pathway Diagram (Cell/Mol Bio Mechanisms)

SVG-based signaling pathway visualization:

```html
<div class="pathway-diagram">
    <svg class="pathway-svg" viewBox="0 0 500 200">
        <!-- Arrow marker definition -->
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="currentColor"/>
            </marker>
            <marker id="arrowhead-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#10B981"/>
            </marker>
            <marker id="arrowhead-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#E11D48"/>
            </marker>
        </defs>

        <!-- Nodes -->
        <g class="pathway-node">
            <rect x="20" y="80" width="80" height="40"/>
            <text x="60" y="105">Ligand</text>
        </g>
        <g class="pathway-node target">
            <rect x="140" y="80" width="80" height="40"/>
            <text x="180" y="105">Receptor</text>
        </g>
        <g class="pathway-node activated">
            <rect x="260" y="80" width="80" height="40"/>
            <text x="300" y="105">Kinase</text>
        </g>
        <g class="pathway-node inhibited">
            <rect x="380" y="80" width="80" height="40"/>
            <text x="420" y="105">TF</text>
        </g>

        <!-- Arrows -->
        <path class="pathway-arrow activation" d="M100,100 L140,100" marker-end="url(#arrowhead-green)"/>
        <path class="pathway-arrow activation" d="M220,100 L260,100" marker-end="url(#arrowhead-green)"/>
        <path class="pathway-arrow inhibition" d="M340,100 L380,100" marker-end="url(#arrowhead-red)"/>
    </svg>
    <div class="pathway-legend">
        <div class="pathway-legend-item">
            <div class="pathway-legend-line activation"></div>
            <span>Activation</span>
        </div>
        <div class="pathway-legend-item">
            <div class="pathway-legend-line inhibition"></div>
            <span>Inhibition</span>
        </div>
    </div>
</div>
```

**Node classes:** `target` (teal), `activated` (emerald), `inhibited` (rose)

---

## Standard Component Formats

### Tabbed Content

```html
<div class="tab-group">
    <div class="tabs">
        <button class="tab-btn active" data-tab="invitro">In Vitro</button>
        <button class="tab-btn" data-tab="invivo">In Vivo</button>
    </div>
    <div class="tab-content active" data-tab="invitro">
        <!-- Content here -->
    </div>
    <div class="tab-content" data-tab="invivo">
        <!-- Content here -->
    </div>
</div>
```

### Collapsible Section

```html
<h3 class="collapsible">Section Title</h3>
<div class="collapse-content">
    <!-- Hidden content here -->
</div>
```

### Split Cards (Strengths/Limitations)

```html
<div class="split-cards">
    <div class="card highlight">
        <h4>Strengths</h4>
        <ul>
            <li>Point 1</li>
            <li>Point 2</li>
        </ul>
    </div>
    <div class="card contrast">
        <h4>Limitations</h4>
        <ul>
            <li>Point 1</li>
            <li>Point 2</li>
        </ul>
    </div>
</div>
```

### Stat Box with Progress Ring (for percentages)

```html
<div class="stat-box">
    <div class="stat-ring">
        <svg viewBox="0 0 36 36">
            <path class="stat-ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path class="stat-ring-fill" stroke-dasharray="72, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <text x="18" y="20.5" class="stat-ring-text">72%</text>
        </svg>
    </div>
    <div class="stat-label">Label here</div>
</div>
```

### Stat Box (for counts/values)

```html
<div class="stat-box">
    <div class="stat-value">1,234</div>
    <div class="stat-label">Label here</div>
</div>
```

### Significance Badges

```html
<span class="badge highly-significant">p < 0.001</span>
<span class="badge significant">p < 0.05</span>
<span class="badge trend">p = 0.08</span>
<span class="badge not-significant">n.s.</span>
```

### Data Table

```html
<table>
    <thead>
        <tr><th>Column 1</th><th>Column 2</th></tr>
    </thead>
    <tbody>
        <tr><td>Data 1</td><td>Data 2</td></tr>
    </tbody>
</table>
```

### Key Quote

```html
<blockquote class="key-quote">
    Important quote from the paper here.
</blockquote>
```

### Reproducibility Card (Comp Bio)

```html
<div class="card code-card">
    <h4>Reproducibility Assessment</h4>
    <div class="badge-row">
        <span class="badge excellent">Code Available</span>
        <span class="badge good">Docker Provided</span>
        <span class="badge partial">Docs Partial</span>
    </div>
    <p>Overall: <span class="rating-good">Good</span></p>
</div>
```

### Hallmarks Panel (Cell Mol Bio)

```html
<div class="card neutral">
    <h4>Cancer Hallmarks Addressed</h4>
    <ul class="hallmarks-list">
        <li class="addressed">Sustained proliferative signaling</li>
        <li class="addressed">Resisting cell death</li>
        <li class="not-addressed">Evading immune destruction</li>
    </ul>
</div>
```

---

## Section Icons (SVG)

Add inline SVG icons before section headers:

```html
<h2>
    <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <!-- path here -->
    </svg>
    Section Title
</h2>
```

| Section | Icon Path |
|---------|-----------|
| Overview | `<circle cx="12" cy="12" r="3"/><path d="M12 5c-4.5 0-8 3-9 7 1 4 4.5 7 9 7s8-3 9-7c-1-4-4.5-7-9-7z"/>` |
| Context | `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>` |
| Key Findings | `<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>` |
| Methods | `<path d="M9 3h6v5l4 9H5l4-9V3z"/><path d="M9 3h6"/>` |
| Critical Analysis | `<path d="M12 3v18"/><path d="M5 8l7-5 7 5"/><circle cx="5" cy="14" r="3"/><circle cx="19" cy="14" r="3"/>` |
| Implications | `<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>` |
| Strengths | `<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>` |
| Limitations | `<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>` |

---

## Content Guidelines

1. **Preserve all quantitative results** - Include exact numbers, p-values, confidence intervals
2. **Include negative/null results** - Don't cherry-pick positive findings
3. **Mark external observations** - Distinguish authors' stated limitations from your analysis
4. **Use semantic colors correctly**:
   - Teal: Key findings, treatment data
   - Indigo: Highly significant (p < 0.001)
   - Emerald: Validated/replicated findings
   - Rose: Limitations, warnings, negative results
   - Amber: Provisional, preprint status

---

## Verification Checklist

Before finishing, verify:

**Content Accuracy:**
- [ ] All numerical results from markdown included
- [ ] Statistical test details preserved
- [ ] Novel claims distinguished from background
- [ ] Limitations reflect authors' statements
- [ ] Methodology specifics preserved

**Visual Components (Required):**
- [ ] Summary Dashboard present with 3-5 key metrics
- [ ] Evidence Strength Meter reflects mechanistic rigor
- [ ] Workflow Timeline shows experimental progression
- [ ] Model Systems Grid displays all models used

**Visual Components (Conditional):**
- [ ] Hallmarks Radar Chart (Cell/Mol Bio articles)
- [ ] Pathway Diagram (if mechanism described)
- [ ] Comparison Cards (if before/after data exists)
- [ ] Heatmap Tables (if expression/matrix data)
- [ ] Reference Network (if key citations identified)

**Structure:**
- [ ] Navigation links match section IDs
- [ ] Tabs/collapsibles are properly structured
- [ ] Confidence indicators used for quality assessments
- [ ] Animations enabled (`stagger-children` on metric rows)
