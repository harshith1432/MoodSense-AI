"""
Custom Face Analyzer - Uses custom-trained model
Alternative to face_analyzer.py that uses your custom-trained model
"""
import cv2
import numpy as np
import logging
from pathlib import Path
import tensorflow as tf

logger = logging.getLogger(__name__)

EMOTION_LABELS = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
IMG_SIZE = 48
MODEL_PATH = "model_cache/custom_face_model.h5"


class CustomFaceAnalyzer:
    def __init__(self):
        """Initialize custom face analyzer"""
        logger.info("Custom Face Analyzer initializing...")
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load custom model if available
        if Path(MODEL_PATH).exists():
            self.model = tf.keras.models.load_model(MODEL_PATH)
            logger.info(f"✓ Custom model loaded from {MODEL_PATH}")
        else:
            logger.warning(f"⚠️  Custom model not found at {MODEL_PATH}")
            logger.warning("Please train the model first using: python train_custom_face_model.py")
            self.model = None
    
    def analyze_face(self, frame: np.ndarray) -> dict:
        """
        Analyze facial expression using custom-trained model
        
        Args:
            frame: Image frame (numpy array from cv2)
            
        Returns:
            dict with emotion, confidence, face_detected status
        """
        if self.model is None:
            return {
                "face_detected": False,
                "emotion": "neutral",
                "confidence": 0.0,
                "error": "Custom model not loaded. Train it first with train_custom_face_model.py"
            }
        
        try:
            # Detect faces
            faces = self.detect_faces(frame)
            
            if len(faces) == 0:
                return {
                    "face_detected": False,
                    "emotion": "neutral",
                    "confidence": 0.0,
                    "message": "No face detected"
                }
            
            # Get the first face
            x, y, w, h = faces[0]
            
            # Extract face ROI
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_roi = gray[y:y+h, x:x+w]
            
            # Preprocess for model
            face_resized = cv2.resize(face_roi, (IMG_SIZE, IMG_SIZE))
            face_normalized = face_resized.astype('float32') / 255.0
            face_input = np.expand_dims(face_normalized, axis=0)
            face_input = np.expand_dims(face_input, axis=-1)
            
            # Predict
            predictions = self.model.predict(face_input, verbose=0)[0]
            
            # Get dominant emotion
            emotion_idx = np.argmax(predictions)
            dominant_emotion = EMOTION_LABELS[emotion_idx]
            confidence = float(predictions[emotion_idx])
            
            # Map to our categories
            mapped_emotion = self._map_emotion(dominant_emotion)
            
            # Calculate risk
            risk_level = self._calculate_risk(mapped_emotion, confidence)
            
            # Create emotion scores dictionary
            emotion_scores = {
                EMOTION_LABELS[i]: float(predictions[i]) 
                for i in range(len(EMOTION_LABELS))
            }
            
            return {
                "face_detected": True,
                "emotion": mapped_emotion,
                "confidence": round(confidence, 3),
                "risk_level": risk_level,
                "detailed_emotions": emotion_scores,
                "faces_count": len(faces),
                "model_type": "custom_trained"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face: {e}")
            return {
                "face_detected": False,
                "emotion": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def _map_emotion(self, emotion: str) -> str:
        """Map custom model emotions to our categories"""
        # Already using our categories
        return emotion
    
    def _calculate_risk(self, emotion: str, confidence: float) -> str:
        """Calculate risk based on facial emotion"""
        risk_score = 0.0
        
        # Emotion-based risk
        high_risk_emotions = ["anger", "fear", "disgust"]
        medium_risk_emotions = ["sadness"]
        
        if emotion in high_risk_emotions:
            risk_score += 0.6 * confidence
        elif emotion in medium_risk_emotions:
            risk_score += 0.4 * confidence
        else:
            risk_score += 0.1 * confidence
        
        # Determine level
        if risk_score >= 0.85:
            return "CRITICAL"
        elif risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"


# Singleton instance
_custom_face_analyzer_instance = None

def get_custom_face_analyzer():
    """Get or create custom face analyzer singleton"""
    global _custom_face_analyzer_instance
    if _custom_face_analyzer_instance is None:
        _custom_face_analyzer_instance = CustomFaceAnalyzer()
    return _custom_face_analyzer_instance
