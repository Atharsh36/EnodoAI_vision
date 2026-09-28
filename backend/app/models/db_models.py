import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class InputTypeEnum(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    LIVE = "LIVE"

class ReviewStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class QualityStatusEnum(str, enum.Enum):
    GOOD = "GOOD"
    WARNING = "WARNING"
    POOR = "POOR"

class ModelStatusEnum(str, enum.Enum):
    DEMO = "DEMO"
    RESEARCH = "RESEARCH"
    VALIDATED = "VALIDATED"

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Examination(Base):
    __tablename__ = "examinations"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_anon_id = Column(String, nullable=True, default="ANON-PATIENT")
    input_type = Column(String, nullable=False, default=InputTypeEnum.IMAGE.value)
    status = Column(String, nullable=False, default="COMPLETED")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    frames = relationship("Frame", back_populates="examination", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="examination", cascade="all, delete-orphan")

class Frame(Base):
    __tablename__ = "frames"

    id = Column(String, primary_key=True, default=generate_uuid)
    examination_id = Column(String, ForeignKey("examinations.id"), nullable=False)
    frame_index = Column(Integer, default=0)
    timestamp_ms = Column(Float, default=0.0)
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    examination = relationship("Examination", back_populates="frames")
    quality_result = relationship("QualityResult", back_populates="frame", uselist=False, cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="frame", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="frame", cascade="all, delete-orphan")

class QualityResult(Base):
    __tablename__ = "quality_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    frame_id = Column(String, ForeignKey("frames.id"), nullable=False)
    overall_quality = Column(String, default=QualityStatusEnum.GOOD.value)
    blur_score = Column(Float, nullable=False)
    brightness_score = Column(Float, nullable=False)
    warnings = Column(JSON, default=list)

    frame = relationship("Frame", back_populates="quality_result")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String, primary_key=True, default=generate_uuid)
    frame_id = Column(String, ForeignKey("frames.id"), nullable=False)
    region_index = Column(Integer, nullable=False)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    detection_confidence = Column(Float, nullable=False)
    detected_class = Column(String, nullable=False)

    frame = relationship("Frame", back_populates="detections")
    prediction = relationship("Prediction", back_populates="detection", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="detection", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    detection_id = Column(String, ForeignKey("detections.id"), nullable=False)
    predicted_class = Column(String, nullable=False)
    class_confidence = Column(Float, nullable=False)
    confidence_level = Column(String, nullable=False, default="HIGH") # HIGH, MEDIUM, LOW
    raw_softmax_scores = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    detection = relationship("Detection", back_populates="prediction")
    explanation = relationship("Explanation", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(String, primary_key=True, default=generate_uuid)
    prediction_id = Column(String, ForeignKey("predictions.id"), nullable=False)
    heatmap_path = Column(String, nullable=True)
    overlay_path = Column(String, nullable=True)
    target_layer = Column(String, default="layer4")

    prediction = relationship("Prediction", back_populates="explanation")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    examination_id = Column(String, ForeignKey("examinations.id"), nullable=True)
    frame_id = Column(String, ForeignKey("frames.id"), nullable=True)
    detection_id = Column(String, ForeignKey("detections.id"), nullable=True)
    review_status = Column(String, default=ReviewStatusEnum.PENDING.value)
    reviewer_notes = Column(Text, nullable=True)
    reviewer_id = Column(String, default="DR-CLINICIAN-01")
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    examination = relationship("Examination", back_populates="reviews")
    frame = relationship("Frame", back_populates="reviews")
    detection = relationship("Detection", back_populates="reviews")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    classes = Column(JSON, nullable=False)
    status = Column(String, default=ModelStatusEnum.DEMO.value)
    is_active = Column(Boolean, default=True)
    loaded_at = Column(DateTime(timezone=True), default=utc_now)
