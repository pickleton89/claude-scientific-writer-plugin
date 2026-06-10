I now have everything I need. I have the exact conventions: `_finding(check, severity, message, principle_ref, location)`, severities `"pass"|"warn"|"fail"`, `principle_ref` uses `doc.md§X` or `doc.md#X` keys, `_iter_elements`, `_collect_color_values`, and the run_checks aggregation. The anti_patterns.md confirms tab10/`1f77b4` is mentioned only as prose (B.5) — no mechanized check exists, so no double-reporting collision there. I'll wire the new section-ref doc as `ai_figure_slop.md`.

One design note: the existing severity enum is only `pass|warn|fail`. The task requires a CATEGORICAL severity that dominates. I'll introduce a new `"categorical"` severity value and document how run_checks/overall must treat it (it maps to fail-or-worse, sorts above fail). Here is the spec.

---

# Track B1 Spec — three new deterministic checks for `preflight_check.py`

## 0. Conventions this spec obeys (verified against the file)

- **PEP-723 header**: `requires-python = ">=3.11"`, `dependencies = []`. All three checks are **stdlib-only** (`re`, `unicodedata`, `string` — all stdlib). No new deps; the header is untouched.
- **Finding shape**: every check emits `_finding(check, severity, message, principle_ref="", location=None)`.
- **Severity enum today**: `"pass" | "warn" | "fail"`. We add one value — **`"categorical"`** — for the dominant garbled-text tell. It is documented as "fail-or-worse; sorts above fail; flips `overall` to `fail`." This honors Guardrail 2 (categorical tells dominate) without collapsing into a composite score.
- **`principle_ref` key style**: existing keys are `doc.md§N.N` or `doc.md#X.Y`. New checks point at a **new reference doc** `ai_figure_slop.md` with `§` section keys: `§1` (garbled text), `§2` (default palette), `§3` (raw-index labels). (You ship `ai_figure_slop.md` separately — it is the Track-B home for these three tells. Its three sections map 1:1 to the rubric's metrics 1.1/1.2, 6.2, and 2.3 respectively.)
- **`location`**: `el.attrib.get("id") or "<tag>"`, matching every other check.
- **Aggregation**: each check returns `list[dict]`; emits exactly one `pass` finding when clean (matching `check_no_banned_filters` etc.).

---

## 1. `check_garbled_text` — lexical-plausibility of `<text>`/`<tspan>` content

**This is the #1 categorical tell** (Frontiers rat: `testtomcels`, `diƨlocttal`, `Tramioncatiion`). Per Guardrail 2 it dominates; per Guardrail 1 it is one sub-score among many, never folded into a composite.

### Constants (module-level, near `ALLOWED_FONT_SIZES`)

```python
# --- check_garbled_text -------------------------------------------------------
# A token is exempt from lexical scrutiny if it matches any ALLOW pattern.
# These cover the legitimate "non-word" strings scientific figures carry.
import string  # stdlib
import unicodedata  # stdlib

_GREEK = (
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi "
    "omicron pi rho sigma tau upsilon phi chi psi omega"
).split()

# Single Greek code points (α … ω, Α … Ω) are always allowed as glyphs.
_GREEK_CODEPOINTS = {chr(c) for c in range(0x0391, 0x03CA)}  # Greek block, letters

# Tokens that are legitimately "wordless" in scientific figures.
_ALLOW_TOKEN_PATTERNS = [
    re.compile(r"^[+\-]?\d+(?:[.,]\d+)?$"),                 # plain numbers: 12, -3.5, 1,000
    re.compile(r"^[+\-]?\d+(?:\.\d+)?[eE][+\-]?\d+$"),      # scientific: 1.2e-3
    re.compile(r"^\d+(?:\.\d+)?\s*[-–—]\s*\d+(?:\.\d+)?$"), # axis ranges: 0-100
    re.compile(r"^[pP]\s*[<>=≤≥]\s*0?\.\d+$"),              # p-values: p<0.05
    re.compile(r"^[<>=≤≥]?\d"),                             # any value starting with comparator+digit
    re.compile(r"^[A-Z][A-Z0-9]{1,9}$"),                   # gene symbols / acronyms: TP53, JAK2, mRNA-ish caps
    re.compile(r"^[A-Za-z]+\d+[A-Za-z0-9]*$"),             # alphanumeric identifiers: CD4, H3K27, R2
    re.compile(r"^\d+[A-Za-z%‰°·/]+$"),                    # number+unit: 60%, 12mm, 5h, 37°
    re.compile(r"^[µμnmkMGTpfcd]?[gLmsMVAJWKΩ]\b"),        # SI-ish unit stems: mg, µL, kDa, mV
    re.compile(r"^[A-Za-z]{1,3}$"),                         # very short tokens (axis ticks, A/B/C, log)
    re.compile(r"^[\W_]+$"),                                # pure punctuation/symbols: →, ±, (, /
]

# Common chemistry/units allowlist (lowercased), extend freely; small + local.
_ALLOW_WORDS = {
    "kda", "bp", "kb", "mb", "rpm", "od", "ph", "ci", "sd", "sem", "se", "ns",
    "log", "ln", "vs", "wt", "ko", "ctrl", "mock", "dmso", "pbs", "rna", "dna",
    "mrna", "cdna", "sirna", "pcr", "elisa", "facs", "ic50", "ec50", "kd", "km",
    "wild", "type", "time", "days", "hours", "min", "sec", "weeks", "months",
    "control", "treatment", "treated", "untreated", "baseline", "fold", "change",
    "expression", "relative", "normalized", "count", "frequency", "percent",
    "concentration", "dose", "response", "mean", "median", "total", "sample",
    "group", "stage", "grade", "score", "value", "ratio", "rate", "index",
    "signaling", "pathway", "stem", "cells", "cell", "tissue", "protein", "gene",
}
# Plus the Greek names themselves:
_ALLOW_WORDS |= set(_GREEK)

# Charset classes used by the heuristic.
_VOWELS = set("aeiouyAEIOUY")
```

### Signature

```python
def check_garbled_text(root: ET.Element) -> list[dict[str, Any]]:
    """Flag lexically-void glyph strings in <text>/<tspan> content.

    The #1 categorical AI tell (ai_figure_slop.md §1): diffusion-rendered
    labels that are typographically letter-shaped but lexically void
    ("diƨlocttal", "Tramioncatiion"), mixed-script runs, invented diacritics,
    or consonant scrambles. Stdlib-only, dictionary-free: decision rests on
    charset mixing, vowel ratio, consonant runs, and a small unit/term
    allowlist. Clearly-void tokens -> severity "categorical" (dominates);
    ambiguous tokens -> "warn".
    """
```

### Algorithm (real Python, tight)

```python
def _tokenize_label(text: str) -> list[str]:
    # Split on whitespace; keep intra-token punctuation (hyphens, slashes, +).
    return [t for t in re.split(r"\s+", text.strip()) if t]

def _script_of(ch: str) -> str | None:
    # Coarse script bucket from the Unicode name; None for digits/punct/space.
    if ch.isdigit() or not ch.isalpha():
        return None
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return "UNKNOWN"          # unnamed code point -> suspicious glyph
    first = name.split(" ", 1)[0]
    # e.g. "LATIN", "GREEK", "CYRILLIC", "ARABIC"
    return first

def _is_allowed_token(tok: str) -> bool:
    low = tok.lower().strip(string.punctuation + "→←↑↓±·∗*•")
    if not low:
        return True                                   # pure punctuation
    if low in _ALLOW_WORDS:
        return True
    if any(ch in _GREEK_CODEPOINTS for ch in tok) and len(tok) <= 3:
        return True                                   # α, Δ, single-Greek labels
    for pat in _ALLOW_TOKEN_PATTERNS:
        if pat.match(tok):
            return True
    return False

def _void_signals(tok: str) -> list[str]:
    """Return the list of categorical-void signals a token trips (may be empty)."""
    signals = []
    letters = [c for c in tok if c.isalpha()]
    if len(letters) < 4:
        return signals                                # too short to judge

    # (a) Mixed-script run within one alphabetic token (Latin+Cyrillic etc.)
    scripts = {s for s in (_script_of(c) for c in letters) if s}
    real_scripts = scripts - {"UNKNOWN"}
    if len(real_scripts) >= 2:
        signals.append("mixed-script")
    if "UNKNOWN" in scripts:
        signals.append("unnamed-glyph")

    # (b) Combining marks on a Latin base that don't form a known precomposed
    #     letter -> "invented diacritic". Count standalone combining marks.
    combining = sum(1 for c in tok if unicodedata.combining(c))
    if combining >= 2:
        signals.append("stacked-diacritics")

    # (c) Vowel ratio: natural words/scientific terms rarely < 0.15 vowels
    #     over a 5+ letter run. Pure-consonant scrambles fall here.
    vowel_ratio = sum(1 for c in letters if c in _VOWELS) / len(letters)
    if len(letters) >= 6 and vowel_ratio < 0.12:
        signals.append("no-vowels")

    # (d) Consonant run length: >5 consecutive consonants is near-impossible
    #     in scientific English (CRISPR=6 is the famous edge; allow <=5).
    run = max_run = 0
    for c in tok:
        if c.isalpha() and c not in _VOWELS:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    if max_run >= 7:
        signals.append("consonant-run")

    # (e) Repeated-letter scramble: same letter >=4x total in a short token
    #     (e.g. "diƨlocttal" doubling), or a trigram repeated.
    from collections import Counter
    counts = Counter(c.lower() for c in letters)
    if max(counts.values()) >= 4 and len(letters) <= 12:
        signals.append("letter-pileup")

    return signals

def _soft_signals(tok: str) -> list[str]:
    """Weaker, ambiguous signals -> warn, not categorical."""
    signals = []
    letters = [c for c in tok if c.isalpha()]
    if len(letters) < 5:
        return signals
    vowel_ratio = sum(1 for c in letters if c in _VOWELS) / len(letters)
    if 0.12 <= vowel_ratio < 0.20:                    # low but not impossible
        signals.append("low-vowel-ratio")
    # Mixed case mid-word (not camelCase identifier, not all-caps acronym)
    inner = tok[1:-1]
    if any(c.isupper() for c in inner) and any(c.islower() for c in inner) \
       and not re.match(r"^[A-Za-z]+\d", tok):
        signals.append("erratic-casing")
    return signals
```

```python
def check_garbled_text(root: ET.Element) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    void_hits: list[tuple[str, str, list[str]]] = []   # (loc, token, signals)
    soft_hits: list[tuple[str, str, list[str]]] = []

    for el, tag in _iter_elements(root):
        if tag not in ("text", "tspan"):
            continue
        # tspans nested in a text contribute their own .text; iterating both
        # is intentional (matplotlib splits runs across tspans). De-dup is not
        # needed: a void run flags wherever it physically lives.
        content = (el.text or "")
        if not content.strip():
            continue
        loc = el.attrib.get("id") or f"<{tag}>"
        for tok in _tokenize_label(content):
            if _is_allowed_token(tok):
                continue
            void = _void_signals(tok)
            if void:
                void_hits.append((loc, tok, void))
                continue
            soft = _soft_signals(tok)
            if soft:
                soft_hits.append((loc, tok, soft))

    for loc, tok, sig in void_hits:
        findings.append(_finding(
            check="garbled_text",
            severity="categorical",
            principle_ref="ai_figure_slop.md§1",
            message=(
                f"Label token {tok!r} is lexically void ({', '.join(sig)}). "
                "Letter-shaped but not a real word/term/unit — the strongest "
                "AI-generation tell (Frontiers rat genre). Retype the label "
                "from the source data; do not regenerate the image."
            ),
            location=loc,
        ))
    for loc, tok, sig in soft_hits:
        findings.append(_finding(
            check="garbled_text",
            severity="warn",
            principle_ref="ai_figure_slop.md§1",
            message=(
                f"Label token {tok!r} is borderline implausible ({', '.join(sig)}). "
                "Likely a typo or an unusual identifier — confirm against source data."
            ),
            location=loc,
        ))

    if not findings:
        findings.append(_finding(
            check="garbled_text",
            severity="pass",
            principle_ref="ai_figure_slop.md§1",
            message="All <text>/<tspan> tokens are plausible words, terms, units, or identifiers.",
        ))
    return findings
```

### Severity

- **`categorical`** when ≥1 token trips a `_void_signals` rule (mixed-script, unnamed-glyph, stacked-diacritics, no-vowels, consonant-run, letter-pileup). Dominates the verdict.
- **`warn`** for `_soft_signals` (low-vowel-ratio, erratic-casing) — ambiguous, two-sided.
- **`pass`** when clean.

### Pytest cases (`tests/test_check_garbled_text.py`)

```python
WRAP = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{}</svg>'

def _run(inner):
    root = ET.fromstring(WRAP.format(inner))
    return check_garbled_text(root)

def test_void_frontiers_token_is_categorical():
    # "Tramioncatiion" — letter-pileup + consonant patterns
    f = _run('<text>Tramioncatiion of cells</text>')
    assert any(x["severity"] == "categorical" for x in f)

def test_mixed_script_is_categorical():
    # Latin 'dis' + Cyrillic 'о' lookalikes inside one token
    f = _run('<text>di\u0455l\u043esttal</text>')   # ѕ + о (Cyrillic) in a Latin run
    assert any(x["severity"] == "categorical" and "mixed-script" in x["message"] for x in f)

def test_gene_symbols_and_pvalues_pass():
    f = _run('<text>TP53</text><text>JAK2</text><text>p&lt;0.05</text><text>CD4</text>')
    assert all(x["severity"] == "pass" for x in f)

def test_units_and_ranges_pass():
    f = _run('<text>60%</text><text>0-100</text><text>kDa</text><text>µL</text><text>1.2e-3</text>')
    assert all(x["severity"] == "pass" for x in f)

def test_greek_and_short_ticks_pass():
    f = _run('<text>\u03b1</text><text>\u0394\u0394Ct</text><text>log</text><text>A</text>')
    assert all(x["severity"] == "pass" for x in f)

def test_consonant_scramble_is_categorical():
    f = _run('<text>dssilcedwxz</text>')   # no-vowels + consonant-run
    assert any(x["severity"] == "categorical" for x in f)

def test_real_sentence_passes():
    f = _run('<text>Treatment reduced tumor volume by 60 percent</text>')
    assert all(x["severity"] == "pass" for x in f)
```

### Limitations note (append to module docstring "Limitations")

> `check_garbled_text` is dictionary-free and heuristic. It will (a) miss a void label that happens to have a natural vowel ratio and a plausible script, and (b) risk false positives on long agglutinated chemical names (e.g. IUPAC strings) and on non-English-but-real terms. The allowlist (`_ALLOW_WORDS`, `_ALLOW_TOKEN_PATTERNS`) is the tuning surface; extend it rather than loosening the thresholds. CRISPR (6 consonants) is deliberately below the `consonant-run >= 7` floor.

---

## 2. `check_default_palette_fingerprint` — tool-default color sequences as data colours

Graded/soft tell (regression-to-mean, Dimension 6.2). **Two-sided** per Guardrail 2: a matching *brand* colour is fine, so this check **defers to the palette** — if `--tokens` is supplied and the hex is in-palette, it is **not** flagged (no double-report with `check_palette_compliance`).

### Constants

```python
# --- check_default_palette_fingerprint ---------------------------------------
# matplotlib tab10 (the default prop_cycle) — the single most common AI/default
# fingerprint. Stored uppercase, 6-hex.
_TAB10 = [
    "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
    "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF",
]
# Other tool defaults worth fingerprinting (kept small + high-precision).
_TOOL_DEFAULTS = {
    "matplotlib tab10": _TAB10,
    # Excel 2016 default series colors:
    "excel": ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5", "#70AD47"],
    # D3 / Chart.js category10 shares tab10 hexes; covered by _TAB10.
    # seaborn "deep":
    "seaborn deep": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"],
}
# A run is "fingerprinted" only if >=3 distinct hexes from one sequence appear,
# in any order — 1-2 collisions are coincidence, not a fingerprint.
_FINGERPRINT_MIN_HITS = 3
```

### Signature

```python
def check_default_palette_fingerprint(
    root: ET.Element, palette: set[str] | None
) -> list[dict[str, Any]]:
    """Flag tool-default color sequences (matplotlib tab10, Excel, seaborn)
    used as data colours (ai_figure_slop.md §2).

    A regression-to-mean 'default-distribution look' tell — SOFT and two-sided:
    a default hex that is ALSO a brand colour is legitimate, so any hex present
    in `palette` is exempt (this is what keeps it from double-reporting with
    check_palette_compliance). Fires only when >=3 distinct hexes from one
    known default sequence co-occur, which a coincidental brand match won't do.
    """
```

### Algorithm

```python
def check_default_palette_fingerprint(root, palette):
    # Collect the set of normalized hexes actually used (reuse the existing
    # normalization the palette check applies).
    used: set[str] = set()
    for el, attr, val in _collect_color_values(root):
        m = re.match(r"^#([0-9A-Fa-f]{3,8})$", val.strip())
        if not m:
            continue
        h = val.strip().upper()
        if len(h) == 4:                       # #RGB -> #RRGGBB
            h = "#" + "".join(c * 2 for c in h[1:])
        if len(h) == 9:                       # strip alpha
            h = h[:7]
        used.add(h)

    findings: list[dict[str, Any]] = []
    brand = palette or set()

    for seq_name, seq in _TOOL_DEFAULTS.items():
        seq_set = set(seq)
        hits = used & seq_set
        # Two-sided exemption: hexes that are ALSO brand colours don't count
        # toward the fingerprint (a same-hue brand match is legitimate).
        non_brand_hits = hits - brand
        if len(non_brand_hits) >= _FINGERPRINT_MIN_HITS:
            findings.append(_finding(
                check="default_palette_fingerprint",
                severity="warn",
                principle_ref="ai_figure_slop.md§2",
                message=(
                    f"{len(non_brand_hits)} colours match the '{seq_name}' default "
                    f"sequence ({sorted(non_brand_hits)}). Reads as untouched tool/"
                    "model default ('Default Syndrome'). SOFT signal — fine if a "
                    "value coincides with a brand colour, but a full default run "
                    "should be re-mapped to the brand palette."
                ),
                location="<document colours>",
            ))

    if not findings:
        findings.append(_finding(
            check="default_palette_fingerprint",
            severity="pass",
            principle_ref="ai_figure_slop.md§2",
            message="No tool-default colour sequence (tab10/Excel/seaborn) detected as a data palette.",
        ))
    return findings
```

### Severity

- **`warn`** only (graded, decaying, false-positive-prone, two-sided). Never `fail`/`categorical`. Honors Guardrail 2's down-weighting of aesthetic signals.

### Reconciliation with `check_palette_compliance` (no double-report)

- `check_palette_compliance` fires `fail` per **off-palette** hex.
- `check_default_palette_fingerprint` fires `warn` only for a **default-sequence run**, and **subtracts brand hexes** before counting. The two never describe the same hex with two findings of differing intent: an off-palette tab10 hex gets one `fail` (palette) + contributes to one aggregate `warn` (fingerprint, run-level not per-hex), which is the intended layered signal (off-palette *and* it's a recognizable default), not a duplicate. An in-palette hex is exempt from the fingerprint entirely.

### Pytest cases

```python
def _runp(inner, palette=None):
    root = ET.fromstring(WRAP.format(inner))
    return check_default_palette_fingerprint(root, palette)

def test_three_tab10_hexes_warn():
    inner = ('<rect fill="#1f77b4"/><rect fill="#ff7f0e"/><rect fill="#2ca02c"/>')
    f = _runp(inner)
    assert any(x["severity"] == "warn" and "tab10" in x["message"] for x in f)

def test_two_tab10_hexes_pass():
    inner = '<rect fill="#1f77b4"/><rect fill="#ff7f0e"/>'
    f = _runp(inner)
    assert all(x["severity"] == "pass" for x in f)   # below 3-hit floor

def test_tab10_hexes_in_brand_palette_are_exempt():
    inner = '<rect fill="#1f77b4"/><rect fill="#ff7f0e"/><rect fill="#2ca02c"/>'
    # All three declared as brand colours -> not a fingerprint.
    f = _runp(inner, palette={"#1F77B4", "#FF7F0E", "#2CA02C"})
    assert all(x["severity"] == "pass" for x in f)

def test_excel_default_run_warns():
    inner = '<rect fill="#4472C4"/><rect fill="#ED7D31"/><rect fill="#A5A5A5"/>'
    f = _runp(inner)
    assert any(x["severity"] == "warn" and "excel" in x["message"].lower() for x in f)

def test_clean_brand_only_passes():
    inner = '<rect fill="#2DB2E8"/><rect fill="#E8622D"/><rect fill="#1B2A4A"/>'
    f = _runp(inner)
    assert all(x["severity"] == "pass" for x in f)
```

### Limitations note

> Fingerprints are exact-hex and short by design (high precision, low recall). A figure that nudges tab10 by one digit, or uses a model default not in `_TOOL_DEFAULTS`, will pass. This is intentional: the report classifies palette as the *weakest, decaying* discriminator, so we accept misses to avoid false positives. The `_FINGERPRINT_MIN_HITS = 3` floor is provisional/uncalibrated.

---

## 3. `check_raw_index_labels` — axis tick labels that are bare sequential integers

Soft tell (Dimension 2.3): ticks rendered as `0,1,2,3…` or `1,2,3…` where **categorical** labels were expected (LLM emitted positional index instead of the category name).

### Constants

```python
# --- check_raw_index_labels --------------------------------------------------
# Minimum run length before a monotone integer sequence is suspicious. A 3-tick
# 0/1/2 is common on a real numeric axis; 5+ consecutive 0..n indices is the tell.
_INDEX_MIN_RUN = 5
```

### Signature

```python
def check_raw_index_labels(root: ET.Element) -> list[dict[str, Any]]:
    """Detect tick labels that are bare sequential integers (0,1,2,... or
    1,2,3,...) where categorical labels were likely intended
    (ai_figure_slop.md §3).

    SOFT signal: an LLM that lost the category names emits the positional
    index instead. False-positive guarded by requiring (a) a long consecutive
    run, (b) an exact step of 1 starting at 0 or 1, and (c) ALL such labels
    being pure small integers with no axis-title-like numeric companions
    (decimals, units, negatives, large magnitudes) that would indicate a
    genuine numeric axis.
    """
```

### Algorithm

The heuristic exploits a structural fact we already hold in the SVG: tick labels are short standalone `<text>` runs of pure integers. We gather all integer-only label tokens, then test whether they form a clean `0..n` / `1..n` index run **and** the figure shows no signs of a real numeric axis.

```python
def check_raw_index_labels(root: ET.Element) -> list[dict[str, Any]]:
    int_labels: list[int] = []
    has_real_numeric_signal = False

    for el, tag in _iter_elements(root):
        if tag != "text":          # tick labels are <text>; skip <tspan> runs
            continue
        raw = (el.text or "").strip()
        if not raw:
            continue
        # Pure small non-negative integer? -> candidate index label.
        if re.fullmatch(r"\d{1,3}", raw):
            int_labels.append(int(raw))
            continue
        # Any of these means a genuine numeric/continuous axis is present:
        #   decimals, negatives, thousands separators, units, scientific notation,
        #   large magnitudes -> suppress the index heuristic for the whole figure.
        if re.search(r"[.\-–%]|,\d{3}|[eE][+\-]?\d|\d{4,}", raw):
            has_real_numeric_signal = True

    findings: list[dict[str, Any]] = []

    if has_real_numeric_signal or len(int_labels) < _INDEX_MIN_RUN:
        findings.append(_finding(
            check="raw_index_labels",
            severity="pass",
            principle_ref="ai_figure_slop.md§3",
            message="No bare sequential-index tick labels detected (or axis is genuinely numeric).",
        ))
        return findings

    seq = sorted(set(int_labels))
    starts_at_index = seq[0] in (0, 1)
    is_consecutive = seq == list(range(seq[0], seq[0] + len(seq)))
    # A real numeric axis with integer ticks usually steps by >1 (0,5,10) or
    # spans a wider range; the index tell is a *dense* 0/1.. run.
    if starts_at_index and is_consecutive and len(seq) >= _INDEX_MIN_RUN:
        findings.append(_finding(
            check="raw_index_labels",
            severity="warn",
            principle_ref="ai_figure_slop.md§3",
            message=(
                f"Axis tick labels are a bare consecutive index run {seq[0]}..{seq[-1]} "
                f"({len(seq)} ticks, step 1). If these mark categories, the category "
                "names were likely dropped and replaced by positional indices — a "
                "Class-B AI tell. Replace with the real category labels. (SOFT: ignore "
                "if the axis is genuinely an integer count.)"
            ),
            location="<axis tick labels>",
        ))
    else:
        findings.append(_finding(
            check="raw_index_labels",
            severity="pass",
            principle_ref="ai_figure_slop.md§3",
            message="Integer tick labels present but not a dense 0/1-based index run; treated as a numeric axis.",
        ))
    return findings
```

### Severity

- **`warn`** only. Soft signal; never dominates.

### False-positive controls (as required)

1. **Run length** `_INDEX_MIN_RUN = 5` — a 0/1/2 three-tick axis is common and not flagged.
2. **Real-numeric suppression** — any label with a decimal, negative, unit, thousands-sep, sci-notation, or 4+ digit magnitude flips `has_real_numeric_signal` and the whole check passes (the figure has a genuine numeric axis).
3. **Step-1 + 0/1 start required** — `0,5,10,15,20` or `2,4,6,8,10` (real numeric ticks) are *not* a dense index run and pass.

### Pytest cases

```python
def _runi(inner):
    root = ET.fromstring(WRAP.format(inner))
    return check_raw_index_labels(root)

def test_index_run_zero_based_warns():
    inner = "".join(f'<text>{i}</text>' for i in range(0, 6))   # 0..5
    f = _runi(inner)
    assert any(x["severity"] == "warn" for x in f)

def test_index_run_one_based_warns():
    inner = "".join(f'<text>{i}</text>' for i in range(1, 7))   # 1..6
    f = _runi(inner)
    assert any(x["severity"] == "warn" for x in f)

def test_short_run_passes():
    inner = '<text>0</text><text>1</text><text>2</text>'        # 3 ticks
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)

def test_numeric_axis_with_decimals_passes():
    inner = '<text>0.0</text><text>0.5</text><text>1.0</text><text>1.5</text><text>2.0</text>'
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)

def test_step_five_integer_axis_passes():
    inner = '<text>0</text><text>5</text><text>10</text><text>15</text><text>20</text>'
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)

def test_categorical_labels_present_passes():
    inner = '<text>Control</text><text>Low</text><text>Med</text><text>High</text>'
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)
```

### Limitations note

> `check_raw_index_labels` cannot know the *intended* axis semantics from the SVG alone, so it errs toward silence: it only fires on a dense, step-1, 0/1-based run with no competing numeric signal. It will miss an index run that legitimately also looks like a count, and will not fire on a *partial* category drop (some names kept, some indexed). For our own generated figures the stronger guarantee is upstream — the plotting code holds the category list — so this is a backstop, not the primary defense.

---

## 4. Wiring into `run_checks` and the severity/`overall` change

### 4a. The new `"categorical"` severity (required by Guardrail 2)

`run_checks` currently computes `overall = "fail" if fail_count > 0 else "pass"` and a summary of `fail/warn/pass`. Add `categorical` as a first-class, dominant severity.

**Edit the summary counters** (near the existing `fail_count = sum(...)` block):

Insert this line next to the existing counters:
```python
    categorical_count = sum(1 for f in findings if f["severity"] == "categorical")
```
near the surrounding line:
> `fail_count = sum(1 for f in findings if f["severity"] == "fail")`

**Edit `overall`** — replace the surrounding line:
> `"overall": "fail" if fail_count > 0 else "pass",`

with:
```python
        "overall": "fail" if (fail_count > 0 or categorical_count > 0) else "pass",
```
and add `"categorical_count": categorical_count` to the `summary` dict next to:
> `"fail_count": fail_count,`

This keeps the VECTOR intact (every sub-score keeps its own severity), surfaces `categorical` distinctly so it can DOMINATE, and never collapses to a composite number — honoring both guardrails.

### 4b. The three `findings.extend(...)` lines

Insert these immediately after the existing line:
> `findings.extend(check_palette_compliance(root, palette))`

```python
    findings.extend(check_garbled_text(root))
    findings.extend(check_default_palette_fingerprint(root, palette))
    findings.extend(check_raw_index_labels(root))
```

(`check_default_palette_fingerprint` takes `palette`, which is already in scope as the local `palette = load_palette(...)`; placing it right after `check_palette_compliance` keeps the two palette-aware checks adjacent and makes the no-double-report relationship obvious to a reader.)

### 4c. CLI / exit codes

No CLI change needed. `main()` returns `0 if result["overall"] == "pass" else 1`; since `overall` now flips to `"fail"` on any `categorical`, a garbled-text categorical hit correctly yields exit 1.

---

## 5. The new reference doc `ai_figure_slop.md` (section anchors the checks point at)

Ship `skills/svg-figure-maker/references/ai_figure_slop.md` with three `§` sections so the `principle_ref` keys resolve. Skeleton (ready to write):

```markdown
# AI figure-slop tells — deterministic SVG checks (Track B)

> We GENERATE these figures, so we hold the ground-truth data and source SVG.
> These checks read text/colour we already have — no OCR, no image recovery.
> Emit a VECTOR of severities; categorical tells DOMINATE; aesthetic tells are
> WEAK, down-weighted, and TWO-SIDED. All thresholds are PROVISIONAL/UNCALIBRATED.
> Never strip decoration to "pass" — over-minimization is itself a failure (Bateman CHI2010).

## §1 Garbled / lexically-void label text  ⚑ categorical
The #1 tell (Frontiers rat: "diƨlocttal", "Tramioncatiion"). Maps to rubric 1.1/1.2.
Heuristic: charset-mixing, vowel ratio, consonant-run, letter-pileup, invented
diacritics, over a unit/term/identifier allowlist. Void -> `categorical`; ambiguous -> `warn`.

## §2 Default-palette fingerprint  (soft, two-sided)
matplotlib tab10 / Excel / seaborn defaults appearing as data colours. Maps to rubric 6.2.
SOFT/`warn` only; brand-colour matches are EXEMT; fires on a >=3-hex default run.

## §3 Raw-index axis labels  (soft)
Bare sequential integers (0,1,2.. / 1,2,3..) where categories were expected. Maps to rubric 2.3.
SOFT/`warn`; suppressed when any genuine numeric-axis signal (decimals/units/negatives/step>1) present.
```

---

## 6. Cross-cutting limitations block (append verbatim to the module docstring)

```text
AI-figure-slop checks (v0.1, PROVISIONAL — uncalibrated thresholds):
    - These three checks (garbled_text, default_palette_fingerprint,
      raw_index_labels) read only text/colour already in the SVG; they do NOT
      perform OCR or image recovery. They are reliable for OUR generated output
      because we hold the source; they are NOT a forensic detector for inbound
      third-party images (that is Track D, advisory only).
    - Output is a VECTOR of per-check severities. The "categorical" severity is
      the ONLY dominant one and corresponds to the strongest tell (void labels).
      Default-palette and raw-index are deliberately SOFT and TWO-SIDED: a
      brand-matching default colour or a genuine integer axis is legitimate.
    - Do NOT "fix" a default-palette or decoration warning by stripping ink or
      flattening style — over-minimization is itself a regression-to-mean
      failure (Bateman et al., CHI 2010). Re-map to the brand palette instead.
```

---

## 7. Adjacent pointer fix (flagged in the brief, one line)

`skills/shared/references/pre_submission_checklist.md` items #13/#14 + the tooling table point at `validate_figure.py` for `check_continuous_as_bars` / `check_riskratio_as_bars`, but those live in `validate_data.py`. Not part of `preflight_check.py`, but it sits in the same gate this work feeds; fix the pointer in that file when you apply this spec (change the referenced filename from `validate_figure.py` to `validate_data.py` for those two function names).

---

## Summary of files to touch

- **`skills/svg-figure-maker/scripts/preflight_check.py`** — add 3 module constants blocks + `import unicodedata, string`; add 3 `check_*` functions (+ 5 helper functions for garbled-text); add 3 `findings.extend(...)` lines after `check_palette_compliance`; add `categorical_count` to summary and to the `overall` test.
- **`skills/svg-figure-maker/references/ai_figure_slop.md`** — NEW, 3 `§` sections (skeleton above).
- **`skills/svg-figure-maker/scripts/tests/test_check_garbled_text.py`**, **`…/test_check_default_palette_fingerprint.py`**, **`…/test_check_raw_index_labels.py`** — NEW (cases above); `tests/` dir does not yet exist for this script.
- **`skills/svg-figure-maker/references/anti_patterns.md`** — extend the **Severity map** table with the three new rows (`garbled_text → categorical`, `default_palette_fingerprint → warn`, `raw_index_labels → warn`) and note `categorical` as a new severity above `fail`.
- **`skills/shared/references/pre_submission_checklist.md`** — fix the `validate_figure.py` → `validate_data.py` pointer for `check_continuous_as_bars`/`check_riskratio_as_bars` (adjacent-gate cleanup).

Run with `uv run python skills/svg-figure-maker/scripts/tests/...` per the PEP-723 self-bootstrap convention (no root pyproject).