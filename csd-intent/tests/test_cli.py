"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

from pytest_intent import intent

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


@intent('INT-CSD-005')
def test_cli_fail_on_schema_only(tmp_path: Path, capsys) -> None:
    """--fail-on schema tolerates unattested claims."""
    (tmp_path / "intent.yaml").write_text(_GOOD_INTENT, encoding="utf-8")
    # No tests at all → INT-001 unattested. Should still exit 0 with --fail-on schema.
    rc = main([str(tmp_path), "--fail-on", "schema"])
    out = capsys.readouterr().out
    assert rc == 0
    # The unattested claim is still printed in the report so the user sees the gap.
    assert "INT-001" in out


@intent("INT-CSD-006")
def test_cli_relative_tests_dir_anchors_to_project_root(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The same audit passes regardless of the caller's working directory."""
    project = tmp_path / "proj"
    tests = project / "tests"
    tests.mkdir(parents=True)
    (project / "intent.yaml").write_text(_GOOD_INTENT, encoding="utf-8")
    (tests / "test_x.py").write_text(
        "from pytest_intent import intent\n@intent('INT-001')\ndef test_one(): pass\n",
        encoding="utf-8",
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    rc = main([str(project), "--tests-dir", "tests", "--intent", "intent.yaml"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CLEAN" in out


@intent('INT-CSD-007')
def test_cli_zero_claims_exits_nonzero_under_fail_on_schema(tmp_path: Path, capsys) -> None:
    """The `spec.claims[]` reproduction from issue #5 must not report CLEAN."""
    non_canonical = """
apiVersion: csd.foundry/v1
kind: Intent
metadata:
  name: task-api
spec:
  claims:
    - id: CSD-001
      name: ci-pipeline
"""
    (tmp_path / "intent.yaml").write_text(non_canonical, encoding="utf-8")
    rc = main([str(tmp_path), "--fail-on", "schema"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "CLEAN" not in out
    assert "no top-level INT-* claims" in out


def test_cli_version_prints_and_exits(capsys) -> None:
    rc = main(["--version"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip()
