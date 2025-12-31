# Version Control for Large Data Reference Guide

> Managing large files and datasets in scientific projects

---

## Overview

Git is not designed for large files. This guide covers tools for versioning large data files alongside code, enabling reproducible data science workflows.

### Tool Comparison

| Feature | Git LFS | DVC | git-annex |
|---------|---------|-----|-----------|
| Complexity | Simple | Medium | Complex |
| Storage | Centralized | Flexible | Flexible |
| Pipelines | No | Yes | No |
| Remote options | Git servers | S3, GCS, SSH, etc. | Many |
| File size limit | ~2 GB | Unlimited | Unlimited |
| Best for | Simple projects | ML pipelines | Large archives |
| Learning curve | Low | Medium | High |

### Decision Tree

```
Do you need data pipeline tracking?
├── Yes → DVC
└── No → Do you need flexible remote storage?
          ├── Yes → DVC or git-annex
          └── No → Git LFS (simplest)
```

---

## Git LFS (Large File Storage)

### Overview
- Simple extension to Git for large files
- Files stored on Git server (GitHub, GitLab, etc.)
- Seamless integration with standard Git workflow

### Setup

```bash
# Install (macOS)
brew install git-lfs

# Install (Ubuntu)
apt-get install git-lfs

# Initialize in repository
git lfs install
```

### Track Files

```bash
# Track file patterns
git lfs track "*.fastq.gz"
git lfs track "*.bam"
git lfs track "data/raw/*"

# Check tracking rules
cat .gitattributes

# Result in .gitattributes:
# *.fastq.gz filter=lfs diff=lfs merge=lfs -text
# *.bam filter=lfs diff=lfs merge=lfs -text
```

### Workflow

```bash
# Add files normally
git add data/sample.fastq.gz
git add .gitattributes

# Commit and push
git commit -m "Add raw data"
git push

# Clone includes LFS files
git clone https://github.com/user/repo.git

# Or skip LFS on clone
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/user/repo.git
cd repo
git lfs pull  # Pull LFS files later
```

### Commands

```bash
# List tracked files
git lfs ls-files

# Show file info
git lfs ls-files -s  # With size

# Check status
git lfs status

# Pull specific files
git lfs pull --include="data/raw/*.fastq.gz"

# Fetch without checking out
git lfs fetch

# Prune old versions
git lfs prune
```

### .gitattributes Template

```
# Git LFS tracking rules

# Sequencing data
*.fastq.gz filter=lfs diff=lfs merge=lfs -text
*.fq.gz filter=lfs diff=lfs merge=lfs -text
*.bam filter=lfs diff=lfs merge=lfs -text
*.cram filter=lfs diff=lfs merge=lfs -text

# Large matrices
*.h5 filter=lfs diff=lfs merge=lfs -text
*.hdf5 filter=lfs diff=lfs merge=lfs -text
*.h5ad filter=lfs diff=lfs merge=lfs -text

# Model files
*.pkl filter=lfs diff=lfs merge=lfs -text
*.pt filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text

# Archives
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
```

### Limitations
- GitHub: 2 GB file limit, 1 GB free storage
- GitLab: 5 GB per repo (free tier)
- Cannot track files >2 GB on most servers
- Storage costs for large projects

---

## DVC (Data Version Control)

### Overview
- Git-like version control for data and ML models
- Stores data externally (S3, GCS, SSH, local)
- Pipeline tracking and reproducibility
- Integrates with MLflow, Weights & Biases

### Setup

```bash
# Install
pip install dvc

# With specific remote support
pip install "dvc[s3]"
pip install "dvc[gdrive]"

# Initialize in git repository
cd my-project
dvc init
git add .dvc .dvcignore
git commit -m "Initialize DVC"
```

### Track Data

```bash
# Track file
dvc add data/raw/sample.fastq.gz

# Creates:
# - data/raw/sample.fastq.gz.dvc (pointer file)
# - Updates .gitignore

# Track directory
dvc add data/raw/

# Add to git
git add data/raw/.gitignore
git add data/raw/sample.fastq.gz.dvc
git commit -m "Track raw data with DVC"
```

