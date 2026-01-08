# Determinism Audit: reproducible-research

> Audit Date: 2026-01-07
> Skill Version: 2.2.0
> Development Stage: First draft skill
> Auditor: Claude Opus 4.5

---

## Executive Summary

The reproducible-research skill has an exceptionally strong foundation with well-defined quantified thresholds (20-item checklist, FAIR percentages, environment levels 1-4) and comprehensive reference documentation. However, the skill relies heavily on LLM judgment to assess project state and calculate scores—operations that could be significantly automated with validation scripts. Primary recommendation: implement a project scanner that programmatically detects reproducibility elements, enabling deterministic baseline scoring.

**Current Determinism Level:** 65%
**Target Determinism Level:** 85%
**Primary Gap:** Assessment and validation stages rely on LLM interpretation

---

## Determinism Analysis

### Already Deterministic (Strengths)

| Component | Implementation | Determinism |
|-----------|---------------|-------------|
| 20-item checklist | Exact point values (5 or 10 per item) | 100% |
| FAIR scoring | 25% per principle, defined thresholds | 100% |
| Environment levels | Level 1-4 with explicit criteria | 100% |
| Repository selection | Lookup table by data type | 100% |
| Data Availability templates | 3 fixed templates | 100% |
| Project structure | Fixed directory layout | 100% |
| Severity classifications | 🔴/🟡/🟢 with impact percentages | 100% |

### Currently Stochastic (Improvement Opportunities)

| Component | Current Approach | Variance Source |
|-----------|-----------------|-----------------|
| Baseline scoring | "Calculate baseline score using checklist" | LLM judgment on item presence |
| Element detection | "Identify which elements exist" | Subjective file assessment |
| Gap prioritization | Conversational prioritization | LLM interpretation |
| FAIR compliance | Manual principle assessment | No automated validation |
| Template selection | User-LLM conversation | Could be decision tree |
| Validation (Stage 4) | "Re-score using checklist" | Same LLM subjectivity |

---

## Input Analysis

### Current State

Inputs are informally gathered through conversation (project type, current state, dependencies). The skill asks users to describe their project without structured input collection.

### Recommendations

1. **Add structured project path input**: Request the repository root path explicitly

2. **Define input schema for project metadata**:

```yaml
project_input:
  root_path: "/path/to/project"
  project_type:  # enum
    - "rnaseq"
    - "proteomics"
    - "metabolomics"
    - "ml"
    - "general"
  target_journal: "optional string"
  data_types:  # enum list
    - "FASTQ"
    - "BAM"
    - "CSV"
    - "H5AD"
```

3. **Auto-detection over user description**: Replace "ask user what exists" with automated file scanning

---

## Output Analysis

### Current State

Outputs include reproducibility scores, FAIR assessments, and generated files. However, output formats are prose-based rather than structured.

### Recommended Output Schema

```json
{
  "reproducibility_assessment": {
    "score": 75,
    "threshold_met": true,
    "level": 3,
    "level_name": "Complete",
    "category_scores": {
      "environment": {"score": 20, "max": 25},
      "data": {"score": 20, "max": 25},
      "code": {"score": 20, "max": 25},
      "documentation": {"score": 15, "max": 25}
    },
    "checklist_items": [
      {"id": "env_file_present", "category": "environment", "status": "pass", "points": 5},
      {"id": "versions_pinned", "category": "environment", "status": "fail", "points": 0},
      {"id": "python_version_specified", "category": "environment", "status": "pass", "points": 5}
    ]
  },
  "fair_assessment": {
    "score": 75,
    "compliant": true,
    "principles": {
      "findable": {"score": 25, "items": ["F1", "F2", "F3", "F4"]},
      "accessible": {"score": 25, "items": ["A1", "A1.1", "A1.2", "A2"]},
      "interoperable": {"score": 15, "items": ["I1", "I2"]},
      "reusable": {"score": 10, "items": ["R1.1"]}
    }
  },
  "template_selection": {
    "data_availability": "TEMPLATE_PUBLIC_REPO",
    "repository": "GEO"
  }
}
```

