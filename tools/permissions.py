"""
T1-T2: Tool scope and permissions checker
"""
from typing import List, Dict, Tuple
import logging
from config import Config

logger = logging.getLogger(__name__)


class PermissionChecker:
    """Checks and validates required tool permissions"""
    
    def __init__(self):
        self.required_scopes = Config.GMAIL_SCOPES
        self.available_scopes: List[str] = []
    
    def check_required_tool_scopes(self, gmail_service) -> Tuple[bool, List[str]]:
        """
        T1: Check Required Tool Scopes
        
        Returns:
            (has_all_permissions, missing_scopes)
        """
        logger.info("Checking required tool scopes...")
        
        missing_scopes = []
        
        try:
            # Try to get user profile to verify basic read access
            profile = gmail_service.users().getProfile(userId='me').execute()
            logger.info(f"Gmail access verified for: {profile.get('emailAddress')}")
            
            # Check each required scope
            for scope in self.required_scopes:
                if not self._verify_scope(gmail_service, scope):
                    missing_scopes.append(scope)
            
            self.available_scopes = [s for s in self.required_scopes if s not in missing_scopes]
            
            has_all = len(missing_scopes) == 0
            
            if has_all:
                logger.info("All required tool scopes are available")
            else:
                logger.warning(f"✗ Missing scopes: {missing_scopes}")
            
            return has_all, missing_scopes
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False, self.required_scopes
    
    def _verify_scope(self, gmail_service, scope: str) -> bool:
        """Verify individual scope availability"""
        try:
            # Different verification methods for different scopes
            if 'readonly' in scope:
                # Try to list messages
                gmail_service.users().messages().list(
                    userId='me', maxResults=1
                ).execute()
                return True
            elif 'compose' in scope or 'modify' in scope:
                # Try to list drafts
                gmail_service.users().drafts().list(
                    userId='me', maxResults=1
                ).execute()
                return True
            elif 'send' in scope:
                # Cannot verify send without actually sending
                # Assume available if compose works
                return True
            else:
                return True
                
        except Exception as e:
            logger.debug(f"Scope verification failed for {scope}: {e}")
            return False
    
    def set_entry_note(self, missing_scopes: List[str]) -> str:
        """
        T3: Set Entry Note for missing permissions
        """
        note = f"⚠️ Missing {len(missing_scopes)} required permission(s):\n"
        
        for scope in missing_scopes:
            scope_name = scope.split('/')[-1]
            note += f"  - {scope_name}\n"
        
        note += "\nAgent will operate with limited functionality."
        
        logger.warning(note)
        return note
    
    def notify_missing_tool_scopes(self, missing_scopes: List[str]) -> Dict[str, str]:
        """
        T4: Notify Missing Tool Scopes
        
        Returns notification message for user
        """
        notification = {
            "title": "Missing Gmail Permissions",
            "message": f"Please grant the following permissions to enable full functionality:",
            "missing_scopes": [],
            "instructions": "Re-authenticate with Gmail to grant required permissions."
        }
        
        scope_descriptions = {
            "gmail.readonly": "Read emails and threads",
            "gmail.compose": "Create draft emails",
            "gmail.modify": "Modify email labels and properties",
            "gmail.send": "Send emails on your behalf"
        }
        
        for scope in missing_scopes:
            scope_name = scope.split('/')[-1]
            description = scope_descriptions.get(scope_name, scope_name)
            notification["missing_scopes"].append({
                "scope": scope_name,
                "description": description
            })
        
        logger.info("Missing tool scopes notification prepared")
        return notification
    
    def create_missing_context(self, available_scopes: List[str]) -> Dict[str, bool]:
        """
        T5: Create Missing Context
        
        Build context map of what operations are available
        """
        context = {
            "can_read": False,
            "can_draft": False,
            "can_send": False,
            "can_modify": False,
            "mode": "limited"
        }
        
        for scope in available_scopes:
            if 'readonly' in scope:
                context["can_read"] = True
            if 'compose' in scope:
                context["can_draft"] = True
            if 'send' in scope:
                context["can_send"] = True
            if 'modify' in scope:
                context["can_modify"] = True
        
        # Determine operating mode
        if all([context["can_read"], context["can_draft"], context["can_send"]]):
            context["mode"] = "full"
        elif context["can_read"] and context["can_draft"]:
            context["mode"] = "draft_only"
        elif context["can_read"]:
            context["mode"] = "read_only"
        else:
            context["mode"] = "unavailable"
        
        logger.info(f"Operating mode: {context['mode']}")
        return context
