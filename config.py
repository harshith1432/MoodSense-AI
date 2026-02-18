"""
MoodSense AI Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Application
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Model Settings
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./model_cache")
    
    # HuggingFace Models
    EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"  # 7 emotions
    SARCASM_MODEL = "helinivan/english-sarcasm-detector"
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Privacy & Security
    ALLOW_IMAGE_STORAGE = os.getenv("ALLOW_IMAGE_STORAGE", "False").lower() == "true"
    REQUIRE_CONSENT = os.getenv("REQUIRE_CONSENT", "True").lower() == "true"
    
    # File Upload Settings
    MAX_AUDIO_SIZE_MB = 10
    MAX_IMAGE_SIZE_MB = 5
    UPLOAD_FOLDER = "./static/uploads"
    ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg"}
    
    # Risk Level Thresholds
    RISK_THRESHOLDS = {
        "LOW": 0.3,
        "MEDIUM": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.85
    }

settings = Settings()
