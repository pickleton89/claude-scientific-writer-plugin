# API Documentation Guide

> Documentation for reusable Python and R packages

---

## Overview

API documentation serves developers who use your code. It should be:

- **Complete**: Every public function, class, and module documented
- **Accurate**: Always matches current behavior
- **Navigable**: Easy to find what you need
- **Tested**: Examples that actually work

| Tool | Language | Output |
|------|----------|--------|
| Sphinx | Python | HTML, PDF, ePub |
| pdoc | Python | HTML (simpler) |
| pkgdown | R | HTML website |
| roxygen2 | R | .Rd files (man pages) |

---

## Python: Sphinx

### Project Setup

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Create docs directory
mkdir docs
cd docs

# Initialize Sphinx
sphinx-quickstart
```

### Directory Structure

```
mypackage/
├── mypackage/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── docs/
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Main page
│   ├── installation.rst  # Installation guide
│   ├── quickstart.rst    # Getting started
│   ├── api/              # API reference
│   │   ├── index.rst
│   │   ├── core.rst
│   │   └── utils.rst
│   └── _build/           # Generated output
├── tests/
└── pyproject.toml
```

### conf.py Configuration

```python
# docs/conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'MyPackage'
author = 'Your Name'
release = '1.0.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',           # Pull docs from docstrings
    'sphinx.ext.napoleon',          # Support NumPy/Google style
    'sphinx.ext.viewcode',          # Link to source code
    'sphinx.ext.intersphinx',       # Link to other docs
    'sphinx_autodoc_typehints',     # Use type hints
]

# Napoleon settings (for NumPy/Google docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Theme
html_theme = 'sphinx_rtd_theme'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}
```

### index.rst (Main Page)

```rst
MyPackage Documentation
=======================

MyPackage is a library for differential expression analysis.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

### API Reference Page

```rst
.. api/core.rst

Core Module
===========

.. automodule:: mypackage.core
   :members:
   :undoc-members:
   :show-inheritance:

Classes
-------

.. autoclass:: mypackage.core.DEResults
   :members:
   :special-members: __init__

Functions
---------

.. autofunction:: mypackage.core.calculate_fold_change

.. autofunction:: mypackage.core.run_differential_expression
```

### Building Documentation

```bash
# Build HTML
cd docs
make html

# Build and auto-refresh during development
pip install sphinx-autobuild
sphinx-autobuild . _build/html

# Clean and rebuild
make clean html
```

---

## Python: pdoc (Simpler Alternative)

For smaller packages, pdoc offers simpler setup:

```bash
# Install
pip install pdoc

# Generate HTML
pdoc --html mypackage --output-dir docs

# Live preview
pdoc --http localhost:8080 mypackage
```

pdoc works entirely from docstrings—no configuration needed.

---

## R: pkgdown

### Setup

```r
# Install
install.packages("pkgdown")

# Initialize
usethis::use_pkgdown()
```

### _pkgdown.yml Configuration

```yaml
# _pkgdown.yml

url: https://user.github.io/mypackage

template:
  bootstrap: 5
  bootswatch: cosmo

home:
  title: MyPackage
  description: Differential expression analysis tools

navbar:
  structure:
    left:  [intro, reference, articles, tutorials, news]
    right: [search, github]

reference:
  - title: Main Functions
    desc: Core analysis functions
    contents:
      - run_deseq2
      - run_edger
      - get_significant

  - title: Visualization
    desc: Plotting functions
    contents:
      - volcano_plot
      - ma_plot
      - heatmap

  - title: Data Classes
    desc: Result containers
    contents:
      - DEResults
      - EnrichmentResults

  - title: Utilities
    desc: Helper functions
    contents:
      - starts_with("helper_")

articles:
  - title: Getting Started
    navbar: Getting Started
    contents:
      - mypackage
      - quickstart

  - title: Advanced Usage
    navbar: Advanced
    contents:
      - batch-correction
      - custom-contrasts
```

### Building the Site

```r
# Build full site
pkgdown::build_site()

# Build just reference
pkgdown::build_reference()

# Build just articles
pkgdown::build_articles()

# Preview locally
pkgdown::preview_site()
```

### Deploy to GitHub Pages

```r
# Setup GitHub Actions
usethis::use_pkgdown_github_pages()
```

This creates `.github/workflows/pkgdown.yaml` for automatic deployment.

---

## Documentation Structure

### Organizing by User Journey

