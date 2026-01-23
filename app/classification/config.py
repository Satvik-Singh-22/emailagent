class Config:
    # Key domains
    VIP_DOMAINS = ["google.com", "deepmind.com", "ycombinator.com"]
    
    # Priority defaults
    PRIORITY_THRESHOLD = 70  # Score needed for HIGH priority
    
    # Keyword Lists
    URGENCY_KEYWORDS = {
    "emergency": 10,
    "urgent": 8,
    "asap": 7,
    "immediately": 9,
    "critical": 9,
    "help": 6,
    "need help": 7,
    "blocked": 8,
    "stuck": 7,
    "deadline": 6,
    "priority": 5,
    "reminder": 4,
    "follow up": 4
    }

    
    LEGAL_KEYWORDS = ["contract", "agreement", "legal", "lawyer", "suing", "court", "compliance"]
    FINANCE_KEYWORDS = ["invoice", "payment", "bank", "transfer", "salary", "budget", "tax"]
    IT_KEYWORDS = ["access", "password", "login", "git", "repo", "server", "database", "api", "console"]
    HR_KEYWORDS = ["benefit", "offer", "hiring", "resume", "leave", "vacation"]
    MEETING_KEYWORDS = ["schedule", "calendar", "meet", "zoom", "hangout", "invite", "availability"]
    INVITATION_KEYWORDS = ["invited you", "invitation", "join", "invited to", "collaborate"]
    
    COMPLAINT_KEYWORDS = ["dissatisfied", "terrible", "bad service", "angry", "unhappy", "complaint", "fail", "broken", "disappointed"]
    
    # VIP Emails (can be extended)
    VIP_EMAILS = ["boss@example.com", "ceo@example.com"]
