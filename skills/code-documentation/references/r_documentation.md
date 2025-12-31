# R Documentation Reference

> Guide to documenting R code with roxygen2 and pkgdown

---

## Overview

R documentation uses **roxygen2** for function and package documentation. Roxygen2 comments are written directly above functions and converted to `.Rd` files and NAMESPACE entries.

| Tool | Purpose |
|------|---------|
| **roxygen2** | Function/class documentation from inline comments |
| **pkgdown** | Package website from documentation |
| **R Markdown** | Vignettes and tutorials |
| **testthat** | Examples that also serve as tests |

---

## roxygen2 Basics

### Syntax

Roxygen2 comments start with `#'` and use tags prefixed with `@`:

```r
#' Short title for the function
#'
#' Longer description that explains what the function does.
#' Can span multiple lines.
#'
#' @param x Description of parameter x
#' @return Description of return value
#' @export
function_name <- function(x) {
  # implementation
}
```

---

## Function Documentation

### Complete Template

```r
#' Calculate log2 fold change between conditions
#'
#' Computes the ratio of treatment to control values with optional
#' log2 transformation. Adds a pseudocount to avoid division by zero
#' and log of zero issues common in expression data.
#'
#' @param treatment Numeric vector of expression values for treatment condition.
#' @param control Numeric vector of expression values for control condition.
#'   Must have the same length as `treatment`.
#' @param log2 Logical. If `TRUE` (default), return log2 fold change.
#'   If `FALSE`, return raw fold change ratio.
#' @param pseudocount Numeric. Value added before division/log transformation.
#'   Default is 1.
#'
#' @return Numeric vector of fold change values with the same length as input.
#'
#' @details
#' Log2 fold change interpretation:
#' \itemize{
#'   \item LFC = 1 means 2-fold increase
#'   \item LFC = -1 means 2-fold decrease
#'   \item LFC = 0 means no change
#' }
#'
#' For RNA-seq data, consider using DESeq2 or edgeR shrinkage estimators
#' for more robust fold change estimates with low-count genes.
#'
#' @seealso
#' \code{\link[DESeq2]{lfcShrink}} for shrunken fold change estimates,
#' \code{\link{normalize_counts}} for count normalization
#'
#' @references
#' Love MI, Huber W, Anders S. "Moderated estimation of fold change
#' and dispersion for RNA-seq data with DESeq2." Genome Biology, 2014.
#' \doi{10.1186/s13059-014-0550-8}
#'
#' @examples
#' treatment <- c(10, 20, 5)
#' control <- c(5, 10, 10)
#' calculate_fold_change(treatment, control)
#' # [1]  1  1 -1
#'
#' # Raw fold change (not log2)
#' calculate_fold_change(treatment, control, log2 = FALSE)
#' # [1] 2.0 2.0 0.5
#'
#' @export
calculate_fold_change <- function(treatment, control, log2 = TRUE, pseudocount = 1) {
  if (length(treatment) != length(control)) {
    stop("treatment and control must have the same length")
  }

  fc <- (treatment + pseudocount) / (control + pseudocount)

  if (log2) {
    return(log2(fc))
  }
  fc
}
```

---

## Common Tags Reference

### Essential Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `@param` | Document a parameter | `@param x Input vector` |
| `@return` | Document return value | `@return A data frame` |
| `@export` | Export to NAMESPACE | `@export` |
| `@examples` | Runnable examples | See below |

### Description Tags

| Tag | Description |
|-----|-------------|
| `@title` | Short title (or first line) |
| `@description` | Extended description (or paragraph after title) |
| `@details` | Additional details section |

### Cross-Reference Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `@seealso` | Related functions | `@seealso \code{\link{other_fun}}` |
| `@family` | Group related functions | `@family differential expression` |
| `@inheritParams` | Inherit param docs | `@inheritParams other_function` |
| `@references` | Citations | `@references Smith (2020) \doi{10.1234/example}` |

### Conditional/Special Tags

| Tag | Description |
|-----|-------------|
| `@importFrom` | Import specific function | `@importFrom dplyr filter select` |
| `@import` | Import whole package | `@import ggplot2` |
| `@noRd` | Don't generate .Rd file | For internal functions |
| `@keywords internal` | Mark as internal | Shows in docs but not index |

---

## S4 Class Documentation

