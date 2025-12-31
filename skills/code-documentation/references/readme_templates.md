# README Templates

> Templates for different types of scientific projects and repositories

---

## Template Selection Guide

| Project Type | Template | Key Sections |
|--------------|----------|--------------|
| Analysis project | [Analysis README](#analysis-project) | Data, Environment, Workflow |
| Software tool/package | [Software README](#software-tool) | Installation, Usage, API |
| Data repository | [Data README](#data-repository) | Data dictionary, Collection, Terms |
| Research compendium | [Compendium README](#research-compendium) | Paper, Code, Data links |

---

## Analysis Project

For computational analysis projects (e.g., RNA-seq analysis, GWAS, ML experiments).

```markdown
# [Project Title]

Brief description of the analysis and its purpose (2-3 sentences).

## Overview

- **Objective**: What question does this analysis answer?
- **Data**: Brief description of input data
- **Methods**: Key analytical approaches used
- **Output**: Main results/deliverables

## Repository Structure

```
├── data/
│   ├── raw/              # Original, immutable data
│   └── processed/        # Cleaned, transformed data
├── notebooks/            # Jupyter/R Markdown notebooks
├── scripts/              # Reusable Python/R scripts
├── results/
│   ├── figures/          # Generated figures
│   └── tables/           # Generated tables
├── docs/                 # Additional documentation
├── environment.yml       # Conda environment specification
└── README.md
```

## Data Requirements

### Input Data

| File | Description | Source |
|------|-------------|--------|
| `data/raw/counts.csv` | Gene expression counts | GEO: GSE12345 |
| `data/raw/metadata.csv` | Sample annotations | Supplementary Table 1 |

### Data Availability

- Raw sequencing data: [SRA: PRJNA123456](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA123456)
- Processed counts: [GEO: GSE12345](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE12345)

## Environment Setup

### Using Conda (Recommended)

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate project-name
```

### Using pip

```bash
pip install -r requirements.txt
```

### Key Dependencies

- Python 3.9+
- pandas >= 1.4.0
- scanpy >= 1.9.0
- DESeq2 (R, via rpy2)

## Usage

### Quick Start

```bash
# Run complete analysis pipeline
./run_analysis.sh

# Or step by step:
python scripts/01_preprocess.py
python scripts/02_differential_expression.py
python scripts/03_pathway_analysis.py
```

### Notebooks

Execute notebooks in order:

1. `notebooks/01_data_exploration.ipynb` - QC and data overview
2. `notebooks/02_differential_analysis.ipynb` - Statistical testing
3. `notebooks/03_visualization.ipynb` - Generate publication figures

## Results

### Key Findings

- Finding 1: Brief description
- Finding 2: Brief description

### Generated Files

| File | Description |
|------|-------------|
| `results/figures/volcano_plot.pdf` | Differential expression volcano plot |
| `results/tables/significant_genes.csv` | Genes with padj < 0.05 |

## Citation

If you use this analysis, please cite:

```bibtex
@article{author2024,
  title={Paper Title},
  author={Author, First and Author, Second},
  journal={Journal Name},
  year={2024},
  doi={10.1234/example}
}
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Contact

- **Author**: Your Name
- **Email**: your.email@institution.edu
- **Lab**: [Lab Website](https://example.com)
```

---

## Software Tool

For Python/R packages and command-line tools.

```markdown
# PackageName

[![PyPI version](https://badge.fury.io/py/packagename.svg)](https://badge.fury.io/py/packagename)
[![Tests](https://github.com/user/packagename/workflows/Tests/badge.svg)](https://github.com/user/packagename/actions)
[![Documentation](https://readthedocs.org/projects/packagename/badge/?version=latest)](https://packagename.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

One-line description of what the tool does.

Extended description (2-3 sentences) explaining the main use case,
key features, and what makes this tool useful.

## Features

- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Installation

### From PyPI (Recommended)

```bash
pip install packagename
```

### From Conda

```bash
conda install -c conda-forge packagename
```

### From Source

```bash
git clone https://github.com/user/packagename.git
cd packagename
pip install -e .
```

## Quick Start

```python
from packagename import main_function

# Basic usage
result = main_function(input_data)

# With options
result = main_function(
    input_data,
    method="advanced",
    threshold=0.05
)
```

### Command Line

```bash
packagename process input.csv --output results.csv --method advanced
```

## Documentation

Full documentation is available at [packagename.readthedocs.io](https://packagename.readthedocs.io/).

- [Installation Guide](https://packagename.readthedocs.io/installation)
- [User Guide](https://packagename.readthedocs.io/user-guide)
- [API Reference](https://packagename.readthedocs.io/api)
- [Examples](https://packagename.readthedocs.io/examples)

## Examples

### Example 1: Basic Analysis

```python
import packagename as pkg

# Load example data
data = pkg.load_example_data()

# Run analysis
results = pkg.analyze(data)

# Visualize
pkg.plot_results(results)
```

### Example 2: Advanced Workflow

See [examples/advanced_workflow.py](examples/advanced_workflow.py) for a complete
example including preprocessing, analysis, and export.

## Benchmarks

| Method | Dataset Size | Runtime | Memory |
|--------|--------------|---------|--------|
| default | 10,000 genes | 2.3s | 500 MB |
| default | 50,000 genes | 8.1s | 2.1 GB |
| fast | 50,000 genes | 3.2s | 1.8 GB |

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/user/packagename.git
cd packagename
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
```

## Citation

If you use PackageName in your research, please cite:

```bibtex
@software{packagename,
  author = {Author, First and Author, Second},
  title = {PackageName: Brief Description},
  year = {2024},
  url = {https://github.com/user/packagename},
  doi = {10.5281/zenodo.1234567}
}
```

## License

PackageName is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Funding: Grant ABC123 from Funding Agency
- Based on methods from [Original Paper](https://doi.org/10.1234/example)
```

---

## Data Repository

For datasets shared via Zenodo, Figshare, or similar platforms.

```markdown
# Dataset Title

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

Brief description of what this dataset contains and its scientific context.

## Dataset Overview

- **Type**: RNA-seq / Proteomics / Imaging / etc.
- **Organism**: Homo sapiens
- **Samples**: 120 total (60 treatment, 60 control)
- **Format**: CSV, FASTQ, HDF5
- **Size**: 15 GB total
- **Version**: 1.0.0

## Data Description

### Files Included

| File | Format | Size | Description |
|------|--------|------|-------------|
| `counts_matrix.csv` | CSV | 50 MB | Gene-by-sample count matrix |
| `sample_metadata.csv` | CSV | 15 KB | Sample annotations |
| `gene_annotations.csv` | CSV | 2 MB | Gene IDs and symbols |
| `supplementary/` | Various | 100 MB | Additional files |

### Data Dictionary

#### counts_matrix.csv

| Column | Type | Description |
|--------|------|-------------|
| gene_id | string | Ensembl gene ID (ENSG...) |
| sample_001...sample_120 | integer | Raw read counts per sample |

#### sample_metadata.csv

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| sample_id | string | sample_001-120 | Unique sample identifier |
| condition | string | treatment, control | Experimental condition |
| batch | integer | 1-4 | Processing batch |
| age | integer | 25-65 | Donor age in years |
| sex | string | M, F | Donor sex |

## Collection Methods

### Sample Collection

Brief description of how samples were collected (tissue type, collection
protocol, consent procedures).

### Sequencing

- Platform: Illumina NovaSeq 6000
- Read length: 150 bp paired-end
- Depth: ~30 million reads per sample
- Library prep: TruSeq Stranded mRNA

### Processing

Raw reads were processed using the following pipeline:

1. Quality control: FastQC v0.11.9
2. Trimming: Trimmomatic v0.39
3. Alignment: STAR v2.7.10a to GRCh38
4. Quantification: featureCounts v2.0.1

## Usage

### Loading in Python

```python
import pandas as pd

counts = pd.read_csv("counts_matrix.csv", index_col=0)
metadata = pd.read_csv("sample_metadata.csv")
```

### Loading in R

```r
counts <- read.csv("counts_matrix.csv", row.names = 1)
metadata <- read.csv("sample_metadata.csv")
```

## Usage Terms

### License

This dataset is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

### Citation

If you use this dataset, please cite:

```bibtex
@dataset{author2024_dataset,
  author = {Author, First and Author, Second},
  title = {Dataset Title},
  year = {2024},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.1234567}
}
```

And the associated publication:

```bibtex
@article{author2024_paper,
  title = {Paper Title},
  author = {Author, First and Author, Second},
  journal = {Journal Name},
  year = {2024},
  doi = {10.1234/journal.123456}
}
```

## Related Resources

- **Code**: Analysis code at [GitHub](https://github.com/user/analysis-repo)
- **Paper**: Published in [Journal Name](https://doi.org/10.1234/example)
- **Raw data**: FASTQ files at [SRA: PRJNA123456](https://www.ncbi.nlm.nih.gov/bioproject/)

## Contact

- **Corresponding Author**: Name (email@institution.edu)
- **Data Questions**: data-contact@institution.edu

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial release |
```

---

## Research Compendium

For reproducible research packages that accompany a publication.

```markdown
# Research Compendium: [Paper Short Title]

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

This repository contains the data and code for our paper:

> Author, F., Author, S., & Author, T. (2024). *Full Paper Title*.
> Journal Name, Volume(Issue), Pages. <https://doi.org/10.1234/example>

## Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Reproduce the Analysis](#reproduce-the-analysis)
- [Data](#data)
- [Code](#code)
- [Figures](#figures)
- [License](#license)
- [Citation](#citation)

## Overview

Brief summary of the paper's findings and methodology (3-4 sentences).

## Repository Structure

```
├── analysis/
│   ├── 01-data-processing.Rmd    # Data cleaning and preparation
│   ├── 02-statistical-analysis.Rmd
│   └── 03-figures.Rmd            # Generate paper figures
├── data/
│   ├── raw/                      # Original data (read-only)
│   └── derived/                  # Processed data
├── figures/                      # Output figures
├── R/                            # Custom R functions
├── paper/
│   ├── manuscript.Rmd            # Paper source
│   └── references.bib            # Bibliography
├── renv.lock                     # R package versions
└── Makefile                      # Automate analysis
```

## Reproduce the Analysis

### Prerequisites

- R >= 4.2.0
- RStudio (recommended)
- LaTeX distribution (for PDF output)

### Setup

```bash
# Clone repository
git clone https://github.com/user/paper-compendium.git
cd paper-compendium

# Restore R environment
Rscript -e "renv::restore()"
```

### Run Analysis

```bash
# Run all analyses and generate figures
make all

# Or step by step:
make data      # Process raw data
make analysis  # Run statistical analysis
make figures   # Generate figures
make paper     # Compile manuscript
```

### Using Docker

```bash
# Build container
docker build -t paper-compendium .

# Run analysis
docker run -v $(pwd)/output:/output paper-compendium make all
```

## Data

### Raw Data

| File | Description | Source |
|------|-------------|--------|
| `data/raw/dataset.csv` | Main dataset | [DOI link] |

### Processed Data

Generated by `analysis/01-data-processing.Rmd`:

| File | Description |
|------|-------------|
| `data/derived/clean_data.rds` | Cleaned dataset |
| `data/derived/model_input.rds` | Data formatted for modeling |

## Code

### Analysis Scripts

| Script | Purpose |
|--------|---------|
| `analysis/01-data-processing.Rmd` | Clean and prepare data |
| `analysis/02-statistical-analysis.Rmd` | Main statistical analyses |
| `analysis/03-figures.Rmd` | Generate all figures |

### Custom Functions

| Function | File | Purpose |
|----------|------|---------|
| `clean_data()` | `R/data-processing.R` | Standardize input data |
| `run_model()` | `R/modeling.R` | Fit statistical model |
| `theme_paper()` | `R/plotting.R` | Custom ggplot theme |

## Figures

| Figure | Script | Output |
|--------|--------|--------|
| Figure 1 | `analysis/03-figures.Rmd` | `figures/fig1_overview.pdf` |
| Figure 2 | `analysis/03-figures.Rmd` | `figures/fig2_results.pdf` |
| Figure S1 | `analysis/03-figures.Rmd` | `figures/figS1_supplement.pdf` |

## License

- **Code**: MIT License (see `LICENSE-CODE`)
- **Data**: CC BY 4.0 (see `LICENSE-DATA`)
- **Text**: CC BY 4.0 (see `LICENSE-TEXT`)

## Citation

Please cite both the paper and this compendium:

**Paper:**
```bibtex
@article{author2024,
  title = {Paper Title},
  author = {Author, First and Author, Second},
  journal = {Journal Name},
  year = {2024},
  doi = {10.1234/example}
}
```

**Compendium:**
```bibtex
@software{author2024compendium,
  author = {Author, First and Author, Second},
  title = {Research Compendium for: Paper Title},
  year = {2024},
  doi = {10.5281/zenodo.1234567}
}
```

## Contact

- First Author (first.author@institution.edu)
- [Lab Website](https://example.com/lab)

## Acknowledgments

This research was supported by Grant ABC123 from Funding Agency.
```

---

## Quick Reference: Essential Sections

### Must-Have (All Projects)

1. **Title** - Clear, descriptive name
2. **Description** - What it does (1-3 sentences)
3. **Installation/Setup** - How to get started
4. **Usage** - Basic example
5. **License** - Terms of use

### Should-Have (Most Projects)

6. **Dependencies** - Required software/packages
7. **Examples** - Working code examples
8. **Citation** - How to credit the work
9. **Contact** - How to reach maintainers

### Nice-to-Have (Larger Projects)

10. **Badges** - Status indicators
11. **Contributing** - How to contribute
12. **Changelog** - Version history
13. **Acknowledgments** - Credits and funding
