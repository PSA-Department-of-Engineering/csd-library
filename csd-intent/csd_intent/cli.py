"""CLI entry point for csd-intent.

Usage:
  csd-intent [PROJECT_DIR]
             [--intent PATH]
             [--tests-dir DIR]...
             [--fail-on schema|orphan|unattested|any|none]
             [--quiet]
             [--version]

Default ``PROJECT_DIR`` is the cwd. Default ``--fail-on`` is ``any`` (exit non-zero
on any violation). Use ``--fail-on schema`` to only fail on schema problems and
treat coverage gaps as warnings (matches the "intent before test" CSD workflow).

Nested projects: when PROJECT_DIR contains nested intent projects (subdirectories with
their own intent.yaml), each is discovered and audited as its own project against the
markers in its own subtree. A per-project summary is printed and the process exits
non-zero if *any* project has a failing violation. Passing ``--intent`` or
``--tests-dir`` switches to an explicit single-project audit (no auto-discovery).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import AuditReport, ViolationKind, audit, audit_tree

_FAIL_MAP = {
    "schema": {ViolationKind.SCHEMA},
    "orphan": {ViolationKind.ORPHAN},
    "unattested": {ViolationKind.UNATTESTED},
    "any": {ViolationKind.SCHEMA, ViolationKind.ORPHAN, ViolationKind.UNATTESTED},
    "none": set(),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csd-intent",
        description="Audit a CSD intent project: schema + orphan + coverage checks.",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        type=Path,
        help="Project root (default: cwd).",
    )
    parser.add_argument(
        "--intent",
        type=Path,
        default=None,
        help="Path to intent.yaml (default: PROJECT_DIR/intent.yaml).",
    )
    parser.add_argument(
        "--tests-dir",
        dest="tests_dirs",
        action="append",
        type=Path,
        default=None,
        help="Directory to scan for test markers (repeatable; default: PROJECT_DIR).",
    )
    parser.add_argument(
        "--fail-on",
        choices=tuple(_FAIL_MAP.keys()),
        default="any",
        help="Which violation kinds cause a non-zero exit (default: any).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the per-violation report; only print the summary line.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    return parser


def _print_report(report: AuditReport, quiet: bool) -> None:
    if quiet:
        print(
            f"{report.intent_path}: {report.claim_count} claims, "
            f"{len(report.violations)} violation(s)."
        )
    else:
        print(report.format())


def _has_failing_violation(report: AuditReport, fail_kinds: set[ViolationKind]) -> bool:
    return any(v.kind in fail_kinds for v in report.violations)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.version:
        from . import __version__

        print(__version__)
        return 0

    fail_kinds = _FAIL_MAP[args.fail_on]

    # Explicit single-project mode: --intent / --tests-dir disables auto-discovery.
    if args.intent is not None or args.tests_dirs is not None:
        report = audit(
            project_dir=args.project_dir,
            intent_path=args.intent,
            test_dirs=args.tests_dirs,
        )
        _print_report(report, args.quiet)
        return 1 if _has_failing_violation(report, fail_kinds) else 0

    # Auto-discovery mode: audit the root project plus any nested intent projects.
    reports = audit_tree(args.project_dir)

    # Backward-compatible single-project output when there is no nesting: identical
    # to the pre-nesting behaviour (one report, no per-project banner).
    if len(reports) == 1:
        _print_report(reports[0], args.quiet)
        return 1 if _has_failing_violation(reports[0], fail_kinds) else 0

    # Multiple projects: per-project report plus an aggregate summary.
    failed = 0
    for i, report in enumerate(reports):
        if i:
            print()
        _print_report(report, args.quiet)
        if _has_failing_violation(report, fail_kinds):
            failed += 1

    clean = len(reports) - failed
    print(
        f"\n{len(reports)} project(s) audited: {clean} clean, {failed} with violation(s)."
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
