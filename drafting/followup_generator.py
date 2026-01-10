"""
S15: Follow-up Generator
Creates follow-up reminders and drafts
"""
import logging
from datetime import datetime, timedelta
from typing import List
from models import FollowUp, EmailMetadata, IntentDetection

logger = logging.getLogger(__name__)


class FollowUpGenerator:
    """Generates follow-up reminders"""
    
    def generate_follow_ups(self, metadata: EmailMetadata,
                           intent: IntentDetection) -> List[FollowUp]:
        """
        S15: Draft Follow-up
        
        Creates follow-up reminders with suggested timing
        """
        logger.info(f"Generating follow-ups for: {metadata.subject}")
        
        follow_ups = []
        
        # Determine if follow-up needed
        if not self._needs_follow_up(intent):
            logger.debug("No follow-up needed")
            return follow_ups
        
        # Calculate follow-up date
        suggested_date = self._calculate_follow_up_date(intent)
        
        # Generate reason
        reason = self._generate_reason(intent)
        
        # Generate draft message
        draft_message = self._generate_follow_up_message(metadata, intent)
        
        follow_up = FollowUp(
            email_id=metadata.message_id,
            subject=f"Follow-up: {metadata.subject}",
            suggested_date=suggested_date,
            reason=reason,
            draft_message=draft_message
        )
        
        follow_ups.append(follow_up)
        
        logger.info(f"Created follow-up for {suggested_date.strftime('%Y-%m-%d')}")
        return follow_ups
    
    def _needs_follow_up(self, intent: IntentDetection) -> bool:
        """Determine if email needs follow-up"""
        # Follow-up needed for:
        # - Questions we asked
        # - Requests we made
        # - Waiting for response
        # - Meeting scheduling
        
        follow_up_intents = ['question', 'request', 'meeting']
        
        for intent_type in follow_up_intents:
            if intent_type in intent.intents:
                return True
        
        return False
    
    def _calculate_follow_up_date(self, intent: IntentDetection) -> datetime:
        """Calculate appropriate follow-up date"""
        now = datetime.now()
        
        # Urgent items: 1 day
        if 'urgent' in intent.intents:
            return now + timedelta(days=1)
        
        # Meeting requests: 2 days
        if 'meeting' in intent.intents:
            return now + timedelta(days=2)
        
        # Questions: 3 days
        if 'question' in intent.intents:
            return now + timedelta(days=3)
        
        # Default: 5 days
        return now + timedelta(days=5)
    
    def _generate_reason(self, intent: IntentDetection) -> str:
        """Generate human-readable reason for follow-up"""
        if 'urgent' in intent.intents:
            return "Urgent matter - follow up if no response"
        
        if 'meeting' in intent.intents:
            return "Meeting request pending - check availability"
        
        if 'question' in intent.intents:
            return "Question asked - follow up if unanswered"
        
        if 'request' in intent.intents:
            return "Request made - verify completion"
        
        return "Check status of this conversation"
    
    def _generate_follow_up_message(self, metadata: EmailMetadata,
                                   intent: IntentDetection) -> str:
        """Generate draft follow-up message"""
        templates = {
            'meeting': f"Hi,\n\nI wanted to follow up on my previous email regarding scheduling a meeting. Have you had a chance to review your calendar?\n\nLooking forward to hearing from you.\n\nBest regards",
            
            'question': f"Hi,\n\nI wanted to check in regarding my previous question. Please let me know if you need any clarification.\n\nThanks!",
            
            'request': f"Hi,\n\nJust following up on my previous request. Please let me know if you have any updates.\n\nThank you!",
            
            'default': f"Hi,\n\nI wanted to follow up on my previous email. Please let me know if you have any questions.\n\nBest regards"
        }
        
        # Choose template
        if 'meeting' in intent.intents:
            return templates['meeting']
        elif 'question' in intent.intents:
            return templates['question']
        elif 'request' in intent.intents:
            return templates['request']
        else:
            return templates['default']
