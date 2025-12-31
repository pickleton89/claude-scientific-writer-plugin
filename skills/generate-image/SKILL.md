---
name: generate-image
version: 2.2.0
extends: visual-design
description: "Generate and edit images using AI models (FLUX, Gemini) via OpenRouter. For photos, illustrations, artwork, and visual assets. Use scientific-schematics for technical diagrams."
allowed-tools: [Read, Write, Edit, Bash]
quantification-reference: "../QUANTIFICATION_THRESHOLDS.md"
---

# Generate Image

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards.

<overview>
Generate and edit high-quality images using OpenRouter's image generation models including FLUX.2 Pro and Gemini 3 Pro. Produces photos, illustrations, artwork, and visual assets for scientific documents, presentations, and publications. For technical diagrams (flowcharts, circuits, pathways), use `scientific-schematics` instead.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Generating photorealistic images for documents
- Creating artistic illustrations and concept art
- Producing visual assets for presentations or posters
- Editing existing images (background changes, modifications)
- Creating conceptual visualizations for scientific concepts

Do NOT use this skill when:
- Creating flowcharts or process diagrams → use `scientific-schematics`
- Creating circuit diagrams or electrical schematics → use `scientific-schematics`
- Creating biological pathways or signaling cascades → use `scientific-schematics`
- Creating system architecture diagrams → use `scientific-schematics`
- Creating data visualizations (charts, plots) → use `plotting-libraries`
</when_to_use>

<decision_framework>
## Image Type Selection

```
What kind of image is needed?
│
├─ Technical diagram?
│  │
│  ├─ Flowchart, process diagram → scientific-schematics
│  ├─ Circuit, electrical schematic → scientific-schematics
│  ├─ Biological pathway → scientific-schematics
│  └─ Architecture diagram → scientific-schematics
│
├─ Data visualization?
│  │
│  └─ Charts, plots, graphs → plotting-libraries
│
└─ Photo, illustration, or artwork?
   │
   ├─ Photorealistic image → generate-image (this skill)
   ├─ Scientific illustration → generate-image (this skill)
   ├─ Concept art → generate-image (this skill)
   └─ Image editing → generate-image (this skill)
```

## Model Selection

> **Full Reference:** See `{baseDir}/references/model_capabilities.md` for detailed model comparison, capabilities, and pricing.

| Use Case | Recommended Model |
|----------|------------------|
| High-quality generation | `google/gemini-3-pro-image-preview` |
| Fast generation | `black-forest-labs/flux.2-pro` |
| Image editing | `google/gemini-3-pro-image-preview` |
| Budget generation | `black-forest-labs/flux.2-flex` |

</decision_framework>

<workflow>
## Image Generation Workflow

### Stage 1: Requirement Analysis

**Objective:** Define image requirements and select approach

**Steps:**
1. Clarify the image purpose (document, presentation, poster)
2. Determine image type using decision tree
3. Select appropriate model based on requirements
4. Define output specifications (size, format, style)

**Exit Criteria:**
- [ ] Image purpose defined
- [ ] Confirmed this skill is appropriate (not scientific-schematics)
- [ ] Model selected from matrix
- [ ] Output format specified (PNG, size)

---

### Stage 2: Prompt Engineering

**Objective:** Craft effective prompt for optimal generation

**Prompt Formula:** `[SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]`

> **Full Reference:** See `{baseDir}/references/prompt_templates.md` for component guide and scientific prompt patterns.

**Steps:**
1. Start with subject description
2. Add style and medium specifications
3. Include technical requirements
4. Add quality modifiers

**Exit Criteria:**
- [ ] Prompt includes all 5 components
- [ ] Prompt is specific (no vague terms)
- [ ] Style appropriate for intended use
- [ ] Technical requirements specified

---

### Stage 3: Generation Execution

**Objective:** Generate image using script

**Prerequisites:**
```bash
# Install required dependency (one-time)
pip install requests
```

**Steps:**
1. Verify API key configuration
2. Execute generation command
3. Monitor for errors
4. Save output

**Commands:**

**Basic Generation:**
```bash
python {baseDir}/scripts/generate_image.py "Your detailed prompt here"
```

**With Model Selection:**
```bash
python {baseDir}/scripts/generate_image.py "Your prompt" --model "google/gemini-3-pro-image-preview"
```

**Custom Output Path:**
```bash
python {baseDir}/scripts/generate_image.py "Your prompt" --output figures/my_image.png
```

**Image Editing:**
```bash
python {baseDir}/scripts/generate_image.py "Make the background blue" --input photo.jpg
```

**API Key Configuration:**
```bash
# Check .env file exists
cat .env | grep OPENROUTER_API_KEY

# Or set environment variable
export OPENROUTER_API_KEY=your-api-key-here
```

**Exit Criteria:**
- [ ] Command executed without errors
- [ ] Output file created
- [ ] File size reasonable (not corrupted)
- [ ] Image opens correctly

---

### Stage 4: Quality Validation

**Objective:** Verify image meets requirements using quantified scoring

