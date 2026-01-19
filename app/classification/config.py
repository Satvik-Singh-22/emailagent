class Config:
    # Key domains
    VIP_DOMAINS = ["google.com", "deepmind.com", "ycombinator.com"]
    
    # Priority defaults
    PRIORITY_THRESHOLD = 70  # Score needed for HIGH priority
    
    # Keyword Lists
    URGENCY_KEYWORDS = [
        "urgent", "asap", "deadline", "immediately", "critical", 
        "emergency", "soon", "priority", "alert", "action required"
    ]
    
    LEGAL_KEYWORDS = ["contract", "agreement", "legal", "lawyer", "suing", "court", "compliance"]
    FINANCE_KEYWORDS = ["invoice", "payment", "bank", "transfer", "salary", "budget", "tax"]
    
    # VIP Emails (can be extended)
    VIP_EMAILS = ["boss@example.com", "ceo@example.com"]
