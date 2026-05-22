# Programmatic Authoring with `drawsvg`

The hand-written XML path (templates + `Edit`) is the default of this skill —
the vision loop pays off most when every coordinate is yours. Reach for the
programmatic path when the figure is **parametric or repeated**: N panels
with identical structure varying only in data, a grid of small multiples,
a stack of overlay annotations driven by an external table. Writing one
script that emits all N panels collapses error surface and makes
re-generation cheap.

This document captures the rules that make `drawsvg` output behave inside
this skill's render→inspect→fix loop: deterministic, brand-compliant, and
preflight-clean on the first try.

---

## When to choose programmatic over hand-written

| Decision input | Choose programmatic | Choose hand-written |
|---|---|---|
| Panel count | ≥ 3 with identical structure | 1–2, or each panel is bespoke |
| Variation across panels | Data only (labels, values, color role) | Layout, decoration, annotations all vary |
| Future re-runs likely? | Yes — data may change | No — one-shot illustration |
| Source-of-truth for geometry | Should live in code (a table, a formula) | Should live in the SVG markup |
| Vision-loop iteration target | Whole-figure composition, not per-element | Per-element placement |

If the answer is mixed (parametric layout + bespoke annotations), do the
parametric base in `drawsvg` and `Edit` the resulting SVG for the
annotations — the post-process step is just another Stage-6 iteration.

---

## Install — PEP-723 inline metadata

Declare `drawsvg` as an inline dependency at the top of the script.
`uv run --script` reads the metadata and installs into an ephemeral
environment — no global install, no `requirements.txt` to maintain.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["drawsvg>=2.4"]
# ///
"""…"""
```

Invoke with `uv run --script` (note: NOT `uv run python script.py` —
that bypasses the PEP-723 metadata block and you'll get
`ModuleNotFoundError`):

```sh
uv run --script templates/parametric_4panel.py --tokens ../oligon-brand/tokens/brand-tokens.json -o figure.svg
```

This matches the convention used across `scripts/preflight_check.py`,
`scripts/render_and_inspect.py`, and `scripts/finalize.py` in this skill —
all PEP-723 self-bootstrapping.

---

## Brand discipline — load the palette, never improvise

The same rule as the hand-written path: **no hex literal in the layout
code**. Read `oligon-brand/tokens/brand-tokens.json` once at startup,
build a role → hex dict, and reference colors by role from then on.

```python
def load_palette(tokens_path: Path) -> dict[str, str]:
    data = json.loads(tokens_path.read_text())
    colors = data["colors"]
    return {
        "background": colors["structure"]["white"]["hex"],
        "highlight": colors["primary"]["brand_blue"]["hex"],
        "neutral_primary": colors["neutrals"]["dark_gray"]["hex"],
        "axis": colors["structure"]["gridline"]["hex"],
        "text": colors["neutrals"]["dark_gray"]["hex"],
        # … add roles as needed
    }
```

KeyError on a missing token is desirable — silent fallback to an off-brand
default is the failure mode we are explicitly preventing. If a role isn't
in the palette, the answer is to use a role that is, not to hard-code a
hex.

The full role → token mapping is shown in `templates/parametric_4panel.py`.

---

## Geometry — pin the grid in constants

Every coordinate `drawsvg` emits comes from your Python. That means every
off-grid pixel is your fault, and the preflight `--strict-grid` mode will
name the offending element. The fix: **declare margins, gutters, and panel
sizes as constants chosen so the grid math works out exactly**.

The arithmetic invariant for an N-panel horizontal row, all on the 8px
grid, with text centering working (PANEL_W // 2 must also be on-grid):

```
2 · MARGIN_X + (N − 1) · GUTTER + N · PANEL_W = VIEWBOX_W
PANEL_W mod 16 == 0      # so PANEL_W // 2 lands on the 8px grid
GUTTER  mod 8  == 0
MARGIN_X mod 8 == 0
```

Worked example used by `templates/parametric_4panel.py`:
`VIEWBOX_W=1024, MARGIN_X=16, GUTTER=32, PANEL_W=224 (= 14·16)`.
Check it: `2·16 + 3·32 + 4·224 = 32 + 96 + 896 = 1024 ✓`.

Add module-level `assert PANEL_W % 16 == 0` so the script fails loudly if
someone tweaks one constant without re-solving the equation.

For derived values (bar widths from data, panel heights from a metric):
snap to the grid as the last step.

```python
GRID = 8

