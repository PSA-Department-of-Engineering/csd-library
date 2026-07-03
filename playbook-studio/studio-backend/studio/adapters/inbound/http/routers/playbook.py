"""Playbook document route."""

from __future__ import annotations

from fastapi import APIRouter

from studio.adapters.inbound.http.dependencies import ContainerDep
from studio.adapters.inbound.http.dtos.playbook_response import PlaybookResponse
from studio.adapters.inbound.http.mappers.playbook_mapper import map_playbook

__all__ = ["router"]

router = APIRouter()


@router.get("/playbook", response_model=PlaybookResponse)
async def get_playbook(container: ContainerDep) -> PlaybookResponse:
    """Return AI-PLAYBOOK.md parsed into titled sections."""
    return map_playbook(container.get_playbook().execute())
