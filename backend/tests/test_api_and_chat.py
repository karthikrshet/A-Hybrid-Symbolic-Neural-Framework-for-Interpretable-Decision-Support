from fastapi.testclient import TestClient

from app.main import app


def test_domains_decision_history_and_feedback() -> None:
    with TestClient(app) as c:
        domains = c.get("/api/domains").json()
        assert len(domains) == 5
        detail = c.get("/api/domains/education").json()
        inputs = detail["presets"][0]["inputs"]
        r = c.post("/api/decisions", json={"domain": "education", "inputs": inputs})
        assert r.status_code == 200
        did = r.json()["id"]
        assert c.get(f"/api/decisions/{did}").status_code == 200
        assert c.post(f"/api/decisions/{did}/feedback", json={"rating": 5}).json()["saved"]
        stats = c.get("/api/stats").json()
        assert stats["total_decisions"] >= 1 and stats["avg_feedback"] == 5
        assert c.get("/api/decisions/nope").status_code == 404
        assert c.post("/api/decisions", json={"domain": "nope", "inputs": {}}).status_code == 404


def test_chat_routes_extracts_and_supports_what_if() -> None:
    with TestClient(app) as c:
        first = c.post("/api/chat/message", json={"message": "My service has CPU 95%, memory 92%, API response time 8 seconds, error rate 25% and is unhealthy"}).json()
        msg = first["message"]
        assert msg["kind"] == "decision"
        assert msg["routing"]["domain"] == "it_troubleshooting"
        assert msg["routing"]["extracted"]["response_time_ms"] == 8000
        assert msg["decision"]["final_decision"]["level"] == 2
        sid = first["session_id"]

        follow = c.post("/api/chat/message", json={"message": "what if the error rate was 1 and cpu 40", "session_id": sid}).json()["message"]
        assert follow["routing"]["what_if"]
        assert follow["decision"]["inputs"]["memory_utilization"] == 92  # remembered from the first turn

        session = c.get(f"/api/chat/sessions/{sid}").json()
        assert len(session["messages"]) == 4
        assert c.post("/api/chat/message", json={"message": "hello", "session_id": sid}).json()["message"]["kind"] == "text"
        assert c.post("/api/chat/message", json={"message": "show the finance rules", "session_id": sid}).json()["message"]["kind"] == "rules"
        assert c.delete(f"/api/chat/sessions/{sid}").json()["deleted"]


def test_chat_asks_for_missing_details_and_accepts_form() -> None:
    with TestClient(app) as c:
        m = c.post("/api/chat/message", json={"message": "can I get a loan?"}).json()
        assert m["message"]["kind"] == "clarify"
        form = m["message"]["form"]
        form["inputs"]["credit_score"] = 560
        r = c.post("/api/chat/message", json={"session_id": m["session_id"], "structured": {"domain": "finance", "inputs": form["inputs"]}}).json()
        assert r["message"]["kind"] == "decision"
        assert r["message"]["decision"]["fusion"]["override_applied"] or r["message"]["decision"]["final_decision"]["level"] == 2


def test_domain_picker_overrides_auto_routing_and_reports_accuracy() -> None:
    with TestClient(app) as c:
        # "score" alone is ambiguous; the picker forces the education agents
        m = c.post("/api/chat/message", json={"message": "attendance 70, assignment 40, exam 45, mock 38", "domain": "education"}).json()["message"]
        assert m["routing"]["domain"] == "education" and m["routing"]["domain_confidence"] == 1.0
        assert "selected by user" in m["routing"]["method"]
        assert m["kind"] == "decision"
        assert m["accuracy"]["test_samples"] > 0 and 0 < m["accuracy"]["hybrid_accuracy"] <= 1
        assert "Measured accuracy" in m["content"]

        # an obvious IT message sent with Healthcare selected is re-routed, and the user is told
        h = c.post("/api/chat/message", json={"message": "cpu 95% memory 92%", "domain": "healthcare"}).json()["message"]
        assert h["routing"]["domain"] == "it_troubleshooting" and h["picker_overridden"]
        assert c.post("/api/chat/message", json={"message": "hi", "domain": "nope"}).status_code == 404


def test_follow_up_flows_and_llm_fallback() -> None:
    with TestClient(app) as c:
        first = c.post("/api/chat/message", json={"message": "can I get a loan? my income is 40000"}).json()
        sid = first["session_id"]
        assert first["message"]["kind"] == "clarify"
        assert "Use typical values" in first["message"]["suggestions"]
        # idle nudge reminds the user what is missing
        n = c.post(f"/api/chat/sessions/{sid}/nudge").json()["message"]
        assert n["kind"] == "nudge" and "Credit score" in n["content"]
        assert c.post(f"/api/chat/sessions/{sid}/nudge").status_code == 409  # only one nudge in a row
        # "use typical values" completes the analysis with remembered + typical parameters
        d = c.post("/api/chat/message", json={"message": "use typical values", "session_id": sid}).json()["message"]
        assert d["kind"] == "decision" and d["decision"]["inputs"]["monthly_income"] == 40000

        # no LLM configured -> offline mode; an invalid key falls back gracefully instead of failing
        assert c.get("/api/chat/llm/status", headers={"X-LLM-Provider": "off"}).json()["enabled"] is False
        bad = {"X-LLM-Provider": "openai", "X-LLM-Key": "sk-invalid", "X-LLM-Model": "gpt-4o-mini"}
        r = c.post("/api/chat/message", json={"message": "income 60000, credit score 720, loan 5 lakh"}, headers=bad).json()["message"]
        assert r["kind"] == "decision"
        assert r["routing"]["llm"]["provider"] == "openai" and r["routing"]["llm"]["used"] is False
