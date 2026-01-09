"""Tests for reproducibility module."""

import json
import tempfile
from pathlib import Path

import pytest
from lib.reproducibility import (
    ReproducibilityConfig,
    EnvironmentSnapshot,
    ReproducibilityManifest,
    VerificationResult,
    hash_file,
    hash_directory,
    hash_directory_files,
    generate_manifest,
    save_manifest,
    load_manifest,
    verify_reproduction,
    format_verification_report,
    compare_manifests,
)


class TestReproducibilityConfig:
    """Tests for ReproducibilityConfig dataclass."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = ReproducibilityConfig()
        assert config.temperature == 0.0
        assert config.seed == 42
        assert config.max_refinement_iterations == 3

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = ReproducibilityConfig(
            model_version="gpt-4-turbo",
            temperature=0.1,
            seed=123,
        )
        assert config.model_version == "gpt-4-turbo"
        assert config.temperature == 0.1
        assert config.seed == 123

    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = ReproducibilityConfig()
        d = config.to_dict()
        assert isinstance(d, dict)
        assert "model_version" in d
        assert "temperature" in d

    def test_config_from_dict(self):
        """Test configuration deserialization."""
        data = {
            "model_version": "test-model",
            "temperature": 0.5,
            "seed": 100,
        }
        config = ReproducibilityConfig.from_dict(data)
        assert config.model_version == "test-model"
        assert config.seed == 100


class TestEnvironmentSnapshot:
    """Tests for EnvironmentSnapshot dataclass."""

    def test_capture_environment(self):
        """Test environment capture."""
        env = EnvironmentSnapshot.capture()
        assert env.python_version != ""
        assert env.platform_system != ""
        assert env.cwd != ""

    def test_environment_to_dict(self):
        """Test environment serialization."""
        env = EnvironmentSnapshot.capture()
        d = env.to_dict()
        assert isinstance(d, dict)
        assert "python_version" in d


class TestHashFunctions:
    """Tests for hashing functions."""

    def test_hash_file(self):
        """Test file hashing."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            f.flush()
            path = Path(f.name)

        try:
            h = hash_file(path)
            assert isinstance(h, str)
            assert len(h) == 64  # SHA-256 hex digest length
        finally:
            path.unlink()

    def test_hash_file_deterministic(self):
        """Test that file hashing is deterministic."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            f.flush()
            path = Path(f.name)

        try:
            h1 = hash_file(path)
            h2 = hash_file(path)
            assert h1 == h2
        finally:
            path.unlink()

    def test_hash_file_different_content(self):
        """Test that different content produces different hashes."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f1:
            f1.write("content 1")
            f1.flush()
            path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f2:
            f2.write("content 2")
            f2.flush()
            path2 = Path(f2.name)

        try:
            h1 = hash_file(path1)
            h2 = hash_file(path2)
            assert h1 != h2
        finally:
            path1.unlink()
            path2.unlink()

    def test_hash_directory(self):
        """Test directory hashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content 1")
            (tmppath / "file2.txt").write_text("content 2")

            h = hash_directory(tmppath)
            assert isinstance(h, str)
            assert len(h) == 64

    def test_hash_directory_deterministic(self):
        """Test that directory hashing is deterministic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content 1")
            (tmppath / "file2.txt").write_text("content 2")

            h1 = hash_directory(tmppath)
            h2 = hash_directory(tmppath)
            assert h1 == h2

    def test_hash_directory_excludes_patterns(self):
        """Test that exclusion patterns work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file.txt").write_text("content")
            (tmppath / "file.pyc").write_text("bytecode")

            h_with = hash_directory(tmppath, exclude_patterns=[])
            h_without = hash_directory(tmppath, exclude_patterns=["*.pyc"])
            assert h_with != h_without

    def test_hash_directory_files(self):
        """Test getting individual file hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content 1")
            (tmppath / "file2.txt").write_text("content 2")

            file_hashes = hash_directory_files(tmppath)
            assert "file1.txt" in file_hashes
            assert "file2.txt" in file_hashes
            assert len(file_hashes) == 2


