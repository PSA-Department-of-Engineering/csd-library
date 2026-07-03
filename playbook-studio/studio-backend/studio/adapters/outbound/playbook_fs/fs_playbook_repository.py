"""Filesystem-backed PlaybookRepository."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from studio.domain.exceptions.entity_not_found_error import EntityNotFoundError
from studio.domain.model.edge_kind import EdgeKind
from studio.domain.model.intent_claim import IntentClaim
from studio.domain.model.playbook_doc import PlaybookDoc
from studio.domain.model.playbook_section import PlaybookSection
from studio.domain.model.ref_doc import RefDoc
from studio.domain.model.ref_domain import RefDomain
from studio.domain.model.ref_section import RefSection
from studio.domain.model.reference_edge import ReferenceEdge
from studio.domain.model.skill_doc import SkillDoc
from studio.logging import get_logger

__all__ = ["FsPlaybookRepository"]

logger = get_logger(__name__)

_PLAYBOOK_NODE_ID = "AI-PLAYBOOK"
_GENERATED_SECTION_TITLE = "Skills that instantiate this REF"

_SECTION_RE = re.compile(r"^## (\d+)\. (.+?)\s*$")
_FENCE_RE = re.compile(r"^(```|~~~)")
_TITLE_RE = re.compile(r"^# REF: (.+?)\s*$")
_BARE_REF_RE = re.compile(r"`(REF-[A-Z][A-Za-z0-9-]*)(?:\.md)?`")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """(frontmatter mapping, body) - frontmatter empty if absent."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = yaml.safe_load("".join(lines[1:i])) or {}
            return fm, "".join(lines[i + 1:])
    return {}, text


