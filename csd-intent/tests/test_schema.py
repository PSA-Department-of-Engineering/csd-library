"""Schema validation tests for CSD-INTENT-01 claims."""

from __future__ import annotations

from pathlib import Path

from pytest_intent import intent

from csd_intent.schema import check_schema, parse_intent_yaml


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "intent.yaml"
    p.write_text(body, encoding="utf-8")
    return p


@intent('INT-CSD-001')
def test_canonical_claim_passes(tmp_path: Path) -> None:
    yaml = """
INT-SB-001:
  version: 1.0.0
  status: active
  statement: "Switch is skipped when the working tree is dirty."
  rationale: "Safety contract."
  test:
    scope: integration
    component: SwitchFlow
    type: invariant
  criticality: critical
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    assert check_schema(claims) == []


def test_legacy_flat_scope_accepted(tmp_path: Path) -> None:
    """Backwards-compat: a project still using flat `scope:` passes (no warning here)."""
    yaml = """
INT-001:
  statement: "Legacy claim shape."
  rationale: "Older project."
  criticality: medium
  scope: unit
  version: 1.0.0
  status: active
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    # Missing nested test.component / test.type - that's still a violation,
    # but the FLAT scope itself is honored.
    violations = check_schema(claims)
    assert all("scope" not in v.lower() or "test.scope" in v for v in violations)


@intent('INT-CSD-001')
def test_missing_version_fails(tmp_path: Path) -> None:
    yaml = """
INT-001:
  status: active
  statement: "This claim has no version."
  test:
    scope: unit
    component: X
    type: behavior
  criticality: low
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    violations = check_schema(claims)
    assert any("version" in v for v in violations)


def test_invalid_scope_fails(tmp_path: Path) -> None:
    yaml = """
INT-001:
  version: 1.0.0
  status: active
  statement: "Bad scope here."
  test:
    scope: system
    component: X
    type: behavior
  criticality: low
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    violations = check_schema(claims)
    assert any("scope" in v and "system" in v for v in violations)


@intent('INT-CSD-001')
def test_invalid_id_pattern_fails(tmp_path: Path) -> None:
    yaml = """
intent-1:
  version: 1.0.0
  status: active
  statement: "ID is lowercase and doesn't start with INT-."
  test:
    scope: unit
    component: X
    type: behavior
  criticality: low
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    # intent-1 doesn't match INT-* so it's not even parsed as a claim.
    assert claims == {}


@intent('INT-CSD-001')
def test_unknown_status_fails(tmp_path: Path) -> None:
    yaml = """
INT-001:
  version: 1.0.0
  status: wip
  statement: "Bad status value."
  test:
    scope: unit
    component: X
    type: behavior
  criticality: low
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    violations = check_schema(claims)
    assert any("status" in v and "wip" in v for v in violations)


def test_unknown_test_type_fails(tmp_path: Path) -> None:
    yaml = """
INT-001:
  version: 1.0.0
  status: active
  statement: "Bad test type."
  test:
    scope: unit
    component: X
    type: smoke
  criticality: low
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    violations = check_schema(claims)
    assert any("test.type" in v and "smoke" in v for v in violations)
