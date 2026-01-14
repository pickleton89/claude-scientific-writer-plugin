"""
Shared API utilities for OpenRouter-based skills.

Used by:
- generate-image
- scientific-schematics

This module provides unified API key loading, configuration, and request
handling for skills that interact with OpenRouter.

Usage:
    from shared.api_utils import get_api_config, make_openrouter_request, APIError

    # Get configuration (raises ValueError if key not found)
    config = get_api_config()

    # Make a request
    response = make_openrouter_request(
        config=config,
        model="google/gemini-3-pro-image-preview",
        messages=[{"role": "user", "content": "Generate an image"}],
        modalities=["image", "text"]
    )
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class APIConfig:
    """Configuration for OpenRouter API requests.

    Attributes:
        api_key: OpenRouter API key
        base_url: API base URL (default: OpenRouter)
        timeout: Request timeout in seconds
        referer: HTTP-Referer header for attribution
        title: X-Title header for OpenRouter dashboard
    """

    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 120
    referer: str = "https://github.com/scientific-writer"
    title: str = "Claude Scientific Writer"


class APIError(Exception):
    """OpenRouter API error with status code and detail.

    Attributes:
        status_code: HTTP status code from the response
        detail: Error message or detail from the API
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")


def load_api_key(
    explicit_key: Optional[str] = None,
    env_var: str = "OPENROUTER_API_KEY",
    search_dotenv: bool = True,
    max_parent_levels: int = 5,
    caller_file: Optional[str] = None,
) -> Optional[str]:
    """
    Load API key with priority order.

    Priority:
        1. Explicit parameter (if provided)
        2. Environment variable
        3. .env file search (walks up directory tree from cwd and caller location)

    Args:
        explicit_key: Directly provided API key (highest priority)
        env_var: Name of environment variable to check
        search_dotenv: Whether to search for .env files
        max_parent_levels: Maximum directory levels to search upward
        caller_file: Optional path to calling script (pass __file__) for
            script-location .env search. If not provided, only searches from cwd.

    Returns:
        API key string if found, None otherwise

    Example:
        # Search from both cwd and script location
        key = load_api_key(caller_file=__file__)
    """
    # Priority 1: Explicit parameter
    if explicit_key:
        return explicit_key

    # Priority 2: Environment variable
    env_key = os.environ.get(env_var)
    if env_key:
        return env_key

    # Priority 3: .env file search
    if search_dotenv:
        return _search_env_file(env_var, max_parent_levels, caller_file)

    return None


def _search_env_file(
    key_name: str, max_levels: int, caller_file: Optional[str] = None
) -> Optional[str]:
    """Search for API key in .env files up the directory tree.

    Tries python-dotenv first if available, falls back to manual parsing.
    Searches from current working directory, and optionally from the caller's
    script location if caller_file is provided.

    Args:
        key_name: Environment variable name to find
        max_levels: Maximum parent directories to search
        caller_file: Optional path to calling script for script-location search

    Returns:
        API key if found in any .env file, None otherwise
    """
    # Try using python-dotenv first (doesn't override existing env vars)
    key = _try_dotenv_load(key_name, max_levels, caller_file)
    if key:
        return key

    # Fall back to manual .env parsing
    return _manual_env_search(key_name, max_levels, caller_file)


