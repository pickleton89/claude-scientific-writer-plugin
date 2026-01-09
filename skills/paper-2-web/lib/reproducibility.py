"""Reproducibility manifest system for paper transformations.

This module provides tools for creating and verifying reproducibility manifests,
enabling deterministic verification that outputs match expected results.

Key features:
- Configuration snapshots with model versions and parameters
- Input/output hashing for integrity verification
- Environment capture for debugging
- Manifest comparison for regression testing
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


@dataclass
class ReproducibilityConfig:
    """Configuration for reproducible transformation runs.

    Attributes:
        model_version: Specific model version (e.g., "gpt-4-0613")
        temperature: LLM temperature setting
        seed: Random seed for deterministic outputs (if supported)
        max_refinement_iterations: Maximum refinement passes
        refinement_threshold: Quality threshold for stopping refinement
        paper2all_version: Version of Paper2All tool
        paper2all_commit: Git commit hash of Paper2All
        additional_params: Any additional parameters
    """

    model_version: str = "gpt-4o-2024-08-06"
    temperature: float = 0.0
    seed: int | None = 42
    max_refinement_iterations: int = 3
    refinement_threshold: float = 0.85
    paper2all_version: str = "1.2.0"
    paper2all_commit: str | None = None
    additional_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReproducibilityConfig:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class EnvironmentSnapshot:
    """Snapshot of the execution environment.

    Attributes:
        python_version: Python version string
        platform_system: Operating system name
        platform_release: OS release version
        platform_machine: Machine architecture
        cwd: Current working directory
        env_vars: Relevant environment variables (sanitized)
        packages: Installed package versions (key packages only)
    """

    python_version: str = ""
    platform_system: str = ""
    platform_release: str = ""
    platform_machine: str = ""
    cwd: str = ""
    env_vars: dict[str, str] = field(default_factory=dict)
    packages: dict[str, str] = field(default_factory=dict)

    @classmethod
    def capture(cls) -> EnvironmentSnapshot:
        """Capture current environment."""
        # Capture key environment variables (sanitized)
        safe_env_vars = {}
        for var in ["LANG", "LC_ALL", "TZ", "PATH"]:
            if var in os.environ:
                # Truncate PATH to avoid huge values
                value = os.environ[var]
                if var == "PATH":
                    value = value[:200] + "..." if len(value) > 200 else value
                safe_env_vars[var] = value

        # Capture key package versions
        packages = {}
        try:
            import importlib.metadata
            key_packages = [
                "openai", "anthropic", "aiohttp", "beautifulsoup4",
                "pillow", "pyyaml", "jsonschema",
            ]
            for pkg in key_packages:
                try:
                    packages[pkg] = importlib.metadata.version(pkg)
                except importlib.metadata.PackageNotFoundError:
                    pass
        except ImportError:
            pass

        return cls(
            python_version=sys.version,
            platform_system=platform.system(),
            platform_release=platform.release(),
            platform_machine=platform.machine(),
            cwd=os.getcwd(),
            env_vars=safe_env_vars,
            packages=packages,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReproducibilityManifest:
    """Complete manifest for reproducing transformation outputs.

    Attributes:
        version: Manifest schema version
        created_at: ISO timestamp of creation
        config: Transformation configuration
        input_hash: Hash of input directory
        input_files: Map of input filenames to hashes
        output_hashes: Map of component names to output hashes
        output_files: Detailed map of output files to hashes
        environment: Environment snapshot
        metadata: Additional metadata
    """

    version: str = "1.0"
    created_at: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    input_hash: str = ""
    input_files: dict[str, str] = field(default_factory=dict)
    output_hashes: dict[str, str] = field(default_factory=dict)
    output_files: dict[str, dict[str, str]] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReproducibilityManifest:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of a file.

    Args:
        path: Path to the file
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hex digest of the file hash
    """
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_directory(
    dir_path: Path,
    algorithm: str = "sha256",
    exclude_patterns: list[str] | None = None,
) -> str:
    """Compute hash of directory contents.

    Hashes all files in sorted order to ensure deterministic results.

    Args:
        dir_path: Path to directory
        algorithm: Hash algorithm
        exclude_patterns: Patterns to exclude (glob-style)

    Returns:
        Hex digest of combined directory hash
    """
    if exclude_patterns is None:
        exclude_patterns = ["*.pyc", "__pycache__", ".DS_Store", ".git"]

    hasher = hashlib.new(algorithm)

    for path in sorted(dir_path.rglob("*")):
        if path.is_file():
            # Check exclusions
            should_exclude = False
            for pattern in exclude_patterns:
                if path.match(pattern):
                    should_exclude = True
                    break
            if should_exclude:
                continue

            # Include relative path in hash for structure sensitivity
            rel_path = path.relative_to(dir_path)
            hasher.update(str(rel_path).encode())
            hasher.update(hash_file(path, algorithm).encode())

    return hasher.hexdigest()


