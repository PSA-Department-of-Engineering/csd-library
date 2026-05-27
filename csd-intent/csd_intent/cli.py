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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import ViolationKind, audit

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


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.version:
        from . import __version__

        print(__version__)
        return 0

    report = audit(
        project_dir=args.project_dir,
        intent_path=args.intent,
        test_dirs=args.tests_dirs,
    )

    if args.quiet:
        print(
            f"{report.intent_path}: {report.claim_count} claims, "
            f"{len(report.violations)} violation(s)."
        )
    else:
        print(report.format())

    fail_kinds = _FAIL_MAP[args.fail_on]
    if any(v.kind in fail_kinds for v in report.violations):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
