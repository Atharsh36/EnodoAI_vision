import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "EndoAI Vision"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./endoai_vision.db"
    
    # Storage
    STORAGE_DIR: str = os.path.abspath("./storage")
    UPLOADS_DIR: str = os.path.abspath("./storage/uploads")
    HEATMAPS_DIR: str = os.path.abspath("./storage/heatmaps")
    REPORTS_DIR: str = os.path.abspath("./storage/reports")
    
    # Model config
    DETECTOR_MODEL_PATH: str = os.path.abspath("./models/detector/yolov8_endo.pt")
    CLASSIFIER_MODEL_PATH: str = os.path.abspath("./models/classifier/resnet50_endo.pt")
    DETECTOR_REGISTRY_PATH: str = os.path.abspath("./models/detector/registry.json")
    CLASSIFIER_REGISTRY_PATH: str = os.path.abspath("./models/classifier/registry.json")
    USE_DEMO_FALLBACK: bool = True
    
    # Thresholds
    CONFIDENCE_HIGH: float = 0.80
    CONFIDENCE_MEDIUM: float = 0.50
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
for directory in [settings.STORAGE_DIR, settings.UPLOADS_DIR, settings.HEATMAPS_DIR, settings.REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)
