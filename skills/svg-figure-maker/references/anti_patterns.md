# Anti-Patterns — banned attributes and "AI slop" markers

> Expanded reference with concrete examples for the universal anti-pattern table in `shared/references/figure_design_principles.md` §7. The preflight checker mechanizes most of these.

---

## Category A: Banned visual effects ("AI slop" signatures)

These attributes signal "AI-generated without taste" and don't appear in editorial-quality scientific figures. The preflight checker rejects them as `fail`.

### A.1 Drop-shadow filters

**Banned forms:**

```xml
<filter id="drop-shadow">
  <feDropShadow dx="2" dy="2" stdDeviation="3"/>
</filter>
<rect ... filter="url(#drop-shadow)"/>
```

```xml
<rect ... style="filter: drop-shadow(2px 2px 3px rgba(0,0,0,0.3));"/>
```

**Why:** decorative; adds visual noise without signal; common signature of LLM-generated web aesthetics applied to scientific contexts.

**Fix:** use a 1-unit stroke border for separation. If you genuinely need to lift an element off the background, vary its fill saturation or use whitespace.

### A.2 Glow / blur effects

**Banned forms:**

```xml
<feGaussianBlur stdDeviation="4"/>
<feOffset dx="0" dy="0"/>
<feMerge>...</feMerge>  <!-- glow assembly -->
```

```xml
<rect ... style="filter: blur(2px);"/>
```

**Why:** another "looks technical" tic from LLM training data; unreadable when rasterized at small scale.

**Fix:** remove. If you need to de-emphasize an element, reduce its `opacity` to ~0.4 instead.

### A.3 Dark mode + cyan/purple neon

**Pattern:** dark background fills (`#000000`, `#0a0a0a`, very dark grays) combined with high-saturation cyan / purple / magenta strokes ("cyberpunk dashboard").

**Why:** unreadable in print; fails WCAG contrast in many combinations; signals "AI aesthetic" rather than editorial figure.

**Fix:** white or near-white background (`#FFFFFF`, off-white if explicitly part of the brand). Use brand palette colors with full saturation only for focal accents.

### A.4 Rounded corners larger than 10 units

**Banned form:**

```xml
<rect ... rx="20" ry="20"/>
```

**Why:** reads as web UI ("rounded-2xl"), not editorial figure.

**Fix:** max `rx` / `ry` of 6 for diagram nodes, 10 for panel backgrounds. Often 0 (sharp corners) is right.

### A.5 Inline gradients without a palette-derived stop set

**Banned form:**

```xml
<linearGradient id="bg">
  <stop offset="0%" stop-color="#aabbcc"/>
  <stop offset="100%" stop-color="#ddeeff"/>
</linearGradient>
```

**Why:** introduces off-palette colors; gradient ramps often have non-monotonic perceived lightness and fail CVD simulation.

**Fix:** flat fill from the palette. If gradient is essential (e.g., colorbar for a continuous scale), derive stops from a CVD-safe sequential map (viridis, cividis) and document the stops in the metadata sidecar.

---

## Category B: Encoding mistakes

### B.1 Color as the only differentiator

**Anti-pattern:**

```xml
<circle cx="100" cy="100" r="5" fill="#2DB2E8"/>  <!-- group A -->
<circle cx="120" cy="110" r="5" fill="#E8622D"/>  <!-- group B -->
<!-- legend distinguishes only by color -->
```

**Why:** Treisman & Gelade 1980 — conjunction search is serial; CVD readers can't distinguish; fails grayscale test.

**Fix:** add shape (`<circle>` vs `<rect>` vs `<polygon>`), line style (solid vs dashed), or a direct label.

### B.2 CSS named colors

**Anti-pattern:**

```xml
<rect fill="lightblue"/>
<line stroke="crimson"/>
```

**Why:** ambiguous, not in palette tokens, fails preflight.

**Fix:** use the equivalent palette hex from `tokens/brand-tokens.json`.

### B.3 `currentColor`

**Anti-pattern:**

```xml
<rect fill="currentColor"/>
```

**Why:** context-dependent; defeats deterministic styling; preflight can't verify the resolved color is in-palette.

**Fix:** specify the hex explicitly.

### B.4 More than 2 focal accents per panel

**Anti-pattern:** every "important" element painted Brand Blue / coral / focal color. Effect: nothing reads as the focus.

**Fix:** one focal accent is best; two acceptable if they're explicitly contrasting (e.g., treatment vs. control). Everything else in neutrals.

### B.5 Library defaults

Although this skill is hand-authored / programmatic SVG (not chart-library output), the principle still applies: if you copy palette values from matplotlib's tab10, seaborn's default, or web design tutorials, you'll likely end up off-palette and not CVD-safe. Always pull colors from `tokens/brand-tokens.json`.

---

## Category C: Typography mistakes

### C.1 Missing font-family on `<text>`

**Anti-pattern:**

```xml
<text x="40" y="40" font-size="12pt">Label</text>  <!-- no font-family -->
```

