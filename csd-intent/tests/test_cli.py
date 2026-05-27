"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

from csd_intent.cli import main

_GOOD_INTENT = """
INT-001:
  version: 1.0.0
  status: active
  statement: "A representative claim."
  rationale: "Has to exist for the CLI test."
  test:
    scope: unit
    component: Foo
    type: behavior
  criticality: medium
"""


def test_cli_clean_exits_zero(tmp_path: Path, capsys) -> None:
    (tmp_path / "intent.yaml").write_text(_GOOD_INTENT, encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text(
        "from pytest_intent import intent\n@intent('INT-001')\ndef test_one(): pass\n",
        encoding="utf-8",
    )
    rc = main([str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CLEAN" in out


def test_cli_missing_intent_exits_one(tmp_path: Path, capsys) -> None:
    rc = main([str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "not found" in out


def test_cli_fail_on_schema_only(tmp_path: Path, capsys) -> None:
    """--fail-on schema tolerates unattested claims."""
    (tmp_path / "intent.yaml").write_text(_GOOD_INTENT, encoding="utf-8")
    # No tests at all → INT-001 unattested. Should still exit 0 with --fail-on schema.
    rc = main([str(tmp_path), "--fail-on", "schema"])
    out = capsys.readouterr().out
    assert rc == 0
    # The unattested claim is still printed in the report so the user sees the gap.
    assert "INT-001" in out


def test_cli_version_prints_and_exits(capsys) -> None:
    rc = main(["--version"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip()
