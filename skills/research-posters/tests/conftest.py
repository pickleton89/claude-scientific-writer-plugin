"""
Pytest fixtures for research-posters validation tests.

Provides reusable test data including:
- Sample LaTeX content
- Color palettes
- Poster specifications
- Mock validation results
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


# =============================================================================
# Color Fixtures
# =============================================================================


@pytest.fixture
def oligon_colors():
    """Oligon brand color palette."""
    return {
        "brand_blue": "#2DB2E8",
        "brand_orange": "#E8622D",
        "dark_gray": "#222222",
        "medium_gray": "#666666",
        "light_gray": "#E5E5E5",
        "white": "#FFFFFF",
        "black": "#000000",
    }


@pytest.fixture
def high_contrast_pair():
    """Color pair with high contrast (passes WCAG AAA)."""
    return {"foreground": "#000000", "background": "#FFFFFF"}


@pytest.fixture
def low_contrast_pair():
    """Color pair with low contrast (fails WCAG)."""
    return {"foreground": "#CCCCCC", "background": "#FFFFFF"}


@pytest.fixture
def colorblind_safe_palette():
    """Palette that is distinguishable under color vision deficiency."""
    return ["#2DB2E8", "#E8622D", "#222222"]


@pytest.fixture
def colorblind_unsafe_palette():
    """Palette with colors that may be confused under CVD."""
    return ["#FF0000", "#00FF00", "#FFFF00"]  # Red/green confusion


# =============================================================================
# Dimension Fixtures
# =============================================================================


@pytest.fixture
def a0_portrait_pts():
    """A0 portrait dimensions in points."""
    return {"width": 2384, "height": 3370}


@pytest.fixture
def a0_landscape_pts():
    """A0 landscape dimensions in points."""
    return {"width": 3370, "height": 2384}


@pytest.fixture
def us_36x48_pts():
    """US 36x48 inch poster dimensions in points."""
    return {"width": 2592, "height": 3456}


@pytest.fixture
def non_standard_pts():
    """Non-standard poster dimensions in points."""
    return {"width": 2000, "height": 3000}


# =============================================================================
# LaTeX Content Fixtures
# =============================================================================


@pytest.fixture
def sample_tikzposter_content():
    """Sample tikzposter LaTeX content with blocks."""
    return r"""
\documentclass[25pt, a0paper, portrait]{tikzposter}
\usepackage{tikz}

\title{Sample Research Poster Title for Testing}
\author{John Smith\textsuperscript{1}, Jane Doe\textsuperscript{2}}
\institute{\textsuperscript{1}University of Testing, \textsuperscript{2}Institute of Science}

\definecolor{brandblue}{HTML}{2DB2E8}
\definecolor{brandorange}{HTML}{E8622D}

\begin{document}
\maketitle

\block{Introduction}{
This is the introduction section with some sample text to test word counting.
The research presented here demonstrates important scientific findings.
We hypothesize that this approach will yield significant improvements.
Background context and motivation are provided in this section.
}

\block{Methods}{
The methodology employed in this study involves several key steps.
First, we collected data from multiple sources and validated the inputs.
Second, we applied our novel algorithm to process the information.
Third, we analyzed the results using statistical methods.
Data collection spanned three months with weekly measurements.
Quality control measures ensured data integrity throughout.
}

\block{Results}{
Our findings demonstrate a significant improvement over baseline methods.
Figure 1 shows the comparison between our approach and existing solutions.
Table 1 presents the quantitative metrics for each experimental condition.
Statistical analysis confirms the significance of our results with p < 0.05.
The improvement was consistent across all tested scenarios and conditions.
Performance gains ranged from 15% to 45% depending on the specific metric.
These results support our initial hypothesis about the effectiveness.
}

\block{Conclusions}{
In conclusion, our research makes several important contributions.
The proposed method outperforms existing approaches significantly.
Future work will explore additional applications and optimizations.
We thank our collaborators and funding agencies for their support.
}

\block{References}{
[1] Smith, J. et al. (2025). Important Research Paper. Journal of Science.
[2] Doe, J. et al. (2024). Another Relevant Study. Science Reports.
}

\end{document}
"""


@pytest.fixture
def sample_beamerposter_content():
    """Sample beamerposter LaTeX content."""
    return r"""
\documentclass{beamer}
\usepackage[orientation=portrait,size=a0,scale=1.4]{beamerposter}

\title{Beamerposter Research Title}
\author{Test Author}
\institute{Test Institute}

\begin{document}
\begin{frame}{}

\begin{block}{Introduction}
Introduction text for the beamerposter format test.
This contains enough words to test the counting functionality.
\end{block}

\begin{block}{Methods}
Methods description with adequate detail for testing purposes.
Multiple sentences ensure proper word counting validation.
\end{block}

