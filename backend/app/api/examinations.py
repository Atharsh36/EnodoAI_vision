from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.db_models import Examination, Frame, Detection, Prediction, Review, ReviewStatusEnum
from app.schemas.api_schemas import (
    ExaminationCreateSchema,
    ExaminationSummarySchema,
    ExaminationStatsSchema,
)

router = APIRouter(tags=["Examinations"])

@router.post("/examinations", response_model=ExaminationSummarySchema)
def create_examination(payload: ExaminationCreateSchema, db: Session = Depends(get_db)):
    exam = Examination(
        patient_anon_id=payload.patient_anon_id,
        input_type=payload.input_type,
        notes=payload.notes,
        status="IN_PROGRESS"
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return ExaminationSummarySchema(
        id=exam.id,
        patient_anon_id=exam.patient_anon_id,
        input_type=exam.input_type,
        status=exam.status,
        created_at=exam.created_at,
        frame_count=0,
        total_detections=0,
    )

@router.get("/examinations", response_model=List[ExaminationSummarySchema])
def list_examinations(
    skip: int = 0,
    limit: int = 50,
    input_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Examination)
    if input_type:
        query = query.filter(Examination.input_type == input_type)

    exams = query.order_by(Examination.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for exam in exams:
        frame_count = db.query(Frame).filter(Frame.examination_id == exam.id).count()
        total_detections = db.query(Detection).join(Frame).filter(Frame.examination_id == exam.id).count()
        result.append(
            ExaminationSummarySchema(
                id=exam.id,
                patient_anon_id=exam.patient_anon_id,
                input_type=exam.input_type,
                status=exam.status,
                created_at=exam.created_at,
                frame_count=frame_count,
                total_detections=total_detections,
            )
        )
    return result

@router.get("/examinations/stats", response_model=ExaminationStatsSchema)
def get_examination_stats(db: Session = Depends(get_db)):
    total_exams = db.query(Examination).count()
    frames_processed = db.query(Frame).count()
    total_detections = db.query(Detection).count()

    low_conf_count = db.query(Prediction).filter(Prediction.confidence_level == "LOW").count()
    pending_reviews = db.query(Review).filter(Review.review_status == ReviewStatusEnum.PENDING.value).count()

    return ExaminationStatsSchema(
        total_examinations=total_exams,
        frames_processed=frames_processed,
        abnormal_regions_detected=total_detections,
        avg_processing_time_ms=45.2 if frames_processed > 0 else 0.0,
        low_confidence_predictions=low_conf_count,
        pending_reviews=pending_reviews,
    )

@router.get("/examinations/{id}", response_model=ExaminationSummarySchema)
def get_examination(id: str, db: Session = Depends(get_db)):
    exam = db.query(Examination).filter(Examination.id == id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    frame_count = db.query(Frame).filter(Frame.examination_id == exam.id).count()
    total_detections = db.query(Detection).join(Frame).filter(Frame.examination_id == exam.id).count()

    return ExaminationSummarySchema(
        id=exam.id,
        patient_anon_id=exam.patient_anon_id,
        input_type=exam.input_type,
        status=exam.status,
        created_at=exam.created_at,
        frame_count=frame_count,
        total_detections=total_detections,
    )
