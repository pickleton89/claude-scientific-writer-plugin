# Bioinformatics Journal Formatting Guide

Comprehensive submission guidelines and formatting requirements for major bioinformatics journals.

**Last Updated**: 2025-01

---

## Nucleic Acids Research (NAR)

**Journal Type**: Top-tier journal for nucleic acids, genomics, and computational biology
**Publisher**: Oxford University Press
**Impact Factor**: ~14-16 (varies by year)
**Open Access**: Hybrid (author choice)

### Article Types

| Type | Length | Deadline | Focus |
|------|--------|----------|-------|
| **Database issue** | 4-8 pages | Annual (October) | New/updated biological databases |
| **Web Server issue** | 4-6 pages | Annual (February) | Web-based tools and servers |
| **Methods Online** | Variable | Rolling | New computational methods |
| **Research Articles** | No limit | Rolling | Original research |
| **Breakthrough Articles** | No limit | Rolling | Major advances (editor invitation) |

### Formatting Requirements

- **Abstract**: 250 words maximum, unstructured (single paragraph)
- **Structure**: Introduction, Materials and Methods, Results, Discussion, Conclusions (optional)
- **Format**: Single column, double-spaced for submission
- **Font**: Any standard font, 12pt
- **Line spacing**: Double
- **Margins**: 2.5 cm (1 inch) all sides
- **Page numbers**: Required
- **Citations**: Numbered in order of appearance (brackets)
- **References**: NAR style
  - Format: Author,A.A., Author,B.B. and Author,C.C. (Year) Title. *Journal Abbrev.*, **vol**, pages.
  - Example: Watson,J.D. and Crick,F.H.C. (1953) Molecular structure of nucleic acids. *Nature*, **171**, 737–738.

### Figure Specifications

| Property | Requirement |
|----------|-------------|
| **Format** | TIFF, EPS, or PDF (vector preferred) |
| **Resolution** | 300 dpi minimum (600 dpi recommended) |
| **Width** | Single column: 86 mm / Double column: 178 mm |
| **Color** | Free, but ensure grayscale readability |
| **Legends** | Provided separately, not embedded in figure |

### MANDATORY Sections

1. **Data Availability Statement**: Required after Conclusion
2. **Code Availability**: GitHub/Zenodo DOI required for software
3. **Supplementary Data**: Hosted by journal, not external links
4. **Funding**: Required
5. **Conflict of Interest**: Required

### Database Issue Specifics

**Submission deadline**: Usually October for following year's January issue

**Required content**:
- URL of the database (must be functional at submission)
- Description of data content and sources
- User interface description with screenshots
- Comparison with existing resources
- Statistics on usage (if updating existing database)
- Plans for maintenance and updates

**Evaluation criteria**:
- Novelty and utility of the resource
- Quality of implementation
- Documentation and help resources
- Long-term availability plan

### Web Server Issue Specifics

**Submission deadline**: Usually February for following year's July issue

**Required content**:
- Working URL for the web server
- Input/output description
- Example use cases with screenshots
- Performance benchmarks (if applicable)
- Comparison with alternative tools
- Server availability and response times

**Technical requirements**:
- Server must be operational during review
- No registration required for basic functionality
- Clear input format specifications
- Downloadable results preferred

### Author Guidelines

https://academic.oup.com/nar/pages/submission_online

---

## Bioinformatics (Oxford)

**Journal Type**: Premier journal for computational biology methods
**Publisher**: Oxford University Press
**Impact Factor**: ~6-7
**Open Access**: Hybrid

### Article Types

| Type | Length | Focus |
|------|--------|-------|
| **Original Paper** | 7 pages (final format) | Novel computational methods |
| **Application Note** | 2 pages (final format) | Software/database description |
| **Review** | By invitation | Comprehensive field reviews |
| **Discovery Note** | 2-4 pages | Brief discoveries |

### Formatting Requirements

- **Abstract**: 150-250 words, unstructured
- **Keywords**: 3-6 keywords required
- **Structure**: Abstract, Introduction, Methods, Results, Discussion, (Conclusions optional)
- **Format**: Double-spaced, single column
- **Font**: Times New Roman or similar, 12pt
- **Margins**: 1 inch all sides
- **Citations**: Numbered in order of appearance
- **References**: Oxford style
  - Example: Watson,J.D. and Crick,F.H.C. (1953) Molecular structure of nucleic acids. *Nature*, **171**, 737–738.

