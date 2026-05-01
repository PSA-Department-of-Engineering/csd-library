"""Sample claim tests demonstrating the @intent decorator."""

from __future__ import annotations

import re

from pytest_intent import intent


SAMPLE_USER_IDS = ["u_abc12345", "u_xyz67890", "u_00000001"]
USER_ID_FORMAT = re.compile(r"^u_[a-z0-9]{8}$")


@intent("INT-001")
def test_user_ids_are_non_empty_strings() -> None:
    """INT-001: every sample user ID is a non-empty string."""
    for uid in SAMPLE_USER_IDS:
        assert isinstance(uid, str)
        assert uid != ""


@intent("INT-002")
def test_user_ids_match_canonical_format() -> None:
    """INT-002: every sample user ID matches u_[a-z0-9]{8}."""
    bad = [uid for uid in SAMPLE_USER_IDS if not USER_ID_FORMAT.match(uid)]
    assert not bad, f"user IDs not matching canonical format: {bad}"
