"""pytest-intent - Python+pytest implementation of CSD's Intent Specification annotation pattern."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .coverage import collect_annotated_tests, coverage_violations
from .decorator import intent
from .schema import (
    REQUIRED_FIELDS,
    VALID_CRITICALITY,
    VALID_SCOPE,
    check_schema,
    parse_intent_yaml,
)

try:
    __version__ = version("pytest-intent")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "REQUIRED_FIELDS",
    "VALID_CRITICALITY",
    "VALID_SCOPE",
    "__version__",
    "check_schema",
    "collect_annotated_tests",
    "coverage_violations",
    "intent",
    "parse_intent_yaml",
]
