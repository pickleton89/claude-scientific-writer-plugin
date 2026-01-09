#!/usr/bin/env python3
"""
Reproducibility Project Scanner

Deterministically scores reproducibility checklist items by scanning
project files rather than relying on LLM interpretation.

Usage:
    python scan_project.py /path/to/project
    python scan_project.py /path/to/project --output json
"""

import argparse
import json
import re
from pathlib import Path

try:
    from .utils.schemas import (
        CategoryScore,
        ChecklistItem,
        CodeScanResult,
        DataScanResult,
        DocumentationScanResult,
        EnvironmentScanResult,
        ProjectScanResult,
        ReproducibilityAssessment,
    )
except ImportError:
    from utils.schemas import (
        CategoryScore,
        ChecklistItem,
        CodeScanResult,
        DataScanResult,
        DocumentationScanResult,
        EnvironmentScanResult,
        ProjectScanResult,
        ReproducibilityAssessment,
    )

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Checklist item definitions with points and categories
CHECKLIST_DEFINITIONS = {
    # Environment (25 points max)
    "env_file_present": {"points": 5, "category": "environment"},
    "versions_pinned": {"points": 10, "category": "environment"},
    "python_version_specified": {"points": 5, "category": "environment"},
    "system_requirements_documented": {"points": 5, "category": "environment"},
    # Data (25 points max)
    "raw_data_archived": {"points": 10, "category": "data"},
    "data_processing_scripts": {"points": 5, "category": "data"},
    "random_seeds_set": {"points": 5, "category": "data"},
    "checksums_present": {"points": 5, "category": "data"},
    # Code (25 points max)
    "all_code_in_repo": {"points": 10, "category": "code"},
    "no_hardcoded_paths": {"points": 5, "category": "code"},
    "readme_present": {"points": 5, "category": "code"},
    "license_present": {"points": 5, "category": "code"},
    # Documentation (25 points max)
    "methods_documented": {"points": 10, "category": "documentation"},
    "parameters_documented": {"points": 5, "category": "documentation"},
    "expected_outputs_described": {"points": 5, "category": "documentation"},
    "execution_order_documented": {"points": 5, "category": "documentation"},
}

# Reproducibility levels
LEVELS = [
    (90, 4, "Exemplary"),
    (75, 3, "Complete"),
    (50, 2, "Standard"),
    (0, 1, "Minimal"),
]

# Threshold for considering dependencies "pinned" (percentage)
# 90% allows for a few unpinned system packages while ensuring reproducibility
PINNED_THRESHOLD_PERCENT = 90

# Minimum score required for publication-ready reproducibility
PUBLICATION_READY_THRESHOLD = 75


def scan_environment(root: Path) -> EnvironmentScanResult:
    """Scan for environment specification files and assess quality."""
    result = EnvironmentScanResult()

    # Check for environment files
    env_yml = root / "environment.yml"
    env_yaml = root / "environment.yaml"
    requirements = root / "requirements.txt"
    pyproject = root / "pyproject.toml"
    dockerfile = root / "Dockerfile"

    if env_yml.exists() or env_yaml.exists():
        env_file = env_yml if env_yml.exists() else env_yaml
        result.env_file_present = True
        result.env_file_type = "conda"

        if HAS_YAML:
            try:
                with open(env_file) as f:
                    env = yaml.safe_load(f)

                deps = env.get("dependencies", [])
                if deps:
                    pinned = 0
                    total = 0
                    for dep in deps:
                        if isinstance(dep, str):
                            total += 1
                            if "=" in dep:
                                pinned += 1
                            if dep.startswith("python="):
                                result.python_version_specified = True
                        elif isinstance(dep, dict) and "pip" in dep:
                            for pip_dep in dep.get("pip", []):
                                total += 1
                                if "==" in pip_dep:
                                    pinned += 1

                    if total > 0:
                        result.pinned_percentage = (pinned / total) * 100
                        result.versions_pinned = result.pinned_percentage >= PINNED_THRESHOLD_PERCENT

                    if not result.versions_pinned:
                        result.issues.append(
                            f"Only {result.pinned_percentage:.0f}% of dependencies are pinned"
                        )
            except Exception as e:
                result.issues.append(f"Failed to parse environment file: {e}")

    elif requirements.exists():
        result.env_file_present = True
        result.env_file_type = "pip"

        content = requirements.read_text()
        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.startswith("#")
        ]

        if lines:
            pinned = sum(1 for line in lines if "==" in line)
            result.pinned_percentage = (pinned / len(lines)) * 100
            result.versions_pinned = result.pinned_percentage >= PINNED_THRESHOLD_PERCENT

            if not result.versions_pinned:
                result.issues.append(
                    f"Only {result.pinned_percentage:.0f}% of dependencies are pinned"
                )

    elif pyproject.exists():
        result.env_file_present = True
        result.env_file_type = "pyproject"

        content = pyproject.read_text()
        # Check for python version constraint
        if re.search(r'python\s*[=<>]', content):
            result.python_version_specified = True
        # Check for pinned dependencies (look for == patterns)
        deps_match = re.search(r'\[project\.dependencies\](.*?)(?:\[|$)', content, re.DOTALL)
        if deps_match:
            deps_section = deps_match.group(1)
            lines = [line for line in deps_section.splitlines() if line.strip() and '"' in line]
            if lines:
                pinned = sum(1 for line in lines if "==" in line)
                result.pinned_percentage = (pinned / len(lines)) * 100
                result.versions_pinned = result.pinned_percentage >= PINNED_THRESHOLD_PERCENT

    # Check for Dockerfile (Level 3+)
    if dockerfile.exists():
        result.dockerfile_present = True
        content = dockerfile.read_text()
        if re.search(r"^FROM\s+\S+:\S+", content, re.MULTILINE):
            result.dockerfile_pinned = True

    # Check for system requirements documentation
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text().lower()
        if any(
            term in content
            for term in ["requirements", "installation", "dependencies", "prerequisites"]
        ):
            result.system_requirements_documented = True

    return result


