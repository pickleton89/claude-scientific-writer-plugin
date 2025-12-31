# Inline Commenting Guide

> When and how to write effective inline comments in scientific code

---

## Core Principle

> Comments should explain **why**, not **what**.

Good code is self-documenting for the *what*. Comments add value by explaining:
- **Why** a particular approach was chosen
- **Why** a workaround is necessary
- **What** isn't obvious from the code itself

---

## When to Comment

### DO Comment

| Situation | Example |
|-----------|---------|
| **Non-obvious logic** | Complex algorithms, mathematical formulas |
| **Workarounds/hacks** | Fixes for library bugs, edge cases |
| **Business/domain logic** | Scientific rationale, biological constraints |
| **Performance optimizations** | Why a faster but less readable approach |
| **External references** | Links to papers, documentation, issues |
| **Assumptions** | What the code expects to be true |
| **TODO/FIXME** | Known issues, planned improvements |

### DON'T Comment

| Anti-pattern | Example |
|--------------|---------|
| **Restating code** | `i += 1  # increment i` |
| **Obvious operations** | `# open file` before `open()` |
| **Dead/commented code** | Use version control instead |
| **Excessive headers** | Long decorative comment blocks |
| **Outdated information** | Comments that no longer match code |

---

## Comment Types

### Single-Line Comments

```python
# Good: Explains why
threshold = 0.05  # Standard significance level for hypothesis testing

# Bad: Restates what
threshold = 0.05  # Set threshold to 0.05
```

### End-of-Line Comments

Use sparingly for very brief clarifications:

```python
result = np.log2(fold_change + 1)  # +1 pseudocount avoids log(0)
```

### Block Comments

For explaining complex logic:

```python
# Benjamini-Hochberg FDR correction
# We sort p-values and compare each to its rank-adjusted threshold.
# This controls the expected proportion of false discoveries among
# all discoveries, rather than the probability of any false discovery.
```

### Section Comments

Divide long functions/files into logical sections:

```python
# ============================================================
# Data Loading and Validation
# ============================================================

# --- Load raw counts ---
counts = pd.read_csv(counts_file)

# --- Validate sample metadata ---
assert all(metadata['sample_id'].isin(counts.columns))
```

---

## Comment Patterns for Scientific Code

### Mathematical Formulas

```python
# Cohen's d: standardized effect size
# d = (mean1 - mean2) / pooled_std
# where pooled_std = sqrt(((n1-1)*s1² + (n2-1)*s2²) / (n1+n2-2))
pooled_std = np.sqrt(
    ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
)
cohens_d = (mean1 - mean2) / pooled_std
```

### Algorithm References

```python
# Storey's q-value estimation (Storey & Tibshirani, 2003)
# doi:10.1073/pnas.1530509100
# Estimates pi0 (proportion of true nulls) using a cubic spline
```

### Biological/Domain Context

```python
# Filter mitochondrial genes - they often dominate variance in scRNA-seq
# due to cell stress during dissociation, not biological signal
mito_genes = gene_names[gene_names.str.startswith('MT-')]
```

### Parameter Choices

```python
# Perplexity ~30 recommended for datasets of this size (500-5000 cells)
# Lower values emphasize local structure, higher values global structure
# See van der Maaten & Hinton (2008) for guidelines
tsne = TSNE(perplexity=30, random_state=42)
```

### Edge Cases and Workarounds

```python
# Handle edge case where all values in a column are zero
# This occurs for genes with no expression in any sample
if (counts == 0).all():
    log_counts = np.zeros_like(counts)  # Avoid log(0)
else:
    log_counts = np.log2(counts + 1)
```

### Library-Specific Workarounds

```python
# Workaround for scipy issue #12345: mannwhitneyu returns NaN
# when all values in one group are identical
if np.std(group1) == 0 or np.std(group2) == 0:
    return np.nan, 1.0  # No test possible
```

---

## TODO/FIXME/XXX Comments

### Conventions

| Tag | Meaning |
|-----|---------|
| `TODO` | Planned enhancement |
| `FIXME` | Known bug that needs fixing |
| `XXX` | Warning, danger, or hack |
| `HACK` | Temporary workaround |
| `NOTE` | Important information |
| `REVIEW` | Needs code review |

### Format

Include your identifier and optionally a date/issue:

```python
# TODO(username): Add support for paired samples
# FIXME(jsmith): This fails when n < 3, see issue #42
# XXX: This is O(n²), will be slow for large datasets
# HACK: Temporary fix until scipy 1.12 is released
```

### Finding TODOs

```bash
# Find all TODOs in project
grep -rn "TODO\|FIXME\|XXX\|HACK" --include="*.py" .

# With rg (ripgrep)
rg "TODO|FIXME|XXX|HACK" --type py
```

---

## Language-Specific Guidelines

### Python

