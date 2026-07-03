"""Orchestrates schema + orphan + coverage checks into a single audit report."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .schema import check_schema, parse_intent_yaml
from .walker import collect_attestations, find_nested_intent_projects

__all__ = [
    "AuditReport",
    "AuditViolation",
    "ViolationKind",
    "audit",
    "audit_tree",
]


class ViolationKind(str, Enum):
    SCHEMA = "schema"
    ORPHAN = "orphan"
    UNATTESTED = "unattested"


@dataclass(frozen=True)
class AuditViolation:
    kind: ViolationKind
    claim_id: str | None
    message: str

    def __str__(self) -> str:
        prefix = self.claim_id or "intent.yaml"
        return f"[{self.kind.value}] {prefix}: {self.message}"


@dataclass
class AuditReport:
    """The result of a project audit. Empty `violations` = clean."""

    intent_path: Path
    claim_count: int
    attested_claims: set[str] = field(default_factory=set)
    orphan_refs: dict[str, list[str]] = field(default_factory=dict)
    violations: list[AuditViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    @property
    def unattested(self) -> list[str]:
        return sorted(
            v.claim_id
            for v in self.violations
            if v.kind == ViolationKind.UNATTESTED and v.claim_id
        )

    def format(self) -> str:
        if self.ok:
            return (
                f"intent.yaml ({self.intent_path}): {self.claim_count} claims, "
                f"{len(self.attested_claims)} attested. CLEAN."
            )
        by_kind: dict[ViolationKind, list[AuditViolation]] = {}
        for v in self.violations:
            by_kind.setdefault(v.kind, []).append(v)
        lines = [
            f"intent.yaml ({self.intent_path}): {self.claim_count} claims, "
            f"{len(self.violations)} violation(s)."
        ]
        for kind in (ViolationKind.SCHEMA, ViolationKind.ORPHAN, ViolationKind.UNATTESTED):
            items = by_kind.get(kind, [])
            if not items:
                continue
            lines.append(f"\n{kind.value.upper()} ({len(items)}):")
            for v in items:
                lines.append(f"  {v}")
        return "\n".join(lines)


def audit(
    project_dir: Path,
    intent_path: Path | None = None,
    test_dirs: list[Path] | None = None,
) -> AuditReport:
    """Audit a project's intent spec + test attestations.

    Args:
        project_dir: project root (used to resolve defaults).
        intent_path: explicit intent.yaml location; defaults to ``project_dir/intent.yaml``.
        test_dirs:   directories to scan for @intent / intent() markers; defaults to
                     ``[project_dir]`` (the walker handles exclude rules).
    """
    project_dir = project_dir.resolve()
    intent_path = (intent_path or project_dir / "intent.yaml").resolve()
    test_dirs = test_dirs or [project_dir]

    report = AuditReport(intent_path=intent_path, claim_count=0)

    if not intent_path.exists():
        report.violations.append(
            AuditViolation(ViolationKind.SCHEMA, None, f"intent.yaml not found at {intent_path}")
        )
        return report

    claims = parse_intent_yaml(intent_path)
    report.claim_count = len(claims)

    # Schema
    for msg in check_schema(claims):
        cid = msg.split(":", 1)[0] if ":" in msg else None
        rest = msg.split(":", 1)[1].strip() if ":" in msg else msg
        report.violations.append(AuditViolation(ViolationKind.SCHEMA, cid, rest))

    # Attestations across all test dirs
    attestations = collect_attestations(test_dirs)
    claim_ids = set(claims.keys())
    attested_ids = set(attestations.keys())
    report.attested_claims = claim_ids & attested_ids

    # Orphans: marker references a claim that does not exist
    for cid in sorted(attested_ids - claim_ids):
        refs = attestations.get(cid, [])
        report.orphan_refs[cid] = refs
        report.violations.append(
            AuditViolation(
                ViolationKind.ORPHAN,
                cid,
                f"test marker references unknown claim ({len(refs)} ref(s): {refs[:3]}{'...' if len(refs) > 3 else ''})",
            )
        )

    # Unattested: claim has no marker anywhere.
    # Only enforce for ACTIVE claims. Deprecated claims document a behaviour
    # that no longer holds (no tests expected). Draft claims are pre-implementation
    # placeholders (tests may not yet exist) - surface as informational but don't
    # treat as a failing violation.
    for cid in sorted(claim_ids - attested_ids):
        status = str(claims[cid].get("status", "active"))
        if status == "deprecated":
            continue
        if status == "draft":
            continue
        report.violations.append(
            AuditViolation(
                ViolationKind.UNATTESTED, cid, "no @intent / intent() marker references this claim"
            )
        )

    return report


def audit_tree(project_dir: Path) -> list[AuditReport]:
    """Discover and audit every intent project at or below ``project_dir``.

    The starting ``project_dir`` is audited as the root project (its marker scan is
    bounded by any nested project subtrees). Each subdirectory that carries its own
    ``intent.yaml`` is then audited as an independent project against the markers in
    its own subtree (bounded, in turn, by any still-deeper nested projects). The result
    is a complete, non-overlapping partition of the tree into projects.

    Returns one :class:`AuditReport` per project, root first, then nested projects in a
    deterministic (sorted) order. This is the auto-discovery path used by the CLI when no
    explicit ``--intent`` / ``--tests-dir`` override is given. For the explicit
    single-project case, call :func:`audit` directly.
    """
    project_dir = project_dir.resolve()
    reports = [audit(project_dir)]
    for nested in find_nested_intent_projects(project_dir):
        reports.append(audit(nested))
    return reports