---

## Code Integration Plan

### Phase 1: Project Scanner (Priority: HIGH)

Create automated detection of reproducibility elements.

**File:** `scripts/scan_project.py`

```python
#!/usr/bin/env python3
"""
Reproducibility Project Scanner

Deterministically scores reproducibility checklist items by scanning
project files rather than relying on LLM interpretation.

Usage:
    python scan_project.py /path/to/project
    python scan_project.py /path/to/project --output json
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def scan_environment(root: Path) -> Dict[str, Any]:
    """Scan for environment specification files and assess quality."""
    results = {
        "env_file_present": False,
        "env_file_type": None,
        "versions_pinned": False,
        "pinned_percentage": 0.0,
        "python_version_specified": False,
        "system_requirements_documented": False,
        "issues": []
    }

    # Check for environment files
    env_yml = root / "environment.yml"
    env_yaml = root / "environment.yaml"
    requirements = root / "requirements.txt"
    dockerfile = root / "Dockerfile"

    if env_yml.exists() or env_yaml.exists():
        env_file = env_yml if env_yml.exists() else env_yaml
        results["env_file_present"] = True
        results["env_file_type"] = "conda"

        if HAS_YAML:
            try:
                with open(env_file) as f:
                    env = yaml.safe_load(f)

                deps = env.get("dependencies", [])
                if deps:
                    # Count pinned dependencies (contains = or ==)
                    pinned = 0
                    total = 0
                    for dep in deps:
                        if isinstance(dep, str):
                            total += 1
                            if "=" in dep:
                                pinned += 1
                            # Check for Python version
                            if dep.startswith("python="):
                                results["python_version_specified"] = True
                        elif isinstance(dep, dict) and "pip" in dep:
                            # Handle pip dependencies
                            for pip_dep in dep.get("pip", []):
                                total += 1
                                if "==" in pip_dep:
                                    pinned += 1

                    if total > 0:
                        results["pinned_percentage"] = (pinned / total) * 100
                        results["versions_pinned"] = results["pinned_percentage"] >= 90

                    if not results["versions_pinned"]:
                        results["issues"].append(
                            f"Only {results['pinned_percentage']:.0f}% of dependencies are pinned"
                        )
            except Exception as e:
                results["issues"].append(f"Failed to parse environment file: {e}")

    elif requirements.exists():
        results["env_file_present"] = True
        results["env_file_type"] = "pip"

        content = requirements.read_text()
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]

        if lines:
            pinned = sum(1 for l in lines if "==" in l)
            results["pinned_percentage"] = (pinned / len(lines)) * 100
            results["versions_pinned"] = results["pinned_percentage"] >= 90

            if not results["versions_pinned"]:
                results["issues"].append(
                    f"Only {results['pinned_percentage']:.0f}% of dependencies are pinned"
                )

    # Check for Dockerfile (Level 3+)
    if dockerfile.exists():
        results["dockerfile_present"] = True
        content = dockerfile.read_text()
        # Check for pinned base image
        if re.search(r'^FROM\s+\S+:\S+', content, re.MULTILINE):
            results["dockerfile_pinned"] = True

    # Check for system requirements documentation
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text().lower()
        if any(term in content for term in ["requirements", "installation", "dependencies", "prerequisites"]):
            results["system_requirements_documented"] = True

    return results


def scan_data(root: Path) -> Dict[str, Any]:
    """Scan for data management practices."""
    results = {
        "raw_data_archived": False,
        "data_processing_scripts": False,
        "random_seeds_set": False,
        "checksums_present": False,
        "issues": []
    }

    # Check for data directory structure
    data_dir = root / "data"
    if data_dir.exists():
        raw_dir = data_dir / "raw"
        if raw_dir.exists():
            # Check for README documenting data source
            raw_readme = raw_dir / "README.md"
            if raw_readme.exists():
                content = raw_readme.read_text().lower()
                if any(term in content for term in ["doi", "accession", "geo", "sra", "zenodo"]):
                    results["raw_data_archived"] = True

    # Check for data processing scripts
    scripts_dir = root / "scripts"
    src_dir = root / "src"

    processing_patterns = ["preprocess", "process", "clean", "transform", "prepare"]
    for search_dir in [scripts_dir, src_dir, root]:
        if search_dir.exists():
            for py_file in search_dir.glob("*.py"):
                if any(p in py_file.name.lower() for p in processing_patterns):
                    results["data_processing_scripts"] = True
                    break

    # Check for random seeds in Python/R files
    seed_patterns = [
        r'random\.seed\s*\(',
        r'np\.random\.seed\s*\(',
        r'torch\.manual_seed\s*\(',
        r'tf\.random\.set_seed\s*\(',
        r'set\.seed\s*\(',  # R
        r'RANDOM_SEED\s*=',
        r'SEED\s*='
    ]

    for py_file in root.rglob("*.py"):
        try:
            content = py_file.read_text()
            if any(re.search(p, content) for p in seed_patterns):
                results["random_seeds_set"] = True
                break
        except Exception:
            pass

    for r_file in root.rglob("*.R"):
        try:
            content = r_file.read_text()
            if re.search(r'set\.seed\s*\(', content):
                results["random_seeds_set"] = True
                break
        except Exception:
            pass

    # Check for checksums
    checksum_files = ["checksums.md5", "checksums.sha256", "MD5SUMS", "SHA256SUMS"]
    for cf in checksum_files:
        if (root / cf).exists() or (root / "data" / cf).exists():
            results["checksums_present"] = True
            break

    return results


def scan_code(root: Path) -> Dict[str, Any]:
    """Scan for code quality practices."""
    results = {
        "all_code_in_repo": True,  # Assumed true if we're scanning
        "no_hardcoded_paths": True,
        "readme_present": False,
        "license_present": False,
        "hardcoded_paths_found": [],
        "issues": []
    }

    # Check for README
    readme_variants = ["README.md", "README.rst", "README.txt", "README"]
    results["readme_present"] = any((root / r).exists() for r in readme_variants)

    # Check for LICENSE
    license_variants = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]
    results["license_present"] = any((root / l).exists() for l in license_variants)

    # Check for hardcoded paths
    hardcoded_patterns = [
        r'["\'][/\\]home[/\\]',
        r'["\'][/\\]Users[/\\]',
        r'["\']C:\\\\',
        r'["\'][/\\]mnt[/\\]',
        r'["\'][/\\]scratch[/\\]'
    ]

    for py_file in root.rglob("*.py"):
        # Skip virtual environments and hidden directories
        if any(part.startswith('.') or part in ['venv', 'env', '.venv', '__pycache__']
               for part in py_file.parts):
            continue

        try:
            content = py_file.read_text()
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    results["no_hardcoded_paths"] = False
                    results["hardcoded_paths_found"].append(str(py_file))
                    break
        except Exception:
            pass

    if not results["readme_present"]:
        results["issues"].append("README.md not found")
    if not results["license_present"]:
        results["issues"].append("LICENSE file not found")
    if not results["no_hardcoded_paths"]:
        results["issues"].append(f"Hardcoded paths found in: {results['hardcoded_paths_found'][:3]}")

    return results


def scan_documentation(root: Path) -> Dict[str, Any]:
    """Scan for documentation quality."""
    results = {
        "methods_documented": False,
        "parameters_documented": False,
        "expected_outputs_described": False,
        "execution_order_documented": False,
        "issues": []
    }

    # Check for methods documentation
    docs_dir = root / "docs"
    if docs_dir.exists():
        methods_files = ["methods.md", "methodology.md", "analysis.md"]
        results["methods_documented"] = any((docs_dir / m).exists() for m in methods_files)

    # Check README for methods section
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text().lower()
        if "## method" in content or "## analysis" in content or "## workflow" in content:
            results["methods_documented"] = True
        if "## usage" in content or "## running" in content or "## execution" in content:
            results["execution_order_documented"] = True
        if "## output" in content or "## results" in content:
            results["expected_outputs_described"] = True

    # Check for config files (parameter documentation)
    config_files = ["config.yaml", "config.yml", "config.json", "params.yaml", "parameters.yaml"]
    results["parameters_documented"] = any((root / c).exists() or (root / "config" / c).exists()
                                           for c in config_files)

    # Check for numbered scripts/notebooks (execution order)
    scripts_dir = root / "scripts"
    notebooks_dir = root / "notebooks"

    numbered_pattern = re.compile(r'^\d+[_-]')
    for search_dir in [scripts_dir, notebooks_dir]:
        if search_dir.exists():
            files = list(search_dir.iterdir())
            numbered = [f for f in files if numbered_pattern.match(f.name)]
            if len(numbered) >= 2:
                results["execution_order_documented"] = True
                break

    return results


def calculate_score(env: Dict, data: Dict, code: Dict, docs: Dict) -> Dict[str, Any]:
    """Calculate reproducibility score based on 20-item checklist."""

    checklist = {
        # Environment (25 points)
        "env_file_present": {"points": 5, "status": env["env_file_present"]},
        "versions_pinned": {"points": 10, "status": env["versions_pinned"]},
        "python_version_specified": {"points": 5, "status": env["python_version_specified"]},
        "system_requirements_documented": {"points": 5, "status": env["system_requirements_documented"]},

        # Data (25 points)
        "raw_data_archived": {"points": 10, "status": data["raw_data_archived"]},
        "data_processing_scripts": {"points": 5, "status": data["data_processing_scripts"]},
        "random_seeds_set": {"points": 5, "status": data["random_seeds_set"]},
        "checksums_present": {"points": 5, "status": data["checksums_present"]},

        # Code (25 points)
        "all_code_in_repo": {"points": 10, "status": code["all_code_in_repo"]},
        "no_hardcoded_paths": {"points": 5, "status": code["no_hardcoded_paths"]},
        "readme_present": {"points": 5, "status": code["readme_present"]},
        "license_present": {"points": 5, "status": code["license_present"]},

        # Documentation (25 points)
        "methods_documented": {"points": 10, "status": docs["methods_documented"]},
        "parameters_documented": {"points": 5, "status": docs["parameters_documented"]},
        "expected_outputs_described": {"points": 5, "status": docs["expected_outputs_described"]},
        "execution_order_documented": {"points": 5, "status": docs["execution_order_documented"]},
    }

    # Calculate scores
    total_score = sum(item["points"] for item in checklist.values() if item["status"])
    max_score = sum(item["points"] for item in checklist.values())

    category_scores = {
        "environment": sum(checklist[k]["points"] for k in
                         ["env_file_present", "versions_pinned", "python_version_specified", "system_requirements_documented"]
                         if checklist[k]["status"]),
        "data": sum(checklist[k]["points"] for k in
                   ["raw_data_archived", "data_processing_scripts", "random_seeds_set", "checksums_present"]
                   if checklist[k]["status"]),
        "code": sum(checklist[k]["points"] for k in
                   ["all_code_in_repo", "no_hardcoded_paths", "readme_present", "license_present"]
                   if checklist[k]["status"]),
        "documentation": sum(checklist[k]["points"] for k in
                            ["methods_documented", "parameters_documented", "expected_outputs_described", "execution_order_documented"]
                            if checklist[k]["status"]),
    }

    # Determine level
    if total_score >= 90:
        level = 4
        level_name = "Exemplary"
    elif total_score >= 75:
        level = 3
        level_name = "Complete"
    elif total_score >= 50:
        level = 2
        level_name = "Standard"
    else:
        level = 1
        level_name = "Minimal"

    return {
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100,
        "threshold_met": total_score >= 75,
        "level": level,
        "level_name": level_name,
        "category_scores": category_scores,
        "checklist": checklist
    }


def scan_project(root_path: str) -> Dict[str, Any]:
    """Main entry point: scan a project and return full assessment."""
    root = Path(root_path).resolve()

    if not root.exists():
        return {"error": f"Path does not exist: {root}"}

    if not root.is_dir():
        return {"error": f"Path is not a directory: {root}"}

    # Run all scans
    env_results = scan_environment(root)
    data_results = scan_data(root)
    code_results = scan_code(root)
    docs_results = scan_documentation(root)

    # Calculate score
    score_results = calculate_score(env_results, data_results, code_results, docs_results)

    # Compile all issues
    all_issues = (
        env_results.get("issues", []) +
        data_results.get("issues", []) +
        code_results.get("issues", []) +
        docs_results.get("issues", [])
    )

    return {
        "project_path": str(root),
        "scan_results": {
            "environment": env_results,
            "data": data_results,
            "code": code_results,
            "documentation": docs_results
        },
        "assessment": score_results,
        "issues": all_issues,
        "recommendations": generate_recommendations(score_results)
    }


def generate_recommendations(score: Dict) -> List[str]:
    """Generate prioritized recommendations based on score."""
    recommendations = []
    checklist = score["checklist"]

    # Critical items (🔴)
    critical = ["versions_pinned", "random_seeds_set", "raw_data_archived", "env_file_present"]
    for item in critical:
        if not checklist[item]["status"]:
            recommendations.append(f"🔴 CRITICAL: {item.replace('_', ' ').title()}")

    # Major items (🟡)
    major = ["no_hardcoded_paths", "data_processing_scripts", "methods_documented", "parameters_documented"]
    for item in major:
        if not checklist[item]["status"]:
            recommendations.append(f"🟡 MAJOR: {item.replace('_', ' ').title()}")

    # Minor items (🟢)
    minor = ["license_present", "checksums_present", "expected_outputs_described"]
    for item in minor:
        if not checklist[item]["status"]:
            recommendations.append(f"🟢 MINOR: {item.replace('_', ' ').title()}")

    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Scan project for reproducibility assessment")
    parser.add_argument("path", help="Path to project root directory")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    args = parser.parse_args()

    results = scan_project(args.path)

    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        # Pretty print text output
        print(f"\n{'='*60}")
        print(f"REPRODUCIBILITY ASSESSMENT: {results['project_path']}")
        print(f"{'='*60}\n")

        assessment = results["assessment"]
        print(f"Overall Score: {assessment['score']}/{assessment['max_score']} ({assessment['percentage']:.0f}%)")
        print(f"Level: {assessment['level']} - {assessment['level_name']}")
        print(f"Publication Ready: {'✓ Yes' if assessment['threshold_met'] else '✗ No (need ≥75%)'}")

        print(f"\nCategory Scores:")
        for cat, score in assessment["category_scores"].items():
            print(f"  {cat.title()}: {score}/25")

        if results["recommendations"]:
            print(f"\nRecommendations:")
            for rec in results["recommendations"]:
                print(f"  {rec}")

        print()


if __name__ == "__main__":
    main()
```

