"""Tests for latex_preflight.py - LaTeX document pre-flight validation."""

import pytest
import sys
from pathlib import Path
import tempfile

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from latex_preflight import (
    PreflightReport,
    count_hypothesis_boxes,
    check_environment,
    check_section,
    check_balanced_environments,
    check_citations,
    check_page_breaks_before_boxes,
    check_figure_references,
    check_table_references,
    check_latex_structure,
    check_latex_file,
    REQUIRED_ENVIRONMENTS,
    REQUIRED_SECTIONS,
    REQUIRED_APPENDICES,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def valid_latex_content():
    """Complete valid LaTeX document content."""
    return r"""
\documentclass{article}

\begin{document}

\section*{Executive Summary}
This is the executive summary.

\begin{summarybox}
Summary content here.
\end{summarybox}

\section{Competing Hypotheses}

\newpage
\begin{hypothesisbox1}
Hypothesis 1 content.
\end{hypothesisbox1}

\newpage
\begin{hypothesisbox2}
Hypothesis 2 content.
\end{hypothesisbox2}

\newpage
\begin{hypothesisbox3}
Hypothesis 3 content.
\end{hypothesisbox3}

\section{Testable Predictions}

\begin{predictionbox}
Prediction content.
\end{predictionbox}

\section{Critical Comparisons}

\begin{comparisonbox}
Comparison content.
\end{comparisonbox}

\cite{Author2023}
\citep{Smith2024}
\citet{Jones2022}
\cite{Brown2023}
\cite{Wilson2024}
\cite{Lee2023}
\cite{Kim2022}
\cite{Chen2024}
\cite{Wang2023}
\cite{Zhang2022}

\section*{Appendix A}
Appendix A content.

\section*{Appendix B}
Appendix B content.

\section*{Appendix C}
Appendix C content.

\bibliography{references}

\end{document}
"""


@pytest.fixture
def minimal_valid_latex():
    """Minimal valid LaTeX with 3 hypothesis boxes."""
    return r"""
\documentclass{article}
\begin{document}

\section{Executive Summary}
Summary.
\begin{summarybox}
Content.
\end{summarybox}

\section{Competing Hypotheses}
\begin{hypothesisbox1}
H1.
\end{hypothesisbox1}
\begin{hypothesisbox2}
H2.
\end{hypothesisbox2}
\begin{hypothesisbox3}
H3.
\end{hypothesisbox3}

\section{Testable Predictions}
\begin{predictionbox}
P.
\end{predictionbox}

\section{Critical Comparisons}
\begin{comparisonbox}
C.
\end{comparisonbox}

\bibliography{refs}
\end{document}
"""


@pytest.fixture
def latex_with_all_hypothesis_variants():
    """LaTeX with all 5 hypothesis box variants."""
    return r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
\begin{summarybox}
S.
\end{summarybox}
\section{Competing Hypotheses}
\begin{hypothesisbox1}H1.\end{hypothesisbox1}
\begin{hypothesisbox2}H2.\end{hypothesisbox2}
\begin{hypothesisbox3}H3.\end{hypothesisbox3}
\begin{hypothesisbox4}H4.\end{hypothesisbox4}
\begin{hypothesisbox5}H5.\end{hypothesisbox5}
\section{Testable Predictions}
\begin{predictionbox}P.\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C.\end{comparisonbox}
\bibliography{refs}
\end{document}
"""


# =============================================================================
# PreflightReport Tests
# =============================================================================


class TestPreflightReport:
    def test_default_values(self):
        """PreflightReport has correct default values."""
        report = PreflightReport()
        assert report.environments == {}
        assert report.sections == {}
        assert report.appendices == {}
        assert report.citations == {}
        assert report.warnings == []
        assert report.errors == []
        assert report.overall_valid is True


# =============================================================================
# count_hypothesis_boxes Tests
# =============================================================================


class TestCountHypothesisBoxes:
    def test_counts_numbered_variants(self):
        """Counts all numbered hypothesis box variants."""
        content = r"""
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox2}H2\end{hypothesisbox2}
\begin{hypothesisbox3}H3\end{hypothesisbox3}
"""
        assert count_hypothesis_boxes(content) == 3

    def test_counts_generic_hypothesisbox(self):
        """Counts generic hypothesisbox environment."""
        content = r"""
