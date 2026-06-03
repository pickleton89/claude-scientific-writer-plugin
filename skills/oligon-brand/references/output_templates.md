# Output Templates for Visual Design

> Reusable templates for design specifications and quality verification.
> Aligned with Oligon Digital Style Guide v2.3 / brand skill v5.0.

## Visual Specifications Document

Use this template to document design decisions before implementation.

### Template

```markdown
# Figure {{N}} Visual Specifications

## Context
- **Purpose:** {{What insight does this communicate?}}
- **Audience:** {{Who will view this?}}
- **Venue:** {{Journal/conference/presentation}}

## Technical Requirements
- **Dimensions:** {{W}} × {{H}} mm
- **Resolution:** {{DPI}} DPI
- **File format:** {{PDF/PNG/TIFF}}
- **Color mode:** {{RGB/CMYK}}

## Color Palette
| Role | Color | Hex Code |
|------|-------|----------|
| Primary | {{name}} | #{{hex}} |
| Secondary | {{name}} | #{{hex}} |
| Accent | {{name}} | #{{hex}} |
| Background | {{name}} | #{{hex}} |
| Text | {{name}} | #{{hex}} |

## Typography
- **Font family:** {{name}}
- **Title:** {{size}}pt bold
- **Axis labels:** {{size}}pt regular
- **Legend:** {{size}}pt regular

## Accessibility
- [ ] Colorblind-safe palette verified
- [ ] Contrast ≥4.5:1 for all text
- [ ] Redundant encoding used
- [ ] Readable at final size

## Notes
{{Additional specifications or constraints}}
```

### Filled Example

```markdown
# Figure 2 Visual Specifications

## Context
- **Purpose:** Show treatment effect on tumor volume over time
- **Audience:** Journal reviewers (Nature Cancer)
- **Venue:** Nature Cancer (single column)

## Technical Requirements
- **Dimensions:** 89 × 70 mm
- **Resolution:** 300 DPI
- **File format:** PDF (vector)
- **Color mode:** RGB

## Color Palette (Cycle 1 · Treatment/Control)
| Role       | Token       | Hex Code  |
|------------|-------------|-----------|
| Treatment line     | brand.blue  | #2DB2E8   |
| Treatment CI band  | brand.blue @ α=0.18 | matching-hue tint |
| Control line       | blue.300    | #76CAF3   |
| Control CI band    | blue.300 @ α=0.18   | matching-hue tint |
| Background         | white       | #FFFFFF   |
| Text       | neutral.900 | #121719   |
| Axis furniture | neutral.200 | #D6DCDF |

## Typography (v2.3 Figure Type Scale)
- **Font family:** Arial / Helvetica / DejaVu Sans
- **Title:** 12 pt bold
- **Axis labels:** 10 pt medium
- **Tick labels:** 9 pt regular
- **Legend:** 8.5 pt regular

## Accessibility
- [x] Cycle follows v2.3 Rule 1 (treatment_control for 2-arm narrative)
- [x] Ramp-matched lightness preserves dark/light differential under CVD
- [x] Contrast ≥ 4.5:1 for all text (neutral.900 on white = 18.07:1 AAA)
- [x] Redundant encoding used (solid vs dashed lines, circle vs square markers)
- [x] Readable at final size (9 pt minimum at 89 mm column width)

## Notes
- Treatment group: brand.blue solid line with filled circles (5–6 pt)
- Control group: blue.300 solid line with filled squares (5–6 pt)
- Error bands: 95% CI, ~18% opacity (v2.3 default) of same hue, no border
- Include at-risk table below x-axis in neutral.900 text
```

---

## Pre-Submission Design Checklist

Use before submitting any figure to verify quality standards.

```markdown
## Figure Quality Checklist

### Clarity
- [ ] Single clear message communicated
- [ ] Can be understood in <10 seconds
- [ ] Labels are complete and unambiguous

### Technical Quality
- [ ] Resolution ≥300 DPI
- [ ] Correct file format for venue
- [ ] Dimensions match journal requirements
- [ ] Fonts embedded (for vector formats)

### Accessibility
- [ ] Cycle drawn from v2.3 Blue / Orange / Neutral ramps
- [ ] No retired v4 hexes (`#E8622D`, `#7D250F`, `#0F5D7D`, `#158BBB`, `#222222`)
- [ ] Contrast ratio ≥ 4.5:1 for text (≥ 3:1 for data elements)
- [ ] No category encoded by hue alone — shape/line-style/label redundancy
- [ ] Minimum 9 pt font at final size (document scale) or 18 pt (projection)

### Consistency
- [ ] Matches style of other figures
- [ ] Consistent color usage
- [ ] Same typography throughout
- [ ] Aligned with brand guidelines

### Publication Ready
- [ ] Caption written and complete
- [ ] Abbreviations defined
- [ ] Referenced in main text
- [ ] Meets journal-specific requirements
```

---

## Quick Specification Card

For rapid design documentation when full template is excessive:

```markdown
## Figure {{N}} Quick Spec

**Target:** {{Journal/Conference}} | **Size:** {{W}}×{{H}}mm | **DPI:** {{300}}

**Cycle:** Treatment=brand.blue `#2DB2E8`, Control=blue.300 `#76CAF3`. **CI bands:** matching-hue tint of each arm's line at α ≈ 0.18, no border.

**Font:** Arial / DejaVu Sans; title 12 pt, axis 10 pt, tick 9 pt | **Accessibility:** v2.3 ramps (Okabe-Ito-class), shapes + color

**Key message:** {{One sentence describing the insight}}
```

---

*See [SKILL.md](../SKILL.md) for the workflow, [brand-colors-full.md](brand-colors-full.md) for ramps and cycles, and [medium_playbooks.md](medium_playbooks.md) for social / deck / email / landing page layouts. Per-journal figure dimensions are not included in this skill — consult the target journal's author guidelines.*

## Plugin integration

Per-journal figure dimensions are not bundled in this skill. Within the
scientific-writer plugin, consult `../../venue-templates/references/figure_specs.md`
for per-journal sizing; otherwise follow the target journal's author guidelines.
