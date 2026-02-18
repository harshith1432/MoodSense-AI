"""
Text Mood Analyzer - Phase 1
Analyzes text messages to detect emotion, sarcasm, and sentiment
"""
from transformers import pipeline
from config import settings
import logging

logger = logging.getLogger(__name__)


class TextAnalyzer:
    def __init__(self):
        """Initialize HuggingFace models"""
        logger.info("Loading HuggingFace models...")
        
        try:
            # Emotion detection (7 emotions: anger, disgust, fear, joy, neutral, sadness, surprise)
            self.emotion_classifier = pipeline(
                "text-classification",
                model=settings.EMOTION_MODEL,
                top_k=None,
                device=-1  # CPU
            )
            
            # Sarcasm detection
            self.sarcasm_classifier = pipeline(
                "text-classification",
                model=settings.SARCASM_MODEL,
                device=-1
            )
            
            # Sentiment analysis
            self.sentiment_classifier = pipeline(
                "sentiment-analysis",
                model=settings.SENTIMENT_MODEL,
                device=-1
            )
            
            logger.info("✓ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def analyze_text(self, message: str) -> dict:
        """
        Main analysis function
        
        Args:
            message: Text message to analyze
            
        Returns:
            dict with emotion, risk_level, confidence, suggestions, etc.
        """
        if not message or not message.strip():
            return {
                "error": "Empty message",
                "emotion": "neutral",
                "risk_level": "LOW",
                "confidence": 0.0
            }
        
        # Get emotion
        emotion_result = self.classify_emotion(message)
        
        # Detect sarcasm
        sarcasm_result = self.detect_sarcasm(message)
        
        # Get sentiment
        sentiment_result = self.sentiment_classifier(message)[0]
        
        # Determine primary emotion considering sarcasm
        primary_emotion = emotion_result["emotion"]
        if sarcasm_result["is_sarcastic"]:
            primary_emotion = "sarcastic"
        
        # Check for passive-aggressive patterns
        is_passive_aggressive = self._detect_passive_aggressive(message, emotion_result)
        if is_passive_aggressive:
            primary_emotion = "passive-aggressive"
        
        # Calculate risk level
        risk_level = self._calculate_risk(
            emotion=primary_emotion,
            emotion_score=emotion_result["confidence"],
            sarcasm_score=sarcasm_result["confidence"],
            sentiment=sentiment_result["label"],
            sentiment_score=sentiment_result["score"]
        )
        
        # Get overall confidence
        confidence = self._calculate_confidence(emotion_result, sarcasm_result, sentiment_result)
        
        return {
            "emotion": primary_emotion,
            "risk_level": risk_level,
            "confidence": round(confidence, 3),
            "detailed_results": {
                "emotion_breakdown": emotion_result["all_emotions"],
                "is_sarcastic": sarcasm_result["is_sarcastic"],
                "sarcasm_confidence": sarcasm_result["confidence"],
                "sentiment": sentiment_result["label"],
                "sentiment_score": sentiment_result["score"]
            }
        }
    
    def classify_emotion(self, message: str) -> dict:
        """Classify emotion using HuggingFace model"""
        results = self.emotion_classifier(message)[0]
        
        # Sort by score
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        primary = results[0]
        
        return {
            "emotion": primary["label"],
            "confidence": primary["score"],
            "all_emotions": {r["label"]: round(r["score"], 3) for r in results}
        }
    
    def detect_sarcasm(self, message: str) -> dict:
        """Detect sarcasm"""
        result = self.sarcasm_classifier(message)[0]
        
        is_sarcastic = result["label"].lower() in ["sarcastic", "sarcasm", "label_1"]
        
        return {
            "is_sarcastic": is_sarcastic,
            "confidence": result["score"] if is_sarcastic else 1 - result["score"]
        }
    
    def _detect_passive_aggressive(self, message: str, emotion_result: dict) -> bool:
        """
        Detect passive-aggressive language using patterns and emotion context
        """
        message_lower = message.lower()
        
        # Common passive-aggressive patterns
        pa_patterns = [
            "fine", "whatever", "sure", "okay", "if you say so",
            "do whatever you want", "i'm fine", "no worries", "it's fine",
            "doesn't matter", "up to you", "your choice", "your call"
        ]
        
        # Check for patterns
        has_pa_pattern = any(pattern in message_lower for pattern in pa_patterns)
        
        # Check for short, dismissive responses
        is_short_dismissive = len(message.split()) <= 5 and has_pa_pattern
        
        # Check if emotion is negative despite "fine" words
        has_negative_emotion = emotion_result["emotion"] in ["anger", "sadness", "disgust"]
        
        # Periods after single words (e.g., "Fine.")
        has_emphatic_period = len(message.split()) <= 3 and message.strip().endswith(".")
        
        return (has_pa_pattern and (is_short_dismissive or has_negative_emotion)) or \
               (has_emphatic_period and has_pa_pattern)
    
    def _calculate_risk(self, emotion: str, emotion_score: float, 
                       sarcasm_score: float, sentiment: str, sentiment_score: float) -> str:
        """
        Calculate risk level based on multiple signals
        
        Risk levels: LOW, MEDIUM, HIGH, CRITICAL
        """
        risk_score = 0.0
        
        # Emotion-based risk
        high_risk_emotions = ["anger", "disgust", "fear"]
        medium_risk_emotions = ["sadness", "passive-aggressive", "sarcastic"]
        
        if emotion in high_risk_emotions:
            risk_score += 0.6 * emotion_score
        elif emotion in medium_risk_emotions:
            risk_score += 0.4 * emotion_score
        else:
            risk_score += 0.1 * emotion_score
        
        # Sarcasm adds risk
        if sarcasm_score > 0.7:
            risk_score += 0.2
        
        # Negative sentiment adds risk
        if sentiment in ["negative", "NEGATIVE", "LABEL_0"]:
            risk_score += 0.2 * sentiment_score
        
        # Determine level
        thresholds = settings.RISK_THRESHOLDS
        
        if risk_score >= thresholds["CRITICAL"]:
            return "CRITICAL"
        elif risk_score >= thresholds["HIGH"]:
            return "HIGH"
        elif risk_score >= thresholds["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(self, emotion_result: dict, sarcasm_result: dict, 
                             sentiment_result: dict) -> float:
        """Calculate overall confidence in the analysis"""
        return (
            emotion_result["confidence"] * 0.5 +
            sarcasm_result["confidence"] * 0.25 +
            sentiment_result["score"] * 0.25
        )


# Singleton instance
_analyzer_instance = None

def get_text_analyzer():
    """Get or create text analyzer singleton"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = TextAnalyzer()
    return _analyzer_instance
