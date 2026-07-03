"""Outbound port: read and write the playbook checkout."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from studio.domain.model.intent_claim import IntentClaim
from studio.domain.model.ref_doc import RefDoc
from studio.domain.model.reference_edge import ReferenceEdge
from studio.domain.model.skill_doc import SkillDoc

__all__ = ["PlaybookRepository"]


@runtime_checkable
class PlaybookRepository(Protocol):
    """Parses the playbook folder into domain objects and writes section edits."""

    def list_refs(self) -> list[RefDoc]: ...

    def get_ref(self, *, name: str) -> RefDoc: ...

    def list_skills(self) -> list[SkillDoc]: ...

    def list_claims(self) -> list[IntentClaim]: ...

    def list_edges(self) -> list[ReferenceEdge]: ...

    def write_ref_section(self, *, ref_name: str, number: int, body: str) -> RefDoc: ...