def hash_directory_files(
    dir_path: Path,
    algorithm: str = "sha256",
    exclude_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Get individual file hashes for a directory.

    Args:
        dir_path: Path to directory
        algorithm: Hash algorithm
        exclude_patterns: Patterns to exclude

    Returns:
        Dictionary mapping relative paths to hashes
    """
    if exclude_patterns is None:
        exclude_patterns = ["*.pyc", "__pycache__", ".DS_Store", ".git"]

    file_hashes = {}

    for path in sorted(dir_path.rglob("*")):
        if path.is_file():
            should_exclude = False
            for pattern in exclude_patterns:
                if path.match(pattern):
                    should_exclude = True
                    break
            if should_exclude:
                continue

            rel_path = str(path.relative_to(dir_path))
            file_hashes[rel_path] = hash_file(path, algorithm)

    return file_hashes


def generate_manifest(
    config: ReproducibilityConfig,
    input_dir: Path,
    output_dir: Path,
    metadata: dict[str, Any] | None = None,
) -> ReproducibilityManifest:
    """Generate a reproducibility manifest for a transformation.

    Args:
        config: Transformation configuration
        input_dir: Path to input directory
        output_dir: Path to output directory
        metadata: Additional metadata to include

    Returns:
        Complete ReproducibilityManifest
    """
    # Capture environment
    env = EnvironmentSnapshot.capture()

    # Hash input
    input_hash = hash_directory(input_dir)
    input_files = hash_directory_files(input_dir)

    # Hash outputs by component
    output_hashes = {}
    output_files: dict[str, dict[str, str]] = {}

    for component in ["website", "poster", "video"]:
        component_dir = output_dir / component
        if component_dir.exists():
            output_hashes[component] = hash_directory(component_dir)
            output_files[component] = hash_directory_files(component_dir)

    return ReproducibilityManifest(
        version="1.0",
        created_at=datetime.now(timezone.utc).isoformat(),
        config=config.to_dict(),
        input_hash=input_hash,
        input_files=input_files,
        output_hashes=output_hashes,
        output_files=output_files,
        environment=env.to_dict(),
        metadata=metadata or {},
    )


def save_manifest(manifest: ReproducibilityManifest, output_path: Path) -> None:
    """Save manifest to JSON file.

    Args:
        manifest: Manifest to save
        output_path: Path for output file
    """
    with open(output_path, "w") as f:
        json.dump(manifest.to_dict(), f, indent=2)


def load_manifest(manifest_path: Path) -> ReproducibilityManifest:
    """Load manifest from JSON file.

    Args:
        manifest_path: Path to manifest file

    Returns:
        Loaded ReproducibilityManifest
    """
    with open(manifest_path) as f:
        data = json.load(f)
    return ReproducibilityManifest.from_dict(data)


@dataclass
class VerificationResult:
    """Result of manifest verification.

    Attributes:
        passed: Whether all checks passed
        input_match: Whether input hash matches
        output_matches: Per-component output match status
        mismatched_files: List of files with hash mismatches
        missing_files: List of expected files that are missing
        extra_files: List of unexpected files
        details: Additional verification details
    """

    passed: bool = True
    input_match: bool = True
    output_matches: dict[str, bool] = field(default_factory=dict)
    mismatched_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    extra_files: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def verify_reproduction(
    manifest_path: Path,
    output_dir: Path,
    input_dir: Path | None = None,
    strict: bool = False,
) -> VerificationResult:
    """Verify that outputs match a manifest.

    Args:
        manifest_path: Path to manifest file
        output_dir: Path to output directory to verify
        input_dir: Optional input directory to also verify
        strict: If True, fail on any file differences

    Returns:
        VerificationResult with match status
    """
    manifest = load_manifest(manifest_path)
    result = VerificationResult()

    # Verify input if provided
    if input_dir is not None:
        current_input_hash = hash_directory(input_dir)
        result.input_match = current_input_hash == manifest.input_hash
        if not result.input_match:
            result.passed = False
            result.details["input_hash_expected"] = manifest.input_hash
            result.details["input_hash_actual"] = current_input_hash

    # Verify outputs
    for component, expected_hash in manifest.output_hashes.items():
        component_dir = output_dir / component

        if not component_dir.exists():
            result.output_matches[component] = False
            result.missing_files.append(f"{component}/")
            result.passed = False
            continue

        actual_hash = hash_directory(component_dir)
        matches = actual_hash == expected_hash
        result.output_matches[component] = matches

        if not matches:
            result.passed = False

            # Check individual files for detailed mismatch info
            if component in manifest.output_files:
                expected_files = manifest.output_files[component]
                actual_files = hash_directory_files(component_dir)

                for filename, expected_hash in expected_files.items():
                    if filename not in actual_files:
                        result.missing_files.append(f"{component}/{filename}")
                    elif actual_files[filename] != expected_hash:
                        result.mismatched_files.append(f"{component}/{filename}")

                for filename in actual_files:
                    if filename not in expected_files:
                        result.extra_files.append(f"{component}/{filename}")

    return result


def format_verification_report(result: VerificationResult) -> str:
    """Format verification result as human-readable report.

    Args:
        result: VerificationResult to format

    Returns:
        Formatted string
    """
    lines = [
        "Reproduction Verification Report",
        "=" * 50,
        "",
        f"Status: {'PASSED' if result.passed else 'FAILED'}",
        f"Input match: {'Yes' if result.input_match else 'No'}",
        "",
        "Component Results:",
    ]

    for component, match in result.output_matches.items():
        status = "MATCH" if match else "MISMATCH"
        lines.append(f"  {component}: {status}")

    if result.mismatched_files:
        lines.append("")
        lines.append(f"Mismatched files ({len(result.mismatched_files)}):")
        for f in result.mismatched_files[:10]:
            lines.append(f"  - {f}")
        if len(result.mismatched_files) > 10:
            lines.append(f"  ... and {len(result.mismatched_files) - 10} more")

    if result.missing_files:
        lines.append("")
        lines.append(f"Missing files ({len(result.missing_files)}):")
        for f in result.missing_files[:10]:
            lines.append(f"  - {f}")

    if result.extra_files:
        lines.append("")
        lines.append(f"Extra files ({len(result.extra_files)}):")
        for f in result.extra_files[:10]:
            lines.append(f"  - {f}")

    return "\n".join(lines)


def compare_manifests(
    manifest1_path: Path,
    manifest2_path: Path,
) -> dict[str, Any]:
    """Compare two manifests to identify differences.

    Useful for debugging why reproductions differ.

    Args:
        manifest1_path: Path to first manifest
        manifest2_path: Path to second manifest

    Returns:
        Dictionary describing differences
    """
    m1 = load_manifest(manifest1_path)
    m2 = load_manifest(manifest2_path)

    differences = {
        "config_changes": {},
        "input_changed": m1.input_hash != m2.input_hash,
        "output_changes": {},
        "environment_changes": {},
    }

    # Compare configs
    for key in set(m1.config.keys()) | set(m2.config.keys()):
        v1 = m1.config.get(key)
        v2 = m2.config.get(key)
        if v1 != v2:
            differences["config_changes"][key] = {"old": v1, "new": v2}

    # Compare outputs
    for component in set(m1.output_hashes.keys()) | set(m2.output_hashes.keys()):
        h1 = m1.output_hashes.get(component)
        h2 = m2.output_hashes.get(component)
        if h1 != h2:
            differences["output_changes"][component] = {
                "hash_changed": True,
                "old_hash": h1,
                "new_hash": h2,
            }

    # Compare key environment items
    env_keys = ["python_version", "platform_system"]
    for key in env_keys:
        v1 = m1.environment.get(key)
        v2 = m2.environment.get(key)
        if v1 != v2:
            differences["environment_changes"][key] = {"old": v1, "new": v2}

    return differences


__all__ = [
    "ReproducibilityConfig",
    "EnvironmentSnapshot",
    "ReproducibilityManifest",
    "VerificationResult",
    "hash_file",
    "hash_directory",
    "hash_directory_files",
    "generate_manifest",
    "save_manifest",
    "load_manifest",
    "verify_reproduction",
    "format_verification_report",
    "compare_manifests",
]
