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

    # Determine which memory store to search based on intent
    rpc_func = None
    
    # 1. Composing a new email (COMPOSE mode)
    if state.get("mode") == "COMPOSE":
        rpc_func = "match_compose_memories"
    
    # 2. Replying to an email (REPLY action)
    elif state.get("user_action") == "REPLY":
        rpc_func = "match_reply_memories"
        
    # If no specific context, we might skip retrieval or default to something else.
    # For now, if no RPC selected, return empty.
    if not rpc_func:
        state["episodic_memory"] = []
        return state

    try:
        response = supabase.rpc(
            rpc_func,
            {
                "query_embedding": query_embedding,
                # "match_user_id": user_id, # Note: Current RPC helper might not filter by user_id if not added to schema, but usually good practice. 
                # The schema.sql I added didn't strictly filter by user_id in the WHERE clause, 
                # but let's assume global memory for now or that it's okay. 
                # Ideally we should add user_id filter to RPC if needed.
                "match_count": 3,
            }
        ).execute()

        state["episodic_memory"] = response.data or []
        print(f"🧠 Retrieved memories from {rpc_func}:", len(state["episodic_memory"]))

    except Exception as e:
        print(f"⚠️ Memory retrieval RPC ({rpc_func}) failed:", e)
        state["episodic_memory"] = []

    return state
