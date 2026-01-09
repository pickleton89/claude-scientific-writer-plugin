"""Tests for generation metadata logging utilities.

Phase 2 Test Suite - Core Infrastructure
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils.metadata import (
    GenerationMetadata,
    GenerationSession,
    append_generation_attempt,
    create_session,
    format_history,
    get_attempt_stats,
    get_latest_metadata,
    load_generation_history,
    load_session,
    log_generation,
    save_session,
)


class TestGenerationMetadata:
    """Tests for GenerationMetadata dataclass."""

    def test_creation_with_required_fields(self):
        """Test creating metadata with required fields only."""
        meta = GenerationMetadata(
            prompt="test prompt",
            model="test/model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
        )
        assert meta.prompt == "test prompt"
        assert meta.model == "test/model"
        assert meta.timestamp == "2026-01-09T12:00:00"
        assert meta.output_path == "/path/to/image.png"
        assert meta.attempt_number == 1
        assert meta.success is True
        assert meta.input_image is None
        assert meta.resolution is None

    def test_creation_with_all_fields(self):
        """Test creating metadata with all fields."""
        meta = GenerationMetadata(
            prompt="detailed prompt",
            model="test/model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            input_image="/path/to/input.png",
            attempt_number=3,
            resolution=(1024, 768),
            file_size_bytes=102400,
            success=True,
            error=None,
            prompt_analysis={"component_count": 4},
            validation_result={"tier": "target"},
            generation_params={"seed": 42},
        )
        assert meta.input_image == "/path/to/input.png"
        assert meta.attempt_number == 3
        assert meta.resolution == (1024, 768)
        assert meta.file_size_bytes == 102400
        assert meta.prompt_analysis == {"component_count": 4}
        assert meta.validation_result == {"tier": "target"}
        assert meta.generation_params == {"seed": 42}

    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        meta = GenerationMetadata(
            prompt="test",
            model="model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            resolution=(1024, 768),
        )
        d = meta.to_dict()
        assert isinstance(d, dict)
        assert d["prompt"] == "test"
        assert d["model"] == "model"
        assert d["resolution"] == (1024, 768)

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        d = {
            "prompt": "test",
            "model": "model",
            "timestamp": "2026-01-09T12:00:00",
            "output_path": "/path/to/image.png",
            "resolution": [1024, 768],  # JSON stores as list
            "attempt_number": 2,
            "success": True,
            "error": None,
            "input_image": None,
            "file_size_bytes": None,
            "prompt_analysis": None,
            "validation_result": None,
            "generation_params": {},
        }
        meta = GenerationMetadata.from_dict(d)
        assert meta.prompt == "test"
        assert meta.resolution == (1024, 768)  # Converted to tuple

    def test_from_dict_without_resolution(self):
        """Test from_dict handles missing resolution."""
        d = {
            "prompt": "test",
            "model": "model",
            "timestamp": "2026-01-09T12:00:00",
            "output_path": "/path/to/image.png",
            "attempt_number": 1,
            "success": True,
            "error": None,
            "input_image": None,
            "file_size_bytes": None,
            "prompt_analysis": None,
            "validation_result": None,
            "generation_params": {},
        }
        meta = GenerationMetadata.from_dict(d)
        assert meta.resolution is None

    def test_failed_generation(self):
        """Test metadata for failed generation."""
        meta = GenerationMetadata(
            prompt="test",
            model="model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            success=False,
            error="API rate limit exceeded",
        )
        assert meta.success is False
        assert meta.error == "API rate limit exceeded"


class TestGenerationSession:
    """Tests for GenerationSession dataclass."""

    def test_session_creation(self):
        """Test creating a generation session."""
        session = GenerationSession(
            session_id="20260109_120000",
            created_at="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            target_description="A scientific illustration",
        )
        assert session.session_id == "20260109_120000"
        assert session.target_description == "A scientific illustration"
        assert session.attempts == []
        assert session.total_attempts == 0
        assert session.successful is False

    def test_session_with_attempts(self):
        """Test session with multiple attempts."""
        attempt1 = GenerationMetadata(
            prompt="first try",
            model="model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
        )
        attempt2 = GenerationMetadata(
            prompt="second try",
            model="model",
            timestamp="2026-01-09T12:05:00",
            output_path="/path/to/image.png",
            attempt_number=2,
        )
        session = GenerationSession(
            session_id="20260109_120000",
            created_at="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            target_description="test",
            attempts=[attempt1, attempt2],
            total_attempts=2,
        )
        assert len(session.attempts) == 2
        assert session.total_attempts == 2

    def test_session_to_dict(self):
        """Test converting session to dictionary."""
        session = GenerationSession(
            session_id="20260109_120000",
            created_at="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            target_description="test",
        )
        d = session.to_dict()
        assert isinstance(d, dict)
        assert d["session_id"] == "20260109_120000"
        assert d["attempts"] == []

    def test_session_from_dict(self):
        """Test creating session from dictionary."""
        d = {
            "session_id": "20260109_120000",
            "created_at": "2026-01-09T12:00:00",
            "output_path": "/path/to/image.png",
            "target_description": "test",
            "attempts": [
                {
                    "prompt": "test",
                    "model": "model",
                    "timestamp": "2026-01-09T12:00:00",
                    "output_path": "/path/to/image.png",
                    "attempt_number": 1,
                    "success": True,
                    "error": None,
                    "input_image": None,
                    "file_size_bytes": None,
                    "prompt_analysis": None,
                    "validation_result": None,
                    "generation_params": {},
                }
            ],
            "final_model": None,
            "total_attempts": 1,
            "successful": False,
            "notes": "",
        }
        session = GenerationSession.from_dict(d)
        assert session.session_id == "20260109_120000"
        assert len(session.attempts) == 1
        assert isinstance(session.attempts[0], GenerationMetadata)


class TestLogGeneration:
    """Tests for log_generation function."""

    def test_log_creates_meta_file(self):
        """Test log_generation creates .meta.json file."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        try:
            meta_path = log_generation(
                output_path=image_path,
                prompt="test prompt",
                model="test/model",
            )
            assert Path(meta_path).exists()
            assert meta_path.endswith(".meta.json")

            # Verify contents
            with open(meta_path) as f:
                data = json.load(f)
            assert data["prompt"] == "test prompt"
            assert data["model"] == "test/model"
        finally:
            Path(image_path).unlink(missing_ok=True)
            Path(meta_path).unlink(missing_ok=True)

    def test_log_with_all_parameters(self):
        """Test log_generation with all parameters."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        try:
            meta_path = log_generation(
                output_path=image_path,
                prompt="detailed prompt",
                model="test/model",
                input_image="/path/to/input.png",
                attempt_number=2,
                success=True,
                prompt_analysis={"component_count": 4},
                validation_result={"tier": "target"},
                generation_params={"seed": 42},
            )

            with open(meta_path) as f:
                data = json.load(f)
            assert data["input_image"] == "/path/to/input.png"
            assert data["attempt_number"] == 2
            assert data["prompt_analysis"] == {"component_count": 4}
            assert data["generation_params"] == {"seed": 42}
        finally:
            Path(image_path).unlink(missing_ok=True)
            Path(meta_path).unlink(missing_ok=True)

    def test_log_failed_generation(self):
        """Test logging failed generation."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        try:
            meta_path = log_generation(
                output_path=image_path,
                prompt="test",
                model="test/model",
                success=False,
                error="API error",
            )

            with open(meta_path) as f:
                data = json.load(f)
            assert data["success"] is False
            assert data["error"] == "API error"
        finally:
            Path(image_path).unlink(missing_ok=True)
            Path(meta_path).unlink(missing_ok=True)


