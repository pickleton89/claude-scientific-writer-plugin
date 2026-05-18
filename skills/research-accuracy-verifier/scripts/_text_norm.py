"""Shared text-normalization utilities for Stage-1 artifact producers.

Centralizes the wrapper-stripping and normalization logic so
`parse_document.py` and `extract_reference_map.py` cannot drift —
identical char offsets are required for `document_inventory.json` and
`reference_map.json` to refer to the same text positions.

This is a private utility module (leading underscore). Other scripts
in this skill import via:

    sys.path.insert(0, str(Path(__file__).parent))
    from _text_norm import normalize_text, strip_document_wrapper
"""

from __future__ import annotations

import re
import unicodedata

# Strip outer <document>...</document> tags if present (LLM-emitted wrappers).
_DOCUMENT_WRAPPER = re.compile(
    r"^\s*<document>\s*\n(.*)\n\s*</document>\s*$",
    re.DOTALL,
)


def normalize_text(raw: str) -> str:
    """Apply the canonical normalization used for SHA-256 anchoring.

    Operations (in order):
      1. NFC unicode normalization.
      2. CRLF / CR → LF.
      3. Trailing whitespace stripped per line.
      4. Trailing blank lines removed (single trailing newline retained).

    Empty input returns "" (no trailing newline).
    """
    s = unicodedata.normalize("NFC", raw)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in s.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""


def strip_document_wrapper(raw: str) -> str:
    """Extract content from inside <document>...</document> if present.

    Idempotent — unwrapped text passes through unchanged.
    """
    m = _DOCUMENT_WRAPPER.match(raw)
    return m.group(1) if m else raw
