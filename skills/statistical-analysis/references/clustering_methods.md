# Clustering Methods for Biological Data

> Hierarchical, k-means, and graph-based clustering for omics analysis

---

## Overview

### Clustering Taxonomy

```
Clustering Methods
│
├── Partitioning (flat)
│   ├── K-means (spherical clusters)
│   ├── K-medoids (robust to outliers)
│   └── Spectral clustering (non-convex shapes)
│
├── Hierarchical
│   ├── Agglomerative (bottom-up)
│   └── Divisive (top-down, less common)
│
├── Density-based
│   ├── DBSCAN (arbitrary shapes, noise detection)
│   └── HDBSCAN (variable density)
│
└── Graph-based
    ├── Louvain (community detection)
    ├── Leiden (improved Louvain)
    └── Phenograph (single-cell focus)
```

### Method Selection Guide

```
What is your data structure?
│
├── Gene expression (bulk RNA-seq)
│   └── Hierarchical clustering
│       └── Method: Ward's or complete linkage
│       └── Distance: 1 - Pearson correlation
│
├── Single-cell transcriptomics
│   └── Graph-based clustering
│       └── Leiden or Louvain on k-NN graph
│
├── Sample clustering (known k)
│   └── K-means or consensus clustering
│
├── Unknown cluster count
│   └── Hierarchical → cut tree, or
│   └── HDBSCAN (density-based)
│
└── Spatial / imaging data
    └── DBSCAN or HDBSCAN
```

---

## Hierarchical Clustering

### Theory

**Agglomerative approach** (most common):
1. Start with each sample as its own cluster
2. Merge closest pairs iteratively
3. Create dendrogram showing merge history
4. Cut tree at desired height/number of clusters

### Linkage Methods

| Method | Merge Criterion | Properties |
|--------|-----------------|------------|
| **Single** | Minimum distance | Chains; sensitive to noise |
| **Complete** | Maximum distance | Compact clusters; sensitive to outliers |
| **Average (UPGMA)** | Mean distance | Balanced; common choice |
| **Ward** | Minimum variance increase | Compact, spherical; minimizes within-cluster variance |
| **Weighted (WPGMA)** | Weighted average | Equal weight to all leaves |

**Recommendation**: Start with **Ward's method** for most omics applications.

### Distance Metrics

| Metric | Formula | Use Case |
|--------|---------|----------|
| **Euclidean** | √Σ(xi - yi)² | Magnitude matters |
| **Correlation** | 1 - r | Pattern similarity (ignore magnitude) |
| **Cosine** | 1 - cos(θ) | Direction similarity |
| **Manhattan** | Σ|xi - yi| | Robust to outliers |

**For gene expression**: Use **1 - Pearson correlation** to focus on expression patterns.

### Python Implementation

