"""
Configuration management for Email Agent (Gmail + Gemini only)
"""
import os
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Central configuration for Email Agent (Gmail + Gemini)"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    TOKENS_DIR = BASE_DIR / "tokens"
    
    # Gmail API (required)
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
    GMAIL_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8080")
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    # Gemini (Google GenAI) - required for drafting & follow-ups
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    # default model; can be overridden in .env
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # quick toggle to disable Gemini and use templates only
    GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "true").lower() in ("1","true","yes")
    
    # Agent settings
    PRIORITY_THRESHOLD = int(os.getenv("PRIORITY_THRESHOLD", "70"))
    MAX_EMAILS_TO_PROCESS = int(os.getenv("MAX_EMAILS_TO_PROCESS", "100"))
    
    # Domain configuration (comma-separated lists in .env)
    VIP_DOMAINS: Set[str] = set(filter(None, map(str.strip, os.getenv("VIP_DOMAINS", "").split(","))))
    ALLOWED_DOMAINS: Set[str] = set(filter(None, map(str.strip, os.getenv("ALLOWED_DOMAINS", "").split(","))))
    BLOCKED_DOMAINS: Set[str] = set(filter(None, map(str.strip, os.getenv("BLOCKED_DOMAINS", "").split(","))))
    
    # DND Mode
    DND_MODE = os.getenv("DND_MODE", "false").lower() == "true"
    AUTO_RESPONDER = os.getenv("AUTO_RESPONDER", "true").lower() == "true"
    
    # Security settings
    REQUIRE_APPROVAL_FOR_EXTERNAL = os.getenv("REQUIRE_APPROVAL_FOR_EXTERNAL", "true").lower() == "true"
    ENABLE_PII_DETECTION = os.getenv("ENABLE_PII_DETECTION", "true").lower() == "true"
    ENABLE_DOMAIN_RESTRICTIONS = os.getenv("ENABLE_DOMAIN_RESTRICTIONS", "true").lower() == "true"
    ENABLE_TONE_ENFORCEMENT = os.getenv("ENABLE_TONE_ENFORCEMENT", "true").lower() == "true"
    
    # Slack Integration (optional)
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#email-agent")
    SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"
    
    # Notion Integration (optional)
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
    NOTION_ENABLED = os.getenv("NOTION_ENABLED", "false").lower() == "true"
    
    # Clarification & Reply-All Settings
    MIN_INTENT_CONFIDENCE = float(os.getenv("MIN_INTENT_CONFIDENCE", "0.6"))
    MAX_RECIPIENTS_WARNING = int(os.getenv("MAX_RECIPIENTS_WARNING", "5"))
    MAX_EXTERNAL_RECIPIENTS = int(os.getenv("MAX_EXTERNAL_RECIPIENTS", "3"))
    
    # Keywords for detection (kept from original)
    URGENCY_KEYWORDS = [
        "urgent", "asap", "immediately", "emergency", "critical",
        "deadline", "time-sensitive", "priority", "important"
    ]
    
    LEGAL_KEYWORDS = [
        "contract", "agreement", "legal", "lawsuit", "litigation",
        "attorney", "lawyer", "settlement", "terms and conditions"
    ]
    
    FINANCE_KEYWORDS = [
        "invoice", "payment", "billing", "purchase order", "po",
        "wire transfer", "bank", "account", "credit", "refund"
    ]
    
    SPAM_INDICATORS = [
        "unsubscribe", "click here", "limited time offer",
        "act now", "free", "winner", "congratulations"
    ]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.TOKENS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of missing items"""
        missing = []
        
        if not cls.GMAIL_CLIENT_ID:
            missing.append("GMAIL_CLIENT_ID")
        if not cls.GMAIL_CLIENT_SECRET:
            missing.append("GMAIL_CLIENT_SECRET")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        
        return missing


# Initialize directories on import
Config.ensure_directories()