def snap_to_grid(n: int) -> int:
    return max(0, int(round(n / GRID)) * GRID)

bar_h = snap_to_grid(int(round(PANEL_H * value / VALUE_MAX)))
```

The snap concentrates the rounding error in one place where it's obvious.
Spreading it inline across the layout produces drift that's hard to
unwind.

---

## Determinism — the rules the loop depends on

The whole reproducibility contract — `tokens_hash` in the sidecar, "same
intent → same SVG" — depends on the script being a pure function of its
inputs. `drawsvg` cooperates by default, but only if you don't introduce
non-determinism yourself.

**Honor drawsvg's defaults:**
- `dw.Drawing(...)` — leave `randomize_ids=False` (the default for
  `as_svg()`). It must be False; otherwise IDs change every run.
- Element order in the SVG is the order you `.append(...)` in — preserve it.

**Avoid these failure modes:**
- `import random` without a seed → re-runs differ on every byte the random
  values touched. If you need randomness for a noisy scatter, seed
  `random.seed(0)` (or per-figure derived from `figure_id`).
- `datetime.now()` baked into the SVG → trivially non-deterministic.
- Iterating a dict where insertion order doesn't equal logical order. CPython
  preserves insertion order, but if your dict came from `set()` operations
  or string-keyed merges across modules, sort before iterating:
  `for k in sorted(data):`.
- `float`-based geometry where rounding mode depends on the value range.
  Stick to integers; if you must compute in float, round once at the end.
- `as_svg(randomize_ids=True)` — explicit opt-out of the determinism contract.

**Verify, don't trust:** run the script twice, `diff -q` the outputs. If
the bytes differ, something is leaking. The Phase 4 test
(`tests/test_programmatic_demo.py`) does exactly this.

---

## Accessibility scaffolding — `<title>`, `<desc>`, `font-family`

`drawsvg` 2.4 ships `dw.Title` but no `Desc` class. Insert the `<desc>`
element via `dw.Raw(...)`; preflight's `root_desc_present` check is keyed
to a non-empty `<desc>`, not to how it got there.

```python
d.append(dw.Title("Parametric four-panel comparison"))
d.append(dw.Raw(
    "<desc>Four panels comparing one control and three treatments; "
    "Treatment B is the focal condition.</desc>"
))
```

For `font-family`, declare it once on a parent `<g>` and let `<text>`
children inherit. Preflight walks the parent chain when checking
`text_font_family`, so the inheritance is honored.

```python
panels = dw.Group(font_family="Arial, Helvetica, sans-serif")
panels.append(dw.Text("Label", font_size=12, x=400, y=240, text_anchor="middle"))
panels.append(dw.Text("Another", font_size=12, x=400, y=280, text_anchor="middle"))
d.append(panels)
```

---

## The drawsvg quirk: root `width`/`height`

`drawsvg.Drawing.as_svg()` always emits `width="…" height="…"` on the root
`<svg>` alongside the `viewBox`. The preflight `no_root_dimensions` check
**warns** on this (it prefers `viewBox` alone for scalable embedding into
PDFs and posters). Strip the pair as the last step before writing:

```python
def render_clean_svg(d: dw.Drawing) -> str:
    svg = d.as_svg()
    return re.sub(
        r'(\s+width="[^"]*"\s+height="[^"]*")(\s+viewBox=)',
        r"\2",
        svg,
        count=1,
    )
