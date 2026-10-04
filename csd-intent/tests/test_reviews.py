"""Latest judgements bind to reviewed repository content."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_intent import intent

from csd_intent import audit, check_schema, parse_intent_yaml, read_review, summarize

_ID = "INT-EXAMPLE-001"

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()

def _commit(root: Path) -> str:
    _git(root, "add", ".")
    _git(root, "-c", "user.name=review-tests", "-c", "user.email=tests@example.invalid",
         "commit", "-m", "test: reviewed content")
    return _git(root, "rev-parse", "HEAD")

def _write(root: Path, claim: dict) -> None:
    (root / "intent.yaml").write_text(yaml.safe_dump({_ID: claim}), encoding="utf-8")

@pytest.fixture()
def reviewed(tmp_path: Path):
    _git(tmp_path, "init", "--quiet")
    claim = {"version": "1.0.0", "status": "draft",
             "statement": "The error explains its cause and recovery action.",
             "test": {"scope": "llm", "component": "Message", "type": "contract"},
             "criticality": "high"}
    _write(tmp_path, claim)
    (tmp_path / "messages.md").write_text("Token expired. Sign in again.\n", encoding="utf-8")
    sha = _commit(tmp_path)
    claim["status"] = "active"
    claim["review"] = {"verdict": "PASS", "commit": sha}
    _write(tmp_path, claim)
    return tmp_path, claim

@intent("INT-CSD-012", "INT-CSD-013", "INT-CSD-009")
def test_current_pass_attests_without_marker(reviewed):
    root, claim = reviewed
    assert check_schema(parse_intent_yaml(root / "intent.yaml")) == []
    report = audit(root)
    assert report.ok, report.format()
    assert report.attested_claims == {_ID}
    record = summarize([report])["projects"][0]["claims_by_id"][_ID]["review"]
    assert record == {"state": "pass", "reason": "recorded PASS",
                      "verdict": "PASS", "commit": claim["review"]["commit"]}
    _commit(root)
    assert audit(root).ok

@intent("INT-CSD-013")
@pytest.mark.parametrize("field,value", [("statement", "The error names a recovery action."),
                                        ("version", "2.0.0"), ("rationale", "A rationale")])
def test_claim_drift_is_unattested(reviewed, field, value):
    root, claim = reviewed
    claim[field] = value
    _write(root, claim)
    assert audit(root).unattested == [_ID]
    assert audit(root).reviews[_ID].state == "stale"

@intent("INT-CSD-013")
@pytest.mark.parametrize("change", ["edit", "delete", "unrelated", "untracked"])
def test_repository_content_drift_is_stale(reviewed, change):
    root, claim = reviewed
    if change == "edit":
        (root / "messages.md").write_text("Something went wrong.", encoding="utf-8")
    elif change == "delete":
        (root / "messages.md").unlink()
    else:
        (root / "other.md").write_text("Other work.", encoding="utf-8")
        if change == "unrelated":
            _commit(root)
    assert read_review(root, root / "intent.yaml", _ID, claim).state == "stale"

@intent("INT-CSD-013")
def test_latest_review_replaces_previous_verdict(reviewed):
    root, claim = reviewed
    claim["review"]["verdict"] = "FAIL"
    _write(root, claim)
    assert audit(root).reviews[_ID].state == "fail"
    sha = _commit(root)
    claim["review"] = {"verdict": "PASS", "commit": sha}
    _write(root, claim)
    assert audit(root).ok
    del claim["review"]
    _write(root, claim)
    assert audit(root).reviews[_ID].state == "unreviewed"
    assert audit(root).unattested == [_ID]

@intent("INT-CSD-013")
@pytest.mark.parametrize("object_kind", ["missing", "tree"])
def test_review_requires_an_available_commit(reviewed, object_kind):
    root, claim = reviewed
    claim["review"]["commit"] = ("a" * 40 if object_kind == "missing"
                                 else _git(root, "rev-parse", "HEAD^{tree}"))
    _write(root, claim)
    assert audit(root).reviews[_ID].state == "unresolvable"

@intent("INT-CSD-013")
def test_pinned_read_checks_the_pinned_claim(reviewed):
    root, claim = reviewed
    pin = _commit(root)
    changed = {**claim, "statement": "The error explains a different condition."}
    _write(root, changed)
    later = _commit(root)
    assert read_review(root, root / "intent.yaml", _ID, claim, commit=later).state == "stale"
    assert read_review(root, root / "intent.yaml", _ID, claim, commit=pin).state == "pass"

@intent("INT-CSD-013")
def test_clean_crlf_checkout_is_current(reviewed):
    root, claim = reviewed
    _git(root, "config", "core.autocrlf", "true")
    claim.pop("review")
    (root / "messages.md").write_bytes(b"Token expired.\r\nSign in again.\r\n")
    _write(root, claim)
    sha = _commit(root)
    claim["review"] = {"verdict": "PASS", "commit": sha}
    _write(root, claim)
    _commit(root)
    assert _git(root, "status", "--short") == ""
    assert audit(root).ok

@intent("INT-CSD-012")
@pytest.mark.parametrize("record", [None, {}, {"verdict": "PASS", "commit": "abc"},
    {"verdict": "MAYBE", "commit": "a" * 40},
    {"verdict": "PASS", "commit": "a" * 40, "reason": "A reason"},
    {"verdict": "PASS", "commit": "a" * 40, "evidence": ["messages.md"]}])
def test_invalid_review_shape_is_refused(reviewed, record):
    _root, claim = reviewed
    claim["review"] = record
    assert any("review" in error for error in check_schema({_ID: claim}))

@intent("INT-CSD-012")
def test_runner_claim_cannot_carry_review(reviewed):
    _root, claim = reviewed
    claim["test"]["scope"] = "unit"
    assert any("llm" in error for error in check_schema({_ID: claim}))
