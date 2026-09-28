import os
import json
from typing import List
from fastapi import APIRouter
from app.config import settings
from app.schemas.api_schemas import ModelInfoSchema

router = APIRouter(tags=["Models"])

@router.get("/models", response_model=List[ModelInfoSchema])
def list_available_models():
    models_info = []

    # Detector model registry
    if os.path.exists(settings.DETECTOR_REGISTRY_PATH):
        try:
            with open(settings.DETECTOR_REGISTRY_PATH, "r") as f:
                det_data = json.load(f)
                models_info.append(
                    ModelInfoSchema(
                        name=det_data.get("name", "EndoAI Detector"),
                        version=det_data.get("version", "0.1.0"),
                        type=det_data.get("type", "YOLOv8"),
                        status=det_data.get("status", "DEMO"),
                        classes=det_data.get("classes", []),
                        input_size=det_data.get("input_size", [640, 640]),
                        description=det_data.get("description", "Abnormality detector model"),
                    )
                )
        except Exception:
            pass

    # Classifier model registry
    if os.path.exists(settings.CLASSIFIER_REGISTRY_PATH):
        try:
            with open(settings.CLASSIFIER_REGISTRY_PATH, "r") as f:
                cls_data = json.load(f)
                models_info.append(
                    ModelInfoSchema(
                        name=cls_data.get("name", "EndoAI Lesion Classifier"),
                        version=cls_data.get("version", "0.1.0"),
                        type=cls_data.get("type", "PyTorch CNN"),
                        status=cls_data.get("status", "DEMO"),
                        classes=cls_data.get("classes", []),
                        input_size=cls_data.get("input_size", [224, 224]),
                        description=cls_data.get("description", "Softmax lesion classifier"),
                    )
                )
        except Exception:
            pass

    return models_info