def _strip_fences(text: str) -> str:
    """Blank out fenced code blocks so scans don't match example content."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


class FsPlaybookRepository:
    """Parses REFs, skills, claims, and edges from a playbook checkout."""

    def __init__(self, playbook_root: Path) -> None:
        self._root = playbook_root

    # -- reads --------------------------------------------------------------

    def get_playbook(self) -> PlaybookDoc:
        path = self._root / "AI-PLAYBOOK.md"
        if not path.is_file():
            raise EntityNotFoundError("playbook", "AI-PLAYBOOK.md")
        lines = path.read_text(encoding="utf-8").splitlines()

        title = "AI Playbook"
        sections: list[PlaybookSection] = []
        in_fence = False
        current: str | None = None
        buffer: list[str] = []
        for line in lines:
            if _FENCE_RE.match(line):
                in_fence = not in_fence
            if not in_fence and line.startswith("# ") and not line.startswith("## "):
                title = line[2:].strip()
                continue
            if not in_fence and line.startswith("## "):
                if current is not None:
                    body = "\n".join(buffer).strip("\n")
                    sections.append(PlaybookSection(title=current, body=body))
                current = line[3:].strip()
                buffer = []
            elif current is not None:
                buffer.append(line)
        if current is not None:
            sections.append(PlaybookSection(title=current, body="\n".join(buffer).strip("\n")))

        return PlaybookDoc(title=title, sections=tuple(sections))

    def list_refs(self) -> list[RefDoc]:
        return [self._parse_ref(p) for p in sorted(self._root.glob("REF-*.md"))]

    def get_ref(self, *, name: str) -> RefDoc:
        path = self._root / f"{name}.md"
        if not path.is_file() or not name.startswith("REF-"):
            raise EntityNotFoundError("REF", name)
        return self._parse_ref(path)

    def list_skills(self) -> list[SkillDoc]:
        out: list[SkillDoc] = []
        for skill_md in sorted((self._root / "skills").glob("*/SKILL.md")):
            fm, _ = _split_frontmatter(skill_md.read_text(encoding="utf-8"))
            name = fm.get("name") or skill_md.parent.name
            out.append(SkillDoc(
                name=str(name),
                description=str(fm.get("description", "")),
                refs=tuple(str(r) for r in (fm.get("refs") or [])),
            ))
        return out

    def list_claims(self) -> list[IntentClaim]:
        intent_path = self._root / "intent.yaml"
        if not intent_path.is_file():
            return []
        spec = yaml.safe_load(intent_path.read_text(encoding="utf-8")) or {}
        return [
            IntentClaim(
                claim_id=claim_id,
                statement=str(claim.get("statement", "")),
                rationale=str(claim.get("rationale", "")),
                criticality=str(claim.get("criticality", "")),
                status=str(claim.get("status", "")),
            )
            for claim_id, claim in spec.items()
            if isinstance(claim, dict)
        ]

    def list_edges(self) -> list[ReferenceEdge]:
        ref_names = {p.stem for p in self._root.glob("REF-*.md")}
        edges: set[ReferenceEdge] = set()

        playbook_md = self._root / "AI-PLAYBOOK.md"
        if playbook_md.is_file():
            playbook_text = _strip_fences(playbook_md.read_text(encoding="utf-8"))
            for target in _BARE_REF_RE.findall(playbook_text):
                if target in ref_names:
                    edges.add(ReferenceEdge(_PLAYBOOK_NODE_ID, target, EdgeKind.PLAYBOOK_TO_REF))

        for ref_path in self._root.glob("REF-*.md"):
            body = _strip_fences(ref_path.read_text(encoding="utf-8"))
            for target in _BARE_REF_RE.findall(body):
                if target in ref_names and target != ref_path.stem:
                    edges.add(ReferenceEdge(ref_path.stem, target, EdgeKind.REF_TO_REF))

        for skill in self.list_skills():
            for target in skill.refs:
                if target in ref_names:
                    edges.add(ReferenceEdge(skill.name, target, EdgeKind.SKILL_TO_REF))

        return sorted(edges, key=lambda e: (e.kind, e.source, e.target))

    # -- writes -------------------------------------------------------------

    def write_ref_section(self, *, ref_name: str, number: int, body: str) -> RefDoc:
        path = self._root / f"{ref_name}.md"
        if not path.is_file():
            raise EntityNotFoundError("REF", ref_name)
        text = path.read_text(encoding="utf-8")
        span = self._section_span(text, number)
        if span is None:
            raise EntityNotFoundError("section", f"{ref_name} §{number}")
        start, end = span
        lines = text.splitlines()
        new_body = body.strip("\n").splitlines()
        new_lines = lines[: start + 1] + [""] + new_body + [""] + lines[end:]
        path.write_text("\n".join(new_lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
        logger.info("Wrote %s section %d (%d body lines)", ref_name, number, len(new_body))
        return self._parse_ref(path)

    # -- parsing ------------------------------------------------------------

    def _parse_ref(self, path: Path) -> RefDoc:
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        domain = RefDomain(str(fm.get("domain", RefDomain.PRACTICE)))
        lines = body.splitlines()

        title = path.stem
        summary = ""
        for line in lines:
            if not line.strip():
                continue
            m = _TITLE_RE.match(line)
            if m and title == path.stem:
                title = m.group(1)
                continue
            if line.startswith(">") and not summary:
                summary = line.lstrip("> ").strip()
                break
            if title != path.stem:
                break

        sections: list[RefSection] = []
        in_fence = False
        current: tuple[int, str] | None = None
        buffer: list[str] = []
        for line in lines:
            if _FENCE_RE.match(line):
                in_fence = not in_fence
            m = None if in_fence else _SECTION_RE.match(line)
            if m:
                if current is not None:
                    sections.append(self._make_section(current, buffer))
                current = (int(m.group(1)), m.group(2))
                buffer = []
            elif current is not None:
                buffer.append(line)
        if current is not None:
            sections.append(self._make_section(current, buffer))

        return RefDoc(
            name=path.stem,
            domain=domain,
            title=title,
            summary=summary,
            sections=tuple(sections),
        )

    @staticmethod
    def _make_section(header: tuple[int, str], buffer: list[str]) -> RefSection:
        number, section_title = header
        return RefSection(
            number=number,
            title=section_title,
            body="\n".join(buffer).strip("\n"),
            generated=section_title == _GENERATED_SECTION_TITLE,
        )

    @staticmethod
    def _section_span(text: str, number: int) -> tuple[int, int] | None:
        """(heading line index, exclusive end line index) of section `number`."""
        lines = text.splitlines()
        in_fence = False
        start: int | None = None
        for i, line in enumerate(lines):
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = _SECTION_RE.match(line)
            if start is None:
                if m and int(m.group(1)) == number:
                    start = i
            elif line.startswith("## "):
                return start, i
        if start is None:
            return None
        return start, len(lines)