**Steps:**
1. Open and inspect generated image
2. Score against quality rubric (0-10 scale)
3. Apply iteration decision logic
4. Decide: accept (≥7/10), regenerate, or edit

**Quality Scoring Rubric (10-point scale):**

| Criterion | 0 (Fail) | 1 (Acceptable) | 2 (Excellent) |
|-----------|----------|----------------|---------------|
| Subject accuracy | Wrong subject | Minor deviations | Matches prompt exactly |
| Style match | Wrong style | Mostly appropriate | Perfect for use case |
| Resolution | <512px | 512-1024px | ≥1024px |
| Artifacts | Visible distortions | Minor imperfections | Clean, professional |
| Composition | Poor balance/framing | Acceptable layout | Strong visual hierarchy |

**Score Interpretation:**
- **0-4:** Reject—regenerate with refined prompt
- **5-6:** Marginal—regenerate if iteration budget allows
- **7-8:** Accept—suitable for most uses
- **9-10:** Excellent—publication quality

**Iteration Stopping Rules:**

| Condition | Action |
|-----------|--------|
| Score ≥ 8/10 | STOP (excellent) |
| Score ≥ 7/10 AND iterations ≥ 3 | STOP (acceptable) |
| Score improvement < 0.5 for 2 iterations | STOP (plateau) |
| Iterations = 5 | STOP (hard limit) |
| Otherwise | Continue refining |

**Quality Checklist (Pass/Fail):**

| Criterion | Pass | Fail Action |
|-----------|------|-------------|
| Subject correct | Matches prompt | Refine prompt |
| Style appropriate | Fits intended use | Add style modifiers |
| Resolution sufficient | ≥1024px dimension | Specify size |
| No artifacts | Clean, professional | Regenerate |
| Color appropriate | Matches context | Specify colors |
| Composition balanced | Visually appealing | Add composition terms |

**Common Issues and Fixes:**

| Issue | Prompt Fix |
|-------|------------|
| Wrong style | Add explicit style: "in the style of scientific illustration" |
| Low detail | Add: "highly detailed", "intricate" |
| Wrong colors | Add: "blue tones", "monochromatic", specific colors |
| Busy composition | Add: "simple composition", "clean background", "minimalist" |
| Generic look | Add specific details about the subject |

**Exit Criteria:**
- [ ] Image passes quality checklist
- [ ] Appropriate for intended use
- [ ] Resolution sufficient for output format
- [ ] No visible artifacts or errors

---

### Stage 5: Integration

**Objective:** Incorporate image into project

**Steps:**
1. Move to appropriate directory
2. Rename following project conventions
3. Add to document/presentation
4. Update references if needed

**File Organization:**
```
project/
├── figures/
│   ├── fig1_concept_illustration.png
│   ├── fig2_lab_setting.png
│   └── fig3_molecular_view.png
└── slides/
    └── background_hero.png
```

**Exit Criteria:**
- [ ] File in correct project location
- [ ] Named following conventions
- [ ] Referenced in document/presentation
- [ ] Backup preserved

</workflow>

<success_criteria>
## Success Criteria

> **Reference:** See `../QUANTIFICATION_THRESHOLDS.md` §7 (Figure Quality Rubric) and §8 (Iteration Limits) for shared thresholds.

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Resolution | 512px | 1024px | 2048px |
| Generation time | <60s | <30s | <10s |
| Quality score | ≥5/10 | ≥7/10 | ≥9/10 |
| Prompt length | 10 words | 20-50 words | Optimal coverage |

**Iteration Limits by Output Type:**

| Output Type | Soft Limit | Hard Limit | Rationale |
|-------------|------------|------------|-----------|
| Quick draft | 2 | 3 | Speed over perfection |
| Presentation | 3 | 4 | Balance quality/time |
| Publication | 4 | 5 | Quality critical |
| Hero image | 4 | 5 | Visual impact matters |

**Stopping Criteria (stop when ANY is true):**
1. Quality score ≥ 8/10 (excellent threshold)
2. Quality score ≥ 7/10 AND iteration count ≥ soft limit
3. Score improvement < 0.5 for 2 consecutive iterations (plateau)
4. Iteration count = hard limit (budget exhausted)
5. API error or rate limit encountered

**Completion Checklist:**
- [ ] Image matches intended subject
- [ ] Style appropriate for use case
- [ ] Resolution sufficient for output
- [ ] No artifacts or distortions
- [ ] Colors and composition professional
- [ ] File saved in correct format and location
- [ ] Quality score documented (for iteration tracking)

</success_criteria>

<scope>
## Scope

**In Scope:**
- Photorealistic image generation
- Artistic illustrations and concept art
- Scientific conceptual visualizations
- Image editing and modification
- Visual assets for documents and presentations
- Background images and hero shots

**Out of Scope** (use specialized resources):
- Flowcharts, process diagrams → use `scientific-schematics`
- Circuit/electrical diagrams → use `scientific-schematics`
- Biological pathways → use `scientific-schematics`
- Data charts and plots → use `plotting-libraries`
- CONSORT/methodology diagrams → use `scientific-schematics`
- Technical architecture diagrams → use `scientific-schematics`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Vague Prompts

