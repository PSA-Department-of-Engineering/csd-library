"""The two fields in a claim's latest review."""
from __future__ import annotations

import re
from collections.abc import Mapping

__all__ = ["check_review"]

def check_review(record: object, scope: str | None = None) -> list[str]:
    """Validate the canonical review record on an llm claim."""
    if not isinstance(record, Mapping):
        return ["review must be a mapping"]
    problems = []
    if scope != "llm":
        problems.append("review is permitted only at llm scope")
    if set(record) != {"claim", "verdict"}:
        problems.append("review requires exactly claim and verdict")
    if record.get("verdict") not in ("PASS", "FAIL"):
        problems.append("review verdict must be PASS or FAIL")
    digest = record.get("claim")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        problems.append("review claim must be the claim's lowercase SHA-256 digest")
    return problems
