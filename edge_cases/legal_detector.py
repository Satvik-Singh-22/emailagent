"""
E3-E4: Legal and Finance content detection with escalation
"""
import logging
from typing import List
from config import Config
from models import ProcessedEmail, SecurityFlag

logger = logging.getLogger(__name__)


class LegalFinanceDetector:
    """Detects legal/finance content requiring special handling"""
    
    def __init__(self):
        self.legal_keywords = Config.LEGAL_KEYWORDS
        self.finance_keywords = Config.FINANCE_KEYWORDS
        
        # High-risk legal phrases
        self.critical_legal_phrases = [
            'hereby agree', 'binding agreement', 'legal obligation',
            'contract terms', 'subject to', 'in accordance with',
            'liability', 'indemnify', 'confidentiality agreement'
        ]
        
        # High-risk finance phrases
        self.critical_finance_phrases = [
            'wire transfer', 'bank account', 'payment details',
            'invoice attached', 'purchase order', 'payment due',
            'credit card', 'routing number'
        ]
    
    def check_legal_finance_content_urgent(self, email: ProcessedEmail) -> bool:
        """
        E3: Thread Financial/Legal Content Urgent?
        
        Detects if email contains urgent legal or financial commitments
        """
        logger.debug(f"Checking legal/finance content for: {email.metadata.subject}")
        
        text = f"{email.metadata.subject}\n{email.metadata.body_text}".lower()
        
        # Check for legal content
        has_legal = self._check_legal_content(text)
        
        # Check for finance content
        has_finance = self._check_finance_content(text)
        
        # Check if urgent
        is_urgent = email.priority and email.priority.score >= 70
        
        is_critical = (has_legal or has_finance) and is_urgent
        
        if is_critical:
            logger.warning(f"⚠️ CRITICAL: Email contains urgent {('legal' if has_legal else 'finance')} content")
        
        return is_critical
    
    def block_auto_reply_and_escalate(self, email: ProcessedEmail) -> ProcessedEmail:
        """
        E4: Block Auto Reply and Escalate
        
        Blocks automatic response and escalates to human review
        """
        logger.warning(f"🚨 BLOCKING AUTO-REPLY and ESCALATING: {email.metadata.subject}")
        
        # Block any reply drafting
        email.requires_reply = False
        email.is_blocked = True
        email.draft_reply = None  # Remove any generated draft
        
        # Add security flag
        flag = SecurityFlag(
            flag_type="legal_finance_critical",
            severity="critical",
            description="Email contains legal or financial commitments requiring human review",
            details={
                "requires_escalation": True,
                "auto_reply_blocked": True,
                "reason": "Contains binding legal or financial language"
            },
            blocks_sending=True
        )
        
        email.security_flags.append(flag)
        
        # Add processing note
        email.processing_notes.append(
            "⚠️ ESCALATED: Contains legal/financial commitments - requires immediate human review"
        )
        
        logger.info("Email escalated successfully")
        return email
    
    def _check_legal_content(self, text: str) -> bool:
        """Check for legal content"""
        # Check basic legal keywords
        legal_count = sum(1 for keyword in self.legal_keywords if keyword in text)
        
        # Check critical legal phrases
        critical_count = sum(1 for phrase in self.critical_legal_phrases if phrase in text)
        
        # Legal content if multiple keywords or any critical phrase
        return legal_count >= 2 or critical_count >= 1
    
    def _check_finance_content(self, text: str) -> bool:
        """Check for financial content"""
        # Check basic finance keywords
        finance_count = sum(1 for keyword in self.finance_keywords if keyword in text)
        
        # Check critical finance phrases
        critical_count = sum(1 for phrase in self.critical_finance_phrases if phrase in text)
        
        # Finance content if multiple keywords or any critical phrase
        return finance_count >= 2 or critical_count >= 1
