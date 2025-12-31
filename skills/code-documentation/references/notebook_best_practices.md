# Notebook Best Practices

> Guidelines for Jupyter, R Markdown, and Quarto notebooks in scientific research

---

## Overview

Computational notebooks combine code, output, and narrative in a single document. This guide covers best practices for creating reproducible, readable, and maintainable notebooks.

| Format | Language | Output Formats | Best For |
|--------|----------|----------------|----------|
| Jupyter (.ipynb) | Python, R, Julia | HTML, PDF, slides | Interactive exploration, Python |
| R Markdown (.Rmd) | R, Python, SQL | HTML, PDF, Word, slides | R-centric analysis, reports |
| Quarto (.qmd) | Python, R, Julia, Observable | HTML, PDF, Word, slides, books | Multi-language, modern projects |

---

## Notebook Structure

### Standard Sections

Every analysis notebook should include:

```markdown
# Title: Descriptive Analysis Name

## Purpose
What question does this notebook answer? What is its role in the project?

## Setup
Import packages, set parameters, load data.

## [Analysis Sections]
Numbered or named sections for each analytical step.

## Summary / Conclusions
Key findings, next steps.

## Session Info
Software versions for reproducibility.
```

### Section Organization

```
1. Title & Purpose
   └── Clear description of notebook goals

2. Setup
   ├── Package imports
   ├── Parameter definitions
   ├── File paths
   └── Data loading

3. Data Exploration (if applicable)
   ├── Data structure
   ├── Summary statistics
   └── Quality checks

4. Main Analysis
   ├── Step 1: [Descriptive name]
   ├── Step 2: [Descriptive name]
   └── Step N: [Descriptive name]

5. Results
   ├── Key figures
   ├── Summary tables
   └── Statistical results

6. Conclusions
   ├── Summary of findings
   ├── Limitations
   └── Next steps

7. Session Info
```

---

## Code Cell Best Practices

### Cell Organization

**One concept per cell:**

```python
# GOOD: Single, focused cell
# Load and preprocess data
data = pd.read_csv("data/raw/counts.csv", index_col=0)
data = data.dropna()
data = data[data.sum(axis=1) > 10]  # Filter low counts
print(f"Loaded {data.shape[0]} genes, {data.shape[1]} samples")
```

```python
# BAD: Too much in one cell
data = pd.read_csv("data/raw/counts.csv", index_col=0)
data = data.dropna()
data = data[data.sum(axis=1) > 10]
normalized = normalize_counts(data)
de_results = run_differential_expression(normalized, metadata)
significant = de_results[de_results['padj'] < 0.05]
volcano_plot(de_results)
export_results(significant, "results/significant_genes.csv")
```

### Cell Size Guidelines

| Cell Type | Recommended Lines | Purpose |
|-----------|-------------------|---------|
| Import | 5-15 | All imports in one cell |
| Data loading | 5-10 | Load and initial inspection |
| Analysis | 10-25 | One analytical step |
| Visualization | 10-30 | One figure |
| Summary | 3-10 | Print key results |

### Markdown Integration

Use markdown cells to explain:

```markdown
## Differential Expression Analysis

We use DESeq2 to identify genes differentially expressed between
treatment and control conditions. Key parameters:

- **FDR threshold**: 0.05
- **Log2 fold change threshold**: 1.0 (2-fold change)
- **Method**: Wald test with BH correction

The following cell runs the analysis...
```

Then the code cell:

```python
# Run DESeq2 analysis
de_results = run_deseq2(counts, metadata, design="~ condition")
significant = de_results.query("padj < 0.05 and abs(log2FoldChange) > 1")
print(f"Found {len(significant)} significant genes")
```

---

## Reproducibility

### Random Seeds

Set seeds at the start of the notebook:

```python
# Python
import numpy as np
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# If using PyTorch
import torch
torch.manual_seed(SEED)

# If using TensorFlow
import tensorflow as tf
tf.random.set_seed(SEED)
```

```r
# R
set.seed(42)
```

### Version Tracking

**Python with watermark:**

