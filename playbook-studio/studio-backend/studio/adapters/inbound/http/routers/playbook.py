"""Playbook document routes."""

from __future__ import annotations

from fastapi import APIRouter

from studio.adapters.inbound.http.dependencies import ContainerDep
from studio.adapters.inbound.http.dtos.playbook_response import PlaybookResponse
from studio.adapters.inbound.http.dtos.update_document_request import UpdateDocumentRequest
from studio.adapters.inbound.http.dtos.validation_report_response import ValidationReportResponse
from studio.adapters.inbound.http.mappers.playbook_mapper import map_playbook
from studio.adapters.inbound.http.mappers.validation_mapper import map_validation_report

__all__ = ["router"]

router = APIRouter()


@router.get("/playbook", response_model=PlaybookResponse)
async def get_playbook(container: ContainerDep) -> PlaybookResponse:
    """Return AI-PLAYBOOK.md parsed into titled sections."""
    return map_playbook(container.get_playbook().execute())


@router.put("/playbook", response_model=ValidationReportResponse)
async def update_playbook(
    request: UpdateDocumentRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Replace AI-PLAYBOOK.md; the edit survives only if the gates pass."""
    report = container.update_playbook_document().execute(raw=request.raw)
    return map_validation_report(report)