### Configure Remote Storage

```bash
# S3
dvc remote add -d myremote s3://mybucket/dvc-storage
dvc remote modify myremote region us-east-1

# Google Cloud Storage
dvc remote add -d myremote gs://mybucket/dvc-storage

# SSH/SFTP
dvc remote add -d myremote ssh://user@server/path/to/dvc-storage

# Local directory
dvc remote add -d myremote /mnt/shared/dvc-storage

# Google Drive
dvc remote add -d myremote gdrive://folder_id

# Azure Blob
dvc remote add -d myremote azure://container/dvc-storage
```

### Push and Pull

```bash
# Push data to remote
dvc push

# Pull data from remote
dvc pull

# Pull specific files
dvc pull data/raw/sample.fastq.gz.dvc

# Fetch without checkout
dvc fetch

# Check status
dvc status
```

### Pipelines

```yaml
# dvc.yaml - Pipeline definition
stages:
  preprocess:
    cmd: python src/preprocess.py --input data/raw --output data/processed
    deps:
      - data/raw
      - src/preprocess.py
    outs:
      - data/processed

  train:
    cmd: python src/train.py --data data/processed --model models/model.pkl
    deps:
      - data/processed
      - src/train.py
    params:
      - train.epochs
      - train.learning_rate
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py --model models/model.pkl --output results/
    deps:
      - models/model.pkl
      - src/evaluate.py
    metrics:
      - results/metrics.json:
          cache: false
    plots:
      - results/confusion_matrix.csv
```

```yaml
# params.yaml - Parameters
train:
  epochs: 100
  learning_rate: 0.001
  batch_size: 32
```

### Run Pipeline

```bash
# Run full pipeline
dvc repro

# Run specific stage
dvc repro train

# Force rerun
dvc repro -f train

# Show pipeline status
dvc status

# Visualize pipeline
dvc dag
```

### Experiments

```bash
# Run experiment with different parameters
dvc exp run --set-param train.learning_rate=0.01

# Compare experiments
dvc exp show

# Apply experiment to workspace
dvc exp apply exp-abc123

# Push experiments
dvc exp push origin
```

### Integration with Git

```bash
# Typical workflow
git checkout -b new-feature
dvc repro  # Run pipeline
dvc push   # Push data
git add .
git commit -m "New experiment"
git push

# Switch branches
git checkout main
dvc checkout  # Get data for this branch
```

### .dvc Files

```yaml
# data/raw/sample.fastq.gz.dvc
outs:
- md5: d41d8cd98f00b204e9800998ecf8427e
  size: 1234567890
  path: sample.fastq.gz
```

---

## git-annex

### Overview
- Powerful tool for managing large files
- Supports many remote backends
- Tracks which remotes have which files
- Complex but very flexible

### Setup

```bash
# Install (macOS)
brew install git-annex

# Install (Ubuntu)
apt-get install git-annex

# Initialize
git annex init "laptop"
```

### Add Files

```bash
# Add file to annex
git annex add data/large_file.bam

# Commit
git commit -m "Add large file"

# Get file content
git annex get data/large_file.bam

# Drop file content (free space)
git annex drop data/large_file.bam

# Sync with remotes
git annex sync
```

### Configure Remotes

```bash
# S3 remote
git annex initremote s3remote type=S3 bucket=mybucket

# SSH remote
git annex initremote server type=rsync \
    rsyncurl=user@server:/path/to/annex

# Directory remote
git annex initremote backup type=directory \
    directory=/mnt/backup/annex encryption=none
```

### Workflow

```bash
# Check where files are
git annex whereis data/large_file.bam

# Copy to remote
git annex copy data/large_file.bam --to s3remote

# Get from remote
git annex get data/large_file.bam --from s3remote

# Sync all
git annex sync --content

# Unused data cleanup
git annex unused
git annex dropunused 1-100
```

