"""The audit as one machine-readable object: what ``csd-intent --json`` prints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .audit import AuditReport
from .schema import effective_scope, effective_status

__all__ = ["summarize"]

_TIMESTAMP = "%Y-%m-%dT%H:%M:%SZ"
_COUNT_KEYS = ("claims", "attested", "unattested", "draft", "active", "deprecated", "violations")


def summarize(reports: list[AuditReport], now: datetime | None = None) -> dict[str, object]:
    """Fold one or more audit reports into the summary object.

    The counts are the audit's own. ``attested`` is the number of declared claims that
    at least one marker references, what the report prints as "N attested";
    ``unattested`` is the number of claims the audit reports under that violation kind,
    an active, runner-scoped claim with no marker. Draft, deprecated, and unmarked
    ``llm`` claims are therefore neither, and the two do not sum to ``claims``.
    ``requirements_traced`` counts the distinct ids across every claim's ``derived_from``
    annotation. Over several reports (a tree of nested projects) the counts sum,
    ``requirements_traced`` stays distinct, and ``claims_by_id`` is the union.

    Args:
        reports: one report per audited project, root first.
        now:     the instant recorded as ``generated_at``; defaults to the current UTC time.
    """
    claims_by_id: dict[str, dict[str, object]] = {}
    projects: list[dict[str, object]] = []
    requirements: set[str] = set()
    per_report = [_counts(report) for report in reports]

    for report, counts in zip(reports, per_report, strict=True):
        traced: set[str] = set()
        for cid, claim in report.claims.items():
            derived = _derived_from(claim)
            traced.update(derived)
            claims_by_id[cid] = {
                "status": effective_status(claim),
                "attested": cid in report.attested_claims,
                "scope": effective_scope(claim),
                "derived_from": derived,
            }
        requirements.update(traced)
        projects.append(
            {
                "intent_path": str(report.intent_path),
                **counts,
                "requirements_traced": len(traced),
                "clean": report.ok,
            }
        )

    stamp = now.astimezone(timezone.utc) if now is not None else datetime.now(timezone.utc)
    return {
        "generated_at": stamp.strftime(_TIMESTAMP),
        **{key: sum(counts[key] for counts in per_report) for key in _COUNT_KEYS},
        "requirements_traced": len(requirements),
        "clean": all(report.ok for report in reports),
        "projects": projects,
        "claims_by_id": claims_by_id,
    }


def _counts(report: AuditReport) -> dict[str, int]:
    statuses = [effective_status(claim) for claim in report.claims.values()]
    return {
        "claims": report.claim_count,
        "attested": len(report.attested_claims),
        "unattested": len(report.unattested),
        "draft": statuses.count("draft"),
        "active": statuses.count("active"),
        "deprecated": statuses.count("deprecated"),
        "violations": len(report.violations),
    }


def _derived_from(claim: dict[str, Any]) -> list[str]:
    """The ids under the claim's ``derived_from`` annotation, as written; a bare scalar is one id."""
    raw = claim.get("derived_from")
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return [str(raw)]