class TestManifest:
    """Tests for ReproducibilityManifest."""

    def test_manifest_creation(self):
        """Test manifest creation."""
        manifest = ReproducibilityManifest(
            version="1.0",
            created_at="2025-01-09T00:00:00Z",
            input_hash="abc123",
        )
        assert manifest.version == "1.0"
        assert manifest.input_hash == "abc123"

    def test_manifest_to_dict(self):
        """Test manifest serialization."""
        manifest = ReproducibilityManifest(
            version="1.0",
            input_hash="abc123",
        )
        d = manifest.to_dict()
        assert isinstance(d, dict)
        assert d["version"] == "1.0"

    def test_manifest_from_dict(self):
        """Test manifest deserialization."""
        data = {
            "version": "1.0",
            "created_at": "2025-01-09T00:00:00Z",
            "config": {},
            "input_hash": "abc123",
            "input_files": {},
            "output_hashes": {},
            "output_files": {},
            "environment": {},
            "metadata": {},
        }
        manifest = ReproducibilityManifest.from_dict(data)
        assert manifest.version == "1.0"
        assert manifest.input_hash == "abc123"


class TestGenerateManifest:
    """Tests for generate_manifest function."""

    def test_generate_manifest_basic(self):
        """Test basic manifest generation."""
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                input_path = Path(input_dir)
                output_path = Path(output_dir)

                # Create test input
                (input_path / "paper.tex").write_text("\\documentclass{article}")

                # Create test output
                (output_path / "website").mkdir()
                (output_path / "website" / "index.html").write_text("<html></html>")

                config = ReproducibilityConfig()
                manifest = generate_manifest(config, input_path, output_path)

                assert manifest.version == "1.0"
                assert manifest.input_hash != ""
                assert "website" in manifest.output_hashes

    def test_generate_manifest_with_metadata(self):
        """Test manifest generation with metadata."""
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                input_path = Path(input_dir)
                output_path = Path(output_dir)
                (input_path / "paper.tex").write_text("test")

                config = ReproducibilityConfig()
                metadata = {"paper_title": "Test Paper"}
                manifest = generate_manifest(config, input_path, output_path, metadata)

                assert manifest.metadata["paper_title"] == "Test Paper"