```python
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import seaborn as sns

def hierarchical_clustering(data, method='ward', metric='euclidean',
                            optimal_ordering=True):
    """
    Perform hierarchical clustering with dendrogram.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    method : str
        Linkage method ('ward', 'complete', 'average', 'single')
    metric : str or callable
        Distance metric ('euclidean', 'correlation', 'cosine', etc.)
    optimal_ordering : bool
        Reorder leaves for better visualization

    Returns
    -------
    dict
        Linkage matrix, distance matrix, dendrogram data
    """
    if isinstance(data, pd.DataFrame):
        sample_names = data.index.tolist()
        data = data.values
    else:
        sample_names = [f"Sample_{i}" for i in range(data.shape[0])]

    # Compute distance matrix
    if metric == 'correlation':
        # 1 - Pearson correlation
        dist_matrix = pdist(data, metric='correlation')
    else:
        dist_matrix = pdist(data, metric=metric)

    # Hierarchical clustering
    linkage_matrix = hierarchy.linkage(
        dist_matrix,
        method=method,
        optimal_ordering=optimal_ordering
    )

    return {
        'linkage': linkage_matrix,
        'distances': squareform(dist_matrix),
        'labels': sample_names,
        'method': method,
        'metric': metric
    }


def plot_dendrogram(hc_result, figsize=(12, 6), title="Hierarchical Clustering",
                    color_threshold=None, truncate_mode=None, p=30):
    """
    Plot dendrogram from hierarchical clustering.

    Parameters
    ----------
    hc_result : dict
        Output from hierarchical_clustering()
    color_threshold : float, optional
        Height to color clusters (None = auto)
    truncate_mode : str, optional
        'lastp' to show only last p merges
    p : int
        Number of leaves to show if truncating
    """
    fig, ax = plt.subplots(figsize=figsize)

    dend = hierarchy.dendrogram(
        hc_result['linkage'],
        labels=hc_result['labels'],
        color_threshold=color_threshold,
        truncate_mode=truncate_mode,
        p=p,
        leaf_rotation=90,
        leaf_font_size=8,
        ax=ax
    )

    ax.set_title(title)
    ax.set_ylabel('Distance')
    plt.tight_layout()

    return fig, dend


def cut_tree(hc_result, n_clusters=None, height=None):
    """
    Cut dendrogram to get cluster assignments.

    Parameters
    ----------
    hc_result : dict
        Output from hierarchical_clustering()
    n_clusters : int, optional
        Number of clusters to extract
    height : float, optional
        Height at which to cut (alternative to n_clusters)

    Returns
    -------
    np.ndarray
        Cluster labels for each sample
    """
    if n_clusters is not None:
        labels = hierarchy.fcluster(hc_result['linkage'], n_clusters,
                                    criterion='maxclust')
    elif height is not None:
        labels = hierarchy.fcluster(hc_result['linkage'], height,
                                    criterion='distance')
    else:
        raise ValueError("Specify either n_clusters or height")

    return labels


def cluster_heatmap(data, row_cluster=True, col_cluster=True,
                    method='ward', metric='correlation',
                    cmap='RdBu_r', figsize=(10, 8),
                    row_colors=None, col_colors=None):
    """
    Create clustered heatmap (common for gene expression).

    Parameters
    ----------
    data : pd.DataFrame
        Samples × genes or genes × samples matrix
    row_cluster, col_cluster : bool
        Whether to cluster rows/columns
    method : str
        Linkage method
    metric : str
        Distance metric
    cmap : str
        Colormap
    row_colors, col_colors : pd.Series, optional
        Annotation colors
    """
    g = sns.clustermap(
        data,
        method=method,
        metric=metric,
        row_cluster=row_cluster,
        col_cluster=col_cluster,
        cmap=cmap,
        figsize=figsize,
        row_colors=row_colors,
        col_colors=col_colors,
        standard_scale=None,  # Set to 0 or 1 for z-score by row/col
        dendrogram_ratio=(0.1, 0.1),
        cbar_pos=(0.02, 0.8, 0.03, 0.18)
    )

    return g
```

### R Implementation

```r
library(pheatmap)
library(dendextend)

# Basic hierarchical clustering
hclust_samples <- function(data, method = "ward.D2", dist_method = "euclidean") {
  # Distance matrix
  if (dist_method == "correlation") {
    dist_mat <- as.dist(1 - cor(t(data)))
  } else {
    dist_mat <- dist(data, method = dist_method)
  }

  # Hierarchical clustering
  hc <- hclust(dist_mat, method = method)

  list(
    hclust = hc,
    dist = dist_mat
  )
}

# Plot dendrogram
plot_dendrogram <- function(hc_result, k = NULL, main = "Cluster Dendrogram") {
  dend <- as.dendrogram(hc_result$hclust)

  if (!is.null(k)) {
    dend <- color_branches(dend, k = k)
  }

  plot(dend, main = main)

  if (!is.null(k)) {
    rect.hclust(hc_result$hclust, k = k, border = 2:k)
  }
}

# Cut tree
cut_clusters <- function(hc_result, k = NULL, h = NULL) {
  if (!is.null(k)) {
    cutree(hc_result$hclust, k = k)
  } else if (!is.null(h)) {
    cutree(hc_result$hclust, h = h)
  }
}

# Heatmap with clustering
cluster_heatmap <- function(data, annotation_row = NULL, annotation_col = NULL,
                            scale = "row", cluster_rows = TRUE, cluster_cols = TRUE) {
  pheatmap(
    data,
    scale = scale,
    cluster_rows = cluster_rows,
    cluster_cols = cluster_cols,
    annotation_row = annotation_row,
    annotation_col = annotation_col,
    clustering_method = "ward.D2",
    clustering_distance_rows = "correlation",
    clustering_distance_cols = "correlation",
    show_rownames = nrow(data) < 100,
    show_colnames = TRUE,
    color = colorRampPalette(c("blue", "white", "red"))(100)
  )
}
```

### Choosing Number of Clusters

