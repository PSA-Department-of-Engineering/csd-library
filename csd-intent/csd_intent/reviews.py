"""Read repository-owned judgements against their named claim and evidence."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal, cast

import yaml

from .review_result import ReviewResult
from .review_schema import check_review
from .schema import parse_intent_text

__all__ = ["evaluate_review", "read_review"]


def read_review(
    project_dir: Path,
    intent_path: Path,
    claim_id: str,
    claim: Mapping[str, object],
    *,
    commit: str = "HEAD",
) -> ReviewResult:
    """Compare the latest review with one pinned commit or the current working tree.

    Evidence paths are repository-relative. The working tree is read when commit is HEAD.
    """
    if claim.get("review") is None:
        return ReviewResult("unreviewed", "no review recorded on the claim")
    try:
        root_answer = _git(project_dir, "rev-parse", "--show-toplevel")
        if root_answer.returncode:
            return ReviewResult("unresolvable", "repository history is unavailable")
        root = Path(root_answer.stdout.decode("utf-8").strip()).resolve()
        record = claim.get("review")
        sha = record.get("commit") if isinstance(record, Mapping) else None
        if isinstance(sha, str) and _git(root, "cat-file", "-t", sha).stdout.strip() != b"commit":
            return ReviewResult("unresolvable", "reviewed object is not an available commit")
        spec = intent_path.resolve().relative_to(root).as_posix()
        return evaluate_review(
            claim_id, claim, spec,
            lambda sha, path: _current_file(root, path, sha),
            commit=commit,
        )
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as exc:
        return ReviewResult("unresolvable", f"review basis cannot be read: {exc}")


def evaluate_review(
    claim_id: str,
    claim: Mapping[str, object],
    spec_path: str,
    read_file: Callable[[str, str], bytes | None],
    *,
    commit: str,
) -> ReviewResult:
    """Compare a review's claim and evidence with one read, without storing state.

    Review metadata and the reviewed claim's lifecycle status do not alter its meaning.
    Every other claim field and named file binds the judgement.
    """
    raw = claim.get("review")
    if raw is None:
        return ReviewResult("unreviewed", "no review recorded on the claim")
    problems = check_review(raw, "llm")
    if problems:
        return ReviewResult("unresolvable", "; ".join(problems))
    assert isinstance(raw, Mapping)
    sha = str(raw["commit"])
    evidence = tuple(cast(list[str], raw["evidence"]))

    def result(
        state: Literal["pass", "fail", "stale", "unreviewed", "unresolvable"], reason: str
    ) -> ReviewResult:
        return ReviewResult(state, reason, str(raw["verdict"]), sha, evidence, str(raw["reason"]))

    try:
        original = read_file(sha, spec_path)
        if original is None:
            return result("unresolvable", "reviewed specification is unavailable")
        target = read_file(commit, spec_path)
        if target is None:
            return result("unresolvable", "current specification is unavailable")
        reviewed = parse_intent_text(original.decode("utf-8")).get(claim_id)
        current_claim = parse_intent_text(target.decode("utf-8")).get(claim_id)
        if reviewed is None or current_claim is None or _meaning(reviewed) != _meaning(current_claim) or _meaning(current_claim) != _meaning(claim):
            return result("stale", "the reviewed claim differs")
        for path in evidence:
            before = read_file(sha, path)
            current = read_file(commit, path)
            if before is None or current is None:
                return result("unresolvable", f"evidence is unavailable: {path}")
            if path == spec_path:
                same = _spec_evidence(before, claim_id) == _spec_evidence(current, claim_id)
            else:
                same = before == current
            if not same:
                return result("stale", f"evidence differs: {path}")
    except (OSError, ValueError, UnicodeError, yaml.YAMLError, subprocess.SubprocessError) as exc:
        return result("unresolvable", f"review basis cannot be read: {exc}")
    state: Literal["pass", "fail"] = "pass" if raw["verdict"] == "PASS" else "fail"
    return result(state, str(raw["reason"]))


def _meaning(claim: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in claim.items() if key not in {"review", "status"}}


def _spec_evidence(content: bytes, claim_id: str) -> dict[str, object]:
    claims = parse_intent_text(content.decode("utf-8"))
    return {
        cid: _meaning(body) if cid == claim_id else {
            key: value for key, value in body.items() if key != "review"
        }
        for cid, body in claims.items()
    }


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments], capture_output=True, check=False, timeout=30
    )


def _file(root: Path, commit: str, path: str) -> bytes | None:
    if _git(root, "cat-file", "-t", f"{commit}:{path}").stdout.strip() != b"blob":
        return None
    answer = _git(root, "show", f"{commit}:{path}")
    return answer.stdout if answer.returncode == 0 else None


def _current_file(root: Path, path: str, commit: str) -> bytes | None:
    if commit != "HEAD":
        return _file(root, commit, path)
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        return None
    oid = _git(root, "hash-object", f"--path={path}", str(target))
    if oid.returncode == 0:
        normalized = _git(root, "cat-file", "-p", oid.stdout.decode("ascii").strip())
        if normalized.returncode == 0:
            return normalized.stdout
    return target.read_bytes()
