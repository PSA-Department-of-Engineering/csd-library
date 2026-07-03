"""One node of the playbook reference graph."""

from __future__ import annotations

from dataclasses import dataclass

from studio.domain.model.node_kind import NodeKind
from studio.domain.model.ref_domain import RefDomain

__all__ = ["GraphNode"]


@dataclass(frozen=True)
class GraphNode:
    """A graph node; `domain` is set only for REF nodes."""

    id: str
    kind: NodeKind
    label: str
    domain: RefDomain | None
    summary: str
