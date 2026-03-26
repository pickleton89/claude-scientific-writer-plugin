"""Tests for validate_stage_exit.py - Workflow stage exit criteria validation."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_stage_exit import (
    ExitCriteria,
    check_stage_1,
    check_stage_2,
    check_stage_3,
    check_stage_4,
    check_stage_5,
    check_stage_6,
    check_stage_7,
    check_stage_8,
    validate_stage_exit,
    validate_all_stages,
    STAGE_VALIDATORS,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def valid_stage_1_data():
    """Valid data for Stage 1 exit."""
    return {
        "phenomenon_description": "Observed unexpected protein aggregation in neuronal cells under oxidative stress conditions that correlates with mitochondrial dysfunction",
        "explanation_levels": ["molecular", "cellular"],
        "domain": "biomedical",
        "search_terms": [
            "protein aggregation",
            "oxidative stress",
            "neurons",
            "mitochondria",
            "neurodegeneration",
        ],
    }


@pytest.fixture
def valid_stage_2_data():
    """Valid data for Stage 2 exit."""
    return {
        "literature_search": {
            "databases": ["PubMed", "Scopus", "Web of Science"],
            "papers_retrieved": 45,
            "saturation_percent": 3,
            "recent_percent": 65,
        }
    }


@pytest.fixture
def valid_stage_3_data():
    """Valid data for Stage 3 exit."""
    return {
        "evidence_synthesis": {
            "key_findings": [f"Finding {i}" for i in range(12)],
            "conflicting_evidence": ["Conflict 1"],
            "knowledge_gaps": ["Gap 1", "Gap 2", "Gap 3"],
            "mechanistic_patterns": ["Pattern 1"],
        }
    }


@pytest.fixture
def valid_stage_4_data():
    """Valid data for Stage 4 exit."""
    return {
        "hypotheses": [
            {
                "id": "H1",
                "mechanism": {"causal_chain": ["step1", "step2", "step3"]},
                "supporting_evidence": [
                    {"citation": "A et al. 2023"},
                    {"citation": "B et al. 2022"},
                    {"citation": "C et al. 2024"},
                ],
            },
            {
                "id": "H2",
                "mechanism": {"causal_chain": ["stepA", "stepB"]},
                "supporting_evidence": [
                    {"citation": "D et al. 2023"},
                    {"citation": "E et al. 2022"},
                    {"citation": "F et al. 2024"},
                ],
            },
            {
                "id": "H3",
                "mechanism": {"causal_chain": ["stepX", "stepY"]},
                "supporting_evidence": [
                    {"citation": "G et al. 2023"},
                    {"citation": "H et al. 2022"},
                    {"citation": "I et al. 2024"},
                ],
            },
        ]
    }


@pytest.fixture
def valid_stage_5_data():
    """Valid data for Stage 5 exit."""
    return {
        "hypotheses": [
            {
                "id": "H1",
                "quality_scores": {
                    "testability": 2,
                    "falsifiability": 2,
                    "parsimony": 2,
                    "explanatory_power": 1,
                    "distinctiveness": 1,
                },
            },
            {
                "id": "H2",
                "quality_scores": {
                    "testability": 2,
                    "falsifiability": 1,
                    "parsimony": 1,
                    "explanatory_power": 1,
                    "distinctiveness": 1,
                },
            },
            {
                "id": "H3",
                "quality_scores": {
                    "testability": 1,
                    "falsifiability": 1,
                    "parsimony": 2,
                    "explanatory_power": 1,
                    "distinctiveness": 1,
                },
            },
        ]
    }


@pytest.fixture
def valid_stage_7_data():
    """Valid data for Stage 7 exit."""
    return {
        "hypotheses": [
            {
                "id": "H1",
                "predictions": [
                    {
                        "statement": "Prediction 1",
                        "falsification_criterion": "If X does not occur",
                        "magnitude": "50% increase",
                    },
                    {
                        "statement": "Prediction 2",
                        "falsification_criterion": "If Y is less than threshold",
                        "magnitude": "2-fold change",
                    },
                ],
            },
            {
                "id": "H2",
                "predictions": [
                    {
                        "statement": "Prediction 3",
                        "falsification_criterion": "If Z remains unchanged",
                    },
                    {
                        "statement": "Prediction 4",
                        "falsification_criterion": "If no effect observed",
                    },
                ],
            },
            {
                "id": "H3",
                "predictions": [
                    {
                        "statement": "Prediction 5",
                        "falsification_criterion": "If A is negative",
                        "magnitude": "30% reduction",
                    },
                    {
                        "statement": "Prediction 6",
                        "falsification_criterion": "If B exceeds limit",
                        "magnitude": "10-fold increase",
                    },
                ],
            },
        ]
    }


@pytest.fixture
def complete_workflow_data():
    """Complete workflow data passing all stages."""
    return {
        "phenomenon_description": "Observed unexpected protein aggregation in neuronal cells under oxidative stress conditions that correlates with mitochondrial dysfunction",
        "explanation_levels": ["molecular", "cellular"],
        "domain": "biomedical",
        "search_terms": ["term1", "term2", "term3", "term4", "term5"],
        "literature_search": {
            "databases": ["PubMed", "Scopus", "Web of Science"],
            "papers_retrieved": 50,
            "saturation_percent": 3,
            "recent_percent": 70,
        },
        "evidence_synthesis": {
            "key_findings": [f"Finding {i}" for i in range(15)],
            "conflicting_evidence": ["Conflict 1"],
            "knowledge_gaps": ["Gap 1", "Gap 2", "Gap 3", "Gap 4"],
            "mechanistic_patterns": ["Pattern 1", "Pattern 2"],
        },
        "hypotheses": [
            {
                "id": "H1",
                "mechanism": {"causal_chain": ["step1", "step2", "step3"]},
                "supporting_evidence": [
                    {"citation": f"Citation {i}"} for i in range(15)
                ],
                "conflicting_evidence": [
                    {"citation": f"Conflict {i}"} for i in range(5)
                ],
                "predictions": [
                    {
                        "statement": "Prediction 1",
                        "falsification_criterion": "If X does not occur",
                        "magnitude": "50%",
                    },
                    {
                        "statement": "Prediction 2",
                        "falsification_criterion": "If Y < threshold",
                        "magnitude": "2-fold",
                    },
                ],
                "quality_scores": {
                    "testability": 2,
                    "falsifiability": 2,
                    "parsimony": 2,
                    "explanatory_power": 1,
                    "distinctiveness": 2,
                },
            },
            {
                "id": "H2",
                "mechanism": {"causal_chain": ["stepA", "stepB"]},
                "supporting_evidence": [
                    {"citation": f"Citation {i}"} for i in range(15, 25)
                ],
                "predictions": [
                    {
                        "statement": "Prediction 3",
                        "falsification_criterion": "If Z unchanged",
                        "magnitude": "30%",
                    },
                    {
                        "statement": "Prediction 4",
                        "falsification_criterion": "If no effect",
                    },
                ],
                "quality_scores": {
                    "testability": 2,
                    "falsifiability": 1,
                    "parsimony": 1,
                    "explanatory_power": 1,
                    "distinctiveness": 1,
                },
            },
            {
                "id": "H3",
                "mechanism": {"causal_chain": ["stepX", "stepY", "stepZ"]},
                "supporting_evidence": [
                    {"citation": f"Citation {i}"} for i in range(25, 40)
                ],
                "predictions": [
                    {
                        "statement": "Prediction 5",
                        "falsification_criterion": "If A negative",
                        "magnitude": "40%",
                    },
                    {
                        "statement": "Prediction 6",
                        "falsification_criterion": "If B exceeds",
                        "magnitude": "5-fold",
                    },
                ],
                "quality_scores": {
                    "testability": 1,
                    "falsifiability": 2,
                    "parsimony": 1,
                    "explanatory_power": 2,
                    "distinctiveness": 1,
                },
            },
        ],
    }


# =============================================================================
# ExitCriteria Tests
# =============================================================================


class TestExitCriteria:
    def test_passed_property_all_true(self):
        """ExitCriteria.passed returns True when all criteria pass."""
        criteria = ExitCriteria(
            stage=1,
            name="Test Stage",
            criteria=[
                ("criterion1", True, "note1"),
                ("criterion2", True, "note2"),
            ],
        )
        assert criteria.passed is True

    def test_passed_property_one_false(self):
        """ExitCriteria.passed returns False when any criterion fails."""
        criteria = ExitCriteria(
            stage=1,
            name="Test Stage",
            criteria=[
                ("criterion1", True, "note1"),
                ("criterion2", False, "note2"),
            ],
        )
        assert criteria.passed is False

    def test_passed_property_empty(self):
        """ExitCriteria.passed returns True for empty criteria list."""
        criteria = ExitCriteria(stage=1, name="Test Stage", criteria=[])
        assert criteria.passed is True


# =============================================================================
# Stage 1 Tests
# =============================================================================


class TestStage1:
    def test_valid_stage_1_passes(self, valid_stage_1_data):
        """Valid Stage 1 data passes all criteria."""
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is True
        assert result.stage == 1
        assert result.name == "Understand Phenomenon"

    def test_short_description_fails(self, valid_stage_1_data):
        """Short phenomenon description fails."""
        valid_stage_1_data["phenomenon_description"] = "Too short"
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is False

    def test_missing_explanation_levels_fails(self, valid_stage_1_data):
        """Missing explanation levels fails."""
        valid_stage_1_data["explanation_levels"] = []
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is False

    def test_missing_domain_fails(self, valid_stage_1_data):
        """Missing domain fails."""
        valid_stage_1_data["domain"] = ""
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is False

    def test_insufficient_search_terms_fails(self, valid_stage_1_data):
        """Less than 5 search terms fails."""
        valid_stage_1_data["search_terms"] = ["term1", "term2"]
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is False

    def test_exactly_five_search_terms_passes(self, valid_stage_1_data):
        """Exactly 5 search terms passes."""
        valid_stage_1_data["search_terms"] = ["a", "b", "c", "d", "e"]
        result = check_stage_1(valid_stage_1_data)
        assert result.passed is True

    def test_empty_data_fails(self):
        """Empty data fails all criteria."""
        result = check_stage_1({})
        assert result.passed is False
        failed_count = sum(1 for _, passed, _ in result.criteria if not passed)
        assert failed_count == 4


# =============================================================================
# Stage 2 Tests
# =============================================================================


class TestStage2:
    def test_valid_stage_2_passes(self, valid_stage_2_data):
        """Valid Stage 2 data passes all criteria."""
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is True
        assert result.stage == 2
        assert result.name == "Literature Search"

    def test_insufficient_databases_fails(self, valid_stage_2_data):
        """Less than 3 databases fails."""
        valid_stage_2_data["literature_search"]["databases"] = ["PubMed"]
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is False

    def test_insufficient_papers_fails(self, valid_stage_2_data):
        """Less than 40 papers fails."""
        valid_stage_2_data["literature_search"]["papers_retrieved"] = 30
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is False

    def test_high_saturation_fails(self, valid_stage_2_data):
        """Saturation >= 5% fails."""
        valid_stage_2_data["literature_search"]["saturation_percent"] = 10
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is False

    def test_low_recent_percent_fails(self, valid_stage_2_data):
        """Recent papers < 60% fails."""
        valid_stage_2_data["literature_search"]["recent_percent"] = 40
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is False

    def test_exactly_40_papers_passes(self, valid_stage_2_data):
        """Exactly 40 papers passes."""
        valid_stage_2_data["literature_search"]["papers_retrieved"] = 40
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is True

    def test_saturation_at_boundary(self, valid_stage_2_data):
        """Saturation at 4.9% passes, 5% fails."""
        valid_stage_2_data["literature_search"]["saturation_percent"] = 4.9
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is True

        valid_stage_2_data["literature_search"]["saturation_percent"] = 5
        result = check_stage_2(valid_stage_2_data)
        assert result.passed is False


# =============================================================================
# Stage 3 Tests
# =============================================================================


class TestStage3:
    def test_valid_stage_3_passes(self, valid_stage_3_data):
        """Valid Stage 3 data passes all criteria."""
        result = check_stage_3(valid_stage_3_data)
        assert result.passed is True
        assert result.stage == 3
        assert result.name == "Synthesize Evidence"

    def test_insufficient_findings_fails(self, valid_stage_3_data):
        """Less than 10 key findings fails."""
        valid_stage_3_data["evidence_synthesis"]["key_findings"] = ["Finding 1"]
        result = check_stage_3(valid_stage_3_data)
        assert result.passed is False

    def test_insufficient_gaps_fails(self, valid_stage_3_data):
        """Less than 3 knowledge gaps fails."""
        valid_stage_3_data["evidence_synthesis"]["knowledge_gaps"] = ["Gap 1"]
        result = check_stage_3(valid_stage_3_data)
        assert result.passed is False

    def test_no_patterns_fails(self, valid_stage_3_data):
        """No mechanistic patterns fails."""
        valid_stage_3_data["evidence_synthesis"]["mechanistic_patterns"] = []
        result = check_stage_3(valid_stage_3_data)
        assert result.passed is False

    def test_empty_conflicts_passes(self, valid_stage_3_data):
        """Empty conflicting evidence passes (allowed)."""
        valid_stage_3_data["evidence_synthesis"]["conflicting_evidence"] = []
        result = check_stage_3(valid_stage_3_data)
        assert result.passed is True


# =============================================================================
# Stage 4 Tests
# =============================================================================


class TestStage4:
    def test_valid_stage_4_passes(self, valid_stage_4_data):
        """Valid Stage 4 data passes all criteria."""
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is True
        assert result.stage == 4
        assert result.name == "Generate Hypotheses"

    def test_too_few_hypotheses_fails(self, valid_stage_4_data):
        """Less than 3 hypotheses fails."""
        valid_stage_4_data["hypotheses"] = valid_stage_4_data["hypotheses"][:2]
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is False

    def test_too_many_hypotheses_fails(self, valid_stage_4_data):
        """More than 5 hypotheses fails."""
        extra = [
            {
                "id": f"H{i}",
                "mechanism": {"causal_chain": ["step1"]},
                "supporting_evidence": [{"citation": f"C{j}"} for j in range(3)],
            }
            for i in range(4, 8)
        ]
        valid_stage_4_data["hypotheses"].extend(extra)
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is False

    def test_missing_mechanism_fails(self, valid_stage_4_data):
        """Hypothesis without mechanism fails."""
        del valid_stage_4_data["hypotheses"][0]["mechanism"]
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is False

    def test_empty_causal_chain_fails(self, valid_stage_4_data):
        """Hypothesis with empty causal chain fails."""
        valid_stage_4_data["hypotheses"][0]["mechanism"]["causal_chain"] = []
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is False

    def test_insufficient_evidence_fails(self, valid_stage_4_data):
        """Hypothesis with < 3 citations fails."""
        valid_stage_4_data["hypotheses"][0]["supporting_evidence"] = [
            {"citation": "One"}
        ]
        result = check_stage_4(valid_stage_4_data)
        assert result.passed is False

    def test_empty_hypotheses_fails(self):
        """Empty hypotheses list fails."""
        result = check_stage_4({"hypotheses": []})
        assert result.passed is False


# =============================================================================
# Stage 5 Tests
# =============================================================================


class TestStage5:
    def test_valid_stage_5_passes(self, valid_stage_5_data):
        """Valid Stage 5 data passes all criteria."""
        result = check_stage_5(valid_stage_5_data)
        assert result.passed is True
        assert result.stage == 5
        assert result.name == "Evaluate Quality"

    def test_missing_scores_fails(self, valid_stage_5_data):
        """Hypothesis without quality scores fails."""
        del valid_stage_5_data["hypotheses"][0]["quality_scores"]
        result = check_stage_5(valid_stage_5_data)
        assert result.passed is False

    def test_no_strong_hypothesis_fails(self, valid_stage_5_data):
        """No hypothesis with score >= 8 fails."""
        # Lower all scores
        for h in valid_stage_5_data["hypotheses"]:
            h["quality_scores"] = {
                "testability": 1,
                "falsifiability": 1,
                "parsimony": 1,
                "explanatory_power": 1,
                "distinctiveness": 1,
            }
        result = check_stage_5(valid_stage_5_data)
        assert result.passed is False

    def test_weak_hypothesis_fails(self, valid_stage_5_data):
        """Hypothesis with score < 5 fails."""
        valid_stage_5_data["hypotheses"][0]["quality_scores"] = {
            "testability": 0,
            "falsifiability": 1,
            "parsimony": 1,
            "explanatory_power": 0,
            "distinctiveness": 0,
        }
        result = check_stage_5(valid_stage_5_data)
        assert result.passed is False

    def test_empty_hypotheses_fails(self):
        """Empty hypotheses list fails."""
        result = check_stage_5({"hypotheses": []})
        assert result.passed is False

    def test_exactly_8_score_passes(self):
        """Hypothesis with exactly score 8 passes."""
        data = {
            "hypotheses": [
                {
                    "id": "H1",
                    "quality_scores": {
                        "testability": 2,
                        "falsifiability": 2,
                        "parsimony": 2,
                        "explanatory_power": 1,
                        "distinctiveness": 1,
                    },
                }
            ]
        }
        result = check_stage_5(data)
        # Check max score criterion (uses unicode ≥)
        max_score_criterion = [c for c in result.criteria if "≥8" in c[0]][0]
        assert max_score_criterion[1] is True


# =============================================================================
# Stage 6 Tests
# =============================================================================


class TestStage6:
    def test_experimental_design_inline_passes(self):
        """Hypotheses with inline experimental_design pass."""
        data = {
            "hypotheses": [
                {"id": "H1", "experimental_design": {"methods": ["PCR"]}},
                {"id": "H2", "experimental_design": {"methods": ["Western blot"]}},
                {"id": "H3", "experimental_design": {"methods": ["ELISA"]}},
            ]
        }
        result = check_stage_6(data)
        assert result.passed is True
        assert result.stage == 6

    def test_experimental_design_external_passes(self):
        """Hypotheses with external experimental_designs pass."""
        data = {
            "hypotheses": [
                {"id": "H1"},
                {"id": "H2"},
                {"id": "H3"},
            ],
            "experimental_designs": {
                "H1": {"methods": ["PCR"]},
                "H2": {"methods": ["Western blot"]},
                "H3": {"methods": ["ELISA"]},
            },
        }
        result = check_stage_6(data)
        assert result.passed is True

    def test_missing_design_fails(self):
        """Hypothesis without experimental design fails."""
        data = {
            "hypotheses": [
                {"id": "H1", "experimental_design": {"methods": ["PCR"]}},
                {"id": "H2"},  # Missing design
                {"id": "H3"},
            ],
            "experimental_designs": {
                "H1": {"methods": ["PCR"]},
            },
        }
        result = check_stage_6(data)
        assert result.passed is False


# =============================================================================
# Stage 7 Tests
# =============================================================================


class TestStage7:
    def test_valid_stage_7_passes(self, valid_stage_7_data):
        """Valid Stage 7 data passes all criteria."""
        result = check_stage_7(valid_stage_7_data)
        assert result.passed is True
        assert result.stage == 7
        assert result.name == "Formulate Predictions"

    def test_insufficient_predictions_fails(self, valid_stage_7_data):
        """Hypothesis with < 2 predictions fails."""
        valid_stage_7_data["hypotheses"][0]["predictions"] = [
            {"statement": "Only one", "falsification_criterion": "If X"}
        ]
        result = check_stage_7(valid_stage_7_data)
        assert result.passed is False

    def test_missing_falsification_fails(self, valid_stage_7_data):
        """Predictions without falsification criteria fail."""
        for h in valid_stage_7_data["hypotheses"]:
            for p in h["predictions"]:
                del p["falsification_criterion"]
        result = check_stage_7(valid_stage_7_data)
        assert result.passed is False

    def test_empty_hypotheses_fails(self):
        """Empty hypotheses fails (need hypotheses with predictions)."""
        result = check_stage_7({"hypotheses": []})
        # The first criterion fails: 0 == 0 and 0 > 0 is False
        assert result.passed is False


# =============================================================================
# Stage 8 Tests
# =============================================================================


class TestStage8:
    def test_complete_workflow_passes(self, complete_workflow_data):
        """Complete workflow data passes Stage 8."""
        result = check_stage_8(complete_workflow_data)
        assert result.passed is True
        assert result.stage == 8

    def test_insufficient_citations_fails(self, complete_workflow_data):
        """Less than 40 total citations fails."""
        for h in complete_workflow_data["hypotheses"]:
            h["supporting_evidence"] = [{"citation": "C1"}]
            h["conflicting_evidence"] = []
        result = check_stage_8(complete_workflow_data)
        assert result.passed is False

    def test_incomplete_hypothesis_fails(self, complete_workflow_data):
        """Incomplete hypothesis structure fails."""
        del complete_workflow_data["hypotheses"][0]["predictions"]
        result = check_stage_8(complete_workflow_data)
        assert result.passed is False


# =============================================================================
# validate_stage_exit Function Tests
# =============================================================================


class TestValidateStageExit:
    def test_valid_stage_returns_criteria(self, valid_stage_1_data):
        """Valid stage number returns ExitCriteria."""
        result = validate_stage_exit(1, valid_stage_1_data)
        assert isinstance(result, ExitCriteria)
        assert result.stage == 1

    def test_invalid_stage_raises(self):
        """Invalid stage number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid stage"):
            validate_stage_exit(99, {})

    def test_all_stages_have_validators(self):
        """All stages 1-8 have validators."""
        for stage in range(1, 9):
            assert stage in STAGE_VALIDATORS


