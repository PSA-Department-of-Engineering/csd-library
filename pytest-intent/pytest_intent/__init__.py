"""pytest-intent — the @intent decorator that links a pytest test to a CSD claim.

Validation, coverage, and orphan-detection live in the separate `csd-intent`
tool (a standalone CLI), not here. This package is intentionally small: it
only exposes the marker; auditing is somebody else's job.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .decorator import intent

try:
    __version__ = version("pytest-intent")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__", "intent"]
