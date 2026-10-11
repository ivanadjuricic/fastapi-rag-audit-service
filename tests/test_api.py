from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "online"}


def test_ask_requires_document():
    app.dependency_overrides = {}
    from app.main import STATE
    STATE.update(index=None, df=None)
    assert client.post("/ask", json={"question": "x"}).status_code == 409


def test_full_flow():
    with open("data/support_tickets.xlsx", "rb") as f:
        r = client.post("/documents", files={"file": ("support_tickets.xlsx", f)})
    assert r.status_code == 200 and r.json()["profile"]["rows"] == 500
    r = client.post("/ask", json={"question": "billing invoice mismatch", "top_k": 3})
    assert r.status_code == 200 and len(r.json()["sources"]) == 3
    assert "row" in r.json()["sources"][0]
    assert client.get("/stats/ResolutionHours?group_by=Priority").status_code == 200
    assert client.get("/export?column=ResolutionHours&group_by=Priority").status_code == 200