```r
#' Differential Expression Results Class
#'
#' A container for storing differential expression analysis results
#' with methods for filtering, visualization, and export.
#'
#' @slot gene_ids Character vector of gene identifiers.
#' @slot log2fc Numeric vector of log2 fold changes.
#' @slot pvalues Numeric vector of raw p-values.
#' @slot padj Numeric vector of adjusted p-values.
#' @slot metadata List of analysis metadata.
#'
#' @seealso \code{\link{runDESeq2}} for generating results
#'
#' @examples
#' # Create from DESeq2 results
#' de <- DEResults(
#'   gene_ids = c("TP53", "BRCA1", "MYC"),
#'   log2fc = c(2.5, -1.2, 0.1),
#'   pvalues = c(0.001, 0.02, 0.8)
#' )
#'
#' # Access significant genes
#' significant(de, padj_threshold = 0.05)
#'
#' @export
setClass("DEResults",
  slots = c(
    gene_ids = "character",
    log2fc = "numeric",
    pvalues = "numeric",
    padj = "numeric",
    metadata = "list"
  )
)
```

---

## R6 Class Documentation

```r
#' @title Differential Expression Analysis
#'
#' @description
#' R6 class for performing and storing differential expression analysis.
#'
#' @details
#' This class provides an object-oriented interface for differential
#' expression analysis, including data loading, normalization,
#' statistical testing, and result visualization.
#'
#' @examples
#' de <- DEAnalysis$new(counts, metadata)
#' de$normalize(method = "TMM")
#' de$test(design = ~ condition)
#' de$plot_volcano()
#'
#' @export
DEAnalysis <- R6::R6Class("DEAnalysis",
  public = list(
    #' @field counts Raw count matrix (genes x samples)
    counts = NULL,

    #' @field metadata Sample metadata data frame
    metadata = NULL,

    #' @description
    #' Create a new DEAnalysis object.
    #'
    #' @param counts Count matrix with genes as rows, samples as columns.
    #' @param metadata Data frame with sample information. Row names must
    #'   match column names of counts.
    #'
    #' @return A new `DEAnalysis` object.
    initialize = function(counts, metadata) {
      self$counts <- counts
      self$metadata <- metadata
    },

    #' @description
    #' Normalize count data.
    #'
    #' @param method Normalization method: "TMM", "RLE", or "upperquartile".
    #'
    #' @return Invisibly returns self for method chaining.
    normalize = function(method = "TMM") {
      # implementation
      invisible(self)
    }
  )
)
```

---

## Package-Level Documentation

### DESCRIPTION File

```
Package: mypackage
Title: Differential Expression Analysis Tools
Version: 1.0.0
Authors@R:
    person("First", "Last", email = "email@example.com", role = c("aut", "cre"),
           comment = c(ORCID = "0000-0000-0000-0000"))
Description: Tools for differential expression analysis of RNA-seq data.
    Provides functions for normalization, statistical testing, and
    visualization of results. Integrates with DESeq2 and edgeR workflows.
License: MIT + file LICENSE
Encoding: UTF-8
Roxygen: list(markdown = TRUE)
RoxygenNote: 7.2.3
Imports:
    dplyr,
    ggplot2
Suggests:
    testthat (>= 3.0.0),
    knitr,
    rmarkdown
VignetteBuilder: knitr
URL: https://github.com/user/mypackage
BugReports: https://github.com/user/mypackage/issues
```

### Package Documentation File

Create `R/mypackage-package.R`:

```r
#' mypackage: Differential Expression Analysis Tools
#'
#' Tools for differential expression analysis of RNA-seq data,
#' including normalization, statistical testing, and visualization.
#'
#' @section Main functions:
#' \describe{
#'   \item{\code{\link{run_deseq2}}}{Run DESeq2 analysis}
#'   \item{\code{\link{run_edger}}}{Run edgeR analysis}
#'   \item{\code{\link{volcano_plot}}}{Create volcano plot}
#'   \item{\code{\link{get_significant}}}{Filter significant genes}
#' }
#'
#' @section Vignettes:
#' \itemize{
#'   \item \code{vignette("quickstart", package = "mypackage")} - Getting started
#'   \item \code{vignette("advanced", package = "mypackage")} - Advanced usage
#' }
#'
#' @docType package
#' @name mypackage
#' @aliases mypackage-package
#'
#' @importFrom stats p.adjust
#' @importFrom utils head
"_PACKAGE"
```

---

## Examples Best Practices

### Runnable Examples

