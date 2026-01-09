"""Test suite for paper-2-web deterministic utilities."""

import sys
from pathlib import Path

# Add lib to path for imports
TEST_DIR = Path(__file__).parent
SKILL_DIR = TEST_DIR.parent
LIB_DIR = SKILL_DIR / "lib"
sys.path.insert(0, str(SKILL_DIR))
