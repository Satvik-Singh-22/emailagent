"""
Clarification Request Handler
Detects when user input is needed due to ambiguous recipients or unclear intent
"""
import logging
from typing import List, Optional, Dict, Any
from models import ProcessedEmail, IntentDetection, ClarificationRequest, ClarificationReason

logger = logging.getLogger(__name__)


class ClarificationHandler:
    """Handles detection and generation of clarification requests"""
    
    def __init__(self):
        self.min_confidence_threshold = 0.6
        self.max_recipients_without_confirmation = 5
    
    def needs_clarification(self, email: ProcessedEmail) -> bool:
        """
        Determines if email processing requires user clarification
        
        Returns: True if clarification needed, False otherwise
        """
        logger.debug(f"Checking if clarification needed for: {email.metadata.subject}")
        
        # Check if draft reply exists
        if not email.draft_reply:
            return False
        
        # Check for ambiguous recipients
        if self._has_ambiguous_recipients(email):
            return True
        
        # Check for low confidence intent
        if self._has_unclear_intent(email):
            return True
        
        # Check for missing critical information
        if self._missing_critical_info(email):
            return True
        
        return False
    
    def generate_clarification_request(self, email: ProcessedEmail) -> ClarificationRequest:
        """
        Generates a clarification request with specific questions
        
        Returns: ClarificationRequest object
        """
        logger.info(f"Generating clarification request for: {email.metadata.subject}")
        
        reasons = []
        questions = []
        
        # Check for ambiguous recipients
        if self._has_ambiguous_recipients(email):
            reason = ClarificationReason.AMBIGUOUS_RECIPIENTS
            reasons.append(reason)
            questions.extend(self._generate_recipient_questions(email))
        
        # Check for unclear intent
        if self._has_unclear_intent(email):
            reason = ClarificationReason.UNCLEAR_INTENT
            reasons.append(reason)
            questions.extend(self._generate_intent_questions(email))
        
        # Check for missing info
        if self._missing_critical_info(email):
            reason = ClarificationReason.MISSING_INFORMATION
            reasons.append(reason)
            questions.extend(self._generate_missing_info_questions(email))
        
        clarification = ClarificationRequest(
            email_id=email.metadata.message_id,
            subject=email.metadata.subject,
            reasons=reasons,
            questions=questions,
            context=self._build_context(email)
        )
        
        logger.info(f"Clarification needed: {len(questions)} question(s)")
        return clarification
    
    def _has_ambiguous_recipients(self, email: ProcessedEmail) -> bool:
        """Check if recipients are ambiguous or missing"""
        if not email.draft_reply:
            return False
        
        recipients = email.draft_reply.recipients
        
        # No recipients specified
        if not recipients:
            logger.debug("No recipients specified - needs clarification")
            return True
        
        # Multiple potential candidates detected (we'll check for common patterns)
        # For example, if original email has CC list and we're not sure who to reply to
        original_recipients = email.metadata.recipients + email.metadata.cc
        
        # If original had multiple recipients and we're replying to just one,
        # might need confirmation
        if len(original_recipients) > 1 and len(recipients) == 1:
            if email.metadata.sender not in recipients:
                logger.debug("Potential reply target ambiguity")
                return True
        
        # Check for generic/ambiguous email addresses
        for recipient in recipients:
            if self._is_ambiguous_email(recipient):
                logger.debug(f"Ambiguous recipient detected: {recipient}")
                return True
        
        return False
    
    def _has_unclear_intent(self, email: ProcessedEmail) -> bool:
        """Check if intent detection confidence is too low"""
        if not email.intent:
            return True
        
        # Low confidence score
        if email.intent.confidence < self.min_confidence_threshold:
            logger.debug(f"Low intent confidence: {email.intent.confidence}")
            return True
        
        # Primary intent is unclear/unknown
        if email.intent.primary_intent in ['unknown', 'unclear']:
            logger.debug("Primary intent unclear")
            return True
        
        # Multiple conflicting intents detected
        if len(email.intent.intents) > 3:
            logger.debug("Too many intents - potentially unclear")
            return True
        
        return False
    
    def _missing_critical_info(self, email: ProcessedEmail) -> bool:
        """Check if critical information is missing for drafting"""
        if not email.draft_reply:
            return False
        
        # Action required but no clear action in draft
        if email.intent and email.intent.action_required:
            draft_body = email.draft_reply.body.lower()
            
            # Check if draft doesn't address the action
            action_indicators = ['will', 'can', 'schedule', 'send', 'provide', 'confirm']
            has_action_response = any(word in draft_body for word in action_indicators)
            
            if not has_action_response:
                logger.debug("Action required but draft doesn't address it")
                return True
        
        # Question detected but no clear answer in draft
        if email.intent and email.intent.question_detected:
            draft_body = email.draft_reply.body.lower()
            
            # Very short draft might not answer question
            if len(draft_body) < 50:
                logger.debug("Question detected but draft too short")
                return True
        
        return False
    
    def _is_ambiguous_email(self, email_address: str) -> bool:
        """Check if email address is generic/ambiguous"""
        ambiguous_patterns = [
            'info@', 'contact@', 'support@', 'help@', 
            'sales@', 'admin@', 'team@', 'noreply@'
        ]
        
        email_lower = email_address.lower()
        return any(pattern in email_lower for pattern in ambiguous_patterns)
    
    def _generate_recipient_questions(self, email: ProcessedEmail) -> List[str]:
        """Generate questions about recipients"""
        questions = []
        
        if not email.draft_reply or not email.draft_reply.recipients:
            questions.append(
                f"Who should receive the reply for '{email.metadata.subject}'? "
                f"Original sender: {email.metadata.sender}"
            )
        else:
            recipients = email.draft_reply.recipients
            if any(self._is_ambiguous_email(r) for r in recipients):
                questions.append(
                    f"The recipient '{recipients[0]}' appears to be a generic address. "
                    f"Should we send to this address or to a specific person?"
                )
        
        # Check if we should include CC recipients
        if email.metadata.cc:
            questions.append(
                f"Should we include CC recipients in the reply? "
                f"CC list: {', '.join(email.metadata.cc[:3])}"
            )
        
        return questions
    
    def _generate_intent_questions(self, email: ProcessedEmail) -> List[str]:
        """Generate questions about intent"""
        questions = []
        
        if email.intent:
            if email.intent.confidence < self.min_confidence_threshold:
                questions.append(
                    f"The intent of this email is unclear (confidence: {email.intent.confidence:.0%}). "
                    f"What action should we take?"
                )
            
            if len(email.intent.intents) > 3:
                questions.append(
                    f"This email seems to cover multiple topics: {', '.join(email.intent.intents[:3])}. "
                    f"Which should we prioritize in the response?"
                )
        
        return questions
    
    def _generate_missing_info_questions(self, email: ProcessedEmail) -> List[str]:
        """Generate questions about missing information"""
        questions = []
        
        if email.intent and email.intent.action_required:
            questions.append(
                "This email requires an action, but we need more context. "
                "What specific action should be taken?"
            )
        
        if email.intent and email.intent.question_detected:
            questions.append(
                "This email contains a question. Do you have the information needed to answer it?"
            )
        
        return questions
    
    def _build_context(self, email: ProcessedEmail) -> Dict[str, Any]:
        """Build context information for clarification"""
        return {
            "message_id": email.metadata.message_id,
            "thread_id": email.metadata.thread_id,
            "subject": email.metadata.subject,
            "sender": email.metadata.sender,
            "date": email.metadata.date.isoformat(),
            "original_recipients": email.metadata.recipients,
            "cc": email.metadata.cc,
            "priority_score": email.priority.score if email.priority else 0,
            "category": email.category.value,
            "intent_confidence": email.intent.confidence if email.intent else 0
        }
