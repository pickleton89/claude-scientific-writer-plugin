# Python Docstring Reference

> Comprehensive guide to Python documentation styles for scientific code

---

## Style Comparison

| Feature | NumPy Style | Google Style |
|---------|-------------|--------------|
| Verbosity | More detailed | More concise |
| Ecosystem | numpy, scipy, pandas, scikit-learn | General Python, TensorFlow |
| Section headers | Underlined (`---`) | Indented with colon |
| Best for | Scientific/numerical code | General applications |
| Sphinx extension | `sphinx.ext.napoleon` | `sphinx.ext.napoleon` |

**Recommendation**: Use NumPy style for scientific Python code to match the ecosystem conventions.

---

## NumPy Style (Recommended for Scientific Code)

### Function Template

```python
def calculate_fold_change(treatment: np.ndarray,
                          control: np.ndarray,
                          log2: bool = True,
                          pseudocount: float = 1.0) -> np.ndarray:
    """
    Calculate fold change between treatment and control conditions.

    Computes the ratio of treatment to control values, optionally
    log2-transformed. Adds pseudocount to avoid division by zero
    and log of zero.

    Parameters
    ----------
    treatment : np.ndarray
        Expression values for treatment condition. Shape (n_genes,)
        or (n_genes, n_samples).
    control : np.ndarray
        Expression values for control condition. Must match treatment shape.
    log2 : bool, optional
        If True, return log2 fold change. Default is True.
    pseudocount : float, optional
        Value added before division/log. Default is 1.0.

    Returns
    -------
    np.ndarray
        Fold change values. Same shape as input arrays.

    Raises
    ------
    ValueError
        If treatment and control shapes don't match.

    See Also
    --------
    scipy.stats.ttest_ind : Statistical test for fold change significance.
    normalize_counts : Normalize raw counts before fold change calculation.

    Notes
    -----
    Log2 fold change interpretation:
    - LFC = 1 means 2-fold increase
    - LFC = -1 means 2-fold decrease
    - LFC = 0 means no change

    For RNA-seq data, consider using DESeq2 or edgeR shrinkage estimators
    for more robust fold change estimates.

    References
    ----------
    .. [1] Love MI, Huber W, Anders S. "Moderated estimation of fold change
       and dispersion for RNA-seq data with DESeq2." Genome Biology, 2014.

    Examples
    --------
    >>> import numpy as np
    >>> treatment = np.array([10, 20, 5])
    >>> control = np.array([5, 10, 10])
    >>> calculate_fold_change(treatment, control)
    array([ 1., 1., -1.])

    With raw fold change (not log2):
    >>> calculate_fold_change(treatment, control, log2=False)
    array([2. , 2. , 0.5])
    """
    if treatment.shape != control.shape:
        raise ValueError(f"Shape mismatch: {treatment.shape} vs {control.shape}")

    fc = (treatment + pseudocount) / (control + pseudocount)

    if log2:
        return np.log2(fc)
    return fc
```

### Class Template

```python
class DifferentialExpression:
    """
    Container for differential expression analysis results.

    Stores results from differential expression analysis and provides
    methods for filtering, visualization, and export. Designed to work
    with output from DESeq2, edgeR, or limma.

    Parameters
    ----------
    gene_ids : array-like
        Gene identifiers (Ensembl IDs or symbols).
    log2fc : array-like
        Log2 fold change values.
    pvalues : array-like
        Raw p-values from statistical test.
    padj : array-like, optional
        Adjusted p-values (FDR). If not provided, computed using
        Benjamini-Hochberg correction.
    gene_names : array-like, optional
        Gene symbols for display. If not provided, uses gene_ids.

    Attributes
    ----------
    results : pd.DataFrame
        Combined results DataFrame with all columns.
    n_genes : int
        Total number of genes tested.
    n_significant : int
        Number of genes passing default thresholds (padj < 0.05, |LFC| > 1).

    Methods
    -------
    get_significant(padj_threshold=0.05, lfc_threshold=1.0)
        Return subset of significant genes.
    volcano_plot(ax=None, **kwargs)
        Generate volcano plot of results.
    to_csv(path)
        Export results to CSV file.

    See Also
    --------
    run_deseq2 : Run DESeq2 analysis to generate these results.
    EnrichmentAnalysis : Perform pathway enrichment on significant genes.

    Examples
    --------
    >>> de = DifferentialExpression(
    ...     gene_ids=['ENSG00000141510', 'ENSG00000171862', 'ENSG00000136997'],
    ...     log2fc=[2.5, -1.2, 0.1],
    ...     pvalues=[0.001, 0.02, 0.8],
    ...     gene_names=['TP53', 'PTEN', 'MYC']
    ... )
    >>> de.n_significant
    1
    >>> sig_genes = de.get_significant(padj_threshold=0.05, lfc_threshold=1.0)
    >>> sig_genes['gene_names'].tolist()
    ['TP53']
    """

    def __init__(self, gene_ids, log2fc, pvalues, padj=None, gene_names=None):
        """Initialize DifferentialExpression with analysis results."""
        self.gene_ids = np.asarray(gene_ids)
        self.log2fc = np.asarray(log2fc)
        self.pvalues = np.asarray(pvalues)
        # ... implementation
```

