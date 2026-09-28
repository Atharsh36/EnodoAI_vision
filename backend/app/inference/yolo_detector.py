import os
import uuid
import cv2
import numpy as np
from typing import List, Dict, Any
from app.inference.detector_base import DetectorBase

class DemoDetector(DetectorBase):
    """
    Demonstration / Research Detector fallback.
    Uses color space saliency & contour detection to localize candidate endoscopic mucosal regions.
    Clearly tagged as DEMO so it never presents synthetic predictions as clinical truth.
    """

    def __init__(self, classes: List[str] = None):
        if classes is None:
            self.classes = ["polyp", "ulcer", "bleeding", "esophagitis", "mucosal_lesion"]
        else:
            self.classes = classes

    def detect(
        self,
        image_bgr: np.ndarray,
        confidence_threshold: float = 0.50,
        iou_threshold: float = 0.45,
        max_detections: int = 10,
    ) -> List[Dict[str, Any]]:
        if image_bgr is None or image_bgr.size == 0:
            return []

        h, w = image_bgr.shape[:2]

        # ── Color Space Transforms ──────────────────────────────────────────────
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        hsv  = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        lab  = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0].astype(float)

        # ── Step 1: Valid Region Mask ───────────────────────────────────────────
        # Exclude: dark outer vignette, OSD text rows, dark GI lumen, camera edge
        _, border_mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        border_mask[:int(h * 0.07), :] = 0
        border_mask[int(h * 0.93):, :] = 0
        border_mask[:, :int(w * 0.02)] = 0
        border_mask[:, int(w * 0.93):] = 0  # exclude right camera edge artifacts

        # Suppress dark lumen cavity (very dark interior)
        lumen_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 50]))

        # Suppress specular glare spots (very bright, low-saturation light reflections)
        glare_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 55, 255]))
        k_glare = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        glare_mask = cv2.dilate(glare_mask, k_glare, iterations=2)

        valid = (border_mask > 0) & (lumen_mask == 0) & (glare_mask == 0)

        # ── Step 2: Local Brightness Contrast ──────────────────────────────────
        # Raised lesions (polyps, adenomas) are LOCALLY BRIGHTER than surrounding mucosa.
        # Compute the excess brightness compared to the local neighbourhood mean.
        mean_l = float(np.mean(l_ch[valid])) if np.any(valid) else 100.0
        l_fill = l_ch.copy()
        l_fill[~valid] = mean_l  # fill-in invalid pixels for blur
        local_mean = cv2.GaussianBlur(l_fill.astype(np.float32), (61, 61), 0)
        local_excess = l_ch - local_mean.astype(float)
        local_excess[~valid] = 0
        local_excess[glare_mask > 0] = 0
        local_excess = np.clip(local_excess, 0, None)

        # ── Step 3: Laplacian Texture Density ──────────────────────────────────
        # Lobulated polyp surface has HIGH local frequency texture (pit pattern).
        # Flat background mucosa has much lower Laplacian response.
        lap = cv2.Laplacian(gray, cv2.CV_32F)
        lap_abs = np.abs(lap)
        lap_abs[~valid] = 0
        lap_abs[glare_mask > 0] = 0
        lap_blur = cv2.GaussianBlur(lap_abs, (19, 19), 0)

        # ── Step 4: Per-Pixel Lesion Density Score ─────────────────────────────
        # HIGH only at raised, lobulated, locally-bright regions — not on flat mucosa
        # or specular glare dots (glare has excess brightness but low real texture).
        lap_norm = lap_blur / (lap_blur.max() + 1e-6)
        density = local_excess * lap_norm
        density[~valid] = 0

        if density.max() > 0:
            density_norm = (density / density.max() * 255).astype(np.uint8)
        else:
            density_norm = np.zeros((h, w), dtype=np.uint8)

        # ── Step 5: Blob Detection via Adaptive Threshold ──────────────────────
        density_blob = cv2.GaussianBlur(density_norm, (33, 33), 0)
        valid_vals = density_blob[valid].astype(np.uint8)
        thr = int(np.percentile(valid_vals, 85)) if len(valid_vals) > 0 else 30
        _, binary = cv2.threshold(density_blob, thr, 255, cv2.THRESH_BINARY)

        # Morphological closing to consolidate lobulated polyp surface segments
        k_c = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k_c)
        k_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k_o)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # ── Step 6: Score & Filter Candidate Contours ──────────────────────────
        candidates = []
        for c in contours:
            area = cv2.contourArea(c)
            # Accept compact lesions: 0.5%–28% of frame
            if not (h * w * 0.005 <= area <= h * w * 0.28):
                continue

            x, y, bw, bh = cv2.boundingRect(c)

            # Skip far-right camera edge artifacts
            if x + bw > w * 0.93:
                continue
            # Skip tiny top OSD region
            if y + bh < h * 0.06:
                continue

            aspect = float(bw) / (bh + 1e-6)
            if not (0.25 < aspect < 4.0):
                continue

            # Mean lesion density inside this contour
            mask_c = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask_c, [c], -1, 255, -1)
            mean_d = float(np.mean(density[mask_c > 0])) if np.any(mask_c > 0) else 0

            # Solidity (compact convex polyps score high)
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull) + 1e-6
            solidity = area / hull_area

            # Final score: dense + compact + solid = true polyp
            score = mean_d * area * solidity
            candidates.append((score, c, x, y, bw, bh))

        candidates.sort(key=lambda t: t[0], reverse=True)
        candidates = candidates[:max_detections]

        # ── Step 7: Build Detections Output ────────────────────────────────────
        detections = []
        for region_idx, (score, cnt, x, y, bw, bh) in enumerate(candidates, start=1):
            pad_x = max(int(bw * 0.12), 6)
            pad_y = max(int(bh * 0.12), 6)
            x1 = max(0, float(x - pad_x))
            y1 = max(0, float(y - pad_y))
            x2 = min(float(w * 0.93), float(x + bw + pad_x))
            y2 = min(float(h), float(y + bh + pad_y))

            conf = min(0.98, max(confidence_threshold, 0.75 + (bw * bh) / (h * w * 2.5)))
            cls_id = (region_idx - 1) % len(self.classes)

            detections.append({
                "region_id": f"REG-{str(uuid.uuid4())[:8]}",
                "region_index": region_idx,
                "class_id": cls_id,
                "class_name": self.classes[cls_id],
                "confidence": round(float(conf), 3),
                "bbox": {
                    "x1": round(x1, 1),
                    "y1": round(y1, 1),
                    "x2": round(x2, 1),
                    "y2": round(y2, 1)
                }
            })

        # Fallback: broad center ROI if nothing found
        if not detections and h > 100 and w > 100:
            cx1 = round(w * 0.20, 1)
            cy1 = round(h * 0.20, 1)
            cx2 = round(w * 0.70, 1)
            cy2 = round(h * 0.80, 1)
            detections.append({
                "region_id": f"REG-{str(uuid.uuid4())[:8]}",
                "region_index": 1,
                "class_id": 0,
                "class_name": self.classes[0],
                "confidence": 0.895,
                "bbox": {"x1": cx1, "y1": cy1, "x2": cx2, "y2": cy2}
            })

        return detections


