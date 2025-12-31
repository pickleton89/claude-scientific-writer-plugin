# Project Structure Reference Guide

> Organizing scientific computing projects for reproducibility

---

## Overview

A well-organized project structure makes analyses easier to understand, reproduce, and maintain. This guide provides templates for different types of scientific projects.

### Principles

1. **Separation of concerns**: Raw data, processed data, code, and results in different locations
2. **Immutability**: Raw data is never modified
3. **Documentation**: Every project has a README explaining structure and usage
4. **Reproducibility**: Clear path from raw data to results
5. **Portability**: Relative paths, documented dependencies

---

## Standard Analysis Project

### Directory Structure

```
my-analysis/
├── README.md                 # Project overview, setup, usage
├── LICENSE                   # Usage terms
├── .gitignore                # Git ignore patterns
│
├── environment.yml           # Conda environment
├── requirements.txt          # Pip requirements (if needed)
├── Dockerfile                # Container definition (optional)
│
├── data/
│   ├── raw/                  # Original, immutable data
│   │   ├── README.md         # Data provenance
│   │   └── .gitkeep
│   ├── processed/            # Cleaned, transformed data
│   │   └── .gitkeep
│   ├── external/             # Data from other sources
│   │   └── README.md         # Attribution and sources
│   └── interim/              # Intermediate processing steps
│       └── .gitkeep
│
├── notebooks/                # Jupyter/R Markdown notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_figures.ipynb
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── data/                 # Data loading and processing
│   │   ├── __init__.py
│   │   ├── load.py
│   │   └── preprocess.py
│   ├── analysis/             # Analysis functions
│   │   ├── __init__.py
│   │   ├── statistics.py
│   │   └── models.py
│   └── visualization/        # Plotting functions
│       ├── __init__.py
│       └── plots.py
│
├── scripts/                  # Standalone scripts
│   ├── 01_download_data.sh
│   ├── 02_preprocess.py
│   └── 03_run_analysis.py
│
├── results/
│   ├── figures/              # Publication figures
│   │   └── .gitkeep
│   ├── tables/               # Summary tables
│   │   └── .gitkeep
│   └── supplementary/        # Supplementary materials
│       └── .gitkeep
│
├── docs/                     # Additional documentation
│   ├── methods.md            # Detailed methods
│   ├── data_dictionary.md    # Variable definitions
│   └── analysis_notes.md     # Analysis decisions
│
├── tests/                    # Unit tests (optional)
│   ├── __init__.py
│   └── test_analysis.py
│
└── config/                   # Configuration files
    ├── config.yaml           # Analysis parameters
    └── paths.yaml            # Path definitions
```

### Key Files

#### README.md

```markdown
# Project Title

Brief description of the project and its goals.

## Installation

```bash
# Clone repository
git clone https://github.com/user/project.git
cd project

# Create environment
conda env create -f environment.yml
conda activate project-env
```

## Data

Raw data should be downloaded to `data/raw/`. See `data/raw/README.md` for details.

```bash
# Download data
./scripts/01_download_data.sh
```

## Usage

### Running the analysis

```bash
# Preprocessing
python scripts/02_preprocess.py

# Main analysis
python scripts/03_run_analysis.py

# Or run notebooks in order
jupyter notebook notebooks/
```

### Reproducing figures

All publication figures can be regenerated from:
```bash
python scripts/generate_figures.py
```

## Project Structure

[Brief description of directories]

## Citation

If you use this code, please cite:

> Author et al. (Year). Title. Journal. DOI

## License

This project is licensed under the MIT License.
```

#### .gitignore

