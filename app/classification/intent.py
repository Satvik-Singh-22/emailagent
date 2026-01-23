from typing import List
from .models import IntentDetection
from .config import Config

class IntentScanner:
    """Scans email content for intents and urgency markers"""
    
    def scan(self, subject: str, body: str) -> IntentDetection:
        # Protect against None inputs
        subject = subject or ""
        body = body or ""
        text = (subject + " " + body).lower()
        
        # 1. Check Urgency
        detected_urgency = [w for w in Config.URGENCY_KEYWORDS if w in text]
        
        # 2. Check Action/Question
        action_required = any(phrase in text for phrase in ["please", "could you", "can you", "action needed"])
        question_detected = "?" in text or any(w in text for w in ["who", "what", "where", "when", "why", "how"])
        
        # 3. Detect Specific Intents
        intents = []
        if any(w in text for w in Config.LEGAL_KEYWORDS):
            intents.append("legal")
        if any(w in text for w in Config.FINANCE_KEYWORDS):
            intents.append("finance")
        if "complaint" in text or "unhappy" in text:
            intents.append("complaint")
            
        return IntentDetection(
            intents=intents,
            urgency_keywords=detected_urgency,
            action_required=action_required,
            question_detected=question_detected
        )
