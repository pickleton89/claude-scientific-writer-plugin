"""Tests for shared API utilities module.

Phase 3 Test Suite - Shared API Infrastructure
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_utils import (
    APIConfig,
    APIError,
    _parse_env_file,
    get_api_config,
    load_api_key,
    make_openrouter_request,
)


class TestAPIConfig:
    """Tests for APIConfig dataclass."""

    def test_api_config_creation_with_defaults(self):
        """Test creating APIConfig with required field and defaults."""
        config = APIConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.base_url == "https://openrouter.ai/api/v1"
        assert config.timeout == 120
        assert config.referer == "https://github.com/scientific-writer"
        assert config.title == "Claude Scientific Writer"

    def test_api_config_creation_with_overrides(self):
        """Test creating APIConfig with all fields overridden."""
        config = APIConfig(
            api_key="custom-key",
            base_url="https://custom.api/v1",
            timeout=60,
            referer="https://example.com",
            title="Custom Title",
        )
        assert config.api_key == "custom-key"
        assert config.base_url == "https://custom.api/v1"
        assert config.timeout == 60
        assert config.referer == "https://example.com"
        assert config.title == "Custom Title"


class TestAPIError:
    """Tests for APIError exception class."""

    def test_api_error_creation(self):
        """Test creating APIError with status and detail."""
        error = APIError(404, "Not found")
        assert error.status_code == 404
        assert error.detail == "Not found"
        assert str(error) == "API Error 404: Not found"

    def test_api_error_inherits_exception(self):
        """Test APIError is an Exception."""
        error = APIError(500, "Server error")
        assert isinstance(error, Exception)

    def test_api_error_can_be_raised(self):
        """Test APIError can be raised and caught."""
        with pytest.raises(APIError) as excinfo:
            raise APIError(401, "Unauthorized")
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Unauthorized"


class TestLoadApiKey:
    """Tests for load_api_key function."""

    def test_explicit_key_has_highest_priority(self):
        """Test explicit key parameter takes precedence."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"}):
            key = load_api_key(explicit_key="explicit-key")
            assert key == "explicit-key"

    def test_env_var_used_when_no_explicit_key(self):
        """Test environment variable is used when no explicit key."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"}):
            key = load_api_key()
            assert key == "env-key"

    def test_custom_env_var_name(self):
        """Test using custom environment variable name."""
        with patch.dict(os.environ, {"CUSTOM_API_KEY": "custom-env-key"}):
            key = load_api_key(env_var="CUSTOM_API_KEY")
            assert key == "custom-env-key"

    def test_returns_none_when_no_key_found(self):
        """Test returns None when no key can be found."""
        with patch.dict(os.environ, {}, clear=True):
            # Also disable .env file search for this test
            key = load_api_key(search_dotenv=False)
            assert key is None

    def test_search_dotenv_disabled(self):
        """Test .env file search can be disabled."""
        with patch.dict(os.environ, {}, clear=True):
            key = load_api_key(search_dotenv=False)
            assert key is None


class TestParseEnvFile:
    """Tests for _parse_env_file function."""

    def test_parse_simple_key_value(self):
        """Test parsing simple KEY=value format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENROUTER_API_KEY=test-key-123\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "test-key-123"

            os.unlink(f.name)

    def test_parse_double_quoted_value(self):
        """Test parsing KEY="quoted value" format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('OPENROUTER_API_KEY="quoted-key"\n')
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "quoted-key"

            os.unlink(f.name)

    def test_parse_single_quoted_value(self):
        """Test parsing KEY='quoted value' format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENROUTER_API_KEY='single-quoted-key'\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "single-quoted-key"

            os.unlink(f.name)

    def test_parse_skips_comments(self):
        """Test parsing skips comment lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("# This is a comment\n")
            f.write("OPENROUTER_API_KEY=real-key\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "real-key"

            os.unlink(f.name)

    def test_parse_skips_empty_lines(self):
        """Test parsing skips empty lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("\n")
            f.write("OPENROUTER_API_KEY=key-value\n")
            f.write("\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "key-value"

            os.unlink(f.name)

    def test_parse_returns_none_for_missing_key(self):
        """Test returns None if key not found in file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OTHER_KEY=other-value\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key is None

            os.unlink(f.name)

    def test_parse_returns_none_for_empty_value(self):
        """Test returns None if key has empty value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENROUTER_API_KEY=\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key is None

            os.unlink(f.name)

    def test_parse_nonexistent_file(self):
        """Test returns None for nonexistent file."""
        key = _parse_env_file(Path("/nonexistent/path/.env"), "OPENROUTER_API_KEY")
        assert key is None


class TestGetApiConfig:
    """Tests for get_api_config function."""

    def test_get_config_with_explicit_key(self):
        """Test getting config with explicit API key."""
        config = get_api_config(api_key="explicit-key")
        assert config.api_key == "explicit-key"
        assert isinstance(config, APIConfig)

    def test_get_config_from_env_var(self):
        """Test getting config from environment variable."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"}):
            config = get_api_config()
            assert config.api_key == "env-key"

    def test_get_config_raises_on_missing_key(self):
        """Test raises ValueError when no key found."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as excinfo:
                get_api_config(api_key=None)
            assert "OPENROUTER_API_KEY not found" in str(excinfo.value)
            assert "https://openrouter.ai/keys" in str(excinfo.value)

    def test_get_config_with_overrides(self):
        """Test getting config with additional overrides."""
        config = get_api_config(
            api_key="test-key",
            timeout=60,
            title="Custom Title",
        )
        assert config.api_key == "test-key"
        assert config.timeout == 60
        assert config.title == "Custom Title"

    def test_get_config_custom_env_var(self):
        """Test getting config with custom env var name."""
        with patch.dict(os.environ, {"MY_API_KEY": "custom-key"}):
            config = get_api_config(env_var="MY_API_KEY")
            assert config.api_key == "custom-key"


class TestMakeOpenrouterRequest:
    """Tests for make_openrouter_request function."""

    def test_successful_request(self):
        """Test successful API request."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "response"}}]
            }
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key")
            result = make_openrouter_request(
                config=config,
                model="google/gemini-3-pro-image-preview",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert result == {"choices": [{"message": {"content": "response"}}]}
            mock_post.assert_called_once()

    def test_request_with_modalities(self):
        """Test request includes modalities when provided."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key")
            make_openrouter_request(
                config=config,
                model="google/gemini-3-pro-image-preview",
                messages=[{"role": "user", "content": "Generate image"}],
                modalities=["image", "text"],
            )

            call_kwargs = mock_post.call_args.kwargs
            assert "modalities" in call_kwargs["json"]
            assert call_kwargs["json"]["modalities"] == ["image", "text"]

    def test_request_headers(self):
        """Test request includes correct headers."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response

            config = APIConfig(
                api_key="test-key",
                referer="https://test.com",
                title="Test App",
            )
            make_openrouter_request(
                config=config,
                model="test/model",
                messages=[],
            )

            call_kwargs = mock_post.call_args.kwargs
            headers = call_kwargs["headers"]
            assert headers["Authorization"] == "Bearer test-key"
            assert headers["Content-Type"] == "application/json"
            assert headers["HTTP-Referer"] == "https://test.com"
            assert headers["X-Title"] == "Test App"

    def test_request_with_extra_params(self):
        """Test request passes extra parameters."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key")
            make_openrouter_request(
                config=config,
                model="test/model",
                messages=[],
                temperature=0.7,
                max_tokens=1000,
            )

            call_kwargs = mock_post.call_args.kwargs
            payload = call_kwargs["json"]
            assert payload["temperature"] == 0.7
            assert payload["max_tokens"] == 1000

    def test_request_uses_config_timeout(self):
        """Test request uses timeout from config."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key", timeout=60)
            make_openrouter_request(
                config=config,
                model="test/model",
                messages=[],
            )

            call_kwargs = mock_post.call_args.kwargs
            assert call_kwargs["timeout"] == 60

    def test_api_error_on_non_200_status(self):
        """Test APIError raised on non-200 status code."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": {"message": "Unauthorized"}}
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            config = APIConfig(api_key="bad-key")
            with pytest.raises(APIError) as excinfo:
                make_openrouter_request(
                    config=config,
                    model="test/model",
                    messages=[],
                )
            assert excinfo.value.status_code == 401
            assert "Unauthorized" in excinfo.value.detail

    def test_api_error_extracts_error_message(self):
        """Test APIError extracts error message from response."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {"message": "Invalid model specified"}
            }
            mock_response.text = "Bad request"
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key")
            with pytest.raises(APIError) as excinfo:
                make_openrouter_request(
                    config=config,
                    model="invalid/model",
                    messages=[],
                )
            assert "Invalid model specified" in excinfo.value.detail

    def test_api_error_falls_back_to_text(self):
        """Test APIError falls back to response text if JSON parse fails."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response

            config = APIConfig(api_key="test-key")
            with pytest.raises(APIError) as excinfo:
                make_openrouter_request(
                    config=config,
                    model="test/model",
                    messages=[],
                )
            assert "Internal Server Error" in excinfo.value.detail


