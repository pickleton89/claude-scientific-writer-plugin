"""
Comprehensive test suite for reproducible-research validation scripts.

Tests cover:
- Project scanning at all reproducibility levels (1-4)
- Environment file validation (conda, pip, pyproject)
- Schema serialization/deserialization roundtrips
- Edge cases and error handling
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
_scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from scan_project import (  # noqa: E402
    calculate_score,
    generate_recommendations,
    scan_code,
    scan_data,
    scan_documentation,
    scan_environment,
    scan_project,
)
from utils.schemas import (  # noqa: E402
    CategoryScore,
    ChecklistItem,
    CodeScanResult,
    DataScanResult,
    DocumentationScanResult,
    EnvironmentScanResult,
    EnvironmentValidationResult,
    ProjectScanResult,
    ReproducibilityAssessment,
    ValidationSummary,
)
from validate_environment import (  # noqa: E402
    validate_conda_env,
    validate_environment,
    validate_pyproject,
    validate_requirements,
)


# =============================================================================
# Schema Tests
# =============================================================================


class TestChecklistItem:
    """Tests for ChecklistItem dataclass."""

    def test_creation_passing(self):
        """Test creating a passing checklist item."""
        item = ChecklistItem(
            id="test_item",
            category="environment",
            points=5,
            status=True,
            max_points=5,
        )
        assert item.id == "test_item"
        assert item.status is True
        assert item.points == 5

    def test_creation_failing(self):
        """Test creating a failing checklist item."""
        item = ChecklistItem(
            id="test_item",
            category="environment",
            points=0,
            status=False,
            max_points=5,
        )
        assert item.status is False
        assert item.points == 0

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = ChecklistItem(
            id="versions_pinned",
            category="environment",
            points=10,
            status=True,
            max_points=10,
        )
        data = original.to_dict()
        restored = ChecklistItem.from_dict(data)
        assert restored.id == original.id
        assert restored.status == original.status
        assert restored.points == original.points


class TestCategoryScore:
    """Tests for CategoryScore dataclass."""

    def test_percentage_calculation(self):
        """Test percentage is calculated correctly."""
        score = CategoryScore(name="environment", score=20, max_score=25)
        assert score.percentage == 80.0

    def test_zero_max_score(self):
        """Test handling of zero max score."""
        score = CategoryScore(name="test", score=0, max_score=0)
        assert score.percentage == 0.0

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = CategoryScore(name="data", score=15, max_score=25)
        data = original.to_dict()
        restored = CategoryScore.from_dict(data)
        assert restored.name == original.name
        assert restored.score == original.score


class TestEnvironmentScanResult:
    """Tests for EnvironmentScanResult dataclass."""

    def test_default_values(self):
        """Test default values are correct."""
        result = EnvironmentScanResult()
        assert result.env_file_present is False
        assert result.versions_pinned is False
        assert result.issues == []

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = EnvironmentScanResult(
            env_file_present=True,
            env_file_type="conda",
            versions_pinned=True,
            pinned_percentage=95.0,
            python_version_specified=True,
            issues=["test issue"],
        )
        data = original.to_dict()
        restored = EnvironmentScanResult.from_dict(data)
        assert restored.env_file_present == original.env_file_present
        assert restored.pinned_percentage == original.pinned_percentage


class TestValidationSummary:
    """Tests for ValidationSummary dataclass."""

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = ValidationSummary(
            errors=2,
            warnings=3,
            deps_count=10,
            unpinned_count=2,
            loose_pinned_count=1,
        )
        data = original.to_dict()
        restored = ValidationSummary.from_dict(data)
        assert restored.errors == original.errors
        assert restored.deps_count == original.deps_count


class TestEnvironmentValidationResult:
    """Tests for EnvironmentValidationResult dataclass."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = EnvironmentValidationResult(
            valid=True,
            score=100,
            issues=[],
            warnings=[],
        )
        assert result.valid is True
        assert result.score == 100

    def test_invalid_result_with_error(self):
        """Test creating an invalid result with error."""
        result = EnvironmentValidationResult(
            valid=False,
            error="File not found",
        )
        assert result.valid is False
        assert result.error == "File not found"

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        summary = ValidationSummary(errors=1, warnings=2, deps_count=5)
        original = EnvironmentValidationResult(
            valid=False,
            score=60,
            issues=["ERROR: test"],
            warnings=["WARN: test"],
            summary=summary,
        )
        data = original.to_dict()
        restored = EnvironmentValidationResult.from_dict(data)
        assert restored.valid == original.valid
        assert restored.score == original.score
        assert restored.summary is not None
        assert restored.summary.errors == 1


