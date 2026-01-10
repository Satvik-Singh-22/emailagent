"""
S8: Spam Detection
Detects spam and promotional emails
"""
import logging
from config import Config
from models import EmailMetadata, ClassificationResult, SenderType

logger = logging.getLogger(__name__)


class SpamFilter:
    """Detects spam emails"""
    
    def __init__(self):
        self.spam_indicators = Config.SPAM_INDICATORS
    
    def is_spam(self, metadata: EmailMetadata,
                classification: ClassificationResult) -> bool:
        """
        S8: Spam?
        
        Determines if email is spam based on multiple signals
        """
        logger.debug(f"Checking spam for: {metadata.subject}")
        
        spam_score = 0
        
        # Signal 1: Sender classified as spam
        if classification.sender_type == SenderType.SPAM:
            spam_score += 40
        
        # Signal 2: Spam keywords in subject/body
        text = f"{metadata.subject}\n{metadata.body_text}".lower()
        spam_keyword_count = sum(1 for indicator in self.spam_indicators 
                                if indicator in text)
        spam_score += min(spam_keyword_count * 10, 30)
        
        # Signal 3: Already in spam label
        if 'SPAM' in metadata.labels:
            spam_score += 50
        
        # Signal 4: Unsubscribe link present (marketing)
        if 'unsubscribe' in text:
            spam_score += 20
        
        # Signal 5: No direct recipient (bulk email)
        if not metadata.recipients or len(metadata.recipients) > 10:
            spam_score += 15
        
        # Signal 6: Excessive links or promotional language
        if text.count('http') > 5 or text.count('click here') > 2:
            spam_score += 15
        
        is_spam_email = spam_score >= 50
        
        if is_spam_email:
            logger.info(f"✗ Marked as SPAM (score: {spam_score})")
        else:
            logger.debug(f"Not spam (score: {spam_score})")
        
        return is_spam_email
    
    def mark_as_blocked(self, email_id: str):
        """
        S9: Mark as Blocked
        
        Mark email as blocked/spam
        """
        logger.info(f"Marking as blocked: {email_id}")
        # In production, would update Gmail labels or database
        pass
