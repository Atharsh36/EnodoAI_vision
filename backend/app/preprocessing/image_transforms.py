import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional

def load_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decodes raw image bytes into an OpenCV BGR numpy array.
    Supports JPG, PNG, WEBP, BMP.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image bytes: {e}")
        return None

def resize_maintain_aspect_ratio(
    image: np.ndarray, target_size: Tuple[int, int] = (640, 640)
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Resizes image maintaining aspect ratio with padding.
    Returns (padded_img, scale_factor, (pad_w, pad_h)).
    """
    h, w = image.shape[:2]
    target_w, target_h = target_size

    scale = min(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Padding
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    pad_w = (target_w - new_w) // 2
    pad_h = (target_h - new_h) // 2

    canvas[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
    return canvas, scale, (pad_w, pad_h)

def crop_roi(image: np.ndarray, bbox: Tuple[float, float, float, float]) -> np.ndarray:
    """
    Crops region of interest from image.
    bbox format: (x1, y1, x2, y2)
    """
    h, w = image.shape[:2]
    x1 = max(0, int(bbox[0]))
    y1 = max(0, int(bbox[1]))
    x2 = min(w, int(bbox[2]))
    y2 = min(h, int(bbox[3]))

    if x2 <= x1 or y2 <= y1:
        return image.copy()

    return image[y1:y2, x1:x2].copy()
