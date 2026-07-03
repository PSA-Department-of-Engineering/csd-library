"""Skill routes: detail, files, gated editing, gated creation, runtime install."""

from __future__ import annotations

from fastapi import APIRouter

from studio.adapters.inbound.http.dependencies import ContainerDep
from studio.adapters.inbound.http.dtos.create_skill_request import CreateSkillRequest
from studio.adapters.inbound.http.dtos.skill_file_response import SkillFileResponse
from studio.adapters.inbound.http.dtos.skill_response import SkillResponse
from studio.adapters.inbound.http.dtos.skill_status_response import SkillStatusResponse
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
    status = container.get_skill_status().execute(name=skill.name)
    return map_skill(skill, status)


@router.get("/skills/{name}", response_model=SkillResponse)
async def get_skill(name: str, container: ContainerDep) -> SkillResponse:
    """Return one parsed skill, its file list, and its runtime state."""
    skill = container.get_skill().execute(name=name)
    status = container.get_skill_status().execute(name=name)
    return map_skill(skill, status)


@router.put("/skills/{name}", response_model=ValidationReportResponse)
async def update_skill_document(
    name: str,
    request: UpdateDocumentRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Replace the whole SKILL.md; the edit survives only if the gates pass."""
    report = container.update_skill_document().execute(name=name, raw=request.raw)
    return map_validation_report(report)


@router.get("/skills/{name}/files/{rel_path:path}", response_model=SkillFileResponse)
async def get_skill_file(name: str, rel_path: str, container: ContainerDep) -> SkillFileResponse:
    """Return one file from the skill folder."""
    content = container.get_skill_file().execute(name=name, rel_path=rel_path)
    return SkillFileResponse(path=rel_path, content=content)


@router.put("/skills/{name}/files/{rel_path:path}", response_model=ValidationReportResponse)
async def update_skill_file(
    name: str,
    rel_path: str,
    request: UpdateDocumentRequest,
    container: ContainerDep,
) -> ValidationReportResponse:
    """Write one skill file; the edit survives only if the gates pass."""
    report = container.update_skill_file().execute(
        name=name, rel_path=rel_path, content=request.raw
    )
    return map_validation_report(report)


@router.post("/skills/{name}/install", response_model=SkillStatusResponse)
async def install_skill(name: str, container: ContainerDep) -> SkillStatusResponse:
    """Copy the master skill folder into the Claude runtime's skills directory."""
    status = container.install_skill().execute(name=name)
    return SkillStatusResponse(installed=status.installed, in_sync=status.in_sync)