class TestSaveLoadManifest:
    """Tests for save_manifest and load_manifest functions."""

    def test_save_and_load_manifest(self):
        """Test saving and loading manifest."""
        manifest = ReproducibilityManifest(
            version="1.0",
            created_at="2025-01-09T00:00:00Z",
            input_hash="abc123",
            output_hashes={"website": "def456"},
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            save_manifest(manifest, path)
            loaded = load_manifest(path)
            assert loaded.version == manifest.version
            assert loaded.input_hash == manifest.input_hash
            assert loaded.output_hashes == manifest.output_hashes
        finally:
            path.unlink()

    def test_manifest_json_format(self):
        """Test that saved manifest is valid JSON."""
        manifest = ReproducibilityManifest(version="1.0", input_hash="test")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            save_manifest(manifest, path)
            with open(path) as f:
                data = json.load(f)
            assert data["version"] == "1.0"
        finally:
            path.unlink()


class TestVerifyReproduction:
    """Tests for verify_reproduction function."""

    def test_verify_matching_outputs(self):
        """Test verification with matching outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create input
            input_dir = tmppath / "input"
            input_dir.mkdir()
            (input_dir / "paper.tex").write_text("content")

            # Create output
            output_dir = tmppath / "output"
            (output_dir / "website").mkdir(parents=True)
            (output_dir / "website" / "index.html").write_text("<html></html>")

            # Generate manifest
            config = ReproducibilityConfig()
            manifest = generate_manifest(config, input_dir, output_dir)
            manifest_path = tmppath / "manifest.json"
            save_manifest(manifest, manifest_path)

            # Verify
            result = verify_reproduction(manifest_path, output_dir)
            assert result.passed is True
            assert result.output_matches.get("website") is True

    def test_verify_mismatched_outputs(self):
        """Test verification with mismatched outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create input
            input_dir = tmppath / "input"
            input_dir.mkdir()
            (input_dir / "paper.tex").write_text("content")

            # Create output
            output_dir = tmppath / "output"
            (output_dir / "website").mkdir(parents=True)
            (output_dir / "website" / "index.html").write_text("<html>v1</html>")

            # Generate manifest
            config = ReproducibilityConfig()
            manifest = generate_manifest(config, input_dir, output_dir)
            manifest_path = tmppath / "manifest.json"
            save_manifest(manifest, manifest_path)

            # Modify output
            (output_dir / "website" / "index.html").write_text("<html>v2</html>")

            # Verify
            result = verify_reproduction(manifest_path, output_dir)
            assert result.passed is False
            assert result.output_matches.get("website") is False


class TestFormatVerificationReport:
    """Tests for format_verification_report function."""

    def test_format_passing_report(self):
        """Test formatting passing report."""
        result = VerificationResult(
            passed=True,
            output_matches={"website": True},
        )
        report = format_verification_report(result)
        assert "PASSED" in report
        assert "website" in report

    def test_format_failing_report(self):
        """Test formatting failing report."""
        result = VerificationResult(
            passed=False,
            output_matches={"website": False},
            mismatched_files=["website/index.html"],
        )
        report = format_verification_report(result)
        assert "FAILED" in report
        assert "Mismatched" in report


class TestCompareManifests:
    """Tests for compare_manifests function."""

    def test_compare_identical_manifests(self):
        """Test comparing identical manifests."""
        manifest = ReproducibilityManifest(
            version="1.0",
            config={"temperature": 0.0},
            input_hash="abc123",
            output_hashes={"website": "def456"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            path1 = tmppath / "m1.json"
            path2 = tmppath / "m2.json"
            save_manifest(manifest, path1)
            save_manifest(manifest, path2)

            diff = compare_manifests(path1, path2)
            assert diff["input_changed"] is False
            assert len(diff["config_changes"]) == 0
            assert len(diff["output_changes"]) == 0

    def test_compare_different_manifests(self):
        """Test comparing different manifests."""
        m1 = ReproducibilityManifest(
            version="1.0",
            config={"temperature": 0.0},
            input_hash="abc123",
            output_hashes={"website": "def456"},
        )
        m2 = ReproducibilityManifest(
            version="1.0",
            config={"temperature": 0.5},
            input_hash="abc123",
            output_hashes={"website": "xyz789"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            path1 = tmppath / "m1.json"
            path2 = tmppath / "m2.json"
            save_manifest(m1, path1)
            save_manifest(m2, path2)

            diff = compare_manifests(path1, path2)
            assert "temperature" in diff["config_changes"]
            assert "website" in diff["output_changes"]


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_hash_deterministic(self):
        """Test that hashing is deterministic."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            path = Path(f.name)

        try:
            results = [hash_file(path) for _ in range(5)]
            assert all(r == results[0] for r in results)
        finally:
            path.unlink()

    def test_manifest_generation_deterministic(self):
        """Test that manifest generation is deterministic."""
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                input_path = Path(input_dir)
                output_path = Path(output_dir)
                (input_path / "paper.tex").write_text("test")
                (output_path / "website").mkdir()
                (output_path / "website" / "index.html").write_text("<html></html>")

                config = ReproducibilityConfig()
                m1 = generate_manifest(config, input_path, output_path)
                m2 = generate_manifest(config, input_path, output_path)

                assert m1.input_hash == m2.input_hash
                assert m1.output_hashes == m2.output_hashes
