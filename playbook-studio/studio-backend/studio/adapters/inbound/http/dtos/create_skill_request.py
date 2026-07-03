"""Request DTO for authoring a new Skill."""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["CreateSkillRequest"]


class CreateSkillRequest(BaseModel):
    """Inputs for the bootstrap-skill transaction."""

    name: str
    description: str
    refs: list[str]
