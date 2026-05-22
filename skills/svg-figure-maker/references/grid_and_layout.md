# Grid and Layout

> 8px-grid discipline for figure work; 4px for dense diagrams. Underlying principle: `shared/references/figure_design_principles.md` §6.1.

---

## The grid unit

**Default: 8px** for figures, panel compositions, posters.
**Alternative: 4px** for dense hand-authored diagrams (svg-figure-maker output that approaches scientific-schematics territory).

All of the following must be divisible by the chosen grid unit:

- viewBox `width` and `height`
- All coordinates (`x`, `y`, `x1`, `y1`, `x2`, `y2`, `cx`, `cy`)
- All rectangular dimensions (`width`, `height` on `<rect>`, `<image>`, `<foreignObject>`)
- All padding, margins, gaps between elements
- All translation distances in `transform="translate(…)"`

**Quick check:** if a coord ends in 1, 2, 3, 5, 6, 7, or 9 on the 8px grid (or ends in 1, 3, 5, 7 on the 4px grid), it's off-grid. Snap to the nearest grid multiple.

The preflight checker reports off-grid coordinates as `warn` by default (because some legitimate values, like circle radii or small offsets, may intentionally break the grid). To enforce strictly, run `preflight_check.py --strict-grid`.

---

## Why grid

- **Visual alignment is automatic** — elements snap to the same axes without per-figure debugging
- **Hierarchy reads cleanly** — consistent spacing communicates that elements are intentionally grouped (Gestalt proximity, Wagemans 2012)
- **Composition stays balanced** — whitespace is intentional, not accidental
- **Vision-loop iterations converge faster** — most "alignment" findings disappear when the grid is honored

---

## The padding table (8px grid)

Reproduced from `shared/references/figure_design_principles.md` §6.4 for quick reference:

| Region | Padding |
|---|---|
| Plot area → axis labels | 8px |
| Axis labels → panel edge | 16px |
| Panel edge → adjacent panel edge | 16–24px |
| Inside a legend / annotation box | 8px |
| Title → top of plot area | 16px |
| Caption → bottom of figure | 24px |

**Default canvas margins:** 32px on all sides for embedded figures; 16px for tight composition.

---

## Multi-panel layout

When composing 2+ panels:

- **Panel labels** (A, B, C, …) in upper-left of each panel, **14pt bold**, sans-serif, black, offset 8px from the panel's top-left corner, outside the plot area
- **Shared axes** whenever the data permits — reduces cognitive load (Cowan 2010), saves space
- **Alignment:** panel boundaries snap to the grid; horizontally adjacent panels share their y-axis extent; vertically adjacent panels share their x-axis extent
- **Inter-panel gaps:** 16px minimum (two grid units); 24px when axes are not shared
- **Don't mix orientations** within one figure — all horizontal, all square, etc., unless content forces otherwise

---

## Legend placement decision

Direct labeling is preferred (see `shared/references/figure_design_principles.md` §5.2). When a legend is needed:

```
Where to place the legend?
│
├─ Is there unused space in the top-right of the plot area?
│   └─ Yes → place legend INSIDE the plot area, top-right, with 8px padding
│
├─ Is there unused space in the top-left of the plot area?
│   └─ Yes → place legend INSIDE the plot area, top-left, with 8px padding
│
├─ Is the figure wider than tall?
│   └─ Yes → bottom strip OUTSIDE the plot area, horizontal layout
│
└─ Otherwise → side strip OUTSIDE the plot area, vertical layout
```

**Never:**
- Place a legend over data
- Use a drop-shadow / glow / fancy bounding box on the legend
- Put more than one legend per panel
- Order legend entries alphabetically (order by data prominence — most-emphasized first)

---

## Worked example: two-panel horizontal figure

For a 1280×480 viewBox with two equal panels:

```
canvas margin: 32px on all sides
inner area: 1216 × 416
panel width: (1216 - 24) / 2 = 596    ← off-grid! 
```

Fix: choose an inter-panel gap that keeps each panel grid-aligned.

```
canvas margin: 32px on all sides
inner area: 1216 × 416
inter-panel gap: 32 (4 grid units)
panel width: (1216 - 32) / 2 = 592    ← 8px-aligned ✓
panel height: 416                       ← 8px-aligned ✓
panel A origin: (32, 32)
panel B origin: (32 + 592 + 32, 32) = (656, 32)
```

This is the kind of arithmetic the templates do for you. Use them.

---

## When you genuinely need to break the grid

Some values legitimately fall off-grid:

- Circle radii (`r`) — geometry, not layout
- Small visual offsets for hand-authored polish (e.g., 1-unit nudge to align optical centers)
- Decorative curves and bezier control points

For these, accept the `warn` finding. Don't run `--strict-grid` for hand-authored figures. Do enforce strict for programmatic figures where every coord should be deliberate.
