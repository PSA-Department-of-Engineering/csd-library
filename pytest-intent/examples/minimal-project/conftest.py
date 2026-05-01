"""Pytest fixtures for the minimal example project."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def pack_root() -> Path:
    """Project root — where intent.yaml lives. tests/ is a sibling."""
    return Path(__file__).resolve().parent
