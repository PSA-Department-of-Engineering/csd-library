"""Use case: edit one skill file behind the validation gate."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["UpdateSkillFile"]

logger = get_logger(__name__)


class UpdateSkillFile:
    """Gated editing of any file inside a skill folder (scripts, themes, docs).

    Implements UpdateSkillFilePort. SKILL.md edits route here too when
    addressed as a file; the whole-document endpoint remains for convenience.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, name: str, rel_path: str, content: str) -> ValidationReport:
        """Write the file; restore the original and raise if gates fail."""
        original = self._repository.read_skill_file(name=name, rel_path=rel_path)

        logger.info("Editing skill file %s/%s", name, rel_path)
        self._repository.write_skill_file(name=name, rel_path=rel_path, content=content)
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for %s/%s; rolling back", name, rel_path)
            self._repository.write_skill_file(name=name, rel_path=rel_path, content=original)
            raise ValidationFailedError(report)
        logger.info("Edit to %s/%s accepted by validation gates", name, rel_path)
        return report
