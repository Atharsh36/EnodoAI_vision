from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from app.database import get_db
from app.config import settings
from app.schemas.api_schemas import SystemHealthSchema

router = APIRouter(tags=["Health"])

MEDICAL_DISCLAIMER = (
    "EndoAI Vision is a research and decision-support prototype. AI-generated outputs are not a substitute "
    "for professional medical judgment and must not be used as an autonomous diagnosis. Clinical use requires "
    "appropriate validation, calibration, safety assessment, regulatory compliance, and review by qualified "
    "healthcare professionals."
)

@router.get("/health", response_model=SystemHealthSchema)
def get_system_health(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    gpu_available = torch.cuda.is_available() if HAS_TORCH else False
    device = "cuda" if gpu_available else "cpu"

    return SystemHealthSchema(
        status="healthy" if db_ok else "degraded",
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        gpu_available=gpu_available,
        device=device,
        model_status="DEMO" if settings.USE_DEMO_FALLBACK else "LOADED",
        database_connected=db_ok,
        medical_disclaimer=MEDICAL_DISCLAIMER,
    )
