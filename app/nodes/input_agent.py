import json
from app.llm.gemini import interpret_intent

def input_agent_node(state):
    """
    Analyzes the user prompt and determines the intent, filters, and parameters.
    Default router / decision diamond.
    """
    user_prompt = state.get("user_prompt", "")
    
    if not user_prompt:
        # If no prompt, maybe we are just entering? 
        # But this node usually expects a prompt.
        # Default to checking inbox if empty? Or ask?
        # Let's assume prompt is present or we ask.
        pass

    print(f"Thinking about: '{user_prompt}'")
    
    try:
        analysis = interpret_intent(user_prompt)
    except Exception as e:
        print(f"⚠️ Intent recognition failed: {e}")
        # Fallback to simple keyword matching or just UNKNOWN
        if "check" in user_prompt.lower() or "inbox" in user_prompt.lower():
             analysis = {"intent": "CHECK_INBOX", "parameters": {}, "filters": {}}
        elif "write" in user_prompt.lower() or "send" in user_prompt.lower() or "email" in user_prompt.lower():
             # Basic fallback for compose, though params will be empty
             analysis = {"intent": "COMPOSE", "parameters": {}, "filters": {}}
        else:
             analysis = {"intent": "UNKNOWN", "parameters": {}, "filters": {}}

    intent = analysis.get("intent", "UNKNOWN")
    filters = analysis.get("filters", {})
    params = analysis.get("parameters", {})
    
    # Update state
    state["mode"] = intent  # repurpose mode or use a new key? generic 'mode' works.
    
    # Store detailed structure
    state["filter_criteria"] = filters
    state["recipient"] = params.get("recipient")
    state["subject"] = params.get("subject")
    state["body"] = params.get("body")
    
    print(f"DEBUG: Intent={intent}, Filters={filters}")
    
    return state
