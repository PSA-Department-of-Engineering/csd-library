"""The CSD-INTENT-01 per-claim review record."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import PurePosixPath

__all__ = ["check_review", "is_evidence_path"]

_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_FIELDS = {"verdict", "commit", "evidence", "reason"}


def is_evidence_path(value: object) -> bool:
    """Evidence names one repository-relative file, with forward slashes."""
    if not isinstance(value, str) or not value or any(c in value for c in "\\:*?[]\x00\n\r"):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in value.split("/"))


def check_review(record: object, scope: str | None) -> list[str]:
    """Validate a present review; an absent review is an attestation concern."""
    if not isinstance(record, Mapping):
        return ["review must be a mapping"]
    problems: list[str] = []
    if scope != "llm":
        problems.append("review requires test.scope: llm")
    missing = _FIELDS - record.keys()
    unknown = record.keys() - _FIELDS
    if missing:
        problems.append(f"review is missing {sorted(missing)}")
    if unknown:
        problems.append(f"review has unknown fields {sorted(str(key) for key in unknown)}")
    if record.get("verdict") not in ("PASS", "FAIL"):
        problems.append("review.verdict must be PASS or FAIL")
    commit = record.get("commit")
    if not isinstance(commit, str) or not _COMMIT.fullmatch(commit):
        problems.append("review.commit must be a full lowercase Git commit id")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(
        is_evidence_path(path) for path in evidence
    ):
        problems.append("review.evidence must name repository-relative files")
    elif len(evidence) != len(set(evidence)):
        problems.append("review.evidence must contain unique paths")
    reason = record.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        problems.append("review.reason must be a non-empty string")
    return problems
