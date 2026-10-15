"""Read a claim's latest judgement against the claim as it reads."""
from __future__ import annotations

import datetime
import hashlib
import json
from collections.abc import Mapping

from .review_result import ReviewResult
from .review_schema import check_review

__all__ = ["claim_digest", "read_review"]

def claim_digest(claim: Mapping[str, object]) -> str:
    """SHA-256 of the claim's meaning: every field except its `review` and `status`.

    The digest covers parsed values as canonical JSON (sorted keys, no spaces, dates in
    ISO 8601), so YAML layout and key order never change it. A value with no canonical
    form, a non-string mapping key, a set or a cycle, raises ValueError.
    """
    meaning = {key: value for key, value in claim.items() if key not in {"review", "status"}}
    text = json.dumps(_canonical(meaning, ()), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_review(claim: Mapping[str, object]) -> ReviewResult:
    """Compare the recorded digest with the claim's digest as it reads now."""
    try:
        digest = claim_digest(claim)
    except ValueError as exc:
        return ReviewResult("unresolvable", f"the claim has no digest: {exc}")
    record = claim.get("review")
    if record is None:
        return ReviewResult("unreviewed", f"no review recorded; the claim's digest is {digest}",
                            claim=digest)
    problems = check_review(record, "llm")
    if problems:
        return ReviewResult("unresolvable", "; ".join(problems), claim=digest)
    assert isinstance(record, Mapping)
    verdict = str(record["verdict"])
    if record["claim"] != digest:
        return ReviewResult("stale", f"the claim changed since its review; its digest is {digest}",
                            verdict, digest)
    return ReviewResult("pass" if verdict == "PASS" else "fail", "recorded " + verdict,
                        verdict, digest)


def _canonical(value: object, ancestors: tuple[int, ...]) -> object:
    if isinstance(value, (Mapping, list)):
        if id(value) in ancestors:
            raise ValueError("a value contains itself")
        inner = (*ancestors, id(value))
        if isinstance(value, list):
            return [_canonical(item, inner) for item in value]
        keys = [key for key in value if not isinstance(key, str)]
        if keys:
            raise ValueError(f"mapping key {keys[0]!r} is not a string; quote it")
        return {key: _canonical(item, inner) for key, item in value.items()}
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise ValueError(f"a {type(value).__name__} value has no canonical form")
