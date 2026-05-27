"""Demo test attesting INT-001. Run csd-intent against this directory to see it work."""

from __future__ import annotations

from pytest_intent import intent


@intent("INT-001")
def test_calculator_sums_integers() -> None:
    assert 2 + 3 == 5