def scan_data(root: Path) -> DataScanResult:
    """Scan for data management practices."""
    result = DataScanResult()

    # Check for data directory structure
    data_dir = root / "data"
    if data_dir.exists():
        raw_dir = data_dir / "raw"
        if raw_dir.exists():
            raw_readme = raw_dir / "README.md"
            if raw_readme.exists():
                content = raw_readme.read_text().lower()
                if any(
                    term in content for term in ["doi", "accession", "geo", "sra", "zenodo"]
                ):
                    result.raw_data_archived = True

    # Check for data processing scripts
    scripts_dir = root / "scripts"
    src_dir = root / "src"

    processing_patterns = ["preprocess", "process", "clean", "transform", "prepare"]
    for search_dir in [scripts_dir, src_dir, root]:
        if search_dir.exists():
            for py_file in search_dir.glob("*.py"):
                if any(p in py_file.name.lower() for p in processing_patterns):
                    result.data_processing_scripts = True
                    break

    # Check for random seeds in Python/R files
    seed_patterns = [
        r"random\.seed\s*\(",
        r"np\.random\.seed\s*\(",
        r"torch\.manual_seed\s*\(",
        r"tf\.random\.set_seed\s*\(",
        r"set\.seed\s*\(",  # R
        r"RANDOM_SEED\s*=",
        r"SEED\s*=",
    ]

    for py_file in root.rglob("*.py"):
        if _should_skip_path(py_file):
            continue
        try:
            content = py_file.read_text()
            if any(re.search(p, content) for p in seed_patterns):
                result.random_seeds_set = True
                break
        except Exception:
            pass

    for r_file in root.rglob("*.R"):
        if _should_skip_path(r_file):
            continue
        try:
            content = r_file.read_text()
            if re.search(r"set\.seed\s*\(", content):
                result.random_seeds_set = True
                break
        except Exception:
            pass

    # Check for checksums
    checksum_files = ["checksums.md5", "checksums.sha256", "MD5SUMS", "SHA256SUMS"]
    for cf in checksum_files:
        if (root / cf).exists() or (data_dir.exists() and (data_dir / cf).exists()):
            result.checksums_present = True
            break

    return result


