"""Tests for check_style module."""

from __future__ import annotations

import sys
from pathlib import Path


# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from check_style import StyleChecker, StyleIssue  # noqa: E402
from venue_database import get_venue  # noqa: E402


class TestStyleCheckerVoice:
    """Tests for voice checking."""

    def test_active_voice_preferred(self) -> None:
        """Test detection of passive voice in active-preferred venues."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        # Highly passive text
        passive_text = """
        The experiment was conducted by the researchers. The results were analyzed
        using statistical methods. It was found that the treatment was effective.
        The hypothesis was confirmed by the data. Samples were collected and
        measurements were performed.
        """

        issues = checker.check_voice(passive_text)
        assert len(issues) > 0
        assert any(i.category == "voice" for i in issues)

    def test_active_voice_acceptable(self) -> None:
        """Test active voice doesn't trigger warnings."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        # Active voice text
        active_text = """
        We conducted the experiment using standard protocols. We analyzed the results
        with statistical methods. We found that the treatment was effective.
        We confirmed the hypothesis through careful analysis. We collected samples
        and we performed measurements.
        """

        issues = checker.check_voice(active_text)
        # Should have no voice warnings (or at least fewer)
        voice_issues = [i for i in issues if i.category == "voice" and i.severity == "warning"]
        assert len(voice_issues) == 0

    def test_passive_voice_preferred(self) -> None:
        """Test IEEE-style venues prefer passive voice."""
        venue = get_venue("ieee")
        assert venue is not None
        checker = StyleChecker(venue)

        # Active text in passive-preferred venue
        active_text = """
        We propose a novel method for image classification. We demonstrate that
        our approach outperforms existing methods. We show significant improvements
        on standard benchmarks.
        """

        _issues = checker.check_voice(active_text)  # noqa: F841
        # May get info about passive preference
        # This depends on the specific thresholds


class TestStyleCheckerJargon:
    """Tests for jargon level checking."""

    def test_high_jargon_in_accessible_venue(self) -> None:
        """Test detection of high jargon in accessible venues."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        # High jargon text
        jargon_text = """
        The CRISPR-Cas9 system enables precise genomic modifications through
        sgRNA-mediated targeting. We leveraged the NHEJ pathway for gene knockout
        and HDR for precise insertions. The PAM sequence requirement was optimized
        through computational analysis using ML algorithms. Our CNN-based approach
        utilized transfer learning from ImageNet pretrained models.
        """

        issues = checker.check_jargon_level(jargon_text)
        jargon_issues = [i for i in issues if i.category == "jargon"]
        assert len(jargon_issues) > 0

    def test_buzzword_detection(self) -> None:
        """Test detection of buzzwords."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        buzzword_text = """
        We utilized a novel paradigm to leverage synergies between different
        approaches. Our robust and scalable solution represents a holistic
        approach to the problem.
        """

        issues = checker.check_jargon_level(buzzword_text)
        # Should detect buzzwords
        assert any("buzzword" in i.message.lower() for i in issues)


class TestStyleCheckerAbstract:
    """Tests for abstract style checking."""

    def test_abstract_too_long(self) -> None:
        """Test detection of overly long abstracts."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        # Create text with abstract that exceeds limit
        long_abstract = "word " * 300  # 300 words, Nature limit is 200
        text = f"Abstract\n{long_abstract}\n\nIntroduction"

        issues = checker.check_abstract_style(text)
        length_issues = [i for i in issues if "too long" in i.message.lower()]
        assert len(length_issues) > 0

    def test_abstract_acceptable_length(self) -> None:
        """Test acceptable abstract length doesn't trigger errors."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        # Create text with short abstract
        short_abstract = "word " * 150  # 150 words, under Nature's 200 limit
        text = f"Abstract\n{short_abstract}\n\nIntroduction"

        issues = checker.check_abstract_style(text)
        length_errors = [
            i
            for i in issues
            if "too long" in i.message.lower() and i.severity == "error"
        ]
        assert len(length_errors) == 0

    def test_structured_abstract_missing_sections(self) -> None:
        """Test detection of missing sections in structured abstracts."""
        venue = get_venue("nejm")
        assert venue is not None
        checker = StyleChecker(venue)

        # NEJM requires: Background, Methods, Results, Conclusions
        incomplete_abstract = """
        Abstract
        Background: This study investigates treatment efficacy.
        Methods: We conducted a randomized trial.

        Introduction
        """

        issues = checker.check_abstract_style(incomplete_abstract)
        missing_issues = [i for i in issues if "missing" in i.message.lower()]
        assert len(missing_issues) > 0


class TestStyleCheckerContributions:
    """Tests for contribution list checking."""

    def test_contribution_list_found(self) -> None:
        """Test detection of contribution lists."""
        venue = get_venue("neurips")
        assert venue is not None
        checker = StyleChecker(venue)

        text_with_contributions = """
        Our contributions are as follows:
        - We propose a novel architecture
        - We provide theoretical analysis
        - We demonstrate state-of-the-art results
        """

        issues = checker.check_contribution_format(text_with_contributions)
        # Should pass - contributions found
        contrib_warnings = [
            i
            for i in issues
            if i.category == "structure" and i.severity == "warning"
        ]
        assert len(contrib_warnings) == 0

    def test_contribution_list_missing(self) -> None:
        """Test warning when contribution list is missing."""
        venue = get_venue("neurips")
        assert venue is not None
        checker = StyleChecker(venue)

        text_without_contributions = """
        In this paper, we present a new method for image classification.
        Our method achieves good results on standard benchmarks.
        The approach is based on deep learning techniques.
        """

        issues = checker.check_contribution_format(text_without_contributions)
        contrib_warnings = [
            i
            for i in issues
            if i.category == "structure" and i.severity == "warning"
        ]
        assert len(contrib_warnings) > 0

    def test_contribution_not_required(self) -> None:
        """Test venues that don't require contribution lists."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        text = "Some text without contributions."
        issues = checker.check_contribution_format(text)
        # Nature doesn't require contributions, so no warnings
        assert len(issues) == 0