class TestAppendGenerationAttempt:
    """Tests for append_generation_attempt function."""

    def test_append_creates_new_history(self):
        """Test append creates new history if none exists."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            append_generation_attempt(
                output_path=image_path,
                prompt="first attempt",
                model="test/model",
            )

            with open(meta_path) as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["attempt_number"] == 1
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def test_append_increments_attempt_number(self):
        """Test append increments attempt number."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            append_generation_attempt(
                output_path=image_path,
                prompt="first",
                model="test/model",
            )
            append_generation_attempt(
                output_path=image_path,
                prompt="second",
                model="test/model",
            )
            append_generation_attempt(
                output_path=image_path,
                prompt="third",
                model="test/model",
            )

            with open(meta_path) as f:
                data = json.load(f)
            assert len(data) == 3
            assert data[0]["attempt_number"] == 1
            assert data[1]["attempt_number"] == 2
            assert data[2]["attempt_number"] == 3
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def test_append_preserves_history(self):
        """Test append preserves existing history."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            append_generation_attempt(
                output_path=image_path,
                prompt="first prompt",
                model="model1",
            )
            append_generation_attempt(
                output_path=image_path,
                prompt="second prompt",
                model="model2",
            )

            with open(meta_path) as f:
                data = json.load(f)
            assert data[0]["prompt"] == "first prompt"
            assert data[0]["model"] == "model1"
            assert data[1]["prompt"] == "second prompt"
            assert data[1]["model"] == "model2"
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)


class TestLoadGenerationHistory:
    """Tests for load_generation_history function."""

    def test_load_nonexistent_returns_empty(self):
        """Test loading nonexistent file returns empty list."""
        history = load_generation_history("/nonexistent/path/image.png")
        assert history == []

    def test_load_single_entry(self):
        """Test loading single entry file."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            # Write single entry (old format)
            with open(meta_path, "w") as f:
                json.dump(
                    {
                        "prompt": "test",
                        "model": "model",
                        "timestamp": "2026-01-09T12:00:00",
                        "output_path": image_path,
                        "attempt_number": 1,
                        "success": True,
                        "error": None,
                        "input_image": None,
                        "file_size_bytes": None,
                        "prompt_analysis": None,
                        "validation_result": None,
                        "generation_params": {},
                    },
                    f,
                )

            history = load_generation_history(image_path)
            assert len(history) == 1
            assert history[0].prompt == "test"
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def test_load_array_format(self):
        """Test loading array format file."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            # Write array format
            with open(meta_path, "w") as f:
                json.dump(
                    [
                        {
                            "prompt": "first",
                            "model": "model",
                            "timestamp": "2026-01-09T12:00:00",
                            "output_path": image_path,
                            "attempt_number": 1,
                            "success": True,
                            "error": None,
                            "input_image": None,
                            "file_size_bytes": None,
                            "prompt_analysis": None,
                            "validation_result": None,
                            "generation_params": {},
                        },
                        {
                            "prompt": "second",
                            "model": "model",
                            "timestamp": "2026-01-09T12:05:00",
                            "output_path": image_path,
                            "attempt_number": 2,
                            "success": True,
                            "error": None,
                            "input_image": None,
                            "file_size_bytes": None,
                            "prompt_analysis": None,
                            "validation_result": None,
                            "generation_params": {},
                        },
                    ],
                    f,
                )

            history = load_generation_history(image_path)
            assert len(history) == 2
            assert history[0].prompt == "first"
            assert history[1].prompt == "second"
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def test_load_invalid_json_returns_empty(self):
        """Test loading invalid JSON returns empty list."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            with open(meta_path, "w") as f:
                f.write("not valid json")

            history = load_generation_history(image_path)
            assert history == []
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)


