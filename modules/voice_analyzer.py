"""
Voice Tone Analyzer - Phase 3
Analyzes emotional tone from voice recordings using audio features
"""
import librosa
import numpy as np
import logging
from pathlib import Path

from modules.advice_engine import get_advice_engine
from modules.reply_generator import get_reply_generator

logger = logging.getLogger(__name__)


class VoiceAnalyzer:
    def __init__(self):
        """Initialize voice analyzer"""
        logger.info("Voice Analyzer initialized")
    
    def analyze_voice(self, audio_path: str) -> dict:
        """
        Main voice analysis function
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with tone, stress_level, features, and recommendations
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Extract features
            features = self.extract_features(audio_path, y, sr)
            
            # Classify tone
            tone = self.classify_tone(features)
            
            # Calculate stress level
            stress_level = self.calculate_stress_level(features)
            
            # Determine emotion from audio
            emotion = self._infer_emotion(tone, stress_level, features)
            
            # Calculate risk
            risk_level = self._calculate_risk(emotion, stress_level, features)
            
            # Generate advice
            advice_engine = get_advice_engine()
            advice = advice_engine.generate_advice(
                emotion=emotion,
                risk_level=risk_level
            )
            
            # Generate reply suggestions (using "Voice Message" as context)
            reply_gen = get_reply_generator()
            replies = reply_gen.generate_replies(
                mood=emotion,
                message="Voice Message" 
            )

            return {
                "tone": tone,
                "emotion": emotion,
                "stress_level": round(stress_level, 3),
                "risk_level": risk_level,
                "features": {
                    "pitch": features["pitch"],
                    "volume": features["volume"],
                    "speech_rate": features["speech_rate"],
                    "energy": features["energy"]
                },
                "interpretation": self._interpret_results(tone, emotion, stress_level),
                "advice": advice,
                "suggested_replies": replies
            }
            
        except Exception as e:
            logger.error(f"Error analyzing voice: {e}")
            raise
    
    def extract_features(self, audio_path: str, y: np.ndarray, sr: int) -> dict:
        """
        Extract audio features: pitch, volume, speech rate, energy
        """
        # 1. Pitch (F0 - fundamental frequency)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        avg_pitch = np.mean(pitch_values) if pitch_values else 0
        pitch_std = np.std(pitch_values) if pitch_values else 0
        
        # 2. Volume (RMS energy)
        rms = librosa.feature.rms(y=y)[0]
        avg_volume = np.mean(rms)
        volume_std = np.std(rms)
        
        # 3. Speech rate (zero crossing rate as proxy)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        avg_zcr = np.mean(zcr)
        
        # 4. Energy (spectral centroid)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_energy = np.mean(spectral_centroids)
        
        # 5. Tempo
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        return {
            "pitch": {
                "mean": float(avg_pitch),
                "std": float(pitch_std),
                "level": self._categorize_pitch(avg_pitch)
            },
            "volume": {
                "mean": float(avg_volume),
                "std": float(volume_std),
                "level": self._categorize_volume(avg_volume)
            },
            "speech_rate": {
                "zcr": float(avg_zcr),
                "tempo": float(tempo),
                "level": self._categorize_speech_rate(avg_zcr)
            },
            "energy": {
                "mean": float(avg_energy),
                "level": self._categorize_energy(avg_energy)
            }
        }
    
    def classify_tone(self, features: dict) -> str:
        """
        Classify overall tone based on features
        """
        pitch_level = features["pitch"]["level"]
        volume_level = features["volume"]["level"]
        speech_rate = features["speech_rate"]["level"]
        
        # High pitch + loud + fast = Excited/Angry
        if pitch_level == "high" and volume_level == "loud" and speech_rate == "fast":
            return "Excited/Agitated"
        
        # High pitch + loud = Angry
        elif pitch_level == "high" and volume_level == "loud":
            return "Angry"
        
        # Low pitch + soft = Sad/Calm
        elif pitch_level == "low" and volume_level == "soft":
            return "Sad/Calm"
        
        # Fast speech = Anxious/Excited
        elif speech_rate == "fast":
            return "Anxious/Excited"
        
        # Slow speech = Calm/Tired
        elif speech_rate == "slow":
            return "Calm/Tired"
        
        else:
            return "Neutral"
    
    def calculate_stress_level(self, features: dict) -> float:
        """
        Calculate stress level (0-1 scale)
        """
        stress_score = 0.0
        
        # High pitch indicates stress
        if features["pitch"]["level"] == "high":
            stress_score += 0.3
        
        # Loud volume indicates stress
        if features["volume"]["level"] == "loud":
            stress_score += 0.25
        
        # Fast speech indicates stress
        if features["speech_rate"]["level"] == "fast":
            stress_score += 0.25
        
        # High pitch variability indicates stress
        if features["pitch"]["std"] > 50:
            stress_score += 0.2
        
        return min(stress_score, 1.0)
    
    def _infer_emotion(self, tone: str, stress_level: float, features: dict) -> str:
        """Infer emotion from tone and stress"""
        if "Angry" in tone or "Agitated" in tone:
            return "anger"
        elif "Sad" in tone:
            return "sadness"
        elif "Anxious" in tone and stress_level > 0.6:
            return "fear"
        elif "Excited" in tone and stress_level < 0.5:
            return "joy"
        else:
            return "neutral"
    
    def _calculate_risk(self, emotion: str, stress_level: float, features: dict) -> str:
        """Calculate risk level from voice analysis"""
        risk_score = 0.0
        
        # Emotion-based risk
        high_risk_emotions = ["anger", "fear"]
        if emotion in high_risk_emotions:
            risk_score += 0.5
        
        # Stress-based risk
        risk_score += stress_level * 0.3
        
        # Volume-based (shouting)
        if features["volume"]["level"] == "loud":
            risk_score += 0.2
        
        # Determine level
        if risk_score >= 0.85:
            return "CRITICAL"
        elif risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _interpret_results(self, tone: str, emotion: str, stress_level: float) -> str:
        """Generate human-readable interpretation"""
        stress_desc = "high" if stress_level > 0.6 else "moderate" if stress_level > 0.3 else "low"
        
        return f"Voice tone indicates {emotion} with {stress_desc} stress level. " \
               f"Overall tone classified as: {tone}."
    
    def _categorize_pitch(self, pitch: float) -> str:
        """Categorize pitch level"""
        if pitch > 250:
            return "high"
        elif pitch > 150:
            return "normal"
        else:
            return "low"
    
    def _categorize_volume(self, volume: float) -> str:
        """Categorize volume level"""
        if volume > 0.1:
            return "loud"
        elif volume > 0.05:
            return "normal"
        else:
            return "soft"
    
    def _categorize_speech_rate(self, zcr: float) -> str:
        """Categorize speech rate"""
        if zcr > 0.1:
            return "fast"
        elif zcr > 0.05:
            return "normal"
        else:
            return "slow"
    
    def _categorize_energy(self, energy: float) -> str:
        """Categorize energy level"""
        if energy > 2000:
            return "high"
        elif energy > 1000:
            return "normal"
        else:
            return "low"


# Singleton instance
_voice_analyzer_instance = None

def get_voice_analyzer():
    """Get or create voice analyzer singleton"""
    global _voice_analyzer_instance
    if _voice_analyzer_instance is None:
        _voice_analyzer_instance = VoiceAnalyzer()
    return _voice_analyzer_instance
