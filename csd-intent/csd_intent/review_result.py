"""The latest judgement and its freshness at a repository read."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["ReviewResult"]


@dataclass(frozen=True)
class ReviewResult:
    """Only a current PASS attests a claim."""

    state: Literal["pass", "fail", "stale", "unreviewed", "unresolvable"]
    reason: str
    verdict: str = ""
    commit: str = ""
    evidence: tuple[str, ...] = ()
    judgement: str = ""
