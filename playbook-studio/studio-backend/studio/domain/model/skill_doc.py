"""A Skill master document."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SkillDoc"]


@dataclass(frozen=True)
class SkillDoc:
    """A skills/<name>/SKILL.md, identified by its frontmatter `name`."""

    name: str
    description: str
    refs: tuple[str, ...]
