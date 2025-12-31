# Dimensionality Reduction for High-Dimensional Data

> PCA, t-SNE, and UMAP: Theory, implementation, and interpretation for omics data

---

## Overview

### Why Reduce Dimensions?

| Problem | Solution |
|---------|----------|
| **Curse of dimensionality** | Reduce to meaningful dimensions |
| **Visualization** | Project to 2-3D for plotting |
| **Noise reduction** | Capture signal, discard noise |
| **Computational efficiency** | Fewer features = faster models |
| **Multicollinearity** | Orthogonal components |

### Method Selection Guide

```
What is your goal?
│
├── Preserve global structure / Quantitative analysis
│   └── PCA (linear, interpretable)
│
├── Visualization / Cluster discovery
│   ├── Small dataset (< 10,000 samples)
│   │   └── t-SNE (local structure)
│   └── Large dataset / Need speed
│       └── UMAP (global + local, faster)
│
└── Preprocessing for ML
    ├── Linear relationships expected
    │   └── PCA
    └── Complex manifold structure
        └── UMAP
```

---

## Principal Component Analysis (PCA)

### Theory

PCA finds orthogonal directions of maximum variance:

1. **Center data** (subtract mean)
2. **Compute covariance matrix**
3. **Find eigenvectors** (principal components)
4. **Project data** onto top k eigenvectors

**Key properties**:
- Linear transformation
- Components are orthogonal
- Ordered by variance explained
- Deterministic (same input → same output)

### Python Implementation

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def run_pca(data, n_components=None, scale=True):
    """
    Run PCA on data matrix.

    Parameters
    ----------
    data : array-like or DataFrame
        Samples × features matrix
    n_components : int, optional
        Number of components (default: min(n_samples, n_features))
    scale : bool
        Whether to standardize features (recommended for omics)

    Returns
    -------
    dict
        PCA results including transformed data, loadings, variance explained
    """
    if isinstance(data, pd.DataFrame):
        feature_names = data.columns.tolist()
        sample_names = data.index.tolist()
        data = data.values
    else:
        feature_names = [f"Feature_{i}" for i in range(data.shape[1])]
        sample_names = [f"Sample_{i}" for i in range(data.shape[0])]

    # Standardize if requested
    if scale:
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
    else:
        data_scaled = data - data.mean(axis=0)

    # Fit PCA
    if n_components is None:
        n_components = min(data.shape)

    pca = PCA(n_components=n_components)
    transformed = pca.fit_transform(data_scaled)

    # Create results
    results = {
        'transformed': pd.DataFrame(
            transformed,
            index=sample_names,
            columns=[f"PC{i+1}" for i in range(n_components)]
        ),
        'loadings': pd.DataFrame(
            pca.components_.T,
            index=feature_names,
            columns=[f"PC{i+1}" for i in range(n_components)]
        ),
        'variance_explained': pca.explained_variance_ratio_,
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_),
        'pca_object': pca
    }

    return results


