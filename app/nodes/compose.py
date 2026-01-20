from app.llm.router import call_llm
import json

def compose_node(state):
    prompt = state.get("user_prompt", "")
    edit_instructions = state.get("edit_instructions", "")
    current_draft = state.get("draft", "")

    recipients = state["recipient"]
    subject = state.get("subject")
    body_hint = state.get("body")

    to_list = recipients.get("to", [])
    cc_list = recipients.get("cc", [])
    bcc_list = recipients.get("bcc", [])

    def join(lst):
        return ", ".join(lst) if lst else ""

    # ================= EDIT MODE (JSON ONLY) =================
    if edit_instructions:
        # print(edit_instructions)
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
  "body": string
}}

Current Email:
{{
  "subject": "{subject}",
  "recipient": {{
    "to": {to_list},
    "cc": {cc_list},
    "bcc": {bcc_list}
  }},
  "body": "{current_draft}"
}}

User Requested Changes:
{edit_instructions}

IMPORTANT:
- Recipient lists (to/cc/bcc) MUST be treated as mutable arrays.
- Apply add/remove operations EXACTLY as requested.
- If a recipient is removed, it MUST NOT appear in the output arrays.
- If a recipient is added, it MUST appear in the correct array.
- Do NOT ignore recipient changes.
- Do NOT add placeholders like [Your Name].
- Preserve existing signature OR use 'Email Agent' OR leave blank.
"""

        raw = call_llm(llm_prompt, "compose").strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print("❌ Gemini failed to return valid JSON. Edit aborted.")
            state["edit_instructions"] = None
            return state

        # 🔒 Hard invariants
        assert isinstance(data["recipient"]["to"], list)
        assert isinstance(data["recipient"]["cc"], list)
        assert isinstance(data["recipient"]["bcc"], list)
        assert isinstance(data["subject"], str)
        assert isinstance(data["body"], str)

        # ✅ Apply Gemini edits
        state["subject"] = data["subject"]
        state["recipient"] = data["recipient"]
        state["draft"] = data["body"]
        state["approval_status"] = "REQUIRED"
        state["summary"] = f"Draft prepared for {join(data['recipient']['to']) or 'Unknown'}"
        state["risk_flags"] = ["USER_COMPOSE"]
        state["edit_instructions"] = None
        return state

    # ================= CREATE MODE (TEXT OK) =================
    llm_prompt = f"""
You are an email writing assistant.

Task:
Write a professional email.

Context:
To: {join(to_list)}
CC: {join(cc_list)}
BCC: {join(bcc_list)}
Subject: {subject}
Intent: {body_hint or prompt}

Rules:
- If Subject is missing, generate one.
- Output format:

SUBJECT: <subject>
BODY:
<email body>

- Subject max 8 words.
- Do NOT include To/CC/BCC in body.
- No reasoning.
- Do NOT add placeholders like [Your Name].
- Preserve existing signature OR use 'Email Agent' OR leave blank.
- Professional tone.
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

    return state
