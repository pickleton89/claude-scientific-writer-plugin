"""Mermaid diagram rendering utilities.

Provides rendering backends for converting Mermaid syntax to image files
(PNG, SVG, PDF). Supports multiple backends with automatic detection and
graceful fallback.

Backends (in order of preference):
1. mermaid-cli (mmdc) - Recommended, highest quality, requires Node.js
2. mermaid-py - Pure Python, no external dependencies
3. kroki.io API - Fallback, requires internet connection

Usage:
    >>> from utils.mermaid_renderer import MermaidRenderer, render_mermaid
    >>> renderer = MermaidRenderer()
    >>> result = renderer.render(
    ...     "flowchart TD\\n    A --> B",
    ...     output_path="diagram.png"
    ... )
    >>> print(result.success, result.output_path)
    True diagram.png
"""

from __future__ import annotations

import base64
import hashlib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal


class RenderBackend(Enum):
    """Available rendering backends."""

    MMDC = "mmdc"  # mermaid-cli
    PYTHON = "python"  # mermaid-py
    API = "api"  # Online API (kroki.io)
    AUTO = "auto"  # Auto-detect best available


@dataclass
class RenderResult:
    """Result of a Mermaid rendering operation."""

    success: bool
    output_path: str | None
    backend_used: str
    error: str | None = None
    render_time_ms: float = 0.0
    mermaid_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "backend_used": self.backend_used,
            "error": self.error,
            "render_time_ms": self.render_time_ms,
            "mermaid_hash": self.mermaid_hash,
        }


@dataclass
class RenderConfig:
    """Configuration for Mermaid rendering."""

    output_format: Literal["png", "svg", "pdf"] = "png"
    width: int = 800
    height: int = 600
    background_color: str = "white"
    theme: Literal["default", "dark", "forest", "neutral", "base"] = "default"
    scale: float = 2.0  # For high-DPI output
    css_file: str | None = None
    puppeteer_config: str | None = None


