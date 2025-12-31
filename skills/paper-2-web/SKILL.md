---
name: paper-2-web
version: 2.1.0
description: "Transform academic papers into promotional formats: interactive websites (Paper2Web), presentation videos (Paper2Video), and conference posters (Paper2Poster)"
when_to_use: "Creating conference materials (posters, videos, companion websites), promoting published papers or preprints, generating video abstracts, creating interactive research homepages, batch processing papers for dissemination"
allowed-tools: [Read, Write, Edit, Bash]
---

# Paper2All: Academic Paper Transformation Pipeline

<overview>
Transform academic papers (LaTeX or PDF) into three promotional formats using the Paper2All autonomous pipeline:
1. **Paper2Web**: Interactive, explorable academic homepages
2. **Paper2Video**: Professional presentation videos with narration
3. **Paper2Poster**: Print-ready conference posters

The pipeline uses LLM-powered content extraction and iterative refinement to create high-quality outputs for conferences, journals, and academic promotion.
</overview>

<prerequisites>
## Prerequisites

Before using this skill, ensure:

| Requirement | Details | Verification |
|-------------|---------|--------------|
| Paper2All repository | Clone from GitHub | `ls Paper2All/pipeline_all.py` |
| Python 3.11+ | With conda environment | `python --version` |
| API keys | OpenAI or OpenRouter configured | Check `.env` file |
| LibreOffice | Document conversion | `libreoffice --version` |
| Poppler utilities | PDF processing | `pdftoppm -v` |
| NVIDIA GPU (optional) | 48GB for talking-head video | `nvidia-smi` |

**Quick Setup:**
```bash
git clone https://github.com/YuhangChen1/Paper2All.git && cd Paper2All
conda create -n paper2all python=3.11 && conda activate paper2all
pip install -r requirements.txt
```

See `{baseDir}/references/installation.md` for complete installation guide.
</prerequisites>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Creating conference materials (posters, videos, companion websites)
- Promoting published papers or preprints
- Generating video abstracts from paper content
- Creating interactive homepages for research
- Batch processing multiple papers for dissemination

Do NOT use this skill when:
- Converting documents to Markdown → use `markitdown`
- Writing the paper itself → use `scientific-writing`
- Creating presentation slides manually → use `scientific-slides`
- Generating standalone images → use `generate-image` or `scientific-schematics`
</when_to_use>

<decision_framework>
## Output Selection

```
What promotional material is needed?
│
├─ Need permanent online presence?
│  └─→ Paper2Web (interactive website)
│       └─ Time: 15-30 min, Cost: $0.50-2.00
│
├─ Need physical conference materials?
│  │
│  ├─ Poster session?
│  │  └─→ Paper2Poster
│  │       └─ Time: 10-20 min, Cost: $0.30-1.00
│  │
│  └─ Oral presentation?
│     └─→ Paper2Video
│          └─ Time: 20-60 min, Cost: $1.00-3.00
│
├─ Need video content?
│  │
│  ├─ Journal video abstract (5-10 min)?
│  │  └─→ Paper2Video (standard)
│  │
│  ├─ Conference talk (15-20 min)?
│  │  └─→ Paper2Video (extended)
│  │
│  └─ Social media (1-3 min)?
│     └─→ Paper2Video (short)
│
└─ Need complete package?
   └─→ Generate all three: Website + Poster + Video
        └─ Time: 45-90 min, Cost: $2.00-6.00
```

## Component Selection Matrix

| Use Case | Website | Poster | Video | Priority |
|----------|---------|--------|-------|----------|
| Conference (oral) | Optional | No | Yes | Video first |
| Conference (poster) | Optional | Yes | Optional | Poster first |
| Journal publication | Yes | No | Optional | Website first |
| Preprint promotion | Yes | No | Yes | Both |
| Lab website | Yes | No | No | Website only |
| Social media | Optional | No | Yes (short) | Video first |

## Model Selection

| Quality Need | Model | Cost | Use When |
|--------------|-------|------|----------|
| Production | GPT-4 | $$ | Conferences, publications |
| Best quality | GPT-4.1 | $$$ | High-stakes venues |
| Quick draft | GPT-3.5-turbo | $ | Testing, simple papers |

</decision_framework>

<workflow>
## Transformation Workflow

### Stage 1: Input Preparation

**Objective:** Verify source material and select outputs

**Steps:**
1. Identify input format (LaTeX preferred, PDF acceptable)
2. Verify all source files present (figures, bibliography)
3. Select target outputs from decision tree
4. Configure API keys and dependencies

**Input Requirements:**

