"""Use case: run the playbook validation gates on demand."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["RunValidation"]

logger = get_logger(__name__)


class RunValidation:
    """Runs intent tests + link checker. Implements RunValidationPort."""

    def __init__(self, validator: PlaybookValidator) -> None:
        self._validator = validator

    def execute(self) -> ValidationReport:
        """Run both gates and return the combined report."""
        report = self._validator.validate()
        if report.ok:
            logger.info("Playbook validation passed")
        else:
            logger.warning(
                "Playbook validation failed (tests_passed=%s, links_ok=%s)",
                report.tests_passed,
                report.links_ok,
            )
        return report
