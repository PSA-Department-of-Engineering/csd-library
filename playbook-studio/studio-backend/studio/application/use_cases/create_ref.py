"""Use case: author a new REF behind the validation gate."""

from __future__ import annotations

import re

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.application.ports.outbound.playbook_validator import PlaybookValidator
from studio.domain.exceptions.invalid_ref_input_error import InvalidRefInputError
from studio.domain.exceptions.validation_failed_error import ValidationFailedError
from studio.domain.model.ref_doc import RefDoc
from studio.domain.model.ref_domain import RefDomain
from studio.logging import get_logger

__all__ = ["CreateRef"]

logger = get_logger(__name__)

_NAME_RE = re.compile(r"^REF-[A-Z][A-Za-z0-9-]*$")


class CreateRef:
    """Scaffolds via the playbook's own bootstrap-ref skill. Implements CreateRefPort.

    The template lives in the playbook, not here; the studio only runs the
    skill's deterministic script and wraps it in the gate + rollback.
    """

    def __init__(self, repository: PlaybookRepository, validator: PlaybookValidator) -> None:
        self._repository = repository
        self._validator = validator

    def execute(self, *, name: str, domain: str, title: str, summary: str) -> RefDoc:
        """Scaffold the file, run the gates, and remove it again if they fail."""
        if not _NAME_RE.match(name):
            raise InvalidRefInputError(f"REF name must match REF-<PascalCase>: {name!r}")
        try:
            RefDomain(domain)
        except ValueError as exc:
            raise InvalidRefInputError(f"unknown domain {domain!r}") from exc
        if not title.strip() or not summary.strip():
            raise InvalidRefInputError("title and summary are required")

        logger.info("Scaffolding %s via bootstrap-ref (domain=%s)", name, domain)
        ref = self._repository.scaffold_ref(
            name=name, domain=domain, title=title.strip(), summary=summary.strip()
        )
        report = self._validator.validate()
        if not report.ok:
            logger.warning("Validation failed for new %s; removing it", name)
            self._repository.delete_ref_document(ref_name=name)
            raise ValidationFailedError(report)
        logger.info("New %s accepted by validation gates", name)
        return ref
