---
name: paperbanana
version: 1.0.1
extends: visual-design
description: "Generate publication-quality academic figures from unstructured text/prose using PaperBanana's multi-agent AI pipeline. Specialized in graphical abstracts, visual summaries, and methodology overviews. Use when the user provides text and wants a polished figure without specifying exact layout or nodes. Do NOT use when user specifies diagram type, nodes, or relationships — use scientific-schematics."
allowed-tools: [Read, Write, Edit, Bash]
shared-thresholds: "../QUANTIFICATION_THRESHOLDS.md"
---

# PaperBanana — Text-to-Visual Figure Generation

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards. Cognitive-foundation citations (Cleveland-McGill 1984, Wagemans 2012 Gestalt grouping, Crameri 2020 colour, Fujii 2026 communication context, Weissgerber 2015 if continuous data) and cross-skill quality gates also live in [`oligon-brand`](../oligon-brand/SKILL.md) `<design_foundation>` and [`shared/references/`](../shared/references/) (`pre_submission_checklist.md`, `communication_context_matrix.md`, `figure_vs_table_decision.md`).

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §2 (Visual Quality), §7 (Quality Rubrics) and §8 (Iteration & Stopping Criteria).

<overview>
Generate publication-quality academic figures from prose text using PaperBanana's multi-agent pipeline. Five specialized agents (Retriever, Planner, Stylist, Visualizer, Critic) collaborate with iterative refinement to produce figures that faithfully communicate the source text's content. Powered by Google Gemini for vision-language understanding and Google Imagen for image generation. Oligon brand styling is applied by default through custom guidelines injected into the Stylist agent.

**Multi-Variant Mode** (`--variants N`): Generate N different visual interpretations of the same text, automatically rank them, refine the winner, and produce an interactive HTML review tool for comparing and annotating variants.
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
3. **Tag the communication context** (Fujii 2026 — see `../shared/references/communication_context_matrix.md`):
   - `audience: lay | specialist`
   - `setting: oral | article | poster | online`
   - `time: brief | moderate | extended`
4. Select document type for quality threshold
5. Check for explicit style preferences

**Exit Criteria:**
- [ ] Source text identified and extracted
- [ ] Communicative intent stated (figure caption / purpose)
- [ ] Communication-context tag set (audience / setting / time)
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

### Stage 2b: Multi-Variant Generation (Optional)

**Objective:** Generate multiple visual interpretations and select the best one

**When to use:** Add `--variants N` to produce N different figure variants instead of a single figure. Recommended for high-stakes figures (journal submissions, graphical abstracts) where exploring multiple visual approaches yields better results.

**Steps:**
1. Generate N variant communicative intents using different strategies:
   - **FAITHFUL**: Original caption verbatim (always included as baseline)
   - **ENHANCED**: Elevated visual detail and scientific precision
   - **ALT_COMPOSITION**: Fundamentally different layout/composition
   - **STYLE_VARIATION**: Different visual style emphasis
   - **BOLD_CREATIVE**: Unconventional approach with scientific rigor
2. Run PaperBanana pipeline for each intent (1 iteration each)
3. Rank all variants via multimodal Gemini evaluation on 4 dimensions
4. Optionally refine the winning variant with additional iterations

**Command:**
```bash
python {baseDir}/scripts/generate_figure.py \
  --input "methodology_text.txt" \
  --caption "Overview of the RNA-seq analysis pipeline" \
  --output figures/graphical_abstract.png \
  --variants 3 \
  --doc-type journal \
  -v
```

**Architecture:**
```
generate_figure.py --variants 3
  ├─ variant_intents.py → 3 different captions (FAITHFUL, ENHANCED, ALT_COMPOSITION)
  ├─ variant_orchestrator.py → 3 sequential pipeline runs (30s delay between)
  ├─ variant_ranker.py → single multimodal Gemini call to rank all 3
  ├─ Refine winner with 2 additional iterations
  └─ Save JSON log + HTML review tool
```

**Exit Criteria:**
- [ ] N variant images generated
- [ ] Variants ranked with composite scores
- [ ] Winner refined (unless `--no-refine`)
- [ ] Review log JSON and HTML saved

---

### Stage 2c: Visual Review (Optional)

**Objective:** Interactively compare, annotate, and select variant figures

**When to use:** After multi-variant generation, open the HTML review tool to visually compare variants, add per-figure feedback, and compile a revision prompt.