\begin{hypothesisbox}H\end{hypothesisbox}
\begin{hypothesisbox}H\end{hypothesisbox}
"""
        assert count_hypothesis_boxes(content) == 2

    def test_counts_mixed_variants(self):
        """Counts mixed numbered and generic boxes."""
        content = r"""
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox}H\end{hypothesisbox}
\begin{hypothesisbox3}H3\end{hypothesisbox3}
"""
        assert count_hypothesis_boxes(content) == 3

    def test_no_boxes_returns_zero(self):
        """Returns 0 when no hypothesis boxes found."""
        content = r"\begin{document}No boxes here\end{document}"
        assert count_hypothesis_boxes(content) == 0

    def test_all_five_variants(self, latex_with_all_hypothesis_variants):
        """Counts all 5 numbered variants."""
        assert count_hypothesis_boxes(latex_with_all_hypothesis_variants) == 5


# =============================================================================
# check_environment Tests
# =============================================================================


class TestCheckEnvironment:
    def test_counts_existing_environment(self):
        """Counts occurrences of existing environment."""
        content = r"""
\begin{summarybox}S1\end{summarybox}
\begin{summarybox}S2\end{summarybox}
"""
        assert check_environment(content, "summarybox") == 2

    def test_missing_environment_returns_zero(self):
        """Returns 0 for missing environment."""
        content = r"\begin{document}No summarybox\end{document}"
        assert check_environment(content, "summarybox") == 0


# =============================================================================
# check_section Tests
# =============================================================================


class TestCheckSection:
    def test_finds_starred_section(self):
        """Finds starred section variant."""
        content = r"\section*{Executive Summary}"
        pattern = r"\\section\*?\{.*Executive Summary.*\}"
        assert check_section(content, pattern) is True

    def test_finds_unstarred_section(self):
        """Finds unstarred section variant."""
        content = r"\section{Executive Summary}"
        pattern = r"\\section\*?\{.*Executive Summary.*\}"
        assert check_section(content, pattern) is True

    def test_missing_section_returns_false(self):
        """Returns False for missing section."""
        content = r"\section{Introduction}"
        pattern = r"\\section\*?\{.*Executive Summary.*\}"
        assert check_section(content, pattern) is False

    def test_case_insensitive_match(self):
        """Matches sections case-insensitively."""
        content = r"\section{EXECUTIVE SUMMARY}"
        pattern = r"\\section\*?\{.*Executive Summary.*\}"
        assert check_section(content, pattern) is True


# =============================================================================
# check_balanced_environments Tests
# =============================================================================


class TestCheckBalancedEnvironments:
    def test_balanced_environment(self):
        """Balanced environment returns True."""
        content = r"""
\begin{summarybox}
Content
\end{summarybox}
"""
        is_balanced, msg = check_balanced_environments(content, "summarybox")
        assert is_balanced is True
        assert "balanced" in msg

    def test_unbalanced_more_begins(self):
        """More begins than ends returns False."""
        content = r"""
\begin{summarybox}
Content
\begin{summarybox}
More
\end{summarybox}
"""
        is_balanced, msg = check_balanced_environments(content, "summarybox")
        assert is_balanced is False
        assert "Unbalanced" in msg

    def test_unbalanced_more_ends(self):
        """More ends than begins returns False."""
        content = r"""
\begin{summarybox}
Content
\end{summarybox}
\end{summarybox}
"""
        is_balanced, msg = check_balanced_environments(content, "summarybox")
        assert is_balanced is False
        assert "Unbalanced" in msg

    def test_no_environment_is_balanced(self):
        """No occurrences is considered balanced."""
        content = r"\begin{document}Content\end{document}"
        is_balanced, msg = check_balanced_environments(content, "summarybox")
        assert is_balanced is True


# =============================================================================
# check_citations Tests
# =============================================================================


class TestCheckCitations:
    def test_counts_cite_commands(self):
        """Counts various cite commands."""
        content = r"""
\cite{Author2023}
\citep{Smith2024}
\citet{Jones2022}
\citeauthor{Brown2023}
"""
        count, has_bib = check_citations(content)
        assert count == 4

    def test_detects_bibliography_command(self):
        """Detects \bibliography command."""
        content = r"\bibliography{references}"
        count, has_bib = check_citations(content)
        assert has_bib is True

    def test_detects_thebibliography_environment(self):
        """Detects thebibliography environment."""
        content = r"\begin{thebibliography}{9}\end{thebibliography}"
        count, has_bib = check_citations(content)
        assert has_bib is True

    def test_detects_biblatex_commands(self):
        """Detects biblatex commands."""
        content = r"""
