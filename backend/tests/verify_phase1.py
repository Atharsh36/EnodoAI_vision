import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from app.models.db_models import Examination, Frame, Detection, Prediction, Review, ModelVersion

def run_phase1_verification():
    print("=== STARTING PHASE 1 VERIFICATION ===")

    # 1. Database table initialization check
    print("\n[1/4] Initializing Database Schema...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully.")

    # 2. FastAPI TestClient
    client = TestClient(app)

    # 3. Test Root Endpoint
    print("\n[2/4] Testing Root Endpoint...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] Root endpoint output: {res.json()['project']}")

    # 4. Test Health Endpoint
    print("\n[3/4] Testing Health API Endpoint...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.json()
    assert health_data["status"] in ["healthy", "degraded"]
    assert "medical_disclaimer" in health_data
    print(f"[OK] Health API returned status: {health_data['status']} | GPU: {health_data['gpu_available']}")

    # 5. Test Models Endpoint
    print("\n[4/4] Testing Models Info Endpoint...")
    res = client.get("/api/models")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    models_data = res.json()
    assert len(models_data) >= 2, f"Expected at least 2 models, got {len(models_data)}"
    print(f"[OK] Loaded models info count: {len(models_data)} ({models_data[0]['name']}, {models_data[1]['name']})")

    # 6. Test Examinations Stats Endpoint
    res = client.get("/api/examinations/stats")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    stats_data = res.json()
    print(f"[OK] Examination stats: Total Exams={stats_data['total_examinations']}, Frames={stats_data['frames_processed']}")

    print("\n=== PHASE 1 VERIFICATION PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_phase1_verification()