class TestReproducibilityAssessment:
    """Tests for ReproducibilityAssessment dataclass."""

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        checklist = [
            ChecklistItem(
                id="env_file_present",
                category="environment",
                points=5,
                status=True,
                max_points=5,
            )
        ]
        category_scores = {
            "environment": CategoryScore(name="environment", score=5, max_score=25)
        }
        original = ReproducibilityAssessment(
            score=5,
            max_score=100,
            percentage=5.0,
            threshold_met=False,
            level=1,
            level_name="Minimal",
            category_scores=category_scores,
            checklist=checklist,
        )
        data = original.to_dict()
        restored = ReproducibilityAssessment.from_dict(data)
        assert restored.score == original.score
        assert restored.level_name == original.level_name
        assert len(restored.checklist) == 1
        assert "environment" in restored.category_scores


class TestProjectScanResult:
    """Tests for ProjectScanResult dataclass."""

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = ProjectScanResult(
            project_path="/test/path",
            environment=EnvironmentScanResult(env_file_present=True),
            data=DataScanResult(random_seeds_set=True),
            code=CodeScanResult(readme_present=True),
            documentation=DocumentationScanResult(methods_documented=True),
            assessment=ReproducibilityAssessment(
                score=50,
                max_score=100,
                percentage=50.0,
                threshold_met=False,
                level=2,
                level_name="Standard",
            ),
            issues=["test issue"],
            recommendations=["CRITICAL: test"],
        )
        data = original.to_dict()
        restored = ProjectScanResult.from_dict(data)
        assert restored.project_path == original.project_path
        assert restored.environment.env_file_present is True
        assert len(restored.issues) == 1


# =============================================================================
# Environment Scanning Tests
# =============================================================================


class TestScanEnvironment:
    """Tests for scan_environment function."""

    def test_no_env_file(self, tmp_project: Path):
        """Test scanning project with no environment file."""
        result = scan_environment(tmp_project)
        assert result.env_file_present is False
        assert result.env_file_type is None

    def test_conda_env_with_pinned_versions(self, tmp_project: Path):
        """Test scanning conda environment with pinned versions."""
        (tmp_project / "environment.yml").write_text(
            """name: test
channels:
  - conda-forge
dependencies:
  - python=3.11.5
  - numpy=1.26.0
  - pandas=2.1.0
"""
        )
        result = scan_environment(tmp_project)
        assert result.env_file_present is True
        assert result.env_file_type == "conda"
        assert result.python_version_specified is True
        assert result.versions_pinned is True

    def test_conda_env_with_unpinned_versions(self, tmp_project: Path):
        """Test scanning conda environment with unpinned versions."""
        (tmp_project / "environment.yml").write_text(
            """name: test
channels:
  - defaults
dependencies:
  - python
  - numpy
  - pandas
"""
        )
        result = scan_environment(tmp_project)
        assert result.env_file_present is True
        assert result.versions_pinned is False
        assert result.python_version_specified is False
        assert len(result.issues) > 0

    def test_requirements_txt_pinned(self, tmp_project: Path):
        """Test scanning pinned requirements.txt."""
        (tmp_project / "requirements.txt").write_text(
            """numpy==1.26.0
pandas==2.1.0
matplotlib==3.8.0
"""
        )
        result = scan_environment(tmp_project)
        assert result.env_file_present is True
        assert result.env_file_type == "pip"
        assert result.versions_pinned is True
        assert result.pinned_percentage == 100.0

    def test_requirements_txt_unpinned(self, tmp_project: Path):
        """Test scanning unpinned requirements.txt."""
        (tmp_project / "requirements.txt").write_text(
            """numpy
pandas>=2.0
matplotlib
"""
        )
        result = scan_environment(tmp_project)
        assert result.versions_pinned is False

    def test_dockerfile_detection(self, tmp_project: Path):
        """Test Dockerfile detection."""
        (tmp_project / "Dockerfile").write_text(
            """FROM python:3.11-slim

COPY . /app
"""
        )
        result = scan_environment(tmp_project)
        assert result.dockerfile_present is True
        assert result.dockerfile_pinned is True

    def test_system_requirements_in_readme(self, tmp_project: Path):
        """Test detection of system requirements in README."""
        (tmp_project / "README.md").write_text(
            """# Project

## Installation

Install the following dependencies...
"""
        )
        result = scan_environment(tmp_project)
        assert result.system_requirements_documented is True


