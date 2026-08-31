"""End-to-end audit tests: schema + orphan + coverage combined."""

from __future__ import annotations

from pathlib import Path

from pytest_intent import intent

from csd_intent.audit import ViolationKind, audit


def _scaffold(tmp_path: Path, intent_body: str, py_body: str = "", ts_body: str = "") -> Path:
    (tmp_path / "intent.yaml").write_text(intent_body, encoding="utf-8")
    if py_body:
        tests = tmp_path / "tests"
        tests.mkdir(exist_ok=True)
        (tests / "test_things.py").write_text(py_body, encoding="utf-8")
    if ts_body:
        src = tmp_path / "src"
        src.mkdir(exist_ok=True)
        (src / "thing.test.ts").write_text(ts_body, encoding="utf-8")
    return tmp_path


_GOOD_INTENT = """
INT-001:
  version: 1.0.0
  status: active
  statement: "Backend must not eat the kittens."
  rationale: "Self-evident."
  test:
    scope: integration
    component: KittenGuard
    type: invariant
  criticality: critical

INT-002:
  version: 1.0.0
  status: active
  statement: "Frontend renders kitten badge."
  rationale: "Operators love kittens."
  test:
    scope: unit
    component: KittenBadge
    type: behavior
  criticality: medium
"""


def test_clean_audit(tmp_path: Path) -> None:
    project = _scaffold(
        tmp_path,
        _GOOD_INTENT,
        py_body="from pytest_intent import intent\n@intent('INT-001')\ndef test_kittens(): pass\n",
        ts_body="intent('INT-002', 'badge renders', () => {});\n",
    )
    report = audit(project)
    assert report.ok
    assert report.claim_count == 2
    assert report.attested_claims == {"INT-001", "INT-002"}


@intent('INT-CSD-002')
def test_orphan_test_marker_flagged(tmp_path: Path) -> None:
    project = _scaffold(
        tmp_path,
        _GOOD_INTENT,
        py_body="from pytest_intent import intent\n@intent('INT-999')\ndef test_ghost(): pass\n",
        ts_body="intent('INT-002', 'badge', () => {});\n",
    )
    report = audit(project)
    assert not report.ok
    orphans = [v for v in report.violations if v.kind == ViolationKind.ORPHAN]
    assert {v.claim_id for v in orphans} == {"INT-999"}


@intent('INT-CSD-003')
def test_unattested_claim_flagged(tmp_path: Path) -> None:
    project = _scaffold(
        tmp_path,
        _GOOD_INTENT,
        py_body="from pytest_intent import intent\n@intent('INT-001')\ndef test_kittens(): pass\n",
        # No frontend attestation for INT-002.
    )
    report = audit(project)
    assert not report.ok
    assert report.unattested == ["INT-002"]


def test_schema_violation_flagged(tmp_path: Path) -> None:
    bad = """
INT-001:
  version: 1.0.0
  status: active
  statement: "Missing test block entirely."
  rationale: "..."
  criticality: medium
"""
    project = _scaffold(tmp_path, bad, py_body="")
    report = audit(project)
    assert not report.ok
    schema_violations = [v for v in report.violations if v.kind == ViolationKind.SCHEMA]
    assert schema_violations
    assert any("scope" in v.message for v in schema_violations)


@intent('INT-CSD-003')
def test_deprecated_claim_not_flagged_as_unattested(tmp_path: Path) -> None:
    """A deprecated claim documents removed behavior; no test expected."""
    yaml = """
INT-001:
  version: 1.0.0
  status: deprecated
  statement: "This used to be guaranteed but the feature was removed."
  rationale: "Out of scope after refactor."
  test:
    scope: integration
    component: GoneService
    type: behavior
  criticality: medium
"""
    project = _scaffold(tmp_path, yaml)  # no tests at all
    report = audit(project)
    assert report.ok
    assert report.unattested == []


@intent('INT-CSD-003')
def test_draft_claim_not_flagged_as_unattested(tmp_path: Path) -> None:
    """A draft claim is a pre-implementation placeholder; not yet a coverage failure."""
    yaml = """
INT-001:
  version: 0.1.0
  status: draft
  statement: "Future behaviour pending implementation."
  rationale: "Captures intent before code is written."
  test:
    scope: integration
    component: FuturePlanner
    type: behavior
  criticality: low
"""
    project = _scaffold(tmp_path, yaml)
    report = audit(project)
    assert report.ok
    assert report.unattested == []