```python
from scipy.cluster import hierarchy
from sklearn.metrics import silhouette_score
import numpy as np

def evaluate_cluster_numbers(hc_result, k_range=range(2, 11)):
    """
    Evaluate different numbers of clusters using silhouette score.
    """
    data_matrix = hc_result.get('data', None)
    if data_matrix is None:
        raise ValueError("Need original data for silhouette calculation")

    scores = []
    for k in k_range:
        labels = hierarchy.fcluster(hc_result['linkage'], k, criterion='maxclust')
        score = silhouette_score(data_matrix, labels)
        scores.append(score)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(k_range), scores, 'bo-')
    ax.set_xlabel('Number of clusters')
    ax.set_ylabel('Silhouette score')
    ax.set_title('Optimal cluster number selection')

    best_k = list(k_range)[np.argmax(scores)]
    ax.axvline(x=best_k, color='r', linestyle='--', label=f'Optimal k={best_k}')
    ax.legend()

    return best_k, scores, fig
```

---

## K-Means Clustering

### Theory

K-means minimizes within-cluster sum of squares:

1. Initialize k centroids (random or k-means++)
2. Assign each point to nearest centroid
3. Recompute centroids as cluster means
4. Repeat until convergence

**Properties**:
- Fast and scalable
- Requires specifying k
- Assumes spherical clusters of similar size
- Sensitive to initialization (use k-means++)

### Python Implementation

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import numpy as np
import matplotlib.pyplot as plt

def run_kmeans(data, n_clusters, n_init=10, random_state=42):
    """
    Run k-means clustering with evaluation metrics.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    n_clusters : int
        Number of clusters
    n_init : int
        Number of random initializations
    random_state : int
        For reproducibility

    Returns
    -------
    dict
        Labels, centroids, and evaluation metrics
    """
    kmeans = KMeans(
        n_clusters=n_clusters,
        n_init=n_init,
        random_state=random_state,
        init='k-means++'
    )

    labels = kmeans.fit_predict(data)

    return {
        'labels': labels,
        'centroids': kmeans.cluster_centers_,
        'inertia': kmeans.inertia_,
        'silhouette': silhouette_score(data, labels),
        'calinski_harabasz': calinski_harabasz_score(data, labels),
        'n_clusters': n_clusters,
        'model': kmeans
    }


def elbow_method(data, k_range=range(2, 11), random_state=42):
    """
    Find optimal k using elbow method and silhouette scores.
    """
    inertias = []
    silhouettes = []

    for k in k_range:
        result = run_kmeans(data, k, random_state=random_state)
        inertias.append(result['inertia'])
        silhouettes.append(result['silhouette'])

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Elbow plot
    axes[0].plot(list(k_range), inertias, 'bo-')
    axes[0].set_xlabel('Number of clusters (k)')
    axes[0].set_ylabel('Inertia')
    axes[0].set_title('Elbow Method')

    # Silhouette plot
    axes[1].plot(list(k_range), silhouettes, 'ro-')
    axes[1].set_xlabel('Number of clusters (k)')
    axes[1].set_ylabel('Silhouette Score')
    axes[1].set_title('Silhouette Analysis')

    best_k = list(k_range)[np.argmax(silhouettes)]
    axes[1].axvline(x=best_k, color='g', linestyle='--',
                    label=f'Best k={best_k}')
    axes[1].legend()

    plt.tight_layout()

    return best_k, fig


def consensus_clustering(data, k_range=range(2, 8), n_reps=100, random_state=42):
    """
    Consensus clustering to determine optimal k and robust clusters.

    Runs k-means multiple times with different initializations and
    subsampling to find stable cluster assignments.
    """
    from sklearn.utils import resample

    n_samples = data.shape[0]
    results = {}

    for k in k_range:
        # Co-occurrence matrix
        cooccurrence = np.zeros((n_samples, n_samples))
        counts = np.zeros((n_samples, n_samples))

        for rep in range(n_reps):
            # Subsample (80% of samples)
            indices = resample(range(n_samples), n_samples=int(0.8 * n_samples),
                              random_state=random_state + rep, replace=False)

            # Cluster
            kmeans = KMeans(n_clusters=k, n_init=1, random_state=random_state + rep)
            labels = kmeans.fit_predict(data[indices])

            # Update co-occurrence
            for i, idx_i in enumerate(indices):
                for j, idx_j in enumerate(indices):
                    if labels[i] == labels[j]:
                        cooccurrence[idx_i, idx_j] += 1
                    counts[idx_i, idx_j] += 1

        # Normalize
        consensus_matrix = cooccurrence / np.maximum(counts, 1)

        # Final clustering on consensus
        from sklearn.cluster import AgglomerativeClustering
        final_labels = AgglomerativeClustering(
            n_clusters=k,
            metric='precomputed',
            linkage='average'
        ).fit_predict(1 - consensus_matrix)

        results[k] = {
            'labels': final_labels,
            'consensus_matrix': consensus_matrix,
            'silhouette': silhouette_score(data, final_labels)
        }

    return results
