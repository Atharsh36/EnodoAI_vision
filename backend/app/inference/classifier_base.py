from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class ClassifierBase(ABC):
    """
    Abstract Base Class for cropped endoscopic region classification.
    """

    @abstractmethod
    def classify(self, crop_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Classifies cropped region of interest image array.
        Returns:
        {
            "predicted_class": str,
            "class_confidence": float,
            "confidence_level": str, # HIGH, MEDIUM, LOW
            "raw_softmax_scores": Dict[str, float],
            "human_review_recommended": bool
        }
        """
        pass
