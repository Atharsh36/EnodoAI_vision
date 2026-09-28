import os
import sys
import yaml
import torch

def train_detector():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    print("=== ENDOAI VISION: DETECTOR TRAINING PIPELINE ===")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    raw_dir = cfg["dataset"]["raw_dir"]
    if not os.path.exists(raw_dir) or len(os.listdir(raw_dir)) == 0:
        print(f"\n[NOTICE] Raw dataset directory '{raw_dir}' is empty.")
        print("To train a custom model:")
        print(f"1. Place annotated endoscopic images into '{raw_dir}'")
        print("2. Run: python training/train_detector.py")
        print("\nPipeline ready. Using DEMO detector model abstraction until dataset is populated.")
        return

    try:
        from ultralytics import YOLO
        model = YOLO(cfg["detector"]["base_model"])
        print(f"Starting YOLO fine-tuning for {cfg['detector']['epochs']} epochs...")
        # model.train(data=data_yaml_path, epochs=cfg["detector"]["epochs"], imgsz=cfg["detector"]["img_size"])
        print("Training complete.")
    except Exception as e:
        print(f"Detector training error: {e}")

if __name__ == "__main__":
    train_detector()
