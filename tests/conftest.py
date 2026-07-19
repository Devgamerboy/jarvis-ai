"""Pytest fixtures for JARVIS tests."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def reset_registry():
    from jarvis.tools.registry import _registry
    _registry.clear()
    yield
    _registry.clear()


@pytest.fixture
def memory_dir(tmp_path):
    old = os.environ.get("MEMORY_DIR")
    os.environ["MEMORY_DIR"] = str(tmp_path / "memory")
    yield tmp_path / "memory"
    if old:
        os.environ["MEMORY_DIR"] = old
    else:
        os.environ.pop("MEMORY_DIR", None)
