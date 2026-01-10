"""
Gmail API client wrapper
"""
import os
import base64
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config
from models import EmailMetadata

logger = logging.getLogger(__name__)


class GmailClient:
    """Gmail API client for email operations"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = Config.TOKENS_DIR / 'token.json'
        
        # Load existing credentials
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), Config.GMAIL_SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Create credentials.json file if needed
                credentials_path = Config.BASE_DIR / 'credentials.json'
                if not credentials_path.exists():
                    logger.error("credentials.json not found. Please download from Google Cloud Console.")
                    raise FileNotFoundError("Gmail API credentials not found")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), Config.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=8080)
            
            # Save credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API authenticated successfully")
    
    def fetch_emails(self, query: str = '', max_results: int = 100, 
                     time_range_days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        D1: Fetch Emails
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to fetch
            time_range_days: Only fetch emails from last N days
        """
        try:
            # Build query with time range
            if time_range_days:
                date_filter = (datetime.now() - timedelta(days=time_range_days)).strftime('%Y/%m/%d')
                query = f"{query} after:{date_filter}" if query else f"after:{date_filter}"
            
            logger.info(f"Fetching emails with query: '{query}'")
            
            # Fetch message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Fetched {len(messages)} email(s)")
            
            return messages
            
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            return []
    
    def get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        D2: Get full email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return message
            
        except HttpError as error:
            logger.error(f"Error getting email details: {error}")
            return None
    
    def extract_metadata(self, message: Dict[str, Any]) -> EmailMetadata:
        """
        D4: Metadata Extraction
        """
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract body
        body_text = ''
        body_html = ''
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body_text = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        # Parse recipients
        recipients = self._parse_email_list(headers.get('To', ''))
        cc = self._parse_email_list(headers.get('Cc', ''))
        bcc = self._parse_email_list(headers.get('Bcc', ''))
        
        # Check attachments
        has_attachments = any('filename' in part for part in message['payload'].get('parts', []))
        attachment_count = sum(1 for part in message['payload'].get('parts', []) if 'filename' in part)
        
        # Parse date
        date_str = headers.get('Date', '')
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()
        
        metadata = EmailMetadata(
            message_id=message['id'],
            thread_id=message['threadId'],
            subject=headers.get('Subject', '(No Subject)'),
            sender=headers.get('From', ''),
            sender_name=self._extract_name(headers.get('From', '')),
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            date=date,
            has_attachments=has_attachments,
            attachment_count=attachment_count,
            labels=message.get('labelIds', []),
            snippet=message.get('snippet', ''),
            body_text=body_text,
            body_html=body_html
        )
        
        return metadata
    
    def _parse_email_list(self, email_string: str) -> List[str]:
        """Parse comma-separated email addresses"""
        if not email_string:
            return []
        
        import re
        # Extract email addresses using regex
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.findall(email_pattern, email_string)
    
    def _extract_name(self, from_header: str) -> Optional[str]:
        """Extract sender name from From header"""
        import re
        match = re.match(r'^(.*?)\s*<', from_header)
        if match:
            return match.group(1).strip(' "')
        return None

    def create_draft(self, to: List[str], subject: str, body: str, 
                    cc: Optional[List[str]] = None, 
                    in_reply_to: Optional[str] = None) -> Optional[str]:
        """
        Create draft email in Gmail and return draft ID, or None on failure.
        """
        if not self.service:
            logger.error("Gmail service not initialized. Cannot create draft.")
            return None

        try:
            message = MIMEMultipart()
            message['to'] = ', '.join(to)
            if cc:
                message['cc'] = ', '.join(cc)
            message['subject'] = subject

            if in_reply_to:
                # Use message-id value if available; keep headers safe
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to

            message.attach(MIMEText(body, 'plain'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()

            draft_id = draft.get('id')
            logger.info(f"✓ Draft created in Gmail: {draft_id}")
            return draft_id

        except HttpError as error:
            logger.error(f"Error creating draft: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating draft: {e}")
            return None

    def send_email(self, draft_id: Optional[str] = None, 
                   to: Optional[List[str]] = None,
                   subject: Optional[str] = None,
                   body: Optional[str] = None) -> bool:
        """
        Send email (from draft or new)
        """
        try:
            if draft_id:
                # Send existing draft
                self.service.users().drafts().send(
                    userId='me',
                    body={'id': draft_id}
                ).execute()
            else:
                # Send new message
                message = MIMEText(body)
                message['to'] = ', '.join(to)
                message['subject'] = subject
                
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                
                self.service.users().messages().send(
                    userId='me',
                    body={'raw': raw}
                ).execute()
            
            logger.info("Email sent successfully")
            return True
            
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            return False
    
    def get_threads(self, message_ids: List[str]) -> Dict[str, List[str]]:
        """
        D3: Thread Mapping
        
        Group messages by thread
        """
        thread_map = {}
        
        for msg_id in message_ids:
            try:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='minimal'
                ).execute()
                
                thread_id = msg['threadId']
                if thread_id not in thread_map:
                    thread_map[thread_id] = []
                thread_map[thread_id].append(msg_id)
                
            except HttpError as error:
                logger.error(f"Error mapping thread for {msg_id}: {error}")
        
        logger.info(f"Mapped {len(message_ids)} messages into {len(thread_map)} threads")
        return thread_map