@intent('INT-CSD-007')
def test_zero_claims_flagged_as_schema_violation(tmp_path: Path) -> None:
    """A non-canonical schema (e.g. `spec.claims[]`) parses to zero INT-* keys.

    That must not read as an empty-but-valid project: it's schema drift and
    should fail loudly rather than report CLEAN (issue #5).
    """
    non_canonical = """
apiVersion: csd.foundry/v1
kind: Intent
metadata:
  name: task-api
spec:
  claims:
    - id: CSD-001
      name: ci-pipeline
      description: "CI pipeline runs lint, test, audit, and conformance."
"""
    project = _scaffold(tmp_path, non_canonical)
    report = audit(project)
    assert not report.ok
    assert report.claim_count == 0
    schema_violations = [v for v in report.violations if v.kind == ViolationKind.SCHEMA]
    assert schema_violations
    message = schema_violations[0].message
    assert "no top-level INT-* claims" in message
    assert "apiVersion" in message and "kind" in message and "spec" in message


@intent('INT-CSD-008')
def test_duplicate_claim_id_flagged_as_schema_violation(tmp_path: Path) -> None:
    """A repeated claim id must fail the audit, not silently drop the first claim.

    YAML resolves the duplicate last-wins before the auditor sees the data, so the
    earlier claim disappears and the marker written for it now attests the survivor
    - while the audit prints CLEAN (issue #12).
    """
    duplicate = """
INT-001:
  version: 1.0.0
  status: active
  statement: "The first claim, which vanishes."
  criticality: high
  test: {scope: unit, component: KittenGuard, type: invariant}
INT-001:
  version: 1.0.0
  status: active
  statement: "The second claim, which survives under the same id."
  criticality: high
  test: {scope: unit, component: KittenGuard, type: invariant}
"""
    project = _scaffold(
        tmp_path,
        duplicate,
        py_body="from pytest_intent import intent\n@intent('INT-001')\ndef test_kittens(): pass\n",
    )
    report = audit(project)
    assert not report.ok
    schema_violations = [v for v in report.violations if v.kind == ViolationKind.SCHEMA]
    assert schema_violations
    message = schema_violations[0].message
    assert "duplicate key `INT-001`" in message
    assert "line 2" in message and "line 8" in message
    assert "CLEAN" not in report.format()


def test_missing_intent_yaml(tmp_path: Path) -> None:
    report = audit(tmp_path)
    assert not report.ok
    assert any("intent.yaml not found" in v.message for v in report.violations)


def test_format_clean_message(tmp_path: Path) -> None:
    project = _scaffold(
        tmp_path,
        _GOOD_INTENT,
        py_body="from pytest_intent import intent\n@intent('INT-001')\ndef test_kittens(): pass\n",
        ts_body="intent('INT-002', 'badge', () => {});\n",
    )
    report = audit(project)
    text = report.format()
    assert "CLEAN" in text


def test_format_violation_message(tmp_path: Path) -> None:
    project = _scaffold(tmp_path, _GOOD_INTENT)  # no tests → both unattested
    report = audit(project)
    text = report.format()
    assert "UNATTESTED" in text
    assert "INT-001" in text
    assert "INT-002" in text


@intent('INT-CSD-009')
def test_llm_scope_is_valid_and_needs_no_marker(tmp_path: Path) -> None:
    """A judged claim carries no marker by construction, so coverage must not ask for one."""
    report = audit(
        _scaffold(
            tmp_path,
            intent_body=(
                "INT-001:\n"
                "  version: 1.0.0\n"
                "  status: active\n"
                '  statement: "Every active claim states a falsifiable condition."\n'
                "  test:\n"
                "    scope: llm\n"
                "    component: ClaimSet\n"
                "    type: invariant\n"
                "  criticality: high\n"
            ),
        )
    )
    assert report.ok, report.format()
    assert not [v for v in report.violations if v.kind is ViolationKind.SCHEMA]
    assert "INT-001" not in report.unattested


@intent('INT-CSD-010')
def test_marker_on_llm_claim_is_a_violation(tmp_path: Path) -> None:
    """A mechanical test standing in for a judgement must not read as attestation."""
    report = audit(
        _scaffold(
            tmp_path,
            intent_body=(
                "INT-001:\n"
                "  version: 1.0.0\n"
                "  status: active\n"
                '  statement: "Every active claim states a falsifiable condition."\n'
                "  test:\n"
                "    scope: llm\n"
                "    component: ClaimSet\n"
                "    type: invariant\n"
                "  criticality: high\n"
            ),
            py_body="from pytest_intent import intent\n@intent('INT-001')\ndef test_approximation(): pass\n",
        )
    )
    assert not report.ok
    kinds = [v.kind for v in report.violations]
    assert ViolationKind.MISMARKED in kinds, report.format()
    assert ViolationKind.UNATTESTED not in kinds