```python
%load_ext watermark
%watermark -v -p numpy,pandas,scipy,matplotlib,seaborn
```

Output:
```
Python implementation: CPython
Python version       : 3.10.12
numpy      : 1.24.3
pandas     : 2.0.2
scipy      : 1.10.1
matplotlib : 3.7.1
seaborn    : 0.12.2
```

**R with sessionInfo:**

```r
sessionInfo()
```

### File Paths

Use relative paths and define them at the top:

```python
# GOOD: Paths defined at top, relative to notebook
from pathlib import Path

# Project structure
PROJECT_ROOT = Path("..")
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# Create directories if needed
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Use throughout notebook
counts = pd.read_csv(DATA_DIR / "raw" / "counts.csv")
```

```python
# BAD: Hardcoded absolute paths
counts = pd.read_csv("/Users/name/projects/analysis/data/raw/counts.csv")
```

### Environment Documentation

Include environment file reference:

```markdown
## Environment

This analysis was run with the following environment:

```bash
conda env create -f environment.yml
conda activate analysis-env
```

See `environment.yml` for full package specifications.
```

---

## Output Management

### Controlling Output Visibility

**Jupyter:**

```python
# Suppress output
_ = long_computation()

# Show only specific output
result = analysis()
result.head()  # Only show first few rows
```

**Quarto:**

```{python}
#| echo: false      # Hide code, show output
#| output: false    # Show code, hide output
#| include: false   # Hide both code and output
```

**R Markdown:**

```{r, echo=FALSE}
# Hide code, show output
```

```{r, results='hide'}
# Show code, hide output
```

```{r, include=FALSE}
# Hide both
```

### Large Output Handling

```python
# Limit DataFrame display
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 10)

# Sample large datasets for display
large_df.sample(10)

# Or use head/tail
large_df.head(10)
```

### Figure Display

```python
# Consistent figure sizing
import matplotlib.pyplot as plt

# Set defaults at top of notebook
plt.rcParams['figure.figsize'] = [8, 6]
plt.rcParams['figure.dpi'] = 100

# For publication figures
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
```

---

## Jupyter-Specific

### Magic Commands

```python
# Useful magics
%matplotlib inline          # Display plots inline
%load_ext autoreload       # Auto-reload changed modules
%autoreload 2

# Timing
%time slow_function()      # Time single execution
%timeit fast_function()    # Time multiple executions

# Debugging
%debug                     # Enter debugger after exception
%pdb on                    # Always enter debugger on exception
```

### Notebook Extensions

Recommended extensions (via jupyter_contrib_nbextensions):

| Extension | Purpose |
|-----------|---------|
| Table of Contents | Navigate long notebooks |
| Variable Inspector | View defined variables |
| ExecuteTime | Show cell execution time |
| Collapsible Headings | Collapse sections |
| Code Folding | Fold long code blocks |

### Converting Notebooks

```bash
# To Python script
jupyter nbconvert --to script notebook.ipynb

# To HTML (with code)
jupyter nbconvert --to html notebook.ipynb

# To HTML (no code)
jupyter nbconvert --to html --no-input notebook.ipynb

# To PDF (requires LaTeX)
jupyter nbconvert --to pdf notebook.ipynb

# Execute and convert
jupyter nbconvert --execute --to html notebook.ipynb
```

---

## R Markdown-Specific

### YAML Header

```yaml
---
title: "Analysis Title"
author: "Your Name"
date: "`r Sys.Date()`"
output:
  html_document:
    toc: true
    toc_float: true
    code_folding: hide
    theme: cosmo
    df_print: paged
---
```

### Setup Chunk

```{r setup, include=FALSE}
knitr::opts_chunk$set(
  echo = TRUE,
  message = FALSE,
  warning = FALSE,
  fig.width = 8,
  fig.height = 6,
  fig.path = "figures/"
)

# Load packages
library(tidyverse)
library(DESeq2)
```

### Chunk Options

