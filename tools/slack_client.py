"""
Slack Integration for Internal Notifications
Sends alerts, escalations, and urgent notifications to Slack
"""
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Slack SDK
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("Slack SDK not available. Install with: pip install slack-sdk")


class SlackClient:
    """Slack integration for notifications and alerts"""
    
    def __init__(self, token: Optional[str] = None, channel: Optional[str] = None):
        """
        Initialize Slack client
        
        Args:
            token: Slack Bot Token (or use SLACK_BOT_TOKEN env var)
            channel: Default channel ID or name (or use SLACK_CHANNEL env var)
        """
        self.enabled = False
        self.client = None
        self.default_channel = channel or os.getenv("SLACK_CHANNEL", "#email-agent")
        
        if not SLACK_AVAILABLE:
            logger.warning("Slack SDK not installed - notifications disabled")
            return
        
        # Get token from parameter or environment
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        
        if not self.token:
            logger.warning("SLACK_BOT_TOKEN not configured - notifications disabled")
            return
        
        try:
            self.client = WebClient(token=self.token)
            # Test connection
            response = self.client.auth_test()
            logger.info(f"Slack connected: {response['team']} - {response['user']}")
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Slack client: {e}")
            self.enabled = False
    
    def send_urgent_alert(self, subject: str, sender: str, priority_score: int, 
                          message_id: str, reason: str) -> bool:
        """
        Send urgent email alert to Slack
        
        Args:
            subject: Email subject
            sender: Email sender
            priority_score: Priority score (0-100)
            message_id: Gmail message ID
            reason: Why it's urgent
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Urgent Email Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Subject:*\n{subject}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*From:*\n{sender}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Priority:*\n{priority_score}/100"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Reason:*\n{reason}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<https://mail.google.com/mail/u/0/#inbox/{message_id}|View in Gmail>"
                    }
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=f"Urgent Email: {subject}",
                blocks=blocks
            )
            
            logger.info(f"Sent urgent alert to Slack: {subject}")
            return response["ok"]
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def send_vip_notification(self, sender: str, subject: str, message_id: str) -> bool:
        """
        Send VIP email notification
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            message = (
                f"⭐ *VIP Email Received*\n"
                f"From: {sender}\n"
                f"Subject: {subject}\n"
                f"<https://mail.google.com/mail/u/0/#inbox/{message_id}|View in Gmail>"
            )
            
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message
            )
            
            logger.info(f"Sent VIP notification to Slack")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send VIP notification: {e}")
            return False
    
    def send_escalation(self, subject: str, category: str, reason: str, 
                       message_id: str, severity: str = "high") -> bool:
        """
        Send escalation notification (legal, finance, security)
        
        Args:
            subject: Email subject
            category: Category (legal, finance, security)
            reason: Escalation reason
            message_id: Gmail message ID
            severity: Severity level (low, medium, high, critical)
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            emoji_map = {
                "legal": "⚖️",
                "finance": "💰",
                "security": "🔒",
                "default": "⚠️"
            }
            
            emoji = emoji_map.get(category.lower(), emoji_map["default"])
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Escalation Required: {category.upper()}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Subject:*\n{subject}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{severity.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Reason:*\n{reason}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<https://mail.google.com/mail/u/0/#inbox/{message_id}|View in Gmail>"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ Escalated at {datetime.now().strftime('%I:%M %p')}"
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=f"Escalation: {category} - {subject}",
                blocks=blocks
            )
            
            logger.info(f"Sent escalation to Slack: {category}")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send escalation: {e}")
            return False
    
    def send_batch_summary(self, total_processed: int, high_priority: int, 
                          drafts_created: int, blocked: int) -> bool:
        """
        Send batch processing summary
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            message = (
                f"📊 *Email Processing Complete*\n"
                f"Processed: {total_processed} emails\n"
                f"High Priority: {high_priority}\n"
                f"Drafts Created: {drafts_created}\n"
                f"Blocked: {blocked}"
            )
            
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message
            )
            
            logger.info("Sent batch summary to Slack")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send batch summary: {e}")
            return False
    
    def send_clarification_request(self, subject: str, questions: list, 
                                   message_id: str) -> bool:
        """
        Send clarification request to user
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            questions_text = "\n".join([f"• {q}" for q in questions])
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❓ Clarification Needed",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Subject:* {subject}\n\n*Questions:*\n{questions_text}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<https://mail.google.com/mail/u/0/#inbox/{message_id}|View in Gmail>"
                    }
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=f"Clarification needed: {subject}",
                blocks=blocks
            )
            
            logger.info("Sent clarification request to Slack")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send clarification request: {e}")
            return False
    
    def send_custom_message(self, message: str, channel: Optional[str] = None) -> bool:
        """
        Send custom message to Slack
        
        Args:
            message: Message text
            channel: Optional channel override
        
        Returns: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            response = self.client.chat_postMessage(
                channel=channel or self.default_channel,
                text=message
            )
            
            logger.info("Sent custom message to Slack")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send custom message: {e}")
            return False
