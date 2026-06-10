I now have everything I need: the exact canonical palettes (Oligon, Okabe-Ito, viridis_7, Paul Tol categorical_8), the matplotlib `tab10` default sequence (`#1f77b4` etc.) and seaborn defaults to flag, the `ValidationResult` contract, and the test conventions. Here is the complete code-first spec.

---

# Track B2 — New plotting-libraries validators (code-first spec)

## File placement decision

| Check | File | Justification |
|---|---|---|
| `check_encoding_value_fidelity` | **`validate_data.py`** | Inputs are the *plotted values + printed labels* — both held at generation time, before any file exists. It's a pure data/encoding reconciliation, identical in spirit to `check_continuous_as_bars` (takes `data` + intent, returns `ValidationResult`, advisory-but-can-error). No file I/O, no PIL/pdfinfo. Belongs with the data-side `ValidationResult` family. |
| `check_closure` | **`validate_data.py`** | Same: operates on the numeric series + declared whole/total. Pure arithmetic on the data dict. No rendered artifact needed. |
| `check_default_palette` | **`validate_data.py`** | Operates on the *color list the caller is about to pass to the plotting call* (a config/data input), compared against literal known-default sequences. No file, no rendered pixels. Goes with the other generation-time advisory checks so a single `from validate_data import ...` pulls the whole pre-plot gate. |

All three are **data-side**. `validate_figure.py` stays what it is: post-hoc, file-level, subprocess/PIL-backed production checks (DPI/format/fonts). Putting these three there would force it to accept in-memory data dicts, which breaks its `fig_path: str` contract. Keeping all generation-time semantic checks in `validate_data.py` also means the existing `check_continuous_as_bars` / `check_riskratio_as_bars` siblings stay co-located, and the checklist cross-reference (currently wrong — see §5) becomes uniformly "validate_data.py".