\addbibresource{refs.bib}
\printbibliography
"""
        count, has_bib = check_citations(content)
        assert has_bib is True

    def test_no_bibliography_returns_false(self):
        """Returns False when no bibliography found."""
        content = r"\cite{Author2023}"
        count, has_bib = check_citations(content)
        assert has_bib is False

    def test_counts_multiple_citations_in_one_command(self):
        """Counts cite command once even with multiple keys."""
        content = r"\cite{Author2023,Smith2024,Jones2022}"
        count, has_bib = check_citations(content)
        assert count == 1  # One cite command


# =============================================================================
# check_page_breaks_before_boxes Tests
# =============================================================================


class TestCheckPageBreaksBeforeBoxes:
    def test_all_boxes_with_pagebreaks(self, valid_latex_content):
        """Returns 0 when all boxes have preceding pagebreaks."""
        missing = check_page_breaks_before_boxes(valid_latex_content)
        assert missing == 0

    def test_boxes_without_pagebreaks(self):
        """Counts boxes without preceding pagebreaks."""
        content = r"""
\begin{hypothesisbox1}
H1
\end{hypothesisbox1}
\begin{hypothesisbox2}
H2
\end{hypothesisbox2}
"""
        missing = check_page_breaks_before_boxes(content)
        assert missing == 2

    def test_detects_clearpage(self):
        """Detects \clearpage as valid page break."""
        content = r"""
\clearpage
\begin{hypothesisbox1}
H1
\end{hypothesisbox1}
"""
        missing = check_page_breaks_before_boxes(content)
        assert missing == 0

    def test_detects_cleardoublepage(self):
        """Detects \cleardoublepage as valid page break."""
        content = r"""
\cleardoublepage
\begin{hypothesisbox1}
H1
\end{hypothesisbox1}
"""
        missing = check_page_breaks_before_boxes(content)
        assert missing == 0


# =============================================================================
# check_figure_references Tests
# =============================================================================


class TestCheckFigureReferences:
    def test_no_warnings_for_referenced_figures(self):
        """No warnings when all figures are referenced."""
        content = r"""
\begin{figure}
\label{fig:test}
\end{figure}
See Figure \ref{fig:test}.
"""
        warnings = check_figure_references(content)
        assert len(warnings) == 0

    def test_warns_unreferenced_figure(self):
        """Warns about unreferenced figures."""
        content = r"""
\begin{figure}
\label{fig:test}
\end{figure}
No reference here.
"""
        warnings = check_figure_references(content)
        assert len(warnings) == 1
        assert "Unreferenced" in warnings[0]

    def test_warns_missing_label(self):
        """Warns about missing figure labels."""
        content = r"See Figure \ref{fig:missing}."
        warnings = check_figure_references(content)
        assert len(warnings) == 1
        assert "Missing" in warnings[0]


# =============================================================================
# check_table_references Tests
# =============================================================================


class TestCheckTableReferences:
    def test_no_warnings_for_referenced_tables(self):
        """No warnings when all tables are referenced."""
        content = r"""
\begin{table}
\label{tab:test}
\end{table}
See Table \ref{tab:test}.
"""
        warnings = check_table_references(content)
        assert len(warnings) == 0

    def test_warns_unreferenced_table(self):
        """Warns about unreferenced tables."""
        content = r"""
\begin{table}
\label{tab:test}
\end{table}
No reference here.
"""
        warnings = check_table_references(content)
        assert len(warnings) == 1
        assert "Unreferenced" in warnings[0]


# =============================================================================
# check_latex_structure Tests
# =============================================================================


class TestCheckLatexStructure:
    def test_valid_document_passes(self, valid_latex_content):
        """Valid LaTeX document passes all checks."""
        report = check_latex_structure(valid_latex_content)
        assert report.overall_valid is True
        assert len(report.errors) == 0

    def test_minimal_valid_passes(self, minimal_valid_latex):
        """Minimal valid document passes."""
        report = check_latex_structure(minimal_valid_latex)
        assert report.overall_valid is True

    def test_missing_documentclass_fails(self, valid_latex_content):
        """Missing documentclass fails."""
        content = valid_latex_content.replace(r"\documentclass{article}", "")
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("documentclass" in e.lower() for e in report.errors)

    def test_missing_begin_document_fails(self, valid_latex_content):
        """Missing begin document fails."""
        content = valid_latex_content.replace(r"\begin{document}", "")
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("begin{document}" in e for e in report.errors)

    def test_missing_end_document_fails(self, valid_latex_content):
        """Missing end document fails."""
        content = valid_latex_content.replace(r"\end{document}", "")
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("end{document}" in e for e in report.errors)

    def test_missing_hypothesis_boxes_fails(self):
        """Missing hypothesis boxes fails."""
        content = r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
\begin{summarybox}S\end{summarybox}
\section{Competing Hypotheses}
No boxes!
\section{Testable Predictions}
\begin{predictionbox}P\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C\end{comparisonbox}
\bibliography{refs}
\end{document}
"""
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("hypothesis" in e.lower() for e in report.errors)

    def test_too_few_hypothesis_boxes_fails(self):
        """Less than 3 hypothesis boxes fails."""
        content = r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
