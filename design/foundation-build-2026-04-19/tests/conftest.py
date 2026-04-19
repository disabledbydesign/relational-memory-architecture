"""pytest configuration for foundation build tests."""
import sys
from pathlib import Path

import pytest

# Add artifacts/ to sys.path so tests can import crystallization_schema etc.
sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate_interface import LocalFileSubstrate


@pytest.fixture
def substrate(tmp_path):
    """A fresh LocalFileSubstrate in a temporary directory."""
    return LocalFileSubstrate(tmp_path)
