"""Response DTO for one Skill."""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["SkillResponse"]


class SkillResponse(BaseModel):
    """A parsed SKILL.md returned over HTTP."""

    name: str
    description: str
    refs: list[str]
    raw: str
    body: str
