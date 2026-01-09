"""
Pytest fixtures for reproducible-research validation tests.

Provides temporary project structures at various reproducibility levels
for testing the scan_project and validate_environment scripts.
"""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create an empty temporary project directory."""
    return tmp_path


@pytest.fixture
def minimal_project(tmp_path: Path) -> Path:
    """Create a Level 1 (Minimal) project - score ~20."""
    project = tmp_path / "minimal_project"
    project.mkdir()

    # Just a README
    (project / "README.md").write_text("# Minimal Project\n\nA minimal project.\n")

    return project


@pytest.fixture
def standard_project(tmp_path: Path) -> Path:
    """Create a Level 2 (Standard) project - score ~50."""
    project = tmp_path / "standard_project"
    project.mkdir()

    # README with basic sections
    (project / "README.md").write_text(
        """# Standard Project

## Installation

Install dependencies with pip.

## Usage

Run the main script.

## Output

Results are saved to output/.
"""
    )

    # License
    (project / "LICENSE").write_text("MIT License\n")

    # Requirements (unpinned)
    (project / "requirements.txt").write_text(
        """numpy
pandas
matplotlib
"""
    )

    # A script
    scripts_dir = project / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "analysis.py").write_text(
        """import numpy as np

def analyze():
    pass
"""
    )

    return project


@pytest.fixture
def complete_project(tmp_path: Path) -> Path:
    """Create a Level 3 (Complete) project - score ~75."""
    project = tmp_path / "complete_project"
    project.mkdir()

    # README with all sections
    (project / "README.md").write_text(
        """# Complete Project

## Requirements

Python 3.11+ and the dependencies listed in environment.yml.

## Methods

This project implements a data analysis pipeline.

## Usage

Run the scripts in order: 01_preprocess.py, 02_analyze.py, 03_visualize.py.

## Output

Results are saved to results/.
"""
    )

    # License
    (project / "LICENSE").write_text("MIT License\n")

    # Conda environment with pinned versions
    (project / "environment.yml").write_text(
        """name: complete_project
channels:
  - conda-forge
dependencies:
  - python=3.11.5
  - numpy=1.26.0
  - pandas=2.1.0
  - matplotlib=3.8.0
"""
    )

    # Config file
    (project / "config.yaml").write_text(
        """parameters:
  seed: 42
  n_samples: 1000
"""
    )

    # Numbered scripts
    scripts_dir = project / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "01_preprocess.py").write_text(
        """import numpy as np

SEED = 42
np.random.seed(SEED)

def preprocess():
    pass
"""
    )
    (scripts_dir / "02_analyze.py").write_text(
        """import numpy as np

def analyze():
    pass
"""
    )

    # Data directory with documentation
    data_dir = project / "data"
    data_dir.mkdir()
    raw_dir = data_dir / "raw"
    raw_dir.mkdir()
    (raw_dir / "README.md").write_text(
        """# Raw Data

Data obtained from GEO accession GSE12345.
DOI: 10.1234/example
"""
    )

    return project


@pytest.fixture
def exemplary_project(tmp_path: Path) -> Path:
    """Create a Level 4 (Exemplary) project - score ~95."""
    project = tmp_path / "exemplary_project"
    project.mkdir()

    # Comprehensive README
    (project / "README.md").write_text(
        """# Exemplary Project

## Requirements

- Python 3.11+
- Conda environment specified in environment.yml
- Docker for containerized execution

## Methods

This project implements a reproducible RNA-seq analysis pipeline
following FAIR principles.

## Workflow

Execute scripts in numerical order:
1. 01_download.py - Download raw data
2. 02_preprocess.py - Quality control and preprocessing
3. 03_analyze.py - Statistical analysis
4. 04_visualize.py - Generate figures

## Output

Results are saved to results/ with the following structure:
- figures/ - Publication-ready figures
- tables/ - Statistical summaries
- logs/ - Execution logs
"""
    )

    # License
    (project / "LICENSE").write_text("MIT License\n")

    # Conda environment with all pinned
    (project / "environment.yml").write_text(
        """name: exemplary_project
channels:
  - conda-forge
  - nodefaults
dependencies:
  - python=3.11.5
  - numpy=1.26.0
  - pandas=2.1.0
  - matplotlib=3.8.0
  - scipy=1.11.0
  - pip:
    - scanpy==1.9.5
    - anndata==0.10.0
