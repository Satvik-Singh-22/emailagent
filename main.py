import sys
from app.graph.graph import build_graph

def run_interactive_mode():
    print("=== EMAIL AGENT INTERACTIVE MODE ===")
    print("Type 'exit' to quit.")
    
    # Compile graph once
    try:
        graph = build_graph()
    except Exception as e:
        print(f"Error building graph: {e}")
        return

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                sys.exit(0)

            print("Thinking...")
            
            # Unified Entry Point
            # The graph handles Intent -> Logic -> Action
            initial_state = {
                "user_prompt": user_input,
                "thread_id": "unified_session",
                "emails": [], # Clear previous email context
                "filter_criteria": {},
                "mode": "UNKNOWN" # Will be set by input_agent
            }

            try:
                graph.invoke(initial_state)
            except Exception as e:
                print(f"Error executing agent: {e}")
                import traceback
                traceback.print_exc()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_interactive_mode()
