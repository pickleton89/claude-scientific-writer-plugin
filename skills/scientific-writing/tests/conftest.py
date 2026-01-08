"""Pytest configuration and shared fixtures for scientific-writing tests."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def sample_imrad_manuscript():
    """Return a well-formed IMRAD manuscript."""
    return """# Abstract

This study investigated the effects of X on Y.

# Introduction

Background information about the research topic.

# Methods

We performed a randomized controlled trial with 100 participants.

# Results

The treatment group showed significant improvement (p < 0.05).

# Discussion

These findings suggest that X is effective for Y.

# References

1. Smith et al. (2023)
"""


@pytest.fixture
def incomplete_manuscript():
    """Return a manuscript missing some IMRAD sections."""
    return """# Abstract

This study investigated something.

# Introduction

Background info.

# Results

Some findings here.
"""


@pytest.fixture
def misordered_manuscript():
    """Return a manuscript with IMRAD sections in wrong order."""
    return """# Abstract

Abstract text.

# Results

Results before methods.

# Methods

Methods after results.

# Introduction

Introduction after results.

# Discussion

Discussion section.
"""
