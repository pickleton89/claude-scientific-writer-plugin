# Brand Quick Reference

> Essential color codes for visual outputs (HTML, PDF, SVG)
> For complete brand specification, see `skills/oligon-brand/SKILL.md`

## Primary Palette

| Role | Color | HEX | Usage |
|------|-------|-----|-------|
| **Primary Highlight** | Brand Blue | `#2DB2E8` | Key findings, links, treatment groups |
| **Contrast/Alert** | Orange | `#E8622D` | Warnings, adverse effects, critical notes |
| **Primary Data** | Dark Gray | `#222222` | Main text, primary chart elements |
| **Secondary Data** | Medium Gray | `#666666` | Secondary text, supporting data |
| **Tertiary Data** | Muted Gray | `#999999` | Annotations, axis labels |
| **Background** | White | `#FFFFFF` | Page background, chart fill |

## Color Assignment Rules

### Charts and Data Visualization

```
Treatment/Intervention → Brand Blue (#2DB2E8)
Control/Baseline → Dark Gray (#222222)
Adverse/Opposing effect → Orange (#E8622D)
Secondary comparison → Medium Gray (#666666)
```

### Statistical Significance Badges

```html
<!-- Significant -->
<span class="badge" style="background: #2DB2E8; color: white;">p < 0.001</span>

<!-- Borderline -->
<span class="badge" style="background: #666666; color: white;">p = 0.05</span>

<!-- Not significant -->
<span class="badge" style="background: #999999; color: white;">p = 0.34</span>
```

### Section Styling

```css
/* Headers */
h1, h2 { color: #222222; }

/* Emphasis */
.highlight { color: #2DB2E8; }
.warning { color: #E8622D; }

/* Borders and dividers */
.border { border-color: #666666; }
.divider { background-color: #999999; }
```

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 Title | Inter/system | 24px | 600 |
| H2 Section | Inter/system | 18px | 600 |
| Body | Inter/system | 14px | 400 |
| Caption | Inter/system | 12px | 400 |
| Code | JetBrains Mono | 13px | 400 |

## Design Principles

1. **White backgrounds only** - No colored backgrounds
2. **Flat design** - No gradients, shadows, or 3D effects
3. **Minimal decoration** - No unnecessary borders or fills
4. **High contrast** - Dark text on light backgrounds
5. **Accessible** - All color combinations meet WCAG AA

## SVG Component Defaults

For SVG infographics, use these defaults:

```javascript
const brandColors = {
  primary: '#2DB2E8',
  secondary: '#E8622D',
  text: '#222222',
  textSecondary: '#666666',
  textMuted: '#999999',
  background: '#FFFFFF'
};
```

## Quick CSS Snippet

```css
:root {
  --brand-blue: #2DB2E8;
  --brand-orange: #E8622D;
  --text-primary: #222222;
  --text-secondary: #666666;
  --text-muted: #999999;
  --background: #FFFFFF;
}
```

## Full Brand Reference

For complete specifications including:
- Extended color cycles for multi-series charts
- Logo usage and placement
- Accessibility guidelines
- Brand tokens and CSS variables

See: `skills/oligon-brand/SKILL.md`
