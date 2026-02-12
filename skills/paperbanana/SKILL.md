---
name: paperbanana
version: 1.0.0
extends: visual-design
description: "Generate publication-quality academic figures from text descriptions using PaperBanana's multi-agent pipeline. Specialized in graphical abstracts, visual summaries, methodology overviews, and explanation diagrams."
allowed-tools: [Read, Write, Edit, Bash]
shared-thresholds: "../QUANTIFICATION_THRESHOLDS.md"
---

# PaperBanana — Text-to-Visual Figure Generation

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards.

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §2 (Visual Quality), §7 (Quality Rubrics) and §8 (Iteration & Stopping Criteria).

<overview>
Generate publication-quality academic figures from prose text using PaperBanana's multi-agent pipeline. Five specialized agents (Retriever, Planner, Stylist, Visualizer, Critic) collaborate with iterative refinement to produce figures that faithfully communicate the source text's content. Powered by Google Gemini for vision-language understanding and Google Imagen for image generation. Oligon brand styling is applied by default through custom guidelines injected into the Stylist agent.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- User provides paper text, methodology description, or summary and wants a visual representation
- Graphical abstract requests (journal-required visual summaries)
- Visual executive summary diagram requests
- "Explain this visually" / "illustrate this method" requests
- Paper overview figures ("Figure 1" methodology overviews)
- Workflow diagrams generated from textual descriptions (not from explicit node/edge specs)
- Explicit "paperbanana" mention

Do NOT use this skill when:
- User specifies diagram type, nodes, or layout explicitly → use `scientific-schematics`
- Data visualization (plots, charts, histograms, statistical plots) → use `plotting-libraries`
- Photorealistic or artistic images → use `generate-image`
- Design guidance only → use `visual-design`
- Creating CONSORT, PRISMA, circuit, or pathway diagrams from specifications → use `scientific-schematics`
</when_to_use>

<prerequisites>
## Prerequisites

| Dependency | Version | Purpose | Required |
|------------|---------|---------|----------|
| Python | >=3.9 | Runtime environment | Yes |
| paperbanana | latest | Multi-agent figure generation pipeline | Yes |
| GOOGLE_API_KEY | required | Google AI Studio API key for Gemini + Imagen | Yes |

**Installation:**
```bash
# Install PaperBanana
pip install paperbanana

# Set API key (get free from https://aistudio.google.com/apikey)
export GOOGLE_API_KEY='your_key_here'
```

**Verification:**
```bash
# Verify installation
python -c "from paperbanana import PaperBananaPipeline; print('OK')"

# Verify CLI
python {baseDir}/scripts/generate_figure.py --help
```
</prerequisites>

<brand_application>
## Brand Application (Default)

**By default, all figures use Oligon Scientific Brand styling.** Custom Oligon aesthetic guidelines are injected into PaperBanana's Stylist agent.

### Default Styling

Oligon guidelines are loaded from `{baseDir}/data/guidelines/oligon_style.yaml` and applied through:
- Custom Stylist prompt with Oligon color palette
- Guidelines file passed to PaperBanana Settings

```
Primary elements: #2DB2E8 (Brand Blue) - highlights, key components
Contrast/alerts: #E8622D (Orange) - warnings, opposing elements
Text/labels: #222222 (Dark Gray) - primary text
Secondary elements: #666666 (Medium Gray) - supporting components
Background: #FFFFFF (White) - clean background
```

### Disabling Brand Styling

To use generic styling instead of Oligon brand:

**CLI flag:**
```bash
python {baseDir}/scripts/generate_figure.py --input text.txt --output fig.png --no-brand
```

**Explicit request in prompt:**
- "No brand colors" or "Generic color scheme"

**Per-project override:** Add to project `CLAUDE.md`:
```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```
</brand_application>

<decision_framework>
## Decision Matrix

### When to Use PaperBanana vs Other Visual Skills

```
Figure/Visual request
├─ Based on DATA (numbers, measurements, statistics)?
│  └─ YES → plotting-libraries
├─ User specifies diagram type, nodes, or layout?
│  └─ YES → scientific-schematics
├─ User provides TEXT to visualize?
│  (graphical abstract, visual summary, methodology overview)
│  └─ YES → paperbanana
├─ Photorealistic or artistic image?
│  └─ YES → generate-image
└─ Design guidance only?
   └─ YES → visual-design
```

**Boundary principle:** If the input is *prose/text to be visualized*, use `paperbanana`. If the input is *data to be plotted* or a *specific diagram specification*, use the existing skills.

### Quality Threshold by Document Type

