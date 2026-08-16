"""csd-intent - cross-runtime auditor for CSD intent specifications.

Validates intent.yaml against CSD-INTENT-01 (schema check), confirms every
@intent / intent() marker references a real claim (orphan check), and reports
unattested claims by walking every test file in the project (coverage check).

Nested projects: a repo may contain nested intent projects (a subdirectory with its
own intent.yaml). ``audit_tree()`` discovers and audits each as its own project, so a
nested project's markers are checked against its own intent.yaml rather than orphaning
against the outer project's claims.

Public API:
    audit(project_dir, intent_path=None, test_dirs=None) -> AuditReport
    audit_tree(project_dir) -> list[AuditReport]
    AuditReport, AuditViolation
    parse_intent_yaml(path)  # raises DuplicateKeyError on a repeated key
    check_schema(claims)
    collect_attestations(test_dirs)
    find_nested_intent_projects(root)
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .audit import AuditReport, AuditViolation, audit, audit_tree
from .schema import DuplicateKeyError, check_schema, parse_intent_yaml
from .walker import collect_attestations, find_nested_intent_projects

try:
    __version__ = version("csd-intent")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "AuditReport",
    "AuditViolation",
    "DuplicateKeyError",
    "__version__",
    "audit",
    "audit_tree",
    "check_schema",
    "collect_attestations",
    "find_nested_intent_projects",
    "parse_intent_yaml",
]
