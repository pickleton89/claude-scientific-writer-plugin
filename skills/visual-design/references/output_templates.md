# Output Templates for Visual Design

> Reusable templates for design specifications and quality verification.

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

## Color Palette
| Role | Color | Hex Code |
|------|-------|----------|
| Primary | Dark Gray | #222222 |
| Secondary | Brand Blue | #2DB2E8 |
| Accent | Contrast Orange | #E8622D |
| Background | White | #FFFFFF |
| Text | Black | #000000 |

## Typography
- **Font family:** Arial
- **Title:** 9pt bold
- **Axis labels:** 8pt regular
- **Legend:** 7pt regular

## Accessibility
- [x] Colorblind-safe palette verified (Okabe-Ito compatible)
- [x] Contrast ≥4.5:1 for all text
- [x] Redundant encoding used (solid vs dashed lines)
- [x] Readable at final size (7pt minimum)

## Notes
- Control group: dark gray solid line with circles
- Treatment group: brand blue solid line with squares
- Error bands: 95% CI, 20% opacity fill
- Include at-risk table below x-axis
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
- [ ] Colorblind-safe palette used
- [ ] Contrast ratio ≥4.5:1
- [ ] Redundant encoding present
- [ ] Minimum 7pt font at final size

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

**Colors:** Control=#222222, Treatment=#2DB2E8, Contrast=#E8622D

**Font:** Arial 8pt | **Accessibility:** Okabe-Ito, shapes + color

**Key message:** {{One sentence describing the insight}}
```

---

*See [SKILL.md](../SKILL.md) for design workflow and [publication_specs.md](publication_specs.md) for journal requirements.*
