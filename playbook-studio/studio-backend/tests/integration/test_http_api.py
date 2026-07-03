"""HTTP integration tests: real app, real file I/O against a synthetic playbook."""

from __future__ import annotations

from fastapi.testclient import TestClient
from pytest_intent import intent


class TestSystem:
    def test_health_returns_ok(self, client: TestClient) -> None:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestGraph:
    @intent("INT-GRAPH-001")
    def test_graph_contains_playbook_refs_and_skills(self, client: TestClient) -> None:
        resp = client.get("/api/graph")
        assert resp.status_code == 200
        graph = resp.json()
        ids = {n["id"] for n in graph["nodes"]}
        assert {"AI-PLAYBOOK", "REF-Alpha", "REF-Beta", "do-alpha"} <= ids

    @intent("INT-GRAPH-001")
    def test_graph_has_all_three_edge_kinds(self, client: TestClient) -> None:
        kinds = {e["kind"] for e in client.get("/api/graph").json()["edges"]}
        assert kinds == {"playbook-to-ref", "ref-to-ref", "skill-to-ref"}

    @intent("INT-GRAPH-001")
    def test_ref_nodes_carry_their_domain(self, client: TestClient) -> None:
        nodes = {n["id"]: n for n in client.get("/api/graph").json()["nodes"]}
        assert nodes["REF-Alpha"]["domain"] == "language"
        assert nodes["AI-PLAYBOOK"]["domain"] is None

    @intent("INT-GRAPH-001")
    def test_nodes_carry_summaries(self, client: TestClient) -> None:
        nodes = {n["id"]: n for n in client.get("/api/graph").json()["nodes"]}
        assert nodes["REF-Alpha"]["summary"] == "Alpha conventions."
        assert nodes["do-alpha"]["summary"].startswith("Do the alpha thing.")


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
    @intent("INT-GATE-001")
    def test_edit_survives_when_gates_pass(self, client: TestClient) -> None:
        resp = client.put(
            "/api/refs/REF-Alpha/sections/1",
            json={"body": "Always be Alpha, twice. See `REF-Beta.md`."},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        body = client.get("/api/refs/REF-Alpha").json()["sections"][0]["body"]
        assert "twice" in body

    @intent("INT-GATE-001")
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

    @intent("INT-GATE-002")
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


class TestUpdateDocument:
    @intent("INT-GATE-001")
    def test_full_rewrite_survives_when_gates_pass(self, client: TestClient) -> None:
        original = client.get("/api/refs/REF-Beta").json()["raw"]
        rewritten = original.replace("## 1. Guidance", "## 1. Guidance (revised)")
        resp = client.put("/api/refs/REF-Beta", json={"raw": rewritten})
        assert resp.status_code == 200
        after = client.get("/api/refs/REF-Beta").json()
        assert after["sections"][0]["title"] == "Guidance (revised)"

    @intent("INT-GATE-001")
    def test_full_rewrite_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        original = failing_client.get("/api/refs/REF-Beta").json()["raw"]
        resp = failing_client.put("/api/refs/REF-Beta", json={"raw": "# REF: Broken\n"})
        assert resp.status_code == 422
        assert failing_client.get("/api/refs/REF-Beta").json()["raw"] == original


class TestCreateRef:
    _PAYLOAD = {
        "name": "REF-Gamma",
        "domain": "practice",
        "title": "Gamma",
        "summary": "Gamma practices.",
    }

    @intent("INT-DERIVE-001")
    def test_create_survives_when_gates_pass(self, client: TestClient) -> None:
        resp = client.post("/api/refs", json=self._PAYLOAD)
        assert resp.status_code == 201
        created = client.get("/api/refs/REF-Gamma").json()
        assert created["domain"] == "practice"
        assert [s["number"] for s in created["sections"]] == [1]

    def test_duplicate_name_returns_409(self, client: TestClient) -> None:
        assert client.post("/api/refs", json=self._PAYLOAD).status_code == 201
        assert client.post("/api/refs", json=self._PAYLOAD).status_code == 409

    def test_bad_name_returns_400(self, client: TestClient) -> None:
        resp = client.post("/api/refs", json={**self._PAYLOAD, "name": "gamma"})
        assert resp.status_code == 400
        assert resp.json()["error"] == "InvalidRefInputError"

    @intent("INT-GATE-001")
    def test_create_is_removed_when_gates_fail(self, failing_client: TestClient) -> None:
        resp = failing_client.post("/api/refs", json=self._PAYLOAD)
        assert resp.status_code == 422
        assert failing_client.get("/api/refs/REF-Gamma").status_code == 404


class TestSkillDocument:
    def test_skill_detail_is_parsed(self, client: TestClient) -> None:
        resp = client.get("/api/skills/do-alpha")
        assert resp.status_code == 200
        skill = resp.json()
        assert skill["refs"] == ["REF-Alpha"]
        assert skill["body"].startswith("# Do alpha")

    @intent("INT-GATE-001")
    def test_skill_rewrite_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        original = failing_client.get("/api/skills/do-alpha").json()["raw"]
        resp = failing_client.put("/api/skills/do-alpha", json={"raw": "broken"})
        assert resp.status_code == 422
        assert failing_client.get("/api/skills/do-alpha").json()["raw"] == original


class TestSkillFiles:
    def test_files_are_listed_skill_md_first(self, client: TestClient) -> None:
        files = client.get("/api/skills/do-alpha").json()["files"]
        assert files[0] == "SKILL.md"

    def test_file_content_is_served(self, client: TestClient) -> None:
        resp = client.get("/api/skills/do-alpha/files/SKILL.md")
        assert resp.status_code == 200
        assert resp.json()["content"].startswith("---")

    def test_path_traversal_is_rejected(self, client: TestClient) -> None:
        resp = client.get("/api/skills/do-alpha/files/..%2F..%2FREF-Alpha.md")
        assert resp.status_code in (400, 404)

    @intent("INT-GATE-001")
    def test_file_edit_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        original = failing_client.get("/api/skills/do-alpha/files/SKILL.md").json()["content"]
        resp = failing_client.put(
            "/api/skills/do-alpha/files/SKILL.md", json={"raw": "broken"}
        )
        assert resp.status_code == 422
        after = failing_client.get("/api/skills/do-alpha/files/SKILL.md").json()["content"]
        assert after == original


class TestInstallSkill:
    def test_skill_starts_uninstalled(self, client: TestClient) -> None:
        skill = client.get("/api/skills/do-alpha").json()
        assert skill["installed"] is False

    def test_install_copies_and_reports_in_sync(self, client: TestClient) -> None:
        resp = client.post("/api/skills/do-alpha/install")
        assert resp.status_code == 200
        assert resp.json() == {"installed": True, "in_sync": True}
        assert client.get("/api/skills/do-alpha").json()["in_sync"] is True

    def test_master_edit_marks_out_of_sync(self, client: TestClient) -> None:
        client.post("/api/skills/do-alpha/install")
        raw = client.get("/api/skills/do-alpha").json()["raw"]
        client.put("/api/skills/do-alpha", json={"raw": f"{raw}{chr(10)}More.{chr(10)}"})
        skill = client.get("/api/skills/do-alpha").json()
        assert skill["installed"] is True
        assert skill["in_sync"] is False


class TestCreateSkill:
    _PAYLOAD = {"name": "do-beta", "description": "Does beta things.", "refs": ["REF-Beta"]}

    @intent("INT-DERIVE-001")
    def test_create_skill_survives_when_gates_pass(self, client: TestClient) -> None:
        resp = client.post("/api/skills", json=self._PAYLOAD)
        assert resp.status_code == 201
        assert client.get("/api/skills/do-beta").json()["description"] == "Does beta things."
        assert "`do-beta`" in client.get("/api/playbook").json()["raw"]

    def test_duplicate_skill_returns_409(self, client: TestClient) -> None:
        assert client.post("/api/skills", json=self._PAYLOAD).status_code == 201
        assert client.post("/api/skills", json=self._PAYLOAD).status_code == 409

    def test_unknown_ref_returns_400(self, client: TestClient) -> None:
        resp = client.post("/api/skills", json={**self._PAYLOAD, "refs": ["REF-Nope"]})
        assert resp.status_code in (400, 404)

    @intent("INT-GATE-001")
    def test_create_skill_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        playbook_before = failing_client.get("/api/playbook").json()["raw"]
        resp = failing_client.post("/api/skills", json=self._PAYLOAD)
        assert resp.status_code == 422
        assert failing_client.get("/api/skills/do-beta").status_code == 404
        assert failing_client.get("/api/playbook").json()["raw"] == playbook_before


class TestUpdatePlaybook:
    @intent("INT-GATE-001")
    def test_playbook_rewrite_survives_when_gates_pass(self, client: TestClient) -> None:
        original = client.get("/api/playbook").json()["raw"]
        resp = client.put("/api/playbook", json={"raw": original + "\n## Extra\n\nMore.\n"})
        assert resp.status_code == 200
        titles = [s["title"] for s in client.get("/api/playbook").json()["sections"]]
        assert "Extra" in titles

    @intent("INT-GATE-001")
    def test_playbook_rewrite_rolls_back_when_gates_fail(self, failing_client: TestClient) -> None:
        original = failing_client.get("/api/playbook").json()["raw"]
        resp = failing_client.put("/api/playbook", json={"raw": "# Broken\n"})
        assert resp.status_code == 422
        assert failing_client.get("/api/playbook").json()["raw"] == original


class TestValidation:
    def test_validate_returns_report(self, client: TestClient) -> None:
        resp = client.post("/api/validate")
        assert resp.status_code == 200
        report = resp.json()
        assert report["ok"] is True
        assert report["tests_passed"] is True