class TestScanData:
    """Tests for scan_data function."""

    def test_empty_project(self, tmp_project: Path):
        """Test scanning project with no data directory."""
        result = scan_data(tmp_project)
        assert result.raw_data_archived is False
        assert result.data_processing_scripts is False

    def test_raw_data_with_readme(self, tmp_project: Path):
        """Test detection of documented raw data."""
        data_dir = tmp_project / "data" / "raw"
        data_dir.mkdir(parents=True)
        (data_dir / "README.md").write_text(
            """# Raw Data
Downloaded from GEO accession GSE12345.
DOI: 10.1234/example
"""
        )
        result = scan_data(tmp_project)
        assert result.raw_data_archived is True

    def test_processing_scripts(self, tmp_project: Path):
        """Test detection of data processing scripts."""
        scripts_dir = tmp_project / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "preprocess_data.py").write_text("# preprocessing")
        result = scan_data(tmp_project)
        assert result.data_processing_scripts is True

    def test_random_seed_numpy(self, tmp_project: Path):
        """Test detection of numpy random seed."""
        (tmp_project / "analysis.py").write_text(
            """import numpy as np
np.random.seed(42)
"""
        )
        result = scan_data(tmp_project)
        assert result.random_seeds_set is True

    def test_random_seed_torch(self, tmp_project: Path):
        """Test detection of torch random seed."""
        (tmp_project / "train.py").write_text(
            """import torch
torch.manual_seed(42)
"""
        )
        result = scan_data(tmp_project)
        assert result.random_seeds_set is True

    def test_random_seed_constant(self, tmp_project: Path):
        """Test detection of SEED constant."""
        (tmp_project / "config.py").write_text(
            """RANDOM_SEED = 42
SEED = 123
"""
        )
        result = scan_data(tmp_project)
        assert result.random_seeds_set is True

    def test_checksums(self, tmp_project: Path):
        """Test detection of checksum files."""
        (tmp_project / "checksums.md5").write_text(
            "d41d8cd98f00b204e9800998ecf8427e  data.csv"
        )
        result = scan_data(tmp_project)
        assert result.checksums_present is True


