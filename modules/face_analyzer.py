import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception as e:
    DEEPFACE_AVAILABLE = False
    logger.warning(f"DeepFace not available: {e}. Face analysis will be limited.")

from modules.advice_engine import get_advice_engine
from modules.reply_generator import get_reply_generator


class FaceAnalyzer:
    def __init__(self):
        """Initialize face analyzer"""
        logger.info("Face Analyzer initialized")
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def analyze_face(self, frame: np.ndarray) -> dict:
        """
        Analyze facial expression in a single frame
        """
        try:
            # Detect faces using OpenCV (works without DeepFace)
            faces = self.detect_faces(frame)
            
            if len(faces) == 0:
                return {
                    "face_detected": False,
                    "emotion": "neutral",
                    "confidence": 0.0,
                    "message": "No face detected"
                }
            
            # If DeepFace is available, use it
            if DEEPFACE_AVAILABLE:
                try:
                    # Use DeepFace for emotion detection
                    result = DeepFace.analyze(
                        frame,
                        actions=['emotion'],
                        enforce_detection=False,
                        silent=True
                    )
                    
                    if isinstance(result, list):
                        result = result[0]
                    
                    dominant_emotion = result['dominant_emotion']
                    emotion_scores = result['emotion']
                    confidence = emotion_scores[dominant_emotion] / 100.0
                    
                    mapped_emotion = self._map_emotion(dominant_emotion)
                    risk_level = self._calculate_risk(mapped_emotion, confidence)
                    detailed_emotions = {k: round(v/100, 3) for k, v in emotion_scores.items()}
                    
                except Exception as e:
                    logger.error(f"DeepFace analysis failed: {e}")
                    # Fallback if DeepFace fails during runtime
                    return self._fallback_result(len(faces))
            else:
                # Fallback if DeepFace is not installed/importable
                return self._fallback_result(len(faces))

            # Generate advice and suggestions
            advice_engine = get_advice_engine()
            advice = advice_engine.generate_advice(
                emotion=mapped_emotion,
                risk_level=risk_level
            )

            return {
                "face_detected": True,
                "emotion": mapped_emotion,
                "confidence": round(confidence, 3),
                "risk_level": risk_level,
                "detailed_emotions": detailed_emotions,
                "faces_count": len(faces),
                "advice": advice,
                "suggested_replies": [] # No direct replies for face, maybe general ones?
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face: {e}")
            return {
                "face_detected": False,
                "emotion": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
            
    def _fallback_result(self, face_count: int) -> dict:
        """Return a basic result when advanced analysis fails but face is detected"""
        return {
            "face_detected": True,
            "emotion": "neutral",
            "confidence": 0.5,
            "risk_level": "LOW",
            "detailed_emotions": {"neutral": 1.0},
            "faces_count": face_count,
            "message": "Face detected, but advanced analysis unavailable."
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
    
    def _map_emotion(self, deepface_emotion: str) -> str:
        """Map DeepFace emotions to our categories"""
        emotion_map = {
            "angry": "anger",
            "disgust": "disgust",
            "fear": "fear",
            "happy": "joy",
            "sad": "sadness",
            "surprise": "surprise",
            "neutral": "neutral"
        }
        
        return emotion_map.get(deepface_emotion.lower(), "neutral")
    
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
_face_analyzer_instance = None

def get_face_analyzer():
    """Get or create face analyzer singleton"""
    global _face_analyzer_instance
    if _face_analyzer_instance is None:
        _face_analyzer_instance = FaceAnalyzer()
    return _face_analyzer_instance