```

### R Implementation

```r
library(cluster)
library(factoextra)

# K-means clustering
run_kmeans <- function(data, k, nstart = 25, seed = 42) {
  set.seed(seed)

  km <- kmeans(data, centers = k, nstart = nstart)

  list(
    cluster = km$cluster,
    centers = km$centers,
    totss = km$totss,
    withinss = km$tot.withinss,
    betweenss = km$betweenss,
    silhouette = silhouette(km$cluster, dist(data))
  )
}

# Elbow method
elbow_plot <- function(data, k_max = 10) {
  fviz_nbclust(data, kmeans, method = "wss") +
    geom_vline(xintercept = 3, linetype = 2)
}

# Silhouette method
silhouette_plot <- function(data, k_max = 10) {
  fviz_nbclust(data, kmeans, method = "silhouette")
}

# Gap statistic
gap_stat <- function(data, k_max = 10, nboot = 50, seed = 42) {
  set.seed(seed)
  gap <- clusGap(data, FUN = kmeans, nstart = 25, K.max = k_max, B = nboot)
  fviz_gap_stat(gap)
}
```

---

## Graph-Based Clustering

### Theory

Graph-based methods are the standard for single-cell data:

1. **Build k-nearest neighbor (k-NN) graph**
2. **Weight edges** by distance (often SNN - shared nearest neighbors)
3. **Detect communities** using Louvain or Leiden algorithm

**Advantages**:
- No assumption about cluster shape
- Scales to millions of cells
- Automatic determination of cluster number (via resolution)

### Python Implementation (Scanpy-style)

```python
import numpy as np
from sklearn.neighbors import NearestNeighbors
import igraph as ig
import leidenalg

def build_knn_graph(data, n_neighbors=15, metric='euclidean'):
    """
    Build k-nearest neighbor graph.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    n_neighbors : int
        Number of neighbors
    metric : str
        Distance metric

    Returns
    -------
    tuple
        (distances, indices) for each sample
    """
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric)
    nn.fit(data)
    distances, indices = nn.kneighbors(data)

    return distances, indices


def knn_to_snn(indices, n_samples):
    """
    Convert k-NN to shared nearest neighbor (SNN) graph.

    Edge weight = number of shared neighbors / k
    """
    k = indices.shape[1]

    # Build adjacency matrix
    from scipy.sparse import lil_matrix

    adj = lil_matrix((n_samples, n_samples))

    for i in range(n_samples):
        for j in indices[i]:
            if i != j:
                # Count shared neighbors
                shared = len(set(indices[i]) & set(indices[j]))
                adj[i, j] = shared / k
                adj[j, i] = shared / k

    return adj.tocsr()


def leiden_clustering(data, n_neighbors=15, resolution=1.0, random_state=42):
    """
    Leiden community detection for clustering.

    Parameters
    ----------
    data : array-like
        Samples × features matrix (or pre-computed PCA)
    n_neighbors : int
        Number of neighbors for graph construction
    resolution : float
        Higher = more clusters (default 1.0)
    random_state : int
        For reproducibility

    Returns
    -------
    np.ndarray
        Cluster labels
    """
    # Build k-NN graph
    distances, indices = build_knn_graph(data, n_neighbors=n_neighbors)

    n_samples = data.shape[0]

    # Build SNN adjacency
    adj = knn_to_snn(indices, n_samples)

    # Convert to igraph
    sources, targets = adj.nonzero()
    weights = adj[sources, targets].A1

    g = ig.Graph(n=n_samples, edges=list(zip(sources, targets)),
                 edge_attrs={'weight': weights})

    # Leiden clustering
    partition = leidenalg.find_partition(
        g,
        leidenalg.RBConfigurationVertexPartition,
        weights=weights,
        resolution_parameter=resolution,
        seed=random_state
    )

    labels = np.array(partition.membership)

    return labels


