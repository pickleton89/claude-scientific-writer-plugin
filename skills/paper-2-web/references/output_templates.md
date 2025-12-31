# Output Templates for Paper2All Pipeline

Standard templates for deployment checklists and output organization.

---

## Deployment Checklist Template

Use this checklist to track deployment status for each paper transformation.

```markdown
# Paper2All Deployment Checklist

**Paper:** {{PAPER_TITLE}}
**Date:** {{YYYY-MM-DD}}
**Pipeline Version:** Paper2All v{{VERSION}}

## Components Generated
- [ ] Website: {{URL or N/A}}
- [ ] Poster: {{filename or N/A}}
- [ ] Video: {{URL or N/A}}

## Quality Checks

### Website
- [ ] Loads in <5s
- [ ] Mobile responsive (passes Google Mobile-Friendly Test)
- [ ] All internal links work
- [ ] All external links work
- [ ] Figures display correctly at proper resolution
- [ ] Citations link to references section
- [ ] Metadata (title, description) set correctly

### Poster
- [ ] Resolution verified at 300+ DPI
- [ ] Text readable at 3-6 feet viewing distance
- [ ] Colors verified as print-safe (CMYK compatible)
- [ ] QR code scans correctly
- [ ] Institution branding present and correct
- [ ] Dimensions match conference requirements

### Video
- [ ] Audio synchronized with visuals throughout
- [ ] Captions accurate and timed correctly
- [ ] Duration within target length
- [ ] Resolution meets platform requirements (1080p+)
- [ ] No audio clipping or distortion
- [ ] Intro/outro professional

## Deployment Status

### Website Deployment
- [ ] Files uploaded to hosting platform
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Analytics tracking enabled
- [ ] Final URL documented: _______________

### Poster Deployment
- [ ] Print-ready PDF exported
- [ ] Test print reviewed
- [ ] Sent to print shop / conference portal
- [ ] Backup copies saved

### Video Deployment
- [ ] Uploaded to target platform (YouTube/institutional)
- [ ] Thumbnail set
- [ ] Description and tags added
- [ ] Captions uploaded/enabled
- [ ] Visibility settings configured
- [ ] Final URL documented: _______________

## Final Sign-Off
- [ ] All URLs documented and tested
- [ ] Files backed up to cloud storage
- [ ] Shared with collaborators
- [ ] Added to lab website / portfolio

**Completed by:** _______________
**Date:** _______________
```

---

## Output Directory Structure

Standard organization for Paper2All outputs.

```
output/
└── {{paper_name}}/
    ├── website/
    │   ├── index.html           # Main homepage
    │   ├── styles.css           # Stylesheet
    │   ├── scripts.js           # Interactive features (if any)
    │   └── assets/
    │       ├── figures/         # Paper figures
    │       │   ├── fig1.png
    │       │   ├── fig2.png
    │       │   └── ...
    │       ├── logos/           # Institution/conference logos
    │       └── icons/           # UI icons
    │
    ├── poster/
    │   ├── poster_final.pdf     # Print-ready PDF (300 DPI)
    │   ├── poster_final.png     # High-res PNG for digital display
    │   ├── poster_preview.png   # Low-res preview
    │   └── source/
    │       ├── poster.pptx      # Editable source (if generated)
    │       └── elements/        # Individual poster elements
    │
    ├── video/
    │   ├── final_video.mp4      # Final rendered video (1080p)
    │   ├── final_video_720p.mp4 # Lower resolution version
    │   ├── slides/
    │   │   ├── slide_01.png     # Individual slide images
    │   │   ├── slide_02.png
    │   │   └── ...
    │   ├── audio/
    │   │   ├── narration.mp3    # Full narration track
    │   │   └── segments/        # Per-slide audio segments
    │   ├── subtitles.srt        # Subtitle file
    │   └── script.md            # Narration script
    │
    └── metadata/
        ├── generation_log.txt   # Processing log
        ├── config.json          # Generation parameters
        └── timestamps.txt       # Processing timestamps
```

---

## Paper Metadata Template

Template for organizing paper information before transformation.

```yaml
# paper_metadata.yaml

paper:
  title: "Full Paper Title"
  short_title: "Short Title for Headers"
  authors:
    - name: "First Author"
      affiliation: "University/Institution"
      email: "author@example.com"
    - name: "Second Author"
      affiliation: "University/Institution"

  abstract: |
    Paper abstract text goes here.
    Can span multiple lines.

  keywords:
    - keyword1
    - keyword2
    - keyword3

  venue:
    name: "Conference/Journal Name"
    year: 2025
    type: "conference"  # or "journal", "preprint"

  links:
    paper_pdf: "https://arxiv.org/pdf/..."
    code: "https://github.com/..."
    data: "https://zenodo.org/..."
    preprint: "https://arxiv.org/abs/..."
    doi: "10.1234/..."

branding:
  institution_logo: "path/to/logo.png"
  color_scheme: "default"  # or custom hex codes

generation:
  components:
    - website
    - poster
    - video
  poster_size:
    width_inches: 48
    height_inches: 36
  video_duration_minutes: 10
  model: "gpt-4"
```

---

## Quality Metrics Reference

Target metrics for each output component.

### Website Metrics

| Metric | Minimum | Target | Tool |
|--------|---------|--------|------|
| Load time | <5s | <2s | Google PageSpeed |
| Mobile score | 70/100 | 90/100 | Mobile-Friendly Test |
| Accessibility | AA | AAA | WAVE Tool |
| Links working | 100% | 100% | Link checker |

### Poster Metrics

| Metric | Minimum | Target | Verification |
|--------|---------|--------|--------------|
| Resolution | 150 DPI | 300 DPI | Image properties |
| Body text | 24pt | 32pt | Design specs |
| Title text | 72pt | 96pt | Design specs |
| QR code size | 1" | 1.5" | Physical measurement |

### Video Metrics

| Metric | Minimum | Target | Verification |
|--------|---------|--------|--------------|
| Resolution | 720p | 1080p | Video properties |
| Audio bitrate | 128kbps | 256kbps | Audio properties |
| Frame rate | 24fps | 30fps | Video properties |
| File size | - | <500MB | File properties |
