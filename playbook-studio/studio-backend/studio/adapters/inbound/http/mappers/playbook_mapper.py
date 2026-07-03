"""Mapper: domain PlaybookDoc to PlaybookResponse DTO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from studio.adapters.inbound.http.dtos.playbook_response import PlaybookResponse
from studio.adapters.inbound.http.dtos.playbook_section_response import PlaybookSectionResponse

if TYPE_CHECKING:
    from studio.domain.model.playbook_doc import PlaybookDoc

__all__ = ["map_playbook"]


def map_playbook(doc: PlaybookDoc) -> PlaybookResponse:
    """Convert the playbook document to its response DTO."""
    return PlaybookResponse(
        title=doc.title,
        sections=[PlaybookSectionResponse(title=s.title, body=s.body) for s in doc.sections],
    )