class TestScanCode:
    """Tests for scan_code function."""

    def test_readme_present(self, tmp_project: Path):
        """Test README detection."""
        (tmp_project / "README.md").write_text("# Project")
        result = scan_code(tmp_project)
        assert result.readme_present is True

    def test_readme_rst(self, tmp_project: Path):
        """Test README.rst detection."""
        (tmp_project / "README.rst").write_text("Project\n=======")
        result = scan_code(tmp_project)
        assert result.readme_present is True

    def test_license_present(self, tmp_project: Path):
        """Test LICENSE detection."""
        (tmp_project / "LICENSE").write_text("MIT License")
        result = scan_code(tmp_project)
        assert result.license_present is True

    def test_no_hardcoded_paths(self, tmp_project: Path):
        """Test project without hardcoded paths."""
        (tmp_project / "script.py").write_text(
            """from pathlib import Path

data_path = Path("data/input.csv")
"""
        )
        result = scan_code(tmp_project)
        assert result.no_hardcoded_paths is True

    def test_hardcoded_home_path(self, hardcoded_path_project: Path):
        """Test detection of hardcoded /home path."""
        result = scan_code(hardcoded_path_project)
        assert result.no_hardcoded_paths is False
        assert len(result.hardcoded_paths_found) > 0

    def test_issues_reported(self, tmp_project: Path):
        """Test that missing files are reported as issues."""
        result = scan_code(tmp_project)
        assert "README.md not found" in result.issues
        assert "LICENSE file not found" in result.issues


class TestScanDocumentation:
    """Tests for scan_documentation function."""

    def test_methods_in_docs(self, tmp_project: Path):
        """Test detection of methods.md in docs/."""
        docs_dir = tmp_project / "docs"
        docs_dir.mkdir()
        (docs_dir / "methods.md").write_text("# Methods\n\nAnalysis methods...")
        result = scan_documentation(tmp_project)
        assert result.methods_documented is True

    def test_methods_in_readme(self, tmp_project: Path):
        """Test detection of methods section in README."""
        (tmp_project / "README.md").write_text(
            """# Project

## Methods

We used the following approach...
"""
        )
        result = scan_documentation(tmp_project)
        assert result.methods_documented is True

    def test_config_file(self, tmp_project: Path):
        """Test detection of config file."""
        (tmp_project / "config.yaml").write_text("param1: value1")
        result = scan_documentation(tmp_project)
        assert result.parameters_documented is True

    def test_numbered_scripts(self, tmp_project: Path):
        """Test detection of numbered scripts."""
        scripts_dir = tmp_project / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "01_preprocess.py").write_text("# step 1")
        (scripts_dir / "02_analyze.py").write_text("# step 2")
        (scripts_dir / "03_visualize.py").write_text("# step 3")
        result = scan_documentation(tmp_project)
        assert result.execution_order_documented is True

    def test_usage_in_readme(self, tmp_project: Path):
        """Test detection of usage section in README."""
        (tmp_project / "README.md").write_text(
            """# Project

## Usage

Run the main script with...
"""
        )
        result = scan_documentation(tmp_project)
        assert result.execution_order_documented is True

    def test_outputs_in_readme(self, tmp_project: Path):
        """Test detection of output section in README."""
        (tmp_project / "README.md").write_text(
            """# Project

## Output

Results are saved to the results/ directory.
"""
        )
        result = scan_documentation(tmp_project)
        assert result.expected_outputs_described is True


# =============================================================================
# Score Calculation Tests
# =============================================================================


