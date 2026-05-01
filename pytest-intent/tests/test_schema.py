"""Tests for schema parsing and validation."""

from __future__ import annotations

from pytest_intent import check_schema, parse_intent_yaml


def test_parse_intent_yaml_basic(tmp_path) -> None:
    yaml_path = tmp_path / "intent.yaml"
    yaml_path.write_text(
        """
INT-001:
  statement: "X must be true"
  rationale: "because Y"
  criticality: critical
  scope: unit

INT-002:
  statement: "another claim"
  rationale: "because Z"
  criticality: high
  scope: integration
""",
        encoding="utf-8",
    )
    claims = parse_intent_yaml(yaml_path)
    assert set(claims.keys()) == {"INT-001", "INT-002"}
    assert claims["INT-001"]["statement"] == "X must be true"
    assert claims["INT-002"]["scope"] == "integration"


def test_parse_intent_yaml_ignores_non_INT_keys(tmp_path) -> None:
    yaml_path = tmp_path / "intent.yaml"
    yaml_path.write_text(
        """
title: "My project intent"
INT-001:
  statement: "x"
  rationale: "y"
  criticality: low
  scope: unit
""",
        encoding="utf-8",
    )
    claims = parse_intent_yaml(yaml_path)
    assert "title" not in claims
    assert "INT-001" in claims


def test_parse_intent_yaml_empty_file(tmp_path) -> None:
    yaml_path = tmp_path / "intent.yaml"
    yaml_path.write_text("", encoding="utf-8")
    claims = parse_intent_yaml(yaml_path)
    assert claims == {}


def test_check_schema_passes_complete_claim() -> None:
    claims = {
        "INT-001": {
            "statement": "x",
            "rationale": "y",
            "criticality": "critical",
            "scope": "unit",
        }
    }
    assert check_schema(claims) == []


def test_check_schema_flags_missing_field() -> None:
    claims = {
        "INT-001": {
            "statement": "x",
            "rationale": "y",
            "criticality": "critical",
            # scope missing
        }
    }
    violations = check_schema(claims)
    assert len(violations) == 1
    assert "scope" in violations[0]


def test_check_schema_flags_invalid_criticality() -> None:
    claims = {
        "INT-001": {
            "statement": "x",
            "rationale": "y",
            "criticality": "BLOCKER",  # invalid
            "scope": "unit",
        }
    }
    violations = check_schema(claims)
    assert any("criticality" in v for v in violations)


def test_check_schema_flags_invalid_scope() -> None:
    claims = {
        "INT-001": {
            "statement": "x",
            "rationale": "y",
            "criticality": "high",
            "scope": "module",  # invalid
        }
    }
    violations = check_schema(claims)
    assert any("scope" in v for v in violations)


def test_check_schema_passes_empty_claims() -> None:
    assert check_schema({}) == []
