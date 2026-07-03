"""Mapping from domain exceptions to HTTP status codes."""

from __future__ import annotations

from studio.domain.exceptions.entity_not_found_error import EntityNotFoundError
from studio.domain.exceptions.generated_section_error import GeneratedSectionError
from studio.domain.exceptions.validation_failed_error import ValidationFailedError

__all__ = ["STATUS_MAP", "DEFAULT_STATUS"]

STATUS_MAP: dict[type[Exception], int] = {
    EntityNotFoundError: 404,
    GeneratedSectionError: 409,
    ValidationFailedError: 422,
}
DEFAULT_STATUS = 500