```gitignore
# Data (usually too large for git)
data/raw/*
data/processed/*
data/interim/*
!data/*/.gitkeep
!data/*/README.md

# Results (regenerable)
results/figures/*
results/tables/*
!results/*/.gitkeep

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
*.egg
.pytest_cache/

# Jupyter
.ipynb_checkpoints/
*.ipynb_cache/

# Environment
.env
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

---

## RNA-seq Analysis Project

### Specialized Structure

```
rnaseq-project/
├── README.md
├── environment.yml
│
├── data/
│   ├── raw/
│   │   ├── fastq/            # Raw FASTQ files (or symlinks)
│   │   │   └── README.md     # SRA accessions, download commands
│   │   └── metadata/         # Sample sheets, clinical data
│   │       └── sample_sheet.csv
│   ├── processed/
│   │   ├── aligned/          # BAM files
│   │   ├── counts/           # Gene count matrices
│   │   └── normalized/       # Normalized expression
│   └── external/
│       ├── references/       # Reference genome, GTF
│       │   └── README.md     # Version, download source
│       └── annotations/      # Gene annotations, pathway files
│
├── notebooks/
│   ├── 01_quality_control.ipynb
│   ├── 02_alignment_summary.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_differential_expression.ipynb
│   ├── 05_pathway_analysis.ipynb
│   └── 06_publication_figures.ipynb
│
├── src/
│   ├── qc/
│   │   └── fastqc_multiqc.py
│   ├── alignment/
│   │   └── star_align.py
│   ├── quantification/
│   │   └── featurecounts.py
│   └── analysis/
│       ├── deseq2.R
│       └── enrichment.R
│
├── workflow/                 # Pipeline definition
│   ├── Snakefile
│   ├── config.yaml
│   └── envs/
│       ├── alignment.yml
│       └── analysis.yml
│
├── results/
│   ├── qc/                   # FastQC, MultiQC reports
│   ├── de/                   # Differential expression results
│   │   ├── all_results.csv
│   │   └── significant_genes.csv
│   ├── enrichment/           # Pathway analysis results
│   └── figures/
│
└── docs/
    ├── methods.md
    └── pipeline_diagram.png
```

### Sample Sheet Format

```csv
sample_id,condition,replicate,batch,fastq_1,fastq_2
Control_1,control,1,batch1,Control_1_R1.fastq.gz,Control_1_R2.fastq.gz
Control_2,control,2,batch1,Control_2_R1.fastq.gz,Control_2_R2.fastq.gz
Control_3,control,3,batch2,Control_3_R1.fastq.gz,Control_3_R2.fastq.gz
Treatment_1,treatment,1,batch1,Treatment_1_R1.fastq.gz,Treatment_1_R2.fastq.gz
Treatment_2,treatment,2,batch1,Treatment_2_R1.fastq.gz,Treatment_2_R2.fastq.gz
Treatment_3,treatment,3,batch2,Treatment_3_R1.fastq.gz,Treatment_3_R2.fastq.gz
```

---

## Machine Learning Project

### Specialized Structure

```
ml-project/
├── README.md
├── environment.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── features/             # Engineered features
│   └── splits/               # Train/val/test splits
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_selection.ipynb
│   └── 04_evaluation.ipynb
│
├── src/
│   ├── data/
│   │   ├── make_dataset.py
│   │   └── features.py
│   ├── models/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   └── visualization/
│       └── visualize.py
│
├── models/                   # Saved model artifacts
│   ├── model_v1.pkl
│   └── model_v1_metadata.json
│
├── experiments/              # Experiment tracking
│   ├── mlruns/              # MLflow tracking
│   └── hyperparameter_search/
│
├── results/
│   ├── metrics/
│   ├── predictions/
│   └── figures/
│
└── config/
    ├── config.yaml
    └── hyperparameters.yaml
```

---

## Multi-Omics Project

### Specialized Structure

```
multiomics-project/
├── README.md
├── environment.yml
│
├── data/
│   ├── raw/
│   │   ├── rnaseq/
│   │   ├── proteomics/
│   │   └── metabolomics/
│   ├── processed/
│   │   ├── rnaseq/
│   │   ├── proteomics/
│   │   └── metabolomics/
│   └── integrated/           # Multi-omics integration
│
├── notebooks/
│   ├── rnaseq/
│   │   └── 01_rnaseq_analysis.ipynb
│   ├── proteomics/
│   │   └── 01_proteomics_analysis.ipynb
│   ├── metabolomics/
│   │   └── 01_metabolomics_analysis.ipynb
│   └── integration/
│       ├── 01_data_harmonization.ipynb
│       ├── 02_multi_omics_factor_analysis.ipynb
│       └── 03_pathway_integration.ipynb
│
├── src/
│   ├── rnaseq/
│   ├── proteomics/
│   ├── metabolomics/
│   └── integration/
│
├── results/
│   ├── rnaseq/
│   ├── proteomics/
│   ├── metabolomics/
│   ├── integration/
│   └── figures/
│
└── docs/
    ├── data_dictionary.md
    └── integration_strategy.md
```

---

## Configuration Files

### config.yaml

```yaml
# Analysis configuration

project:
  name: "RNA-seq Analysis"
  version: "1.0.0"
  author: "Researcher Name"

data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  results_dir: "results"

reference:
  genome: "GRCh38"
  annotation: "Ensembl 107"
  gtf: "data/external/references/Homo_sapiens.GRCh38.107.gtf"

alignment:
  tool: "STAR"
  version: "2.7.10b"
  threads: 8
  parameters:
    outSAMtype: "BAM SortedByCoordinate"
    quantMode: "GeneCounts"