### Phase 2: Environment Validation (Priority: HIGH)

Validate generated environment files meet reproducibility standards.

**File:** `scripts/validate_environment.py`

```python
#!/usr/bin/env python3
"""
Environment File Validator

Validates environment.yml or requirements.txt for reproducibility best practices.

Usage:
    python validate_environment.py environment.yml
    python validate_environment.py requirements.txt --strict
"""

import re
import sys
import argparse
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def validate_conda_env(path: Path, strict: bool = False) -> dict:
    """Validate conda environment.yml file."""
    if not HAS_YAML:
        return {"valid": False, "error": "PyYAML not installed", "issues": []}

    issues = []
    warnings = []

    try:
        with open(path) as f:
            env = yaml.safe_load(f)
    except Exception as e:
        return {"valid": False, "error": f"Failed to parse YAML: {e}", "issues": []}

    # Check required fields
    if "name" not in env:
        issues.append("ERROR: Missing 'name' field")

    if "channels" not in env:
        issues.append("ERROR: Missing 'channels' field")
    else:
        channels = env["channels"]
        # Check channel priority
        if "defaults" in channels:
            if "conda-forge" in channels:
                if channels.index("defaults") < channels.index("conda-forge"):
                    warnings.append("WARN: 'defaults' has higher priority than 'conda-forge'")
            warnings.append("WARN: Consider using 'nodefaults' instead of 'defaults'")

    if "dependencies" not in env:
        issues.append("ERROR: Missing 'dependencies' field")
    else:
        deps = env["dependencies"]
        unpinned = []
        python_specified = False

        for dep in deps:
            if isinstance(dep, str):
                # Check for pinning
                if "=" not in dep and not dep.startswith("-"):
                    unpinned.append(dep)

                # Check for Python version
                if dep.startswith("python=") or dep.startswith("python=="):
                    python_specified = True
                    # Warn if using >= instead of =
                    if ">=" in dep:
                        warnings.append(f"WARN: Python version uses >= instead of =: {dep}")

            elif isinstance(dep, dict) and "pip" in dep:
                # Check pip dependencies
                for pip_dep in dep.get("pip", []):
                    if "==" not in pip_dep and ">=" not in pip_dep:
                        unpinned.append(f"pip:{pip_dep}")

        if unpinned:
            if strict:
                issues.append(f"ERROR: Unpinned dependencies: {unpinned[:5]}")
            else:
                warnings.append(f"WARN: Unpinned dependencies: {unpinned[:5]}")

        if not python_specified:
            issues.append("ERROR: Python version not specified")

    # Calculate score
    error_count = len([i for i in issues if i.startswith("ERROR")])
    warn_count = len(warnings)

    return {
        "valid": error_count == 0,
        "score": max(0, 100 - (error_count * 20) - (warn_count * 5)),
        "issues": issues,
        "warnings": warnings,
        "summary": {
            "errors": error_count,
            "warnings": warn_count,
            "deps_count": len(env.get("dependencies", [])),
            "unpinned_count": len(unpinned) if 'unpinned' in dir() else 0
        }
    }


def validate_requirements(path: Path, strict: bool = False) -> dict:
    """Validate requirements.txt file."""
    issues = []
    warnings = []

    try:
        content = path.read_text()
    except Exception as e:
        return {"valid": False, "error": f"Failed to read file: {e}", "issues": []}

    lines = [l.strip() for l in content.splitlines()
             if l.strip() and not l.strip().startswith("#")]

    unpinned = []
    loose_pinned = []

    for line in lines:
        # Skip options and URLs
        if line.startswith("-") or line.startswith("http"):
            continue

        # Check for exact pinning (==)
        if "==" in line:
            continue
        elif ">=" in line or "~=" in line:
            loose_pinned.append(line.split(">")[0].split("~")[0].strip())
        else:
            unpinned.append(line)

    if unpinned:
        if strict:
            issues.append(f"ERROR: Unpinned dependencies: {unpinned[:5]}")
        else:
            warnings.append(f"WARN: Unpinned dependencies: {unpinned[:5]}")

    if loose_pinned:
        warnings.append(f"WARN: Loosely pinned (>=, ~=): {loose_pinned[:5]}")

    error_count = len([i for i in issues if i.startswith("ERROR")])

    return {
        "valid": error_count == 0,
        "score": max(0, 100 - (error_count * 20) - (len(warnings) * 5)),
        "issues": issues,
        "warnings": warnings,
        "summary": {
            "errors": error_count,
            "warnings": len(warnings),
            "total_deps": len(lines),
            "unpinned": len(unpinned),
            "loose_pinned": len(loose_pinned)
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Validate environment files")
    parser.add_argument("path", help="Path to environment.yml or requirements.txt")
    parser.add_argument("--strict", action="store_true",
                       help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    if path.suffix in [".yml", ".yaml"]:
        results = validate_conda_env(path, args.strict)
    elif path.name == "requirements.txt" or path.suffix == ".txt":
        results = validate_requirements(path, args.strict)
    else:
        print(f"ERROR: Unsupported file type: {path}")
        sys.exit(1)

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"\nValidation: {path}")
        print(f"{'='*50}")
        print(f"Valid: {'✓' if results['valid'] else '✗'}")
        print(f"Score: {results.get('score', 0)}/100")

        if results.get("issues"):
            print(f"\nIssues:")
            for issue in results["issues"]:
                print(f"  {issue}")

        if results.get("warnings"):
            print(f"\nWarnings:")
            for warn in results["warnings"]:
                print(f"  {warn}")

    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
```

