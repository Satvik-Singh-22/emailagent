"""
E1-E2: Conflict resolution for multiple emails from same sender
"""
import logging
from typing import List, Dict
from datetime import datetime
from models import ProcessedEmail

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolves conflicts when multiple emails from same sender"""
    
    def check_multiple_from_same_sender(self,
                                       emails: List[ProcessedEmail]) -> Dict[str, List[ProcessedEmail]]:
        """
        E1: Multiple Sender Same Sender?
        
        Groups emails by sender to detect conflicts
        """
        logger.info("Checking for multiple emails from same sender...")
        
        sender_map: Dict[str, List[ProcessedEmail]] = {}
        
        for email in emails:
            sender = email.metadata.sender
            if sender not in sender_map:
                sender_map[sender] = []
            sender_map[sender].append(email)
        
        # Find senders with multiple emails
        conflicts = {
            sender: emails_list
            for sender, emails_list in sender_map.items()
            if len(emails_list) > 1
        }
        
        if conflicts:
            logger.warning(f"Found {len(conflicts)} sender(s) with multiple emails")
        else:
            logger.debug("No conflicts found")
        
        return conflicts
    
    def latest_email_overrides(self, emails: List[ProcessedEmail]) -> ProcessedEmail:
        """
        E2: Latest Email Overrides
        
        Returns the most recent email from a sender, marking others as superseded
        """
        if not emails:
            return None
        
        # Sort by date (most recent first)
        sorted_emails = sorted(emails, key=lambda e: e.metadata.date, reverse=True)
        
        latest = sorted_emails[0]
        superseded = sorted_emails[1:]
        
        # Mark older emails as superseded
        for email in superseded:
            email.processing_notes.append(
                f"Superseded by newer email from same sender: {latest.metadata.message_id}"
            )
            email.is_blocked = True
        
        logger.info(f"Latest email from sender: {latest.metadata.subject} ({latest.metadata.date})")
        logger.info(f"Marked {len(superseded)} older email(s) as superseded")
        
        return latest
    
    def resolve_conflicts(self, conflicts: Dict[str, List[ProcessedEmail]]) -> List[ProcessedEmail]:
        """Resolve all conflicts and return list of active emails"""
        active_emails = []
        
        for sender, email_list in conflicts.items():
            logger.info(f"Resolving conflict for sender: {sender}")
            latest = self.latest_email_overrides(email_list)
            if latest:
                active_emails.append(latest)
        
        return active_emails
