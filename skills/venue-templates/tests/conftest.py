"""Pytest configuration and fixtures for venue-templates tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def sample_nature_text() -> str:
    """Sample text written in Nature style."""
    return """
    Abstract
    We discovered a fundamental mechanism of gene regulation that has
    broad implications for understanding cellular development. Using
    a combination of genetic and biochemical approaches, we show that
    protein X controls the expression of hundreds of downstream genes.
    Our findings reveal unexpected complexity in gene regulatory networks.

    Introduction
    Gene regulation is central to cellular function. Despite decades of
    research, many aspects of how genes are controlled remain poorly
    understood. Here we show that a previously uncharacterized pathway
    plays a critical role in this process.
    """


@pytest.fixture
def sample_neurips_text() -> str:
    """Sample text written in NeurIPS style."""
    return """
    Abstract
    We propose TransformerX, a novel architecture for sequence modeling
    that achieves 95.2% accuracy on GLUE benchmark, outperforming BERT
    by 3.1%. Our method introduces a new attention mechanism that reduces
    computational complexity from O(n^2) to O(n log n).

    Introduction
    Large language models have revolutionized NLP. In this paper, we
    make the following contributions:
    - We propose TransformerX, a novel architecture
    - We provide theoretical analysis of convergence
    - We demonstrate state-of-the-art results on 5 benchmarks
    - We release code and pretrained models
    """


@pytest.fixture
def sample_medical_text() -> str:
    """Sample text written in medical journal style."""
    return """
    Abstract
    Background: Cardiovascular disease is a leading cause of mortality.
    Methods: We conducted a randomized controlled trial with 500 patients.
    Results: Treatment reduced mortality by 25% (95% CI: 15-35%).
    Conclusions: The intervention is effective for preventing cardiac events.

    Introduction
    Heart disease affects millions worldwide. Previous studies have shown
    that lifestyle interventions may reduce risk.
    """


@pytest.fixture
def sample_passive_text() -> str:
    """Sample text with heavy passive voice usage."""
    return """
    The experiment was conducted using standard protocols. Samples were
    collected from multiple sites. Data were analyzed using statistical
    methods. Results were found to be significant. The hypothesis was
    confirmed by the experimental evidence. Conclusions were drawn based
    on the observed patterns.
    """


@pytest.fixture
def sample_active_text() -> str:
    """Sample text with active voice."""
    return """
    We conducted the experiment using standard protocols. We collected
    samples from multiple sites. We analyzed the data using statistical
    methods. We found significant results. We confirmed our hypothesis
    through experimental evidence. We drew conclusions based on the
    observed patterns.
    """