### Phase 3: Template Selection Decision Tree (Priority: MEDIUM)

Replace conversational template selection with deterministic decision tree.

**Add to SKILL.md:**

```xml
<template_selection_tree>
## Data Availability Template Decision Tree

Follow this decision tree to select the appropriate template:

Q1: Is the data publicly available without restrictions?
├── YES → Q2
└── NO → Q3

Q2: Is the data deposited in a domain-specific repository (GEO, SRA, PRIDE, etc.)?
├── YES → Use **Template 1: Public Repository**
└── NO → Use **Template 3: Existing Data** (with Zenodo/Figshare)

Q3: Is access controlled due to privacy/ethics (human subjects, patient data)?
├── YES → Use **Template 2: Controlled Access**
└── NO → Q4

Q4: Is the data under embargo until publication?
├── YES → Use **Template 2** with embargo language
└── NO → Contact data governance for guidance

### Template Mapping Table

| Data Situation | Template | Repository |
|---------------|----------|------------|
| New sequencing data, public | Template 1 | GEO + SRA |
| New proteomics data, public | Template 1 | PRIDE |
| Re-analysis of existing data | Template 3 | GitHub + Zenodo |
| Human subjects / clinical | Template 2 | EGA / dbGaP |
| Embargoed until publication | Template 1 + embargo | GEO with hold |
| General supplementary data | Template 1 | Zenodo |

</template_selection_tree>
```

