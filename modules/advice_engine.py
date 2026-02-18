"""
Advice Engine - Phase 1
Generates contextual advice and safe response suggestions
"""


class AdviceEngine:
    def __init__(self):
        """Initialize advice database"""
        self.advice_db = self._build_advice_database()
    
    def generate_advice(self, emotion: str, risk_level: str, context: dict = None) -> dict:
        """
        Generate advice based on detected emotion and risk level
        
        Args:
            emotion: Detected emotion (anger, sadness, etc.)
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
            context: Additional context (optional)
            
        Returns:
            dict with suggested_response, things_to_avoid, general_advice
        """
        emotion = emotion.lower()
        
        # Get emotion-specific advice
        emotion_advice = self.advice_db.get(emotion, self.advice_db["neutral"])
        
        # Get risk-specific recommendations
        risk_advice = self._get_risk_specific_advice(risk_level)
        
        return {
            "suggested_response": emotion_advice["suggested_response"],
            "things_to_avoid": emotion_advice["things_to_avoid"],
            "general_advice": emotion_advice["general_advice"],
            "risk_specific": risk_advice,
            "explanation": emotion_advice["explanation"]
        }
    
    def _build_advice_database(self) -> dict:
        """Build comprehensive advice database for each emotion"""
        return {
            "anger": {
                "suggested_response": "I can see you're upset. Can we talk about what's bothering you?",
                "things_to_avoid": [
                    "Dismissive responses like 'Calm down' or 'It's not a big deal'",
                    "Arguing back or being defensive",
                    "Minimizing their feelings",
                    "Using sarcasm or joking"
                ],
                "general_advice": [
                    "Listen actively without interrupting",
                    "Acknowledge their feelings",
                    "Give them space if needed",
                    "Stay calm and don't match their energy"
                ],
                "explanation": "Anger indicates strong frustration. De-escalation is key."
            },
            
            "sadness": {
                "suggested_response": "I'm here for you. Do you want to talk about it?",
                "things_to_avoid": [
                    "Saying 'Don't be sad' or 'Cheer up'",
                    "Trying to immediately fix the problem",
                    "Comparing their situation to others",
                    "Changing the subject"
                ],
                "general_advice": [
                    "Offer emotional support",
                    "Listen with empathy",
                    "Ask if they need anything",
                    "Be patient and present"
                ],
                "explanation": "Sadness needs validation and emotional support, not solutions."
            },
            
            "passive-aggressive": {
                "suggested_response": "I feel like something is bothering you. Want to talk about it?",
                "things_to_avoid": [
                    "Responding with 'Okay 👍' or matching their tone",
                    "Ignoring the underlying issue",
                    "Being passive-aggressive back",
                    "Asking 'What's wrong?' repeatedly"
                ],
                "general_advice": [
                    "Address the underlying issue directly but gently",
                    "Create a safe space for honest communication",
                    "Don't take the bait - stay calm",
                    "Acknowledge there might be unspoken concerns"
                ],
                "explanation": "Passive-aggression hides deeper feelings. Encourage open communication."
            },
            
            "sarcastic": {
                "suggested_response": "I sense some frustration. Let's talk about what's really going on.",
                "things_to_avoid": [
                    "Being sarcastic back",
                    "Taking it personally",
                    "Ignoring the underlying message",
                    "Laughing it off"
                ],
                "general_advice": [
                    "Read between the lines",
                    "Address the real issue, not the sarcasm",
                    "Stay genuine and sincere",
                    "Don't escalate with humor"
                ],
                "explanation": "Sarcasm often masks frustration or hurt. Look for the real message."
            },
            
            "joy": {
                "suggested_response": "That's wonderful! I'm so happy for you!",
                "things_to_avoid": [
                    "Downplaying their excitement",
                    "Making it about yourself",
                    "Being cynical or negative",
                    "Ignoring their good news"
                ],
                "general_advice": [
                    "Share in their happiness",
                    "Ask them to tell you more",
                    "Be genuinely enthusiastic",
                    "Celebrate with them"
                ],
                "explanation": "Joy is contagious. Amplify positive moments together."
            },
            
            "fear": {
                "suggested_response": "I understand you're worried. Let's figure this out together.",
                "things_to_avoid": [
                    "Saying 'Don't worry' or 'It's fine'",
                    "Dismissing their concerns",
                    "Adding to their anxiety",
                    "Being overly logical"
                ],
                "general_advice": [
                    "Validate their concerns",
                    "Offer reassurance and support",
                    "Help them feel safe",
                    "Be patient and understanding"
                ],
                "explanation": "Fear needs reassurance and a sense of safety."
            },
            
            "disgust": {
                "suggested_response": "I can see this really bothers you. Let's talk about it.",
                "things_to_avoid": [
                    "Arguing about what's 'disgusting' or not",
                    "Minimizing their reaction",
                    "Forcing them to engage with the source",
                    "Being dismissive"
                ],
                "general_advice": [
                    "Respect their boundaries",
                    "Acknowledge their feelings",
                    "Give them space from the trigger",
                    "Don't push them to explain"
                ],
                "explanation": "Disgust is a strong aversion. Respect their reaction."
            },
            
            "surprise": {
                "suggested_response": "That must have caught you off guard! How are you feeling?",
                "things_to_avoid": [
                    "Assuming it's positive or negative",
                    "Downplaying the surprise",
                    "Moving on too quickly",
                    "Making it about yourself"
                ],
                "general_advice": [
                    "Give them time to process",
                    "Ask how they feel about it",
                    "Be supportive regardless of their reaction",
                    "Listen to their perspective"
                ],
                "explanation": "Surprise can be positive or negative. Let them process."
            },
            
            "neutral": {
                "suggested_response": "I hear you. What would you like to talk about?",
                "things_to_avoid": [
                    "Assuming everything is fine",
                    "Being overly analytical",
                    "Ignoring subtle cues",
                    "Being dismissive"
                ],
                "general_advice": [
                    "Stay present and engaged",
                    "Watch for subtle emotional shifts",
                    "Ask open-ended questions",
                    "Create space for deeper sharing"
                ],
                "explanation": "Neutral doesn't mean emotionless. Stay attentive."
            }
        }
    
    def _get_risk_specific_advice(self, risk_level: str) -> dict:
        """Get advice specific to risk level"""
        risk_db = {
            "LOW": {
                "priority": "Monitor the conversation",
                "action": "Continue normal communication",
                "urgency": "No immediate action needed"
            },
            "MEDIUM": {
                "priority": "Be mindful and considerate",
                "action": "Pay attention to your tone and word choice",
                "urgency": "Slight caution recommended"
            },
            "HIGH": {
                "priority": "De-escalation needed",
                "action": "Focus on listening and validating feelings",
                "urgency": "Careful communication required"
            },
            "CRITICAL": {
                "priority": "🚨 IMMEDIATE ATTENTION REQUIRED",
                "action": "Stop, listen, and prioritize emotional safety",
                "urgency": "High risk of conflict escalation",
                "emergency_tips": [
                    "Pause the conversation if necessary",
                    "Apologize if you contributed to the situation",
                    "Focus entirely on understanding their perspective",
                    "Avoid being defensive at all costs",
                    "Consider suggesting a break if emotions are too high"
                ]
            }
        }
        
        return risk_db.get(risk_level, risk_db["LOW"])


# Singleton instance
_advice_engine_instance = None

def get_advice_engine():
    """Get or create advice engine singleton"""
    global _advice_engine_instance
    if _advice_engine_instance is None:
        _advice_engine_instance = AdviceEngine()
    return _advice_engine_instance
