"""Mapping from domain exceptions to HTTP status codes."""

from __future__ import annotations

from studio.domain.exceptions.already_exists_error import AlreadyExistsError
from studio.domain.exceptions.entity_not_found_error import EntityNotFoundError
from studio.domain.exceptions.generated_section_error import GeneratedSectionError
from studio.domain.exceptions.invalid_ref_input_error import InvalidRefInputError
from studio.domain.exceptions.validation_failed_error import ValidationFailedError

__all__ = ["STATUS_MAP", "DEFAULT_STATUS"]

STATUS_MAP: dict[type[Exception], int] = {
    AlreadyExistsError: 409,
    EntityNotFoundError: 404,
    GeneratedSectionError: 409,
    InvalidRefInputError: 400,
    ValidationFailedError: 422,
}
DEFAULT_STATUS = 500
