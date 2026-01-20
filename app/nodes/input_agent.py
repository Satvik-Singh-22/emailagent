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
        analysis = {
            "intent": "UNKNOWN",
            "parameters": {
                "recipient": {"to": [], "cc": [], "bcc": []},
                "subject": None,
                "body": None
            },
            "filters": {
                "priority": "ANY",
                "time_range": None,
                "limit": 5
            }
        }


    state["mode"] = analysis["intent"]
    state["filter_criteria"] = analysis["filters"]

    params = analysis["parameters"]
    state["recipient"] = params["recipient"]
    state["subject"] = params["subject"]
    state["body"] = params["body"]
    state["attachments"] = params["attachments"]

    print(f"DEBUG: Intent={state['mode']}, Filters={state['filter_criteria']}")
    
    return state