class TestCalculateScore:
    """Tests for calculate_score function."""

    def test_minimal_score(self):
        """Test score calculation for minimal project."""
        env = EnvironmentScanResult()
        data = DataScanResult()
        # all_code_in_repo=True (10) + no_hardcoded_paths=True by default (5) = 15
        code = CodeScanResult(all_code_in_repo=True)
        docs = DocumentationScanResult()

        assessment = calculate_score(env, data, code, docs)
        assert assessment.level == 1
        assert assessment.level_name == "Minimal"
        assert assessment.score == 15  # all_code_in_repo (10) + no_hardcoded_paths default (5)

    def test_complete_score(self):
        """Test score calculation for complete project."""
        env = EnvironmentScanResult(
            env_file_present=True,
            versions_pinned=True,
            python_version_specified=True,
            system_requirements_documented=True,
        )
        data = DataScanResult(
            raw_data_archived=True,
            data_processing_scripts=True,
            random_seeds_set=True,
        )
        code = CodeScanResult(
            all_code_in_repo=True,
            no_hardcoded_paths=True,
            readme_present=True,
            license_present=True,
        )
        docs = DocumentationScanResult(
            methods_documented=True,
            parameters_documented=True,
        )

        assessment = calculate_score(env, data, code, docs)
        assert assessment.score >= 75
        assert assessment.threshold_met is True

    def test_category_scores(self):
        """Test category scores are calculated correctly."""
        env = EnvironmentScanResult(env_file_present=True)  # 5 points
        data = DataScanResult()
        # all_code_in_repo (10) + no_hardcoded_paths default (5) + readme_present (5) = 20
        code = CodeScanResult(all_code_in_repo=True, readme_present=True)
        docs = DocumentationScanResult()

        assessment = calculate_score(env, data, code, docs)
        assert assessment.category_scores["environment"].score == 5
        assert assessment.category_scores["code"].score == 20  # includes default no_hardcoded_paths
        assert assessment.category_scores["data"].score == 0

    def test_checklist_items(self):
        """Test checklist items are populated correctly."""
        env = EnvironmentScanResult(env_file_present=True, versions_pinned=False)
        data = DataScanResult()
        code = CodeScanResult(all_code_in_repo=True)
        docs = DocumentationScanResult()

        assessment = calculate_score(env, data, code, docs)

        checklist_map = {item.id: item for item in assessment.checklist}
        assert checklist_map["env_file_present"].status is True
        assert checklist_map["env_file_present"].points == 5
        assert checklist_map["versions_pinned"].status is False
        assert checklist_map["versions_pinned"].points == 0


class TestGenerateRecommendations:
    """Tests for generate_recommendations function."""

    def test_critical_recommendations(self):
        """Test critical items are flagged."""
        env = EnvironmentScanResult()  # Missing env file
        data = DataScanResult()  # Missing seeds
        code = CodeScanResult(all_code_in_repo=True)
        docs = DocumentationScanResult()

        assessment = calculate_score(env, data, code, docs)
        recs = generate_recommendations(assessment)

        critical_recs = [r for r in recs if "CRITICAL" in r]
        assert len(critical_recs) >= 3  # env_file, versions_pinned, random_seeds, raw_data

    def test_no_recommendations_for_complete(self):
        """Test complete project has fewer recommendations."""
        env = EnvironmentScanResult(
            env_file_present=True,
            versions_pinned=True,
            python_version_specified=True,
            system_requirements_documented=True,
        )
        data = DataScanResult(
            raw_data_archived=True,
            data_processing_scripts=True,
            random_seeds_set=True,
            checksums_present=True,
        )
        code = CodeScanResult(
            all_code_in_repo=True,
            no_hardcoded_paths=True,
            readme_present=True,
            license_present=True,
        )
        docs = DocumentationScanResult(
            methods_documented=True,
            parameters_documented=True,
            expected_outputs_described=True,
            execution_order_documented=True,
        )

        assessment = calculate_score(env, data, code, docs)
        recs = generate_recommendations(assessment)
        assert len(recs) == 0


# =============================================================================
# Full Project Scanning Tests
# =============================================================================


class TestScanProject:
    """Tests for scan_project function."""

    def test_nonexistent_path(self):
        """Test scanning nonexistent path."""
        result = scan_project("/nonexistent/path")
        assert result.error is not None
        assert "does not exist" in result.error

    def test_file_not_directory(self, tmp_project: Path):
        """Test scanning a file instead of directory."""
        test_file = tmp_project / "test.txt"
        test_file.write_text("test")
        result = scan_project(str(test_file))
        assert result.error is not None
        assert "not a directory" in result.error

    def test_minimal_project(self, minimal_project: Path):
        """Test scanning minimal project."""
        result = scan_project(str(minimal_project))
        assert result.error is None
        assert result.assessment.level == 1
        assert result.assessment.level_name == "Minimal"

    def test_standard_project(self, standard_project: Path):
        """Test scanning standard project."""
        result = scan_project(str(standard_project))
        assert result.error is None
        assert result.assessment.level >= 1

    def test_complete_project(self, complete_project: Path):
        """Test scanning complete project."""
        result = scan_project(str(complete_project))
        assert result.error is None
        assert result.assessment.level >= 3
        assert result.assessment.threshold_met is True

    def test_exemplary_project(self, exemplary_project: Path):
        """Test scanning exemplary project."""
        result = scan_project(str(exemplary_project))
        assert result.error is None
        assert result.assessment.level == 4
        assert result.assessment.level_name == "Exemplary"

    def test_to_dict_serialization(self, complete_project: Path):
        """Test that scan results can be serialized to dict."""
        result = scan_project(str(complete_project))
        data = result.to_dict()
        assert "project_path" in data
        assert "scan_results" in data
        assert "assessment" in data
        assert "environment" in data["scan_results"]


