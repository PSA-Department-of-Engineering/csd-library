"""Canonical skeleton for a newly authored REF (REF-Authoring §3)."""

from __future__ import annotations

from studio.domain.model.ref_domain import RefDomain

__all__ = ["render_new_ref"]


def render_new_ref(*, domain: RefDomain, title: str, summary: str) -> str:
    """Template-conformant starting content: frontmatter, title, summary, §1."""
    return (
        "---\n"
        f"domain: {domain}\n"
        "---\n"
        "\n"
        f"# REF: {title}\n"
        "\n"
        f"> {summary}\n"
        "\n"
        "---\n"
        "\n"
        "## 1. Scope\n"
        "\n"
        "State the first rule set for this REF here.\n"
    )
