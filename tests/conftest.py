"""Shared test configuration for Archon test suite."""
import sys
from pathlib import Path

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))
sys.path.insert(0, str(ARCHON_ROOT))
