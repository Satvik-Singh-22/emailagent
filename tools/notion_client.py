"""
Notion Integration for Email Logs and Task Management
Stores processed email summaries, creates tasks, and logs decisions
"""
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Notion SDK
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    logger.warning("Notion SDK not available. Install with: pip install notion-client")


class NotionClient:
    """Notion integration for email logging and task creation"""
    
    def __init__(self, token: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize Notion client
        
        Args:
            token: Notion Integration Token (or use NOTION_TOKEN env var)
            database_id: Notion Database ID (or use NOTION_DATABASE_ID env var)
        """
        self.enabled = False
        self.client = None
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        
        if not NOTION_AVAILABLE:
            logger.warning("Notion SDK not installed - logging disabled")
            return
        
        # Get token from parameter or environment
        self.token = token or os.getenv("NOTION_TOKEN")
        
        if not self.token:
            logger.warning("NOTION_TOKEN not configured - logging disabled")
            return
        
        if not self.database_id:
            logger.warning("NOTION_DATABASE_ID not configured - logging disabled")
            return
        
        try:
            self.client = Client(auth=self.token)
            # Test connection
            self.client.users.me()
            logger.info("Notion connected successfully")
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            self.enabled = False
    
    def log_email_summary(self, email_data: Dict[str, Any]) -> bool:
        """
        Log processed email summary to Notion
        
        Args:
            email_data: Dictionary with email details
                - subject: str
                - sender: str
                - date: str (ISO format)
                - priority_score: int
                - category: str
                - action_taken: str
                - draft_created: bool
                - notes: str
        
        Returns: True if logged successfully
        """
        if not self.enabled:
            return False
        
        try:
            properties = {
                "Subject": {
                    "title": [
                        {
                            "text": {
                                "content": email_data.get("subject", "No Subject")[:2000]
                            }
                        }
                    ]
                },
                "Sender": {
                    "rich_text": [
                        {
                            "text": {
                                "content": email_data.get("sender", "Unknown")[:2000]
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": email_data.get("date", datetime.now().isoformat())
                    }
                },
                "Priority": {
                    "number": email_data.get("priority_score", 0)
                },
                "Category": {
                    "select": {
                        "name": email_data.get("category", "Unknown")
                    }
                },
                "Draft Created": {
                    "checkbox": email_data.get("draft_created", False)
                }
            }
            
            # Add notes as page content
            children = []
            if "notes" in email_data and email_data["notes"]:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": email_data["notes"][:2000]
                                }
                            }
                        ]
                    }
                })
            
            # Add action taken
            if "action_taken" in email_data and email_data["action_taken"]:
                children.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Action Taken"
                                }
                            }
                        ]
                    }
                })
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": email_data["action_taken"][:2000]
                                }
                            }
                        ]
                    }
                })
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children if children else None
            )
            
            logger.info(f"Logged email to Notion: {email_data.get('subject', 'No Subject')[:50]}")
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to log email to Notion: {e}")
            return False
    
    def create_task_from_email(self, subject: str, description: str, 
                              priority: str = "Medium", due_date: Optional[str] = None) -> bool:
        """
        Create a task in Notion from an email
        
        Args:
            subject: Task title
            description: Task description
            priority: Priority level (Low, Medium, High)
            due_date: Due date in ISO format (optional)
        
        Returns: True if created successfully
        """
        if not self.enabled:
            return False
        
        try:
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": subject[:2000]
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "To Do"
                    }
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                }
            }
            
            # Add due date if provided
            if due_date:
                properties["Due Date"] = {
                    "date": {
                        "start": due_date
                    }
                }
            
            # Add description as page content
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": description[:2000]
                                }
                            }
                        ]
                    }
                }
            ]
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            logger.info(f"Created task in Notion: {subject[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create task in Notion: {e}")
            return False
    
    def log_batch_summary(self, batch_data: Dict[str, Any]) -> bool:
        """
        Log batch processing summary to Notion
        
        Args:
            batch_data: Dictionary with batch summary
                - batch_id: str
                - total_processed: int
                - high_priority: int
                - drafts_created: int
                - blocked: int
                - time_saved_minutes: int
        
        Returns: True if logged successfully
        """
        if not self.enabled:
            return False
        
        try:
            properties = {
                "Subject": {
                    "title": [
                        {
                            "text": {
                                "content": f"Batch Summary - {batch_data.get('batch_id', 'Unknown')}"
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                },
                "Category": {
                    "select": {
                        "name": "Batch Summary"
                    }
                }
            }
            
            # Create detailed summary content
            summary_text = f"""
**Batch Processing Summary**

- Total Processed: {batch_data.get('total_processed', 0)}
- High Priority: {batch_data.get('high_priority', 0)}
- Drafts Created: {batch_data.get('drafts_created', 0)}
- Blocked: {batch_data.get('blocked', 0)}
- Time Saved: {batch_data.get('time_saved_minutes', 0)} minutes
"""
            
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": summary_text
                                }
                            }
                        ]
                    }
                }
            ]
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            logger.info("Logged batch summary to Notion")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log batch summary to Notion: {e}")
            return False
    
    def log_escalation(self, subject: str, category: str, reason: str, 
                      severity: str, details: Dict[str, Any]) -> bool:
        """
        Log escalation event to Notion
        
        Returns: True if logged successfully
        """
        if not self.enabled:
            return False
        
        try:
            properties = {
                "Subject": {
                    "title": [
                        {
                            "text": {
                                "content": f"🚨 ESCALATION: {subject[:1950]}"
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                },
                "Category": {
                    "select": {
                        "name": category.title()
                    }
                },
                "Priority": {
                    "select": {
                        "name": "High" if severity in ["high", "critical"] else "Medium"
                    }
                }
            }
            
            # Create escalation details content
            escalation_text = f"""
**Escalation Details**

**Category:** {category}
**Severity:** {severity}
**Reason:** {reason}

**Additional Details:**
{self._format_details(details)}
"""
            
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": escalation_text[:2000]
                                }
                            }
                        ]
                    }
                }
            ]
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            logger.info(f"Logged escalation to Notion: {category}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log escalation to Notion: {e}")
            return False
    
    def _format_details(self, details: Dict[str, Any]) -> str:
        """Format details dictionary as readable text"""
        formatted = []
        for key, value in details.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
