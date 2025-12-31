# Conda Environment Reference Guide

> Environment management for reproducible scientific computing

---

## Overview

Conda is the standard environment manager for bioinformatics and data science. This guide covers environment creation, management, and best practices for reproducibility.

### Conda vs Mamba vs Micromamba

| Tool | Speed | Use Case |
|------|-------|----------|
| Conda | Slow | Standard, included with Anaconda/Miniconda |
| Mamba | Fast | Drop-in replacement, use for complex environments |
| Micromamba | Fastest | Minimal install, CI/CD, containers |

**Recommendation**: Use Mamba for day-to-day work, Micromamba for containers.

---

## Environment Files

### Basic environment.yml

```yaml
name: my-analysis
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - python=3.10
  - numpy
  - pandas
  - matplotlib
```

### Pinned environment.yml (Recommended for Reproducibility)

```yaml
name: rnaseq-analysis
channels:
  - conda-forge
  - bioconda
  - nodefaults  # Exclude defaults for consistency

dependencies:
  # Core Python
  - python=3.10.12
  - pip=23.2.1

  # Data manipulation
  - numpy=1.24.3
  - pandas=2.0.2
  - scipy=1.11.1

  # Visualization
  - matplotlib=3.7.2
  - seaborn=0.12.2

  # Bioinformatics
  - bioconda::star=2.7.10b
  - bioconda::samtools=1.17
  - bioconda::subread=2.0.6

  # Statistics
  - bioconda::bioconductor-deseq2=1.38.0
  - r-base=4.2.3

  # Pip packages (when conda package unavailable)
  - pip:
    - scanpy==1.9.3
    - scvi-tools==0.20.3
```

### Minimal requirements.txt

For pip-only environments or supplementary packages:

```
numpy==1.24.3
pandas==2.0.2
scipy==1.11.1
matplotlib==3.7.2
seaborn==0.12.2
scanpy==1.9.3
```

---

## Creating Environments

### From environment.yml

```bash
# Create environment
conda env create -f environment.yml

# With Mamba (faster)
mamba env create -f environment.yml

# With specific name (override YAML name)
conda env create -f environment.yml -n custom-name

# Update existing environment
conda env update -f environment.yml --prune
```

### From Scratch

```bash
# Create new environment
conda create -n myenv python=3.10

# Activate
conda activate myenv

# Install packages
conda install -c conda-forge numpy pandas matplotlib
conda install -c bioconda star samtools

# For Bioconductor R packages
conda install -c bioconda bioconductor-deseq2
```

### Clone Existing Environment

```bash
# Clone local environment
conda create --clone source-env --name new-env

# Clone from explicit spec
conda list --explicit > spec-file.txt
conda create --name new-env --file spec-file.txt
```

---

## Exporting Environments

### For Sharing (Cross-Platform)

```bash
# Export with version constraints (recommended)
conda env export --from-history > environment.yml

# Result:
# dependencies:
#   - python=3.10
#   - numpy
#   - pandas
```

### For Exact Reproduction (Same Platform)

```bash
# Explicit package URLs and hashes
conda list --explicit > spec-file.txt

# Result:
# @EXPLICIT
# https://conda.anaconda.org/conda-forge/linux-64/python-3.10.12-hd12c33a_0_cpython.conda#...
```

### Full Export (Includes Build Strings)

```bash
# All packages with exact versions and builds
conda env export > environment-full.yml

# Result includes build strings:
# dependencies:
#   - python=3.10.12=hd12c33a_0_cpython
```

### Comparison

| Export Type | Cross-Platform | Exact | Use Case |
|-------------|----------------|-------|----------|
| `--from-history` | Yes | No | Sharing, collaboration |
| Full export | Partial | Yes | Same OS reproduction |
| `--explicit` | No | Yes | Exact same machine/OS |

---

## Managing Environments

### List and Info

```bash
# List all environments
conda env list
conda info --envs

# Show packages in active environment
conda list

# Show packages matching pattern
conda list numpy

# Show environment location
conda info
```

### Activation

```bash
# Activate
conda activate myenv

# Deactivate
conda deactivate

# Activate in script (bash)
source $(conda info --base)/etc/profile.d/conda.sh
conda activate myenv
```

### Removing Environments

```bash
# Remove environment
conda env remove -n myenv

# Remove all packages but keep environment
conda remove -n myenv --all
```

---

## Channel Configuration

### Channel Priority

```yaml
# .condarc file
channels:
  - conda-forge    # Highest priority
  - bioconda
  - defaults       # Lowest priority

channel_priority: strict  # Only use lower channels if package not in higher
```

### In environment.yml

```yaml
channels:
  - conda-forge
  - bioconda
  - nodefaults  # Exclude defaults entirely

dependencies:
  # Use channel::package syntax for specificity
  - conda-forge::numpy=1.24.3
  - bioconda::star=2.7.10b
```

### Bioconda Setup

```bash
# One-time setup for bioconda
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

---

## Best Practices for Reproducibility

### 1. Pin All Versions

```yaml
# BAD - will change over time
dependencies:
  - numpy
  - pandas

# GOOD - reproducible
dependencies:
  - numpy=1.24.3
  - pandas=2.0.2