### Module Docstring

```python
"""
Differential expression analysis utilities.

This module provides functions and classes for analyzing differential
gene expression from RNA-seq experiments. It includes utilities for:

- Fold change calculation with various normalization methods
- Multiple testing correction
- Result filtering and export
- Visualization (volcano plots, MA plots, heatmaps)

The module is designed to work with output from DESeq2, edgeR, or limma,
and follows conventions from the Bioconductor ecosystem.

Examples
--------
Basic usage with DESeq2 results:

>>> from diffexp import DifferentialExpression, volcano_plot
>>> de = DifferentialExpression.from_deseq2("deseq2_results.csv")
>>> significant = de.get_significant(padj_threshold=0.01)
>>> volcano_plot(de, highlight=significant.gene_ids)

Notes
-----
This module requires numpy, pandas, and matplotlib. For full functionality,
scipy and statsmodels are also recommended.

See Also
--------
statsmodels.stats.multitest : Multiple testing correction methods.
scipy.stats : Statistical tests for custom analyses.
"""
```

---

## Google Style

### Function Template

```python
def calculate_fold_change(treatment: np.ndarray,
                          control: np.ndarray,
                          log2: bool = True,
                          pseudocount: float = 1.0) -> np.ndarray:
    """Calculate fold change between treatment and control conditions.

    Computes the ratio of treatment to control values, optionally
    log2-transformed.

    Args:
        treatment: Expression values for treatment condition.
            Shape (n_genes,) or (n_genes, n_samples).
        control: Expression values for control condition.
            Must match treatment shape.
        log2: If True, return log2 fold change. Defaults to True.
        pseudocount: Value added before division/log to avoid
            division by zero. Defaults to 1.0.

    Returns:
        Fold change values with same shape as input arrays.

    Raises:
        ValueError: If treatment and control shapes don't match.

    Example:
        >>> treatment = np.array([10, 20, 5])
        >>> control = np.array([5, 10, 10])
        >>> calculate_fold_change(treatment, control)
        array([ 1., 1., -1.])
    """
```

### Class Template

```python
class DifferentialExpression:
    """Container for differential expression analysis results.

    Stores and provides access to differential expression results with
    methods for filtering and visualization.

    Attributes:
        results: DataFrame containing all analysis results.
        n_genes: Total number of genes tested.
        n_significant: Number of significant genes (default thresholds).

    Example:
        >>> de = DifferentialExpression(gene_ids, log2fc, pvalues)
        >>> significant = de.get_significant(padj_threshold=0.05)
    """
```

---

## Section Reference

### NumPy Style Sections (in order)

| Section | Required | Content |
|---------|----------|---------|
| Short summary | Yes | One line, imperative mood ("Calculate...", "Return...") |
| Deprecation warning | If deprecated | `.. deprecated:: 1.0` |
| Extended summary | If needed | Paragraph(s) explaining details |
| Parameters | If any | `name : type` with description |
| Returns | If returns value | `type` with description |
| Yields | If generator | `type` with description |
| Receives | If generator with send() | `type` with description |
| Other Parameters | If many params | Less common parameters |
| Raises | If raises exceptions | `ExceptionType` with when |
| Warns | If issues warnings | `WarningType` with when |
| Warnings | General warnings | Free-form text |
| See Also | Related functions | `function_name : One-line description` |
| Notes | Implementation details | Free-form, can include math |
| References | Citations | Numbered list with `.. [1]` |
| Examples | Recommended | Doctest-compatible code |

