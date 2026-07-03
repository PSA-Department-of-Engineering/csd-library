"""HTTP integration tests: real app, real file I/O against a synthetic playbook."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestSystem:
    def test_health_returns_ok(self, client: TestClient) -> None:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestGraph:
    def test_graph_contains_playbook_refs_and_skills(self, client: TestClient) -> None:
        resp = client.get("/api/graph")
        assert resp.status_code == 200
        graph = resp.json()
        ids = {n["id"] for n in graph["nodes"]}
        assert {"AI-PLAYBOOK", "REF-Alpha", "REF-Beta", "do-alpha"} <= ids

    def test_graph_has_all_three_edge_kinds(self, client: TestClient) -> None:
        kinds = {e["kind"] for e in client.get("/api/graph").json()["edges"]}
        assert kinds == {"playbook-to-ref", "ref-to-ref", "skill-to-ref"}

    def test_ref_nodes_carry_their_domain(self, client: TestClient) -> None:
        nodes = {n["id"]: n for n in client.get("/api/graph").json()["nodes"]}
        assert nodes["REF-Alpha"]["domain"] == "language"
        assert nodes["AI-PLAYBOOK"]["domain"] is None


class TestRefDetail:
    def test_ref_detail_parses_sections(self, client: TestClient) -> None:
        resp = client.get("/api/refs/REF-Alpha")
        assert resp.status_code == 200
        ref = resp.json()
        assert ref["title"] == "Alpha"
        assert ref["summary"] == "Alpha conventions."
        assert [s["number"] for s in ref["sections"]] == [1, 2]

    def test_generated_section_is_flagged(self, client: TestClient) -> None:
        sections = client.get("/api/refs/REF-Alpha").json()["sections"]
        by_number = {s["number"]: s for s in sections}
        assert by_number[2]["generated"] is True
        assert by_number[1]["generated"] is False

    def test_unknown_ref_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/refs/REF-Nope")
        assert resp.status_code == 404
        assert resp.json()["error"] == "EntityNotFoundError"


class TestPlaybook:
    def test_playbook_sections_are_parsed(self, client: TestClient) -> None:
        resp = client.get("/api/playbook")
        assert resp.status_code == 200
        doc = resp.json()
        assert doc["title"] == "AI Playbook"
        titles = [s["title"] for s in doc["sections"]]
        assert "Top Violations - Check EVERY Change" in titles
        violations = next(s for s in doc["sections"] if s["title"].startswith("Top Violations"))
        assert "Do not duplicate" in violations["body"]


class TestClaims:
    def test_claims_are_listed(self, client: TestClient) -> None:
        claims = client.get("/api/claims").json()
        assert [c["claim_id"] for c in claims] == ["INT-001"]
        assert claims[0]["criticality"] == "high"


class TestUpdateSection:
    def test_edit_survives_when_gates_pass(self, client: TestClient) -> None:
        resp = client.put(
            "/api/refs/REF-Alpha/sections/1",
            json={"body": "Always be Alpha, twice. See `REF-Beta.md`."},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        body = client.get("/api/refs/REF-Alpha").json()["sections"][0]["body"]
        assert "twice" in body

    def test_edit_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        original = failing_client.get("/api/refs/REF-Alpha").json()["sections"][0]["body"]
        resp = failing_client.put(
            "/api/refs/REF-Alpha/sections/1",
            json={"body": "This edit must not survive."},
        )
        assert resp.status_code == 422
        assert resp.json()["error"] == "ValidationFailedError"
        assert resp.json()["report"]["ok"] is False
        after = failing_client.get("/api/refs/REF-Alpha").json()["sections"][0]["body"]
        assert after == original

    def test_generated_section_is_immutable(self, client: TestClient) -> None:
        resp = client.put(
            "/api/refs/REF-Alpha/sections/2",
            json={"body": "hand edit"},
        )
        assert resp.status_code == 409
        assert resp.json()["error"] == "GeneratedSectionError"

    def test_missing_section_returns_404(self, client: TestClient) -> None:
        resp = client.put("/api/refs/REF-Beta/sections/9", json={"body": "x"})
        assert resp.status_code == 404


class TestValidation:
    def test_validate_returns_report(self, client: TestClient) -> None:
        resp = client.post("/api/validate")
        assert resp.status_code == 200
        report = resp.json()
        assert report["ok"] is True
        assert report["tests_passed"] is True
