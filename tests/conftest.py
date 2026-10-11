"""Global test configuration and fixtures."""

import os
from pathlib import Path
import tempfile
import pytest

# Ensure offscreen Qt platform for headless test execution
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture
def tmp_path():
    """Robust local temporary directory fixture avoiding Windows Temp symlink locks."""
    base_dir = Path("data/test_tmp")
    base_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base_dir) as td:
        yield Path(td)
