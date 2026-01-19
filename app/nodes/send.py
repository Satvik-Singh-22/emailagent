from app.gmail.send import send_email
from app.gmail.client import get_gmail_service

def send_node(state):
    """
    Executes the email send action.
    """
    print("\nSending email...")
    
    # Check if we have real credentials/service (simulated if not available is fine for now, 
    # but based on previous code we have get_gmail_service)
    try:
        service = get_gmail_service()
        print("Service found successfully")
        print(state.get("recipient"))
        print(state.get("subject"))
        
        send_email(
            service=service,
            to=state.get("recipient"),
            subject=state.get("subject"),
            body=state.get("draft"),
            approval_status="APPROVED"
        )
        print("✅ Email sent successfully.")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        # In a real app we might want to loop back to review on failure
        
    return state
