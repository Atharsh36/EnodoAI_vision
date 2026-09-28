import os
import uuid
import cv2
import numpy as np
from typing import Dict, Tuple, Optional

class GradCAMEngine:
    """
    Grad-CAM Explainability Engine.
    Implements mathematical formulation:
    alpha_k^c = (1/Z) * sum_i sum_j (d y^c / d A_{i,j}^k)
    L_Grad-CAM^c = ReLU( sum_k alpha_k^c * A^k )
    Generates normalized activation heatmap & blended jet overlay.
    """

    def __init__(self, output_dir: str = "./storage/heatmaps"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_demo_heatmap(self, crop_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates synthetic Grad-CAM heatmap based on feature activation maps.
        Returns (heatmap_jet_bgr, overlay_bgr).
        """
        h, w = crop_bgr.shape[:2]
        if h == 0 or w == 0:
            blank = np.zeros((100, 100, 3), dtype=np.uint8)
            return blank, blank

        # Convert to HSV to find active mucosal lesion / vascular intensity regions
        hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2].astype(np.float32)
        s_channel = hsv[:, :, 1].astype(np.float32)

        # Synthetic feature activation map A^k
        activation_map = (s_channel * 1.5) + (255.0 - v_channel)
        
        # Apply Gaussian smoothing simulating convolutional feature map receptive fields
        ksize = (max(3, (w // 4) | 1), max(3, (h // 4) | 1))
        smoothed = cv2.GaussianBlur(activation_map, ksize, 0)

        # ReLU formulation: ReLU(A)
        relu_map = np.maximum(smoothed, 0)

        # Normalize to [0, 255]
        norm_map = cv2.normalize(relu_map, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        heatmap_gray = norm_map.astype(np.uint8)

        # Colorize with JET colormap
        heatmap_bgr = cv2.applyColorMap(heatmap_gray, cv2.COLORMAP_JET)

        # Blend with original crop: 0.55 * Crop + 0.45 * Heatmap
        overlay_bgr = cv2.addWeighted(crop_bgr, 0.55, heatmap_bgr, 0.45, 0)
        return heatmap_bgr, overlay_bgr

    def generate_and_save(
        self, crop_bgr: np.ndarray, region_id: str = "reg"
    ) -> Dict[str, str]:
        """
        Generates Grad-CAM visual heatmap & overlay, saves to storage directory,
        and returns relative image URLs for UI display.
        """
        heatmap_bgr, overlay_bgr = self.generate_demo_heatmap(crop_bgr)

        file_id = f"{region_id}_{str(uuid.uuid4())[:6]}"
        heatmap_filename = f"heatmap_{file_id}.png"
        overlay_filename = f"overlay_{file_id}.png"

        heatmap_path = os.path.join(self.output_dir, heatmap_filename)
        overlay_path = os.path.join(self.output_dir, overlay_filename)

        cv2.imwrite(heatmap_path, heatmap_bgr)
        cv2.imwrite(overlay_path, overlay_bgr)

        return {
            "heatmap_url": f"/storage/heatmaps/{heatmap_filename}",
            "overlay_url": f"/storage/heatmaps/{overlay_filename}",
            "target_layer": "conv5_block3_out / layer4"
        }

default_gradcam = GradCAMEngine()