def louvain_clustering(data, n_neighbors=15, resolution=1.0, random_state=42):
    """
    Louvain community detection (faster, less optimal than Leiden).
    """
    # Build k-NN graph
    distances, indices = build_knn_graph(data, n_neighbors=n_neighbors)

    n_samples = data.shape[0]
    adj = knn_to_snn(indices, n_samples)

    # Convert to igraph
    sources, targets = adj.nonzero()
    weights = adj[sources, targets].A1

    g = ig.Graph(n=n_samples, edges=list(zip(sources, targets)),
                 edge_attrs={'weight': weights})

    # Louvain clustering
    partition = g.community_multilevel(weights=weights)
    labels = np.array(partition.membership)

    return labels


def resolution_sweep(data, resolutions=[0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0],
                     n_neighbors=15, method='leiden', random_state=42):
    """
    Compare clustering across resolution parameters.
    """
    results = {}

    cluster_func = leiden_clustering if method == 'leiden' else louvain_clustering

    for res in resolutions:
        labels = cluster_func(data, n_neighbors=n_neighbors,
                             resolution=res, random_state=random_state)
        results[res] = {
            'labels': labels,
            'n_clusters': len(np.unique(labels))
        }

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    n_clusters = [results[r]['n_clusters'] for r in resolutions]
    ax.plot(resolutions, n_clusters, 'bo-')
    ax.set_xlabel('Resolution')
    ax.set_ylabel('Number of clusters')
    ax.set_title(f'{method.capitalize()} - Resolution vs Cluster Count')

    return results, fig
```

### Using Scanpy (Recommended for Single-Cell)

```python
import scanpy as sc

def scanpy_clustering(adata, n_neighbors=15, n_pcs=50, resolution=1.0):
    """
    Standard Scanpy clustering pipeline.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix
    n_neighbors : int
        k for k-NN graph
    n_pcs : int
        Number of PCs to use
    resolution : float
        Clustering resolution

    Returns
    -------
    AnnData
        Updated with clustering results
    """
    # PCA (if not already computed)
    if 'X_pca' not in adata.obsm:
        sc.pp.pca(adata, n_comps=n_pcs)

    # Build neighbor graph
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs)

    # Leiden clustering
    sc.tl.leiden(adata, resolution=resolution)

    # UMAP for visualization
    sc.tl.umap(adata)

    return adata


def plot_clusters(adata, color='leiden'):
    """Plot clusters on UMAP."""
    sc.pl.umap(adata, color=color, legend_loc='on data')
```

### R Implementation (Seurat)

```r
library(Seurat)

# Standard Seurat clustering
seurat_clustering <- function(seurat_obj, dims = 1:30, resolution = 0.8) {
  # Find neighbors
  seurat_obj <- FindNeighbors(seurat_obj, dims = dims)

  # Cluster
  seurat_obj <- FindClusters(seurat_obj, resolution = resolution)

  # UMAP
  seurat_obj <- RunUMAP(seurat_obj, dims = dims)

  seurat_obj
}

# Resolution sweep
resolution_sweep <- function(seurat_obj, dims = 1:30,
                             resolutions = c(0.2, 0.4, 0.6, 0.8, 1.0)) {
  seurat_obj <- FindNeighbors(seurat_obj, dims = dims)

  for (res in resolutions) {
    seurat_obj <- FindClusters(seurat_obj, resolution = res,
                               verbose = FALSE)
  }

  # Clustering tree visualization
  library(clustree)
  clustree(seurat_obj, prefix = "RNA_snn_res.")
}
```

---

## Density-Based Clustering

### DBSCAN

**Advantages**:
- Finds arbitrary-shaped clusters
- Automatically detects outliers/noise
- No need to specify k

**Parameters**:
- `eps`: Neighborhood radius
- `min_samples`: Minimum points to form cluster

```python
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import numpy as np
import matplotlib.pyplot as plt

def run_dbscan(data, eps=0.5, min_samples=5):
    """Run DBSCAN clustering."""
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(data)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    return {
        'labels': labels,
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'noise_fraction': n_noise / len(labels)
    }


def find_optimal_eps(data, k=5):
    """
    Find optimal eps using k-distance graph.

    The elbow in the k-distance plot suggests good eps value.
    """
    nn = NearestNeighbors(n_neighbors=k)
    nn.fit(data)
    distances, _ = nn.kneighbors(data)

    # k-th nearest neighbor distance
    k_distances = distances[:, k-1]
    k_distances = np.sort(k_distances)[::-1]

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(k_distances)), k_distances)
    ax.set_xlabel('Points (sorted)')
    ax.set_ylabel(f'{k}-th nearest neighbor distance')
    ax.set_title('k-Distance Graph (elbow = optimal eps)')

    return fig
