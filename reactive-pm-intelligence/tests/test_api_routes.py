from fastapi.testclient import TestClient

from backend.main import app
from backend.models.database import init_db


def get_client() -> TestClient:
    init_db()
    return TestClient(app)


def test_health_endpoint_returns_ok():
    client = get_client()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pipeline_and_dashboard_endpoints_work():
    client = get_client()
    token = client.post("/api/v1/auth/token").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    pipeline_response = client.post("/api/v1/pipeline/run", headers=headers)
    assert pipeline_response.status_code == 200
    dashboard_response = client.get("/api/v1/dashboard/kpis", headers=headers)
    assert dashboard_response.status_code == 200
    assert "total_work_orders" in dashboard_response.json()


def test_portfolio_overview_returns_reference_counts():
    client = get_client()
    token = client.post("/api/v1/auth/token").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/pipeline/run", headers=headers)
    response = client.get("/api/v1/portfolio/overview", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["facilities"] >= 1
    assert payload["assets"] >= 1
    assert payload["technicians"] >= 1


def test_assistant_endpoint_returns_quick_actions():
    client = get_client()
    token = client.post("/api/v1/auth/token").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/pipeline/run", headers=headers)
    response = client.post(
        "/api/v1/assistant/chat",
        headers=headers,
        json={"action": "executive-summary", "message": "Summarize this portfolio for leadership."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"]
    assert payload["quick_actions"]
    assert payload["provider"]