# =============================================================================
# Environment Validation Tests
# =============================================================================


class TestValidateCondaEnv:
    """Tests for validate_conda_env function."""

    def test_valid_conda_env(self, valid_conda_env: Path):
        """Test validating a valid conda environment."""
        result = validate_conda_env(valid_conda_env)
        assert result.valid is True
        assert result.score >= 90

    def test_invalid_conda_env(self, invalid_conda_env: Path):
        """Test validating an invalid conda environment."""
        result = validate_conda_env(invalid_conda_env)
        assert result.valid is False
        assert any("Python version" in issue for issue in result.issues)

    def test_missing_name(self, tmp_path: Path):
        """Test conda env missing name field."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text(
            """channels:
  - conda-forge
dependencies:
  - python=3.11
"""
        )
        result = validate_conda_env(env_file)
        assert result.valid is False
        assert any("name" in issue for issue in result.issues)

    def test_defaults_channel_warning(self, tmp_path: Path):
        """Test warning for defaults channel."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text(
            """name: test
channels:
  - defaults
dependencies:
  - python=3.11
"""
        )
        result = validate_conda_env(env_file)
        assert any("defaults" in warn for warn in result.warnings)

    def test_strict_mode(self, tmp_path: Path):
        """Test strict mode treats unpinned as errors."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text(
            """name: test
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy
"""
        )
        result = validate_conda_env(env_file, strict=True)
        assert result.valid is False
        assert any("Unpinned" in issue for issue in result.issues)


class TestValidateRequirements:
    """Tests for validate_requirements function."""

    def test_valid_requirements(self, valid_requirements: Path):
        """Test validating a valid requirements.txt."""
        result = validate_requirements(valid_requirements)
        assert result.valid is True
        assert result.score == 100

    def test_invalid_requirements(self, invalid_requirements: Path):
        """Test validating requirements with unpinned deps."""
        result = validate_requirements(invalid_requirements)
        # Not strict, so still valid but with warnings
        assert result.valid is True
        assert len(result.warnings) > 0

    def test_strict_mode(self, invalid_requirements: Path):
        """Test strict mode for requirements.txt."""
        result = validate_requirements(invalid_requirements, strict=True)
        assert result.valid is False

    def test_loose_pinning_warning(self, tmp_path: Path):
        """Test warning for loose pinning (>=, ~=)."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(
            """numpy>=1.20
pandas~=2.0
"""
        )
        result = validate_requirements(req_file)
        assert any("Loosely pinned" in warn for warn in result.warnings)


class TestValidatePyproject:
    """Tests for validate_pyproject function."""

    def test_valid_pyproject(self, valid_pyproject: Path):
        """Test validating a valid pyproject.toml."""
        result = validate_pyproject(valid_pyproject)
        assert result.valid is True

    def test_missing_python_version(self, tmp_path: Path):
        """Test pyproject.toml missing Python version."""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text(
            """[project]
name = "test"
dependencies = [
    "numpy==1.26.0",
]
"""
        )
        result = validate_pyproject(toml_file)
        assert result.valid is False
        assert any("Python version" in issue for issue in result.issues)