class TestIntegration:
    """Integration tests for api_utils module."""

    def test_full_workflow_with_explicit_key(self):
        """Test complete workflow with explicit API key."""
        # Get config
        config = get_api_config(api_key="test-key-123")

        # Verify config
        assert config.api_key == "test-key-123"
        assert config.base_url == "https://openrouter.ai/api/v1"
        assert isinstance(config, APIConfig)

    def test_load_key_from_temp_env_file(self):
        """Test loading API key from temporary .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("OPENROUTER_API_KEY=file-key-456\n")

            # Test _parse_env_file directly
            key = _parse_env_file(env_path, "OPENROUTER_API_KEY")
            assert key == "file-key-456"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_explicit_key_falls_through(self):
        """Test empty string explicit key falls through to env var."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"}):
            # Empty string is falsy, should fall through
            key = load_api_key(explicit_key="")
            assert key == "env-key"

    def test_none_explicit_key_falls_through(self):
        """Test None explicit key falls through to env var."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"}):
            key = load_api_key(explicit_key=None)
            assert key == "env-key"

    def test_parse_env_file_with_equals_in_value(self):
        """Test parsing .env file where value contains equals sign."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENROUTER_API_KEY=sk-key=with=equals\n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "sk-key=with=equals"

            os.unlink(f.name)

    def test_parse_env_file_with_leading_whitespace_in_line(self):
        """Test parsing .env file with leading whitespace in line.

        The current implementation strips whitespace from each line before
        checking for the key, so lines with leading whitespace will match.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("  OPENROUTER_API_KEY=trimmed-key  \n")
            f.flush()

            # Line is stripped, so "  OPENROUTER_API_KEY=..." becomes
            # "OPENROUTER_API_KEY=..." which matches
            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "trimmed-key"

            os.unlink(f.name)

    def test_parse_env_file_strips_value_whitespace(self):
        """Test parsing .env file strips whitespace from value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENROUTER_API_KEY=  spaced-value  \n")
            f.flush()

            key = _parse_env_file(Path(f.name), "OPENROUTER_API_KEY")
            assert key == "spaced-value"

            os.unlink(f.name)
