from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QualityMetricsSchema(BaseModel):
    overall_quality: str
    blur_score: float
    brightness_score: float
    warnings: List[str]

class BoundingBoxSchema(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class PredictionSchema(BaseModel):
    id: Optional[str] = None
    predicted_class: str
    class_confidence: float
    confidence_level: str  # HIGH, MEDIUM, LOW
    raw_softmax_scores: Dict[str, float]
    human_review_recommended: bool = False

class ExplanationSchema(BaseModel):
    id: Optional[str] = None
    heatmap_url: Optional[str] = None
    overlay_url: Optional[str] = None
    target_layer: str = "layer4"

class DetectionSchema(BaseModel):
    id: Optional[str] = None
    region_id: str
    region_index: int
    class_name: str
    confidence: float
    bbox: BoundingBoxSchema
    prediction: Optional[PredictionSchema] = None
    explanation: Optional[ExplanationSchema] = None

class FrameAnalysisResponse(BaseModel):
    frame_id: str
    examination_id: str
    frame_index: int
    timestamp_ms: float
    image_url: str
    quality: QualityMetricsSchema
    detections: List[DetectionSchema]
    review_status: str = "PENDING"
    created_at: datetime

class ReviewCreateSchema(BaseModel):
    examination_id: Optional[str] = None
    frame_id: Optional[str] = None
    detection_id: Optional[str] = None
    review_status: str  # ACCEPTED, REJECTED, NEEDS_REVIEW
    reviewer_notes: Optional[str] = None
    reviewer_id: str = "DR-CLINICIAN-01"

class ReviewResponseSchema(BaseModel):
    id: str
    examination_id: Optional[str] = None
    frame_id: Optional[str] = None
    detection_id: Optional[str] = None
    review_status: str
    reviewer_notes: Optional[str] = None
    reviewer_id: str
    updated_at: datetime

class ExaminationCreateSchema(BaseModel):
    patient_anon_id: Optional[str] = "ANON-PATIENT"
    input_type: str = "IMAGE"
    notes: Optional[str] = None

class ExaminationSummarySchema(BaseModel):
    id: str
    patient_anon_id: Optional[str]
    input_type: str
    status: str
    created_at: datetime
    frame_count: int = 0
    total_detections: int = 0

class ExaminationStatsSchema(BaseModel):
    total_examinations: int
    frames_processed: int
    abnormal_regions_detected: int
    avg_processing_time_ms: float
    low_confidence_predictions: int
    pending_reviews: int

class ModelInfoSchema(BaseModel):
    name: str
    version: str
    type: str
    status: str  # DEMO, RESEARCH, VALIDATED
    classes: List[str]
    input_size: List[int]
    description: str
    loaded_at: Optional[datetime] = None

class SystemHealthSchema(BaseModel):
    status: str
    project_name: str
    version: str
    gpu_available: bool
    device: str
    model_status: str
    database_connected: bool
    medical_disclaimer: str
