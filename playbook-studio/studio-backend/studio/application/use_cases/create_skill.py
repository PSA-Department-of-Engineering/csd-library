"""Use case: author a new Skill behind the validation gate."""

from __future__ import annotations

import re

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.invalid_ref_input_error import InvalidRefInputError
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.skill_doc import SkillDoc
from studio.logging import get_logger

__all__ = ["CreateSkill"]

logger = get_logger(__name__)

_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class CreateSkill:
    """Scaffolds via the playbook's own bootstrap-skill skill. Implements CreateSkillPort.

    bootstrap-skill is a three-artifact transaction (SKILL.md, playbook table
    row, regenerated back-links); this use case snapshots everything it can
    touch and restores all of it if the gates reject the result.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, name: str, description: str, refs: list[str]) -> SkillDoc:
        """Scaffold skill + table row + back-links; roll all three back on failure."""
        if not _NAME_RE.match(name):
            raise InvalidRefInputError(f"skill name must be kebab-case: {name!r}")
        if not description.strip():
            raise InvalidRefInputError("description is required")

        playbook_before = self._repository.get_playbook().raw
        refs_before = {r: self._repository.get_ref(name=r).raw for r in refs}

        logger.info("Scaffolding skill %s via bootstrap-skill (refs=%s)", name, refs)
        skill = self._repository.scaffold_skill(
            name=name, description=description.strip(), refs=refs
        )
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for new skill %s; rolling back", name)
            self._repository.delete_skill_document(name=name)
            self._repository.write_playbook_document(raw=playbook_before)
            for ref_name, raw in refs_before.items():
                self._repository.write_ref_document(ref_name=ref_name, raw=raw)
            raise ValidationFailedError(report)
        logger.info("New skill %s accepted by validation gates", name)
        return skill
