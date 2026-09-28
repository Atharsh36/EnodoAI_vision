import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class QualityEvaluator:
    """
    Measurable endoscopic image quality evaluation.
    Evaluates:
    - Blur via Variance of Laplacian: Var(Laplacian(Gray))
    - Brightness via Mean Grayscale Intensity (0 - 255)
    - Overexposure percentage (pixels > 240)
    - Underexposure percentage (pixels < 15)
    """

    def __init__(
        self,
        blur_warning_threshold: float = 100.0,
        blur_poor_threshold: float = 40.0,
        brightness_low_threshold: float = 40.0,
        brightness_high_threshold: float = 215.0,
        overexposure_threshold_pct: float = 15.0,
        underexposure_threshold_pct: float = 25.0,
    ):
        self.blur_warning_threshold = blur_warning_threshold
        self.blur_poor_threshold = blur_poor_threshold
        self.brightness_low_threshold = brightness_low_threshold
        self.brightness_high_threshold = brightness_high_threshold
        self.overexposure_threshold_pct = overexposure_threshold_pct
        self.underexposure_threshold_pct = underexposure_threshold_pct

    def compute_blur_score(self, gray_img: np.ndarray) -> float:
        """Variance of Laplacian calculation."""
        laplacian_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
        return float(laplacian_var)

    def compute_brightness_score(self, gray_img: np.ndarray) -> float:
        """Mean intensity score (0.0 to 255.0)."""
        return float(np.mean(gray_img))

    def compute_exposure_percentages(self, gray_img: np.ndarray) -> Tuple[float, float]:
        """Returns (overexposed_pct, underexposed_pct)."""
        total_pixels = gray_img.size
        if total_pixels == 0:
            return 0.0, 0.0

        overexposed_count = np.sum(gray_img > 240)
        underexposed_count = np.sum(gray_img < 15)

        over_pct = float((overexposed_count / total_pixels) * 100.0)
        under_pct = float((underexposed_count / total_pixels) * 100.0)
        return over_pct, under_pct

    def evaluate(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Evaluates BGR image array and returns comprehensive quality metrics dictionary.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {
                "overall_quality": "POOR",
                "quality_score": 0.0,
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "overexposed_pct": 0.0,
                "underexposed_pct": 0.0,
                "warnings": ["Invalid or corrupted image payload."]
            }

        # Convert to grayscale
        if len(image_bgr.shape) == 3:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_bgr.copy()

        blur_score = self.compute_blur_score(gray)
        brightness_score = self.compute_brightness_score(gray)
        over_pct, under_pct = self.compute_exposure_percentages(gray)

        warnings: List[str] = []

        # Check blur
        if blur_score < self.blur_poor_threshold:
            warnings.append(f"Severe image blur detected (Blur score: {blur_score:.1f} < {self.blur_poor_threshold}).")
        elif blur_score < self.blur_warning_threshold:
            warnings.append(f"Moderate image blur detected (Blur score: {blur_score:.1f}).")

        # Check brightness
        if brightness_score < self.brightness_low_threshold:
            warnings.append(f"Low illumination / underexposure (Brightness: {brightness_score:.1f}).")
        elif brightness_score > self.brightness_high_threshold:
            warnings.append(f"High illumination / glare (Brightness: {brightness_score:.1f}).")

        # Check exposure percentages
        if over_pct > self.overexposure_threshold_pct:
            warnings.append(f"Excessive specular glare / overexposure ({over_pct:.1f}% pixels).")
        if under_pct > self.underexposure_threshold_pct:
            warnings.append(f"Dark shadow regions ({under_pct:.1f}% pixels).")

        # Overall quality determination
        if blur_score < self.blur_poor_threshold or (brightness_score < 20.0 and under_pct > 50.0):
            overall_quality = "POOR"
        elif len(warnings) > 0:
            overall_quality = "WARNING"
        else:
            overall_quality = "GOOD"

        # Normalized quality score (0 - 100)
        norm_blur = min(100.0, (blur_score / 150.0) * 100.0)
        norm_bright = 100.0 - abs(brightness_score - 128.0) * (100.0 / 128.0)
        quality_score = max(0.0, min(100.0, (norm_blur * 0.6) + (norm_bright * 0.4)))

        return {
            "overall_quality": overall_quality,
            "quality_score": round(quality_score, 1),
            "blur_score": round(blur_score, 2),
            "brightness_score": round(brightness_score, 2),
            "overexposed_pct": round(over_pct, 2),
            "underexposed_pct": round(under_pct, 2),
            "warnings": warnings,
        }

default_evaluator = QualityEvaluator()
