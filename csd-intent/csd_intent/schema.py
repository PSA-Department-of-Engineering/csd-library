"""CSD-INTENT-01 schema validation for intent.yaml claims.

Validates the canonical claim shape:

    INT-NNN:
      version: X.Y.Z
      status: draft | active | deprecated
      statement: "..."             # required
      rationale: "..."             # optional in CSD; recommended
      test:
        scope: unit | integration | e2e | llm
        component: "..."
        type: invariant | behavior | contract
      criticality: critical | high | medium | low

The legacy flat shape (top-level `scope:` instead of nested `test.scope`) is
accepted with a warning so projects can migrate incrementally.
"""

from __future__ import annotations

import re
from collections.abc import Hashable
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
    "DuplicateKeyError",
    "check_schema",
    "effective_scope",
    "parse_intent_yaml",
    "top_level_keys",
]

# Accept either canonical `INT-NNN` (CSD-INTENT-01 §3.1) or our extended
# `INT-PREFIX-NNN` style for multi-module monorepos. Both are valid here.
ID_PATTERN = re.compile(r"^INT-[A-Z0-9-]+$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

VALID_STATUS = {"draft", "active", "deprecated"}
# `llm` is CSD-INTENT-01 section 3.3's judged scope: a claim a runner cannot decide,
# attested by a reviewer's recorded verdict in its review record rather than by a test.
VALID_SCOPE = {"unit", "integration", "e2e", "llm"}
VALID_TYPE = {"invariant", "behavior", "contract"}
VALID_CRITICALITY = {"critical", "high", "medium", "low"}

# Top-level fields required on every claim per CSD-INTENT-01 §4.1.
# (id is implicit from the YAML key, so we don't check it separately.)
REQUIRED_TOP = {"version", "status", "statement", "criticality"}


_MERGE_TAG = "tag:yaml.org,2002:merge"


class DuplicateKeyError(ValueError):
    """A mapping in intent.yaml declares the same key twice.

    YAML's own resolution is last-wins and silent, so a repeated claim id destroys
    the earlier claim before any check can see it: the claim stops being enforced
    and every marker written for it silently re-points at the survivor (issue #12).
    A duplicate id has no valid interpretation, so the parse refuses it.
    """

    def __init__(self, key: object, first_line: int, second_line: int) -> None:
        self.key = key
        self.first_line = first_line
        self.second_line = second_line
        super().__init__(
            f"duplicate key `{key}` (first declared on line {first_line}, "
            f"declared again on line {second_line}); YAML would silently keep only "
            f"the last one"
        )


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader that refuses a repeated mapping key instead of resolving last-wins."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        # Scan the raw key nodes before the base class flattens merge keys (`<<`),
        # so a legitimate merge-plus-override is not mistaken for a duplicate.
        seen: dict[Any, int] = {}
        for key_node, _ in node.value:
            if key_node.tag == _MERGE_TAG:
                continue  # `<<` is expanded by the base class, and an override is legal
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, Hashable):
                continue  # the base constructor reports unhashable keys itself
            line = key_node.start_mark.line + 1
            if key in seen:
                raise DuplicateKeyError(key, seen[key], line)
            seen[key] = line
        return super().construct_mapping(node, deep=deep)


def _load(path: Path) -> Any:
    """Load a YAML document, refusing duplicate mapping keys (`DuplicateKeyError`)."""
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=_UniqueKeySafeLoader)


def parse_intent_yaml(path: Path) -> dict[str, dict[str, Any]]:
    """Parse an intent.yaml. Returns {claim_id: claim_dict}. Non-INT keys ignored.

    Raises `DuplicateKeyError` when the file declares the same key twice: dropping
    one of them silently is never the right answer (issue #12).
    """
    data = _load(path) or {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for key, value in data.items():
        if isinstance(key, str) and key.startswith("INT-") and isinstance(value, dict):
            out[key] = value
    return out


def top_level_keys(path: Path) -> list[str]:
    """Sorted top-level YAML keys, for diagnosing a zero-claims schema mismatch."""
    data = _load(path) or {}
    if not isinstance(data, dict):
        return []
    return sorted(str(key) for key in data.keys())


def effective_scope(claim: dict[str, Any]) -> str | None:
    """The claim's scope, from the nested `test` block or the legacy top-level field.

    The single reader of a claim's scope: callers that re-derive it drop the type
    guards below and traceback on a malformed `test:` value instead of reporting it.
    """
    return _scope_and_test(claim)[0]


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