class MermaidRenderer:
    """Renders Mermaid diagrams to image files.

    Supports multiple backends with automatic detection:
    1. mermaid-cli (mmdc) - Recommended, requires Node.js
    2. mermaid-py - Pure Python, limited features
    3. kroki.io API - Fallback, requires internet

    Example:
        >>> renderer = MermaidRenderer()
        >>> result = renderer.render(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     output_path="diagram.png"
        ... )
    """

    # Backend availability cache
    _backend_cache: dict[str, bool] = {}

    def __init__(
        self,
        backend: RenderBackend | str = RenderBackend.AUTO,
        config: RenderConfig | None = None,
    ):
        """Initialize renderer with specified backend.

        Args:
            backend: Rendering backend to use (auto, mmdc, python, api)
            config: Optional render configuration
        """
        if isinstance(backend, str):
            backend = RenderBackend(backend.lower())
        self.backend = backend
        self.config = config or RenderConfig()
        self._selected_backend: str | None = None

    def render(
        self,
        mermaid_code: str,
        output_path: str | Path,
        **config_overrides: Any,
    ) -> RenderResult:
        """Render Mermaid code to an image file.

        Args:
            mermaid_code: Valid Mermaid diagram code
            output_path: Path for output file
            **config_overrides: Override default config options

        Returns:
            RenderResult with success status and metadata
        """
        import time

        start_time = time.time()
        output_path = Path(output_path)

        # Merge config overrides
        config = RenderConfig(
            output_format=config_overrides.get(
                "output_format", self.config.output_format
            ),
            width=config_overrides.get("width", self.config.width),
            height=config_overrides.get("height", self.config.height),
            background_color=config_overrides.get(
                "background_color", self.config.background_color
            ),
            theme=config_overrides.get("theme", self.config.theme),
            scale=config_overrides.get("scale", self.config.scale),
            css_file=config_overrides.get("css_file", self.config.css_file),
            puppeteer_config=config_overrides.get(
                "puppeteer_config", self.config.puppeteer_config
            ),
        )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Compute hash for caching/reproducibility
        mermaid_hash = hashlib.sha256(mermaid_code.encode()).hexdigest()[:16]

        # Select backend
        backend_name = self._select_backend()
        if backend_name is None:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="none",
                error=self._no_backend_error_message(),
                mermaid_hash=mermaid_hash,
            )

        # Render with selected backend
        try:
            if backend_name == "mmdc":
                result = self._render_with_mmdc(mermaid_code, output_path, config)
            elif backend_name == "python":
                result = self._render_with_python(mermaid_code, output_path, config)
            elif backend_name == "api":
                result = self._render_with_api(mermaid_code, output_path, config)
            else:
                result = RenderResult(
                    success=False,
                    output_path=None,
                    backend_used=backend_name,
                    error=f"Unknown backend: {backend_name}",
                )
        except Exception as e:
            result = RenderResult(
                success=False,
                output_path=None,
                backend_used=backend_name,
                error=str(e),
            )

        # Add timing and hash
        result.render_time_ms = (time.time() - start_time) * 1000
        result.mermaid_hash = mermaid_hash

        return result

    def _select_backend(self) -> str | None:
        """Select the best available backend.

        Returns:
            Backend name or None if none available
        """
        if self._selected_backend:
            return self._selected_backend

        if self.backend == RenderBackend.AUTO:
            # Try backends in order of preference
            for backend_name in ["mmdc", "python", "api"]:
                if self.check_backend_available(backend_name):
                    self._selected_backend = backend_name
                    return backend_name
            return None
        else:
            backend_name = self.backend.value
            if self.check_backend_available(backend_name):
                self._selected_backend = backend_name
                return backend_name
            return None

    def check_backend_available(self, backend: str) -> bool:
        """Check if a rendering backend is available.

        Args:
            backend: Backend name (mmdc, python, api)

        Returns:
            True if backend is available and working
        """
        # Use cache
        if backend in self._backend_cache:
            return self._backend_cache[backend]

        available = False

        if backend == "mmdc":
            available = self._check_mmdc_available()
        elif backend == "python":
            available = self._check_python_available()
        elif backend == "api":
            available = self._check_api_available()

        self._backend_cache[backend] = available
        return available

    def _check_mmdc_available(self) -> bool:
        """Check if mermaid-cli (mmdc) is installed."""
        try:
            result = subprocess.run(
                ["mmdc", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _check_python_available(self) -> bool:
        """Check if mermaid-py is available."""
        try:
            import mermaid  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_api_available(self) -> bool:
        """Check if online API is reachable."""
        try:
            import urllib.request

            req = urllib.request.Request(
                "https://kroki.io/health",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def _render_with_mmdc(
        self,
        mermaid_code: str,
        output_path: Path,
        config: RenderConfig,
    ) -> RenderResult:
        """Render using mermaid-cli (mmdc).

        This is the recommended backend with highest quality output.
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".mmd",
            delete=False,
        ) as temp_input:
            temp_input.write(mermaid_code)
            temp_input_path = temp_input.name

        try:
            cmd = [
                "mmdc",
                "-i",
                temp_input_path,
                "-o",
                str(output_path),
                "-t",
                config.theme,
                "-b",
                config.background_color,
                "-w",
                str(config.width),
                "-H",
                str(config.height),
                "-s",
                str(config.scale),
            ]

            if config.css_file:
                cmd.extend(["-C", config.css_file])

            if config.puppeteer_config:
                cmd.extend(["-p", config.puppeteer_config])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return RenderResult(
                    success=False,
                    output_path=None,
                    backend_used="mmdc",
                    error=f"mmdc failed: {error_msg}",
                )

            if not output_path.exists():
                return RenderResult(
                    success=False,
                    output_path=None,
                    backend_used="mmdc",
                    error="Output file not created",
                )

            return RenderResult(
                success=True,
                output_path=str(output_path),
                backend_used="mmdc",
            )

        except subprocess.TimeoutExpired:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="mmdc",
                error="mmdc timed out after 60 seconds",
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_input_path)
            except OSError:
                pass

    def _render_with_python(
        self,
        mermaid_code: str,
        output_path: Path,
        config: RenderConfig,
    ) -> RenderResult:
        """Render using mermaid-py Python library.

        Simpler setup but may have limited features compared to mmdc.
        """
        try:
            import mermaid
            from mermaid.graph import Graph

            graph = Graph(title="diagram", script=mermaid_code)
            rendered = mermaid.Mermaid(graph)

            # mermaid-py outputs SVG by default
            svg_content = rendered.svg

            if config.output_format == "svg":
                with open(output_path, "w") as f:
                    f.write(svg_content)
            else:
                # For PNG/PDF, we need to convert SVG
                # Try using cairosvg if available
                try:
                    import cairosvg

                    if config.output_format == "png":
                        cairosvg.svg2png(
                            bytestring=svg_content.encode(),
                            write_to=str(output_path),
                            scale=config.scale,
                        )
                    elif config.output_format == "pdf":
                        cairosvg.svg2pdf(
                            bytestring=svg_content.encode(),
                            write_to=str(output_path),
                        )
                except ImportError:
                    # Fall back to saving as SVG
                    svg_path = output_path.with_suffix(".svg")
                    with open(svg_path, "w") as f:
                        f.write(svg_content)
                    return RenderResult(
                        success=True,
                        output_path=str(svg_path),
                        backend_used="python",
                        error=f"Saved as SVG (install cairosvg for {config.output_format})",
                    )

            return RenderResult(
                success=True,
                output_path=str(output_path),
                backend_used="python",
            )

        except ImportError as e:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="python",
                error=f"mermaid-py import error: {e}",
            )
        except Exception as e:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="python",
                error=f"Python rendering error: {e}",
            )

    def _render_with_api(
        self,
        mermaid_code: str,
        output_path: Path,
        config: RenderConfig,
    ) -> RenderResult:
        """Render using kroki.io online API.

        Fallback option that requires internet connection.
        """
        import urllib.error
        import urllib.request
        import zlib

        # Kroki expects zlib-compressed, base64 URL-safe encoded diagram code
        compressed = zlib.compress(mermaid_code.encode("utf-8"), level=9)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii")

        # Build API URL
        output_format = config.output_format
        if output_format == "pdf":
            output_format = "svg"  # Kroki doesn't support PDF directly

        url = f"https://kroki.io/mermaid/{output_format}/{encoded}"

        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()

            with open(output_path, "wb") as f:
                f.write(content)

            return RenderResult(
                success=True,
                output_path=str(output_path),
                backend_used="api",
            )

        except urllib.error.HTTPError as e:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="api",
                error=f"API error: HTTP {e.code} - {e.reason}",
            )
        except urllib.error.URLError as e:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="api",
                error=f"Network error: {e.reason}",
            )
        except Exception as e:
            return RenderResult(
                success=False,
                output_path=None,
                backend_used="api",
                error=f"API rendering error: {e}",
            )

    def _no_backend_error_message(self) -> str:
        """Generate helpful error message when no backend is available."""
        return (
            "No Mermaid rendering backend available.\n\n"
            "Please install one of the following:\n\n"
            "1. mermaid-cli (Recommended):\n"
            "   npm install -g @mermaid-js/mermaid-cli\n\n"
            "2. Python package:\n"
            "   pip install mermaid-py\n\n"
            "3. Ensure internet access for API fallback\n\n"
            "After installation, run: mmdc --version"
        )

    @staticmethod
    def install_instructions(backend: str) -> str:
        """Return installation instructions for a backend.

        Args:
            backend: Backend name (mmdc, python, api)

        Returns:
            Installation instructions string
        """
        instructions = {
            "mmdc": (
                "Install mermaid-cli (recommended):\n"
                "  npm install -g @mermaid-js/mermaid-cli\n\n"
                "Verify installation:\n"
                "  mmdc --version\n\n"
                "Requires Node.js 16+ installed."
            ),
            "python": (
                "Install mermaid-py:\n"
                "  pip install mermaid-py\n\n"
                "For PNG/PDF output, also install:\n"
                "  pip install cairosvg\n\n"
                "Note: cairosvg requires Cairo system library."
            ),
            "api": (
                "The API backend uses kroki.io and requires:\n"
                "  - Active internet connection\n"
                "  - No firewall blocking kroki.io\n\n"
                "Test connectivity:\n"
                "  curl https://kroki.io/health"
            ),
        }
        return instructions.get(backend, f"Unknown backend: {backend}")

    def get_available_backends(self) -> list[str]:
        """Get list of available backends on this system.

        Returns:
            List of available backend names
        """
        available = []
        for backend in ["mmdc", "python", "api"]:
            if self.check_backend_available(backend):
                available.append(backend)
        return available


def render_mermaid(
    mermaid_code: str,
    output_path: str | Path,
    output_format: Literal["png", "svg", "pdf"] = "png",
    theme: Literal["default", "dark", "forest", "neutral", "base"] = "default",
    width: int = 800,
    height: int = 600,
    scale: float = 2.0,
    background: str = "white",
    backend: str = "auto",
) -> RenderResult:
    """Convenience function to render Mermaid code to an image.

    This is a simpler interface for common use cases.

    Args:
        mermaid_code: Valid Mermaid diagram syntax
        output_path: Path for output file
        output_format: Output format (png, svg, pdf)
        theme: Mermaid theme
        width: Output width in pixels
        height: Output height in pixels
        scale: Scale factor for high-DPI
        background: Background color
        backend: Rendering backend (auto, mmdc, python, api)

    Returns:
        RenderResult with success status

    Example:
        >>> result = render_mermaid(
        ...     "flowchart TD\\n    A --> B",
        ...     "output.png"
        ... )
    """
    config = RenderConfig(
        output_format=output_format,
        width=width,
        height=height,
        background_color=background,
        theme=theme,
        scale=scale,
    )
    renderer = MermaidRenderer(backend=backend, config=config)
    return renderer.render(mermaid_code, output_path)


def validate_mermaid_syntax(mermaid_code: str) -> tuple[bool, str | None]:
    """Validate Mermaid syntax without rendering.

    Uses mmdc's dry-run capability if available, otherwise
    performs basic syntax checks.

    Args:
        mermaid_code: Mermaid code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Basic syntax validation
    code = mermaid_code.strip()
    if not code:
        return False, "Empty Mermaid code"

    # Check for valid diagram type declaration
    valid_starts = [
        "flowchart",
        "graph",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "erDiagram",
        "gantt",
        "pie",
        "mindmap",
        "timeline",
        "block-beta",
        "quadrantChart",
        "sankey-beta",
        "gitGraph",
        "journey",
        "requirementDiagram",
    ]

    first_line = code.split("\n")[0].strip().lower()
    has_valid_start = any(first_line.startswith(vs.lower()) for vs in valid_starts)

    if not has_valid_start:
        return (
            False,
            f"Invalid diagram type. Must start with one of: {', '.join(valid_starts)}",
        )

    # Check for balanced brackets
    brackets = {"[": "]", "{": "}", "(": ")"}
    stack = []
    for char in code:
        if char in brackets:
            stack.append(brackets[char])
        elif char in brackets.values():
            if not stack or stack.pop() != char:
                return False, f"Unbalanced bracket: {char}"

    if stack:
        return False, f"Unclosed brackets: {''.join(stack)}"

    # Try mmdc validation if available
    renderer = MermaidRenderer()
    if renderer.check_backend_available("mmdc"):
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".mmd",
            delete=False,
        ) as temp_input:
            temp_input.write(mermaid_code)
            temp_input_path = temp_input.name

        try:
            # Use mmdc to parse without rendering
            result = subprocess.run(
                ["mmdc", "-i", temp_input_path, "-o", os.devnull],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                error = result.stderr or result.stdout or "Syntax error"
                return False, f"Mermaid syntax error: {error}"
        except Exception:
            pass  # Fall through to success if mmdc fails
        finally:
            try:
                os.unlink(temp_input_path)
            except OSError:
                pass

    return True, None


def get_mermaid_version() -> str | None:
    """Get installed mermaid-cli version.

    Returns:
        Version string or None if not installed
    """
    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None
