from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert data["project"] == "EndoAI Vision"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "medical_disclaimer" in data
    assert "gpu_available" in data

def test_models_endpoint():
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_examinations_stats():
    response = client.get("/api/examinations/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_examinations" in data
    assert "frames_processed" in data