def plot_pca(pca_results, color_by=None, title="PCA"):
    """
    Create PCA visualization with scree plot and scatter.

    Parameters
    ----------
    pca_results : dict
        Output from run_pca()
    color_by : array-like, optional
        Labels for coloring points
    title : str
        Plot title
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    transformed = pca_results['transformed']
    var_exp = pca_results['variance_explained'] * 100

    # Scree plot
    n_show = min(10, len(var_exp))
    axes[0].bar(range(1, n_show + 1), var_exp[:n_show], alpha=0.7)
    axes[0].plot(range(1, n_show + 1),
                 pca_results['cumulative_variance'][:n_show] * 100,
                 'ro-', label='Cumulative')
    axes[0].set_xlabel('Principal Component')
    axes[0].set_ylabel('Variance Explained (%)')
    axes[0].set_title('Scree Plot')
    axes[0].legend()

    # PC1 vs PC2
    if color_by is not None:
        scatter = axes[1].scatter(transformed['PC1'], transformed['PC2'],
                                  c=pd.Categorical(color_by).codes,
                                  cmap='tab10', alpha=0.7)
    else:
        scatter = axes[1].scatter(transformed['PC1'], transformed['PC2'], alpha=0.7)

    axes[1].set_xlabel(f"PC1 ({var_exp[0]:.1f}%)")
    axes[1].set_ylabel(f"PC2 ({var_exp[1]:.1f}%)")
    axes[1].set_title('PC1 vs PC2')

    # PC2 vs PC3 (if available)
    if transformed.shape[1] >= 3:
        if color_by is not None:
            axes[2].scatter(transformed['PC2'], transformed['PC3'],
                           c=pd.Categorical(color_by).codes,
                           cmap='tab10', alpha=0.7)
        else:
            axes[2].scatter(transformed['PC2'], transformed['PC3'], alpha=0.7)

        axes[2].set_xlabel(f"PC2 ({var_exp[1]:.1f}%)")
        axes[2].set_ylabel(f"PC3 ({var_exp[2]:.1f}%)")
        axes[2].set_title('PC2 vs PC3')

    plt.suptitle(title)
    plt.tight_layout()
    return fig


def select_n_components(pca_results, threshold=0.9):
    """
    Select number of components explaining threshold variance.

    Parameters
    ----------
    pca_results : dict
        Output from run_pca()
    threshold : float
        Cumulative variance threshold (default: 0.9 for 90%)

    Returns
    -------
    int
        Number of components needed
    """
    cumvar = pca_results['cumulative_variance']
    n_components = np.argmax(cumvar >= threshold) + 1
    print(f"{n_components} components explain {cumvar[n_components-1]*100:.1f}% of variance")
    return n_components
```

### R Implementation

```r
library(ggplot2)
library(factoextra)

run_pca <- function(data, scale = TRUE, center = TRUE) {
  # PCA
  pca_result <- prcomp(data, scale. = scale, center = center)

  # Variance explained
  var_explained <- pca_result$sdev^2 / sum(pca_result$sdev^2)

  list(
    pca = pca_result,
    scores = pca_result$x,
    loadings = pca_result$rotation,
    var_explained = var_explained,
    cumulative_var = cumsum(var_explained)
  )
}

# Visualization
plot_pca <- function(pca_result, metadata = NULL, color_var = NULL) {
  # Quick visualization with factoextra
  fviz_pca_ind(pca_result$pca,
               col.ind = if (!is.null(color_var)) metadata[[color_var]] else "blue",
               palette = "jco",
               addEllipses = TRUE,
               legend.title = color_var)
}

# Scree plot
plot_scree <- function(pca_result) {
  fviz_eig(pca_result$pca, addlabels = TRUE)
}

# Loadings plot
plot_loadings <- function(pca_result, top_n = 10) {
  fviz_pca_var(pca_result$pca,
               col.var = "contrib",
               gradient.cols = c("blue", "yellow", "red"),
               select.var = list(contrib = top_n))
}
```

### PCA Interpretation

**Variance explained**:
- PC1 + PC2 > 50%: Good separation likely
- PC1 dominates (>40%): Strong primary signal
- Flat scree plot: Noise or complex structure

**Loadings analysis**:
```python
def top_loading_genes(pca_results, component='PC1', n_top=20):
    """Get genes with highest loadings on a component."""
    loadings = pca_results['loadings'][component].abs().sort_values(ascending=False)
    return loadings.head(n_top)
```

**Common issues**:
| Observation | Interpretation | Action |
|-------------|----------------|--------|
| Batch separates on PC1 | Strong batch effect | Batch correction needed |
| Outliers visible | Technical failures or biological outliers | Investigate, consider removal |
| No separation | No strong effect or wrong features | Check normalization, feature selection |
| Horseshoe/arch | Gradient effect or compositional data | Consider alternatives (UMAP, NMF) |

---

## t-SNE (t-Distributed Stochastic Neighbor Embedding)

### Theory

t-SNE preserves local neighborhood structure:

1. **Compute pairwise similarities** in high-D (Gaussian kernel)
2. **Initialize low-D embedding** (random or PCA)
3. **Optimize** to match high-D similarities in low-D (Student t-distribution)

**Key properties**:
- Non-linear, non-parametric
- Preserves local structure well
- Global structure NOT preserved (distances between clusters meaningless)
- Stochastic (different runs → different results)
- Slow for large datasets

### Critical Parameters

| Parameter | Effect | Recommended |
|-----------|--------|-------------|
| **perplexity** | Balance local/global; ~k nearest neighbors | 5-50, try 30 first |
| **learning_rate** | Step size for optimization | 10-1000, default 200 |
| **n_iter** | Number of iterations | ≥1000 for convergence |
| **early_exaggeration** | Initial cluster separation | Default 12 |

**Perplexity guidelines**:
- Small dataset (n < 100): perplexity = 5-10
- Medium dataset (n ~ 1000): perplexity = 30
- Large dataset (n > 10000): perplexity = 50-100
- Rule of thumb: perplexity ≈ n/100 to n/50

### Python Implementation

```python
from sklearn.manifold import TSNE
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_tsne(data, n_components=2, perplexity=30, learning_rate=200,
             n_iter=1000, random_state=42, pca_init=True, n_pca=50):
    """
    Run t-SNE with recommended settings.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    n_components : int
        Output dimensions (usually 2)
    perplexity : float
        Balance between local and global structure
    learning_rate : float
        Optimization step size
    n_iter : int
        Number of iterations
    random_state : int
        For reproducibility
    pca_init : bool
        Initialize with PCA (recommended)
    n_pca : int
        Number of PCA components for preprocessing

    Returns
    -------
    np.ndarray
        Transformed coordinates
    """
    if isinstance(data, pd.DataFrame):
        data = data.values

    # PCA preprocessing (recommended for high-D data)
    if pca_init and data.shape[1] > n_pca:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_pca)
        data_pca = pca.fit_transform(data)
        print(f"PCA: {data.shape[1]} → {n_pca} dimensions "
              f"({pca.explained_variance_ratio_.sum()*100:.1f}% variance)")
        init = 'pca'
    else:
        data_pca = data
        init = 'pca' if data.shape[1] <= 50 else 'random'

    # Run t-SNE
    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        learning_rate=learning_rate,
        n_iter=n_iter,
        random_state=random_state,
        init=init,
        metric='euclidean',
        n_jobs=-1  # Parallel
    )

    embedding = tsne.fit_transform(data_pca)

    return embedding


def plot_tsne(embedding, labels=None, title="t-SNE"):
    """Plot t-SNE embedding."""
    fig, ax = plt.subplots(figsize=(8, 6))

    if labels is not None:
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax.scatter(embedding[mask, 0], embedding[mask, 1],
                      c=[colors[i]], label=label, alpha=0.7)
        ax.legend()
    else:
        ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.7)

    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    ax.set_title(title)

    return fig


def tsne_parameter_sweep(data, perplexities=[5, 10, 30, 50, 100],
                         labels=None, random_state=42):
    """
    Compare t-SNE results across perplexity values.

    Helps identify optimal perplexity for your data.
    """
    n_perp = len(perplexities)
    fig, axes = plt.subplots(1, n_perp, figsize=(4*n_perp, 4))

    for ax, perp in zip(axes, perplexities):
        embedding = run_tsne(data, perplexity=perp, random_state=random_state)

        if labels is not None:
            for label in np.unique(labels):
                mask = labels == label
                ax.scatter(embedding[mask, 0], embedding[mask, 1],
                          label=label, alpha=0.7, s=10)
        else:
            ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=10)

        ax.set_title(f'Perplexity = {perp}')
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    return fig
```

### R Implementation

```r
library(Rtsne)
library(ggplot2)

run_tsne <- function(data, perplexity = 30, max_iter = 1000,
                     pca_init = TRUE, n_pca = 50, seed = 42) {

  set.seed(seed)

  # PCA preprocessing
  if (pca_init && ncol(data) > n_pca) {
    pca <- prcomp(data, scale. = TRUE, center = TRUE)
    data_input <- pca$x[, 1:n_pca]
    message(sprintf("PCA: %d → %d dimensions", ncol(data), n_pca))
  } else {
    data_input <- as.matrix(data)
  }

  # Run t-SNE
  tsne_result <- Rtsne(
    data_input,
    dims = 2,
    perplexity = perplexity,
    max_iter = max_iter,
    pca = FALSE,  # Already done above
    check_duplicates = FALSE
  )

  as.data.frame(tsne_result$Y)
}

plot_tsne <- function(embedding, labels = NULL) {
  df <- data.frame(
    tSNE1 = embedding[, 1],
    tSNE2 = embedding[, 2]
  )

  if (!is.null(labels)) {
    df$label <- labels
    ggplot(df, aes(tSNE1, tSNE2, color = label)) +
      geom_point(alpha = 0.7) +
      theme_minimal()
  } else {
    ggplot(df, aes(tSNE1, tSNE2)) +
      geom_point(alpha = 0.7) +
      theme_minimal()
  }
}
```

### t-SNE Interpretation Caveats

**DO**:
- Compare cluster membership
- Identify outliers
- Qualitative pattern assessment
- Use for visualization only

**DON'T**:
- Interpret distances between clusters
- Claim cluster sizes are meaningful
- Use as input for downstream analysis
- Trust without multiple runs

---

## UMAP (Uniform Manifold Approximation and Projection)

### Theory

UMAP constructs a topological representation:

1. **Build weighted k-neighbor graph** in high-D
2. **Construct fuzzy simplicial set** (topological structure)
3. **Optimize low-D layout** to preserve structure

**Advantages over t-SNE**:
- Faster (scales to millions)
- Better global structure preservation
- Deterministic with random_state
- Works as preprocessing for ML

### Key Parameters

| Parameter | Effect | Recommended |
|-----------|--------|-------------|
| **n_neighbors** | Local vs global; larger = more global | 5-50, default 15 |
| **min_dist** | Cluster tightness; smaller = tighter | 0.0-0.99, default 0.1 |
| **metric** | Distance function | 'euclidean', 'cosine', 'correlation' |
| **n_components** | Output dimensions | 2 for viz, higher for preprocessing |

**Parameter intuition**:
- Low n_neighbors (5-15): Fine local structure, may fragment clusters
- High n_neighbors (50-200): More global, may merge similar clusters
- Low min_dist (0.0-0.1): Tight clusters, clear separation
- High min_dist (0.5-0.9): Spread out, preserves continuity

### Python Implementation

```python
import umap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_umap(data, n_neighbors=15, min_dist=0.1, n_components=2,
             metric='euclidean', random_state=42):
    """
    Run UMAP dimensionality reduction.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    n_neighbors : int
        Size of local neighborhood (5-50)
    min_dist : float
        Minimum distance between points (0.0-0.99)
    n_components : int
        Output dimensions
    metric : str
        Distance metric
    random_state : int
        For reproducibility

    Returns
    -------
    np.ndarray
        Transformed coordinates
    """
    if isinstance(data, pd.DataFrame):
        data = data.values

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        random_state=random_state,
        n_jobs=-1
    )

    embedding = reducer.fit_transform(data)

    return embedding, reducer


def plot_umap(embedding, labels=None, title="UMAP"):
    """Plot UMAP embedding."""
    fig, ax = plt.subplots(figsize=(8, 6))

    if labels is not None:
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax.scatter(embedding[mask, 0], embedding[mask, 1],
                      c=[colors[i]], label=label, alpha=0.7)
        ax.legend()
    else:
        ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.7)

    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    ax.set_title(title)

    return fig


def umap_parameter_sweep(data, labels=None, random_state=42):
    """
    Compare UMAP results across parameter combinations.
    """
    n_neighbors_list = [5, 15, 50]
    min_dist_list = [0.0, 0.1, 0.5]

    fig, axes = plt.subplots(len(n_neighbors_list), len(min_dist_list),
                             figsize=(12, 12))

    for i, n_neighbors in enumerate(n_neighbors_list):
        for j, min_dist in enumerate(min_dist_list):
            embedding, _ = run_umap(data, n_neighbors=n_neighbors,
                                    min_dist=min_dist, random_state=random_state)

            ax = axes[i, j]

            if labels is not None:
                for label in np.unique(labels):
                    mask = labels == label
                    ax.scatter(embedding[mask, 0], embedding[mask, 1],
                              label=label, alpha=0.7, s=10)
            else:
                ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=10)

            ax.set_title(f'n={n_neighbors}, d={min_dist}')
            ax.set_xticks([])
            ax.set_yticks([])

    plt.tight_layout()
    return fig


def supervised_umap(data, labels, n_neighbors=15, min_dist=0.1,
                    random_state=42):
    """
    Run supervised UMAP for better class separation.

    Uses label information to guide embedding.
    """
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=2,
        random_state=random_state,
        target_metric='categorical'
    )

    embedding = reducer.fit_transform(data, y=labels)

    return embedding, reducer
```

### R Implementation

```r
library(umap)
library(ggplot2)

run_umap <- function(data, n_neighbors = 15, min_dist = 0.1,
                     metric = "euclidean", seed = 42) {

  config <- umap.defaults
  config$n_neighbors <- n_neighbors
  config$min_dist <- min_dist
  config$metric <- metric
  config$random_state <- seed

  result <- umap(as.matrix(data), config = config)

  as.data.frame(result$layout)
}

plot_umap <- function(embedding, labels = NULL) {
  df <- data.frame(
    UMAP1 = embedding[, 1],
    UMAP2 = embedding[, 2]
  )

  if (!is.null(labels)) {
    df$label <- labels
    ggplot(df, aes(UMAP1, UMAP2, color = label)) +
      geom_point(alpha = 0.7, size = 1) +
      theme_minimal() +
      theme(legend.position = "right")
  } else {
    ggplot(df, aes(UMAP1, UMAP2)) +
      geom_point(alpha = 0.7, size = 1) +
      theme_minimal()
  }
}
```

---

## Method Comparison

### When to Use Which

| Method | Use When | Avoid When |
|--------|----------|------------|
| **PCA** | Need interpretability; Linear relationships; Preprocessing | Non-linear structure dominates |
| **t-SNE** | Visualization only; Local structure matters; Small data | Need speed; Want reproducibility |
| **UMAP** | Speed needed; Global + local; Preprocessing for ML | Need strict reproducibility |

### Quantitative Comparison

```python
def compare_methods(data, labels=None, random_state=42):
    """
    Compare PCA, t-SNE, and UMAP on same data.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # PCA
    pca_results = run_pca(data, n_components=2)
    pca_embedding = pca_results['transformed'].values
    var = pca_results['variance_explained']

    # t-SNE
    tsne_embedding = run_tsne(data, random_state=random_state)

    # UMAP
    umap_embedding, _ = run_umap(data, random_state=random_state)

    embeddings = [pca_embedding, tsne_embedding, umap_embedding]
    titles = [f'PCA ({var[0]*100:.1f}% + {var[1]*100:.1f}%)',
              't-SNE', 'UMAP']

    for ax, emb, title in zip(axes, embeddings, titles):
        if labels is not None:
            for label in np.unique(labels):
                mask = labels == label
                ax.scatter(emb[mask, 0], emb[mask, 1],
                          label=label, alpha=0.7, s=20)
            ax.legend(fontsize=8)
        else:
            ax.scatter(emb[:, 0], emb[:, 1], alpha=0.7, s=20)

        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    return fig
