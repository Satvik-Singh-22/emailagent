"""
S14: Tone and timing preservation checker
"""
import logging
from datetime import datetime, time
from models import DraftReply

logger = logging.getLogger(__name__)


class TonePreserver:
    """Validates tone and timing of replies"""
    
    def __init__(self):
        self.business_hours_start = time(9, 0)  # 9 AM
        self.business_hours_end = time(18, 0)  # 6 PM
    
    def preserves_tone_or_reply_after_hour(self, draft: DraftReply) -> bool:
        """
        S14: Preserves Tone or Reply After Hour?
        
        Checks if:
        1. Draft preserves appropriate professional tone
        2. If it's outside business hours
        
        Returns True if either condition suggests delay
        """
        logger.debug("Checking tone and timing for draft")
        
        # Check 1: Tone preservation
        tone_ok = self._check_tone(draft)
        
        # Check 2: Business hours
        is_after_hours = self._is_after_hours()
        
        # Should delay if tone issues OR after hours
        should_delay = (not tone_ok) or is_after_hours
        
        if should_delay:
            reason = []
            if not tone_ok:
                reason.append("tone needs review")
            if is_after_hours:
                reason.append("after business hours")
            
            logger.info(f"Draft should be delayed: {', '.join(reason)}")
        else:
            logger.debug("Draft timing and tone OK")
        
        return should_delay
    
    def _check_tone(self, draft: DraftReply) -> bool:
        """Check if tone is appropriate"""
        body_lower = draft.body.lower()
        
        # Problematic phrases
        problematic = [
            'asap', 'immediately', 'right now', 'urgent',
            'must', 'need to', 'have to', 'demand'
        ]
        
        # Check for aggressive language
        for phrase in problematic:
            if phrase in body_lower:
                logger.warning(f"Potentially aggressive phrase detected: {phrase}")
                return False
        
        # Check for appropriate length (not too short/curt)
        if len(draft.body) < 50:
            logger.warning("Draft is too short, may seem curt")
            return False
        
        # Check for proper closing
        closings = ['regards', 'sincerely', 'thanks', 'best', 'thank you']
        has_closing = any(closing in body_lower for closing in closings)
        
        if not has_closing:
            logger.warning("Draft missing proper closing")
            return False
        
        return True
    
    def _is_after_hours(self) -> bool:
        """Check if current time is outside business hours"""
        now = datetime.now().time()
        
        # Check if it's weekend
        if datetime.now().weekday() >= 5:  # Saturday or Sunday
            logger.debug("It's weekend - after hours")
            return True
        
        # Check if outside business hours
        if now < self.business_hours_start or now > self.business_hours_end:
            logger.debug(f"Outside business hours: {now}")
            return True
        
        return False
