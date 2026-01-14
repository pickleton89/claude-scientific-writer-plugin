"""
Shared utilities for Claude Scientific Writer skills.

This package provides common functionality used across multiple skills,
reducing code duplication and ensuring consistent behavior.

Modules:
    api_utils: OpenRouter API configuration and request handling
"""

from .api_utils import (
    APIConfig,
    APIError,
    get_api_config,
    load_api_key,
    make_openrouter_request,
)

__all__ = [
    "APIConfig",
    "APIError",
    "get_api_config",
    "load_api_key",
    "make_openrouter_request",
]
