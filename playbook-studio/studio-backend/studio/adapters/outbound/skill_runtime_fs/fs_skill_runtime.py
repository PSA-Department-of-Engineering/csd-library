"""Filesystem-backed SkillRuntime."""

from __future__ import annotations

import shutil
from pathlib import Path

from studio.domain.exceptions.entity_not_found_error import EntityNotFoundError
from studio.domain.model.skill_status import SkillStatus
from studio.logging import get_logger

__all__ = ["FsSkillRuntime"]

logger = get_logger(__name__)

_IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc")


class FsSkillRuntime:
    """Copies skills/<name>/ into the runtime skills dir and compares state."""

    def __init__(self, playbook_root: Path, runtime_dir: Path) -> None:
        self._source_root = playbook_root / "skills"
        self._runtime_dir = runtime_dir

    def status(self, *, name: str) -> SkillStatus:
        source = self._source_root / name
        target = self._runtime_dir / name
        if not (target / "SKILL.md").is_file():
            return SkillStatus(installed=False, in_sync=False)
        return SkillStatus(installed=True, in_sync=self._same_content(source, target))

    def install(self, *, name: str) -> SkillStatus:
        source = self._source_root / name
        if not (source / "SKILL.md").is_file():
            raise EntityNotFoundError("skill", name)
        target = self._runtime_dir / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, ignore=_IGNORED)
        logger.info("Installed skill %s to %s", name, target)
        return self.status(name=name)

    def _same_content(self, source: Path, target: Path) -> bool:
        for src_file in sorted(source.rglob("*")):
            if not src_file.is_file() or "__pycache__" in src_file.parts:
                continue
            dst_file = target / src_file.relative_to(source)
            if not dst_file.is_file() or dst_file.read_bytes() != src_file.read_bytes():
                return False
        return True
