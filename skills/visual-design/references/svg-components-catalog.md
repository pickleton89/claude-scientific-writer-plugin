# SVG Component Library

> Reference components for creating scientific infographics
> Converted from JSX component files for documentation purposes

## Overview

This library provides reusable SVG components for creating brand-compliant scientific infographics. All components use the Oligon brand color palette.

## Available Components

### Data Visualization

#### DonutChart
Circular chart for showing proportions.

```svg
<!-- Example: 75% completion -->
<svg viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="none" stroke="#999999" stroke-width="10"/>
  <circle cx="50" cy="50" r="40" fill="none" stroke="#2DB2E8" stroke-width="10"
          stroke-dasharray="188.5 251.3" transform="rotate(-90 50 50)"/>
  <text x="50" y="55" text-anchor="middle" fill="#222222" font-size="20">75%</text>
</svg>
```

**Props:**
- `value`: Percentage (0-100)
- `label`: Center text
- `color`: Primary color (default: Brand Blue)

#### HorizontalBarChart
For comparing values across categories.

```svg
<svg viewBox="0 0 300 100">
  <!-- Bar 1: Treatment (75%) -->
  <rect x="80" y="10" width="165" height="20" fill="#2DB2E8"/>
  <text x="5" y="25" fill="#222222" font-size="12">Treatment</text>
  <text x="250" y="25" fill="#222222" font-size="12">75%</text>

  <!-- Bar 2: Control (45%) -->
  <rect x="80" y="40" width="99" height="20" fill="#666666"/>
  <text x="5" y="55" fill="#222222" font-size="12">Control</text>
  <text x="184" y="55" fill="#222222" font-size="12">45%</text>
</svg>
```

#### StatCallout
Highlight a key statistic.

```svg
<svg viewBox="0 0 150 80">
  <rect x="0" y="0" width="150" height="80" fill="#FFFFFF" stroke="#2DB2E8" stroke-width="2"/>
  <text x="75" y="35" text-anchor="middle" fill="#2DB2E8" font-size="28" font-weight="bold">78%</text>
  <text x="75" y="55" text-anchor="middle" fill="#666666" font-size="12">Reduction</text>
  <text x="75" y="70" text-anchor="middle" fill="#999999" font-size="10">p < 0.001</text>
</svg>
```

### Timeline & Process

#### TimelineNode
Single node in a horizontal timeline.

```svg
<svg viewBox="0 0 100 60">
  <circle cx="50" cy="20" r="15" fill="#2DB2E8"/>
  <text x="50" y="25" text-anchor="middle" fill="#FFFFFF" font-size="12">1</text>
  <text x="50" y="50" text-anchor="middle" fill="#222222" font-size="10">Step Name</text>
</svg>
```

#### ProcessArrow
Connecting arrow between timeline nodes.

```svg
<svg viewBox="0 0 50 20">
  <line x1="5" y1="10" x2="40" y2="10" stroke="#666666" stroke-width="2"/>
  <polygon points="40,5 50,10 40,15" fill="#666666"/>
</svg>
```

### Hierarchical

#### HierarchicalTree
For showing relationships and taxonomies.

```svg
<svg viewBox="0 0 200 150">
  <!-- Root node -->
  <rect x="75" y="5" width="50" height="25" fill="#2DB2E8" rx="3"/>
  <text x="100" y="22" text-anchor="middle" fill="#FFFFFF" font-size="10">Root</text>

  <!-- Connectors -->
  <line x1="100" y1="30" x2="100" y2="45" stroke="#666666" stroke-width="1"/>
  <line x1="50" y1="45" x2="150" y2="45" stroke="#666666" stroke-width="1"/>

  <!-- Child nodes -->
  <rect x="25" y="55" width="50" height="25" fill="#666666" rx="3"/>
  <rect x="125" y="55" width="50" height="25" fill="#666666" rx="3"/>
</svg>
```

### Scientific Diagrams

#### MoleculeIcon
Generic molecule representation.

```svg
<svg viewBox="0 0 40 40">
  <circle cx="20" cy="10" r="6" fill="#2DB2E8"/>
  <circle cx="10" cy="30" r="6" fill="#666666"/>
  <circle cx="30" cy="30" r="6" fill="#666666"/>
  <line x1="20" y1="16" x2="12" y2="24" stroke="#222222" stroke-width="2"/>
  <line x1="20" y1="16" x2="28" y2="24" stroke="#222222" stroke-width="2"/>
</svg>
```

#### CellIcon
Simplified cell representation.

```svg
<svg viewBox="0 0 50 50">
  <ellipse cx="25" cy="25" rx="22" ry="18" fill="none" stroke="#666666" stroke-width="2"/>
  <circle cx="25" cy="25" r="8" fill="#2DB2E8"/>
</svg>
```

#### DNAHelix
Stylized DNA representation.

```svg
<svg viewBox="0 0 30 60">
  <path d="M5,5 Q15,15 25,5 Q35,15 25,25 Q15,35 5,25 Q-5,35 5,45 Q15,55 25,45"
        fill="none" stroke="#2DB2E8" stroke-width="2"/>
  <path d="M25,5 Q15,15 5,5 Q-5,15 5,25 Q15,35 25,25 Q35,35 25,45 Q15,55 5,45"
        fill="none" stroke="#E8622D" stroke-width="2"/>
</svg>
```

## Layout Guidelines

### Infographic Structure

```
┌─────────────────────────────────────────────┐
│  TITLE (Brand Blue underline)               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Stat 1  │  │ Stat 2  │  │ Stat 3  │    │
│  │ Callout │  │ Callout │  │ Callout │    │
│  └─────────┘  └─────────┘  └─────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │         Main Visualization          │   │
│  │      (Chart, Timeline, Tree)        │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Key Findings:                              │
│  • Finding 1 with stat                      │
│  • Finding 2 with stat                      │
│                                             │
└─────────────────────────────────────────────┘
```

### Recommended Dimensions

| Output | Width | Height |
|--------|-------|--------|
| Poster (portrait) | 800px | 1200px |
| Slide (landscape) | 1200px | 675px |
| Square (social) | 800px | 800px |

### Spacing

- **Margins:** 40px on all sides
- **Section gaps:** 30px
- **Component gaps:** 20px
- **Text padding:** 10px

## Usage Notes

1. **Always use viewBox** - Enables scaling without distortion
2. **White backgrounds only** - Match brand guidelines
3. **Text as text** - Don't convert to paths for accessibility
4. **Semantic grouping** - Use `<g>` elements with descriptive IDs
5. **No gradients** - Flat colors only per brand guidelines
