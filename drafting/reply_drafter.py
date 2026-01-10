"""
S12: Draft Reply
Generates draft email replies using Gemini with template fallback
"""

import logging
from typing import Optional
from datetime import datetime

from config import Config
from models import DraftReply, EmailMetadata, IntentDetection

# Gemini SDK
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ReplyDrafter:
    """Generates draft email replies"""

    def __init__(self):
        # Gemini is the only LLM we support
        self.use_gemini = Config.GEMINI_ENABLED and bool(Config.GEMINI_API_KEY)

        # Initialize Gemini client once
        self.gemini_client = None
        if self.use_gemini:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel(Config.GEMINI_MODEL)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.use_gemini = False

    def draft_reply(
        self,
        metadata: EmailMetadata,
        intent: IntentDetection
    ) -> Optional[DraftReply]:
        """
        S12: Draft Reply

        Generate draft response aligned to tone and policy.
        Always returns a draft using:
        Gemini → template fallback
        """
        logger.info(f"Drafting reply for: {metadata.subject}")

        draft_body: Optional[str] = None

        # 1️⃣ Try Gemini first (basic, low-token prompt)
        if self.use_gemini:
            try:
                context = self._build_context(metadata, intent)
                draft_body = self._generate_with_gemini(context)
            except Exception as e:
                logger.error(f"Gemini draft generation failed: {e}")
                draft_body = None

        # 2️⃣ Fallback to template (ALWAYS)
        if not draft_body:
            logger.info("Using fallback template for draft reply")
            draft_body = self._generate_template_response(metadata, intent)

        # 3️⃣ Final safety check
        if not draft_body:
            logger.error("Template draft generation failed — no draft created")
            return None

        # Create reply subject
        subject = self._create_reply_subject(metadata.subject)

        draft = DraftReply(
            subject=subject,
            body=draft_body,
            recipients=[metadata.sender],
            cc=[],
            tone="professional",
            preserves_tone=True,
            created_at=datetime.now(),
            requires_approval=True  # Guardrail: never auto-send
        )

        logger.info("Draft reply generated")
        return draft

    # ------------------------------------------------------------------
    # Gemini generation (INTENTIONALLY SIMPLE TO SAVE CREDITS)
    # ------------------------------------------------------------------

    def _generate_with_gemini(self, context: str) -> Optional[str]:
        """
        Generate a short, professional reply using Gemini.
        Prompt is intentionally minimal to reduce token usage.
        """
        if not self.gemini_client:
            return None

        try:
            response = self.gemini_client.generate_content(context)

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            return None

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    # ------------------------------------------------------------------
    # Prompt builder (SHORT + SAFE)
    # ------------------------------------------------------------------

    def _build_context(
        self,
        metadata: EmailMetadata,
        intent: IntentDetection
    ) -> str:
        """
        Minimal prompt to reduce token usage.
        """
        return (
            "Write a short, professional email reply.\n\n"
            f"Original subject: {metadata.subject}\n"
            f"Sender: {metadata.sender}\n"
            f"Intent: {intent.primary_intent}\n"
            f"Action required: {intent.action_required}\n\n"
            "Reply rules:\n"
            "- Be polite and professional\n"
            "- Acknowledge the email\n"
            "- Do not promise actions\n"
            "- Keep it to 2–3 sentences\n\n"
            "Draft reply:"
        )

    # ------------------------------------------------------------------
    # Template fallback (POLICY-SAFE)
    # ------------------------------------------------------------------

    def _generate_template_response(
        self,
        metadata: EmailMetadata,
        intent: IntentDetection
    ) -> str:
        """Generate simple template-based response"""

        templates = {
            "question": (
                "Thank you for your email. I’ve received your question and will "
                "review it shortly. I’ll get back to you with more details.\n\n"
                "Best regards"
            ),
            "request": (
                "Thank you for reaching out. I’ve noted your request and will "
                "review it shortly. I’ll follow up soon.\n\n"
                "Best regards"
            ),
            "meeting": (
                "Thank you for your message. I’ll check my availability and "
                "get back to you shortly.\n\n"
                "Best regards"
            ),
            "complaint": (
                "Thank you for bringing this to my attention. I understand your "
                "concerns and will look into this matter.\n\n"
                "Best regards"
            ),
            "default": (
                "Thank you for your email. I’ve received your message and will "
                "respond accordingly.\n\n"
                "Best regards"
            ),
        }

        key = intent.primary_intent if intent.primary_intent in templates else "default"
        return templates[key]

    # ------------------------------------------------------------------
    # Subject helper
    # ------------------------------------------------------------------

    def _create_reply_subject(self, original_subject: str) -> str:
        """Create reply subject line"""
        if original_subject.lower().startswith("re:"):
            return original_subject
        return f"Re: {original_subject}"
