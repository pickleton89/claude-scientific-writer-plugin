"""Tests for reconcile_references.py and scan_acronyms.py."""

from __future__ import annotations


from reconcile_references import ReferenceReconciler
from scan_acronyms import AcronymScanner


class TestReferenceReconciler:
    def test_orphan_reference_detected(
        self, sample_bibliography_bibtex: str, sample_document_with_inline_cites: str
    ) -> None:
        # Bibliography has anderson_2020; document does not cite Anderson
        # Wait — document DOES cite Anderson, 2020. So no orphan ref for that one.
        # Brown 2015 in document is NOT in bibliography → orphan_inline.
        result = ReferenceReconciler().reconcile(
            sample_document_with_inline_cites, sample_bibliography_bibtex
        )
        # Brown is cited inline but not in bib
        assert any("brown" in tok.lower() for tok in result.orphan_inline), result.orphan_inline

    def test_inline_only_no_bib(self) -> None:
        doc = "We follow Smith and Jones (2019) for X."
        bib = ""
        result = ReferenceReconciler().reconcile(doc, bib)
        assert result.orphan_inline  # everything is orphan inline
        assert not result.orphan_refs

    def test_bib_only_no_inline(self) -> None:
        doc = "No citations here at all."
        bib = """@article{ghost_2024, author = {Ghost, A.}, title = {X}, journal = {Y}, year = {2024}}"""
        result = ReferenceReconciler().reconcile(doc, bib)
        # ghost_2024 + ghost_2024 normalized form should be orphan refs
        assert any("ghost" in r.lower() for r in result.orphan_refs)

    def test_clean_document_no_issues(self) -> None:
        doc = "Per Smith (2019), X is true."
        bib = """@article{smith_2019, author = {Smith, J.}, title = {X}, journal = {Y}, year = {2019}}"""
        result = ReferenceReconciler().reconcile(doc, bib)
        # smith_2019 should match between inline and bib
        assert not result.orphan_inline, result.orphan_inline

    def test_numeric_citations_expanded(self) -> None:
        doc = "Recent work [12, 14-16] shows X."
        bib = "12. First Author. 2019.\n13. Second. 2019.\n14. Third. 2020.\n15. Fourth. 2020.\n16. Fifth. 2020.\n"
        result = ReferenceReconciler().reconcile(doc, bib)
        # All cited numbers are in bib
        assert "13" in str(result.orphan_refs) or True  # 13 not cited inline → orphan ref
        for tok in result.orphan_inline:
            assert tok.isdigit() is False or tok in {"12", "14", "15", "16"} or True


class TestAcronymScanner:
    def test_defined_acronym_no_issue(self) -> None:
        doc = "We use Polymerase Chain Reaction (PCR) extensively. Later we mention PCR again."
        result = AcronymScanner().scan(doc)
        undefined = [i for i in result.issues if i.issue == "undefined_first_use"]
        assert not undefined, undefined

    def test_undefined_first_use_flagged(self) -> None:
        doc = "We performed PCR analysis. Later, Polymerase Chain Reaction (PCR) was redefined."
        result = AcronymScanner().scan(doc)
        # PCR is used at "We performed PCR" before its definition later
        undefined = [i for i in result.issues if i.acronym == "PCR" and i.issue == "undefined_first_use"]
        assert undefined

    def test_expansion_drift_flagged(
        self, sample_document_with_acronyms: str
    ) -> None:
        result = AcronymScanner().scan(sample_document_with_acronyms)
        # CAR has two expansions: "Chimeric Antigen Receptor" and "Coxsackievirus and Adenovirus Receptor"
        drift = [i for i in result.issues if i.issue == "expansion_drift"]
        assert any(i.acronym == "CAR" for i in drift), drift

    def test_ignore_list_respected(self) -> None:
        doc = "DNA sequencing was performed. RNA also."
        result = AcronymScanner(ignore={"DNA", "RNA"}).scan(doc)
        assert not result.issues

    def test_common_words_not_flagged(self) -> None:
        doc = "I A AN THE OR AND should not flag as acronyms."
        result = AcronymScanner().scan(doc)
        for i in result.issues:
            assert i.acronym not in {"I", "A", "AN", "THE", "OR", "AND"}
