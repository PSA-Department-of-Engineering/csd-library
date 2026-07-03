"""Nested-project awareness: project boundaries, discovery, and aggregation.

A repo may contain a *nested* intent project - a subdirectory that carries its own
``intent.yaml``. The outer audit must treat that subtree as a separate project boundary
(so its markers don't orphan against the outer claims), and ``audit_tree`` / the CLI must
audit each nested project independently against its own ``intent.yaml``.
"""

from __future__ import annotations

from pathlib import Path

from csd_intent.audit import ViolationKind, audit, audit_tree
from csd_intent.cli import main
from csd_intent.walker import (
    collect_attestations,
    find_nested_intent_projects,
)

# A minimal, schema-valid claim template. {id} / {status} are filled per use.
_CLAIM = """\
{id}:
  version: 1.0.0
  status: {status}
  statement: "A representative claim that is at least ten characters long."
  rationale: "Exists for the nested-project tests."
  test:
    scope: unit
    component: Thing
    type: behavior
  criticality: medium
"""


def _claim(cid: str, status: str = "active") -> str:
    return _CLAIM.format(id=cid, status=status)


def _py_marker(cid: str, fn: str = "test_it") -> str:
    return f"from pytest_intent import intent\n@intent('{cid}')\ndef {fn}(): pass\n"


def _ts_marker(cid: str, name: str = "does the thing") -> str:
    return f"intent('{cid}', '{name}', () => {{}});\n"


def _make_root_with_nested(tmp_path: Path) -> Path:
    """Build root project (INT-ROOT-001) with a nested sub/ project (INT-SUB-001).

    Root has a Python marker for INT-ROOT-001 in tests/.
    The nested sub/ project has its own intent.yaml + a TS marker for INT-SUB-001.
    """
    (tmp_path / "intent.yaml").write_text(_claim("INT-ROOT-001"), encoding="utf-8")
    root_tests = tmp_path / "tests"
    root_tests.mkdir()
    (root_tests / "test_root.py").write_text(_py_marker("INT-ROOT-001", "test_root"), encoding="utf-8")

    sub = tmp_path / "sub"
    sub_tests = sub / "tests"
    sub_tests.mkdir(parents=True)
    (sub / "intent.yaml").write_text(_claim("INT-SUB-001"), encoding="utf-8")
    (sub_tests / "sub.test.ts").write_text(_ts_marker("INT-SUB-001"), encoding="utf-8")
    return tmp_path


# --- Walker: project boundary rule ------------------------------------------------


def test_walker_does_not_descend_into_nested_project(tmp_path: Path) -> None:
    """A subdir with its own intent.yaml is a boundary; its markers are not collected."""
    root = _make_root_with_nested(tmp_path)
    out = collect_attestations([root])
    assert "INT-ROOT-001" in out
    assert "INT-SUB-001" not in out  # behind the nested boundary


def test_walker_scan_root_is_never_skipped(tmp_path: Path) -> None:
    """The starting root has its own intent.yaml but is still fully scanned."""
    root = _make_root_with_nested(tmp_path)
    # Scanning the nested project directly must collect its own marker.
    out = collect_attestations([root / "sub"])
    assert out == {"INT-SUB-001": ["tests/sub.test.ts::does the thing"]}


def test_walker_can_opt_out_of_boundary(tmp_path: Path) -> None:
    """With respect_nested_projects=False the legacy whole-tree walk is preserved."""
    root = _make_root_with_nested(tmp_path)
    out = collect_attestations([root], respect_nested_projects=False)
    assert set(out) == {"INT-ROOT-001", "INT-SUB-001"}


def test_walker_handles_deeper_nesting(tmp_path: Path) -> None:
    """A project nested two levels deep also acts as a boundary for its parent."""
    (tmp_path / "intent.yaml").write_text(_claim("INT-A"), encoding="utf-8")
    mid = tmp_path / "mid"
    deep = mid / "deep"
    deep.mkdir(parents=True)
    (mid / "intent.yaml").write_text(_claim("INT-MID"), encoding="utf-8")
    (deep / "intent.yaml").write_text(_claim("INT-DEEP"), encoding="utf-8")
    (tmp_path / "test_a.py").write_text(_py_marker("INT-A", "test_a"), encoding="utf-8")
    (mid / "test_mid.py").write_text(_py_marker("INT-MID", "test_mid"), encoding="utf-8")
    (deep / "test_deep.py").write_text(_py_marker("INT-DEEP", "test_deep"), encoding="utf-8")

    # Root scan stops at mid/.
    assert set(collect_attestations([tmp_path])) == {"INT-A"}
    # mid scan stops at deep/ but includes its own.
    assert set(collect_attestations([mid])) == {"INT-MID"}
    # deep scan sees only its own.
    assert set(collect_attestations([deep])) == {"INT-DEEP"}


# --- Discovery --------------------------------------------------------------------


def test_find_nested_excludes_root(tmp_path: Path) -> None:
    root = _make_root_with_nested(tmp_path)
    nested = find_nested_intent_projects(root)
    assert nested == [(root / "sub").resolve()]
    assert root.resolve() not in nested


def test_find_nested_discovers_all_depths(tmp_path: Path) -> None:
    (tmp_path / "intent.yaml").write_text(_claim("INT-A"), encoding="utf-8")
    mid = tmp_path / "mid"
    deep = mid / "deep"
    deep.mkdir(parents=True)
    (mid / "intent.yaml").write_text(_claim("INT-MID"), encoding="utf-8")
    (deep / "intent.yaml").write_text(_claim("INT-DEEP"), encoding="utf-8")
    nested = find_nested_intent_projects(tmp_path)
    assert nested == [mid.resolve(), deep.resolve()]


