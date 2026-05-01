"""Intent.yaml schema parsing + validation."""

from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED_FIELDS = {"statement", "rationale", "criticality", "scope"}
VALID_CRITICALITY = {"critical", "high", "medium", "low"}
VALID_SCOPE = {"unit", "integration", "e2e", "system"}


def parse_intent_yaml(path: Path) -> dict[str, dict[str, object]]:
    """Parse intent.yaml. Returns {claim_id: {field: value}} for INT-NNN keys.

    Non-INT-* keys (e.g. document-level metadata) are ignored. Each field's value
    keeps its YAML-native type (str, int, list, etc.) — useful for `tests:` lists,
    nested annotations, etc.
    """
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, dict[str, object]] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            continue
        if not key.startswith("INT-"):
            continue
        if not isinstance(value, dict):
            continue
        out[key] = value
    return out


def check_schema(claims: dict[str, dict[str, object]]) -> list[str]:
    """Return list of human-readable schema violations. Empty list = pass."""
    violations: list[str] = []
    for cid, fields in claims.items():
        missing = REQUIRED_FIELDS - set(fields.keys())
        if missing:
            violations.append(f"{cid}: missing fields {sorted(missing)}")
        crit = fields.get("criticality")
        if crit and crit not in VALID_CRITICALITY:
            violations.append(f"{cid}: invalid criticality `{crit}` (allowed {sorted(VALID_CRITICALITY)})")
        scope = fields.get("scope")
        if scope and scope not in VALID_SCOPE:
            violations.append(f"{cid}: invalid scope `{scope}` (allowed {sorted(VALID_SCOPE)})")
    return violations
