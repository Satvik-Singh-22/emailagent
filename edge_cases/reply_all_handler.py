"""
Reply-All Risk Detection
Detects and prevents risky reply-all scenarios with large external lists
"""
import logging
from typing import List, Tuple, Set
from config import Config
from models import ProcessedEmail, SecurityFlag

logger = logging.getLogger(__name__)


class ReplyAllHandler:
    """Handles detection and prevention of reply-all risks"""
    
    def __init__(self):
        self.max_recipients_warning = 5  # Warn if replying to more than 5
        self.max_external_recipients = 3  # Block if more than 3 external
        self.allowed_domains = Config.ALLOWED_DOMAINS
    
    def check_reply_all_risk(self, email: ProcessedEmail) -> Tuple[bool, str]:
        """
        Check if reply has reply-all risk
        
        Returns: (has_risk, risk_description)
        """
        logger.debug(f"Checking reply-all risk for: {email.metadata.subject}")
        
        if not email.draft_reply:
            return False, ""
        
        # Get all recipients from draft
        all_recipients = (
            email.draft_reply.recipients + 
            email.draft_reply.cc
        )
        
        if not all_recipients:
            return False, ""
        
        # Check 1: Large recipient list
        if len(all_recipients) > self.max_recipients_warning:
            risk = f"Large recipient list detected: {len(all_recipients)} recipients"
            logger.warning(risk)
            return True, risk
        
        # Check 2: Multiple external recipients
        external_recipients = self._get_external_recipients(all_recipients)
        if len(external_recipients) > self.max_external_recipients:
            risk = f"Too many external recipients: {len(external_recipients)} external addresses"
            logger.warning(risk)
            return True, risk
        
        # Check 3: Mix of internal and external
        if self._has_mixed_internal_external(all_recipients):
            external_count = len(external_recipients)
            if external_count > 0:
                risk = f"Mixed internal/external recipients with {external_count} external addresses"
                logger.warning(risk)
                return True, risk
        
        # Check 4: Original email was sent to large list
        original_recipients = (
            email.metadata.recipients + 
            email.metadata.cc
        )
        if len(original_recipients) > 10:
            risk = f"Original email had large recipient list ({len(original_recipients)}). Verify reply-all is intended."
            logger.warning(risk)
            return True, risk
        
        return False, ""
    
    def analyze_reply_all_risk(self, email: ProcessedEmail) -> dict:
        """
        Detailed analysis of reply-all risks
        
        Returns: Dictionary with risk analysis
        """
        logger.info(f"Analyzing reply-all risk for: {email.metadata.subject}")
        
        if not email.draft_reply:
            return {
                "has_risk": False,
                "risk_level": "none",
                "details": {}
            }
        
        all_recipients = (
            email.draft_reply.recipients + 
            email.draft_reply.cc
        )
        
        external_recipients = self._get_external_recipients(all_recipients)
        internal_recipients = self._get_internal_recipients(all_recipients)
        
        # Calculate risk level
        risk_level = "none"
        risk_factors = []
        
        # Factor 1: Total recipient count
        if len(all_recipients) > 10:
            risk_level = "high"
            risk_factors.append(f"Very large recipient list: {len(all_recipients)}")
        elif len(all_recipients) > self.max_recipients_warning:
            risk_level = "medium" if risk_level == "none" else risk_level
            risk_factors.append(f"Large recipient list: {len(all_recipients)}")
        
        # Factor 2: External recipients
        if len(external_recipients) > self.max_external_recipients:
            risk_level = "high"
            risk_factors.append(f"Many external recipients: {len(external_recipients)}")
        elif len(external_recipients) > 0:
            risk_level = "medium" if risk_level == "none" else risk_level
            risk_factors.append(f"External recipients present: {len(external_recipients)}")
        
        # Factor 3: Mixed audiences
        if len(internal_recipients) > 0 and len(external_recipients) > 0:
            risk_level = "high" if len(external_recipients) > 2 else "medium"
            risk_factors.append("Mixed internal and external recipients")
        
        # Factor 4: Sensitive categories
        if email.category.value in ['legal', 'finance']:
            if len(external_recipients) > 0:
                risk_level = "high"
                risk_factors.append(f"Sensitive category ({email.category.value}) with external recipients")
        
        # Factor 5: Contains PII
        if email.security_flags:
            for flag in email.security_flags:
                if flag.flag_type == "pii_detected":
                    if len(external_recipients) > 0:
                        risk_level = "critical"
                        risk_factors.append("PII detected with external recipients")
        
        has_risk = risk_level != "none"
        
        analysis = {
            "has_risk": has_risk,
            "risk_level": risk_level,
            "details": {
                "total_recipients": len(all_recipients),
                "external_count": len(external_recipients),
                "internal_count": len(internal_recipients),
                "external_addresses": list(external_recipients)[:5],  # First 5 only
                "risk_factors": risk_factors
            },
            "recommendation": self._get_recommendation(risk_level, len(external_recipients))
        }
        
        return analysis
    
    def block_if_risky(self, email: ProcessedEmail) -> ProcessedEmail:
        """
        Block email draft if reply-all risk is too high
        
        Returns: Updated email with blocking flag if necessary
        """
        analysis = self.analyze_reply_all_risk(email)
        
        if analysis["risk_level"] in ["high", "critical"]:
            logger.warning(f"Blocking email due to reply-all risk: {analysis['risk_level']}")
            
            # Add security flag
            flag = SecurityFlag(
                flag_type="reply_all_risk",
                severity=analysis["risk_level"],
                description="Reply-all risk detected",
                details=analysis["details"],
                blocks_sending=True
            )
            
            email.security_flags.append(flag)
            email.is_blocked = True
            
            # Mark draft as requiring approval
            if email.draft_reply:
                email.draft_reply.requires_approval = True
            
            logger.info(f"Email blocked: {', '.join(analysis['details']['risk_factors'])}")
        
        elif analysis["risk_level"] == "medium":
            # Don't block but require approval
            logger.warning(f"Reply-all warning: {analysis['risk_level']}")
            
            flag = SecurityFlag(
                flag_type="reply_all_warning",
                severity="medium",
                description="Reply-all warning - approval recommended",
                details=analysis["details"],
                blocks_sending=False
            )
            
            email.security_flags.append(flag)
            
            if email.draft_reply:
                email.draft_reply.requires_approval = True
        
        return email
    
    def _get_external_recipients(self, recipients: List[str]) -> Set[str]:
        """Get list of external email addresses"""
        external = set()
        
        for recipient in recipients:
            domain = self._extract_domain(recipient)
            if not self._is_internal_domain(domain):
                external.add(recipient)
        
        return external
    
    def _get_internal_recipients(self, recipients: List[str]) -> Set[str]:
        """Get list of internal email addresses"""
        internal = set()
        
        for recipient in recipients:
            domain = self._extract_domain(recipient)
            if self._is_internal_domain(domain):
                internal.add(recipient)
        
        return internal
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address"""
        if '@' in email:
            return email.split('@')[1].lower()
        return ""
    
    def _is_internal_domain(self, domain: str) -> bool:
        """Check if domain is internal"""
        if not domain:
            return False
        
        # Check against allowed domains
        if domain in self.allowed_domains:
            return True
        
        # Add your company domain logic here
        # For now, we'll consider allowed_domains as internal
        return False
    
    def _has_mixed_internal_external(self, recipients: List[str]) -> bool:
        """Check if recipients include both internal and external"""
        has_internal = False
        has_external = False
        
        for recipient in recipients:
            domain = self._extract_domain(recipient)
            if self._is_internal_domain(domain):
                has_internal = True
            else:
                has_external = True
            
            if has_internal and has_external:
                return True
        
        return False
    
    def _get_recommendation(self, risk_level: str, external_count: int) -> str:
        """Get recommendation based on risk level"""
        if risk_level == "critical":
            return "BLOCK: Critical risk detected. Do not send without explicit approval."
        elif risk_level == "high":
            return "WARNING: High risk. Verify all recipients are intended before sending."
        elif risk_level == "medium":
            return f"CAUTION: {external_count} external recipient(s). Confirm reply-all is necessary."
        else:
            return "OK: No significant reply-all risks detected."
