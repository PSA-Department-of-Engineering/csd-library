"""Use case: edit one REF section behind the validation gate."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.entity_not_found_error import EntityNotFoundError
from studio.domain.exceptions.generated_section_error import GeneratedSectionError
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["UpdateRefSection"]

logger = get_logger(__name__)


class UpdateRefSection:
    """Trusted-output editing: write, validate, roll back on failure.

    Implements UpdateRefSectionPort. The edit only survives if the playbook's
    own deterministic gates (intent tests + link checker) still pass.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, ref_name: str, number: int, body: str) -> ValidationReport:
        """Write the section body; restore the original and raise if gates fail."""
        ref = self._repository.get_ref(name=ref_name)
        section = ref.section(number)
        if section is None:
            raise EntityNotFoundError("section", f"{ref_name} §{number}")
        if section.generated:
            raise GeneratedSectionError(ref_name, number)

        logger.info("Editing %s section %d", ref_name, number)
        self._repository.write_ref_section(ref_name=ref_name, number=number, body=body)
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for %s section %d; rolling back", ref_name, number)
            self._repository.write_ref_section(ref_name=ref_name, number=number, body=section.body)
            raise ValidationFailedError(report)
        logger.info("Edit to %s section %d accepted by validation gates", ref_name, number)
        return report