def scan_code(root: Path) -> CodeScanResult:
    """Scan for code quality practices."""
    result = CodeScanResult()

    # Check for README
    readme_variants = ["README.md", "README.rst", "README.txt", "README"]
    result.readme_present = any((root / r).exists() for r in readme_variants)

    # Check for LICENSE
    license_variants = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]
    result.license_present = any((root / lic).exists() for lic in license_variants)

    # Check for hardcoded paths
    hardcoded_patterns = [
        r'["\'][/\\]home[/\\]',
        r'["\'][/\\]Users[/\\]',
        r'["\']C:\\\\',
        r'["\'][/\\]mnt[/\\]',
        r'["\'][/\\]scratch[/\\]',
    ]

    for py_file in root.rglob("*.py"):
        if _should_skip_path(py_file):
            continue

        try:
            content = py_file.read_text()
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result.no_hardcoded_paths = False
                    result.hardcoded_paths_found.append(str(py_file))
                    break
        except Exception:
            pass

    if not result.readme_present:
        result.issues.append("README.md not found")
    if not result.license_present:
        result.issues.append("LICENSE file not found")
    if not result.no_hardcoded_paths:
        result.issues.append(f"Hardcoded paths found in: {result.hardcoded_paths_found[:3]}")

    return result


def scan_documentation(root: Path) -> DocumentationScanResult:
    """Scan for documentation quality."""
    result = DocumentationScanResult()

    # Check for methods documentation
    docs_dir = root / "docs"
    if docs_dir.exists():
        methods_files = ["methods.md", "methodology.md", "analysis.md"]
        result.methods_documented = any((docs_dir / m).exists() for m in methods_files)

    # Check README for methods section
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text().lower()
        if "## method" in content or "## analysis" in content or "## workflow" in content:
            result.methods_documented = True
        if "## usage" in content or "## running" in content or "## execution" in content:
            result.execution_order_documented = True
        if "## output" in content or "## results" in content:
            result.expected_outputs_described = True

    # Check for config files (parameter documentation)
    config_files = [
        "config.yaml",
        "config.yml",
        "config.json",
        "params.yaml",
        "parameters.yaml",
    ]
    config_dir = root / "config"
    result.parameters_documented = any(
        (root / c).exists() or (config_dir.exists() and (config_dir / c).exists())
        for c in config_files
    )

    # Check for numbered scripts/notebooks (execution order)
    scripts_dir = root / "scripts"
    notebooks_dir = root / "notebooks"

    numbered_pattern = re.compile(r"^\d+[_-]")
    for search_dir in [scripts_dir, notebooks_dir]:
        if search_dir.exists():
            files = list(search_dir.iterdir())
            numbered = [f for f in files if numbered_pattern.match(f.name)]
            if len(numbered) >= 2:
                result.execution_order_documented = True
                break

    return result


