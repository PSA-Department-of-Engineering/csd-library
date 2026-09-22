"""CLI smoke tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pytest_intent import intent

from csd_intent.audit import audit
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


# One claim of every kind the summary has to count: an attested active claim, an
# unattested one, a draft, a deprecated, and a judged (`llm`) claim, with overlapping
# derived_from ids so requirements_traced has a duplicate to fold.
_SUMMARY_INTENT = """
INT-001:
  version: 1.0.0
  status: active
  statement: "An attested active claim."
  derived_from: [REQ-001, REQ-002]
  test:
    scope: unit
    component: Foo
    type: behavior
  criticality: medium

INT-002:
  version: 1.0.0
  status: active
  statement: "An active claim nothing attests."
  derived_from: [REQ-002]
  test:
    scope: integration
    component: Foo
    type: behavior
  criticality: high

INT-003:
  version: 0.1.0
  status: draft
  statement: "A draft claim, ahead of its test."
  derived_from: [REQ-003]
  test:
    scope: unit
    component: Foo
    type: behavior
  criticality: low

INT-004:
  version: 1.0.0
  status: deprecated
  statement: "A deprecated claim, with no derivation."
  test:
    scope: unit
    component: Foo
    type: behavior
  criticality: low

INT-005:
  version: 1.0.0
  status: active
  statement: "A judged claim, attested by a reviewer's recorded verdict."
  derived_from: [REQ-001]
  test:
    scope: llm
    component: Foo
    type: invariant
  criticality: high
"""


def _summary_project(tmp_path: Path) -> Path:
    (tmp_path / "intent.yaml").write_text(_SUMMARY_INTENT, encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text(
        "from pytest_intent import intent\n@intent('INT-001')\ndef test_one(): pass\n",
        encoding="utf-8",
    )
    return tmp_path


@intent("INT-CSD-011")
def test_cli_json_prints_one_object_and_nothing_else(tmp_path: Path, capsys) -> None:
    """stdout parses as JSON on its own: any stray line breaks the consumer's parse."""
    project = _summary_project(tmp_path)
    rc = main([str(project), "--json", "--quiet"])
    captured = capsys.readouterr()
    # INT-002 is unattested, and --fail-on any still governs the exit code.
    assert rc == 1
    assert captured.err == ""
    data = json.loads(captured.out)
    assert isinstance(data, dict)


@intent("INT-CSD-011")
def test_cli_json_summary_counts_the_audit(tmp_path: Path, capsys) -> None:
    project = _summary_project(tmp_path)
    main([str(project), "--json"])
    data = json.loads(capsys.readouterr().out)

    assert data["claims"] == 5
    assert data["attested"] == 1
    assert data["unattested"] == 1
    assert data["draft"] == 1
    assert data["active"] == 3
    assert data["deprecated"] == 1
    assert data["violations"] == 1
    assert data["requirements_traced"] == 3
    assert data["clean"] is False
    assert datetime.strptime(data["generated_at"], "%Y-%m-%dT%H:%M:%SZ")

    assert len(data["projects"]) == 1
    assert Path(data["projects"][0]["intent_path"]) == (project / "intent.yaml").resolve()
    assert {k: v for k, v in data["projects"][0].items() if k != "intent_path"} == {
        "claims": 5,
        "attested": 1,
        "unattested": 1,
        "draft": 1,
        "active": 3,
        "deprecated": 1,
        "violations": 1,
        "requirements_traced": 3,
        "clean": False,
    }

    assert set(data["claims_by_id"]) == {"INT-001", "INT-002", "INT-003", "INT-004", "INT-005"}
    assert data["claims_by_id"]["INT-001"] == {
        "status": "active",
        "attested": True,
        "scope": "unit",
        "derived_from": ["REQ-001", "REQ-002"],
    }
    assert data["claims_by_id"]["INT-004"] == {
        "status": "deprecated",
        "attested": False,
        "scope": "unit",
        "derived_from": [],
    }
    assert data["claims_by_id"]["INT-005"] == {
        "status": "active",
        "attested": False,
        "scope": "llm",
        "derived_from": ["REQ-001"],
    }


@intent("INT-CSD-011")
def test_cli_json_attested_means_what_the_report_means(tmp_path: Path, capsys) -> None:
    """The count a postflight records is the report's own attested set, a mismarked claim included."""
    project = _summary_project(tmp_path)
    (project / "tests" / "test_y.py").write_text(
        "from pytest_intent import intent\n@intent('INT-005')\ndef test_judged(): pass\n",
        encoding="utf-8",
    )
    report = audit(project)
    assert report.attested_claims == {"INT-001", "INT-005"}

    main([str(project), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["attested"] == len(report.attested_claims) == 2
    assert data["unattested"] == len(report.unattested) == 1
    assert data["violations"] == len(report.violations) == 2  # INT-002 unattested, INT-005 mismarked
    assert data["claims_by_id"]["INT-005"]["attested"] is True


@intent("INT-CSD-011")
def test_cli_json_clean_project_exits_zero(tmp_path: Path, capsys) -> None:
    (tmp_path / "intent.yaml").write_text(_GOOD_INTENT, encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text(
        "from pytest_intent import intent\n@intent('INT-001')\ndef test_one(): pass\n",
        encoding="utf-8",
    )
    rc = main([str(tmp_path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert data["clean"] is True
    assert data["violations"] == 0
    assert data["claims"] == data["attested"] == 1
    assert data["requirements_traced"] == 0


@intent("INT-CSD-011")
def test_cli_json_missing_intent_yaml_still_prints_the_object(tmp_path: Path, capsys) -> None:
    rc = main([str(tmp_path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert data["clean"] is False
    assert data["claims"] == data["attested"] == 0
    assert data["violations"] == 1
    assert data["claims_by_id"] == {}


@intent("INT-CSD-011")
def test_cli_json_nested_projects_sum_counts_and_union_claims(tmp_path: Path, capsys) -> None:
    """A tree of nested projects folds into one object: counts sum, requirement ids stay distinct."""
    root = _summary_project(tmp_path)
    nested = root / "frontend"
    nested.mkdir()
    (nested / "intent.yaml").write_text(
        "INT-FE-001:\n"
        "  version: 1.0.0\n"
        "  status: active\n"
        '  statement: "The frontend claim."\n'
        "  derived_from: [REQ-001, REQ-009]\n"
        "  test: {scope: unit, component: Ui, type: behavior}\n"
        "  criticality: medium\n",
        encoding="utf-8",
    )
    (nested / "ui.test.ts").write_text("intent('INT-FE-001', 'renders', () => {});\n", encoding="utf-8")

    rc = main([str(root), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert data["claims"] == 6
    assert data["attested"] == 2
    assert data["unattested"] == 1
    assert data["requirements_traced"] == 4  # REQ-001 is traced by both projects and counted once
    assert data["clean"] is False
    assert [Path(p["intent_path"]) for p in data["projects"]] == [
        (root / "intent.yaml").resolve(),
        (nested / "intent.yaml").resolve(),
    ]
    assert data["projects"][1]["claims"] == 1
    assert data["projects"][1]["requirements_traced"] == 2
    assert data["projects"][1]["clean"] is True
    assert set(data["claims_by_id"]) == {"INT-001", "INT-002", "INT-003", "INT-004", "INT-005", "INT-FE-001"}
