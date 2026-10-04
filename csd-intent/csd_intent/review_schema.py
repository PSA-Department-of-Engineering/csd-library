"""The two fields in a claim's latest repository review."""
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
    if set(record) != {"commit", "verdict"}:
        problems.append("review requires exactly commit and verdict")
    if record.get("verdict") not in ("PASS", "FAIL"):
        problems.append("review verdict must be PASS or FAIL")
    sha = record.get("commit")
    if not isinstance(sha, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", sha):
        problems.append("review commit must be a full lowercase Git object ID")
    return problems