```

### HDBSCAN

**Advantages over DBSCAN**:
- Handles variable density
- More robust parameter selection
- Cluster stability metrics

```python
import hdbscan

def run_hdbscan(data, min_cluster_size=15, min_samples=None):
    """
    Run HDBSCAN clustering.

    Parameters
    ----------
    data : array-like
        Samples × features matrix
    min_cluster_size : int
        Minimum cluster size
    min_samples : int, optional
        Minimum samples in neighborhood (default: min_cluster_size)
    """
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_epsilon=0.0
    )

    labels = clusterer.fit_predict(data)

    return {
        'labels': labels,
        'probabilities': clusterer.probabilities_,  # Cluster membership strength
        'outlier_scores': clusterer.outlier_scores_,
        'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
        'clusterer': clusterer
    }


def plot_hdbscan_tree(clusterer):
    """Plot condensed tree for cluster selection."""
    clusterer.condensed_tree_.plot(select_clusters=True)
```

---

## Cluster Validation

### Internal Validation Metrics

```python
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score,
    davies_bouldin_score
)

def evaluate_clustering(data, labels):
    """
    Compute internal validation metrics.

    Higher silhouette and Calinski-Harabasz = better.
    Lower Davies-Bouldin = better.
    """
    # Remove noise points if present
    mask = labels != -1
    if mask.sum() < 2:
        return None

    data_clean = data[mask]
    labels_clean = labels[mask]

    if len(np.unique(labels_clean)) < 2:
        return None

    return {
        'silhouette': silhouette_score(data_clean, labels_clean),
        'calinski_harabasz': calinski_harabasz_score(data_clean, labels_clean),
        'davies_bouldin': davies_bouldin_score(data_clean, labels_clean),
        'n_clusters': len(np.unique(labels_clean)),
        'n_samples': len(labels_clean)
    }
```

### External Validation (with known labels)

```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

def compare_to_ground_truth(true_labels, predicted_labels):
    """Compare clustering to known labels."""
    return {
        'adjusted_rand_index': adjusted_rand_score(true_labels, predicted_labels),
        'normalized_mutual_info': normalized_mutual_info_score(true_labels, predicted_labels)
    }
```

---

## Reporting in Manuscripts

### Methods Section

```markdown
**Clustering analysis**

[For hierarchical clustering]:
Hierarchical clustering was performed using Ward's method with
Pearson correlation distance. The dendrogram was cut to obtain
[k] clusters based on [silhouette analysis / gap statistic / domain knowledge].

[For k-means]:
K-means clustering (k=[N]) was performed with 25 random initializations.
The optimal number of clusters was determined using the elbow method
and silhouette analysis.

[For graph-based (single-cell)]:
Cells were clustered using the Leiden algorithm on a shared nearest
neighbor graph (k=15 neighbors, resolution=[X]). [N] clusters were
identified. Cluster stability was assessed across resolution parameters
from 0.2 to 2.0.
```

### Figure Legends

```markdown
**Figure X. Clustering reveals [N] distinct [sample/cell] populations.**

(A) Hierarchical clustering dendrogram of [N] samples using Ward's linkage
and correlation distance. Samples colored by [condition/cluster assignment].

(B) Heatmap of [top variable genes / markers] with samples (columns) and
genes (rows) clustered independently. Color scale indicates [z-score /
log2 expression].

(C) UMAP visualization of [cells] colored by Leiden cluster assignment
(resolution=[X]).
```

---

## References

1. Ward JH (1963). Hierarchical grouping to optimize an objective function.
   *JASA* 58:236-244.

2. Lloyd S (1982). Least squares quantization in PCM.
   *IEEE Trans Inf Theory* 28:129-137.

3. Traag VA, Waltman L, van Eck NJ (2019). From Louvain to Leiden:
   guaranteeing well-connected communities. *Sci Rep* 9:5233.

4. Ester M, et al. (1996). A density-based algorithm for discovering
   clusters in large spatial databases with noise. *KDD*.

5. McInnes L, Healy J, Astels S (2017). HDBSCAN: Hierarchical density
   based clustering. *JOSS* 2:205.