def _try_dotenv_load(
    key_name: str, max_levels: int, caller_file: Optional[str] = None
) -> Optional[str]:
    """Try to load .env using python-dotenv library.

    Args:
        key_name: Environment variable name to find
        max_levels: Maximum parent directories to search
        caller_file: Optional path to calling script for script-location search

    Returns:
        API key if found after loading .env, None otherwise
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return None

    # Build list of starting directories to search from
    search_roots: List[Path] = [Path.cwd()]
    if caller_file:
        script_dir = Path(caller_file).resolve().parent
        if script_dir not in search_roots:
            search_roots.append(script_dir)

    # Search from each root directory
    for start_dir in search_roots:
        current = start_dir
        for _ in range(max_levels + 1):
            env_path = current / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=False)
                # Check if key is now available
                key = os.environ.get(key_name)
                if key:
                    return key
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent

    return None


def _manual_env_search(
    key_name: str, max_levels: int, caller_file: Optional[str] = None
) -> Optional[str]:
    """Manually search and parse .env files for API key.

    Used as fallback when python-dotenv is not installed.

    Args:
        key_name: Environment variable name to find
        max_levels: Maximum parent directories to search
        caller_file: Optional path to calling script for script-location search

    Returns:
        API key if found in any .env file, None otherwise
    """
    # Build list of starting directories to search from
    search_roots: List[Path] = [Path.cwd()]
    if caller_file:
        script_dir = Path(caller_file).resolve().parent
        if script_dir not in search_roots:
            search_roots.append(script_dir)

    # Search from each root directory
    for start_dir in search_roots:
        current = start_dir
        for _ in range(max_levels + 1):
            env_path = current / ".env"
            if env_path.exists():
                key = _parse_env_file(env_path, key_name)
                if key:
                    return key
            parent = current.parent
            if parent == current:
                break
            current = parent

    return None


def _parse_env_file(path: Path, key_name: str) -> Optional[str]:
    """Parse a .env file and extract a specific key value.

    Handles common .env formats:
        KEY=value
        KEY="quoted value"
        KEY='single quoted'

    Args:
        path: Path to .env file
        key_name: Key to extract

    Returns:
        Value if key found, None otherwise
    """
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Check for key match
                if line.startswith(f"{key_name}="):
                    value = line.split("=", 1)[1]
                    # Strip quotes (both single and double)
                    value = value.strip().strip('"').strip("'")
                    if value:
                        return value
    except (OSError, IOError):
        pass
    return None


def get_api_config(
    api_key: Optional[str] = None,
    env_var: str = "OPENROUTER_API_KEY",
    caller_file: Optional[str] = None,
    **overrides: Any,
) -> APIConfig:
    """
    Get API configuration, raising error if key not found.

    This is the primary entry point for obtaining API configuration.
    It will attempt to load the API key from multiple sources and
    raise a helpful error if not found.

    Args:
        api_key: Explicit API key (optional)
        env_var: Environment variable name to check
        caller_file: Optional path to calling script (pass __file__) for
            script-location .env search. If not provided, only searches from cwd.
        **overrides: Override default APIConfig values (base_url, timeout, etc.)

    Returns:
        APIConfig instance with loaded key and settings

    Raises:
        ValueError: If API key cannot be found in any location

    Example:
        # Search from both cwd and script location
        config = get_api_config(caller_file=__file__)
    """
    key = load_api_key(explicit_key=api_key, env_var=env_var, caller_file=caller_file)
    if not key:
        raise ValueError(
            f"{env_var} not found. Please either:\n"
            f"  1. Set the {env_var} environment variable\n"
            f"  2. Add {env_var} to your .env file\n"
            f"  3. Pass api_key parameter directly\n"
            f"Get your API key from: https://openrouter.ai/keys"
        )

    return APIConfig(api_key=key, **overrides)


def make_openrouter_request(
    config: APIConfig,
    model: str,
    messages: List[Dict[str, Any]],
    modalities: Optional[List[str]] = None,
    **extra_params: Any,
) -> Dict[str, Any]:
    """
    Make a request to OpenRouter API.

    Handles authentication, headers, and error extraction.

    Args:
        config: API configuration with key and settings
        model: OpenRouter model ID (e.g., "google/gemini-3-pro-image-preview")
        messages: List of message dictionaries for the chat completion
        modalities: Output modalities (e.g., ["image", "text"])
        **extra_params: Additional parameters to include in the request body

    Returns:
        Parsed JSON response from the API

    Raises:
        APIError: If the API returns a non-200 status code
        ImportError: If requests library is not installed
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests library not found. Install with: pip install requests"
        )

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.referer,
        "X-Title": config.title,
    }

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        **extra_params,
    }

    if modalities:
        payload["modalities"] = modalities

    response = requests.post(
        f"{config.base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=config.timeout,
    )

    if response.status_code != 200:
        error_detail = _extract_error(response)
        raise APIError(response.status_code, error_detail)

    return response.json()


def _extract_error(response: Any) -> str:
    """Extract error detail from API response.

    Attempts to parse JSON error format, falls back to raw text.

    Args:
        response: requests.Response object

    Returns:
        Error message string
    """
    try:
        data = response.json()
        if "error" in data:
            error = data["error"]
            if isinstance(error, dict):
                return error.get("message", str(error))
            return str(error)
        return response.text
    except Exception:
        return response.text
