from graph.state import AppointmentState


def human_review(state: AppointmentState) -> AppointmentState:
    state["path_trace"].append("HITL")

    # Skip review for escalation
    if state["status"] == "ESCALATE":
        state["final_response"] = state["draft_response"]
        return state

    # Skip review for NEED_INFO
    if state["status"] == "NEED_INFO":
        state["final_response"] = state["draft_response"]
        return state

    # Only review actions that modify appointments
    if state["intent"] not in ["BOOK", "RESCHEDULE", "CANCEL"]:
        state["final_response"] = state.get("draft_response")
        state["status"] = "READY"
        return state

    # Streamlit/non-interactive mode: approve without terminal prompts.
    if state.get("hitl_mode") == "AUTO_APPROVE":
        state["final_response"] = state["draft_response"]
        state["human_action"] = "APPROVED_AUTO"
        state["status"] = "READY"
        return state

    print("\n--- HUMAN REVIEW REQUIRED ---")
    print("Draft Response:")
    print(state["draft_response"])
    print("\nChoose action:")
    print("1 - Approve")
    print("2 - Edit")
    print("3 - Escalate")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        state["final_response"] = state["draft_response"]
        state["human_action"] = "APPROVED"
        state["status"] = "READY"

    elif choice == "2":
        edited = input("Enter edited response: ").strip()
        state["final_response"] = edited
        state["human_action"] = "EDITED"
        state["status"] = "READY"

    elif choice == "3":
        state["final_response"] = (
            "This request has been escalated for further review."
        )
        state["human_action"] = "ESCALATED"
        state["status"] = "ESCALATE"

    else:
        state["final_response"] = (
            "Invalid selection. Operation cancelled."
        )
        state["human_action"] = "INVALID"
        state["status"] = "READY"

    return state
