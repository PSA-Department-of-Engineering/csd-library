"""Use case: replace AI-PLAYBOOK.md behind the validation gate."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["UpdatePlaybookDocument"]

logger = get_logger(__name__)


class UpdatePlaybookDocument:
    """Gated editing of the entry-point document itself (routing, violations).

    Implements UpdatePlaybookDocumentPort. INT-LAYER-003 keeps the Available
    Skills table honest; a table edit that orphans a skill rolls back.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, raw: str) -> ValidationReport:
        """Write the full document; restore the original and raise if gates fail."""
        original = self._repository.get_playbook().raw

        logger.info("Rewriting AI-PLAYBOOK.md")
        self._repository.write_playbook_document(raw=raw)
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for AI-PLAYBOOK.md; rolling back")
            self._repository.write_playbook_document(raw=original)
            raise ValidationFailedError(report)
        logger.info("AI-PLAYBOOK.md rewrite accepted by validation gates")
        return report
