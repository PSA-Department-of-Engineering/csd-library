"""Walker tests for Python AST + JS/TS regex extraction of intent markers."""

from __future__ import annotations

from pathlib import Path

from csd_intent.walker import collect_attestations


def test_python_ast_picks_up_decorator(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("", encoding="utf-8")
    (tests / "test_a.py").write_text(
        "from pytest_intent import intent\n\n"
        "@intent('INT-001')\n"
        "def test_one() -> None:\n"
        "    assert True\n"
        "\n"
        "@intent('INT-002', 'INT-003')\n"
        "def test_two() -> None:\n"
        "    assert True\n",
        encoding="utf-8",
    )
    out = collect_attestations([tests])
    assert set(out) == {"INT-001", "INT-002", "INT-003"}
    assert out["INT-001"] == ["test_a.py::test_one"]
    assert out["INT-002"] == ["test_a.py::test_two"]


def test_python_walker_skips_excluded_dirs(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    venv = tests / ".venv"
    venv.mkdir()
    (venv / "test_ignored.py").write_text(
        "from pytest_intent import intent\n@intent('INT-IGNORED')\ndef test_x(): pass\n",
        encoding="utf-8",
    )
    out = collect_attestations([tests])
    assert "INT-IGNORED" not in out


def test_python_walker_ignores_non_test_files(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "helpers.py").write_text(
        "from pytest_intent import intent\n@intent('INT-NOT')\ndef helper(): pass\n",
        encoding="utf-8",
    )
    out = collect_attestations([tests])
    assert out == {}


def test_js_regex_picks_up_intent_call(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "thing.test.ts").write_text(
        "import { intent } from 'vitest-intent';\n\n"
        "intent('INT-FE-001', 'renders', () => { /* ... */ });\n"
        'intent("INT-FE-002", "another", async () => { /* ... */ });\n',
        encoding="utf-8",
    )
    out = collect_attestations([src])
    assert set(out) == {"INT-FE-001", "INT-FE-002"}
    assert any("renders" in r for r in out["INT-FE-001"])


def test_js_regex_picks_up_array_form(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "multi.test.tsx").write_text(
        "import { intent } from 'vitest-intent';\n"
        "intent(['INT-A', 'INT-B'], 'two claims', () => {});\n",
        encoding="utf-8",
    )
    out = collect_attestations([src])
    assert set(out) == {"INT-A", "INT-B"}


def test_walker_handles_missing_dir(tmp_path: Path) -> None:
    out = collect_attestations([tmp_path / "does-not-exist"])
    assert out == {}


def test_walker_unions_across_dirs(tmp_path: Path) -> None:
    a = tmp_path / "be"
    b = tmp_path / "fe"
    a.mkdir()
    b.mkdir()
    (a / "test_x.py").write_text(
        "from pytest_intent import intent\n@intent('INT-001')\ndef test_p(): pass\n",
        encoding="utf-8",
    )
    (b / "y.test.ts").write_text(
        "intent('INT-001', 'frontend too', () => {});\n",
        encoding="utf-8",
    )
    out = collect_attestations([a, b])
    assert out["INT-001"] == ["test_x.py::test_p", "y.test.ts::frontend too"]