\begin{summarybox}S\end{summarybox}
\section{Competing Hypotheses}
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox2}H2\end{hypothesisbox2}
\section{Testable Predictions}
\begin{predictionbox}P\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C\end{comparisonbox}
\bibliography{refs}
\end{document}
"""
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("2" in e and "hypothesis" in e.lower() for e in report.errors)

    def test_missing_executive_summary_fails(self, minimal_valid_latex):
        """Missing Executive Summary section fails."""
        content = minimal_valid_latex.replace(
            r"\section{Executive Summary}", r"\section{Introduction}"
        )
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("Executive Summary" in e for e in report.errors)

    def test_missing_bibliography_fails(self, minimal_valid_latex):
        """Missing bibliography fails."""
        content = minimal_valid_latex.replace(r"\bibliography{refs}", "")
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("bibliography" in e.lower() for e in report.errors)

    def test_missing_summarybox_fails(self, minimal_valid_latex):
        """Missing summarybox environment fails."""
        content = minimal_valid_latex.replace(
            r"\begin{summarybox}" + "\nContent.\n" + r"\end{summarybox}",
            "Just text.",
        )
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("summarybox" in e for e in report.errors)

    def test_missing_predictionbox_fails(self, minimal_valid_latex):
        """Missing predictionbox environment fails."""
        content = minimal_valid_latex.replace(
            r"\begin{predictionbox}" + "\nP.\n" + r"\end{predictionbox}",
            "Just text.",
        )
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("predictionbox" in e for e in report.errors)

    def test_missing_comparisonbox_fails(self, minimal_valid_latex):
        """Missing comparisonbox environment fails."""
        content = minimal_valid_latex.replace(
            r"\begin{comparisonbox}" + "\nC.\n" + r"\end{comparisonbox}",
            "Just text.",
        )
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("comparisonbox" in e for e in report.errors)

    def test_warns_about_low_citations(self, minimal_valid_latex):
        """Warns about low citation count."""
        report = check_latex_structure(minimal_valid_latex)
        assert any("citation" in w.lower() for w in report.warnings)

    def test_warns_about_missing_appendices(self, minimal_valid_latex):
        """Warns about missing appendices."""
        report = check_latex_structure(minimal_valid_latex)
        assert any("Appendix" in w for w in report.warnings)

    def test_warns_about_too_many_hypothesis_boxes(
        self, latex_with_all_hypothesis_variants
    ):
        """Warns when more than 5 hypothesis boxes."""
        content = latex_with_all_hypothesis_variants + r"""
\begin{hypothesisbox1}Extra\end{hypothesisbox1}
"""
        report = check_latex_structure(content)
        assert any("6" in w and "hypothesis" in w.lower() for w in report.warnings)

    def test_detects_unbalanced_environments(self):
        """Detects unbalanced environments."""
        content = r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
\begin{summarybox}
S
\begin{summarybox}
Nested!
\end{summarybox}
\section{Competing Hypotheses}
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox2}H2\end{hypothesisbox2}
\begin{hypothesisbox3}H3\end{hypothesisbox3}
\section{Testable Predictions}
\begin{predictionbox}P\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C\end{comparisonbox}
\bibliography{refs}
\end{document}
"""
        report = check_latex_structure(content)
        assert report.overall_valid is False
        assert any("Unbalanced" in e for e in report.errors)


# =============================================================================
# check_latex_file Tests
# =============================================================================


class TestCheckLatexFile:
    def test_valid_file_passes(self, valid_latex_content):
        """Valid file passes checks."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tex", delete=False
        ) as f:
            f.write(valid_latex_content)
            f.flush()
            report = check_latex_file(Path(f.name))
            assert report.overall_valid is True
            Path(f.name).unlink()

    def test_missing_file_raises(self):
        """Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            check_latex_file(Path("/nonexistent/file.tex"))

    def test_reads_utf8_content(self):
        """Reads UTF-8 encoded content correctly."""
        content = r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