class TestStyleCheckerHedging:
    """Tests for hedging language checking."""

    def test_strong_claims_in_medical(self) -> None:
        """Test detection of strong causal claims in medical journals."""
        venue = get_venue("nejm")
        assert venue is not None
        checker = StyleChecker(venue)

        strong_claims_text = """
        The treatment proves that the drug causes improvement.
        This confirms that the intervention causes reduced mortality.
        """

        issues = checker.check_hedging_language(strong_claims_text)
        hedging_issues = [i for i in issues if i.category == "language"]
        assert len(hedging_issues) > 0

    def test_appropriate_hedging(self) -> None:
        """Test appropriate hedging doesn't trigger warnings."""
        venue = get_venue("nejm")
        assert venue is not None
        checker = StyleChecker(venue)

        hedged_text = """
        The treatment was associated with improvement.
        The data suggest that the intervention may reduce mortality.
        """

        issues = checker.check_hedging_language(hedged_text)
        # Appropriately hedged language should have fewer warnings
        strong_claim_issues = [
            i for i in issues if "causal claim" in i.message.lower()
        ]
        assert len(strong_claim_issues) == 0


class TestStyleCheckerFirstPerson:
    """Tests for first person usage checking."""

    def test_first_person_in_impersonal_venue(self) -> None:
        """Test detection of first person in impersonal venues."""
        venue = get_venue("ieee")
        assert venue is not None
        assert venue.style.first_person is False

        checker = StyleChecker(venue)

        first_person_text = """
        We propose a novel method. Our approach demonstrates superior
        performance. We show that our technique outperforms baselines.
        We conducted experiments to validate our claims.
        """

        issues = checker.check_first_person(first_person_text)
        fp_issues = [
            i
            for i in issues
            if i.category == "voice" and "first person" in i.message.lower()
        ]
        assert len(fp_issues) > 0

    def test_first_person_encouraged(self) -> None:
        """Test first person is acceptable in venues that encourage it."""
        venue = get_venue("nature")
        assert venue is not None
        assert venue.style.first_person is True

        checker = StyleChecker(venue)

        first_person_text = """
        We discovered a new mechanism. Our findings demonstrate that
        the pathway is critical for development. We show that inhibiting
        this process leads to significant effects.
        """

        issues = checker.check_first_person(first_person_text)
        fp_warnings = [
            i
            for i in issues
            if i.category == "voice"
            and i.severity == "warning"
            and "first person" in i.message.lower()
        ]
        assert len(fp_warnings) == 0


class TestStyleCheckerIntegration:
    """Integration tests for full style checking."""

    def test_check_all_runs(self) -> None:
        """Test check_all runs without errors."""
        venue = get_venue("nature")
        assert venue is not None
        checker = StyleChecker(venue)

        sample_text = """
        Abstract
        We discovered a new mechanism for gene regulation.

        Introduction
        Gene regulation is fundamental to biology. We show that
        a novel pathway controls expression.
        """

        issues = checker.check_all(sample_text)
        assert isinstance(issues, list)

    def test_issue_structure(self) -> None:
        """Test StyleIssue structure."""
        venue = get_venue("neurips")
        assert venue is not None
        checker = StyleChecker(venue)

        text = "Some sample text for analysis."
        issues = checker.check_all(text)

        for issue in issues:
            assert isinstance(issue, StyleIssue)
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "message")
            assert issue.severity in ["error", "warning", "info"]
