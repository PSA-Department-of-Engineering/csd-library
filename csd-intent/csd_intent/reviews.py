"""Read the latest judgement against the reviewed repository commit."""
from __future__ import annotations

import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import yaml

from .review_result import ReviewResult
from .review_schema import check_review
from .schema import parse_intent_text

__all__ = ["read_review"]

def read_review(
    project_dir: Path, intent_path: Path, claim_id: str, claim: Mapping[str, object],
    *, commit: str = "HEAD",
) -> ReviewResult:
    """Compare Git content, excluding specification review and lifecycle metadata.

    HEAD reads the working tree. An explicit commit pins every compared file.
    """
    record = claim.get("review")
    if record is None:
        return ReviewResult("unreviewed", "no review recorded on the claim")
    problems = check_review(record, "llm")
    if problems:
        return ReviewResult("unresolvable", "; ".join(problems))
    assert isinstance(record, Mapping)
    sha = str(record["commit"])
    verdict = str(record["verdict"])
    def result(state: Literal["pass", "fail", "stale", "unreviewed", "unresolvable"], reason: str) -> ReviewResult:
        return ReviewResult(state, reason, verdict, sha)
    try:
        root_answer = _git(project_dir, "rev-parse", "--show-toplevel")
        if root_answer.returncode:
            return result("unresolvable", "repository history is unavailable")
        root = Path(root_answer.stdout.decode("utf-8").strip()).resolve()
        spec = intent_path.resolve().relative_to(root).as_posix()
        if _git(root, "cat-file", "-t", sha).stdout.strip() != b"commit":
            return result("unresolvable", "reviewed commit is unavailable")
        if commit != "HEAD":
            if check_review({"commit": commit, "verdict": "PASS"}, "llm"):
                return result("unresolvable", "requested commit must be a full Git object ID")
            if _git(root, "cat-file", "-t", commit).stdout.strip() != b"commit":
                return result("unresolvable", "requested commit is unavailable")
        before = _git(root, "show", f"{sha}:{spec}")
        after = (_git(root, "show", f"{commit}:{spec}") if commit != "HEAD"
                 else None)
        if before.returncode or (after is not None and after.returncode):
            return result("unresolvable", "specification is unavailable")
        original_text = before.stdout.decode("utf-8")
        current_text = (after.stdout.decode("utf-8") if after is not None
                        else intent_path.read_text(encoding="utf-8"))
        parse_intent_text(original_text)
        current = parse_intent_text(current_text)
        if claim_id not in current or _meaning(current[claim_id]) != _meaning(claim):
            return result("stale", "the claim differs from the requested revision")
        compared = _git(root, "diff", "--name-only", "-z", sha,
                        *([commit] if commit != "HEAD" else []), "--")
        if compared.returncode:
            return result("unresolvable", "repository content cannot be compared")
        paths = set(compared.stdout.decode("utf-8").split("\0")) - {""}
        if commit == "HEAD":
            untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z")
            paths.update(set(untracked.stdout.decode("utf-8").split("\0")) - {""})
        if paths - {spec} or _spec_meaning(original_text) != _spec_meaning(current_text):
            return result("stale", "repository content differs from the reviewed commit")
        return result("pass" if verdict == "PASS" else "fail", "recorded " + verdict)
    except (OSError, ValueError, UnicodeError, yaml.YAMLError, subprocess.SubprocessError):
        return result("unresolvable", "review basis cannot be read")


def _meaning(claim: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in claim.items() if key not in {"review", "status"}}


def _spec_meaning(text: str) -> object:
    value = yaml.safe_load(text)
    if not isinstance(value, Mapping):
        return value
    return {
        key: _meaning(body) if isinstance(key, str) and key.startswith("INT-")
             and isinstance(body, Mapping) else body
        for key, body in value.items()
    }


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          check=False, timeout=30)