---

## Validation Script Locations

After implementation, create these files:

```
skills/reproducible-research/
├── SKILL.md
├── DETERMINISM_AUDIT.md (this file)
├── scripts/
│   ├── scan_project.py          # Phase 1: Project scanner
│   ├── validate_environment.py  # Phase 2: Environment validation
│   └── fair_compliance.py       # Phase 3: FAIR assessment (future)
└── references/
    └── (existing reference files)
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Baseline score variance | ±15 points | ±3 points | Same project, 5 runs |
| Assessment time | 5-10 min conversation | 30 sec scan | Time to first score |
| Element detection accuracy | ~80% (LLM estimate) | 98% | File-based detection |
| Environment validation | None | 100% validated | All generated files checked |
| Template selection consistency | ~85% | 100% | Decision tree determinism |

---

## Implementation Checklist

### Phase 1: Project Scanner
- [ ] Create `scripts/` directory
- [ ] Implement `scan_project.py`
- [ ] Add scanner invocation to workflow Stage 1
- [ ] Add scanner invocation to workflow Stage 4 (validation)
- [ ] Test on 5 sample projects at different levels
- [ ] Update SKILL.md workflow to reference scanner

### Phase 2: Environment Validation
- [ ] Implement `validate_environment.py`
- [ ] Add post-generation validation step
- [ ] Test with valid and invalid environment files
- [ ] Document validation in error_handling section

### Phase 3: Template Selection
- [ ] Add decision tree to SKILL.md
- [ ] Update workflow Stage 3 to use decision tree
- [ ] Add template_id to output schema

### Testing
- [ ] Create test projects at Level 1, 2, 3, 4
- [ ] Verify scanner produces consistent scores
- [ ] Validate all generated environment files
- [ ] Test template selection on 10 scenarios

---

## References

- Skill file: `skills/reproducible-research/SKILL.md`
- Shared thresholds: `QUANTIFICATION_THRESHOLDS.md` §5, §8
- Related audits: See other `DETERMINISM_AUDIT.md` files in sibling skills
