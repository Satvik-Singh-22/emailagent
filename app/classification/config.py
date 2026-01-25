class Config:
    # Key domains - VIP organizations and important partners
    VIP_DOMAINS = [
        "google.com", "deepmind.com", "ycombinator.com",
        "microsoft.com", "apple.com", "amazon.com",
        "meta.com", "facebook.com", "openai.com",
        "anthropic.com", "nvidia.com", "tesla.com"
    ]
    
    # Priority defaults
    PRIORITY_THRESHOLD = 70  # Score needed for HIGH priority
    
    # Keyword Lists
    URGENCY_KEYWORDS = {
    # Critical urgency (9-11 points)
    "emergency": 11,
    "immediately": 10,
    "critical": 10,
    "breaking": 9,
    "production down": 11,
    "system down": 11,
    "outage": 10,
    "data loss": 10,
    "security breach": 11,
    "right now": 9,
    "losing money": 10,
    
    # High urgency (7-8 points)
    "urgent": 8,
    "asap": 8,
    "blocked": 8,
    "blocker": 8,
    "stuck": 7,
    "time sensitive": 8,
    "before eod": 7,
    "by end of day": 7,
    "today": 7,
    "this afternoon": 7,
    "within hours": 8,
    "stop everything": 9,
    
    # Medium urgency (5-6 points)
    "help": 6,
    "need help": 6,
    "deadline": 6,
    "priority": 5,
    "important": 5,
    "action required": 6,
    "attention needed": 6,
    "please review": 5,
    "waiting on": 6,
    "response needed": 6,
    
    # Low urgency (3-4 points)
    "reminder": 4,
    "follow up": 4,
    "checking in": 3,
    "update": 3,
    "when you can": 2,
    "no rush": 1
    }

    
    LEGAL_KEYWORDS = ["contract", "agreement", "legal", "lawyer", "suing", "court", "compliance"]
    FINANCE_KEYWORDS = ["invoice", "payment", "bank", "transfer", "salary", "budget", "tax"]
    IT_KEYWORDS = ["access", "password", "login", "git", "repo", "server", "database", "api", "console"]
    HR_KEYWORDS = ["benefit", "offer", "hiring", "resume", "leave", "vacation"]
    MEETING_KEYWORDS = ["schedule", "calendar", "meet", "zoom", "hangout", "invite", "availability"]
    INVITATION_KEYWORDS = ["invited you", "invitation", "join", "invited to", "collaborate"]
    
    COMPLAINT_KEYWORDS = ["dissatisfied", "terrible", "bad service", "angry", "unhappy", "complaint", "fail", "broken", "disappointed", "frustrated", "upset", "unacceptable", "not working", "issue", "problem", "concern", "escalate"]
    
    # High priority indicators
    HIGH_PRIORITY_PATTERNS = [
        "ceo", "cto", "cfo", "executive", "director", "vp",
        "board", "investor", "shareholder", "client",
        "revenue", "sales", "deal", "contract",
        "security", "breach", "vulnerability", "hack"
    ]
    
    # Time-sensitive patterns
    TIME_SENSITIVE_PATTERNS = [
        "due today", "due tomorrow", "expires", "expiring",
        "within 24 hours", "by tomorrow", "this afternoon",
        "before 5pm", "eod today", "end of business"
    ]
    
    # VIP Emails (can be extended)
    VIP_EMAILS = ["boss@example.com", "ceo@example.com"]
    
    # Low priority indicators (reduce score)
    LOW_PRIORITY_INDICATORS = [
        "fyi", "for your information", "heads up", "just so you know",
        "no action required", "optional", "when you have time",
        "no response needed", "read when convenient", "newsletter",
        "automated", "unsubscribe", "notification only"
    ]
    
    # Response time indicators
    RESPONSE_TIME_URGENT = [
        "need by", "due by", "respond by", "reply by",
        "before", "deadline is", "expires", "time is running"
    ]
