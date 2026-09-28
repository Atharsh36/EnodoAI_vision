from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Examination, Frame, Detection, Prediction, Explanation, Review, QualityResult
from app.reporting.pdf_generator import ReportGenerator

router = APIRouter(tags=["Reports"])

def compile_examination_report_dict(exam_id: str, db: Session):
    exam = db.query(Examination).filter(Examination.id == exam_id).first()
    if not exam:
        return None

    frames = db.query(Frame).filter(Frame.examination_id == exam.id).all()
    frames_data = []
    all_detections = []

    for f in frames:
        detections = db.query(Detection).filter(Detection.frame_id == f.id).all()
        dets_data = []
        for d in detections:
            pred = db.query(Prediction).filter(Prediction.detection_id == d.id).first()
            exp = db.query(Explanation).filter(Explanation.prediction_id == pred.id).first() if pred else None
            review = db.query(Review).filter(Review.detection_id == d.id).first()

            det_obj = {
                "id": d.id,
                "region_index": d.region_index,
                "frame_index": f.frame_index,
                "bbox": {"x1": d.bbox_x1, "y1": d.bbox_y1, "x2": d.bbox_x2, "y2": d.bbox_y2},
                "detection_confidence": d.detection_confidence,
                "class_name": d.detected_class,
                "prediction": {
                    "predicted_class": pred.predicted_class if pred else d.detected_class,
                    "class_confidence": pred.class_confidence if pred else d.detection_confidence,
                    "confidence_level": pred.confidence_level if pred else "HIGH",
                    "raw_softmax_scores": pred.raw_softmax_scores if pred else {}
                },
                "explanation": {
                    "heatmap_url": exp.heatmap_path if exp else None,
                    "overlay_url": exp.overlay_path if exp else None,
                    "target_layer": exp.target_layer if exp else "layer4"
                },
                "review": {
                    "status": review.review_status if review else "PENDING",
                    "notes": review.reviewer_notes if review else None,
                    "reviewer_id": review.reviewer_id if review else None
                }
            }
            dets_data.append(det_obj)
            all_detections.append(det_obj)

        frames_data.append({
            "frame_id": f.id,
            "frame_index": f.frame_index,
            "image_url": f.image_path,
            "detections": dets_data
        })

    quality_info = {"overall_quality": "GOOD", "blur_score": 120.0, "brightness_score": 110.0, "warnings": []}
    if frames:
        q = db.query(QualityResult).filter(QualityResult.frame_id == frames[0].id).first()
        if q:
            quality_info = {
                "overall_quality": q.overall_quality,
                "blur_score": q.blur_score,
                "brightness_score": q.brightness_score,
                "warnings": q.warnings or []
            }

    return {
        "id": exam.id,
        "patient_anon_id": exam.patient_anon_id,
        "input_type": exam.input_type,
        "status": exam.status,
        "created_at": exam.created_at.isoformat(),
        "frames": frames_data,
        "detections": all_detections,
        "quality": quality_info
    }

@router.get("/reports/{id}")
def get_json_report(id: str, db: Session = Depends(get_db)):
    data = compile_examination_report_dict(id, db)
    if not data:
        raise HTTPException(status_code=404, detail="Examination report not found.")
    return data

@router.get("/reports/{id}/pdf")
def get_pdf_report(id: str, db: Session = Depends(get_db)):
    data = compile_examination_report_dict(id, db)
    if not data:
        raise HTTPException(status_code=404, detail="Examination report not found.")

    pdf_bytes = ReportGenerator.generate_pdf_report_bytes(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=EndoAI_Report_{id[:8]}.pdf"}
    )
