def review_node(state):
    """
    Interactively asks the user to review the draft.
    Returns the state with 'user_action' set to SEND, EDIT, or CANCEL.
    """
    draft = state.get("draft", "")
    recipient = state.get("recipient", "Unknown")
    subject = state.get("subject", "No Subject")

    print("\n--- DRAFT REVIEW ---")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print("-" * 20)
    print(draft)
    print("-" * 20)

    while True:
        choice = input("\n[S]end / [E]dit / [C]ancel: ").strip().lower()

        if choice in ["s", "send"]:
            state["user_action"] = "SEND"
            state["approval_status"] = "APPROVED"
            break
        
        elif choice in ["e", "edit"]:
            state["user_action"] = "EDIT"
            state["approval_status"] = "REJECTED"
            instructions = input("What changes would you like? ")
            state["edit_instructions"] = instructions
            break

        elif choice in ["c", "cancel"]:
            state["user_action"] = "CANCEL"
            break
            
        else:
            print("Invalid choice. Please type S, E, or C.")

    return state
