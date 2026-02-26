from dotenv import load_dotenv
load_dotenv()

from tools.appointment_db import init_db
from graph.state import initialize_state
from graph.routing import build_graph
from middleware.pii import apply_pii_masking


def run():
    print("\n=== Appointment Assistance System ===\n")

    # Ensure database exists
    init_db()

    # Get user name
    user_name = input("Please enter your name: ").strip() or "Guest"
    print(f"\nHi {user_name}, what can I do for you today?\n")

    # Build LangGraph app
    app = build_graph()

    # Conversation state
    state = None

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print(f"\nGoodbye {user_name}!\n")
            break

        # FIRST TURN
        if state is None:
            state = initialize_state(user_input, user_name)

        # CONTINUING CONVERSATION
        else:
            state["user_input"] = user_input

            # 🔥 IMPORTANT:
            # Only reset to IN_PROGRESS if we are NOT collecting missing info
            if state.get("status") != "NEED_INFO":
                state["status"] = "IN_PROGRESS"

        # Run through LangGraph
        final_state = app.invoke(state)

        # Apply PII masking (post-processing)
        final_state = apply_pii_masking(final_state)

        # Print response
        print("\n------------------------------")
        print("Assistant:", final_state.get("final_response") or final_state.get("draft_response"))
        print("------------------------------\n")

        # End conversation only if finished or escalated
        if final_state.get("status") in ["READY", "ESCALATE"]:
            print("Conversation complete.\n")
            break

        # Continue conversation with updated state
        state = final_state


if __name__ == "__main__":
    run()