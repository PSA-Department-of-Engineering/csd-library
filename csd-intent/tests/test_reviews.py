"""Judgements bind to the reviewed claim and named repository evidence."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_intent import intent

from csd_intent import audit, check_schema, parse_intent_yaml, read_review, summarize

_ID = "INT-EXAMPLE-001"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _commit(root: Path) -> str:
    _git(root, "add", ".")
    _git(root, "-c", "user.name=review-tests", "-c", "user.email=tests@example.invalid",
         "commit", "-m", "test: review evidence")
    return _git(root, "rev-parse", "HEAD")


def _write(root: Path, claim: dict[str, object]) -> None:
    (root / "intent.yaml").write_text(yaml.safe_dump({_ID: claim}), encoding="utf-8")


@pytest.fixture()
def reviewed(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    _git(tmp_path, "init", "--quiet")
    claim: dict[str, object] = {
        "version": "1.0.0", "status": "draft",
        "statement": "The failure message explains its cause.",
        "test": {"scope": "llm", "component": "messages.md", "type": "contract"},
        "criticality": "high",
    }
    _write(tmp_path, claim)
    (tmp_path / "messages.md").write_text("The token has expired. Sign in again.", encoding="utf-8")
    sha = _commit(tmp_path)
    claim["status"] = "active"
    claim["review"] = {
        "verdict": "PASS", "commit": sha,
        "evidence": ["messages.md", "intent.yaml"],
        "reason": "The message identifies expiry and a recovery action.",
    }
    _write(tmp_path, claim)
    return tmp_path, claim


@intent("INT-CSD-012", "INT-CSD-013", "INT-CSD-009")
def test_current_pass_attests_without_a_marker(reviewed: tuple[Path, dict[str, object]]) -> None:
    root, claim = reviewed
    assert check_schema(parse_intent_yaml(root / "intent.yaml")) == []
    report = audit(root)
    assert report.ok, report.format()
    assert report.attested_claims == {_ID}
    assert report.reviews[_ID].state == "pass"
    record = summarize([report])["projects"][0]["claims_by_id"][_ID]["review"]
    assert record["commit"] == claim["review"]["commit"]
    assert record["evidence"] == ["messages.md", "intent.yaml"]


@intent("INT-CSD-013")
def test_recording_metadata_and_unrelated_commits_preserves_pass(
    reviewed: tuple[Path, dict[str, object]],
) -> None:
    root, claim = reviewed
    _commit(root)
    (root / "unrelated.txt").write_text("Other work", encoding="utf-8")
    _commit(root)
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "pass"


@intent("INT-CSD-013")
@pytest.mark.parametrize("field,value", [("statement", "The message names a recovery step."),
                                        ("version", "2.0.0"), ("rationale", "A new rationale")])
def test_claim_drift_is_unattested(
    reviewed: tuple[Path, dict[str, object]], field: str, value: str,
) -> None:
    root, claim = reviewed
    claim[field] = value
    _write(root, claim)
    report = audit(root)
    assert report.unattested == [_ID]
    assert report.reviews[_ID].state == "stale"


@intent("INT-CSD-013")
def test_evidence_drift_and_deletion_cannot_pass(reviewed: tuple[Path, dict[str, object]]) -> None:
    root, claim = reviewed
    (root / "messages.md").write_text("Something went wrong.", encoding="utf-8")
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "stale"
    (root / "messages.md").unlink()
    report = audit(root)
    assert report.unattested == [_ID]
    assert report.reviews[_ID].state == "unresolvable"


@intent("INT-CSD-013")
def test_failed_and_missing_reviews_are_unattested(reviewed: tuple[Path, dict[str, object]]) -> None:
    root, claim = reviewed
    claim["review"]["verdict"] = "FAIL"
    _write(root, claim)
    assert audit(root).reviews[_ID].state == "fail"
    assert audit(root).unattested == [_ID]
    del claim["review"]
    _write(root, claim)
    report = audit(root)
    assert report.reviews[_ID].state == "unreviewed"
    assert report.unattested == [_ID]


@intent("INT-CSD-013")
def test_unavailable_review_commit_cannot_pass(reviewed: tuple[Path, dict[str, object]]) -> None:
    root, claim = reviewed
    claim["review"]["commit"] = "a" * 40
    _write(root, claim)
    report = audit(root)
    assert report.unattested == [_ID]
    assert report.reviews[_ID].state == "unresolvable"


@intent("INT-CSD-013")
def test_pinned_read_uses_that_commits_evidence(reviewed: tuple[Path, dict[str, object]]) -> None:
    root, claim = reviewed
    pinned = _commit(root)
    (root / "messages.md").write_text("Changed working copy", encoding="utf-8")
    assert read_review(root, root / "intent.yaml", _ID, claim, commit=pinned).state == "pass"
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "stale"


@intent("INT-CSD-012")
@pytest.mark.parametrize("field,value", [
    ("verdict", "maybe"), ("commit", "abc1234"), ("commit", "--output=leak"),
    ("evidence", []), ("evidence", ["../secret"]), ("evidence", ["/absolute"]),
    ("evidence", ["src/*"]), ("evidence", ["messages.md", "messages.md"]),
    ("reason", ""), ("round", 1),
])
def test_invalid_review_records_are_schema_violations(
    reviewed: tuple[Path, dict[str, object]], field: str, value: object,
) -> None:
    _, claim = reviewed
    claim["review"][field] = value
    assert check_schema({_ID: claim})


@intent("INT-CSD-012")
def test_runner_claim_cannot_carry_a_review(reviewed: tuple[Path, dict[str, object]]) -> None:
    _, claim = reviewed
    claim["test"]["scope"] = "unit"
    assert any("test.scope: llm" in problem for problem in check_schema({_ID: claim}))


@intent("INT-CSD-013")
def test_tree_object_is_not_a_review_commit(reviewed):
    root, claim = reviewed
    claim["review"]["commit"] = _git(root, "rev-parse", "HEAD^{tree}")
    _write(root, claim)
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "unresolvable"


@intent("INT-CSD-013")
def test_pinned_claim_is_read_independently(reviewed):
    root, claim = reviewed
    claim["review"]["evidence"] = ["messages.md"]
    changed = {**claim, "statement": "The failure message explains its recovery action."}
    _write(root, changed)
    sha = _commit(root)
    assert read_review(root, root / "intent.yaml", _ID, claim, commit=sha).state == "stale"


@intent("INT-CSD-013")
def test_directory_evidence_is_unresolvable(reviewed):
    root, claim = reviewed
    (root / "docs").mkdir()
    (root / "docs" / "message.md").write_text("Sign in again.", encoding="utf-8")
    claim.pop("review")
    _write(root, claim)
    sha = _commit(root)
    claim["review"] = {"verdict": "PASS", "commit": sha, "evidence": ["docs"], "reason": "Clear recovery action."}
    _write(root, claim)
    target = _commit(root)
    assert read_review(root, root / "intent.yaml", _ID, claim, commit=target).state == "unresolvable"


@intent("INT-CSD-013")
def test_clean_crlf_evidence_is_current(reviewed):
    root, claim = reviewed
    _git(root, "config", "core.autocrlf", "true")
    claim.pop("review")
    (root / "messages.md").write_bytes(b"Token expired.\r\nSign in again.\r\n")
    _write(root, claim)
    sha = _commit(root)
    claim["review"] = {"verdict": "PASS", "commit": sha, "evidence": ["messages.md"], "reason": "Clear recovery action."}
    _write(root, claim)
    _commit(root)
    assert _git(root, "status", "--short") == ""
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "pass"
