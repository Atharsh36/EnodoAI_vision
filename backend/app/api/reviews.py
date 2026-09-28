from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.db_models import Review, ReviewStatusEnum
from app.schemas.api_schemas import ReviewCreateSchema, ReviewResponseSchema

router = APIRouter(tags=["Clinician Review"])

@router.post("/reviews", response_model=ReviewResponseSchema)
def save_clinician_review(payload: ReviewCreateSchema, db: Session = Depends(get_db)):
    if payload.review_status not in [e.value for e in ReviewStatusEnum]:
        raise HTTPException(status_code=400, detail=f"Invalid review status. Must be one of: {[e.value for e in ReviewStatusEnum]}")

    review = Review(
        examination_id=payload.examination_id,
        frame_id=payload.frame_id,
        detection_id=payload.detection_id,
        review_status=payload.review_status,
        reviewer_notes=payload.reviewer_notes,
        reviewer_id=payload.reviewer_id,
        updated_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewResponseSchema(
        id=review.id,
        examination_id=review.examination_id,
        frame_id=review.frame_id,
        detection_id=review.detection_id,
        review_status=review.review_status,
        reviewer_notes=review.reviewer_notes,
        reviewer_id=review.reviewer_id,
        updated_at=review.updated_at
    )
