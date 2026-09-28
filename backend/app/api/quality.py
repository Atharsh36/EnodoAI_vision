from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.quality_service import QualityService
from app.schemas.api_schemas import QualityMetricsSchema

router = APIRouter(tags=["Quality Check"])

@router.post("/quality/evaluate", response_model=QualityMetricsSchema)
async def evaluate_image_quality(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (JPG, PNG, WEBP).")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Uploaded image exceeds 25MB maximum size limit.")

    result = QualityService.evaluate_bytes(content)
    return QualityMetricsSchema(
        overall_quality=result["overall_quality"],
        blur_score=result["blur_score"],
        brightness_score=result["brightness_score"],
        warnings=result["warnings"],
    )
