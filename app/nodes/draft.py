from app.llm.router import call_llm
from app.memory.memory_utils import summarize_compose_memory


def draft_node(state):
    summary = state.get("summary", "")
    extracted = state.get("extracted_details", {})
    classification = state.get("classification", {})
    risk_flags = state.get("risk_flags", [])
    approval_status = state.get("approval_status", "REQUIRED")

    # If approval is required, draft must be extra conservative
    conservative_mode = approval_status == "REQUIRED"
    memories = state.get("compose_memory", []) or []
    memory_prefs = summarize_compose_memory(memories)

    tone_hint = (
        f"Use a {memory_prefs['tone']} tone."
        if memory_prefs.get("tone")
        else ""
    )

    brevity_hint = (
        "Keep the email concise."
        if memory_prefs.get("brevity") == "concise"
        else ""
    )

    prompt = f"""
You are an email reply drafting assistant.

STRICT RULES:
- Produce a reply DRAFT ONLY
- Do NOT send anything
- Do NOT make legal or financial commitments
- Do NOT confirm agreements or obligations
- Keep tone professional and neutral
- Ask clarifying questions if needed

Context summary:
{summary}

Extracted details:
{extracted}

Style Guidelines (if applicable):
{tone_hint}
{brevity_hint}

Email category: {classification.get("category")}
Intent: {classification.get("intent")}
Risk flags: {risk_flags}

Drafting instructions:
{"Use cautious language and ask for clarification." if conservative_mode else "Respond concisely and helpfully."}

Write the draft reply text only.
"""

    raw_response = call_llm(prompt, "drafting")

    draft = raw_response.strip()

    # Absolute safety fallback
    if not draft:
        draft = (
            "Thank you for your message. I have reviewed the details and will "
            "get back to you after confirming internally."
        )

    state["draft"] = draft
    return state
