# Oligon Medium Playbooks & Asset Conventions

Per-medium specifications for applying the Oligon visual system.
Source: Oligon Digital Style Guide v2.3, §11 (Medium Playbooks) and
§12 (Asset Specs & File Naming).

Every playbook here **inherits** tokens from `brand-colors-full.md`
(ramps, semantic tokens), typography from that file's §5, and voice
rules from `voice_and_copy.md`. Playbooks do not redefine visual
specifications — they describe how to render the system at each
medium's dimensions and conventions.

---

## 1. LinkedIn & X

### Single-image post

| Parameter        | Specification |
|------------------|---------------|
| Square format    | 1200 × 1200 px |
| Landscape format | 1200 × 628 px |
| Background       | `blue.900` `#001A2E` (dark theme) |
| Headline         | H2-equivalent at display size, 6–12 words, sentence case |
| Eyebrow          | H3 (category only — `PLATFORM SPOTLIGHT`, `PIPELINE UPDATE`) |
| Logo placement   | Bottom-left or bottom-right, Brand Blue wordmark |
| CTA inside image | None — CTA lives in post body |

### Carousel

| Parameter      | Specification |
|----------------|---------------|
| Format         | 1080 × 1350 px, 5–10 slides |
| Slide 1        | Hook — eyebrow + headline only, no body |
| Slides 2–N     | One claim per slide — eyebrow, headline, ≤30 words body |
| Final slide    | "Learn more at oligon.com" + wordmark, Brand Blue ground |

### Post body copy

| Parameter         | Specification |
|-------------------|---------------|
| First two lines   | Must hook before LinkedIn's "…see more" truncation (~210 characters) |
| Total length      | 800–1,300 characters; line breaks for scannability |
| Hashtags (LinkedIn) | 3–5 at end: `#RNAtherapeutics #oncology #immunology #drugdiscovery #biotech` |
| Hashtags (X)      | 1–2 maximum — more suppress reach |
| Links             | One per post |

---

## 2. Websites & Landing Pages

### Program landing-page section order

1. **Hero** — video or dark-theme image; H3 eyebrow + H1 + short lede
   + primary button (`blue.700`)
2. **At-a-glance feature tiles** — 3- or 4-up grid
3. **Mechanism section** — diagram + H2 explainer
4. **Proof block** — quote, stat grid, or trial data
5. **Pipeline context** — where this program fits in the six-program roster
6. **Closing CTA block**

### Funnel / lead-gen page variant

| Constraint        | Specification |
|-------------------|---------------|
| Hero              | Solid `blue.900` or tight image — no video, to minimize load |
| Form placement    | Inline email capture above the fold |
| Page length       | < 4 viewport scrolls on desktop |
| CTA variety       | Single primary button style, repeated; no competing CTA styles |

---

## 3. Presentations

### Investor & scientific deck structure

| Slide type          | Specification |
|---------------------|---------------|
| Cover               | `blue.900` full-bleed; H3 eyebrow (e.g. `INVESTOR UPDATE — Q2 2026`); H1 title (28 pt); wordmark bottom-right |
| Section divider     | `blue.900`; H3 eyebrow + H1 only, no body |
| Content slide       | White ground; H3 eyebrow + H2 title; content area |
| Data slide          | White ground; H3 eyebrow + H2 title; figure per brand-colors-full.md §3–§6 at 300 dpi |
| Quote slide         | `blue.900`; oversized quotation mark in Brand Blue at 0.25 opacity; display-size quote; attribution |
| Closing / contact   | `blue.900`; CTA text; wordmark; contact email |

### Projection typography minimums

Body 18 pt, heading 28 pt, axis labels on embedded figures 18 pt.
Never use caption size (11 pt) on projected slides. If a data figure's
axis labels are below 18 pt at projected scale, relabel them natively
in PowerPoint or scale the figure up before exporting.

### Figure integration

Data figures come from matplotlib or ggplot2. **Do not re-style them
inside PowerPoint** — export at 300 dpi PNG or SVG and drop in. The
unified Arial / DejaVu Sans typography means figures render
consistently alongside slide titles.

### Slide-title headline rule

Make the slide title a full-sentence declarative takeaway, not a topic
label. The title should carry the finding in words so a reader who
never hears the presenter can reconstruct the argument from titles
alone. See `voice_and_copy.md` §4.4 for examples and exceptions.

### Persistent footer & confidentiality

Every content slide after the cover carries footer content set at the
Slide Master so it cannot be removed on individual slides. Exact
content varies by audience.

