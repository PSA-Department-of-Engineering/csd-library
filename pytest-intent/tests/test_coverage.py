"""Tests for AST-based coverage walking."""

from __future__ import annotations

from pytest_intent import collect_annotated_tests, coverage_violations


def test_collect_finds_single_decorator(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text(
        '''
from pytest_intent import intent

@intent("INT-001")
def test_thing():
    assert True
''',
        encoding="utf-8",
    )
    found = collect_annotated_tests(tests_dir)
    assert "INT-001" in found
    assert found["INT-001"] == ["tests/test_a.py::test_thing"]


def test_collect_finds_multi_claim_decorator(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_b.py").write_text(
        '''
from pytest_intent import intent

@intent("INT-001", "INT-002")
def test_thing():
    pass
''',
        encoding="utf-8",
    )
    found = collect_annotated_tests(tests_dir)
    assert found["INT-001"] == ["tests/test_b.py::test_thing"]
    assert found["INT-002"] == ["tests/test_b.py::test_thing"]


def test_collect_handles_module_with_syntax_error(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_broken.py").write_text("def test_x(:\n    pass\n", encoding="utf-8")
    # Should not raise
    found = collect_annotated_tests(tests_dir)
    assert found == {}


def test_collect_skips_undecorated_tests(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text(
        '''
def test_no_decorator():
    pass

def test_other_decorator():
    pass
''',
        encoding="utf-8",
    )
    assert collect_annotated_tests(tests_dir) == {}


def test_collect_ignores_non_test_functions(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text(
        '''
from pytest_intent import intent

@intent("INT-001")
def helper_thing():  # not a test_ prefix
    pass

@intent("INT-001")
def test_thing():
    pass
''',
        encoding="utf-8",
    )
    found = collect_annotated_tests(tests_dir)
    assert found["INT-001"] == ["tests/test_a.py::test_thing"]


def test_coverage_violations_uncovered_claim() -> None:
    claims = {"INT-001": {}, "INT-002": {}}
    annotated = {"INT-001": ["tests/test_a.py::t"]}
    violations = coverage_violations(claims, annotated)
    assert len(violations) == 1
    assert "INT-002" in violations[0]


def test_coverage_violations_orphan_test() -> None:
    claims = {"INT-001": {}}
    annotated = {"INT-001": ["t1"], "INT-999": ["t2"]}
    violations = coverage_violations(claims, annotated)
    assert any("INT-999" in v for v in violations)


def test_coverage_violations_clean_pass() -> None:
    claims = {"INT-001": {}, "INT-002": {}}
    annotated = {"INT-001": ["t1"], "INT-002": ["t2"]}
    assert coverage_violations(claims, annotated) == []
