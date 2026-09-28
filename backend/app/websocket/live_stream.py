import time
import json
import base64
import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.preprocessing.image_transforms import load_image_bytes, crop_roi
from app.quality.metrics import default_evaluator
from app.inference.yolo_detector import YOLODetector
from app.inference.torch_classifier import TorchClassifier
from app.explainability.gradcam_engine import default_gradcam
from app.config import settings

router = APIRouter(tags=["WebSocket Live Stream"])

detector = YOLODetector(settings.DETECTOR_MODEL_PATH)
classifier = TorchClassifier(settings.CLASSIFIER_MODEL_PATH)

@router.websocket("/ws/live-analysis")
async def websocket_live_analysis(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected to /ws/live-analysis")

    frame_counter = 0
    frame_skip = 1  # Process every frame by default
    mode = "FAST"   # "FAST" or "EXPLAINABLE"

    try:
        while True:
            # Receive text payload (JSON config or base64 frame)
            data = await websocket.receive_text()
            start_time = time.time()

            try:
                payload = json.loads(data)
                
                # Check mode / config update payload
                if "mode" in payload:
                    mode = payload.get("mode", "FAST")
                if "frame_skip" in payload:
                    frame_skip = max(1, int(payload.get("frame_skip", 1)))

                frame_base64 = payload.get("frame", None)
                if not frame_base64:
                    await websocket.send_json({"status": "ready", "mode": mode, "frame_skip": frame_skip})
                    continue

                frame_counter += 1

                # Frame skipping logic
                if (frame_counter % frame_skip) != 0:
                    await websocket.send_json({
                        "frame_number": frame_counter,
                        "skipped": True,
                        "status": "skipped"
                    })
                    continue

                # Strip base64 prefix if present
                if "," in frame_base64:
                    frame_base64 = frame_base64.split(",")[1]

                img_bytes = base64.b64decode(frame_base64)
                img_bgr = load_image_bytes(img_bytes)

                if img_bgr is None:
                    await websocket.send_json({"error": "Failed to decode frame image."})
                    continue

                # Preprocessing & Quality Check
                quality_res = default_evaluator.evaluate(img_bgr)

                # Detection
                det_start = time.time()
                detections = detector.detect(img_bgr, confidence_threshold=0.45)
                det_latency = (time.time() - det_start) * 1000.0

                # Multi-Region Classification & Optional Grad-CAM
                detections_output = []
                for det in detections:
                    bbox = det["bbox"]
                    crop = crop_roi(img_bgr, (bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]))

                    cls_res = classifier.classify(crop)

                    explanation = None
                    if mode == "EXPLAINABLE":
                        cam_res = default_gradcam.generate_and_save(crop, region_id=det["region_id"])
                        explanation = cam_res

                    detections_output.append({
                        "region_id": det["region_id"],
                        "region_index": det["region_index"],
                        "class_name": det["class_name"],
                        "confidence": det["confidence"],
                        "bbox": bbox,
                        "prediction": cls_res,
                        "explanation": explanation
                    })

                total_latency_ms = (time.time() - start_time) * 1000.0
                fps = round(1000.0 / total_latency_ms, 1) if total_latency_ms > 0 else 30.0

                response_data = {
                    "frame_number": frame_counter,
                    "mode": mode,
                    "fps": fps,
                    "latency_ms": round(total_latency_ms, 1),
                    "detection_latency_ms": round(det_latency, 1),
                    "quality": quality_res,
                    "detections": detections_output,
                    "timestamp": time.time()
                }

                await websocket.send_json(response_data)

            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON text message."})
            except Exception as e:
                await websocket.send_json({"error": f"Frame processing error: {str(e)}"})

    except WebSocketDisconnect:
        print("WebSocket client disconnected from /ws/live-analysis")
