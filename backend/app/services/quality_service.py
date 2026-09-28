import os
import cv2
from typing import Dict, Any
from app.quality.metrics import default_evaluator
from app.preprocessing.image_transforms import load_image_bytes

class QualityService:
    @staticmethod
    def evaluate_bytes(image_bytes: bytes) -> Dict[str, Any]:
        image_bgr = load_image_bytes(image_bytes)
        if image_bgr is None:
            return {
                "overall_quality": "POOR",
                "quality_score": 0.0,
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "overexposed_pct": 0.0,
                "underexposed_pct": 0.0,
                "warnings": ["Corrupted or invalid image file upload."]
            }
        return default_evaluator.evaluate(image_bgr)

    @staticmethod
    def evaluate_file_path(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {
                "overall_quality": "POOR",
                "quality_score": 0.0,
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "overexposed_pct": 0.0,
                "underexposed_pct": 0.0,
                "warnings": [f"Image file path not found: {file_path}"]
            }
        img_bgr = cv2.imread(file_path)
        return default_evaluator.evaluate(img_bgr)
