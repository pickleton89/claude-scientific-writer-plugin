---
name: scientific-schematics
version: 2.3.0
extends: visual-design
description: "Create publication-quality scientific diagrams using Nano Banana Pro AI with iterative refinement and Gemini 3 Flash/Pro quality review. Specialized in neural networks, flowcharts, biological pathways, and system architectures."
allowed-tools: [Read, Write, Edit, Bash]
shared-thresholds: "../QUANTIFICATION_THRESHOLDS.md"
---

# Scientific Schematics and Diagrams

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards.

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §7 (Quality Rubrics) and §8 (Iteration & Stopping Criteria).

<overview>
Generate publication-quality scientific diagrams through AI-powered creation with iterative refinement. Uses Nano Banana Pro for image generation and Gemini 3 Flash (default) or Pro for quality review. Smart iteration stops early when quality score ≥ document threshold (6.5-8.5/10), with soft limit of 3 iterations and hard limit of 5 iterations per diagram.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Creating neural network architecture diagrams (Transformers, CNNs, RNNs)
- Designing methodology flowcharts (CONSORT, PRISMA, study design)
- Illustrating biological pathways and molecular interactions
- Generating system architecture and data flow diagrams
- Drawing circuit diagrams and electrical schematics
- Creating algorithm workflows and processing pipelines
- Designing conceptual frameworks and theoretical models

Do NOT use this skill when:
- Creating data visualizations (plots, charts) → use `plotting-libraries`
- Generating photorealistic images → use `generate-image`
- Designing slides or posters → use `scientific-slides`, `latex-posters`, `pptx-posters`
- Need design philosophy guidance → use `visual-design`
</when_to_use>

<prerequisites>
## Prerequisites

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.9 | Runtime environment |
| requests | any | HTTP API calls to OpenRouter |
| OPENROUTER_API_KEY | required | Environment variable for API authentication |

**Installation:**
```bash
# Install Python dependency
pip install requests

# Set API key (get from https://openrouter.ai/keys)
export OPENROUTER_API_KEY='sk-or-v1-your_key_here'
```

**Verification:**
```bash
# Verify setup
python {baseDir}/scripts/generate_schematic.py --help
```
</prerequisites>

<decision_framework>
## Decision Matrix

### Schematic Type Selection

```
What do you need to visualize?
│
├─ Study Design / Methodology
│  │
│  ├─ Clinical trial participant flow → CONSORT flowchart
│  │
│  ├─ Systematic review article flow → PRISMA flowchart
│  │
│  ├─ General experimental procedure → Methods flowchart
│  │
│  └─ Data processing pipeline → Pipeline diagram
│
├─ Machine Learning / AI
│  │
│  ├─ Attention-based model → Transformer architecture
│  │
│  ├─ Image processing model → CNN architecture
│  │
│  ├─ Sequential data model → RNN/LSTM architecture
│  │
│  └─ General neural network → Block diagram with layers
│
├─ Biological Systems
│  │
│  ├─ Signal transduction → Pathway diagram (MAPK, PI3K, etc.)
│  │
│  ├─ Metabolic process → Metabolic pathway
│  │
│  ├─ Gene regulation → Regulatory network
│  │
│  └─ Protein interactions → Interaction network
│
├─ Systems / Engineering
│  │
│  ├─ Software components → System architecture
│  │
│  ├─ Hardware connections → Block diagram
│  │
│  ├─ Data flow → Data flow diagram
│  │
│  └─ Electronic circuit → Circuit schematic
│
└─ Abstract Concepts
   │
   ├─ Theoretical framework → Conceptual diagram
   │
   ├─ Classification system → Hierarchy diagram
   │
   └─ Process overview → Block diagram
```

### Quality Threshold by Document Type

