"""Use case: replace a whole SKILL.md behind the validation gate."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["UpdateSkillDocument"]

logger = get_logger(__name__)


class UpdateSkillDocument:
    """Gated whole-document skill editing. Implements UpdateSkillDocumentPort.

    Frontmatter edits (refs, description) may desync the generated back-link
    sections; INT-LAYER-002/004 catch that and the edit rolls back, pointing
    the author at scripts/sync_backlinks.py.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, name: str, raw: str) -> ValidationReport:
        """Write the full document; restore the original and raise if gates fail."""
        original = self._repository.get_skill(name=name).raw

        logger.info("Rewriting skill %s (full document)", name)
        self._repository.write_skill_document(name=name, raw=raw)
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for skill %s; rolling back", name)
            self._repository.write_skill_document(name=name, raw=original)
            raise ValidationFailedError(report)
        logger.info("Rewrite of skill %s accepted by validation gates", name)
        return report
