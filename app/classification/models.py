from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class SenderType(Enum):
    VIP = "vip"
    TEAM = "team"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    SPAM = "spam"
    UNKNOWN = "unknown"

class PriorityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_REQUIRED = "not_required"

@dataclass
class EmailMetadata:
    sender: str
    subject: str
    body: str
    date: datetime
    recipients: List[str] = field(default_factory=list)
    has_attachments: bool = False

@dataclass
class ClassificationResult:
    sender_type: SenderType
    sender_email: str
    sender_domain: str
    is_vip: bool
    is_internal: bool
    confidence: float
    notes: str

@dataclass
class IntentDetection:
    intents: List[str]  # e.g., 'legal', 'finance', 'urgent'
    urgency_keywords: List[str]
    action_required: bool
    question_detected: bool

@dataclass
class PriorityScore:
    score: int
    priority_level: PriorityLevel
    factors: dict
    reasoning: str
