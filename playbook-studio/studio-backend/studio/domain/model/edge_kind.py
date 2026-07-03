"""Kinds of edges in the playbook reference graph."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["EdgeKind"]


class EdgeKind(StrEnum):
    """How one playbook artifact references another."""

    PLAYBOOK_TO_REF = "playbook-to-ref"
    REF_TO_REF = "ref-to-ref"
    SKILL_TO_REF = "skill-to-ref"
