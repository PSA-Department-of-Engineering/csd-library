"""@intent decorator — links a test function to one or more INT-NNN claims.

Mirrors CSD's annotation pattern from CSD-TEST-03 §2.2 (Java's `@IntentTest`).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable)


def intent(*claim_ids: str) -> Callable[[F], F]:
    """Mark a test function as serving one or more intent claims.

    Usage:
        @intent("INT-001")
        def test_unique_ids(...): ...

        @intent("INT-021", "INT-022")  # multi-claim
        def test_referential_integrity(...): ...

    The decorator just attaches metadata; pytest behavior is unchanged.
    Schema/coverage meta-tests inspect this metadata via `func.__csd_intents__`.
    """
    if not claim_ids:
        raise ValueError("@intent() requires at least one claim ID")
    for cid in claim_ids:
        if not cid.startswith("INT-"):
            raise ValueError(f"intent ID must start with 'INT-': got {cid!r}")

    def wrap(func: F) -> F:
        existing = getattr(func, "__csd_intents__", ())
        func.__csd_intents__ = tuple(existing) + tuple(claim_ids)  # type: ignore[attr-defined]
        return func

    return wrap