```

---

## Best Practices

### Preprocessing

1. **Filter features**: Remove low-variance, irrelevant features
2. **Normalize**: Scale appropriately for your data type
3. **Log transform**: For count data (add pseudocount first)
4. **Handle missing values**: Impute or exclude

```python
def preprocess_for_dr(data, log_transform=True, pseudocount=1,
                      min_variance=0.01, scale=True):
    """
    Standard preprocessing for dimensionality reduction.
    """
    data = data.copy()

    # Log transform (for count data)
    if log_transform:
        data = np.log2(data + pseudocount)

    # Remove low-variance features
    variances = data.var(axis=0)
    keep_features = variances > np.percentile(variances, min_variance * 100)
    data = data.loc[:, keep_features]

    # Scale
    if scale:
        data = (data - data.mean()) / data.std()

    return data
```

### Reproducibility

```python
# Always set random state
random_state = 42

# For t-SNE: run multiple times
embeddings = [run_tsne(data, random_state=i) for i in range(5)]
# Check consistency of cluster assignments

# Report parameters in methods
methods_text = """
Dimensionality reduction was performed using UMAP (v0.5.3) with
n_neighbors=15, min_dist=0.1, metric='euclidean'. Data were
log2-transformed and scaled before analysis.
"""
```

### Validation

```python
from sklearn.metrics import silhouette_score