| Deck audience           | Footer line | Slide number |
|-------------------------|-------------|--------------|
| Investor / BD           | `Confidential — Do Not Distribute`, `neutral.600`, 10 pt | Bottom-right, `neutral.600`, 10 pt |
| Scientific Advisory Board | `Confidential — SAB use only`, optional per-advisor watermark at `neutral.200` | Bottom-right, `neutral.600`, 10 pt |
| Conference / seminar    | Embargo line if data is pre-publication; otherwise empty | Bottom-right, `neutral.600`, 10 pt |
| KOL / medical education | MLR job code `US-OLIGON-123456 MM/YYYY` with expiration | Bottom-right, `neutral.600`, 10 pt |
| Internal review         | Document control line with version and date if regulated; otherwise empty | Bottom-right, `neutral.600`, 10 pt |

> **Set at the master.** Footer text placed on individual slides will
> drift — a collaborator will delete or overwrite it. Enter the footer
> via `Insert > Header & Footer` applied to all slides, or edit the
> Slide Master directly. Apply `Home > Reset` to any slide where the
> footer has disappeared.

---

## 4. Email Funnels

### Template structure

| Element              | Specification |
|----------------------|---------------|
| Template width       | 600 px max |
| Header               | White ground, 48 px height, Brand Blue wordmark |
| Hero block           | H2 title + body paragraph + single primary button (`blue.700`) |
| Body                 | 2–3 short sections, each H3 eyebrow + ≤3 sentences |
| Footer               | `neutral.50` ground; contact line; unsubscribe link; physical address (regulatory) |
| Body length          | ≤200 words |
| CTAs per email       | One; repeat once at bottom if body > 150 words |
| Background images    | Disallowed — inconsistent rendering across clients |
| Plain-text fallback  | Says the same thing, in the same order |

### Subject line rules

- 30–50 characters
- Concrete subject, no curiosity-gap tricks
- Action or newsworthy anchor preferred

| Do | Don't |
|----|-------|
| New preprint: SeekR bridge architecture | You won't believe what we just discovered |

---

## 5. Posters & Print

Poster-specific layout and print guidance live in the
`research-posters/` skill (Oligon-branded templates) and the
`venue-templates/` skill (per-conference size specs). This reference
does not duplicate those — follow the color, typography, and figure-
integrity rules from `brand-colors-full.md` and apply them at poster
scale.

Printing notes:

- CMYK conversion required for offset print; review proof before
  reproduction.
- 300 dpi minimum at final print size (600 dpi for line art).
- Bleed and safe margins per venue print spec.
- QR codes should be tested with ≥ 2 scanner apps before submission.

---

## 6. File Naming

Pattern:

```
oligon_[asset-type]_[topic]_[variant]_v[N]_[YYYY-MM].[ext]
```

The `v[N]` segment is required. Iterate by bumping `v1 → v2 → v3`
and preserve prior versions until explicitly retired — never
overwrite a prior version, even for changes that feel trivial.
Year-month alone cannot disambiguate two iterations in the same month.

### Examples

| Filename | Asset type |
|----------|------------|
| `oligon_social_seekr-mechanism_li-square_v1_2026-04.png` | LinkedIn square social tile |
| `oligon_deck_investor-q1_master_v3_2026-04.pptx`         | Investor presentation, third iteration |
| `oligon_landing_ctla4-program_hero_v2_2026-04.jpg`       | Landing page hero image, second iteration |
| `oligon_email_aimed25-invite_html_v1_2026-04.html`       | Email funnel asset |
| `oligon_figure_km-survival_fig3_v1_2026-04.svg`          | Scientific figure |

### Required source files

Every asset delivered under this guide ships with:

1. The final rendered output (`.png` / `.pdf` / `.mp4`)
2. Editable source (`.figma` / `.psd` / `.indd` / `.pptx` / `.html`)
3. A one-line token manifest stating which semantic tokens and type
   roles the asset consumes

---

## 7. Asset Repository Structure

| Asset type                       | Location |
|----------------------------------|----------|
| Wordmark and icon                | SharePoint › Brand › Logos |
| Color swatches (`.ase`)          | SharePoint › Brand › Swatches |
| Presentation template (`.potx`)  | SharePoint › Organization Assets Library |
| Word template (`.dotx`)          | SharePoint › Organization Assets Library |
| Figma library                    | To be established |
| Scientific figure skill (this repo) | `skills/oligon-brand/` |

---

## Cross-references

- Brand palette + typography + figure standards:
  `references/brand-colors-full.md`
- Voice, messaging, copy patterns, glossary:
  `references/voice_and_copy.md`
- Scientific figure code:
  `plotting-libraries/` (consumes oligon-brand adapters)
- Poster templates and layouts:
  `research-posters/`
- Slide templates:
  `scientific-slides/`