Résumé with üñíçödé.
\begin{summarybox}S\end{summarybox}
\section{Competing Hypotheses}
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox2}H2\end{hypothesisbox2}
\begin{hypothesisbox3}H3\end{hypothesisbox3}
\section{Testable Predictions}
\begin{predictionbox}P\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C\end{comparisonbox}
\bibliography{refs}
\end{document}
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tex", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            f.flush()
            report = check_latex_file(Path(f.name))
            assert report.overall_valid is True
            Path(f.name).unlink()


# =============================================================================
# Required Constants Tests
# =============================================================================


class TestRequiredConstants:
    def test_required_environments_defined(self):
        """All required environments are defined."""
        assert "summarybox" in REQUIRED_ENVIRONMENTS
        assert "hypothesisbox" in REQUIRED_ENVIRONMENTS
        assert "predictionbox" in REQUIRED_ENVIRONMENTS
        assert "comparisonbox" in REQUIRED_ENVIRONMENTS

    def test_required_sections_defined(self):
        """All required sections are defined."""
        section_names = [name for _, name in REQUIRED_SECTIONS]
        assert "Executive Summary" in section_names
        assert "Competing Hypotheses" in section_names
        assert "Testable Predictions" in section_names
        assert "Critical Comparisons" in section_names

    def test_required_appendices_defined(self):
        """All required appendices are defined."""
        assert "Appendix A" in REQUIRED_APPENDICES
        assert "Appendix B" in REQUIRED_APPENDICES
        assert "Appendix C" in REQUIRED_APPENDICES


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    def test_empty_content_fails(self):
        """Empty content fails all checks."""
        report = check_latex_structure("")
        assert report.overall_valid is False
        assert len(report.errors) > 0

    def test_whitespace_only_fails(self):
        """Whitespace-only content fails."""
        report = check_latex_structure("   \n\t\n   ")
        assert report.overall_valid is False

    def test_very_long_document_handled(self, minimal_valid_latex):
        """Very long documents are handled."""
        long_content = minimal_valid_latex + ("\n% " + "x" * 1000) * 100
        report = check_latex_structure(long_content)
        assert report.overall_valid is True

    def test_special_characters_in_content(self, minimal_valid_latex):
        """Special characters don't break parsing."""
        content = minimal_valid_latex.replace(
            "Summary.",
            "Summary with $math$ and \\textbf{bold} and \\% percent.",
        )
        report = check_latex_structure(content)
        assert report.overall_valid is True

    def test_nested_environments(self):
        """Properly nested environments pass."""
        content = r"""
\documentclass{article}
\begin{document}
\section{Executive Summary}
\begin{summarybox}
\begin{itemize}
\item Item 1
\item Item 2
\end{itemize}
\end{summarybox}
\section{Competing Hypotheses}
\begin{hypothesisbox1}H1\end{hypothesisbox1}
\begin{hypothesisbox2}H2\end{hypothesisbox2}
\begin{hypothesisbox3}H3\end{hypothesisbox3}
\section{Testable Predictions}
\begin{predictionbox}P\end{predictionbox}
\section{Critical Comparisons}
\begin{comparisonbox}C\end{comparisonbox}
\bibliography{refs}
\end{document}
"""
        report = check_latex_structure(content)
        assert report.overall_valid is True


# =============================================================================
# Report Content Tests
# =============================================================================


class TestReportContent:
    def test_environments_counted(self, valid_latex_content):
        """Environment counts are recorded."""
        report = check_latex_structure(valid_latex_content)
        assert "summarybox" in report.environments
        assert "hypothesisbox" in report.environments
        assert "predictionbox" in report.environments
        assert "comparisonbox" in report.environments

    def test_sections_recorded(self, valid_latex_content):
        """Section presence is recorded."""
        report = check_latex_structure(valid_latex_content)
        assert "Executive Summary" in report.sections
        assert "Competing Hypotheses" in report.sections
        assert "Testable Predictions" in report.sections
        assert "Critical Comparisons" in report.sections

    def test_appendices_recorded(self, valid_latex_content):
        """Appendix presence is recorded."""
        report = check_latex_structure(valid_latex_content)
        assert "Appendix A" in report.appendices
        assert "Appendix B" in report.appendices
        assert "Appendix C" in report.appendices
        assert all(report.appendices.values())

    def test_citations_recorded(self, valid_latex_content):
        """Citation info is recorded."""
        report = check_latex_structure(valid_latex_content)
        assert "count" in report.citations
        assert "has_bibliography" in report.citations
        assert report.citations["count"] == 10
        assert report.citations["has_bibliography"] is True
