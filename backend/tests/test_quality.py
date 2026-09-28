import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.quality.metrics import default_evaluator

def test_sharp_image_evaluation():
    # Create sharp synthetic image (high gradient checkerboard)
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[::20, :] = 255
    img[:, ::20] = 255

    res = default_evaluator.evaluate(img)
    assert res["blur_score"] > 100.0, f"Expected sharp blur score > 100, got {res['blur_score']}"
    assert res["overall_quality"] in ["GOOD", "WARNING"]
    print(f"[OK] Sharp image test passed. Blur score: {res['blur_score']:.1f}")

def test_blurred_image_evaluation():
    # Create sharp image then apply heavy Gaussian blur
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[::20, :] = 255
    blurred = cv2.GaussianBlur(img, (51, 51), 0)

    res = default_evaluator.evaluate(blurred)
    assert res["blur_score"] < 50.0, f"Expected blurry score < 50, got {res['blur_score']}"
    assert any("blur" in w.lower() for w in res["warnings"])
    print(f"[OK] Blurred image test passed. Blur score: {res['blur_score']:.1f} | Warnings: {res['warnings']}")

def test_dark_underexposed_image():
    # Create dark image (low mean intensity)
    dark_img = np.full((300, 300, 3), 10, dtype=np.uint8)

    res = default_evaluator.evaluate(dark_img)
    assert res["brightness_score"] < 20.0
    assert any("low illumination" in w.lower() for w in res["warnings"])
    print(f"[OK] Dark image test passed. Brightness: {res['brightness_score']:.1f}")

if __name__ == "__main__":
    test_sharp_image_evaluation()
    test_blurred_image_evaluation()
    test_dark_underexposed_image()
    print("=== ALL QUALITY ENGINE TESTS PASSED ===")
