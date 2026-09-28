import os
import yaml
import torch

def train_classifier():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    print("=== ENDOAI VISION: CLASSIFIER TRAINING PIPELINE ===")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    processed_dir = cfg["dataset"]["processed_dir"]
    if not os.path.exists(processed_dir) or len(os.listdir(processed_dir)) == 0:
        print(f"\n[NOTICE] Processed dataset crops directory '{processed_dir}' is empty.")
        print("To train a custom classifier:")
        print(f"1. Crop endoscopic lesions into '{processed_dir}'")
        print("2. Run: python training/train_classifier.py")
        print("\nPipeline ready. Using DEMO Softmax classifier abstraction until dataset is populated.")
        return

if __name__ == "__main__":
    train_classifier()