> Reference: [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §8

| Document Type | Threshold | Soft Limit | Hard Limit | Use Case |
|---------------|-----------|------------|------------|----------|
| journal | 8.5/10 | 3 | 5 | Nature, Science, peer-reviewed journals |
| conference | 8.0/10 | 3 | 5 | Conference papers |
| thesis | 8.0/10 | 3 | 5 | Dissertations, theses |
| grant | 8.0/10 | 3 | 5 | Grant proposals |
| preprint | 7.5/10 | 2 | 4 | arXiv, bioRxiv preprints |
| report | 7.5/10 | 2 | 4 | Technical reports |
| poster | 7.0/10 | 2 | 3 | Academic posters |
| presentation | 6.5/10 | 2 | 3 | Slides, talks |
| default | 7.5/10 | 3 | 5 | General purpose |

**Iteration Behavior:**
- **Soft limit:** Target iterations; stop if quality ≥ threshold OR soft limit reached
- **Hard limit:** Absolute maximum; never exceed regardless of quality score

### Tool Selection Matrix

| Diagram Type | Primary Tool | Alternative | Export Format |
|--------------|--------------|-------------|---------------|
| Flowcharts (CONSORT, PRISMA) | Nano Banana Pro | TikZ/LaTeX | PNG, PDF |
| Neural Network Architecture | Nano Banana Pro | draw.io | PNG, SVG |
| Biological Pathways | Nano Banana Pro | BioRender | PNG, PDF |
| Circuit Diagrams | Nano Banana Pro | Schemdraw | PNG, PDF |
| System Architecture | Nano Banana Pro | Mermaid | PNG, SVG |
| Block Diagrams | Nano Banana Pro | TikZ/LaTeX | PNG, PDF |

</decision_framework>

<workflow>
## Workflow

### Stage 1: Requirements Analysis

**Objective:** Understand diagram requirements and constraints

**Steps:**
1. Identify diagram type from decision matrix
2. Determine document type for quality threshold
3. List all components to include
4. Define flow direction (top-to-bottom, left-to-right)
5. Identify labeling requirements

**Exit Criteria:**
- [ ] Diagram type identified (flowchart, architecture, pathway, etc.)
- [ ] Document type selected (journal, poster, presentation, etc.)
- [ ] Component list complete (≥3 elements for meaningful diagram)
- [ ] Flow direction specified
- [ ] Key labels documented

---

### Stage 2: Prompt Construction

**Objective:** Create effective prompt for AI generation

**Steps:**
1. Start with diagram type and layout specification
2. Add specific components with relationships
3. Include quantitative details (node counts, dimensions)
4. Specify visual style preferences
5. Add accessibility requirements (colorblind-safe)

**Exit Criteria:**
- [ ] Prompt specifies diagram type explicitly
- [ ] All components listed with connections
- [ ] Flow direction stated
- [ ] Label requirements included
- [ ] Prompt length 50-200 words (optimal range)

**Prompt Template:**
```
{{DIAGRAM_TYPE}} diagram showing {{MAIN_SUBJECT}}.

Layout: {{FLOW_DIRECTION}} (top-to-bottom/left-to-right/circular)

Components:
- {{Component 1}} connected to {{Component 2}} via {{relationship}}
- {{Component 3}} with label "{{label text}}"
- ...

Quantitative details: {{specific numbers, dimensions, counts}}

Visual style: {{style preferences}}
- Colorblind-friendly palette
- Clear labels (minimum 10pt)
- Professional typography
```

---

### Stage 3: AI Generation

**Objective:** Generate diagram with quality review

**Steps:**
1. Set OPENROUTER_API_KEY environment variable
2. Execute generation script with document type
3. Nano Banana Pro generates initial image
4. Gemini 3 Flash (or Pro) reviews quality against threshold
5. If quality < threshold AND iterations < max, improve and regenerate

**Exit Criteria:**
- [ ] API key configured and valid
- [ ] Generation completed without errors
- [ ] Quality score ≥ document type threshold
- [ ] Image saved to figures/ directory
- [ ] Review log saved as JSON

**Command:**
```bash
python {baseDir}/scripts/generate_schematic.py "{{prompt}}" \
  -o figures/{{output_name}}.png \
  --doc-type {{document_type}} \
  --iterations 2 \
  -v
# For high-stakes work, use Pro review:
# --review-model pro
```

**Smart Iteration Logic:**
```
Generate Image → Review Quality → Score >= Threshold?
                                        │
                                        ├─ YES → DONE (early stop)
                                        │
                                        └─ NO → Iteration < Hard Limit?
                                                     │
                                                     ├─ NO → DONE (hard limit reached)
                                                     │
                                                     └─ YES → Iteration < Soft Limit?
                                                                   │
                                                                   ├─ YES → Improve prompt, regenerate
                                                                   │
                                                                   └─ NO → Score improving? (Δ ≥ 0.5)
                                                                                │
                                                                                ├─ YES → Continue to hard limit
                                                                                │
                                                                                └─ NO → DONE (diminishing returns)
```

**Stopping Criteria** (from §8):

| Stop When | Reason |
|-----------|--------|
| Quality score ≥ threshold | Target achieved |
| Soft limit reached AND score not improving | Diminishing returns |
| Hard limit reached | Absolute maximum |
| Score improvement < 0.5 between iterations | Plateau detected |
| Critical error in generation | Cannot proceed |

---

### Stage 4: Quality Verification

**Objective:** Verify diagram meets publication standards

**Steps:**
1. Review quality assessment from Gemini 3 Flash/Pro
2. Check 5 quality dimensions (see scoring rubric)
3. Verify accessibility (colorblind-safe, contrast)
4. Confirm all labels readable at final size
5. Validate file format and resolution

**Exit Criteria:**
- [ ] Overall quality score ≥ threshold for document type
- [ ] No high-severity issues in quality report
- [ ] Colorblind simulation passes
- [ ] Text readable at target reproduction size
- [ ] File format appropriate (PNG for web, PDF for print)

**Quality Scoring Rubric (10 points total):**

> Reference: [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §7 (Schematic Quality Rubric)

| Dimension | Points | 0 (Fail) | 1 (Acceptable) | 2 (Excellent) |
|-----------|--------|----------|----------------|---------------|
| Scientific Accuracy | 0-2 | Factual errors | Minor issues | Scientifically accurate |
| Clarity & Readability | 0-2 | Confusing layout | Understandable | Intuitive flow |
| Label Quality | 0-2 | Missing/unreadable | Present but issues | Clear, consistent |
| Layout & Composition | 0-2 | Overlaps/cramped | Reasonable spacing | Balanced, logical |
| Professional Appearance | 0-2 | Amateur look | Acceptable | Publication-ready |

**Score Interpretation:**
- 0-4: Needs revision (below all thresholds)
- 5-6: Acceptable for presentations/posters
- 7-8: Acceptable for preprints/reports
- 9-10: Publication-ready (journal quality)

---

### Stage 5: Integration

**Objective:** Integrate diagram into manuscript/presentation

**Steps:**
1. Move final image to appropriate figures/ directory
2. Add to LaTeX with `\includegraphics{}`
3. Write comprehensive figure caption
4. Add cross-reference in main text
5. Verify consistent styling with other figures

**Exit Criteria:**
- [ ] Image in correct directory
- [ ] Caption describes all diagram elements
- [ ] Abbreviations defined in caption
- [ ] Figure referenced in text (e.g., "Figure 1 shows...")
- [ ] Style consistent with other manuscript figures

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Quality score (journal) | 8.0/10 | 8.5/10 | 9.5/10 |
| Quality score (poster) | 6.5/10 | 7.0/10 | 8.0/10 |
| Iteration efficiency | 2 iterations | 1 iteration | 1 iteration |
| Label readability | 8pt at final | 10pt at final | 12pt at final |
| Resolution | 150 DPI | 300 DPI | 600 DPI |

**Completion Checklist:**
- [ ] Diagram type matches content requirements
- [ ] Quality score meets document type threshold
- [ ] All components present and labeled
- [ ] Colorblind-accessible palette used
- [ ] No overlapping elements
- [ ] Professional, consistent styling
- [ ] Appropriate file format for venue

</success_criteria>

<scope>
## Scope

**In Scope:**
- AI-generated scientific diagrams via Nano Banana Pro
- Quality review via Gemini 3 Flash (default) or Pro
- CONSORT/PRISMA flowcharts
- Neural network architecture diagrams
- Biological pathway illustrations
- System architecture diagrams
- Circuit schematics
- Conceptual frameworks

**Out of Scope** (use specialized resources):
- Data visualizations (plots, charts) → use `plotting-libraries`
- Photorealistic image generation → use `generate-image`
- Slide design → use `scientific-slides`
- Poster layout → use `latex-posters`, `pptx-posters`
- Design principles → use `visual-design`
- Hand-drawn or sketch-style diagrams → external tools

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Vague Prompts

**Anti-pattern:**
```
"Make a flowchart"
"Neural network diagram"
"Pathway illustration"
```

**Solution:**
```
"CONSORT participant flow diagram with 500 screened,
150 excluded (80 age<18, 50 declined, 20 other),
350 randomized into treatment (n=175) and control (n=175) arms.
Show lost to follow-up (15 treatment, 10 control) and final
analyzed (160 treatment, 165 control). Top-to-bottom layout."
```

---

### 2. Missing Component Details

**Anti-pattern:**
```
"Transformer architecture"
```

**Solution:**
```
"Transformer encoder-decoder architecture.
Left: Encoder with input embedding, positional encoding,
multi-head self-attention (8 heads), add & norm, feed-forward, add & norm.
Right: Decoder with output embedding, positional encoding, masked self-attention,
cross-attention from encoder, add & norm, feed-forward, linear & softmax.
Show cross-attention connection with dashed line."
```

---

### 3. Wrong Quality Threshold

**Anti-pattern:**
Using journal-quality threshold (8.5) for a quick internal presentation, wasting API calls on unnecessary refinement.

**Solution:**
Match document type to use case:
- `--doc-type presentation` for slides (6.5 threshold)
- `--doc-type poster` for posters (7.0 threshold)
- `--doc-type journal` only for publication (8.5 threshold)

---

### 4. Ignoring Accessibility

**Anti-pattern:**
Using red/green color scheme for distinguishing elements.

**Solution:**
Always specify in prompt:
- "Colorblind-friendly colors (Okabe-Ito palette)"
- "High contrast for readability"
- Add redundant encoding (shapes, patterns, labels)

---

### 5. No Flow Direction

**Anti-pattern:**
Not specifying layout direction, getting inconsistent results.

**Solution:**
Always specify flow:
- "Top-to-bottom layout" for vertical processes
- "Left-to-right layout" for horizontal sequences
- "Circular layout" for cycles
- "Hierarchical layout" for tree structures

---

### 6. Overcrowded Diagrams

**Anti-pattern:**
Requesting too many elements in a single diagram.

**Solution:**
Limit complexity per diagram type:

| Diagram Type | Max Elements | Max Connections | Max Hierarchy Levels |
|--------------|--------------|-----------------|---------------------|
| Flowchart | 15 nodes | 20 edges | 4 levels |
| Neural network | 12 layers | — | 3 groups |
| Pathway | 10 molecules | 12 reactions | 3 cascades |
| System architecture | 12 components | 15 connections | 3 tiers |
| Block diagram | 10 blocks | 12 arrows | 2 levels |

**When exceeding limits:**
- Break into multiple figures (overview + detail)
- Use hierarchical views with zoom levels
- Create figure panels (a, b, c) for related components

</anti_patterns>

<error_handling>
## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `OPENROUTER_API_KEY not set` | Missing environment variable | Run `export OPENROUTER_API_KEY='your_key'` |
| `401 Unauthorized` | Invalid or expired API key | Verify key at https://openrouter.ai/keys |
| `429 Rate Limited` | Too many requests | Wait 60 seconds, reduce iteration count |
| `Connection timeout` | Network issues | Check internet connection, retry |
| `Score < threshold after max iterations` | Complex diagram or vague prompt | Refine prompt with more specific details |
| `FileNotFoundError: scripts/` | Wrong working directory | Run from skill directory or use `{baseDir}` paths |
| `ImportError: requests` | Missing dependency | Run `pip install requests` |

**Recovery Patterns:**

1. **API failures**: The script saves partial results; check `*_review_log.json` for last successful iteration
2. **Low scores**: Review critique in JSON log, improve prompt specificity
3. **Timeout**: Reduce diagram complexity or break into multiple figures
</error_handling>

<templates>
## Output Templates

### Generation Command

```bash
# Basic usage
python {baseDir}/scripts/generate_schematic.py "{{prompt}}" -o figures/{{name}}.png

# With document type
python {baseDir}/scripts/generate_schematic.py "{{prompt}}" \
  -o figures/{{name}}.png \
  --doc-type {{journal|conference|thesis|grant|preprint|report|poster|presentation}}

# Verbose with custom iterations
python {baseDir}/scripts/generate_schematic.py "{{prompt}}" \
  -o figures/{{name}}.png \
  --doc-type journal \
  --iterations 2 \
  -v
```

### Example Prompts by Type

**CONSORT Flowchart:**
```
CONSORT participant flow diagram for randomized controlled trial.
Top: 'Assessed for eligibility (n=500)'.
Exclusion box: 'Excluded (n=150)' with reasons: age<18 (n=80), declined (n=50), other (n=20).
Randomization: 'Randomized (n=350)' splits to Treatment (n=175) and Control (n=175).
Follow-up losses: Treatment lost n=15, Control lost n=10.
Analysis: Treatment analyzed n=160, Control analyzed n=165.
Top-to-bottom layout, blue process boxes, orange exclusion, green analysis.
```

**Neural Network Architecture:**
```
Transformer encoder-decoder architecture diagram.
Encoder (left): Input embedding → Positional encoding → Multi-head self-attention (8 heads) →
Add & Norm → Feed-forward → Add & Norm.
Decoder (right): Output embedding → Positional encoding → Masked self-attention →
Add & Norm → Cross-attention (from encoder) → Add & Norm → Feed-forward → Add & Norm →
Linear → Softmax.
Cross-attention connection shown with dashed arrow.
Light blue encoder blocks, light red decoder blocks.
```

**Biological Pathway:**
```
MAPK signaling pathway diagram.
Cell membrane at top with EGFR receptor.
Sequential cascade: EGFR → RAS (GTP-bound) → RAF kinase → MEK kinase → ERK kinase → Nucleus.
Label each arrow with 'phosphorylation' or 'activation'.
Rounded rectangles for proteins, different colors for each.
Include membrane boundary line at top.
Vertical top-to-bottom layout.
```

### Review Log Structure

```json
{
  "user_prompt": "{{original prompt}}",
  "doc_type": "{{document type}}",
  "quality_threshold": {{threshold value}},
  "iterations": [
    {
      "iteration": 1,
      "image_path": "figures/{{name}}_v1.png",
      "score": {{score}},
      "needs_improvement": {{true|false}},
      "critique": "{{Gemini review text}}"
    }
  ],
  "final_score": {{final score}},
  "early_stop": {{true|false}},
  "early_stop_reason": "{{reason if early stopped}}"
}
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `plotting-libraries` | Use for data visualizations (plots, charts); schematics for diagrams |
| `visual-design` | Consult for design principles before creating schematics |
| `generate-image` | Use for photorealistic images; schematics for diagrams |
| `scientific-slides` | Schematics integrates into slide presentations |
| `latex-posters` | Schematics provides figures for posters |
| `scientific-writing` | Schematics provides methodology diagrams for papers |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. `visual-design` → establish design direction
2. `scientific-schematics` → generate diagram
3. `scientific-writing` or `scientific-slides` → integrate into document

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/diagram_types.md` | Catalog of scientific diagram types with prompt keywords |
| `{baseDir}/references/best_practices.md` | Publication standards and accessibility guidelines |
| `{baseDir}/references/quick_reference.md` | Quick start guide and common examples |

### External Resources

**Publication Standards:**
- Nature Figure Guidelines: https://www.nature.com/nature/for-authors/final-submission
- Science Figure Guidelines: https://www.science.org/content/page/instructions-preparing-initial-manuscript
- CONSORT Diagram: http://www.consort-statement.org/consort-statement/flow-diagram
- PRISMA Flow Diagram: http://www.prisma-statement.org/

**Accessibility:**
- Okabe-Ito Color Palette: https://jfly.uni-koeln.de/color/
- Color Oracle (colorblind simulator): https://colororacle.org/

### Environment Setup

```bash
# Required
export OPENROUTER_API_KEY='your_api_key_here'

# Get key at: https://openrouter.ai/keys
```

</references>