```r
#' @examples
#' # Basic usage
#' x <- c(1, 2, 3, 4, 5)
#' result <- my_function(x)
#'
#' # With options
#' result2 <- my_function(x, normalize = TRUE)
```

### Examples with Conditionals

```r
#' @examples
#' # Only run if suggested package is available
#' if (requireNamespace("ggplot2", quietly = TRUE)) {
#'   plot_results(de_results)
#' }
#'
#' \dontrun{
#' # This won't run during R CMD check (slow/needs external resources)
#' fetch_from_database("gene_list.txt")
#' }
#'
#' \donttest{
#' # Skip during CRAN checks but run locally
#' slow_computation(large_data)
#' }
```

### Using Example Data

```r
#' @examples
#' # Use package data
#' data(example_counts)
#' result <- analyze(example_counts)
#'
#' # Create minimal example data
#' counts <- matrix(rpois(100, lambda = 10), nrow = 10)
#' rownames(counts) <- paste0("gene", 1:10)
#' colnames(counts) <- paste0("sample", 1:10)
#' result <- analyze(counts)
```

---

## Formatting in Documentation

### Text Formatting

```r
#' @details
#' Use \code{code_font} for inline code.
#' Use \emph{emphasis} for emphasis.
#' Use \strong{bold} for strong emphasis.
#' Use \pkg{packagename} for package names.
#' Use \file{path/to/file} for file paths.
```

### Lists

```r
#' @details
#' Itemized list:
#' \itemize{
#'   \item First item
#'   \item Second item
#' }
#'
#' Enumerated list:
#' \enumerate{
#'   \item First step
#'   \item Second step
#' }
#'
#' Description list:
#' \describe{
#'   \item{term1}{Definition of term1}
#'   \item{term2}{Definition of term2}
#' }
```

### Links

```r
#' @seealso
#' \code{\link{function_in_same_pkg}}
#' \code{\link[other.pkg]{function_in_other_pkg}}
#' \url{https://example.com}
#' \href{https://example.com}{Link text}
#' \doi{10.1234/example}
```

### Math

```r
#' @details
#' The formula is \eqn{x^2 + y^2 = z^2} for inline math.
#'
#' For display math:
#' \deqn{
#'   \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
#' }
```

---

## Building Documentation

### Generate Docs

```r
# Generate man/ files from roxygen comments
devtools::document()

# Or with roxygen2 directly
roxygen2::roxygenize()
```

### Build Package Website (pkgdown)

```r
# Setup
usethis::use_pkgdown()

# Build site
pkgdown::build_site()

# Build just reference pages
pkgdown::build_reference()
```

### Check Documentation

```r
# Check package including docs
devtools::check()

# Check a specific man page
tools::checkRd("man/my_function.Rd")

# Preview a function's help
devtools::load_all()
?my_function
```

---

## Common Mistakes

### 1. Missing @export

```r
# BAD - function won't be exported
#' My function
my_function <- function(x) { x + 1 }

# GOOD
#' My function
#' @export
my_function <- function(x) { x + 1 }
```

### 2. Parameter Name Mismatch

```r
# BAD - @param name doesn't match actual parameter
#' @param data Input data  # But function uses 'x'
my_function <- function(x) { ... }

# GOOD
#' @param x Input data
my_function <- function(x) { ... }
```

### 3. Examples That Fail

```r
# BAD - example fails because result isn't assigned
#' @examples
#' calculate_mean(1:10)
#' print(result)  # Error: 'result' not found

# GOOD
#' @examples
#' result <- calculate_mean(1:10)
#' print(result)
```

---

## Vignettes

### Create a Vignette

```r
usethis::use_vignette("introduction")
```

### Vignette Header

```yaml
---
title: "Introduction to mypackage"
author: "Your Name"
date: "`r Sys.Date()`"
output: rmarkdown::html_vignette
vignette: >
  %\VignetteIndexEntry{Introduction to mypackage}
  %\VignetteEngine{knitr::rmarkdown}
  %\VignetteEncoding{UTF-8}
---
```

### Vignette Structure

```markdown
# Overview

Brief introduction to what the package does.

# Installation

\```{r, eval = FALSE}
install.packages("mypackage")
\```

# Quick Start

\```{r}
library(mypackage)
data(example_data)
result <- analyze(example_data)
\```

# Detailed Usage

## Step 1: Load Data

...

## Step 2: Analyze

...

# Session Info

\```{r}
sessionInfo()
\```
```
