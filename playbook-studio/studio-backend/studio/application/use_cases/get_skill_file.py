"""Use case: read one file from a skill folder."""

from __future__ import annotations

from studio.application.ports.outbound.playbook_repository import PlaybookRepository
from studio.logging import get_logger

__all__ = ["GetSkillFile"]

logger = get_logger(__name__)


class GetSkillFile:
    """Returns a skill file's content. Implements GetSkillFilePort."""

    def __init__(self, repository: PlaybookRepository) -> None:
        self._repository = repository

    def execute(self, *, name: str, rel_path: str) -> str:
        """Return the file content (text)."""
        logger.debug("Reading skill file %s/%s", name, rel_path)
        return self._repository.read_skill_file(name=name, rel_path=rel_path)