class TestGetLatestMetadata:
    """Tests for get_latest_metadata function."""

    def test_get_latest_returns_last(self):
        """Test get_latest returns last entry."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        meta_path = Path(image_path).with_suffix(".meta.json")

        try:
            append_generation_attempt(
                output_path=image_path,
                prompt="first",
                model="model1",
            )
            append_generation_attempt(
                output_path=image_path,
                prompt="second",
                model="model2",
            )

            latest = get_latest_metadata(image_path)
            assert latest is not None
            assert latest.prompt == "second"
            assert latest.attempt_number == 2
        finally:
            Path(image_path).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def test_get_latest_nonexistent_returns_none(self):
        """Test get_latest on nonexistent file returns None."""
        latest = get_latest_metadata("/nonexistent/image.png")
        assert latest is None


class TestCreateSession:
    """Tests for create_session function."""

    def test_create_session_basic(self):
        """Test creating a basic session."""
        session = create_session(
            output_path="/path/to/image.png",
            target_description="A scientific illustration",
        )
        assert session.output_path == "/path/to/image.png"
        assert session.target_description == "A scientific illustration"
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.attempts == []

    def test_create_session_with_notes(self):
        """Test creating session with notes."""
        session = create_session(
            output_path="/path/to/image.png",
            target_description="test",
            notes="This is a test session",
        )
        assert session.notes == "This is a test session"


class TestSaveAndLoadSession:
    """Tests for save_session and load_session functions."""

    def test_save_and_load_roundtrip(self):
        """Test saving and loading session preserves data."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        session_path = str(Path(image_path).with_suffix(".session.json"))

        try:
            session = create_session(
                output_path=image_path,
                target_description="Test session",
                notes="Test notes",
            )

            saved_path = save_session(session)
            assert Path(saved_path).exists()

            loaded = load_session(saved_path)
            assert loaded is not None
            assert loaded.target_description == "Test session"
            assert loaded.notes == "Test notes"
        finally:
            Path(image_path).unlink(missing_ok=True)
            Path(session_path).unlink(missing_ok=True)

    def test_load_nonexistent_returns_none(self):
        """Test loading nonexistent session returns None."""
        session = load_session("/nonexistent/session.json")
        assert session is None

    def test_save_to_custom_path(self):
        """Test saving session to custom path."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            custom_path = f.name

        try:
            session = create_session(
                output_path="/path/to/image.png",
                target_description="test",
            )

            saved_path = save_session(session, path=custom_path)
            assert saved_path == custom_path
            assert Path(custom_path).exists()
        finally:
            Path(custom_path).unlink(missing_ok=True)


class TestFormatHistory:
    """Tests for format_history function."""

    def test_format_empty_history(self):
        """Test formatting empty history."""
        result = format_history([])
        assert "No generation history found" in result

    def test_format_single_entry(self):
        """Test formatting single entry."""
        history = [
            GenerationMetadata(
                prompt="test prompt",
                model="test/model",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
                resolution=(1024, 768),
                file_size_bytes=102400,
            )
        ]
        result = format_history(history)
        assert "Attempt 1" in result
        assert "test/model" in result
        assert "1024x768" in result

    def test_format_multiple_entries(self):
        """Test formatting multiple entries."""
        history = [
            GenerationMetadata(
                prompt="first",
                model="model1",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
            ),
            GenerationMetadata(
                prompt="second",
                model="model2",
                timestamp="2026-01-09T12:05:00",
                output_path="/path/to/image.png",
                attempt_number=2,
            ),
        ]
        result = format_history(history)
        assert "2 attempts" in result
        assert "Attempt 1" in result
        assert "Attempt 2" in result

    def test_format_includes_error(self):
        """Test formatting includes error message."""
        history = [
            GenerationMetadata(
                prompt="test",
                model="model",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
                success=False,
                error="API error occurred",
            )
        ]
        result = format_history(history)
        assert "API error occurred" in result

    def test_format_truncates_long_prompt(self):
        """Test formatting truncates long prompts."""
        long_prompt = "a" * 200
        history = [
            GenerationMetadata(
                prompt=long_prompt,
                model="model",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
            )
        ]
        result = format_history(history)
        assert "..." in result
        assert len(result) < len(long_prompt) + 500


class TestGetAttemptStats:
    """Tests for get_attempt_stats function."""

    def test_stats_empty_history(self):
        """Test stats for empty history."""
        stats = get_attempt_stats([])
        assert stats["total_attempts"] == 0
        assert stats["successful_attempts"] == 0
        assert stats["failed_attempts"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["models_used"] == []
        assert stats["avg_file_size_kb"] is None

    def test_stats_all_successful(self):
        """Test stats with all successful attempts."""
        history = [
            GenerationMetadata(
                prompt="test1",
                model="model1",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
                file_size_bytes=102400,
                success=True,
            ),
            GenerationMetadata(
                prompt="test2",
                model="model2",
                timestamp="2026-01-09T12:05:00",
                output_path="/path/to/image.png",
                file_size_bytes=204800,
                success=True,
                attempt_number=2,
            ),
        ]
        stats = get_attempt_stats(history)
        assert stats["total_attempts"] == 2
        assert stats["successful_attempts"] == 2
        assert stats["failed_attempts"] == 0
        assert stats["success_rate"] == 1.0
        assert len(stats["models_used"]) == 2
        assert stats["avg_file_size_kb"] == pytest.approx(150.0)

    def test_stats_mixed_results(self):
        """Test stats with mixed success/failure."""
        history = [
            GenerationMetadata(
                prompt="test1",
                model="model",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
                success=True,
            ),
            GenerationMetadata(
                prompt="test2",
                model="model",
                timestamp="2026-01-09T12:05:00",
                output_path="/path/to/image.png",
                success=False,
                error="Failed",
                attempt_number=2,
            ),
        ]
        stats = get_attempt_stats(history)
        assert stats["total_attempts"] == 2
        assert stats["successful_attempts"] == 1
        assert stats["failed_attempts"] == 1
        assert stats["success_rate"] == 0.5

    def test_stats_unique_models(self):
        """Test stats counts unique models."""
        history = [
            GenerationMetadata(
                prompt="test1",
                model="model1",
                timestamp="2026-01-09T12:00:00",
                output_path="/path/to/image.png",
            ),
            GenerationMetadata(
                prompt="test2",
                model="model1",  # Same model
                timestamp="2026-01-09T12:05:00",
                output_path="/path/to/image.png",
                attempt_number=2,
            ),
        ]
        stats = get_attempt_stats(history)
        assert len(stats["models_used"]) == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_metadata_with_none_values(self):
        """Test metadata handles None values correctly."""
        meta = GenerationMetadata(
            prompt="test",
            model="model",
            timestamp="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            resolution=None,
            file_size_bytes=None,
            prompt_analysis=None,
        )
        d = meta.to_dict()
        assert d["resolution"] is None
        assert d["file_size_bytes"] is None

    def test_log_nonexistent_image_path(self):
        """Test logging with nonexistent image path still works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "nonexistent.png"
            meta_path = log_generation(
                output_path=str(image_path),
                prompt="test",
                model="model",
            )
            assert Path(meta_path).exists()
            Path(meta_path).unlink()

    def test_session_serialization_with_complex_attempts(self):
        """Test session serialization with complex attempt data."""
        session = GenerationSession(
            session_id="test",
            created_at="2026-01-09T12:00:00",
            output_path="/path/to/image.png",
            target_description="test",
            attempts=[
                GenerationMetadata(
                    prompt="test",
                    model="model",
                    timestamp="2026-01-09T12:00:00",
                    output_path="/path/to/image.png",
                    prompt_analysis={"nested": {"data": True}},
                    generation_params={"list": [1, 2, 3]},
                )
            ],
        )

        d = session.to_dict()
        reconstructed = GenerationSession.from_dict(d)
        assert reconstructed.attempts[0].prompt_analysis == {"nested": {"data": True}}
        assert reconstructed.attempts[0].generation_params == {"list": [1, 2, 3]}