### Parameter Type Conventions

```python
"""
Parameters
----------
x : int
    Simple type.
y : float, optional
    Optional with default (mention in description).
z : {"option1", "option2"}, default "option1"
    Enumerated options.
arr : array-like
    Anything that can become an array.
data : DataFrame or dict
    Multiple accepted types.
callback : callable
    Function or method.
*args : tuple
    Variable positional arguments.
**kwargs : dict
    Variable keyword arguments.
"""
```

---

## Type Hints Integration

### Modern Python (3.9+) with Docstrings

```python
from typing import Optional, Union
import numpy as np
import pandas as pd


def process_data(
    data: pd.DataFrame,
    columns: list[str],
    threshold: float = 0.05,
    method: str = "fdr_bh",
    inplace: bool = False
) -> Optional[pd.DataFrame]:
    """
    Process data with multiple testing correction.

    Parameters
    ----------
    data : pd.DataFrame
        Input data with p-values to correct.
    columns : list of str
        Column names containing p-values.
    threshold : float, default 0.05
        Significance threshold after correction.
    method : {"fdr_bh", "bonferroni", "holm"}, default "fdr_bh"
        Correction method to apply.
    inplace : bool, default False
        If True, modify data in place and return None.

    Returns
    -------
    pd.DataFrame or None
        Processed DataFrame with adjusted p-values, or None if inplace=True.
    """
```

### Note on Type Hints vs Docstrings

- Type hints: Machine-readable, for type checkers (mypy, pyright)
- Docstrings: Human-readable, for documentation and help()
- **Include both**: Type hints in signature, types in docstrings for clarity
- **Don't duplicate excessively**: If types are complex, docstring can focus on semantics

---

## Quick Reference Card

### Minimal Docstring (Scripts)

```python
def load_data(path):
    """Load expression data from CSV file."""
    return pd.read_csv(path, index_col=0)
```

### Standard Function

```python
def function_name(param1, param2):
    """
    Short description in imperative mood.

    Parameters
    ----------
    param1 : type
        Description of param1.
    param2 : type
        Description of param2.

    Returns
    -------
    type
        Description of return value.
    """
```

### With Examples

```python
def add_numbers(a, b):
    """
    Add two numbers together.

    Parameters
    ----------
    a : int or float
        First number.
    b : int or float
        Second number.

    Returns
    -------
    int or float
        Sum of a and b.

    Examples
    --------
    >>> add_numbers(2, 3)
    5
    >>> add_numbers(1.5, 2.5)
    4.0
    """
    return a + b
```

---

## Common Mistakes

### 1. Incomplete Parameter Documentation

```python
# BAD
def process(data, method="default", threshold=0.05):
    """Process the data."""  # No parameter docs!

# GOOD
def process(data, method="default", threshold=0.05):
    """
    Process the data with specified method.

    Parameters
    ----------
    data : pd.DataFrame
        Input data to process.
    method : str, default "default"
        Processing method to use.
    threshold : float, default 0.05
        Significance threshold.
    """
```

### 2. Missing Return Documentation

```python
# BAD
def get_significant(data, threshold):
    """Filter to significant results."""
    return data[data['padj'] < threshold]  # What does it return?

# GOOD
def get_significant(data, threshold):
    """
    Filter to significant results.

    Returns
    -------
    pd.DataFrame
        Subset of input data where padj < threshold.
    """
```

### 3. Examples That Don't Run

```python
# BAD - example won't work
"""
Examples
--------
>>> result = my_function(data)  # 'data' not defined
"""

# GOOD - self-contained example
"""
Examples
--------
>>> import numpy as np
>>> data = np.array([1, 2, 3])
>>> result = my_function(data)
>>> result
array([2, 4, 6])
"""
```

---

## Tools and Validation

### Docstring Linting

```bash
# pydocstyle - check docstring conventions
pip install pydocstyle
pydocstyle --convention=numpy my_module.py

# darglint - check docstrings match signatures
pip install darglint
darglint my_module.py
```

### Doctest Execution

```bash
# Run doctests in a module
python -m doctest my_module.py -v

# Or in pytest
pytest --doctest-modules
```

### IDE Integration

- **VS Code**: Python Docstring Generator extension
- **PyCharm**: Built-in docstring generation (Ctrl+Shift+D)
- **Vim**: vim-pydocstring plugin