**Steps:**
1. Open the generated HTML review file in a browser
2. Gallery view: compare all variants with score breakdowns
3. Compare view: side-by-side with score deltas
4. Add per-variant annotations and global notes
5. Click "Compile Revision Prompt" to generate structured feedback

**Command:**
```bash
# Generate HTML from an existing review log
python {baseDir}/scripts/review_variants.py \
  --input figures/fig_variant_review_log.json \
  --embed-images \
  --open
```

The compiled revision prompt can be used as `--caption` input for a focused refinement run.

**Exit Criteria:**
- [ ] HTML review page opens in browser
- [ ] Variant selection and annotations captured
- [ ] Revision prompt compiled (if needed)

---

### Stage 3: Quality Evaluation

**Objective:** Evaluate figure against publication standards

**Steps:**
1. PaperBanana Critic evaluates on 4 dimensions (Faithfulness, Readability, Conciseness, Aesthetics)
2. **Communication-context fit check (Fujii 2026):** confirm the figure's complexity matches the Stage 1 context tag (audience / setting / time). E.g., an `oral / brief / lay` figure with 4 panels and 12 colours fails this check; a single-message annotated figure passes. Cross-reference `../shared/references/communication_context_matrix.md`.
3. Quality bridge maps 4-dim scores → 5-point rubric (10 points total)
4. Compare against document type threshold
5. If below threshold and iterations remain, pipeline refines automatically

**Quality Scoring (mapped from PaperBanana 4-dim to 5-point rubric):**

| PaperBanana Dimension | Maps To | Points |
|---|---|---|
| Faithfulness | Scientific Accuracy | 0-2 |
| Readability | Clarity & Readability + Label Quality | 0-2 each |
| Conciseness | Layout & Composition | 0-2 |
| Aesthetics | Professional Appearance | 0-2 |
| **Communication-context fit (added)** | Reviewer-mediated check against Stage 1 context tag | gating, not scored |

**Exit Criteria:**
- [ ] Quality score meets document type threshold
- [ ] Review log includes per-dimension scores
- [ ] **Figure complexity matches Stage 1 communication-context tag** (Fujii 2026)
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

### 4. Overusing Variant Mode

**Anti-pattern:** Using `--variants 5` for every quick draft or internal figure.

**Solution:** Variant mode costs ~2-3x a single run. Use it strategically:
- Quick drafts / presentations: single mode (no `--variants`)
- Journal figures / graphical abstracts: `--variants 3`
- High-stakes competition figures: `--variants 5`

### 5. Wrong Quality Threshold

**Anti-pattern:** Using journal threshold (8.5) for a quick internal presentation.

**Solution:** Match `--doc-type` to actual use case:
- `--doc-type presentation` for slides (6.5 threshold)
- `--doc-type poster` for posters (7.0 threshold)
- `--doc-type journal` only for publication (8.5 threshold)

### 6. Trusting GenAI Output Without a Communication-Context Review

**Anti-pattern:** Treating Imagen / Gemini output as final without reviewing it against the figure's actual viewing context.

**Solution:** Per Fujii 2026 §"Choose the right graph and colour", GenAI text-to-figure tools tend to map data 1:1 to a default visualisation without considering message, audience, or interaction context. After every generation, run the post-generation review:

1. **Key message check:** does the figure convey the single takeaway from the caption / Stage 1 input?
2. **Communication-context tag check:** does the complexity match the Stage 1 audience / setting / time tag? See `../shared/references/communication_context_matrix.md`.
3. **Figure-design canon check:** does the output respect Cleveland-McGill 1984 channel ranking, Crameri 2020 colour, Wagemans 2012 direct-labelling, and (if continuous data is involved) Weissgerber 2015? See `../oligon-brand/SKILL.md` `<design_foundation>`.

If any check fails, iterate via the Critic loop or refine the caption with more specific intent. Do not accept the first generation as final for journal-grade output.

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
4. **Variant mode failures:** Individual variant failures are caught and skipped; ranking falls back to equal scores if Gemini call fails; partial results are always saved
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

### Multi-Variant Generation Commands