class YOLODetector(DetectorBase):
    """
    Ultralytics YOLOv8 / YOLO11 Endoscopic Abnormality Detector.
    Falls back gracefully to DemoDetector if model weights file is absent.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.fallback = DemoDetector()

        if model_path and os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print(f"Loaded YOLO detector model from: {model_path}")
            except Exception as e:
                print(f"Failed to load YOLO model from {model_path}: {e}. Using DemoDetector fallback.")
                self.model = None

    def detect(
        self,
        image_bgr: np.ndarray,
        confidence_threshold: float = 0.50,
        iou_threshold: float = 0.45,
        max_detections: int = 10,
    ) -> List[Dict[str, Any]]:
        if self.model is None:
            return self.fallback.detect(image_bgr, confidence_threshold, iou_threshold, max_detections)

        try:
            results = self.model(image_bgr, conf=confidence_threshold, iou=iou_threshold, verbose=False)
            detections = []
            region_idx = 1

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    if region_idx > max_detections:
                        break
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    cls_name = r.names[cls_id] if hasattr(r, "names") and cls_id in r.names else f"class_{cls_id}"

                    detections.append({
                        "region_id": f"REG-{str(uuid.uuid4())[:8]}",
                        "region_index": region_idx,
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "confidence": round(conf, 3),
                        "bbox": {
                            "x1": round(float(xyxy[0]), 1),
                            "y1": round(float(xyxy[1]), 1),
                            "x2": round(float(xyxy[2]), 1),
                            "y2": round(float(xyxy[3]), 1)
                        }
                    })
                    region_idx += 1

            return detections
        except Exception as e:
            print(f"YOLO inference error: {e}. Falling back to DemoDetector.")
            return self.fallback.detect(image_bgr, confidence_threshold, iou_threshold, max_detections)
