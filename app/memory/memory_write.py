from app.memory.supabase_client import supabase
from app.memory.embeddings import embed_text


def memory_write_node(state):
    """
    Persist a completed agent interaction as an episodic memory.
    """
    print("🧠 MEMORY STATE KEYS:", state.keys())
    print("🧠 intent:", state.get("intent"))
    print("🧠 user_intent:", state.get("user_intent"))
    print("🧠 mode:", state.get("mode"))

    # --- REQUIRED FIELDS ---
    user_id = state.get("user_id", "default_user")
    intent = state.get("mode", "UNKNOWN")

    # --- OUTCOME LOGIC ---
    if state.get("approval_status") == "APPROVED":
        outcome = "APPROVED"
    elif state.get("draft"):
        outcome = "DRAFT_CREATED"
    elif state.get("ranked_emails"):
        outcome = "EMAILS_RANKED"
    else:
        outcome = "COMPLETED"

    # --- EPISODE SUMMARY (THIS IS WHAT WE EMBED) ---
    summary = f"User intent was {intent}. Outcome was {outcome}."

    # --- OPTIONAL METADATA ---
    metadata = {
        "thread_id": state.get("thread_id"),
        "cc": state.get("cc"),
        "bcc": state.get("bcc"),
        "has_attachment": bool(state.get("attachments")),
    }

    # --- EMBEDDING ---
    try:
        embedding = embed_text(summary)
    except Exception as e:
        # Fail-safe: do NOT crash agent
        print("⚠️ Memory embedding failed:", e)
        return state

    # --- WRITE TO SUPABASE ---
    try:
        supabase.from_("episodic_memory").insert({
            "user_id": user_id,
            "intent": intent,
            "outcome": outcome,
            "summary": summary,
            "metadata": metadata,
            "embedding": embedding
        }).execute()
    except Exception as e:
        print("⚠️ Memory write failed:", e)

    return state