**Anti-pattern:**
```bash
python {baseDir}/scripts/generate_image.py "a cell"
# Result: Generic, unusable image
```

**Solution:**
```bash
python {baseDir}/scripts/generate_image.py "Microscopic view of a human cancer cell being attacked by immunotherapy T-cells, scientific illustration style, high detail, colorful, professional medical visualization"
```

---

### 2. Missing API Key

**Anti-pattern:**
```bash
python {baseDir}/scripts/generate_image.py "prompt"
# Error: API key not found
```

**Solution:**
```bash
# Check for API key first
if [ -z "$OPENROUTER_API_KEY" ] && ! grep -q OPENROUTER_API_KEY .env 2>/dev/null; then
    echo "API key required. Add to .env: OPENROUTER_API_KEY=your-key"
    exit 1
fi

python {baseDir}/scripts/generate_image.py "prompt"
```

---

### 3. Wrong Skill Selection

**Anti-pattern:**
Using generate-image for flowcharts or diagrams (produces artistic interpretation, not accurate diagram)

**Solution:**
Use decision tree:
- Technical diagrams → `scientific-schematics`
- Data plots → `plotting-libraries`
- Photos/illustrations → `generate-image`

---

### 4. No Quality Validation

**Anti-pattern:**
```bash
python {baseDir}/scripts/generate_image.py "prompt" --output final_figure.png
# Used directly without checking
```

**Solution:**
```bash
# Generate to temp location
python {baseDir}/scripts/generate_image.py "prompt" --output temp_image.png

# Open and validate
open temp_image.png  # macOS
# Check: subject, style, resolution, artifacts

# If acceptable, move to final location
mv temp_image.png figures/fig1_final.png
```

---

### 5. Excessive Iterations

**Anti-pattern:**
Regenerating 10+ times with minor prompt tweaks, wasting API calls and time.

**Solution:**
Apply quantified stopping criteria:
1. Score each generation using 10-point rubric
2. Stop if score ≥ 8/10 (excellent) or ≥ 7/10 with soft limit reached
3. Stop if score improvement < 0.5 for 2 consecutive iterations (plateau detected)
4. Hard limit: 5 iterations maximum for publication, 3 for drafts
5. If hard limit reached with score < 5/10, reconsider approach entirely

**Iteration Budget by Context:**
- Quick draft/exploration: 3 max
- Presentation/poster: 4 max
- Publication/hero image: 5 max

---

### 6. Transient API Failures

**Anti-pattern:**
Giving up after a single API timeout or temporary error.

**Solution:**
Retry with exponential backoff for transient failures:

```bash
# Retry logic (conceptual)
for attempt in 1 2 3; do
    python {baseDir}/scripts/generate_image.py "prompt" --output image.png && break
    echo "Attempt $attempt failed, waiting..."
    sleep $((2 ** attempt))  # 2s, 4s, 8s
done
```

**Transient vs. Permanent Errors:**
| Error Type | Action |
|------------|--------|
| Timeout / 503 | Retry (transient) |
| Rate limit (429) | Wait and retry |
| Invalid API key (401) | Fix key (permanent) |
| Invalid model (404) | Fix model name (permanent) |
| Bad request (400) | Fix prompt (permanent) |

</anti_patterns>

<templates>
## Prompt Templates

> **Full Reference:** See `{baseDir}/references/prompt_templates.md` for complete templates with examples.

**Quick Reference - Template Patterns:**

| Template | Pattern |
|----------|---------|
| Scientific Illustration | `[SUBJECT], scientific illustration style, clean white background, high detail` |
| Conceptual Visualization | `Conceptual illustration of [CONCEPT], modern scientific visualization, [COLOR] palette` |
| Laboratory/Equipment | `Modern [EQUIPMENT] in research laboratory, photorealistic, professional lighting` |
| Image Editing | `[EDIT INSTRUCTION]. Keep [ELEMENTS]. Make natural and professional.` |

**Prompt Formula:** `[SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]`

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `scientific-schematics` | Use for technical diagrams (flowcharts, pathways, circuits) |
| `plotting-libraries` | Use for data visualizations (charts, plots, graphs) |
| `scientific-slides` | Combine for visually rich presentations |
| `latex-posters` | Combine for poster visuals and hero images |
| `visual-design` | Consult for design principles and accessibility |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/scripts/generate_image.py` | Main generation script |
| `{baseDir}/references/prompt_templates.md` | Complete prompt templates with examples |
| `{baseDir}/references/model_capabilities.md` | Model comparison and selection guide |
| `../QUANTIFICATION_THRESHOLDS.md` | Shared quality thresholds (§7-8) |

## External Resources

- **OpenRouter**: https://openrouter.ai
- **API Keys**: https://openrouter.ai/keys
- **Model List**: https://openrouter.ai/models

</references>