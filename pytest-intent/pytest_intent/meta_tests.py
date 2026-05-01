"""Reusable meta-test functions for pytest-intent projects.

Drop-in usage in any project's `tests/test_meta.py`:

    from pytest_intent.meta_tests import test_intent_schema, test_intent_coverage  # noqa: F401

Both meta-tests use override-able fixtures so projects can layout intent specs and
tests across multiple files / directories. Defaults assume the simple case:
  - intent.yaml at pack_root
  - tests/ at pack_root

Override paths via fixtures in your conftest.py for multi-file / multi-dir layouts:
    @pytest.fixture
    def intent_yaml_paths(pack_root):
        return [pack_root / "intent" / "users.yaml", pack_root / "intent" / "permissions.yaml"]

    @pytest.fixture
    def intent_tests_dirs(pack_root):
        return [pack_root / "src" / "users" / "tests", pack_root / "src" / "auth" / "tests"]
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .coverage import collect_annotated_tests, coverage_violations
from .schema import check_schema, parse_intent_yaml


@pytest.fixture
def intent_yaml_paths(pack_root: Path) -> list[Path]:
    """Default: single intent.yaml at pack_root. Override for multi-file layouts."""
    return [pack_root / "intent.yaml"]


@pytest.fixture
def intent_tests_dirs(pack_root: Path) -> list[Path]:
    """Default: single tests/ dir at pack_root. Override for multi-dir layouts."""
    return [pack_root / "tests"]


def _merged_claims(paths: list[Path]) -> dict[str, dict[str, object]]:
    """Union claims across all intent.yaml sources. On key collision, later wins."""
    out: dict[str, dict[str, object]] = {}
    for p in paths:
        if not p.exists():
            continue
        out.update(parse_intent_yaml(p))
    return out


def _merged_annotated(dirs: list[Path]) -> dict[str, list[str]]:
    """Union @intent-annotated tests across all test directories."""
    out: dict[str, list[str]] = {}
    for d in dirs:
        for cid, refs in collect_annotated_tests(d).items():
            out.setdefault(cid, []).extend(refs)
    return out


def test_intent_schema(intent_yaml_paths: list[Path]) -> None:
    """Every claim across all intent.yaml sources conforms to schema."""
    claims = _merged_claims(intent_yaml_paths)
    if not claims:
        return  # nothing declared yet
    violations = check_schema(claims)
    assert not violations, "intent.yaml schema violations:\n" + "\n".join("  " + v for v in violations)


def test_intent_coverage(intent_yaml_paths: list[Path], intent_tests_dirs: list[Path]) -> None:
    """Every claim has ≥1 @intent-decorated test; every annotated test references a real claim."""
    claims = _merged_claims(intent_yaml_paths)
    if not claims:
        return
    annotated = _merged_annotated(intent_tests_dirs)
    violations = coverage_violations(claims, annotated)
    assert not violations, "intent ↔ test coverage violations:\n" + "\n".join("  " + v for v in violations)
