"""Schema validation tests for CSD-INTENT-01 claims."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_intent import intent

from csd_intent.schema import DuplicateKeyError, check_schema, parse_intent_yaml, top_level_keys


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


_DUPLICATE_ID = """
INT-A-001:
  version: 1.0.0
  status: active
  statement: "The first claim, which vanishes."
  criticality: high
  test: {scope: unit, component: X, type: invariant}
INT-A-001:
  version: 1.0.0
  status: active
  statement: "The second claim, which survives under the same id."
  criticality: high
  test: {scope: unit, component: X, type: invariant}
"""


@intent('INT-CSD-008')
def test_duplicate_claim_id_is_refused(tmp_path: Path) -> None:
    """A repeated id must raise, not silently drop the first claim (issue #12)."""
    with pytest.raises(DuplicateKeyError) as excinfo:
        parse_intent_yaml(_write(tmp_path, _DUPLICATE_ID))
    assert excinfo.value.key == "INT-A-001"
    # Both occurrences are located, so the author can see what collided.
    assert (excinfo.value.first_line, excinfo.value.second_line) == (2, 8)


@intent('INT-CSD-008')
def test_duplicate_key_inside_a_claim_is_refused(tmp_path: Path) -> None:
    """The same silent last-wins drop applies to a claim's own fields."""
    yaml = """
INT-001:
  version: 1.0.0
  status: active
  statement: "The statement the author believes is enforced."
  statement: "The statement that actually survives."
  criticality: high
  test: {scope: unit, component: X, type: invariant}
"""
    with pytest.raises(DuplicateKeyError) as excinfo:
        parse_intent_yaml(_write(tmp_path, yaml))
    assert excinfo.value.key == "statement"


@intent('INT-CSD-008')
def test_merge_key_override_is_not_a_duplicate(tmp_path: Path) -> None:
    """A YAML merge plus an explicit override is legal and must still parse."""
    yaml = """
_base: &base
  version: 1.0.0
  status: active
  criticality: high
  test: {scope: unit, component: X, type: invariant}

INT-001:
  <<: *base
  status: draft
  statement: "Overrides the merged status, which is not a duplicate key."
"""
    claims = parse_intent_yaml(_write(tmp_path, yaml))
    assert claims["INT-001"]["status"] == "draft"
    assert check_schema(claims) == []


def test_top_level_keys_refuses_a_duplicate(tmp_path: Path) -> None:
    """The zero-claims diagnostic reads the file the same strict way the parse does."""
    with pytest.raises(DuplicateKeyError):
        top_level_keys(_write(tmp_path, _DUPLICATE_ID))