```bash
# Generate 3 variants with ranking and refinement
python {baseDir}/scripts/generate_figure.py \
  --input methods.txt \
  --caption "Methodology overview" \
  --output figures/fig.png \
  --variants 3 \
  --doc-type journal \
  -v

# Generate 5 variants without winner refinement
python {baseDir}/scripts/generate_figure.py \
  --input methods.txt \
  --caption "Overview of experimental pipeline" \
  --output figures/fig.png \
  --variants 5 \
  --no-refine

# Generate variants with custom delay between runs
python {baseDir}/scripts/generate_figure.py \
  --input abstract.txt \
  --caption "Graphical abstract" \
  --output figures/abstract.png \
  --variants 3 \
  --variant-delay 45

# Generate HTML review from existing log
python {baseDir}/scripts/review_variants.py \
  --input figures/fig_variant_review_log.json \
  --embed-images \
  --open
```

### JSON Spec Mode (experimental)

Pass a structured `scientific_figure` JSON spec instead of prose. The spec is validated, optionally patched, and deterministically translated into the prose `source_context` + `communicative_intent` that PaperBanana already consumes — backend and pipeline are unchanged. Purpose: enable scoped re-rolls (change one element without rewriting everything).

- Schema: `{baseDir}/references/scientific_figure.schema.json`
- Worked example: `{baseDir}/references/examples/spec_egfr_inhibition.json`
- Patches use [RFC 6902 JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902) (replace / add / remove)

```bash
# Generate v1 from a spec, save the effective spec for later re-patching
python {baseDir}/scripts/generate_figure.py \
  --spec {baseDir}/references/examples/spec_egfr_inhibition.json \
  --save-spec figures/egfr_v1.spec.json \
  --output figures/egfr_v1.png

# Re-roll only the aesthetic via a JSON Patch (components + brand stay locked)
cat > /tmp/patch_aesthetic.json <<'JSON'
[{"op": "replace", "path": "/scientific_figure/style/aesthetic", "value": "infographic"}]
JSON

python {baseDir}/scripts/generate_figure.py \
  --spec figures/egfr_v1.spec.json \
  --patch /tmp/patch_aesthetic.json \
  --save-spec figures/egfr_v2.spec.json \
  --output figures/egfr_v2.png
```

Spike status: this mode is gated on a 9-figure iteration-cost benchmark (3 base specs × 3 scoped patches each). Ship-criterion: ≥6/9 patches produce visually scoped changes. Below that, the mode does not generalise to other skills and gets removed.

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

### Variant Review Log Structure

```json
{
  "source_text_preview": "First 200 chars...",
  "caption": "Communicative intent",
  "doc_type": "journal",
  "brand_enabled": true,
  "n_variants": 3,
  "variants": [
    {
      "index": 0,
      "strategy": "faithful",
      "image_path": "figures/fig_v0.png",
      "communicative_intent": "Original caption...",
      "scores": {"faithfulness": 0.85, "readability": 0.78, "conciseness": 0.82, "aesthetics": 0.90}
    }
  ],
  "ranking": {
    "winner_index": 1,
    "rationale": "Variant 1 scored highest...",
    "scores": [
      {"variant_index": 1, "strategy": "enhanced", "faithfulness": 0.92, "readability": 0.85, "conciseness": 0.80, "aesthetics": 0.88, "composite_score": 0.87, "rank": 1}
    ]
  },
  "refined_image_path": "figures/fig_refined.png"
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
| `oligon-brand` | Consult `<design_foundation>` for cognitive-foundation citations (Cleveland, Crameri, Fujii 2026) — complementary to visual-design |
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
| `{baseDir}/references/scientific_figure.schema.json` | JSON Schema for `--spec` mode (graphical abstracts, methodology, mechanism diagrams) |
| `{baseDir}/references/examples/spec_egfr_inhibition.json` | Worked example for JSON spec mode |
| `{baseDir}/data/guidelines/oligon_style.yaml` | Oligon aesthetic guidelines for Stylist agent |
| `../shared/references/iconography-licensing.md` | Icon-library licensing (BioRender, NIH BIOART, SciDraw, Servier, Noun Project) — re-verify at submission |
| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (Q0 = "should this be a table?") |
| `../shared/references/communication_context_matrix.md` | Audience × time × interaction → figure complexity (Fujii 2026) |
| `../shared/references/figure_vs_table_decision.md` | Decision aid for figure vs table vs both (Fujii 2026; Midway 2020) |
| `../oligon-brand/SKILL.md` `<design_foundation>` | Cognitive-foundation citations (Cleveland-McGill, Crameri, Wilke, Fujii 2026, Weissgerber 2015 for plots, etc.) |

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
