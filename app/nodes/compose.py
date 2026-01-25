from app.llm.router import call_llm
from app.utils.reasoning import add_reasoning
import json
from app.memory.memory_utils import summarize_compose_memory
from app.utils.json_cleaner import *

def compose_node(state):
    prompt = state.get("user_prompt", "")
    edit_instructions = state.get("edit_instructions", "")
    current_draft = state.get("draft", "")

    recipients = state["recipient"]
    attachments = state["attachments"] or []
    subject = state.get("subject")
    body_hint = state.get("body")

    to_list = recipients.get("to", [])
    cc_list = recipients.get("cc", [])
    bcc_list = recipients.get("bcc", [])

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
    

    # ================= EDIT MODE (JSON ONLY) =================
    if edit_instructions:
        add_reasoning(state, "User requested edits — applying requested changes while preserving unchanged fields.")
        llm_prompt = f"""
You are a STRICT EMAIL EDITOR.

Return ONLY valid JSON.
NO prose. NO explanations. NO markdown.

Current Email State:
{{
  "subject": {json.dumps(subject)},
  "draft": {json.dumps(current_draft)},
  "recipient": {{
    "to": {to_list},
    "cc": {cc_list},
    "bcc": {bcc_list}
  }},
  "attachments": {attachments},
  "tone": {json.dumps(state.get("tone"))},
  "brevity": {json.dumps(state.get("brevity"))},
  "summary": {json.dumps(state.get("summary"))}
}}

User Requested Changes:
{edit_instructions}

Rules:
- Apply add/remove operations EXACTLY as requested
- recipient.to / cc / bcc and attachments are MUTABLE ARRAYS
- If a field is NOT mentioned, copy it unchanged
- Do NOT add placeholders like [Your Name]

JSON SCHEMA (MUST MATCH EXACTLY):

{{
  "subject": string,
  "draft": string,
  "recipient": {{
    "to": string[],
    "cc": string[],
    "bcc": string[]
  }},
  "attachments": string[],
  "tone": string,
  "brevity": string,
  "summary": string
}}
"""


        raw = call_llm(llm_prompt, "compose").strip()
        raw= clean_json(raw)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print("❌ Gemini failed to return valid JSON. Edit aborted.")
            state["edit_instructions"] = None
            return state

        # ✅ Apply Gemini edits
        state["subject"] = data["subject"]
        state["recipient"] = data["recipient"]
        state["attachments"] = data["attachments"]
        state["draft"] = data["draft"]
        state["approval_status"] = "REQUIRED"
        state["summary"] = f"Draft prepared for {join(data['recipient']['to']) or 'Unknown'}"
        state["risk_flags"] = ["USER_COMPOSE"]
        state["edit_instructions"] = None
        add_reasoning(state, "Edits applied to draft.")
        return state

    # ================= CREATE MODE (JSON ONLY) =================
    add_reasoning(state, "Creating a new email draft with metadata from the provided intent.")
    llm_prompt = f"""
You are an email writing assistant.

Return ONLY valid JSON.
NO prose. NO explanations. NO markdown.

Context:
To: {join(to_list)}
CC: {join(cc_list)}
BCC: {join(bcc_list)}
Attachments: {attachments}
Existing Subject: {subject}
User Intent: {body_hint or prompt}

Style Hints:
{tone_hint}
{brevity_hint}

Rules:
- If subject is missing, generate one (max 8 words)
- Do NOT add placeholders like [Your Name]
- Preserve existing signature OR use 'Email Agent' OR leave blank

JSON SCHEMA (MUST MATCH EXACTLY):

{{
  "subject": string,
  "draft": string,
  "recipient": {{
    "to": string[],
    "cc": string[],
    "bcc": string[]
  }},
  "attachments": string[],
  "tone": string,
  "brevity": string,
  "summary": string
}}
"""


    raw = call_llm(llm_prompt, "compose").strip()
    raw= clean_json(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(raw)
        print("❌ Gemini failed to return valid JSON. Fallback to simple creation.")
        # Fallback is dangerous here if we need metadata, but for now let's just error or retry? 
        # Ideally we'd retry. For this iteration, let's assume valid JSON or fail.
        # To be safe, we can raise or return a basic error state, but let's try to recover if possible or just fail.
        add_reasoning(state, "JSON generation failed.")
        return state


    state["subject"] = data["subject"]
    state["draft"] = data["draft"]
    state["recipient"] = data["recipient"]
    state["attachments"] = data["attachments"]
    state["tone"] = data["tone"]
    state["brevity"] = data["brevity"]
    state["summary"] = data["summary"]

    print(state["summary"])
    state["approval_status"] = "REQUIRED"
    state["risk_flags"] = ["USER_COMPOSE"]

    add_reasoning(state, "Draft and metadata created.")
    
    state["draft_metadata"] = {
      "tone": data.get("metadata", {}).get("tone") or memory_prefs.get("tone") or "professional",
      "brevity": data.get("metadata", {}).get("brevity") or memory_prefs.get("brevity") or "default",
      "summary": data.get("metadata", {}).get("summary")
    }

    return state
