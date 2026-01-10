"""
Comprehensive test suite for citation style selection.

Tests cover:
- Venue type inference from strings
- Citation style selection by venue type
- Style recommendations with confidence scores
- LaTeX command generation
- Edge cases and unknown venues
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from select_citation_style import (
    VenueType,
    CitationStyle,
    infer_venue_type,
    select_citation_style,
    get_style_recommendation,
    get_latex_commands,
    format_recommendation,
    ALTERNATIVE_STYLES,
)


class TestVenueTypeInference:
    """Test venue type inference from venue name strings."""

    # Biomedical journals
    def test_infer_nejm(self):
        """Test NEJM detection."""
        venue, conf = infer_venue_type("NEJM")
        assert venue == VenueType.BIOMEDICAL_JOURNAL
        assert conf >= 0.9

    def test_infer_new_england_journal(self):
        """Test full name NEJM detection."""
        venue, conf = infer_venue_type("New England Journal of Medicine")
        assert venue == VenueType.BIOMEDICAL_JOURNAL

    def test_infer_jama(self):
        """Test JAMA detection."""
        venue, conf = infer_venue_type("JAMA Internal Medicine")
        assert venue == VenueType.BIOMEDICAL_JOURNAL

    def test_infer_lancet(self):
        """Test Lancet detection."""
        venue, conf = infer_venue_type("The Lancet")
        assert venue == VenueType.BIOMEDICAL_JOURNAL

    def test_infer_bmj(self):
        """Test BMJ detection."""
        venue, conf = infer_venue_type("BMJ")
        assert venue == VenueType.BIOMEDICAL_JOURNAL

    def test_infer_circulation(self):
        """Test Circulation detection."""
        venue, conf = infer_venue_type("Circulation")
        assert venue == VenueType.BIOMEDICAL_JOURNAL

    # Life sciences
    def test_infer_nature(self):
        """Test Nature detection."""
        venue, conf = infer_venue_type("Nature")
        assert venue == VenueType.LIFE_SCIENCES
        assert conf >= 0.9

    def test_infer_nature_communications(self):
        """Test Nature Communications detection."""
        venue, conf = infer_venue_type("Nature Communications")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_science(self):
        """Test Science detection."""
        venue, conf = infer_venue_type("Science")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_science_advances(self):
        """Test Science Advances detection."""
        venue, conf = infer_venue_type("Science Advances")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_cell(self):
        """Test Cell detection."""
        venue, conf = infer_venue_type("Cell")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_pnas(self):
        """Test PNAS detection."""
        venue, conf = infer_venue_type("PNAS")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_plos(self):
        """Test PLOS detection."""
        venue, conf = infer_venue_type("PLOS Biology")
        assert venue == VenueType.LIFE_SCIENCES

    def test_infer_elife(self):
        """Test eLife detection."""
        venue, conf = infer_venue_type("eLife")
        assert venue == VenueType.LIFE_SCIENCES

    # IEEE venues
    def test_infer_ieee_transactions(self):
        """Test IEEE Transactions detection."""
        venue, conf = infer_venue_type("IEEE Transactions on Neural Networks")
        assert venue == VenueType.IEEE_VENUE
        assert conf >= 0.95

    def test_infer_ieee_journal(self):
        """Test IEEE Journal detection."""
        venue, conf = infer_venue_type("IEEE Journal of Biomedical Engineering")
        assert venue == VenueType.IEEE_VENUE

    def test_infer_ieee_conference(self):
        """Test IEEE Conference detection."""
        venue, conf = infer_venue_type("IEEE Conference on Computer Vision")
        assert venue == VenueType.IEEE_VENUE

    # ACM venues
    def test_infer_acm(self):
        """Test ACM detection."""
        venue, conf = infer_venue_type("ACM Computing Surveys")
        assert venue == VenueType.ACM_VENUE
        assert conf >= 0.95

    def test_infer_sigchi(self):
        """Test SIGCHI detection."""
        venue, conf = infer_venue_type("SIGCHI Conference")
        assert venue == VenueType.ACM_VENUE

    def test_infer_siggraph(self):
        """Test SIGGRAPH detection."""
        venue, conf = infer_venue_type("SIGGRAPH")
        assert venue == VenueType.ACM_VENUE

    def test_infer_communications_acm(self):
        """Test Communications of the ACM detection."""
        venue, conf = infer_venue_type("Communications of the ACM")
        assert venue == VenueType.ACM_VENUE

    # CS conferences
    def test_infer_neurips(self):
        """Test NeurIPS detection."""
        venue, conf = infer_venue_type("NeurIPS 2024")
        assert venue == VenueType.CS_CONFERENCE
        assert conf >= 0.9

    def test_infer_icml(self):
        """Test ICML detection."""
        venue, conf = infer_venue_type("ICML")
        assert venue == VenueType.CS_CONFERENCE

    def test_infer_iclr(self):
        """Test ICLR detection."""
        venue, conf = infer_venue_type("ICLR 2025")
        assert venue == VenueType.CS_CONFERENCE

    def test_infer_cvpr(self):
        """Test CVPR detection."""
        venue, conf = infer_venue_type("CVPR")
        assert venue == VenueType.CS_CONFERENCE

    def test_infer_acl(self):
        """Test ACL detection."""
        venue, conf = infer_venue_type("ACL 2024")
        assert venue == VenueType.CS_CONFERENCE

    def test_infer_aaai(self):
        """Test AAAI detection."""
        venue, conf = infer_venue_type("AAAI Conference")
        assert venue == VenueType.CS_CONFERENCE

    # NIH grants
    def test_infer_nih(self):
        """Test NIH detection."""
        venue, conf = infer_venue_type("NIH R01 Grant")
        assert venue == VenueType.NIH_GRANT
        assert conf >= 0.9

    def test_infer_r01(self):
        """Test R01 detection."""
        venue, conf = infer_venue_type("R01 Application")
        assert venue == VenueType.NIH_GRANT

    def test_infer_ninds(self):
        """Test NINDS detection."""
        venue, conf = infer_venue_type("NINDS")
        assert venue == VenueType.NIH_GRANT

    def test_infer_nci(self):
        """Test NCI detection."""
        venue, conf = infer_venue_type("NCI Grant")
        assert venue == VenueType.NIH_GRANT

    # NSF grants
    def test_infer_nsf(self):
        """Test NSF detection."""
        venue, conf = infer_venue_type("NSF CAREER Award")
        assert venue == VenueType.NSF_GRANT
        assert conf >= 0.9

    def test_infer_national_science_foundation(self):
        """Test full NSF name detection."""
        venue, conf = infer_venue_type("National Science Foundation")
        assert venue == VenueType.NSF_GRANT

    # Chemistry
    def test_infer_acs(self):
        """Test ACS detection."""
        venue, conf = infer_venue_type("ACS Nano")
        assert venue == VenueType.CHEMISTRY

    def test_infer_jacs(self):
        """Test JACS detection."""
        venue, conf = infer_venue_type("JACS")
        assert venue == VenueType.CHEMISTRY

    def test_infer_angewandte(self):
        """Test Angewandte Chemie detection."""
        venue, conf = infer_venue_type("Angewandte Chemie")
        assert venue == VenueType.CHEMISTRY

    # Physics
    def test_infer_physical_review(self):
        """Test Physical Review detection."""
        venue, conf = infer_venue_type("Physical Review Letters")
        assert venue == VenueType.PHYSICS
        assert conf >= 0.85

    def test_infer_aps(self):
        """Test APS detection."""
        venue, conf = infer_venue_type("APS Meeting")
        assert venue == VenueType.PHYSICS

    # Social sciences
    def test_infer_psychology(self):
        """Test psychology journal detection."""
        venue, conf = infer_venue_type("Journal of Experimental Psychology")
        assert venue == VenueType.SOCIAL_SCIENCES

    def test_infer_sociology(self):
        """Test sociology journal detection."""
        venue, conf = infer_venue_type("American Sociological Review")
        assert venue == VenueType.SOCIAL_SCIENCES

    def test_infer_cognitive(self):
        """Test cognitive science detection."""
        venue, conf = infer_venue_type("Cognitive Science")
        assert venue == VenueType.SOCIAL_SCIENCES

    # Humanities
    def test_infer_history(self):
        """Test history journal detection."""
        venue, conf = infer_venue_type("American Historical Review")
        assert venue == VenueType.HUMANITIES

    def test_infer_philosophy(self):
        """Test philosophy journal detection."""
        venue, conf = infer_venue_type("Journal of Philosophy")
        assert venue == VenueType.HUMANITIES

    def test_infer_literary(self):
        """Test literary journal detection."""
        venue, conf = infer_venue_type("Modern Literary Studies")
        assert venue == VenueType.HUMANITIES

    # Legal
    def test_infer_law_review(self):
        """Test law review detection."""
        venue, conf = infer_venue_type("Harvard Law Review")
        assert venue == VenueType.LEGAL
        assert conf >= 0.9

    def test_infer_legal_journal(self):
        """Test legal journal detection."""
        venue, conf = infer_venue_type("Legal Studies Journal")
        assert venue == VenueType.LEGAL

    # Thesis
    def test_infer_thesis(self):
        """Test thesis detection."""
        venue, conf = infer_venue_type("PhD Thesis")
        assert venue == VenueType.THESIS

    def test_infer_dissertation(self):
        """Test dissertation detection."""
        venue, conf = infer_venue_type("Doctoral Dissertation")
        assert venue == VenueType.THESIS

    # Unknown
    def test_infer_unknown_venue(self):
        """Test unknown venue returns UNKNOWN."""
        venue, conf = infer_venue_type("Random Obscure Journal")
        assert venue == VenueType.UNKNOWN
        assert conf == 0.0

    def test_infer_empty_string(self):
        """Test empty string returns UNKNOWN."""
        venue, conf = infer_venue_type("")
        assert venue == VenueType.UNKNOWN
        assert conf == 0.0

    def test_infer_case_insensitive(self):
        """Test inference is case-insensitive."""
        venue1, _ = infer_venue_type("NATURE")
        venue2, _ = infer_venue_type("nature")
        venue3, _ = infer_venue_type("Nature")
        assert venue1 == venue2 == venue3 == VenueType.LIFE_SCIENCES


class TestCitationStyleSelection:
    """Test citation style selection by venue type."""

    def test_style_biomedical(self):
        """Test biomedical venues get Vancouver style."""
        style = select_citation_style(VenueType.BIOMEDICAL_JOURNAL)
        assert style == CitationStyle.VANCOUVER

    def test_style_life_sciences(self):
        """Test life sciences venues get Nature style."""
        style = select_citation_style(VenueType.LIFE_SCIENCES)
        assert style == CitationStyle.NATURE

    def test_style_social_sciences(self):
        """Test social sciences venues get APA style."""
        style = select_citation_style(VenueType.SOCIAL_SCIENCES)
        assert style == CitationStyle.APA7

    def test_style_humanities(self):
        """Test humanities venues get Chicago notes style."""
        style = select_citation_style(VenueType.HUMANITIES)
        assert style == CitationStyle.CHICAGO_NOTES

    def test_style_cs_conference(self):
        """Test CS conferences get IEEE style."""
        style = select_citation_style(VenueType.CS_CONFERENCE)
        assert style == CitationStyle.IEEE

    def test_style_ieee(self):
        """Test IEEE venues get IEEE style."""
        style = select_citation_style(VenueType.IEEE_VENUE)
        assert style == CitationStyle.IEEE

    def test_style_acm(self):
        """Test ACM venues get ACM style."""
        style = select_citation_style(VenueType.ACM_VENUE)
        assert style == CitationStyle.ACM

    def test_style_thesis(self):
        """Test thesis gets APA style."""
        style = select_citation_style(VenueType.THESIS)
        assert style == CitationStyle.APA7

    def test_style_nih_grant(self):
        """Test NIH grants get Vancouver style."""
        style = select_citation_style(VenueType.NIH_GRANT)
        assert style == CitationStyle.VANCOUVER

    def test_style_nsf_grant(self):
        """Test NSF grants get APA style."""
        style = select_citation_style(VenueType.NSF_GRANT)
        assert style == CitationStyle.APA7

    def test_style_chemistry(self):
        """Test chemistry journals get ACS style."""
        style = select_citation_style(VenueType.CHEMISTRY)
        assert style == CitationStyle.ACS

    def test_style_physics(self):
        """Test physics journals get AIP style."""
        style = select_citation_style(VenueType.PHYSICS)
        assert style == CitationStyle.AIP

    def test_style_legal(self):
        """Test legal venues get Bluebook style."""
        style = select_citation_style(VenueType.LEGAL)
        assert style == CitationStyle.BLUEBOOK

    def test_style_unknown_default(self):
        """Test unknown venues default to APA."""
        style = select_citation_style(VenueType.UNKNOWN)
        assert style == CitationStyle.APA7

    def test_all_venue_types_have_style(self):
        """Test every venue type has a style mapping."""
        for venue_type in VenueType:
            style = select_citation_style(venue_type)
            assert isinstance(style, CitationStyle)


class TestStyleRecommendation:
    """Test full style recommendation functionality."""

    def test_recommendation_nature(self):
        """Test recommendation for Nature."""
        rec = get_style_recommendation("Nature")
        assert rec.venue_type == VenueType.LIFE_SCIENCES
        assert rec.style == CitationStyle.NATURE
        assert rec.confidence >= 0.9
        assert len(rec.notes) > 0

    def test_recommendation_ieee(self):
        """Test recommendation for IEEE."""
        rec = get_style_recommendation("IEEE Transactions")
        assert rec.venue_type == VenueType.IEEE_VENUE
        assert rec.style == CitationStyle.IEEE
        assert rec.confidence >= 0.95

    def test_recommendation_has_alternatives(self):
        """Test recommendation includes alternatives."""
        rec = get_style_recommendation("Nature")
        assert isinstance(rec.alternatives, list)

    def test_recommendation_unknown_low_confidence(self):
        """Test unknown venue has zero confidence."""
        rec = get_style_recommendation("Unknown Random Venue")
        assert rec.venue_type == VenueType.UNKNOWN
        assert rec.confidence == 0.0
        assert "Could not determine" in rec.notes

    def test_recommendation_dataclass_fields(self):
        """Test StyleRecommendation has all expected fields."""
        rec = get_style_recommendation("Nature")
        assert hasattr(rec, "style")
        assert hasattr(rec, "venue_type")
        assert hasattr(rec, "confidence")
        assert hasattr(rec, "alternatives")
        assert hasattr(rec, "notes")


class TestLatexCommands:
    """Test LaTeX command generation."""

    def test_latex_vancouver(self):
        """Test Vancouver LaTeX commands."""
        cmds = get_latex_commands(CitationStyle.VANCOUVER)
        assert "vancouver" in cmds["bibliographystyle"]

    def test_latex_ieee(self):
        """Test IEEE LaTeX commands."""
        cmds = get_latex_commands(CitationStyle.IEEE)
        assert "ieeetr" in cmds["bibliographystyle"]

    def test_latex_apa(self):
        """Test APA LaTeX commands."""
        cmds = get_latex_commands(CitationStyle.APA7)
        assert "apa" in cmds["bibliographystyle"]

    def test_latex_acm(self):
        """Test ACM LaTeX commands."""
        cmds = get_latex_commands(CitationStyle.ACM)
        assert "ACM-Reference-Format" in cmds["bibliographystyle"]

    def test_latex_acs(self):
        """Test ACS LaTeX commands."""
        cmds = get_latex_commands(CitationStyle.ACS)
        assert "achemso" in cmds["bibliographystyle"]

    def test_latex_has_package(self):
        """Test LaTeX commands include package info."""
        cmds = get_latex_commands(CitationStyle.APA7)
        assert "package" in cmds

    def test_latex_all_styles(self):
        """Test all citation styles have LaTeX commands."""
        for style in CitationStyle:
            cmds = get_latex_commands(style)
            assert "bibliographystyle" in cmds


class TestFormatRecommendation:
    """Test recommendation formatting."""

    def test_format_contains_venue_type(self):
        """Test formatted output contains venue type."""
        rec = get_style_recommendation("Nature")
        formatted = format_recommendation(rec)
        assert "life_sciences" in formatted

    def test_format_contains_style(self):
        """Test formatted output contains style."""
        rec = get_style_recommendation("Nature")
        formatted = format_recommendation(rec)
        assert "naturemag" in formatted

    def test_format_contains_confidence(self):
        """Test formatted output contains confidence."""
        rec = get_style_recommendation("Nature")
        formatted = format_recommendation(rec)
        assert "%" in formatted  # Confidence is formatted as percentage

    def test_format_contains_latex(self):
        """Test formatted output contains LaTeX command."""
        rec = get_style_recommendation("Nature")
        formatted = format_recommendation(rec)
        assert "bibliographystyle" in formatted

    def test_format_contains_notes(self):
        """Test formatted output contains notes."""
        rec = get_style_recommendation("Nature")
        formatted = format_recommendation(rec)
        assert "Notes:" in formatted


class TestAlternativeStyles:
    """Test alternative style recommendations."""

    def test_life_sciences_alternatives(self):
        """Test life sciences has alternatives."""
        alts = ALTERNATIVE_STYLES.get(VenueType.LIFE_SCIENCES, [])
        assert len(alts) > 0
        assert CitationStyle.VANCOUVER in alts or CitationStyle.APA7 in alts

    def test_social_sciences_alternatives(self):
        """Test social sciences has Chicago alternative."""
        alts = ALTERNATIVE_STYLES.get(VenueType.SOCIAL_SCIENCES, [])
        assert CitationStyle.CHICAGO in alts

    def test_humanities_alternatives(self):
        """Test humanities has MLA alternative."""
        alts = ALTERNATIVE_STYLES.get(VenueType.HUMANITIES, [])
        assert CitationStyle.MLA in alts

    def test_unknown_has_alternatives(self):
        """Test unknown venue has reasonable alternatives."""
        alts = ALTERNATIVE_STYLES.get(VenueType.UNKNOWN, [])
        assert len(alts) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_none_venue_name(self):
        """Test None venue name doesn't crash."""
        venue, conf = infer_venue_type(None)
        assert venue == VenueType.UNKNOWN

    def test_whitespace_venue_name(self):
        """Test whitespace-only venue name."""
        venue, conf = infer_venue_type("   ")
        assert venue == VenueType.UNKNOWN

    def test_numeric_venue_name(self):
        """Test numeric venue name."""
        venue, conf = infer_venue_type("12345")
        assert venue == VenueType.UNKNOWN

    def test_special_characters_venue_name(self):
        """Test venue name with special characters."""
        venue, conf = infer_venue_type("@#$%^&*()")
        assert venue == VenueType.UNKNOWN

    def test_partial_match(self):
        """Test partial keyword matching."""
        # 'nature' should match even in a longer string
        venue, conf = infer_venue_type("Some Nature-related journal")
        assert venue == VenueType.LIFE_SCIENCES


