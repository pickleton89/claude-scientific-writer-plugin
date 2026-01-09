#!/usr/bin/env python3
"""
Environment File Validator

Validates environment.yml or requirements.txt for reproducibility best practices.

Usage:
    python validate_environment.py environment.yml
    python validate_environment.py requirements.txt --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from .utils.schemas import EnvironmentValidationResult, ValidationSummary
except ImportError:
    from utils.schemas import EnvironmentValidationResult, ValidationSummary

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def validate_conda_env(path: Path, strict: bool = False) -> EnvironmentValidationResult:
    """Validate conda environment.yml file."""
    if not HAS_YAML:
        return EnvironmentValidationResult(
            valid=False,
            error="PyYAML not installed",
        )

    issues: list[str] = []
    warnings: list[str] = []
    unpinned: list[str] = []

    try:
        with open(path) as f:
            env = yaml.safe_load(f)
    except Exception as e:
        return EnvironmentValidationResult(
            valid=False,
            error=f"Failed to parse YAML: {e}",
        )

    if env is None:
        return EnvironmentValidationResult(
            valid=False,
            error="Empty or invalid YAML file",
        )

    # Check required fields
    if "name" not in env:
        issues.append("ERROR: Missing 'name' field")

    if "channels" not in env:
        issues.append("ERROR: Missing 'channels' field")
    else:
        channels = env["channels"]
        if "defaults" in channels:
            if "conda-forge" in channels:
                if channels.index("defaults") < channels.index("conda-forge"):
                    warnings.append("WARN: 'defaults' has higher priority than 'conda-forge'")
            warnings.append("WARN: Consider using 'nodefaults' instead of 'defaults'")

    deps_count = 0
    python_specified = False

    if "dependencies" not in env:
        issues.append("ERROR: Missing 'dependencies' field")
    else:
        deps = env["dependencies"]
        if deps:
            for dep in deps:
                if isinstance(dep, str):
                    deps_count += 1
                    if "=" not in dep and not dep.startswith("-"):
                        unpinned.append(dep)
                    if dep.startswith("python=") or dep.startswith("python=="):
                        python_specified = True
                        if ">=" in dep:
                            warnings.append(
                                f"WARN: Python version uses >= instead of =: {dep}"
                            )
                elif isinstance(dep, dict) and "pip" in dep:
                    for pip_dep in dep.get("pip", []):
                        deps_count += 1
                        if "==" not in pip_dep and ">=" not in pip_dep:
                            unpinned.append(f"pip:{pip_dep}")

            if unpinned:
                if strict:
                    issues.append(f"ERROR: Unpinned dependencies: {unpinned[:5]}")
                else:
                    warnings.append(f"WARN: Unpinned dependencies: {unpinned[:5]}")

            if not python_specified:
                issues.append("ERROR: Python version not specified")

    error_count = len([i for i in issues if i.startswith("ERROR")])
    warn_count = len(warnings)

    return EnvironmentValidationResult(
        valid=error_count == 0,
        score=max(0, 100 - (error_count * 20) - (warn_count * 5)),
        issues=issues,
        warnings=warnings,
        summary=ValidationSummary(
            errors=error_count,
            warnings=warn_count,
            deps_count=deps_count,
            unpinned_count=len(unpinned),
        ),
    )


def validate_requirements(path: Path, strict: bool = False) -> EnvironmentValidationResult:
    """Validate requirements.txt file."""
    issues: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except Exception as e:
        return EnvironmentValidationResult(
            valid=False,
            error=f"Failed to read file: {e}",
        )

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    unpinned: list[str] = []
    loose_pinned: list[str] = []

    for line in lines:
        # Skip options and URLs
        if line.startswith("-") or line.startswith("http"):
            continue

        # Check for exact pinning (==)
        if "==" in line:
            continue
        elif ">=" in line or "~=" in line:
            pkg_name = line.split(">")[0].split("~")[0].strip()
            loose_pinned.append(pkg_name)
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

    return EnvironmentValidationResult(
        valid=error_count == 0,
        score=max(0, 100 - (error_count * 20) - (len(warnings) * 5)),
        issues=issues,
        warnings=warnings,
        summary=ValidationSummary(
            errors=error_count,
            warnings=len(warnings),
            deps_count=len(lines),
            unpinned_count=len(unpinned),
            loose_pinned_count=len(loose_pinned),
        ),
    )


def validate_pyproject(path: Path, strict: bool = False) -> EnvironmentValidationResult:
    """Validate pyproject.toml file for reproducibility."""
    issues: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except Exception as e:
        return EnvironmentValidationResult(
            valid=False,
            error=f"Failed to read file: {e}",
        )

    unpinned: list[str] = []
    loose_pinned: list[str] = []
    deps_count = 0

    # Check for python version constraint
    python_specified = bool(re.search(r'requires-python\s*=', content))
    if not python_specified:
        issues.append("ERROR: Python version not specified (requires-python)")

    # Parse dependencies section
    deps_match = re.search(
        r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL
    )
    if deps_match:
        deps_section = deps_match.group(1)
        # Extract quoted strings
        deps = re.findall(r'"([^"]+)"', deps_section)
        deps_count = len(deps)

        for dep in deps:
            if "==" in dep:
                continue
            elif ">=" in dep or "~=" in dep or ">" in dep:
                pkg_name = re.split(r'[><=~]', dep)[0].strip()
                loose_pinned.append(pkg_name)
            else:
                # No version specifier at all
                unpinned.append(dep)

    if unpinned:
        if strict:
            issues.append(f"ERROR: Unpinned dependencies: {unpinned[:5]}")
        else:
            warnings.append(f"WARN: Unpinned dependencies: {unpinned[:5]}")

    if loose_pinned:
        warnings.append(f"WARN: Loosely pinned (>=, ~=, >): {loose_pinned[:5]}")

    error_count = len([i for i in issues if i.startswith("ERROR")])

    return EnvironmentValidationResult(
        valid=error_count == 0,
        score=max(0, 100 - (error_count * 20) - (len(warnings) * 5)),
        issues=issues,
        warnings=warnings,
        summary=ValidationSummary(
            errors=error_count,
            warnings=len(warnings),
            deps_count=deps_count,
            unpinned_count=len(unpinned),
            loose_pinned_count=len(loose_pinned),
        ),
    )


def validate_environment(
    path: Path | str, strict: bool = False
) -> EnvironmentValidationResult:
    """Validate any environment file type."""
    path = Path(path)

    if not path.exists():
        return EnvironmentValidationResult(
            valid=False,
            error=f"File not found: {path}",
        )

    if path.suffix in [".yml", ".yaml"]:
        return validate_conda_env(path, strict)
    elif path.name == "requirements.txt" or path.suffix == ".txt":
        return validate_requirements(path, strict)
    elif path.name == "pyproject.toml":
        return validate_pyproject(path, strict)
    else:
        return EnvironmentValidationResult(
            valid=False,
            error=f"Unsupported file type: {path}",
        )


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate environment files")
    parser.add_argument("path", help="Path to environment.yml, requirements.txt, or pyproject.toml")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    result = validate_environment(path, args.strict)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\nValidation: {path}")
        print("=" * 50)
        print(f"Valid: {'Yes' if result.valid else 'No'}")
        print(f"Score: {result.score}/100")

        if result.error:
            print(f"\nError: {result.error}")

        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  {issue}")

        if result.warnings:
            print("\nWarnings:")
            for warn in result.warnings:
                print(f"  {warn}")

        if result.summary:
            print("\nSummary:")
            print(f"  Dependencies: {result.summary.deps_count}")
            print(f"  Unpinned: {result.summary.unpinned_count}")
            if result.summary.loose_pinned_count > 0:
                print(f"  Loosely pinned: {result.summary.loose_pinned_count}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