| Option | Values | Effect |
|--------|--------|--------|
| `echo` | TRUE/FALSE | Show/hide code |
| `eval` | TRUE/FALSE | Run/skip code |
| `include` | TRUE/FALSE | Include in output |
| `message` | TRUE/FALSE | Show messages |
| `warning` | TRUE/FALSE | Show warnings |
| `fig.cap` | "text" | Figure caption |
| `cache` | TRUE/FALSE | Cache results |

### Inline Code

```markdown
We identified `r nrow(significant)` significant genes
with FDR < `r threshold`.
```

---

## Quarto-Specific

### YAML Header

```yaml
---
title: "Analysis Title"
author: "Your Name"
date: today
format:
  html:
    toc: true
    code-fold: true
    code-tools: true
execute:
  echo: true
  warning: false
---
```

### Cell Options

```{python}
#| label: fig-volcano
#| fig-cap: "Volcano plot of differential expression results"
#| fig-width: 8
#| fig-height: 6

volcano_plot(de_results)
```

### Cross-References

```markdown
As shown in @fig-volcano, most genes...

See @tbl-significant for the complete list.
```

### Callouts

```markdown
::: {.callout-note}
## Key Finding
The treatment group showed significant upregulation...
:::

::: {.callout-warning}
## Caveat
These results should be validated with...
:::
```

---

## Common Mistakes

### 1. Non-Linear Execution

```python
# BAD: Cells depend on execution order that isn't top-to-bottom
# Cell 5 defines 'data', Cell 3 uses it

# GOOD: Clear dependencies, runnable top-to-bottom
# Restart kernel and run all before sharing
```

### 2. Hidden State

```python
# BAD: Variable modified in one cell, used elsewhere
data = load_data()
# ... many cells later ...
data = data.dropna()  # Changes data for cells above if re-run

# GOOD: Create new variables for transformations
data_raw = load_data()
data_clean = data_raw.dropna()
```

### 3. Missing Imports

```python
# BAD: Imports scattered throughout
x = np.array([1, 2, 3])  # Where is numpy imported?

# GOOD: All imports at top
import numpy as np
import pandas as pd
# ... all other imports ...
```

### 4. Absolute Paths

```python
# BAD
data = pd.read_csv("/Users/name/project/data/file.csv")

# GOOD
from pathlib import Path
DATA_DIR = Path("../data")
data = pd.read_csv(DATA_DIR / "file.csv")
```

### 5. No Narrative

```python
# BAD: Just code cells with no explanation

# GOOD: Markdown cells explaining the why and what
```

---

## Notebook Hygiene Checklist

Before sharing or committing:

- [ ] **Restart and run all** - Ensure linear execution works
- [ ] **Clear outputs** (optional) - Reduce file size, avoid diffs
- [ ] **Check paths** - All relative, no hardcoded user directories
- [ ] **Verify seeds** - Random operations reproducible
- [ ] **Review output** - No sensitive data, appropriate detail level
- [ ] **Add session info** - Package versions documented
- [ ] **Write conclusions** - Summarize findings
- [ ] **Review markdown** - Narrative is clear and complete

### Clearing Outputs

```bash
# Jupyter
jupyter nbconvert --clear-output --inplace notebook.ipynb

# Or with nbstripout (pre-commit hook)
pip install nbstripout
nbstripout notebook.ipynb
```

---

## Notebook vs Script Decision

| Choose Notebook When | Choose Script When |
|---------------------|-------------------|
| Exploratory analysis | Production pipeline |
| Teaching/tutorials | Batch processing |
| Interactive visualization | CLI tool |
| Report generation | Large codebase |
| One-off analysis | Reusable module |

### Extracting Code from Notebooks

When analysis matures, extract reusable code:

```
notebooks/
├── 01_exploration.ipynb      # Keep as notebook
├── 02_analysis.ipynb         # Keep as notebook, import from scripts
scripts/
├── preprocessing.py          # Extracted reusable functions
├── analysis.py               # Core analysis functions
└── visualization.py          # Plotting functions
```

In notebook:

```python
# Import project modules
import sys
sys.path.append("..")
from scripts.preprocessing import clean_data
from scripts.analysis import run_model
```
