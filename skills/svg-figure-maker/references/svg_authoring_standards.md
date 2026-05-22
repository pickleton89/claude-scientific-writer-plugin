# SVG Authoring Standards

> Structural conventions for hand-authored SVG figures in this skill. Enforced mechanically by `scripts/preflight_check.py`. See `shared/references/figure_design_principles.md` for the underlying design rationale.

---

## viewBox

Every SVG must declare a `viewBox` and omit explicit `width` / `height` attributes on the root `<svg>` element. This makes the figure scalable without distortion.

```xml
<!-- Good -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">

<!-- Bad: width/height pin the figure to a specific pixel size -->
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
```

**viewBox coordinates:** `x y width height`. Origin at top-left. Use 8px-grid-aligned values for `width` and `height`.

**Common viewBox sizes** (all 8px-grid-aligned):

| Use case | viewBox |
|---|---|
| Single panel, square | `0 0 640 640` |
| Single panel, 4:3 | `0 0 800 600` |
| Two panel horizontal | `0 0 1280 480` |
| Two panel vertical | `0 0 640 960` |
| Slide aspect 16:9 | `0 0 1920 1080` |
| Poster panel | `0 0 1600 1200` |

---

## Units

Internal coordinates are unit-less and interpreted as user units (= viewBox units). Do not mix in `px`, `pt`, `mm`, or `em` for positions, widths, heights, or stroke widths.

```xml
<!-- Good -->
<rect x="40" y="40" width="320" height="240"/>
<line x1="40" y1="40" x2="360" y2="40" stroke-width="2"/>

<!-- Bad -->
<rect x="40px" y="40px" width="20mm" height="240"/>
```

Font sizes are the exception: they may carry `pt` (preferred for print) or `px` (preferred for screen). Whichever is chosen, the value must land on the type ladder (10/12/14/16). The preflight checker grep-matches both.

---

## Group structure

Use `<g>` groups to organize logical sub-elements. Group `id` attributes are useful for the vision-loop critique (Claude can name a specific group when reporting a finding).

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <title>Figure title (one-line, accessibility)</title>
  <desc>Two-sentence alt-text describing the takeaway message and the key supporting evidence.</desc>

  <g id="canvas-background">
    <!-- background rect, gridlines if any -->
  </g>

  <g id="panel-a">
    <g id="panel-a-content">
      <!-- data marks, illustrations -->
    </g>
    <g id="panel-a-labels">
      <!-- axis labels, annotations -->
    </g>
    <text id="panel-a-label" font-family="Arial, Helvetica, sans-serif" font-size="14pt" font-weight="bold">A</text>
  </g>

  <g id="figure-legend">
    <!-- legend if any -->
  </g>
</svg>
```

**Naming convention:** `id` values are kebab-case, descriptive, and reflect the logical role. Avoid `g1`, `g2`, `layer_3` — they don't help the vision-loop critique.

---

## Accessibility tags

Every SVG must include at minimum:

- One root `<title>` — a one-line label suitable for tooltips and screen-reader summary
- One root `<desc>` — the 2-sentence alt-text formula (takeaway message + key supporting evidence). See `shared/references/figure_design_principles.md` §4.2 and `venue-templates/references/figure_specs.md` §4.

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <title>Treatment X reduces tumor volume</title>
  <desc>Treatment X reduced tumor volume by 60% compared to control over 12 weeks; combination therapy with drug Y achieved 85% reduction.</desc>
  ...
</svg>
```

Additional `<title>` / `<desc>` may be nested inside `<g>` groups for per-panel accessibility.

**Bad:**

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <!-- no <title>, no <desc> -->
  <rect ...
```

The preflight checker flags missing root `<title>` and `<desc>` as `fail`.

---

## Font declarations

Every `<text>` and `<tspan>` element MUST carry an explicit `font-family` attribute:

```xml
<text x="40" y="40" font-family="Arial, Helvetica, sans-serif" font-size="12pt">Label</text>
```

Inheriting via a parent `<g>` `font-family` is acceptable, but the root `<svg>` `font-family` is not — many renderers (Mermaid, some browsers) ignore root-level inheritance for `<text>`.

For multi-element runs, prefer setting `font-family` on a wrapping `<g>`:

```xml
<g font-family="Arial, Helvetica, sans-serif">
  <text x="40" y="40" font-size="12pt">Label A</text>
  <text x="40" y="80" font-size="12pt">Label B</text>
</g>
```

**Font-size values** must land on the ladder: 10, 12, 14, 16 (pt or px). The preflight checker rejects intermediate values (11, 13, 15).

---

## Stroke widths

Default stroke widths align to a 0.5-unit ladder:

| Use | Stroke width |
|---|---|
| Subtle outlines, secondary marks | 0.5 |
| Standard outlines, axes | 1.0 |
| Connections, primary lines | 1.5 |
| Emphasis, focal marks | 2.0 |
| Very heavy emphasis | 3.0 |

Use `stroke-linecap="round"` for line endings and `stroke-linejoin="round"` for corners by default — softens hand-authored figures.

---

## Color attributes

All `fill`, `stroke`, `stop-color` values are hexes from the active palette. The preflight checker rejects:

- Off-palette hexes (any hex not present in `oligon-brand/tokens/brand-tokens.json`)
- CSS named colors (`lightblue`, `darkred`, `crimson`, etc.) — ambiguous
- `currentColor` — context-dependent, defeats deterministic styling
- Inline gradients without a palette-derived stop set

```xml
<!-- Good -->
<rect fill="#2DB2E8" stroke="#222222" stroke-width="1"/>

<!-- Bad -->
<rect fill="lightblue" stroke="currentColor"/>
<rect fill="#3498DB"/>  <!-- close to Brand Blue, but not in palette -->
```

---

## What NOT to include

These attributes / elements are banned (preflight `fail`):

- `<filter>` blocks of any kind (drop-shadow, glow, blur) — `<filter id="drop-shadow">…</filter>` and any `filter="url(#…)"` reference
- `feDropShadow`, `feGaussianBlur`, `feOffset` (as anti-pattern aesthetics; if you genuinely need a blur for content, it's almost certainly the wrong skill)
- Inline `style="filter: drop-shadow(...)"` or `style="filter: blur(...)"`
- `writing-mode: vertical-*` or `transform="rotate(90)"` on `<text>` elements
- `<script>` blocks (figures are static)
- `<foreignObject>` (breaks portability across renderers)

See `references/anti_patterns.md` for the full banned list with examples.

---

## Minimal complete example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480">
  <title>Minimal example figure</title>
  <desc>Demonstrates a brand-compliant SVG skeleton with viewBox, accessibility tags, and a single text element.</desc>

  <g id="canvas-background">
    <rect x="0" y="0" width="640" height="480" fill="#FFFFFF"/>
  </g>

  <g id="content" font-family="Arial, Helvetica, sans-serif">
    <text x="320" y="240" font-size="16pt" font-weight="bold" text-anchor="middle" fill="#222222">
      Hello, brand-compliant SVG
    </text>
    <text x="320" y="272" font-size="12pt" text-anchor="middle" fill="#666666">
      All coordinates on 8px grid; palette hex only; accessibility tags present.
    </text>
  </g>
</svg>
```

Run `uv run python scripts/preflight_check.py <this.svg>` — should return `overall: pass` with zero findings.
