"""PlaybookValidator that shells out to the playbook's own gates."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from studio.domain.model.validation_report import ValidationReport
from studio.logging import get_logger

__all__ = ["SubprocessPlaybookValidator"]

logger = get_logger(__name__)

_TIMEOUT_SECONDS = 180


class SubprocessPlaybookValidator:
    """Runs the intent-test suite and link checker in the playbook checkout."""

    def __init__(self, playbook_root: Path, python_executable: str | None = None) -> None:
        self._root = playbook_root
        self._python = python_executable or sys.executable

    def validate(self) -> ValidationReport:
        tests_rc, tests_out = self._run([self._python, "-m", "pytest", "-q"])
        links_rc, links_out = self._run([self._python, "scripts/check_links.py"])
        logger.info("Validation gates: pytest rc=%d, check_links rc=%d", tests_rc, links_rc)
        return ValidationReport(
            tests_passed=tests_rc == 0,
            links_ok=links_rc == 0,
            tests_output=tests_out,
            links_output=links_out,
        )

    def _run(self, argv: list[str]) -> tuple[int, str]:
        try:
            proc = subprocess.run(
                argv,
                cwd=self._root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.warning("Validation command failed to run: %s", exc)
            return 1, str(exc)
        return proc.returncode, (proc.stdout + proc.stderr)[-8000:]