quantification:
  tool: "featureCounts"
  version: "2.0.3"
  parameters:
    paired: true
    strand: 2  # reverse stranded

analysis:
  pvalue_threshold: 0.05
  lfc_threshold: 1.0
  min_count: 10
```

### paths.yaml

```yaml
# Path definitions (use relative paths)

data:
  raw:
    fastq: "data/raw/fastq"
    metadata: "data/raw/metadata/sample_sheet.csv"
  processed:
    aligned: "data/processed/aligned"
    counts: "data/processed/counts"
  external:
    genome: "data/external/references/genome.fa"
    gtf: "data/external/references/genes.gtf"

results:
  qc: "results/qc"
  de: "results/de"
  figures: "results/figures"
```

---

## Naming Conventions

### Files

```
# Data files
sample_id_condition_replicate.fastq.gz    # Raw data
sample_id_aligned.bam                      # Processed data
gene_counts_matrix.tsv                     # Results

# Scripts (numbered for order)
01_download_data.sh
02_preprocess.py
03_run_analysis.py
04_generate_figures.py

# Notebooks (numbered for order)
01_data_exploration.ipynb
02_quality_control.ipynb
03_differential_expression.ipynb

# Figures (descriptive names)
figure1_pca_by_condition.pdf
figure2_volcano_plot.pdf
figure3_heatmap_top_genes.pdf
figureS1_qc_metrics.pdf                    # Supplementary
```

### Variables and Functions

```python
# Python conventions
def calculate_fold_change(treatment, control):
    """Clear function names in snake_case."""
    pass

# Constants in UPPERCASE
PVALUE_THRESHOLD = 0.05
LFC_THRESHOLD = 1.0

# Data variables - descriptive
gene_expression_matrix = ...
significant_genes = ...
enrichment_results = ...
```

### Directories

```
# Lowercase with hyphens or underscores
data/raw/
data/processed/
results/figures/

# NOT
Data/Raw/
RESULTS/
```

---

## Version Control Integration

### What to Track

```
# ALWAYS track
✓ Code (src/, scripts/, notebooks/)
✓ Configuration (config/, environment.yml)
✓ Documentation (README.md, docs/)
✓ Small data files (< 100 KB)
✓ Sample sheets, metadata

# NEVER track (use .gitignore)
✗ Large raw data files
✗ Processed data (regenerable)
✗ Results (regenerable)
✗ Credentials, secrets
✗ Virtual environments
```

### Data Management

```
# For large data files, document in README:

## Data

Raw data files are too large for Git. Download using:

```bash
# From SRA
prefetch SRR1234567 SRR1234568 SRR1234569

# From GEO
wget -r -np -nd https://ftp.ncbi.nlm.nih.gov/geo/...

# From institutional server
rsync -avz user@server:/path/to/data/ data/raw/
```

Alternatively, use Git LFS or DVC for version-controlled large files.
```

---

## Templates

### Minimal Project

```
project/
├── README.md
├── environment.yml
├── data/
│   └── raw/
├── notebooks/
│   └── analysis.ipynb
└── results/
```

### Publishable Project

```
project/
├── README.md              # Comprehensive
├── LICENSE
├── CITATION.cff           # Citation file
├── environment.yml        # Pinned versions
├── Dockerfile             # Container
├── data/
│   ├── raw/README.md      # Data provenance
│   └── processed/
├── notebooks/             # Numbered, documented
├── src/                   # Reusable code
├── scripts/               # Standalone scripts
├── results/
│   └── figures/           # Publication-ready
├── docs/
│   └── methods.md         # Detailed methods
└── tests/                 # Optional but recommended
```

---

## Checklist

```markdown
## Project Setup Checklist

### Structure
- [ ] README.md with setup instructions
- [ ] LICENSE file
- [ ] .gitignore configured
- [ ] environment.yml with pinned versions
- [ ] Logical directory structure

### Data
- [ ] Raw data separated from processed
- [ ] Data provenance documented
- [ ] Sample metadata in structured format
- [ ] External data sources documented

### Code
- [ ] Numbered scripts/notebooks for order
- [ ] Modular, reusable functions in src/
- [ ] Configuration separated from code
- [ ] Comments explaining non-obvious logic

### Documentation
- [ ] Project overview in README
- [ ] Methods documentation
- [ ] Data dictionary for variables
- [ ] Analysis decisions documented

### Reproducibility
- [ ] All dependencies specified
- [ ] Random seeds set
- [ ] Paths are relative
- [ ] Pipeline can run from scratch
```
