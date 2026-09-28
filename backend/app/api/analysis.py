from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analysis_orchestrator import analysis_orchestrator
from app.schemas.api_schemas import FrameAnalysisResponse

router = APIRouter(tags=["Analysis"])

@router.post("/analyze/image", response_model=FrameAnalysisResponse)
async def analyze_endoscopic_image(
    file: UploadFile = File(...),
    examination_id: Optional[str] = Form(None),
    patient_anon_id: Optional[str] = Form("ANON-PATIENT"),
    db: Session = Depends(get_db)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be a valid endoscopic image (JPG, PNG, WEBP).")

    content = await file.read()
    if len(content) > 30 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Uploaded file size exceeds 30MB maximum limit.")

    try:
        res = analysis_orchestrator.analyze_image_bytes(
            image_bytes=content,
            db=db,
            examination_id=examination_id,
            patient_anon_id=patient_anon_id
        )
        return FrameAnalysisResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")

@router.post("/analyze/video")
async def analyze_endoscopic_video(
    file: UploadFile = File(...),
    patient_anon_id: Optional[str] = Form("ANON-PATIENT"),
    db: Session = Depends(get_db)
):
    filename = file.filename or "video.mp4"
    ext_valid = filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))
    if not ext_valid and (not file.content_type or not file.content_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="File must be a valid endoscopic video file (MP4, AVI, MOV, MKV).")

    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Uploaded video file size exceeds 100MB limit.")

    try:
        res = analysis_orchestrator.analyze_video_bytes(
            video_bytes=content,
            filename=filename,
            db=db,
            patient_anon_id=patient_anon_id
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis error: {str(e)}")