### MANDATORY Requirements

1. **Web link for software**: Required and must be functional
2. **Comparison with existing methods**: Required for Original Papers
3. **Supplementary validation data**: Expected
4. **Runtime and memory benchmarks**: Expected for method papers

### Application Note Specifics

**Length**: Maximum 2 pages in final format (~1,300 words + 1 figure/table)

**Required content**:
- Summary of the software functionality
- Novelty statement (what's new?)
- Availability (URL, license, platform requirements)
- Example usage (command-line or screenshot)

**Evaluation criteria**:
- Utility to the bioinformatics community
- Implementation quality
- Documentation quality
- Comparison with alternatives

### Original Paper Specifics

**Length**: Maximum 7 pages in final format

**Required content**:
- Clear problem statement
- Novel algorithmic/statistical approach
- Comprehensive benchmarking
- Comparison with state-of-the-art methods
- Discussion of limitations

**Expected benchmarks**:
- Accuracy metrics (sensitivity, specificity, F1, AUC-ROC)
- Runtime complexity (O(n) analysis preferred)
- Memory usage profiles
- Scalability to large datasets

### Author Guidelines

https://academic.oup.com/bioinformatics/pages/instructions_for_authors

---

## Genome Biology

**Journal Type**: Open-access journal for genomics research
**Publisher**: BioMed Central (Springer Nature)
**Impact Factor**: ~10-13
**Open Access**: Yes (APC: ~$4,290)

### Article Types

| Type | Length | Focus |
|------|--------|-------|
| **Research** | No limit | Major genomics advances |
| **Method** | No limit | New computational/experimental methods |
| **Software** | 2-4 pages | Open-source tools |
| **Comment/Review** | Variable | Field perspectives |

### Formatting Requirements

- **Abstract**: Structured (Background, Results, Conclusions), 350 words max
- **Keywords**: 3-10 keywords
- **Structure**: Background, Results, Discussion, Conclusions, Methods
  - Note: Methods section at END (unusual placement)
- **Format**: Single column
- **Font**: Any standard font, 12pt
- **Line spacing**: Double
- **Citations**: Vancouver style, numbered in brackets [1]
- **References**: Vancouver/NLM format

### MANDATORY Sections (Declarations)

1. **Ethics approval and consent**: Required if applicable
2. **Consent for publication**: Required if applicable
3. **Data Availability**: GEO/SRA/ArrayExpress accession MANDATORY
4. **Code Availability**: GitHub/Zenodo DOI for all software
5. **Competing interests**: Required
6. **Funding**: Required
7. **Authors' contributions**: Required (CRediT roles encouraged)
8. **Acknowledgements**: Optional

### Data Availability Specifics

**STRICT requirements**:
- All sequencing data: NCBI SRA, ENA, or DDBJ
- All processed expression data: GEO or ArrayExpress
- All variants: EVA or ClinVar
- Proteomics: PRIDE
- Metabolomics: MetaboLights
- Other data: Zenodo, Figshare, or Dryad

### Review Criteria

**What editors/reviewers look for**:
1. Novelty of biological insight (primary criterion)
2. Technical rigor and reproducibility
3. Broad interest to genomics community
4. Quality of data presentation
5. Complete data/code availability

### Software Paper Specifics

**Required elements**:
- Open-source license (MIT, Apache, GPL)
- Installation instructions
- Example data with expected output
- Documentation (README at minimum)
- Version control (GitHub/GitLab)
- Archived version with DOI (Zenodo)

### Author Guidelines

https://genomebiology.biomedcentral.com/submission-guidelines

---

## Genome Research

**Journal Type**: Premier journal for genome science
**Publisher**: Cold Spring Harbor Laboratory Press
**Impact Factor**: ~7-9
**Open Access**: Hybrid (delayed open access after 6 months)

### Article Types

| Type | Length | Focus |
|------|--------|-------|
| **Research** | No strict limit | Original genome research |
| **Methods** | Variable | New methods and algorithms |
| **Resource** | Variable | Large datasets, databases, tools |
| **Letter** | 2-4 pages | Brief communications |

### Focus Areas

- Genome structure and function
- Comparative and evolutionary genomics
- Population genetics and genomics
- Epigenomics and chromatin biology
- Functional genomics
- New sequencing technologies and methods

### Formatting Requirements

- **Abstract**: 250 words max, unstructured
- **Structure**: Introduction, Results, Discussion, Methods
  - Note: Methods at END (Cold Spring Harbor style)
- **Format**: Double-spaced
- **Font**: 12pt, standard fonts
- **Citations**: Numbered in order of appearance
- **References**: Cold Spring Harbor style
  - Example: Watson JD, Crick FHC. 1953. Molecular structure of nucleic acids. *Nature* **171**: 737–738.

### MANDATORY Requirements

1. **Data deposition**: All sequence data must be deposited before publication
2. **Code availability**: All code must be openly available
3. **Methods reproducibility**: Sufficient detail for reproduction
4. **Resource papers**: Must deposit ALL data in appropriate repositories

### Review Criteria

**Emphasis on**:
- Biological significance of findings
- Technical innovation
- Data quality and reproducibility
- Potential impact on the field

### Author Guidelines

https://genome.cshlp.org/site/misc/ifora.xhtml

---

## Nature Methods

**Journal Type**: Top-tier methods journal across all life sciences
**Publisher**: Nature Publishing Group
**Impact Factor**: ~30-40
**Open Access**: Hybrid

### Article Types

| Type | Length | Focus |
|------|--------|-------|
| **Article** | 5,000-6,000 words | Transformative methodological advances |
| **Brief Communication** | 2,500 words | Significant but concise advances |
| **Analysis** | Variable | Comparison of methods |
| **Resource** | Variable | Large-scale datasets |
| **Correspondence** | 1,000 words | Comments and replies |

### Scope and Selection Criteria

**What Nature Methods publishes**:
- **Transformative** methodological advances (not incremental)
- Methods enabling previously impossible experiments
- Substantial improvements in accuracy, speed, or accessibility
- Novel approaches to data analysis with broad applicability

**What it does NOT typically publish**:
- Incremental improvements to existing methods
- Application of known methods to new datasets
- Niche tools with limited user base

### Formatting Requirements

- **Abstract**: 200 words max, unstructured
- **Structure**: Introduction, Results, Discussion (Methods in separate section)
- **Format**: Single column, double-spaced
- **Font**: Any standard font, 12pt
- **Line spacing**: Double
- **Margins**: 2.5 cm all sides
- **Citations**: Numbered superscript (Nature style)
- **References**: Nature style

### MANDATORY Requirements

1. **Validation on multiple datasets**: Independent validation required
2. **Comparison with gold standards**: Head-to-head comparisons
3. **Code/software with documentation**: GitHub + archived DOI
4. **Life Sciences Reporting Summary**: Required checklist
5. **Benchmark datasets**: Public availability required

### Life Sciences Reporting Summary

**Required for all manuscripts**:
- Experimental design and statistics
- Biological and chemical materials
- Antibodies validation
- Cell lines authentication
- Data and code availability
- Protocol availability

### Review Process

**Two-stage evaluation**:
1. Editorial assessment (scope and significance)
2. Expert peer review (technical rigor)

**Common reasons for rejection**:
- Incremental rather than transformative
- Insufficient validation
- Limited comparison with alternatives
- Restricted applicability

### Author Guidelines

https://www.nature.com/nmeth/about/for-authors

---

## PLOS Computational Biology

**Journal Type**: Open-access computational biology journal
**Publisher**: Public Library of Science
**Impact Factor**: ~4-5
**Open Access**: Yes (APC: ~$2,500)

### Article Types

| Type | Length | Focus |
|------|--------|-------|
| **Research Article** | No limit | Novel computational methods/analyses |
| **Software** | Variable | Open-source tools |
| **Methods** | Variable | Detailed methodologies |
| **Education** | Variable | Tutorials, "Ten Simple Rules" series |
| **Review** | Variable | Comprehensive reviews (invited) |

### Scope

**In scope**:
- Novel computational methods for biological problems
- New algorithms with biological applications
- Software tools for biological data analysis
- Mathematical modeling of biological systems
- Systems biology approaches
- Machine learning for biology

**Out of scope**:
- Pure computer science without biological application
- Purely experimental biology without computational contribution
- Database updates without novel analysis

### Formatting Requirements

- **Abstract**: 300 words max, unstructured
- **Keywords**: 3-5 keywords
- **Structure**: Introduction, Materials and Methods, Results, Discussion
- **Format**: Single column, double-spaced
- **Font**: Times, Arial, or Helvetica, 12pt
- **Margins**: 1 inch all sides
- **Citations**: Vancouver style, numbered in brackets [1]
- **References**: Vancouver/NLM format
  - Example: Watson JD, Crick FHC. Molecular structure of nucleic acids. Nature. 1953;171:737-738.

### MANDATORY Requirements

1. **Open Access**: All articles fully open access
2. **FAIR data principles**: All data findable, accessible, interoperable, reusable
3. **Open source code**: GitHub/GitLab + archived DOI (Zenodo)
4. **Data Availability Statement**: Required
5. **Funding Statement**: Required
6. **Competing Interests**: Required

### Software Paper Requirements

**Checklist for submission**:
- [ ] Source code on GitHub/GitLab
- [ ] Archived version with DOI (Zenodo)
- [ ] Installation instructions (tested on clean system)
- [ ] Example data with expected output
- [ ] License clearly stated (OSI-approved preferred)
- [ ] Version number in manuscript
- [ ] Documentation (API if applicable)

### "Ten Simple Rules" Series

**Popular education format**:
- 10 numbered, actionable recommendations
- Practical guidance for researchers
- Topics: reproducibility, data visualization, scientific writing, career development
- Format: Short, accessible, highly cited

### Author Guidelines

https://journals.plos.org/ploscompbiol/s/submission-guidelines

---

## Common Bioinformatics Journal Requirements

### Data Deposition Standards (Universal)

| Data Type | Primary Repository | Alternatives |
|-----------|-------------------|--------------|
| **Raw sequencing (FASTQ)** | NCBI SRA | ENA (EBI), DDBJ |
| **Processed expression** | GEO | ArrayExpress |
| **Variants** | ClinVar, EVA | dbSNP, dbVar |
| **Protein structures** | PDB | EMDB (cryo-EM) |
| **Proteomics** | PRIDE | MassIVE, PeptideAtlas |
| **Metabolomics** | MetaboLights | Metabolomics Workbench |
| **Genome assemblies** | NCBI GenBank | ENA, DDBJ |
| **Workflows/pipelines** | WorkflowHub | Dockstore |
| **General/other** | Zenodo | Figshare, Dryad |
| **Code** | GitHub + Zenodo DOI | GitLab + Zenodo DOI |

### Software Availability Checklist

Essential for all bioinformatics software papers:

**Code Accessibility**:
- [ ] Source code on GitHub/GitLab
- [ ] Archived version with DOI (Zenodo/Figshare)
- [ ] Clear license (MIT, Apache, GPL, BSD)
- [ ] Version number explicitly stated in manuscript

**Documentation**:
- [ ] Installation instructions (for all supported platforms)
- [ ] Dependencies listed with versions
- [ ] Quick start guide
- [ ] Example data with expected output
- [ ] API documentation (if applicable)
- [ ] Troubleshooting guide

**Reproducibility**:
- [ ] Container available (Docker/Singularity)
- [ ] Conda environment.yml or requirements.txt
- [ ] Test suite included
- [ ] Continuous integration configured

### Benchmarking Best Practices

**Standard metrics for method comparisons**:

| Application | Common Metrics |
|-------------|---------------|
| **Classification** | Accuracy, Precision, Recall, F1, AUC-ROC, AUC-PR |
| **Regression** | MAE, RMSE, R², Spearman ρ, Pearson r |
| **Clustering** | ARI, NMI, Silhouette, V-measure |
| **Sequence alignment** | Sensitivity, Specificity, Accuracy |
| **Variant calling** | Sensitivity, Precision, F1, Transition/Transversion ratio |
| **Differential expression** | TPR at controlled FDR, overlap with gold standard |

**Performance reporting**:
- Runtime complexity (O notation when possible)
- Wall-clock time on standardized hardware
- Memory usage (peak and average)
- Scalability analysis across data sizes
- Hardware specifications used

### Figure Standards for Bioinformatics

**Common figure types**:

| Figure Type | Key Requirements |
|-------------|-----------------|
| **Volcano plots** | Log2FC vs -log10(p-value), threshold lines, labeled genes |
| **Heatmaps** | Hierarchical clustering, color scale legend, row/column annotations |
| **PCA/t-SNE/UMAP** | Variance explained (PCA), perplexity (t-SNE), color by condition |
| **Kaplan-Meier** | Confidence intervals, number at risk table, p-value |
| **ROC curves** | Diagonal reference line, AUC in legend, confidence intervals |
| **Sequence logos** | Bits scale, proper font, position numbers |
| **Genome browser** | Coordinate scale, gene annotations, track labels |

**General requirements**:
- Resolution: 300 dpi minimum (600 dpi for line art)
- Color: RGB for online, colorblind-accessible palettes recommended
- Font: Readable at final size (8pt minimum)
- Scale bars: Required for images with spatial dimensions

### Common Rejection Reasons

**Top reasons for desk rejection**:
1. **Missing data availability**: No accession numbers for deposited data
2. **No comparison with existing methods**: Required for method papers
3. **Irreproducible results**: Missing parameters, versions, or code
4. **Overstated claims**: Claims not supported by evidence
5. **No biological validation**: Computational predictions without experimental support
6. **Out of scope**: Pure CS or pure biology without computational/biological integration

**Top reasons for rejection after review**:
1. Limited novelty or incremental improvement
2. Insufficient benchmarking or validation
3. Poor reproducibility documentation
4. Unclear method description
5. Selective or biased comparisons
6. Overfitting without proper cross-validation

### Writing Conventions

**Bioinformatics-specific terminology**:
- Use **gene symbols** correctly: *TP53* (human gene, italicized), TP53 (protein, roman)
- Report **genome assembly versions**: GRCh38 or hg38
- Specify **coordinate systems**: 1-based (VCF, Ensembl) vs 0-based (BED, BAM)
- Use **standard nomenclature**: HGVS for variants, HGNC for gene names

**Methods section essentials**:
- Software versions and parameters
- Hardware specifications for runtime comparisons
- Random seed values for reproducibility
- Train/test split methodology
- Cross-validation strategy
- Multiple testing correction method (BH FDR preferred)

---

## Quick Reference Table

| Journal | Impact Factor | Open Access | Page Limit | APC |
|---------|--------------|-------------|------------|-----|
| **NAR (Database)** | ~14-16 | Optional | 4-8 pages | ~$2,500-3,500 |
| **NAR (Web Server)** | ~14-16 | Optional | 4-6 pages | ~$2,500-3,500 |
| **Bioinformatics** | ~6-7 | Optional | 7 pages / 2 pages | ~$2,500 |
| **Genome Biology** | ~10-13 | Yes | No limit | ~$4,290 |
| **Genome Research** | ~7-9 | Delayed | No limit | ~$4,500 |
| **Nature Methods** | ~30-40 | Optional | 5-6k words | ~$11,690 |
| **PLOS Comp Bio** | ~4-5 | Yes | No limit | ~$2,500 |

---

## Choosing the Right Journal

### Decision Framework

```
Is your contribution primarily...
│
├─► A NEW DATABASE → NAR Database issue
│
├─► A WEB SERVER/TOOL → NAR Web Server issue OR Bioinformatics Application Note
│
├─► A NOVEL METHOD...
│   │
│   ├─► ...that is TRANSFORMATIVE → Nature Methods
│   │
│   ├─► ...with SOLID benchmarking → Bioinformatics Original Paper
│   │
│   └─► ...with BROAD biological impact → Genome Biology Method
│
├─► A SOFTWARE PACKAGE...
│   │
│   ├─► ...that is OPEN SOURCE → PLOS Computational Biology
│   │
│   └─► ...with BIOLOGICAL validation → Genome Biology Software
│
└─► GENOME-SCALE RESEARCH...
    │
    ├─► ...with MAJOR biological insight → Genome Biology, Genome Research
    │
    └─► ...with COMPUTATIONAL focus → PLOS Computational Biology
```

### Matching Content to Venue

| Your Work | Best Fit Journals |
|-----------|-------------------|
| Biological database | NAR (Database issue) |
| Web server/tool | NAR (Web Server), Bioinformatics |
| Novel algorithm | Bioinformatics, PLOS Comp Bio |
| Transformative method | Nature Methods |
| Open-source software | PLOS Comp Bio, Genome Biology |
| Large genomics study | Genome Biology, Genome Research |
| Educational tutorial | PLOS Comp Bio ("Ten Simple Rules") |

---

## Notes

1. **Always check current guidelines**: Journal requirements change; verify before submission
2. **APC amounts**: Approximate and subject to change; check journal websites
3. **Impact factors**: Fluctuate annually; use as rough guide only
4. **Preprint policies**: All listed journals allow preprints (bioRxiv, arXiv)
5. **Double-check deadlines**: Database and Web Server issues have annual deadlines
6. **Verify data requirements**: Repository requirements may change; confirm current policies

---

*This guide covers major bioinformatics journals as of January 2025. Always consult official author guidelines before submission.*