```

### 2. Use conda-forge as Primary Channel

```yaml
channels:
  - conda-forge
  - bioconda
  - nodefaults  # Avoid mixing with defaults
```

### 3. Separate Development and Runtime

```yaml
# environment.yml (runtime only)
name: analysis
dependencies:
  - python=3.10
  - numpy=1.24.3

# environment-dev.yml (includes dev tools)
name: analysis-dev
dependencies:
  - python=3.10
  - numpy=1.24.3
  - pytest
  - black
  - jupyter
```

### 4. Lock Files for CI/CD

```bash
# Generate lock file
conda-lock -f environment.yml -p linux-64 -p osx-64

# Creates: conda-lock.yml

# Install from lock file
conda-lock install conda-lock.yml
```

### 5. Document Environment Creation

```bash
# README.md or INSTALL.md

## Installation

### Option 1: Conda/Mamba
```bash
mamba env create -f environment.yml
conda activate analysis
```

### Option 2: From lock file (exact)
```bash
conda-lock install -n analysis conda-lock.yml
conda activate analysis
```
```

---

## Troubleshooting

### Solving Takes Forever

```bash
# Use Mamba instead
mamba env create -f environment.yml

# Or use libmamba solver with conda
conda config --set solver libmamba
```

### Conflict Resolution

```bash
# Check for conflicts
conda install package --dry-run

# Create minimal environment and add packages one by one
conda create -n test python=3.10
conda activate test
conda install numpy  # Check each package
```

### Platform-Specific Packages

```yaml
# Use selectors for platform-specific packages
dependencies:
  - python=3.10
  - numpy=1.24.3
  # Linux-only packages
  - cudatoolkit=11.8  # [linux]
  # macOS-only
  - libomp  # [osx]
```

### Pip Inside Conda

```yaml
dependencies:
  - python=3.10
  - pip
  - pip:
    # Always put pip packages last
    # Use exact versions
    - some-package==1.2.3

# Better: check if conda-forge has the package first
# conda search -c conda-forge package-name
```

---

## Environment for Different Scenarios

### RNA-seq Analysis

```yaml
name: rnaseq
channels:
  - conda-forge
  - bioconda
  - nodefaults

dependencies:
  - python=3.10.12
  - r-base=4.2.3

  # Alignment
  - star=2.7.10b
  - samtools=1.17
  - subread=2.0.6  # featureCounts

  # QC
  - fastqc=0.12.1
  - multiqc=1.14

  # Python analysis
  - numpy=1.24.3
  - pandas=2.0.2
  - matplotlib=3.7.2
  - seaborn=0.12.2

  # R analysis
  - bioconductor-deseq2=1.38.0
  - bioconductor-edger=3.40.0
  - r-pheatmap=1.0.12

  - pip:
    - pydeseq2==0.4.0
```

### Single-Cell Analysis

```yaml
name: singlecell
channels:
  - conda-forge
  - bioconda
  - nodefaults

dependencies:
  - python=3.10.12

  # Core
  - scanpy=1.9.3
  - anndata=0.9.1

  # Preprocessing
  - cellranger=7.1.0  # [linux]

  # Analysis
  - numpy=1.24.3
  - scipy=1.11.1
  - scikit-learn=1.3.0

  # Visualization
  - matplotlib=3.7.2
  - seaborn=0.12.2

  # GPU support (optional)
  - pytorch=2.0.1
  - cudatoolkit=11.8  # [linux]

  - pip:
    - scvi-tools==0.20.3
    - cell2location==0.1.3
```

### Structural Biology

```yaml
name: structural
channels:
  - conda-forge
  - bioconda
  - salilab  # For IMP, MODELLER
  - nodefaults

dependencies:
  - python=3.10.12

  # Structure analysis
  - biopython=1.81
  - mdanalysis=2.5.0

  # Visualization
  - pymol-open-source=2.5.0
  - nglview=3.0.3

  # Docking
  - autodock-vina=1.2.3

  # AlphaFold (if running locally)
  - openmm=8.0.0
  - pdbfixer=1.8.1
```

---

## Integration with Other Tools

### Snakemake

```yaml
# Snakefile uses conda environments per rule
rule align:
    conda: "envs/alignment.yml"
    shell: "star ..."

# Run with conda
snakemake --use-conda
```

### Nextflow

```groovy
// nextflow.config
conda.enabled = true

process {
    conda = 'environment.yml'
}
```

### Jupyter

```bash
# Make environment available as kernel
conda activate myenv
python -m ipykernel install --user --name=myenv --display-name="My Analysis"

# Or include in environment.yml
dependencies:
  - ipykernel
  - jupyter
```

---

## Quick Reference Card

```bash
# Create
conda env create -f environment.yml
mamba env create -f environment.yml  # faster

# Activate/Deactivate
conda activate myenv
conda deactivate

# Export
conda env export --from-history > environment.yml  # shareable
conda list --explicit > spec-file.txt              # exact

# Update
conda env update -f environment.yml --prune

# Remove
conda env remove -n myenv

# List
conda env list
conda list

# Search
conda search -c conda-forge package
conda search -c bioconda package

# Install
conda install -c conda-forge package=version
mamba install -c bioconda package=version  # faster

# Clean cache
conda clean --all
```
