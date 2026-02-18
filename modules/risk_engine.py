"""
Relationship Risk Engine - Final Integration
Combines text, voice, and facial signals for comprehensive risk assessment
"""
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    def __init__(self):
        """Initialize risk engine"""
        logger.info("Risk Engine initialized")
        
        # Weights for multi-modal fusion
        self.weights = {
            "text": 0.40,
            "voice": 0.30,
            "face": 0.30
        }
    
    def calculate_combined_risk(self,
                               text_data: Optional[Dict] = None,
                               voice_data: Optional[Dict] = None,
                               face_data: Optional[Dict] = None) -> Dict:
        """
        Calculate overall risk from multiple signals
        
        Args:
            text_data: Text analysis results
            voice_data: Voice analysis results
            face_data: Face analysis results
            
        Returns:
            dict with combined risk assessment and recommendations
        """
        # Collect available signals
        signals = {}
        risk_scores = []
        
        if text_data:
            signals["text"] = {
                "emotion": text_data.get("emotion", "neutral"),
                "risk_level": text_data.get("risk_level", "LOW"),
                "confidence": text_data.get("confidence", 0.0)
            }
            risk_scores.append(
                (self._risk_to_score(text_data.get("risk_level", "LOW")), self.weights["text"])
            )
        
        if voice_data:
            signals["voice"] = {
                "emotion": voice_data.get("emotion", "neutral"),
                "tone": voice_data.get("tone", "Neutral"),
                "stress_level": voice_data.get("stress_level", 0.0),
                "risk_level": voice_data.get("risk_level", "LOW")
            }
            risk_scores.append(
                (self._risk_to_score(voice_data.get("risk_level", "LOW")), self.weights["voice"])
            )
        
        if face_data and face_data.get("face_detected"):
            signals["face"] = {
                "emotion": face_data.get("emotion", "neutral"),
                "confidence": face_data.get("confidence", 0.0),
                "risk_level": face_data.get("risk_level", "LOW")
            }
            risk_scores.append(
                (self._risk_to_score(face_data.get("risk_level", "LOW")), self.weights["face"])
            )
        
        # Calculate weighted risk score
        if risk_scores:
            combined_score = sum(score * weight for score, weight in risk_scores)
            # Normalize by total weight used
            total_weight = sum(weight for _, weight in risk_scores)
            combined_score = combined_score / total_weight if total_weight > 0 else 0.0
        else:
            combined_score = 0.0
        
        # Convert to risk level
        combined_risk_level = self._score_to_risk(combined_score)
        
        # Detect conflicts between signals
        conflict_detected = self._detect_signal_conflict(signals)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            combined_risk_level,
            signals,
            conflict_detected
        )
        
        # Get dominant emotion
        dominant_emotion = self._get_dominant_emotion(signals)
        
        return {
            "risk_level": combined_risk_level,
            "risk_score": round(combined_score, 3),
            "confidence": self._calculate_confidence(signals),
            "dominant_emotion": dominant_emotion,
            "signals": signals,
            "signal_conflict": conflict_detected,
            "recommendations": recommendations,
            "explanation": self._generate_explanation(signals, combined_risk_level)
        }
    
    def detect_escalation(self, history: List[Dict]) -> Dict:
        """
        Detect if situation is escalating based on historical trend
        
        Args:
            history: List of past risk assessments
            
        Returns:
            dict with trend analysis
        """
        if len(history) < 3:
            return {
                "trend": "insufficient_data",
                "is_escalating": False
            }
        
        # Get last 5 risk scores
        recent = history[-5:]
        scores = [self._risk_to_score(item.get("risk_level", "LOW")) for item in recent]
        
        # Check if generally increasing
        is_escalating = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
        is_improving = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if is_escalating:
            trend = "escalating"
        elif is_improving:
            trend = "improving"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "is_escalating": is_escalating,
            "is_improving": is_improving,
            "recent_scores": scores
        }
    
    def _risk_to_score(self, risk_level: str) -> float:
        """Convert risk level to numeric score"""
        mapping = {
            "LOW": 0.2,
            "MEDIUM": 0.5,
            "HIGH": 0.75,
            "CRITICAL": 0.95
        }
        return mapping.get(risk_level, 0.2)
    
    def _score_to_risk(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 0.85:
            return "CRITICAL"
        elif score >= 0.7:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _detect_signal_conflict(self, signals: Dict) -> bool:
        """Detect if different signals contradict each other"""
        emotions = [s.get("emotion") for s in signals.values() if "emotion" in s]
        
        if len(emotions) < 2:
            return False
        
        # Check if we have both positive and negative emotions
        positive = ["joy", "surprise"]
        negative = ["anger", "sadness", "fear", "disgust"]
        
        has_positive = any(e in positive for e in emotions)
        has_negative = any(e in negative for e in emotions)
        
        return has_positive and has_negative
    
    def _get_dominant_emotion(self, signals: Dict) -> str:
        """Determine overall dominant emotion"""
        emotions = {}
        
        for source, data in signals.items():
            if "emotion" in data:
                emotion = data["emotion"]
                emotions[emotion] = emotions.get(emotion, 0) + 1
        
        if not emotions:
            return "neutral"
        
        # Return most common emotion
        return max(emotions.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, signals: Dict) -> float:
        """Calculate overall confidence in assessment"""
        confidences = []
        
        if "text" in signals:
            confidences.append(signals["text"].get("confidence", 0.5))
        
        if "face" in signals:
            confidences.append(signals["face"].get("confidence", 0.5))
        
        if "voice" in signals:
            # Use inverse of stress level variability as confidence proxy
            confidences.append(0.7)  # Default voice confidence
        
        return round(sum(confidences) / len(confidences), 3) if confidences else 0.5
    
    def _generate_recommendations(self, risk_level: str, signals: Dict, 
                                 has_conflict: bool) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 IMMEDIATE ATTENTION REQUIRED",
                "Pause the conversation immediately",
                "Take responsibility if you contributed to this",
                "Focus entirely on listening and understanding",
                "Avoid being defensive at all costs",
                "Consider suggesting a break if emotions are too high"
            ])
        
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ De-escalation needed",
                "Stop arguing or defending your position",
                "Listen actively without interrupting",
                "Acknowledge their feelings sincerely",
                "Apologize if appropriate"
            ])
        
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Be mindful of your communication",
                "Pay attention to tone and word choice",
                "Show empathy and understanding",
                "Ask clarifying questions"
            ])
        
        else:  # LOW
            recommendations.extend([
                "Continue communicating normally",
                "Stay present and engaged",
                "Monitor for subtle emotional shifts"
            ])
        
        # Add signal-specific recommendations
        if has_conflict:
            recommendations.append(
                "⚠️ Mixed signals detected - Pay extra attention to subtle cues"
            )
        
        if "voice" in signals and signals["voice"].get("stress_level", 0) > 0.7:
            recommendations.append(
                "💭 High vocal stress detected - Consider calming your own tone"
            )
        
        return recommendations
    
    def _generate_explanation(self, signals: Dict, risk_level: str) -> str:
        """Generate human-readable explanation"""
        parts = []
        
        if "text" in signals:
            text_emotion = signals["text"]["emotion"]
            parts.append(f"text shows {text_emotion}")
        
        if "voice" in signals:
            voice_tone = signals["voice"]["tone"]
            parts.append(f"voice tone is {voice_tone}")
        
        if "face" in signals:
            face_emotion = signals["face"]["emotion"]
            parts.append(f"facial expression indicates {face_emotion}")
        
        signal_summary = ", ".join(parts) if parts else "limited data available"
        
        return f"Overall risk level is {risk_level}. {signal_summary.capitalize()}."


# Singleton instance
_risk_engine_instance = None

def get_risk_engine():
    """Get or create risk engine singleton"""
    global _risk_engine_instance
    if _risk_engine_instance is None:
        _risk_engine_instance = RiskEngine()
    return _risk_engine_instance
