"""
Smart Reply Generator - Phase 2
Generates emotionally intelligent reply suggestions
"""
import re
from typing import List, Dict


class ReplyGenerator:
    def __init__(self):
        """Initialize reply generator"""
        self.reply_templates = self._build_reply_templates()
        self.toxic_patterns = self._build_toxic_patterns()
    
    def generate_replies(self, mood: str, message: str, context: Dict = None) -> List[str]:
        """
        Generate 3-5 safe, emotionally intelligent replies
        
        Args:
            mood: Detected emotion
            message: Original message
            context: Additional context (optional)
            
        Returns:
            List of suggested replies
        """
        mood = mood.lower()
        
        # Get templates for this mood
        templates = self.reply_templates.get(mood, self.reply_templates["neutral"])
        
        # Generate replies
        raw_replies = templates["replies"]
        
        # Filter out toxic content
        safe_replies = [r for r in raw_replies if not self._is_toxic(r)]
        
        # Rank responses
        ranked_replies = self._rank_responses(safe_replies, mood)
        
        return ranked_replies[:5]  # Return top 5
    
    def _build_reply_templates(self) -> Dict:
        """Build reply templates for each emotion"""
        return {
            "anger": {
                "replies": [
                    "I'm sorry if I made you feel this way. Can we talk about what's bothering you?",
                    "I can see you're upset. I want to understand your perspective.",
                    "You're right to be frustrated. Let me listen to what you have to say.",
                    "I didn't mean to upset you. Help me understand so I can do better.",
                    "Let's take a step back. What can I do to make this right?"
                ]
            },
            
            "sadness": {
                "replies": [
                    "I'm here for you. Do you want to talk about it?",
                    "I can see you're going through something. I'm here to listen.",
                    "Is there anything I can do to help or support you?",
                    "You don't have to go through this alone. I'm here.",
                    "Take all the time you need. I'm not going anywhere."
                ]
            },
            
            "passive-aggressive": {
                "replies": [
                    "I feel like something is bothering you. Can we talk about it openly?",
                    "I sense there might be more to this. I'm ready to listen.",
                    "If something's wrong, I'd rather you tell me directly. I want to understand.",
                    "Let's be honest with each other. What's really going on?",
                    "I care about how you feel. Please tell me what's on your mind."
                ]
            },
            
            "sarcastic": {
                "replies": [
                    "I can tell you're frustrated. Let's talk about what's really bothering you.",
                    "I hear the frustration in your message. I'm listening.",
                    "Let's address the real issue here. I want to understand.",
                    "I know something's bothering you. Can we talk about it seriously?",
                    "Your feelings matter to me. Let's have an honest conversation."
                ]
            },
            
            "joy": {
                "replies": [
                    "That's amazing! I'm so happy for you! Tell me more!",
                    "This is wonderful news! I'm thrilled!",
                    "You deserve this! I'm so proud of you!",
                    "This made my day! Let's celebrate!",
                    "I love seeing you this happy! This is fantastic!"
                ]
            },
            
            "fear": {
                "replies": [
                    "I understand you're worried. Let's figure this out together.",
                    "Your concerns are valid. I'm here to help.",
                    "We'll get through this together. You're not alone.",
                    "Let's talk about what's worrying you. I'm here to support you.",
                    "It's okay to be scared. Let me help you feel safer."
                ]
            },
            
            "disgust": {
                "replies": [
                    "I understand this bothers you. Let's talk about it.",
                    "I respect how you feel about this. What can I do?",
                    "Your reaction is completely valid. How can I help?",
                    "I see this really bothers you. Let's address it.",
                    "I hear you. What would make this better for you?"
                ]
            },
            
            "surprise": {
                "replies": [
                    "I can see this caught you off guard. How are you feeling about it?",
                    "Take your time to process. I'm here when you're ready to talk.",
                    "That's quite unexpected! What do you think about it?",
                    "I understand this is a lot to take in. Let's talk about it.",
                    "How are you feeling about this surprise?"
                ]
            },
            
            "neutral": {
                "replies": [
                    "I hear you. What would you like to talk about?",
                    "Thanks for sharing. What's on your mind?",
                    "I'm listening. Tell me more.",
                    "I appreciate you telling me this.",
                    "What else is going on?"
                ]
            }
        }
    
    def _build_toxic_patterns(self) -> List[str]:
        """Build patterns for toxic content detection"""
        return [
            r'\b(shut up|stupid|idiot|dumb|hate you|don\'t care)\b',
            r'\b(whatever|fine|okay)\b$',  # Single dismissive words
            r'🙄|😒',  # Eye-roll emojis
            r'\b(your fault|blame you|always|never)\b',  # Absolutes and blame
        ]
    
    def _is_toxic(self, reply: str) -> bool:
        """Check if reply contains toxic patterns"""
        reply_lower = reply.lower()
        
        for pattern in self.toxic_patterns:
            if re.search(pattern, reply_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _rank_responses(self, replies: List[str], mood: str) -> List[str]:
        """
        Rank responses by appropriateness
        Priority: empathy > solution-focused > neutral
        """
        
        # Keywords that indicate empathy
        empathy_keywords = ["understand", "feel", "here for you", "sorry", "listen"]
        
        # Keywords that indicate solution-focus
        solution_keywords = ["help", "do", "figure out", "support", "make"]
        
        def score_reply(reply: str) -> float:
            score = 0.0
            reply_lower = reply.lower()
            
            # Empathy gets highest score for negative emotions
            if mood in ["anger", "sadness", "fear", "passive-aggressive"]:
                for keyword in empathy_keywords:
                    if keyword in reply_lower:
                        score += 2.0
                        
                for keyword in solution_keywords:
                    if keyword in reply_lower:
                        score += 1.0
            
            # For positive emotions, enthusiasm matters
            elif mood == "joy":
                if "!" in reply:
                    score += 2.0
                if any(word in reply_lower for word in ["amazing", "wonderful", "happy", "proud"]):
                    score += 1.5
            
            # Length preference (not too short, not too long)
            word_count = len(reply.split())
            if 8 <= word_count <= 20:
                score += 1.0
            
            return score
        
        # Sort by score
        ranked = sorted(replies, key=score_reply, reverse=True)
        
        return ranked


# Singleton instance
_reply_generator_instance = None

def get_reply_generator():
    """Get or create reply generator singleton"""
    global _reply_generator_instance
    if _reply_generator_instance is None:
        _reply_generator_instance = ReplyGenerator()
    return _reply_generator_instance
