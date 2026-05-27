"""CSD-INTENT-01 schema validation for intent.yaml claims.

Validates the canonical claim shape:

    INT-NNN:
      version: X.Y.Z
      status: draft | active | deprecated
      statement: "..."             # required
      rationale: "..."             # optional in CSD; recommended
      test:
        scope: unit | integration | e2e
        component: "..."
        type: invariant | behavior | contract
      criticality: critical | high | medium | low

The legacy flat shape (top-level `scope:` instead of nested `test.scope`) is
accepted with a warning so projects can migrate incrementally.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "ID_PATTERN",
    "VALID_CRITICALITY",
    "VALID_SCOPE",
    "VALID_STATUS",
    "VALID_TYPE",
    "VERSION_PATTERN",
    "check_schema",
    "parse_intent_yaml",
]

# Accept either canonical `INT-NNN` (CSD-INTENT-01 §3.1) or our extended
# `INT-PREFIX-NNN` style for multi-module monorepos. Both are valid here.
ID_PATTERN = re.compile(r"^INT-[A-Z0-9-]+$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

VALID_STATUS = {"draft", "active", "deprecated"}
VALID_SCOPE = {"unit", "integration", "e2e"}
VALID_TYPE = {"invariant", "behavior", "contract"}
VALID_CRITICALITY = {"critical", "high", "medium", "low"}

# Top-level fields required on every claim per CSD-INTENT-01 §4.1.
# (id is implicit from the YAML key, so we don't check it separately.)
REQUIRED_TOP = {"version", "status", "statement", "criticality"}


def parse_intent_yaml(path: Path) -> dict[str, dict[str, Any]]:
    """Parse an intent.yaml. Returns {claim_id: claim_dict}. Non-INT keys ignored."""
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for key, value in data.items():
        if isinstance(key, str) and key.startswith("INT-") and isinstance(value, dict):
            out[key] = value
    return out


def _scope_and_test(claim: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    """Return (effective_scope, nested_test_dict_or_None)."""
    test = claim.get("test")
    if isinstance(test, dict):
        scope = test.get("scope")
        return (scope if isinstance(scope, str) else None, test)
    legacy = claim.get("scope")
    return (legacy if isinstance(legacy, str) else None, None)


def check_schema(claims: dict[str, dict[str, Any]]) -> list[str]:
    """Return a list of human-readable schema violations. Empty list = pass."""
    violations: list[str] = []

    for cid, claim in claims.items():
        if not ID_PATTERN.match(cid):
            violations.append(f"{cid}: id does not match {ID_PATTERN.pattern}")

        missing = REQUIRED_TOP - set(claim.keys())
        if missing:
            violations.append(f"{cid}: missing required fields {sorted(missing)}")

        version = claim.get("version")
        if version is not None and (
            not isinstance(version, str) or not VERSION_PATTERN.match(version)
        ):
            violations.append(f"{cid}: version `{version!r}` is not semver X.Y.Z")

        status = claim.get("status")
        if status is not None and status not in VALID_STATUS:
            violations.append(
                f"{cid}: invalid status `{status!r}` (allowed {sorted(VALID_STATUS)})"
            )

        criticality = claim.get("criticality")
        if criticality is not None and criticality not in VALID_CRITICALITY:
            violations.append(
                f"{cid}: invalid criticality `{criticality!r}` "
                f"(allowed {sorted(VALID_CRITICALITY)})"
            )

        statement = claim.get("statement")
        if statement is not None and (not isinstance(statement, str) or len(statement) < 10):
            violations.append(f"{cid}: statement must be a string of >=10 characters")

        scope, test = _scope_and_test(claim)
        if scope is None:
            violations.append(f"{cid}: missing scope (must appear as `test.scope` or top-level `scope`)")
        elif scope not in VALID_SCOPE:
            violations.append(
                f"{cid}: invalid scope `{scope!r}` (allowed {sorted(VALID_SCOPE)})"
            )

        # Test object validation (only meaningful when present)
        if test is not None:
            if "component" not in test:
                violations.append(f"{cid}: test.component is required")
            if "type" not in test:
                violations.append(f"{cid}: test.type is required")
            else:
                ttype = test["type"]
                if ttype not in VALID_TYPE:
                    violations.append(
                        f"{cid}: invalid test.type `{ttype!r}` (allowed {sorted(VALID_TYPE)})"
                    )

    return violations
