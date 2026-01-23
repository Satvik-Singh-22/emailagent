import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv() 

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))

def call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def interpret_intent(user_prompt: str) -> dict:
    """
    Classifies the user prompt into a structured intent.
    Returns dict with keys: 'intent', 'parameters'.
    Intents: CHECK_INBOX, COMPOSE, EXIT, UNKNOWN
    """
    system_instruction = (
'''        You are an email command interpreter for a CLI email agent.

Your task is to classify the user's message into EXACTLY ONE of the following intents:

INTENTS:
1. CHECK_INBOX  
   - User wants to read, check, search, filter, or list emails.
   - Examples: "check my inbox", "show unread mails", "any urgent emails?"

2. COMPOSE  
   - User wants to write, draft, reply to, or send an email.
   - Examples: "write an email to HR", "mail my professor about deadline"

3. EXIT  
   - User wants to quit, stop, or exit the application.
   - Examples: "exit", "quit", "close the app"

4. UNKNOWN  
   - Anything that does not clearly match the above.

OUTPUT FORMAT (STRICT JSON ONLY):
Do NOT include markdown, explanations, or extra text.
  {
    "intent": "CHECK_INBOX | COMPOSE | EXIT | UNKNOWN",
    "parameters": {
      "recipient":{
        "to": [],
        "cc": [],
        "bcc": []
      },
      "subject": string | null,
      "body": string | null,
      "attachments": [],
    },
    "filters": {
      "priority": "HIGH" | "MEDIUM" | "LOW" | "ANY",
      "time_range": string | null, 
      "limit": integer (default 5)
    }
  }

  RULES:
  - Always include all keys.
  - If intent = CHECK_INBOX:
    - Extract priority constraints (e.g., "important" -> HIGH, "urgent" -> HIGH).
    - Extract time range (e.g., "last 5 days").
    - Extract limit (e.g., "last 5 mails" -> 5).
  - If intent = COMPOSE:
    - Same rules as before for recipient/subject/body.
    - Set filters to default (ANY, null, 5).
'''    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_instruction}\nUser Prompt: {user_prompt}"
    )

    raw_text = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON:\n{raw_text}") from e

    return parsed
