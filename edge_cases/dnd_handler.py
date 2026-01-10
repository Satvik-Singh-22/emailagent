"""
E5-E9: DND (Do Not Disturb) mode handler
"""
import logging
from typing import Tuple
from config import Config
from models import ProcessedEmail, SecurityFlag

logger = logging.getLogger(__name__)


class DNDHandler:
    """Handles Do Not Disturb mode and external email filtering"""
    
    def __init__(self):
        self.dnd_mode = Config.DND_MODE
        self.auto_responder = Config.AUTO_RESPONDER
        self.allowed_domains = Config.ALLOWED_DOMAINS
    
    def check_tool_alert(self, can_send: bool) -> Tuple[bool, str]:
        """
        E5: Tool Alert?
        
        Checks if tool capabilities are missing
        """
        if not can_send:
            logger.warning("⚠️ TOOL ALERT: Send capability missing")
            return True, "Gmail send permission not granted"
        
        return False, ""
    
    def force_draft_only_and_warn(self, email: ProcessedEmail, reason: str) -> ProcessedEmail:
        """
        E6: Force Draft Only and Warn User
        
        Forces draft-only mode and adds warning
        """
        logger.warning(f"Forcing draft-only mode: {reason}")
        
        email.requires_reply = True
        
        if email.draft_reply:
            email.draft_reply.requires_approval = True
        
        flag = SecurityFlag(
            flag_type="tool_limitation",
            severity="medium",
            description=f"Draft-only mode enforced: {reason}",
            details={"reason": reason},
            blocks_sending=True
        )
        
        email.security_flags.append(flag)
        email.processing_notes.append(f"⚠️ {reason} - Draft only mode")
        
        return email
    
    def check_external_email_to_dnd(self, email: ProcessedEmail) -> bool:
        """
        E7: External Email to DND?
        
        Checks if email is external and user is in DND mode
        """
        if not self.dnd_mode:
            return False
        
        # Check if email is from external domain
        sender_domain = email.classification.sender_domain if email.classification else ""
        is_external = sender_domain not in self.allowed_domains and not email.classification.is_internal
        
        if is_external:
            logger.warning(f"External email detected while in DND mode: {email.metadata.sender}")
            return True
        
        return False
    
    def handle_dnd_decision(self, email: ProcessedEmail) -> str:
        """
        E8-E9: Draft To Blocked Or send Without DND? + External email Send Without DND?
        
        Determines how to handle email during DND mode
        
        Returns: 'draft_allowed', 'sending_blocked', or 'show_warning'
        """
        logger.info("Evaluating DND policy for email...")
        
        # Check if VIP sender (VIPs can override DND)
        is_vip = email.classification and email.classification.is_vip
        
        # Check if truly urgent
        is_urgent = email.priority and email.priority.score >= 80
        
        # Decision logic
        if is_vip and is_urgent:
            logger.info("VIP + Urgent: Draft allowed with warning")
            email.processing_notes.append("⚠️ DND MODE: VIP urgent email - draft created")
            return "draft_allowed"
        
        elif is_vip:
            logger.info("VIP: Show warning but create draft")
            email.processing_notes.append("⚠️ DND MODE: VIP email - review when available")
            return "show_warning"
        
        elif is_urgent:
            logger.info("Urgent: Show warning")
            email.processing_notes.append("⚠️ DND MODE: Urgent email - may need attention")
            return "show_warning"
        
        else:
            logger.info("Non-urgent external: Sending blocked")
            email.is_blocked = True
            email.requires_reply = False
            email.draft_reply = None
            
            if self.auto_responder:
                email.processing_notes.append(
                    "🚫 DND MODE: Auto-responder sent. Email queued for later review."
                )
            else:
                email.processing_notes.append(
                    "🚫 DND MODE: Email blocked. Will be reviewed after DND mode ends."
                )
            
            return "sending_blocked"
    
    def set_dnd_mode(self, enabled: bool):
        """Enable or disable DND mode"""
        self.dnd_mode = enabled
        logger.info(f"DND mode {'enabled' if enabled else 'disabled'}")
    
    def set_auto_responder(self, enabled: bool):
        """Enable or disable auto-responder"""
        self.auto_responder = enabled
        logger.info(f"Auto-responder {'enabled' if enabled else 'disabled'}")
