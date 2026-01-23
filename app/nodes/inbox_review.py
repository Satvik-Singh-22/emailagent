def inbox_review_node(state):
    """
    Shows a list of processed emails, filtered by priority/criteria.
    Allows user to select an email to act on (Summarize/Reply).
    """
    emails = state.get("emails", [])
    filters = state.get("filter_criteria", {})
    
    # 1. Filter Logic
    target_priority = filters.get("priority", "ANY")
    filtered_emails = []
    
    for email in emails:
        # Check priority match
        prio = email.get("classification", {}).get("priority", "MEDIUM")
        if target_priority != "ANY" and prio != target_priority:
            continue
        filtered_emails.append(email)

    if not filtered_emails:
        print(f"\nNo emails found matching filter: {filters}")
        return {**state, "user_action": "DONE"}

    # 2. Display List
    print(f"\n=== INBOX ({len(filtered_emails)}) - Filter: {target_priority} ===")
    for i, email in enumerate(filtered_emails):
        prio = email.get("classification", {}).get("priority", "MED")
        subject = email.get("subject", "No Subject")
        sender = email.get("from", "Unknown")
        print(f"[{i+1}] [{prio}] {sender}: {subject}")
    
    print("-" * 30)

    # 3. Interaction Loop
    while True:
        choice = input("\nSelect Email # (or [E]xit): ").strip().lower()
        
        if choice in ["e", "exit", "done"]:
            state["user_action"] = "DONE"
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(filtered_emails):
                selected_email = filtered_emails[idx]
                
                # Load selected email into main context for other nodes
                state["raw_thread"] = selected_email
                state["thread_id"] = selected_email.get("thread_id")
                # Also copy classification if available
                if "classification" in selected_email:
                    state["classification"] = selected_email["classification"]

                action = input(f"Selected #{idx+1}. Action? [S]ummarize / [R]eply / [B]ack: ").strip().lower()
                
                if action in ["s", "summarize"]:
                    state["user_action"] = "SUMMARIZE"
                    break
                elif action in ["r", "reply"]:
                    state["user_action"] = "REPLY"
                    break
                elif action in ["b", "back"]:
                    continue
                else:
                    print("Invalid action.")
            else:
                print("Invalid selection number.")
        except ValueError:
            print("Please enter a valid number or 'exit'.")

    return state
