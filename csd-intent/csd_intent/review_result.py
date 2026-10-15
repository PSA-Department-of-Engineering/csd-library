"""The verdict and freshness of one claim review."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["ReviewResult"]

@dataclass(frozen=True)
class ReviewResult:
    """A derived read result; `claim` is the digest a current record names."""
    state: Literal["pass", "fail", "stale", "unreviewed", "unresolvable"]
    reason: str
    verdict: str = ""
    claim: str = ""
