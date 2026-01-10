"""
Main Email Agent Orchestrator
Coordinates all components following the architecture diagram flow
"""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from config import Config
from models import (
    ProcessedEmail, ProcessingBatch, EmailMetadata,
    ProcessingStatus, EmailCategory
)

# Import all modules
from tools import GmailClient, PermissionChecker, SlackClient, NotionClient
from core import (
    SenderClassifier, IntentDetector, PriorityScorer,
    EmailCategorizer, SpamFilter
)
from drafting import ReplyDrafter, TonePreserver, FollowUpGenerator, ClarificationHandler
from edge_cases import ConflictResolver, LegalFinanceDetector, DNDHandler, ReplyAllHandler
from guardrails import PIIDetector, DomainChecker, ToneEnforcer
from output import QueueBuilder, MetricsGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailAgent:
    """
    Main Email Agent orchestrating the complete processing pipeline
    Following the architecture diagram flow
    """
    
    def __init__(self):
        logger.info("="*60)
        logger.info("Initializing Email Agent...")
        logger.info("="*60)
        
        # S0: Start - Initialize all components
        self.gmail_client = None
        self.permission_checker = PermissionChecker()
        
        # Core processing modules
        self.classifier = SenderClassifier()
        self.intent_detector = IntentDetector()
        self.priority_scorer = PriorityScorer()
        self.categorizer = EmailCategorizer()
        self.spam_filter = SpamFilter()
        
        # Drafting modules
        self.reply_drafter = ReplyDrafter()
        self.tone_preserver = TonePreserver()
        self.followup_generator = FollowUpGenerator()
        self.clarification_handler = ClarificationHandler()
        
        # Edge case handlers
        self.conflict_resolver = ConflictResolver()
        self.legal_detector = LegalFinanceDetector()
        self.dnd_handler = DNDHandler()
        self.reply_all_handler = ReplyAllHandler()
        
        # Guardrails
        self.pii_detector = PIIDetector()
        self.domain_checker = DomainChecker()
        self.tone_enforcer = ToneEnforcer()
        
        # Output generators
        self.queue_builder = QueueBuilder()
        self.metrics_generator = MetricsGenerator()
        
        # Optional integrations
        self.slack_client = None
        self.notion_client = None
        if Config.SLACK_ENABLED:
            try:
                self.slack_client = SlackClient()
                if self.slack_client.enabled:
                    logger.info("Slack integration enabled")
            except Exception as e:
                logger.warning(f"Slack integration failed: {e}")
        
        if Config.NOTION_ENABLED:
            try:
                self.notion_client = NotionClient()
                if self.notion_client.enabled:
                    logger.info("✓ Notion integration enabled")
            except Exception as e:
                logger.warning(f"Notion integration failed: {e}")
        
        # Operating context
        self.operating_context = {}
        
        logger.info("Email Agent initialized successfully")
    
    def run(self, user_command: str, user_scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution flow following the architecture diagram
        
        Args:
            user_command: Natural language command from user
            user_scope: Optional scope parameters (time range, filters, etc.)
        
        Returns:
            Final response queue with metrics
        """
        logger.info("="*60)
        logger.info(f"STARTING EMAIL AGENT")
        logger.info(f"Command: {user_command}")
        logger.info("="*60)
        
        # S1: User Command
        batch_id = str(uuid.uuid4())[:8]
        batch = ProcessingBatch(
            batch_id=batch_id,
            user_command=user_command,
            user_scope=user_scope or {}
        )
        
        # S2: User Scope Note
        logger.info(f"Batch ID: {batch_id}")
        logger.info(f"Scope: {user_scope}")
        
        try:
            # SECTION 1: Tool Permissions Check
            self._check_tool_permissions()
            
            # SECTION 2: Data Ingestion
            raw_emails = self._data_ingestion(user_scope)
            
            if not raw_emails:
                logger.warning("No emails found to process")
                return self._build_empty_response(batch)
            
            # Convert to ProcessedEmail objects
            emails = [self._create_processed_email(metadata) for metadata in raw_emails]
            batch.emails = emails
            
            logger.info(f"Processing {len(emails)} email(s)...")
            
            # SECTION 3: Core Classification Pipeline
            for email in emails:
                self._process_email_core_pipeline(email)
            
            # SECTION 4: Edge Case Handling (parallel with core)
            self._handle_edge_cases(batch)
            
            # SECTION 5: Drafting
            for email in batch.emails:
                if not email.is_blocked:
                    self._draft_replies(email)
            
            # SECTION 6: Guardrails (Security checks)
            for email in batch.emails:
                self._apply_guardrails(email)
            
            # SECTION 7: Final Output
            batch.completed_at = datetime.now()
            batch.total_processed = len(batch.emails)
            
            response = self._generate_final_output(batch)
            
            logger.info("="*60)
            logger.info("EMAIL AGENT COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in email agent: {e}", exc_info=True)
            batch.errors.append(str(e))
            return self._build_error_response(batch, str(e))
    
    def _check_tool_permissions(self):
        """T1-T6: Tool Scopes and Permissions Check"""
        logger.info("\n" + "="*60)
        logger.info("SECTION 1: Checking Tool Permissions")
        logger.info("="*60)
        
        # Initialize Gmail client
        self.gmail_client = GmailClient()
        
        # T1-T2: Check Required Tool Scopes
        has_permissions, missing_scopes = self.permission_checker.check_required_tool_scopes(
            self.gmail_client.service
        )
        
        if not has_permissions:
            # T3: Set Entry Note
            note = self.permission_checker.set_entry_note(missing_scopes)
            logger.warning(note)
            
            # T4: Notify Missing Tool Scopes
            notification = self.permission_checker.notify_missing_tool_scopes(missing_scopes)
            logger.warning(f"Missing scopes: {notification}")
        
        # T5: Create Missing Context
        self.operating_context = self.permission_checker.create_missing_context(
            self.permission_checker.available_scopes
        )
        
        logger.info(f"Operating mode: {self.operating_context['mode']}")
    
    def _data_ingestion(self, user_scope: Optional[Dict[str, Any]]) -> List[EmailMetadata]:
        """D1-D5: Data Ingestion Workflow"""
        logger.info("\n" + "="*60)
        logger.info("SECTION 2: Data Ingestion")
        logger.info("="*60)
        
        # Parse user scope
        query = user_scope.get('query', '') if user_scope else ''
        max_results = user_scope.get('max_results', Config.MAX_EMAILS_TO_PROCESS) if user_scope else Config.MAX_EMAILS_TO_PROCESS
        time_range = user_scope.get('time_range_days', 7) if user_scope else 7
        
        # D1: Fetch Emails
        messages = self.gmail_client.fetch_emails(
            query=query,
            max_results=max_results,
            time_range_days=time_range
        )
        
        # D2: Inbox Scan + D4: Metadata Extraction
        email_metadata_list = []
        for msg in messages:
            email_details = self.gmail_client.get_email_details(msg['id'])
            if email_details:
                metadata = self.gmail_client.extract_metadata(email_details)
                email_metadata_list.append(metadata)
        
        # D3: Thread Mapping
        message_ids = [msg['id'] for msg in messages]
        thread_map = self.gmail_client.get_threads(message_ids)
        logger.info(f"Mapped into {len(thread_map)} thread(s)")
        
        # D5: Start Mode Note
        logger.info("Data ingestion complete")
        
        return email_metadata_list
    
    def _create_processed_email(self, metadata: EmailMetadata) -> ProcessedEmail:
        """Create ProcessedEmail object from metadata"""
        return ProcessedEmail(
            metadata=metadata,
            status=ProcessingStatus.PENDING,
            received_at=metadata.date
        )
    
    def _process_email_core_pipeline(self, email: ProcessedEmail):
        """S1-S16: Core Classification Pipeline"""
        email.status = ProcessingStatus.PROCESSING
        
        # S1: Sender Classification
        email.classification = self.classifier.classify(email.metadata)
        # --- Explanation: classification notes ---
        if not hasattr(email, "processing_notes"):
            email.processing_notes = []

        # Append classifier notes if present
        if getattr(email.classification, "notes", None):
            email.processing_notes.append(f"Classification notes: {email.classification.notes}")

        # Append sender type / VIP
        try:
            email.processing_notes.append(
                f"Sender type: {email.classification.sender_type.value}, VIP: {bool(email.classification.is_vip)}"
            )
        except Exception:
            # defensive: some test objects may not have fields
            pass

        # S2: Keyword and Intent Detection
        email.intent = self.intent_detector.detect(email.metadata)
        # --- Explanation: intent notes ---
        if getattr(email, "intent", None):
            if getattr(email.intent, "primary_intent", None):
                email.processing_notes.append(f"Intent detected: {email.intent.primary_intent}")
            # detected keywords
            kws = getattr(email.intent, "keywords_detected", None)
            if kws:
                try:
                    email.processing_notes.append(f"Keywords: {', '.join(kws)}")
                except Exception:
                    email.processing_notes.append(f"Keywords: {kws}")
            # urgency keywords
            urgency_kws = getattr(email.intent, "urgency_keywords", None)
            if urgency_kws:
                try:
                    email.processing_notes.append(f"Urgency keywords: {', '.join(urgency_kws)}")
                except Exception:
                    email.processing_notes.append(f"Urgency keywords: {urgency_kws}")

        # S3: Priority Scoring Engine
        email.priority = self.priority_scorer.calculate_score(
            email.metadata,
            email.classification,
            email.intent
        )
        # --- Explanation: priority notes ---
        if getattr(email, "priority", None):
            try:
                score = email.priority.score
            except Exception:
                score = getattr(email.priority, "score", None) or 0
            level = getattr(email.priority, "priority_level", None)
            if level:
                level_name = level.name if hasattr(level, "name") else str(level)
            else:
                level_name = "UNKNOWN"
            email.processing_notes.append(f"Priority score: {score}/100 ({level_name})")
            if getattr(email.priority, "reasoning", None):
                email.processing_notes.append(f"Priority reasoning: {email.priority.reasoning}")

        # S4: High Priority Decision + S5: Map to Important / Mark as NotReq
        # (handled automatically by priority_scorer)
        
        # S6-S7: Categorization
        email.is_spam = self.spam_filter.is_spam(email.metadata, email.classification)
        email.category = self.categorizer.categorize(
            email.intent,
            email.priority,
            email.is_spam
        )
        # --- Explanation: category & spam notes ---
        try:
            email.processing_notes.append(f"Category assigned: {email.category.value}")
        except Exception:
            email.processing_notes.append(f"Category assigned: {email.category}")

        if email.is_spam:
            email.processing_notes.append("Marked as SPAM by spam filter")
            # email.is_blocked already set later; leave that logic unchanged

        # S8-S9: Spam Check
        if email.is_spam:
            self.spam_filter.mark_as_blocked(email.metadata.message_id)
            email.is_blocked = True
            email.status = ProcessingStatus.BLOCKED
            return
        
        # S11: Draft Reply Decision
        email.requires_reply = (
            email.intent.action_required or
            email.intent.question_detected or
            email.category in [EmailCategory.ACTION]
        )
        # --- Explanation: reply requirement ---
        if email.requires_reply:
            email.processing_notes.append("Marked as requiring a reply")
        else:
            email.processing_notes.append("No reply required")

    def _handle_edge_cases(self, batch: ProcessingBatch):
        """E1-E9: Edge Case Handling"""
        logger.info("\n" + "="*60)
        logger.info("SECTION 3: Edge Case Handling")
        logger.info("="*60)

        # E1-E2: Multiple emails from same sender (resolve + explain)
        conflicts = self.conflict_resolver.check_multiple_from_same_sender(batch.emails)
        if conflicts:
            active_emails = self.conflict_resolver.resolve_conflicts(conflicts)

            # Build a set of active message ids
            active_ids = {e.metadata.message_id for e in active_emails}

            # Mark emails not in active_ids as superseded and append notes
            for e in batch.emails:
                if e.metadata.message_id not in active_ids:
                    # do not change blocking / core logic; only add explanation
                    if not hasattr(e, "processing_notes"):
                        e.processing_notes = []
                    e.processing_notes.append("Superseded by a newer email from the same sender")

            # Rebuild batch.emails: preserve emails from senders that had no conflict, plus the chosen active emails
            non_conflict_emails = [e for e in batch.emails if e.metadata.sender not in conflicts]
            batch.emails = non_conflict_emails + active_emails
            logger.info(f"Resolved sender conflicts; active emails count: {len(batch.emails)}")

        
        # E3-E4: Legal/Finance Detection
        for email in batch.emails:
            if not email.is_blocked:
                is_critical = self.legal_detector.check_legal_finance_content_urgent(email)
                if is_critical:
                    self.legal_detector.block_auto_reply_and_escalate(email)
        
        # E5-E9: DND Mode and Tool Alerts
        can_send = self.operating_context.get('can_send', False)
        
        for email in batch.emails:
            if not email.is_blocked:
                # E5-E6: Tool Alert
                has_alert, alert_reason = self.dnd_handler.check_tool_alert(can_send)
                if has_alert:
                    self.dnd_handler.force_draft_only_and_warn(email, alert_reason)
                
                # E7-E9: DND Mode
                if self.dnd_handler.check_external_email_to_dnd(email):
                    dnd_decision = self.dnd_handler.handle_dnd_decision(email)
                    logger.info(f"DND decision: {dnd_decision}")
    
    def _draft_replies(self, email: ProcessedEmail):
        """S11-S15: Drafting Pipeline"""
        if not email.requires_reply or email.is_blocked:
            return
        
        # S12: Draft Reply (Gemini → template)
        draft = self.reply_drafter.draft_reply(
            email.metadata,
            email.intent
        )

        if not draft:
            return

        email.draft_reply = draft
        
        # 🔹 NEW: Check if clarification is needed
        if self.clarification_handler.needs_clarification(email):
            email.needs_clarification = True
            email.clarification_request = self.clarification_handler.generate_clarification_request(email)
            logger.warning(f"⚠️ Clarification needed for: {email.metadata.subject}")
            
            # Send clarification request via Slack if enabled
            if self.slack_client and self.slack_client.enabled:
                self.slack_client.send_clarification_request(
                    subject=email.metadata.subject,
                    questions=email.clarification_request.questions,
                    message_id=email.metadata.message_id
                )
            
            # Mark as requiring approval
            draft.requires_approval = True
            email.status = ProcessingStatus.APPROVAL_REQUIRED

        # 🔹 SAVE DRAFT TO GMAIL
        try:
            recipients = (
                draft.recipients
                if isinstance(draft.recipients, list)
                else [draft.recipients]
            )

            draft_id = self.gmail_client.create_draft(
                to=recipients,
                subject=draft.subject,
                body=draft.body,
                cc=draft.cc if hasattr(draft, "cc") else None
            )

            if draft_id:
                draft.draft_id = draft_id
                logger.info(f"✓ Draft saved to Gmail (draft_id={draft_id})")
            else:
                logger.warning("Draft generated but Gmail returned no draft id")

        except Exception as e:
            logger.error(f"Failed to save Gmail draft: {e}")

        # S14: Tone and Timing Check
        should_delay = self.tone_preserver.preserves_tone_or_reply_after_hour(draft)

        # S15: Follow-ups (only if delayed)
        if should_delay:
            email.follow_ups = self.followup_generator.generate_follow_ups(
                email.metadata,
                email.intent
            )

    
    def _apply_guardrails(self, email: ProcessedEmail):
        """G1-G7: Guardrails and Security"""
        logger.debug(f"Applying guardrails to: {email.metadata.subject}")
        
        # G1: PII Detection
        has_pii, pii_types = self.pii_detector.detect_pii_and_confidential(email)
        # --- Explanation: PII detection notes ---
        if has_pii:
            email.has_pii = True
            if not hasattr(email, "processing_notes"):
                email.processing_notes = []
            if pii_types:
                email.processing_notes.append(f"PII detected: {', '.join(pii_types)}")
            else:
                email.processing_notes.append("PII detected (types not identified)")

        # G2: Domain Restriction Check
        domain_approved = self.domain_checker.check_domain_restrictions(email)
        # --- Explanation: domain restriction notes ---
        if not domain_approved:
            if not hasattr(email, "processing_notes"):
                email.processing_notes = []
            email.processing_notes.append("Domain restriction: external domain not approved for automatic action")

        # G3: Safe Tone Enforcement
        if email.draft_reply:
            tone_approved, tone_issues = self.tone_enforcer.enforce_safe_tone(email)
        else:
            tone_approved = True
        # --- Explanation: tone enforcement notes ---
        if not tone_approved:
            if not hasattr(email, "processing_notes"):
                email.processing_notes = []
            if tone_issues:
                email.processing_notes.append(f"Tone issues found: {', '.join(tone_issues)}")
            else:
                email.processing_notes.append("Tone enforcement flagged the draft")
        
        # 🔹 NEW: Reply-All Risk Detection
        if email.draft_reply:
            email = self.reply_all_handler.block_if_risky(email)
            
        # G4: External Email or High Risk?
        is_external = self.domain_checker.is_external_email(email)
        has_security_flags = len(email.security_flags) > 0
        
        if is_external or has_security_flags:
            # G5: Approval Required
            email.status = ProcessingStatus.APPROVAL_REQUIRED
            if email.draft_reply:
                email.draft_reply.requires_approval = True
            logger.info(f"⚠️ Approval required for: {email.metadata.subject}")
            email.processing_notes.append("Approval required due to external sender or high-risk security flags")
        else:
            # G6: Draft Marked Ready
            email.status = ProcessingStatus.DRAFT_READY
            if email.draft_reply:
                email.draft_reply.requires_approval = False  # Can auto-send if configured
        
        # G7: Guardrail Rules Note (logged)
        logger.debug("Guardrails applied successfully")
    
    def _send_notifications(self, batch: ProcessingBatch, queue: Dict[str, Any]):
        """Send Slack notifications for urgent items, VIPs, and escalations"""
        if not self.slack_client or not self.slack_client.enabled:
            return
        
        logger.info("Sending Slack notifications...")
        
        # Send urgent alerts
        for email in batch.emails:
            if email.priority and email.priority.score >= 90:
                self.slack_client.send_urgent_alert(
                    subject=email.metadata.subject,
                    sender=email.metadata.sender,
                    priority_score=email.priority.score,
                    message_id=email.metadata.message_id,
                    reason=email.priority.reasoning
                )
            
            # Send VIP notifications
            if email.classification and email.classification.is_vip:
                self.slack_client.send_vip_notification(
                    sender=email.metadata.sender,
                    subject=email.metadata.subject,
                    message_id=email.metadata.message_id
                )
            
            # Send escalations for legal/finance
            if email.category.value in ['legal', 'finance'] and email.priority and email.priority.score >= 70:
                for flag in email.security_flags:
                    if flag.flag_type in ['legal_content', 'finance_content']:
                        self.slack_client.send_escalation(
                            subject=email.metadata.subject,
                            category=email.category.value,
                            reason=flag.description,
                            message_id=email.metadata.message_id,
                            severity=flag.severity
                        )
        
        # Send batch summary
        self.slack_client.send_batch_summary(
            total_processed=queue["summary"]["total_processed"],
            high_priority=queue["summary"]["high_priority"],
            drafts_created=queue["summary"]["drafts_created"],
            blocked=queue["summary"]["blocked"]
        )
    
    def _log_to_notion(self, batch: ProcessingBatch, metrics: Dict[str, Any]):
        """Log processed emails and batch summary to Notion"""
        if not self.notion_client or not self.notion_client.enabled:
            return
        
        logger.info("Logging to Notion...")
        
        # Log high-priority emails
        for email in batch.emails:
            if email.priority and email.priority.score >= 80:
                email_data = {
                    "subject": email.metadata.subject,
                    "sender": email.metadata.sender,
                    "date": email.metadata.date.isoformat(),
                    "priority_score": email.priority.score,
                    "category": email.category.value,
                    "action_taken": "Draft created" if email.draft_reply else "No action",
                    "draft_created": email.draft_reply is not None,
                    "notes": "\n".join(email.processing_notes) if email.processing_notes else ""
                }
                self.notion_client.log_email_summary(email_data)
            
            # Log escalations
            if email.category.value in ['legal', 'finance']:
                for flag in email.security_flags:
                    if flag.flag_type in ['legal_content', 'finance_content']:
                        self.notion_client.log_escalation(
                            subject=email.metadata.subject,
                            category=email.category.value,
                            reason=flag.description,
                            severity=flag.severity,
                            details=flag.details
                        )
        
        # Log batch summary
        batch_data = {
            "batch_id": batch.batch_id,
            "total_processed": batch.total_processed,
            "high_priority": metrics.get("high_priority", 0),
            "drafts_created": metrics.get("drafts_created", 0),
            "blocked": metrics.get("blocked_items", 0),
            "time_saved_minutes": metrics.get("time_saved_minutes", 0)
        }
        self.notion_client.log_batch_summary(batch_data)
    
    def _generate_final_output(self, batch: ProcessingBatch) -> Dict[str, Any]:
        """F1-F2: Final Output Generation"""
        logger.info("\n" + "="*60)
        logger.info("SECTION 4: Generating Final Output")
        logger.info("="*60)
        
        # Collect all clarification requests
        for email in batch.emails:
            if email.needs_clarification and email.clarification_request:
                batch.clarifications.append(email.clarification_request)
        
        # F1: Build Final Response Queue
        queue = self.queue_builder.build_final_queue(batch)
        
        # F2: Generate Metrics Panel
        metrics = self.metrics_generator.generate_metrics(batch)
        metrics_display = self.metrics_generator.format_metrics_display(metrics)
        
        print("\n" + metrics_display)
        
        print("\nTOP 10 IMPORTANT EMAILS (with reasons):")
        print(json.dumps(queue.get("top_10_emails", []), indent=2, default=str))
        
        # 🔹 NEW: Send notifications and log to integrations
        self._send_notifications(batch, queue)
        self._log_to_notion(batch, metrics)

        # Combine into final response
        response = {
            "queue": queue,
            "metrics": metrics,
            "clarifications": [
                {
                    "email_id": c.email_id,
                    "subject": c.subject,
                    "questions": c.questions,
                    "reasons": [r.value for r in c.reasons]
                }
                for c in batch.clarifications
            ],
            "batch_info": {
                "batch_id": batch.batch_id,
                "started_at": batch.started_at.isoformat(),
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
                "command": batch.user_command
            }
        }
        
        return response
    
    def _build_empty_response(self, batch: ProcessingBatch) -> Dict[str, Any]:
        """Build response when no emails found"""
        return {
            "queue": {
                "batch_id": batch.batch_id,
                "summary": {"total_processed": 0},
                "message": "No emails found matching criteria"
            },
            "metrics": None
        }
    
    def _build_error_response(self, batch: ProcessingBatch, error: str) -> Dict[str, Any]:
        """Build error response"""
        return {
            "error": error,
            "batch_id": batch.batch_id,
            "errors": batch.errors
        }


# Main entry point
def main():
    """Main entry point for Email Agent"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║                EMAIL AGENT v1.0                       ║
    ║                                                       ║
    ║         AI-Powered Email Management System            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Validate configuration
    missing = Config.validate()
    if missing:
        logger.error(f"❌ Missing configuration: {', '.join(missing)}")
        logger.error("Please update your .env file with required values")
        return
    
    # Create agent
    agent = EmailAgent()
    
    # Example user command
    user_command = "Handle my inbox from today. Show only urgent items. Draft replies for approval and create follow-ups."
    user_scope = {
        'time_range_days': 1,
        'max_results': 50
    }
    
    # Run agent
    result = agent.run(user_command, user_scope)
    
    # Display results
    if "error" in result:
        logger.error(f"❌ Agent failed: {result['error']}")
    else:
        logger.info("\n✓ Processing complete!")
        logger.info(f"See batch {result['batch_info']['batch_id']} for results")


if __name__ == "__main__":
    main()