---

## Comparison Examples

### Simple Project: Git LFS

```bash
# Setup
git init
git lfs install
git lfs track "*.h5ad"
echo "data/processed/*.h5ad" >> .gitignore

# Use
git add data/processed/adata.h5ad
git commit -m "Add processed data"
git push
```

### ML Project: DVC

```bash
# Setup
git init
dvc init
dvc remote add -d storage s3://my-bucket/dvc

# Track data
dvc add data/training_data.parquet
git add data/training_data.parquet.dvc data/.gitignore
git commit -m "Add training data"

# Create pipeline
dvc run -n train \
    -d src/train.py -d data/training_data.parquet \
    -o models/model.pkl \
    python src/train.py

# Push everything
dvc push
git push
```

### Archive Project: git-annex

```bash
# Setup
git init
git annex init

# Add remote
git annex initremote archive type=directory \
    directory=/mnt/archive encryption=none

# Add large files
git annex add data/raw/*.fastq.gz
git commit -m "Add raw data"

# Copy to archive
git annex copy --to archive

# Free local space
git annex drop data/raw/*.fastq.gz
```

---

## Best Practices

### 1. Track Metadata, Not Just Data

```yaml
# data/raw/README.md or metadata.yml
source: "GEO GSE12345"
download_date: "2024-01-15"
download_command: |
  wget -r -np https://ftp.ncbi.nlm.nih.gov/...
md5_checksums:
  sample1.fastq.gz: abc123...
  sample2.fastq.gz: def456...
```

### 2. Use Consistent Naming

```bash
# DVC files
data/raw.dvc           # Directory
data/raw/sample.dvc    # Avoid tracking subdirectories

# Clear organization
data/
├── raw.dvc
├── processed.dvc
└── external.dvc
```

### 3. Document Data Lineage

```bash
# In README.md
## Data

### Raw Data
- Source: GEO GSE12345
- Downloaded: 2024-01-15
- DVC tracked: `dvc pull data/raw.dvc`

### Processed Data
- Generated by: `dvc repro preprocess`
- Depends on: raw data + src/preprocess.py
```

### 4. Ignore Appropriately

```gitignore
# .gitignore for DVC project

# Data files (tracked by DVC)
/data/raw
/data/processed
/models

# But keep DVC files
!/data/raw.dvc
!/data/processed.dvc
!/models.dvc

# DVC internal
/.dvc/cache
/.dvc/tmp
```

### 5. Lock Dependencies

```yaml
# dvc.lock - Automatically generated
# Tracks exact versions of all dependencies

stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
    - path: data/raw
      md5: abc123...
    - path: src/preprocess.py
      md5: def456...
    outs:
    - path: data/processed
      md5: ghi789...
```

---

## Workflow Integration

### GitHub Actions with DVC

```yaml
# .github/workflows/pipeline.yml
name: DVC Pipeline

on:
  push:
    branches: [main]

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install dvc[s3]
          pip install -r requirements.txt

      - name: Configure DVC remote
        run: |
          dvc remote modify myremote \
            access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
          dvc remote modify myremote \
            secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Pull data
        run: dvc pull

      - name: Run pipeline
        run: dvc repro

      - name: Push results
        run: dvc push
```

### Reproducibility Report

```bash
# Generate reproducibility info
dvc version          # DVC version
dvc status           # Data status
dvc dag --md         # Pipeline as Markdown
dvc params diff      # Parameter changes
dvc metrics show     # Current metrics
```

---

## Quick Reference

```bash
# GIT LFS
git lfs install
git lfs track "*.bam"
git lfs push origin main

# DVC
dvc init
dvc add data/raw/
dvc remote add -d storage s3://bucket/path
dvc push
dvc pull
dvc repro

# GIT-ANNEX
git annex init
git annex add large_file
git annex copy --to remote
git annex get large_file
git annex sync
```
