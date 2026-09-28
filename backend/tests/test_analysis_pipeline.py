import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base, SessionLocal
from app.services.analysis_orchestrator import analysis_orchestrator

def test_full_analysis_pipeline():
    print("=== TESTING END-TO-END ANALYSIS PIPELINE ===")

    # 1. Initialize DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 2. Create synthetic endoscopic image frame with a mucosal lesion spot
    img = np.full((400, 400, 3), (40, 50, 180), dtype=np.uint8)  # Endoscopic mucosa reddish hue
    cv2.circle(img, (200, 200), 45, (80, 120, 240), -1)          # Synthetic polyp lesion

    _, encoded_bytes = cv2.imencode(".png", img)

    # 3. Execute Analysis Pipeline
    res = analysis_orchestrator.analyze_image_bytes(
        image_bytes=encoded_bytes.tobytes(),
        db=db,
        patient_anon_id="TEST-PATIENT-01"
    )

    db.close()

    # 4. Assertions
    assert "frame_id" in res
    assert "quality" in res
    assert "detections" in res
    assert len(res["detections"]) > 0, "Expected at least 1 detection region"

    first_det = res["detections"][0]
    assert "bbox" in first_det
    assert "prediction" in first_det
    assert "explanation" in first_det

    pred = first_det["prediction"]
    exp = first_det["explanation"]

    assert "predicted_class" in pred
    assert "raw_softmax_scores" in pred
    assert "heatmap_url" in exp
    assert "overlay_url" in exp

    print(f"[OK] Examination ID: {res['examination_id']}")
    print(f"[OK] Quality Status: {res['quality']['overall_quality']} (Blur score: {res['quality']['blur_score']})")
    print(f"[OK] Detected Regions Count: {len(res['detections'])}")
    print(f"[OK] Region 1 Prediction: {pred['predicted_class']} (Confidence: {pred['class_confidence']:.2%})")
    print(f"[OK] Grad-CAM Overlay Generated: {exp['overlay_url']}")
    print("=== END-TO-END ANALYSIS PIPELINE TEST PASSED! ===")

if __name__ == "__main__":
    test_full_analysis_pipeline()
