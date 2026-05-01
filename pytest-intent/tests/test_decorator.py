"""Tests for the @intent decorator."""

from __future__ import annotations

import pytest

from pytest_intent import intent


def test_intent_attaches_single_claim_id() -> None:
    @intent("INT-001")
    def t():
        pass

    assert t.__csd_intents__ == ("INT-001",)


def test_intent_attaches_multiple_claim_ids() -> None:
    @intent("INT-001", "INT-002")
    def t():
        pass

    assert t.__csd_intents__ == ("INT-001", "INT-002")


def test_intent_stacks_with_repeated_decoration() -> None:
    @intent("INT-002")
    @intent("INT-001")
    def t():
        pass

    assert t.__csd_intents__ == ("INT-001", "INT-002")


def test_intent_requires_at_least_one_id() -> None:
    with pytest.raises(ValueError, match="at least one"):
        intent()


def test_intent_rejects_invalid_id_prefix() -> None:
    with pytest.raises(ValueError, match="must start with 'INT-'"):
        intent("BAD-001")


def test_intent_preserves_function_callability() -> None:
    @intent("INT-001")
    def t(x: int) -> int:
        return x * 2

    assert t(3) == 6
