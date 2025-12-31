# Image Generation Prompt Templates

> Reference document for crafting effective image generation prompts.
> See main SKILL.md for workflow and decision framework.

## Prompt Structure Formula

```
[SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]
```

### Component Guide

| Component | Examples |
|-----------|----------|
| Subject | "DNA double helix", "laboratory setting", "cancer cells" |
| Style | "scientific illustration", "photorealistic", "modern", "minimalist" |
| Medium | "digital art", "3D render", "photograph", "watercolor" |
| Technical | "high contrast", "neutral background", "well-lit" |
| Quality | "detailed", "professional", "publication-quality", "4K" |

### Scientific Image Prompt Patterns

| Image Type | Prompt Pattern |
|------------|----------------|
| Conceptual | "Conceptual illustration of [topic], scientific visualization style, clean background" |
| Microscopy | "Microscopic view of [subject], scientific imaging style, detailed, high contrast" |
| Lab setting | "Modern laboratory with [equipment], photorealistic, professional lighting" |
| Molecular | "[Molecule/structure] visualization, 3D render, scientific accuracy, clean background" |

---

## Template 1: Scientific Illustration

**Pattern:**
```
[SUBJECT DESCRIPTION], scientific illustration style,
clean white background, high detail,
professional medical/scientific visualization,
suitable for academic publication
```

**Example:**
```bash
python {baseDir}/scripts/generate_image.py "DNA double helix structure with highlighted mutation site, scientific illustration style, clean white background, high detail, professional molecular visualization, suitable for academic publication" --output figures/dna_mutation.png
```

---

## Template 2: Conceptual Visualization

**Pattern:**
```
Conceptual illustration representing [CONCEPT],
modern scientific visualization,
abstract yet professional,
[COLOR SCHEME] color palette,
clean composition
```

**Example:**
```bash
python {baseDir}/scripts/generate_image.py "Conceptual illustration representing machine learning in drug discovery, modern scientific visualization, abstract yet professional, blue and teal color palette, clean composition" --output figures/ml_drug_discovery.png
```

---

## Template 3: Laboratory/Equipment

**Pattern:**
```
Modern [EQUIPMENT/SETTING] in a contemporary research laboratory,
photorealistic, professional photography style,
well-lit, clean environment,
suitable for presentation or publication
```

**Example:**
```bash
python {baseDir}/scripts/generate_image.py "Modern CRISPR gene editing equipment in a contemporary research laboratory, photorealistic, professional photography style, well-lit, clean environment, suitable for presentation" --output slides/lab_hero.png
```

---

## Template 4: Image Editing

**Pattern:**
```
[EDIT INSTRUCTION]. Keep the [ELEMENTS TO PRESERVE].
Make the change look natural and professional.
```

**Example:**
```bash
python {baseDir}/scripts/generate_image.py "Change the background to a clean white color. Keep the main subject and its details. Make the change look natural and professional." --input original.png --output edited.png
```

---

## Common Prompt Modifiers

### Style Modifiers
- `scientific illustration style` - Clean, accurate, educational
- `photorealistic` - Lifelike, detailed
- `modern minimalist` - Simple, clean lines
- `3D render` - Dimensional, polished

### Quality Modifiers
- `high detail` / `highly detailed` / `intricate`
- `professional` / `publication-quality`
- `4K` / `high resolution`
- `sharp focus`

### Composition Modifiers
- `clean background` / `white background` / `neutral background`
- `centered composition` / `rule of thirds`
- `simple composition` / `minimalist`
- `well-lit` / `professional lighting`

### Color Modifiers
- `[color] tones` - e.g., "blue tones", "warm tones"
- `monochromatic`
- `vibrant colors` / `muted colors`
- `[color] and [color] color palette`
