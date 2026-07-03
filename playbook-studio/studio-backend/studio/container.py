"""Composition root: wires adapters and use cases."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from studio.adapters.outbound.playbook_fs.fs_playbook_repository import FsPlaybookRepository
from studio.adapters.outbound.playbook_fs.subprocess_playbook_validator import (
    SubprocessPlaybookValidator,
)
from studio.application.ports.inbound.get_graph_port import GetGraphPort
from studio.application.ports.inbound.get_ref_port import GetRefPort
from studio.application.ports.inbound.list_claims_port import ListClaimsPort
from studio.application.ports.inbound.run_validation_port import RunValidationPort
from studio.application.ports.inbound.update_ref_section_port import UpdateRefSectionPort
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.application.use_cases.get_graph import GetGraph
from studio.application.use_cases.get_ref import GetRef
from studio.application.use_cases.list_claims import ListClaims
from studio.application.use_cases.run_validation import RunValidation
from studio.application.use_cases.update_ref_section import UpdateRefSection

__all__ = ["Container", "resolve_playbook_root"]

_T = TypeVar("_T")

_PLAYBOOK_ROOT_ENV = "STUDIO_PLAYBOOK_ROOT"


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
    ) -> None:
        root = playbook_root or resolve_playbook_root()
        self._repository = FsPlaybookRepository(root)
        self._validator = validator or SubprocessPlaybookValidator(root)

    def get_graph(self) -> GetGraphPort:
        return _check(GetGraph(self._repository), GetGraphPort)

    def get_ref(self) -> GetRefPort:
        return _check(GetRef(self._repository), GetRefPort)

    def update_ref_section(self) -> UpdateRefSectionPort:
        return _check(UpdateRefSection(self._repository, self._validator), UpdateRefSectionPort)

    def list_claims(self) -> ListClaimsPort:
        return _check(ListClaims(self._repository), ListClaimsPort)

    def run_validation(self) -> RunValidationPort:
        return _check(RunValidation(self._validator), RunValidationPort)