| Format | Structure | Quality Notes |
|--------|-----------|---------------|
| LaTeX | `main.tex`, `figures/`, `*.bib` | Best extraction |
| PDF | High-quality, selectable text | Good extraction |
| PDF (scanned) | 300+ DPI images | Requires OCR |

**Exit Criteria:**
- [ ] Input format verified (LaTeX or PDF)
- [ ] All figures accessible (300+ DPI for poster)
- [ ] Bibliography file present (for citations)
- [ ] Target outputs selected (website/poster/video)
- [ ] API keys configured in `.env`

---

### Stage 2: Environment Setup

**Objective:** Configure Paper2All pipeline

**Steps:**
1. Clone and install Paper2All
2. Configure environment variables
3. Install system dependencies
4. Verify GPU availability (if using talking-head)

**Installation:**
```bash
git clone https://github.com/YuhangChen1/Paper2All.git
cd Paper2All
conda create -n paper2all python=3.11
conda activate paper2all
pip install -r requirements.txt
```

**Environment Configuration:**
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=optional_for_logo_search
GOOGLE_CSE_ID=optional_for_logo_search
```

**System Dependencies:**
- LibreOffice (document conversion)
- Poppler utilities (PDF processing)
- NVIDIA GPU 48GB (optional, talking-head only)

**Exit Criteria:**
- [ ] Paper2All installed and importable
- [ ] API keys in `.env` file
- [ ] System dependencies verified
- [ ] GPU check passed (if using talking-head)

**Error Handling:**

| Error | Cause | Resolution |
|-------|-------|------------|
| `ModuleNotFoundError` | Dependencies missing | Run `pip install -r requirements.txt` |
| `libreoffice: command not found` | LibreOffice not in PATH | Install LibreOffice; add to PATH |
| `pdftoppm: command not found` | Poppler missing | Install poppler-utils (apt) or poppler (brew) |
| `CUDA not available` | GPU drivers/CUDA issue | Update NVIDIA drivers; use `pipeline_light.py` |

---

### Stage 3: Content Generation

**Objective:** Execute selected pipeline components

**Steps:**
1. Run pipeline with selected components
2. Monitor progress and handle errors
3. Verify intermediate outputs

**Command Templates:**

**All Components:**
```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1
```

**Website Only:**
```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-website
```

**Poster with Custom Size:**
```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches 60 \
  --poster-height-inches 40
```

**Video (lightweight):**
```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir "path/to/output" \
  --paper_latex_root "path/to/paper"