```
Getting Started (for new users)
├── Installation
├── Quick Start
└── Basic Tutorial

User Guide (for regular users)
├── Core Concepts
├── Common Tasks
├── Configuration
└── Advanced Topics

API Reference (for developers)
├── Modules/Packages
├── Classes
├── Functions
└── Constants

Developer Guide (for contributors)
├── Contributing
├── Architecture
├── Testing
└── Release Process
```

### Module/Package Overview Pages

Each module should have an overview:

```rst
Analysis Module
===============

The ``analysis`` module provides functions for differential
expression analysis of RNA-seq data.

Quick Example
-------------

.. code-block:: python

    from mypackage import analysis

    results = analysis.run_deseq2(counts, metadata)
    significant = analysis.get_significant(results)

Submodules
----------

.. autosummary::
   :toctree: generated

   analysis.differential
   analysis.enrichment
   analysis.visualization
```

---

## Best Practices

### Versioning Documentation

Document which version the docs apply to:

```rst
.. note::
   This documentation is for MyPackage v2.0.
   For v1.x documentation, see `here <link>`_.
```

### Deprecation Notices

```python
import warnings

def old_function(x):
    """
    Original function.

    .. deprecated:: 2.0
       Use :func:`new_function` instead.
    """
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function(x)
```

### Code Examples That Work

All examples should be tested:

**Python (doctest):**

```python
def add(a, b):
    """
    Add two numbers.

    Examples
    --------
    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b
```

```bash
# Run doctests
python -m doctest mymodule.py
pytest --doctest-modules
```

**R (examples):**

```r
#' @examples
#' add(2, 3)
#' #> [1] 5
```

```r
# Check examples during R CMD check
devtools::check()
```

### Cross-References

Link related functions:

**Sphinx:**

```rst
See :func:`related_function` for more details.
See :class:`MyClass` for the main interface.
See :doc:`tutorial` for a complete walkthrough.
```

**roxygen2:**

```r
#' @seealso \code{\link{related_function}}
#' @family analysis functions
```

---

## Automating Documentation

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: docs
        name: Build docs
        entry: make -C docs html
        language: system
        pass_filenames: false
```

### GitHub Actions (Python)

```yaml
# .github/workflows/docs.yml
name: Docs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[docs]"

      - name: Build docs
        run: |
          cd docs
          make html

      - name: Deploy to GitHub Pages
        if: github.event_name == 'push'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

### GitHub Actions (R)

```yaml
# .github/workflows/pkgdown.yaml
name: pkgdown

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  pkgdown:
    runs-on: ubuntu-latest
    env:
      GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4

      - uses: r-lib/actions/setup-r@v2

      - uses: r-lib/actions/setup-pandoc@v2

      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: any::pkgdown

      - name: Build site
        run: pkgdown::build_site_github_pages(new_process = FALSE)
        shell: Rscript {0}

      - name: Deploy
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: docs
```

---

## Documentation Hosting

### Options

| Platform | Cost | Features |
|----------|------|----------|
| Read the Docs | Free (open source) | Versioning, search, PDF |
| GitHub Pages | Free | Simple static hosting |
| GitLab Pages | Free | CI/CD integration |
| Netlify | Free tier | Deploy previews, forms |

### Read the Docs Setup

1. Create `.readthedocs.yaml`:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.10"

sphinx:
  configuration: docs/conf.py

python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```

2. Connect repo at readthedocs.org

### GitHub Pages Setup

```yaml
# In conf.py for Sphinx
html_baseurl = 'https://username.github.io/mypackage/'

# Enable GitHub Pages in repo settings
# Source: gh-pages branch or docs/ folder
```

---

## Quick Reference

### Sphinx Directives

| Directive | Purpose |
|-----------|---------|
| `.. automodule::` | Document entire module |
| `.. autoclass::` | Document a class |
| `.. autofunction::` | Document a function |
| `.. autosummary::` | Generate summary table |
| `.. toctree::` | Table of contents |
| `.. note::` | Note admonition |
| `.. warning::` | Warning admonition |
| `.. code-block::` | Syntax-highlighted code |

### roxygen2 Tags

| Tag | Purpose |
|-----|---------|
| `@param` | Document parameter |
| `@return` | Document return value |
| `@export` | Export from namespace |
| `@examples` | Usage examples |
| `@seealso` | Related functions |
| `@family` | Group related functions |
| `@inheritParams` | Inherit param docs |

### Common Commands

```bash
# Python/Sphinx
cd docs && make html          # Build HTML
sphinx-autobuild . _build/html  # Live reload
make clean                    # Clean build

# R/pkgdown
pkgdown::build_site()         # Build full site
pkgdown::build_reference()    # Build API only
devtools::document()          # Generate .Rd from roxygen
```
