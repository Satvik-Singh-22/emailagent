"""
S3: Priority Scoring Engine
Calculates priority score based on multiple factors
"""
import logging
from datetime import datetime, timedelta
from .config import Config
from .models import (
    PriorityScore, PriorityLevel, EmailMetadata,
    ClassificationResult, IntentDetection
)

logger = logging.getLogger(__name__)


class PriorityScorer:
    """Calculates email priority scores"""
    
    def __init__(self):
        self.threshold = Config.PRIORITY_THRESHOLD
    
    def calculate_score(self,
                       metadata: EmailMetadata,
                       classification: ClassificationResult,
                       intent: IntentDetection) -> PriorityScore:
        """
        S3: Priority Scoring Engine
        
        Calculates composite priority score (0-100) based on:
        - Sender importance (VIP, team, etc.)
        - Urgency keywords
        - Deadline proximity
        - Question/action required
        - Email age
        """
        logger.debug(f"Calculating priority for: {metadata.subject}")
        
        factors = {}
        score = 0
        
        # Factor 1: Sender importance (0-40 points)
        sender_score = self._score_sender(classification)
        
        # Boost sender score for complaints - treat as at least 'customer' level importance
        if 'complaint' in intent.intents:
            sender_score = max(sender_score, 25)
            
        if not intent.urgency_keywords and not intent.action_required and 'complaint' not in intent.intents and 'invitation' not in intent.intents:
            sender_score = min(sender_score, 20)
        factors['sender_importance'] = sender_score
        score += sender_score
        
        # Factor 2: Urgency keywords (0-20 points)
        urgency_score = self._score_urgency(intent)
        factors['urgency_keywords'] = urgency_score
        score += urgency_score
        
        # Factor 3: Action required (0-15 points)
        action_score = self._score_action(intent)
        factors['action_required'] = action_score
        score += action_score
        
        # Factor 4: Email age (0-10 points)
        age_score = self._score_age(metadata.date)
        factors['email_age'] = age_score
        score += age_score
        
        # Factor 5: Thread context (0-10 points)
        thread_score = self._score_thread(metadata)
        factors['thread_context'] = thread_score
        score += thread_score
        
        # Factor 6: Special categories (0-5 points bonus)
        category_score = self._score_category(intent)
        factors['special_category'] = category_score
        score += category_score
        
        # Urgency Override: If urgency is high, push to at least MEDIUM priority (50)
        # unless it's explicitly spam
        if intent.urgency_score >= 15:
            score = max(score, 50)
            logger.info("Urgency override triggered: Score boosted to minimum 50")
        
        # Ensure score is within 0-100
        score = max(0, min(100, int(score)))
        
        # Determine priority level
        priority_level = self._determine_level(score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(score, factors, priority_level)
        
        result = PriorityScore(
            score=score,
            priority_level=priority_level,
            factors=factors,
            reasoning=reasoning
        )
        
        logger.info(f"Priority score: {score}/100 ({priority_level.value})")
        return result
    
    def _score_sender(self, classification: ClassificationResult) -> int:
        """Score based on sender importance (0-40)"""
        if classification.is_vip:
            return 40
        
        sender_scores = {
            'vip': 40,
            'team': 30,
            'customer': 25,
            'vendor': 15,
            'unknown': 5,
            'spam': 0
        }
        
        return sender_scores.get(classification.sender_type.value, 5)
    
    def _score_urgency(self, intent: IntentDetection) -> int:
        return min(intent.urgency_score, 20)
    
    def _score_action(self, intent: IntentDetection) -> int:
        """Score based on action required (0-15)"""
        score = 0

        if intent.action_required:
            score += 8

        if intent.question_detected:
            score += 4

        if intent.action_required and intent.question_detected:
            score += 3

        if intent.is_follow_up:
            score += 3

        return min(score, 15)
    
    def _score_age(self, email_date: datetime) -> int:
        """Score based on email age (0-10) - newer = higher"""
        if not email_date:
            return 0
            
        now = datetime.now(email_date.tzinfo) if email_date.tzinfo else datetime.now()
        age = now - email_date
        
        # Less than 1 hour = 10 points
        if age < timedelta(hours=1):
            return 10
        # Less than 4 hours = 8 points
        elif age < timedelta(hours=4):
            return 8
        # Less than 24 hours = 5 points
        elif age < timedelta(days=1):
            return 5
        # Less than 3 days = 2 points
        elif age < timedelta(days=3):
            return 2
        # Older = 0 points
        else:
            return 0
    
    def _score_thread(self, metadata: EmailMetadata) -> int:
        """Score based on thread context (0-10)"""
        score = 0
        
        # If it's a reply (has Re: in subject)
        if metadata.subject.lower().startswith('re:'):
            score += 5
        
        # If user is in To: (not just CC)
        # This would require knowing user's email - simplified here
        if metadata.recipients:
            score += 3
        
        # Has attachments
        if metadata.has_attachments:
            score += 2
        
        return min(score, 10)
    
    def _score_category(self, intent: IntentDetection) -> int:
        """Score based on special categories (0-5 bonus)"""
        score = 0
        
        # Legal or finance = high priority bonus
        # 1. High Priority (+15)
        if 'complaint' in intent.intents:
            score += 15
        elif 'invitation' in intent.intents:
            score += 15
            
        # 2. Medium Priority (+5)
        elif 'legal' in intent.intents:
            score += 5
        elif 'finance' in intent.intents:
            score += 5
        elif 'it' in intent.intents:
            score += 5
        elif 'hr' in intent.intents:
            score += 5
            
        # 3. Low Priority (+3)
        elif 'meeting' in intent.intents:
            score += 3
        
        return min(score, 15)
    
    def _determine_level(self, score: int) -> PriorityLevel:
        """
        S4: High Priority? Decision
        
        Determines priority level based on score
        """
        if score >= self.threshold:
            return PriorityLevel.HIGH
        elif score >= 50:
            return PriorityLevel.MEDIUM
        elif score >= 30:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.NOT_REQUIRED
    
    def _generate_reasoning(self, score: int, factors: dict,
                           level: PriorityLevel) -> str:
        """Generate human-readable reasoning for priority score"""
        reasons = []
        
        # Sort factors by score
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        
        # Add top contributors
        for factor_name, factor_score in sorted_factors:
            if factor_score > 0:
                reason = self._factor_to_reason(factor_name, factor_score)
                if reason:
                    reasons.append(reason)
        
        reasoning = f"Priority: {level.value.upper()} ({score}/100)"
        if reasons:
            reasoning += " - " + ", ".join(reasons[:3])  # Top 3 reasons
        
        return reasoning
    
    def _factor_to_reason(self, factor_name: str, score: int) -> str:
        """Convert factor name and score to readable reason"""
        reason_map = {
            'sender_importance': f"Important sender (+{score})",
            'urgency_keywords': f"Urgent keywords (+{score})",
            'action_required': f"Action needed (+{score})",
            'email_age': f"Recent email (+{score})",
            'thread_context': f"Active thread (+{score})",
            'special_category': f"Special category (+{score})"
        }
        
        return reason_map.get(factor_name, "")
