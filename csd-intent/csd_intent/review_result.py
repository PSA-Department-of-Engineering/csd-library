"""The verdict and freshness of one repository review."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["ReviewResult"]

@dataclass(frozen=True)
class ReviewResult:
    """A derived read result; the recorded fields are commit and verdict."""
    state: Literal["pass", "fail", "stale", "unreviewed", "unresolvable"]
    reason: str
    verdict: str = ""
    commit: str = ""