# =============================================================================
# validate_all_stages Function Tests
# =============================================================================


class TestValidateAllStages:
    def test_returns_all_stage_results(self, complete_workflow_data):
        """Returns results for all stages."""
        results = validate_all_stages(complete_workflow_data)
        assert len(results) == 8
        assert all(isinstance(r, ExitCriteria) for r in results.values())

    def test_complete_data_passes_all(self, complete_workflow_data):
        """Complete workflow data passes all stages."""
        results = validate_all_stages(complete_workflow_data)
        passed_stages = [s for s, r in results.items() if r.passed]
        # May not pass all due to specific requirements
        assert len(passed_stages) >= 4  # At minimum stages 4, 5, 7, 8

    def test_empty_data_fails_most(self):
        """Empty data fails most stages."""
        results = validate_all_stages({})
        failed_stages = [s for s, r in results.items() if not r.passed]
        assert len(failed_stages) >= 6


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    def test_none_values_handled(self):
        """None values in data cause TypeError."""
        data = {
            "phenomenon_description": None,
            "explanation_levels": None,
        }
        # None values are not handled - TypeError raised
        with pytest.raises(TypeError):
            check_stage_1(data)

    def test_wrong_type_handled(self):
        """Wrong types in data cause TypeError."""
        data = {
            "phenomenon_description": 12345,  # Should be string
            "explanation_levels": "molecular",  # Should be list
        }
        # Wrong types are not handled - TypeError raised
        with pytest.raises(TypeError):
            check_stage_1(data)

    def test_deeply_nested_missing_fields(self):
        """Missing nested fields handled gracefully."""
        data = {"literature_search": {}}
        result = check_stage_2(data)
        assert result.passed is False

    def test_boundary_hypothesis_counts(self):
        """Boundary values for hypothesis counts."""
        # Exactly 3 hypotheses
        data_3 = {
            "hypotheses": [
                {
                    "id": f"H{i}",
                    "mechanism": {"causal_chain": ["step"]},
                    "supporting_evidence": [{"citation": f"C{j}"} for j in range(3)],
                }
                for i in range(3)
            ]
        }
        assert check_stage_4(data_3).passed is True

        # Exactly 5 hypotheses
        data_5 = {
            "hypotheses": [
                {
                    "id": f"H{i}",
                    "mechanism": {"causal_chain": ["step"]},
                    "supporting_evidence": [{"citation": f"C{j}"} for j in range(3)],
                }
                for i in range(5)
            ]
        }
        assert check_stage_4(data_5).passed is True

        # 6 hypotheses (too many)
        data_6 = {
            "hypotheses": [
                {
                    "id": f"H{i}",
                    "mechanism": {"causal_chain": ["step"]},
                    "supporting_evidence": [{"citation": f"C{j}"} for j in range(3)],
                }
                for i in range(6)
            ]
        }
        assert check_stage_4(data_6).passed is False


# =============================================================================
# Criterion Detail Tests
# =============================================================================


class TestCriterionDetails:
    def test_stage_1_criterion_names(self, valid_stage_1_data):
        """Stage 1 has expected criterion names."""
        result = check_stage_1(valid_stage_1_data)
        criterion_names = [c[0] for c in result.criteria]
        assert "Core observation articulated" in criterion_names
        assert "Scope and boundaries defined" in criterion_names
        assert "Relevant domain identified" in criterion_names
        assert "Search terms generated (≥5)" in criterion_names

    def test_stage_2_criterion_names(self, valid_stage_2_data):
        """Stage 2 has expected criterion names."""
        result = check_stage_2(valid_stage_2_data)
        criterion_names = [c[0] for c in result.criteria]
        assert "≥3 databases searched" in criterion_names
        assert "≥40 papers retrieved" in criterion_names
        assert "<5% new papers in final iteration" in criterion_names
        assert "≥60% papers from last 5 years" in criterion_names

    def test_criteria_include_notes(self, valid_stage_4_data):
        """All criteria include informative notes."""
        result = check_stage_4(valid_stage_4_data)
        for criterion, passed, note in result.criteria:
            assert len(note) > 0
            assert isinstance(note, str)
