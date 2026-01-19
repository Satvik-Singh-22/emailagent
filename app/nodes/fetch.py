from app.gmail.client import get_gmail_service
from app.gmail.fetch import fetch_recent_emails

def fetch_node(state):
    """
    Fetches emails from Gmail API based on filters in state.
    """
    filters = state.get("filter_criteria", {})
    limit = filters.get("limit", 5)
    
    # Check if we should filter by unread/time_range? 
    # Current fetch_recent_emails is basic. We pass limit.
    # Advanced filtering logic can be added to fetch_recent_emails later 
    # or filtered in-memory here/classify node.
    
    print(f"DEBUG: Fetching {limit} emails...")
    
    try:
        service = get_gmail_service()
        emails = fetch_recent_emails(service, max_results=limit)
    except Exception as e:
        print(f"Error fetching emails: {e}")
        emails = []
        
    state["emails"] = emails
    return state