class TestIntegration:
    """Integration tests for the full workflow."""

    def test_full_workflow_nature(self):
        """Test complete workflow for Nature submission."""
        venue_name = "Nature Methods"
        rec = get_style_recommendation(venue_name)

        assert rec.venue_type == VenueType.LIFE_SCIENCES
        assert rec.style == CitationStyle.NATURE
        assert rec.confidence > 0.9

        latex = get_latex_commands(rec.style)
        assert "naturemag" in latex["bibliographystyle"]

    def test_full_workflow_ieee(self):
        """Test complete workflow for IEEE submission."""
        venue_name = "IEEE Transactions on Pattern Analysis"
        rec = get_style_recommendation(venue_name)

        assert rec.venue_type == VenueType.IEEE_VENUE
        assert rec.style == CitationStyle.IEEE

        latex = get_latex_commands(rec.style)
        assert "ieeetr" in latex["bibliographystyle"]

    def test_full_workflow_nih_grant(self):
        """Test complete workflow for NIH grant."""
        venue_name = "NIH R01 Application"
        rec = get_style_recommendation(venue_name)

        assert rec.venue_type == VenueType.NIH_GRANT
        assert rec.style == CitationStyle.VANCOUVER
        assert "PMCID" in rec.notes or "NIH" in rec.notes

    def test_multiple_recommendations(self):
        """Test getting recommendations for multiple venues."""
        venues = [
            "Nature",
            "IEEE Transactions",
            "JAMA",
            "ACL 2024",
            "PhD Thesis",
        ]

        for venue in venues:
            rec = get_style_recommendation(venue)
            assert isinstance(rec.style, CitationStyle)
            assert isinstance(rec.venue_type, VenueType)
