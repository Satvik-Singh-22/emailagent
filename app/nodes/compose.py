from app.llm.router import call_llm
from app.utils.reasoning import add_reasoning
import json
from app.memory.memory_utils import summarize_compose_memory


def compose_node(state):
    prompt = state.get("user_prompt", "")
    edit_instructions = state.get("edit_instructions", "")
    current_draft = state.get("draft", "")

    recipients = state["recipient"]
    attachments = state["attachments"]
    subject = state.get("subject")
    body_hint = state.get("body")

    to_list = recipients.get("to", [])
    cc_list = recipients.get("cc", [])
    bcc_list = recipients.get("bcc", [])

    # 🧠 Episodic memory (optional, safe)
    memories = state.get("episodic_memory", []) or []
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


    def join(lst):
        return ", ".join(lst) if lst else ""
    



    # ================= EDIT MODE (JSON ONLY) =================
    if edit_instructions:

        safe_subject = json.dumps(subject)
        safe_to = json.dumps(to_list)
        safe_cc = json.dumps(cc_list)
        safe_bcc = json.dumps(bcc_list)
        safe_attachments = json.dumps(attachments)
        safe_body = json.dumps(current_draft)
        safe_edit = json.dumps(edit_instructions)

        add_reasoning(state, "User requested edits — applying requested changes while preserving unchanged fields.")
        llm_prompt = f"""
You are a STRICT EMAIL EDITOR.

Return ONLY valid JSON.
NO prose. NO explanations. NO markdown.

JSON SCHEMA (MUST MATCH EXACTLY):

{{
  "subject": string,
  "recipient": {{
    "to": string[],
    "cc": string[],
    "bcc": string[]
  }},
  "attachments": string[],
  "body": string
}}

Current Email:
{{
  "subject": {safe_subject},
  "recipient": {{
    "to": {safe_to},
    "cc": {safe_cc},
    "bcc": {safe_bcc}
  }},
  "attachments": {safe_attachments},
  "body": {safe_body}
}}

User Requested Changes:
{safe_edit}

IMPORTANT:

- The following fields are mutable arrays and MUST be updated deterministically if mentioned:
  recipient.to, recipient.cc, recipient.bcc, attachments

- Apply add/remove operations EXACTLY as requested.
- Removed items MUST NOT appear in the output.
- Added items MUST appear in the correct array.
- Fields not mentioned by the user MUST be copied unchanged.
- You MUST NOT ignore requested changes.

- Preserve the existing tone unless the user explicitly requests a tone change.
- Do NOT add placeholders.
- Preserve the existing signature; otherwise use "Email Agent" or leave blank.
"""

        raw = call_llm(llm_prompt, "compose").strip()

        try:
            # print(raw)
            data = json.loads(raw)
        except json.JSONDecodeError:
            print("❌ Gemini failed to return valid JSON. Edit aborted.")
            state["edit_instructions"] = None
            return state

        # 🔒 Hard invariants
        assert isinstance(data["recipient"]["to"], list)
        assert isinstance(data["recipient"]["cc"], list)
        assert isinstance(data["recipient"]["bcc"], list)
        assert isinstance(data["attachments"], list)
        assert isinstance(data["subject"], str)
        assert isinstance(data["body"], str)

        # ✅ Apply Gemini edits
        state["subject"] = data["subject"]
        state["recipient"] = data["recipient"]
        state["attachments"] = data["attachments"]
        state["draft"] = data["body"]
        state["approval_status"] = "REQUIRED"
        state["summary"] = f"Draft prepared for {join(data['recipient']['to']) or 'Unknown'}"
        state["risk_flags"] = ["USER_COMPOSE"]
        state["edit_instructions"] = None
        add_reasoning(state, "Edits applied to draft.")
        return state

    # ================= CREATE MODE (TEXT OK) =================
    add_reasoning(state, "Creating a new email draft from the provided intent.")
    llm_prompt = f"""
You are an email writing assistant.

Task:
Write a professional email.

Context:
To: {join(to_list)}
CC: {join(cc_list)}
BCC: {join(bcc_list)}
attachments: {attachments}
Subject: {subject}
Intent: {body_hint or prompt}

Style Guidelines (if applicable):
{tone_hint}
{brevity_hint}

Rules:
- If Subject is missing, generate one (MUST be ≤ 8 words).
- Output format:

SUBJECT: <subject>
BODY:
<email body>

- Do NOT include To/CC/BCC in the body.
- Use a professional tone by default.
- If the user explicitly requests a different tone, follow it exactly.
- Do NOT add placeholders.
- Preserve an existing signature; otherwise use "Email Agent" or leave blank.
- No reasoning, explanations, or meta text.
- Output email content only.
"""

    raw = call_llm(llm_prompt, "compose").strip()

    # Simple parse for creation
    subject_out = subject
    body_lines = []
    mode = None

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("SUBJECT:"):
            subject_out = line.replace("SUBJECT:", "").strip()
        elif line.startswith("BODY:"):
            mode = "BODY"
            body_lines = []
        elif mode == "BODY":
            body_lines.append(line)

    state["subject"] = subject_out
    state["draft"] = "\n".join(body_lines).strip()
    state["approval_status"] = "REQUIRED"
    state["summary"] = f"Draft prepared for {join(to_list) or 'Unknown'}"
    state["risk_flags"] = ["USER_COMPOSE"]
    add_reasoning(state, "Draft created.")
    state["draft_metadata"] = {
      "tone": memory_prefs.get("tone") or "professional",
      "brevity": memory_prefs.get("brevity") or "default",
    }

    return state