```

A regex tied to `drawsvg`'s exact output is acceptable here: if `drawsvg`
ever changes its tag layout we want the determinism test to fail loudly,
not silently emit root dimensions.

---

## End-to-end pipeline

The programmatic path joins the standard workflow at Stage 3 — the SVG
produced by your script is the same artifact a hand-written template would
have produced.

```sh
# Stage 2 (Draft) — emit SVG from the parametric script
uv run --script templates/parametric_4panel.py \
    --tokens ../oligon-brand/tokens/brand-tokens.json \
    -o figure.svg

# Stage 3 + 4 (Preflight + Rasterize)
uv run python scripts/render_and_inspect.py figure.svg \
    --tokens ../oligon-brand/tokens/brand-tokens.json \
    --iteration 1 \
    -o report.json

# Stage 5 (Vision critique) — Read figure.preview.png and walk
# references/visual_critique_checklist.md, emit critique.json

# Stage 6 (Iterate) — for the programmatic path, ALWAYS edit the script,
# not the SVG. If you fix the SVG by hand, the next re-run regenerates the
# bug. This is the defining discipline of the programmatic path.

# Stage 7 (Finalize)
uv run python scripts/finalize.py figure.svg \
    --tokens ../oligon-brand/tokens/brand-tokens.json \
    --preview figure.preview.png \
    --figure-id my-figure \
    --out-dir ./out
```

---

## Common pitfalls

### Editing the SVG output instead of the script

You ran the script, the preflight flagged a label position, you opened
`figure.svg` and nudged the `<text x>` value. Next time someone re-runs
the script, the nudge vanishes. The script is the source of truth.

**Fix:** every Stage-6 iteration in the programmatic path edits the
**script**, then re-emits the SVG, then re-runs preflight. If a fix is
inherently per-instance (a one-off annotation for one figure), do that as
a hand-written Edit step after the parametric base — but document it in
the figure's iteration log (`primary_fixes: ["hand-tuned annotation X"]`)
so the next reader knows the SVG diverged from the script.

### Hex literals creep back in

Six iterations into a complex figure, a teammate adds `fill="#3498DB"`
because "it's close enough to Brand Blue." Preflight will catch it (it's
not in the palette), but the warning is louder if you keep the discipline
visible: every `fill=` / `stroke=` / `stop-color=` in the layout code
references `palette["role"]`, never a literal.

**Fix:** code-review yourself for hex literals before re-running preflight.
A grep against the script — `grep -E '#[0-9A-Fa-f]{3,6}' templates/yourfig.py`
— should match nothing in layout code (only in palette test fixtures).

### Off-grid coords from un-checked arithmetic

`PANEL_W = 222` happens when you change `VIEWBOX_W` from 1024 to 1000 and
forget to re-solve the grid equation. The script still runs; the
preflight `--strict-grid` mode names every off-grid coord.

**Fix:** module-level `assert PANEL_W % 16 == 0`. The script crashes on
import instead of producing a quietly-drifted figure.

### `randomize_ids=True` slipped in via a copy-paste

`dw.Drawing.as_svg()` defaults to `randomize_ids=False`. Some drawsvg
docs/examples set it True for animation contexts; pasting one of those
into your figure script silently breaks determinism.

**Fix:** the determinism test (two runs, `diff -q`) catches this on the
first regression.

---

## Reference: the canonical worked example

`templates/parametric_4panel.py` is the canonical end-to-end example. It
demonstrates every pattern in this doc:

- PEP-723 inline metadata with `drawsvg>=2.4`
- Palette loaded from `brand-tokens.json` with explicit role mapping
- Grid arithmetic with module-level `assert` invariants
- `dw.Title` + `dw.Raw` for accessibility tags
- `dw.Group(font_family=…)` for inherited typography
- `snap_to_grid` helper for derived values
- `render_clean_svg` post-process to strip the root `width`/`height`
- CLI matching the rest of the skill's script idiom

Read it before starting your own programmatic figure; copy it as a
starting point if it's close to what you need.