def _should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped (virtual env, hidden, etc.)."""
    skip_parts = {".git", ".venv", "venv", "env", "__pycache__", "node_modules", ".tox"}
    return any(part.startswith(".") or part in skip_parts for part in path.parts)


def calculate_score(
    env: EnvironmentScanResult,
    data: DataScanResult,
    code: CodeScanResult,
    docs: DocumentationScanResult,
) -> ReproducibilityAssessment:
    """Calculate reproducibility score based on 20-item checklist."""
    # Build checklist items with actual status
    status_map = {
        "env_file_present": env.env_file_present,
        "versions_pinned": env.versions_pinned,
        "python_version_specified": env.python_version_specified,
        "system_requirements_documented": env.system_requirements_documented,
        "raw_data_archived": data.raw_data_archived,
        "data_processing_scripts": data.data_processing_scripts,
        "random_seeds_set": data.random_seeds_set,
        "checksums_present": data.checksums_present,
        "all_code_in_repo": code.all_code_in_repo,
        "no_hardcoded_paths": code.no_hardcoded_paths,
        "readme_present": code.readme_present,
        "license_present": code.license_present,
        "methods_documented": docs.methods_documented,
        "parameters_documented": docs.parameters_documented,
        "expected_outputs_described": docs.expected_outputs_described,
        "execution_order_documented": docs.execution_order_documented,
    }

    checklist_items = []
    for item_id, defn in CHECKLIST_DEFINITIONS.items():
        item = ChecklistItem(
            id=item_id,
            category=defn["category"],
            points=defn["points"] if status_map[item_id] else 0,
            status=status_map[item_id],
            max_points=defn["points"],
        )
        checklist_items.append(item)

    # Calculate total and category scores
    total_score = sum(item.points for item in checklist_items)
    max_score = sum(item.max_points for item in checklist_items)

    category_scores = {}
    for category in ["environment", "data", "code", "documentation"]:
        cat_items = [item for item in checklist_items if item.category == category]
        cat_score = sum(item.points for item in cat_items)
        category_scores[category] = CategoryScore(name=category, score=cat_score, max_score=25)

    # Determine level
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    level = 1
    level_name = "Minimal"
    for threshold, lvl, name in LEVELS:
        if percentage >= threshold:
            level = lvl
            level_name = name
            break

    return ReproducibilityAssessment(
        score=total_score,
        max_score=max_score,
        percentage=percentage,
        threshold_met=total_score >= PUBLICATION_READY_THRESHOLD,
        level=level,
        level_name=level_name,
        category_scores=category_scores,
        checklist=checklist_items,
    )


def generate_recommendations(assessment: ReproducibilityAssessment) -> list[str]:
    """Generate prioritized recommendations based on score."""
    recommendations = []

    # Critical items (high impact)
    critical = ["versions_pinned", "random_seeds_set", "raw_data_archived", "env_file_present"]
    # Major items (medium impact)
    major = [
        "no_hardcoded_paths",
        "data_processing_scripts",
        "methods_documented",
        "parameters_documented",
    ]
    # Minor items (low impact)
    minor = ["license_present", "checksums_present", "expected_outputs_described"]

    checklist_map = {item.id: item for item in assessment.checklist}

    for item_id in critical:
        if item_id in checklist_map and not checklist_map[item_id].status:
            recommendations.append(f"CRITICAL: {item_id.replace('_', ' ').title()}")

    for item_id in major:
        if item_id in checklist_map and not checklist_map[item_id].status:
            recommendations.append(f"MAJOR: {item_id.replace('_', ' ').title()}")

    for item_id in minor:
        if item_id in checklist_map and not checklist_map[item_id].status:
            recommendations.append(f"MINOR: {item_id.replace('_', ' ').title()}")

    return recommendations


def scan_project(root_path: str) -> ProjectScanResult:
    """Main entry point: scan a project and return full assessment."""
    root = Path(root_path).resolve()

    if not root.exists():
        return ProjectScanResult(
            project_path=str(root),
            environment=EnvironmentScanResult(),
            data=DataScanResult(),
            code=CodeScanResult(),
            documentation=DocumentationScanResult(),
            assessment=ReproducibilityAssessment(
                score=0,
                max_score=100,
                percentage=0,
                threshold_met=False,
                level=0,
                level_name="Error",
            ),
            error=f"Path does not exist: {root}",
        )

    if not root.is_dir():
        return ProjectScanResult(
            project_path=str(root),
            environment=EnvironmentScanResult(),
            data=DataScanResult(),
            code=CodeScanResult(),
            documentation=DocumentationScanResult(),
            assessment=ReproducibilityAssessment(
                score=0,
                max_score=100,
                percentage=0,
                threshold_met=False,
                level=0,
                level_name="Error",
            ),
            error=f"Path is not a directory: {root}",
        )

    # Run all scans
    env_results = scan_environment(root)
    data_results = scan_data(root)
    code_results = scan_code(root)
    docs_results = scan_documentation(root)

    # Calculate score
    assessment = calculate_score(env_results, data_results, code_results, docs_results)

    # Compile all issues
    all_issues = (
        env_results.issues + data_results.issues + code_results.issues + docs_results.issues
    )

    return ProjectScanResult(
        project_path=str(root),
        environment=env_results,
        data=data_results,
        code=code_results,
        documentation=docs_results,
        assessment=assessment,
        issues=all_issues,
        recommendations=generate_recommendations(assessment),
    )


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Scan project for reproducibility assessment")
    parser.add_argument("path", help="Path to project root directory")
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    result = scan_project(args.path)

    if args.output == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"REPRODUCIBILITY ASSESSMENT: {result.project_path}")
        print(f"{'=' * 60}\n")

        if result.error:
            print(f"ERROR: {result.error}")
            return

        assessment = result.assessment
        print(
            f"Overall Score: {assessment.score}/{assessment.max_score} "
            f"({assessment.percentage:.0f}%)"
        )
        print(f"Level: {assessment.level} - {assessment.level_name}")
        print(
            f"Publication Ready: "
            f"{'Yes' if assessment.threshold_met else f'No (need >={PUBLICATION_READY_THRESHOLD}%)'}"
        )

        print("\nCategory Scores:")
        for cat, score in assessment.category_scores.items():
            print(f"  {cat.title()}: {score.score}/{score.max_score}")

        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  {rec}")

        print()


if __name__ == "__main__":
    main()
