from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict, Any

class DetectorBase(ABC):
    """
    Abstract Base Class for endoscopic abnormality object detection.
    Allows runtime swapping between Ultralytics YOLO models and dev demo abstractions.
    """

    @abstractmethod
    def detect(
        self,
        image_bgr: np.ndarray,
        confidence_threshold: float = 0.50,
        iou_threshold: float = 0.45,
        max_detections: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Processes BGR image numpy array and returns list of detected abnormality regions.
        Each detection dictionary format:
        {
            "region_id": str,
            "region_index": int,
            "class_id": int,
            "class_name": str,
            "confidence": float,
            "bbox": {
                "x1": float,
                "y1": float,
                "x2": float,
                "y2": float
            }
        }
        """
        pass