> Reference: [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §8

| Document Type | Threshold | Soft Limit | Hard Limit |
|---------------|-----------|------------|------------|
| journal | 8.5/10 | 3 | 5 |
| conference | 8.0/10 | 3 | 5 |
| thesis | 8.0/10 | 3 | 5 |
| grant | 8.0/10 | 3 | 5 |
| preprint | 7.5/10 | 2 | 4 |
| report | 7.5/10 | 2 | 4 |
| poster | 7.0/10 | 2 | 3 |
| presentation | 6.5/10 | 2 | 3 |
| default | 7.5/10 | 3 | 5 |

</decision_framework>

<workflow>
## Workflow

### Stage 1: Context Extraction

**Objective:** Extract and prepare the source text for visualization

**Steps:**
1. Identify source text (paper excerpt, methodology, executive summary)
2. Determine communicative intent (what should the figure convey?)
3. Select document type for quality threshold
4. Check for explicit style preferences

**Exit Criteria:**
- [ ] Source text identified and extracted
- [ ] Communicative intent stated (figure caption / purpose)
- [ ] Document type selected for quality threshold

---

### Stage 2: Generation

**Objective:** Generate figure via PaperBanana pipeline

**Steps:**
1. Load `GOOGLE_API_KEY` via shared `load_api_key()`
2. Create Settings with Oligon brand (unless `--no-brand`)
3. Run `PaperBananaPipeline.generate()` with `DiagramType.METHODOLOGY`
4. Pipeline internally executes: Retriever → Planner → Stylist → Visualizer → Critic
5. Iterative refinement up to configured iteration count

**Command:**
```bash
python {baseDir}/scripts/generate_figure.py \
  --input "methodology_text.txt" \
  --caption "Overview of the RNA-seq analysis pipeline" \
  --output figures/graphical_abstract.png \
  --doc-type journal \
  --iterations 3 \
  -v
```

**Exit Criteria:**
- [ ] Generation completed without errors
- [ ] Image saved to output path
- [ ] Review log saved as JSON

---

### Stage 3: Quality Evaluation

**Objective:** Evaluate figure against publication standards

**Steps:**
1. PaperBanana Critic evaluates on 4 dimensions (Faithfulness, Readability, Conciseness, Aesthetics)
2. Quality bridge maps 4-dim scores → 5-point rubric (10 points total)
3. Compare against document type threshold
4. If below threshold and iterations remain, pipeline refines automatically

**Quality Scoring (mapped from PaperBanana 4-dim to 5-point rubric):**

| PaperBanana Dimension | Maps To | Points |
|---|---|---|
| Faithfulness | Scientific Accuracy | 0-2 |
| Readability | Clarity & Readability + Label Quality | 0-2 each |
| Conciseness | Layout & Composition | 0-2 |
| Aesthetics | Professional Appearance | 0-2 |

**Exit Criteria:**
- [ ] Quality score meets document type threshold
- [ ] Review log includes per-dimension scores
- [ ] No critical issues flagged

---

### Stage 4: Integration

**Objective:** Integrate figure into manuscript/presentation

**Steps:**
1. Move final image to appropriate figures/ directory
2. Write figure caption based on communicative intent
3. Add cross-reference in main text
4. Verify styling consistency with other figures

**Exit Criteria:**
- [ ] Image in correct directory
- [ ] Caption written
- [ ] Figure referenced in text

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Quality score (journal) | 8.0/10 | 8.5/10 | 9.5/10 |
| Quality score (poster) | 6.5/10 | 7.0/10 | 8.0/10 |
| Iteration efficiency | 3 iterations | 2 iterations | 1 iteration |
| Resolution | 150 DPI | 300 DPI | 600 DPI |

**Completion Checklist:**
- [ ] Figure faithfully represents source text
- [ ] Quality score meets document type threshold
- [ ] Communicative intent clearly conveyed
- [ ] Professional, consistent styling
- [ ] Appropriate file format for venue

</success_criteria>

<scope>
## Scope

**In Scope:**
- Graphical abstracts from paper text
- Visual executive summaries
- Methodology overview figures
- Explanation diagrams from prose descriptions
- Workflow diagrams from textual descriptions

**Out of Scope** (use specialized skills):
- Data visualizations (plots, charts) → use `plotting-libraries`
- User-specified diagrams (CONSORT, PRISMA, circuits, pathways) → use `scientific-schematics`
- Photorealistic image generation → use `generate-image`
- Design principles guidance → use `visual-design`
- Statistical plots → use `plotting-libraries`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Using PaperBanana for Data Plots

**Anti-pattern:** Asking PaperBanana to create a bar chart or scatter plot from data.

**Solution:** Use `plotting-libraries` for any data-driven visualization. PaperBanana is for text-to-visual, not data-to-visual.

### 2. Specifying Exact Diagram Layout

**Anti-pattern:** Providing specific node names, edge connections, and layout directions.

**Solution:** Use `scientific-schematics` when you have a specific diagram specification. PaperBanana works best when given prose text and a communicative intent, letting the pipeline determine the best visual representation.

### 3. Missing Communicative Intent

**Anti-pattern:** Only providing source text without explaining what the figure should convey.

**Solution:** Always provide a `--caption` that describes the figure's purpose:
```bash
# Bad: no intent
python {baseDir}/scripts/generate_figure.py --input paper.txt --output fig.png

# Good: clear intent
python {baseDir}/scripts/generate_figure.py --input paper.txt \
  --caption "Graphical abstract showing the three-phase experimental approach" \
  --output fig.png
```

### 4. Wrong Quality Threshold

**Anti-pattern:** Using journal threshold (8.5) for a quick internal presentation.

**Solution:** Match `--doc-type` to actual use case:
- `--doc-type presentation` for slides (6.5 threshold)
- `--doc-type poster` for posters (7.0 threshold)
- `--doc-type journal` only for publication (8.5 threshold)

</anti_patterns>

<error_handling>
## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `GOOGLE_API_KEY not set` | Missing environment variable | Set via `export GOOGLE_API_KEY='your_key'` (get from https://aistudio.google.com/apikey) |
| `ImportError: paperbanana` | Package not installed | Run `pip install paperbanana` |
| `Score < threshold after max iterations` | Complex text or vague intent | Refine caption with more specific communicative intent |
| `Connection timeout` | Network issues | Check internet, retry |
| `API quota exceeded` | Too many requests | Wait and retry, or use fewer iterations |

**Recovery Patterns:**
1. **Low scores:** Review critique in review_log.json, improve caption specificity
2. **API failures:** Script saves partial results; check review log for last successful iteration
3. **Style issues:** Try `--no-brand` to see if brand injection causes problems
</error_handling>

<templates>
## Output Templates

### Generation Commands

```bash
# Basic generation from text file
python {baseDir}/scripts/generate_figure.py \
  --input methodology.txt \
  --caption "Overview of the experimental workflow" \
  --output figures/graphical_abstract.png

# Journal-quality with verbose output
python {baseDir}/scripts/generate_figure.py \
  --input paper_excerpt.txt \
  --caption "Graphical abstract for Nature submission" \
  --output figures/fig1_overview.png \
  --doc-type journal \
  --iterations 3 \
  -v

# Without brand styling
python {baseDir}/scripts/generate_figure.py \
  --input methods.txt \
  --caption "Method overview for conference poster" \
  --output figures/poster_fig.png \
  --doc-type poster \
  --no-brand

# With custom reference images
python {baseDir}/scripts/generate_figure.py \
  --input pipeline.txt \
  --caption "Data processing pipeline" \
  --output figures/pipeline.png \
  --reference-dir path/to/example_figures/
```

### Standalone Evaluation

```bash
# Evaluate an existing figure against source text
python {baseDir}/scripts/evaluate_figure.py \
  --image figures/graphical_abstract.png \
  --source methodology.txt \
  --doc-type journal
```

### Review Log Structure

```json
{
  "source_text_preview": "First 200 chars of input...",
  "caption": "Communicative intent",
  "doc_type": "journal",
  "quality_threshold": 8.5,
  "brand_enabled": true,
  "iterations": [
    {
      "iteration": 1,
      "image_path": "figures/fig_v1.png",
      "paperbanana_scores": {
        "faithfulness": 0.85,
        "readability": 0.78,
        "conciseness": 0.82,
        "aesthetics": 0.90
      },
      "rubric_scores": {
        "scientific_accuracy": 1.7,
        "clarity_readability": 1.6,
        "label_quality": 1.6,
        "layout_composition": 1.6,
        "professional_appearance": 1.8
      },
      "total_score": 8.3,
      "meets_threshold": false
    }
  ],
  "final_score": 8.7,
  "final_image": "figures/graphical_abstract.png"
}
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `plotting-libraries` | Use for data visualizations; paperbanana for text-to-visual |
| `scientific-schematics` | Use for specified diagrams; paperbanana for prose-to-figure |
| `generate-image` | Use for photorealistic images; paperbanana for academic figures |
| `visual-design` | Consult for design principles before creating figures |
| `executive-summary` | Pair with paperbanana for visual executive summaries |
| `scientific-writing` | Paperbanana provides methodology figures for papers |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. `scientific-writing` or `executive-summary` → produce text content
2. `paperbanana` → generate visual figure from text
3. `scientific-slides` or `research-posters` → integrate into presentation

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/integration_notes.md` | Architecture decisions and PaperBanana version notes |
| `{baseDir}/data/guidelines/oligon_style.yaml` | Oligon aesthetic guidelines for Stylist agent |

### External Resources

- PaperBanana PyPI: https://pypi.org/project/paperbanana/
- PaperBanana GitHub: https://github.com/llmsresearch/paperbanana
- Google AI Studio (API key): https://aistudio.google.com/apikey

### Environment Setup

```bash
# Required
export GOOGLE_API_KEY='your_api_key_here'

# Get key at: https://aistudio.google.com/apikey
```

</references>