def test_find_nested_skips_excluded_dirs(tmp_path: Path) -> None:
    (tmp_path / "intent.yaml").write_text(_claim("INT-A"), encoding="utf-8")
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "intent.yaml").write_text(_claim("INT-VENDOR"), encoding="utf-8")
    assert find_nested_intent_projects(tmp_path) == []


# --- audit(): no cross-project orphans --------------------------------------------


def test_audit_root_has_no_cross_project_orphan(tmp_path: Path) -> None:
    """The root audit must NOT flag the nested project's marker as an orphan."""
    root = _make_root_with_nested(tmp_path)
    report = audit(root)
    assert report.ok
    orphans = [v for v in report.violations if v.kind == ViolationKind.ORPHAN]
    assert orphans == []
    assert report.attested_claims == {"INT-ROOT-001"}


# --- audit_tree(): per-project, independent --------------------------------------


def test_audit_tree_audits_each_project_independently(tmp_path: Path) -> None:
    root = _make_root_with_nested(tmp_path)
    reports = audit_tree(root)
    assert len(reports) == 2
    root_report, sub_report = reports
    assert root_report.intent_path == (root / "intent.yaml").resolve()
    assert sub_report.intent_path == (root / "sub" / "intent.yaml").resolve()
    # Each project is clean against its own intent.yaml + own markers.
    assert root_report.ok
    assert sub_report.ok
    assert sub_report.attested_claims == {"INT-SUB-001"}


def test_audit_tree_nested_detects_its_own_unattested(tmp_path: Path) -> None:
    """The nested project independently flags an unattested claim of its own."""
    root = _make_root_with_nested(tmp_path)
    # Add a second, unattested active claim to the nested project only.
    sub_intent = root / "sub" / "intent.yaml"
    sub_intent.write_text(
        _claim("INT-SUB-001") + "\n" + _claim("INT-SUB-002"), encoding="utf-8"
    )
    reports = audit_tree(root)
    root_report, sub_report = reports
    # Root is unaffected.
    assert root_report.ok
    # Nested flags only its own unattested claim - not anything from the root.
    assert sub_report.unattested == ["INT-SUB-002"]


def test_audit_tree_nested_detects_its_own_orphan(tmp_path: Path) -> None:
    """An orphan marker in the nested subtree orphans against the nested intent.yaml."""
    root = _make_root_with_nested(tmp_path)
    (root / "sub" / "tests" / "ghost.test.ts").write_text(
        _ts_marker("INT-SUB-GHOST", "ghost"), encoding="utf-8"
    )
    reports = audit_tree(root)
    root_report, sub_report = reports
    assert root_report.ok  # root never sees the nested ghost
    sub_orphans = {
        v.claim_id for v in sub_report.violations if v.kind == ViolationKind.ORPHAN
    }
    assert sub_orphans == {"INT-SUB-GHOST"}


def test_audit_tree_without_nesting_returns_single_report(tmp_path: Path) -> None:
    """A repo with no nested intent.yaml yields exactly one report (root only)."""
    (tmp_path / "intent.yaml").write_text(_claim("INT-ROOT-001"), encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_root.py").write_text(_py_marker("INT-ROOT-001", "test_root"), encoding="utf-8")
    reports = audit_tree(tmp_path)
    assert len(reports) == 1
    assert reports[0].ok


# --- CLI aggregation --------------------------------------------------------------


def test_cli_nested_prints_per_project_and_aggregates(tmp_path: Path, capsys) -> None:
    root = _make_root_with_nested(tmp_path)
    # Make the nested project fail with an unattested claim so exit is non-zero.
    sub_intent = root / "sub" / "intent.yaml"
    sub_intent.write_text(
        _claim("INT-SUB-001") + "\n" + _claim("INT-SUB-002"), encoding="utf-8"
    )
    rc = main([str(root)])
    out = capsys.readouterr().out
    # Both projects appear in the report.
    assert str((root / "intent.yaml").resolve()) in out
    assert str((root / "sub" / "intent.yaml").resolve()) in out
    # Aggregate summary line and non-zero exit because one project has a violation.
    assert "2 project(s) audited" in out
    assert rc == 1


def test_cli_nested_all_clean_exits_zero(tmp_path: Path, capsys) -> None:
    root = _make_root_with_nested(tmp_path)
    rc = main([str(root)])
    out = capsys.readouterr().out
    assert "2 project(s) audited: 2 clean, 0 with violation(s)." in out
    assert rc == 0


def test_cli_non_nested_output_is_unchanged(tmp_path: Path, capsys) -> None:
    """No nesting → byte-for-byte the legacy single-project output (no aggregate banner)."""
    (tmp_path / "intent.yaml").write_text(_claim("INT-ROOT-001"), encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_root.py").write_text(_py_marker("INT-ROOT-001", "test_root"), encoding="utf-8")
    rc = main([str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CLEAN" in out
    # The multi-project aggregate banner must NOT appear in the single-project case.
    assert "project(s) audited" not in out


def test_cli_explicit_override_disables_discovery(tmp_path: Path, capsys) -> None:
    """--tests-dir forces single-project mode: no nested discovery, no aggregate banner.

    With an explicit tests dir pointing at the whole tree, the nested marker IS seen by
    the root scan (the override opts out of discovery), so it orphans as before - proving
    the explicit single-project path is preserved unchanged.
    """
    root = _make_root_with_nested(tmp_path)
    rc = main([str(root), "--tests-dir", str(root / "sub")])
    out = capsys.readouterr().out
    # Single-project report only - no aggregate banner.
    assert "project(s) audited" not in out
    # INT-SUB-001 marker now orphans against the ROOT intent.yaml.
    assert "INT-SUB-001" in out
    assert rc == 1