def evaluate_embedding(embedding, labels):
    """
    Evaluate embedding quality using silhouette score.

    Higher score = better cluster separation.
    """
    score = silhouette_score(embedding, labels)
    print(f"Silhouette score: {score:.3f}")
    return score
```

---

## Reporting in Manuscripts

### Methods Section

```markdown
**Dimensionality reduction**

For exploratory visualization, we applied [PCA / UMAP / t-SNE] to
[log2-transformed, scaled] expression data. [For PCA: The first N
principal components explained X% of total variance.] [For UMAP:
Parameters were set to n_neighbors=15, min_dist=0.1, using Euclidean
distance.] [For t-SNE: Perplexity was set to 30 with 1000 iterations.]

Samples were colored by [condition/batch/cell type] to assess
[batch effects / biological signal / cluster structure].
```

### Figure Legends

```markdown
**Figure X. Dimensionality reduction reveals [biological insight].**

(A) PCA of [N] samples showing separation by [factor]. PC1 and PC2
explain [X]% and [Y]% of variance, respectively.

(B) UMAP visualization colored by [factor] demonstrates [clustering /
trajectory / separation]. n_neighbors=15, min_dist=0.1.

(C) [Additional panel if needed]
```

---

## References

1. Jolliffe IT, Cadima J (2016). Principal component analysis: a review and recent developments. *Phil Trans R Soc A* 374:20150202.

2. van der Maaten L, Hinton G (2008). Visualizing Data using t-SNE. *JMLR* 9:2579-2605.

3. McInnes L, Healy J, Melville J (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv:1802.03426*.

4. Kobak D, Berens P (2019). The art of using t-SNE for single-cell transcriptomics. *Nature Communications* 10:5416.
