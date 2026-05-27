"""csd-intent — cross-runtime auditor for CSD intent specifications.

Validates intent.yaml against CSD-INTENT-01 (schema check), confirms every
@intent / intent() marker references a real claim (orphan check), and reports
unattested claims by walking every test file in the project (coverage check).

Public API:
    audit(project_dir, intent_path=None, test_dirs=None) -> AuditReport
    AuditReport, AuditViolation
    parse_intent_yaml(path)
    check_schema(claims)
    collect_attestations(test_dirs)
"""

from __future__ import annotations

from .audit import AuditReport, AuditViolation, audit
from .schema import check_schema, parse_intent_yaml
from .walker import collect_attestations

__all__ = [
    "AuditReport",
    "AuditViolation",
    "audit",
    "check_schema",
    "collect_attestations",
    "parse_intent_yaml",
]

__version__ = "0.1.0"
