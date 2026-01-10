"""
S6-S7: Email Categorization
Assigns emails to categories (action, FYI, waiting, spam, legal, finance)
"""
import logging
from models import EmailCategory, IntentDetection, PriorityScore

logger = logging.getLogger(__name__)


class EmailCategorizer:
    """Categorizes emails based on intent and priority"""
    
    def categorize(self, intent: IntentDetection, 
                   priority: PriorityScore,
                   is_spam: bool) -> EmailCategory:
        """
        S6: Categorization
        
        Assigns email to appropriate category
        """
        logger.debug(f"Categorizing email with intent: {intent.primary_intent}")
        
        # Spam takes precedence
        if is_spam:
            return EmailCategory.SPAM
        
        # Legal category
        if 'legal' in intent.intents:
            logger.info("Categorized as LEGAL")
            return EmailCategory.LEGAL
        
        # Finance category
        if 'finance' in intent.intents:
            logger.info("Categorized as FINANCE")
            return EmailCategory.FINANCE
        
        # Action required
        if intent.action_required or intent.question_detected:
            logger.info("Categorized as ACTION")
            return EmailCategory.ACTION
        
        # Waiting (no action but not FYI)
        if 'request' in intent.intents or 'meeting' in intent.intents:
            logger.info("Categorized as WAITING")
            return EmailCategory.WAITING
        
        # FYI (informational only)
        if intent.primary_intent in ['informational', 'notification']:
            logger.info("Categorized as FYI")
            return EmailCategory.FYI
        
        # Default to FYI if uncertain
        logger.info("Categorized as FYI (default)")
        return EmailCategory.FYI
    
    def categorization_base_update(self, email_id: str, category: EmailCategory):
        """
        S7: Categorization Base
        
        Store categorization in database (placeholder for now)
        """
        logger.debug(f"Storing categorization: {email_id} -> {category.value}")
        # In production, this would update a database
        # For now, we just log it
        pass
