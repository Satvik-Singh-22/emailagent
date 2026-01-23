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
        FOLLOW_UP_PHRASES = ["any update", "following up", "reminder", "checking in"]
        is_follow_up = any(p in text for p in FOLLOW_UP_PHRASES)

        # 1. Check Urgency
        detected_urgency = []
        urgency_score = 0

        for keyword, weight in Config.URGENCY_KEYWORDS.items():
            if keyword in text:
                detected_urgency.append(keyword)
                urgency_score += weight

        
        # 2. Check Action/Question
        action_required = any(phrase in text for phrase in ["please", "could you", "can you", "action needed"])
        question_detected = "?" in text or any(w in text for w in ["who", "what", "where", "when", "why", "how"])
        
        # 3. Detect Specific Intents
        intents = []
        if any(w in text for w in Config.LEGAL_KEYWORDS):
            intents.append("legal")
        if any(w in text for w in Config.FINANCE_KEYWORDS):
            intents.append("finance")
        if any(w in text for w in Config.IT_KEYWORDS):
            intents.append("it")
        if any(w in text for w in Config.HR_KEYWORDS):
            intents.append("hr")
        if any(w in text for w in Config.MEETING_KEYWORDS):
            intents.append("meeting")
        if any(w in text for w in Config.INVITATION_KEYWORDS):
            intents.append("invitation")
            
        if any(w in text for w in Config.COMPLAINT_KEYWORDS) or "unhappy" in text:
            intents.append("complaint")
            
        return IntentDetection(
            intents=intents,
            urgency_keywords=detected_urgency,
            urgency_score=min(urgency_score, 20),
            action_required=action_required,
            question_detected=question_detected,
            is_follow_up=is_follow_up
)

