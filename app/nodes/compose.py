from app.llm.router import call_llm
import re

def compose_node(state):
    prompt = state.get("user_prompt", "")
    edit_instructions = state.get("edit_instructions", "")
    current_draft = state.get("draft", "")

    # If parameters exist from Gemini intent
    recipient = state.get("recipient")
    subject = state.get("subject")
    initial_body = state.get("body")

    if edit_instructions:
        # Refinement mode
        llm_prompt = f"""
You are an email writing assistant.

Task:
Refine the existing email draft based on the user's feedback.

Existing Draft:
{current_draft}

User Feedback:
{edit_instructions}

Rules:
- Output ONLY the updated email body.
- Do not include subject line in the body.
- Keep tone professional.
"""
    else:
        # New composition mode
        context = f"Recipient: {recipient}\nContent: {prompt}"
        print(context)
        llm_prompt = f"""
You are an email writing assistant.

Task:
Write a professional email based on the following context.

Context:
{context}

Rules:
- Output ONLY the email body.
- Do not include your reasoning, if enough context is not provided, write a general message based on user's message.
- Do NOT include subject lines or headers.
- Do NOT use placeholders like [Your Name] - just sign off as 'Email Agent' or leave blank.
- Keep tone polite and concise.
"""

    raw = call_llm(llm_prompt, "compose")

    # safety fallback
    draft = raw.strip()
    if not draft or draft.startswith("{"):
        draft = "Draft could not be generated. Please write manually."

    state["draft"] = draft
    state["approval_status"] = "REQUIRED"
    state["summary"] = f"Draft for {recipient or 'Unknown'}: {subject or 'No Subject'}"
    state["risk_flags"] = ["USER_COMPOSE"]

    # Clear edit instructions to avoid loops if re-invoked incorrectly
    state["edit_instructions"] = None

    return state
