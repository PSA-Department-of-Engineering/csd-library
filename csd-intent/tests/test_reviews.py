"""Latest judgements bind to the claim they judged."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml
from pytest_intent import intent

from csd_intent import audit, check_schema, claim_digest, parse_intent_yaml, read_review, summarize

_ID = "INT-EXAMPLE-001"
_OTHER = "INT-EXAMPLE-002"

def _write(root: Path, *claims: tuple[str, dict]) -> None:
    (root / "intent.yaml").write_text(yaml.safe_dump(dict(claims)), encoding="utf-8")

def _claim(statement: str) -> dict:
    return {"version": "1.0.0", "status": "active", "statement": statement,
            "test": {"scope": "llm", "component": "Message", "type": "contract"},
            "criticality": "high"}

@pytest.fixture()
def reviewed(tmp_path: Path):
    claim = _claim("The error explains its cause and recovery action.")
    claim["review"] = {"verdict": "PASS", "claim": claim_digest(claim)}
    other = _claim("The error names the failed operation.")
    _write(tmp_path, (_ID, claim), (_OTHER, other))
    (tmp_path / "messages.md").write_text("Token expired. Sign in again.\n", encoding="utf-8")
    return tmp_path, claim, other

@intent("INT-CSD-012", "INT-CSD-013", "INT-CSD-009")
def test_current_pass_attests_without_marker(reviewed):
    root, claim, _other = reviewed
    assert check_schema(parse_intent_yaml(root / "intent.yaml")) == []
    report = audit(root)
    assert report.attested_claims == {_ID}
    assert report.unattested == [_OTHER]
    record = summarize([report])["projects"][0]["claims_by_id"][_ID]["review"]
    assert record == {"state": "pass", "reason": "recorded PASS",
                      "verdict": "PASS", "claim": claim["review"]["claim"]}

@intent("INT-CSD-013")
@pytest.mark.parametrize("field,value", [("statement", "The error names a recovery action."),
                                        ("version", "2.0.0"), ("rationale", "A rationale"),
                                        ("test", {"scope": "llm", "component": "Copy",
                                                  "type": "contract"})])
def test_claim_drift_is_stale(reviewed, field, value):
    root, claim, other = reviewed
    claim[field] = value
    _write(root, (_ID, claim), (_OTHER, other))
    review = audit(root).reviews[_ID]
    assert review.state == "stale"
    assert review.claim == claim_digest(claim) in review.reason
    assert _ID in audit(root).unattested

@intent("INT-CSD-013")
@pytest.mark.parametrize("change", ["file", "other-claim", "annotation"])
def test_content_outside_the_claim_keeps_the_review_current(reviewed, change):
    root, claim, other = reviewed
    if change == "file":
        (root / "messages.md").write_text("Something went wrong.", encoding="utf-8")
    elif change == "other-claim":
        other["statement"] = "The error names the operation and its target."
        _write(root, (_ID, claim), (_OTHER, other))
    else:
        with (root / "intent.yaml").open("a", encoding="utf-8") as stream:
            stream.write("policy: changed policy\n")
    assert audit(root).reviews[_ID].state == "pass"

@intent("INT-CSD-013")
def test_status_and_layout_keep_the_review_current(reviewed):
    root, claim, _other = reviewed
    claim["status"] = "draft"
    assert read_review(claim).state == "pass"
    claim["status"] = "active"
    folded = yaml.safe_dump({_ID: claim}, default_flow_style=True, width=40)
    (root / "intent.yaml").write_text(folded, encoding="utf-8")
    assert audit(root).reviews[_ID].state == "pass"

@intent("INT-CSD-013")
def test_latest_review_replaces_previous_verdict(reviewed):
    root, claim, other = reviewed
    claim["review"]["verdict"] = "FAIL"
    _write(root, (_ID, claim), (_OTHER, other))
    assert audit(root).reviews[_ID].state == "fail"
    del claim["review"]
    _write(root, (_ID, claim), (_OTHER, other))
    review = audit(root).reviews[_ID]
    assert review.state == "unreviewed"
    assert review.claim == claim_digest(claim) in review.reason
    assert _ID in audit(root).unattested

@intent("INT-CSD-012")
@pytest.mark.parametrize("record", [None, {}, {"verdict": "PASS", "claim": "abc"},
    {"verdict": "PASS", "claim": "A" * 64},
    {"verdict": "MAYBE", "claim": "a" * 64},
    {"verdict": "PASS", "commit": "a" * 40},
    {"verdict": "PASS", "claim": "a" * 64, "reason": "A reason"},
    {"verdict": "PASS", "claim": "a" * 64, "commit": "a" * 40}])
def test_invalid_review_shape_is_refused(reviewed, record):
    _root, claim, _other = reviewed
    claim["review"] = record
    assert any("review" in error for error in check_schema({_ID: claim}))
    if record is not None:
        assert read_review(claim).state == "unresolvable"

@intent("INT-CSD-012")
def test_runner_claim_cannot_carry_review(reviewed):
    _root, claim, _other = reviewed
    claim["test"]["scope"] = "unit"
    assert any("llm" in error for error in check_schema({_ID: claim}))


_GOLDEN_YAML = """\
INT-EXAMPLE-001:
  version: 1.2.0
  status: active
  statement: "O erro explica a causa e a recuperação."
  derived_from: [REQ-001, REQ-002]
  rationale: Since 2026-10-01.
  reviewed_on: 2026-10-01
  test: {scope: llm, component: Messages, type: contract}
  criticality: high
  weight: 3
