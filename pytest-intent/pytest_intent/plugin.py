"""Pytest plugin entry point.

Registered via the `pytest11` entry point in pyproject.toml. Pytest auto-discovers
this module on `pip install pytest-intent`.

Currently this module re-exports the fixtures defined in `meta_tests.py` so they're
available without manual imports. The actual meta-test functions still need to be
imported in a project's `tests/test_meta.py` (a thin one-liner) — pytest does not
collect tests from plugins automatically, only fixtures and hooks.

In a future v0.2, we may add a `pytest_collection_modifyitems` hook that auto-injects
the meta-tests into every session, eliminating the `tests/test_meta.py` file entirely.
For now, the manual import keeps things explicit.
"""

from __future__ import annotations

# Re-export fixtures so they're discoverable as plugin fixtures
from .meta_tests import intent_tests_dirs, intent_yaml_paths  # noqa: F401