\begin{block}{Results}
Results section showing important findings from the research.
Data and analysis are presented in a clear and concise manner.
\end{block}

\begin{block}{Conclusions}
Conclusions summarizing the key takeaways from this work.
\end{block}

\end{frame}
\end{document}
"""


@pytest.fixture
def sample_baposter_content():
    """Sample baposter LaTeX content with headerbox."""
    return r"""
\documentclass[a0paper,portrait]{baposter}

\begin{document}
\begin{poster}{
  columns=3,
  background=plain,
  bgColorOne=white
}
{}
{Sample Baposter Title}
{Author Name}
{Institution}

\headerbox{Introduction}{name=intro,column=0,row=0}{
Introduction content for baposter format testing.
This section provides background and motivation.
}

\headerbox{Methods}{name=methods,column=1,row=0}{
Methodology description for the research study.
Detailed steps and procedures are outlined here.
}

\headerbox{Results}{name=results,column=2,row=0}{
Key findings and results from the experiments.
Statistical significance was achieved for main outcomes.
}

\headerbox{Conclusions}{name=conclusions,column=0,row=1,span=3}{
Summary of conclusions and future directions.
}

\end{poster}
\end{document}
"""


@pytest.fixture
def latex_with_colors():
    """LaTeX content with color definitions."""
    return r"""
\documentclass{article}
\usepackage{xcolor}

\definecolor{primaryBlue}{HTML}{2DB2E8}
\definecolor{accentOrange}{HTML}{E8622D}
\definecolor{textGray}{RGB}{34, 34, 34}
\definecolor{lightBg}{rgb}{0.9, 0.9, 0.9}

\begin{document}
\textcolor{primaryBlue}{Blue text}
\textcolor{accentOrange}{Orange text}
\end{document}
"""


# =============================================================================
# Poster Specification Fixtures
# =============================================================================


@pytest.fixture
def valid_poster_spec():
    """Valid complete poster specification."""
    return {
        "title": "Test Research Poster",
        "dimensions": "A0",
        "orientation": "portrait",
        "poster_format": "latex",
        "latex_package": "tikzposter",
        "brand": "oligon",
        "authors": [
            {"name": "John Smith", "affiliation": 1, "presenting": True},
            {"name": "Jane Doe", "affiliation": 2, "presenting": False},
        ],
        "affiliations": {
            1: "University of Testing",
            2: "Institute of Science",
        },
        "content": {
            "introduction": {"word_budget": 100, "key_points": ["Background", "Objective"]},
            "methods": {"word_budget": 150},
            "results": {"word_budget": 200, "figure_id": "fig1"},
            "conclusions": {"word_budget": 100},
        },
        "figures": [
            {"id": "fig1", "figure_type": "chart", "description": "Main results"},
            {"id": "fig2", "figure_type": "schematic", "description": "Methods diagram"},
        ],
    }


@pytest.fixture
def minimal_poster_spec():
    """Minimal valid poster specification."""
    return {
        "title": "Minimal Poster",
        "dimensions": "A0",
    }


@pytest.fixture
def invalid_poster_spec():
    """Invalid poster specification with multiple errors."""
    return {
        "dimensions": "A0",  # Missing title
        "orientation": "diagonal",  # Invalid orientation
        "poster_format": "word",  # Invalid format
        "authors": [
            {"name": "John", "affiliation": 99},  # Invalid affiliation reference
        ],
        "affiliations": {1: "University"},
        "content": {
            "results": {"word_budget": -50, "figure_id": "nonexistent"},
        },
    }


# =============================================================================
# Validation Result Fixtures
# =============================================================================


@pytest.fixture
def passing_word_count():
    """Word count result that passes validation."""
    return {
        "total": 500,
        "by_section": {
            "introduction": 100,
            "methods": 150,
            "results": 175,
            "conclusions": 75,
        },
    }


@pytest.fixture
def failing_word_count():
    """Word count result that fails validation (too few words)."""
    return {
        "total": 150,
        "by_section": {
            "introduction": 50,
            "methods": 50,
            "results": 50,
        },
    }


@pytest.fixture
def sample_quality_report():
    """Sample quality report structure."""
    return {
        "poster_path": "test_poster.pdf",
        "source_path": "test_poster.tex",
        "overall_pass": True,
        "checks": {
            "word_count": {
                "total": 500,
                "target_range": [300, 800],
                "pass": True,
            },
            "dimensions": {
                "width_pts": 2384,
                "height_pts": 3370,
                "detected_size": "A0",
                "pass": True,
            },
            "fonts": {
                "all_embedded": True,
                "font_count": 5,
                "pass": True,
            },
        },
        "errors": [],
        "warnings": [],
    }