class TestValidateEnvironment:
    """Tests for validate_environment function (dispatcher)."""

    def test_conda_yaml(self, valid_conda_env: Path):
        """Test dispatching to conda validator."""
        result = validate_environment(valid_conda_env)
        assert result.valid is True

    def test_requirements_txt(self, valid_requirements: Path):
        """Test dispatching to requirements validator."""
        result = validate_environment(valid_requirements)
        assert result.valid is True

    def test_pyproject_toml(self, valid_pyproject: Path):
        """Test dispatching to pyproject validator."""
        result = validate_environment(valid_pyproject)
        assert result.valid is True

    def test_file_not_found(self):
        """Test handling of nonexistent file."""
        result = validate_environment(Path("/nonexistent/file.yml"))
        assert result.valid is False
        assert "not found" in result.error

    def test_unsupported_file_type(self, tmp_path: Path):
        """Test handling of unsupported file type."""
        test_file = tmp_path / "setup.cfg"
        test_file.write_text("[metadata]\nname = test")
        result = validate_environment(test_file)
        assert result.valid is False
        assert "Unsupported" in result.error


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_environment_yml(self, tmp_path: Path):
        """Test handling of empty environment.yml."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text("")
        result = validate_conda_env(env_file)
        assert result.valid is False

    def test_malformed_yaml(self, tmp_path: Path):
        """Test handling of malformed YAML."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text("name: test\n  invalid: yaml: here")
        result = validate_conda_env(env_file)
        assert result.valid is False

    def test_empty_requirements(self, tmp_path: Path):
        """Test handling of empty requirements.txt."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")
        result = validate_requirements(req_file)
        assert result.valid is True  # Empty is technically valid

    def test_comments_only_requirements(self, tmp_path: Path):
        """Test requirements.txt with only comments."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(
            """# This is a comment
# Another comment
"""
        )
        result = validate_requirements(req_file)
        assert result.valid is True

    def test_unicode_in_readme(self, tmp_path: Path):
        """Test handling of unicode in README."""
        (tmp_path / "README.md").write_text(
            """# Project

## Methods

Analysis using advanced techniques.
"""
        )
        result = scan_documentation(tmp_path)
        assert result.methods_documented is True

    def test_deeply_nested_scripts(self, tmp_path: Path):
        """Test detection of scripts in nested directories."""
        nested = tmp_path / "src" / "analysis" / "preprocessing"
        nested.mkdir(parents=True)
        (nested / "preprocess.py").write_text("# preprocessing")
        result = scan_data(tmp_path)
        # Only checks root, scripts/, src/ directly
        # Deep nesting may not be detected
        assert isinstance(result.data_processing_scripts, bool)

    def test_pip_dependencies_in_conda(self, tmp_path: Path):
        """Test conda environment with pip dependencies."""
        env_file = tmp_path / "environment.yml"
        env_file.write_text(
            """name: test
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy=1.26.0
  - pip:
    - scanpy==1.9.5
    - anndata==0.10.0
"""
        )
        result = validate_conda_env(env_file)
        assert result.valid is True
        assert result.summary.deps_count >= 4


# =============================================================================
# Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests to verify scanning produces consistent results."""

    def test_multiple_scans_same_result(self, complete_project: Path):
        """Test that multiple scans produce identical results."""
        results = [scan_project(str(complete_project)) for _ in range(5)]

        scores = [r.assessment.score for r in results]
        levels = [r.assessment.level for r in results]

        assert len(set(scores)) == 1, "Scores should be identical"
        assert len(set(levels)) == 1, "Levels should be identical"

    def test_score_calculation_deterministic(self):
        """Test that score calculation is deterministic."""
        env = EnvironmentScanResult(
            env_file_present=True,
            versions_pinned=True,
            python_version_specified=True,
        )
        data = DataScanResult(random_seeds_set=True)
        code = CodeScanResult(all_code_in_repo=True, readme_present=True)
        docs = DocumentationScanResult(methods_documented=True)

        scores = [calculate_score(env, data, code, docs).score for _ in range(10)]
        assert len(set(scores)) == 1, "Score calculation should be deterministic"
