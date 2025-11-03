from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_available_backends() -> None:
    response = client.get("/backends")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["key"] == "cpu" for item in payload)


def test_infer_returns_policy() -> None:
    board = [[0] * 7 for _ in range(6)]
    payload = {"board": board, "current_player": 1, "backend": "cpu"}
    response = client.post("/infer", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["policy"]) == 7
    assert abs(sum(body["policy"]) - 1.0) < 1e-5


def test_metrics_summary_updates() -> None:
    board = [[0] * 7 for _ in range(6)]
    client.post("/infer", json={"board": board, "current_player": 1})
    summary = client.get("/metrics/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert "overall" in payload
    assert "latency_ms" in payload["overall"]
