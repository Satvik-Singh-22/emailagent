"""
Demo script to test Email Agent
Run this after setting up Gmail API credentials
"""
import json
from email_agent import EmailAgent
from config import Config

def demo_basic_run():
    """Basic demo of email agent"""
    print("\n" + "="*60)
    print("DEMO: Basic Email Agent Run")
    print("="*60)
    
    agent = EmailAgent()
    
    # Simple command
    result = agent.run(
        user_command="Show me today's urgent emails and draft replies",
        user_scope={
            'time_range_days': 10,
            'max_results': 20
        }
    )
    
    print("\n📊 RESULTS:")
    print(json.dumps(result['queue']['summary'], indent=2))
    
    return result


def demo_vip_only():
    """Demo: Process only VIP emails"""
    print("\n" + "="*60)
    print("DEMO: VIP Emails Only")
    print("="*60)
    
    agent = EmailAgent()
    
    # Add some VIP emails
    agent.classifier.add_vip("ceo@company.com")
    agent.classifier.add_vip("founder@startup.com")
    
    result = agent.run(
        user_command="Show only VIP emails from this week",
        user_scope={
            'time_range_days': 7,
            'max_results': 50
        }
    )
    
    return result


def demo_dnd_mode():
    """Demo: DND mode enabled"""
    print("\n" + "="*60)
    print("DEMO: DND (Do Not Disturb) Mode")
    print("="*60)
    
    agent = EmailAgent()
    
    # Enable DND mode
    agent.dnd_handler.set_dnd_mode(True)
    agent.dnd_handler.set_auto_responder(True)
    
    result = agent.run(
        user_command="Process inbox while I'm on vacation",
        user_scope={
            'time_range_days': 1,
            'max_results': 30
        }
    )
    
    # Check how many were blocked
    blocked = result['queue']['summary']['blocked']
    print(f"\n🚫 {blocked} emails blocked due to DND mode")
    
    return result


def demo_with_filters():
    """Demo: Custom Gmail filters"""
    print("\n" + "="*60)
    print("DEMO: Custom Gmail Query Filters")
    print("="*60)
    
    agent = EmailAgent()
    
    result = agent.run(
        user_command="Process unread important emails",
        user_scope={
            'query': 'is:unread is:important',
            'time_range_days': 7,
            'max_results': 50
        }
    )
    
    return result


def demo_check_permissions():
    """Demo: Check what permissions are available"""
    print("\n" + "="*60)
    print("DEMO: Check Gmail API Permissions")
    print("="*60)
    
    from tools import GmailClient, PermissionChecker
    
    gmail = GmailClient()
    checker = PermissionChecker()
    
    has_all, missing = checker.check_required_tool_scopes(gmail.service)
    
    if has_all:
        print("\n✅ All required permissions granted!")
    else:
        print(f"\n⚠️ Missing permissions:")
        for scope in missing:
            print(f"   - {scope}")
        
        notification = checker.notify_missing_tool_scopes(missing)
        print(f"\n{notification['message']}")
    
    context = checker.create_missing_context(checker.available_scopes)
    print(f"\nOperating Mode: {context['mode']}")
    print(f"Can Read: {context['can_read']}")
    print(f"Can Draft: {context['can_draft']}")
    print(f"Can Send: {context['can_send']}")


def main():
    """Main demo menu"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║                 EMAIL AGENT DEMO                      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    
    Available Demos:
    
    1. Basic Run - Process today's emails
    2. VIP Only - Filter for VIP senders
    3. DND Mode - Do Not Disturb mode enabled
    4. Custom Filters - Use Gmail query syntax
    5. Check Permissions - Verify API access
    
    0. Exit
    """)
    
    demos = {
        '1': demo_basic_run,
        '2': demo_vip_only,
        '3': demo_dnd_mode,
        '4': demo_with_filters,
        '5': demo_check_permissions
    }
    
    while True:
        print("""
        ╔═══════════════════════════════════════════════════════╗
        ║                                                       ║
        ║              📧 EMAIL AGENT DEMO 📧                   ║
        ║                                                       ║
        ╚═══════════════════════════════════════════════════════╝
        
        Available Demos:
        
        1. Basic Run - Process today's emails
        2. VIP Only - Filter for VIP senders
        3. DND Mode - Do Not Disturb mode enabled
        4. Custom Filters - Use Gmail query syntax
        5. Check Permissions - Verify API access
        
        0. Exit
        """)
        choice = input("\nSelect demo (0-5): ").strip()
        
        if choice == '0':
            print("\nExiting demo application")
            break
        
        if choice in demos:
            try:
                demos[choice]()
                input("\n Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\nMake sure you have:")
                print("1. Created .env file with API keys")
                print("2. Downloaded credentials.json from Google")
                print("3. Authenticated with Gmail API")
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    # Validate config first
    missing = Config.validate()
    if missing:
        print("Configuration Error: Missing required values:")
        for item in missing:
            print(f"   - {item}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Fill in required values")
        print("3. Download credentials.json from Google Cloud Console")
        exit(1)
    
    main()
