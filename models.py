"""
Data models for Email Agent
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailCategory(Enum):
    """Email categorization types"""
    ACTION = "action"
    FYI = "fyi"
    WAITING = "waiting"
    SPAM = "spam"
    LEGAL = "legal"
    FINANCE = "finance"
    UNKNOWN = "unknown"


class PriorityLevel(Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_REQUIRED = "not_required"


class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    DRAFT_READY = "draft_ready"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"
    SENT = "sent"
    FAILED = "failed"


class SenderType(Enum):
    """Sender classification"""
    VIP = "vip"
    TEAM = "team"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    UNKNOWN = "unknown"
    SPAM = "spam"


class ClarificationReason(Enum):
    """Reasons for requesting clarification"""
    AMBIGUOUS_RECIPIENTS = "ambiguous_recipients"
    UNCLEAR_INTENT = "unclear_intent"
    MISSING_INFORMATION = "missing_information"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    LOW_CONFIDENCE = "low_confidence"


@dataclass
class EmailMetadata:
    """Extracted email metadata"""
    message_id: str
    thread_id: str
    subject: str
    sender: str
    sender_name: Optional[str]
    recipients: List[str]
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    date: datetime = field(default_factory=datetime.now)
    has_attachments: bool = False
    attachment_count: int = 0
    labels: List[str] = field(default_factory=list)
    snippet: str = ""
    body_text: str = ""
    body_html: str = ""


@dataclass
class ClassificationResult:
    """Results from sender classification"""
    sender_type: SenderType
    sender_email: str
    sender_domain: str
    is_vip: bool = False
    is_internal: bool = False
    confidence: float = 0.0
    notes: str = ""


@dataclass
class IntentDetection:
    """Intent detection results"""
    primary_intent: str
    intents: List[str] = field(default_factory=list)
    keywords_detected: List[str] = field(default_factory=list)
    urgency_keywords: List[str] = field(default_factory=list)
    action_required: bool = False
    question_detected: bool = False
    confidence: float = 0.0


@dataclass
class PriorityScore:
    """Priority scoring results"""
    score: int  # 0-100
    priority_level: PriorityLevel
    factors: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class DraftReply:
    """Draft email reply"""
    draft_id: Optional[str] = None
    subject: str = ""
    body: str = ""
    recipients: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    tone: str = "professional"
    preserves_tone: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    requires_approval: bool = True


@dataclass
class FollowUp:
    """Follow-up reminder"""
    email_id: str
    subject: str
    suggested_date: datetime
    reason: str
    draft_message: str = ""


@dataclass
class SecurityFlag:
    """Security/guardrail flag"""
    flag_type: str
    severity: str  # low, medium, high, critical
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    blocks_sending: bool = False


@dataclass
class ClarificationRequest:
    """Request for user clarification"""
    email_id: str
    subject: str
    reasons: List['ClarificationReason'] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class ProcessedEmail:
    """Complete processed email with all analysis"""
    # Original metadata
    metadata: EmailMetadata
    
    # Classification results
    classification: Optional[ClassificationResult] = None
    intent: Optional[IntentDetection] = None
    priority: Optional[PriorityScore] = None
    category: EmailCategory = EmailCategory.UNKNOWN
    
    # Processing decisions
    is_spam: bool = False
    requires_reply: bool = False
    is_blocked: bool = False
    
    # Generated content
    draft_reply: Optional[DraftReply] = None
    follow_ups: List[FollowUp] = field(default_factory=list)
    
    # Clarification
    needs_clarification: bool = False
    clarification_request: Optional[ClarificationRequest] = None
    
    # Security
    security_flags: List[SecurityFlag] = field(default_factory=list)
    has_pii: bool = False
    domain_approved: bool = True
    tone_approved: bool = True
    
    # Status
    status: ProcessingStatus = ProcessingStatus.PENDING
    processing_notes: List[str] = field(default_factory=list)
    
    # Timestamps
    received_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


@dataclass
class ProcessingBatch:
    """Batch of emails being processed"""
    batch_id: str
    user_command: str
    user_scope: Dict[str, Any] = field(default_factory=dict)
    emails: List[ProcessedEmail] = field(default_factory=list)
    clarifications: List[ClarificationRequest] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_processed: int = 0
    high_priority_count: int = 0
    drafts_created: int = 0
    blocked_count: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class MetricsReport:
    """Final metrics report"""
    total_emails: int
    high_priority: int
    medium_priority: int
    low_priority: int
    drafts_created: int
    follow_ups_scheduled: int
    blocked_items: int
    categories: Dict[str, int]
    time_saved_minutes: int
    vip_emails: int
    approval_required_count: int
