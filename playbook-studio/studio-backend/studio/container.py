"""Composition root: wires adapters and use cases."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from studio.adapters.outbound.playbook_fs.fs_playbook_repository import FsPlaybookRepository
from studio.adapters.outbound.playbook_fs.subprocess_playbook_validator import (
    SubprocessPlaybookValidator,
)
from studio.adapters.outbound.skill_runtime_fs.fs_skill_runtime import FsSkillRuntime
from studio.application.ports.inbound.create_ref_port import CreateRefPort
from studio.application.ports.inbound.create_skill_port import CreateSkillPort
from studio.application.ports.inbound.get_graph_port import GetGraphPort
from studio.application.ports.inbound.get_playbook_port import GetPlaybookPort
from studio.application.ports.inbound.get_ref_port import GetRefPort
from studio.application.ports.inbound.get_skill_file_port import GetSkillFilePort
from studio.application.ports.inbound.get_skill_port import GetSkillPort
from studio.application.ports.inbound.get_skill_status_port import GetSkillStatusPort
from studio.application.ports.inbound.install_skill_port import InstallSkillPort
from studio.application.ports.inbound.list_claims_port import ListClaimsPort
from studio.application.ports.inbound.run_validation_port import RunValidationPort
from studio.application.ports.inbound.update_playbook_document_port import (
    UpdatePlaybookDocumentPort,
)
from studio.application.ports.inbound.update_ref_document_port import UpdateRefDocumentPort
from studio.application.ports.inbound.update_ref_section_port import UpdateRefSectionPort
from studio.application.ports.inbound.update_skill_document_port import UpdateSkillDocumentPort
from studio.application.ports.inbound.update_skill_file_port import UpdateSkillFilePort
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.application.use_cases.create_ref import CreateRef
from studio.application.use_cases.create_skill import CreateSkill
from studio.application.use_cases.get_graph import GetGraph
from studio.application.use_cases.get_playbook import GetPlaybook
from studio.application.use_cases.get_ref import GetRef
from studio.application.use_cases.get_skill import GetSkill
from studio.application.use_cases.get_skill_file import GetSkillFile
from studio.application.use_cases.get_skill_status import GetSkillStatus
from studio.application.use_cases.install_skill import InstallSkill
from studio.application.use_cases.list_claims import ListClaims
from studio.application.use_cases.run_validation import RunValidation
from studio.application.use_cases.update_playbook_document import UpdatePlaybookDocument
from studio.application.use_cases.update_ref_document import UpdateRefDocument
from studio.application.use_cases.update_ref_section import UpdateRefSection
from studio.application.use_cases.update_skill_document import UpdateSkillDocument
from studio.application.use_cases.update_skill_file import UpdateSkillFile

__all__ = ["Container", "resolve_playbook_root"]

_T = TypeVar("_T")

_PLAYBOOK_ROOT_ENV = "STUDIO_PLAYBOOK_ROOT"
_RUNTIME_SKILLS_ENV = "STUDIO_RUNTIME_SKILLS_DIR"


def resolve_runtime_skills_dir() -> Path:
    """Runtime install dir: $STUDIO_RUNTIME_SKILLS_DIR, else ~/.claude/skills."""
    env = os.environ.get(_RUNTIME_SKILLS_ENV)
    if env:
        return Path(env)
    return Path.home() / ".claude" / "skills"


def resolve_playbook_root() -> Path:
    """Playbook checkout: $STUDIO_PLAYBOOK_ROOT, else the sibling-clone default.

    This file lives at <workspace>/csd-library/playbook-studio/studio-backend/studio/,
    and the playbook is the sibling checkout <workspace>/ai-coding-prompts.
    """
    env = os.environ.get(_PLAYBOOK_ROOT_ENV)
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[4] / "ai-coding-prompts"


def _check(instance: object, port: type[_T]) -> _T:
    if not isinstance(instance, port):
        raise TypeError(f"{type(instance).__name__} does not satisfy {port.__name__}")
    return instance


class Container:
    """Instantiates outbound adapters once and builds use cases on demand."""

    def __init__(
        self,
        playbook_root: Path | None = None,
        validator: PlaybookValidator | None = None,
        runtime_skills_dir: Path | None = None,
    ) -> None:
        root = playbook_root or resolve_playbook_root()
        self._repository = FsPlaybookRepository(root)
        self._validator = validator or SubprocessPlaybookValidator(root)
        runtime_dir = runtime_skills_dir or resolve_runtime_skills_dir()
        self._skill_runtime = FsSkillRuntime(root, runtime_dir)

    def get_graph(self) -> GetGraphPort:
        return _check(GetGraph(self._repository), GetGraphPort)

    def get_playbook(self) -> GetPlaybookPort:
        return _check(GetPlaybook(self._repository), GetPlaybookPort)

    def get_ref(self) -> GetRefPort:
        return _check(GetRef(self._repository), GetRefPort)

    def update_ref_section(self) -> UpdateRefSectionPort:
        return _check(UpdateRefSection(self._repository, self._validator), UpdateRefSectionPort)

    def update_ref_document(self) -> UpdateRefDocumentPort:
        return _check(UpdateRefDocument(self._repository, self._validator), UpdateRefDocumentPort)

    def create_ref(self) -> CreateRefPort:
        return _check(CreateRef(self._repository, self._validator), CreateRefPort)

    def create_skill(self) -> CreateSkillPort:
        return _check(CreateSkill(self._repository, self._validator), CreateSkillPort)

    def get_skill(self) -> GetSkillPort:
        return _check(GetSkill(self._repository), GetSkillPort)

    def update_skill_document(self) -> UpdateSkillDocumentPort:
        return _check(
            UpdateSkillDocument(self._repository, self._validator), UpdateSkillDocumentPort
        )

    def get_skill_status(self) -> GetSkillStatusPort:
        return _check(GetSkillStatus(self._skill_runtime), GetSkillStatusPort)

    def install_skill(self) -> InstallSkillPort:
        return _check(InstallSkill(self._skill_runtime), InstallSkillPort)

    def get_skill_file(self) -> GetSkillFilePort:
        return _check(GetSkillFile(self._repository), GetSkillFilePort)

    def update_skill_file(self) -> UpdateSkillFilePort:
        return _check(UpdateSkillFile(self._repository, self._validator), UpdateSkillFilePort)

    def update_playbook_document(self) -> UpdatePlaybookDocumentPort:
        return _check(
            UpdatePlaybookDocument(self._repository, self._validator), UpdatePlaybookDocumentPort
        )

    def list_claims(self) -> ListClaimsPort:
        return _check(ListClaims(self._repository), ListClaimsPort)

    def run_validation(self) -> RunValidationPort:
        return _check(RunValidation(self._validator), RunValidationPort)