"""
_GOLDEN_JSON = ('{"criticality":"high","derived_from":["REQ-001","REQ-002"],'
                '"rationale":"Since 2026-10-01.","reviewed_on":"2026-10-01",'
                '"statement":"O erro explica a causa e a recuperação.",'
                '"test":{"component":"Messages","scope":"llm","type":"contract"},'
                '"version":"1.2.0","weight":3}')
_GOLDEN = "0c28cdfda5176d44ed3b7b150b468bb8e8694e6566a255e2f5e7ffa8ddca5cd4"

@intent("INT-CSD-012")
def test_digest_is_the_sha256_of_the_canonical_claim(tmp_path: Path):
    (tmp_path / "intent.yaml").write_text(_GOLDEN_YAML, encoding="utf-8")
    claim = parse_intent_yaml(tmp_path / "intent.yaml")[_ID]
    assert hashlib.sha256(_GOLDEN_JSON.encode("utf-8")).hexdigest() == _GOLDEN
    assert claim_digest(claim) == _GOLDEN

@intent("INT-CSD-013")
def test_hand_written_layouts_share_one_digest(tmp_path: Path):
    block = (
        "# the claim, block style\r\n"
        "INT-EXAMPLE-001:\r\n"
        "  criticality: high\r\n"
        "  weight: 3\r\n"
        "  version: '1.2.0'\r\n"
        "  status: draft\r\n"
        "  statement: >-\r\n"
        "    O erro explica a causa\r\n"
        "    e a recuperação.\r\n"
        "  derived_from:\r\n"
        "    - REQ-001\r\n"
        "    - \"REQ-002\"\r\n"
        "  rationale: 'Since 2026-10-01.'\r\n"
        "  reviewed_on: 2026-10-01\r\n"
        "  test:\r\n"
        "    type: contract\r\n"
        "    scope: llm  # judged\r\n"
        "    component: Messages\r\n"
    )
    (tmp_path / "intent.yaml").write_bytes(block.encode("utf-8"))
    claim = parse_intent_yaml(tmp_path / "intent.yaml")[_ID]
    assert claim_digest(claim) == _GOLDEN

@intent("INT-CSD-013")
@pytest.mark.parametrize("field", [
    "rubric:\n    on: every release\n",
    "rubric: !!set {a, b}\n",
    "rubric: &loop [*loop]\n",
])
def test_a_claim_without_a_canonical_form_is_unresolvable(tmp_path: Path, field):
    text = _GOLDEN_YAML.replace("  weight: 3\n", "  " + field)
    (tmp_path / "intent.yaml").write_text(text, encoding="utf-8")
    report = audit(tmp_path)
    review = report.reviews[_ID]
    assert review.state == "unresolvable"
    assert review.reason.startswith("the claim has no digest")
    assert report.unattested == [_ID]
    assert summarize([report])["projects"][0]["claims_by_id"][_ID]["review"]["claim"] == ""
