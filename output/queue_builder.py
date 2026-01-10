"""
F1: Final Response Queue Builder
"""
import logging
from typing import List, Dict, Any
from models import ProcessedEmail, ProcessingBatch, PriorityLevel

logger = logging.getLogger(__name__)


class QueueBuilder:
    """Builds final response queue for user"""
    
    def build_final_queue(self, batch: ProcessingBatch) -> Dict[str, Any]:
        """
        F1: Final Response Queue to User
        
        Compiles all processed emails into organized output
        """
        logger.info("Building final response queue...")
        
        # Separate emails by category
        high_priority = [e for e in batch.emails 
                        if e.priority and e.priority.priority_level == PriorityLevel.HIGH 
                        and not e.is_blocked]
        
        medium_priority = [e for e in batch.emails 
                          if e.priority and e.priority.priority_level == PriorityLevel.MEDIUM
                          and not e.is_blocked]
        
        low_priority = [e for e in batch.emails 
                       if e.priority and e.priority.priority_level == PriorityLevel.LOW
                       and not e.is_blocked]
        
        drafts_ready = [e for e in batch.emails if e.draft_reply and not e.is_blocked]
        
        needs_approval = [e for e in batch.emails 
                         if e.draft_reply and e.draft_reply.requires_approval]
        
        blocked = [e for e in batch.emails if e.is_blocked]
        
        needs_clarification = [e for e in batch.emails if e.needs_clarification]
        
        follow_ups = []
        for email in batch.emails:
            follow_ups.extend(email.follow_ups)
        # Build top 10 by priority score across all non-blocked emails
        sortable_emails = [e for e in batch.emails if not e.is_blocked and getattr(e, "priority", None)]
        sorted_emails = sorted(sortable_emails, key=lambda e: getattr(e.priority, "score", 0), reverse=True)
        top_10 = sorted_emails[:10]

        # Build response queue
        queue = {
            "batch_id": batch.batch_id,
            "summary": {
                "total_processed": len(batch.emails),
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "drafts_created": len(drafts_ready),
                "needs_approval": len(needs_approval),
                "blocked": len(blocked),
                "follow_ups": len(follow_ups),
                "needs_clarification": len(needs_clarification)
            },
            "top_10_emails": [self._email_to_dict(e) for e in top_10],
            "draft_replies": [self._draft_to_dict(e) for e in drafts_ready[:10]],
            "follow_ups": [self._followup_to_dict(f) for f in follow_ups],
            "blocked_items": [self._blocked_to_dict(e) for e in blocked],
            "clarifications": [self._clarification_to_dict(e) for e in needs_clarification],
            "warnings": self._collect_warnings(batch.emails),
            "errors": batch.errors
        }
        
        logger.info(f"✓ Queue built with {len(high_priority)} high-priority items")
        return queue
    
    def _email_to_dict(self, email: ProcessedEmail) -> Dict[str, Any]:
        """Convert email to dictionary format"""
        return {
            "message_id": email.metadata.message_id,
            "thread_id": email.metadata.thread_id,
            "subject": email.metadata.subject,
            "from": email.metadata.sender,
            "date": email.metadata.date.isoformat(),
            "priority_score": email.priority.score if email.priority else 0,
            "priority_reasoning": email.priority.reasoning if email.priority else "",
            "category": email.category.value,
            "has_draft": email.draft_reply is not None,
            "requires_action": email.requires_reply,
            "snippet": email.metadata.snippet,
            "reasons": getattr(email, "processing_notes", [])
        }

    
    def _draft_to_dict(self, email: ProcessedEmail) -> Dict[str, Any]:
        """Convert draft to dictionary format"""
        if not email.draft_reply:
            return {}
        
        return {
            "email_id": email.metadata.message_id,
            "original_subject": email.metadata.subject,
            "reply_subject": email.draft_reply.subject,
            "reply_body": email.draft_reply.body,
            "to": email.draft_reply.recipients,
            "cc": email.draft_reply.cc,
            "requires_approval": email.draft_reply.requires_approval,
            "security_flags": [f.flag_type for f in email.security_flags]
        }
    
    def _followup_to_dict(self, followup) -> Dict[str, Any]:
        """Convert follow-up to dictionary format"""
        return {
            "email_id": followup.email_id,
            "subject": followup.subject,
            "suggested_date": followup.suggested_date.isoformat(),
            "reason": followup.reason,
            "draft_message": followup.draft_message
        }
    
    def _blocked_to_dict(self, email: ProcessedEmail) -> Dict[str, Any]:
        """Convert blocked email to dictionary format"""
        return {
            "message_id": email.metadata.message_id,
            "subject": email.metadata.subject,
            "from": email.metadata.sender,
            "reason": " | ".join(email.processing_notes),
            "security_flags": [
                {
                    "type": f.flag_type,
                    "severity": f.severity,
                    "description": f.description
                }
                for f in email.security_flags
            ]
        }
    
    def _clarification_to_dict(self, email: ProcessedEmail) -> Dict[str, Any]:
        """Convert clarification request to dictionary format"""
        if not email.clarification_request:
            return {}
        
        return {
            "message_id": email.metadata.message_id,
            "subject": email.metadata.subject,
            "from": email.metadata.sender,
            "questions": email.clarification_request.questions,
            "reasons": [r.value for r in email.clarification_request.reasons],
            "context": email.clarification_request.context
        }
    
    def _collect_warnings(self, emails: List[ProcessedEmail]) -> List[str]:
        """Collect all warnings from processing"""
        warnings = []
        
        for email in emails:
            for flag in email.security_flags:
                if flag.severity in ['high', 'critical']:
                    warnings.append(f"{email.metadata.subject}: {flag.description}")
        
        return warnings
