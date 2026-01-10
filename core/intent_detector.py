"""
S2: Keyword and Intent Detection
Detects email intent and extracts key information
"""
import logging
import re
from typing import List, Set
from config import Config
from models import IntentDetection, EmailMetadata

logger = logging.getLogger(__name__)


class IntentDetector:
    """Detects intent and keywords in emails"""
    
    def __init__(self):
        self.urgency_keywords = Config.URGENCY_KEYWORDS
        self.legal_keywords = Config.LEGAL_KEYWORDS
        self.finance_keywords = Config.FINANCE_KEYWORDS
        
        # Action keywords
        self.action_keywords = [
            'please', 'can you', 'could you', 'would you',
            'need', 'require', 'request', 'asking', 'help'
        ]
        
        # Question indicators
        self.question_indicators = ['?', 'how', 'what', 'when', 'where', 'why', 'who']
    
    def detect(self, metadata: EmailMetadata) -> IntentDetection:
        """
        S2: Keyword and Intent Detection
        
        Analyzes email content to determine intent and extract keywords
        """
        logger.debug(f"Detecting intent for: {metadata.subject}")
        
        # Combine subject and body for analysis
        full_text = f"{metadata.subject}\n{metadata.body_text}".lower()
        
        # Detect keywords
        urgency_found = self._find_keywords(full_text, self.urgency_keywords)
        legal_found = self._find_keywords(full_text, self.legal_keywords)
        finance_found = self._find_keywords(full_text, self.finance_keywords)
        action_found = self._find_keywords(full_text, self.action_keywords)
        
        # Combine all keywords
        all_keywords = urgency_found + legal_found + finance_found + action_found
        
        # Detect question
        question_detected = self._is_question(full_text, metadata.subject)
        
        # Determine intents
        intents = self._determine_intents(
            urgency_found, legal_found, finance_found,
            action_found, question_detected, full_text
        )
        
        # Determine primary intent
        primary_intent = intents[0] if intents else "informational"
        
        # Determine if action required
        action_required = (
            len(action_found) > 0 or
            question_detected or
            'action' in intents or
            'request' in intents
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(intents, all_keywords)
        
        result = IntentDetection(
            primary_intent=primary_intent,
            intents=intents,
            keywords_detected=list(set(all_keywords)),
            urgency_keywords=urgency_found,
            action_required=action_required,
            question_detected=question_detected,
            confidence=confidence
        )
        
        logger.info(f"Detected intent: {primary_intent} (action required: {action_required})")
        return result
    
    def _find_keywords(self, text: str, keyword_list: List[str]) -> List[str]:
        """Find keywords in text"""
        found = []
        for keyword in keyword_list:
            if keyword.lower() in text:
                found.append(keyword)
        return found
    
    def _is_question(self, text: str, subject: str) -> bool:
        """Detect if email is asking a question"""
        # Check for question mark
        if '?' in subject or text.count('?') > 0:
            return True
        
        # Check for question words at start of sentences
        sentences = text.split('.')
        for sentence in sentences[:3]:  # Check first 3 sentences
            sentence = sentence.strip().lower()
            for indicator in self.question_indicators:
                if sentence.startswith(indicator):
                    return True
        
        return False
    
    def _determine_intents(self, urgency_found: List[str],
                          legal_found: List[str],
                          finance_found: List[str],
                          action_found: List[str],
                          question_detected: bool,
                          full_text: str) -> List[str]:
        """Determine all applicable intents"""
        intents = []
        
        # Urgent intent
        if urgency_found:
            intents.append('urgent')
        
        # Legal intent
        if legal_found:
            intents.append('legal')
        
        # Finance intent
        if finance_found:
            intents.append('finance')
        
        # Action/request intent
        if action_found:
            intents.append('request')
        
        # Question intent
        if question_detected:
            intents.append('question')
        
        # Meeting request
        if self._is_meeting_request(full_text):
            intents.append('meeting')
        
        # Notification
        if self._is_notification(full_text):
            intents.append('notification')
        
        # Complaint
        if self._is_complaint(full_text):
            intents.append('complaint')
        
        # Sales/promotional
        if self._is_sales(full_text):
            intents.append('sales')
        
        # If no specific intent, it's informational
        if not intents:
            intents.append('informational')
        
        return intents
    
    def _is_meeting_request(self, text: str) -> bool:
        """Detect meeting request"""
        meeting_keywords = [
            'meeting', 'call', 'schedule', 'calendar',
            'available', 'time to talk', 'discuss', 'zoom', 'teams'
        ]
        return any(keyword in text for keyword in meeting_keywords)
    
    def _is_notification(self, text: str) -> bool:
        """Detect notification email"""
        notification_keywords = [
            'notification', 'alert', 'reminder', 'update',
            'fyi', 'for your information', 'heads up'
        ]
        return any(keyword in text for keyword in notification_keywords)
    
    def _is_complaint(self, text: str) -> bool:
        """Detect complaint"""
        complaint_keywords = [
            'complaint', 'issue', 'problem', 'disappointed',
            'unhappy', 'dissatisfied', 'not working', 'broken',
            'frustrated', 'unacceptable'
        ]
        return any(keyword in text for keyword in complaint_keywords)
    
    def _is_sales(self, text: str) -> bool:
        """Detect sales/promotional email"""
        sales_keywords = [
            'offer', 'discount', 'sale', 'promotion', 'deal',
            'limited time', 'special', 'buy now', 'save'
        ]
        return any(keyword in text for keyword in sales_keywords)
    
    def _calculate_confidence(self, intents: List[str],
                             keywords: List[str]) -> float:
        """Calculate detection confidence"""
        # More intents and keywords = higher confidence
        intent_score = min(len(intents) * 0.2, 0.6)
        keyword_score = min(len(keywords) * 0.05, 0.4)
        
        confidence = intent_score + keyword_score
        return min(confidence, 1.0)
    
    def extract_deadlines(self, metadata: EmailMetadata) -> List[str]:
        """Extract deadline mentions from email"""
        text = f"{metadata.subject}\n{metadata.body_text}"
        
        # Regex patterns for dates
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}',  # Month Day
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Day of week
            r'(today|tomorrow|tonight|next week|this week)'  # Relative dates
        ]
        
        deadlines = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower())
            deadlines.extend(matches)
        
        return list(set(deadlines))