```python
# Single line comment (preferred for most cases)
x = 1

"""
Multi-line strings are NOT comments.
Use for docstrings only.
"""

# For multi-line explanations, use multiple # lines
# This is clearer than a docstring
# and more explicit as a comment
```

### R

```r
# Single line comment
x <- 1

# Multi-line comments: just use multiple #
# R has no block comment syntax
# This is the standard approach
```

### SQL (in scripts)

```sql
-- Single line comment
SELECT * FROM table;

/*
   Block comment for longer explanations
   Useful for complex queries
*/
```

---

## Comment Maintenance

### Keeping Comments Updated

Comments that don't match code are worse than no comments:

```python
# BAD: Comment doesn't match code
# Filter genes with mean expression > 10
filtered = data[data.mean(axis=1) > 5]  # Actually filters > 5!

# GOOD: Keep in sync, or remove if obvious
filtered = data[data.mean(axis=1) > 5]
```

### When Refactoring

- Update comments when you change code
- Delete comments that no longer apply
- Consider if code can be made clearer instead of commented

---

## Self-Documenting Code Alternatives

Often, better naming eliminates the need for comments:

### Variable Names

```python
# BAD
x = 0.05  # significance threshold
if p < x:
    ...

# GOOD
significance_threshold = 0.05
if p < significance_threshold:
    ...
```

### Function Names

```python
# BAD
def process(data):
    # Remove rows with missing values and normalize
    ...

# GOOD
def remove_missing_and_normalize(data):
    ...
```

### Extract to Named Functions

```python
# BAD
# Calculate fold change with pseudocount
fc = (treatment + 1) / (control + 1)

# GOOD
def calculate_fold_change(treatment, control, pseudocount=1):
    """Calculate fold change with pseudocount to avoid division by zero."""
    return (treatment + pseudocount) / (control + pseudocount)

fc = calculate_fold_change(treatment, control)
```

### Constants

```python
# BAD
if coverage > 30:  # Minimum coverage threshold

# GOOD
MIN_COVERAGE_THRESHOLD = 30
if coverage > MIN_COVERAGE_THRESHOLD:
```

---

## Comment Quality Checklist

Good comments should be:

- [ ] **Accurate** - Matches what the code actually does
- [ ] **Necessary** - Can't be replaced by better naming
- [ ] **Concise** - As short as possible while being clear
- [ ] **Maintained** - Updated when code changes
- [ ] **Valuable** - Adds information not in the code

---

## Examples: Before and After

### Example 1: Over-Commented

```python
# BAD: Too many obvious comments
# Import pandas library
import pandas as pd

# Load the data from CSV file
data = pd.read_csv("data.csv")

# Get the number of rows
n_rows = len(data)

# Print the number of rows
print(n_rows)
```

```python
# GOOD: Only comment what's not obvious
import pandas as pd

data = pd.read_csv("data.csv")
print(f"Loaded {len(data)} rows")
```

### Example 2: Under-Commented

```python
# BAD: Complex logic with no explanation
mask = ((x > np.percentile(x, 5)) &
        (x < np.percentile(x, 95)) &
        (~np.isnan(y)) &
        (y > 0))
```

```python
# GOOD: Explain the filtering criteria
# Remove outliers (outside 5th-95th percentile) and invalid entries
# (missing y values or non-positive y) before correlation analysis
mask = ((x > np.percentile(x, 5)) &
        (x < np.percentile(x, 95)) &
        (~np.isnan(y)) &
        (y > 0))
```

### Example 3: Balancing Comments

```python
# GOOD: Right balance for scientific code
def calculate_adjusted_pvalues(pvalues, method='fdr_bh'):
    """
    Apply multiple testing correction to p-values.

    Parameters
    ----------
    pvalues : array-like
        Raw p-values from statistical tests.
    method : str, default 'fdr_bh'
        Correction method: 'fdr_bh' (Benjamini-Hochberg),
        'bonferroni', or 'holm'.

    Returns
    -------
    np.ndarray
        Adjusted p-values.
    """
    pvalues = np.asarray(pvalues)

    # Handle edge case: all p-values are NaN (e.g., no valid tests)
    if np.all(np.isnan(pvalues)):
        return pvalues

    # Benjamini-Hochberg: controls FDR (expected false discovery rate)
    # More powerful than Bonferroni for large numbers of tests
    _, padj, _, _ = multipletests(pvalues, method=method)

    return padj
```

---

## Summary

| Guideline | Do | Don't |
|-----------|-----|-------|
| **Purpose** | Explain *why* | Explain *what* |
| **Necessity** | Add new information | Restate the obvious |
| **Accuracy** | Keep in sync with code | Leave outdated comments |
| **Length** | Be concise | Write essays |
| **Alternatives** | Use clear naming first | Comment unclear code |
| **TODOs** | Include name/issue | Leave anonymous |