**Severity model (honoring guardrail #2).** These return `ValidationResult`, which has only `errors` (sets `valid=False`) and `warnings`. We map the two-tier severity onto that:
- **Categorical tells DOMINATE → `add_error`** (sets `valid=False`, blocking): encoding-vs-label geometry mismatch beyond tolerance; parts that fail to sum to the whole beyond rounding. These are the report's ⚑ override dimensions 2.1/2.2.
- **Weak / two-sided aesthetic signals → `add_warning`** (advisory, never blocks): literal default palette. We never tell the model to *strip* color or minimize ink — we only flag the *literal default* and name alternatives. A bespoke non-default palette never warns, even if "decorated."

Each check also returns the per-sub-score **vector** the orchestrator wants by tagging every message with a stable `[check_name/severity]` prefix, so the caller can collect a vector of `(check, severity, message)` without a composite score.

---

## 1. `check_encoding_value_fidelity` → `validate_data.py`

Insert after `check_riskratio_as_bars` (after line 606, the final `return result` of that function).

### Input contract (precise)

The caller passes the values it is *about to encode geometrically* plus any *printed value-labels* it is about to stamp, and the encoding family. The check confirms geometry-derived values reconcile to printed labels — exact, because we hold both.

```python
def check_encoding_value_fidelity(
    values: object,
    encoding: str,
    *,
    printed_labels: object = None,
    geometry: object = None,
    rel_tol: float = 0.01,
    abs_tol: float = 1e-9,
    axis_is_log: bool = False,
    axis_baseline: float = 0.0,
) -> ValidationResult:
```

**Contract per argument:**

- `values`: the numeric series being encoded. `list/tuple/np.ndarray/pd.Series`, or a `dict[str, number]` (label→value, e.g. pie wedges). These are the *true* data values the geometry must represent.
- `encoding`: one of `{"bar", "column", "stacked_bar", "pie", "donut", "scatter", "point", "line"}` (case-insensitive; bar aliases normalized). Selects the geometry→value law:
  - `bar`/`column`/`stacked_bar`: geometric length is linear in `(value - axis_baseline)`; on a log axis, length is linear in `log10(value) - log10(baseline_or_axis_min)`.
  - `pie`/`donut`: wedge angle (deg) is linear in `value`, total = 360°.
  - `scatter`/`point`/`line`: position is linear in value (identity), so a printed label must equal its plotted value.
- `printed_labels`: OPTIONAL. The literal value-labels/annotations the caller will stamp on the marks, **parallel to `values`** (same length / same dict keys). Each may be a number or a numeric string (`"42"`, `"3.0%"`, `"1,250"`) — parsed by stripping `%`, `,`, surrounding whitespace, `$`. `None` ⇒ the label-fidelity branch is skipped (no labels to desync). This is the dimension-2.1 categorical tell: **printed label must equal the value the geometry encodes.**
- `geometry`: OPTIONAL. The *actual rendered measure* per mark, if the caller computed it independently (post-transform bar pixel heights, wedge degrees, point coords) — parallel to `values`. When supplied, the check verifies `geometry` is the correct monotone transform of `values` (catches a transform that desyncs height from value: e.g. a secondary-axis rescale, an accidental `sqrt`, a log applied to height but not to the label). `None` ⇒ geometry is assumed to be the canonical law for `encoding`, so only `printed_labels` is checked.
- `rel_tol`, `abs_tol`: reconciliation tolerance (math.isclose semantics). Defaults are **provisional / uncalibrated** (1% relative). Documented as such in the docstring.
- `axis_is_log` / `axis_baseline`: edge-case handling for log axes and non-zero bar baselines (see edge cases).

### Return object

`ValidationResult` (existing dataclass). `valid=False` (`add_error`) on any reconciliation failure beyond tolerance — this is a dominating categorical tell. `add_warning` only for soft advisories (e.g. printed labels supplied but length mismatch makes the check inconclusive, or a non-zero baseline that *could* mislead but isn't strictly wrong).

### Algorithm

```
1. Normalize encoding (lowercase, strip; map bar aliases {bar,barplot,column,bar chart}->"bar").
   If encoding not in known set -> add_warning("unknown encoding, fidelity not checked"); return.
2. Coerce values to an ordered list of (key, float):
   - dict -> items() in insertion order
   - Series -> (index, value)
   - list/array -> (positional_index, value)
   Drop entries whose value is NaN, recording dropped keys.
3. PIE/DONUT branch (closure-adjacent but here we check angle proportionality):
   - total = sum(values). If total <= 0 -> add_error("non-positive total; angles undefined"); return.
   - expected_angle[i] = 360 * values[i] / total
   - if geometry given (rendered degrees): for each i, isclose(geometry[i], expected_angle[i]) else add_error.
4. BAR/COLUMN/STACKED branch (geometry vs value, when geometry given):
   - define encode(v):
        if axis_is_log: log10(v) - log10(axis_min_or_baseline)   # require v>0
        else:           v - axis_baseline
   - geometry must be POSITIVELY PROPORTIONAL to encode(values):
        compute ratios geometry[i]/encode(values[i]) over entries with encode!=0;
        if ratios are not all isclose to a single constant k>0 -> add_error
        ("geometry not a consistent linear transform of values; label/height desync").
     This catches: one bar scaled by a different factor, an inverted axis (k<0),
     a sqrt/log applied to height but not value.
5. SCATTER/POINT/LINE branch (when geometry given): encode is identity; geometry[i] must isclose value[i].
6. PRINTED-LABEL branch (all encodings, when printed_labels given):
   - parse each label to float (strip %, ',', '$', whitespace); unparseable -> add_warning(garbled label), continue.
   - For pie/donut: a printed label is conventionally the PERCENT or the raw value.
       Accept if isclose(label, value) OR isclose(label, 100*value/total) OR isclose(label, expected_angle).
   - Else: label must isclose(value).  (axis_baseline does NOT change the printed value — only the height.)
   - Any mismatch -> add_error("printed label X does not match encoded value Y for key K"
       " (encoding-vs-printed-value mismatch, dimension 2.1 categorical tell)").
7. Length/keys mismatch between values and printed_labels/geometry:
   -> add_warning("labels/geometry length differs from values; fidelity check incomplete").
8. Return result (valid=False if any add_error fired).
```

Note step 4 deliberately checks *proportional consistency* (a single shared scale `k`), not absolute pixel values — that is the exact, transform-agnostic way to detect "a transform that desyncs label from height" without knowing the renderer's units.

### Edge cases

- **Single series / single bar:** one entry. Proportionality with one point is trivially satisfied (k = geometry/encode); label branch still meaningful. No false error.
- **Negatives:** allowed for bar on a zero baseline (downward bars). `encode(v)=v-baseline` is signed; proportionality with shared `k>0` preserves sign. A *pie* with any negative value → `add_error("pie/donut cannot encode negative values")`. Scatter negatives fine.
- **NaN:** dropped before reconciliation; recorded in a warning (`"N NaN values excluded from fidelity check"`). Never crashes.
- **Log scale:** `axis_is_log=True` switches `encode` to log10-space; any `value <= 0` under log → `add_error("non-positive value on log axis")`. This is the classic place geometry desyncs from a linear printed label.
- **Non-zero baseline (truncated bar):** `axis_baseline != 0` is honored in `encode` (so geometry can legitimately be proportional to `v-baseline`) but the *printed label* must still equal `v`, not `v-baseline` — guarding the truncated-axis deception where the height shrinks but the number stamped is the full value (consistent) vs. the bar height being read as the value (we only assert label==value).
- **All-zero values:** `encode` all zero ⇒ skip proportionality (no ratios), `add_warning("all encoded magnitudes zero")`.

### Pytest cases (mirror `test_plot_selector.py` class style)

```python
class TestCheckEncodingValueFidelity:
    """Report dimension 2.1 (encoding–value fidelity), categorical tell."""

    def test_bar_geometry_matches_values_passes(self) -> None:
        r = check_encoding_value_fidelity(
            [10, 20, 30], "bar", geometry=[1.0, 2.0, 3.0]  # consistent k=0.1
        )
        assert r.valid is True
        assert len(r.errors) == 0

    def test_bar_geometry_desync_errors(self) -> None:
        # third bar scaled by a different factor -> height/label desync
        r = check_encoding_value_fidelity(
            [10, 20, 30], "bar", geometry=[1.0, 2.0, 9.0]
        )
        assert r.valid is False
        assert any("desync" in e or "linear transform" in e for e in r.errors)

    def test_printed_label_mismatch_errors(self) -> None:
        r = check_encoding_value_fidelity(
            [42.0], "bar", printed_labels=["57"]
        )
        assert r.valid is False
        assert any("does not match" in e for e in r.errors)

    def test_pie_angles_proportional_passes(self) -> None:
        r = check_encoding_value_fidelity(
            {"A": 25, "B": 25, "C": 50}, "pie",
            geometry=[90.0, 90.0, 180.0],          # degrees sum 360
            printed_labels=["25%", "25%", "50%"],
        )
        assert r.valid is True

    def test_pie_negative_value_errors(self) -> None:
        r = check_encoding_value_fidelity({"A": -5, "B": 10}, "pie")
        assert r.valid is False
        assert any("negative" in e.lower() for e in r.errors)

    def test_log_axis_nonpositive_value_errors(self) -> None:
        r = check_encoding_value_fidelity(
            [0.0, 10.0], "bar", geometry=[0.0, 1.0], axis_is_log=True
        )
        assert r.valid is False
        assert any("log" in e.lower() for e in r.errors)

    def test_nan_excluded_warns_not_errors(self) -> None:
        import numpy as np
        r = check_encoding_value_fidelity(
            [10.0, np.nan, 30.0], "bar", geometry=[1.0, 0.0, 3.0]
        )
        assert r.valid is True
        assert any("NaN" in w for w in r.warnings)
```

---

## 2. `check_closure` → `validate_data.py`

Insert immediately after `check_encoding_value_fidelity`.

### Signature

```python
def check_closure(
    parts: object,
    encoding: str,
    *,
    declared_total: Optional[float] = None,
    expect_percent: Optional[bool] = None,
    abs_tol_pct: float = 0.5,
    abs_tol_total: Optional[float] = None,
    rel_tol_total: float = 0.005,
) -> ValidationResult:
```

**Contract:**
- `parts`: the parts-of-whole series — `list/tuple/np.ndarray/pd.Series` or `dict[str, number]` (segment→value). For pie/donut and stacked-bar.
- `encoding`: `{"pie", "donut", "stacked_bar", "stacked_column", "100_stacked_bar"}` (others ⇒ no-op return).
- `declared_total`: the stated whole the segments must reconcile to (e.g. a printed "n = 1,250" or a "Total" annotation). For percent pies the implied whole is 100. `None` + percent-mode ⇒ compare to 100; `None` + absolute-mode ⇒ closure is auto-satisfied (nothing to reconcile against) and we only flag *internal* impossibilities.
- `expect_percent`: force percent interpretation. `None` ⇒ auto-detect (all parts in [0,100] and sum within tolerance of 100, OR keys/labels suggest %). 
- `abs_tol_pct`: tolerance in percentage points for the "sum to 100%" test. Default **0.5 pp** — chosen so legitimately-rounded slices (e.g. 33.3 + 33.3 + 33.3 = 99.9) pass, but a real conservation failure (sums to 92%) fails. Provisional/uncalibrated.
- `abs_tol_total` / `rel_tol_total`: tolerance for reconciling against an absolute `declared_total` (default 0.5% relative).

### Rounding-tolerance handling (specified)

This is the crux of dimension 2.2's "1 = rounding-level gap" vs "2 = fails to sum":
- **Percent mode:** `gap = abs(sum(parts) - 100)`.
  - `gap <= abs_tol_pct` → pass (rounding-level, no message).
  - `abs_tol_pct < gap <= 1.0` → `add_warning` (rounding-level gap, dimension-2.2 anchor "1": advisory, the slices were probably independently rounded).
  - `gap > 1.0` → `add_error` (fails to close — dominating categorical tell, anchor "2").
- **Absolute mode:** `gap = abs(sum(parts) - declared_total)`; tolerance = `max(abs_tol_total or 0, rel_tol_total*declared_total)`. Within tol → pass; within 2× tol → warn; else error.

The two-band split (warn vs error) is exactly the report's 1/2 anchor and keeps rounding noise out of the blocking tier.

### Return object

`ValidationResult`. Error (blocking) on true conservation failure; warning on rounding-band gap or structural advisories.

### Algorithm

```
1. Normalize encoding; if not a parts-of-whole encoding -> return empty valid result.
2. Coerce parts to [(key, float)]; drop NaN (record count in a warning).
   If empty after drop -> add_warning("no numeric parts"); return.
3. Negatives: any part < 0 ->
     pie/donut/100_stacked -> add_error("negative segment cannot be part of a whole")
     stacked_bar -> add_warning (diverging stacked bars exist; advisory only).
4. Determine mode:
     if expect_percent is True OR (expect_percent None and declared_total None and
        all 0<=p<=100 and abs(sum-100)<=1.0):  -> percent mode, whole=100
     elif declared_total is not None: -> absolute mode, whole=declared_total
     else: -> "no whole to reconcile"; only internal checks ran; return.
5. gap = abs(sum(parts) - whole)
6. Apply two-band tolerance (see Rounding-tolerance handling) -> pass / warn / error
   with message naming sum, whole, and gap, tagged
   "[check_closure/...] parts sum to {s} but whole is {whole} (gap {gap}); ...
    dimension 2.2 conservation".
7. Return.
```

### Edge cases

- **Single series:** one part. Percent-mode: a single 100% slice passes; a single 80% slice errors (doesn't close). Sensible.
- **Negatives:** pie/donut/100%-stacked → error; ordinary diverging stacked bar → warning (two-sided: we don't forbid a legitimate diverging stack).
- **NaN:** dropped, counted in a warning; closure computed on the remainder (so an all-NaN input is inconclusive, not a crash).
- **Log scale:** not applicable to parts-of-whole; if `axis_is_log` were ever relevant it isn't here — closure is on raw values, ignore axis transform entirely.
- **Floating rounding:** handled by the explicit two-band tolerance; `33.33*3` passes, `0.333*3` (fractions) in percent auto-detect won't misfire because auto-detect requires values in [0,100].
- **declared_total = 0:** `add_error("declared total is zero; cannot reconcile")`.

### Pytest cases

```python
class TestCheckClosure:
    """Report dimension 2.2 (closure / conservation)."""

    def test_pie_sums_to_100_passes(self) -> None:
        r = check_closure({"A": 25, "B": 25, "C": 50}, "pie")
        assert r.valid is True
        assert len(r.errors) == 0

    def test_pie_rounding_gap_warns_not_errors(self) -> None:
        # 33.3*3 = 99.9 -> within the rounding band (>0.5pp, <=1.0pp)
        r = check_closure([33.3, 33.3, 33.3], "pie", expect_percent=True)
        assert r.valid is True
        assert any("gap" in w for w in r.warnings)

    def test_pie_fails_to_sum_errors(self) -> None:
        r = check_closure([20, 30, 42], "pie", expect_percent=True)  # 92%
        assert r.valid is False
        assert any("conservation" in e or "whole" in e for e in r.errors)

    def test_stacked_bar_reconciles_to_declared_total(self) -> None:
        r = check_closure([400, 350, 500], "stacked_bar", declared_total=1250)
        assert r.valid is True

    def test_stacked_bar_total_mismatch_errors(self) -> None:
        r = check_closure([400, 350, 500], "stacked_bar", declared_total=2000)
        assert r.valid is False

    def test_negative_pie_segment_errors(self) -> None:
        r = check_closure({"A": -10, "B": 110}, "pie")
        assert r.valid is False
        assert any("negative" in e.lower() for e in r.errors)

    def test_non_partsofwhole_encoding_is_noop(self) -> None:
        r = check_closure([20, 30, 42], "scatter")
        assert r.valid is True
        assert len(r.errors) == 0 and len(r.warnings) == 0
```

---

## 3. `check_default_palette` → `validate_data.py`

Insert after `check_closure`. Also add the module-level default fingerprints near the top constants (after `_RISKRATIO_PATTERNS`).

### Module-level constants

```python
# Literal tool-default color cycles, lowercased hex. Flagged (advisory) when
# passed verbatim as a series palette. TWO-SIDED: we flag the *literal default*
# only; any bespoke / brand / CVD-safe palette never warns. We never instruct
# stripping color or minimizing ink (Bateman CHI2010: over-minimization is itself
# a regression-to-mean failure).
_MPL_TAB10 = (
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
)
# seaborn "deep" default (sns.color_palette() with no args, mpl>=2 cycle variant)
_SEABORN_DEEP = (
    "#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3",
    "#937860", "#da8bc3", "#8c8c8c", "#ccb974", "#64b5cd",
)
# Recommended replacements (names from plotting_params.PALETTES).
_DEFAULT_PALETTE_REPLACEMENTS = "Oligon, Okabe-Ito, Paul-Tol Categorical 8, or viridis"
```

### Signature

```python
def check_default_palette(
    palette: object,
    *,
    match_threshold: float = 0.6,
    require_prefix_run: int = 3,
) -> ValidationResult:
```

**Contract:**
- `palette`: the color sequence the caller is about to pass as the series palette — `list/tuple` of hex strings (`"#1f77b4"`), or named-string sentinels `{"tab10", "C0", "default", "matplotlib", "seaborn", "deep"}` indicating an unmodified default was requested by name. RGB tuples `(0.12, 0.47, 0.71)` accepted and converted to hex. `None` / empty ⇒ no-op (caller didn't pin colors; renderer default applies — out of scope here because we can't see it).
- `match_threshold`: fraction of the supplied palette that must coincide (order-aligned) with a known default to flag. Default 0.6 — provisional. Prevents flagging a bespoke palette that merely happens to reuse one tab10 blue.
- `require_prefix_run`: minimum length of an *aligned leading run* matching a default (e.g. the C0-blue/C1-orange/C2-green opening of tab10) that also triggers a flag even if the tail diverges — because the recognizable tab10 *opening* is the documented fingerprint (Chart_slop §"Default-library-styling detection").

### Return object

`ValidationResult`, **warning-only** (never `add_error`). Palette is the weak, two-sided aesthetic axis (guardrail #2): a literal default is *flagged*, but it is not a lie. `valid` stays `True` always.

### Algorithm

```
1. If palette is None / empty / a non-color scalar -> return empty valid result.
2. If palette is a known default-by-name sentinel ("tab10","default","C0",
   "matplotlib","seaborn","deep") -> add_warning(named-default flag); return.
3. Normalize to a list of lowercase hex strings:
   - "#RRGGBB" / "#RGB" -> lowercase, expand short form
   - (r,g,b) floats in 0..1 -> "#rrggbb"
   - unparseable entries -> skipped (recorded count); if nothing parses -> no-op return.
4. For each known default D in (_MPL_TAB10, _SEABORN_DEEP):
     a. aligned_matches = count(i where palette[i] == D[i]) over min(len) prefix
        frac = aligned_matches / len(palette)
     b. leading_run = length of the maximal i-prefix where palette[i]==D[i]
     c. if frac >= match_threshold OR leading_run >= require_prefix_run:
          add_warning(
            "check_default_palette: palette matches the {name} tool default "
            "(frac={frac:.0%}, leading run={run}). This is a generative-slop "
            "fingerprint (template/default-distribution look, report dimension 6.2). "
            "TWO-SIDED: a default is not an error; if a default look is intended, ignore. "
            "Otherwise prefer a bespoke/brand CVD-safe palette: {replacements}. "
            "See plotting_params.recommend_palette()."
          )
          break   # one match is enough; don't double-warn
5. Return (always valid=True).
```

### Edge cases

- **Single series:** a one-color palette can't match a multi-color default fingerprint by `frac` unless that single color *is* `#1f77b4` and `require_prefix_run` allows a run of 1 — we set `require_prefix_run=3` precisely so a lone C0-blue does **not** false-flag (one blue is not a fingerprint).
- **Negatives / NaN:** not applicable to color strings; non-string/non-RGB entries are skipped and counted (no crash).
- **Log scale:** irrelevant to palette; ignored.
- **Brand/CVD palettes (Oligon, Okabe-Ito, viridis_7, Tol categorical_8):** none share an aligned ≥3 prefix or ≥60% overlap with tab10/seaborn-deep, so they pass clean. (Verified against the hex in `plotting_params.PALETTES`.) This is the two-sided guarantee: recommended palettes never warn.
- **Reordered default:** if a user shuffles tab10, `frac` over aligned positions drops and `leading_run` breaks — we *intentionally don't* flag a reordered default (it's no longer the recognizable canonical opening; treating it as bespoke is the conservative, low-false-positive choice).

### Pytest cases

```python
class TestCheckDefaultPalette:
    """Report dimension 6.2 (template/default-distribution look), two-sided weak signal."""

    def test_tab10_palette_warns(self) -> None:
        r = check_default_palette(
            ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        )
        assert r.valid is True            # never blocks
        assert len(r.warnings) == 1
        assert "default" in r.warnings[0].lower()

    def test_named_default_sentinel_warns(self) -> None:
        r = check_default_palette("tab10")
        assert r.valid is True
        assert any("default" in w.lower() for w in r.warnings)

    def test_okabe_ito_palette_no_warning(self) -> None:
        r = check_default_palette(
            ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2"]
        )
        assert len(r.warnings) == 0       # recommended palette is clean (two-sided)

    def test_oligon_brand_palette_no_warning(self) -> None:
        r = check_default_palette(["#222222", "#2db2e8", "#666666", "#e8622d"])
        assert len(r.warnings) == 0

    def test_single_c0_blue_does_not_false_flag(self) -> None:
        r = check_default_palette(["#1f77b4"])  # one blue is not a fingerprint
        assert len(r.warnings) == 0

    def test_seaborn_deep_palette_warns(self) -> None:
        r = check_default_palette(
            ["#4c72b0", "#dd8452", "#55a868", "#c44e52"]
        )
        assert len(r.warnings) == 1

    def test_rgb_float_tuples_normalized_and_flagged(self) -> None:
        # tab10 C0/C1/C2 as 0..1 RGB floats
        r = check_default_palette(
            [(0.121, 0.466, 0.705), (1.0, 0.498, 0.054), (0.172, 0.627, 0.172)]
        )
        assert len(r.warnings) == 1

    def test_none_palette_is_noop(self) -> None:
        r = check_default_palette(None)
        assert r.valid is True
        assert len(r.warnings) == 0
```

---

## 4. Module docstring + `__main__` updates (match existing conventions)

**Extend the top-of-file usage import block** (lines 8–14) — insert after `check_riskratio_as_bars,`:

```python
        check_encoding_value_fidelity,
        check_closure,
        check_default_palette,
```

**Extend the section banner comment** (the `CHART-DESIGN VALIDATORS` block, lines 417–431) with three new bullets so the file's self-documentation stays accurate:

> Insert near the line `#   check_riskratio_as_bars   -- Fujii 2023 J Epidemiol: risk ratios / odds`:
```
#   check_encoding_value_fidelity -- AI-figure-slop dim 2.1: bar/pie/point
#                                geometry must reconcile to printed value-labels.
#   check_closure             -- dim 2.2: parts-of-whole must sum to the whole
#                                (pie ~100%, stacked-bar to declared total).
#   check_default_palette     -- dim 6.2 (two-sided, advisory): flags literal
#                                matplotlib tab10 / seaborn-deep default cycles.
```

These three are GENERATION-time exact checks against data we already hold (no OCR / forensic CV — see Track-B governing insight).

---

## 5. Corrected cross-reference lines for `pre_submission_checklist.md`

All three new checks land in `validate_data.py`, and the existing two are *already* in `validate_data.py` but mis-pointed at `validate_figure.py`. Apply these exact edits.

**Item #13, line 117** — replace:
```
**Verify:** See `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md` for code recipes.
```
with:
```
**Verify:** See `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md` for code recipes.
```

**Item #14, line 123** — replace:
```
**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`.
```
with (append the corrected programmatic pointer that was missing):
```
**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`. Programmatic: `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars`.
```

**Tooling cross-references table, lines 149–150** — replace both rows:
```
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_figure.py::check_riskratio_as_bars` |
```
with (corrected path + two new rows for the new checks):
```
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars` |
| Encoding–value fidelity | `plotting-libraries/scripts/validate_data.py::check_encoding_value_fidelity` |
| Closure / conservation | `plotting-libraries/scripts/validate_data.py::check_closure` |
| Default-palette fingerprint | `plotting-libraries/scripts/validate_data.py::check_default_palette` |
```

(Optionally, two new checklist items #16/#17 could be added for encoding-value fidelity and closure, but that expands the "15-point" gate — flag for the checklist owner rather than silently renumbering.)

---

## 6. Guardrail compliance summary

- **Guardrail #1 (vector, not composite; provisional thresholds):** each check returns an independent `ValidationResult`; the orchestrator collects `(check_name, severity, message)` tuples via the `[check_name/severity]` message prefix — no single number is produced. Every tolerance (`rel_tol=0.01`, `abs_tol_pct=0.5`, `match_threshold=0.6`, `require_prefix_run=3`) is documented in-docstring as **provisional / uncalibrated**, mirroring the report's "constructed instrument, needs calibration" caveat.
- **Guardrail #2 (categorical tells dominate; aesthetics weak + two-sided):** fidelity and closure failures use `add_error` (blocking, `valid=False`) — they are the ⚑ dimensions 2.1/2.2. Default-palette uses `add_warning` only, never blocks, explicitly two-sided ("a default is not an error… if a default look is intended, ignore"), and the message **never** tells the model to strip color or minimize ink (Bateman CHI2010 over-minimization caveat is quoted in the constant comment). Recommended CVD/brand palettes are verified to pass clean.
- **Track-B governing insight:** all three are EXACT checks against the data dict + chosen encoding we already hold at generation time — no OCR, no forensic CV, no image→data recovery. They live in `validate_data.py` precisely because they operate pre-render on inputs.

**Files to modify:**
- `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/plotting-libraries/scripts/validate_data.py` (add 3 functions + 3 constants + docstring/banner edits)
- `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/plotting-libraries/scripts/tests/test_plot_selector.py` (add 3 test classes — this is where the sibling `check_*` tests already live)
- `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/shared/references/pre_submission_checklist.md` (fix lines 117, 123, 149–150 per §5)