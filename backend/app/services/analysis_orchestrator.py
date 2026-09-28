import os
import uuid
import cv2
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.config import settings
from app.preprocessing.image_transforms import load_image_bytes, crop_roi
from app.quality.metrics import default_evaluator
from app.inference.yolo_detector import YOLODetector
from app.inference.torch_classifier import TorchClassifier
from app.explainability.gradcam_engine import default_gradcam
from app.models.db_models import (
    Examination,
    Frame,
    QualityResult,
    Detection,
    Prediction,
    Explanation,
    Review,
    ReviewStatusEnum,
)

class AnalysisOrchestrator:
    def __init__(self):
        self.detector = YOLODetector(settings.DETECTOR_MODEL_PATH)
        self.classifier = TorchClassifier(settings.CLASSIFIER_MODEL_PATH)

    def analyze_image_bytes(
        self,
        image_bytes: bytes,
        db: Session,
        examination_id: str = None,
        patient_anon_id: str = "ANON-PATIENT",
    ) -> Dict[str, Any]:
        # 1. Load Image
        image_bgr = load_image_bytes(image_bytes)
        if image_bgr is None:
            raise ValueError("Unable to decode uploaded image file.")

        # 2. Save original uploaded frame to storage
        frame_uuid = str(uuid.uuid4())
        frame_filename = f"frame_{frame_uuid[:8]}.png"
        frame_filepath = os.path.join(settings.UPLOADS_DIR, frame_filename)
        cv2.imwrite(frame_filepath, image_bgr)
        image_url = f"/storage/uploads/{frame_filename}"

        # 3. Create or retrieve Examination in DB
        if not examination_id:
            exam = Examination(
                patient_anon_id=patient_anon_id,
                input_type="IMAGE",
                status="COMPLETED"
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)
            examination_id = exam.id
        else:
            exam = db.query(Examination).filter(Examination.id == examination_id).first()

        # 4. Create Frame record in DB
        frame_record = Frame(
            id=frame_uuid,
            examination_id=examination_id,
            frame_index=1,
            timestamp_ms=0.0,
            image_path=image_url
        )
        db.add(frame_record)
        db.commit()

        # 5. Quality Check
        quality_res = default_evaluator.evaluate(image_bgr)
        db_quality = QualityResult(
            frame_id=frame_record.id,
            overall_quality=quality_res["overall_quality"],
            blur_score=quality_res["blur_score"],
            brightness_score=quality_res["brightness_score"],
            warnings=quality_res["warnings"]
        )
        db.add(db_quality)

        # 6. Abnormality Detection (YOLO)
        raw_detections = self.detector.detect(image_bgr, confidence_threshold=0.45)
        
        detections_output = []

        # 7. Multi-Region Processing Loop
        for det_data in raw_detections:
            bbox = det_data["bbox"]
            bbox_tuple = (bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"])

            # Crop Region ROI
            crop = crop_roi(image_bgr, bbox_tuple)

            # Classify Crop (Softmax)
            cls_res = self.classifier.classify(crop)

            # Grad-CAM Explainability
            cam_res = default_gradcam.generate_and_save(crop, region_id=det_data["region_id"])

            # Persist Detection to DB
            db_det = Detection(
                id=str(uuid.uuid4()),
                frame_id=frame_record.id,
                region_index=det_data["region_index"],
                bbox_x1=bbox["x1"],
                bbox_y1=bbox["y1"],
                bbox_x2=bbox["x2"],
                bbox_y2=bbox["y2"],
                detection_confidence=det_data["confidence"],
                detected_class=det_data["class_name"]
            )
            db.add(db_det)
            db.commit()

            # Persist Prediction to DB
            db_pred = Prediction(
                id=str(uuid.uuid4()),
                detection_id=db_det.id,
                predicted_class=cls_res["predicted_class"],
                class_confidence=cls_res["class_confidence"],
                confidence_level=cls_res["confidence_level"],
                raw_softmax_scores=cls_res["raw_softmax_scores"]
            )
            db.add(db_pred)
            db.commit()

            # Persist Explanation to DB
            db_exp = Explanation(
                id=str(uuid.uuid4()),
                prediction_id=db_pred.id,
                heatmap_path=cam_res["heatmap_url"],
                overlay_path=cam_res["overlay_url"],
                target_layer=cam_res["target_layer"]
            )
            db.add(db_exp)

            # Initial Pending Review record
            db_rev = Review(
                examination_id=examination_id,
                frame_id=frame_record.id,
                detection_id=db_det.id,
                review_status=ReviewStatusEnum.PENDING.value
            )
            db.add(db_rev)

            detections_output.append({
                "id": db_det.id,
                "region_id": det_data["region_id"],
                "region_index": det_data["region_index"],
                "class_name": det_data["class_name"],
                "confidence": det_data["confidence"],
                "bbox": bbox,
                "prediction": {
                    "id": db_pred.id,
                    "predicted_class": cls_res["predicted_class"],
                    "class_confidence": cls_res["class_confidence"],
                    "confidence_level": cls_res["confidence_level"],
                    "raw_softmax_scores": cls_res["raw_softmax_scores"],
                    "human_review_recommended": cls_res["human_review_recommended"]
                },
                "explanation": {
                    "id": db_exp.id,
                    "heatmap_url": cam_res["heatmap_url"],
                    "overlay_url": cam_res["overlay_url"],
                    "target_layer": cam_res["target_layer"]
                }
            })

        db.commit()

        return {
            "frame_id": frame_record.id,
            "examination_id": examination_id,
            "frame_index": 1,
            "timestamp_ms": 0.0,
            "image_url": image_url,
            "quality": quality_res,
            "detections": detections_output,
            "review_status": "PENDING",
            "created_at": datetime.now(timezone.utc)
        }

    def analyze_video_bytes(
        self,
        video_bytes: bytes,
        filename: str,
        db: Session,
        patient_anon_id: str = "ANON-PATIENT",
    ) -> Dict[str, Any]:
        video_uuid = str(uuid.uuid4())
        safe_ext = os.path.splitext(filename)[1] or ".mp4"
        temp_filename = f"vid_{video_uuid[:8]}{safe_ext}"
        temp_filepath = os.path.join(settings.UPLOADS_DIR, temp_filename)

        with open(temp_filepath, "wb") as f:
            f.write(video_bytes)

        cap = cv2.VideoCapture(temp_filepath)
        if not cap.isOpened():
            raise ValueError("Unable to open or parse uploaded video file.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 25.0

        # Sample 1 frame per second, capped between 5 and 30 frames
        sample_step = max(1, int(fps))
        if total_frames > 0 and (total_frames // sample_step) > 30:
            sample_step = total_frames // 30

        # 1. Create Examination record in DB
        exam = Examination(
            patient_anon_id=patient_anon_id,
            input_type="VIDEO",
            status="COMPLETED"
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)

        frames_output = []
        all_detections = []

        curr_frame_idx = 0
        saved_frame_count = 0

        while cap.isOpened():
            ret, frame_bgr = cap.read()
            if not ret:
                break

            curr_frame_idx += 1
            if (curr_frame_idx - 1) % sample_step != 0:
                continue

            saved_frame_count += 1
            timestamp_ms = round((curr_frame_idx / fps) * 1000.0, 1)

            # Save frame PNG
            frame_uuid = str(uuid.uuid4())
            frame_file = f"frame_v_{frame_uuid[:8]}.png"
            frame_path = os.path.join(settings.UPLOADS_DIR, frame_file)
            cv2.imwrite(frame_path, frame_bgr)
            image_url = f"/storage/uploads/{frame_file}"

            # Create Frame in DB
            frame_record = Frame(
                id=frame_uuid,
                examination_id=exam.id,
                frame_index=saved_frame_count,
                timestamp_ms=timestamp_ms,
                image_path=image_url
            )
            db.add(frame_record)
            db.commit()

            # Quality Check
            quality_res = default_evaluator.evaluate(frame_bgr)
            db_quality = QualityResult(
                frame_id=frame_record.id,
                overall_quality=quality_res["overall_quality"],
                blur_score=quality_res["blur_score"],
                brightness_score=quality_res["brightness_score"],
                warnings=quality_res["warnings"]
            )
            db.add(db_quality)

            # Detections (YOLO)
            raw_detections = self.detector.detect(frame_bgr, confidence_threshold=0.40)
            frame_dets = []

            for det_data in raw_detections:
                bbox = det_data["bbox"]
                crop = crop_roi(frame_bgr, (bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]))
                cls_res = self.classifier.classify(crop)
                cam_res = default_gradcam.generate_and_save(crop, region_id=det_data["region_id"])

                db_det = Detection(
                    id=str(uuid.uuid4()),
                    frame_id=frame_record.id,
                    region_index=det_data["region_index"],
                    bbox_x1=bbox["x1"],
                    bbox_y1=bbox["y1"],
                    bbox_x2=bbox["x2"],
                    bbox_y2=bbox["y2"],
                    detection_confidence=det_data["confidence"],
                    detected_class=det_data["class_name"]
                )
                db.add(db_det)
                db.commit()

                db_pred = Prediction(
                    id=str(uuid.uuid4()),
                    detection_id=db_det.id,
                    predicted_class=cls_res["predicted_class"],
                    class_confidence=cls_res["class_confidence"],
                    confidence_level=cls_res["confidence_level"],
                    raw_softmax_scores=cls_res["raw_softmax_scores"]
                )
                db.add(db_pred)
                db.commit()

                db_exp = Explanation(
                    id=str(uuid.uuid4()),
                    prediction_id=db_pred.id,
                    heatmap_path=cam_res["heatmap_url"],
                    overlay_path=cam_res["overlay_url"],
                    target_layer=cam_res["target_layer"]
                )
                db.add(db_exp)

                db_rev = Review(
                    examination_id=exam.id,
                    frame_id=frame_record.id,
                    detection_id=db_det.id,
                    review_status=ReviewStatusEnum.PENDING.value
                )
                db.add(db_rev)

                det_obj = {
                    "id": db_det.id,
                    "region_id": det_data["region_id"],
                    "region_index": det_data["region_index"],
                    "frame_index": saved_frame_count,
                    "class_name": det_data["class_name"],
                    "confidence": det_data["confidence"],
                    "bbox": bbox,
                    "prediction": {
                        "id": db_pred.id,
                        "predicted_class": cls_res["predicted_class"],
                        "class_confidence": cls_res["class_confidence"],
                        "confidence_level": cls_res["confidence_level"],
                        "raw_softmax_scores": cls_res["raw_softmax_scores"],
                        "human_review_recommended": cls_res["human_review_recommended"]
                    },
                    "explanation": {
                        "id": db_exp.id,
                        "heatmap_url": cam_res["heatmap_url"],
                        "overlay_url": cam_res["overlay_url"],
                        "target_layer": cam_res["target_layer"]
                    }
                }
                frame_dets.append(det_obj)
                all_detections.append(det_obj)

            db.commit()

            frames_output.append({
                "frame_id": frame_record.id,
                "frame_index": saved_frame_count,
                "timestamp_ms": timestamp_ms,
                "image_url": image_url,
                "quality": quality_res,
                "detections": frame_dets
            })

        cap.release()

        return {
            "examination_id": exam.id,
            "patient_anon_id": patient_anon_id,
            "input_type": "VIDEO",
            "status": "COMPLETED",
            "frame_count": len(frames_output),
            "total_detections": len(all_detections),
            "frames": frames_output,
            "detections": all_detections,
            "created_at": datetime.now(timezone.utc)
        }

analysis_orchestrator = AnalysisOrchestrator()
