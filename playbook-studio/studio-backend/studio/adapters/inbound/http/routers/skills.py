"""Skill routes: detail, gated editing, gated creation."""

from __future__ import annotations

from fastapi import APIRouter

from studio.adapters.inbound.http.dependencies import ContainerDep
from studio.adapters.inbound.http.dtos.create_skill_request import CreateSkillRequest
from studio.adapters.inbound.http.dtos.skill_response import SkillResponse
from studio.adapters.inbound.http.dtos.update_document_request import UpdateDocumentRequest
from studio.adapters.inbound.http.dtos.validation_report_response import ValidationReportResponse
from studio.adapters.inbound.http.mappers.skill_mapper import map_skill
from studio.adapters.inbound.http.mappers.validation_mapper import map_validation_report

__all__ = ["router"]

router = APIRouter()


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def create_skill(request: CreateSkillRequest, container: ContainerDep) -> SkillResponse:
    """Run the bootstrap-skill transaction; gated like every edit."""
    skill = container.create_skill().execute(
        name=request.name, description=request.description, refs=request.refs
    )
    return map_skill(skill)


@router.get("/skills/{name}", response_model=SkillResponse)
async def get_skill(name: str, container: ContainerDep) -> SkillResponse:
    """Return one parsed skill by name."""
    return map_skill(container.get_skill().execute(name=name))


@router.put("/skills/{name}", response_model=ValidationReportResponse)
async def update_skill_document(
    name: str,
    request: UpdateDocumentRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Replace the whole SKILL.md; the edit survives only if the gates pass."""
    report = container.update_skill_document().execute(name=name, raw=request.raw)
    return map_validation_report(report)