**Why:** falls back to renderer default (often Times New Roman on Linux); not brand-compliant; fails grep check.

**Fix:** add `font-family="Arial, Helvetica, sans-serif"` to every `<text>` element, or set it on a wrapping `<g>`.

### C.2 Off-ladder font sizes

**Anti-pattern:**

```xml
<text font-size="11pt">…</text>
<text font-size="13pt">…</text>
```

**Why:** the ladder (10/12/14/16) is the source of truth. Off-ladder values signal hand-tuned drift.

**Fix:** snap to the nearest ladder value.

### C.3 Text below 10pt

**Anti-pattern:**

```xml
<text font-size="8pt">tiny label</text>
```

**Why:** illegible at print scale; below the design floor of 10pt.

**Fix:** snap to 10pt. If the figure has too much text to fit at 10pt, the figure is overloaded — split into panels.

### C.4 Vertical text

**Anti-pattern:**

```xml
<text writing-mode="vertical-rl">Vertical label</text>
<text transform="rotate(90 100 100)">Sideways</text>
```

**Why:** unreadable at print scale; signals layout failure (you couldn't fit the label horizontally).

**Fix:** rotate the panel layout, abbreviate the label, or move the label to a position where it fits horizontally.

### C.5 All-caps everywhere

**Anti-pattern:** `text-transform: uppercase` or actually-uppercase strings on axis labels and annotations.

**Fix:** sentence case. "Time (seconds)" not "TIME". Caps reserved for panel labels (A, B, C) and unit symbols.

---

## Category D: Layout mistakes

### D.1 Off-grid coordinates

See `references/grid_and_layout.md` for the grid discipline. Quick check: if a coord ends in 1, 2, 3, 5, 6, 7, 9 on 8px grid, snap it.

### D.2 Legend inside the diagram body

**Anti-pattern:** floating a legend over data marks, or stuffing it into a corner of the plot area without padding.

**Fix:** see the legend placement decision tree in `references/grid_and_layout.md`. Priority: top-right inside (with 8px padding) > bottom strip outside.

### D.3 Identical boxes for every diagram node

**Anti-pattern:** every node a same-size, same-color rounded rectangle.

**Why:** erases visual hierarchy; reader can't tell what's important.

**Fix:** vary size, weight, or fill for focal nodes. Use shape variety where it carries meaning (rect vs. ellipse vs. diamond).

### D.4 Crowding (no whitespace)

**Anti-pattern:** packing elements right up to panel edges and to each other.

**Fix:** apply the padding table from `references/grid_and_layout.md`. When in doubt, use more whitespace.

---

## Category E: Accessibility and metadata mistakes

### E.1 Missing root `<title>` / `<desc>`

**Anti-pattern:**

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <!-- straight to content, no <title>, no <desc> -->
  <rect ...
```

**Why:** screen-readers have nothing to surface; the alt-text formula has no anchor; preflight `fail`.

**Fix:** add one `<title>` (one-line label) and one `<desc>` (2-sentence alt-text formula). See `references/svg_authoring_standards.md` "Accessibility tags".

### E.2 Alt-text that describes mechanics, not findings

**Anti-pattern:**

```xml
<desc>Bar chart showing four bars in different colors.</desc>
```

**Why:** alt-text exists to communicate the message to readers who can't see the figure. "Bar chart" doesn't tell them anything.

**Fix:**

```xml
<desc>Treatment X reduced tumor volume by 60% compared to control over 12 weeks; combination therapy with drug Y achieved 85% reduction.</desc>
```

### E.3 `<script>` blocks

**Banned form:**

```xml
<script>...</script>
```

**Why:** figures are static. Scripts in SVG are a security and portability problem; many renderers strip them.

**Fix:** remove. If interactivity is required, the deliverable is HTML, not SVG.

### E.4 `<foreignObject>`

**Banned form:**

```xml
<foreignObject>
  <div xmlns="http://www.w3.org/1999/xhtml">...</div>
</foreignObject>
```

**Why:** breaks portability across renderers; rsvg-convert doesn't handle it cleanly.

**Fix:** use native SVG elements (`<text>`, `<rect>`, `<g>`).

---

## Severity map

The preflight checker uses these severity assignments:

| Category | Severity |
|---|---|
| A.1 Drop-shadow filters | `fail` |
| A.2 Glow / blur | `fail` |
| A.4 Rounded corners > 10 | `warn` |
| A.5 Inline gradients | `warn` |
| B.1 Color-only encoding | not mechanizable (vision-loop) |
| B.2 CSS named colors | `fail` |
| B.3 `currentColor` | `fail` |
| C.1 Missing font-family | `fail` |
| C.2 Off-ladder font sizes | `fail` |
| C.3 Text below 10pt | `fail` |
| C.4 Vertical text | `fail` |
| D.1 Off-grid coords | `warn` (or `fail` with `--strict-grid`) |
| E.1 Missing `<title>` / `<desc>` | `fail` |
| E.3 `<script>` blocks | `fail` |
| E.4 `<foreignObject>` | `fail` |
| Off-palette hex | `fail` |
