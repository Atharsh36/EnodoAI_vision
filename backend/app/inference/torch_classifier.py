import os
import numpy as np
from typing import Dict, List, Any
from app.inference.classifier_base import ClassifierBase
from app.config import settings

def softmax(logits: np.ndarray) -> np.ndarray:
    """
    Mathematical Softmax formulation:
    p_k = exp(s_k) / sum(exp(s_j))
    Subtractions of max logit applied for numerical stability.
    """
    exp_s = np.exp(logits - np.max(logits))
    return exp_s / np.sum(exp_s)


class DemoClassifier(ClassifierBase):
    """
    Demonstration Softmax Classifier with explicit Softmax probability normalization math.
    """

    def __init__(self, classes: List[str] = None):
        if classes is None:
            self.classes = [
                "Polyp (Adenomatous)",
                "Polyp (Hyperplastic)",
                "Ulcerative Lesion",
                "Active Bleeding",
                "Esophagitis (Grade A/B)",
                "Normal Mucosa"
            ]
        else:
            self.classes = classes

    def classify(self, crop_bgr: np.ndarray) -> Dict[str, Any]:
        if crop_bgr is None or crop_bgr.size == 0:
            default_scores = {c: round(1.0 / len(self.classes), 4) for c in self.classes}
            return {
                "predicted_class": self.classes[-1],
                "class_confidence": 0.50,
                "confidence_level": "LOW",
                "raw_softmax_scores": default_scores,
                "human_review_recommended": True,
            }

        # Calculate synthetic logit features based on image color intensity variance
        mean_bgr = np.mean(crop_bgr, axis=(0, 1))
        std_bgr = np.std(crop_bgr, axis=(0, 1))

        # Build raw logit vector s_k
        logits = np.array([
            mean_bgr[2] * 0.05 + std_bgr[0] * 0.1,    # Adenomatous Polyp
            mean_bgr[1] * 0.04 + std_bgr[1] * 0.08,   # Hyperplastic Polyp
            mean_bgr[0] * 0.06 + std_bgr[2] * 0.07,   # Ulcerative Lesion
            mean_bgr[2] * 0.09,                       # Active Bleeding (High Red)
            std_bgr[0] * 0.12,                        # Esophagitis
            15.0 - (std_bgr[0] + std_bgr[1] + std_bgr[2]) * 0.1  # Normal Mucosa
        ])

        # Apply Softmax formulation: p_k = exp(s_k) / sum(exp(s_j))
        probs = softmax(logits)

        # Map to class dictionary
        raw_softmax_scores = {
            self.classes[i]: round(float(probs[i]), 4) for i in range(len(self.classes))
        }

        top_idx = int(np.argmax(probs))
        top_class = self.classes[top_idx]
        top_prob = float(probs[top_idx])

        # Confidence Threshold Assessment
        if top_prob >= settings.CONFIDENCE_HIGH:
            conf_level = "HIGH"
            review_rec = False
        elif top_prob >= settings.CONFIDENCE_MEDIUM:
            conf_level = "MEDIUM"
            review_rec = True
        else:
            conf_level = "LOW"
            review_rec = True

        return {
            "predicted_class": top_class,
            "class_confidence": round(top_prob, 4),
            "confidence_level": conf_level,
            "raw_softmax_scores": raw_softmax_scores,
            "human_review_recommended": review_rec,
        }


class TorchClassifier(ClassifierBase):
    """
    PyTorch Neural Network Classifier.
    Falls back to DemoClassifier if weights file is absent.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.fallback = DemoClassifier()

        if model_path and os.path.exists(model_path):
            try:
                import torch
                self.model = torch.load(model_path, map_location="cpu")
                self.model.eval()
                print(f"Loaded PyTorch Classifier from {model_path}")
            except Exception as e:
                print(f"Failed loading PyTorch classifier from {model_path}: {e}. Using DemoClassifier.")
                self.model = None

    def classify(self, crop_bgr: np.ndarray) -> Dict[str, Any]:
        if self.model is None:
            return self.fallback.classify(crop_bgr)

        try:
            import torch
            import torchvision.transforms as T
            from PIL import Image

            crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(crop_rgb)

            transform = T.Compose([
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            input_tensor = transform(pil_img).unsqueeze(0)

            with torch.no_grad():
                logits = self.model(input_tensor).numpy()[0]

            probs = softmax(logits)
            classes = getattr(self.model, "classes", self.fallback.classes)

            raw_softmax_scores = {
                classes[i]: round(float(probs[i]), 4) for i in range(len(classes))
            }

            top_idx = int(np.argmax(probs))
            top_class = classes[top_idx]
            top_prob = float(probs[top_idx])

            if top_prob >= settings.CONFIDENCE_HIGH:
                conf_level = "HIGH"
                review_rec = False
            elif top_prob >= settings.CONFIDENCE_MEDIUM:
                conf_level = "MEDIUM"
                review_rec = True
            else:
                conf_level = "LOW"
                review_rec = True

            return {
                "predicted_class": top_class,
                "class_confidence": round(top_prob, 4),
                "confidence_level": conf_level,
                "raw_softmax_scores": raw_softmax_scores,
                "human_review_recommended": review_rec,
            }
        except Exception as e:
            print(f"PyTorch classifier inference error: {e}. Falling back to DemoClassifier.")
            return self.fallback.classify(crop_bgr)
