from app.memory.supabase_client import supabase
from app.memory.embeddings import embed_text

def memory_retrieve_node(state):
    user_id = state.get("user_id", "default_user")

    query_text = (
        state.get("user_input")
        or state.get("user_prompt")
        or ""
    )

    if not query_text.strip():
        state["episodic_memory"] = []
        return state

    try:
        query_embedding = embed_text(query_text)
    except Exception as e:
        print("⚠️ Memory retrieval embedding failed:", e)
        state["episodic_memory"] = []
        return state

    try:
        response = supabase.rpc(
            "match_episodic_memory",
            {
                "query_embedding": query_embedding,
                "match_user_id": user_id,
                "match_count": 3,
            }
        ).execute()

        state["episodic_memory"] = response.data or []
        print("🧠 Retrieved memories:", state["episodic_memory"])

    except Exception as e:
        print("⚠️ Memory retrieval RPC failed:", e)
        state["episodic_memory"] = []

    return state
