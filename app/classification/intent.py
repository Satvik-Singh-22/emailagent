from typing import List
import re
from .models import IntentDetection
from .config import Config

class IntentScanner:
    """Scans email content for intents and urgency markers with enhanced NLP"""
    
    def scan(self, subject: str, body: str) -> IntentDetection:
        # Protect against None inputs
        subject = subject or ""
        body = body or ""
        text = (subject + " " + body).lower()
        
        # Prioritize subject line - multiply subject keywords by 1.5x
        subject_lower = subject.lower()
        
        FOLLOW_UP_PHRASES = ["any update", "following up", "reminder", "checking in", "ping", "bumping"]
        is_follow_up = any(p in text for p in FOLLOW_UP_PHRASES)

        # 1. Enhanced Urgency Detection
        detected_urgency = []
        urgency_score = 0
        
        # Check for LOW priority indicators first (reduce score)
        if hasattr(Config, 'LOW_PRIORITY_INDICATORS'):
            low_pri_found = sum(1 for indicator in Config.LOW_PRIORITY_INDICATORS if indicator in text)
            if low_pri_found > 0:
                urgency_score -= (low_pri_found * 5)  # Reduce 5 points per indicator
                detected_urgency.append(f"low_priority_indicator:{low_pri_found}")

        # Check urgency in subject (higher weight)
        for keyword, weight in Config.URGENCY_KEYWORDS.items():
            if keyword in subject_lower:
                detected_urgency.append(keyword)
                urgency_score += int(weight * 1.5)  # 50% boost for subject line
            elif keyword in text:
                detected_urgency.append(keyword)
                urgency_score += weight
        
        # Check response time urgency
        if hasattr(Config, 'RESPONSE_TIME_URGENT'):
            for pattern in Config.RESPONSE_TIME_URGENT:
                if pattern in text:
                    urgency_score += 7
                    detected_urgency.append(f"response_deadline:{pattern}")
        
        # Check high priority patterns
        if hasattr(Config, 'HIGH_PRIORITY_PATTERNS'):
            for pattern in Config.HIGH_PRIORITY_PATTERNS:
                if pattern in text:
                    urgency_score += 5
                    detected_urgency.append(f"high_priority:{pattern}")
        
        # Check time-sensitive patterns
        if hasattr(Config, 'TIME_SENSITIVE_PATTERNS'):
            for pattern in Config.TIME_SENSITIVE_PATTERNS:
                if pattern in text:
                    urgency_score += 8
                    detected_urgency.append(f"time_sensitive:{pattern}")
        
        # Detect deadline dates (today, tomorrow, specific dates)
        if self._has_near_deadline(text):
            urgency_score += 7
            detected_urgency.append("near_deadline")
        
        # 2. Enhanced Action/Question Detection
        action_phrases = [
            "please", "could you", "can you", "would you",
            "action needed", "action required", "need you to",
            "expecting", "waiting for", "require", "must",
            "need", "requested", "pending", "approval needed"
        ]
        action_required = any(phrase in text for phrase in action_phrases)
        
        # Enhanced question detection
        question_detected = ("?" in text or 
                           any(f"{w} " in text or f" {w}" in text 
                               for w in ["who", "what", "where", "when", "why", "how", "which"]))
        
        # Multiple questions = higher priority
        question_count = text.count("?")
        if question_count > 2:
            urgency_score += 3
        
        # 3. Detect Specific Intents
        intents = []
        if any(w in text for w in Config.LEGAL_KEYWORDS):
            intents.append("legal")
            urgency_score += 3  # Legal matters often important
        if any(w in text for w in Config.FINANCE_KEYWORDS):
            intents.append("finance")
            urgency_score += 3
        if any(w in text for w in Config.IT_KEYWORDS):
            intents.append("it")
        if any(w in text for w in Config.HR_KEYWORDS):
            intents.append("hr")
        if any(w in text for w in Config.MEETING_KEYWORDS):
            intents.append("meeting")
        if any(w in text for w in Config.INVITATION_KEYWORDS):
            intents.append("invitation")
            
        # Complaints = high priority
        complaint_count = sum(1 for w in Config.COMPLAINT_KEYWORDS if w in text)
        if complaint_count >= 2 or "complaint" in text:
            intents.append("complaint")
            urgency_score += 10  # Complaints need immediate attention
        
        # Detect if sender is angry/frustrated (multiple exclamation marks)
        exclamation_count = text.count("!")
        if exclamation_count > 2:
            urgency_score += 5
            detected_urgency.append("emotional_intensity")
        
        # ALL CAPS detection (yelling/urgent)
        words = text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 3]
        if len(caps_words) > 3:  # More than 3 all-caps words
            urgency_score += 4
            detected_urgency.append("all_caps_urgency")
        
        # Negative sentiment words increase urgency
        negative_words = ["problem", "issue", "error", "fail", "broken", "not working", 
                         "stopped", "down", "lost", "missing", "wrong", "bug", 
                         "crash", "dead", "critical error", "severe"]
        negative_count = sum(1 for word in negative_words if word in text)
        if negative_count >= 2:
            urgency_score += 6
            detected_urgency.append(f"negative_sentiment:{negative_count}")
        elif negative_count == 1:
            urgency_score += 3
        
        # Business impact words
        business_impact_words = ["revenue", "customer", "client", "deal", "contract",
                                "lawsuit", "legal action", "competitor", "market share",
                                "losing", "risk", "threat"]
        business_count = sum(1 for word in business_impact_words if word in text)
        if business_count >= 2:
            urgency_score += 8
            detected_urgency.append(f"business_impact:{business_count}")
        
        # Action verbs that indicate required response
        strong_action_verbs = ["approve", "sign", "authorize", "confirm", 
                              "review immediately", "validate", "verify now"]
        if any(verb in text for verb in strong_action_verbs):
            urgency_score += 5
            detected_urgency.append("strong_action_required")
        
        # Cap urgency score at 35 (increased from 30) and ensure minimum of 0
        urgency_score = max(0, min(urgency_score, 35))
            
        return IntentDetection(
            intents=intents,
            urgency_keywords=detected_urgency,
            urgency_score=urgency_score,
            action_required=action_required,
            question_detected=question_detected,
            is_follow_up=is_follow_up
        )
    
    def _has_near_deadline(self, text: str) -> bool:
        """Detect if email mentions a near deadline"""
        deadline_patterns = [
            r"due (today|tomorrow|this week)",
            r"deadline.*?(today|tomorrow)",
            r"by (today|tomorrow|tonight|eod)",
            r"expires? (today|tomorrow|soon)",
            r"(today|tomorrow).*deadline",
            r"within.*?(24|48) hours?"
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in deadline_patterns)