```

**Exit Criteria:**
- [ ] Pipeline completed without errors
- [ ] Output files generated in expected locations
- [ ] No API errors or rate limits hit
- [ ] Intermediate files preserved for debugging

**Error Handling:**

| Error | Cause | Resolution |
|-------|-------|------------|
| `RateLimitError` | API quota exceeded | Wait 60s and retry; reduce batch size |
| `InvalidAPIKeyError` | API key invalid/expired | Verify key in `.env`; check account status |
| `FileNotFoundError: .tex` | LaTeX source not found | Check input path; ensure main.tex exists |
| `Timeout during generation` | Large paper or slow API | Use `--model-choice 3` (GPT-3.5-turbo) |
| `Memory Error` | Insufficient RAM | Close other apps; process fewer components |

---

### Stage 4: Quality Validation

**Objective:** Verify output quality before deployment

**Steps:**
1. Check each component against quality criteria
2. Test functionality (links, interactivity)
3. Review for content accuracy
4. Assess visual quality

**Website Validation:**

| Check | Pass Criteria | Action if Fail |
|-------|---------------|----------------|
| Loads correctly | No 404s, all assets load | Fix broken paths |
| Mobile responsive | Readable on phone | Adjust CSS |
| Links work | All internal/external links valid | Fix hrefs |
| Figures display | All images render | Check paths |
| Citations link | References clickable | Verify anchors |

**Poster Validation:**

| Check | Pass Criteria | Action if Fail |
|-------|---------------|----------------|
| Resolution | 300+ DPI at print size | Regenerate |
| Readability | Text readable from 3-6 feet | Increase font |
| Layout balance | No crowded sections | Redistribute |
| Colors print | CMYK-safe colors | Adjust palette |
| QR code works | Scans correctly | Regenerate |

**Video Validation:**

| Check | Pass Criteria | Action if Fail |
|-------|---------------|----------------|
| Audio sync | Narration matches slides | Re-render |
| Duration | Within target length | Edit content |
| Resolution | 1080p minimum | Re-export |
| Captions | Accurate transcription | Edit SRT |
| Playback | Smooth on target platform | Re-encode |

**Exit Criteria:**
- [ ] All validation checks passed
- [ ] Content accuracy verified
- [ ] Visual quality acceptable
- [ ] Functionality tested

---

### Stage 5: Deployment

**Objective:** Deploy outputs to target platforms

**Steps:**
1. Prepare files for target platform
2. Deploy website (if generated)
3. Submit poster for printing (if generated)
4. Upload video to platform (if generated)

**Website Deployment Options:**

| Platform | Command/Process | Best For |
|----------|-----------------|----------|
| GitHub Pages | `git push` to gh-pages branch | Free, custom domain |
| Netlify | Drag-drop or CLI deploy | Fast, CI/CD |
| University hosting | SCP/SFTP upload | Institutional URL |

**Poster Printing:**
- Export: PDF at 300 DPI minimum
- Size: Verify conference requirements
- Services: University print shop, online services

**Video Distribution:**
- YouTube: Public or unlisted
- Institutional: University video platforms
- Conference: Virtual conference systems

**Exit Criteria:**
- [ ] Website live and accessible (if applicable)
- [ ] Poster print-ready file prepared (if applicable)
- [ ] Video uploaded to target platform (if applicable)
- [ ] All URLs documented

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Component | Metric | Minimum | Target |
|-----------|--------|---------|--------|
| Website | Load time | <5s | <2s |
| Website | Mobile score | 70/100 | 90/100 |
| Poster | Resolution | 150 DPI | 300 DPI |
| Poster | Text size | 24pt min | 32pt body |
| Video | Resolution | 720p | 1080p |
| Video | Audio clarity | Understandable | Clear narration |
| All | Content accuracy | 90% | 100% |

**Completion Checklist:**
- [ ] All selected components generated
- [ ] Quality validation passed for each component
- [ ] Content accurately represents paper
- [ ] Figures and citations properly handled
- [ ] Deployed to target platform(s)
- [ ] URLs documented for sharing

</success_criteria>

<scope>
## Scope

**In Scope:**
- LaTeX/PDF paper to interactive website
- Paper to presentation video (with narration)
- Paper to print-ready poster
- Batch processing multiple papers
- Custom branding and sizing
- Multi-language support

**Out of Scope** (use specialized resources):
- Manual slide creation → use `scientific-slides`
- Document conversion only → use `markitdown`
- Writing the paper → use `scientific-writing`
- Standalone diagram generation → use `scientific-schematics`
- Image generation → use `generate-image`

</scope>

<best_practices>
## Best Practices Quick Reference

| Practice | Guideline |
|----------|-----------|
| **Prefer LaTeX input** | Use LaTeX source over PDF for better structure and quality |
| **Verify poster dimensions** | Check conference specs before generation (48"x36", 60"x40", A0) |
| **Always validate outputs** | Test website on mobile, print poster sample, watch full video |
| **Implement rate limiting** | Add 60s delays between batch jobs |
| **Use high-resolution figures** | Vector formats preferred; 300 DPI minimum for poster rasters |
| **Match model to use case** | GPT-4 for production, GPT-3.5-turbo for testing |
| **Organize input files** | Standard structure: main.tex, figures/, bibliography.bib |
| **Plan deployment early** | Choose platform before generation to configure outputs |

For detailed guidance with code examples, see `{baseDir}/references/best_practices.md`.

</best_practices>

<templates>
## Output Templates

**Standard Output Structure:**
```
output/{{paper_name}}/
├── website/     # index.html, styles.css, assets/
├── poster/      # poster_final.pdf, poster_final.png
└── video/       # final_video.mp4, slides/, subtitles.srt
```

For deployment checklists, quality metrics, and detailed templates, see `{baseDir}/references/output_templates.md`.

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `markitdown` | Use to convert PDF to Markdown first if needed |
| `scientific-writing` | Use to write the paper before transformation |
| `scientific-slides` | Use for manual slide creation (Paper2Video is automated) |
| `latex-posters` | Alternative for manual poster creation |
| `venue-templates` | Check venue requirements before generation |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/installation.md` | Complete installation and configuration guide |
| `{baseDir}/references/best_practices.md` | Detailed guidelines with code examples |
| `{baseDir}/references/output_templates.md` | Deployment checklists and quality metrics |
| `{baseDir}/references/paper2web.md` | Website generation documentation |
| `{baseDir}/references/paper2video.md` | Video generation with talking-head setup |
| `{baseDir}/references/paper2poster.md` | Poster design templates and specifications |
| `{baseDir}/references/usage_examples.md` | Real-world workflow examples |

## External Resources

- **GitHub Repository**: https://github.com/YuhangChen1/Paper2All
- **Dataset**: Hugging Face (13 research categories)

</references>