"""
    )

    # Config
    config_dir = project / "config"
    config_dir.mkdir()
    (config_dir / "params.yaml").write_text(
        """parameters:
  seed: 42
  n_samples: 1000
  alpha: 0.05
"""
    )

    # Numbered scripts with seeds
    scripts_dir = project / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "01_download.py").write_text(
        """#!/usr/bin/env python3
import os

def download():
    pass

if __name__ == "__main__":
    download()
"""
    )
    (scripts_dir / "02_preprocess.py").write_text(
        """#!/usr/bin/env python3
import numpy as np

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def preprocess():
    pass

if __name__ == "__main__":
    preprocess()
"""
    )
    (scripts_dir / "03_analyze.py").write_text(
        """#!/usr/bin/env python3
import numpy as np

np.random.seed(42)

def analyze():
    pass
"""
    )
    (scripts_dir / "04_visualize.py").write_text(
        """#!/usr/bin/env python3
def visualize():
    pass
"""
    )

    # Data with checksums
    data_dir = project / "data"
    data_dir.mkdir()
    raw_dir = data_dir / "raw"
    raw_dir.mkdir()
    (raw_dir / "README.md").write_text(
        """# Raw Data

Data downloaded from GEO (accession: GSE12345).
SRA accession: SRP123456
DOI: 10.1234/example.dataset
Zenodo archive: https://zenodo.org/record/123456
"""
    )
    (data_dir / "checksums.md5").write_text(
        """d41d8cd98f00b204e9800998ecf8427e  raw/sample1.fastq.gz
d41d8cd98f00b204e9800998ecf8427e  raw/sample2.fastq.gz
"""
    )

    # Dockerfile
    (project / "Dockerfile").write_text(
        """FROM continuumio/miniconda3:23.5.2-0

COPY environment.yml .
RUN conda env create -f environment.yml

COPY . /app
WORKDIR /app

CMD ["conda", "run", "-n", "exemplary_project", "python", "scripts/03_analyze.py"]
"""
    )

    # Docs with methods
    docs_dir = project / "docs"
    docs_dir.mkdir()
    (docs_dir / "methods.md").write_text(
        """# Methods

## Data Processing

Raw sequencing data was processed using...

## Statistical Analysis

Differential expression was calculated using...
"""
    )

    return project


@pytest.fixture
def valid_conda_env(tmp_path: Path) -> Path:
    """Create a valid conda environment.yml file."""
    env_file = tmp_path / "environment.yml"
    env_file.write_text(
        """name: test_env
channels:
  - conda-forge
dependencies:
  - python=3.11.5
  - numpy=1.26.0
  - pandas=2.1.0
"""
    )
    return env_file


@pytest.fixture
def invalid_conda_env(tmp_path: Path) -> Path:
    """Create an invalid conda environment.yml file (missing python)."""
    env_file = tmp_path / "environment.yml"
    env_file.write_text(
        """name: test_env
channels:
  - defaults
dependencies:
  - numpy
  - pandas
"""
    )
    return env_file


@pytest.fixture
def valid_requirements(tmp_path: Path) -> Path:
    """Create a valid requirements.txt file with pinned versions."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        """numpy==1.26.0
pandas==2.1.0
matplotlib==3.8.0
scipy==1.11.0
"""
    )
    return req_file


@pytest.fixture
def invalid_requirements(tmp_path: Path) -> Path:
    """Create requirements.txt with unpinned versions."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        """numpy
pandas>=2.0
matplotlib
"""
    )
    return req_file


@pytest.fixture
def valid_pyproject(tmp_path: Path) -> Path:
    """Create a valid pyproject.toml with pinned versions."""
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(
        """[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy==1.26.0",
    "pandas==2.1.0",
]
"""
    )
    return toml_file


@pytest.fixture
def hardcoded_path_project(tmp_path: Path) -> Path:
    """Create a project with hardcoded paths."""
    project = tmp_path / "hardcoded_project"
    project.mkdir()

    (project / "README.md").write_text("# Project\n")
    (project / "LICENSE").write_text("MIT\n")

    scripts_dir = project / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "bad_script.py").write_text(
        '''data_path = "/home/user/data/file.csv"
output_path = "/Users/john/output/"
'''
    )

    return project
