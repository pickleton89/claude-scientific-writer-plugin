# Best Practices for Paper2All Pipeline

Guidelines for optimal results when transforming academic papers into promotional materials.

---

## 1. Prefer LaTeX Source Input

LaTeX source files preserve document structure, figure quality, and citation metadata better than PDF extraction.

**Recommended Approach:**
```bash
# Check for LaTeX source first
ls paper_dir/*.tex

# Use LaTeX directory as input
python pipeline_all.py --input-dir paper_dir/  # Will auto-detect .tex files
```

**Benefits of LaTeX input:**
- Higher figure quality extraction
- Preserved document structure
- Better equation rendering
- Citation metadata intact

**When PDF is acceptable:**
- LaTeX source unavailable
- Published paper only accessible as PDF
- PDF is high-quality with selectable text

---

## 2. Verify Poster Dimensions First

Conference poster requirements vary significantly. Check specifications before generation.

**Recommended Approach:**
```bash
# Always specify dimensions matching conference requirements
# Common sizes: 48"x36", 60"x40", A0 (33.1"x46.8")

python pipeline_all.py \
  --generate-poster \
  --poster-width-inches 48 \
  --poster-height-inches 36
```

**Common Conference Specifications:**

| Conference Type | Typical Size | Orientation |
|-----------------|--------------|-------------|
| Portrait standard | 36" x 48" | Portrait |
| Landscape standard | 48" x 36" | Landscape |
| Large format | 60" x 40" | Landscape |
| A0 international | 33.1" x 46.8" | Portrait |

**Verification Steps:**
1. Check conference website for poster guidelines
2. Note orientation requirement (portrait vs landscape)
3. Verify DPI requirements (usually 150-300 DPI)

---

## 3. Always Run Quality Validation

Test all generated outputs before deployment to catch issues early.

**Recommended Validation Workflow:**

### Website Validation
1. Open in browser and verify all assets load
2. Test on mobile device for responsiveness
3. Click all internal and external links
4. Verify figures display at proper resolution
5. Check citations link correctly

### Poster Validation
1. Print test section at actual size (e.g., 8.5"x11" crop)
2. Verify text readability from 3-6 feet distance
3. Check color accuracy in print preview
4. Test QR code functionality with phone scanner

### Video Validation
1. Watch entire video checking audio synchronization
2. Verify captions match narration
3. Check resolution meets platform requirements
4. Test playback on target platform (YouTube, institutional)

---

## 4. Implement Rate Limit Protection

When batch processing multiple papers, add delays between jobs to avoid API throttling.

**Recommended Approach:**
```bash
# Sequential processing with rate limit buffer
for paper in papers/*; do
    echo "Processing: $paper"
    python pipeline_all.py --input-dir "$paper"
    echo "Completed: $paper"
    sleep 60  # Rate limit buffer between jobs
done
```

**Best Practices for Batch Processing:**
- Process papers sequentially, not in parallel
- Add 60-second delay between jobs
- Monitor API usage during processing
- Save intermediate outputs for recovery
- Log completion status for each paper

---

## 5. Use High-Resolution Figures

Ensure source figures meet quality requirements for the target output format.

**Resolution Requirements by Output:**

| Output Type | Minimum DPI | Recommended DPI | Format Preference |
|-------------|-------------|-----------------|-------------------|
| Website | 72 | 144 (retina) | PNG, WebP |
| Poster | 150 | 300 | PDF, SVG, EPS |
| Video | 72 | 144 | PNG |

**Recommended Approach:**
- Use vector formats (PDF, SVG, EPS) when possible
- Export raster images at 300+ DPI for poster use
- Re-export figures from original source if quality insufficient
- Calculate actual print size: `DPI = pixels / inches`

**Figure Quality Checklist:**
- [ ] Figures are at least 300 DPI at poster print size
- [ ] Text in figures is readable at target viewing distance
- [ ] Vector graphics used where possible
- [ ] Color space is CMYK-compatible for printing

---

## 6. Match Model to Use Case

Select the appropriate LLM model based on quality needs and budget constraints.

**Model Selection Guide:**

| Quality Need | Recommended Model | Cost | Best For |
|--------------|-------------------|------|----------|
| Production | GPT-4 | $$ | Conference submissions, publications |
| Best quality | GPT-4.1 | $$$ | High-stakes venues, flagship papers |
| Quick draft | GPT-3.5-turbo | $ | Testing pipelines, simple papers |

**Budget Optimization Tips:**
- Use GPT-3.5-turbo for initial testing
- Generate website-only first (lowest cost)
- Review draft before regenerating with better model
- Generate only needed components

---

## 7. Organize Input Files Properly

Consistent file organization improves extraction quality and reduces errors.

**Recommended Directory Structure:**
```
paper_name/
├── main.tex           # Primary LaTeX file
├── figures/           # All figure files
│   ├── fig1.pdf
│   ├── fig2.png
│   └── ...
├── tables/            # Table files (if separate)
├── bibliography.bib   # Citation database
└── supplementary/     # Optional supplementary materials
```

**Pre-Processing Checklist:**
- [ ] Main .tex file compiles without errors
- [ ] All figures present in figures/ directory
- [ ] Bibliography file includes all citations
- [ ] No broken file references in LaTeX source
- [ ] Figures at sufficient resolution for target output

---

## 8. Plan Deployment Platform Early

Different platforms have different requirements. Plan deployment before generation.

**Platform Requirements:**

| Platform | Requirements | Notes |
|----------|--------------|-------|
| GitHub Pages | Static HTML, <100MB | Free, custom domain support |
| Netlify | Static HTML | Fast CDN, CI/CD integration |
| YouTube | 1080p+, MP4/MOV | Public or unlisted options |
| Conference portal | Varies | Check submission guidelines |
| Print shop | 300 DPI PDF | CMYK color space preferred |

**Deployment Preparation:**
1. Choose platform before generation
2. Configure output settings for platform
3. Prepare metadata (descriptions, tags)
4. Plan URL structure for sharing
