"""REF routes: detail and gated section editing."""

from __future__ import annotations

from fastapi import APIRouter

from studio.adapters.inbound.http.dependencies import ContainerDep
from studio.adapters.inbound.http.dtos.create_ref_request import CreateRefRequest
from studio.adapters.inbound.http.dtos.ref_detail_response import RefDetailResponse
from studio.adapters.inbound.http.dtos.update_document_request import UpdateDocumentRequest
from studio.adapters.inbound.http.dtos.update_section_request import UpdateSectionRequest
from studio.adapters.inbound.http.dtos.validation_report_response import ValidationReportResponse
from studio.adapters.inbound.http.mappers.ref_mapper import map_ref
from studio.adapters.inbound.http.mappers.validation_mapper import map_validation_report

__all__ = ["router"]

router = APIRouter()


@router.post("/refs", response_model=RefDetailResponse, status_code=201)
async def create_ref(request: CreateRefRequest, container: ContainerDep) -> RefDetailResponse:
    """Author a new REF from the canonical template; gated like every edit."""
    ref = container.create_ref().execute(
        name=request.name,
        domain=request.domain,
        title=request.title,
        summary=request.summary,
    )
    return map_ref(ref)


@router.get("/refs/{name}", response_model=RefDetailResponse)
async def get_ref(name: str, container: ContainerDep) -> RefDetailResponse:
    """Return one parsed REF by name (e.g. REF-Python)."""
    return map_ref(container.get_ref().execute(name=name))


@router.put("/refs/{name}", response_model=ValidationReportResponse)
async def update_ref_document(
    name: str,
    request: UpdateDocumentRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Replace the whole document; the edit survives only if the gates pass."""
    report = container.update_ref_document().execute(ref_name=name, raw=request.raw)
    return map_validation_report(report)


@router.put("/refs/{name}/sections/{number}", response_model=ValidationReportResponse)
async def update_ref_section(
    name: str,
    number: int,
    request: UpdateSectionRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Write a section body; the edit survives only if the validation gates pass."""
    report = container.update_ref_section().execute(
        ref_name=name, number=number, body=request.body
    )
    return map_validation_report(report)
